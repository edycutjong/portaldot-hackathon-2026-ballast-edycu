from ballast.rpc import HttpRpc, WsRpc, http_url, node_rpc


def test_public_wss_endpoints_use_websocket_local_nodes_use_http():
    # the V3 node answers HTTPS with 403, so wss:// must stay a WebSocket
    assert isinstance(node_rpc("wss://test-node-v3.portaldot.dev"), WsRpc)
    local = node_rpc("ws://127.0.0.1:49944")
    assert isinstance(local, HttpRpc) and local.url == "http://127.0.0.1:49944"
    assert http_url("wss://x.example") == "https://x.example"


class _Sock:
    def __init__(self, replies):
        self.replies, self.sent, self.closed = list(replies), [], False

    def send(self, body):
        self.sent.append(body)

    def recv(self):
        r = self.replies.pop(0)
        if isinstance(r, Exception):
            raise r
        return r

    def close(self):
        self.closed = True


def test_ws_rpc_reconnects_once_after_a_dropped_socket(monkeypatch):
    import websocket

    import ballast.rpc as rpc

    socks = [_Sock([websocket.WebSocketConnectionClosedException("gone")]), _Sock(['{"jsonrpc":"2.0","id":1,"result":"0x01"}'])]
    monkeypatch.setattr(rpc.websocket, "create_connection", lambda url, timeout: socks.pop(0))
    client = WsRpc("wss://node.invalid")
    assert client.call("chain_getBlockHash", [0]) == "0x01"
    assert not socks


def test_ws_rpc_raises_rpc_errors(monkeypatch):
    import pytest

    import ballast.rpc as rpc

    monkeypatch.setattr(rpc.websocket, "create_connection",
                        lambda url, timeout: _Sock(['{"jsonrpc":"2.0","id":1,"error":{"code":-32601}}']))
    with pytest.raises(rpc.RpcError, match="nope"):
        WsRpc("wss://node.invalid").call("nope")
