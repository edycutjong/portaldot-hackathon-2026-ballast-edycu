"""Receipts: evidence JSON -> docs/RECEIPTS.md, and re-fetching every row from the chain by extrinsic id."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .chain_profile import blake2_256
from .dispatch import extrinsic_outcome, multisig_inner_results

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "evidence"
RECEIPTS_MD = ROOT / "docs" / "RECEIPTS.md"


RUN_PATTERNS = ("spike-assets-*.json", "drill-*.json", "oracle-*.json", "roles-*.json")


def load_runs(patterns: tuple[str, ...] = RUN_PATTERNS) -> list[dict]:
    """Runs in evidence/ (spike runs and drills), newest first."""
    paths = sorted({p for pattern in patterns for p in EVIDENCE.glob(pattern)})
    runs = [json.loads(p.read_text()) | {"_file": p.name} for p in paths]
    return sorted(runs, key=lambda r: r["started_at"], reverse=True)


def clean_text(text: str) -> str:
    """No local absolute paths in committed evidence."""
    return text.replace(str(ROOT), "<build>").replace(str(Path.home()), "~")


def summarize(run: dict) -> dict:
    """Verdict = every counted step as expected AND every state check ok AND no error. Observations don't count."""
    if run.get("error"):
        run["error"] = clean_text(run["error"])
    steps = run["steps"] + run.get("evm_steps", [])
    counted = [s for s in steps if s.get("counted", True)]
    run["passed"] = sum(1 for s in counted if s["as_expected"])
    run["counted_steps"] = len(counted)
    run["observation_steps"] = len(steps) - len(counted)
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
        n = run["observation_steps"]
        text += f" + {n} observation{'s' if n > 1 else ''}"
    checks = run.get("state_checks", [])
    if checks:
        text += f", {sum(1 for c in checks if c['ok'])}/{len(checks)} state checks"
    return text


def failure_cause(run: dict) -> str:
    """One line: why a run is not PASS (its error, or the failed steps / checks)."""
    parts = []
    if run.get("error"):
        last = [ln.strip() for ln in clean_text(run["error"]).splitlines() if ln.strip()]
        parts.append((last[-1] if last else run["error"])[:160])
    bad = []
    for st in run["steps"] + run.get("evm_steps", []):
        if st.get("counted", True) and not st["as_expected"]:
            outcome = st.get("receipt", {}).get("outcome", {}).get("text")
            bad.append(f"{st['name']}" + (f" -> {outcome}" if outcome else ""))
    bad += [c["what"] for c in run.get("state_checks", []) if not c["ok"]]
    if bad:
        parts.append("failed: " + "; ".join(bad))
    return " — ".join(parts)[:320]


def pin_text(run: dict) -> str:
    src = run.get("source")
    if not src:
        return "source: not pinned (recorded before pinning existed)"
    head = (src.get("git_head") or "unknown")[:7]
    state = {False: "clean", True: "UNCOMMITTED CHANGES", None: "unknown"}[src.get("dirty")]
    return f"source: `{head}` ({state})"


def clean_pass(run: dict) -> bool:
    return run.get("verdict") == "PASS" and (run.get("source") or {}).get("dirty") is False


def _mark(ok: bool | None) -> str:
    return "—" if ok is None else ("✅" if ok else "❌")


def render_spike_section(run: dict) -> list[str]:
    ident = run["chain"]
    lines = [
        f"### Spike run — asset {run['asset_id']} — {run['started_at']}",
        "",
        f"Chain: **{ident['label']}** · genesis `{ident['genesis_hash']}` · spec `{ident['spec_name']}/"
        f"{ident['spec_version']}` · raw JSON: [`evidence/{run['_file']}`](../evidence/{run['_file']}) · "
        f"result: **{run['verdict']}** ({score(run)}) · {pin_text(run)}",
        "",
    ]
    return lines + _steps_body(run)


def _steps_body(run: dict) -> list[str]:
    lines: list[str] = []
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


