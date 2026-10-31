#!/usr/bin/env python3
"""ReserveOracle v2 trip() drill: deploy, post a backed status, a non-watcher's trip refused, a watcher's trip, a
stale unfrozen post refused, a later post clears it.

  python scripts/trip_drill.py [--profile standin-upstream] [--url ws://127.0.0.1:49944]

Runs on the stand-in by default (labelled NOT V3). On v3 it needs --allow-v3: the v2 deploy's storage deposit is the
largest single cost there (v1 measured 138.53 tPOT for 1,818 bytes of initcode; v2 is 2,960 bytes), so it is a
human-funded step. The posted values are a drill status (S1 = S2 = 50.00, reserves 100.00) — the oracle mirrors
whatever B attests; nothing here reads a reserve chain. Evidence: evidence/oracle-trip-<profile>-<UTC>.json.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ballast.chain import connect, ensure_connected, submit  # noqa: E402
from ballast.chain_profile import ProfileError, identify  # noqa: E402
from ballast.config import load_chain_config  # noqa: E402
from ballast.drill import forge_build, source_pin  # noqa: E402
from ballast.keys import keypair  # noqa: E402
from ballast.oracle import deploy, initcode, is_backed, post, status, trip, tripped_block, watcher_list  # noqa: E402
from ballast.receipts import write_receipts_md  # noqa: E402
from ballast.revive import eth_address  # noqa: E402
from ballast.roles import JUDGE_URI, Deployment  # noqa: E402
from ballast.rpc import node_rpc  # noqa: E402
from ballast.runlog import Run  # noqa: E402

S1 = S2 = 50_000_000
MAX_AGE = 3600
SEP_HASH = "0x" + "00" * 31 + "01"  # drill status: no reserve chain is read here


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config")
    ap.add_argument("--profile")
    ap.add_argument("--url")
    ap.add_argument("--allow-v3", action="store_true", help="spend real tPOT on the v2 deploy (human-funded)")
    args = ap.parse_args()
    try:
        cfg = load_chain_config(args.config, profile=args.profile, url=args.url)
        ident = identify(node_rpc(cfg.url), cfg.profile.name, measure=False)
        dep = Deployment.load(ident.profile.name)
    except (ProfileError, OSError, ValueError) as exc:
        print(f"trip_drill: {exc}", file=sys.stderr)
        return 2
    profile = ident.profile
    if not profile.is_standin and not args.allow_v3:
        print("trip_drill: a real chain needs --allow-v3 (the v2 deploy deposit is human-funded)", file=sys.stderr)
        return 2
    print(ident.banner())
    forge_build()
    substrate = connect(profile, cfg.url)
    keys = {"B": keypair(profile, "//BallastB"), "W1": keypair(profile, "//BallastW1"),
            "W2": keypair(profile, "//BallastW2"), "Judge": keypair(profile, JUDGE_URI)}
    role_of = {k.ss58_address: f"{name} ({'reserve bot' if name == 'B' else 'watcher' if name[0] == 'W' else 'not a watcher'})"
               for name, k in keys.items()}
    h160 = {name: eth_address(substrate, k.ss58_address) for name, k in keys.items()}
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    run = Run("oracle-trip", {**ident.as_dict(), "url": cfg.url}, role_of, asset_id=dep.breaker,
              reserve={"label": "none — the oracle mirrors B's attestation; this drill posts a fixed drill status"},
              h160=h160, source=source_pin() | {"ReserveOracle_initcode_sha256": hashlib.sha256(initcode()).hexdigest(),
                                                "ReserveOracle_initcode_bytes": len(initcode())})

    def send_ok(name: str, expected: str, r, ok: bool, events=()):
        return run.step(name, expected, r, ok, events)

    try:
        for name in ("B", "W1", "W2", "Judge"):
            ensure_connected(substrate)
            if not substrate.query("Revive", "OriginalAccount", [h160[name]]).value:
                r = submit(substrate, profile, keys[name], "Revive", "map_account", {}, step=f"map_{name.lower()}")
                send_ok(f"{name} maps its account in Revive", "Ok", r, r.outcome.ok)
        r, contract, attester = deploy(substrate, profile, keys["B"], watchers=[h160["W1"], h160["W2"]],
                                       step="deploy_oracle_v2")
        send_ok("B deploys ReserveOracle v2 (attester = B, watchers = W1, W2)", "Ok + Revive.Instantiated", r,
                r.outcome.ok and contract is not None, ("Revive.Instantiated",))
        if not contract:
            raise RuntimeError("no Revive.Instantiated event")
        run["oracle"] = {"address": contract, "attester": attester, "version": "v2 (trip)",
                         "deploy_extrinsic": r.extrinsic_id}
        run.check("watchers() == [W1, W2] H160", watcher_list(substrate, keys["B"].ss58_address, contract),
                  [h160["W1"].lower(), h160["W2"].lower()], r.block_hash)

        head = substrate.get_block_number(None)
        r = post(substrate, profile, keys["B"], contract, (S1, S2, S1 + S2, 1, SEP_HASH, head, False), step="post_backed")
        send_ok(f"B posts a backed drill status (pdBlock #{head})", "Ok + Revive.ContractEmitted", r, r.outcome.ok,
                ("Revive.ContractEmitted",))
        run.check("isBacked(3600) after the backed post", is_backed(substrate, keys["B"].ss58_address, contract, MAX_AGE),
                  True, r.block_hash)

        r = trip(substrate, profile, keys["Judge"], contract, step="trip_judge")
        send_ok("Judge (not a listed watcher) calls trip()", "Err (NotWatcher revert)", r, not r.outcome.ok)
        run.check("isBacked(3600) unchanged after the refused trip",
                  is_backed(substrate, keys["B"].ss58_address, contract, MAX_AGE), True, r.block_hash)

        r = trip(substrate, profile, keys["W1"], contract, step="trip_w1")
        send_ok("W1 (listed watcher) calls trip()", "Ok + Revive.ContractEmitted (Tripped)", r, r.outcome.ok,
                ("Revive.ContractEmitted",))
        tb = tripped_block(substrate, keys["B"].ss58_address, contract, r.block_hash)
        run.check("trippedBlock() == the trip extrinsic's Portaldot block (Revive block.number)", tb, r.block_number,
                  r.block_hash)
        st = status(substrate, keys["B"].ss58_address, contract, r.block_hash)
        run.check("status().frozen after the trip", st["frozen"], True, r.block_hash)
        run.check("status().reserves / pdBlock unchanged by the trip", [st["reserves"], st["pd_block"]],
                  [S1 + S2, head], r.block_hash)
        run.check("isBacked(3600) after the trip", is_backed(substrate, keys["B"].ss58_address, contract, MAX_AGE),
                  False, r.block_hash)

        r = post(substrate, profile, keys["B"], contract, (S1, S2, S1 + S2, 2, SEP_HASH, tb, False), step="post_stale")
        send_ok(f"B posts frozen=false with pdBlock = trippedBlock #{tb} (a reading not after the trip)",
                "Err (TripNotCleared revert)", r, not r.outcome.ok)
        run.check("isBacked(3600) still false", is_backed(substrate, keys["B"].ss58_address, contract, MAX_AGE),
                  False, r.block_hash)

        later = substrate.get_block_number(None)
        if later <= tb:
            raise RuntimeError(f"head #{later} not past the trip #{tb}")
        r = post(substrate, profile, keys["B"], contract, (S1, S2, S1 + S2, 3, SEP_HASH, later, False), step="post_clear")
        send_ok(f"B posts frozen=false with pdBlock #{later} > trippedBlock", "Ok + Revive.ContractEmitted", r,
                r.outcome.ok, ("Revive.ContractEmitted",))
        run.check("isBacked(3600) after a post from after the trip",
                  is_backed(substrate, keys["B"].ss58_address, contract, MAX_AGE), True, r.block_hash)
    except Exception as exc:  # noqa: BLE001 — keep every receipt that landed
        run["error"] = f"{type(exc).__name__}: {exc}"
        traceback.print_exc()
    run.finish(f"oracle-trip-{profile.name}-{stamp}.json")
    write_receipts_md()
    return 0 if run["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
