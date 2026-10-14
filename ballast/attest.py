"""Attestations — the public record the breaker is checked against. Posted by the reserve bot (key B) only.

  BALLAST/1|attest|a=<asset 1>|a2=<control>|s=<S1>|s2=<S2>|f=<0|1 frozen>|pb=<pd block>|ph=<pd hash>
           |eb=<reserve block>|eh=<reserve block hash>|r=<vault balance>
  (`heartbeat` = the same fields, posted when nothing changed for H blocks; reserves are always the FINALIZED reading)

S1, S2 and the frozen flag are read at Portaldot block `ph`; `r` is `balanceOf(vault)` at reserve-chain block `eh`.
Anyone re-reads both at those hashes (`ballast verify`). One remark per change of (S1, S2, frozen, r) plus a heartbeat
every H blocks — watchers freeze if B's nonce does not move for K = 3H blocks (I8). After each remark is INCLUDED the
same values are mirrored to ReserveOracle (`post`, I10: the mirror never leads). One-off binding remarks:
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
        oracle_rx = None
        if ok and self.oracle:  # I10: only after the remark is included
            o = oracle_mod.post(self.substrate, self.profile, self.keypair, self.oracle, snap.oracle_state(),
                                step=f"oracle_post_{kind}")
            oracle_rx = o.as_dict()
            record["oracle_receipt"] = oracle_rx
            record["oracle_ok"] = o.outcome.ok and "Revive.ContractEmitted" in o.event_names()
        self.store.attestation(kind=kind, pd_block=snap.pb, pd_hash=snap.ph, supply=str(snap.s), supply2=str(snap.s2),
                               sep_block=snap.eb, sep_hash=snap.eh, reserves=str(snap.r), remark=text,
                               remark_tx=r.extrinsic_id, oracle_tx=oracle_rx and oracle_rx["extrinsic_id"],
                               profile=self.profile.name)
        self.log("post" if ok else "post-failed", level="info" if ok else "critical", head=snap.pb, **record,
                 message=f"{kind} {r.extrinsic_id} {r.outcome}" + (f" · oracle {oracle_rx['extrinsic_id']} "
                                                                  f"{oracle_rx['outcome']['text']}" if oracle_rx else ""))
        if ok:
            self.last_key, self.last_block = snap.key(), r.block_number
            self.posts += 1
        return record

    def announce(self, watchers: list[str], threshold: int) -> list[dict]:
        out = []
        texts = [encode("watchers", t=threshold, m=",".join(watchers))]
        if self.oracle:
            texts.append(encode("evm-attester", h160=oracle_mod.attester(self.substrate, self.keypair.ss58_address,
                                                                           self.oracle), oracle=self.oracle))
        for text in texts:
            kind = text.split("|")[1]
            r = submit(self.substrate, self.profile, self.keypair, "System", "remark_with_event", {"remark": text},
                       step=f"bot_{kind}", call_label=f"System.remark_with_event(BALLAST/1|{kind})")
            rec = self.log("announce", remark=text, receipt=r.as_dict(), ok=r.outcome.ok,
                           message=f"{kind} {r.extrinsic_id} {r.outcome}")
            out.append(rec)
        return out


def run_attester(args: Any, *, profile: Any, substrate: Any, dep: Any, keypair: Any, providers: Any, store: Any) -> int:
    """`ballast bot attest`: poll the head every second, act every N blocks."""
    from .chain_profile import identify
    from .rpc import HttpRpc

    url = args.url or substrate.url
    ident = identify(HttpRpc(url), profile.name, measure=args.heartbeat_blocks is None or args.poll_blocks is None)
    h = args.heartbeat_blocks or ident.counts.heartbeat_h
    n = args.poll_blocks or ident.counts.poll_n
    log = JsonLog(args.log, profile=profile.name, chain=profile.label, breaker=dep.breaker, role="reserve-bot")
    oracle = None if args.no_oracle else (dep.oracle or {}).get("address")
    att = Attester(substrate=substrate, profile=profile, keypair=keypair, dep=dep, providers=providers, store=store,
                   log=log, oracle=oracle)
    rpc = HttpRpc(url)
    log("start", heartbeat_blocks=h, poll_blocks=n, oracle=oracle, reserve=dep.reserve["label"],
        message=f"attesting asset {dep.breaker} (+ control {dep.control}) every change + heartbeat every {h} blocks"
                f" · oracle {oracle or 'off'}")
    started, last_checked = time.time(), None
    try:
        if args.announce:
            att.announce(dep.roles["watchers"], dep.roles["M_watch"]["threshold"])
        while True:
            try:
                block_hash = rpc.call("chain_getBlockHash", [])
                number = int(rpc.call("chain_getHeader", [block_hash])["number"], 16)
            except Exception as exc:  # noqa: BLE001 — node hiccup: keep polling
                log("head-error", message=f"{type(exc).__name__}: {exc}")
                number = None
            if number is not None and (last_checked is None or number >= last_checked + n):
                last_checked = number
                try:
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
