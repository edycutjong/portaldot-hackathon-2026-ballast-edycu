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
PROOF_MD = ROOT / "docs" / "PROOF.md"
FINALITY = EVIDENCE / "v3-finality.json"  # written by scripts/check_receipts.py --profile v3
V3_CONSOLE = "https://node-console.portaldot.dev/?rpc=wss%3A%2F%2Ftest-node-v3.portaldot.dev#/explorer/query/"


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
    "roles-attest": "Attestations — BALLAST/1 remarks by B, ReserveOracle mirror, `ballast verify` + negative control",
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
    if run.get("verify"):
        vs = run["verify"]["summary"]
        lines += [f"`ballast verify` blocks #{run['verify']['from']}..#{run['verify']['to']} "
                  f"([`evidence/{run['verify']['file']}`](../evidence/{run['verify']['file']})): **{vs['verdict']}** — "
                  f"{vs['attestations_pass']}/{vs['attestations_counted']} B attestations PASS on both chains, "
                  f"{vs['rejected']} REJECTED (not counted), {vs['failures_or_flags']} FAIL/FLAGGED.", ""]
    if run.get("heartbeat"):
        hb = run["heartbeat"]
        lines += [f"Heartbeat H = {hb['H_used']} blocks ({hb['basis']}; production H = "
                  f"{hb['production_H_on_this_profile']}, K = {hb['production_K_on_this_profile']} on this profile).", ""]
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
    lines = [f"Earlier V3 reachability probe (the old DNS names): [`evidence/{latest.name}`](../evidence/{latest.name}) ({first})."]
    day0 = sorted(EVIDENCE.glob("v3-day0-*.json"))
    if day0:
        lines.append(f"Current V3 identity (read-only day-0 check): [`evidence/{day0[-1].name}`](../evidence/{day0[-1].name}).")
    return lines + [""]


STANDIN_NOTE = [
    "Measured on a **local** stand-in chain (before the Portaldot V3 testnet was reachable). Nothing in this",
    "section is a V3 measurement. The chain is a local `--dev` node: `scripts/check_receipts.py` re-fetches",
    "these rows from that node only, there is no public explorer for it, and a fresh node + spike run",
    "produces new hashes (same steps, same outcomes). V3 runs, once funded, are listed in `docs/PROOF.md`.",
    "",
]


def render_receipts_md() -> str:
    runs = load_runs()
    out = [
        "# Receipts",
        "",
        "Every extrinsic row below is a real extrinsic, identified by extrinsic id (`block-index`); decoded events are",
        "in the linked JSON. `python scripts/check_receipts.py` re-fetches every extrinsic from the chain it ran on and",
        "every drill reserve-chain tx from the local anvil. An index comes first, then the read-only Sepolia section.",
        "",
    ]
    if not runs:
        out.append("_No receipts yet._")
    out += render_index(runs)
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
        kinds = (("roles-drill", None), ("roles-attest", None), ("roles-setup", None), ("drill", "drain"), ("drill", "outage"),
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
                              "roles-setup": render_roles_section, "roles-drill": render_roles_section,
                              "roles-attest": render_roles_section}
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


INDEX_ROWS = (
    ("roles-drill", None, "Breaker drill on the role-split asset 1 (gated mint, over-mint refused, freeze, gated thaw, team gate)"),
    ("roles-attest", None, "Attestations + ReserveOracle mirror + `ballast verify` (negative control REJECTED)"),
    ("roles-setup", None, "Role split: asset 1 owner/issuer M_mint, admin M_admin, freezer M_watch; asset 2 keyless"),
    ("drill", "drain", "Breaker drill, scratch asset: drain -> freeze"),
    ("drill", "outage", "Breaker drill, scratch asset: every provider down -> fail-closed freeze (I6)"),
    ("drill", "heartbeat", "Breaker drill, scratch asset: bot silent for K blocks -> freeze (I8)"),
    ("oracle-deploy", None, "ReserveOracle on Revive, mirroring a drill"),
    ("spike-assets", None, "Assets spike: watcher-set freeze, freezer thaw refused"),
)


