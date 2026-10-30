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


def test_committed_receipts_md_is_exactly_the_render_of_committed_evidence():
    assert receipts.RECEIPTS_MD.read_text() == render_receipts_md()


def test_failure_cause_names_the_error_and_the_failed_steps():
    run = _run()
    run["steps"][0]["as_expected"] = False
    run["steps"][0]["receipt"]["outcome"]["text"] = "Err(Token.CannotCreate)"
    run["error"] = "Traceback (most recent call last):\n  ...\nRuntimeError: no freeze in the watchdog log (exit 4)"
    cause = receipts.failure_cause(summarize(run))
    assert cause.startswith("RuntimeError: no freeze in the watchdog log (exit 4)")
    assert "failed: create -> Err(Token.CannotCreate)" in cause


def test_summarize_strips_local_paths_from_errors():
    run = _run()
    run["error"] = f'File "{receipts.ROOT}/ballast/drill.py", line 1 in {receipts.Path.home()}/x'
    assert summarize(run)["error"] == 'File "<build>/ballast/drill.py", line 1 in ~/x'


def test_lead_is_the_newest_clean_pinned_pass(monkeypatch):
    def drill(started, verdict, dirty):
        r = _run() | {"kind": "drill", "scenario": "drain", "started_at": started, "verdict": verdict,
                      "reserve": {"label": "local-anvil (not Sepolia)"}, "watchdog_log": "w.jsonl", "_file": f"{started}.json",
                      "evm_steps": []}
        if dirty is not None:
            r["source"] = {"git_head": "abc1234def", "dirty": dirty}
        return summarize(r) | {"verdict": verdict}

    runs = [drill("2026-10-14T12:00:03Z", "FAIL", False), drill("2026-10-14T12:00:02Z", "PASS", True),
            drill("2026-10-14T12:00:01Z", "PASS", False), drill("2026-10-14T12:00:00Z", "PASS", None)]
    monkeypatch.setattr(receipts, "load_runs", lambda *a, **k: runs)
    md = render_receipts_md()
    lead = md.split("### Breaker drill")[1].split("\n")[0]
    assert "2026-10-14T12:00:01Z" in lead  # not the newer dirty PASS, not the newest FAIL
    assert "`abc1234` (UNCOMMITTED CHANGES)" in md and "not pinned" in md


def test_v3_probe_line_picks_the_newest_probe_by_its_own_timestamp(monkeypatch, tmp_path):
    (tmp_path / "v3-probe-2026-10-14.txt").write_text("probe: 2026-10-14T10:06Z\n")
    (tmp_path / "v3-probe-2026-10-14-p3.txt").write_text("# V3 reachability probe — 2026-10-14T11:41:33Z\n")
    monkeypatch.setattr(receipts, "EVIDENCE", tmp_path)
    assert "v3-probe-2026-10-14-p3.txt" in receipts.v3_probe_line()[0]


def test_sepolia_reads_section(monkeypatch, tmp_path):
    import json

    report = {"note": "deployer wallet, not a vault", "cross_check": {
        "read_at": "t", "block_number": 7, "agree": True,
        "providers": {"a": {"block_hash": "0x" + "11" * 32, "reserves": "5"}, "b": {"error": "down"}}}}
    (tmp_path / "sepolia-crosscheck-x.json").write_text(json.dumps(report))
    monkeypatch.setattr(receipts, "EVIDENCE", tmp_path)
    text = "\n".join(receipts.render_sepolia_reads())
    assert "no Ballast contract is deployed on Sepolia" in text and "#7" in text and "AGREE" in text
    assert "b: `down`" in text and "deployer wallet, not a vault" in text


def test_committed_evidence_has_no_local_paths_and_clean_pinned_leads():
    from pathlib import Path

    home = str(Path.home())
    for f in receipts.EVIDENCE.glob("*"):
        assert home not in f.read_text(), f.name
    drills = [r for r in receipts.load_runs() if r.get("kind") in ("drill", "oracle-deploy")]
    for kind, scenario in {(r["kind"], r.get("scenario")) for r in drills}:
        group = [r for r in drills if (r["kind"], r.get("scenario")) == (kind, scenario)]
        assert any(receipts.clean_pass(r) for r in group), (kind, scenario)


