"""Reserve bot gates, finalized reader and decision log (offline)."""

from __future__ import annotations

import pytest
from substrateinterface import Keypair

from ballast.bot import (freeze_anchor, last_freeze, mint_gate, parse_amount, read_finalized, read_view,
                         set_team_gate, thaw_gate)
from ballast.store import Store
from test_sepolia import FakeRpc, USDC_ADDR, VAULT

S = 50_000_000
H1, H2 = "0x" + "aa" * 32, "0x" + "bb" * 32
M_MINT = Keypair.create_from_uri("//m_mint").ss58_address
W = Keypair.create_from_uri("//w").ss58_address
A = Keypair.create_from_uri("//a").ss58_address


def test_mint_signed_when_reserves_cover_supply_plus_amount():
    g = mint_gate(2 * S, 2 * S, 0, S, S, frozen=False)
    assert g.sign and g.decision == "signed"


def test_over_mint_refused_by_one_unit():
    g = mint_gate(2 * S, 2 * S, S, S, 1, frozen=False)
    assert not g.sign and g.reason.startswith("over-mint")


def test_mint_refused_while_a_drain_is_not_yet_final():
    # finalized still shows the pre-drain balance; latest already shows the drain -> refuse (M1)
    g = mint_gate(10 * S, S, S, 0, 1, frozen=False)
    assert not g.sign and "not yet final" in g.reason


def test_mint_refused_while_frozen_even_with_reserves():
    g = mint_gate(10 * S, 10 * S, 0, 0, 1, frozen=True)
    assert not g.sign and "I7" in g.reason


def test_mint_refused_when_reserves_unknown_or_amount_not_positive():
    assert not mint_gate(None, 10 * S, 0, 0, 1, frozen=False).sign
    assert not mint_gate(10 * S, None, 0, 0, 1, frozen=False).sign
    assert not mint_gate(10 * S, 10 * S, 0, 0, 0, frozen=False).sign


def tg(frozen=True, fin=2 * S, latest=2 * S, fb=100, ts=None, anchor=None):
    return thaw_gate(frozen, fin, latest, S, S, finalized_block=fb, finalized_ts=ts,
                     anchor={"eb": 90} if anchor is None else anchor)


def test_thaw_gate():
    assert not tg(frozen=False).sign  # nothing to thaw
    assert not tg(fin=2 * S - 1).sign  # still short at finality
    assert not tg(latest=2 * S - 1).sign  # short again at latest
    assert not tg(fin=None).sign and not tg(fb=None).sign
    assert tg().sign
    assert tg(fb=90).sign


def test_thaw_refused_on_a_finalized_reading_older_than_the_drain():
    # finality lags: a finalized block before the drain still shows full reserves — never a reason to thaw
    g = tg(fb=80)
    assert not g.sign and "older than the deficit block" in g.reason
    assert not tg(anchor={}).sign  # freeze not found: fail closed


def test_thaw_after_a_freeze_without_eb_is_anchored_by_time():
    # heartbeat / providers-down freezes carry no deficit block: finality must pass the freeze's own time (M2)
    anchor = {"eb": None, "freeze_ts_ms": 1_000_000_000}
    g = tg(ts=999_999, anchor=anchor)
    assert not g.sign and "predates the freeze" in g.reason
    assert tg(ts=1_000_000, anchor=anchor).sign
    assert not tg(ts=None, anchor=anchor).sign
    assert not tg(ts=2_000_000, anchor={"eb": None, "freeze_ts_ms": None}).sign


class Ev:
    def __init__(self, module, event, attrs, idx=1):
        self.value = {"module_id": module, "event_id": event, "attributes": attrs, "extrinsic_idx": idx}


class EventChain:
    """Blocks with events; `frozen_at` = {block: extrinsic index} of AssetFrozen events for asset 1."""

    def __init__(self, frozen_at, other=None):
        self.frozen_at, self.other, self.reads = frozen_at, other or {}, 0

    def get_block_hash(self, n):
        return f"0x{n:064x}"

    def get_events(self, block_hash):
        self.reads += 1
        n = int(block_hash, 16)
        evs = [Ev("Assets", "AssetFrozen", {"asset_id": 1}, self.frozen_at[n])] if n in self.frozen_at else []
        if n in self.other:
            evs.append(Ev("Assets", "AssetFrozen", {"asset_id": self.other[n]}, 2))
        return evs


def test_last_freeze_is_the_most_recent_asset_frozen_event():
    # frozen at 50, thawed, frozen again at 300: the gate must anchor on 300, not 50 (M3)
    chain = EventChain({50: 1, 300: 3}, other={350: 2037})
    f = last_freeze(chain, 1, 400)
    assert f["block_number"] == 300 and f["extrinsic_index"] == 3
    assert last_freeze(chain, 1, 299)["block_number"] == 50


