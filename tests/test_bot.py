"""Reserve bot gates, finalized reader and decision log (offline)."""

from __future__ import annotations

import pytest
from substrateinterface import Keypair

from ballast.bot import mint_gate, parse_amount, read_finalized, set_team_gate, thaw_gate
from ballast.store import Store
from test_sepolia import FakeRpc, USDC_ADDR, VAULT

S = 50_000_000
H1, H2 = "0x" + "aa" * 32, "0x" + "bb" * 32
M_MINT = Keypair.create_from_uri("//m_mint").ss58_address
W = Keypair.create_from_uri("//w").ss58_address
A = Keypair.create_from_uri("//a").ss58_address


def test_mint_signed_when_reserves_cover_supply_plus_amount():
    g = mint_gate(2 * S, 0, S, S, frozen=False)
    assert g.sign and g.decision == "signed"


def test_over_mint_refused_by_one_unit():
    g = mint_gate(2 * S, S, S, 1, frozen=False)
    assert not g.sign and g.reason.startswith("over-mint")


def test_mint_refused_while_frozen_even_with_reserves():
    g = mint_gate(10 * S, 0, 0, 1, frozen=True)
    assert not g.sign and "I7" in g.reason


def test_mint_refused_when_reserves_unknown_or_amount_not_positive():
    assert not mint_gate(None, 0, 0, 1, frozen=False).sign
    assert not mint_gate(10 * S, 0, 0, 0, frozen=False).sign


def test_thaw_gate():
    assert not thaw_gate(False, 2 * S, S, S).sign  # nothing to thaw
    assert not thaw_gate(True, 2 * S - 1, S, S).sign  # still short at finality
    assert not thaw_gate(True, None, S, S).sign
    assert thaw_gate(True, 2 * S, S, S).sign


def test_set_team_gate_only_with_issuer_and_freezer_unchanged():
    cur = {"issuer": M_MINT, "freezer": W}
    assert set_team_gate(cur, {"issuer": M_MINT, "freezer": W, "admin": A}, M_MINT).sign
    assert not set_team_gate(cur, {"issuer": A, "freezer": W}, M_MINT).sign
    assert not set_team_gate(cur, {"issuer": M_MINT, "freezer": A}, M_MINT).sign


def test_parse_amount():
    assert parse_amount("50.00", 6) == S
    assert parse_amount("0.000001", 6) == 1
    for bad in ("0", "-1", "0.0000001", "abc"):
        with pytest.raises(ValueError):
            parse_amount(bad, 6)


def test_finalized_uses_the_lowest_reading():
    a = FakeRpc("drpc", {"finalized": (100, H1)}, {H1: 2 * S})
    b = FakeRpc("publicnode", {"finalized": (99, H2)}, {H2: S})
    fin = read_finalized([a, b], USDC_ADDR, VAULT)
    assert fin.ok and fin.reserves == S and fin.provider == "publicnode" and fin.block_hash == H2


def test_finalized_refuses_on_disagreement_or_silence():
    a = FakeRpc("drpc", {"finalized": (100, H1)}, {H1: 2 * S})
    fork = FakeRpc("publicnode", {"finalized": (100, H2)}, {H2: 2 * S})
    fin = read_finalized([a, fork], USDC_ADDR, VAULT)
    assert not fin.ok and "disagree" in fin.reason
    down = [FakeRpc("drpc", {}, {}, down=True), FakeRpc("publicnode", {}, {}, down=True)]
    fin = read_finalized(down, USDC_ADDR, VAULT)
    assert not fin.ok and fin.reserves is None and len(fin.readings) == 2


def test_finalized_survives_one_provider_down():
    a = FakeRpc("drpc", {"finalized": (100, H1)}, {H1: 2 * S})
    fin = read_finalized([a, FakeRpc("publicnode", {}, {}, down=True)], USDC_ADDR, VAULT)
    assert fin.ok and fin.reserves == 2 * S and "1 provider(s) down" in fin.reason


def test_store_logs_decisions(tmp_path):
    st = Store(tmp_path / "b.db")
    row = st.request(kind="mint", amount="1", decision="refused", reason="over-mint", frozen=0)
    st.set_exec(row, "12-1")
    st.readings([{"provider": "p", "tag": "finalized", "block_number": 1, "block_hash": H1, "reserves": "5",
                  "error": None, "read_at": "t"}])
    rows = st.rows("mint_request")
    assert rows[0]["decision"] == "refused" and rows[0]["exec_tx"] == "12-1"
    assert st.rows("provider_reading")[0]["block_hash"] == H1
