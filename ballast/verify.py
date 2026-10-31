"""`ballast verify` — re-check the public record of one deployment over a block range, on BOTH chains.

Remarks (`BALLAST/1|<type>|…`, found via `System.Remarked`; the sender is the effective origin). Signers are fixed
per type (I5); any other signer/type pair is REJECTED and never counted:
  attest, heartbeat, watchers, evm-attester, final -> B          override -> A, A2 or M_admin
  freeze -> a member of the watcher set                          redeem   -> a holder of asset 1
  attest / heartbeat: S1, S2 and the frozen flag re-read at the remark's Portaldot block hash `ph` (and `pb` must be
    that block's number); reserves re-read with `eth_call` at the reserve-chain block hash `eh` (EIP-1898) and `eb`
    must be its number. PASS iff every value matches; UNVERIFIABLE if no provider can serve that block (pruned).
    Every provider that serves `eh` must report the same number and balance (else FAIL).
  A malformed BALLAST/1 remark sent by B is a FAIL (the bot published something unparseable); from anyone else it is
    REJECTED (noise, never counted).
  watchers: the members + threshold must recompute to asset 1's freezer at that block.
  evm-attester: the oracle's `attester()` must equal the announced H160.
Events on asset 1 — flagged on WHAT changed, not who signed (I4):
  AssetThawed      ok only via M_admin with B as the executing (last) approval; via A + A2 only after an `override`
                   remark — each override justifies ONE later thaw; anything else FLAGGED.
  TeamChanged      issuer != M_mint, admin != M_admin or freezer != M_watch -> DISARMED.
  OwnerChanged     to anyone but M_mint -> FLAGGED.
  AssetStatusChanged (Root force) -> FLAGGED.
  MultisigExecuted on M_mint / M_admin with an inner Err -> listed with the decoded error (I9).
Events on the control asset (asset 2, S2 fixed, keyless roles): any Issued / Burned / TeamChanged / OwnerChanged /
  AssetThawed / AssetStatusChanged -> FLAGGED (S2 must never move).
Verdict: FAIL on any FAIL/FLAGGED; EMPTY (exit 1) when no B attestation was counted — nothing was proven; else PASS.
ReserveOracle `Posted` events (I10): each must match a PASSing attestation with the same pb and values, included in
the same or an earlier block — else FLAGGED (a mirror that leads or invents).
"""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any

from .attest import ATTEST_TYPES, snapshot_from_fields
from .dispatch import decode_dispatch_result
from .multisig import multi_address, public_key
from .oracle import decode_posted
from .remarks import block_remarks, parse
from .sepolia import EvmRpc, ProviderError, balance_at
from .watchdog import asset_state

B_TYPES = ("attest", "heartbeat", "watchers", "admins", "evm-attester", "final")
CONTROL_FLAGGED = ("Issued", "Burned", "TeamChanged", "OwnerChanged", "AssetThawed", "AssetStatusChanged",
                   "AssetFrozen", "Destroyed", "DestructionStarted")


@dataclass
class Roles:
    b: str
    a: str
    a2: str
    m_mint: str
    m_admin: str
    m_watch: str
    watchers: list[str]
    breaker: int
    control: int
    oracle: str | None = None

    @classmethod
    def from_deployment(cls, dep: Any) -> "Roles":
        rm = dep.role_map()
        return cls(b=rm.b, a=rm.a, a2=rm.a2, m_mint=rm.m_mint, m_admin=rm.m_admin, m_watch=rm.m_watch,
                   watchers=list(rm.watchers), breaker=dep.breaker, control=dep.control,
                   oracle=((dep.oracle or {}).get("address") or "").lower() or None)

    def is_(self, who: str | None, *accounts: str) -> bool:
        return who is not None and public_key(who) in {public_key(a) for a in accounts}

    def role_name(self, who: str | None) -> str:
        names = {"B": self.b, "A": self.a, "A2": self.a2, "M_mint": self.m_mint, "M_admin": self.m_admin,
                 "M_watch": self.m_watch} | {f"W{i}": w for i, w in enumerate(self.watchers, 1)}
        return next((n for n, a in names.items() if self.is_(who, a)), who or "?")