def test_last_freeze_none_within_the_lookback():
    assert last_freeze(EventChain({50: 1}), 1, 400, max_lookback=100) is None
    assert last_freeze(EventChain({}), 1, 30) is None


class AnchorChain:
    def __init__(self, sender, extrinsic_index=1):
        self.sender, self.idx = sender, extrinsic_index

    def query(self, pallet, item, params=None, block_hash=None):
        class V:
            value = 1_700_000_000_000
        return V()


def test_freeze_anchor_trusts_only_a_watcher_remark_in_the_freezing_extrinsic(monkeypatch):
    import ballast.remarks as remarks

    text = "BALLAST/1|freeze|a=1|reason=deficit|s=1|eb=77|eh=0x" + "cd" * 32
    freeze = {"block_number": 300, "block_hash": "0x" + "01" * 32, "extrinsic_index": 3}

    def run(sender, idx):
        monkeypatch.setattr(remarks, "block_remarks", lambda *a, **k: [{"extrinsic_index": idx, "sender": sender,
                                                                         "text": text}])
        return freeze_anchor(AnchorChain(sender), 1, freeze, [W])

    good = run(W, 3)
    assert good["eb"] == 77 and good["reason"] == "deficit" and good["freeze_ts_ms"] == 1_700_000_000_000
    assert run(A, 3)["eb"] is None  # not a watcher
    assert run(W, 2)["eb"] is None  # another extrinsic in the block


M_ADMIN = Keypair.create_from_uri("//m_admin").ss58_address


def test_set_team_gate_only_for_the_role_map():
    cur = {"issuer": M_MINT, "freezer": W, "admin": M_ADMIN}
    assert set_team_gate(cur, {"issuer": M_MINT, "freezer": W, "admin": M_ADMIN}, M_MINT, M_ADMIN).sign
    assert not set_team_gate(cur, {"issuer": A, "freezer": W, "admin": M_ADMIN}, M_MINT, M_ADMIN).sign
    assert "freezer would change" in set_team_gate(cur, {"issuer": M_MINT, "freezer": A, "admin": M_ADMIN},
                                                   M_MINT, M_ADMIN).reason
    g = set_team_gate(cur, {"issuer": M_MINT, "freezer": W, "admin": A}, M_MINT, M_ADMIN)  # B1: admin swap
    assert not g.sign and "admin must stay M_admin" in g.reason


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


def fresh(name, finalized, latest, balances, down=False):
    rpc = FakeRpc(name, {"finalized": finalized, "latest": latest}, balances, down=down)
    return rpc


def test_view_refuses_when_any_provider_is_down():
    a = fresh("drpc", (100, H1), (110, H2), {H1: 2 * S, H2: 2 * S})
    v = read_view([a, FakeRpc("publicnode", {}, {}, down=True)], USDC_ADDR, VAULT, max_finalized_age_s=None,
                  max_latest_age_s=None)
    assert not v.ok and "provider(s) without a valid" in v.reason


def test_view_reads_finalized_and_latest_from_every_provider():
    a = fresh("drpc", (100, H1), (110, H2), {H1: 2 * S, H2: S})
    b = fresh("publicnode", (100, H1), (110, H2), {H1: 2 * S, H2: S})
    v = read_view([a, b], USDC_ADDR, VAULT, max_finalized_age_s=None, max_latest_age_s=None)
    assert v.ok and v.finalized.reserves == 2 * S and v.latest.reserves == S
    assert v.finalized.block_timestamp == 1_760_000_100


def test_view_refuses_a_stale_finalized_block():
    a = fresh("drpc", (100, H1), (110, H2), {H1: 2 * S, H2: 2 * S})
    v = read_view([a], USDC_ADDR, VAULT, max_finalized_age_s=3600, max_latest_age_s=None)  # blocks dated 2025
    assert not v.ok and "stale" in v.finalized.readings[0]["error"] and v.latest.ok


def test_store_records_execution_outcome_and_oracle_mirror(tmp_path):
    st = Store(tmp_path / "b.db")
    row = st.request(kind="mint", amount="1", decision="signed", reason="ok", frozen=0)
    st.set_exec(row, "12-1", "signed-inner-failed")
    assert st.rows("mint_request")[0]["decision"] == "signed-inner-failed"
    st.attestation(kind="attest", remark="x", remark_tx="20-2")
    st.set_oracle_tx("20-2", "21-2")
    assert st.rows("attestation")[0]["oracle_tx"] == "21-2"


