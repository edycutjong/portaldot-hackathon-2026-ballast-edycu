"""The watchdog: freeze the wrapped asset the moment its reserve is short, or when nobody can tell.

Loop (one watcher key, freeze-only):
  1. poll the Portaldot head over HTTP (no subscription) and act every N blocks;
  2. read the supply S of every backed asset (asset 1 + the control asset) and the breaker asset's status at
     that head's hash;
  3. read `balanceOf(vault)` on the reserve token from every EVM provider, each at its own `latest` block hash;
  4. decide (`decide`, pure):
       - already frozen                         -> nothing to do (idempotent, no transaction);
       - any provider reads reserves < S        -> freeze, why=deficit;
       - every provider unreachable > timeout   -> freeze, why=providers-down (fail-closed, invariant I6);
       - otherwise                              -> level (provider disagreements are logged, never ignored);
  5. freeze = ONE atomic `Utility.batch_all` signed by the watcher:
       [System.remark_with_event("BALLAST/1|freeze|…reason…"),
        Multisig.as_multi_threshold_1(other watchers, Assets.freeze_asset(breaker))]
     so the reason is on chain in the same extrinsic as the freeze, and the freezer role is the 1-of-N watcher
     multisig, never a single key. `as_multi_threshold_1` returns the wrapped call's error as its own (measured on
     standin-upstream: a watcher thaw through it fails as Err(Assets.NoPermission) — docs/RECEIPTS.md, spike step 7),
     so `batch_all` reverts the remark with a failed freeze; the receipt is still checked for Assets.AssetFrozen and
     every inner multisig result (I9). A failed freeze is logged `critical` and retried on the next poll, not N
     blocks later.
Scope: an OPERATOR watcher (freeze on either provider short; fail-closed I6). The community-watcher rule (both
providers short at the same block, no I6) is not implemented here.
Every record is one JSON line (`log`) with the chain profile and the reserve label on it.
"""

from __future__ import annotations

import json
import sys
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any

from .sepolia import (
    ANVIL_CHAIN_ID,
    SEPOLIA_CHAIN_ID,
    Comparison,
    EvmRpc,
    chain_id,
    compare,
    now_iso,
    read_all,
    token_decimals,
)

REMARK_PREFIX = "BALLAST/1"
REMARK_MAX_BYTES = 320  # our own budget for any BALLAST/1 remark (architecture: attestation format)
FAIL_CLOSED_AFTER_S = 300.0  # I6: both providers unreachable for > 5 minutes -> freeze
MAX_BLOCK_AGE_S = 300.0  # a `latest` block older than this is a failed reading (stuck cache / lagging node)
FEE_HEADROOM = 10  # the watcher key must hold ED + 10 x the freeze extrinsic's fee

LEVEL, DEFICIT, OUTAGE, FAIL_CLOSED, ALREADY_FROZEN = "level", "deficit", "outage", "fail-closed", "already-frozen"


def reserve_label(evm_chain_id: int | None) -> str:
    if evm_chain_id == SEPOLIA_CHAIN_ID:
        return "Sepolia"
    if evm_chain_id == ANVIL_CHAIN_ID:
        return "local-anvil (not Sepolia)"
    return f"EVM chain {evm_chain_id} (unrecognised)" if evm_chain_id is not None else "unknown (no provider answered)"


@dataclass(frozen=True)
class AssetState:
    asset_id: int
    exists: bool
    supply: int = 0
    frozen: bool = False
    freezer: str | None = None


def asset_state(asset_id: int, details: dict | None) -> AssetState:
    """`Assets.Asset(id)` -> state. Modern runtimes carry `status: Live|Frozen|Destroying`; spec 1002 `is_frozen`."""
    if not details:
        return AssetState(asset_id=asset_id, exists=False)
    if "status" in details:
        frozen = details["status"] == "Frozen"
    else:
        frozen = bool(details.get("is_frozen", False))
    return AssetState(asset_id=asset_id, exists=True, supply=int(details["supply"]), frozen=frozen,
                      freezer=details.get("freezer"))


