"""`ballast drill` — the breaker, end to end, on a stand-in chain against a LOCAL anvil reserve.

Labelled "reserve: local-anvil (not Sepolia)" everywhere: the vault and its token live on a local anvil chain
(chain id 31337, `scripts/anvil_local.sh`). The Portaldot side is the configured stand-in profile. Nothing here is
a V3 or Sepolia measurement.

Scenario `drain` (the kill-rule flow):
  1. EVM: deploy MockUSDC + ReserveVault (forge artifacts), deposit S1 + S2 = 100.00 into the vault;
  2. Portaldot: fresh breaker asset (freezer = 1-of-2 watcher multisig M_watch) + control asset, mint S1 to the
     judge and S2 to the peer — reserves == supply, level;
  3. start the watchdog as its own process (key W2) and wait until it reports `level`;
  4. the custodian drains 30% of the vault (`release`);
  5. the watchdog sees reserves < S1 + S2 and freezes through M_watch (one batch: reason remark + freeze);
  6. the judge's transfer of the breaker asset is refused while frozen; the control asset is untouched.
Scenario `outage`: same setup, but the watchdog's only providers are unreachable local URLs; with nothing to
read it fails closed after `--fail-closed-after` seconds (production 300 s) and freezes with why=providers-down.

Receipts: evidence/drill-<scenario>-<profile>-asset<id>.json (+ the watchdog's JSON-lines log), docs/RECEIPTS.md.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

from .chain import Receipt, connect, dev_keypair, submit
from .chain_profile import ProfileError, blake2_256, identify
from .config import load_chain_config
from .multisig import multi_address, public_key
from .receipts import EVIDENCE, score, summarize, write_receipts_md
from .rpc import HttpRpc
from .sepolia import ANVIL_CHAIN_ID
from .watchdog import parse_remark, reserve_label

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
DRILL_ASSET_FROM = 2001  # drill assets: ids >= 2001 (spike >= 1001; ids 1 and 2 stay for the role-split assets)
DECIMALS = 6
S1 = 50_000_000  # 50.00 of the breaker asset (6 decimals, like USDC)
S2 = 50_000_000  # 50.00 of the control asset
TRANSFER = 1_000_000  # 1.00
FROZEN_TRANSFER_ERRORS = {"standin-upstream": "Err(Assets.AssetNotLive)"}
UNREACHABLE = ("down-1=http://127.0.0.1:9", "down-2=http://127.0.0.1:10")  # nothing listens: connection refused


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def epoch(iso: str) -> float:
    return datetime.strptime(iso, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc).timestamp()


def artifact(name: str) -> tuple[list, str]:
    path = OUT / f"{name}.sol" / f"{name}.json"
    if not path.exists():
        subprocess.run(["forge", "build"], cwd=ROOT, check=True, capture_output=True)
    data = json.loads(path.read_text())
    return data["abi"], data["bytecode"]["object"]


def free_asset_id(substrate, start: int) -> int:
    asset_id = start
    while substrate.query("Assets", "Asset", [asset_id]).value is not None:
        asset_id += 1
    return asset_id


def read_log(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text().splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:  # a line being written right now
            pass
    return out


def run_drill(args: argparse.Namespace) -> int:
    from web3 import HTTPProvider, Web3
    from web3.logs import DISCARD

    try:
        cfg = load_chain_config(args.config, profile=args.profile, url=args.url)
        ident = identify(HttpRpc(cfg.url), cfg.profile.name)
    except (ProfileError, OSError, ValueError) as exc:
        print(f"drill: {exc}", file=sys.stderr)
        return 2
    profile = ident.profile
    if profile.name not in FROZEN_TRANSFER_ERRORS:
        print(f"drill: profile {profile.name!r} not supported (supported: {', '.join(FROZEN_TRANSFER_ERRORS)})",
              file=sys.stderr)
        return 2
    frozen_error = FROZEN_TRANSFER_ERRORS[profile.name]
    w3 = Web3(HTTPProvider(args.evm_url, request_kwargs={"timeout": 10}))
    try:
        evm_chain = w3.eth.chain_id
    except Exception as exc:  # noqa: BLE001
        print(f"drill: no EVM chain at {args.evm_url} ({type(exc).__name__}); start it: scripts/anvil_local.sh start",
              file=sys.stderr)
        return 2
    if evm_chain != ANVIL_CHAIN_ID:
        print(f"drill: {args.evm_url} is chain {evm_chain}; this drill runs on a local anvil (31337) only",
              file=sys.stderr)
        return 2
    label = reserve_label(evm_chain)
    print(ident.banner())
    print(f"chain: {profile.label} · reserve: {label} · scenario: {args.scenario}")

    substrate = connect(profile, cfg.url)
    fmt = substrate.ss58_format or 42
    alice = dev_keypair(profile, "//Alice")
    keys = {role: dev_keypair(profile, f"//Ballast{role}") for role in ("A", "W1", "W2", "Judge", "Peer")}
    addr = {role: kp.ss58_address for role, kp in keys.items()}
    watchers = [addr["W1"], addr["W2"]]
    m_watch = multi_address(watchers, 1, ss58_format=fmt)
    custodian = w3.eth.accounts[0]
    breaker = free_asset_id(substrate, DRILL_ASSET_FROM)
    control = free_asset_id(substrate, breaker + 1)
    EVIDENCE.mkdir(exist_ok=True)
    stem = f"drill-{args.scenario}-{profile.name}-asset{breaker}"
    log_path = EVIDENCE / f"{stem}.watchdog.jsonl"
    log_path.unlink(missing_ok=True)

    run: dict = {
        "kind": "drill",
        "scenario": args.scenario,
        "chain": {**ident.as_dict(), "url": cfg.url},
        "reserve": {"label": label, "evm_chain_id": evm_chain, "evm_url": args.evm_url, "custodian": custodian},
        "started_at": now(),
        "asset_id": breaker,
        "assets": {"breaker": breaker, "control": control, "S1": S1, "S2": S2, "decimals": DECIMALS},
        "accounts": {**addr, "M_watch": m_watch, "funder": alice.ss58_address},
        "watchdog_log": log_path.name,
        "steps": [],
        "evm_steps": [],
        "state_checks": [],
    }
    role_of = {kp.ss58_address: role for role, kp in keys.items()} | {alice.ss58_address: "Alice, stand-in funder"}

    def step(name: str, expected: str, r: Receipt | dict, ok: bool, events: tuple[str, ...] = ()):
        rd = r.as_dict() if isinstance(r, Receipt) else r
        names = [f"{e['module_id']}.{e['event_id']}" for e in rd["events"]]
        run["steps"].append({
            "name": name, "expected": expected, "as_expected": ok, "counted": True,
            "signer_role": role_of.get(rd["signer"], rd["signer"]),
            "events_seen": [e for e in events if e in names], "receipt": rd,
        })
        print(f"{'PASS' if ok else 'FAIL'} {rd['extrinsic_id']:>9} {rd['call'][:60]:<60} {rd['outcome']['text']}  {name}")

    def evm_step(name: str, expected: str, tx_hash, ok_extra: bool = True, **extra) -> dict:
        rcpt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
        ok = rcpt["status"] == 1 and ok_extra
        row = {
            "name": name, "expected": expected, "as_expected": ok, "counted": True, "chain": label,
            "tx_hash": rcpt["transactionHash"].to_0x_hex(), "block_number": rcpt["blockNumber"],
            "block_hash": rcpt["blockHash"].to_0x_hex(), "status": rcpt["status"], "from": rcpt["from"],
            "to": rcpt["to"], "contract": rcpt["contractAddress"], **extra,
        }
        run["evm_steps"].append(row)
        print(f"{'PASS' if ok else 'FAIL'} evm #{row['block_number']:<5} {name}  {row['tx_hash']}")
        return row

    def check(what: str, observed, expected, where: str, ok: bool | None = None) -> bool:
        ok = (observed == expected) if ok is None else ok
        run["state_checks"].append({"what": what, "expected": expected, "observed": observed, "ok": ok,
                                    "block_hash": where})
        print(f"     {'ok  ' if ok else 'FAIL'} state: {what}: {observed}")
        return ok

    def has(r: Receipt, *events: str) -> bool:
        return all(e in r.event_names() for e in events)

    def call(module: str, function: str, params: dict):
        return substrate.compose_call(call_module=module, call_function=function, call_params=params)

    def details(asset_id: int, block_hash: str) -> dict:
        return substrate.query("Assets", "Asset", [asset_id], block_hash=block_hash).value or {}

    def balance(asset_id: int, who: str, block_hash: str) -> int:
        acct = substrate.query("Assets", "Account", [asset_id, who], block_hash=block_hash).value
        return acct["balance"] if acct else 0

    proc = None
    try:
        # 1. EVM reserve on the local anvil chain.
        usdc_abi, usdc_bin = artifact("MockUSDC")
        vault_abi, vault_bin = artifact("ReserveVault")
        tx = w3.eth.contract(abi=usdc_abi, bytecode=usdc_bin).constructor().transact({"from": custodian})
        usdc_addr = evm_step("deploy MockUSDC (test-only token)", "status 1", tx)["contract"]
        usdc = w3.eth.contract(address=usdc_addr, abi=usdc_abi)
        tx = w3.eth.contract(abi=vault_abi, bytecode=vault_bin).constructor(usdc_addr).transact({"from": custodian})
        vault_addr = evm_step("deploy ReserveVault(usdc) — owner = custodian", "status 1", tx)["contract"]
        vault = w3.eth.contract(address=vault_addr, abi=vault_abi)
        tx = usdc.functions.mint(vault_addr, S1 + S2).transact({"from": custodian})
        evm_step("deposit S1 + S2 = 100.00 into the vault", "status 1", tx)
        run["reserve"] |= {"vault": vault_addr, "usdc": usdc_addr}
        check("vault reserves() after deposit", vault.functions.reserves().call(), S1 + S2, "evm latest")

        # 2. Portaldot: fund, two fresh assets, breaker freezer = M_watch.
        const = lambda pallet, name: substrate.get_constant(pallet, name).value  # noqa: E731
        ed = const("Balances", "ExistentialDeposit")
        per_asset = (const("Assets", "AssetDeposit") + const("Assets", "MetadataDepositBase")
                     + 2 * len("pUSDC-test") * const("Assets", "MetadataDepositPerByte"))
        fund = [call("Balances", "transfer_keep_alive", {"dest": who, "value": amount}) for who, amount in (
            (addr["A"], 2 * per_asset + 10 * ed), (addr["W1"], 10 * ed), (addr["W2"], 10 * ed),
            (addr["Judge"], 10 * ed), (addr["Peer"], 10 * ed), (m_watch, 2 * ed))]
        r = submit(substrate, profile, alice, "Utility", "batch_all", {"calls": fund}, step="fund",
                   call_label="Utility.batch_all[6 x Balances.transfer_keep_alive]")
        step("fund A, W1, W2, judge, peer, M_watch (>= ED)", "Ok", r, r.outcome.ok)
        for asset_id, symbol in ((breaker, "pUSDC-test"), (control, "pUSDC-ctl")):
            r = submit(substrate, profile, keys["A"], "Assets", "create",
                       {"id": asset_id, "admin": addr["A"], "min_balance": 1}, step=f"create_{asset_id}")
            step(f"create asset {asset_id}", "Ok + Assets.Created", r, r.outcome.ok and has(r, "Assets.Created"),
                 ("Assets.Created",))
            r = submit(substrate, profile, keys["A"], "Assets", "set_metadata",
                       {"id": asset_id, "name": symbol, "symbol": symbol, "decimals": DECIMALS},
                       step=f"set_metadata_{asset_id}")
            step(f"set_metadata {symbol} ({DECIMALS} decimals)", "Ok + Assets.MetadataSet", r,
                 r.outcome.ok and has(r, "Assets.MetadataSet"), ("Assets.MetadataSet",))
        r = submit(substrate, profile, keys["A"], "Assets", "set_team",
                   {"id": breaker, "issuer": addr["A"], "admin": addr["A"], "freezer": m_watch}, step="set_team")
        step(f"set_team asset {breaker}: freezer = M_watch (1-of-2 watchers)", "Ok + Assets.TeamChanged", r,
             r.outcome.ok and has(r, "Assets.TeamChanged"), ("Assets.TeamChanged",))
        r = submit(substrate, profile, keys["A"], "Assets", "mint",
                   {"id": breaker, "beneficiary": addr["Judge"], "amount": S1}, step="mint_s1")
        step(f"mint S1 = 50.00 of asset {breaker} to the judge", "Ok + Assets.Issued", r,
             r.outcome.ok and has(r, "Assets.Issued"), ("Assets.Issued",))
        r = submit(substrate, profile, keys["A"], "Assets", "mint",
                   {"id": control, "beneficiary": addr["Peer"], "amount": S2}, step="mint_s2")
        step(f"mint S2 = 50.00 of control asset {control} to the peer", "Ok + Assets.Issued", r,
             r.outcome.ok and has(r, "Assets.Issued"), ("Assets.Issued",))
        level_hash = r.block_hash
        check(f"supply S1 + S2 == vault reserves (level)",
              details(breaker, level_hash)["supply"] + details(control, level_hash)["supply"],
              vault.functions.reserves().call(), level_hash)

        # 3. The watchdog, as its own process with its own key.
        providers = [f"anvil={args.evm_url}"] if args.scenario == "drain" else list(UNREACHABLE)
        cmd = [sys.executable, "-m", "ballast.cli", "--profile", profile.name, "--url", cfg.url, "watch",
               "--breaker", str(breaker), "--supply-assets", f"{breaker},{control}", "--holder", vault_addr,
               "--token", usdc_addr, "--watcher", "//BallastW2", "--watchers", "//BallastW1,//BallastW2",
               "--until-frozen", "--max-seconds", str(args.timeout), "--log", str(log_path.relative_to(ROOT)), "--timeout", "3",
               "--fail-closed-after", str(args.fail_closed_after if args.scenario == "outage" else 300)]
        for p in providers:
            cmd += ["--provider", p]
        run["watchdog_cmd"] = " ".join(c if c != sys.executable else "python" for c in cmd)
        proc = subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        print(f"watchdog pid {proc.pid}: {run['watchdog_cmd']}")
        deadline = time.time() + 120
        want = "level" if args.scenario == "drain" else "outage"
        while time.time() < deadline:
            recs = read_log(log_path)
            if any(r["event"] == "not-armed" for r in recs) or proc.poll() is not None:
                raise RuntimeError(f"watchdog exited early: {[r for r in recs if r['event'] in ('not-armed', 'stop')]}"
                                   f" {proc.stderr.read()[-800:] if proc.poll() is not None else ''}")
            if any(r["event"] == "check" and r["decision"]["action"] == want for r in recs):
                break
            time.sleep(0.5)
        else:
            raise RuntimeError(f"watchdog never reported {want!r} within 120 s")
        start_rec = next(r for r in read_log(log_path) if r["event"] == "start")
        run["watchdog"] = {k: start_rec.get(k) for k in ("watcher", "m_watch", "reserve", "poll_blocks",
                                                          "fail_closed_after", "providers", "supply_ids")}
        check("watchdog armed: its M_watch == the breaker's freezer",
              public_key(start_rec["m_watch"]) == public_key(m_watch), True, "watchdog start record")

        # 4. Drain (drain scenario only).
        drain_at = None
        if args.scenario == "drain":
            amount = (S1 + S2) * args.drain_pct // 100
            redeem_id = Web3.keccak(text=f"ballast-drill-{breaker}")
            pd_before = substrate.get_block_number(None)
            tx = vault.functions.release(custodian, amount, redeem_id).transact({"from": custodian})
            row = evm_step(f"custodian drains {args.drain_pct}% ({amount / 1e6:.2f}) — release()",
                           "status 1 + Released", tx, redeem_id=redeem_id.to_0x_hex(), amount=amount)
            drain_at = time.time()
            logs = vault.events.Released().process_receipt(w3.eth.get_transaction_receipt(tx), errors=DISCARD)
            row["released_event"] = bool(logs) and logs[0]["args"]["amount"] == amount
            row["as_expected"] = row["as_expected"] and row["released_event"]
            row["pd_head_before_drain"] = pd_before
            left = vault.functions.reserves().call()
            check("vault reserves() after the drain < S1 + S2", left, S1 + S2 - amount, row["block_hash"],
                  ok=left == S1 + S2 - amount and left < S1 + S2)

        # 5. Wait (foreground) for the watchdog to freeze and exit.
        try:
            proc.wait(timeout=args.timeout + 30)
        except subprocess.TimeoutExpired:
            proc.kill()
            raise RuntimeError("watchdog did not freeze in time") from None
        recs = read_log(log_path)
        freeze = next((r for r in recs if r["event"] == "freeze"), None)
        if freeze is None:
            raise RuntimeError(f"no freeze in the watchdog log (exit {proc.returncode})")
        trigger = next(r for r in recs if r["event"] == "check" and r["decision"]["freeze"])
        fr = freeze["receipt"]
        expected_why = "deficit" if args.scenario == "drain" else "fail-closed"
        remark = parse_remark(freeze["remark"])
        step(f"watchdog (W2) freezes asset {breaker} via M_watch, reason on chain (why={remark['why']})",
             "Ok + inner Ok + Assets.AssetFrozen + System.Remarked", fr,
             fr["outcome"]["ok"] and all(o["ok"] for o in fr["inner"]) and remark["why"] == expected_why,
             ("Assets.AssetFrozen", "System.Remarked", "Multisig.MultisigExecuted"))
        check(f"Asset({breaker}).status after the freeze", details(breaker, fr["block_hash"]).get("status"),
              "Frozen", fr["block_hash"])
        remarked = [e for e in fr["events"] if (e["module_id"], e["event_id"]) == ("System", "Remarked")]
        on_chain_hash = remarked[0]["attributes"]["hash"] if remarked else None
        check("System.Remarked hash == blake2_256(the reason remark)", on_chain_hash,
              blake2_256(freeze["remark"].encode()), fr["block_hash"])
        check(f"control asset {control} untouched (Live)", details(control, fr["block_hash"]).get("status"),
              "Live", fr["block_hash"])

        # 6. The judge's transfer is refused while frozen.
        r = submit(substrate, profile, keys["Judge"], "Assets", "transfer",
                   {"id": breaker, "target": addr["Peer"], "amount": TRANSFER}, step="judge_transfer_frozen")
        step("judge transfer 1.00 while frozen is refused", frozen_error, r, str(r.outcome) == frozen_error)
        check("judge balance unchanged after the refused transfer", balance(breaker, addr["Judge"], r.block_hash),
              S1, r.block_hash)

        # Timings — local stand-in + local anvil: wall-clock on this machine, NOT a V3 or Sepolia latency.
        included_block_ts = substrate.query("Timestamp", "Now", block_hash=fr["block_hash"]).value
        timing = {
            "basis": "wall-clock on one machine; stand-in chain + local anvil reserve (not V3, not Sepolia)",
            "trigger_head": trigger["head"],
            "freeze_block": fr["block_number"],
            "freeze_block_timestamp_ms": included_block_ts,
            "submit_to_inclusion_s": round(freeze["included_at"] - freeze["submitted_at"], 2),
        }
        if drain_at is not None:
            seen_at = epoch(trigger["t"])
            timing |= {
                "pd_head_before_drain": run["evm_steps"][-1]["pd_head_before_drain"],
                "blocks_head_before_drain_to_freeze": fr["block_number"] - run["evm_steps"][-1]["pd_head_before_drain"],
                "drain_to_deficit_seen_s": round(seen_at - drain_at, 2),
                "deficit_seen_to_submit_s": round(freeze["submitted_at"] - seen_at, 2),
                "drain_to_freeze_included_s": round(freeze["included_at"] - drain_at, 2),
            }
        else:
            first_outage = next(r for r in recs if r["event"] == "check" and r["decision"]["action"] == "outage")
            timing |= {
                "fail_closed_after_s": run["watchdog"]["fail_closed_after"],
                "first_outage_seen_to_freeze_included_s": round(freeze["included_at"] - epoch(first_outage["t"]), 2),
                "down_for_s_in_remark": remark.get("down"),
            }
        run["timing"] = timing
        run["remark"] = freeze["remark"]
    except Exception as exc:  # keep every receipt that did land
        run["error"] = f"{type(exc).__name__}: {exc}"
        traceback.print_exc()
    finally:
        if proc is not None and proc.poll() is None:
            proc.terminate()
        run["finished_at"] = now()
        summarize(run)
        out = EVIDENCE / f"{stem}.json"
        out.write_text(json.dumps(run, indent=2, default=str) + "\n")
        md = write_receipts_md()

    print(f"\n[{profile.name} · reserve {label}] drill {args.scenario}: {run['verdict']} ({score(run)}); "
          f"asset {breaker}")
    if run.get("timing"):
        print(f"timing: {json.dumps(run['timing'])}")
    print(f"evidence -> evidence/{out.name} · watchdog log -> evidence/{log_path.name} · receipts -> docs/{md.name}")
    return 0 if run["verdict"] == "PASS" else 1
