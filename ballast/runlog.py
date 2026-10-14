"""Evidence recorder shared by the scripted runs: every extrinsic is a step, every storage read a state check.

The JSON it writes is what `docs/RECEIPTS.md` is rendered from and what `scripts/check_receipts.py` re-fetches.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .chain import Receipt
from .receipts import EVIDENCE, score, summarize


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Run:
    def __init__(self, kind: str, chain: dict, role_of: dict[str, str] | None = None, **fields: Any):
        self.data: dict = {"kind": kind, "chain": chain, "started_at": now(), **fields, "steps": [],
                           "evm_steps": [], "state_checks": []}
        self.role_of = role_of or {}

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.data[key] = value

    def step(self, name: str, expected: str, r: Receipt | dict, ok: bool, events: tuple[str, ...] = (),
             counted: bool = True) -> dict:
        rd = r.as_dict() if isinstance(r, Receipt) else r
        names = [f"{e['module_id']}.{e['event_id']}" for e in rd["events"]]
        row = {"name": name, "expected": expected, "as_expected": ok, "counted": counted,
               "signer_role": self.role_of.get(rd["signer"], rd["signer"]),
               "events_seen": [e for e in events if e in names], "receipt": rd}
        self.data["steps"].append(row)
        mark = ("PASS" if ok else "FAIL") if counted else "OBS "
        inner = f" inner={[o['text'] for o in rd['inner']]}" if rd["inner"] else ""
        print(f"{mark} {rd['extrinsic_id']:>9} {rd['call'][:58]:<58} {rd['outcome']['text']}{inner}  {name}")
        return row

    def evm_step(self, row: dict) -> dict:
        self.data["evm_steps"].append(row)
        print(f"{'PASS' if row['as_expected'] else 'FAIL'} evm #{row['block_number']:<5} {row['name']}  {row['tx_hash']}")
        return row

    def check(self, what: str, observed: Any, expected: Any, where: str, ok: bool | None = None) -> bool:
        ok = (observed == expected) if ok is None else ok
        self.data["state_checks"].append({"what": what, "expected": expected, "observed": observed, "ok": ok,
                                          "block_hash": where})
        print(f"     {'ok  ' if ok else 'FAIL'} state: {what}: {observed}")
        return ok

    def note(self, key: str, value: Any) -> None:
        self.data.setdefault("notes", {})[key] = value

    def finish(self, filename: str) -> Path:
        self.data["finished_at"] = now()
        summarize(self.data)
        EVIDENCE.mkdir(exist_ok=True)
        out = EVIDENCE / filename
        out.write_text(json.dumps(self.data, indent=2, default=str) + "\n")
        print(f"\n{self.data['kind']}: {self.data['verdict']} ({score(self.data)}) -> evidence/{out.name}")
        return out