@dataclass
class Decision:
    action: str
    supply: int
    reserves_min: int | None = None
    short: list[dict] = field(default_factory=list)  # provider readings below supply
    down_for_s: float | None = None
    detail: str = ""

    @property
    def freeze(self) -> bool:
        return self.action in (DEFICIT, FAIL_CLOSED)

    def as_dict(self) -> dict:
        return {
            "action": self.action,
            "freeze": self.freeze,
            "supply": str(self.supply),
            "reserves_min": None if self.reserves_min is None else str(self.reserves_min),
            "short": self.short,
            "down_for_s": self.down_for_s,
            "detail": self.detail,
        }


def decide(
    supply: int,
    frozen: bool,
    comparison: Comparison,
    outage_since: float | None,
    now: float,
    fail_closed_after: float = FAIL_CLOSED_AFTER_S,
) -> tuple[Decision, float | None]:
    """Pure decision for one check. Returns (decision, new outage_since)."""
    ok = comparison.ok
    outage_since = None if ok else (outage_since if outage_since is not None else now)
    reserves_min = comparison.min_reserves
    if frozen:
        return Decision(ALREADY_FROZEN, supply, reserves_min, detail="asset already frozen; no transaction"), outage_since
    short = comparison.short(supply)
    if short:
        worst = min(short, key=lambda r: r.reserves)
        return (
            Decision(
                DEFICIT,
                supply,
                reserves_min,
                short=[r.as_dict() for r in short],
                detail=f"{worst.provider} reads {worst.reserves} < supply {supply} at #{worst.block_number}",
            ),
            outage_since,
        )
    if not ok:
        down = round(now - outage_since, 1)
        if down > fail_closed_after:
            return Decision(FAIL_CLOSED, supply, None, down_for_s=down,
                            detail=f"every provider unreachable for {down}s > {fail_closed_after}s"), outage_since
        return Decision(OUTAGE, supply, None, down_for_s=down,
                        detail=f"every provider unreachable for {down}s (fail-closed after {fail_closed_after}s)"), outage_since
    degraded = f"; {len(comparison.failed)} provider(s) down" if comparison.failed else ""
    return Decision(LEVEL, supply, reserves_min, detail=f"reserves {reserves_min} >= supply {supply}{degraded}"), outage_since


def freeze_remark(asset_id: int, decision: Decision, providers: Sequence[str]) -> str:
    """`BALLAST/1|freeze|…` — why the watcher froze, in the same extrinsic as the freeze."""
    parts = [REMARK_PREFIX, "freeze", f"a={asset_id}", f"why={decision.action}", f"s={decision.supply}"]
    if decision.action == DEFICIT:
        worst = min(decision.short, key=lambda r: int(r["reserves"]))
        parts += [f"r={worst['reserves']}", f"p={worst['provider']}", f"eb={worst['block_number']}",
                  f"eh={worst['block_hash']}"]
    elif decision.action == FAIL_CLOSED:
        names = ",".join(providers)
        if len(names) > 120:  # user-supplied names: keep the remark within budget, never block the freeze
            names = f"{len(providers)}-providers"
        parts += [f"down={int(decision.down_for_s or 0)}s", f"p={names}"]
    else:
        raise ValueError(f"no freeze for action {decision.action!r}")
    text = "|".join(parts)
    if len(text.encode()) > REMARK_MAX_BYTES:
        raise ValueError(f"remark is {len(text.encode())} bytes > {REMARK_MAX_BYTES}")
    return text


def parse_remark(text: str) -> dict:
    """`BALLAST/1|<type>|k=v|…` -> {"type": <type>, k: v, …}. Raises on anything else."""
    parts = text.split("|")
    if len(parts) < 2 or parts[0] != REMARK_PREFIX:
        raise ValueError("not a BALLAST/1 remark")
    out = {"type": parts[1]}
    for part in parts[2:]:
        key, sep, value = part.partition("=")
        if not sep or not key:
            raise ValueError(f"bad field {part!r}")
        out[key] = value
    return out


