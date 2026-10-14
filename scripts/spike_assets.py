#!/usr/bin/env python3
"""S0 spike: Assets role split + watcher-set freeze, end to end, on the configured chain profile.

  python scripts/spike_assets.py [--profile standin-upstream] [--url ws://127.0.0.1:49944]

Dev keys -> assets.create (free asset id) -> set_metadata (pUSDC-test) -> set_team(issuer=A, admin=A,
freezer=M_watch) where M_watch = 1-of-2 watcher multisig {W1, W2} -> mint to a holder -> W2 freezes the
asset through multisig.as_multi_threshold_1 -> a watcher's thaw is refused (inner error decoded) -> the
holder's transfer fails while frozen (error name read from metadata) -> control: A thaws -> the same
transfer succeeds. Every step is a real extrinsic; receipts go to evidence/ and docs/RECEIPTS.md, each
labelled with the chain profile. Dev keys are refused on anything but a stand-in.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ballast.chain import Receipt, connect, dev_keypair, submit  # noqa: E402
from ballast.chain_profile import identify, require_multisig_shape  # noqa: E402
from ballast.config import load_chain_config  # noqa: E402
from ballast.multisig import multi_address, other_signatories  # noqa: E402
from ballast.receipts import EVIDENCE, write_receipts_md  # noqa: E402
from ballast.rpc import HttpRpc  # noqa: E402

SPIKE_ASSET_FROM = 1001  # spike assets live at >= 1001; ids 1 and 2 stay free for the breaker + control assets
DECIMALS = 6
MINT = 50_000_000  # 50.00 pUSDC-test
MINT_WHILE_FROZEN = 10_000  # 0.01, the G3 "mint while frozen" observation
TRANSFER = 1_000_000  # 1.00
UNIT_FUND = 10**12  # 1 native unit at 12 decimals (standin-upstream)


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def free_asset_id(substrate, start: int) -> int:
    asset_id = start
    while substrate.query("Assets", "Asset", [asset_id]).value is not None:
        asset_id += 1
    return asset_id


def asset_status(substrate, asset_id: int, block_hash: str) -> str:
    return substrate.query("Assets", "Asset", [asset_id], block_hash=block_hash).value["status"]


def balance_of(substrate, asset_id: int, who: str, block_hash: str) -> int:
    acct = substrate.query("Assets", "Account", [asset_id, who], block_hash=block_hash).value
    return acct["balance"] if acct else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config")
    ap.add_argument("--profile")
    ap.add_argument("--url")
    args = ap.parse_args()

    cfg = load_chain_config(args.config, profile=args.profile, url=args.url)
    ident = identify(HttpRpc(cfg.url), cfg.profile.name)
    profile = ident.profile
    shape = require_multisig_shape(profile)
    print(ident.banner())
    print(f"label: {profile.label} · as_multi shape: {shape}")

    substrate = connect(profile, cfg.url)
    alice = dev_keypair(profile, "//Alice")
    keys = {role: dev_keypair(profile, f"//Ballast{role}") for role in ("A", "W1", "W2", "Judge", "Peer")}
    addr = {role: kp.ss58_address for role, kp in keys.items()}
    watchers = [addr["W1"], addr["W2"]]
    m_watch = multi_address(watchers, 1)
    sdk_m_watch = substrate.generate_multisig_account([addr["W1"], addr["W2"]], 1).ss58_address
    if sdk_m_watch != m_watch:
        print(f"FAIL: M_watch derivation {m_watch} != SDK {sdk_m_watch}")
        return 1
    print(f"M_watch (1-of-2 {{W1, W2}}) = {m_watch} (matches the SDK derivation)")

    ed = substrate.get_constant("Balances", "ExistentialDeposit").value
    deposits = {
        "Balances.ExistentialDeposit": ed,
        "Assets.AssetDeposit": substrate.get_constant("Assets", "AssetDeposit").value,
        "Assets.MetadataDepositBase": substrate.get_constant("Assets", "MetadataDepositBase").value,
        "Assets.MetadataDepositPerByte": substrate.get_constant("Assets", "MetadataDepositPerByte").value,
    }
    asset_id = free_asset_id(substrate, SPIKE_ASSET_FROM)
    print(f"free asset id: {asset_id} · ED {ed} · asset deposit {deposits['Assets.AssetDeposit']} (planck)")

    run = {
        "kind": "spike-assets",
        "chain": {**ident.as_dict(), "url": cfg.url},
        "started_at": now(),
        "asset_id": asset_id,
        "accounts": {**addr, "M_watch": m_watch, "funder": alice.ss58_address},
        "multisig": {"M_watch": {"threshold": 1, "signatories": sorted(watchers), "sdk_match": True}},
        "deposits_planck": deposits,
        "steps": [],
        "state_checks": [],
    }
    role_of = {kp.ss58_address: role for role, kp in keys.items()} | {alice.ss58_address: "Alice, stand-in funder"}

    def step(name: str, expected: str, receipt: Receipt, ok: bool, events_seen: list[str] | None = None) -> Receipt:
        run["steps"].append(
            {
                "name": name,
                "expected": expected,
                "as_expected": ok,
                "signer_role": role_of.get(receipt.signer, receipt.signer),
                "events_seen": events_seen or [],
                "receipt": receipt.as_dict(),
            }
        )
        mark = "PASS" if ok else "FAIL"
        print(f"{mark} {receipt.extrinsic_id:>9} {receipt.call:<42} {receipt.outcome}  {name}")
        print(f"     block {receipt.block_hash} tx {receipt.extrinsic_hash}")
        return receipt

    def has(receipt: Receipt, event: str) -> bool:
        return event in receipt.event_names()

    def call(module: str, function: str, params: dict) -> object:
        return substrate.compose_call(call_module=module, call_function=function, call_params=params)

    def via_watchers(signer: str, inner) -> tuple[str, str, dict]:
        others = other_signatories(watchers, addr[signer])
        return "Multisig", "as_multi_threshold_1", {"other_signatories": others, "call": inner}

    # 0. Fund the dev accounts and M_watch (>= ED) from //Alice (stand-in only).
    fund = [
        call("Balances", "transfer_keep_alive", {"dest": who, "value": amount})
        for who, amount in (
            (addr["A"], 100_000 * UNIT_FUND),
            (addr["W1"], 1_000 * UNIT_FUND),
            (addr["W2"], 1_000 * UNIT_FUND),
            (addr["Judge"], 1_000 * UNIT_FUND),
            (addr["Peer"], 1_000 * UNIT_FUND),
            (m_watch, max(ed, 1_000 * UNIT_FUND)),
        )
    ]
    r = submit(substrate, profile, alice, "Utility", "batch_all", {"calls": fund}, step="fund",
               call_label="Utility.batch_all[6 x transfer_keep_alive]")
    step("fund A, W1, W2, judge, peer, M_watch (>= ED)", "Ok", r, r.outcome.ok and not has(r, "Utility.BatchInterrupted"))

    # 1-3. Asset with a split team: issuer = admin = A, freezer = the watcher multisig.
    r = submit(substrate, profile, keys["A"], "Assets", "create",
               {"id": asset_id, "admin": addr["A"], "min_balance": 1}, step="create")
    step("create the asset", "Ok + Assets.Created", r, r.outcome.ok and has(r, "Assets.Created"), ["Assets.Created"] if has(r, "Assets.Created") else [])
    r = submit(substrate, profile, keys["A"], "Assets", "set_metadata",
               {"id": asset_id, "name": "pUSDC-test", "symbol": "pUSDC-test", "decimals": DECIMALS}, step="set_metadata")
    step("set_metadata pUSDC-test", "Ok + Assets.MetadataSet", r, r.outcome.ok and has(r, "Assets.MetadataSet"), ["Assets.MetadataSet"] if has(r, "Assets.MetadataSet") else [])
    r = submit(substrate, profile, keys["A"], "Assets", "set_team",
               {"id": asset_id, "issuer": addr["A"], "admin": addr["A"], "freezer": m_watch}, step="set_team")
    step("set_team(issuer=A, admin=A, freezer=M_watch)", "Ok + Assets.TeamChanged", r, r.outcome.ok and has(r, "Assets.TeamChanged"), ["Assets.TeamChanged"] if has(r, "Assets.TeamChanged") else [])
    team = substrate.query("Assets", "Asset", [asset_id], block_hash=r.block_hash).value
    run["state_checks"].append({"what": f"Asset({asset_id}) freezer == M_watch", "observed": team["freezer"] == m_watch,
                                "block_hash": r.block_hash})

    # 4. Mint to the holder.
    r = submit(substrate, profile, keys["A"], "Assets", "mint",
               {"id": asset_id, "beneficiary": addr["Judge"], "amount": MINT}, step="mint")
    step("mint 50.00 to the holder", "Ok + Assets.Issued", r, r.outcome.ok and has(r, "Assets.Issued"), ["Assets.Issued"] if has(r, "Assets.Issued") else [])

    # 5. Watcher 2 alone freezes the asset through the 1-of-2 watcher multisig.
    m, f, p = via_watchers("W2", call("Assets", "freeze_asset", {"id": asset_id}))
    r = submit(substrate, profile, keys["W2"], m, f, p, step="freeze", call_label="Multisig.as_multi_threshold_1(Assets.freeze_asset)")
    step("W2 freezes via M_watch (1-of-2)", "Ok + Assets.AssetFrozen", r, r.outcome.ok and has(r, "Assets.AssetFrozen"), ["Assets.AssetFrozen"] if has(r, "Assets.AssetFrozen") else [])
    status = asset_status(substrate, asset_id, r.block_hash)
    run["state_checks"].append({"what": f"Asset({asset_id}).status after freeze", "observed": status, "block_hash": r.block_hash})
    executed = [e for e in r.events if (e["module_id"], e["event_id"]) == ("Multisig", "MultisigExecuted")]
    if executed:  # this runtime names the dispatching multisig account: check it against the local derivation
        on_chain = executed[0]["attributes"]["multisig"]
        run["state_checks"].append({"what": "MultisigExecuted.multisig == locally derived M_watch",
                                    "observed": on_chain == m_watch, "block_hash": r.block_hash})
        run["multisig"]["M_watch"]["on_chain_match"] = on_chain == m_watch
        if on_chain != m_watch:
            run["steps"][-1]["as_expected"] = False

    # 6-7. The freezer cannot thaw (G3, measured on this profile).
    m, f, p = via_watchers("W1", call("Assets", "thaw_asset", {"id": asset_id}))
    r = submit(substrate, profile, keys["W1"], m, f, p, step="watcher_thaw_asset", call_label="Multisig.as_multi_threshold_1(Assets.thaw_asset)")
    step("watcher thaw_asset via M_watch is refused", "Err(Assets.NoPermission)", r, str(r.outcome) == "Err(Assets.NoPermission)")
    m, f, p = via_watchers("W1", call("Assets", "thaw", {"id": asset_id, "who": addr["Judge"]}))
    r = submit(substrate, profile, keys["W1"], m, f, p, step="watcher_thaw_account", call_label="Multisig.as_multi_threshold_1(Assets.thaw)")
    step("watcher thaw(holder) via M_watch is refused", "Err(Assets.NoPermission)", r, str(r.outcome) == "Err(Assets.NoPermission)")

    # 8. Observation (G3): does the pallet mint while the asset is frozen? (I7 is a bot rule either way.)
    r = submit(substrate, profile, keys["A"], "Assets", "mint",
               {"id": asset_id, "beneficiary": addr["Judge"], "amount": MINT_WHILE_FROZEN}, step="mint_while_frozen")
    step("observation: issuer mints 0.01 while frozen", "observe (I7 refuses in the bot)", r, True,
         ["Assets.Issued"] if has(r, "Assets.Issued") else [])

    # 9. The holder's transfer fails while frozen; the error name comes from the chain's metadata.
    r = submit(substrate, profile, keys["Judge"], "Assets", "transfer",
               {"id": asset_id, "target": addr["Peer"], "amount": TRANSFER}, step="transfer_frozen")
    frozen_ok = (not r.outcome.ok) and r.outcome.pallet == "Assets"
    step("holder transfer 1.00 while frozen fails", "Err(Assets.*) — name pinned from metadata", r, frozen_ok)
    run["frozen_transfer_error"] = str(r.outcome)
    run["state_checks"].append({"what": f"Peer balance after the frozen transfer", "observed": balance_of(substrate, asset_id, addr["Peer"], r.block_hash), "block_hash": r.block_hash})

    # 10-11. Control: the admin (A) thaws; the same transfer now succeeds.
    r = submit(substrate, profile, keys["A"], "Assets", "thaw_asset", {"id": asset_id}, step="admin_thaw")
    step("control: admin A thaws", "Ok + Assets.AssetThawed", r, r.outcome.ok and has(r, "Assets.AssetThawed"), ["Assets.AssetThawed"] if has(r, "Assets.AssetThawed") else [])
    run["state_checks"].append({"what": f"Asset({asset_id}).status after admin thaw", "observed": asset_status(substrate, asset_id, r.block_hash), "block_hash": r.block_hash})
    r = submit(substrate, profile, keys["Judge"], "Assets", "transfer",
               {"id": asset_id, "target": addr["Peer"], "amount": TRANSFER}, step="transfer_level")
    step("control: the same transfer succeeds", "Ok + Assets.Transferred", r, r.outcome.ok and has(r, "Assets.Transferred"), ["Assets.Transferred"] if has(r, "Assets.Transferred") else [])
    run["state_checks"].append({"what": f"Peer balance after the level transfer", "observed": balance_of(substrate, asset_id, addr["Peer"], r.block_hash), "block_hash": r.block_hash})

    mint_obs = next(s for s in run["steps"] if s["name"].startswith("observation"))
    run["observations"] = {
        "mint_while_frozen": mint_obs["receipt"]["outcome"]["text"]
        + (" + Assets.Issued" if "Assets.Issued" in mint_obs["events_seen"] else ""),
        "frozen_transfer_error": run["frozen_transfer_error"],
        "freezer_thaw_asset": run["steps"][6]["receipt"]["outcome"]["text"],
        "freezer_thaw_account": run["steps"][7]["receipt"]["outcome"]["text"],
    }
    run["finished_at"] = now()
    run["passed"] = sum(s["as_expected"] for s in run["steps"])
    run["verdict"] = "PASS" if run["passed"] == len(run["steps"]) else "FAIL"

    EVIDENCE.mkdir(exist_ok=True)
    out = EVIDENCE / f"spike-assets-{profile.name}-asset{asset_id}.json"
    out.write_text(json.dumps(run, indent=2) + "\n")
    md = write_receipts_md()
    print(f"\n[{profile.name}] {run['verdict']}: {run['passed']}/{len(run['steps'])} steps as expected; asset {asset_id}")
    print(f"observations: {json.dumps(run['observations'])}")
    print(f"evidence -> {out.relative_to(out.parent.parent)} · receipts -> {md.relative_to(md.parent.parent)}")
    return 0 if run["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
