#!/usr/bin/env python3
"""S0 spike: Assets role split + watcher-set freeze, end to end, on the configured chain profile.

  python scripts/spike_assets.py [--profile standin-upstream] [--url ws://127.0.0.1:49944]

Dev keys -> assets.create (free asset id) -> set_metadata (pUSDC-test) -> set_team(issuer=A, admin=A,
freezer=M_watch) where M_watch = 1-of-2 watcher multisig {W1, W2} -> mint to a holder -> W2 freezes the
asset through multisig.as_multi_threshold_1 -> a watcher's thaw is refused (error decoded) -> the holder's
transfer fails while frozen (error name read from metadata) -> control: A thaws -> the same transfer
succeeds. Every step is a real extrinsic; state is re-read at the step's block. Receipts go to evidence/
and docs/RECEIPTS.md, each labelled with the chain profile. Dev keys are refused on anything but a stand-in.
The evidence file is written even if a step errors (verdict ERROR).
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ballast.chain import Receipt, connect, dev_keypair, submit  # noqa: E402
from ballast.chain_profile import SHAPE_WEIGHT_V2, identify, require_multisig_shape  # noqa: E402
from ballast.config import load_chain_config  # noqa: E402
from ballast.multisig import multi_address, other_signatories, public_key  # noqa: E402
from ballast.receipts import EVIDENCE, score, summarize, write_receipts_md  # noqa: E402
from ballast.rpc import HttpRpc  # noqa: E402

SPIKE_ASSET_FROM = 1001  # spike assets live at >= 1001; ids 1 and 2 stay free for the breaker + control assets
DECIMALS = 6
MINT = 50_000_000  # 50.00 pUSDC-test
MINT_WHILE_FROZEN = 10_000  # 0.01: does the pallet mint while the asset is frozen? (observation)
TRANSFER = 1_000_000  # 1.00
# Asset-frozen transfer errors seen across runtimes: AssetNotLive (polkadot-sdk), Frozen (spec 1002)
FROZEN_TRANSFER_ERRORS = {"Err(Assets.AssetNotLive)", "Err(Assets.Frozen)"}


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def same_account(a: str | None, b: str | None) -> bool:
    return a is not None and b is not None and public_key(a) == public_key(b)


def free_asset_id(substrate, start: int) -> int:
    asset_id = start
    while substrate.query("Assets", "Asset", [asset_id]).value is not None:
        asset_id += 1
    return asset_id


def asset_details(substrate, asset_id: int, block_hash: str) -> dict:
    return substrate.query("Assets", "Asset", [asset_id], block_hash=block_hash).value or {}


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
    m_watch = multi_address(watchers, 1, ss58_format=substrate.ss58_format or 42)
    sdk_m_watch = substrate.generate_multisig_account(watchers, 1).ss58_address
    if not same_account(sdk_m_watch, m_watch):
        print(f"FAIL: M_watch derivation {m_watch} != SDK {sdk_m_watch}")
        return 1
    print(f"M_watch (1-of-2 {{W1, W2}}) = {m_watch} (matches the SDK derivation)")

    const = lambda pallet, name: substrate.get_constant(pallet, name).value  # noqa: E731
    deposits = {
        "Balances.ExistentialDeposit": const("Balances", "ExistentialDeposit"),
        "Assets.AssetDeposit": const("Assets", "AssetDeposit"),
        "Assets.MetadataDepositBase": const("Assets", "MetadataDepositBase"),
        "Assets.MetadataDepositPerByte": const("Assets", "MetadataDepositPerByte"),
    }
    ed = deposits["Balances.ExistentialDeposit"]
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

    def step(name: str, expected: str, r: Receipt, ok: bool, events: tuple[str, ...] = (), counted: bool = True):
        seen = [e for e in events if e in r.event_names()]
        run["steps"].append(
            {
                "name": name,
                "expected": expected,
                "as_expected": ok,
                "counted": counted,
                "signer_role": role_of.get(r.signer, r.signer),
                "events_seen": seen,
                "receipt": r.as_dict(),
            }
        )
        mark = "PASS" if ok else "FAIL"
        if not counted:
            mark = "OBS "
        print(f"{mark} {r.extrinsic_id:>9} {r.call:<52} {r.outcome}  {name}")
        return r

    def check(what: str, observed, expected, block_hash: str, ok: bool | None = None) -> bool:
        ok = (observed == expected) if ok is None else ok
        run["state_checks"].append(
            {"what": what, "expected": expected, "observed": observed, "ok": ok, "block_hash": block_hash}
        )
        print(f"     {'ok  ' if ok else 'FAIL'} state: {what}: {observed}")
        return ok

    def has_all(r: Receipt, *events: str) -> bool:
        return all(e in r.event_names() for e in events)

    def call(module: str, function: str, params: dict):
        return substrate.compose_call(call_module=module, call_function=function, call_params=params)

    def via_watchers(signer: str, inner) -> tuple[str, str, dict]:
        others = other_signatories(watchers, addr[signer], ss58_format=substrate.ss58_format or 42)
        return "Multisig", "as_multi_threshold_1", {"other_signatories": others, "call": inner}

    try:
        # 0. Fund the dev accounts and M_watch (>= ED) from //Alice (stand-in only), in multiples of the
        #    chain's own ED and deposits, so no decimals are assumed.
        name_bytes = 2 * len("pUSDC-test")
        a_needs = 2 * (
            deposits["Assets.AssetDeposit"]
            + deposits["Assets.MetadataDepositBase"]
            + name_bytes * deposits["Assets.MetadataDepositPerByte"]
        ) + 10 * ed
        fund = [
            call("Balances", "transfer_keep_alive", {"dest": who, "value": amount})
            for who, amount in (
                (addr["A"], a_needs),
                (addr["W1"], 10 * ed),
                (addr["W2"], 10 * ed),
                (addr["Judge"], 10 * ed),
                (addr["Peer"], 10 * ed),
                (m_watch, 2 * ed),
            )
        ]
        r = submit(substrate, profile, alice, "Utility", "batch_all", {"calls": fund}, step="fund",
                   call_label="Utility.batch_all[6 x Balances.transfer_keep_alive]")
        step("fund A, W1, W2, judge, peer, M_watch (>= ED)", "Ok", r, r.outcome.ok)
        check("M_watch native balance >= ED", substrate.query("System", "Account", [m_watch], block_hash=r.block_hash)
              .value["data"]["free"] >= ed, True, r.block_hash)

        # 1-3. Asset with a split team: issuer = admin = A, freezer = the watcher multisig.
        r = submit(substrate, profile, keys["A"], "Assets", "create",
                   {"id": asset_id, "admin": addr["A"], "min_balance": 1}, step="create")
        step("create the asset", "Ok + Assets.Created", r, r.outcome.ok and has_all(r, "Assets.Created"), ("Assets.Created",))
        r = submit(substrate, profile, keys["A"], "Assets", "set_metadata",
                   {"id": asset_id, "name": "pUSDC-test", "symbol": "pUSDC-test", "decimals": DECIMALS}, step="set_metadata")
        step("set_metadata pUSDC-test", "Ok + Assets.MetadataSet", r, r.outcome.ok and has_all(r, "Assets.MetadataSet"),
             ("Assets.MetadataSet",))
        r = submit(substrate, profile, keys["A"], "Assets", "set_team",
                   {"id": asset_id, "issuer": addr["A"], "admin": addr["A"], "freezer": m_watch}, step="set_team")
        step("set_team(issuer=A, admin=A, freezer=M_watch)", "Ok + Assets.TeamChanged", r,
             r.outcome.ok and has_all(r, "Assets.TeamChanged"), ("Assets.TeamChanged",))
        team = asset_details(substrate, asset_id, r.block_hash)
        check(f"Asset({asset_id}) freezer is M_watch", same_account(team.get("freezer"), m_watch), True, r.block_hash)
        check(f"Asset({asset_id}) issuer and admin are A",
              same_account(team.get("issuer"), addr["A"]) and same_account(team.get("admin"), addr["A"]), True, r.block_hash)

        # 4. Mint to the holder.
        r = submit(substrate, profile, keys["A"], "Assets", "mint",
                   {"id": asset_id, "beneficiary": addr["Judge"], "amount": MINT}, step="mint")
        step("mint 50.00 to the holder", "Ok + Assets.Issued", r, r.outcome.ok and has_all(r, "Assets.Issued"), ("Assets.Issued",))
        check("holder balance after mint", balance_of(substrate, asset_id, addr["Judge"], r.block_hash), MINT, r.block_hash)

        # 5. Watcher 2 alone freezes the asset through the 1-of-2 watcher multisig.
        m, f, p = via_watchers("W2", call("Assets", "freeze_asset", {"id": asset_id}))
        r = submit(substrate, profile, keys["W2"], m, f, p, step="freeze",
                   call_label="Multisig.as_multi_threshold_1(Assets.freeze_asset)")
        step("W2 freezes via M_watch (1-of-2)", "Ok + Assets.AssetFrozen", r,
             r.outcome.ok and has_all(r, "Assets.AssetFrozen") and all(o.ok for o in r.inner), ("Assets.AssetFrozen",))
        check(f"Asset({asset_id}).status after freeze", asset_details(substrate, asset_id, r.block_hash).get("status"),
              "Frozen", r.block_hash)
        executed = [e for e in r.events if (e["module_id"], e["event_id"]) == ("Multisig", "MultisigExecuted")]
        if executed or shape == SHAPE_WEIGHT_V2:  # polkadot-sdk runtimes name the dispatching multisig here
            on_chain = executed[0]["attributes"]["multisig"] if executed else None
            run["multisig"]["M_watch"]["on_chain_match"] = same_account(on_chain, m_watch)
            check("MultisigExecuted.multisig is the locally derived M_watch", on_chain, m_watch, r.block_hash,
                  ok=same_account(on_chain, m_watch))

        # 6-7. The freezer cannot thaw: neither the asset nor a single account.
        m, f, p = via_watchers("W1", call("Assets", "thaw_asset", {"id": asset_id}))
        r = submit(substrate, profile, keys["W1"], m, f, p, step="watcher_thaw_asset",
                   call_label="Multisig.as_multi_threshold_1(Assets.thaw_asset)")
        step("watcher thaw_asset via M_watch is refused", "Err(Assets.NoPermission)", r,
             str(r.outcome) == "Err(Assets.NoPermission)" or [str(o) for o in r.inner] == ["Err(Assets.NoPermission)"])
        check(f"Asset({asset_id}).status after the refused thaw", asset_details(substrate, asset_id, r.block_hash).get("status"),
              "Frozen", r.block_hash)
        m, f, p = via_watchers("W1", call("Assets", "thaw", {"id": asset_id, "who": addr["Judge"]}))
        r = submit(substrate, profile, keys["W1"], m, f, p, step="watcher_thaw_account",
                   call_label="Multisig.as_multi_threshold_1(Assets.thaw)")
        step("watcher thaw(holder) via M_watch is refused", "Err(Assets.NoPermission)", r,
             str(r.outcome) == "Err(Assets.NoPermission)" or [str(o) for o in r.inner] == ["Err(Assets.NoPermission)"])

        # 8. Observation, not counted: does the pallet mint while the asset is frozen?
        r = submit(substrate, profile, keys["A"], "Assets", "mint",
                   {"id": asset_id, "beneficiary": addr["Judge"], "amount": MINT_WHILE_FROZEN}, step="mint_while_frozen")
        step("observation: issuer mints 0.01 while frozen", "observation only (not counted)", r, True,
             ("Assets.Issued",), counted=False)

        # 9. The holder's transfer fails while frozen; the error name comes from the chain's metadata.
        r = submit(substrate, profile, keys["Judge"], "Assets", "transfer",
                   {"id": asset_id, "target": addr["Peer"], "amount": TRANSFER}, step="transfer_frozen")
        step("holder transfer 1.00 while frozen fails", " or ".join(sorted(FROZEN_TRANSFER_ERRORS)), r,
             str(r.outcome) in FROZEN_TRANSFER_ERRORS)
        run["frozen_transfer_error"] = str(r.outcome)
        check("peer balance after the frozen transfer", balance_of(substrate, asset_id, addr["Peer"], r.block_hash), 0, r.block_hash)

        # 10-11. Control: the admin (A) thaws; the same transfer now succeeds.
        r = submit(substrate, profile, keys["A"], "Assets", "thaw_asset", {"id": asset_id}, step="admin_thaw")
        step("control: admin A thaws", "Ok + Assets.AssetThawed", r, r.outcome.ok and has_all(r, "Assets.AssetThawed"),
             ("Assets.AssetThawed",))
        check(f"Asset({asset_id}).status after admin thaw", asset_details(substrate, asset_id, r.block_hash).get("status"),
              "Live", r.block_hash)
        r = submit(substrate, profile, keys["Judge"], "Assets", "transfer",
                   {"id": asset_id, "target": addr["Peer"], "amount": TRANSFER}, step="transfer_level")
        step("control: the same transfer succeeds", "Ok + Assets.Transferred", r,
             r.outcome.ok and has_all(r, "Assets.Transferred"), ("Assets.Transferred",))
        check("peer balance after the level transfer", balance_of(substrate, asset_id, addr["Peer"], r.block_hash),
              TRANSFER, r.block_hash)

        by_step = {s["receipt"]["step"]: s for s in run["steps"]}
        mint_obs = by_step["mint_while_frozen"]
        run["observations"] = {
            "mint_while_frozen": mint_obs["receipt"]["outcome"]["text"]
            + (" + Assets.Issued" if mint_obs["events_seen"] else ""),
            "frozen_transfer_error": run["frozen_transfer_error"],
            "freezer_thaw_asset": by_step["watcher_thaw_asset"]["receipt"]["outcome"]["text"],
            "freezer_thaw_account": by_step["watcher_thaw_account"]["receipt"]["outcome"]["text"],
        }
    except Exception as exc:  # keep the receipts of every extrinsic that did land
        run["error"] = f"{type(exc).__name__}: {exc}"
        traceback.print_exc()
    finally:
        run["finished_at"] = now()
        summarize(run)
        EVIDENCE.mkdir(exist_ok=True)
        out = EVIDENCE / f"spike-assets-{profile.name}-asset{asset_id}.json"
        out.write_text(json.dumps(run, indent=2) + "\n")
        md = write_receipts_md()

    print(f"\n[{profile.name}] {run['verdict']}: {score(run)}; asset {asset_id}")
    print(f"observations: {json.dumps(run.get('observations', {}))}")
    print(f"evidence -> {out.relative_to(out.parent.parent)} · receipts -> {md.relative_to(md.parent.parent)}")
    return 0 if run["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
