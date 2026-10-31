#!/usr/bin/env python3
"""Governance drill on a scratch asset: announced watcher-set rotation, announced M_admin rotation, a community
watcher's freeze, the wind-down thaw, a holder's redemption.

  python scripts/governance_drill.py [--profile v3] [--url URL] [--evm-url http://127.0.0.1:49545] [--k 5] [--w 5]

Portaldot: the configured profile (v3 with the role seed files, or standin-upstream with dev keys); a FRESH scratch
breaker asset (ids from 4601 on v3), never the role-split assets 4401/4402 — the wind-down is destructive. Control
asset = the deployment's (read only; S2). Reserve: a fresh MockUSDC + ReserveVault on the LOCAL anvil chain
(labelled "local-anvil (not Sepolia)"). Drill overrides, labelled in the evidence: K (announcement age) and W
(frozen time before a wind-down) are a few blocks instead of 3 x H and ~24 h; both providers are the same anvil
under two URLs (the community rule's same-block confirmation runs, but the providers cannot disagree).

  1. A creates the scratch asset, mints S1 = 30.00 to the judge + 20.00 to the peer, hands the team to M_mint /
     M_admin / M_watch {W1, W2} (manifest deployments/<profile>-gov.json, rewritten after each rotation).
  2. Watcher rotation: A proposes freezer -> M_watch' {W1, W2, W3}; the bot refuses (no announcement), B announces,
     the bot refuses (younger than K), then co-signs after K. W1 through the OLD M_watch cannot freeze any more.
  3. Admin rotation: B announces {A, A3, B} 2-of-3 (A2 retired); the bot co-signs after K.
  4. Community watcher W3 (own process, `ballast watch --community`): with every provider down it never fails
     closed; then the custodian drains 30% and W3 freezes through M_watch' once every provider reads short at one
     pinned block. The judge's transfer is refused.
  5. Wind-down: after W blocks frozen, W3 freezes the judge's account; B posts final r = reserves / (S1 + S2); the
     bot refuses the thaw while the peer is still open, W3 freezes the peer, the bot co-signs the thaw through
     M_admin'. A community watcher then holds (`winddown-hold`) instead of re-freezing; the judge stays frozen.
  6. Redemption: the judge posts a redeem request; A proposes batch_all([thaw(judge), burn(judge, 30.00)]) through
     M_admin', the bot co-signs; the custodian releases r x 30.00 with redeemId = redeem_id(request).
Evidence: evidence/roles-governance-<profile>-<UTC>.json (+ watcher logs), docs/RECEIPTS.md.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import time
import traceback
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ballast.bot import ReserveBot  # noqa: E402
from ballast.chain import connect, ensure_connected, submit  # noqa: E402
from ballast.chain_profile import ProfileError, identify  # noqa: E402
from ballast.config import load_chain_config  # noqa: E402
from ballast.drill import UNREACHABLE, artifact, epoch, forge_build, free_asset_id, read_log, source_pin  # noqa: E402
from ballast.governance import announcement_text, final_text, holders, redeem_id, redeem_text  # noqa: E402
from ballast.keys import keypair  # noqa: E402
from ballast.multisig import multi_address, other_signatories  # noqa: E402
from ballast.multisig_ops import MultisigAccount  # noqa: E402
from ballast.receipts import EVIDENCE, write_receipts_md  # noqa: E402
from ballast.roles import DEPLOYMENTS, JUDGE_URI, Deployment, RoleMap  # noqa: E402
from ballast.rpc import node_rpc  # noqa: E402
from ballast.runlog import Run  # noqa: E402
from ballast.sepolia import ANVIL_CHAIN_ID, providers_from  # noqa: E402
from ballast.store import Store  # noqa: E402
from ballast.watchdog import asset_state  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
GOV_ASSET_FROM = {"v3": 4601, "standin-upstream": 3001}
JUDGE_HOLDS, PEER_HOLDS = 30_000_000, 20_000_000  # S1 = 50.00
DRAIN = 30_000_000  # 30% of 100.00
REDEEM_EVM = "0x90F79bf6EB2c4f870365E785982E1f101E93b906"  # anvil's public dev account #3 (the judge's EVM address)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config")
    ap.add_argument("--profile")
    ap.add_argument("--url")
    ap.add_argument("--evm-url", default="http://127.0.0.1:49545")
    ap.add_argument("--k", type=int, default=5, help="drill K: announcement age in blocks (production K = 3 x H)")
    ap.add_argument("--w", type=int, default=5, help="drill W: blocks frozen before a wind-down (production ~24 h)")
    ap.add_argument("--timeout", type=float, default=240.0, help="max seconds to wait for the community freeze")
    args = ap.parse_args()
    from web3 import HTTPProvider, Web3

    try:
        cfg = load_chain_config(args.config, profile=args.profile, url=args.url)
        ident = identify(node_rpc(cfg.url), cfg.profile.name, measure=False)
        base_dep = Deployment.load(ident.profile.name)
    except (ProfileError, OSError, ValueError) as exc:
        print(f"governance_drill: {exc}", file=sys.stderr)
        return 2
    profile = ident.profile
    if profile.name not in GOV_ASSET_FROM or base_dep.genesis_hash != ident.facts.genesis_hash:
        print(f"governance_drill: profile {profile.name!r} unsupported or the deployment is for another chain",
              file=sys.stderr)
        return 2
    w3 = Web3(HTTPProvider(args.evm_url, request_kwargs={"timeout": 10}))
    if w3.eth.chain_id != ANVIL_CHAIN_ID:
        print("governance_drill: the reserve must be the local anvil chain (31337)", file=sys.stderr)
        return 2
    print(ident.banner())
    substrate = connect(profile, cfg.url)
    fmt = substrate.ss58_format or 42
    uris = {"A": "//BallastA", "A2": "//BallastA2", "A3": "//BallastA3", "B": "//BallastB", "W1": "//BallastW1",
            "W2": "//BallastW2", "W3": "//BallastW3", "Judge": JUDGE_URI if profile.is_standin else "//BallastJudge",
            "Peer": "//BallastPeer//roles" if profile.is_standin else "//BallastPeer"}
    keys = {name: keypair(profile, uri) for name, uri in uris.items()}
    addr = {name: k.ss58_address for name, k in keys.items()}
    rm0 = RoleMap(a=addr["A"], a2=addr["A2"], b=addr["B"], watchers=(addr["W1"], addr["W2"]), ss58_format=fmt)
    m_watch2 = multi_address([addr["W1"], addr["W2"], addr["W3"]], 1, ss58_format=fmt)
    m_admin2 = multi_address([addr["A"], addr["A3"], addr["B"]], 2, ss58_format=fmt)
    role_of = {addr["A"]: "A (operator)", addr["A2"]: "A2 (cold key, rotated out)", addr["A3"]: "A3 (new admin key)",
               addr["B"]: "B (reserve bot)", addr["W1"]: "W1 (watcher)", addr["W2"]: "W2 (watcher)",
               addr["W3"]: "W3 (community watcher)", addr["Judge"]: "Judge (holder)", addr["Peer"]: "Peer (holder)",
               rm0.m_mint: "M_mint", rm0.m_admin: "M_admin", rm0.m_watch: "M_watch", m_watch2: "M_watch'",
               m_admin2: "M_admin'"}
    custodian = w3.eth.accounts[0]
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    stem = f"roles-governance-{profile.name}-{stamp}"
    run = Run("roles-governance", {**ident.as_dict(), "url": cfg.url}, role_of, decisions=[], source=source_pin(),
              reserve={"label": "local-anvil (not Sepolia)", "evm_url": args.evm_url, "custodian": custodian},
              roles=rm0.as_dict(), rotated={"M_watch'": m_watch2, "M_admin'": m_admin2, "A3": addr["A3"],
                                            "W3": addr["W3"]},
              overrides={"K": args.k, "W": args.w, "basis": "drill overrides; production K = 3 x H blocks, W ~ 24 h",
                         "providers": "one local anvil under two URLs (anvil-a 127.0.0.1, anvil-b localhost)"})
    run.note("watchers", "W1, W2 and W3 run on ONE machine; W3 plays the community watcher (no separate operator yet)")
    db = Path(tempfile.gettempdir()) / f"ballast-{stem}.db"
    manifest = DEPLOYMENTS / f"{profile.name}-gov.json"
    base = [sys.executable, "-m", "ballast.cli", "--profile", profile.name, "--url", cfg.url]
    procs: list[subprocess.Popen] = []

    def has(r, *events: str) -> bool:
        return all(e in r.event_names() for e in events)

    def compose(module: str, function: str, params: dict):
        return substrate.compose_call(call_module=module, call_function=function, call_params=params)

    def send(name: str, signer: str, module: str, function: str, params: dict, expected: str, ok_fn, *, step: str,
             events: tuple[str, ...] = (), label: str | None = None):
        ensure_connected(substrate)
        r = submit(substrate, profile, keys[signer], module, function, params, step=step, call_label=label)
        run.step(name, expected, r, ok_fn(r), events)
        return r

    def details(asset_id: int, block_hash: str | None = None) -> dict:
        return substrate.query("Assets", "Asset", [asset_id], block_hash=block_hash).value

    def wait_blocks(until: int, why: str) -> None:
        t0 = time.time()
        while substrate.get_block_number(None) < until:
            if time.time() - t0 > 600:
                raise RuntimeError(f"chain did not reach #{until} ({why})")
            time.sleep(2)
        print(f"     waited to #{until} ({why})")

    def evm(name: str, tx, **extra) -> dict:
        rcpt = w3.eth.wait_for_transaction_receipt(tx, timeout=30)
        return run.evm_step({"name": name, "expected": "status 1", "as_expected": rcpt["status"] == 1, "counted": True,
                             "chain": run["reserve"]["label"], "tx_hash": rcpt["transactionHash"].to_0x_hex(),
                             "block_number": rcpt["blockNumber"], "block_hash": rcpt["blockHash"].to_0x_hex(),
                             "status": rcpt["status"], "from": rcpt["from"], "to": rcpt["to"],
                             "contract": rcpt["contractAddress"], **extra})

    def make_bot(dep: Deployment) -> ReserveBot:
        return ReserveBot(substrate=substrate, profile=profile, keypair=keys["B"], deployment=dep,
                          providers=providers_from([f"anvil={args.evm_url}"]), store=Store(db),
                          max_finalized_age_s=None, max_latest_age_s=None, log=lambda m: print(f"     [bot] {m}"))

    def decided(command: str, out: dict) -> dict:
        run["decisions"].append({"command": command, "decision": out["decision"], "reason": out["reason"],
                                 "call_hash": out.get("call_hash"),
                                 "executed": (out.get("receipt") or {}).get("extrinsic_id")})
        print(f"     bot: {out['decision']} — {out['reason']}")
        if out.get("receipt"):
            rd = out["receipt"]
            run.step(f"bot co-signs ({command})", "Ok, executed", rd, bool(out.get("executed_ok")))
        return out

    def watcher(name: str, providers: list[str], extra: list[str], log_path: Path, timeout: float) -> subprocess.Popen:
        argv = base + ["watch", "--community", "--breaker", str(breaker), "--supply-assets", f"{breaker},{control}",
                       "--holder", vault_addr, "--token", usdc_addr, "--watcher", uris["W3"],
                       "--watchers", ",".join([addr["W1"], addr["W2"], addr["W3"]]), "--poll-blocks", "1",
                       "--poll-interval", "1", "--max-block-age", "0", "--timeout", "5", "--log", str(log_path),
                       *[a for p in providers for a in ("--provider", p)], *extra]
        print(f"     [{name}] {' '.join(argv[2:6])} … watch --community")
        p = subprocess.Popen(argv, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        procs.append(p)
        return p

    breaker = control = vault_addr = usdc_addr = None
    try:
        # --- 0. reserve + scratch asset --------------------------------------------------------------------------
        forge_build()
        usdc_abi, usdc_bin = artifact("MockUSDC")
        vault_abi, vault_bin = artifact("ReserveVault")
        control = base_dep.control
        s2 = details(control)["supply"]
        tx = w3.eth.contract(abi=usdc_abi, bytecode=usdc_bin).constructor().transact({"from": custodian})
        usdc_addr = evm("deploy MockUSDC (test-only token)", tx)["contract"]
        usdc = w3.eth.contract(address=usdc_addr, abi=usdc_abi)
        tx = w3.eth.contract(abi=vault_abi, bytecode=vault_bin).constructor(usdc_addr).transact({"from": custodian})
        vault_addr = evm("deploy ReserveVault(usdc), owner = custodian", tx)["contract"]
        vault = w3.eth.contract(address=vault_addr, abi=vault_abi)
        evm(f"deposit S1 + S2 = {(JUDGE_HOLDS + PEER_HOLDS + s2) / 1e6:.2f}",
            usdc.functions.mint(vault_addr, JUDGE_HOLDS + PEER_HOLDS + s2).transact({"from": custodian}))
        run["reserve"] |= {"vault": vault_addr, "usdc": usdc_addr}

        ed = substrate.get_constant("Balances", "ExistentialDeposit").value
        const = lambda pallet, name: substrate.get_constant(pallet, name).value  # noqa: E731
        per_asset = (const("Assets", "AssetDeposit") + const("Assets", "MetadataDepositBase")
                     + 2 * len("pUSDC-gov") * const("Assets", "MetadataDepositPerByte"))
        msig = const("Multisig", "DepositBase") + 3 * const("Multisig", "DepositFactor")
        free = lambda who: substrate.query("System", "Account", [who]).value["data"]["free"]  # noqa: E731
        want = ((addr["A"], per_asset + msig + 20 * ed), (addr["W1"], 5 * ed), (addr["W3"], 10 * ed),
                (addr["Judge"], 5 * ed), (addr["Peer"], 3 * ed), (addr["B"], 20 * ed))
        fund = [compose("Balances", "transfer_keep_alive", {"dest": who, "value": amount - free(who)})
                for who, amount in want if free(who) < amount]
        run.note("funding", {"wanted": {role_of.get(w, w): str(a) for w, a in want},
                             "topped_up": len(fund), "ed": str(ed), "multisig_deposit": str(msig)})
        if fund:
            funder = keypair(profile, "//Alice")
            ensure_connected(substrate)
            r = submit(substrate, profile, funder, "Utility", "batch_all", {"calls": fund}, step="fund",
                       call_label=f"Utility.batch_all[{len(fund)} x Balances.transfer_keep_alive]")
            run.step("funder tops up the accounts below their working balance", "Ok", r, r.outcome.ok)
        breaker = free_asset_id(substrate, GOV_ASSET_FROM[profile.name])
        run["asset_id"] = breaker
        run["assets"] = {"breaker": breaker, "control": control, "decimals": base_dep.decimals}
        send(f"A creates scratch asset {breaker}", "A", "Assets", "create",
             {"id": breaker, "admin": addr["A"], "min_balance": 1}, "Ok + Assets.Created",
             lambda r: r.outcome.ok and has(r, "Assets.Created"), step="create", events=("Assets.Created",))
        send("set_metadata pUSDC-gov (6 decimals)", "A", "Assets", "set_metadata",
             {"id": breaker, "name": "pUSDC-gov", "symbol": "pUSDC-gov", "decimals": base_dep.decimals},
             "Ok + Assets.MetadataSet", lambda r: r.outcome.ok, step="metadata", events=("Assets.MetadataSet",))
        for who, amount in (("Judge", JUDGE_HOLDS), ("Peer", PEER_HOLDS)):
            send(f"A mints {amount / 1e6:.2f} to the {who.lower()} (scratch S1, before the team hand-over)", "A",
                 "Assets", "mint", {"id": breaker, "beneficiary": addr[who], "amount": amount}, "Ok + Assets.Issued",
                 lambda r: r.outcome.ok and has(r, "Assets.Issued"), step=f"mint_{who.lower()}",
                 events=("Assets.Issued",))
        send("A hands the team over: issuer M_mint, admin M_admin, freezer M_watch {W1, W2}", "A", "Assets",
             "set_team", {"id": breaker, "issuer": rm0.m_mint, "admin": rm0.m_admin, "freezer": rm0.m_watch},
             "Ok + Assets.TeamChanged", lambda r: r.outcome.ok and has(r, "Assets.TeamChanged"), step="team0",
             events=("Assets.TeamChanged",))
        r = send("A transfers ownership to M_mint", "A", "Assets", "transfer_ownership",
                 {"id": breaker, "owner": rm0.m_mint}, "Ok + Assets.OwnerChanged",
                 lambda r: r.outcome.ok and has(r, "Assets.OwnerChanged"), step="owner0", events=("Assets.OwnerChanged",))
        d = details(breaker, r.block_hash)
        run.check("scratch team == role map (owner/issuer M_mint, admin M_admin, freezer M_watch)",
                  [d["owner"], d["issuer"], d["admin"], d["freezer"]],
                  [rm0.m_mint, rm0.m_mint, rm0.m_admin, rm0.m_watch], r.block_hash)
        dep = Deployment(profile=profile.name, genesis_hash=base_dep.genesis_hash, breaker=breaker, control=control,
                         decimals=base_dep.decimals, s2=s2, roles=rm0.as_dict(),
                         reserve={"label": "local-anvil (not Sepolia)", "evm_chain_id": ANVIL_CHAIN_ID,
                                  "vault": vault_addr, "erc20": usdc_addr, "custodian": custodian,
                                  "providers": [f"anvil={args.evm_url}"]},
                         created_at=run["started_at"], setup_evidence=f"{stem}.json")
        dep.save(manifest)
        bot = make_bot(dep)
        m_mint = MultisigAccount([addr["A"], addr["B"]], 2, fmt)

        # --- 1. watcher-set rotation -----------------------------------------------------------------------------
        team_w = {"issuer": rm0.m_mint, "admin": rm0.m_admin, "freezer": m_watch2}
        call = compose("Assets", "set_team", {"id": breaker, **team_w})
        r = m_mint.propose(substrate, profile, keys["A"], call, step="propose_team_w",
                           label="Assets.set_team(freezer=M_watch')")
        run.step("A proposes set_team(freezer = M_watch' {W1, W2, W3}) through M_mint", "Ok + Multisig.NewMultisig",
                 r, r.outcome.ok and has(r, "Multisig.NewMultisig"), ("Multisig.NewMultisig",))
        out = decided("cosign-team (no announcement)", bot.cosign_team(**team_w, k=args.k))
        run.check("bot refuses an unannounced watcher rotation", [out["decision"], "without an announcement" in
                  out["reason"]], ["refused", True], "bot")
        out = bot.announce(announcement_text("watchers", breaker, 1, [addr["W1"], addr["W2"], addr["W3"]]),
                           step="announce_watchers")
        ann_w = out["extrinsic_id"]
        run.step("B announces the watcher set {W1, W2, W3} 1-of-3 (BALLAST/1|watchers)", "Ok + System.Remarked",
                 out["receipt"], out["decision"] == "posted", ("System.Remarked",))
        out = decided("cosign-team --announcement (younger than K)",
                      bot.cosign_team(**team_w, announcement=ann_w, k=args.k))
        run.check("bot refuses before the announcement is K blocks old", [out["decision"], "too early" in out["reason"]],
                  ["refused", True], "bot")
        wait_blocks(int(ann_w.split("-")[0]) + args.k, f"announcement {ann_w} + K = {args.k}")
        out = decided("cosign-team --announcement (after K)", bot.cosign_team(**team_w, announcement=ann_w, k=args.k))
        d = details(breaker)
        run.check("freezer after the co-signed rotation == M_watch'", d["freezer"], m_watch2, "head")
        rm1 = RoleMap(a=addr["A"], a2=addr["A2"], b=addr["B"], watchers=(addr["W1"], addr["W2"], addr["W3"]),
                      ss58_format=fmt)
        dep.roles = rm1.as_dict()
        dep.save(manifest)
        send("W1 tries to freeze through the OLD M_watch {W1, W2}", "W1", "Multisig", "as_multi_threshold_1",
             {"other_signatories": other_signatories([addr["W1"], addr["W2"]], addr["W1"], ss58_format=fmt),
              "call": compose("Assets", "freeze_asset", {"id": breaker})}, "Err(Assets.NoPermission)",
             lambda r: str(r.outcome) == "Err(Assets.NoPermission)", step="freeze_old_set",
             label="Multisig.as_multi_threshold_1(Assets.freeze_asset) via old M_watch")
        run.check("asset still live after the old set's attempt", asset_state(breaker, details(breaker)).frozen, False,
                  "head")

        # --- 2. M_admin rotation ---------------------------------------------------------------------------------
        bot = make_bot(dep)
        out = bot.announce(announcement_text("admins", breaker, 2, [addr["A"], addr["A3"], addr["B"]]),
                           step="announce_admins")
        ann_a = out["extrinsic_id"]
        run.step("B announces the admin set {A, A3, B} 2-of-3 (A2 retired; BALLAST/1|admins)", "Ok + System.Remarked",
                 out["receipt"], out["decision"] == "posted", ("System.Remarked",))
        team_a = {"issuer": rm1.m_mint, "admin": m_admin2, "freezer": m_watch2}
        call = compose("Assets", "set_team", {"id": breaker, **team_a})
        r = m_mint.propose(substrate, profile, keys["A"], call, step="propose_team_a",
                           label="Assets.set_team(admin=M_admin')")
        run.step("A proposes set_team(admin = M_admin' {A, A3, B}) through M_mint", "Ok + Multisig.NewMultisig",
                 r, r.outcome.ok and has(r, "Multisig.NewMultisig"), ("Multisig.NewMultisig",))
        wait_blocks(int(ann_a.split("-")[0]) + args.k, f"announcement {ann_a} + K = {args.k}")
        out = decided("cosign-team --announcement (admins, after K)",
                      bot.cosign_team(**team_a, announcement=ann_a, k=args.k))
        run.check("admin after the co-signed rotation == M_admin'", details(breaker)["admin"], m_admin2, "head")
        rm2 = RoleMap(a=addr["A"], a2=addr["A2"], b=addr["B"], watchers=rm1.watchers, ss58_format=fmt,
                      admins=(addr["A"], addr["A3"], addr["B"]))
        dep.roles = rm2.as_dict()
        dep.save(manifest)
        bot = make_bot(dep)
        m_admin = MultisigAccount(rm2.admin_signatories, 2, fmt)

        # --- 3. community watcher ---------------------------------------------------------------------------------
        log_out = EVIDENCE / f"{stem}-watch-outage.log"
        p = watcher("W3 outage", list(UNREACHABLE), ["--until-frozen", "--max-seconds", "30"], log_out, 60)
        p.wait(timeout=90)
        recs = read_log(log_out)
        checks = [x for x in recs if x["event"] == "check"]
        run.check("community watcher, every provider down for 30 s: exit 4 (not frozen), no freeze submitted",
                  [p.returncode, any(x["event"] == "freeze-submit" for x in recs)], [4, False], "watcher log")
        run.check("…its checks all read 'outage' with 'never fail-closed'",
                  bool(checks) and all(x["decision"]["action"] == "outage" and "never fail-closed" in
                                       x["decision"]["detail"] for x in checks), True, "watcher log")
        log_c = EVIDENCE / f"{stem}-watch-community.log"
        provs = [f"anvil-a={args.evm_url}", f"anvil-b={args.evm_url.replace('127.0.0.1', 'localhost')}"]
        p = watcher("W3 community", provs, ["--until-frozen", "--max-seconds", str(int(args.timeout))], log_c,
                    args.timeout)
        t0 = time.time()
        while not any(x["event"] == "check" and x["decision"]["action"] == "level" for x in read_log(log_c)):
            if p.poll() is not None or time.time() - t0 > 120:
                raise RuntimeError(f"community watcher never read level (exit {p.poll()})")
            time.sleep(1)
        drain_sent = time.time()
        evm(f"custodian drains {DRAIN / 1e6:.2f} (30%) from the vault",
            vault.functions.release(custodian, DRAIN, b"\x00" * 32).transact({"from": custodian}), amount=DRAIN)
        p.wait(timeout=args.timeout + 30)
        recs = read_log(log_c)
        fz = next((x for x in recs if x["event"] == "freeze"), None)
        if fz is None:
            raise RuntimeError(f"no freeze in the community watcher log (exit {p.returncode})")
        trig = next(x for x in recs if x["event"] == "check" and x["decision"]["freeze"])
        run.step("W3 (community watcher) freezes through M_watch' once every provider reads short at one block",
                 "Ok + Assets.AssetFrozen", fz["receipt"],
                 fz["receipt"]["outcome"]["ok"] and "Assets.AssetFrozen" in
                 [f"{e['module_id']}.{e['event_id']}" for e in fz["receipt"]["events"]], ("Assets.AssetFrozen",))
        run.check("the freeze's trigger: community mode, pinned block, every provider short",
                  [trig.get("mode"), (trig.get("pinned") or {}).get("block") is not None,
                   len(trig["decision"]["short"])], ["community", True, 2], "watcher log")
        run.note("community_freeze_seconds_after_drain_sent (one sample, poll every block)",
                 round(epoch(fz["t"]) - drain_sent, 2))
        freeze_block = int(fz["receipt"]["extrinsic_id"].split("-")[0])
        send("judge transfers 1.00 while the asset is frozen", "Judge", "Assets", "transfer",
             {"id": breaker, "target": addr["Peer"], "amount": 1_000_000}, "Err(Assets.AssetNotLive)",
             lambda r: str(r.outcome) == "Err(Assets.AssetNotLive)", step="transfer_frozen")

        # --- 4. wind-down -----------------------------------------------------------------------------------------
        others3 = lambda me: other_signatories(list(rm1.watchers), addr[me], ss58_format=fmt)  # noqa: E731
        wait_blocks(freeze_block + args.w, f"frozen for W = {args.w} blocks")

        def freeze_account(who: str, step: str):
            return send(f"W3 freezes the {who.lower()}'s account through M_watch' (wind-down step 1)", "W3",
                        "Multisig", "as_multi_threshold_1",
                        {"other_signatories": others3("W3"), "call": compose("Assets", "freeze",
                                                                             {"id": breaker, "who": addr[who]})},
                        "Ok + Assets.Frozen", lambda r: r.outcome.ok and has(r, "Assets.Frozen"), step=step,
                        events=("Assets.Frozen",), label="Multisig.as_multi_threshold_1(Assets.freeze)")

        freeze_account("Judge", "freeze_judge")
        reserves = vault.functions.reserves().call()
        s1 = details(breaker)["supply"]
        r_cut = (Decimal(reserves) / Decimal(s1 + s2)).quantize(Decimal("0.0001"))
        out = bot.announce(final_text(breaker, r_cut), step="announce_final")
        fin = out["extrinsic_id"]
        run.step(f"B posts final r = {reserves / 1e6:.2f} / {(s1 + s2) / 1e6:.2f} = {r_cut} (BALLAST/1|final)",
                 "Ok + System.Remarked", out["receipt"], out["decision"] == "posted", ("System.Remarked",))
        thaw = compose("Assets", "thaw_asset", {"id": breaker})
        r = m_admin.propose(substrate, profile, keys["A"], thaw, step="propose_thaw",
                            label="Assets.thaw_asset via M_admin'")
        run.step("A proposes thaw_asset through M_admin'", "Ok + Multisig.NewMultisig", r,
                 r.outcome.ok and has(r, "Multisig.NewMultisig"), ("Multisig.NewMultisig",))
        out = decided("cosign-thaw --final (peer still open)", bot.cosign_thaw(final=fin, w=args.w, max_lookback=200))
        run.check("bot refuses the wind-down thaw while a holder is open",
                  [out["decision"], "1 of 2 holders" in out["reason"]], ["refused", True], "bot")
        freeze_account("Peer", "freeze_peer")
        out = decided("cosign-thaw --final (all holders frozen)", bot.cosign_thaw(final=fin, w=args.w, max_lookback=200))
        st = details(breaker)
        run.check("asset live after the wind-down thaw", asset_state(breaker, st).frozen, False, "head")
        rows = holders(substrate, breaker)
        run.check("every holder with a balance individually frozen",
                  sorted((role_of.get(h["who"], h["who"]), h["frozen"]) for h in rows if h["balance"] > 0),
                  [("Judge (holder)", True), ("Peer (holder)", True)], "head")
        log_h = EVIDENCE / f"{stem}-watch-hold.log"
        p = watcher("W3 hold", provs, ["--until-frozen", "--max-seconds", "40"], log_h, 60)
        p.wait(timeout=90)
        recs = read_log(log_h)
        holds = [x for x in recs if x["event"] == "check" and x["decision"]["action"] == "winddown-hold"]
        run.check("community watcher after the thaw: deficit but winddown-hold, no freeze (exit 4)",
                  [bool(holds), any(x["event"] == "freeze-submit" for x in recs), p.returncode], [True, False, 4],
                  "watcher log")
        send("judge transfers 1.00 after the thaw (account still frozen)", "Judge", "Assets", "transfer",
             {"id": breaker, "target": addr["Peer"], "amount": 1_000_000}, "Err(Assets.Frozen)",
             lambda r: str(r.outcome) == "Err(Assets.Frozen)", step="transfer_acct_frozen")

        # --- 5. redemption ----------------------------------------------------------------------------------------
        r = send("judge asks first: BALLAST/1|redeem with its EVM address", "Judge", "System", "remark_with_event",
                 {"remark": redeem_text(breaker, REDEEM_EVM)}, "Ok + System.Remarked",
                 lambda r: r.outcome.ok and has(r, "System.Remarked"), step="redeem_request", events=("System.Remarked",))
        req = r.extrinsic_id
        call = bot.redeem_call(addr["Judge"], JUDGE_HOLDS)
        r = m_admin.propose(substrate, profile, keys["A"], call, step="propose_redeem",
                            label="Utility.batch_all[thaw(judge), burn(judge, 30.00)] via M_admin'")
        run.step("A proposes batch_all([thaw(judge), burn(judge, 30.00)]) through M_admin'",
                 "Ok + Multisig.NewMultisig", r, r.outcome.ok and has(r, "Multisig.NewMultisig"),
                 ("Multisig.NewMultisig",))
        out = decided("cosign_redeem", bot.cosign_redeem(addr["Judge"], JUDGE_HOLDS, req, fin))
        names = [f"{e['module_id']}.{e['event_id']}" for e in (out.get("receipt") or {}).get("events", [])]
        run.check("the redemption executed atomically: Thawed + Burned in one extrinsic",
                  ["Assets.Thawed" in names, "Assets.Burned" in names], [True, True], "receipt")
        owed = int(r_cut * JUDGE_HOLDS)
        evm(f"custodian releases r x 30.00 = {owed / 1e6:.2f} to the judge's EVM address, redeemId = redeem_id({req})",
            vault.functions.release(REDEEM_EVM, owed, redeem_id(req)).transact({"from": custodian}),
            amount=owed, redeem_request=req, redeem_id="0x" + redeem_id(req).hex())
        s1_after = details(breaker)["supply"]
        res_after = vault.functions.reserves().call()
        run.check("after the redemption: S1, reserves, and r unchanged", [s1_after, res_after,
                  str((Decimal(res_after) / Decimal(s1_after + s2)).quantize(Decimal("0.0001")))],
                  [PEER_HOLDS, reserves - owed, str(r_cut)], "head + evm latest")
        run.check("the judge's EVM address received r x 30.00", usdc.functions.balanceOf(REDEEM_EVM).call(), owed,
                  "evm latest")
        run["governance"] = {"announce_watchers": ann_w, "announce_admins": ann_a, "final": fin, "redeem_request": req,
                             "r": str(r_cut), "freeze_block": freeze_block, "manifest": f"deployments/{manifest.name}"}
    except Exception as exc:  # noqa: BLE001 — keep every receipt that landed
        run["error"] = f"{type(exc).__name__}: {exc}"
        traceback.print_exc()
    finally:
        for p in procs:
            if p.poll() is None:
                p.terminate()
    out_path = run.finish(f"{stem}.json")
    write_receipts_md()
    print(json.dumps({"evidence": str(out_path.relative_to(ROOT)), "verdict": run["verdict"]}))
    return 0 if run["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
