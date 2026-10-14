#!/usr/bin/env bash
# Start / stop the standin-upstream chain on Ballast's ports (NOT V3 — a labelled stand-in while V3 is unreachable).
#   scripts/standin_node.sh start | stop | status
# Binary: prebuilt polkadot-sdk substrate-node, release polkadot-stable2606-3, aarch64-apple-darwin, sha256-pinned:
#   https://github.com/paritytech/polkadot-sdk/releases/download/polkadot-stable2606-3/substrate-node-aarch64-apple-darwin
# Download it to the default path below (chmod +x) or point BALLAST_NODE_BIN at it. Other platforms: build `substrate-node` from that tag and
# set BALLAST_NODE_SHA256 to its hash (the runtime :code hash is what scripts check, see ballast/chain_profile.py).
# Ports: RPC (WS + HTTP on one port) 49944, p2p 30349 bound to 127.0.0.1, no peer discovery, no peers allowed:
# every --dev chain shares a genesis, so a node that peered with another local dev node would share its chain.
set -euo pipefail

BIN="${BALLAST_NODE_BIN:-$HOME/.cache/ballast-interim/bin/substrate-node-aarch64-apple-darwin}"
SHA256="${BALLAST_NODE_SHA256:-e687db4993973bd83922cfa9f01e29bb549af16560511b1fd51ff883b996207f}"
DATA="${BALLAST_NODE_DIR:-$HOME/.cache/ballast-interim}"
PIDFILE="$DATA/node.pid"
RPC_PORT=49944
P2P_PORT=30349

# Only ever the PID this script started, and only while it still runs from our data dir.
running() { [ -f "$PIDFILE" ] && ps -o command= -p "$(cat "$PIDFILE")" 2>/dev/null | grep -qF -- "$DATA/chain-sdk"; }

case "${1:-status}" in
  start)
    if running; then echo "already running: pid $(cat "$PIDFILE")"; exit 0; fi
    if lsof -nP -iTCP:"$RPC_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
      echo "port $RPC_PORT is busy and $PIDFILE does not match it — not touching it" >&2; exit 1
    fi
    echo "$SHA256  $BIN" | shasum -a 256 -c - >/dev/null || { echo "binary sha256 mismatch: $BIN" >&2; exit 1; }
    mkdir -p "$DATA/chain-sdk"
    nohup "$BIN" --dev --base-path "$DATA/chain-sdk" \
      --state-pruning archive --blocks-pruning archive \
      --rpc-port "$RPC_PORT" --listen-addr "/ip4/127.0.0.1/tcp/$P2P_PORT" \
      --no-mdns --reserved-only --in-peers 0 --out-peers 0 \
      --no-prometheus --no-telemetry >>"$DATA/node.log" 2>&1 &
    echo $! >"$PIDFILE"
    for _ in $(seq 1 60); do
      if curl -sf -m 2 -H 'Content-Type: application/json' \
        -d '{"id":1,"jsonrpc":"2.0","method":"system_health","params":[]}' "http://127.0.0.1:$RPC_PORT" >/dev/null; then
        echo "standin-upstream up: pid $(cat "$PIDFILE"), rpc ws/http://127.0.0.1:$RPC_PORT"; exit 0
      fi
      sleep 1
    done
    echo "node did not answer on $RPC_PORT; see $DATA/node.log" >&2; exit 1
    ;;
  stop)
    if running; then
      pid="$(cat "$PIDFILE")"; kill "$pid"
      for _ in $(seq 1 30); do kill -0 "$pid" 2>/dev/null || break; sleep 1; done
      if kill -0 "$pid" 2>/dev/null; then echo "pid $pid still running after 30 s" >&2; exit 1; fi
      rm -f "$PIDFILE"; echo "stopped pid $pid"
    else
      echo "not running"
    fi
    ;;
  status)
    if running; then echo "running: pid $(cat "$PIDFILE")"; else echo "not running"; exit 1; fi
    curl -s -m 2 -H 'Content-Type: application/json' \
      -d '{"id":1,"jsonrpc":"2.0","method":"system_health","params":[]}' "http://127.0.0.1:$RPC_PORT"; echo
    ;;
  *) echo "usage: $0 start|stop|status" >&2; exit 2 ;;
esac
