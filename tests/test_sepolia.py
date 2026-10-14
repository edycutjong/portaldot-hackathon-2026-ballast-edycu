"""EVM reserve reader: snapshots pinned by block hash, failures as readings, disagreements surfaced (offline)."""

from __future__ import annotations

import pytest

from ballast.sepolia import (
    ProviderError,
    Web3Provider,
    balance_of_data,
    compare,
    cross_check,
    providers_from,
    read_all,
    read_reserves,
)

USDC_ADDR = "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238"
VAULT = "0x00000000000000000000000000000000000000aa"
H100 = "0x" + "11" * 32
H100_FORK = "0x" + "22" * 32


class FakeRpc:
    """Blocks by tag/number, balances by block hash; records every call."""

    def __init__(self, name, blocks, balances, down=False):
        self.name, self.blocks, self.balances, self.down = name, blocks, balances, down
        self.calls = []

    def call(self, method, params):
        self.calls.append((method, params))
        if self.down:
            raise ProviderError(f"{self.name}: {method}: connection refused")
        if method == "eth_getBlockByNumber":
            key = params[0] if params[0] in ("latest", "safe", "finalized") else int(params[0], 16)
            number, block_hash = self.blocks[key]
            return {"number": hex(number), "hash": block_hash, "timestamp": hex(1_760_000_000 + number)}
        if method == "eth_call":
            pin = params[1]
            assert pin == {"blockHash": pin["blockHash"], "requireCanonical": True}
            return f"0x{self.balances[pin['blockHash']]:064x}"
        raise AssertionError(method)


def test_balance_of_calldata():
    assert balance_of_data(VAULT) == "0x70a08231" + "0" * 62 + "aa"
    with pytest.raises(ValueError):
        balance_of_data("0x1234")


def test_reading_is_pinned_to_the_block_hash():
    rpc = FakeRpc("a", {"latest": (100, H100)}, {H100: 100_000_000})
    r = read_reserves(rpc, USDC_ADDR, VAULT, "latest")
    assert r.ok and r.reserves == 100_000_000 and r.block_number == 100 and r.block_hash == H100
    method, params = rpc.calls[1]
    assert method == "eth_call" and params[1] == {"blockHash": H100, "requireCanonical": True}
    assert params[0]["to"] == USDC_ADDR and params[0]["data"] == balance_of_data(VAULT)


def test_unreachable_provider_is_a_reading_not_an_exception():
    r = read_reserves(FakeRpc("a", {}, {}, down=True), USDC_ADDR, VAULT)
    assert not r.ok and "connection refused" in r.error and r.reserves is None


def test_compare_flags_hash_disagreement_at_one_height():
    a = FakeRpc("a", {"latest": (100, H100)}, {H100: 5})
    b = FakeRpc("b", {"latest": (100, H100_FORK)}, {H100_FORK: 5})
    c = compare(read_all([a, b], USDC_ADDR, VAULT))
    assert len(c.disagreements) == 1 and "disagree on the hash" in c.disagreements[0]


def test_compare_flags_balance_disagreement_at_one_hash():
    a = FakeRpc("a", {"latest": (100, H100)}, {H100: 5})
    b = FakeRpc("b", {"latest": (100, H100)}, {H100: 6})
    c = compare(read_all([a, b], USDC_ADDR, VAULT))
    assert c.disagreements == [f"block {H100[:12]}…: providers disagree on reserves (a=5, b=6)"]


def test_lag_is_not_a_disagreement_and_min_and_short_use_all_ok_readings():
    h101 = "0x" + "33" * 32
    a = FakeRpc("a", {"latest": (101, h101)}, {h101: 70})
    b = FakeRpc("b", {"latest": (100, H100)}, {H100: 100})
    d = FakeRpc("d", {}, {}, down=True)
    c = compare(read_all([a, b, d], USDC_ADDR, VAULT))
    assert c.disagreements == []
    assert c.min_reserves == 70 and [r.provider for r in c.short(100)] == ["a"]
    assert [r.provider for r in c.failed] == ["d"] and not c.all_down


