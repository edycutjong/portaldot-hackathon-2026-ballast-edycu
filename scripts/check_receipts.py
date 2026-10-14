#!/usr/bin/env python3
"""Re-fetch every receipt in evidence/ from the chain by extrinsic id, in a fresh process.

  python scripts/check_receipts.py [--profile standin-upstream] [--url ws://127.0.0.1:49944] [--regen]

For each row: block hash at that height, blake2-256 of the extrinsic at that index == the recorded tx hash,
the decoded outcome (Ok / Err(Pallet.Error)), inner multisig results and the event list. Runs are selected by
genesis hash; every `--dev` chain of one binary shares a genesis, so stand-in receipts verify only against the
node that recorded them (its persistent data dir) — a fresh or wiped dev node reports block-hash mismatches.
Drill runs also list reserve-chain transactions; `--evm-url` (default: the local anvil) re-reads each one by tx hash
(block hash + status) when the run's reserve chain id matches the endpoint's. `--regen` rewrites docs/RECEIPTS.md.
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
    ap.add_argument("--evm-url", default="http://127.0.0.1:49545", help="reserve chain to re-read drill txs from")
    ap.add_argument("--skip-evm", action="store_true", help="do not require the drill reserve-chain txs")
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
    evm_checked = evm_failed = 0
    evm_runs = [r for r in runs if r.get("evm_steps")]
    if evm_runs:
        from ballast.sepolia import ProviderError, Web3Provider, chain_id

        evm = Web3Provider("reserve", args.evm_url, timeout=5)
        try:
            evm_chain = chain_id(evm)
        except ProviderError as exc:
            evm_chain = None
            print(f"reserve chain not reachable at {args.evm_url} ({exc}); drill tx rows NOT re-checked")
        for run in evm_runs:
            if evm_chain is None or run["reserve"]["evm_chain_id"] != evm_chain:
                continue
            for row in run["evm_steps"]:
                evm_checked += 1
                err = "eth_getTransactionReceipt returned null"
                try:
                    rcpt = evm.call("eth_getTransactionReceipt", [row["tx_hash"]])
                except ProviderError as exc:
                    rcpt, err = None, str(exc)
                if rcpt is None:
                    evm_failed += 1
                    print(f"MISMATCH {run['_file']} evm {row['tx_hash']}: not found ({err})")
                    continue
                got = (int(rcpt["blockNumber"], 16), rcpt["blockHash"], int(rcpt["status"], 16))
                want = (row["block_number"], row["block_hash"], row["status"])
                if got != want:
                    evm_failed += 1
                    print(f"MISMATCH {run['_file']} evm {row['tx_hash']}: {got} != {want}")
                else:
                    print(f"ok {run['_file']} evm #{row['block_number']} {row['tx_hash'][:18]}… status {row['status']}")
        print(f"[reserve {args.evm_url}] {evm_checked - evm_failed}/{evm_checked} reserve-chain txs confirmed")
        if evm_checked == 0 and not args.skip_evm:
            print("drill runs list reserve-chain txs but none were re-checked (pass --skip-evm to accept)")
            evm_failed = 1
    if args.regen:
        print(f"rewrote {write_receipts_md()}")
    return 1 if failed or evm_failed or not checked else 0


if __name__ == "__main__":
    sys.exit(main())
