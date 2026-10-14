"""BALLAST/1 remarks on chain: format, parse, and find them in blocks.

Every Ballast remark is `System.remark_with_event`, so each one leaves a `System.Remarked {sender, hash}` event. The
event is the anchor: its `sender` is the EFFECTIVE origin (a remark dispatched through a multisig is sent by the
multisig account), and its hash is blake2_256 of the text. The text itself is only in the extrinsic body, so it is
found by walking the extrinsic's call tree (batch_all, as_multi, …) for a remark whose hash matches.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from .chain_profile import blake2_256

PREFIX = "BALLAST/1"
MAX_BYTES = 320  # our own budget for any BALLAST/1 remark (architecture: attestation format)


def encode(kind: str, **fields: Any) -> str:
    for k, v in fields.items():
        if any(c in f"{k}{v}" for c in "|="):
            raise ValueError(f"field {k}={v!r} contains a separator")
    text = "|".join([PREFIX, kind, *(f"{k}={v}" for k, v in fields.items())])
    if len(text.encode()) > MAX_BYTES:
        raise ValueError(f"remark is {len(text.encode())} bytes > {MAX_BYTES}")
    return text


def parse(text: str) -> dict:
    """`BALLAST/1|<type>|k=v|…` -> {"type": <type>, k: v, …}. Raises on anything else."""
    parts = text.split("|")
    if len(parts) < 2 or parts[0] != PREFIX or not parts[1] or "=" in parts[1]:
        raise ValueError("not a BALLAST/1 remark")
    out = {"type": parts[1]}
    for part in parts[2:]:
        key, sep, value = part.partition("=")
        if not sep or not key or key in out:
            raise ValueError(f"bad field {part!r}")
        out[key] = value
    return out


def _text(value: Any) -> str | None:
    if isinstance(value, (bytes, bytearray)):
        raw = bytes(value)
    elif isinstance(value, str) and value.startswith("0x"):
        try:
            raw = bytes.fromhex(value[2:])
        except ValueError:
            return value
    elif isinstance(value, str):
        return value
    else:
        return None
    try:
        return raw.decode()
    except UnicodeDecodeError:
        return None


def walk(call: dict, path: str = "") -> Iterator[tuple[str, dict]]:
    """Every call in a decoded call tree (depth-first), with its path, e.g. `Utility.batch_all>System.remark_with_event`."""
    here = f"{path}>{call['call_module']}.{call['call_function']}" if path else f"{call['call_module']}.{call['call_function']}"
    yield here, call
    for arg in call.get("call_args", []):
        value = arg.get("value")
        children = value if isinstance(value, list) else [value]
        for child in children:
            if isinstance(child, dict) and "call_module" in child and "call_function" in child:
                yield from walk(child, here)


def remarks_in_call(call: dict) -> list[tuple[str, str]]:
    """(path, text) of every System.remark / remark_with_event in the call tree."""
    out = []
    for path, c in walk(call):
        if c["call_module"] == "System" and c["call_function"] in ("remark", "remark_with_event"):
            for arg in c.get("call_args", []):
                if arg.get("name") == "remark":
                    text = _text(arg.get("value"))
                    if text is not None:
                        out.append((path, text))
    return out


def block_remarks(substrate: Any, block_hash: str, prefix: str = PREFIX) -> list[dict]:
    """Every remark in the block that (1) left a System.Remarked event and (2) starts with `prefix`.
    `sender` is the event's sender (effective origin), `signer` the extrinsic's signer."""
    block = substrate.get_block(block_hash)
    events = substrate.get_events(block_hash)
    number = block["header"]["number"]
    out = []
    for ev in events:
        v = ev.value
        if (v.get("module_id"), v.get("event_id")) != ("System", "Remarked"):
            continue
        idx = v.get("extrinsic_idx")
        if idx is None or idx >= len(block["extrinsics"]):
            continue
        attrs = v["attributes"]
        xt = block["extrinsics"][idx].value
        for path, text in remarks_in_call(xt["call"]):
            if blake2_256(text.encode()) == attrs["hash"] and text.startswith(prefix):
                out.append({"block_number": number, "block_hash": block_hash, "extrinsic_index": idx,
                            "extrinsic_id": f"{number}-{idx}", "extrinsic_hash": xt.get("extrinsic_hash"),
                            "signer": xt.get("address"), "sender": attrs["sender"], "path": path, "text": text})
                break
    return out
