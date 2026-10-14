"""reserve_bot — key B, the mandatory co-signer. It signs only what the reserve covers, at a FINALIZED block.

Gates (pure functions, unit-tested):
  mint     sign <=> asset 1 not frozen (I7) and reserves_finalized >= S1 + S2 + amount
  thaw     sign <=> asset 1 frozen and reserves_finalized >= S1 + S2   (wind-down branch: not built)
  set_team sign <=> issuer stays M_mint and the freezer is unchanged
S1 = supply of asset 1, S2 = supply of the control asset (fixed: its roles are keyless), both read at the head.
Pending mints: the bot's approval is always the LAST one (2-of-2 / 2-of-3 with the operator first), so a signed
mint executes in the same extrinsic — there is no "approved but not yet executed" supply to add.

The finalized reader asks every provider for its `finalized` block (drpc first on Sepolia: archive depth) and uses the
LOWEST reserves among the answers; any provider disagreement on a block's hash or balance, or no answer at all,
is a refusal — the bot never signs on a reading it cannot pin. Every decision is a row in `ballast.db`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any, Callable, Sequence

from .multisig import public_key
from .multisig_ops import MultisigAccount, Pending, call_hash, pending
from .roles import Deployment, audit_team, same
from .sepolia import EvmRpc, compare, read_all
from .watchdog import asset_state

READ_DEADLINE_S = 30.0


def parse_amount(text: str, decimals: int) -> int:
    """"50.00" -> 50_000_000 at 6 decimals. Refuses more decimal places than the asset has, and amounts <= 0."""
    try:
        value = Decimal(text)
    except InvalidOperation:
        raise ValueError(f"not an amount: {text!r}") from None
    units = value * (Decimal(10) ** decimals)
    if units != units.to_integral_value() or units <= 0:
        raise ValueError(f"amount {text} must be > 0 with at most {decimals} decimals")
    return int(units)


@dataclass
class Finalized:
    ok: bool
    reserves: int | None = None
    block_number: int | None = None
    block_hash: str | None = None
    provider: str | None = None
    reason: str = ""
    readings: list[dict] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {"ok": self.ok, "reserves": None if self.reserves is None else str(self.reserves),
                "block_number": self.block_number, "block_hash": self.block_hash, "provider": self.provider,
                "reason": self.reason, "readings": self.readings}


def read_finalized(providers: Sequence[EvmRpc], token: str, holder: str, deadline_s: float = READ_DEADLINE_S) -> Finalized:
    readings = read_all(providers, token, holder, "finalized", None, deadline_s)
    comp = compare(readings)
    rows = [r.as_dict() for r in readings]
    if not comp.ok:
        return Finalized(False, reason="no provider answered a finalized reading", readings=rows)
    if comp.disagreements:
        return Finalized(False, reason="providers disagree: " + "; ".join(comp.disagreements), readings=rows)
    low = min(comp.ok, key=lambda r: r.reserves)
    down = f" ({len(comp.failed)} provider(s) down)" if comp.failed else ""
    return Finalized(True, low.reserves, low.block_number, low.block_hash, low.provider,
                     reason=f"lowest finalized reading{down}", readings=rows)


@dataclass(frozen=True)
class Gate:
    sign: bool
    reason: str

    @property
    def decision(self) -> str:
        return "signed" if self.sign else "refused"


def mint_gate(reserves: int | None, s1: int, s2: int, amount: int, frozen: bool) -> Gate:
    if frozen:
        return Gate(False, "I7: the breaker asset is frozen — no mint over a tripped breaker")
    if amount <= 0:
        return Gate(False, "amount must be > 0")
    if reserves is None:
        return Gate(False, "finalized reserves unknown")
    need = s1 + s2 + amount
    if reserves < need:
        return Gate(False, f"over-mint: finalized reserves {reserves} < S1 {s1} + S2 {s2} + amount {amount} = {need}")
    return Gate(True, f"finalized reserves {reserves} >= S1 {s1} + S2 {s2} + amount {amount} = {need}")


def thaw_gate(frozen: bool, reserves: int | None, s1: int, s2: int, finalized_block: int | None = None,
              deficit_block: int | None = None) -> Gate:
    """`deficit_block` = the reserve-chain block at which the freezing watcher saw the deficit (`eb` of its freeze
    remark). A finalized reading OLDER than that predates the drain and would show full reserves: refused."""
    if not frozen:
        return Gate(False, "the breaker asset is not frozen")
    if reserves is None or finalized_block is None:
        return Gate(False, "finalized reserves unknown")
    if deficit_block is None:
        return Gate(False, "the freeze's deficit block is unknown: cannot tell whether finality has passed it")
    if finalized_block < deficit_block:
        return Gate(False, f"finalized block #{finalized_block} is older than the deficit block #{deficit_block}: "
                           "finality has not reached the drain yet")
    if reserves < s1 + s2:
        return Gate(False, f"finalized reserves {reserves} < S1 {s1} + S2 {s2} = {s1 + s2}: still short at finality")
    return Gate(True, f"finalized reserves {reserves} >= S1 {s1} + S2 {s2} = {s1 + s2}")


def set_team_gate(current: dict, proposed: dict, m_mint: str) -> Gate:
    if not same(proposed.get("issuer"), m_mint) or not same(current.get("issuer"), m_mint):
        return Gate(False, f"issuer must stay M_mint {m_mint}")
    if not same(proposed.get("freezer"), current.get("freezer")):
        return Gate(False, "the freezer would change (a new watcher set needs a K-block announcement — not built)")
    return Gate(True, "issuer stays M_mint and the freezer is unchanged")


def frozen_since(substrate: Any, asset_id: int, head: int) -> int | None:
    """The block at which the asset last went from live to frozen (archive state: galloping + binary search over
    `Assets.Asset(id)` at past blocks). None if it is not frozen at `head`."""
    def frozen_at(n: int) -> bool:
        h = substrate.get_block_hash(n)
        return asset_state(asset_id, substrate.query("Assets", "Asset", [asset_id], block_hash=h).value).frozen

    if not frozen_at(head):
        return None
    hi, step = head, 1
    while True:
        lo = max(hi - step, 0)
        if not frozen_at(lo):
            break
        if lo == 0:
            return 0
        hi, step = lo, step * 2
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if frozen_at(mid):
            hi = mid
        else:
            lo = mid
    return hi


def deficit_anchor(substrate: Any, asset_id: int, freeze_block: int) -> dict:
    """The freeze remark in the freeze block: {"reason", "eb", "remark", "extrinsic_id"}; eb is None if the freeze
    carried no deficit block (providers-down / heartbeat / a freeze without a Ballast remark)."""
    from .remarks import block_remarks, parse

    block_hash = substrate.get_block_hash(freeze_block)
    for rem in block_remarks(substrate, block_hash, prefix="BALLAST/1|freeze|"):
        fields = parse(rem["text"])
        if fields.get("a") == str(asset_id):
            eb = fields.get("eb")
            return {"reason": fields.get("reason"), "eb": int(eb) if eb and eb.isdigit() else None,
                    "remark": rem["text"], "extrinsic_id": rem["extrinsic_id"]}
    return {"reason": None, "eb": None, "remark": None, "extrinsic_id": None}


class ReserveBot:
    """Key B. `cosign_*` find the operator's pending proposal by call hash, apply the gate, and either execute
    (final approval) or refuse. Never proposes."""

    def __init__(self, *, substrate: Any, profile: Any, keypair: Any, deployment: Deployment,
                 providers: Sequence[EvmRpc], store: Any, log: Callable[[str], None] = print):
        self.substrate, self.profile, self.keypair, self.dep = substrate, profile, keypair, deployment
        self.providers, self.store, self.log = providers, store, log
        self.rm = deployment.role_map()
        if not same(keypair.ss58_address, self.rm.b):
            raise ValueError(f"this key is not the bot key B {self.rm.b}")
        fmt = substrate.ss58_format or 42
        self.m_mint = MultisigAccount(self.rm.mint_signatories, 2, fmt)
        self.m_admin = MultisigAccount(self.rm.admin_signatories, 2, fmt)

    # --- reads -------------------------------------------------------------------------------------------
    def supplies(self, block_hash: str | None = None) -> dict:
        q = lambda i: self.substrate.query("Assets", "Asset", [i], block_hash=block_hash).value  # noqa: E731
        d1, d2 = q(self.dep.breaker), q(self.dep.control)
        a1, a2 = asset_state(self.dep.breaker, d1), asset_state(self.dep.control, d2)
        if not a1.exists:
            raise RuntimeError(f"asset {self.dep.breaker} does not exist")
        problems = audit_team(d1, self.rm.breaker_team())
        return {"s1": a1.supply, "s2": a2.supply if a2.exists else 0, "frozen": a1.frozen, "status": a1.status,
                "team_problems": problems}

    def finalized(self) -> Finalized:
        fin = read_finalized(self.providers, self.dep.reserve["token"], self.dep.reserve["vault"])
        self.store.readings(fin.readings)
        return fin

    def _pending(self, account: MultisigAccount, call: Any, proposers: Sequence[str]) -> Pending | None:
        op = pending(self.substrate, account.address, call_hash(call))
        if op is None:
            return None
        if op.approved_by(self.keypair.ss58_address):
            raise RuntimeError("B already approved this operation")
        if not any(op.approved_by(p) for p in proposers):
            raise RuntimeError("the pending operation is not approved by an operator key")
        return op

    def _record(self, kind: str, gate: Gate, fin: Finalized, st: dict, **extra) -> int:
        return self.store.request(kind=kind, decision=gate.decision, reason=gate.reason,
                                  sep_block_finalized=fin.block_number, sep_hash_finalized=fin.block_hash,
                                  reserves=None if fin.reserves is None else str(fin.reserves),
                                  supply_before=f"{st['s1']}+{st['s2']}", frozen=int(st["frozen"]),
                                  profile=self.profile.name, **extra)

    # --- co-signing --------------------------------------------------------------------------------------
    def mint_call(self, amount: int, beneficiary: str):
        return self.substrate.compose_call(call_module="Assets", call_function="mint",
                                           call_params={"id": self.dep.breaker, "beneficiary": beneficiary,
                                                        "amount": amount})

    def thaw_call(self):
        return self.substrate.compose_call(call_module="Assets", call_function="thaw_asset",
                                           call_params={"id": self.dep.breaker})

    def cosign_mint(self, amount: int, beneficiary: str) -> dict:
        call = self.mint_call(amount, beneficiary)
        op = self._pending(self.m_mint, call, [self.rm.a])
        if op is None:
            return {"decision": "no-proposal", "reason": f"no pending M_mint proposal for {call_hash(call)}"}
        st = self.supplies()
        fin = self.finalized()
        gate = mint_gate(fin.reserves if fin.ok else None, st["s1"], st["s2"], amount, st["frozen"])
        if not fin.ok and not st["frozen"]:
            gate = Gate(False, f"finalized reserves unreadable: {fin.reason}")
        if st["team_problems"]:
            gate = Gate(False, "DISARMED: " + "; ".join(st["team_problems"]))
        row = self._record("mint", gate, fin, st, amount=str(amount), beneficiary=beneficiary, call_hash=op.call_hash)
        out = {"decision": gate.decision, "reason": gate.reason, "call_hash": op.call_hash, "timepoint": op.timepoint,
               "amount": str(amount), "state": st, "finalized": fin.as_dict(), "db_row": row}
        if gate.sign:
            r = self.m_mint.execute(self.substrate, self.profile, self.keypair, call, op, step="bot_mint",
                                    label="Assets.mint")
            self.store.set_exec(row, r.extrinsic_id)
            out["receipt"] = r.as_dict()
            out["executed_ok"] = r.outcome.ok and bool(r.inner) and all(o.ok for o in r.inner) and \
                "Assets.Issued" in r.event_names()
        return out

    def cosign_thaw(self) -> dict:
        call = self.thaw_call()
        op = self._pending(self.m_admin, call, [self.rm.a, self.rm.a2])
        if op is None:
            return {"decision": "no-proposal", "reason": f"no pending M_admin proposal for {call_hash(call)}"}
        head = self.substrate.get_block_number(None)
        st = self.supplies(self.substrate.get_block_hash(head))
        since = frozen_since(self.substrate, self.dep.breaker, head) if st["frozen"] else None
        anchor = deficit_anchor(self.substrate, self.dep.breaker, since) if since is not None else {}
        fin = self.finalized()
        gate = thaw_gate(st["frozen"], fin.reserves if fin.ok else None, st["s1"], st["s2"],
                         fin.block_number if fin.ok else None, anchor.get("eb"))
        if not fin.ok and st["frozen"]:
            gate = Gate(False, f"finalized reserves unreadable: {fin.reason}")
        row = self._record("thaw", gate, fin, st, call_hash=op.call_hash)
        out = {"decision": gate.decision, "reason": gate.reason, "call_hash": op.call_hash, "timepoint": op.timepoint,
               "state": st, "frozen_since": since, "freeze": anchor, "finalized": fin.as_dict(), "db_row": row}
        if gate.sign:
            r = self.m_admin.execute(self.substrate, self.profile, self.keypair, call, op, step="bot_thaw",
                                     label="Assets.thaw_asset")
            self.store.set_exec(row, r.extrinsic_id)
            out["receipt"] = r.as_dict()
            out["executed_ok"] = r.outcome.ok and bool(r.inner) and all(o.ok for o in r.inner) and \
                "Assets.AssetThawed" in r.event_names()
        return out


def operator_accounts(deployment: Deployment, ss58_format: int) -> tuple[MultisigAccount, MultisigAccount]:
    rm = deployment.role_map()
    return MultisigAccount(rm.mint_signatories, 2, ss58_format), MultisigAccount(rm.admin_signatories, 2, ss58_format)


def is_operator(deployment: Deployment, who: str) -> bool:
    rm = deployment.role_map()
    return public_key(who) in {public_key(rm.a), public_key(rm.a2)}
