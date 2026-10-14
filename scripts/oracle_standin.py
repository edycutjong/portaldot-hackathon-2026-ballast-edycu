#!/usr/bin/env python3
"""ReserveOracle on the stand-in's Revive pallet (standin-upstream, NOT V3), end to end.

  python scripts/oracle_standin.py [--profile standin-upstream] [--url ws://127.0.0.1:49944] [--drill FILE]

The stand-in's Revive accepts EVM bytecode (`Revive.AllowEVMBytecode = true`), so the solc build of
contracts/ReserveOracle.sol (forge, `out/`) is deployed as is — no PolkaVM toolchain. On V3 the deploy goes through
the V3 EVM RPC with Hardhat once the V3 day-0 gate passes; whether V3 accepts EVM bytecode is UNVERIFIED.

Steps: fund B (the reserve bot, attester) and a stranger from //Alice -> both `Revive.map_account` -> B deploys
ReserveOracle(attester = B's H160) via `Revive.instantiate_with_code` -> B posts the drill's LEVEL state (reserves
== S1 + S2) -> `isBacked(3600)` is true -> the stranger's post is refused (contract revert) -> B posts the drill's
DRAINED + FROZEN state -> `isBacked` is false and `status()` reads the frozen mirror. The posted numbers are copied
from a drain-drill evidence file (local-anvil reserve, not Sepolia) and labelled as such. Reads are dry-run runtime
calls (`ReviveApi_call`) pinned to the block of each step. Receipts -> evidence/ + docs/RECEIPTS.md.
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from eth_abi import decode, encode  # noqa: E402
from eth_utils import function_signature_to_4byte_selector as selector  # noqa: E402

from ballast.chain import Receipt, connect, dev_keypair, submit  # noqa: E402
from ballast.chain_profile import ProfileError, identify  # noqa: E402
from ballast.config import load_chain_config  # noqa: E402
from ballast.receipts import EVIDENCE, score, summarize, write_receipts_md  # noqa: E402
from ballast.revive import dry_call, dry_instantiate, eth_address  # noqa: E402
from ballast.rpc import HttpRpc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARTIFACT = ROOT / "out" / "ReserveOracle.sol" / "ReserveOracle.json"
SUPPORTED = ("standin-upstream",)
MAX_AGE = 3600
POST_SIG = "post(uint128,uint128,uint256,uint64,bytes32,uint64,bool)"
POST_TYPES = ["uint128", "uint128", "uint256", "uint64", "bytes32", "uint64", "bool"]
STATUS_TYPES = ["(uint128,uint128,uint256,uint64,bytes32,uint64,bool,uint64)"]


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def post_data(s1, s2, reserves, sep_block, sep_hash, pd_block, frozen) -> bytes:
    args = [s1, s2, reserves, sep_block, bytes.fromhex(sep_hash[2:]), pd_block, frozen]
    return selector(POST_SIG) + encode(POST_TYPES, args)


def latest_drain_drill() -> Path | None:
    runs = sorted(EVIDENCE.glob("drill-drain-*.json"), key=lambda p: json.loads(p.read_text())["started_at"])
    passing = [p for p in runs if json.loads(p.read_text()).get("verdict") == "PASS"]
    return passing[-1] if passing else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config")
    ap.add_argument("--profile")
    ap.add_argument("--url")
    ap.add_argument("--drill", help="drain-drill evidence JSON whose states are mirrored (default: newest PASS)")
    args = ap.parse_args()
    try:
        cfg = load_chain_config(args.config, profile=args.profile, url=args.url)
        ident = identify(HttpRpc(cfg.url), cfg.profile.name, measure=False)
    except (ProfileError, OSError, ValueError) as exc:
        print(f"oracle_standin: {exc}", file=sys.stderr)
        return 2
    profile = ident.profile
    if profile.name not in SUPPORTED:
        print(f"oracle_standin: profile {profile.name!r} not supported (supported: {', '.join(SUPPORTED)})",
              file=sys.stderr)
        return 2
    drill_path = Path(args.drill) if args.drill else latest_drain_drill()
    if drill_path is None or not drill_path.exists():
        print("oracle_standin: no PASS drain drill in evidence/ — run `ballast drill` first", file=sys.stderr)
        return 2
    drill = json.loads(drill_path.read_text())
    if not ARTIFACT.exists():
        print("oracle_standin: run `forge build` first", file=sys.stderr)
        return 2
    print(ident.banner())

    substrate = connect(profile, cfg.url)
    if not substrate.get_constant("Revive", "AllowEVMBytecode").value:
        print("oracle_standin: this chain's Revive does not accept EVM bytecode", file=sys.stderr)
        return 2
    alice = dev_keypair(profile, "//Alice")
    bot = dev_keypair(profile, "//BallastB")
    stranger = dev_keypair(profile, "//BallastJudge")
    role_of = {bot.ss58_address: "B (reserve bot, attester)", stranger.ss58_address: "Judge (stranger)",
               alice.ss58_address: "Alice, stand-in funder"}

    # The two mirrored states, from the drill: level (after both mints) and drained + frozen (the freeze block).
    a = drill["assets"]
    by_step = {s["receipt"]["step"]: s["receipt"] for s in drill["steps"]}
    deposit, drain = drill["evm_steps"][2], drill["evm_steps"][-1]
    freeze = by_step["watchdog_freeze"]
    level_state = (a["S1"], a["S2"], a["S1"] + a["S2"], deposit["block_number"], deposit["block_hash"],
                   by_step["mint_s2"]["block_number"], False)
    drained_state = (a["S1"], a["S2"], a["S1"] + a["S2"] - drain["amount"], drain["block_number"],
                     drain["block_hash"], freeze["block_number"], True)

    run: dict = {
        "kind": "oracle-deploy",
        "chain": {**ident.as_dict(), "url": cfg.url},
        "started_at": now(),
        "asset_id": a["breaker"],
        "mirrors": {"drill": drill_path.name, "reserve": drill["reserve"]["label"],
                    "note": "posted values copied from that drill's evidence; posted by this script, not by a bot"},
        "steps": [],
        "reads": [],
        "state_checks": [],
    }

    def step(name: str, expected: str, r: Receipt, ok: bool, events: tuple[str, ...] = ()):
        seen = [e for e in events if e in r.event_names()]
        run["steps"].append({"name": name, "expected": expected, "as_expected": ok, "counted": True,
                             "signer_role": role_of.get(r.signer, r.signer), "events_seen": seen,
                             "receipt": r.as_dict()})
        print(f"{'PASS' if ok else 'FAIL'} {r.extrinsic_id:>9} {r.call:<34} {r.outcome}  {name}")

    def check(what: str, observed, expected, block_hash: str) -> bool:
        ok = observed == expected
        run["state_checks"].append({"what": what, "expected": expected, "observed": observed, "ok": ok,
                                    "block_hash": block_hash})
        print(f"     {'ok  ' if ok else 'FAIL'} state: {what}: {observed}")
        return ok

    def read(contract: str, sig: str, out_types: list[str], block_hash: str):
        res = dry_call(substrate, bot.ss58_address, contract, selector(sig), block_hash)
        if not res.ok or res.reverted:
            raise RuntimeError(f"{sig} dry-run failed: ok={res.ok} reverted={res.reverted}")
        value = decode(out_types, res.data)
        run["reads"].append({"call": sig, "block_hash": block_hash, "result": json.loads(json.dumps(
            value, default=lambda v: "0x" + v.hex() if isinstance(v, bytes) else str(v)))})
        return value

    try:
        ed = substrate.get_constant("Balances", "ExistentialDeposit").value
        attester = eth_address(substrate, bot.ss58_address)
        code = bytes.fromhex(json.loads(ARTIFACT.read_text())["bytecode"]["object"][2:]) + encode(["address"], [attester])
        dry = dry_instantiate(substrate, alice.ss58_address, code)
        if not dry.ok or dry.reverted:
            raise RuntimeError(f"deploy dry-run failed: {dry}")
        fund = [substrate.compose_call(call_module="Balances", call_function="transfer_keep_alive",
                                       call_params={"dest": who, "value": amount})
                for who, amount in ((bot.ss58_address, 10 * dry.storage_deposit + 100 * ed),
                                    (stranger.ss58_address, dry.storage_deposit + 100 * ed))]
        r = submit(substrate, profile, alice, "Utility", "batch_all", {"calls": fund}, step="fund",
                   call_label="Utility.batch_all[2 x Balances.transfer_keep_alive]")
        step("fund B and the stranger (deposits + fees)", "Ok", r, r.outcome.ok)
        for kp in (bot, stranger):
            if substrate.query("Revive", "OriginalAccount", [eth_address(substrate, kp.ss58_address)]).value:
                print(f"     {role_of[kp.ss58_address]} already mapped")
                continue
            r = submit(substrate, profile, kp, "Revive", "map_account", {}, step=f"map_{kp.ss58_address[:6]}")
            step(f"Revive.map_account ({role_of[kp.ss58_address]})", "Ok", r, r.outcome.ok)

        weight = {"ref_time": max(20 * dry.weight_required["ref_time"], 10**10), "proof_size": 2_000_000}
        r = submit(substrate, profile, bot, "Revive", "instantiate_with_code",
                   {"value": 0, "weight_limit": weight, "storage_deposit_limit": 2 * dry.storage_deposit,
                    "code": "0x" + code.hex(), "data": "0x", "salt": None}, step="deploy_oracle")
        inst = [e for e in r.events if (e["module_id"], e["event_id"]) == ("Revive", "Instantiated")]
        contract = inst[0]["attributes"]["contract"] if inst else None
        step(f"B deploys ReserveOracle(attester = {attester})", "Ok + Revive.Instantiated", r,
             r.outcome.ok and bool(inst), ("Revive.Instantiated",))
        run["oracle"] = {"address": contract, "attester": attester, "deploy_extrinsic": r.extrinsic_id,
                         "code_bytes": len(code), "storage_deposit_dry_run": dry.storage_deposit}
        if not contract:
            raise RuntimeError("no Revive.Instantiated event")
        check("attester() == B's H160", "0x" + read(contract, "attester()", ["address"], r.block_hash)[0][2:].lower(),
              attester.lower(), r.block_hash)
        check("isBacked(3600) before any post", _is_backed(substrate, bot, contract, r.block_hash, run), False,
              r.block_hash)

        def post(kp, state, name, expect_ok):
            data = post_data(*state)
            est = dry_call(substrate, kp.ss58_address, contract, data)
            limit = {"ref_time": max(20 * est.weight_required["ref_time"], 10**10), "proof_size": 2_000_000}
            rr = submit(substrate, profile, kp, "Revive", "call",
                        {"dest": contract, "value": 0, "weight_limit": limit,
                         "storage_deposit_limit": 10 * max(est.storage_deposit, ed), "data": "0x" + data.hex()},
                        step=name)
            emitted = "Revive.ContractEmitted" in rr.event_names()
            if expect_ok:
                step(f"{role_of[kp.ss58_address]} posts {'FROZEN/drained' if state[-1] else 'level'} state "
                     f"(pdBlock {state[5]})", "Ok + Revive.ContractEmitted(Posted)", rr, rr.outcome.ok and emitted,
                     ("Revive.ContractEmitted",))
            else:
                step("stranger's post is refused (onlyAttester)", "Err(Revive.ContractReverted)", rr,
                     str(rr.outcome) == "Err(Revive.ContractReverted)" and not emitted)
            return rr

        r = post(bot, level_state, "post_level", True)
        check("isBacked(3600) after the level post", _is_backed(substrate, bot, contract, r.block_hash, run), True,
              r.block_hash)
        r = post(stranger, drained_state, "post_stranger", False)
        check("isBacked(3600) unchanged by the refused post", _is_backed(substrate, bot, contract, r.block_hash, run),
              True, r.block_hash)
        r = post(bot, drained_state, "post_frozen", True)
        check("isBacked(3600) after the frozen/drained post", _is_backed(substrate, bot, contract, r.block_hash, run),
              False, r.block_hash)
        status = read(contract, "status()", STATUS_TYPES, r.block_hash)[0]
        check("status() = (S1, S2, reserves, sepBlock, sepHash, pdBlock, frozen) of the drained drill state",
              [status[0], status[1], status[2], status[3], "0x" + status[4].hex(), status[5], status[6]],
              list(drained_state), r.block_hash)
    except Exception as exc:  # noqa: BLE001 — keep every receipt that landed
        run["error"] = f"{type(exc).__name__}: {exc}"
        traceback.print_exc()
    finally:
        run["finished_at"] = now()
        summarize(run)
        stamp = run["started_at"].replace("-", "").replace(":", "")
        out = EVIDENCE / f"oracle-revive-{profile.name}-{stamp}.json"
        out.write_text(json.dumps(run, indent=2, default=str) + "\n")
        md = write_receipts_md()
    print(f"\n[{profile.name}] ReserveOracle on Revive: {run['verdict']} ({score(run)}); "
          f"address {run.get('oracle', {}).get('address')}")
    print(f"evidence -> evidence/{out.name} · receipts -> docs/{md.name}")
    return 0 if run["verdict"] == "PASS" else 1


def _is_backed(substrate, bot, contract: str, block_hash: str, run: dict) -> bool:
    res = dry_call(substrate, bot.ss58_address, contract, selector("isBacked(uint256)") + encode(["uint256"], [MAX_AGE]),
                   block_hash)
    if not res.ok or res.reverted:
        raise RuntimeError("isBacked dry-run failed")
    value = decode(["bool"], res.data)[0]
    run["reads"].append({"call": f"isBacked({MAX_AGE})", "block_hash": block_hash, "result": value})
    return value


if __name__ == "__main__":
    sys.exit(main())
