"""Reserve reads on the EVM side: `balanceOf(vault)` on the reserve token, from every provider independently.

Each reading is a consistent snapshot: the block (number + hash) is read first, then `eth_call` runs at that
block's hash (EIP-1898, `requireCanonical`), so a reading never mixes two blocks. Providers are read one by one
and never trusted together: an unreachable provider is a reading with an error, and two providers that disagree
on the hash of a block number, or on the balance at one hash, are reported — the caller decides what that means.

Sepolia is read keyless (no API key, no signing key); the same reader serves the local anvil chain the drill uses.
"""

from __future__ import annotations

import re
import time
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol

SEPOLIA_CHAIN_ID = 11155111
ANVIL_CHAIN_ID = 31337
SEPOLIA_USDC = "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238"  # Circle test USDC on Sepolia (6 decimals)
SEPOLIA_PROVIDERS = (
    ("publicnode", "https://ethereum-sepolia-rpc.publicnode.com"),  # pruned: ~1.4 days of state
    ("drpc", "https://sepolia.drpc.org"),  # serves eth_call at weeks-old block hashes
)
SELECTOR_BALANCE_OF = "0x70a08231"  # balanceOf(address)
SELECTOR_DECIMALS = "0x313ce567"  # decimals()
TAGS = ("latest", "safe", "finalized")


class ProviderError(RuntimeError):
    """The provider could not answer (transport error, JSON-RPC error, or a malformed reply)."""


class EvmRpc(Protocol):
    name: str

    def call(self, method: str, params: list[Any]) -> Any: ...


class Web3Provider:
    """One JSON-RPC endpoint over HTTP via web3.py. Every failure becomes a ProviderError naming the provider."""

    def __init__(self, name: str, url: str, timeout: float = 10.0):
        from web3 import HTTPProvider

        self.name = name
        self.url = url
        self._provider = HTTPProvider(url, request_kwargs={"timeout": timeout})

    def call(self, method: str, params: list[Any]) -> Any:
        try:
            reply = self._provider.make_request(method, params)
        except Exception as exc:  # requests/urllib3/web3 errors: all mean "this provider did not answer"
            raise ProviderError(f"{self.name}: {method}: {_short(exc)}") from None
        if not isinstance(reply, dict):
            raise ProviderError(f"{self.name}: {method}: malformed reply")
        if reply.get("error"):
            raise ProviderError(f"{self.name}: {method}: {reply['error']}")
        if "result" not in reply:
            raise ProviderError(f"{self.name}: {method}: no result")
        return reply["result"]


def _short(exc: Exception) -> str:
    """`ConnectionError: [Errno 61] Connection refused` rather than a urllib3 retry essay."""
    text = str(exc)
    errno = re.search(r"\[Errno -?\d+\][^'\")]*", text)
    if errno:
        return f"{type(exc).__name__}: {errno.group(0).strip()}"
    if "timed out" in text.lower():
        return f"{type(exc).__name__}: timed out"
    return f"{type(exc).__name__}: {text[:160]}"


def providers_from(specs: Iterable[str | tuple[str, str]], timeout: float = 10.0) -> list[Web3Provider]:
    """`name=url` strings (or (name, url) pairs) -> providers. A bare URL is named by its position."""
    out = []
    for i, spec in enumerate(specs, 1):
        if isinstance(spec, tuple):
            name, url = spec
        elif "=" in spec and not spec.startswith("http"):
            name, url = spec.split("=", 1)
        else:
            name, url = f"provider{i}", spec
        out.append(Web3Provider(name, url, timeout=timeout))
    if len({p.name for p in out}) != len(out):
        raise ValueError("provider names must be unique")
    return out


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4] + "Z"


def _int(value: Any) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.startswith("0x"):
        return int(value, 16) if len(value) > 2 else 0
    raise ProviderError(f"not a hex quantity: {value!r}")


def _address_word(address: str) -> str:
    raw = address.lower().removeprefix("0x")
    if len(raw) != 40 or any(c not in "0123456789abcdef" for c in raw):
        raise ValueError(f"not an EVM address: {address!r}")
    return raw.rjust(64, "0")


def balance_of_data(holder: str) -> str:
    return SELECTOR_BALANCE_OF + _address_word(holder)


def chain_id(rpc: EvmRpc) -> int:
    return _int(rpc.call("eth_chainId", []))


def read_block(rpc: EvmRpc, tag: str | int) -> tuple[int, str, int]:
    """(number, hash, timestamp) of a block by tag (`latest` / `safe` / `finalized`) or number."""
    ref = tag if isinstance(tag, str) else hex(tag)
    block = rpc.call("eth_getBlockByNumber", [ref, False])
    if not block or not block.get("hash"):
        raise ProviderError(f"{rpc.name}: no block {tag!r}")
    return _int(block["number"]), block["hash"], _int(block["timestamp"])


def call_at(rpc: EvmRpc, to: str, data: str, block_hash: str) -> str:
    """`eth_call` pinned to a block hash (EIP-1898): the provider must answer for exactly that block."""
    return rpc.call("eth_call", [{"to": to, "data": data}, {"blockHash": block_hash, "requireCanonical": True}])


def balance_at(rpc: EvmRpc, token: str, holder: str, block_hash: str) -> int:
    return _int(call_at(rpc, token, balance_of_data(holder), block_hash))


def token_decimals(rpc: EvmRpc, token: str) -> int:
    return _int(rpc.call("eth_call", [{"to": token, "data": SELECTOR_DECIMALS}, "latest"]))


