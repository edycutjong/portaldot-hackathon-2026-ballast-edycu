import copy

import ballast.receipts as receipts
from ballast.receipts import render_receipts_md, score, summarize


def _receipt(text="Ok", ok=True):
    return {
        "call": "Assets.create", "extrinsic_id": "10-2", "block_hash": "0x" + "aa" * 32, "extrinsic_hash": "0x" + "bb" * 32,
        "outcome": {"ok": ok, "pallet": None, "error": None, "text": text}, "inner": [], "events": [], "step": "create",
    }


def _run(profile="standin-upstream", is_standin=True):
    return {
        "chain": {"profile": profile, "is_standin": is_standin, "label": f"{profile} label", "genesis_hash": "0x" + "cc" * 32,
                  "spec_name": "node", "spec_version": 268},
        "started_at": "2026-10-14T09:00:00Z", "asset_id": 1001,
        "steps": [
            {"name": "create", "expected": "Ok", "as_expected": True, "counted": True, "signer_role": "A",
             "events_seen": [], "receipt": _receipt()},
            {"name": "observation", "expected": "observation only", "as_expected": True, "counted": False,
             "signer_role": "A", "events_seen": [], "receipt": _receipt("Err(Assets.AssetNotLive)", ok=False)},
        ],
        "state_checks": [{"what": "status", "expected": "Frozen", "observed": "Frozen", "ok": True, "block_hash": "0x" + "dd" * 32}],
    }


def test_verdict_needs_every_counted_step_and_state_check():
    run = summarize(_run())
    assert run["verdict"] == "PASS" and score(run) == "1/1 steps as expected + 1 observation, 1/1 state checks"
    bad_check = _run()
    bad_check["state_checks"][0].update(observed="Live", ok=False)
    assert summarize(bad_check)["verdict"] == "FAIL"
    bad_step = _run()
    bad_step["steps"][0]["as_expected"] = False
    assert summarize(bad_step)["verdict"] == "FAIL"
    errored = _run()
    errored["error"] = "SubstrateRequestException: pool full"
    assert summarize(errored)["verdict"] == "ERROR"


def test_observation_steps_never_decide_the_verdict():
    run = _run()
    run["steps"][1]["as_expected"] = False
    assert summarize(run)["verdict"] == "PASS"


def test_standin_and_v3_sections_are_labelled_differently(monkeypatch):
    standin = summarize(_run()) | {"_file": "a.json"}
    v3 = summarize(copy.deepcopy(_run("v3", is_standin=False))) | {"_file": "b.json"}
    monkeypatch.setattr(receipts, "load_runs", lambda *a, **k: [standin, v3])
    md = render_receipts_md()
    assert "## Stand-in receipts — standin-upstream (not V3)" in md
    assert "## V3 receipts — v3" in md and "Stand-in receipts — v3" not in md
    # the stand-in disclaimer appears once, under the stand-in heading only
    assert md.count("Nothing in this") == 1 and md.index("## V3 receipts") < md.index("## Stand-in receipts")
    assert "0x" + "aa" * 32 in md and "0x" + "bb" * 32 in md  # full hashes


def test_empty_evidence_renders_a_placeholder(monkeypatch):
    monkeypatch.setattr(receipts, "load_runs", lambda *a, **k: [])
    assert "_No receipts yet._" in render_receipts_md()
