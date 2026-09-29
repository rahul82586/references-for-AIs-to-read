#!/usr/bin/env bash
# ============================================================================
# D12 CLOUD PROOF — can a client close a position, against real money plumbing?
#
# The cloud database held 31 IN deals and ZERO OUT deals for the whole life of
# the project, because no client-facing close route existed (D11) — and the route
# D11 added then described the close it made as `volume_closed 0E-8 / close_price
# 0 / realized_pnl 0E-8` (D12). Both are fixed and both are tested locally, but
# the only proof that matters for a broker is the one against the real thing:
# live MT5 prices through the tunnel, Neon PostgreSQL, Upstash Redis, real HTTP.
#
#   1  the trade-server tunnel answers and its MT5 terminal is CONNECTED
#   2  boot the API: MARKET_DATA_SOURCE=trade_server, cloud DB, cloud bus
#   3  /health, and the log must announce the LIVE price source
#   4  create an account in Neon, log in over HTTP with the Argon2 password
#   5  BUY at the live price, confirm it holds margin
#   6  POST /trade/positions/{id}/close, then check the response says what the
#      trade did (D12) and that Neon holds an OUT deal, deal_close set, margin 0
#
# Symbol default is BTCUSD, not EURUSD: BTCUSD is a 7x24 session in the cloud
# config, so this proof runs at a weekend. EURUSD is correctly closed Sat/Sun and
# every trade check would skip — that is right behaviour and a useless proof.
#
# Deliberately NOT set: BROKER_LP_GATEWAY. Leaving it at the default keeps the
# order on the B-Book, so the proof creates no A-Book hedge in the real MT5
# account that nothing would unwind (see PROJECT-STATE.md: A-Book position close
# is still an open item, and six orphaned hedges had to be closed by hand).
#
# Usage:  ./scripts/d12_proof_cloud_close.sh [SYMBOL] [VOLUME]
# Needs:  .env with DATABASE_URL, REDIS_URL, TRADE_SERVER_WS_URL
# ============================================================================
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

SYMBOL="${1:-BTCUSD}"
VOLUME="${2:-0.01}"
PORT="${PORT:-8066}"
BASE="http://127.0.0.1:${PORT}"
LOG="${ARENA_WORKSPACE:-/tmp}/work/logs/d12_cloud_api.log"
PIDFILE="/tmp/d12-cloud-api.pid"

PASS=0; FAIL=0
ok()  { PASS=$((PASS+1)); printf '  [PASS] %s %s\n' "$1" "${2:-}"; }
bad() { FAIL=$((FAIL+1)); printf '  [FAIL] %s %s\n' "$1" "${2:-}"; }
step(){ printf '\n[%s] %s\n' "$1" "$2"; }

cleanup() {
  if [ -f "$PIDFILE" ]; then
    kill "$(cat "$PIDFILE")" 2>/dev/null; sleep 2
    kill -9 "$(cat "$PIDFILE")" 2>/dev/null; rm -f "$PIDFILE"
  fi
}
trap cleanup EXIT

export PYTHONPATH="$PWD"
if [ ! -f .env ]; then bad ".env exists"; echo "cannot continue"; exit 1; fi
set -a; . ./.env; set +a
export DATABASE_URL REDIS_URL SECRET_KEY ADMIN_API_KEY
export MARKET_DATA_SOURCE=trade_server
export TRADE_SERVER_WS_SYMBOLS="$SYMBOL"
unset BROKER_LP_GATEWAY || true
mkdir -p "$(dirname "$LOG")"

# ---------------------------------------------------------------- 1. tunnel
step 1 "the MT5 terminal behind the tunnel"
WS="${TRADE_SERVER_WS_URL:-}"
HTTP="${WS%%/ws*}"; HTTP="${HTTP#wss://}"; HTTP="https://${HTTP}"
STATUS=$(python3 - "$HTTP" <<'PY'
import json, sys, urllib.request
req = urllib.request.Request(sys.argv[1] + "/api/v1/status",
                             headers={"ngrok-skip-browser-warning": "1"})
try:
    with urllib.request.urlopen(req, timeout=25) as r:
        print(json.dumps(json.load(r)))
except Exception as e:
    print("ERR", type(e).__name__, e)
PY
)
echo "         $STATUS" | head -c 300; echo
if echo "$STATUS" | grep -q '"status": *"connected"\|"status":"connected"'; then
  ok "MT5 terminal connected" "$(echo "$STATUS" | grep -o '"login":[0-9]*')"
else
  bad "MT5 terminal connected" "no live prices without it - reconnect the terminal"
  echo "cannot continue"; exit 1
fi

# ------------------------------------------------------------------ 2. boot
step 2 "boot the API against Neon + Upstash with the LIVE price source"
if python3 -c "
import socket,sys
s=socket.socket(); sys.exit(0 if s.connect_ex(('127.0.0.1',$PORT))==0 else 1)" 2>/dev/null; then
  bad "port $PORT free" "a stale server would answer every check below"; exit 3
fi
# LOG_LEVEL=debug turns on the market-data engine's own tick logging, which is the
# only place that distinguishes "no ticks arriving" from "ticks arriving and being
# dropped". Without it a dead feed and a weekend feed look identical.
LOG_LEVEL="${LOG_LEVEL:-debug}" \
python3 -m uvicorn api.main:app --host 127.0.0.1 --port "$PORT" > "$LOG" 2>&1 &
echo $! > "$PIDFILE"
BOOTED=0
for _ in $(seq 1 90); do
  grep -q "Application startup complete" "$LOG" 2>/dev/null && { BOOTED=1; break; }
  kill -0 "$(cat "$PIDFILE")" 2>/dev/null || break
  sleep 1
