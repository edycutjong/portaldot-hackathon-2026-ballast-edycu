"""Load raw runtime metadata (SCALE bytes) offline — for tests and for verifying receipts without a node."""

from __future__ import annotations

from typing import Any

from scalecodec.base import RuntimeConfigurationObject, ScaleBytes
from scalecodec.type_registry import load_type_registry_preset

from .chain_profile import Profile
from .types_1002 import patch_assets_balance_u64


def load_metadata(raw: bytes, profile: Profile) -> tuple[RuntimeConfigurationObject, Any]:
    """(runtime config, decoded metadata) the same way the profile connects: preset + 1002 patch if any."""
    config = RuntimeConfigurationObject()
    config.update_type_registry(load_type_registry_preset("core"))
    if profile.type_registry_preset:
        config.update_type_registry(load_type_registry_preset(profile.type_registry_preset))
    metadata = config.create_scale_object("MetadataVersioned", data=ScaleBytes(raw))
    metadata.decode()
    if metadata.portable_registry:
        config.add_portable_registry(metadata)
    if profile.patch_assets_u64:
        patch_assets_balance_u64(metadata)
    return config, metadata


def encode_call(config: RuntimeConfigurationObject, metadata: Any, module: str, function: str, args: dict) -> bytes:
    call = config.create_scale_object("Call", metadata=metadata)
    data = call.encode({"call_module": module, "call_function": function, "call_args": args})
    return bytes(data.data)
