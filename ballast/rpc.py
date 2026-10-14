"""Minimal JSON-RPC over HTTP. Watchers poll; they never hold a subscription open."""

from __future__ import annotations

import json
import urllib.request
from typing import Any, Protocol


class RpcError(RuntimeError):
    pass


class Rpc(Protocol):
    def call(self, method: str, params: list[Any] | None = None) -> Any: ...


def http_url(url: str) -> str:
    """The modern node serves WS and HTTP on one port; map ws(s):// to http(s)://."""
    if url.startswith("ws://"):
        return "http://" + url[len("ws://"):]
    if url.startswith("wss://"):
        return "https://" + url[len("wss://"):]
    return url


class HttpRpc:
    def __init__(self, url: str, timeout: float = 15.0):
        self.url = http_url(url)
        self.timeout = timeout
        self._id = 0

    def call(self, method: str, params: list[Any] | None = None) -> Any:
        self._id += 1
        body = json.dumps({"jsonrpc": "2.0", "id": self._id, "method": method, "params": params or []})
        req = urllib.request.Request(
            self.url, data=body.encode(), headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            reply = json.loads(resp.read())
        if "error" in reply:
            raise RpcError(f"{method}: {reply['error']}")
        return reply["result"]
