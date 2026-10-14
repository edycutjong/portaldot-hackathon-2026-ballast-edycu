#!/usr/bin/env python3
"""The breaker drill on the ROLE-SPLIT asset (asset 1), with every key in its own process.

  python scripts/role_drill.py [--profile standin-upstream] [--url ws://127.0.0.1:49944] [--drain-pct 30]

Needs deployments/<profile>.json (scripts/setup_roles.py). Reserve: the deployment's local-anvil vault — labelled
"local-anvil (not Sepolia)"; anvil's `finalized` tag is latest − 64 blocks, so "waiting for finality" is mining 65
empty blocks (`anvil_mine`), the local stand-in for Sepolia's ~13–19 min finality wait.

  1. custodian deposits 1.00 -> finality -> operator A proposes mint 1.00 (M_mint) -> bot B co-signs -> Issued
  2. A proposes 0.01 more -> bot refuses (over-mint: no MultisigExecuted) -> A cancels (deposit returned)
  3. watchers W1 and W2 start as two processes (same machine) and report level
  4. custodian drains N% (`release`) -> a watcher freezes asset 1 through M_watch (reason remark in the same tx)
  5. judge transfer refused · W1's thaw through M_watch refused (NoPermission) · mint while frozen refused (I7)
  6. custodian re-deposits -> A proposes thaw (M_admin) -> bot refuses: finality has not reached the drain block
  7. finality (anvil) -> bot co-signs -> AssetThawed -> judge transfer succeeds
The operator, the bot and the watchers run as `ballast` CLI subprocesses with their own keys; their receipts and
decisions are copied into evidence/roles-drill-<profile>-<stamp>.json.
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
from ballast.drill import artifact, epoch, forge_build, read_log, source_pin  # noqa: E402
from ballast.multisig_ops import pending  # noqa: E402
from ballast.receipts import write_receipts_md  # noqa: E402
from ballast.roles import Deployment, audit_team  # noqa: E402
from ballast.rpc import HttpRpc  # noqa: E402
from ballast.runlog import Run  # noqa: E402
from ballast.sepolia import ANVIL_CHAIN_ID  # noqa: E402
from ballast.watchdog import asset_state, parse_remark  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SUPPORTED = ("standin-upstream",)
FROZEN_TRANSFER_ERRORS = {"standin-upstream": "Err(Assets.AssetNotLive)"}
JUDGE, PEER = "//BallastJudge//roles", "//BallastPeer//roles"
ANVIL_FINALITY_LAG = 64


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config")
    ap.add_argument("--profile")
    ap.add_argument("--url")
    ap.add_argument("--evm-url", default="http://127.0.0.1:49545")
    ap.add_argument("--drain-pct", type=int, default=30)
    ap.add_argument("--timeout", type=float, default=180.0, help="max seconds to wait for the freeze")
    args = ap.parse_args()
    from web3 import HTTPProvider, Web3

    try:
        cfg = load_chain_config(args.config, profile=args.profile, url=args.url)
        ident = identify(HttpRpc(cfg.url), cfg.profile.name, measure=False)
        dep = Deployment.load(ident.profile.name)
    except (ProfileError, OSError, ValueError) as exc:
        print(f"role_drill: {exc}", file=sys.stderr)
        return 2
    profile = ident.profile
    if profile.name not in SUPPORTED or dep.genesis_hash != ident.facts.genesis_hash:
        print(f"role_drill: profile {profile.name!r} unsupported or the deployment is for another chain", file=sys.stderr)
        return 2
    w3 = Web3(HTTPProvider(args.evm_url, request_kwargs={"timeout": 10}))
    if w3.eth.chain_id != ANVIL_CHAIN_ID or dep.reserve["evm_chain_id"] != ANVIL_CHAIN_ID:
        print("role_drill: the reserve must be the local anvil chain (31337)", file=sys.stderr)
        return 2
    print(ident.banner())
    substrate = connect(profile, cfg.url)
    rm = dep.role_map()
    frozen_error = FROZEN_TRANSFER_ERRORS[profile.name]
    keys = {"W1": dev_keypair(profile, "//BallastW1"), "Judge": dev_keypair(profile, JUDGE),
            "Peer": dev_keypair(profile, PEER)}
    judge, peer = keys["Judge"].ss58_address, keys["Peer"].ss58_address
    role_of = {rm.a: "A (operator)", rm.a2: "A2 (cold key)", rm.b: "B (reserve bot)", rm.watchers[0]: "W1 (watcher)",
               rm.watchers[1]: "W2 (watcher)", judge: "Judge", peer: "Peer"}
    forge_build()
    usdc = w3.eth.contract(address=dep.reserve["token"], abi=artifact("MockUSDC")[0])
    vault = w3.eth.contract(address=dep.reserve["vault"], abi=artifact("ReserveVault")[0])
    custodian = dep.reserve["custodian"]
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    stem = f"roles-drill-{profile.name}-{stamp}"
    run = Run("roles-drill", {**ident.as_dict(), "url": cfg.url}, role_of, asset_id=dep.breaker,
              assets={"breaker": dep.breaker, "control": dep.control, "decimals": dep.decimals},
              roles=dep.roles, reserve=dep.reserve | {"label": dep.reserve["label"], "evm_url": args.evm_url},
              deployment=f"deployments/{profile.name}.json", decisions=[], source=source_pin(),
              watchers_note="W1 and W2 run as two processes on ONE machine (a watcher on separate infrastructure "
                            "is still to be recruited)")
    base = [sys.executable, "-m", "ballast.cli", "--profile", profile.name, "--url", cfg.url]
    db = Path(tempfile.gettempdir()) / f"ballast-{stem}.db"

    def cli(*argv: str, timeout: float = 180) -> tuple[int, dict]:
        p = subprocess.run(base + list(argv), cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        lines = [ln for ln in p.stdout.splitlines() if ln.startswith("{")]
        if not lines:
            raise RuntimeError(f"`ballast {' '.join(argv)}` exited {p.returncode} without JSON: {p.stderr[-600:]}")
        return p.returncode, json.loads(lines[-1])

    def bot(*argv: str) -> tuple[int, dict]:
        rc, out = cli("bot", *argv, "--db", str(db))
        fin = out.get("finalized", {})
        run["decisions"].append({"command": "ballast bot " + " ".join(argv), "decision": out["decision"],
                                 "reason": out["reason"], "exit": rc, "finalized_block": fin.get("block_number"),
                                 "finalized_reserves": fin.get("reserves"), "state": out.get("state"),
                                 "freeze": out.get("freeze"), "call_hash": out.get("call_hash"),
                                 "executed": (out.get("receipt") or {}).get("extrinsic_id")})
        print(f"     bot: {out['decision']} — {out['reason']}")
        return rc, out

    def state(block_hash: str | None = None) -> dict:
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

    def finalize(why: str) -> None:
        before = w3.eth.get_block("finalized")["number"]
        w3.provider.make_request("anvil_mine", [hex(ANVIL_FINALITY_LAG + 1)])
        after = w3.eth.get_block("finalized")["number"]
        run.data.setdefault("finality_emulation", []).append(
            {"why": why, "mined_blocks": ANVIL_FINALITY_LAG + 1, "finalized_before": before, "finalized_after": after,
             "basis": f"anvil finalized = latest - {ANVIL_FINALITY_LAG}; local stand-in for Sepolia finality"})
        print(f"     finality (anvil): finalized #{before} -> #{after} ({why})")

    def transfer(name: str, expected: str, step: str):
        r = submit(substrate, profile, keys["Judge"], "Assets", "transfer",
                   {"id": dep.breaker, "target": peer, "amount": 1_000_000}, step=step)
        run.step(name, expected, r, str(r.outcome) == expected)
        return r

    watchers: list[subprocess.Popen] = []
    try:
        st0 = state()
        reserves0 = vault.functions.reserves().call()
        run.check("asset 1 team == role map before the drill (ARMED)", st0["team"], [], "head")
        run.check("level before the drill: vault reserves == S1 + S2", reserves0, st0["s1"] + st0["s2"], "head",
                  ok=reserves0 >= st0["s1"] + st0["s2"])
        if st0["frozen"]:
            raise RuntimeError("asset 1 is frozen: thaw it first")

        # 1. Deposit 1.00, wait for finality, gated mint of 1.00.
        one = 10 ** dep.decimals
        evm("custodian receives 1.00 test token", usdc.functions.mint(custodian, one).transact({"from": custodian}))
        evm("custodian deposits 1.00 into the vault", usdc.functions.transfer(dep.reserve["vault"], one)
            .transact({"from": custodian}))
        finalize("the 1.00 deposit")
        rc, out = cli("mint", "1.00", JUDGE)
        r = out["receipt"]
        run.step("A proposes mint 1.00 to the judge through M_mint (first approval)", "Ok + Multisig.NewMultisig", r,
                 rc == 0, ("Multisig.NewMultisig",))
        rc, out = bot("cosign-mint", "1.00", JUDGE)
        if "receipt" not in out:
            raise RuntimeError(f"bot did not co-sign the covered mint: {out['reason']}")
        r = out["receipt"]
        run.step("bot B co-signs: finalized reserves cover S1 + S2 + 1.00 -> mint executes",
                 "Ok + inner Ok + Assets.Issued", r, rc == 0, ("Multisig.MultisigExecuted", "Assets.Issued"))
        st1 = state(r["block_hash"])
        run.check("S1 after the gated mint == S1 + 1.00", st1["s1"], st0["s1"] + one, r["block_hash"])

        # 2. Over-mint: refused by the bot, cancelled by the operator.
        rc, out = cli("mint", "0.01", JUDGE)
        r = out["receipt"]
        run.step("A proposes 0.01 more (reserves cover S1 + S2 exactly)", "Ok + Multisig.NewMultisig", r, rc == 0,
                 ("Multisig.NewMultisig",))
        over_hash = out["call_hash"]
        rc, out = bot("cosign-mint", "0.01", JUDGE)
        run.check("bot refuses the over-mint (exit 1, no signature)", [rc, out["decision"]], [1, "refused"], "bot",
                  ok=rc == 1 and out["decision"] == "refused" and out["reason"].startswith("over-mint"))
        mid = substrate.get_block_hash(None)
        run.check("over-mint still pending (no MultisigExecuted): approvals == [A]",
                  [role_of.get(a, a) for a in (pending(substrate, rm.m_mint, over_hash, mid).approvals)],
                  ["A (operator)"], mid)
        run.check("S1 unchanged by the refused over-mint", state(mid)["s1"], st1["s1"], mid)
        rc, out = cli("mint", "0.01", JUDGE, "--cancel")
        r = out["receipt"]
        run.step("A cancels the refused proposal (deposit returned)", "Ok + Multisig.MultisigCancelled", r, rc == 0,
                 ("Multisig.MultisigCancelled",))
        run.check("no pending over-mint after the cancel", pending(substrate, rm.m_mint, over_hash, r["block_hash"]),
                  None, r["block_hash"])

        # 3. Two watcher processes (same machine), each with its own key.
        for i, uri in ((1, "//BallastW1"), (2, "//BallastW2")):
            log = ROOT / "evidence" / f"{stem}.w{i}.jsonl"
            cmd = base + ["watch", "--breaker", str(dep.breaker), "--supply-assets", f"{dep.breaker},{dep.control}",
                          "--holder", dep.reserve["vault"], "--token", dep.reserve["token"], "--watcher", uri,
                          "--watchers", "//BallastW1,//BallastW2", "--provider", f"anvil={args.evm_url}",
                          "--until-frozen", "--max-seconds", str(args.timeout), "--timeout", "3",
                          "--max-block-age", "0", "--log", str(log.relative_to(ROOT))]
            watchers.append(subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        logs = [ROOT / "evidence" / f"{stem}.w{i}.jsonl" for i in (1, 2)]
        run["watchdog_logs"] = [p.name for p in logs]
        deadline = time.time() + 120
        while time.time() < deadline:
            recs = [read_log(p) for p in logs]
            if any(r["event"] == "not-armed" for rs in recs for r in rs) or any(w.poll() is not None for w in watchers):
                raise RuntimeError(f"a watcher exited early: {[[r for r in rs if r['event'] in ('not-armed', 'stop')] for rs in recs]}")
            if all(any(r["event"] == "check" and r["decision"]["action"] == "level" for r in rs) for rs in recs):
                break
            time.sleep(0.5)
        else:
            raise RuntimeError("watchers never both reported level")
        run.check("both watchers armed and level (W1, W2 processes)", True, True, "watchdog logs")

        # 4. Drain.
        total = state()["s1"] + state()["s2"]
        amount = vault.functions.reserves().call() * args.drain_pct // 100
        drain_sent = time.time()
        row = evm(f"custodian drains {args.drain_pct}% ({amount / one:.2f}) — release()",
                  vault.functions.release(custodian, amount, Web3.keccak(text=stem)).transact({"from": custodian}),
                  amount=amount)
        drained_at = time.time()
        for w in watchers:
            try:
                w.wait(timeout=args.timeout + 30)
            except subprocess.TimeoutExpired:
                w.kill()
        recs = [read_log(p) for p in logs]
        freezes = [(i, r) for i, rs in enumerate(recs, 1) for r in rs if r["event"] == "freeze"]
        if not freezes:
            raise RuntimeError("no watcher froze asset 1")
        who, freeze = freezes[0]
        fr = freeze["receipt"]
        remark = parse_remark(freeze["remark"])
        run.step(f"watcher W{who} freezes asset 1 through M_watch (reason={remark.get('reason')})",
                 "Ok + inner Ok + Assets.AssetFrozen + System.Remarked", fr,
                 fr["outcome"]["ok"] and all(o["ok"] for o in fr["inner"]) and remark.get("reason") == "deficit"
                 and int(remark.get("eb", -1)) == row["block_number"],
                 ("Assets.AssetFrozen", "System.Remarked", "Multisig.MultisigExecuted"))
        others = [r["event"] for i, rs in enumerate(recs, 1) if i != who for r in rs
                  if r["event"] in ("freeze", "freeze-raced", "freeze-failed")
                  or (r["event"] == "check" and r["decision"]["action"] == "already-frozen")]
        run.note("other watcher", f"W{3 - who}: {others[-1] if others else 'no record after the drain'}")
        run.note("drain -> freeze included (wall clock, one machine; local anvil + stand-in)",
                 f"{freeze['included_at'] - drained_at:.2f} s")
        run.check("freeze remark eb == the drain's reserve-chain block", remark.get("eb"), str(row["block_number"]),
                  fr["block_hash"])
        run.check("trigger check ran after the drain was sent",
                  epoch(next(r for r in recs[who - 1] if r["event"] == "check" and r["decision"]["freeze"])["t"])
                  >= drain_sent, True, "watchdog log")
        run.check("asset 1 status after the freeze", state(fr["block_hash"])["status"], "Frozen", fr["block_hash"])

        # 5. What the freeze blocks.
        transfer("judge transfer 1.00 while frozen is refused", frozen_error, "judge_transfer_frozen")
        thaw_call = substrate.compose_call(call_module="Assets", call_function="thaw_asset", call_params={"id": dep.breaker})
        r = submit(substrate, profile, keys["W1"], "Multisig", "as_multi_threshold_1",
                   {"other_signatories": [rm.watchers[1]], "call": thaw_call}, step="watcher_thaw",
                   call_label="Multisig.as_multi_threshold_1(Assets.thaw_asset)")
        run.step("watcher W1 tries to thaw through M_watch (freezer is inert)", "Err(Assets.NoPermission)", r,
                 str(r.outcome) == "Err(Assets.NoPermission)")
        rc, out = cli("mint", "0.01", JUDGE)
        run.step("A proposes a mint while frozen", "Ok + Multisig.NewMultisig", out["receipt"], rc == 0,
                 ("Multisig.NewMultisig",))
        rc, out = bot("cosign-mint", "0.01", JUDGE)
        run.check("bot refuses any mint while frozen (I7)", out["reason"][:2], "I7", "bot",
                  ok=rc == 1 and out["reason"].startswith("I7"))
        rc, out = cli("mint", "0.01", JUDGE, "--cancel")
        run.step("A cancels it", "Ok + Multisig.MultisigCancelled", out["receipt"], rc == 0,
                 ("Multisig.MultisigCancelled",))

        # 6. Re-deposit; the thaw waits for finality past the drain.
        evm(f"custodian re-deposits {amount / one:.2f}", usdc.functions.transfer(dep.reserve["vault"], amount)
            .transact({"from": custodian}))
        run.check("vault reserves (latest) back to >= S1 + S2", vault.functions.reserves().call() >= total, True,
                  "evm latest")
        rc, out = cli("thaw")
        run.step("A proposes thaw_asset through M_admin (first approval)", "Ok + Multisig.NewMultisig", out["receipt"],
                 rc == 0, ("Multisig.NewMultisig",))
        rc, out = bot("cosign-thaw")
        run.check("bot refuses the thaw: finality has not reached the drain block yet",
                  [out["decision"], out.get("freeze", {}).get("eb")], ["refused", row["block_number"]], "bot",
                  ok=rc == 1 and "finality has not reached" in out["reason"])
        run.check("bot located the freeze block by archive search == the freeze receipt's block",
                  out.get("frozen_since"), fr["block_number"], fr["block_hash"])

        # 7. Finality reached -> co-signed thaw -> transfers work again.
        finalize("past the drain and the re-deposit")
        rc, out = bot("cosign-thaw")
        if "receipt" not in out:
            raise RuntimeError(f"bot did not co-sign the thaw: {out['reason']}")
        r = out["receipt"]
        run.step("bot B co-signs the thaw: finalized reserves >= S1 + S2 past the drain",
                 "Ok + inner Ok + Assets.AssetThawed", r, rc == 0, ("Multisig.MultisigExecuted", "Assets.AssetThawed"))
        run.check("asset 1 status after the thaw", state(r["block_hash"])["status"], "Live", r["block_hash"])
        transfer("judge transfer 1.00 after the thaw", "Ok", "judge_transfer_live")
        run.check("asset 1 team unchanged (ARMED)", state()["team"], [], "head")
    except Exception as exc:  # noqa: BLE001 — keep every receipt that landed
        run["error"] = f"{type(exc).__name__}: {exc}"
        traceback.print_exc()
    finally:
        for w in watchers:
            if w.poll() is None:
                w.terminate()
        db.unlink(missing_ok=True)
    run.finish(f"{stem}.json")
    write_receipts_md()
    return 0 if run["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