def render_drill_section(run: dict) -> list[str]:
    ident, reserve = run["chain"], run["reserve"]
    title = {"drain": "reserve drained -> watchdog freezes", "outage": "every provider down -> fail-closed freeze",
             "heartbeat": "no bot heartbeat for K blocks -> freeze (I8)"}
    lines = [
        f"### Breaker drill ({run['scenario']}: {title.get(run['scenario'], run['scenario'])}) — asset "
        f"{run['asset_id']} — {run['started_at']}",
        "",
        f"Chain: **{ident['label']}** · reserve: **{reserve['label']}** · raw JSON: "
        f"[`evidence/{run['_file']}`](../evidence/{run['_file']}) · watchdog log: "
        f"[`evidence/{run['watchdog_log']}`](../evidence/{run['watchdog_log']}) · result: **{run['verdict']}** "
        f"({score(run)}) · {pin_text(run)}",
        "",
    ]
    src = run.get("source") or {}
    hashes = {k: v for k, v in src.items() if k.endswith("_sha256")}
    if hashes:
        lines += ["Deployed initcode sha256: " + ", ".join(f"{k.removesuffix('_initcode_sha256')} `{v}`"
                                                         for k, v in hashes.items()) + ".", ""]
    if reserve.get("watcher_read"):
        lines += [f"Watcher reserve reads: {reserve['watcher_read']}.", ""]
    if run.get("watchdog_cmd"):
        params = {k: v for k, v in zip(run["watchdog_cmd"].split()[:-1], run["watchdog_cmd"].split()[1:])
                  if k in ("--poll-blocks", "--fail-closed-after", "--max-block-age", "--timeout", "--heartbeat-k")}
        if "--max-block-age" in params:
            params["--max-block-age"] += " (stale-block check off: anvil mines only when a tx lands)"
        lines += ["Watcher parameters: " + ", ".join(f"`{k} {v}`" for k, v in params.items()) + ".", ""]
    if run.get("remark"):
        note = " (`eb`/`eh` = the local-anvil block the watcher read, not Sepolia)" if "|eb=" in run["remark"] else ""
        lines += [f"Reason remark (in the freeze extrinsic): `{run['remark']}`{note}", ""]
    if run.get("timing"):
        t = run["timing"]
        lines += [f"Timing ({t['basis']}):", ""]
        lines += [f"- `{k}`: {v}" for k, v in t.items() if k != "basis"]
        lines.append("")
    if run.get("evm_steps"):
        lines += [
            f"Reserve-chain transactions ({reserve['label']}; vault `{reserve.get('vault')}`, token "
            f"`{reserve.get('usdc')}`):",
            "",
            "| # | Step | Block | Tx hash | Expected | Observed |",
            "|---|---|---|---|---|---|",
        ]
        for i, row in enumerate(run["evm_steps"], 1):
            lines.append(f"| {i} | {row['name']} | {row['block_number']} | `{row['tx_hash']}` | {row['expected']} | "
                         f"{_mark(row['as_expected'])} status {row['status']} |")
        lines += ["", "Portaldot extrinsics:", ""]
    return lines + _steps_body(run)


def render_oracle_section(run: dict) -> list[str]:
    ident, oracle = run["chain"], run.get("oracle", {})
    lines = [
        f"### ReserveOracle on Revive — {run['started_at']}",
        "",
        f"Chain: **{ident['label']}** (Revive accepts EVM bytecode on this stand-in; V3 deploy pending) · contract "
        f"`{oracle.get('address')}` · attester `{oracle.get('attester')}` · raw JSON: "
        f"[`evidence/{run['_file']}`](../evidence/{run['_file']}) · result: **{run['verdict']}** ({score(run)}) · "
        f"{pin_text(run)}" + (f" · initcode sha256 `{run['source']['ReserveOracle_initcode_sha256']}`"
                              if (run.get("source") or {}).get("ReserveOracle_initcode_sha256") else ""),
        "",
        f"Posted values mirror drill `{run['mirrors']['drill']}` (reserve: {run['mirrors']['reserve']}); "
        f"{run['mirrors']['note']}.",
        "",
    ]
    return lines + _steps_body(run)


ROLE_TITLES = {
    "roles-setup": "Role split — asset 1 (breaker) + asset 2 (control), reserve vault, ReserveOracle",
    "roles-drill": "Role-split drill — gated mint, over-mint refused, drain -> freeze, gated thaw",
}


def render_roles_section(run: dict) -> list[str]:
    ident, reserve = run["chain"], run.get("reserve", {})
    lines = [
        f"### {ROLE_TITLES.get(run['kind'], run['kind'])} — {run['started_at']}",
        "",
        f"Chain: **{ident['label']}** · reserve: **{reserve.get('label')}** · raw JSON: "
        f"[`evidence/{run['_file']}`](../evidence/{run['_file']}) · result: **{run['verdict']}** ({score(run)}) · "
        f"{pin_text(run)}",
        "",
    ]
    roles = run.get("roles")
    if roles:
        lines += [f"Role map: `M_mint` {roles['M_mint']['address']} (2-of-2 A, B) · `M_admin` "
                  f"{roles['M_admin']['address']} (2-of-3 A, A2, B) · `M_watch` {roles['M_watch']['address']} "
                  f"(1-of-{len(roles['watchers'])} watchers).", ""]
    for key, value in (run.get("notes") or {}).items():
        lines.append(f"- {key}: {value}")
    if run.get("notes"):
        lines.append("")
    if run.get("evm_steps"):
        lines += [f"Reserve-chain transactions ({reserve.get('label')}; vault `{reserve.get('vault')}`):", "",
                  "| # | Step | Block | Tx hash | Observed |", "|---|---|---|---|---|"]
        for i, row in enumerate(run["evm_steps"], 1):
            lines.append(f"| {i} | {row['name']} | {row['block_number']} | `{row['tx_hash']}` | "
                         f"{_mark(row['as_expected'])} status {row['status']} |")
        lines += ["", "Portaldot extrinsics:", ""]
    return lines + _steps_body(run)


