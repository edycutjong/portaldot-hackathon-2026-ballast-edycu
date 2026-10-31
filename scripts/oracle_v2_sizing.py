#!/usr/bin/env python3
"""Read-only V3 probe: Ballast key balances, a dry-run deploy of ReserveOracle v2 from B, and the live v1 mirror's
status() / isBacked() (nothing is submitted).

  python scripts/oracle_v2_sizing.py > evidence/v3-oracle-v2-sizing-<date>.json
"""

import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ballast.chain import connect  # noqa: E402
from ballast.chain_profile import get_profile  # noqa: E402
from ballast.keys import keypair  # noqa: E402
from ballast.oracle import constructor_args, initcode, is_backed, status  # noqa: E402
from ballast.roles import Deployment  # noqa: E402
from ballast.revive import dry_instantiate, eth_address  # noqa: E402

ROLES = {"funder": "//Alice", "a": "//BallastA", "a2": "//BallastA2", "a3": "//BallastA3", "b": "//BallastB",
         "w1": "//BallastW1", "w2": "//BallastW2", "w3": "//BallastW3", "judge": "//BallastJudge",
         "peer": "//BallastPeer"}


def main() -> int:
    profile = get_profile("v3")
    substrate = connect(profile, profile.default_url)
    head = substrate.get_block_number(None)
    block_hash = substrate.get_block_hash(head)
    balances = {}
    for role, uri in ROLES.items():
        data = substrate.query("System", "Account", [keypair(profile, uri).ss58_address], block_hash=block_hash).value["data"]
        balances[role] = {"free_tpot": round(data["free"] / 1e14, 4), "reserved_tpot": round(data["reserved"] / 1e14, 4)}
    b = keypair(profile, "//BallastB").ss58_address
    watchers = [eth_address(substrate, keypair(profile, u).ss58_address) for u in ("//BallastW1", "//BallastW2")]
    dry = dry_instantiate(substrate, b, initcode() + constructor_args(eth_address(substrate, b), watchers))
    v1 = Deployment.load("v3").oracle["address"]
    v1_status = {k: (v.hex() if isinstance(v, bytes) else v) for k, v in status(substrate, b, v1, block_hash).items()}
    print(json.dumps({
        "kind": "v3-oracle-v2-sizing", "read_only": True, "chain": "Portaldot V3 testnet",
        "at": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), "head": head, "head_hash": block_hash,
        "v2_initcode_bytes": len(initcode()),
        "dry_run_instantiate_from_B": {"ok": dry.ok, "reverted": dry.reverted, "storage_deposit": dry.storage_deposit},
        "v1_mirror": {"address": v1, "status": v1_status, "isBacked_3600": is_backed(substrate, b, v1, 3600, block_hash)},
        "balances": balances, "sum_free_tpot": round(sum(v["free_tpot"] for v in balances.values()), 4),
        "v1_deposit_measured_tpot": 138.53, "v1_deposit_source": "scripts/setup_roles.py docstring (dry-run 2026-10-20)",
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
