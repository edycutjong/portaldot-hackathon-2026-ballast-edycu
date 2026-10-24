#!/usr/bin/env bash
# Start / stop the LOCAL anvil chain the breaker drill uses as its reserve chain (labelled "reserve: local-anvil
# (not Sepolia)" everywhere). The Sepolia drill runs against the real ReserveVault instead.
#   scripts/anvil_local.sh start | stop | status
# Port 49545 on 127.0.0.1 only; chain id 31337; instant mining; state saved every 10 s and on exit, so receipts
# can be re-read after a restart. Accounts are anvil's public, unlocked dev accounts — nothing here is a secret.
set -euo pipefail

DATA="${BALLAST_NODE_DIR:-$HOME/.cache/ballast-interim}"
PIDFILE="$DATA/anvil.pid"
STATE="$DATA/anvil-state.json"
PORT=49545

running() { [ -f "$PIDFILE" ] && ps -o command= -p "$(cat "$PIDFILE")" 2>/dev/null | grep -qF -- "$STATE"; }

case "${1:-status}" in
  start)
    if running; then echo "already running: pid $(cat "$PIDFILE")"; exit 0; fi
    if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
      echo "port $PORT is busy and $PIDFILE does not match it — not touching it" >&2; exit 1
    fi
    command -v anvil >/dev/null || { echo "anvil not found (install Foundry: https://getfoundry.sh)" >&2; exit 1; }
    mkdir -p "$DATA"
    nohup anvil --host 127.0.0.1 --port "$PORT" --chain-id 31337 --state "$STATE" --state-interval 10 \
      --silent >>"$DATA/anvil.log" 2>&1 &
    echo $! >"$PIDFILE"
    for _ in $(seq 1 30); do
      if curl -sf -m 2 -H 'Content-Type: application/json' \
        -d '{"id":1,"jsonrpc":"2.0","method":"eth_chainId","params":[]}' "http://127.0.0.1:$PORT" >/dev/null; then
        # A reloaded state keeps its old block clock: every reserve reading would look hours stale and the bot (rightly)
        # refuses it. Re-anchor the clock to now with one empty block.
        rpc() { curl -sf -m 5 -H 'Content-Type: application/json' -d "{\"id\":1,\"jsonrpc\":\"2.0\",\"method\":\"$1\",\"params\":$2}" "http://127.0.0.1:$PORT" >/dev/null; }
        rpc evm_setNextBlockTimestamp "[$(date +%s)]" && rpc evm_mine "[]" || echo "warning: could not re-anchor the anvil clock" >&2
        echo "local anvil up: pid $(cat "$PIDFILE"), http://127.0.0.1:$PORT (chain id 31337)"; exit 0
      fi
      sleep 1
    done
    echo "anvil did not answer on $PORT; see $DATA/anvil.log" >&2; exit 1
    ;;
  stop)
    if running; then
      pid="$(cat "$PIDFILE")"; kill "$pid"
      for _ in $(seq 1 15); do kill -0 "$pid" 2>/dev/null || break; sleep 1; done
      if kill -0 "$pid" 2>/dev/null; then echo "pid $pid still running after 15 s" >&2; exit 1; fi
      rm -f "$PIDFILE"; echo "stopped pid $pid"
    else
      echo "not running"
    fi
    ;;
  status)
    if running; then echo "running: pid $(cat "$PIDFILE")"; else echo "not running"; exit 1; fi
    curl -s -m 2 -H 'Content-Type: application/json' \
      -d '{"id":1,"jsonrpc":"2.0","method":"eth_blockNumber","params":[]}' "http://127.0.0.1:$PORT"; echo
    ;;
  *) echo "usage: $0 start|stop|status" >&2; exit 2 ;;
esac
