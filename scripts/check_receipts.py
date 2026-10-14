#!/usr/bin/env python3
"""Re-fetch every receipt in evidence/ from the chain by extrinsic id, in a fresh process.

  python scripts/check_receipts.py [--profile standin-upstream] [--url ws://127.0.0.1:49944] [--regen]

For each row: block hash at that height, blake2-256 of the extrinsic at that index == the recorded tx hash,
the decoded outcome (Ok / Err(Pallet.Error)), inner multisig results and the event list. Runs are selected by
genesis hash; every `--dev` chain of one binary shares a genesis, so stand-in receipts verify only against the
node that recorded them (its persistent data dir) — a fresh or wiped dev node reports block-hash mismatches.
`--regen` rewrites docs/RECEIPTS.md from evidence/.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ballast.chain import connect  # noqa: E402
from ballast.chain_profile import ProfileError, identify  # noqa: E402
from ballast.config import load_chain_config  # noqa: E402
from ballast.receipts import load_runs, refetch, write_receipts_md  # noqa: E402
from ballast.rpc import HttpRpc, RpcError  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config")
    ap.add_argument("--profile")
    ap.add_argument("--url")
    ap.add_argument("--regen", action="store_true")
    args = ap.parse_args()

    try:
        cfg = load_chain_config(args.config, profile=args.profile, url=args.url)
        ident = identify(HttpRpc(cfg.url), cfg.profile.name, measure=False)
    except (ProfileError, RpcError, OSError, ValueError) as exc:
        print(f"check_receipts: {exc}", file=sys.stderr)
        return 2
    print(ident.banner())
    substrate = connect(ident.profile, cfg.url)
    runs = [r for r in load_runs() if r["chain"]["genesis_hash"] == ident.facts.genesis_hash]
    checked = failed = 0
    for run in runs:
        for step in run["steps"]:
            problems = refetch(substrate, step["receipt"])
            checked += 1
            rid = step["receipt"]["extrinsic_id"]
            if problems:
                failed += 1
                print(f"MISMATCH {run['_file']} {rid}: " + "; ".join(problems))
            else:
                print(f"ok {run['_file']} {rid:>9} {step['receipt']['outcome']['text']}")
    print(f"[{ident.profile.name}] {checked - failed}/{checked} receipts confirmed from {len(runs)} run(s)")
    if args.regen:
        print(f"rewrote {write_receipts_md()}")
    return 1 if failed or not checked else 0


if __name__ == "__main__":
    sys.exit(main())
