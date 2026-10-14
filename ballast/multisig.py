"""Multisig account derivation and the `as_multi` call-shape adapter.

The account is derived exactly like pallet-multisig: blake2_256(SCALE(("modlpy/utilisuba", sorted signatories,
threshold))). The pallet wants `other_signatories` sorted by raw public key, without the caller.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from typing import Any

from scalecodec.utils.ss58 import ss58_decode, ss58_encode

from .chain_profile import SHAPE_LEGACY_1002, SHAPE_WEIGHT_V2, ProfileUnverified

MULTISIG_PREFIX = b"modlpy/utilisuba"


def public_key(who: str | bytes) -> bytes:
    if isinstance(who, bytes):
        if len(who) != 32:
            raise ValueError("account id must be 32 bytes")
        return who
    if who.startswith("0x"):
        return public_key(bytes.fromhex(who[2:]))
    return bytes.fromhex(ss58_decode(who))


def compact_len(n: int) -> bytes:
    if n < 1 << 6:
        return bytes([n << 2])
    if n < 1 << 14:
        return ((n << 2) | 1).to_bytes(2, "little")
    if n < 1 << 30:
        return ((n << 2) | 2).to_bytes(4, "little")
    raise ValueError("signatory list too long")


def sorted_keys(signatories: Iterable[str | bytes]) -> list[bytes]:
    keys = [public_key(s) for s in signatories]
    if len(set(keys)) != len(keys):
        raise ValueError("duplicate signatory")
    return sorted(keys)


def multi_account_id(signatories: Iterable[str | bytes], threshold: int) -> bytes:
    keys = sorted_keys(signatories)
    if not 1 <= threshold <= len(keys):
        raise ValueError(f"threshold {threshold} out of range for {len(keys)} signatories")
    # The b"modlpy/utilisuba" prefix is a fixed-size array (no length); the signatory slice is a Vec.
    encoded = MULTISIG_PREFIX + compact_len(len(keys)) + b"".join(keys) + threshold.to_bytes(2, "little")
    return hashlib.blake2b(encoded, digest_size=32).digest()


def multi_address(signatories: Iterable[str | bytes], threshold: int, ss58_format: int = 42) -> str:
    return ss58_encode(multi_account_id(signatories, threshold), ss58_format=ss58_format)


def other_signatories(signatories: Iterable[str | bytes], me: str | bytes, ss58_format: int = 42) -> list[str]:
    mine = public_key(me)
    keys = sorted_keys(signatories)
    if mine not in keys:
        raise ValueError("caller is not a signatory")
    return [ss58_encode(k, ss58_format=ss58_format) for k in keys if k != mine]


def as_multi_params(
    shape: str | None,
    *,
    threshold: int,
    other_signatories: list[str],
    maybe_timepoint: dict | None,
    call: Any,
    max_weight: dict | int,
    store_call: bool = False,
) -> dict:
    """`Multisig.as_multi` arguments for the chain's call shape."""
    params = {
        "threshold": threshold,
        "other_signatories": other_signatories,
        "maybe_timepoint": maybe_timepoint,
        "call": call,
    }
    if shape == SHAPE_WEIGHT_V2:
        if isinstance(max_weight, int):
            raise ValueError("weight-v2 needs max_weight = {'ref_time': .., 'proof_size': ..}")
        params["max_weight"] = {"ref_time": int(max_weight["ref_time"]), "proof_size": int(max_weight["proof_size"])}
        return params
    if shape == SHAPE_LEGACY_1002:
        params["store_call"] = store_call
        params["max_weight"] = int(max_weight["ref_time"]) if isinstance(max_weight, dict) else int(max_weight)
        return params
    if shape is None:
        raise ProfileUnverified("as_multi call shape is UNVERIFIED (V3 day-0)")
    raise ValueError(f"unknown as_multi shape {shape!r}")
