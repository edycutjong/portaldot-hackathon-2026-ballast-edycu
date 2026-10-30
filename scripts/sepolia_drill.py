#!/usr/bin/env python3
"""The breaker drill against a REAL Sepolia ReserveVault, with the real finality wait.

  python scripts/sepolia_drill.py [--vault 0x…] [--drain-pct 30]

Chain side: the v3 role-split deployment (deployments/v3.json; asset 4401 breaker + 4402 control). Reserve side:
Ethereum Sepolia — a ReserveVault deployed here, holding exactly 100.00 Circle test USDC. The Sepolia key is read from
$SEPOLIA_DEPLOYER_KEY (a testnet-only key, ~/.config/ballast/sepolia.env) and is never printed or written.

  0. level: S1 + S2 must equal the 100.00 deposit — burn any surplus of asset 4401 through M_admin (A proposes, A2 executes)
  1. deploy ReserveVault(Circle USDC) on Sepolia, deposit 100.00 -> wait for Sepolia FINALITY past the deposit
  2. write deployments/v3-sepolia.json (same roles as v3.json, reserve = the Sepolia vault; providers = defaults)
  3. W1 and W2 start as two processes against Sepolia (publicnode + tenderly), both report level
  4. the vault owner releases N% -> a watcher freezes asset 4401 on V3 through M_watch (reason remark in the same tx)
  5. judge transfer refused · W1's thaw through M_watch refused (NoPermission)
  6. owner re-deposits -> A proposes thaw (M_admin) -> bot refuses: finality has not reached the drain / re-deposit
  7. wait for Sepolia finality past the re-deposit -> bot co-signs -> AssetThawed -> judge transfer succeeds
  8. every Sepolia tx is re-read from BOTH providers at / below the finalized head
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ballast.chain import connect, ensure_connected, submit  # noqa: E402
from ballast.chain_profile import ProfileError, identify  # noqa: E402
from ballast.config import load_chain_config  # noqa: E402
from ballast.drill import artifact, epoch, forge_build, read_log, source_pin  # noqa: E402
from ballast.keys import keypair  # noqa: E402
from ballast.multisig_ops import call_hash, pending  # noqa: E402
from ballast.receipts import write_receipts_md  # noqa: E402
from ballast.roles import Deployment, audit_team  # noqa: E402
from ballast.rpc import node_rpc  # noqa: E402
from ballast.runlog import Run  # noqa: E402
from ballast.sepolia import SEPOLIA_CHAIN_ID, SEPOLIA_PROVIDERS, SEPOLIA_USDC  # noqa: E402
from ballast.watchdog import asset_state, parse_remark  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PROFILE = "v3"
ONE = 10 ** 6  # Circle test USDC, 6 decimals; the V3 assets use 6 as well
DEPOSIT = 100 * ONE
MANIFEST = "deployments/v3-sepolia.json"
FINALITY_TIMEOUT = 45 * 60


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--vault", help="reuse an already deployed + funded Sepolia vault (resume)")
    ap.add_argument("--drain-pct", type=int, default=30)
    ap.add_argument("--timeout", type=float, default=240.0, help="max seconds to wait for the freeze")
    args = ap.parse_args()
    from eth_account import Account
    from web3 import HTTPProvider, Web3

    key = os.environ.get("SEPOLIA_DEPLOYER_KEY")
    if not key:
        print("sepolia_drill: load ~/.config/ballast/sepolia.env into the environment first", file=sys.stderr)
        return 2
    acct = Account.from_key(key)
    del key
    try:
        cfg = load_chain_config(None, profile=PROFILE, url=None)
        ident = identify(node_rpc(cfg.url), cfg.profile.name, measure=False)
        v3 = Deployment.load(PROFILE)
    except (ProfileError, OSError, ValueError) as exc:
        print(f"sepolia_drill: {exc}", file=sys.stderr)
        return 2
    profile = ident.profile
    if profile.name != PROFILE or v3.genesis_hash != ident.facts.genesis_hash:
        print("sepolia_drill: this drill runs on the v3 profile only", file=sys.stderr)
        return 2
    print(ident.banner())
    substrate = connect(profile, cfg.url)
    rm = v3.role_map()
    keys = {n: keypair(profile, u) for n, u in (("A", "//BallastA"), ("A2", "//BallastA2"), ("W1", "//BallastW1"),
                                                 ("Judge", "//BallastJudge//roles"), ("Peer", "//BallastPeer//roles"))}
    judge, peer = keys["Judge"].ss58_address, keys["Peer"].ss58_address
    role_of = {rm.a: "A (operator)", rm.a2: "A2 (cold key)", rm.b: "B (reserve bot)", rm.watchers[0]: "W1 (watcher)",
               rm.watchers[1]: "W2 (watcher)", judge: "Judge", peer: "Peer"}
    forge_build()
    providers = [Web3(HTTPProvider(url, request_kwargs={"timeout": 20})) for _, url in SEPOLIA_PROVIDERS]
    names = [n for n, _ in SEPOLIA_PROVIDERS]
    w3 = providers[1]  # tenderly: archive depth + finalized tag
    for n, p in zip(names, providers):
        if p.eth.chain_id != SEPOLIA_CHAIN_ID:
            print(f"sepolia_drill: provider {n} is not Sepolia", file=sys.stderr)
            return 2
    usdc_abi = artifact("MockUSDC")[0]  # transfer/balanceOf only: the ERC-20 surface
    usdc = w3.eth.contract(address=SEPOLIA_USDC, abi=usdc_abi)
    vault_abi, vault_bin = artifact("ReserveVault")
    owner = acct.address
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    stem = f"sepolia-drill-{stamp}"
    run = Run("sepolia-drill", {**ident.as_dict(), "url": cfg.url}, role_of, asset_id=v3.breaker,
              assets={"breaker": v3.breaker, "control": v3.control, "decimals": v3.decimals}, roles=v3.roles,
              reserve={"label": "Sepolia", "evm_chain_id": SEPOLIA_CHAIN_ID, "erc20": SEPOLIA_USDC, "owner": owner,
                       "providers": names}, deployment=MANIFEST, decisions=[], source=source_pin(),
              watchers_note="W1 and W2 run as two processes on ONE machine (W2 on GitHub Actions is a later phase)")
    base = [sys.executable, "-m", "ballast.cli", "--profile", PROFILE, "--url", cfg.url]
    db = Path(tempfile.gettempdir()) / f"ballast-{stem}.db"
    tx_log: list[dict] = []

    def cli(*argv: str, timeout: float = 240) -> tuple[int, dict]:
        p = subprocess.run(base + list(argv), cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        lines = [ln for ln in p.stdout.splitlines() if ln.startswith("{")]
        if not lines:
            raise RuntimeError(f"`ballast {' '.join(argv)}` exited {p.returncode} without JSON: {p.stderr[-600:]}")
        return p.returncode, json.loads(lines[-1])

    def bot(*argv: str) -> tuple[int, dict]:
        rc, out = cli("bot", *argv, "--deployment", MANIFEST, "--db", str(db))
        fin = out.get("finalized", {})
        run["decisions"].append({"command": "ballast bot " + " ".join(argv), "decision": out["decision"],
                                 "reason": out["reason"], "exit": rc, "finalized_block": fin.get("block_number"),
                                 "finalized_reserves": fin.get("reserves"), "state": out.get("state"),
                                 "freeze": out.get("freeze"), "call_hash": out.get("call_hash"),
                                 "executed": (out.get("receipt") or {}).get("extrinsic_id")})
        print(f"     bot: {out['decision']} — {out['reason']}")
        return rc, out

    def state(block_hash: str | None = None) -> dict:
        ensure_connected(substrate)
        q = lambda i: substrate.query("Assets", "Asset", [i], block_hash=block_hash).value  # noqa: E731
        d1, d2 = q(v3.breaker), q(v3.control)
        return {"s1": d1["supply"], "s2": d2["supply"], "frozen": asset_state(v3.breaker, d1).frozen,
                "status": d1["status"], "team": audit_team(d1, rm.breaker_team())}

    def finalized(p=w3) -> int:
        return p.eth.get_block("finalized")["number"]

    def send(name: str, fn, **extra) -> dict:
        """Sign + send one Sepolia tx from the owner key; the row is the receipt re-read from the chain."""
        tx = fn.build_transaction({"from": owner, "nonce": w3.eth.get_transaction_count(owner, "pending"),
                                   "chainId": SEPOLIA_CHAIN_ID})
        tx["gas"] = int(w3.eth.estimate_gas(tx) * 1.3)
        h = w3.eth.send_raw_transaction(acct.sign_transaction(tx).raw_transaction)
        rcpt = w3.eth.wait_for_transaction_receipt(h, timeout=180)
        row = run.evm_step({"name": name, "expected": "status 1", "as_expected": rcpt["status"] == 1, "counted": True,
                            "chain": "Sepolia", "tx_hash": rcpt["transactionHash"].to_0x_hex(),
                            "block_number": rcpt["blockNumber"], "block_hash": rcpt["blockHash"].to_0x_hex(),
                            "status": rcpt["status"], "from": rcpt["from"], "to": rcpt["to"],
                            "contract": rcpt["contractAddress"], "gas_used": rcpt["gasUsed"],
                            "fee_wei": rcpt["gasUsed"] * rcpt["effectiveGasPrice"], **extra})
        tx_log.append(row)
        return row

    def wait_finality(block: int, why: str) -> dict:
        """Poll BOTH providers until each one's finalized head is >= `block`. The measured wait is evidence."""
        t0 = time.time()
        fin = None
        while time.time() - t0 < FINALITY_TIMEOUT:
            fin = [finalized(p) for p in providers]
            if min(fin) >= block:
                break
            time.sleep(20)
        else:
            raise RuntimeError(f"Sepolia finality did not reach #{block} within {FINALITY_TIMEOUT} s: {fin}")
        rec = {"why": why, "target_block": block, "finalized_heads": dict(zip(names, fin)),
               "waited_s": round(time.time() - t0, 1)}
        run.data.setdefault("finality_waits", []).append(rec)
        print(f"     finality: {why}: target #{block}, finalized {rec['finalized_heads']} after {rec['waited_s']} s")
        return rec

    watchers: list[subprocess.Popen] = []
    try:
        st0 = state()
        if st0["frozen"]:
            raise RuntimeError("asset 4401 is frozen: thaw it first")
        run.check("asset 4401 team == role map before the drill (ARMED)", st0["team"], [], "head")
        eth0 = w3.eth.get_balance(owner)
        usdc0 = usdc.functions.balanceOf(owner).call()
        run.note("owner before", {"address": owner, "eth_wei": eth0, "usdc": usdc0})
        run.check("owner holds >= 100.00 test USDC and gas", usdc0 >= DEPOSIT and eth0 > 10 ** 16, True, "sepolia latest")

        # 0. Level S1 + S2 to the 100.00 deposit.
        surplus = st0["s1"] + st0["s2"] - DEPOSIT
        if surplus < 0:
            raise RuntimeError(f"S1 + S2 = {(st0['s1'] + st0['s2']) / ONE} is below the 100.00 deposit: mint is a later row")
        if surplus > 0:
            from ballast.bot import operator_accounts

            _, m_admin = operator_accounts(v3, substrate.ss58_format or 42)
            burn = substrate.compose_call(call_module="Assets", call_function="burn",
                                          call_params={"id": v3.breaker, "who": judge, "amount": surplus})
            r = m_admin.propose(substrate, profile, keys["A"], burn, step="level_burn_propose",
                                label=f"Assets.burn({surplus / ONE:.2f} of the judge's S1)")
            run.step(f"A proposes burning the {surplus / ONE:.2f} S1 surplus from the judge through M_admin (level to 100.00)",
                     "Ok + Multisig.NewMultisig", r, r.outcome.ok and "Multisig.NewMultisig" in r.event_names(),
                     ("Multisig.NewMultisig",))
            op = pending(substrate, m_admin.address, call_hash(burn))
            r = m_admin.execute(substrate, profile, keys["A2"], burn, op, step="level_burn_execute",
                                label="Assets.burn")
            run.step("cold key A2 co-signs: the burn executes (S1 + S2 == 100.00)", "Ok + inner Ok + Assets.Burned", r,
                     r.outcome.ok and all(o.ok for o in r.inner) and "Assets.Burned" in r.event_names(),
                     ("Multisig.MultisigExecuted", "Assets.Burned"))
        st0 = state()
        run.check("S1 + S2 == 100.00 before the deposit", st0["s1"] + st0["s2"], DEPOSIT, "head")

        # 1. Deploy + deposit on Sepolia, then wait for finality.
        if args.vault:
            vault_addr = Web3.to_checksum_address(args.vault)
            run.note("vault", f"resumed {vault_addr}")
        else:
            row = send("deploy ReserveVault(Circle test USDC) — owner = the Sepolia deployer",
                       w3.eth.contract(abi=vault_abi, bytecode=vault_bin).constructor(SEPOLIA_USDC))
            vault_addr = row["contract"]
            run["reserve"]["vault"] = vault_addr
            send("deposit 100.00 test USDC into the vault (plain ERC-20 transfer)",
                 usdc.functions.transfer(vault_addr, DEPOSIT), amount=DEPOSIT)
        run["reserve"]["vault"] = vault_addr
        vault = w3.eth.contract(address=vault_addr, abi=vault_abi)
        run.check("vault.owner() == the Sepolia deployer", vault.functions.owner().call(), owner, "sepolia latest")
        run.check("vault.usdc() == Circle test USDC", vault.functions.usdc().call(), SEPOLIA_USDC, "sepolia latest")
        run.check("vault.reserves() == 100.00", vault.functions.reserves().call(), DEPOSIT, "sepolia latest")
        dep_block = max([r["block_number"] for r in tx_log] or [w3.eth.block_number])
        wait_finality(dep_block, "the vault deploy + 100.00 deposit")
        for n, p in zip(names, providers):
            at = p.eth.get_block("finalized")["number"]
            c = p.eth.contract(address=vault_addr, abi=vault_abi)
            run.check(f"[{n}] vault.reserves() at the finalized head #{at} == 100.00",
                      c.functions.reserves().call(block_identifier=at), DEPOSIT, f"sepolia finalized #{at}")

        # 2. Manifest: same roles/assets as v3.json, reserve = the Sepolia vault (keyless, public data only).
        sep = Deployment(profile=PROFILE, genesis_hash=v3.genesis_hash, breaker=v3.breaker, control=v3.control,
                         decimals=v3.decimals, s2=v3.s2, roles=v3.roles,
                         reserve={"label": "Sepolia", "evm_chain_id": SEPOLIA_CHAIN_ID, "vault": vault_addr,
                                  "erc20": SEPOLIA_USDC, "custodian": owner},
                         oracle=v3.oracle, created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                         setup_evidence=f"{stem}.json")
        sep.save(ROOT / MANIFEST)

        # 3. Two watcher processes against Sepolia.
        for i, uri in ((1, "//BallastW1"), (2, "//BallastW2")):
            log = ROOT / "evidence" / f"{stem}.w{i}.jsonl"
            cmd = base + ["watch", "--breaker", str(v3.breaker), "--supply-assets", f"{v3.breaker},{v3.control}",
                          "--holder", vault_addr, "--token", SEPOLIA_USDC, "--watcher", uri,
                          "--watchers", "//BallastW1,//BallastW2", "--until-frozen",
                          "--max-seconds", str(args.timeout + 180), "--log", str(log.relative_to(ROOT))]
            watchers.append(subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        logs = [ROOT / "evidence" / f"{stem}.w{i}.jsonl" for i in (1, 2)]
        run["watchdog_logs"] = [p.name for p in logs]
        deadline = time.time() + 180
        while time.time() < deadline:
            recs = [read_log(p) for p in logs]
            if any(r["event"] == "not-armed" for rs in recs for r in rs) or any(w.poll() is not None for w in watchers):
                raise RuntimeError(f"a watcher exited early: {[[r for r in rs if r['event'] in ('not-armed', 'stop')] for rs in recs]}")
            if all(any(r["event"] == "check" and r["decision"]["action"] == "level" for r in rs) for rs in recs):
                break
            time.sleep(1)
        else:
            raise RuntimeError("watchers never both reported level")
        run.check("both watchers armed and level on the Sepolia reserve (W1, W2 processes)", True, True, "watchdog logs")

        # 4. Drain: the vault owner releases N% to itself.
        total = state()["s1"] + state()["s2"]
        amount = vault.functions.reserves().call() * args.drain_pct // 100
        drain_sent = time.time()
        drain = send(f"vault owner drains {args.drain_pct}% ({amount / ONE:.2f}) — release()",
                     vault.functions.release(owner, amount, Web3.keccak(text=stem)), amount=amount)
        drained_at = time.time()
        for w in watchers:
            try:
                w.wait(timeout=args.timeout + 200)
            except subprocess.TimeoutExpired:
                w.kill()
        recs = [read_log(p) for p in logs]
        freezes = [(i, r) for i, rs in enumerate(recs, 1) for r in rs if r["event"] == "freeze"]
        if not freezes:
            raise RuntimeError("no watcher froze asset 4401")
        who, freeze = freezes[0]
        fr = freeze["receipt"]
        remark = parse_remark(freeze["remark"])
        run.step(f"watcher W{who} freezes asset {v3.breaker} on V3 through M_watch (reason={remark.get('reason')})",
                 "Ok + inner Ok + Assets.AssetFrozen + System.Remarked", fr,
                 fr["outcome"]["ok"] and all(o["ok"] for o in fr["inner"]) and remark.get("reason") == "deficit"
                 and int(remark.get("eb", -1)) == drain["block_number"],
                 ("Assets.AssetFrozen", "System.Remarked", "Multisig.MultisigExecuted"))
        others = [r for i, rs in enumerate(recs, 1) if i != who for r in rs
                  if r["event"] in ("freeze", "freeze-raced", "freeze-failed")
                  or (r["event"] == "check" and r["decision"]["action"] == "already-frozen")]
        run.note("other watcher", f"W{3 - who} " + (
            f"saw asset {v3.breaker} already frozen at #{others[-1].get('head')} and stood down"
            if others and others[-1]["event"] == "check" else
            (f"{others[-1]['event']} at #{others[-1].get('head')}" if others else "no freeze-related record after the drain")))
        run.note("drain -> freeze included (wall clock, one machine; Sepolia reserve + V3)",
                 f"{freeze['included_at'] - drained_at:.2f} s")
        run.check("freeze remark eb == the drain's Sepolia block", remark.get("eb"), str(drain["block_number"]),
                  fr["block_hash"])
        run.check("trigger check ran after the drain was sent",
                  epoch(next(r for r in recs[who - 1] if r["event"] == "check" and r["decision"]["freeze"])["t"])
                  >= drain_sent, True, "watchdog log")
        run.check(f"asset {v3.breaker} status after the freeze", state(fr["block_hash"])["status"], "Frozen", fr["block_hash"])

        # 5. What the freeze blocks.
        ensure_connected(substrate)
        r = submit(substrate, profile, keys["Judge"], "Assets", "transfer",
                   {"id": v3.breaker, "target": peer, "amount": ONE}, step="judge_transfer_frozen")
        run.step("judge transfer 1.00 while frozen is refused", "Err(Assets.AssetNotLive)", r,
                 str(r.outcome) == "Err(Assets.AssetNotLive)")
        thaw_call = substrate.compose_call(call_module="Assets", call_function="thaw_asset",
                                           call_params={"id": v3.breaker})
        r = submit(substrate, profile, keys["W1"], "Multisig", "as_multi_threshold_1",
                   {"other_signatories": [rm.watchers[1]], "call": thaw_call}, step="watcher_thaw",
                   call_label="Multisig.as_multi_threshold_1(Assets.thaw_asset)")
        run.step("watcher W1 tries to thaw through M_watch (freezer is inert)", "Err(Assets.NoPermission)", r,
                 str(r.outcome) == "Err(Assets.NoPermission)")

        # 6. Refill; the thaw waits for Sepolia finality past the drain AND the refill.
        refill = send(f"vault owner re-deposits {amount / ONE:.2f}", usdc.functions.transfer(vault_addr, amount),
                      amount=amount)
        refilled_at = time.time()
        run.check("vault reserves (latest) back to >= S1 + S2", vault.functions.reserves().call() >= total, True,
                  "sepolia latest")
        rc, out = cli("thaw", "--deployment", MANIFEST)
        run.step("A proposes thaw_asset through M_admin (first approval)", "Ok + Multisig.NewMultisig", out["receipt"],
                 rc == 0, ("Multisig.NewMultisig",))
        rc, out = bot("cosign-thaw")
        run.check("bot refuses the thaw: Sepolia finality has not reached the drain block yet",
                  [out["decision"], out.get("freeze", {}).get("eb")], ["refused", drain["block_number"]], "bot",
                  ok=rc == 1 and "finality has not reached" in out["reason"])
        run.check("bot located the freeze (latest AssetFrozen, backward event scan) == the freeze receipt",
                  (out.get("freeze") or {}).get("extrinsic_id"), fr["extrinsic_id"], fr["block_hash"])

        # 7. Wait for REAL Sepolia finality past the re-deposit -> co-signed thaw.
        wait = wait_finality(refill["block_number"], "past the drain and the re-deposit")
        run.note("re-deposit sent -> finalized (wall clock, both providers)", f"{time.time() - refilled_at:.0f} s")
        rc, out = bot("cosign-thaw")
        if "receipt" not in out:
            raise RuntimeError(f"bot did not co-sign the thaw: {out['reason']}")
        r = out["receipt"]
        run.step("bot B co-signs the thaw: finalized Sepolia reserves >= S1 + S2 past the drain",
                 "Ok + inner Ok + Assets.AssetThawed", r, rc == 0, ("Multisig.MultisigExecuted", "Assets.AssetThawed"))
        run.check(f"asset {v3.breaker} status after the thaw", state(r["block_hash"])["status"], "Live", r["block_hash"])
        ensure_connected(substrate)
        r = submit(substrate, profile, keys["Judge"], "Assets", "transfer",
                   {"id": v3.breaker, "target": peer, "amount": ONE}, step="judge_transfer_live")
        run.step("judge transfer 1.00 after the thaw", "Ok", r, str(r.outcome) == "Ok")
        run.check("asset 4401 team unchanged (ARMED)", state()["team"], [], "head")

        # 8. Every Sepolia tx re-read from BOTH providers at / below the finalized head.
        fin = [finalized(p) for p in providers]
        ok_all = True
        for row in tx_log:
            for n, p in zip(names, providers):
                rc_ = p.eth.get_transaction_receipt(row["tx_hash"])
                ok_all &= rc_["status"] == 1 and rc_["blockNumber"] == row["block_number"] <= fin[names.index(n)]
        run.check(f"all {len(tx_log)} Sepolia txs re-read from both providers: status 1, same block, <= finalized "
                  f"{dict(zip(names, fin))}", ok_all, True, "sepolia finalized")
        run.note("owner after", {"eth_wei": w3.eth.get_balance(owner), "usdc": usdc.functions.balanceOf(owner).call(),
                                 "vault_reserves": vault.functions.reserves().call()})
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
    raise SystemExit(main())
