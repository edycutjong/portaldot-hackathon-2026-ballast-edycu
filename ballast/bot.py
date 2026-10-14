"""reserve_bot — key B, the mandatory co-signer. It signs only what the reserve covers, at a FINALIZED block.

Gates (pure functions, unit-tested):
  mint     sign <=> asset 1 not frozen (I7) and min(finalized, latest) reserves >= S1 + S2 + amount
  thaw     sign <=> asset 1 frozen, finality has passed the freeze (the deficit block `eb` the watcher saw, else
                    the freeze's own time), and min(finalized, latest) reserves >= S1 + S2   (wind-down: not built)
  set_team sign <=> the proposed team IS the role map (issuer M_mint, admin M_admin) and the freezer is unchanged —
                    an admin swap would let one key thaw past the reserve gate
Both money gates also refuse while either asset's team differs from the role map (DISARMED) or S2 moved.
S1 = supply of asset 1, S2 = supply of the control asset (fixed: its roles are keyless), both read at the head.
Pending mints: the bot's approval is always the LAST one (2-of-2 / 2-of-3 with the operator first), so a signed
mint executes in the same extrinsic — there is no "approved but not yet executed" supply to add. Co-signing holds
a file lock next to the decision log, so two bot processes can't both pass the gate on the same S1.

The reserve view asks EVERY provider (drpc first on Sepolia: archive depth) for its `finalized` and its `latest`
block. Any provider down or disagreeing on a block's hash or balance, a finalized block older than
`max_finalized_age_s`, a latest block older than `max_latest_age_s`, or a latest block below the finalized one is a
refusal — the bot never signs on a reading it cannot pin. `latest` only ever LOWERS the number used (a drain not yet
final still blocks a mint). Every decision is a row in `ballast.db`.

The thaw gate finds the freeze by scanning events backwards from the head (exact even after several freeze/thaw
episodes; ~4.5 ms per block on the local stand-in, so W = 28,800 blocks ≈ 2 min) BEFORE taking the co-signing lock.
The lookback is W (~24 h) in blocks of the measured block time; a freeze older than W is not found → refused (the
A + A2 override path remains).
"""

from __future__ import annotations

import contextlib
import fcntl
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Callable, Iterator, Sequence

from .chain_profile import derive_block_counts, round_block_time

from .multisig_ops import MultisigAccount, Pending, call_hash, pending
from .roles import Deployment, audit_team, same
from .sepolia import EvmRpc, compare, read_all
from .watchdog import asset_state

READ_DEADLINE_S = 30.0
MAX_FINALIZED_AGE_S = 3600.0  # Sepolia finality lags ~13–19 min; a "finalized" block an hour old = a stuck provider
MAX_LATEST_AGE_S = 120.0  # same bound as the watcher's (10 Sepolia slots): a stale `latest` can hide a fresh drain
FREEZE_LOOKBACK_BLOCKS = 28_800  # fallback lookback (W on the 3 s stand-in, ~24 h) when the block time can't be read
SCAN_LOG_EVERY = 2_000
LOCK_DIR = Path.home() / ".cache" / "ballast"


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
    block_timestamp: int | None = None  # seconds
    provider: str | None = None
    reason: str = ""
    readings: list[dict] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {"ok": self.ok, "reserves": None if self.reserves is None else str(self.reserves),
                "block_number": self.block_number, "block_hash": self.block_hash,
                "block_timestamp": self.block_timestamp, "provider": self.provider, "reason": self.reason,
                "readings": self.readings}