done
if [ "$BOOTED" = 1 ]; then
  ok "server booted"
  grep -q "Connected to Redis" "$LOG" && ok "Upstash event bus connected" || bad "Upstash event bus connected"
  grep -qi "MARKET_DATA_SOURCE=trade_server\|trade_server" "$LOG" \
    && ok "live price source announced" || bad "live price source announced"
  grep -q "Trading plane wired" "$LOG" && ok "trading plane wired" || bad "trading plane wired"
else
  bad "server booted"; tail -25 "$LOG"; exit 1
fi

# ---------------------------------------------------------------- 3. health
step 3 "GET /health -> real Neon SELECT 1 + real Upstash PING"
HEALTH=$(python3 -c "
import json,sys,urllib.request
with urllib.request.urlopen('$BASE/health',timeout=20) as r: print(json.dumps(json.load(r)))" 2>&1)
echo "         $HEALTH" | head -c 300; echo
echo "$HEALTH" | grep -q '"status": *"healthy"\|"status":"healthy"' && ok "/health healthy" || bad "/health healthy"

# Give the feed a moment to subscribe. A log grep cannot answer "are ticks being
# processed": a healthy tick logs nothing at INFO, so the first version of this gate
# matched the startup banner and declared tick activity on a feed that had delivered
# nothing. What is visible is the two failure modes, so report them and let step 5's
# position-row check (D13) be the verdict on the engine.
step 4 "feed state (diagnostic)"
# Ground truth first: connect to the tunnel's WS ourselves and see whether it is
# pushing live quotes or replaying a stale one. That is the difference between "our
# engine is dropping ticks" and "there is nothing live to drop", and the server log
# alone cannot tell you - a healthy tick logs nothing at INFO.
python3 - "$TRADE_SERVER_WS_URL" "$SYMBOL" <<'PY'
import asyncio, json, sys, time
from datetime import datetime, timezone
import msgpack, websockets
url, symbol = sys.argv[1], sys.argv[2].upper()
async def main():
    try:
        ws = await asyncio.wait_for(websockets.connect(url, max_size=None), timeout=20)
    except Exception as e:
        print(f"         WS probe could not connect: {type(e).__name__}: {e}")
        return
    await ws.send(json.dumps({"action": "sub", "symbol": symbol}))
    n, newest = 0, None
    end = asyncio.get_event_loop().time() + 10
    while asyncio.get_event_loop().time() < end:
        try:
            raw = await asyncio.wait_for(ws.recv(), timeout=5)
        except asyncio.TimeoutError:
            continue
        except Exception:
            break
        m = (msgpack.unpackb(raw, raw=False) if isinstance(raw, (bytes, bytearray))
             else json.loads(raw))
        if str(m.get("s", "")).upper() != symbol:
            continue
        n += 1
        if m.get("ts"):
            newest = max(newest or 0, int(m["ts"]))
    await ws.close()
    if n == 0:
        print(f"         WS probe: no {symbol} frames in 10s - the terminal is not quoting it")
        return
    age = (time.time() - newest / 1000.0) if newest else None
    stamp = (datetime.fromtimestamp(newest / 1000.0, timezone.utc).strftime("%H:%M:%S")
             if newest else "?")
    print(f"         WS probe: {n} {symbol} frames in 10s, newest quote stamped "
          f"{stamp} UTC" + (f" ({age:.0f}s old)" if age is not None else ""))
    if age is not None and age > 60:
        print("         the terminal is replaying a STALE quote (market closed, or the "
              "symbol is not in its Market Watch), so the D6 guard is right to drop it "
              "and the engine prices from the symbol's configured spread instead.")
    else:
        print("         quotes are fresh, so the engine must be holding a live price.")
asyncio.run(main())
PY
sleep 5
if grep -q "as stale" "$LOG"; then
  echo "         $(grep -m1 'as stale' "$LOG" | cut -c1-190)"
  echo "         the feed IS delivering; quotes are being rejected as stale (D6 guard)"
elif grep -q "Error streaming from feed" "$LOG"; then
  echo "         $(grep -m1 'Error streaming from feed' "$LOG" | cut -c1-190)"
  echo "         the feed dropped and is reconnecting"
elif grep -q "trade-server feed connected" "$LOG"; then
  echo "         connected, no stale drops, no errors: ticks are being accepted"
else
  bad "the feed never connected"; echo "cannot continue"; exit 1
fi

step 5 "open, then CLOSE over HTTP - and read Neon directly afterwards"
python3 scripts/d12_cloud_close_driver.py "$BASE" "$SYMBOL" "$VOLUME"
DRIVER=$?
step 6 "shutdown"
kill "$(cat "$PIDFILE")" 2>/dev/null; sleep 3
grep -qi "shutdown" "$LOG" && ok "clean shutdown logged" || bad "clean shutdown"
grep -iE "dropping|stale|refus" "$LOG" | tail -3 | sed 's/^/         /'

echo
echo "============================================================"
echo " D12 CLOUD CLOSE: shell gates $PASS passed / $FAIL failed, driver exit $DRIVER"
echo "============================================================"
[ "$FAIL" -eq 0 ] && [ "$DRIVER" -eq 0 ]
