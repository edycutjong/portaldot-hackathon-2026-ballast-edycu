"""ReserveOracle on Revive: deploy, post, read, and decode its `Posted` events — native-side (Substrate extrinsics).

The bot's SS58 key B acts inside Revive as its mapped H160 (`Revive.map_account`, `ReviveApi_address`); that H160 is
the oracle's attester. Posts are ordinary `Revive.call` extrinsics, so they get the same receipts as every other step.
Reads are dry-run runtime calls pinned to a block. The oracle is a mirror, never the enforcement point (the freeze
lives in the Assets pallet); `isBacked` fails closed on age.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from eth_abi import decode, encode
from eth_utils import function_signature_to_4byte_selector as selector
from eth_utils import keccak

from .chain import Receipt, submit
from .revive import dry_call, dry_instantiate, eth_address

ROOT = Path(__file__).resolve().parent.parent
ARTIFACT = ROOT / "out" / "ReserveOracle.sol" / "ReserveOracle.json"
POST_SIG = "post(uint128,uint128,uint256,uint64,bytes32,uint64,bool)"
POST_TYPES = ["uint128", "uint128", "uint256", "uint64", "bytes32", "uint64", "bool"]
STATUS_TYPES = ["(uint128,uint128,uint256,uint64,bytes32,uint64,bool,uint64)"]
POSTED_TOPIC = "0x" + keccak(text="Posted(uint128,uint128,uint256,uint64,bytes32,uint64,bool)").hex()
STATE_FIELDS = ("s1", "s2", "reserves", "sep_block", "sep_hash", "pd_block", "frozen")


def initcode() -> bytes:
    return bytes.fromhex(json.loads(ARTIFACT.read_text())["bytecode"]["object"][2:])


def post_data(s1, s2, reserves, sep_block, sep_hash, pd_block, frozen) -> bytes:
    args = [s1, s2, reserves, sep_block, bytes.fromhex(sep_hash[2:]), pd_block, frozen]
    return selector(POST_SIG) + encode(POST_TYPES, args)


def _limit(weight: dict) -> dict:
    return {"ref_time": max(20 * weight["ref_time"], 10**10), "proof_size": 2_000_000}


def deploy(substrate: Any, profile: Any, keypair: Any, *, step: str = "deploy_oracle") -> tuple[Receipt, str | None, str]:
    """B deploys ReserveOracle(attester = B's H160). Returns (receipt, contract address or None, attester H160)."""
    attester = eth_address(substrate, keypair.ss58_address)
    code = initcode() + encode(["address"], [attester])
    dry = dry_instantiate(substrate, keypair.ss58_address, code)
    if not dry.ok or dry.reverted:
        raise RuntimeError(f"ReserveOracle deploy dry-run failed: ok={dry.ok} reverted={dry.reverted}")
    r = submit(substrate, profile, keypair, "Revive", "instantiate_with_code",
               {"value": 0, "weight_limit": _limit(dry.weight_required),
                "storage_deposit_limit": 2 * dry.storage_deposit, "code": "0x" + code.hex(), "data": "0x",
                "salt": None}, step=step, call_label="Revive.instantiate_with_code(ReserveOracle)")
    inst = [e for e in r.events if (e["module_id"], e["event_id"]) == ("Revive", "Instantiated")]
    return r, (inst[0]["attributes"]["contract"] if inst else None), attester


def post(substrate: Any, profile: Any, keypair: Any, contract: str, state: tuple, *, step: str) -> Receipt:
    data = post_data(*state)
    ed = substrate.get_constant("Balances", "ExistentialDeposit").value
    est = dry_call(substrate, keypair.ss58_address, contract, data)
    return submit(substrate, profile, keypair, "Revive", "call",
                  {"dest": contract, "value": 0, "weight_limit": _limit(est.weight_required),
                   "storage_deposit_limit": 10 * max(est.storage_deposit, ed), "data": "0x" + data.hex()},
                  step=step, call_label="Revive.call(ReserveOracle.post)")


def read(substrate: Any, origin: str, contract: str, sig: str, out_types: list[str], args: bytes = b"",
         block_hash: str | None = None):
    res = dry_call(substrate, origin, contract, selector(sig) + args, block_hash)
    if not res.ok or res.reverted:
        raise RuntimeError(f"{sig} dry-run failed: ok={res.ok} reverted={res.reverted}")
    return decode(out_types, res.data)


def is_backed(substrate: Any, origin: str, contract: str, max_age: int, block_hash: str | None = None) -> bool:
    return read(substrate, origin, contract, "isBacked(uint256)", ["bool"], encode(["uint256"], [max_age]),
                block_hash)[0]


def status(substrate: Any, origin: str, contract: str, block_hash: str | None = None) -> dict:
    s = read(substrate, origin, contract, "status()", STATUS_TYPES, block_hash=block_hash)[0]
    return {"s1": s[0], "s2": s[1], "reserves": s[2], "sep_block": s[3], "sep_hash": "0x" + s[4].hex(),
            "pd_block": s[5], "frozen": s[6], "updated_at": s[7]}


def attester(substrate: Any, origin: str, contract: str, block_hash: str | None = None) -> str:
    return read(substrate, origin, contract, "attester()", ["address"], block_hash=block_hash)[0].lower()


def _hex(value: Any) -> bytes:
    if isinstance(value, (bytes, bytearray)):
        return bytes(value)
    if isinstance(value, (list, tuple)):
        return bytes(value)
    return bytes.fromhex(str(value).removeprefix("0x"))


def decode_posted(attrs: dict) -> dict | None:
    """`Revive.ContractEmitted {contract, data, topics}` -> the Posted fields, or None if it is another event.
    Indexed: sepBlock, pdBlock (topics 1, 2); data: s1, s2, reserves, sepHash, frozen."""
    topics = ["0x" + _hex(t).hex() for t in attrs.get("topics", [])]
    if not topics or topics[0] != POSTED_TOPIC or len(topics) != 3:
        return None
    s1, s2, reserves, sep_hash, frozen = decode(["uint128", "uint128", "uint256", "bytes32", "bool"], _hex(attrs["data"]))
    return {"contract": str(attrs["contract"]).lower(), "s1": s1, "s2": s2, "reserves": reserves,
            "sep_block": int(topics[1], 16), "sep_hash": "0x" + sep_hash.hex(), "pd_block": int(topics[2], 16),
            "frozen": frozen}
