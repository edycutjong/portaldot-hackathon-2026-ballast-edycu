#!/usr/bin/env python3
"""Turn the freeze-drill evidence into docs/BENCHMARKS.md + evidence/bench-summary-<stamp>.json.

  python scripts/bench_report.py [--out docs/BENCHMARKS.md]

Reads only files already in evidence/ (never the chain): `roles-bench-v3-*.json` (scripts/bench_drill.py) and
`sepolia-drill-*.json` (scripts/sepolia_drill.py). A sample is one drain -> freeze: it counts when its own freeze
extrinsic was as expected (signed through M_watch, outer and inner Ok, Assets.AssetFrozen, a `reason=deficit` remark);
the verdict of the run it sits in is printed next to it, never hidden. Percentiles are nearest-rank
(p50 = the ceil(0.50 n)-th, p95 = the ceil(0.95 n)-th smallest value), so every printed percentile is an actual sample.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "evidence"
DECIMALS = 14  # tPOT on V3
GROUPS = (
    ("v3-anvil", "V3 + local-anvil reserve, watcher on this machine (W1/W2 alternating)"),
    ("v3-sepolia-local", "V3 + real Sepolia reserve, watchers W1/W2 as processes on this machine"),
    ("v3-sepolia-actions", "V3 + real Sepolia reserve, watcher W2 on GitHub Actions (W1 off)"),
)


def rank(values: list[float], q: float) -> float:
    ordered = sorted(values)
    return ordered[max(1, math.ceil(q * len(ordered))) - 1]


def stats(values: list[float]) -> dict:
    if not values:
        return {"n": 0}
    return {"n": len(values), "min": min(values), "p50": rank(values, 0.50), "p95": rank(values, 0.95),
            "max": max(values), "mean": round(statistics.mean(values), 3)}


def fee_paid(receipt: dict) -> int:
    for e in receipt["events"]:
        if e["module_id"] == "TransactionPayment" and e["event_id"] == "TransactionFeePaid":
            return int(e["attributes"]["actual_fee"])
    raise ValueError(f"no TransactionFeePaid in {receipt['extrinsic_id']}")


def sepolia_samples(path: Path, run: dict) -> list[dict]:
    steps = [s for s in run["steps"] if "freezes" in s["name"]]
    note = next((v for k, v in (run.get("notes") or {}).items() if k.startswith("drain -> freeze included")), None)
    if not steps or note is None:
        return []
    step = steps[0]
    receipt = step["receipt"]
    actions = (run.get("watchers_note") or "").startswith("W1 is OFF")
    return [{
        "group": "v3-sepolia-actions" if actions else "v3-sepolia-local",
        "run": path.name, "run_verdict": run["verdict"], "i": 1,
        "watcher": "W2 (Actions)" if actions else ("W2" if "watcher W2" in step["name"] else "W1"),
        "freeze_ok": bool(step["as_expected"]), "freeze_extrinsic": receipt["extrinsic_id"],
        "drain_to_freeze_s": float(str(note).split()[0]), "fee_planck": fee_paid(receipt),
        "v3_blocks_to_freeze": None,
    }]


def bench_samples(path: Path, run: dict) -> list[dict]:
    return [{
        "group": "v3-anvil", "run": path.name, "run_verdict": run["verdict"], "i": it["i"], "watcher": it["watcher"],
        "freeze_ok": bool(it.get("freeze_ok")), "freeze_extrinsic": it["freeze_extrinsic"],
        "drain_to_freeze_s": it["drain_to_freeze_s"], "drain_to_detect_s": it.get("drain_to_detect_s"),
        "fee_planck": it["freeze_fee_planck"], "v3_blocks_to_freeze": it["freeze_blocks_after_drain_head"],
    } for it in run["bench"]["iterations"] if "freeze_extrinsic" in it]


def tpot(planck: float) -> str:
    return f"{planck / 10 ** DECIMALS:.4f}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=str(ROOT / "docs" / "BENCHMARKS.md"))
    args = ap.parse_args()
    samples: list[dict] = []
    runs: list[dict] = []
    for path in sorted(EVIDENCE.glob("roles-bench-v3-*.json")) + sorted(EVIDENCE.glob("sepolia-drill-2026*.json")):
        if path.name.endswith(".jsonl") or "reread" in path.name:
            continue
        run = json.loads(path.read_text())
        got = bench_samples(path, run) if run.get("kind") == "roles-bench" else sepolia_samples(path, run)
        samples += got
        runs.append({"file": path.name, "kind": run["kind"], "verdict": run["verdict"], "started_at": run["started_at"],
                     "samples": len(got), "samples_ok": sum(1 for s in got if s["freeze_ok"]),
                     "source": (run.get("source") or {}).get("git_head", "")[:7]})
    good = [s for s in samples if s["freeze_ok"]]
    summary: dict = {"generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                     "method": "nearest-rank percentiles over samples whose own freeze step was as expected",
                     "runs": runs, "groups": {}, "samples": samples}
    for key, _ in GROUPS:
        g = [s for s in good if s["group"] == key]
        summary["groups"][key] = {
            "drain_to_freeze_s": stats([s["drain_to_freeze_s"] for s in g]),
            "drain_to_detect_s": stats([s["drain_to_detect_s"] for s in g if s.get("drain_to_detect_s") is not None]),
            "freeze_fee_planck": stats([s["fee_planck"] for s in g]),
            "v3_blocks_to_freeze": stats([s["v3_blocks_to_freeze"] for s in g if s["v3_blocks_to_freeze"] is not None]),
        }
    summary["total_freeze_samples"] = len(good)
    summary["excluded_samples"] = len(samples) - len(good)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    sp = EVIDENCE / f"bench-summary-{stamp}.json"
    sp.write_text(json.dumps(summary, indent=2) + "\n")

    md = ["# Benchmarks — drain → freeze latency, fee, and what the number means", "",
          f"Generated by `scripts/bench_report.py` from `evidence/` ({summary['generated_at']}); the numbers below are in "
          f"[`evidence/{sp.name}`](../evidence/{sp.name}) and every sample links to the run JSON it comes from. "
          "Reproduce: `python scripts/bench_drill.py --n 24` (V3 + local anvil), `python scripts/sepolia_drill.py [--w2-actions]` "
          "(V3 + real Sepolia), then `python scripts/bench_report.py`.", "",
          f"**{len(good)} freeze drills** are counted ({len(samples) - len(good)} excluded, listed under Runs). "
          "A sample is one `ReserveVault.release` (the drain) followed by the freeze of asset 4401 on the real Portaldot V3 testnet "
          "through `M_watch`; the clock runs from the drain transaction's confirmation to the freeze extrinsic's inclusion "
          "(wall clock). Percentiles are nearest-rank: every printed p50/p95 is an actual sample.", "",
          "## Latency, drain → freeze included (seconds)", "",
          "| Setup | n | min | p50 | p95 | max | mean |", "|---|---|---|---|---|---|---|"]
    for key, label in GROUPS:
        s = summary["groups"][key]["drain_to_freeze_s"]
        md.append(f"| {label} | {s['n']} | " + " | ".join(f"{s[k]:.2f}" for k in ("min", "p50", "p95", "max", "mean")) + " |"
                  if s["n"] else f"| {label} | 0 | – | – | – | – | – |")
    md += ["", "Of that, the watcher's own detection (drain → the check that decided to freeze), V3 blocks, and fee:", "",
           "| Setup | detect p50 / p95 (s) | blocks drain-head → freeze p50 / p95 | freeze fee p50 / p95 (tPOT) |", "|---|---|---|---|"]
    for key, label in GROUPS:
        g = summary["groups"][key]
        d, b, f = g["drain_to_detect_s"], g["v3_blocks_to_freeze"], g["freeze_fee_planck"]
        md.append(f"| {label} | " + (f"{d['p50']:.2f} / {d['p95']:.2f}" if d["n"] else "not recorded") + " | "
                  + (f"{b['p50']:.0f} / {b['p95']:.0f}" if b["n"] else "not recorded") + " | "
                  + (f"{tpot(f['p50'])} / {tpot(f['p95'])}" if f["n"] else "–") + " |")
    md += ["", "## How to read it", "",
           "- **One machine.** In the first and second rows the drain, the watcher and the V3 client all run on one laptop; the V3 node is "
           "remote. The third row crosses two clocks (this machine's drain, the Actions runner's inclusion record) and includes the "
           "workflow queue, runner start and `pip install`: it is **not** the latency of a scheduled run, and GitHub's cron is not real-time.",
           "- **Local anvil is not Sepolia.** The first row's reserve chain is a local anvil with instant mining; the freeze leg "
           "(read vault → decide → sign `M_watch` → V3 inclusion) is the same code, but the provider read is faster than a public "
           "Sepolia RPC. The thaw leg in that row uses an emulated finality (`anvil_mine`) and says nothing about Sepolia's measured 14–19 min (841–1,168 s) finality waits.",
           "- **What dominates.** Waiting for the watcher's next poll (the detect column, every 2 V3 blocks of ~6 s) and for inclusion in "
           "a ~6 s block; both are mostly waiting, not computation (a provider read takes ~0.003 s on the anvil and ~0.4–0.6 s on Sepolia in the watcher logs). A sample can land in under one poll interval when the drain happens just before a check.",
           "- **Small n.** With fewer than 20 samples a nearest-rank p95 is simply the largest sample; read the Sepolia "
           f"rows (n = {summary['groups']['v3-sepolia-local']['drain_to_freeze_s']['n']} and "
           f"{summary['groups']['v3-sepolia-actions']['drain_to_freeze_s']['n']}) as a handful of observed drills, not as a percentile.",
           "- **Fee.** The freeze is `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]`; "
           "the figure is the on-chain `TransactionPayment.TransactionFeePaid` of that extrinsic.",
           "- **Samples are not independent trials of a service.** They are sequential drills on one asset; the n is a count of drills, "
           "not a claim about the long-run distribution.", "",
           "## Runs", "", "| Run | Kind | Verdict | Samples counted / in run | Commit |", "|---|---|---|---|---|"]
    for r in runs:
        md.append(f"| [`{r['file']}`](../evidence/{r['file']}) | {r['kind']} | {r['verdict']} | {r['samples_ok']} / {r['samples']} | `{r['source']}` |")
    excluded = [x for x in samples if not x["freeze_ok"]]

    def why(x: dict) -> str:
        if x["group"] == "v3-sepolia-actions":
            return ("the freeze itself was Ok with a `reason=deficit` remark, but the harness version then in use required the remark's "
                    "Sepolia block to equal the drain block, and the Actions runner reads a later block (fixed since, see docs/W2-ACTIONS.md); "
                    "kept out to be conservative")
        return "its own freeze step was not as expected (see the run JSON)"

    md += ["", "Excluded: " + ("; ".join(f"`{x['run']}` ({x['watcher']}, {x['drain_to_freeze_s']:.2f} s): {why(x)}" for x in excluded) or "none") + ".",
           "", "FAIL / ERROR run verdicts above come from pre-flight state checks, not the freeze: `roles-bench-v3-20261031T015842Z` (the vault held a 6.00 surplus, "
           "check relaxed afterwards), `sepolia-drill-20261030T204614Z` and `…212330Z` (owner funding checks). Their freeze steps were as expected and are counted. "
           "`sepolia-drill-20261030T200923Z` ran with uncommitted changes (`dirty: true` in its JSON).", "", "## Samples", "", "| Group | Run | # | Watcher | Freeze extrinsic | Drain → freeze (s) | Fee (tPOT) |", "|---|---|---|---|---|---|---|"]
    for s in samples:
        md.append(f"| {s['group']} | `{s['run']}` | {s['i']} | {s['watcher']} | {s['freeze_extrinsic']}{'' if s['freeze_ok'] else ' (excluded)'} | "
                  f"{s['drain_to_freeze_s']:.2f} | {tpot(s['fee_planck'])} |")
    out = Path(args.out)
    out.write_text("\n".join(md) + "\n")
    print(f"{len(good)} samples counted ({len(samples) - len(good)} excluded) -> {out}, evidence/{sp.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