def test_all_down():
    c = compare(read_all([FakeRpc("a", {}, {}, down=True), FakeRpc("b", {}, {}, down=True)], USDC_ADDR, VAULT))
    assert c.all_down and c.min_reserves is None


def test_cross_check_agrees_on_one_finalized_block():
    blocks = {"finalized": (90, H100), 90: (90, H100)}
    a, b = FakeRpc("a", blocks, {H100: 20}), FakeRpc("b", dict(blocks), {H100: 20})
    out = cross_check([a, b], USDC_ADDR, VAULT, "finalized")
    assert out["agree"] and out["block_number"] == 90 and out["providers"]["b"]["block_hash"] == H100


def test_cross_check_reports_a_fork_and_a_down_provider():
    a = FakeRpc("a", {"finalized": (90, H100), 90: (90, H100)}, {H100: 20})
    b = FakeRpc("b", {90: (90, H100_FORK)}, {H100: 20})
    assert not cross_check([a, b], USDC_ADDR, VAULT)["agree"]
    down = FakeRpc("c", {}, {}, down=True)
    out = cross_check([a, down], USDC_ADDR, VAULT)
    assert not out["agree"] and "error" in out["providers"]["c"]


def test_providers_from_parses_names_and_rejects_duplicates():
    ps = providers_from(["x=http://127.0.0.1:1", "http://127.0.0.1:2"])
    assert [p.name for p in ps] == ["x", "provider2"] and isinstance(ps[0], Web3Provider)
    with pytest.raises(ValueError):
        providers_from(["x=http://127.0.0.1:1", "x=http://127.0.0.1:2"])


def test_web3_provider_wraps_transport_errors():
    # a port nothing listens on: the real HTTP stack fails, the reader gets a named ProviderError
    p = Web3Provider("closed", "http://127.0.0.1:9", timeout=2)
    with pytest.raises(ProviderError, match="closed: eth_chainId"):
        p.call("eth_chainId", [])


class Malformed(FakeRpc):
    """A provider that answers, but with garbage (rate-limit page, partial JSON, hostile gateway)."""

    def __init__(self, name, block_reply=None, call_reply=None):
        super().__init__(name, {}, {})
        self.block_reply, self.call_reply = block_reply, call_reply

    def call(self, method, params):
        if method == "eth_getBlockByNumber":
            return self.block_reply
        return self.call_reply


@pytest.mark.parametrize("block_reply", ["rate limited", {"hash": H100}, {"number": "0x1", "hash": "0xzz",
                                                                         "timestamp": "0x1"}, None, [1, 2]])
def test_malformed_block_reply_is_a_failed_reading_not_an_exception(block_reply):
    r = read_reserves(Malformed("bad", block_reply=block_reply), USDC_ADDR, VAULT)
    assert not r.ok and r.error


@pytest.mark.parametrize("call_reply", ["0x", "0x" + "00" * 64, None, "0xnothex" + "0" * 58, 5])
def test_eth_call_must_return_exactly_one_word(call_reply):
    good_block = {"number": "0x64", "hash": H100, "timestamp": "0x1"}
    r = read_reserves(Malformed("bad", block_reply=good_block, call_reply=call_reply), USDC_ADDR, VAULT)
    assert not r.ok and ("32-byte word" in r.error or "hex quantity" in r.error)


def test_one_malformed_provider_cannot_hide_anothers_deficit():
    healthy = FakeRpc("a", {"latest": (100, H100)}, {H100: 70})
    c = compare(read_all([healthy, Malformed("b", block_reply="oops")], USDC_ADDR, VAULT))
    assert [r.provider for r in c.short(100)] == ["a"] and [r.provider for r in c.failed] == ["b"]


def test_stale_latest_block_is_a_failed_reading():
    rpc = FakeRpc("a", {"latest": (100, H100)}, {H100: 100})  # fake timestamps are from 2025: hours old
    assert not read_reserves(rpc, USDC_ADDR, VAULT, max_block_age_s=300).ok
    assert "stale" in read_reserves(rpc, USDC_ADDR, VAULT, max_block_age_s=300).error
    assert read_reserves(rpc, USDC_ADDR, VAULT, max_block_age_s=None).ok
