#!/usr/bin/env python3
"""V3 day-0 check, read-only: identity, pallets/calls Ballast uses, deposits, block time, EVM chain id.

Writes evidence/v3-day0-<UTC>.json. Sends nothing. Usage:
    python scripts/v3_day0.py [--url wss://test-node-v3.portaldot.dev] [--evm https://test-evm-rpc-v3.portaldot.dev]
                              [--account <ss58> ...]
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from substrateinterface import SubstrateInterface  # noqa: E402

from ballast.chain_profile import MIN_SAMPLE_BLOCKS, observe  # noqa: E402
from ballast.rpc import node_rpc  # noqa: E402

PALLETS = ("Assets", "Multisig", "Utility", "Revive", "Sudo", "Proxy", "System", "Balances")
CONSTANTS = {
    "Balances": ("ExistentialDeposit",),
    "Assets": ("AssetDeposit", "AssetAccountDeposit", "MetadataDepositBase", "MetadataDepositPerByte", "StringLimit"),
    "Multisig": ("DepositBase", "DepositFactor", "MaxSignatories"),
    "Revive": ("DepositPerByte", "DepositPerItem", "AllowEVMBytecode", "ChainId"),
}


def evm(url: str, method: str) -> str:
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": []}).encode()
    # The endpoint's CDN refuses urllib's default User-Agent (Cloudflare error 1010).
    headers = {"Content-Type": "application/json", "User-Agent": "ballast-v3-day0/1"}
    req = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read())["result"]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--url", default="wss://test-node-v3.portaldot.dev")
    ap.add_argument("--evm", default="https://test-evm-rpc-v3.portaldot.dev")
    ap.add_argument("--account", action="append", default=[], help="public SS58 address to report the free balance of")
    ap.add_argument("--dry-run-origin", help="any FUNDED public address to size the ReserveOracle deploy from "
                    "(ReviveApi_instantiate state_call: nothing is signed or sent)")
    ap.add_argument("--out", type=Path, default=ROOT / "evidence")
    args = ap.parse_args(argv)

    started = datetime.now(timezone.utc)
    facts = observe(node_rpc(args.url), sample_blocks=MIN_SAMPLE_BLOCKS)
    sub = SubstrateInterface(url=args.url, ws_options={"timeout": 60})
    sub.init_runtime()
    props = sub.rpc_request("system_properties", [])["result"]
    chain = sub.rpc_request("system_chain", [])["result"]
    version = sub.rpc_request("system_version", [])["result"]
    rt = sub.rpc_request("state_getRuntimeVersion", [])["result"]

    pallets: dict[str, list[str] | None] = {}
    by_name = {p.name: p for p in sub.metadata.pallets}
    for name in PALLETS:
        p = by_name.get(name)
        pallets[name] = None if p is None else [c.name for c in (p.calls or [])]
    as_multi_args = None
    if by_name.get("Multisig"):
        call = sub.get_metadata_call_function("Multisig", "as_multi")
        as_multi_args = {a["name"]: a["typeName"] for a in call.value["fields"]}

    constants: dict[str, dict[str, object]] = {}
    for pallet, names in CONSTANTS.items():
        for n in names:
            try:
                c = sub.get_constant(pallet, n)
                constants.setdefault(pallet, {})[n] = c.value if c is not None else None
            except Exception as exc:  # noqa: BLE001 — a missing constant is a finding, not a crash
                constants.setdefault(pallet, {})[n] = f"unavailable: {type(exc).__name__}"

    balances = {}
    for who in args.account:
        acct = sub.query("System", "Account", [who]).value
        balances[who] = {"free": acct["data"]["free"], "nonce": acct["nonce"]}

    sudo_key = sub.query("Sudo", "Key").value if pallets.get("Sudo") is not None else None
    oracle_dry_run = None
    if args.dry_run_origin:
        from eth_abi import encode

        from ballast.oracle import initcode
        from ballast.revive import dry_instantiate

        code = initcode() + encode(["address"], ["0x" + "11" * 20])
        res = dry_instantiate(sub, args.dry_run_origin, code)
        oracle_dry_run = {"origin": args.dry_run_origin, "init_code_bytes": len(code), "ok": res.ok,
                          "reverted": res.reverted, "storage_deposit": res.storage_deposit,
                          "note": "ReviveApi_instantiate state_call with a placeholder attester; nothing signed or sent"}

    out = {
        "written_by": "ballast scripts/v3_day0.py (read-only, sends nothing)",
        "checked_at_utc": started.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "endpoint": args.url,
        "system_chain": chain,
        "system_version": version,
        "genesis_hash": facts.genesis_hash,
        "code_hash": facts.code_hash,
        "spec_name": rt["specName"],
        "spec_version": rt["specVersion"],
        "transaction_version": rt["transactionVersion"],
        "system_properties": props,
        "head": facts.head,
        "block_time_ms": {"median": facts.block_time_ms, "mean": facts.mean_block_time_ms, "blocks": facts.sample_blocks},
        "pallets": pallets,
        "multisig_as_multi_args": as_multi_args,
        "constants": constants,
        "balances": balances,
        "sudo_key": sudo_key,
        "reserve_oracle_dry_run": oracle_dry_run,
        "evm": {"url": args.evm, "eth_chainId": evm(args.evm, "eth_chainId"), "eth_blockNumber": evm(args.evm, "eth_blockNumber")},
    }
    args.out.mkdir(parents=True, exist_ok=True)
    path = args.out / f"v3-day0-{started.strftime('%Y%m%dT%H%M%SZ')}.json"
    path.write_text(json.dumps(out, indent=2, default=str) + "\n")
    print(json.dumps({k: out[k] for k in ("genesis_hash", "code_hash", "spec_name", "spec_version", "head", "block_time_ms")}))
    print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
