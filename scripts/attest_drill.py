#!/usr/bin/env python3
"""Attestations end to end on the role-split deployment, then `ballast verify` with a negative control.

  python scripts/attest_drill.py [--profile standin-upstream] [--url ws://127.0.0.1:49944] [--heartbeat-blocks 20]

  1. the reserve bot's attester runs as its own process (key B): announces the watcher set and its EVM attester
     key, posts an attestation, and mirrors each included remark into ReserveOracle (I10)
  2. a change: the custodian deposits 1.00 (attested once final) and the operator mints 1.00 with the bot's
     co-signature (attested again)
  3. nothing changes for H blocks -> heartbeat (H here is a drill override; production H = 10 min of blocks)
  4. negative control: the judge key posts a copy of the last attestation -> `verify` must list it REJECTED
  5. `ballast verify` over the run: every B remark PASS on both chains, every oracle post matched, 1 REJECTED
Reserve: the deployment's local-anvil vault (NOT Sepolia); finality = 65 mined anvil blocks (finalized = latest − 64).
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

from ballast.chain import connect, dev_keypair, submit  # noqa: E402
from ballast.chain_profile import ProfileError, identify  # noqa: E402
from ballast.config import load_chain_config  # noqa: E402
from ballast.drill import artifact, read_log, source_pin  # noqa: E402
from ballast.receipts import write_receipts_md  # noqa: E402
from ballast.roles import JUDGE_URI as JUDGE, Deployment  # noqa: E402
from ballast.rpc import HttpRpc  # noqa: E402
from ballast.runlog import Run  # noqa: E402
from ballast.sepolia import ANVIL_CHAIN_ID  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ANVIL_FINALITY_LAG = 64


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config")
    ap.add_argument("--profile")
    ap.add_argument("--url")
    ap.add_argument("--evm-url", default="http://127.0.0.1:49545")
    ap.add_argument("--heartbeat-blocks", type=int, default=20, help="H — a drill override (production: profile H)")
    args = ap.parse_args()
    from web3 import HTTPProvider, Web3

    try:
        cfg = load_chain_config(args.config, profile=args.profile, url=args.url)
        ident = identify(HttpRpc(cfg.url), cfg.profile.name)
        dep = Deployment.load(ident.profile.name)
    except (ProfileError, OSError, ValueError) as exc:
        print(f"attest_drill: {exc}", file=sys.stderr)
        return 2
    profile = ident.profile
    w3 = Web3(HTTPProvider(args.evm_url, request_kwargs={"timeout": 10}))
    if dep.genesis_hash != ident.facts.genesis_hash or w3.eth.chain_id != ANVIL_CHAIN_ID:
        print("attest_drill: the deployment must be on this chain, with its local-anvil reserve", file=sys.stderr)
        return 2
    print(ident.banner())
    substrate = connect(profile, cfg.url)
    rm = dep.role_map()
    judge = dev_keypair(profile, JUDGE)
    role_of = {rm.a: "A (operator)", rm.b: "B (reserve bot)", judge.ss58_address: "Judge (negative control)"}
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    stem = f"roles-attest-{profile.name}-{stamp}"
    log_path = ROOT / "evidence" / f"{stem}.bot.jsonl"
    run = Run("roles-attest", {**ident.as_dict(), "url": cfg.url}, role_of, asset_id=dep.breaker,
              reserve=dep.reserve | {"evm_url": args.evm_url}, oracle=dep.oracle, source=source_pin(),
              deployment=f"deployments/{profile.name}.json", bot_log=log_path.name,
              heartbeat={"H_used": args.heartbeat_blocks, "basis": "drill override",
                         "production_H_on_this_profile": ident.counts.heartbeat_h,
                         "production_K_on_this_profile": ident.counts.heartbeat_freeze_k})
    base = [sys.executable, "-m", "ballast.cli", "--profile", profile.name, "--url", cfg.url]
    db = Path(tempfile.gettempdir()) / f"ballast-{stem}.db"
    usdc = w3.eth.contract(address=dep.reserve["erc20"], abi=artifact("MockUSDC")[0])
    custodian = dep.reserve["custodian"]

    def cli(*argv: str) -> tuple[int, dict]:
        p = subprocess.run(base + list(argv), cwd=ROOT, capture_output=True, text=True, timeout=600)
        lines = [ln for ln in p.stdout.splitlines() if ln.startswith("{")]
        if not lines:
            raise RuntimeError(f"`ballast {' '.join(argv)}` exited {p.returncode} without JSON: {p.stderr[-600:]}")
        return p.returncode, json.loads(lines[-1])

    def posts() -> list[dict]:
        return [r for r in read_log(log_path) if r["event"] in ("post", "post-failed", "announce", "mirror",
                                                                 "mirror-failed")]

    def wait_posts(n: int, why: str, timeout: float = 240) -> list[dict]:
        deadline = time.time() + timeout
        while time.time() < deadline:
            if bot.poll() is not None:
                raise RuntimeError(f"attester exited ({bot.returncode}) while waiting for {why}")
            got = [r for r in posts() if r["event"] == "post"]
            if len(got) >= n:
                return got
            time.sleep(1)
        raise RuntimeError(f"attester never posted {why} within {timeout}s")

    def evm(name: str, tx) -> None:
        rcpt = w3.eth.wait_for_transaction_receipt(tx, timeout=30)
        run.evm_step({"name": name, "expected": "status 1", "as_expected": rcpt["status"] == 1, "counted": True,
                      "chain": dep.reserve["label"], "tx_hash": rcpt["transactionHash"].to_0x_hex(),
                      "block_number": rcpt["blockNumber"], "block_hash": rcpt["blockHash"].to_0x_hex(),
                      "status": rcpt["status"], "from": rcpt["from"], "to": rcpt["to"], "contract": None})

    start = substrate.get_block_number(None)
    run["from_block"] = start
    log_path.unlink(missing_ok=True)
    bot = subprocess.Popen(base + ["bot", "attest", "--announce", "--heartbeat-blocks", str(args.heartbeat_blocks),
                                   "--poll-blocks", "2", "--max-seconds", "900", "--db", str(db),
                                   "--log", str(log_path.relative_to(ROOT))],
                           cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        first = wait_posts(1, "the first attestation")
        # 2. a change on each chain: reserves (after finality), then supply (gated mint)
        one = 10 ** dep.decimals
        evm("custodian receives 1.00 test token", usdc.functions.mint(custodian, one).transact({"from": custodian}))
        evm("custodian deposits 1.00 into the vault",
            usdc.functions.transfer(dep.reserve["vault"], one).transact({"from": custodian}))
        w3.provider.make_request("anvil_mine", [hex(ANVIL_FINALITY_LAG + 1)])
        run.note("finality (anvil)", f"mined {ANVIL_FINALITY_LAG + 1} blocks: finalized = latest − {ANVIL_FINALITY_LAG}")
        wait_posts(len(first) + 1, "the reserves change")
        rc, out = cli("mint", "1.00", JUDGE)
        run.step("A proposes mint 1.00 through M_mint", "Ok + Multisig.NewMultisig", out["receipt"], rc == 0,
                 ("Multisig.NewMultisig",))
        rc, out = cli("bot", "cosign-mint", "1.00", JUDGE, "--db", str(db))
        if "receipt" not in out:
            raise RuntimeError(f"bot refused a covered mint: {out['reason']}")
        run.step("bot B co-signs (finalized reserves cover it)", "Ok + inner Ok + Assets.Issued", out["receipt"],
                 rc == 0, ("Multisig.MultisigExecuted", "Assets.Issued"))
        changed = wait_posts(len(first) + 2, "the supply change")
        # 3. heartbeat: nothing changes for H blocks
        hb = wait_posts(len(changed) + 1, "a heartbeat", timeout=args.heartbeat_blocks * 3 * 3 + 120)[-1]
        run.check("the post after H quiet blocks is a heartbeat", hb["kind"], "heartbeat", hb["receipt"]["block_hash"])
        last_attest = hb["remark"]
        # 4. negative control, while the bot still runs
        r = submit(substrate, profile, judge, "System", "remark_with_event",
                   {"remark": last_attest.replace("|heartbeat|", "|attest|")}, step="negative_control",
                   call_label="System.remark_with_event(BALLAST/1|attest) — forged by a non-bot key")
        run.step("negative control: the judge key posts a copy of the bot's attestation", "Ok + System.Remarked "
                 "(included — verify must REJECT it)", r, r.outcome.ok and "System.Remarked" in r.event_names(),
                 ("System.Remarked",))
        forged = r.extrinsic_id
        time.sleep(4)
    except Exception as exc:  # noqa: BLE001
        run["error"] = f"{type(exc).__name__}: {exc}"
        traceback.print_exc()
        forged = None
    finally:
        if bot.poll() is None:
            bot.terminate()
            bot.wait(timeout=30)
        db.unlink(missing_ok=True)

    # The bot's own receipts (remarks + oracle posts) from its log.
    for rec in posts():
        if rec["event"] in ("mirror", "mirror-failed"):
            rx = rec.get("oracle_receipt") or {}
            if "events" in rx:
                run.step(f"bot mirrors {rec['remark_tx']} to ReserveOracle (after inclusion, I10)",
                         "Ok + Revive.ContractEmitted(Posted)", rx, bool(rec.get("oracle_ok")),
                         ("Revive.ContractEmitted",))
            else:  # failed before submission: retried by the next round
                run.note(f"oracle mirror of {rec['remark_tx']} failed before submission", rx.get("error", "?"))
            continue
        if rec["event"] == "announce":
            kind = rec["remark"].split("|")[1]
            run.step(f"bot announces {kind} ({rec['remark'][:60]}…)", "Ok + System.Remarked", rec["receipt"], rec["ok"],
                     ("System.Remarked",))
            continue
        run.step(f"bot posts {rec['kind']} (pb {rec['remark'].split('|pb=')[1].split('|')[0]})",
                 "Ok + System.Remarked", rec["receipt"], rec["event"] == "post", ("System.Remarked",))
    run["steps"].sort(key=lambda s: (s["receipt"]["block_number"], s["receipt"]["extrinsic_index"]))

    # 5. verify over the run, in a fresh process.
    if not run.data.get("error"):
        end = substrate.get_block_number(None)
        out_path = ROOT / "evidence" / f"verify-{profile.name}-{stamp}.json"
        p = subprocess.run(base + ["verify", "--from", str(start), "--to", str(end), "--json",
                                   "--out", str(out_path.relative_to(ROOT))], cwd=ROOT, capture_output=True, text=True,
                           timeout=900)
        report = json.loads(p.stdout)
        sm = report["summary"]
        run["verify"] = {"file": out_path.name, "from": start, "to": end, "exit": p.returncode, "summary": sm}
        b_posts = [s for s in run["steps"] if s["name"].startswith("bot posts")]
        mirrors = [s for s in run["steps"] if s["name"].startswith("bot mirrors")]
        rejected = [f for f in report["findings"] if f["verdict"] == "REJECTED"]
        run.check("verify exit 0 and verdict PASS", [p.returncode, sm["verdict"]], [0, "PASS"], "verify")
        run.check("every bot attestation/heartbeat PASSes on both chains", sm["attestations_pass"], len(b_posts),
                  "verify", ok=sm["attestations_pass"] == sm["attestations_counted"] == len(b_posts) > 0)
        run.check("every oracle post matches a PASSing remark (I10)", sm["counts"].get("oracle-post:OK", 0),
                  len(mirrors), "verify")
        run.check("the forged remark is listed REJECTED (not counted)", [f["extrinsic_id"] for f in rejected],
                  [forged], "verify")
        run.check("watcher-set and evm-attester announcements PASS",
                  [sm["counts"].get("watchers:PASS", 0), sm["counts"].get("evm-attester:PASS", 0)], [1, 1], "verify")
    run.finish(f"{stem}.json")
    write_receipts_md()
    return 0 if run["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
