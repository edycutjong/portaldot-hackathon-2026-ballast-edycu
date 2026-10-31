#!/usr/bin/env python3
"""Read-only snapshot for the static fallback of the reserves page (https://ballast.edycu.dev/reserves/).

  python scripts/reserves_snapshot.py [--out docs/reserves/snapshot.json]

Reads, with no key and no transaction: the Sepolia ReserveVault's test-USDC balance from both providers (latest and
finalized), the V3 supply + status of assets 4401 / 4402 at the finalized head, and the ReserveOracle mirror's
`status()` over the V3 EVM RPC. Writes the JSON the page falls back to when a live read fails, and a copy under
evidence/reserves-snapshot-<stamp>.json (the page prints the timestamp and says "static snapshot").
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from web3 import HTTPProvider, Web3  # noqa: E402

from ballast.chain import connect  # noqa: E402
from ballast.config import load_chain_config  # noqa: E402
from ballast.roles import Deployment  # noqa: E402
from ballast.sepolia import SEPOLIA_PROVIDERS, SEPOLIA_USDC  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EVM_RPC = "https://test-evm-rpc-v3.portaldot.dev"
BALANCE_OF = "0x70a08231"
STATUS = "0x200d2ed2"  # ReserveOracle.status()
STATUS_NAMES = {0: "Live", 1: "Frozen", 2: "Destroying"}


def call(w3: Web3, to: str, data: str, block="latest") -> bytes:
    return bytes(w3.eth.call({"to": Web3.to_checksum_address(to), "data": data}, block))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=str(ROOT / "docs" / "reserves" / "snapshot.json"))
    args = ap.parse_args()
    dep = json.loads((ROOT / "deployments" / "v3-sepolia.json").read_text())
    vault = dep["reserve"]["vault"]
    data = BALANCE_OF + "0" * 24 + vault[2:].lower()
    sepolia = {"vault": vault, "token": SEPOLIA_USDC, "providers": []}
    for name, url in SEPOLIA_PROVIDERS:
        w3 = Web3(HTTPProvider(url, request_kwargs={"timeout": 20}))
        row: dict = {"name": name}
        for tag in ("latest", "finalized"):
            block = w3.eth.get_block(tag)
            row[tag] = {"block": block["number"], "balance": int.from_bytes(call(w3, SEPOLIA_USDC, data, block["number"]), "big")}
        sepolia["providers"].append(row)

    cfg = load_chain_config(None, profile="v3", url=None)
    sub = connect(cfg.profile, cfg.url)
    fin_hash = sub.get_chain_finalised_head()
    fin_number = sub.get_block_number(fin_hash)
    assets = {}
    for a in (dep["breaker"], dep["control"]):
        d = sub.query("Assets", "Asset", [a], block_hash=fin_hash).value
        assets[str(a)] = {"supply": d["supply"], "status": d["status"],
                          "storage_key": sub.create_storage_key("Assets", "Asset", [a]).to_hex()}
    oracle_addr = Deployment.load("v3").oracle["address"]
    evm = Web3(HTTPProvider(EVM_RPC, request_kwargs={"timeout": 20, "headers": {"User-Agent": "Mozilla/5.0 ballast-snapshot", "Content-Type": "application/json"}}))
    raw = call(evm, oracle_addr, STATUS)
    word = lambda i: int.from_bytes(raw[32 * i:32 * (i + 1)], "big")  # noqa: E731
    oracle = {"address": oracle_addr, "s1": word(0), "s2": word(1), "reserves": word(2), "sep_block": word(3),
              "sep_hash": "0x" + raw[128:160].hex(), "pd_block": word(5), "frozen": bool(word(6)), "updated_at": word(7)}

    out = {"generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "kind": "reserves-snapshot (read-only; no transaction)", "sepolia": sepolia,
           "v3": {"genesis": dep["genesis_hash"], "finalized_block": fin_number, "finalized_hash": fin_hash, "assets": assets},
           "oracle": oracle}
    text = json.dumps(out, indent=2) + "\n"
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(text)
    ev = ROOT / "evidence" / f"reserves-snapshot-{out['generated_at'].replace('-', '').replace(':', '')}.json"
    ev.write_text(text)
    print(f"snapshot {out['generated_at']} -> {args.out} and evidence/{ev.name}")
    print(json.dumps({"sepolia": [(p["name"], p["finalized"]["balance"]) for p in sepolia["providers"]],
                      "v3": {k: (v["supply"], v["status"]) for k, v in assets.items()}, "oracle_pd_block": oracle["pd_block"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
