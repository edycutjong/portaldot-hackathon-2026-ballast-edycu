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
    """Runs in evidence/, newest first."""
    runs = [json.loads(p.read_text()) | {"_file": p.name} for p in sorted(EVIDENCE.glob(pattern))]
    return sorted(runs, key=lambda r: r["started_at"], reverse=True)


def summarize(run: dict) -> dict:
    """Verdict = every counted step as expected AND every state check ok AND no error. Observations don't count."""
    counted = [s for s in run["steps"] if s.get("counted", True)]
    run["passed"] = sum(1 for s in counted if s["as_expected"])
    run["counted_steps"] = len(counted)
    run["observation_steps"] = len(run["steps"]) - len(counted)
    checks_ok = all(c["ok"] for c in run.get("state_checks", []))
    if run.get("error"):
        run["verdict"] = "ERROR"
    elif counted and run["passed"] == len(counted) and checks_ok:
        run["verdict"] = "PASS"
    else:
        run["verdict"] = "FAIL"
    return run


def score(run: dict) -> str:
    text = f"{run['passed']}/{run['counted_steps']} steps as expected"
    if run.get("observation_steps"):
        text += f" + {run['observation_steps']} observation"
    checks = run.get("state_checks", [])
    if checks:
        text += f", {sum(1 for c in checks if c['ok'])}/{len(checks)} state checks"
    return text


def _mark(ok: bool | None) -> str:
    return "—" if ok is None else ("✅" if ok else "❌")


def render_spike_section(run: dict) -> list[str]:
    ident = run["chain"]
    lines = [
        f"### Spike run — asset {run['asset_id']} — {run['started_at']}",
        "",
        f"Chain: **{ident['label']}** · genesis `{ident['genesis_hash']}` · spec `{ident['spec_name']}/"
        f"{ident['spec_version']}` · raw JSON: [`evidence/{run['_file']}`](../evidence/{run['_file']}) · "
        f"result: **{run['verdict']}** ({score(run)})",
        "",
    ]
    if run.get("error"):
        lines += [f"Run stopped with an error: `{run['error']}`", ""]
    lines += [
        "| # | Step | Call (signer) | Extrinsic id | Expected | Observed |",
        "|---|---|---|---|---|---|",
    ]
    for i, step in enumerate(run["steps"], 1):
        r = step["receipt"]
        observed = r["outcome"]["text"]
        if r["inner"]:
            observed += " · inner " + ", ".join(o["text"] for o in r["inner"])
        if step.get("events_seen"):
            observed += " · " + ", ".join(step["events_seen"])
        mark = _mark(step["as_expected"] if step.get("counted", True) else None)
        lines.append(
            f"| {i} | {step['name']} | `{r['call']}` ({step['signer_role']}) | `{r['extrinsic_id']}` | "
            f"{step['expected']} | {mark} {observed} |"
        )
    lines += ["", "Block and transaction hashes (full):", "", "```"]
    for i, step in enumerate(run["steps"], 1):
        r = step["receipt"]
        lines.append(f"{i:>2} {r['extrinsic_id']:>9} block {r['block_hash']}  tx {r['extrinsic_hash']}")
    lines += ["```", "", "State checks (storage/events read at the step's block):", ""]
    for check in run.get("state_checks", []):
        lines.append(
            f"- {_mark(check['ok'])} {check['what']}: expected `{check['expected']}`, observed `{check['observed']}` "
            f"at block `{check['block_hash']}`"
        )
    lines.append("")
    return lines


STANDIN_NOTE = [
    "Measured on a **local** stand-in chain while the Portaldot V3 testnet is unreachable. Nothing in this",
    "section is a V3 measurement. The chain is a local `--dev` node: `scripts/check_receipts.py` re-fetches",
    "these rows from that node only, there is no public explorer for it, and a fresh node + spike run",
    "produces new hashes (same steps, same outcomes). These rows are re-run on V3 once V3 is reachable.",
    "",
]


def render_receipts_md() -> str:
    runs = load_runs()
    out = [
        "# Receipts",
        "",
        "Every row below is a real extrinsic, identified by extrinsic id (`block-index`). Decoded events are",
        "in the linked JSON; `python scripts/check_receipts.py` re-fetches every row from the chain it ran on.",
        "",
    ]
    if not runs:
        out.append("_No receipts yet._")
    groups: dict[tuple[bool, str], list[dict]] = {}
    for run in runs:
        groups.setdefault((run["chain"]["is_standin"], run["chain"]["profile"]), []).append(run)
    # V3 sections first, stand-ins after
    for (is_standin, profile), group in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        if is_standin:
            out += [f"## Stand-in receipts — {profile} (not V3)", "", *STANDIN_NOTE]
        elif not group[0]["chain"].get("genesis_pinned", False):
            out += [f"## V3 receipts — {profile} (genesis not pinned: UNVERIFIED (V3 day-0))", "",
                    f"Chain label: {group[0]['chain']['label']}", ""]
        else:
            out += [f"## V3 receipts — {profile}", "", f"Chain label: {group[0]['chain']['label']}", ""]
        # the newest PASS run leads; every other run (any verdict) is listed below it
        lead = next((r for r in group if r.get("verdict") == "PASS"), group[0])
        group = [lead] + [r for r in group if r is not lead]
        for i, run in enumerate(group):
            if i == 0:
                out += render_spike_section(run)
            else:
                if i == 1:
                    out += ["Earlier runs (full tables in the JSON):", ""]
                out.append(
                    f"- asset {run['asset_id']} — {run['started_at']} — {run['verdict']} ({score(run)}) — "
                    f"[`evidence/{run['_file']}`](../evidence/{run['_file']})"
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