def read_finalized(providers: Sequence[EvmRpc], token: str, holder: str, *, tag: str = "finalized",
                   require_all: bool = False, max_age_s: float | None = None,
                   deadline_s: float = READ_DEADLINE_S) -> Finalized:
    """The LOWEST reading across providers at `tag`. Refuses (ok=False) on silence, disagreement, a block older than
    `max_age_s`, or — with `require_all` — any provider down."""
    readings = read_all(providers, token, holder, tag, max_age_s, deadline_s)
    comp = compare(readings)
    rows = [r.as_dict() for r in readings]
    if not comp.ok:
        return Finalized(False, reason=f"no provider answered a {tag} reading", readings=rows)
    if require_all and comp.failed:
        return Finalized(False, reason=f"{len(comp.failed)} provider(s) without a valid {tag} reading: "
                                       + "; ".join(r.error or "?" for r in comp.failed), readings=rows)
    if comp.disagreements:
        return Finalized(False, reason="providers disagree: " + "; ".join(comp.disagreements), readings=rows)
    low = min(comp.ok, key=lambda r: r.reserves)
    down = f" ({len(comp.failed)} provider(s) down)" if comp.failed else ""
    return Finalized(True, low.reserves, low.block_number, low.block_hash, low.block_timestamp, low.provider,
                     reason=f"lowest {tag} reading{down}", readings=rows)


@dataclass
class ReserveView:
    finalized: Finalized
    latest: Finalized

    @property
    def ok(self) -> bool:
        return self.finalized.ok and self.latest.ok

    @property
    def reason(self) -> str:
        bad = [f"{name}: {v.reason}" for name, v in (("finalized", self.finalized), ("latest", self.latest)) if not v.ok]
        return "; ".join(bad)

    def as_dict(self) -> dict:
        return {"finalized": self.finalized.as_dict(), "latest": self.latest.as_dict()}


def read_view(providers: Sequence[EvmRpc], token: str, holder: str,
              max_finalized_age_s: float | None = MAX_FINALIZED_AGE_S,
              max_latest_age_s: float | None = MAX_LATEST_AGE_S) -> ReserveView:
    view = ReserveView(
        finalized=read_finalized(providers, token, holder, require_all=True, max_age_s=max_finalized_age_s),
        latest=read_finalized(providers, token, holder, tag="latest", require_all=True, max_age_s=max_latest_age_s))
    fin, lat = view.finalized, view.latest
    if fin.ok and lat.ok and lat.block_number < fin.block_number:
        view.latest = Finalized(False, reason=f"latest block #{lat.block_number} is below the finalized block "
                                              f"#{fin.block_number}: a provider serves a stale head",
                                readings=lat.readings)
    return view


@dataclass(frozen=True)
class Gate:
    sign: bool
    reason: str

    @property
    def decision(self) -> str:
        return "signed" if self.sign else "refused"


def mint_gate(finalized: int | None, latest: int | None, s1: int, s2: int, amount: int, frozen: bool) -> Gate:
    if frozen:
        return Gate(False, "I7: the breaker asset is frozen — no mint over a tripped breaker")
    if amount <= 0:
        return Gate(False, "amount must be > 0")
    if finalized is None or latest is None:
        return Gate(False, "reserves unknown")
    need = s1 + s2 + amount
    if finalized < need:
        return Gate(False, f"over-mint: finalized reserves {finalized} < S1 {s1} + S2 {s2} + amount {amount} = {need}")
    if latest < need:
        return Gate(False, f"latest reserves {latest} < S1 + S2 + amount = {need} (a drain not yet final)")
    return Gate(True, f"finalized reserves {finalized} (latest {latest}) >= S1 {s1} + S2 {s2} + amount {amount} = {need}")


