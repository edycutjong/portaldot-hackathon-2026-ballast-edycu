#!/usr/bin/env python3
"""Role split, once per chain: breaker asset 1 + control asset 2 + their reserve vault + the ReserveOracle mirror.

  python scripts/setup_roles.py [--profile standin-upstream] [--url ws://127.0.0.1:49944] [--evm-url URL]

Portaldot (stand-in profiles only — dev keys):
  fund A, A2, B, W1, W2, judge, peer, and M_mint / M_admin / M_watch / the control asset's keyless owner (>= ED,
  `transfer_ownership` to an account below ED fails) -> A creates asset 1 (pUSDC-test) and asset 2 (pUSDC-ctl, 6
  decimals) -> A mints S2 = 50.00 of asset 2 to the peer (its one and only mint) -> asset 1:
  set_team(issuer=M_mint, admin=M_admin, freezer=M_watch) + transfer_ownership(M_mint) -> asset 2: every role to a
  keyless account blake2_256("ballast:a2-<role>:v1") -> B maps its account in Revive and deploys ReserveOracle
  (attester = B's H160).
Reserve (local anvil, labelled "local-anvil (not Sepolia)"; the Sepolia vault needs >= 100 test USDC): MockUSDC +
  ReserveVault, the custodian deposits S1 + S2 = 100.00 with a plain ERC-20 transfer.
Asset 1 is NOT minted here: its S1 = 50.00 is minted through M_mint, gated by the reserve bot (scripts/role_drill.py).
Writes deployments/<profile>.json (public addresses only) and evidence/roles-setup-<profile>.json.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ballast.chain import connect, dev_keypair, submit  # noqa: E402
from ballast.chain_profile import ProfileError, identify  # noqa: E402
from ballast.config import load_chain_config  # noqa: E402
from ballast.drill import artifact, forge_build, source_pin  # noqa: E402
from ballast.oracle import deploy as deploy_oracle  # noqa: E402
from ballast.oracle import initcode  # noqa: E402
from ballast.receipts import write_receipts_md  # noqa: E402
from ballast.roles import DEPLOYMENTS, Deployment, RoleMap, audit_team  # noqa: E402
from ballast.rpc import HttpRpc  # noqa: E402
from ballast.runlog import Run, now  # noqa: E402
from ballast.sepolia import ANVIL_CHAIN_ID  # noqa: E402
from ballast.watchdog import reserve_label  # noqa: E402

BREAKER, CONTROL = 1, 2
DECIMALS = 6
S1 = S2 = 50_000_000  # 50.00 each, 6 decimals like USDC
SUPPORTED = ("standin-upstream",)
KEYS = {"A": "//BallastA", "A2": "//BallastA2", "B": "//BallastB", "W1": "//BallastW1", "W2": "//BallastW2",
        "Judge": "//BallastJudge//roles", "Peer": "//BallastPeer//roles"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config")
    ap.add_argument("--profile")
    ap.add_argument("--url")
    ap.add_argument("--evm-url", default="http://127.0.0.1:49545", help="local anvil (chain id 31337)")
    args = ap.parse_args()
    from web3 import HTTPProvider, Web3

    try:
        cfg = load_chain_config(args.config, profile=args.profile, url=args.url)
        ident = identify(HttpRpc(cfg.url), cfg.profile.name, measure=False)
    except (ProfileError, OSError, ValueError) as exc:
        print(f"setup_roles: {exc}", file=sys.stderr)
        return 2
    profile = ident.profile
    if profile.name not in SUPPORTED:
        print(f"setup_roles: profile {profile.name!r} not supported (supported: {', '.join(SUPPORTED)})", file=sys.stderr)
        return 2
    if (DEPLOYMENTS / f"{profile.name}.json").exists():
        print(f"setup_roles: deployments/{profile.name}.json exists — the role split runs once per chain", file=sys.stderr)
        return 2
    w3 = Web3(HTTPProvider(args.evm_url, request_kwargs={"timeout": 10}))
    try:
        evm_chain = w3.eth.chain_id
    except Exception as exc:  # noqa: BLE001
        print(f"setup_roles: no EVM chain at {args.evm_url} ({type(exc).__name__}); scripts/anvil_local.sh start",
              file=sys.stderr)
        return 2
    if evm_chain != ANVIL_CHAIN_ID:
        print(f"setup_roles: {args.evm_url} is chain {evm_chain}; this setup uses a local anvil reserve only",
              file=sys.stderr)
        return 2
    print(ident.banner())
    substrate = connect(profile, cfg.url)
    for asset_id in (BREAKER, CONTROL):
        if substrate.query("Assets", "Asset", [asset_id]).value is not None:
            print(f"setup_roles: asset {asset_id} already exists on this chain", file=sys.stderr)
            return 2
    fmt = substrate.ss58_format or 42
    alice = dev_keypair(profile, "//Alice")
    keys = {role: dev_keypair(profile, uri) for role, uri in KEYS.items()}
    addr = {role: kp.ss58_address for role, kp in keys.items()}
    rm = RoleMap(a=addr["A"], a2=addr["A2"], b=addr["B"], watchers=(addr["W1"], addr["W2"]), ss58_format=fmt)
    role_of = {kp.ss58_address: role for role, kp in keys.items()} | {alice.ss58_address: "Alice, stand-in funder"}
    custodian = w3.eth.accounts[0]
    run = Run("roles-setup", {**ident.as_dict(), "url": cfg.url}, role_of, asset_id=BREAKER,
              assets={"breaker": BREAKER, "control": CONTROL, "S1": S1, "S2": S2, "decimals": DECIMALS},
              accounts={**addr, "M_mint": rm.m_mint, "M_admin": rm.m_admin, "M_watch": rm.m_watch,
                        "funder": alice.ss58_address},
              roles=rm.as_dict(), dev_key_uris=KEYS,
              reserve={"label": reserve_label(evm_chain), "evm_chain_id": evm_chain, "evm_url": args.evm_url,
                       "custodian": custodian})

    def call(module: str, function: str, params: dict):
        return substrate.compose_call(call_module=module, call_function=function, call_params=params)

    def has(r, *events: str) -> bool:
        return all(e in r.event_names() for e in events)

    def evm(name: str, tx) -> dict:
        rcpt = w3.eth.wait_for_transaction_receipt(tx, timeout=30)
        return run.evm_step({"name": name, "expected": "status 1", "as_expected": rcpt["status"] == 1,
                             "counted": True, "chain": run["reserve"]["label"],
                             "tx_hash": rcpt["transactionHash"].to_0x_hex(), "block_number": rcpt["blockNumber"],
                             "block_hash": rcpt["blockHash"].to_0x_hex(), "status": rcpt["status"],
                             "from": rcpt["from"], "to": rcpt["to"], "contract": rcpt["contractAddress"]})

    deployment = None
    try:
        # Reserve: vault on the local anvil chain, deposit S1 + S2 as a plain ERC-20 transfer.
        forge_build()
        usdc_abi, usdc_bin = artifact("MockUSDC")
        vault_abi, vault_bin = artifact("ReserveVault")
        run["source"] = source_pin() | {
            "ReserveVault_initcode_sha256": hashlib.sha256(bytes.fromhex(vault_bin[2:])).hexdigest(),
            "MockUSDC_initcode_sha256": hashlib.sha256(bytes.fromhex(usdc_bin[2:])).hexdigest(),
            "ReserveOracle_initcode_sha256": hashlib.sha256(initcode()).hexdigest(),
        }
        usdc_addr = evm("deploy MockUSDC (test-only token)",
                        w3.eth.contract(abi=usdc_abi, bytecode=usdc_bin).constructor().transact({"from": custodian}))["contract"]
        vault_addr = evm("deploy ReserveVault(usdc) — owner = custodian",
                         w3.eth.contract(abi=vault_abi, bytecode=vault_bin).constructor(usdc_addr)
                         .transact({"from": custodian}))["contract"]
        usdc = w3.eth.contract(address=usdc_addr, abi=usdc_abi)
        vault = w3.eth.contract(address=vault_addr, abi=vault_abi)
        evm("custodian receives 100.00 test tokens", usdc.functions.mint(custodian, S1 + S2).transact({"from": custodian}))
        evm("deposit S1 + S2 = 100.00 — plain ERC-20 transfer into the vault",
            usdc.functions.transfer(vault_addr, S1 + S2).transact({"from": custodian}))
        run["reserve"] |= {"vault": vault_addr, "usdc": usdc_addr}
        run.check("vault reserves() after the deposit", vault.functions.reserves().call(), S1 + S2, "evm latest")

        # Portaldot: fund every account that signs or holds a role.
        const = lambda pallet, name: substrate.get_constant(pallet, name).value  # noqa: E731
        ed = const("Balances", "ExistentialDeposit")
        per_asset = (const("Assets", "AssetDeposit") + const("Assets", "MetadataDepositBase")
                     + 2 * len("pUSDC-test") * const("Assets", "MetadataDepositPerByte"))
        msig = const("Multisig", "DepositBase") + 3 * const("Multisig", "DepositFactor")
        fund = [(addr["A"], 2 * per_asset + 20 * msig + 100 * ed), (addr["A2"], 10 * msig + 100 * ed),
                (addr["B"], 20 * msig + 10 * per_asset + 1000 * ed), (addr["W1"], 100 * ed), (addr["W2"], 100 * ed),
                (addr["Judge"], 100 * ed), (addr["Peer"], 100 * ed), (rm.m_mint, 10 * ed), (rm.m_admin, 10 * ed),
                (rm.m_watch, 10 * ed), (rm.control["owner"], 10 * ed)]
        r = submit(substrate, profile, alice, "Utility", "batch_all",
                   {"calls": [call("Balances", "transfer_keep_alive", {"dest": who, "value": v}) for who, v in fund]},
                   step="fund", call_label=f"Utility.batch_all[{len(fund)} x Balances.transfer_keep_alive]")
        run.step("fund A, A2, B, W1, W2, judge, peer, M_mint, M_admin, M_watch, asset-2 keyless owner (>= ED)", "Ok",
                 r, r.outcome.ok)

        for asset_id, symbol in ((BREAKER, "pUSDC-test"), (CONTROL, "pUSDC-ctl")):
            r = submit(substrate, profile, keys["A"], "Assets", "create",
                       {"id": asset_id, "admin": addr["A"], "min_balance": 1}, step=f"create_{asset_id}")
            run.step(f"A creates asset {asset_id}", "Ok + Assets.Created", r, r.outcome.ok and has(r, "Assets.Created"),
                     ("Assets.Created",))
            r = submit(substrate, profile, keys["A"], "Assets", "set_metadata",
                       {"id": asset_id, "name": symbol, "symbol": symbol, "decimals": DECIMALS},
                       step=f"set_metadata_{asset_id}")
            run.step(f"set_metadata {symbol} ({DECIMALS} decimals)", "Ok + Assets.MetadataSet", r,
                     r.outcome.ok and has(r, "Assets.MetadataSet"), ("Assets.MetadataSet",))

        r = submit(substrate, profile, keys["A"], "Assets", "mint",
                   {"id": CONTROL, "beneficiary": addr["Peer"], "amount": S2}, step="mint_s2")
        run.step("A mints S2 = 50.00 of control asset 2 to the peer (its only mint)", "Ok + Assets.Issued", r,
                 r.outcome.ok and has(r, "Assets.Issued"), ("Assets.Issued",))

        team = rm.breaker_team()
        r = submit(substrate, profile, keys["A"], "Assets", "set_team",
                   {"id": BREAKER, "issuer": team["issuer"], "admin": team["admin"], "freezer": team["freezer"]},
                   step="set_team_1")
        run.step("asset 1 set_team(issuer=M_mint, admin=M_admin, freezer=M_watch)", "Ok + Assets.TeamChanged", r,
                 r.outcome.ok and has(r, "Assets.TeamChanged"), ("Assets.TeamChanged",))
        r = submit(substrate, profile, keys["A"], "Assets", "transfer_ownership", {"id": BREAKER, "owner": rm.m_mint},
                   step="transfer_ownership_1")
        run.step("asset 1 transfer_ownership(M_mint 2-of-2 {A, B})", "Ok + Assets.OwnerChanged", r,
                 r.outcome.ok and has(r, "Assets.OwnerChanged"), ("Assets.OwnerChanged",))
        details1 = substrate.query("Assets", "Asset", [BREAKER], block_hash=r.block_hash).value
        run.check("asset 1 team == role map (owner/issuer = M_mint, admin = M_admin, freezer = M_watch)",
                  audit_team(details1, team), [], r.block_hash)

        ctl = rm.control_team()
        r = submit(substrate, profile, keys["A"], "Assets", "set_team",
                   {"id": CONTROL, "issuer": ctl["issuer"], "admin": ctl["admin"], "freezer": ctl["freezer"]},
                   step="set_team_2")
        run.step("asset 2 set_team(keyless issuer, admin, freezer)", "Ok + Assets.TeamChanged", r,
                 r.outcome.ok and has(r, "Assets.TeamChanged"), ("Assets.TeamChanged",))
        r = submit(substrate, profile, keys["A"], "Assets", "transfer_ownership", {"id": CONTROL, "owner": ctl["owner"]},
                   step="transfer_ownership_2")
        run.step("asset 2 transfer_ownership(keyless owner)", "Ok + Assets.OwnerChanged", r,
                 r.outcome.ok and has(r, "Assets.OwnerChanged"), ("Assets.OwnerChanged",))
        details2 = substrate.query("Assets", "Asset", [CONTROL], block_hash=r.block_hash).value
        run.check("asset 2 team == keyless accounts (S2 can never change)", audit_team(details2, ctl), [], r.block_hash)
        run.check("supply S1 (asset 1) before the gated mint", details1["supply"], 0, r.block_hash)
        run.check("supply S2 (asset 2)", details2["supply"], S2, r.block_hash)

        # A cannot act alone any more: a direct mint by A is refused by the pallet.
        r = submit(substrate, profile, keys["A"], "Assets", "mint",
                   {"id": BREAKER, "beneficiary": addr["A"], "amount": 1}, step="a_alone_mint")
        run.step("A alone tries to mint asset 1 (issuer is M_mint)", "Err(Assets.NoPermission)", r,
                 str(r.outcome) == "Err(Assets.NoPermission)")

        # ReserveOracle mirror on Revive (stand-in: Revive accepts EVM bytecode; V3 deploy at gate G4).
        if not substrate.query("Revive", "OriginalAccount", [_h160(substrate, addr["B"])]).value:
            r = submit(substrate, profile, keys["B"], "Revive", "map_account", {}, step="map_b")
            run.step("B maps its account in Revive", "Ok", r, r.outcome.ok)
        r, contract, attester = deploy_oracle(substrate, profile, keys["B"])
        run.step(f"B deploys ReserveOracle(attester = {attester})", "Ok + Revive.Instantiated", r,
                 r.outcome.ok and contract is not None, ("Revive.Instantiated",))
        if not contract:
            raise RuntimeError("no Revive.Instantiated event")
        run["oracle"] = {"address": contract, "attester": attester, "deploy_extrinsic": r.extrinsic_id}

        deployment = Deployment(
            profile=profile.name, genesis_hash=ident.facts.genesis_hash, breaker=BREAKER, control=CONTROL,
            decimals=DECIMALS, s2=S2, roles=rm.as_dict(),
            reserve={"label": run["reserve"]["label"], "evm_chain_id": evm_chain, "vault": vault_addr,
                     "token": usdc_addr, "custodian": custodian},
            oracle={"address": contract, "attester": attester, "chain": profile.label},
            created_at=now(), setup_evidence=f"roles-setup-{profile.name}.json")
    except Exception as exc:  # noqa: BLE001 — keep every receipt that landed
        run["error"] = f"{type(exc).__name__}: {exc}"
        traceback.print_exc()
    run.finish(f"roles-setup-{profile.name}.json")
    if deployment is not None and run["verdict"] == "PASS":
        print(f"deployment -> {deployment.save().relative_to(DEPLOYMENTS.parent)}")
    write_receipts_md()
    return 0 if run["verdict"] == "PASS" else 1


def _h160(substrate, ss58: str) -> str:
    from ballast.revive import eth_address

    return eth_address(substrate, ss58)


if __name__ == "__main__":
    sys.exit(main())
