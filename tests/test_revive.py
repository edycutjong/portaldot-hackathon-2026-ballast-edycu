"""Hand-rolled SCALE for the two ReviveApi runtime calls (offline)."""

from __future__ import annotations

from ballast.multisig import compact_len
from ballast.revive import decode_contract_result, encode_bytes, read_compact


def weight(ref: int, proof: int) -> bytes:
    return compact_len(ref) + compact_len(proof) if ref < 1 << 30 and proof < 1 << 30 else b""


def charge(n: int) -> bytes:
    return b"\x01" + n.to_bytes(16, "little")


def result_ok(flags: int, data: bytes, addr: bytes | None = None) -> bytes:
    body = weight(5, 0) + weight(3_876_478, 7) + charge(123) + charge(456) + (99).to_bytes(16, "little")
    body += b"\x00" + flags.to_bytes(4, "little") + encode_bytes(data)
    return body + (addr or b"")


def test_compact_round_trip():
    for n in (0, 1, 63, 64, 16383, 16384, (1 << 30) - 1):
        assert read_compact(compact_len(n), 0) == (n, len(compact_len(n)))
    assert read_compact(b"\x13" + (2**40).to_bytes(8, "little"), 0) == (2**40, 9)  # big-integer mode


def test_call_result_ok_and_revert_flag():
    r = decode_contract_result(result_ok(0, b"\x00" * 31 + b"\x01"))
    assert r.ok and not r.reverted and r.data[-1] == 1
    assert r.weight_required == {"ref_time": 3_876_478, "proof_size": 7}
    assert r.storage_deposit == 123 and r.gas_consumed == 99
    assert decode_contract_result(result_ok(1, b"\xde\xad")).reverted


def test_instantiate_result_carries_the_address():
    addr = bytes(range(20))
    r = decode_contract_result(result_ok(0, b"", addr), instantiate=True)
    assert r.address == "0x" + addr.hex()


def test_dispatch_error_and_refund_sign():
    raw = weight(1, 1) + weight(1, 1) + b"\x00" + (7).to_bytes(16, "little") + charge(0) + bytes(16) + b"\x01\x03\x50"
    r = decode_contract_result(raw)
    assert not r.ok and r.error == b"\x03\x50" and r.storage_deposit == -7