def thaw_gate(frozen: bool, finalized: int | None, latest: int | None, s1: int, s2: int, *,
              finalized_block: int | None, finalized_ts: int | None, anchor: dict | None) -> Gate:
    """`anchor` = the freeze being undone: {"eb": reserve-chain block the freezing watcher saw short (deficit
    freezes), "freeze_ts_ms": Portaldot timestamp of the freeze block}. A finalized reading from before the drain
    shows full reserves; it must never justify a thaw."""
    if not frozen:
        return Gate(False, "the breaker asset is not frozen")
    if finalized is None or latest is None or finalized_block is None:
        return Gate(False, "reserves unknown")
    if not anchor:
        return Gate(False, "the freeze could not be located: cannot tell whether finality has passed it")
    if anchor.get("eb") is not None:
        if finalized_block < anchor["eb"]:
            return Gate(False, f"finalized block #{finalized_block} is older than the deficit block #{anchor['eb']}: "
                               "finality has not reached the drain yet")
    elif anchor.get("freeze_ts_ms") is None or finalized_ts is None:
        return Gate(False, "the freeze carries no deficit block and its time is unknown")
    elif finalized_ts * 1000 < anchor["freeze_ts_ms"]:
        return Gate(False, f"finalized block #{finalized_block} (t={finalized_ts}) predates the freeze "
                           f"(t={anchor['freeze_ts_ms'] // 1000}): finality has not passed it yet")
    if finalized < s1 + s2:
        return Gate(False, f"finalized reserves {finalized} < S1 {s1} + S2 {s2} = {s1 + s2}: still short at finality")
    if latest < s1 + s2:
        return Gate(False, f"latest reserves {latest} < S1 + S2 = {s1 + s2}: short again")
    return Gate(True, f"finalized reserves {finalized} (latest {latest}) >= S1 {s1} + S2 {s2} = {s1 + s2}, "
                      f"finalized block #{finalized_block} past the freeze")


def set_team_gate(current: dict, proposed: dict, m_mint: str, m_admin: str) -> Gate:
    if not same(proposed.get("issuer"), m_mint) or not same(current.get("issuer"), m_mint):
        return Gate(False, f"issuer must stay M_mint {m_mint}")
    if not same(proposed.get("freezer"), current.get("freezer")):
        return Gate(False, "the freezer would change (a new watcher set needs a K-block announcement — not built)")
    if not same(proposed.get("admin"), m_admin):
        return Gate(False, f"admin must stay M_admin {m_admin}: another admin could thaw without the bot "
                           "(a new admin set = a new deployment manifest)")
    return Gate(True, "issuer M_mint, admin M_admin, freezer unchanged")


def lookback_blocks(substrate: Any, head: int, sample: int = 20) -> int:
    """W (~24 h) in blocks of the block time measured over the last `sample` blocks (mean: a restart gap only makes
    the lookback SHORTER, which refuses more, never less)."""
    if head <= sample:
        return FREEZE_LOOKBACK_BLOCKS
    ts = lambda n: substrate.query("Timestamp", "Now", block_hash=substrate.get_block_hash(n)).value  # noqa: E731
    ms = (ts(head) - ts(head - sample)) / sample
    return derive_block_counts(round_block_time(ms)).wind_down_w if ms > 0 else FREEZE_LOOKBACK_BLOCKS


def last_freeze(substrate: Any, asset_id: int, head: int, max_lookback: int = FREEZE_LOOKBACK_BLOCKS,
                log: Callable[[str], None] | None = None) -> dict | None:
    """The most recent `Assets.AssetFrozen` of the asset at or before `head` (backward event scan — exact, unlike a
    storage bisection, when the asset was frozen and thawed more than once)."""
    for n in range(head, max(head - max_lookback, 0) - 1, -1):
        if log and (head - n) and (head - n) % SCAN_LOG_EVERY == 0:
            log(f"thaw gate: scanned {head - n}/{max_lookback} blocks back for the freeze")
        block_hash = substrate.get_block_hash(n)
        for ev in substrate.get_events(block_hash):
            v = ev.value
            attrs = v.get("attributes")
            if (v.get("module_id"), v.get("event_id")) == ("Assets", "AssetFrozen") and isinstance(attrs, dict) \
                    and attrs.get("asset_id") == asset_id:
                return {"block_number": n, "block_hash": block_hash, "extrinsic_index": v.get("extrinsic_idx")}
    return None


