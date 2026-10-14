import json

import pytest
from conftest import EVIDENCE, fixture_sha256, pinned_sums

from ballast.dispatch import (
    decode_dispatch_error,
    decode_dispatch_result,
    extrinsic_outcome,
    module_error_name,
    multisig_inner_results,
)


def test_metadata_fixtures_match_their_pinned_sha256():
    sums = pinned_sums()
    assert set(sums) == {"standin-upstream-metadata.scale", "standin-1002-metadata.scale"}
    for name, digest in sums.items():
        assert fixture_sha256(name) == digest


def test_modern_module_error_is_read_from_metadata(upstream_md):
    _, md = upstream_md
    # ModuleError.error is [u8; 4] on modern runtimes; the first byte is the variant index
    assert str(decode_dispatch_error({"Module": {"index": 39, "error": "0x02000000"}}, md)) == "Err(Assets.NoPermission)"
    assert module_error_name(md, 39, 0) == ("Assets", "BalanceLow")


def test_error_names_round_trip_through_the_assets_pallet(upstream_md):
    _, md = upstream_md
    assets = next(p for p in md.pallets if p.value["name"] == "Assets")
    by_name = {e.value["name"]: e.value["index"] for e in assets.errors}
    for name in ("NoPermission", "AssetNotLive", "Frozen", "BalanceLow"):
        err = {"Module": {"index": assets.value["index"], "error": f"0x{by_name[name]:02x}000000"}}
        assert str(decode_dispatch_error(err, md)) == f"Err(Assets.{name})"


def test_legacy_1002_module_error(md_1002):
    _, md = md_1002
    # spec 1002: Assets is pallet 26 and errors are plain u8 (FINDINGS: 26/2 = NoPermission)
    assert str(decode_dispatch_error({"Module": {"index": 26, "error": 2}}, md)) == "Err(Assets.NoPermission)"
    assert str(decode_dispatch_error({"Module": (26, 2)}, md)) == "Err(Assets.NoPermission)"


def test_non_module_errors_and_ok_forms(upstream_md):
    _, md = upstream_md
    assert decode_dispatch_result({"Ok": []}, md).ok
    assert decode_dispatch_result("Ok", md).ok
    assert str(decode_dispatch_error("BadOrigin", md)) == "Err(BadOrigin)"
    assert str(decode_dispatch_error({"Token": "FundsUnavailable"}, md)) == "Err(Token.FundsUnavailable)"
    with pytest.raises(ValueError):
        decode_dispatch_result(42, md)


def test_multisig_inner_result_err_is_not_hidden_by_an_ok_extrinsic(upstream_md):
    _, md = upstream_md
    events = [
        {"module_id": "Multisig", "event_id": "MultisigExecuted",
         "attributes": {"approving": "x", "timepoint": {}, "multisig": "m", "call_hash": "0x",
                        "result": {"Err": {"Module": {"index": 39, "error": "0x02000000"}}}}},
        {"module_id": "System", "event_id": "ExtrinsicSuccess", "attributes": {"dispatch_info": {}}},
    ]
    assert extrinsic_outcome(events, md).ok
    assert [str(o) for o in multisig_inner_results(events, md)] == ["Err(Assets.NoPermission)"]


def test_legacy_positional_event_attributes(md_1002):
    _, md = md_1002
    events = [
        {"module_id": "Multisig", "event_id": "MultisigExecuted", "attributes": [
            {"type": "AccountId", "value": "a"}, {"type": "Timepoint", "value": {}}, {"type": "AccountId", "value": "m"},
            {"type": "CallHash", "value": "0x"}, {"type": "DispatchResult", "value": {"Err": {"Module": {"index": 26, "error": 2}}}},
        ]},
        {"module_id": "System", "event_id": "ExtrinsicFailed", "attributes": [
            {"type": "DispatchError", "value": {"Module": {"index": 26, "error": 2}}}, {"type": "DispatchInfo", "value": {}},
        ]},
    ]
    assert str(multisig_inner_results(events, md)[0]) == "Err(Assets.NoPermission)"
    assert str(extrinsic_outcome(events, md)) == "Err(Assets.NoPermission)"


def test_extrinsic_outcome_needs_a_system_event(upstream_md):
    _, md = upstream_md
    with pytest.raises(ValueError):
        extrinsic_outcome([{"module_id": "Assets", "event_id": "Issued", "attributes": {}}], md)


def test_recorded_spike_receipts_decode_identically_offline(upstream_md):
    """Every committed standin-upstream receipt re-decodes to its recorded outcome from the metadata fixture."""
    _, md = upstream_md
    runs = [json.loads(p.read_text()) for p in sorted(EVIDENCE.glob("spike-assets-standin-upstream-*.json"))]
    assert runs, "no committed standin-upstream spike evidence"
    seen = set()
    for run in runs:
        for step in run["steps"]:
            r = step["receipt"]
            assert extrinsic_outcome(r["events"], md).as_dict() == r["outcome"]
            assert [o.as_dict() for o in multisig_inner_results(r["events"], md)] == r["inner"]
            seen.add(r["outcome"]["text"])
    assert {"Ok", "Err(Assets.NoPermission)", "Err(Assets.AssetNotLive)"} <= seen