class JsonLog:
    """One JSON object per line to a file (and a short human line to stderr)."""

    def __init__(self, path: str | None, echo: bool = True, **context: Any):
        self.path, self.echo, self.context = path, echo, context
        self._fh = open(path, "a", buffering=1) if path else None

    def __call__(self, event: str, **fields: Any) -> dict:
        record = {"t": now_iso(), "event": event, **self.context, **fields}
        if self._fh:
            self._fh.write(json.dumps(record, default=str) + "\n")
        if self.echo:
            summary = fields.get("decision", {}).get("detail") if isinstance(fields.get("decision"), dict) else None
            msg = fields.get("message") or summary or ""
            head = f" #{fields['head']}" if "head" in fields else ""
            print(f"[watchdog {self.context.get('profile', '?')}] {event}{head} {msg}".rstrip(), file=sys.stderr)
        return record

    def close(self) -> None:
        if self._fh:
            self._fh.close()


@dataclass
class WatchConfig:
    breaker_id: int
    supply_ids: list[int]
    watchers: list[str]  # SS58 of every watcher-set member
    threshold: int
    token: str
    holder: str
    poll_blocks: int
    fail_closed_after: float = FAIL_CLOSED_AFTER_S
    poll_interval_s: float = 1.0
    max_block_age_s: float | None = MAX_BLOCK_AGE_S  # None/0 = off (e.g. an instant-mining local anvil)