def v3_probe_line() -> list[str]:
    def stamp(path: Path) -> str:  # the probe's own UTC time from its first line, e.g. 2026-10-14T11:41:33Z
        found = re.search(r"\d{4}-\d\d-\d\dT\d\d:\d\d(?::\d\d)?Z", path.read_text().splitlines()[0])
        return found.group(0) if found else ""

    probes = sorted(EVIDENCE.glob("v3-probe-*.txt"), key=stamp)
    if not probes:
        return []
    latest = probes[-1]
    first = latest.read_text().splitlines()[0].lstrip("# ").strip()
    return [f"Latest V3 reachability probe: [`evidence/{latest.name}`](../evidence/{latest.name}) ({first}).", ""]


STANDIN_NOTE = [
    "Measured on a **local** stand-in chain while the Portaldot V3 testnet is unreachable. Nothing in this",
    "section is a V3 measurement. The chain is a local `--dev` node: `scripts/check_receipts.py` re-fetches",
    "these rows from that node only, there is no public explorer for it, and a fresh node + spike run",
    "produces new hashes (same steps, same outcomes). Re-running them on V3 is planned for when V3 is reachable.",
    "",
]


def render_receipts_md() -> str:
    runs = load_runs()
    out = [
        "# Receipts",
        "",
        "Every extrinsic row below is a real extrinsic, identified by extrinsic id (`block-index`); decoded events are",
        "in the linked JSON. `python scripts/check_receipts.py` re-fetches every extrinsic from the chain it ran on and",
        "every drill reserve-chain tx from the local anvil. Read-only Sepolia reads are listed first.",
        "",
    ]
    if not runs:
        out.append("_No receipts yet._")
    out += render_sepolia_reads()
    groups: dict[tuple[bool, str], list[dict]] = {}
    for run in runs:
        groups.setdefault((run["chain"]["is_standin"], run["chain"]["profile"]), []).append(run)
    # V3 sections first, stand-ins after
    for (is_standin, profile), group in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        if is_standin:
            out += [f"## Stand-in receipts — {profile} (not V3)", "", *STANDIN_NOTE, *v3_probe_line()]
        elif not group[0]["chain"].get("genesis_pinned", False):
            out += [f"## V3 receipts — {profile} (genesis not pinned: UNVERIFIED (V3 day-0))", "",
                    f"Chain label: {group[0]['chain']['label']}", ""]
        else:
            out += [f"## V3 receipts — {profile}", "", f"Chain label: {group[0]['chain']['label']}", ""]
        kinds = (("roles-drill", None), ("roles-setup", None), ("drill", "drain"), ("drill", "outage"),
                 ("drill", "heartbeat"), ("oracle-deploy", None), ("spike-assets", None))
        for kind, scenario in kinds:
            runs_k = [r for r in group if r.get("kind", "spike-assets") == kind and r.get("scenario") == scenario]
            if not runs_k:
                continue
            # the newest clean-pinned PASS leads (else the newest PASS, else the newest run); all others listed below
            lead = next((r for r in runs_k if clean_pass(r)),
                        next((r for r in runs_k if r.get("verdict") == "PASS"), runs_k[0]))
            runs_k = [lead] + [r for r in runs_k if r is not lead]
            for i, run in enumerate(runs_k):
                if i == 0:
                    render = {"drill": render_drill_section, "oracle-deploy": render_oracle_section,
                              "roles-setup": render_roles_section, "roles-drill": render_roles_section}
                    out += render.get(kind, render_spike_section)(run)
                else:
                    if i == 1:
                        out += ["Other runs, newest first, any verdict (full tables in the JSON):", ""]
                    cause = failure_cause(run) if run.get("verdict") != "PASS" else ""
                    what = (f"contract `{(run.get('oracle') or {}).get('address')}`" if kind == "oracle-deploy"
                            else f"asset {run['asset_id']}")
                    out.append(
                        f"- {what} — {run['started_at']} — {run['verdict']} ({score(run)}) — "
                        f"{pin_text(run)} — [`evidence/{run['_file']}`](../evidence/{run['_file']})"
                        + (f" — {cause}" if cause else "")
                    )
            out.append("")
    return "\n".join(out).rstrip() + "\n"


def render_sepolia_reads() -> list[str]:
    files = sorted(EVIDENCE.glob("sepolia-crosscheck-*.json"))
    if not files:
        return []
    out = ["## Sepolia reads (read-only — no Ballast contract is deployed on Sepolia yet)", ""]
    for f in files:
        rep = json.loads(f.read_text())
        cc = rep.get("cross_check", {})
        rows = ", ".join(f"{name}: `{p.get('block_hash', p.get('error'))}` reserves {p.get('reserves', '-')}"
                         for name, p in cc.get("providers", {}).items())
        out += [
            f"- [`evidence/{f.name}`](../evidence/{f.name}) — read at {cc.get('read_at')}: finalized block "
            f"#{cc.get('block_number')} via {len(cc.get('providers', {}))} providers — "
            f"{'AGREE' if cc.get('agree') else 'DISAGREE'} ({rows}). Note: {rep.get('note', 'holder ' + str(rep.get('holder')))}",
        ]
    return out + [""]


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
