"""The bot's local log: SQLite `ballast.db` (gitignored). Every decision is a row — signed or refused, with why.

Never the source of truth (the chains are); it makes refusals inspectable and benchmarks reproducible without
re-scanning both chains.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS mint_request (id INTEGER PRIMARY KEY, kind TEXT, amount TEXT, beneficiary TEXT,
  call_hash TEXT, sep_block_finalized INTEGER, sep_hash_finalized TEXT, reserves TEXT, supply_before TEXT,
  frozen INTEGER, decision TEXT, reason TEXT, exec_tx TEXT, profile TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS attestation (id INTEGER PRIMARY KEY, kind TEXT, pd_block INTEGER, pd_hash TEXT,
  supply TEXT, supply2 TEXT, sep_block INTEGER, sep_hash TEXT, reserves TEXT, remark TEXT, remark_tx TEXT,
  oracle_tx TEXT, verified INTEGER, profile TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS provider_reading (id INTEGER PRIMARY KEY, provider TEXT, tag TEXT, block INTEGER,
  block_hash TEXT, reserves TEXT, error TEXT, read_at TEXT);
"""


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Store:
    def __init__(self, path: str | Path = "ballast.db"):
        self.path = str(path)
        self.db = sqlite3.connect(self.path)
        self.db.executescript(SCHEMA)

    def close(self) -> None:
        self.db.close()

    def _insert(self, table: str, row: dict) -> int:
        row = {k: (json.dumps(v) if isinstance(v, (dict, list)) else v) for k, v in row.items()}
        cols = ", ".join(row)
        cur = self.db.execute(f"INSERT INTO {table} ({cols}) VALUES ({', '.join('?' * len(row))})", list(row.values()))
        self.db.commit()
        return cur.lastrowid

    def request(self, **row) -> int:
        return self._insert("mint_request", {"created_at": _now(), **row})

    def set_exec(self, row_id: int, exec_tx: str, decision: str | None = None) -> None:
        if decision:
            self.db.execute("UPDATE mint_request SET exec_tx = ?, decision = ? WHERE id = ?", (exec_tx, decision, row_id))
        else:
            self.db.execute("UPDATE mint_request SET exec_tx = ? WHERE id = ?", (exec_tx, row_id))
        self.db.commit()

    def set_oracle_tx(self, remark_tx: str, oracle_tx: str) -> None:
        self.db.execute("UPDATE attestation SET oracle_tx = ? WHERE remark_tx = ?", (oracle_tx, remark_tx))
        self.db.commit()

    def attestation(self, **row) -> int:
        return self._insert("attestation", {"created_at": _now(), **row})

    def readings(self, readings: list[dict]) -> None:
        for r in readings:
            self._insert("provider_reading", {"provider": r["provider"], "tag": r["tag"], "block": r["block_number"],
                                              "block_hash": r["block_hash"], "reserves": r["reserves"],
                                              "error": r["error"], "read_at": r["read_at"]})

    def rows(self, table: str) -> list[dict]:
        cur = self.db.execute(f"SELECT * FROM {table} ORDER BY id")  # noqa: S608 — table names are ours
        names = [c[0] for c in cur.description]
        return [dict(zip(names, row)) for row in cur.fetchall()]
