"""standin-1002 only: the spec-1002 Assets pallet uses a u64 Balance.

substrate-interface's `legacy` preset types every `Balance` as u128, so `assets.create` encodes an 8-byte
`min_balance` as 16 bytes (the node answers "bad signature") and Assets events fail to decode. The fix
re-types the Assets pallet's own call and event `Balance` arguments (plain and `Compact<...>`) to u64 in the
loaded metadata.
Other pallets (Balances, Treasury, ...) keep u128. Never applied on any other profile.
"""

from __future__ import annotations

from typing import Any

ASSETS_BALANCE_TYPES = {
    "T::Balance": "u64",
    "Balance": "u64",
    "TBalance": "u64",
    "Compact<T::Balance>": "Compact<u64>",
    "Compact<Balance>": "Compact<u64>",
}


def patch_assets_balance_u64(metadata: Any) -> int:
    """Re-type Assets call/event Balance args to u64 in place. Idempotent; returns the number of args changed."""
    pallet = metadata.get_metadata_pallet("Assets")
    if pallet is None:
        raise RuntimeError("no Assets pallet in metadata")
    changed = 0
    for call in pallet.calls or []:
        for arg in call.args:
            if arg.value["type"] in ASSETS_BALANCE_TYPES:
                arg.value["type"] = ASSETS_BALANCE_TYPES[arg.value["type"]]
                changed += 1
    for event in pallet.events or []:
        args = event.value["args"]
        for i, t in enumerate(args):
            if t in ASSETS_BALANCE_TYPES:
                args[i] = ASSETS_BALANCE_TYPES[t]
                changed += 1
    return changed
