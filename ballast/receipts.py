"""Receipts: evidence JSON -> docs/RECEIPTS.md, and re-fetching every row from the chain by extrinsic id."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .chain_profile import blake2_256
from .dispatch import extrinsic_outcome, multisig_inner_results

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "evidence"
RECEIPTS_MD = ROOT / "docs" / "RECEIPTS.md"


def load_runs(pattern: str = "spike-assets-*.json") -> list[dict]:
    runs = [json.loads(p.read_text()) | {"_file": p.name} for p in sorted(EVIDENCE.glob(pattern))]
    return sorted(runs, key=lambda r: r["started_at"], reverse=True)


def _short(h: str, n: int = 10) -> str:
    return f"{h[:n]}…{h[-6:]}"


def render_spike_section(run: dict) -> list[str]:
    ident = run["chain"]
    lines = [
        f"### Spike run — asset {run['asset_id']} — {run['started_at']}",
        "",
        f"Chain: **{ident['label']}** · genesis `{ident['genesis_hash']}` · spec `{ident['spec_name']}/"
        f"{ident['spec_version']}` · raw JSON: [`evidence/{run['_file']}`](../evidence/{run['_file']}) · "
        f"result: **{run['verdict']}** ({run['passed']}/{len(run['steps'])} steps as expected)",
        "",
        "| # | Step | Call (signer) | Extrinsic id | Block hash | Tx hash | Expected | Observed |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for i, step in enumerate(run["steps"], 1):
        r = step["receipt"]
        observed = r["outcome"]["text"]
        if r["inner"]:
            observed += " · inner " + ", ".join(o["text"] for o in r["inner"])
        if step.get("events_seen"):
            observed += " · " + ", ".join(step["events_seen"])
        lines.append(
            f"| {i} | {step['name']} | `{r['call']}` ({step['signer_role']}) | `{r['extrinsic_id']}` | "
            f"`{_short(r['block_hash'])}` | `{_short(r['extrinsic_hash'])}` | {step['expected']} | "
            f"{'✅' if step['as_expected'] else '❌'} {observed} |"
        )
    lines += ["", "State checks (storage reads at the step's block):", ""]
    for check in run.get("state_checks", []):
        lines.append(f"- {check['what']}: `{check['observed']}` at block `{_short(check['block_hash'])}`")
    lines.append("")
    return lines


def render_receipts_md() -> str:
    runs = load_runs()
    profiles = sorted({r["chain"]["profile"] for r in runs})
    out = [
        "# Receipts",
        "",
        "Every row below is a real extrinsic: re-fetch it by extrinsic id (`block-index`) with",
        "`python scripts/check_receipts.py`. Full hashes and decoded events are in the linked JSON.",
        "",
    ]
    if not runs:
        out.append("_No receipts yet._")
    for profile in profiles:
        out += [
            f"## Stand-in receipts — {profile} (not V3)",
            "",
            "Measured on a local stand-in chain while the Portaldot V3 testnet is unreachable. Nothing in this",
            "section is a V3 measurement; it is re-run on V3 once V3 is reachable.",
            "",
        ]
        for i, run in enumerate(r for r in runs if r["chain"]["profile"] == profile):
            if i == 0:
                out += render_spike_section(run)
            else:
                if i == 1:
                    out += ["Earlier runs (full tables in the JSON):", ""]
                out.append(
                    f"- asset {run['asset_id']} — {run['started_at']} — {run['verdict']} "
                    f"({run['passed']}/{len(run['steps'])}) — [`evidence/{run['_file']}`](../evidence/{run['_file']})"
                )
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def write_receipts_md() -> Path:
    RECEIPTS_MD.parent.mkdir(parents=True, exist_ok=True)
    RECEIPTS_MD.write_text(render_receipts_md())
    return RECEIPTS_MD


def refetch(substrate: Any, receipt: dict) -> list[str]:
    """Re-read one receipt from the chain by extrinsic id; returns a list of mismatches (empty = confirmed)."""
    problems = []
    number, index = receipt["block_number"], receipt["extrinsic_index"]
    block_hash = substrate.get_block_hash(number)
    if block_hash != receipt["block_hash"]:
        problems.append(f"block #{number} hash {block_hash} != {receipt['block_hash']}")
        return problems
    block = substrate.rpc_request("chain_getBlock", [block_hash])["result"]["block"]
    extrinsics = block["extrinsics"]
    if index >= len(extrinsics):
        return problems + [f"block #{number} has no extrinsic {index}"]
    raw = bytes.fromhex(extrinsics[index][2:])
    if blake2_256(raw) != receipt["extrinsic_hash"]:
        problems.append(f"{receipt['extrinsic_id']}: tx hash {blake2_256(raw)} != {receipt['extrinsic_hash']}")
    events = [
        {k: e.value[k] for k in ("module_id", "event_id", "attributes")}
        for e in substrate.get_events(block_hash)
        if e.value.get("extrinsic_idx") == index
    ]
    events = json.loads(json.dumps(events, default=str))
    outcome = extrinsic_outcome(events, substrate.metadata).as_dict()
    if outcome != receipt["outcome"]:
        problems.append(f"{receipt['extrinsic_id']}: outcome {outcome['text']} != {receipt['outcome']['text']}")
    inner = [o.as_dict() for o in multisig_inner_results(events, substrate.metadata)]
    if inner != receipt["inner"]:
        problems.append(f"{receipt['extrinsic_id']}: inner results differ")
    names = [f"{e['module_id']}.{e['event_id']}" for e in events]
    recorded = [f"{e['module_id']}.{e['event_id']}" for e in receipt["events"]]
    if names != recorded:
        problems.append(f"{receipt['extrinsic_id']}: events {names} != recorded {recorded}")
    return problems
