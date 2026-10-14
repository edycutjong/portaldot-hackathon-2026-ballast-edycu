"""Watchdog: the freeze decision, the reason remark, idempotence and preflight — offline, with fakes."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from substrateinterface import Keypair

import ballast.chain
import ballast.watchdog
from ballast.dispatch import OK
from ballast.multisig import multi_address
from ballast.sepolia import ReserveReading, compare
from ballast.watchdog import (  # noqa: I001
    ALREADY_FROZEN,
    DEFICIT,
    FAIL_CLOSED,
    LEVEL,
    OUTAGE,
    REMARK_MAX_BYTES,
    Decision,
    WatchConfig,
    Watchdog,
    asset_state,
    decide,
    freeze_remark,
    parse_remark,
    reserve_label,
)

H = "0x" + "ab" * 32
# public dev keys, offline tests only
W1, W2, OUTSIDER = (Keypair.create_from_uri(u).ss58_address for u in ("//BallastW1", "//BallastW2", "//Charlie"))
M_WATCH = multi_address([W1, W2], 1)


def ok(provider: str, reserves: int, number: int = 100, block_hash: str = H) -> ReserveReading:
    return ReserveReading(provider=provider, tag="latest", block_number=number, block_hash=block_hash, reserves=reserves)


def down(provider: str) -> ReserveReading:
    return ReserveReading(provider=provider, tag="latest", error=f"{provider}: connection refused")


# --- decide ------------------------------------------------------------------------------------------------
def test_level_when_reserves_cover_supply():
    d, since = decide(100, False, compare([ok("a", 100), ok("b", 100)]), None, 0.0)
    assert d.action == LEVEL and not d.freeze and since is None


def test_deficit_on_either_provider_freezes():
    # operator watcher rule: one provider short is enough (the other may lag)
    d, _ = decide(100, False, compare([ok("a", 70, 101, "0x" + "01" * 32), ok("b", 100, 100)]), None, 0.0)
    assert d.action == DEFICIT and d.freeze and d.reserves_min == 70
    assert [r["provider"] for r in d.short] == ["a"]


def test_deficit_with_one_provider_down_still_freezes():
    d, since = decide(100, False, compare([ok("a", 99), down("b")]), None, 5.0)
    assert d.action == DEFICIT and since is None


def test_one_provider_down_is_level_but_degraded():
    d, since = decide(100, False, compare([ok("a", 100), down("b")]), None, 5.0)
    assert d.action == LEVEL and "1 provider(s) down" in d.detail and since is None


def test_total_outage_waits_then_fails_closed():
    both_down = compare([down("a"), down("b")])
    d, since = decide(100, False, both_down, None, 1000.0, fail_closed_after=300)
    assert d.action == OUTAGE and not d.freeze and since == 1000.0
    d, since = decide(100, False, both_down, since, 1300.0, fail_closed_after=300)
    assert d.action == OUTAGE and d.down_for_s == 300.0  # not yet: strictly more than the timeout
    d, since = decide(100, False, both_down, since, 1300.5, fail_closed_after=300)
    assert d.action == FAIL_CLOSED and d.freeze and since == 1000.0


def test_outage_clock_resets_when_a_provider_answers():
    _, since = decide(100, False, compare([down("a")]), None, 0.0)
    _, since = decide(100, False, compare([ok("a", 100)]), since, 200.0)
    d, since = decide(100, False, compare([down("a")]), since, 400.0, fail_closed_after=300)
    assert d.action == OUTAGE and since == 400.0


def test_already_frozen_is_idempotent_even_in_deficit():
    d, _ = decide(100, True, compare([ok("a", 1)]), None, 0.0)
    assert d.action == ALREADY_FROZEN and not d.freeze


def test_exactly_backed_is_level():
    d, _ = decide(100, False, compare([ok("a", 100)]), None, 0.0)
    assert d.action == LEVEL


# --- remark ------------------------------------------------------------------------------------------------
def test_deficit_remark_names_the_short_reading():
    d, _ = decide(100_000_000, False, compare([ok("anvil", 70_000_000, 5, H)]), None, 0.0)
    text = freeze_remark(2001, d, ["anvil"])
    assert text == f"BALLAST/1|freeze|a=2001|reason=deficit|s=100000000|r=70000000|p=anvil|eb=5|eh={H}"
    assert parse_remark(text) == {"type": "freeze", "a": "2001", "reason": "deficit", "s": "100000000",
                                  "r": "70000000", "p": "anvil", "eb": "5", "eh": H}


def test_fail_closed_remark():
    d = Decision(FAIL_CLOSED, 100, down_for_s=301.7)
    assert freeze_remark(1, d, ["publicnode", "drpc"]) == \
        "BALLAST/1|freeze|a=1|reason=providers-down|s=100|down=301s|p=publicnode,drpc"  # spec: reason=providers-down


def test_remark_worst_case_fits_the_budget():
    u128, u256 = 2**128 - 1, 2**256 - 1
    d, _ = decide(u128 * 2, False, compare([ok("publicnode", u256 // 2**200, 99_999_999, H)]), None, 0.0)
    d.short[0]["reserves"] = str(u128)  # worst case: a u128-sized reading in the remark
    text = freeze_remark(2**32 - 1, d, ["publicnode"])
    assert len(text.encode()) <= REMARK_MAX_BYTES


def test_no_remark_for_non_freeze_actions():
    with pytest.raises(ValueError):
        freeze_remark(1, Decision(LEVEL, 1), ["a"])


@pytest.mark.parametrize("bad", ["HELLO|x", "BALLAST/1", "BALLAST/1|freeze|novalue", "BALLAST/2|freeze|a=1"])
def test_parse_remark_rejects(bad):
    with pytest.raises(ValueError):
        parse_remark(bad)


# --- chain state shapes ------------------------------------------------------------------------------------
def test_asset_state_modern_and_1002_shapes():
    assert asset_state(1, {"supply": 5, "status": "Frozen", "freezer": M_WATCH}).frozen
    assert not asset_state(1, {"supply": 5, "status": "Live"}).frozen
    assert asset_state(1, {"supply": 5, "is_frozen": True}).frozen  # spec 1002 AssetDetails
    assert not asset_state(1, None).exists


def test_reserve_labels():
    assert reserve_label(11155111) == "Sepolia"
    assert reserve_label(31337) == "local-anvil (not Sepolia)"
    assert "unrecognised" in reserve_label(1)
    assert "no provider" in reserve_label(None)


# --- the loop, with fakes ----------------------------------------------------------------------------------
class FakeSubstrate:
    ss58_format = 42

    def __init__(self, assets, metadata=None, free=10**18):
        self.assets, self.metadata_, self.free = assets, metadata or {}, free
        self.composed = []

    def query(self, module, item, params, block_hash=None):
        if item == "Asset":
            return SimpleNamespace(value=self.assets.get(params[0]))
        if item == "Account":
            return SimpleNamespace(value={"data": {"free": self.free}})
        return SimpleNamespace(value=self.metadata_.get(params[0]))

    def get_constant(self, module, name):
        return SimpleNamespace(value=10**14)

    def get_payment_info(self, call, keypair):
        return {"partialFee": 10**12}

    def compose_call(self, call_module, call_function, call_params):
        c = {"call": f"{call_module}.{call_function}", "params": call_params}
        self.composed.append(c)
        return c


class FakeHead:
    def __init__(self, numbers):
        self.numbers = list(numbers)
        self.current = self.numbers[0]

    def call(self, method, params):
        if method == "chain_getBlockHash":
            self.current = self.numbers.pop(0) if len(self.numbers) > 1 else self.numbers[0]
            return f"0x{self.current:064x}"
        return {"number": hex(self.current)}


class FakeEvm:
    def __init__(self, name, reserves=None, decimals=6):
        self.name, self.reserves, self.decimals = name, reserves, decimals

    def call(self, method, params):
        import time as _time

        from ballast.sepolia import ProviderError

        if self.reserves is None:
            raise ProviderError(f"{self.name}: down")
        if method == "eth_chainId":
            return hex(31337)
        if method == "eth_getBlockByNumber":
            return {"number": "0x10", "hash": H, "timestamp": hex(int(_time.time()))}
        if params[1] == "latest":  # decimals()
            return f"0x{self.decimals:064x}"
        return f"0x{self.reserves:064x}"


def make_dog(monkeypatch, *, reserves, frozen=False, freezer=M_WATCH, signer=W2, heads=(10, 11, 12, 13),
             outcomes=None, threshold=1, free=10**18, decimals=6, providers=None):
    """`outcomes`: per-submit behaviour, in order — "ok", "raise", "inner-err" (default: always "ok")."""
    status = "Frozen" if frozen else "Live"
    substrate = FakeSubstrate(
        {1: {"supply": 60, "status": status, "freezer": freezer}, 2: {"supply": 40, "status": "Live"}},
        {1: {"decimals": 6}, 2: {"decimals": 6}},
        free=free,
    )
    submitted = []
    plan = list(outcomes or [])

    def fake_submit(sub, profile, keypair, module, function, params, **kw):
        submitted.append((module, function, params))
        kind = plan.pop(0) if plan else "ok"
        if kind == "raise":
            raise ConnectionError("pool full")
        if kind == "inner-err":
            err = SimpleNamespace(ok=False, __str__=lambda self=None: "Err(Assets.NoPermission)")
            return SimpleNamespace(outcome=OK, inner=[err], extrinsic_id="12-2", event_names=lambda: [],
                                   as_dict=lambda: {"extrinsic_id": "12-2"})
        substrate.assets[1]["status"] = "Frozen"
        return SimpleNamespace(
            outcome=OK, inner=[OK], extrinsic_id="12-2", event_names=lambda: ["Assets.AssetFrozen"],
            as_dict=lambda: {"extrinsic_id": "12-2"},
        )

    monkeypatch.setattr(ballast.chain, "submit", fake_submit)
    logs = []
    cfg = WatchConfig(breaker_id=1, supply_ids=[1, 2], watchers=[W1, W2], threshold=threshold,
                      token="0x" + "00" * 20, holder="0x" + "11" * 20, poll_blocks=2, fail_closed_after=300,
                      poll_interval_s=0)
    clock = iter(range(0, 10_000, 1))
    dog = Watchdog(substrate=substrate, profile=SimpleNamespace(name="standin-upstream"), head_rpc=FakeHead(heads),
                   keypair=SimpleNamespace(ss58_address=signer),
                   providers=providers or [FakeEvm("a", reserves, decimals)], cfg=cfg,
                   log=lambda event, **f: logs.append({"event": event, **f}) or {"event": event, **f},
                   clock=lambda: float(next(clock)), sleep=lambda s: None)
    return dog, substrate, submitted, logs


def test_check_freezes_through_the_watcher_multisig_with_a_reason(monkeypatch):
    dog, substrate, submitted, logs = make_dog(monkeypatch, reserves=70)
    dog.check(10, H)
    assert len(submitted) == 1
    module, function, params = submitted[0]
    assert (module, function) == ("Utility", "batch_all")
    remark, multisig = params["calls"]
    assert remark["call"] == "System.remark_with_event"
    assert remark["params"]["remark"].startswith("BALLAST/1|freeze|a=1|reason=deficit|s=100|r=70|p=a|")
    assert multisig["call"] == "Multisig.as_multi_threshold_1"
    assert multisig["params"]["other_signatories"] == [W1]  # the other member only, never the caller
    assert multisig["params"]["call"] == {"call": "Assets.freeze_asset", "params": {"id": 1}}
    assert [entry["event"] for entry in logs] == ["check", "freeze-submit", "freeze"]


def test_level_check_submits_nothing(monkeypatch):
    dog, _, submitted, logs = make_dog(monkeypatch, reserves=100)
    record = dog.check(10, H)
    assert submitted == [] and record["decision"]["action"] == LEVEL


def test_already_frozen_submits_nothing(monkeypatch):
    dog, _, submitted, _ = make_dog(monkeypatch, reserves=1, frozen=True)
    assert dog.check(10, H)["decision"]["action"] == ALREADY_FROZEN and submitted == []


def test_run_checks_every_n_blocks_and_stops_once_frozen(monkeypatch):
    dog, _, submitted, logs = make_dog(monkeypatch, reserves=70, heads=(10, 11, 12, 13))
    assert dog.run(until_frozen=True, max_seconds=100) == 0
    checks = [e["head"] for e in logs if e["event"] == "check"]
    assert checks == [10] and len(submitted) == 1 and logs[-1]["event"] == "stop"


def test_run_polls_heads_and_skips_until_n_blocks_passed(monkeypatch):
    dog, _, submitted, logs = make_dog(monkeypatch, reserves=100, heads=(10, 11, 12, 13, 14, 14))
    assert dog.run(until_frozen=True, max_seconds=8) == 4  # timed out, never frozen
    assert [e["head"] for e in logs if e["event"] == "check"] == [10, 12, 14] and submitted == []


def test_preflight_refuses_a_breaker_whose_freezer_is_not_the_watcher_set(monkeypatch):
    dog, *_ = make_dog(monkeypatch, reserves=100, freezer=OUTSIDER)
    with pytest.raises(RuntimeError, match="not the watcher set"):
        dog.preflight()


def test_preflight_refuses_a_key_outside_the_set(monkeypatch):
    dog, *_ = make_dog(monkeypatch, reserves=100, signer=OUTSIDER)
    with pytest.raises(RuntimeError, match="not in the watcher set"):
        dog.preflight()


def test_preflight_reports_the_reserve_label(monkeypatch):
    dog, *_ = make_dog(monkeypatch, reserves=100)
    pre = dog.preflight()
    assert pre["reserve"] == "local-anvil (not Sepolia)" and pre["m_watch"] == M_WATCH and pre["asset_decimals"] == 6


# --- failure paths --------------------------------------------------------------------------------------------
def test_submit_error_is_critical_and_retried_on_the_next_poll(monkeypatch):
    dog, substrate, submitted, logs = make_dog(monkeypatch, reserves=70, heads=(10, 11, 12, 13),
                                               outcomes=["raise", "ok"])
    dog.cfg.poll_blocks = 10
    assert dog.run(until_frozen=True, max_seconds=50) == 0
    events = [e["event"] for e in logs]
    assert events.count("freeze-error") == 1 and events.count("freeze") == 1
    assert next(e for e in logs if e["event"] == "freeze-error")["level"] == "critical"
    # retried on the next poll (the fake head also advances for the state read and the race probe), not 10 blocks later
    checks = [e["head"] for e in logs if e["event"] == "check"]
    assert len(checks) == 2 and checks[1] - checks[0] < dog.cfg.poll_blocks and len(submitted) == 2


def test_inner_error_is_a_failed_freeze_and_retried(monkeypatch):
    dog, _, submitted, logs = make_dog(monkeypatch, reserves=70, heads=(10, 11, 12), outcomes=["inner-err", "ok"])
    assert dog.run(until_frozen=True, max_seconds=50) == 0
    failed = next(e for e in logs if e["event"] == "freeze-failed")
    assert failed["level"] == "critical" and len(submitted) == 2


def test_fail_closed_through_check_submits_the_reason(monkeypatch):
    dog, _, submitted, logs = make_dog(monkeypatch, reserves=None)  # every provider down
    dog.cfg.fail_closed_after = 2
    for head in (10, 12, 14, 16):
        dog.check(head, H)
    actions = [e["decision"]["action"] for e in logs if e["event"] == "check"]
    assert actions[:3] == [OUTAGE, OUTAGE, OUTAGE] and FAIL_CLOSED in actions
    remark = submitted[0][2]["calls"][0]["params"]["remark"]
    assert remark.startswith("BALLAST/1|freeze|a=1|reason=providers-down|s=100|down=") and remark.endswith("|p=a")


def test_check_and_head_errors_do_not_kill_the_loop(monkeypatch):
    dog, _, submitted, logs = make_dog(monkeypatch, reserves=70, heads=(10, 11, 12))
    calls = {"n": 0}
    real_head = dog.head

    def flaky_head():
        calls["n"] += 1
        if calls["n"] == 1:
            raise OSError("node restarting")
        return real_head()

    real_assets = dog.assets
    state = {"n": 0}

    def flaky_assets(block_hash):
        state["n"] += 1
        if state["n"] == 1:
            raise RuntimeError("decode hiccup")
        return real_assets(block_hash)

    dog.head, dog.assets = flaky_head, flaky_assets
    assert dog.run(until_frozen=True, max_seconds=50) == 0
    events = [e["event"] for e in logs]
    assert "head-error" in events and "check-error" in events and "freeze" in events


def test_malformed_provider_cannot_veto_a_deficit(monkeypatch):
    class Garbage(FakeEvm):
        def call(self, method, params):
            return "<html>rate limited</html>" if method == "eth_getBlockByNumber" else super().call(method, params)

    dog, _, submitted, logs = make_dog(monkeypatch, reserves=70,
                                       providers=[FakeEvm("a", 70), Garbage("b", 100)])
    record = dog.check(10, H)
    assert record["decision"]["action"] == DEFICIT and len(submitted) == 1


def test_preflight_rejects_threshold_above_one(monkeypatch):
    dog, *_ = make_dog(monkeypatch, reserves=100, threshold=2)
    dog.cfg.watchers = [W1, W2]
    dog.substrate.assets[1]["freezer"] = multi_address([W1, W2], 2)
    with pytest.raises(RuntimeError, match="1-of-N"):
        dog.preflight()


def test_preflight_rejects_a_decimals_mismatch(monkeypatch):
    dog, *_ = make_dog(monkeypatch, reserves=100, decimals=18)
    with pytest.raises(RuntimeError, match="decimals mismatch"):
        dog.preflight()


def test_preflight_rejects_an_unfunded_watcher(monkeypatch):
    dog, *_ = make_dog(monkeypatch, reserves=100, free=10**14)  # exactly ED: cannot pay any fee
    with pytest.raises(RuntimeError, match="needs >= ED"):
        dog.preflight()


def test_long_provider_names_never_block_the_fail_closed_remark():
    d = Decision(FAIL_CLOSED, 100, down_for_s=301)
    text = freeze_remark(1, d, ["p" * 200, "q" * 200])
    assert text.endswith("|p=2-providers") and len(text.encode()) <= REMARK_MAX_BYTES


def test_lost_race_is_not_a_failure(monkeypatch):
    dog, substrate, submitted, logs = make_dog(monkeypatch, reserves=70, outcomes=["raise"])
    real_submit = ballast.chain.submit

    def racing_submit(*a, **k):
        substrate.assets[1]["status"] = "Frozen"  # another watcher froze it first
        return real_submit(*a, **k)

    monkeypatch.setattr(ballast.chain, "submit", racing_submit)
    dog.check(10, H)
    assert [e["event"] for e in logs] == ["check", "freeze-submit", "freeze-raced"] and not dog.freeze_failed


def test_retries_are_fast_then_every_n_blocks_and_never_stop(monkeypatch):
    dog, _, submitted, logs = make_dog(monkeypatch, reserves=70, heads=tuple(range(10, 80)),
                                       outcomes=["raise"] * 50)
    dog.cfg.poll_blocks = 10
    dog.raced = lambda head, why: False  # keep the fake head sequence simple
    assert dog.run(until_frozen=True, max_seconds=60) == 4
    heads = [e["head"] for e in logs if e["event"] == "check"]
    gaps = [b - a for a, b in zip(heads, heads[1:])]
    assert all(g < 10 for g in gaps[:3]) and all(g >= 10 for g in gaps[3:]) and len(heads) >= 6
    assert all(e["level"] == "critical" for e in logs if e["event"] == "freeze-error")
    assert dog.failures == len(heads)


def test_a_logging_failure_never_blocks_the_freeze(monkeypatch, tmp_path):
    from ballast.watchdog import JsonLog

    log = JsonLog(str(tmp_path / "w.jsonl"), echo=True)
    log._fh.close()  # writes now raise ValueError (closed file)
    dog, _, submitted, _ = make_dog(monkeypatch, reserves=70)
    dog.log = log
    dog.check(10, H)
    assert len(submitted) == 1 and log.dropped >= 2


def test_zero_reserves_is_a_deficit(monkeypatch):
    d, _ = decide(100, False, compare([ok("a", 0)]), None, 0.0)
    assert d.action == DEFICIT and d.reserves_min == 0
    dog, _, submitted, _ = make_dog(monkeypatch, reserves=0)
    assert dog.check(10, H)["decision"]["action"] == DEFICIT and len(submitted) == 1


def test_preflight_refuses_when_providers_answer_but_the_reserve_is_unreadable(monkeypatch):
    class NoCode(FakeEvm):
        def call(self, method, params):
            if method == "eth_call":
                return "0x"  # no contract at the token address
            return super().call(method, params)

    dog, *_ = make_dog(monkeypatch, reserves=100, providers=[NoCode("a", 100)])
    with pytest.raises(RuntimeError, match="no valid reserve reading"):
        dog.preflight()


def test_preflight_arms_when_every_provider_is_down(monkeypatch):
    # nothing to read at start is an outage, not a misconfiguration: arm, and let I6 decide
    dog, *_ = make_dog(monkeypatch, reserves=None)
    assert dog.preflight()["reserve"].startswith("unknown")


def test_reserves_are_read_before_supply(monkeypatch):
    """A redemption burns (supply down) then releases (reserves down): reading reserves first never sees a gap."""
    order = []
    dog, _, submitted, _ = make_dog(monkeypatch, reserves=100)
    real_assets, real_read = dog.assets, ballast.watchdog.read_all

    def spy_assets(h):
        order.append("supply")
        return real_assets(h)

    def spy_read(*a, **k):
        order.append("reserves")
        return real_read(*a, **k)

    monkeypatch.setattr(ballast.watchdog, "read_all", spy_read)
    dog.assets = spy_assets
    dog.check(10, H)
    assert order == ["reserves", "supply"]


def test_vanished_asset_is_a_check_error_not_level(monkeypatch):
    dog, substrate, submitted, _ = make_dog(monkeypatch, reserves=100)
    del substrate.assets[2]
    with pytest.raises(RuntimeError, match="no longer exist"):
        dog.check(10, H)


def test_destroying_asset_is_not_freezable(monkeypatch):
    dog, substrate, submitted, _ = make_dog(monkeypatch, reserves=1)
    substrate.assets[1]["status"] = "Destroying"
    record = dog.check(10, H)
    assert record["decision"]["action"] == ALREADY_FROZEN and record["status"] == "Destroying" and submitted == []


def test_inner_error_while_someone_else_froze_it_is_a_race(monkeypatch):
    dog, substrate, submitted, logs = make_dog(monkeypatch, reserves=70, outcomes=["inner-err"])
    real = ballast.chain.submit

    def submit_then_other_watcher_freezes(*a, **k):
        r = real(*a, **k)
        substrate.assets[1]["status"] = "Frozen"
        return r

    monkeypatch.setattr(ballast.chain, "submit", submit_then_other_watcher_freezes)
    dog.check(10, H)
    assert logs[-1]["event"] == "freeze-raced" and not dog.freeze_failed


def test_log_file_failure_still_echoes(monkeypatch, tmp_path, capsys):
    from ballast.watchdog import JsonLog

    log = JsonLog(str(tmp_path / "w.jsonl"), echo=True, profile="p")
    log._fh.close()
    log("freeze-error", level="critical", message="pool full")
    err = capsys.readouterr().err
    assert "freeze-error" in err and "pool full" in err and "1 record(s) dropped" in err