def render_index(runs: list[dict]) -> list[str]:
    """One row per run kind: where it ran (chain + reserve, both labelled) and its newest clean PASS."""
    rows = []
    for kind, scenario, what in INDEX_ROWS:
        group = [r for r in runs if r.get("kind", "spike-assets") == kind and r.get("scenario") == scenario]
        v3 = [r for r in group if r["chain"]["profile"] == "v3"]
        for part in (v3, [r for r in group if r["chain"]["profile"] != "v3"]):  # V3 gets its own row
            if not part:
                continue
            lead = next((r for r in part if clean_pass(r)), None) or next(
                (r for r in part if r.get("verdict") == "PASS"), part[0])
            chain = lead["chain"]["profile"] + (" (stand-in, NOT V3)" if lead["chain"]["is_standin"] else "")
            reserve = (lead.get("reserve") or {}).get("label") or "—"
            dirty = " · ran from uncommitted changes" if (lead.get("source") or {}).get("dirty") else ""
            rows.append(f"| {what} | {chain} | {reserve} | {lead['verdict']} ({score(lead)}){dirty} | "
                        f"[`{lead['_file']}`](../evidence/{lead['_file']}) |")
    if not rows:
        return []
    return ["## At a glance", "",
            "Four places, each labelled on every row: the **Portaldot V3 testnet** (profile v3, real tPOT — every V3",
            "extrinsic is also listed in [`PROOF.md`](PROOF.md)), the Portaldot **stand-in** chain (not V3), the",
            "**local-anvil** reserve chain (not Sepolia), and **Sepolia** (read-only so far — see its section).", "",
            "| Run | Portaldot chain | Reserve chain | Newest result (clean source preferred) | Evidence |",
            "|---|---|---|---|---|",
            *rows, ""]


def render_sepolia_reads() -> list[str]:
    files = sorted(EVIDENCE.glob("sepolia-crosscheck-*.json"))
    if not files:
        return []
    out = ["## Sepolia (read-only — no Ballast contract is deployed on Sepolia yet)", "",
           "The Sepolia `ReserveVault` deploy, its 100.00 USDC deposit and the real-Sepolia drill wait until the "
           "deployer wallet holds >= 100.00 Circle test USDC; the reads below show what it holds. Every drill above "
           "uses the local-anvil reserve instead, labelled as such.", ""]
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


def v3_receipts(run: dict) -> list[tuple[str, dict]]:
    """Every (step name, receipt) on profile v3 anywhere in a run (setup steps, CLI subprocess receipts, bot executions)."""
    found: list[tuple[str, dict]] = []

    def walk(node: Any, name: str) -> None:
        if isinstance(node, dict):
            if node.get("profile") == "v3" and node.get("extrinsic_hash") and node.get("block_hash"):
                found.append((name, node))
                return
            for k, v in node.items():
                walk(v, node.get("name", name) if k == "receipt" else name)
        elif isinstance(node, list):
            for v in node:
                walk(v, name)

    for step in run.get("steps", []):
        walk(step, step.get("name", ""))
    for key, value in run.items():
        if key != "steps":
            walk(value, key)
    seen, out = set(), []
    for name, r in found:
        if r["extrinsic_hash"] not in seen:
            seen.add(r["extrinsic_hash"])
            out.append((name, r))
    return out


