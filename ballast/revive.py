"""Minimal pallet-revive client: account -> H160, read-only contract calls via the `ReviveApi_call` runtime API.

substrate-interface 1.8 has no `ReviveApi` definition and scalecodec cannot decode metadata V15, so the two
runtime calls used here are SCALE-encoded / decoded by hand, against the signatures the stand-in reports in its
V15 metadata (polkadot-stable2606-3):

  ReviveApi_address(account_id: AccountId32) -> H160
  ReviveApi_call(origin: AccountId32, dest: H160, value: u128, gas_limit: Option<Weight>,
                 storage_deposit_limit: Option<u128>, input_data: Bytes)
    -> ContractResult { weight_consumed: Weight, weight_required: Weight, storage_deposit: StorageDeposit,
                        max_storage_deposit: StorageDeposit, gas_consumed: u128,
                        result: Result<ExecReturnValue { flags: u32, data: Bytes }, DispatchError> }
  ReviveApi_instantiate(origin, value: u128, gas_limit: Option<Weight>, storage_deposit_limit: Option<u128>,
                        code: Code { Upload(Bytes), Existing(H256) }, data: Bytes, salt: Option<[u8; 32]>)
    -> ContractResult { …same…, result: Result<InstantiateReturnValue { result: ExecReturnValue, addr: H160 }, …> }

Deploys and state-changing calls are ordinary extrinsics (`Revive.map_account`, `Revive.instantiate_with_code`,
`Revive.call`) submitted with `ballast.chain.submit`, so they get the same receipts as every other step.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .multisig import compact_len, public_key

REVERT_FLAG = 0x1  # ReturnFlags::REVERT


def read_compact(buf: bytes, pos: int) -> tuple[int, int]:
    mode = buf[pos] & 0b11
    if mode == 0:
        return buf[pos] >> 2, pos + 1
    if mode == 1:
        return int.from_bytes(buf[pos:pos + 2], "little") >> 2, pos + 2
    if mode == 2:
        return int.from_bytes(buf[pos:pos + 4], "little") >> 2, pos + 4
    n = (buf[pos] >> 2) + 4
    return int.from_bytes(buf[pos + 1:pos + 1 + n], "little"), pos + 1 + n


def encode_bytes(data: bytes) -> bytes:
    if len(data) >= 1 << 30:
        raise ValueError("input too long")
    return compact_len(len(data)) + data


@dataclass(frozen=True)
class CallResult:
    ok: bool  # dispatched without a DispatchError
    reverted: bool  # the contract reverted (REVERT flag)
    data: bytes  # return data (ABI-encoded) or revert data
    weight_required: dict  # {"ref_time", "proof_size"}: what a real extrinsic needs as weight_limit
    storage_deposit: int  # charged (+) or refunded (-) planck
    gas_consumed: int
    address: str | None = None  # instantiate only
    error: bytes | None = None  # raw SCALE DispatchError when not ok


def decode_contract_result(raw: bytes, instantiate: bool = False) -> CallResult:
    pos = 0
    weights = []
    for _ in range(4):  # weight_consumed, weight_required: Weight { ref_time: Compact<u64>, proof_size: Compact<u64> }
        value, pos = read_compact(raw, pos)
        weights.append(value)
    deposits = []
    for _ in range(2):  # storage_deposit, max_storage_deposit: enum { Refund(u128), Charge(u128) }
        sign = -1 if raw[pos] == 0 else 1
        deposits.append(sign * int.from_bytes(raw[pos + 1:pos + 17], "little"))
        pos += 17
    gas_consumed = int.from_bytes(raw[pos:pos + 16], "little")
    pos += 16
    tag = raw[pos]
    pos += 1
    common = {"weight_required": {"ref_time": weights[2], "proof_size": weights[3]}, "storage_deposit": deposits[0],
              "gas_consumed": gas_consumed}
    if tag != 0:
        return CallResult(ok=False, reverted=False, data=b"", error=raw[pos:], **common)
    flags = int.from_bytes(raw[pos:pos + 4], "little")
    n, pos = read_compact(raw, pos + 4)
    data = raw[pos:pos + n]
    pos += n
    address = "0x" + raw[pos:pos + 20].hex() if instantiate else None
    return CallResult(ok=True, reverted=bool(flags & REVERT_FLAG), data=data, address=address, **common)


def _state_call(substrate: Any, method: str, args: bytes, block_hash: str | None = None) -> bytes:
    params = [method, "0x" + args.hex()] + ([block_hash] if block_hash else [])
    result = substrate.rpc_request("state_call", params)["result"]
    return bytes.fromhex(result[2:])


def eth_address(substrate: Any, account: str | bytes) -> str:
    """The H160 a Substrate account acts as inside Revive (`msg.sender`), as the runtime computes it."""
    return "0x" + _state_call(substrate, "ReviveApi_address", public_key(account)).hex()


def dry_call(substrate: Any, origin: str | bytes, dest: str, data: bytes, block_hash: str | None = None) -> CallResult:
    """Read-only contract call (nothing is submitted): `ReviveApi_call` with no gas / deposit limit."""
    dest_bytes = bytes.fromhex(dest.removeprefix("0x"))
    if len(dest_bytes) != 20:
        raise ValueError("dest must be an H160")
    args = public_key(origin) + dest_bytes + (0).to_bytes(16, "little") + b"\x00" + b"\x00" + encode_bytes(data)
    return decode_contract_result(_state_call(substrate, "ReviveApi_call", args, block_hash))


def dry_instantiate(substrate: Any, origin: str | bytes, code: bytes, data: bytes = b"") -> CallResult:
    """Dry-run a deploy of `code` (EVM init code with constructor args appended, or PolkaVM blob)."""
    args = (public_key(origin) + (0).to_bytes(16, "little") + b"\x00" + b"\x00" + b"\x00" + encode_bytes(code)
            + encode_bytes(data) + b"\x00")
    return decode_contract_result(_state_call(substrate, "ReviveApi_instantiate", args), instantiate=True)
