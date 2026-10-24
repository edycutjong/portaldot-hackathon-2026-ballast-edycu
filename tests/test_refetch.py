"""receipts.refetch follows an extrinsic whose inclusion block lost a fork; chain.find_receipt rebuilds a lost receipt."""

from types import SimpleNamespace

from ballast.chain import find_receipt
from ballast.chain_profile import blake2_256
from ballast.receipts import refetch

TX = "0x" + "ab" * 40
TX_HASH = blake2_256(bytes.fromhex(TX[2:]))
OK_EVENTS = [{"module_id": "System", "event_id": "ExtrinsicSuccess", "attributes": {}, "extrinsic_idx": 1}]


class FakeChain:
    """Canonical block #10 holds [inherent, TX]; get_events returns TX's success event."""

    metadata = None

    def __init__(self, canonical: str = "0xcanon"):
        self.canonical = canonical

    def get_block_hash(self, number):
        return self.canonical

    def get_block_number(self, block_hash):
        return 10

    def rpc_request(self, method, params):
        return {"result": {"block": {"extrinsics": ["0x00", TX]}}}

    def get_events(self, block_hash):
        return [SimpleNamespace(value=e) for e in OK_EVENTS]

    def get_extrinsics(self, block_hash):
        return [SimpleNamespace(value={"address": None, "call": {"call_module": "Timestamp", "call_function": "set"}}),
                SimpleNamespace(value={"address": "5Signer", "extrinsic_hash": TX_HASH,
                                       "call": {"call_module": "Assets", "call_function": "transfer_ownership",
                                                "call_args": [{"name": "id", "value": 4401}]}})]


def receipt(block_hash: str, index: int = 1) -> dict:
    return {"block_number": 10, "block_hash": block_hash, "extrinsic_index": index, "extrinsic_id": f"10-{index}",
            "extrinsic_hash": TX_HASH, "outcome": {"ok": True, "pallet": None, "error": None, "text": "Ok"}, "inner": [],
            "events": [{"module_id": "System", "event_id": "ExtrinsicSuccess", "attributes": {}}]}


def test_confirmed_in_place():
    placed: dict = {}
    assert refetch(FakeChain(), receipt("0xcanon"), placed) == []
    assert placed["reorged_from"] is None and placed["block_hash"] == "0xcanon"


def test_inclusion_block_lost_a_fork_but_the_extrinsic_is_canonical():
    placed: dict = {}
    assert refetch(FakeChain(), receipt("0xfork"), placed) == []
    assert placed == {"block_number": 10, "block_hash": "0xcanon", "extrinsic_index": 1, "reorged_from": "0xfork"}


def test_inclusion_block_lost_and_the_extrinsic_is_gone():
    chain = FakeChain()
    chain.rpc_request = lambda m, p: {"result": {"block": {"extrinsics": ["0x00"]}}}
    problems = refetch(chain, receipt("0xfork"))
    assert problems and "not in it" in problems[0]


def test_find_receipt_matches_signer_call_and_args():
    profile = SimpleNamespace(name="v3")
    r = find_receipt(FakeChain(), profile, "5Signer", "Assets", "transfer_ownership", step="t", from_block=10,
                     to_block=10, call_args={"id": 4401})
    assert r is not None and r.extrinsic_id == "10-1" and r.outcome.ok and r.extrinsic_hash == TX_HASH
    assert find_receipt(FakeChain(), profile, "5Signer", "Assets", "transfer_ownership", step="t", from_block=10,
                        to_block=10, call_args={"id": 4402}) is None
    assert find_receipt(FakeChain(), profile, "5Other", "Assets", "transfer_ownership", step="t", from_block=10,
                        to_block=10) is None