def freeze_anchor(substrate: Any, asset_id: int, freeze: dict, watchers: Sequence[str]) -> dict:
    """What the thaw gate needs about one freeze: its time, and the deficit block `eb` from the reason remark — only
    a remark IN THE FREEZING EXTRINSIC and SENT BY A WATCHER counts (I5); anything else leaves `eb` unknown."""
    from .remarks import block_remarks, parse

    ts = substrate.query("Timestamp", "Now", block_hash=freeze["block_hash"]).value
    out = {"block_number": freeze["block_number"], "extrinsic_id": f"{freeze['block_number']}-{freeze['extrinsic_index']}",
           "freeze_ts_ms": int(ts) if ts is not None else None, "reason": None, "eb": None, "remark": None}
    for rem in block_remarks(substrate, freeze["block_hash"], prefix="BALLAST/1|freeze|"):
        if rem["extrinsic_index"] != freeze["extrinsic_index"] or not any(same(rem["sender"], w) for w in watchers):
            continue
        try:
            fields = parse(rem["text"])
        except ValueError:
            continue
        if fields.get("a") == str(asset_id):
            eb = fields.get("eb")
            out |= {"reason": fields.get("reason"), "eb": int(eb) if eb and eb.isdigit() else None,
                    "remark": rem["text"]}
    return out


