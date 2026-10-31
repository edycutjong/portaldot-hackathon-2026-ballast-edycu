import importlib.util
import json
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("bench_report", Path(__file__).resolve().parent.parent / "scripts" / "bench_report.py")
bench_report = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bench_report)


def test_rank_is_nearest_rank_and_an_actual_sample():
    values = [float(v) for v in range(1, 21)]  # n = 20: p50 = 10th, p95 = 19th
    assert bench_report.rank(values, 0.50) == 10.0
    assert bench_report.rank(values, 0.95) == 19.0
    assert bench_report.rank([7.0], 0.95) == 7.0
    assert bench_report.rank([3.0, 1.0, 2.0], 0.50) == 2.0  # order of the input does not matter


def test_stats_empty_and_filled():
    assert bench_report.stats([]) == {"n": 0}
    s = bench_report.stats([10.0, 12.0, 30.0])
    assert (s["n"], s["min"], s["p50"], s["p95"], s["max"]) == (3, 10.0, 12.0, 30.0, 30.0)
    assert s["mean"] == 17.333


def _receipt(fee=2990576854518):
    return {"extrinsic_id": "10-1", "events": [
        {"module_id": "Balances", "event_id": "Withdraw", "attributes": {"amount": fee}},
        {"module_id": "TransactionPayment", "event_id": "TransactionFeePaid", "attributes": {"actual_fee": fee, "tip": 0}}]}


def test_fee_is_the_transaction_fee_paid_event():
    assert bench_report.fee_paid(_receipt()) == 2990576854518
    assert bench_report.tpot(2990576854518) == "0.0299"


def test_sepolia_sample_group_and_watcher():
    step = {"name": "watcher W2 freezes asset 4401 through M_watch", "as_expected": True, "receipt": _receipt()}
    local = {"verdict": "PASS", "steps": [step], "watchers_note": "W1 and W2 run as two processes on ONE machine (W2 on GitHub Actions is a later phase)",
             "notes": {"drain -> freeze included (wall clock)": "10.61 s"}}
    actions = {**local, "watchers_note": "W1 is OFF; W2 runs on GitHub Actions (.github/workflows/watcher-w2.yml)"}
    (a,) = bench_report.sepolia_samples(Path("x.json"), local)
    (b,) = bench_report.sepolia_samples(Path("y.json"), actions)
    assert (a["group"], a["watcher"], a["drain_to_freeze_s"]) == ("v3-sepolia-local", "W2", 10.61)
    assert (b["group"], b["watcher"]) == ("v3-sepolia-actions", "W2 (Actions)")
    assert bench_report.sepolia_samples(Path("z.json"), {**local, "notes": {}}) == []


def test_bench_samples_skip_iterations_without_a_freeze():
    run = {"verdict": "ERROR", "bench": {"iterations": [
        {"i": 1, "watcher": "W1", "freeze_ok": True, "freeze_extrinsic": "5-1", "drain_to_freeze_s": 11.5, "freeze_fee_planck": 3,
         "freeze_blocks_after_drain_head": 3},
        {"i": 2, "watcher": "W2", "ok": False}]}}
    got = bench_report.bench_samples(Path("b.json"), run)
    assert [s["i"] for s in got] == [1] and got[0]["group"] == "v3-anvil"
    json.dumps(got)