def render_proof_md(runs: list[dict] | None = None) -> str:
    runs = [r for r in (runs if runs is not None else load_runs()) if r.get("chain", {}).get("profile") == "v3"]
    lines = ["# PROOF — real Portaldot V3 testnet transactions", "",
             "Generated by `ballast.receipts` from `evidence/` (never hand-edited). Only runs whose chain identified as "
             "profile **v3** (genesis `0xd4f9acbcf7f52388d8b095abe3c198d19fc510e0343e643e87cfbccb155283bd`, "
             "spec portaldot-v3/3002, tPOT) are listed; stand-in rows live in `RECEIPTS.md` and are not V3.",
             "Reserve rows in these runs are on a **local anvil chain, NOT Sepolia**.",
             "Each block link opens https://node-console.portaldot.dev/ on the V3 endpoint; "
             "`python scripts/check_receipts.py --profile v3` re-queries every row on chain.", ""]
    if not runs:
        lines += ["No V3 transaction yet.", ""]
        return "\n".join(lines)
    fin = json.loads(FINALITY.read_text()) if FINALITY.exists() else {"receipts": {}}
    if fin.get("finalized_head"):
        lines += [f"Finality: `check_receipts.py --profile v3` at {fin['checked_at']} found every row marked final at or below "
                  f"the finalized head #{fin['finalized_head']}. A row whose inclusion block lost a fork links the canonical block "
                  "holding the same extrinsic.", ""]
    for run in sorted(runs, key=lambda r: r["started_at"]):
        summarize(run)
        lines += [f"## {run['kind']} — {run['_file']} — {run['verdict']} ({score(run)})", "",
                  f"Started {run['started_at']} · {pin_text(run)}", ""]
        oracle = run.get("oracle") or {}
        if oracle.get("address"):
            lines += [f"ReserveOracle on V3 Revive: `{oracle['address']}` (attester `{oracle.get('attester')}`)", ""]
        lines += ["| step | call | outcome | block | extrinsic | extrinsic hash | final | profile |",
                  "|---|---|---|---|---|---|---|---|"]
        for name, r in v3_receipts(run):
            out = (r.get("outcome") or {}).get("text", "")
            inner = ", ".join(i.get("text", "") for i in r.get("inner") or [])
            f = fin["receipts"].get(r["extrinsic_hash"]) or {}
            bh, xid = f.get("block_hash", r["block_hash"]), r.get("extrinsic_id", "")
            if f.get("reorged_from"):
                xid = f"{f['block_number']}-{f['extrinsic_index']} (inclusion block `{f['reorged_from'][:12]}…` lost a fork)"
            final = f"yes (≤ #{f['finalized_head']})" if f.get("ok") else ("NO" if f else "unchecked")
            lines.append(f"| {clean_text(name)} | {r.get('call', '')} | {out}{f' (inner {inner})' if inner else ''} | "
                         f"[#{r['block_number']}]({V3_CONSOLE}{bh}) `{bh}` | {xid} | `{r['extrinsic_hash']}` | {final} | v3 |")
        lines.append("")
    return "\n".join(lines)


def write_receipts_md() -> Path:
    RECEIPTS_MD.parent.mkdir(parents=True, exist_ok=True)
    RECEIPTS_MD.write_text(render_receipts_md())
    PROOF_MD.write_text(render_proof_md())
    return RECEIPTS_MD


def refetch(substrate: Any, receipt: dict, placed: dict | None = None) -> list[str]:
    """Re-read one receipt from the chain by extrinsic id; returns a list of mismatches (empty = confirmed).

    A receipt is recorded at inclusion. If that block lost a fork, the same extrinsic is looked up in the canonical
    block at the same height; found there, it is checked against that block instead and `placed` (if given) gets
    {"block_number", "block_hash", "extrinsic_index", "reorged_from"} — the canonical location."""
    problems = []
    number, index = receipt["block_number"], receipt["extrinsic_index"]
    block_hash = substrate.get_block_hash(number)
    block = substrate.rpc_request("chain_getBlock", [block_hash])["result"]["block"]
    extrinsics = block["extrinsics"]
    hashes = [blake2_256(bytes.fromhex(x[2:])) for x in extrinsics]
    reorged_from = None
    if block_hash != receipt["block_hash"]:
        if receipt["extrinsic_hash"] not in hashes:
            return [f"block #{number} hash {block_hash} != {receipt['block_hash']} and the extrinsic is not in it"]
        reorged_from, index = receipt["block_hash"], hashes.index(receipt["extrinsic_hash"])
    if index >= len(extrinsics):
        return problems + [f"block #{number} has no extrinsic {index}"]
    if hashes[index] != receipt["extrinsic_hash"]:
        problems.append(f"{receipt['extrinsic_id']}: tx hash {hashes[index]} != {receipt['extrinsic_hash']}")
    if placed is not None:
        placed.update({"block_number": number, "block_hash": block_hash, "extrinsic_index": index,
                       "reorged_from": reorged_from})
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
