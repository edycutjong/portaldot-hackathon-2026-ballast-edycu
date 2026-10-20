"""Attestations — the public record the breaker is checked against. Posted by the reserve bot (key B) only.

  BALLAST/1|attest|a=<asset 1>|a2=<control>|s=<S1>|s2=<S2>|f=<0|1 frozen>|pb=<pd block>|ph=<pd hash>
           |eb=<reserve block>|eh=<reserve block hash>|r=<vault balance>
  (`heartbeat` = the same fields, posted when nothing changed for H blocks; reserves are always the FINALIZED reading)

S1, S2 and the frozen flag are read at Portaldot block `ph` — the FINALIZED Portaldot head, so a reorg can never turn
a true attestation into a false FAIL; `r` is `balanceOf(vault)` at reserve-chain block `eh`.
Anyone re-reads both at those hashes (`ballast verify`). One remark per change of (S1, S2, frozen, r) plus a heartbeat
every H blocks — watchers freeze if B's nonce does not move for K = 3H blocks (I8). After each remark is INCLUDED the
same values are mirrored to ReserveOracle (`post`, I10: the mirror never leads); a failed mirror is retried every
round until it lands, and never re-posts the remark. No heartbeat while the finalized reserve read fails — deliberate:
the watchers' I8 rule then freezes (fail closed). One-off binding remarks:
  BALLAST/1|evm-attester|h160=<B's H160>|oracle=<address>   BALLAST/1|watchers|t=<threshold>|m=<ss58,ss58,…>
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from . import oracle as oracle_mod
from .bot import read_finalized
from .chain import submit
from .remarks import encode
from .watchdog import JsonLog, asset_state

ATTEST_TYPES = ("attest", "heartbeat")
MIRROR_TRIES = 5  # a mirror still failing after this many rounds is dropped (logged critical); the next remark re-arms
FIELDS = ("a", "a2", "s", "s2", "f", "pb", "ph", "eb", "eh", "r")


@dataclass(frozen=True)
class Snapshot:
    a: int
    a2: int
    s: int
    s2: int
    frozen: bool
    pb: int
    ph: str
    eb: int
    eh: str
    r: int

    def key(self) -> tuple:
        """What counts as a change: supplies, frozen flag, reserves."""
        return (self.s, self.s2, self.frozen, self.r)

    def remark(self, kind: str) -> str:
        if kind not in ATTEST_TYPES:
            raise ValueError(kind)
        return encode(kind, a=self.a, a2=self.a2, s=self.s, s2=self.s2, f=int(self.frozen), pb=self.pb, ph=self.ph,
                      eb=self.eb, eh=self.eh, r=self.r)

    def oracle_state(self) -> tuple:
        return (self.s, self.s2, self.r, self.eb, self.eh, self.pb, self.frozen)


def snapshot_from_fields(f: dict) -> Snapshot:
    return Snapshot(a=int(f["a"]), a2=int(f["a2"]), s=int(f["s"]), s2=int(f["s2"]), frozen=f["f"] == "1",
                    pb=int(f["pb"]), ph=f["ph"], eb=int(f["eb"]), eh=f["eh"], r=int(f["r"]))


def due(last_key: tuple | None, last_block: int | None, snap: Snapshot, head: int, h: int) -> str | None:
    """'attest' on the first post or any change, 'heartbeat' after H blocks without one, else None."""
    if last_key is None or snap.key() != last_key:
        return "attest"
    if last_block is not None and head - last_block >= h:
        return "heartbeat"
    return None


class Attester:
    def __init__(self, *, substrate: Any, profile: Any, keypair: Any, dep: Any, providers: Any, store: Any,
                 log: Any, oracle: str | None):
        self.substrate, self.profile, self.keypair, self.dep = substrate, profile, keypair, dep
        self.providers, self.store, self.log, self.oracle = providers, store, log, oracle
        self.last_key: tuple | None = None
        self.last_block: int | None = None
        self.posts = 0
        self.pending_mirror: tuple | None = None  # (kind, snapshot, remark extrinsic id) not yet on the oracle
        self.mirror_tries = 0

    def snapshot(self, block_hash: str, number: int) -> Snapshot | None:
        q = lambda i: self.substrate.query("Assets", "Asset", [i], block_hash=block_hash).value  # noqa: E731
        a1 = asset_state(self.dep.breaker, q(self.dep.breaker))
        a2 = asset_state(self.dep.control, q(self.dep.control))
        fin = read_finalized(self.providers, self.dep.reserve["erc20"], self.dep.reserve["vault"])
        self.store.readings(fin.readings)
        if not fin.ok:
            self.log("skip", level="warning", head=number, message=f"no attestation: {fin.reason}")
            return None
        return Snapshot(a=self.dep.breaker, a2=self.dep.control, s=a1.supply, s2=a2.supply if a2.exists else 0,
                        frozen=a1.frozen, pb=number, ph=block_hash, eb=fin.block_number, eh=fin.block_hash,
                        r=fin.reserves)

    def post(self, kind: str, snap: Snapshot) -> dict:
        text = snap.remark(kind)
        r = submit(self.substrate, self.profile, self.keypair, "System", "remark_with_event", {"remark": text},
                   step=f"bot_{kind}", call_label=f"System.remark_with_event(BALLAST/1|{kind})")
        ok = r.outcome.ok and "System.Remarked" in r.event_names()
        record = {"kind": kind, "remark": text, "receipt": r.as_dict(), "ok": ok}
        if ok:  # the remark is on chain: record it before anything else can fail
            self.last_key, self.last_block = snap.key(), r.block_number
            self.posts += 1
            self.pending_mirror = (kind, snap, r.extrinsic_id) if self.oracle else None
            self.mirror_tries = 0
        row = self.store.attestation(kind=kind, pd_block=snap.pb, pd_hash=snap.ph, supply=str(snap.s),
                                     supply2=str(snap.s2), sep_block=snap.eb, sep_hash=snap.eh, reserves=str(snap.r),
                                     remark=text, remark_tx=r.extrinsic_id if ok else None, profile=self.profile.name)
        self.log("post" if ok else "post-failed", level="info" if ok else "critical", head=snap.pb, **record,
                 message=f"{kind} {r.extrinsic_id} {r.outcome}")
        if ok and self.oracle:
            record |= self.mirror(row)
        return record

    def mirror(self, row: int | None = None) -> dict:
        """Mirror the last included remark to ReserveOracle (I10: only after inclusion). Failures stay pending and are
        retried by the next round; the remark itself is never re-posted."""
        if not self.pending_mirror:
            return {}
        kind, snap, remark_tx = self.pending_mirror
        if self.mirror_tries:  # a retry: did an earlier try land after all (e.g. submit raised after inclusion)?
            try:
                landed = oracle_mod.status(self.substrate, self.keypair.ss58_address, self.oracle)["pd_block"]
            except Exception:  # noqa: BLE001 — unknown: just try again
                landed = None
            if landed is not None and landed >= snap.pb:
                self.pending_mirror = None
                self.log("mirror", head=snap.pb, remark_tx=remark_tx, oracle_ok=True,
                         message=f"oracle already holds pdBlock {landed} >= {snap.pb}: mirror of {remark_tx} landed")
                return {"oracle_ok": True}
        if self.mirror_tries >= MIRROR_TRIES:
            self.pending_mirror = None
            self.log("mirror-dropped", level="critical", head=snap.pb, remark_tx=remark_tx,
                     message=f"oracle mirror of {remark_tx} failed {MIRROR_TRIES} times: dropped — the oracle keeps its "
                             "previous state until the next remark's mirror lands (isBacked() ages out meanwhile)")
            return {"oracle_ok": False}
        self.mirror_tries += 1
        try:
            o = oracle_mod.post(self.substrate, self.profile, self.keypair, self.oracle, snap.oracle_state(),
                                step=f"oracle_post_{kind}")
            rx = o.as_dict()
            ok = o.outcome.ok and "Revive.ContractEmitted" in o.event_names()
        except Exception as exc:  # noqa: BLE001 — a mirror failure must never stop attesting
            rx, ok = {"error": f"{type(exc).__name__}: {exc}"[:300]}, False
        if ok:
            self.pending_mirror = None
            self.store.set_oracle_tx(remark_tx, rx["extrinsic_id"])
        self.log("mirror" if ok else "mirror-failed", level="info" if ok else "warning", head=snap.pb,
                 remark_tx=remark_tx, oracle_receipt=rx, oracle_ok=ok,
                 message=f"oracle mirror of {remark_tx}: " + (f"{rx['extrinsic_id']} {rx['outcome']['text']}" if ok
                                                               else f"failed, retried next round ({rx.get('error') or rx.get('outcome')})"))
        return {"oracle_receipt": rx, "oracle_ok": ok}

    def announce(self, watchers: list[str], threshold: int) -> list[dict]:
        out = []
        try:
            texts = [encode("watchers", t=threshold, m=",".join(watchers))]
            if self.oracle:
                texts.append(encode("evm-attester", h160=oracle_mod.attester(self.substrate, self.keypair.ss58_address,
                                                                               self.oracle), oracle=self.oracle))
        except Exception as exc:  # noqa: BLE001 — e.g. a watcher set too large for one remark: attesting goes on
            out.append(self.log("announce-failed", level="critical", message=f"{type(exc).__name__}: {exc}"))
            return out
        for text in texts:
            kind = text.split("|")[1]
            try:
                r = submit(self.substrate, self.profile, self.keypair, "System", "remark_with_event", {"remark": text},
                           step=f"bot_{kind}", call_label=f"System.remark_with_event(BALLAST/1|{kind})")
                out.append(self.log("announce", remark=text, receipt=r.as_dict(), ok=r.outcome.ok,
                                    message=f"{kind} {r.extrinsic_id} {r.outcome}"))
            except Exception as exc:  # noqa: BLE001
                out.append(self.log("announce-failed", level="critical", remark=text,
                                    message=f"{kind}: {type(exc).__name__}: {exc}"))
        return out


def run_attester(args: Any, *, profile: Any, substrate: Any, dep: Any, keypair: Any, providers: Any, store: Any) -> int:
    """`ballast bot attest`: poll the head every second, act every N blocks."""
    from .chain_profile import identify
    from .rpc import node_rpc

    url = args.url or substrate.url
    ident = identify(node_rpc(url), profile.name, measure=args.heartbeat_blocks is None or args.poll_blocks is None)
    h = args.heartbeat_blocks or ident.counts.heartbeat_h
    n = args.poll_blocks or ident.counts.poll_n
    log = JsonLog(args.log, profile=profile.name, chain=profile.label, breaker=dep.breaker, role="reserve-bot")
    oracle = None if args.no_oracle else (dep.oracle or {}).get("address")
    att = Attester(substrate=substrate, profile=profile, keypair=keypair, dep=dep, providers=providers, store=store,
                   log=log, oracle=oracle)
    rpc = node_rpc(url)
    log("start", heartbeat_blocks=h, poll_blocks=n, oracle=oracle, reserve=dep.reserve["label"],
        message=f"attesting asset {dep.breaker} (+ control {dep.control}) every change + heartbeat every {h} blocks"
                f" · oracle {oracle or 'off'}")
    started, last_checked, lag_warned = time.time(), None, False
    try:
        if args.announce:
            att.announce(dep.roles["watchers"], dep.roles["M_watch"]["threshold"])
        while True:
            try:
                block_hash = rpc.call("chain_getFinalizedHead", [])  # L2: attest finalized state only
                number = int(rpc.call("chain_getHeader", [block_hash])["number"], 16)
            except Exception as exc:  # noqa: BLE001 — node hiccup: keep polling
                log("head-error", message=f"{type(exc).__name__}: {exc}")
                number = None
            try:  # heartbeats ride on finality: a lag near K = 3H would trip I8 — say so once per episode
                best = int(rpc.call("chain_getHeader", [])["number"], 16)
                lagging = number is not None and best - number > h
                if lagging and not lag_warned:
                    log("finality-lag", level="warning", head=number,
                        message=f"finalized head #{number} is {best - number} blocks behind best #{best} (> H={h})")
                lag_warned = lagging
            except Exception:  # noqa: BLE001, S110 — advisory only: never skips an attestation round
                pass
            if number is not None and (last_checked is None or number >= last_checked + n):
                last_checked = number
                try:
                    att.mirror()  # a mirror that failed last round goes first (I10 order is kept: remark already in)
                    snap = att.snapshot(block_hash, number)
                    kind = due(att.last_key, att.last_block, snap, number, h) if snap else None
                    if kind:
                        att.post(kind, snap)
                except Exception as exc:  # noqa: BLE001 — a failed round is logged; the next poll retries
                    log("error", level="critical", head=number, message=f"{type(exc).__name__}: {exc}")
            if args.max_posts and att.posts >= args.max_posts:
                log("stop", message=f"{att.posts} posts")
                return 0
            if args.max_seconds and time.time() - started > args.max_seconds:
                log("stop", message=f"max {args.max_seconds}s reached")
                return 0
            time.sleep(1.0)
    except KeyboardInterrupt:
        log("stop", message="interrupted")
        return 0
    finally:
        log.close()
        store.close()