def test_view_refuses_a_stale_latest_or_latest_below_finalized():
    import time
    now = int(time.time())

    class Rpc(FakeRpc):
        def __init__(self, name, blocks, balances, ages):
            super().__init__(name, blocks, balances)
            self.ages = ages

        def call(self, method, params):
            out = super().call(method, params)
            if method == "eth_getBlockByNumber":
                out["timestamp"] = hex(now - self.ages[params[0]])
            return out

    a = Rpc("drpc", {"finalized": (100, H1), "latest": (110, H2)}, {H1: 2 * S, H2: 2 * S},
            {"finalized": 900, "latest": 600})
    v = read_view([a], USDC_ADDR, VAULT)
    assert v.finalized.ok and not v.latest.ok  # latest 10 min old > 120 s
    b = Rpc("drpc", {"finalized": (100, H1), "latest": (90, H2)}, {H1: 2 * S, H2: 2 * S},
            {"finalized": 900, "latest": 5})
    v = read_view([b], USDC_ADDR, VAULT)
    assert not v.ok and "below the finalized block" in v.latest.reason


def test_lookback_is_w_in_measured_blocks():
    from ballast.bot import lookback_blocks

    class C:
        def get_block_hash(self, n):
            return n

        def query(self, *a, block_hash=None, **k):
            class V:
                value = block_hash * 6000  # 6 s blocks
            return V()

    assert lookback_blocks(C(), 1000) == 14_400  # 24 h of 6 s blocks


class FrozenChain:
    """Asset 1 frozen; AssetFrozen at `freezes` (block -> extrinsic idx); the head moves to `later` after the first
    scan (a re-freeze while the bot scanned)."""

    def __init__(self, freezes, head, later):
        self.freezes, self.head, self.later, self.calls = freezes, head, later, 0
        self.ss58_format = 42

    def get_block_number(self, _):
        self.calls += 1
        return self.head if self.calls == 1 else self.later

    def get_block_hash(self, n):
        return f"0x{n:064x}"

    def get_events(self, block_hash):
        n = int(block_hash, 16)
        return [Ev("Assets", "AssetFrozen", {"asset_id": 1}, self.freezes[n])] if n in self.freezes else []

    def query(self, pallet, item, params=None, block_hash=None):
        class V:
            value = 1_700_000_000_000 if item == "Now" else {"status": "Frozen", "supply": 5}
        return V()


def test_cosign_thaw_anchors_on_a_freeze_that_lands_while_it_scans(monkeypatch, tmp_path):
    import ballast.bot as bot_mod

    rm = type("RM", (), {"a": A, "a2": W, "b": "x", "watchers": [W], "mint_signatories": [], "admin_signatories": [], "admin_proposers": [A, W], "admin_threshold": 2})
    b = object.__new__(bot_mod.ReserveBot)
    b.substrate = FrozenChain({100: 1, 150: 4}, head=120, later=160)
    b.dep = type("D", (), {"breaker": 1})()
    b.rm, b.m_admin, b.log = rm, None, lambda m: None
    b.lock_path = tmp_path / "x.lock"
    seen = {}
    monkeypatch.setattr(bot_mod.ReserveBot, "compose", lambda self, f, **k: f)
    monkeypatch.setattr(bot_mod, "call_hash", lambda c: "0xhash")
    monkeypatch.setattr(bot_mod.ReserveBot, "_pending", lambda self, *a: object())
    monkeypatch.setattr(bot_mod, "lookback_blocks", lambda *a: 1000)
    monkeypatch.setattr(bot_mod, "freeze_anchor", lambda s, a, f, w: seen.__setitem__("anchor", dict(f)) or dict(f))

    class Stop(Exception):  # stop at the reserve read, right after the under-lock re-check
        pass

    monkeypatch.setattr(bot_mod.ReserveBot, "supplies", lambda self, bh=None: {"s1": 0, "s2": 0, "frozen": True,
                                                                            "status": "Frozen", "team_problems": []})
    monkeypatch.setattr(bot_mod.ReserveBot, "reserves", lambda self: (_ for _ in ()).throw(Stop()))
    with pytest.raises(Stop):
        b.cosign_thaw()
    assert seen["anchor"]["block_number"] == 150  # the newer freeze, found under the lock


def test_execute_failure_is_signed_unknown(tmp_path):
    import ballast.bot as bot_mod

    st = Store(tmp_path / "b.db")
    row = st.request(kind="mint", decision="signed", reason="ok", frozen=0)
    b = object.__new__(bot_mod.ReserveBot)
    b.substrate = b.profile = b.keypair = None
    b.store = st

    class Acct:
        def execute(self, *a, **k):
            raise TimeoutError("no inclusion within 60 s")

    out = {"reason": "covered", "call_hash": "0xab"}
    b._execute(Acct(), None, None, row, out, step="s", label="l", event="Assets.Issued")
    assert out["decision"] == "signed-unknown" and not out["executed_ok"] and "check the chain" in out["reason"]
    assert st.rows("mint_request")[0]["decision"] == "signed-unknown"