class ReserveBot:
    """Key B. `cosign_*` find the operator's pending proposal by call hash, apply the gate, and either execute
    (final approval) or refuse. Never proposes."""

    def __init__(self, *, substrate: Any, profile: Any, keypair: Any, deployment: Deployment,
                 providers: Sequence[EvmRpc], store: Any, log: Callable[[str], None] = print,
                 max_finalized_age_s: float | None = MAX_FINALIZED_AGE_S,
                 max_latest_age_s: float | None = MAX_LATEST_AGE_S, lock_dir: Path | None = None):
        self.substrate, self.profile, self.keypair, self.dep = substrate, profile, keypair, deployment
        self.providers, self.store, self.log = providers, store, log
        self.max_finalized_age_s, self.max_latest_age_s = max_finalized_age_s, max_latest_age_s
        self.lock_path = (lock_dir or LOCK_DIR) / f"bot-{deployment.profile}-{deployment.genesis_hash[2:10]}.lock"
        self.rm = deployment.role_map()
        if not same(keypair.ss58_address, self.rm.b):
            raise ValueError(f"this key is not the bot key B {self.rm.b}")
        fmt = substrate.ss58_format or 42
        self.m_mint = MultisigAccount(self.rm.mint_signatories, 2, fmt)
        self.m_admin = MultisigAccount(self.rm.admin_signatories, 2, fmt)

    @contextlib.contextmanager
    def _lock(self) -> Iterator[None]:
        """One co-signer at a time per deployment (any db path, any working directory)."""
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.lock_path, "w") as fh:
            fcntl.flock(fh, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(fh, fcntl.LOCK_UN)

    # --- reads -------------------------------------------------------------------------------------------
    def supplies(self, block_hash: str | None = None) -> dict:
        q = lambda i: self.substrate.query("Assets", "Asset", [i], block_hash=block_hash).value  # noqa: E731
        d1, d2 = q(self.dep.breaker), q(self.dep.control)
        a1, a2 = asset_state(self.dep.breaker, d1), asset_state(self.dep.control, d2)
        if not a1.exists:
            raise RuntimeError(f"asset {self.dep.breaker} does not exist")
        problems = audit_team(d1, self.rm.breaker_team())
        problems += [f"control asset: {p}" for p in audit_team(d2, self.rm.control_team())]
        if a2.exists and a2.supply != self.dep.s2:
            problems.append(f"control asset supply {a2.supply} != S2 {self.dep.s2} (S2 is fixed)")
        return {"s1": a1.supply, "s2": a2.supply if a2.exists else 0, "frozen": a1.frozen, "status": a1.status,
                "team_problems": problems}

    def reserves(self) -> ReserveView:
        view = read_view(self.providers, self.dep.reserve["erc20"], self.dep.reserve["vault"], self.max_finalized_age_s,
                         self.max_latest_age_s)
        self.store.readings(view.finalized.readings + view.latest.readings)
        return view

    def _pending(self, account: MultisigAccount, call: Any, proposers: Sequence[str]) -> Pending | None:
        op = pending(self.substrate, account.address, call_hash(call))
        if op is None:
            return None
        if op.approved_by(self.keypair.ss58_address):
            raise RuntimeError("B already approved this operation")
        if not any(op.approved_by(p) for p in proposers):
            raise RuntimeError("the pending operation is not approved by an operator key")
        return op

    def _record(self, kind: str, gate: Gate, view: ReserveView | None, st: dict, **extra) -> int:
        fin = view.finalized if view else Finalized(False)
        return self.store.request(kind=kind, decision=gate.decision, reason=gate.reason,
                                  sep_block_finalized=fin.block_number, sep_hash_finalized=fin.block_hash,
                                  reserves=None if fin.reserves is None else str(fin.reserves),
                                  supply_before=f"{st['s1']}+{st['s2']}", frozen=int(st["frozen"]),
                                  profile=self.profile.name, **extra)

    def _execute(self, account: MultisigAccount, call: Any, op: Pending, row: int, out: dict, *, step: str,
                 label: str, event: str) -> None:
        try:
            r = account.execute(self.substrate, self.profile, self.keypair, call, op, step=step, label=label)
        except Exception:
            self.store.set_exec(row, None, "signed-unknown")  # submitted or not: check the chain, never assume
            raise
        ok = r.outcome.ok and bool(r.inner) and all(o.ok for o in r.inner) and event in r.event_names()
        self.store.set_exec(row, r.extrinsic_id, "signed-executed" if ok else "signed-inner-failed")
        out["receipt"], out["executed_ok"] = r.as_dict(), ok

    # --- co-signing --------------------------------------------------------------------------------------
    def compose(self, function: str, **params: Any):
        return self.substrate.compose_call(call_module="Assets", call_function=function,
                                           call_params={"id": self.dep.breaker, **params})

    def cosign_mint(self, amount: int, beneficiary: str) -> dict:
        call = self.compose("mint", beneficiary=beneficiary, amount=amount)
        with self._lock():
            op = self._pending(self.m_mint, call, [self.rm.a])
            if op is None:
                return {"decision": "no-proposal", "reason": f"no pending M_mint proposal for {call_hash(call)}"}
            st = self.supplies()
            view = self.reserves()
            gate = mint_gate(view.finalized.reserves if view.ok else None, view.latest.reserves if view.ok else None,
                             st["s1"], st["s2"], amount, st["frozen"])
            if not view.ok and not st["frozen"]:
                gate = Gate(False, f"reserves unreadable: {view.reason}")
            if st["team_problems"]:
                gate = Gate(False, "DISARMED: " + "; ".join(st["team_problems"]))
            row = self._record("mint", gate, view, st, amount=str(amount), beneficiary=beneficiary,
                               call_hash=op.call_hash)
            out = {"decision": gate.decision, "reason": gate.reason, "call_hash": op.call_hash,
                   "timepoint": op.timepoint, "amount": str(amount), "state": st, "reserves": view.as_dict(),
                   "finalized": view.finalized.as_dict(), "db_row": row}
            if gate.sign:
                self._execute(self.m_mint, call, op, row, out, step="bot_mint", label="Assets.mint",
                              event="Assets.Issued")
            return out

    def cosign_thaw(self, max_lookback: int | None = None) -> dict:
        call = self.compose("thaw_asset")
        if self._pending(self.m_admin, call, [self.rm.a, self.rm.a2]) is None:
            return {"decision": "no-proposal", "reason": f"no pending M_admin proposal for {call_hash(call)}"}
        # The freeze scan is read-only and can take minutes: done BEFORE the lock, then re-checked under it.
        head = self.substrate.get_block_number(None)
        frozen_now = asset_state(self.dep.breaker, self.substrate.query(
            "Assets", "Asset", [self.dep.breaker], block_hash=self.substrate.get_block_hash(head)).value).frozen
        lookback = max_lookback or lookback_blocks(self.substrate, head)
        freeze = last_freeze(self.substrate, self.dep.breaker, head, lookback, log=self.log) if frozen_now else None
        anchor = freeze_anchor(self.substrate, self.dep.breaker, freeze, self.rm.watchers) if freeze else None
        with self._lock():
            op = self._pending(self.m_admin, call, [self.rm.a, self.rm.a2])
            if op is None:
                return {"decision": "no-proposal", "reason": f"no pending M_admin proposal for {call_hash(call)}"}
            now = self.substrate.get_block_number(None)
            st = self.supplies(self.substrate.get_block_hash(now))
            newer = last_freeze(self.substrate, self.dep.breaker, now, now - head) if now > head else None
            if newer:  # re-frozen while we scanned: anchor on the newest freeze
                anchor = freeze_anchor(self.substrate, self.dep.breaker, newer, self.rm.watchers)
            if anchor is not None:
                anchor["lookback_blocks"] = lookback
            view = self.reserves()
            fin = view.finalized
            gate = thaw_gate(st["frozen"], fin.reserves if view.ok else None, view.latest.reserves if view.ok else None,
                             st["s1"], st["s2"], finalized_block=fin.block_number if view.ok else None,
                             finalized_ts=fin.block_timestamp, anchor=anchor)
            if not view.ok and st["frozen"]:
                gate = Gate(False, f"reserves unreadable: {view.reason}")
            if st["team_problems"]:
                gate = Gate(False, "DISARMED: " + "; ".join(st["team_problems"]))
            row = self._record("thaw", gate, view, st, call_hash=op.call_hash)
            out = {"decision": gate.decision, "reason": gate.reason, "call_hash": op.call_hash,
                   "timepoint": op.timepoint, "state": st, "freeze": anchor, "reserves": view.as_dict(),
                   "finalized": fin.as_dict(), "db_row": row}
            if gate.sign:
                self._execute(self.m_admin, call, op, row, out, step="bot_thaw", label="Assets.thaw_asset",
                              event="Assets.AssetThawed")
            return out

    def cosign_team(self, issuer: str, admin: str, freezer: str) -> dict:
        call = self.compose("set_team", issuer=issuer, admin=admin, freezer=freezer)
        with self._lock():
            op = self._pending(self.m_mint, call, [self.rm.a])  # owner = M_mint
            if op is None:
                return {"decision": "no-proposal", "reason": f"no pending M_mint proposal for {call_hash(call)}"}
            current = self.substrate.query("Assets", "Asset", [self.dep.breaker]).value or {}
            st = self.supplies()
            gate = set_team_gate(current, {"issuer": issuer, "admin": admin, "freezer": freezer}, self.rm.m_mint,
                                 self.rm.m_admin)
            row = self._record("set_team", gate, None, st, call_hash=op.call_hash)
            out = {"decision": gate.decision, "reason": gate.reason, "call_hash": op.call_hash,
                   "timepoint": op.timepoint, "proposed": {"issuer": issuer, "admin": admin, "freezer": freezer},
                   "state": st, "db_row": row}
            if gate.sign:
                self._execute(self.m_mint, call, op, row, out, step="bot_team", label="Assets.set_team",
                              event="Assets.TeamChanged")
            return out


def operator_accounts(deployment: Deployment, ss58_format: int) -> tuple[MultisigAccount, MultisigAccount]:
    rm = deployment.role_map()
    return MultisigAccount(rm.mint_signatories, 2, ss58_format), MultisigAccount(rm.admin_signatories, 2, ss58_format)
