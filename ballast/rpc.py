"""Minimal JSON-RPC: plain request/response polling, no subscriptions.

HTTP for local nodes; WebSocket for public wss:// endpoints (the V3 node answers HTTPS with 403)."""

from __future__ import annotations

import json
import urllib.request

import websocket
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


class WsRpc:
    """Request/response over one WebSocket; reconnects once if the socket dropped between calls."""

    def __init__(self, url: str, timeout: float = 30.0):
        self.url = url
        self.timeout = timeout
        self._id = 0
        self._ws: websocket.WebSocket | None = None

    def _send(self, body: str) -> dict:
        if self._ws is None:
            self._ws = websocket.create_connection(self.url, timeout=self.timeout)
        self._ws.send(body)
        return json.loads(self._ws.recv())

    def call(self, method: str, params: list[Any] | None = None) -> Any:
        self._id += 1
        body = json.dumps({"jsonrpc": "2.0", "id": self._id, "method": method, "params": params or []})
        try:
            reply = self._send(body)
        except (websocket.WebSocketException, OSError):
            self.close()
            reply = self._send(body)
        if "error" in reply:
            raise RpcError(f"{method}: {reply['error']}")
        return reply["result"]

    def close(self) -> None:
        if self._ws is not None:
            try:
                self._ws.close()
            finally:
                self._ws = None


def node_rpc(url: str) -> Rpc:
    """wss:// (public endpoints) -> WebSocket; anything else -> HTTP on the same port."""
    return WsRpc(url) if url.startswith("wss://") else HttpRpc(url)