class Watchdog:
    """One watcher process. `substrate` submits; `head_rpc` is the plain HTTP poller; `providers` read reserves."""

    def __init__(
        self,
        *,
        substrate: Any,
        profile: Any,
        head_rpc: Any,
        keypair: Any,
        providers: Sequence[EvmRpc],
        cfg: WatchConfig,
        log: Callable[..., dict],
        clock: Callable[[], float] = time.time,
        sleep: Callable[[float], None] = time.sleep,
    ):
        self.substrate, self.profile, self.head_rpc, self.keypair = substrate, profile, head_rpc, keypair
        self.providers, self.cfg, self.log, self.clock, self.sleep = providers, cfg, log, clock, sleep
        self.outage_since: float | None = None
        self.last_checked: int | None = None
        self.freezes: list[dict] = []
        self.retry_now = False  # set by a failed freeze: check again on the next poll

    # --- reads -------------------------------------------------------------------------------------------
    def head(self) -> tuple[int, str]:
        block_hash = self.head_rpc.call("chain_getBlockHash", [])
        header = self.head_rpc.call("chain_getHeader", [block_hash])
        return int(header["number"], 16), block_hash

    def assets(self, block_hash: str) -> dict[int, AssetState]:
        ids = sorted({self.cfg.breaker_id, *self.cfg.supply_ids})
        return {
            i: asset_state(i, self.substrate.query("Assets", "Asset", [i], block_hash=block_hash).value) for i in ids
        }

    # --- preflight ---------------------------------------------------------------------------------------
    def preflight(self) -> dict:
        """The watcher must be able to freeze: the breaker's freezer is the watcher-set multisig, we are a member."""
        from .multisig import multi_address, public_key

        number, block_hash = self.head()
        states = self.assets(block_hash)
        missing = [i for i, s in states.items() if not s.exists]
        if missing:
            raise RuntimeError(f"asset(s) {missing} do not exist at #{number}")
        fmt = self.substrate.ss58_format or 42
        m_watch = multi_address(self.cfg.watchers, self.cfg.threshold, ss58_format=fmt)
        freezer = states[self.cfg.breaker_id].freezer
        if freezer is None or public_key(freezer) != public_key(m_watch):
            raise RuntimeError(f"asset {self.cfg.breaker_id} freezer is {freezer}, not the watcher set {m_watch}")
        if public_key(self.keypair.ss58_address) not in {public_key(w) for w in self.cfg.watchers}:
            raise RuntimeError("this watcher key is not in the watcher set")
        if self.cfg.threshold != 1:
            raise RuntimeError(f"threshold {self.cfg.threshold}: a watcher freezes alone (as_multi_threshold_1), "
                               "so the watcher set must be 1-of-N")
        evm_ids = {}
        for p in self.providers:
            try:
                evm_ids[p.name] = chain_id(p)
            except Exception as exc:  # noqa: BLE001 — a down provider is a reading problem, not a startup error
                evm_ids[p.name] = f"error: {exc}"
        known = {v for v in evm_ids.values() if isinstance(v, int)}
        if len(known) > 1:
            raise RuntimeError(f"providers serve different EVM chains: {evm_ids}")
        # Supply and reserves are compared raw: every backed asset must use the reserve token's decimals.
        decimals = {i: (self.substrate.query("Assets", "Metadata", [i], block_hash=block_hash).value or {}).get("decimals")
                    for i in states}
        token_dec = None
        for p in self.providers:
            try:
                token_dec = token_decimals(p, self.cfg.token)
                break
            except Exception:  # noqa: BLE001 — try the next provider
                continue
        if token_dec is not None and any(d != token_dec for d in decimals.values()):
            raise RuntimeError(f"decimals mismatch: assets {decimals} vs reserve token {token_dec}")
        # The watcher key must be able to pay for the freeze when it matters.
        fee = self.freeze_fee()
        ed = self.substrate.get_constant("Balances", "ExistentialDeposit").value
        free = self.substrate.query("System", "Account", [self.keypair.ss58_address]).value["data"]["free"]
        if free < ed + FEE_HEADROOM * fee:
            raise RuntimeError(f"watcher {self.keypair.ss58_address} holds {free}, needs >= ED {ed} + "
                               f"{FEE_HEADROOM} x freeze fee {fee}")
        meta = {"decimals": decimals.get(self.cfg.breaker_id)}
        return {
            "head": number,
            "m_watch": m_watch,
            "watcher": self.keypair.ss58_address,
            "evm_chain_ids": evm_ids,
            "reserve": reserve_label(next(iter(known)) if known else None),
            "asset_decimals": meta.get("decimals"),
            "token_decimals": token_dec if token_dec is not None else "unread (no provider answered)",
            "watcher_free": str(free),
            "freeze_fee_estimate": str(fee),
            "supplies": {str(i): str(s.supply) for i, s in states.items()},
            "frozen": states[self.cfg.breaker_id].frozen,
        }

    # --- one check ---------------------------------------------------------------------------------------
    def check(self, number: int, block_hash: str) -> dict:
        states = self.assets(block_hash)
        supply = sum(states[i].supply for i in self.cfg.supply_ids)
        frozen = states[self.cfg.breaker_id].frozen
        readings = read_all(self.providers, self.cfg.token, self.cfg.holder, "latest", self.cfg.max_block_age_s)
        comparison = compare(readings)
        decision, self.outage_since = decide(
            supply, frozen, comparison, self.outage_since, self.clock(), self.cfg.fail_closed_after
        )
        record = self.log(
            "check",
            head=number,
            head_hash=block_hash,
            supplies={str(i): str(s.supply) for i, s in states.items()},
            frozen=frozen,
            reserves=comparison.as_dict(),
            decision=decision.as_dict(),
        )
        if decision.freeze:
            self.freeze(decision, number)
        return record

    def freeze_calls(self, remark: str) -> list:
        from .multisig import other_signatories

        fmt = self.substrate.ss58_format or 42
        others = other_signatories(self.cfg.watchers, self.keypair.ss58_address, ss58_format=fmt)
        compose = self.substrate.compose_call
        return [
            compose(call_module="System", call_function="remark_with_event", call_params={"remark": remark}),
            compose(
                call_module="Multisig",
                call_function="as_multi_threshold_1",
                call_params={
                    "other_signatories": others,
                    "call": compose(call_module="Assets", call_function="freeze_asset",
                                    call_params={"id": self.cfg.breaker_id}),
                },
            ),
        ]

    def freeze_fee(self) -> int:
        """Fee estimate for the freeze extrinsic (worst-case-length remark), from the node's payment API."""
        probe = Decision(FAIL_CLOSED, 2**128 - 1, down_for_s=10**6)
        remark = freeze_remark(self.cfg.breaker_id, probe, [p.name for p in self.providers])
        batch = self.substrate.compose_call(call_module="Utility", call_function="batch_all",
                                            call_params={"calls": self.freeze_calls(remark)})
        info = self.substrate.get_payment_info(call=batch, keypair=self.keypair)
        return int(info.get("partialFee", info.get("partial_fee")))  # RPC name vs runtime-API name

    def freeze(self, decision: Decision, seen_at_head: int) -> dict | None:
        from .chain import submit

        try:
            remark = freeze_remark(self.cfg.breaker_id, decision, [p.name for p in self.providers])
        except ValueError:  # never let the reason text block the freeze
            remark = f"{REMARK_PREFIX}|freeze|a={self.cfg.breaker_id}|why={decision.action}"
        submitted_at = self.clock()
        self.log("freeze-submit", head=seen_at_head, remark=remark, message=remark)
        try:
            calls = self.freeze_calls(remark)
            r = submit(self.substrate, self.profile, self.keypair, "Utility", "batch_all", {"calls": calls},
                       step="watchdog_freeze",
                       call_label="Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]")
        except Exception as exc:  # noqa: BLE001 — logged; the next poll re-reads the asset (another watcher may have frozen it)
            self.retry_now = True
            self.log("freeze-error", level="critical", head=seen_at_head, message=f"{type(exc).__name__}: {exc}")
            return None
        included_at = self.clock()
        frozen_event = "Assets.AssetFrozen" in r.event_names()
        ok = r.outcome.ok and frozen_event and all(o.ok for o in r.inner)
        if not ok:
            self.retry_now = True
        record = self.log(
            "freeze" if ok else "freeze-failed",
            level="info" if ok else "critical",
            head=seen_at_head,
            remark=remark,
            receipt=r.as_dict(),
            submitted_at=submitted_at,
            included_at=included_at,
            message=f"{r.extrinsic_id} {r.outcome} inner={[str(o) for o in r.inner]} AssetFrozen={frozen_event}",
        )
        if ok:
            self.freezes.append(record)
        return record

    # --- loop --------------------------------------------------------------------------------------------
    def run(self, *, until_frozen: bool = False, max_seconds: float | None = None) -> int:
        """Poll the head; check every `poll_blocks` blocks. Returns 0 (stopped / frozen as asked) or 4 (timed out)."""
        started = self.clock()
        while True:
            try:
                number, block_hash = self.head()
            except Exception as exc:  # noqa: BLE001 — the Portaldot node itself is down: log, keep polling
                self.log("head-error", message=f"{type(exc).__name__}: {exc}")
                number = None
            due = self.last_checked is None or self.retry_now
            if number is not None and (due or number >= self.last_checked + self.cfg.poll_blocks):
                self.last_checked, self.retry_now = number, False
                try:
                    record = self.check(number, block_hash)
                except Exception as exc:  # noqa: BLE001
                    self.log("check-error", head=number, message=f"{type(exc).__name__}: {exc}")
                    record = None
                if until_frozen and record is not None and (record["frozen"] or self.freezes):
                    self.log("stop", head=number, message="asset frozen")
                    return 0
            if max_seconds is not None and self.clock() - started > max_seconds:
                self.log("stop", message=f"max {max_seconds}s reached")
                return 4 if until_frozen else 0
            self.sleep(self.cfg.poll_interval_s)