def signer_verdict(kind: str, sender: str, roles: Roles, holds_asset1: Callable[[], bool]) -> tuple[bool, str]:
    """(accepted, rule) for one remark type + effective sender (I5)."""
    if kind in B_TYPES:
        return roles.is_(sender, roles.b), "signer must be B"
    if kind == "override":
        return roles.is_(sender, roles.a, roles.a2, roles.m_admin), "signer must be A, A2 or M_admin"
    if kind == "freeze":
        return roles.is_(sender, *roles.watchers), "signer must be a watcher-set member"
    if kind == "redeem":
        return holds_asset1(), "signer must hold asset 1"
    return False, f"unknown type {kind!r}"


@dataclass
class Finding:
    extrinsic_id: str
    block_number: int
    kind: str
    verdict: str  # PASS | FAIL | REJECTED | ACCEPTED | UNVERIFIABLE | IGNORED | OK | FLAGGED | INFO
    detail: str
    sender: str | None = None
    text: str | None = None
    checks: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v not in (None, {}, "")}


class Verifier:
    def __init__(self, substrate: Any, roles: Roles, providers: Sequence[EvmRpc], vault: str, erc20: str,
                 log: Callable[[str], None] = lambda s: None, control_settled_at: int = 0):
        self.substrate, self.roles, self.providers = substrate, roles, providers
        self.vault, self.erc20, self.log = vault, erc20, log
        self.control_settled_at = control_settled_at  # last block of the setup that made asset 2 keyless
        self.findings: list[Finding] = []
        self.attested: dict[int, dict] = {}  # pb -> {fields, block, verdict}
        self.overrides: list[int] = []  # blocks of accepted override remarks not yet used by a thaw

    # --- reads -------------------------------------------------------------------------------------------
    def asset(self, asset_id: int, block_hash: str):
        return asset_state(asset_id, self.substrate.query("Assets", "Asset", [asset_id], block_hash=block_hash).value)

    def reserve_at(self, eh: str) -> tuple[int | None, int | None, str]:
        """(block number, balance, providers) at the reserve-chain block hash, asked of EVERY provider; providers that
        serve it must agree on both, else (None, None, "disagree: …") with a `disagree` marker. (None, None, why) if
        nobody serves it."""
        errors, answers = [], []
        for p in self.providers:
            try:
                block = p.call("eth_getBlockByHash", [eh, False])
                if not block:
                    errors.append(f"{p.name}: no block {eh[:12]}…")
                    continue
                answers.append((int(block["number"], 16), balance_at(p, self.erc20, self.vault, eh), p.name))
            except (ProviderError, ValueError, KeyError, TypeError) as exc:
                errors.append(str(exc)[:120])
        if not answers:
            return None, None, "; ".join(errors) or "no provider"
        if len({(n, b) for n, b, _ in answers}) > 1:
            return None, None, "DISAGREE: " + ", ".join(f"{name}=#{n}/{b}" for n, b, name in answers)
        return answers[0][0], answers[0][1], "+".join(name for _, _, name in answers)

    # --- remarks -----------------------------------------------------------------------------------------
    def check_remark(self, rem: dict) -> Finding:
        base = dict(extrinsic_id=rem["extrinsic_id"], block_number=rem["block_number"], sender=rem["sender"],
                    text=rem["text"])
        try:
            fields = parse(rem["text"])
        except ValueError as exc:
            if self.roles.is_(rem["sender"], self.roles.b):
                return Finding(kind="?", verdict="FAIL", detail=f"malformed remark from B: {exc}", **base)
            return Finding(kind="?", verdict="REJECTED", detail=f"malformed: {exc}", **base)
        kind = fields["type"]
        scoped = ("attest", "heartbeat", "freeze", "watchers", "admins", "final", "redeem")
        if kind in scoped and (kind in ("attest", "heartbeat", "freeze") or "a" in fields) \
                and fields.get("a") != str(self.roles.breaker):
            return Finding(kind=kind, verdict="IGNORED", detail=f"asset {fields.get('a')} is not this deployment's", **base)

        def holds() -> bool:
            parent = self.substrate.get_block_hash(rem["block_number"] - 1)
            acct = self.substrate.query("Assets", "Account", [self.roles.breaker, rem["sender"]], block_hash=parent).value
            return bool(acct and acct["balance"] > 0)

        accepted, rule = signer_verdict(kind, rem["sender"], self.roles, holds)
        who = self.roles.role_name(rem["sender"])
        if not accepted:
            return Finding(kind=kind, verdict="REJECTED", detail=f"sender {who}: {rule} (I5) — not counted", **base)
        if kind in ATTEST_TYPES:
            return self.check_attestation(fields, rem, base)
        if kind in ("watchers", "admins") and "a" in fields:  # a rotation announcement (ballast/governance.py)
            from .governance import announcement_of
            from .governance import Posted as _Posted

            try:
                a = announcement_of(_Posted(rem["extrinsic_id"], rem["block_number"], rem["sender"], rem["sender"],
                                            rem["text"], fields), self.substrate.ss58_format or 42)
            except ValueError as exc:
                return Finding(kind=kind, verdict="FAIL", detail=f"bad rotation announcement: {exc}", **base)
            role = "freezer" if kind == "watchers" else "admin"
            return Finding(kind=kind, verdict="ACCEPTED",
                           detail=f"rotation announced by B: {role} -> t={a.threshold} m={len(a.members)} "
                                  f"{a.address} (the bot co-signs the set_team only >= K blocks later)", **base)
        if kind == "watchers":
            members = fields.get("m", "").split(",")
            try:
                derived = multi_address(members, int(fields.get("t", "0")))
            except ValueError as exc:
                return Finding(kind=kind, verdict="FAIL", detail=f"bad watcher set: {exc}", **base)
            freezer = self.substrate.query("Assets", "Asset", [self.roles.breaker],
                                           block_hash=rem["block_hash"]).value["freezer"]
            ok = public_key(derived) == public_key(freezer)
            return Finding(kind=kind, verdict="PASS" if ok else "FAIL",
                           detail=f"t={fields.get('t')} m={len(members)} -> {derived} "
                                  f"{'==' if ok else '!='} asset {self.roles.breaker} freezer {freezer}", **base)
        if kind == "evm-attester":
            if not self.roles.oracle or fields.get("oracle", "").lower() != self.roles.oracle:
                return Finding(kind=kind, verdict="FAIL", detail="announces another oracle than the deployment's", **base)
            from .oracle import attester

            onchain = attester(self.substrate, self.roles.b, self.roles.oracle, rem["block_hash"])
            ok = onchain.lower() == fields.get("h160", "").lower()
            return Finding(kind=kind, verdict="PASS" if ok else "FAIL",
                           detail=f"oracle attester() {onchain} {'==' if ok else '!='} announced {fields.get('h160')}",
                           **base)
        if kind == "override":
            self.overrides.append(rem["block_number"])
        return Finding(kind=kind, verdict="ACCEPTED", detail=f"sender {who}", **base)

    def check_attestation(self, fields: dict, rem: dict, base: dict) -> Finding:
        kind = fields["type"]
        try:
            snap = snapshot_from_fields(fields)
        except (KeyError, ValueError) as exc:
            return Finding(kind=kind, verdict="FAIL", detail=f"missing/bad field: {exc}", **base)
        checks: dict[str, Any] = {}
        problems = []
        header = self.substrate.get_block_header(snap.ph)
        pb_seen = header["header"]["number"] if header and header.get("header") else None
        checks["pb"] = [snap.pb, pb_seen]
        if pb_seen != snap.pb or self.substrate.get_block_hash(snap.pb) != snap.ph:
            problems.append(f"ph is not block #{snap.pb} on this chain")
        elif snap.pb >= rem["block_number"]:
            problems.append("pb is not before the remark's block")
        else:
            a1, a2 = self.asset(snap.a, snap.ph), self.asset(snap.a2, snap.ph)
            checks |= {"s": [snap.s, a1.supply], "s2": [snap.s2, a2.supply], "f": [snap.frozen, a1.frozen]}
            if snap.a2 != self.roles.control:
                problems.append(f"a2={snap.a2} is not the control asset {self.roles.control}")
            for k in ("s", "s2", "f"):
                if checks[k][0] != checks[k][1]:
                    problems.append(f"{k} {checks[k][0]} != chain {checks[k][1]} at ph")
        eb, r, provider = self.reserve_at(snap.eh)
        if eb is None:
            verdict = "FAIL" if problems or provider.startswith("DISAGREE") else "UNVERIFIABLE"
            return Finding(kind=kind, verdict=verdict, detail="; ".join(problems + [f"reserve block unavailable: {provider}"]),
                           checks=checks, **base)
        checks |= {"eb": [snap.eb, eb], "r": [snap.r, r], "provider": provider}
        if eb != snap.eb:
            problems.append(f"eh is block #{eb}, remark says #{snap.eb}")
        if r != snap.r:
            problems.append(f"r {snap.r} != {r} at eh ({provider})")
        verdict = "FAIL" if problems else "PASS"
        if verdict == "PASS":
            self.attested[snap.pb] = {"fields": fields, "block": rem["block_number"], "extrinsic_id": rem["extrinsic_id"]}
        detail = "; ".join(problems) if problems else (
            f"S1 {snap.s} + S2 {snap.s2} (frozen={snap.frozen}) at #{snap.pb} · reserves {snap.r} at #{snap.eb} "
            f"via {provider}: both chains match")
        return Finding(kind=kind, verdict=verdict, detail=detail, checks=checks, **base)

    # --- events ------------------------------------------------------------------------------------------
    def check_events(self, number: int, block_hash: str, events: list[dict], posted: list[tuple]) -> None:
        by_idx: dict[int, list[dict]] = {}
        for ev in events:
            by_idx.setdefault(ev.get("extrinsic_idx"), []).append(ev)
        for idx, evs in by_idx.items():
            xid = f"{number}-{idx}"
            execs = [e["attributes"] for e in evs if (e["module_id"], e["event_id"]) == ("Multisig", "MultisigExecuted")]
            for e in evs:
                mod, name, attrs = e["module_id"], e["event_id"], e["attributes"]
                if mod == "Assets" and isinstance(attrs, dict) and attrs.get("asset_id") == self.roles.breaker:
                    self._asset_event(xid, number, name, attrs, execs)
                elif mod == "Assets" and isinstance(attrs, dict) and attrs.get("asset_id") == self.roles.control \
                        and name in CONTROL_FLAGGED and number > self.control_settled_at:
                    self.findings.append(Finding(xid, number, "control", "FLAGGED",
                                                 f"Assets.{name} on the control asset {self.roles.control} "
                                                 "(S2 and its keyless roles must never change)"))
                elif (mod, name) == ("Revive", "ContractEmitted") and self.roles.oracle and \
                        str(attrs.get("contract", "")).lower() == self.roles.oracle:
                    p = decode_posted(attrs)
                    if p:
                        posted.append((xid, number, p))
            for ex in execs:
                if self.roles.is_(ex["multisig"], self.roles.m_mint, self.roles.m_admin):
                    outcome = decode_dispatch_result(ex["result"], self.substrate.metadata)
                    if not outcome.ok:
                        self.findings.append(Finding(xid, number, "multisig-inner", "INFO",
                                                     f"{self.roles.role_name(ex['multisig'])} executed with inner "
                                                     f"{outcome} (I9: outer Ok, inner failed)"))

    def _asset_event(self, xid: str, number: int, name: str, attrs: dict, execs: list[dict]) -> None:
        r = self.roles
        if name == "AssetThawed":
            admin = [x for x in execs if r.is_(x["multisig"], r.m_admin)]
            if admin and r.is_(admin[-1]["approving"], r.b):
                self.findings.append(Finding(xid, number, "thaw", "OK", "M_admin thaw, executed by the bot's co-signature"))
            elif admin and any(o <= number for o in self.overrides):
                used = min(o for o in self.overrides if o <= number)
                self.overrides.remove(used)  # one override justifies one thaw
                self.findings.append(Finding(xid, number, "thaw", "OK",
                                             f"M_admin thaw without the bot, after the override remark in #{used} "
                                             "(emergency path; that override is now used)"))
            else:
                self.findings.append(Finding(xid, number, "thaw", "FLAGGED",
                                             "thaw without the bot's co-signature or an override remark (I4)"))
        elif name == "TeamChanged":
            bad = [k for k, want in (("issuer", r.m_mint), ("admin", r.m_admin), ("freezer", r.m_watch))
                   if not r.is_(attrs.get(k), want)]
            self.findings.append(Finding(xid, number, "team", "FLAGGED" if bad else "OK",
                                         f"DISARMED: {', '.join(bad)} changed" if bad else
                                         "issuer M_mint, admin M_admin, freezer M_watch"))
        elif name == "OwnerChanged":
            ok = r.is_(attrs.get("owner"), r.m_mint)
            self.findings.append(Finding(xid, number, "owner", "OK" if ok else "FLAGGED",
                                         "owner M_mint" if ok else f"owner moved to {attrs.get('owner')}"))
        elif name == "AssetStatusChanged":
            self.findings.append(Finding(xid, number, "status", "FLAGGED", "force_asset_status (Root) changed asset 1"))

    def check_posted(self, posted: list[tuple]) -> None:
        for xid, number, p in posted:
            rem = self.attested.get(p["pd_block"])
            if rem is None:
                self.findings.append(Finding(xid, number, "oracle-post", "FLAGGED",
                                             f"Posted pdBlock {p['pd_block']} has no PASSing B attestation (I10)"))
                continue
            f = snapshot_from_fields(rem["fields"])
            same = (p["s1"], p["s2"], p["reserves"], p["sep_block"], p["sep_hash"], p["frozen"]) == \
                (f.s, f.s2, f.r, f.eb, f.eh, f.frozen)
            leads = number < rem["block"]
            verdict = "OK" if same and not leads else "FLAGGED"
            why = "values match attestation " + rem["extrinsic_id"] if same else "values differ from " + rem["extrinsic_id"]
            if leads:
                why += "; the mirror was posted BEFORE the remark (leads)"
            self.findings.append(Finding(xid, number, "oracle-post", verdict, why))

    # --- driver ------------------------------------------------------------------------------------------
    def run(self, start: int, end: int) -> list[Finding]:
        posted: list[tuple] = []
        for number in range(start, end + 1):
            block_hash = self.substrate.get_block_hash(number)
            events = [e.value for e in self.substrate.get_events(block_hash)]
            if any((e["module_id"], e["event_id"]) == ("System", "Remarked") for e in events):
                for rem in block_remarks(self.substrate, block_hash):
                    f = self.check_remark(rem)
                    self.findings.append(f)
                    self.log(f"{f.verdict:<12} {f.extrinsic_id:>9} {f.kind:<12} {f.detail}")
            before = len(self.findings)
            self.check_events(number, block_hash, json.loads(json.dumps(events, default=str)), posted)
            for f in self.findings[before:]:
                self.log(f"{f.verdict:<12} {f.extrinsic_id:>9} {f.kind:<12} {f.detail}")
        before = len(self.findings)
        self.check_posted(posted)
        for f in self.findings[before:]:
            self.log(f"{f.verdict:<12} {f.extrinsic_id:>9} {f.kind:<12} {f.detail}")
        return self.findings


def summary(findings: list[Finding]) -> dict:
    counts: dict[str, int] = {}
    for f in findings:
        counts[f"{f.kind}:{f.verdict}"] = counts.get(f"{f.kind}:{f.verdict}", 0) + 1
    bad = [f for f in findings if f.verdict in ("FAIL", "FLAGGED")]
    att = [f for f in findings if f.kind in ATTEST_TYPES and f.verdict != "IGNORED"]
    counted = [f for f in att if f.verdict != "REJECTED"]
    return {"counts": counts, "attestations_counted": len(counted),
            "attestations_pass": sum(f.verdict == "PASS" for f in counted),
            "rejected": sum(f.verdict == "REJECTED" for f in findings), "failures_or_flags": len(bad),
            "verdict": "FAIL" if bad or not all(f.verdict == "PASS" for f in counted)
            else "EMPTY" if not counted else "PASS"}