@dataclass
class ReserveReading:
    provider: str
    tag: str
    block_number: int | None = None
    block_hash: str | None = None
    block_timestamp: int | None = None
    reserves: int | None = None
    error: str | None = None
    read_at: str = field(default_factory=now_iso)
    seconds: float | None = None

    @property
    def ok(self) -> bool:
        return self.error is None and self.reserves is not None

    def as_dict(self) -> dict:
        return {
            "provider": self.provider,
            "tag": self.tag,
            "block_number": self.block_number,
            "block_hash": self.block_hash,
            "block_timestamp": self.block_timestamp,
            "reserves": None if self.reserves is None else str(self.reserves),
            "error": self.error,
            "read_at": self.read_at,
            "seconds": self.seconds,
        }


def read_reserves(rpc: EvmRpc, token: str, holder: str, tag: str = "latest") -> ReserveReading:
    """One provider, one consistent snapshot. Never raises: a failure is a reading with `error` set."""
    started = time.monotonic()
    reading = ReserveReading(provider=rpc.name, tag=tag)
    try:
        number, block_hash, ts = read_block(rpc, tag)
        reading.block_number, reading.block_hash, reading.block_timestamp = number, block_hash, ts
        reading.reserves = balance_at(rpc, token, holder, block_hash)
    except (ProviderError, ValueError) as exc:
        reading.error = str(exc)
    reading.seconds = round(time.monotonic() - started, 3)
    return reading


def read_all(providers: Sequence[EvmRpc], token: str, holder: str, tag: str = "latest") -> list[ReserveReading]:
    return [read_reserves(p, token, holder, tag) for p in providers]


@dataclass
class Comparison:
    """What a set of readings says together. `disagreements` are human-readable and also logged."""

    readings: list[ReserveReading]
    disagreements: list[str]

    @property
    def ok(self) -> list[ReserveReading]:
        return [r for r in self.readings if r.ok]

    @property
    def failed(self) -> list[ReserveReading]:
        return [r for r in self.readings if not r.ok]

    @property
    def all_down(self) -> bool:
        return not self.ok

    @property
    def min_reserves(self) -> int | None:
        return min((r.reserves for r in self.ok), default=None)

    def short(self, supply: int) -> list[ReserveReading]:
        """Readings whose reserves are below `supply`."""
        return [r for r in self.ok if r.reserves < supply]

    def as_dict(self) -> dict:
        return {"readings": [r.as_dict() for r in self.readings], "disagreements": self.disagreements}


def compare(readings: list[ReserveReading], cross_hashes: dict[str, dict[int, str]] | None = None) -> Comparison:
    """Flag (a) two providers naming different hashes for one block number, (b) different reserves at one hash.

    Different block numbers are normal (one provider lags); they are not a disagreement. `cross_hashes`
    (provider -> {number: hash}) adds hashes fetched from other providers for the numbers seen here.
    """
    issues: list[str] = []
    ok = [r for r in readings if r.ok]
    by_number: dict[int, dict[str, str]] = {}
    for r in ok:
        by_number.setdefault(r.block_number, {})[r.provider] = r.block_hash
    for provider, hashes in (cross_hashes or {}).items():
        for number, block_hash in hashes.items():
            by_number.setdefault(number, {}).setdefault(provider, block_hash)
    for number, named in sorted(by_number.items()):
        if len(set(named.values())) > 1:
            listing = ", ".join(f"{p}={h[:12]}…" for p, h in sorted(named.items()))
            issues.append(f"block #{number}: providers disagree on the hash ({listing})")
    by_hash: dict[str, dict[str, int]] = {}
    for r in ok:
        by_hash.setdefault(r.block_hash, {})[r.provider] = r.reserves
    for block_hash, values in by_hash.items():
        if len(set(values.values())) > 1:
            listing = ", ".join(f"{p}={v}" for p, v in sorted(values.items()))
            issues.append(f"block {block_hash[:12]}…: providers disagree on reserves ({listing})")
    return Comparison(readings=readings, disagreements=issues)


def cross_check(providers: Sequence[EvmRpc], token: str, holder: str, tag: str = "finalized") -> dict:
    """Pin one block from the first provider that answers `tag`, then ask EVERY provider for that block number's
    hash and for the balance at that hash. Agreement = one hash and one balance across all answering providers."""
    anchor = None
    for p in providers:
        try:
            anchor = (p.name, *read_block(p, tag))
            break
        except ProviderError:
            continue
    if anchor is None:
        return {"tag": tag, "agree": False, "error": "no provider answered", "providers": {}}
    source, number, anchor_hash, _ts = anchor
    rows: dict[str, dict] = {}
    for p in providers:
        row: dict[str, Any] = {}
        try:
            _n, row["block_hash"], _t = read_block(p, number)
            row["reserves"] = str(balance_at(p, token, holder, anchor_hash))
        except (ProviderError, ValueError) as exc:
            row["error"] = str(exc)
        rows[p.name] = row
    answered = [r for r in rows.values() if "error" not in r]
    agree = (
        len(answered) == len(rows)
        and len({r["block_hash"] for r in answered}) == 1
        and answered[0]["block_hash"] == anchor_hash
        and len({r["reserves"] for r in answered}) == 1
    )
    return {
        "tag": tag,
        "anchor_provider": source,
        "block_number": number,
        "block_hash": anchor_hash,
        "erc20": token,
        "holder": holder,
        "providers": rows,
        "agree": agree,
        "read_at": now_iso(),
    }
