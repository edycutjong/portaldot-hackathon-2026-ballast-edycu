"""Decode dispatch results into `Pallet.Error` names read from the chain's own metadata.

A multisig extrinsic can succeed while the call inside it fails: `Multisig.MultisigExecuted` carries the inner
`DispatchResult` as its last attribute, so every multisig step must check it, not just the outer result.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Outcome:
    ok: bool
    pallet: str | None = None
    error: str | None = None
    detail: str | None = None

    def __str__(self) -> str:
        if self.ok:
            return "Ok"
        if self.pallet:
            return f"Err({self.pallet}.{self.error})"
        return f"Err({self.error})"

    def as_dict(self) -> dict:
        return {"ok": self.ok, "pallet": self.pallet, "error": self.error, "text": str(self)}


OK = Outcome(ok=True)


def _error_index(raw: Any) -> int:
    # Modern runtimes: ModuleError.error is [u8; 4] (hex string); the first byte is the variant index.
    if isinstance(raw, str):
        return bytes.fromhex(raw[2:] if raw.startswith("0x") else raw)[0]
    if isinstance(raw, (bytes, bytearray)):
        return raw[0]
    if isinstance(raw, (list, tuple)):
        return int(raw[0])
    return int(raw)


def module_error_name(metadata: Any, pallet_index: int, error_index: int) -> tuple[str, str]:
    """(pallet name, error name) for a module error, from scale-info (V14+) or legacy (V13) metadata."""
    for pallet in metadata.pallets:
        if pallet.value["index"] != pallet_index:
            continue
        errors = pallet.errors or []
        for position, err in enumerate(errors):
            value = err.value
            if value.get("index", position) == error_index:
                return pallet.value["name"], value["name"]
        return pallet.value["name"], f"#{error_index}"
    return f"pallet#{pallet_index}", f"#{error_index}"


def decode_dispatch_error(err: Any, metadata: Any) -> Outcome:
    if isinstance(err, dict) and "Module" in err:
        mod = err["Module"]
        if isinstance(mod, dict):
            p_idx, e_idx = int(mod["index"]), _error_index(mod["error"])
        else:
            p_idx, e_idx = int(mod[0]), _error_index(mod[1])
        pallet, name = module_error_name(metadata, p_idx, e_idx)
        return Outcome(ok=False, pallet=pallet, error=name)
    if isinstance(err, dict) and len(err) == 1:
        kind, inner = next(iter(err.items()))
        return Outcome(ok=False, error=f"{kind}.{inner}" if inner is not None else kind)
    return Outcome(ok=False, error=str(err))


def decode_dispatch_result(result: Any, metadata: Any) -> Outcome:
    if result == "Ok" or (isinstance(result, dict) and "Ok" in result):
        return OK
    if isinstance(result, dict) and "Err" in result:
        return decode_dispatch_error(result["Err"], metadata)
    raise ValueError(f"not a DispatchResult: {result!r}")


def attribute(event: dict, name: str, position: int) -> Any:
    """An event attribute by name (scale-info metadata) or by position (legacy metadata)."""
    attrs = event["attributes"]
    if isinstance(attrs, dict):
        return attrs[name]
    item = attrs[position]
    return item["value"] if isinstance(item, dict) and "value" in item else item


def extrinsic_outcome(events: list[dict], metadata: Any) -> Outcome:
    """Ok / Err(Pallet.Error) of one extrinsic, from its System.ExtrinsicSuccess/Failed event."""
    for ev in events:
        if ev["module_id"] != "System":
            continue
        if ev["event_id"] == "ExtrinsicSuccess":
            return OK
        if ev["event_id"] == "ExtrinsicFailed":
            return decode_dispatch_error(attribute(ev, "dispatch_error", 0), metadata)
    raise ValueError("no ExtrinsicSuccess/ExtrinsicFailed among the events")


def multisig_inner_results(events: list[dict], metadata: Any) -> list[Outcome]:
    """The inner DispatchResult of every Multisig.MultisigExecuted in the events."""
    return [
        decode_dispatch_result(attribute(ev, "result", 4), metadata)
        for ev in events
        if ev["module_id"] == "Multisig" and ev["event_id"] == "MultisigExecuted"
    ]