def test_source_pin_unknown_on_git_error_and_dirty_on_untracked(monkeypatch):
    import subprocess

    import ballast.drill as drill

    def git_fails(*a, **k):
        raise subprocess.CalledProcessError(128, a[0])

    monkeypatch.setattr(drill.subprocess, "run", git_fails)
    assert drill.source_pin() == {"git_head": None, "dirty": None}  # unknown — never "clean"

    def git_dirty(cmd, **k):
        out = "abc123\n" if cmd[1] == "rev-parse" else "?? scripts/new_tool.py\n"
        return subprocess.CompletedProcess(cmd, 0, stdout=out, stderr="")

    monkeypatch.setattr(drill.subprocess, "run", git_dirty)
    assert drill.source_pin() == {"git_head": "abc123", "dirty": True}
    assert {"foundry.lock", ".gitmodules", "lib", "tests"} <= set(drill.PINNED_PATHS)


def test_index_labels_chain_and_reserve_per_row():
    from ballast.receipts import render_index

    run = {"kind": "roles-drill", "scenario": None, "verdict": "PASS", "passed": 1, "counted_steps": 1,
           "steps": [], "_file": "roles-drill-x.json", "source": {"dirty": False},
           "chain": {"profile": "standin-upstream", "is_standin": True},
           "reserve": {"label": "local-anvil (not Sepolia)"}}
    lines = render_index([run])
    row = next(ln for ln in lines if "roles-drill-x.json" in ln)
    assert "stand-in, NOT V3" in row and "local-anvil (not Sepolia)" in row and "PASS" in row
    assert render_index([]) == []


def test_proof_md_lists_only_v3_receipts_with_console_links():
    from ballast.receipts import V3_CONSOLE, render_proof_md

    def v3_receipt(n):
        return _receipt() | {"profile": "v3", "block_number": 10 + n, "block_hash": "0x" + f"{n:02x}" * 32,
                             "extrinsic_hash": "0x" + f"{n + 16:02x}" * 32}

    v3 = _run("v3", is_standin=False) | {"_file": "roles-setup-v3.json", "kind": "roles-setup",
                                          "oracle": {"address": "0x" + "ee" * 20, "attester": "0x" + "ff" * 20}}
    v3["steps"][0]["receipt"] = v3_receipt(1)
    v3["steps"][1]["receipt"] = v3_receipt(2)
    v3["decisions"] = [{"receipt": v3_receipt(3)}, {"receipt": v3_receipt(1)}]  # duplicate hash listed once
    standin = _run() | {"_file": "a.json", "kind": "spike-assets"}
    md = render_proof_md([standin, v3])
    assert "a.json" not in md and "roles-setup-v3.json" in md
    assert md.count("| v3 |") == 3 and f"{V3_CONSOLE}0x{'01' * 32}" in md
    assert "local anvil chain, NOT Sepolia" in md and "0x" + "ee" * 20 in md
    assert "No V3 transaction yet." in render_proof_md([standin])


def test_sepolia_drill_rows_are_labelled_and_linked_to_etherscan():
    from ballast.receipts import render_proof_md, render_roles_section

    tx = "0x" + "ab" * 32
    run = _run("v3", is_standin=False) | {
        "_file": "sepolia-drill-x.json", "kind": "sepolia-drill", "source": {"dirty": False},
        "reserve": {"label": "Sepolia", "vault": "0x" + "12" * 20},
        "evm_steps": [{"name": "deposit", "block_number": 7, "tx_hash": tx, "as_expected": True, "status": 1,
                       "chain": "Sepolia"}]}
    run["chain"]["label"] = "Portaldot V3 testnet"
    run["steps"][0]["receipt"] = _receipt() | {"profile": "v3", "block_number": 11, "block_hash": "0x" + "01" * 32,
                                               "extrinsic_hash": "0x" + "02" * 32}
    run["steps"][1]["receipt"] = run["steps"][0]["receipt"]
    summarize(run)
    section = "\n".join(render_roles_section(run))
    assert f"https://sepolia.etherscan.io/tx/{tx}" in section and "reserve: **Sepolia**" in section
    md = render_proof_md([run])
    assert "Reserve chain: **Sepolia**" in md and "sepolia-drill-x.json" in md
