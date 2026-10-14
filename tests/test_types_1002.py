from substrateinterface import Keypair

from ballast.metadata import encode_call
from ballast.types_1002 import patch_assets_balance_u64

ALICE = Keypair.create_from_uri("//Alice").ss58_address


# call index (2) + Compact<u32> id (1) + MultiAddress::Id (1 + 32), then min_balance
HEAD = 2 + 1 + 1 + 32


def _create(config, md) -> bytes:
    return encode_call(config, md, "Assets", "create", {"id": 7, "admin": ALICE, "min_balance": 1})


def test_unpatched_1002_create_encodes_min_balance_as_u128(md_1002):
    config, md = md_1002
    encoded = _create(config, md)
    assert len(encoded) == HEAD + 16 and encoded[HEAD:] == (1).to_bytes(16, "little")


def test_patch_makes_assets_balance_u64_only(md_1002):
    config, md = md_1002
    changed = patch_assets_balance_u64(md)
    assert changed > 0
    encoded = _create(config, md)
    assert len(encoded) == HEAD + 8 and encoded[HEAD:] == (1).to_bytes(8, "little")
    assets = md.get_metadata_pallet("Assets")
    transferred = next(e for e in assets.events if e.value["name"] == "Transferred")
    assert transferred.value["args"][-1] == "u64"
    balances = md.get_metadata_pallet("Balances")
    assert "u64" not in next(e for e in balances.events if e.value["name"] == "Transfer").value["args"]
    assert patch_assets_balance_u64(md) == 0  # idempotent


def test_patch_also_retypes_compact_amounts(md_1002):
    _, md = md_1002
    patch_assets_balance_u64(md)
    calls = {c.value["name"]: [a.value["type"] for a in c.args] for c in md.get_metadata_pallet("Assets").calls}
    for name in ("mint", "burn", "transfer", "transfer_keep_alive", "force_transfer"):
        assert calls[name][-1] == "Compact<u64>", name
    assert "Compact<T::Balance>" not in sum(calls.values(), [])
