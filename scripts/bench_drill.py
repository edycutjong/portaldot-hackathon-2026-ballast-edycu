#!/usr/bin/env python3
"""Benchmark: N back-to-back drain -> freeze -> thaw cycles on the role-split V3 asset 4401 (local-anvil reserve).

  python scripts/bench_drill.py [--profile v3] [--n 20] [--evm-url http://127.0.0.1:49545] [--drain-pct 10]

Every iteration is one complete freeze drill against the real V3 deployment (deployments/v3.json):

  1. one watcher process (W1 on odd iterations, W2 on even ones; the other key stays idle) reports `level`
  2. the custodian drains N% of the vault (`release`) -> that watcher freezes asset 4401 through M_watch
     (drain -> freeze included, wall clock on THIS machine, is the latency)
  3. the custodian re-deposits; A proposes the thaw (M_admin), anvil finality is advanced (65 blocks), bot B co-signs
     -> AssetThawed, the asset is Live again for the next iteration

The reserve is a LOCAL anvil chain (labelled so everywhere): its finality is emulated (`anvil_mine`), so the thaw leg
says nothing about Sepolia's ~13-19 min finality. The freeze leg is the same code path as against Sepolia except for
the provider read time. Evidence: evidence/roles-bench-<profile>-<stamp>.json (a standard run: every extrinsic is a
step and is re-fetched by scripts/check_receipts.py); scripts/bench_report.py turns it into docs/BENCHMARKS.md.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ballast.chain import connect, ensure_connected  # noqa: E402
from ballast.chain_profile import ProfileError, identify  # noqa: E402
from ballast.config import load_chain_config  # noqa: E402
from ballast.drill import artifact, epoch, forge_build, read_log, source_pin  # noqa: E402
from ballast.keys import keypair  # noqa: E402
from ballast.receipts import write_receipts_md  # noqa: E402
from ballast.roles import Deployment, audit_team  # noqa: E402
from ballast.rpc import node_rpc  # noqa: E402
from ballast.runlog import Run  # noqa: E402
from ballast.sepolia import ANVIL_CHAIN_ID  # noqa: E402
from ballast.watchdog import asset_state, parse_remark  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ANVIL_FINALITY_LAG = 64


def fee_paid(receipt: dict) -> int:
    for e in receipt["events"]:
        if e["module_id"] == "TransactionPayment" and e["event_id"] == "TransactionFeePaid":
            return int(e["attributes"]["actual_fee"])
    raise RuntimeError(f"no TransactionFeePaid in {receipt['extrinsic_id']}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config")
    ap.add_argument("--profile", default="v3")
    ap.add_argument("--url")
    ap.add_argument("--evm-url", default="http://127.0.0.1:49545")
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--drain-pct", type=int, default=10)
    ap.add_argument("--timeout", type=float, default=120.0, help="max seconds to wait for each freeze")
    args = ap.parse_args()
    from web3 import HTTPProvider, Web3

    try:
        cfg = load_chain_config(args.config, profile=args.profile, url=args.url)
        ident = identify(node_rpc(cfg.url), cfg.profile.name, measure=False)
        dep = Deployment.load(ident.profile.name)
    except (ProfileError, OSError, ValueError) as exc:
        print(f"bench_drill: {exc}", file=sys.stderr)
        return 2
    profile = ident.profile
    if profile.name != "v3" or dep.genesis_hash != ident.facts.genesis_hash:
        print("bench_drill: only the v3 deployment is benchmarked (genesis must match deployments/v3.json)", file=sys.stderr)
        return 2
    w3 = Web3(HTTPProvider(args.evm_url, request_kwargs={"timeout": 10}))
    if w3.eth.chain_id != ANVIL_CHAIN_ID or dep.reserve["evm_chain_id"] != ANVIL_CHAIN_ID:
        print("bench_drill: the reserve must be the local anvil chain (31337)", file=sys.stderr)
        return 2
    print(ident.banner())
    substrate = connect(profile, cfg.url)
    rm = dep.role_map()
    judge = keypair(profile, "//BallastJudge").ss58_address
    role_of = {rm.a: "A (operator)", rm.a2: "A2 (cold key)", rm.b: "B (reserve bot)", rm.watchers[0]: "W1 (watcher)",
               rm.watchers[1]: "W2 (watcher)", judge: "Judge"}
    forge_build()
    usdc = w3.eth.contract(address=dep.reserve["erc20"], abi=artifact("MockUSDC")[0])
    vault = w3.eth.contract(address=dep.reserve["vault"], abi=artifact("ReserveVault")[0])
    custodian = dep.reserve["custodian"]
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    stem = f"roles-bench-{profile.name}-{stamp}"
    run = Run("roles-bench", {**ident.as_dict(), "url": cfg.url}, role_of, asset_id=dep.breaker,
              assets={"breaker": dep.breaker, "control": dep.control, "decimals": dep.decimals},
              roles=dep.roles, reserve=dep.reserve | {"label": dep.reserve["label"], "evm_url": args.evm_url},
              deployment=f"deployments/{profile.name}.json", decisions=[], source=source_pin(),
              bench={"iterations": [], "n_requested": args.n, "drain_pct": args.drain_pct,
                     "machine": "one machine: watcher, operator, bot and the anvil reserve all run locally; the V3 node is remote"})
    base = [sys.executable, "-m", "ballast.cli", "--profile", profile.name, "--url", cfg.url]
    db = Path(tempfile.gettempdir()) / f"ballast-{stem}.db"
    iterations = run["bench"]["iterations"]

    def cli(*argv: str, timeout: float = 180) -> tuple[int, dict]:
        p = subprocess.run(base + list(argv), cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        lines = [ln for ln in p.stdout.splitlines() if ln.startswith("{")]
        if not lines:
            raise RuntimeError(f"`ballast {' '.join(argv)}` exited {p.returncode} without JSON: {p.stderr[-600:]}")
        return p.returncode, json.loads(lines[-1])

    def bot(*argv: str) -> tuple[int, dict]:
        rc, out = cli("bot", *argv, "--db", str(db))
        run["decisions"].append({"command": "ballast bot " + " ".join(argv), "decision": out["decision"],
                                 "reason": out["reason"], "exit": rc})
        print(f"     bot: {out['decision']} — {out['reason'][:90]}")
        return rc, out

    def state(block_hash: str | None = None) -> dict:
        ensure_connected(substrate)
        q = lambda i: substrate.query("Assets", "Asset", [i], block_hash=block_hash).value  # noqa: E731
        d1, d2 = q(dep.breaker), q(dep.control)
        return {"s1": d1["supply"], "s2": d2["supply"], "frozen": asset_state(dep.breaker, d1).frozen,
                "status": d1["status"], "team": audit_team(d1, rm.breaker_team())}

    def evm(name: str, tx, **extra) -> dict:
        rcpt = w3.eth.wait_for_transaction_receipt(tx, timeout=30)
        return run.evm_step({"name": name, "expected": "status 1", "as_expected": rcpt["status"] == 1, "counted": True,
                             "chain": dep.reserve["label"], "tx_hash": rcpt["transactionHash"].to_0x_hex(),
                             "block_number": rcpt["blockNumber"], "block_hash": rcpt["blockHash"].to_0x_hex(),
                             "status": rcpt["status"], "from": rcpt["from"], "to": rcpt["to"],
                             "contract": rcpt["contractAddress"], **extra})

    def finalize() -> None:
        w3.provider.make_request("anvil_mine", [hex(ANVIL_FINALITY_LAG + 1)])

    one = 10 ** dep.decimals
    proc: subprocess.Popen | None = None
    try:
        st0 = state()
        reserves0 = vault.functions.reserves().call()
        run.check("asset 4401 team == role map before the bench (ARMED)", st0["team"], [], "head")
        run.check("level before the bench: vault reserves == S1 + S2", reserves0, st0["s1"] + st0["s2"], "head")
        if st0["frozen"]:
            raise RuntimeError("asset 4401 is frozen: thaw it first")
        for i in range(1, args.n + 1):
            who = 1 if i % 2 else 2
            uri = f"//BallastW{who}"
            log = ROOT / "evidence" / f"{stem}.i{i:02d}.jsonl"
            it: dict = {"i": i, "watcher": f"W{who}", "log": log.name, "ok": False}
            iterations.append(it)
            print(f"\n=== iteration {i}/{args.n} · watcher W{who} ===")
            cmd = base + ["watch", "--breaker", str(dep.breaker), "--supply-assets", f"{dep.breaker},{dep.control}",
                          "--holder", dep.reserve["vault"], "--token", dep.reserve["erc20"], "--watcher", uri,
                          "--watchers", "//BallastW1,//BallastW2", "--provider", f"anvil={args.evm_url}",
                          "--until-frozen", "--max-seconds", str(args.timeout), "--timeout", "3",
                          "--max-block-age", "0", "--log", str(log.relative_to(ROOT))]
            log.unlink(missing_ok=True)
            proc = subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            deadline = time.time() + 120
            while time.time() < deadline:
                recs = read_log(log)
                if any(r["event"] == "not-armed" for r in recs) or proc.poll() is not None:
                    raise RuntimeError(f"iteration {i}: watcher exited early: "
                                       f"{[r for r in recs if r['event'] in ('not-armed', 'stop')]}")
                if any(r["event"] == "check" and r["decision"]["action"] == "level" for r in recs):
                    break
                time.sleep(0.3)
            else:
                raise RuntimeError(f"iteration {i}: watcher never reported level")
            head_before = substrate.get_block_number(None)
            total = state()["s1"] + state()["s2"]
            amount = vault.functions.reserves().call() * args.drain_pct // 100
            drain_sent = time.time()
            row = evm(f"iter {i}: custodian drains {args.drain_pct}% ({amount / one:.2f}) — release()",
                      vault.functions.release(custodian, amount, Web3.keccak(text=f"{stem}-{i}")).transact({"from": custodian}),
                      amount=amount)
            drained_at = time.time()
            try:
                proc.wait(timeout=args.timeout + 30)
            except subprocess.TimeoutExpired:
                proc.kill()
            recs = read_log(log)
            freezes = [r for r in recs if r["event"] == "freeze"]
            if not freezes:
                raise RuntimeError(f"iteration {i}: the watcher did not freeze asset {dep.breaker}")
            fr = freezes[0]["receipt"]
            remark = parse_remark(freezes[0]["remark"])
            detect = next((r for r in recs if r["event"] == "check" and r["decision"]["freeze"]), None)
            ok = (fr["outcome"]["ok"] and all(o["ok"] for o in fr["inner"]) and remark.get("reason") == "deficit"
                  and int(remark.get("eb", -1)) == row["block_number"])
            run.step(f"iter {i}: watcher W{who} freezes asset {dep.breaker} through M_watch (reason={remark.get('reason')})",
                     "Ok + inner Ok + Assets.AssetFrozen + System.Remarked", fr, ok,
                     ("Assets.AssetFrozen", "System.Remarked", "Multisig.MultisigExecuted"))
            it |= {
                "drain_tx": row["tx_hash"], "drain_reserve_block": row["block_number"],
                "freeze_extrinsic": fr["extrinsic_id"], "freeze_block": fr["block_number"],
                "freeze_ok": bool(ok), "drain_to_freeze_s": round(freezes[0]["included_at"] - drained_at, 3),
                "drain_sent_to_freeze_s": round(freezes[0]["included_at"] - drain_sent, 3),
                "drain_to_detect_s": round(epoch(detect["t"]) - drained_at, 3) if detect else None,
                "v3_head_at_drain": head_before, "freeze_blocks_after_drain_head": fr["block_number"] - head_before,
                "freeze_fee_planck": fee_paid(fr), "freeze_signer": role_of.get(fr["signer"], fr["signer"]),
            }
            run.check(f"iter {i}: asset status after the freeze", state(fr["block_hash"])["status"], "Frozen", fr["block_hash"])

            # reset: refill, thaw through M_admin gated by the bot at (emulated) finality
            evm(f"iter {i}: custodian re-deposits {amount / one:.2f}",
                usdc.functions.transfer(dep.reserve["vault"], amount).transact({"from": custodian}))
            finalize()
            rc, out = cli("thaw")
            run.step(f"iter {i}: A proposes thaw_asset through M_admin (first approval)", "Ok + Multisig.NewMultisig",
                     out["receipt"], rc == 0, ("Multisig.NewMultisig",))
            rc, out = bot("cosign-thaw")
            if "receipt" not in out:
                raise RuntimeError(f"iteration {i}: bot did not co-sign the thaw: {out['reason']}")
            tr = out["receipt"]
            run.step(f"iter {i}: bot B co-signs the thaw: finalized reserves >= S1 + S2 past the drain",
                     "Ok + inner Ok + Assets.AssetThawed", tr, rc == 0, ("Multisig.MultisigExecuted", "Assets.AssetThawed"))
            st = state(tr["block_hash"])
            run.check(f"iter {i}: asset status after the thaw (Live) and level (reserves == supply)",
                      [st["status"], vault.functions.reserves().call() >= total, st["s1"] + st["s2"]],
                      ["Live", True, total], tr["block_hash"])
            it |= {"thaw_extrinsic": tr["extrinsic_id"], "ok": bool(ok) and st["status"] == "Live"}
            print(f"     drain -> freeze {it['drain_to_freeze_s']} s (detect {it['drain_to_detect_s']} s), "
                  f"{it['freeze_extrinsic']}, fee {it['freeze_fee_planck']}")
    except Exception as exc:  # noqa: BLE001 — keep every receipt that landed
        run["error"] = f"{type(exc).__name__}: {exc}"
        traceback.print_exc()
    finally:
        if proc is not None and proc.poll() is None:
            proc.terminate()
        db.unlink(missing_ok=True)
    run["bench"]["n_completed"] = sum(1 for it in iterations if it.get("ok"))
    run.finish(f"{stem}.json")
    write_receipts_md()
    return 0 if run["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
