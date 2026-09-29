#!/usr/bin/env bash
# ============================================================================
# M10 PROOF (cloud) - does the LIVE market-data source run on cloud infra?
#
# Same targets as the M5 gate (Neon PostgreSQL + Upstash Redis), but the price
# source is MARKET_DATA_SOURCE=trade_server: a trade-server-protocol WebSocket
# upstream (scripts/m10_ws_simulator.py) instead of the mock random walk.
#
# Steps
#   1  fail-hard: trade_server without TRADE_SERVER_WS_URL refuses to boot
#   2  WS upstream simulator up on a local port
#   3  boot the API on cloud DB + cloud Redis + LIVE ws price source
#   4  GET /health healthy
#   5  trade over HTTP: the fill price is the price pushed over the socket
#   6  clean shutdown (ingestor stopped)
#
# Usage:  ./scripts/m10_proof_cloud_ws.sh
# ============================================================================
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

PASS=0; FAIL=0
ok()   { PASS=$((PASS+1)); printf '  [PASS] %s %s\n' "$1" "${2:-}"; }
bad()  { FAIL=$((FAIL+1)); printf '  [FAIL] %s %s\n' "$1" "${2:-}"; }
step() { printf '\n[%s] %s\n' "$1" "$2"; }

export PYTHONPATH="$PWD"
SIM_PORT="${SIM_PORT:-8066}"
PORT="${PORT:-8067}"
BASE="http://127.0.0.1:${PORT}"
WS_URL="ws://127.0.0.1:${SIM_PORT}/ws/marketdata"
LOG=/tmp/m10-api.log
SIMLOG=/tmp/m10-sim.log
PIDFILE=/tmp/m10-api.pid
SIMPIDFILE=/tmp/m10-sim.pid
FILL_ASK="1.23460"   # must match M10_SIM_PRICES below

cleanup() {
  for pf in "$PIDFILE" "$SIMPIDFILE"; do
    if [ -f "$pf" ]; then
      kill "$(cat "$pf")" 2>/dev/null
      sleep 1
      kill -9 "$(cat "$pf")" 2>/dev/null
      rm -f "$pf"
    fi
  done
}
trap cleanup EXIT

[ -f .env ] || { bad ".env exists" "the M5 gate needs it too"; exit 1; }
set -a; . ./.env; set +a

# --------------------------------------------- 1. fail-hard without the URL
step 1 "MARKET_DATA_SOURCE=trade_server without TRADE_SERVER_WS_URL must refuse to boot"
MARKET_DATA_SOURCE=trade_server TRADE_SERVER_WS_URL= \
  timeout 30 python3 -m uvicorn api.main:app --host 127.0.0.1 --port "$((PORT+1))" > /tmp/m10-fail.log 2>&1
if grep -q "requires TRADE_SERVER_WS_URL" /tmp/m10-fail.log; then
  ok "startup refused, naming the missing setting"
else
  bad "startup refused, naming the missing setting"; tail -5 /tmp/m10-fail.log
fi

# ------------------------------------------------ 2. WS upstream simulator
step 2 "trade-server-protocol WS upstream on :$SIM_PORT"
M10_SIM_PORT="$SIM_PORT" M10_SIM_PRICES="{\"EURUSD\": [\"1.23450\", \"$FILL_ASK\"]}" \
  python3 scripts/m10_ws_simulator.py > "$SIMLOG" 2>&1 &
echo $! > "$SIMPIDFILE"
SIMUP=0
for _ in $(seq 1 30); do
  if python3 -c "import urllib.request,sys; urllib.request.urlopen('http://127.0.0.1:$SIM_PORT/healthz', timeout=2)" 2>/dev/null; then SIMUP=1; break; fi
  sleep 0.5
done
[ "$SIMUP" = 1 ] && ok "WS simulator up" || { bad "WS simulator up"; tail -5 "$SIMLOG"; exit 1; }

# ------------------------------------------------------ 3. boot with live WS
step 3 "boot the API: cloud DB + cloud Redis + MARKET_DATA_SOURCE=trade_server"
MARKET_DATA_SOURCE=trade_server TRADE_SERVER_WS_URL="$WS_URL" TRADE_SERVER_WS_SYMBOLS=EURUSD \
  python3 -m uvicorn api.main:app --host 127.0.0.1 --port "$PORT" > "$LOG" 2>&1 &
echo $! > "$PIDFILE"
BOOTED=0
for _ in $(seq 1 60); do
  if grep -q "Application startup complete" "$LOG" 2>/dev/null; then BOOTED=1; break; fi
  if ! kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then break; fi
  sleep 1
done
if [ "$BOOTED" = 1 ]; then
  ok "server booted"
  grep -q "MARKET_DATA_SOURCE=trade_server: live ticks" "$LOG" && ok "live WS price source announced" || bad "live WS price source announced"
  grep -q "MARKET_DATA_SOURCE=mock" "$LOG" && bad "mock source NOT running" || ok "mock source NOT running"
  grep -q "trade-server feed connected" "$LOG" && ok "feed adapter connected upstream" || bad "feed adapter connected upstream"
  sleep 2
  grep -q "subscribed EURUSD" "$SIMLOG" && ok "upstream saw the EURUSD subscription" || bad "upstream saw the EURUSD subscription"
else
  bad "server booted"; tail -20 "$LOG"
fi

# ------------------------------------------------------------- 4. health
step 4 "GET /health"
HEALTH=$(python3 -c "
import json, urllib.request
with urllib.request.urlopen('$BASE/health', timeout=15) as r:
    print(json.dumps(json.load(r)))" 2>&1)
echo "$HEALTH" | grep -q '"status": *"healthy"\|"status":"healthy"' \
  && ok "/health healthy on live WS source" || bad "/health healthy" "$HEALTH"

# ------------------------------------------ 5. trade: fill == socket price
step 5 "trade over HTTP; the fill must carry the price pushed over the socket"
TRADE=$(python3 - "$BASE" "$FILL_ASK" << 'PY'
import asyncio, json, os, sys, time, urllib.request
sys.path.insert(0, os.getcwd())
BASE, FILL_ASK = sys.argv[1], sys.argv[2]
PROOF_PASSWORD = "M10-CloudProof!2026"

def req(path, payload=None, token=None):
    data = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(BASE + path, data=data,
                               method="POST" if data else "GET",
                               headers={"Content-Type": "application/json"})
    if token:
        r.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:200]

async def make_account():
    from decimal import Decimal
    from api.main import default_providers
    from core.domains.accounts.account import Account
    from core.domains.common.value_objects import Money
    from infrastructure.security.password_hasher import Argon2PasswordHasher

    providers = default_providers()
    db, group_repo, account_repo = providers["database"], providers["group_repo"], providers["account_repo"]
    groups = {g.name: g for g in await group_repo.get_all()}
    group = groups.get("demo\\Standard") or next(iter(groups.values()))
    login = 800000 + (int(time.time()) % 99999)
    account = Account(login=login, client_id="CLIENT_M10", group=group, group_id=group.id,
                      currency="USD", balance=Money(Decimal("10000"), "USD"),
                      credit=Money(Decimal("0"), "USD"), equity=Money(Decimal("10000"), "USD"),
                      margin_used=Money(Decimal("0"), "USD"), margin_free=Money(Decimal("10000"), "USD"))
    account.password_hash = Argon2PasswordHasher().hash_password(PROOF_PASSWORD)
    await account_repo.save(account)
    await db.close()
    return login

async def main():
    out = {}
    try:
        login = await make_account()
    except Exception as e:
        print(json.dumps({"account_error": f"{type(e).__name__}: {e}"})); return
    out["login"] = login
    st, tok = req("/api/v1/auth/login", {"login_id": str(login), "password": PROOF_PASSWORD})
    out["login_status"] = st
    if st != 200:
        print(json.dumps(out)); return
    token = tok["access_token"]
    st, body = req("/api/v1/trade/orders", {"symbol": "EURUSD", "order_type": "BUY", "volume": "0.10"}, token)
    out["order_status"] = st
    out["order"] = body if st == 200 else str(body)[:300]
    if st == 200 and isinstance(body, dict):
        from decimal import Decimal
        out["filled_volume"] = str(body.get("filled_volume"))
        out["filled_ok"] = str(
            Decimal(str(body.get("filled_volume", 0))) == Decimal("0.10"))
    st, pos = req("/api/v1/account/positions", None, token)
    out["positions_status"] = st
    if isinstance(pos, list) and pos:
        out["average_price"] = str(pos[0].get("average_price"))
        out["positions_count"] = len(pos)
    print(json.dumps(out))

asyncio.run(main())
PY
)
echo "         $TRADE"
echo "$TRADE" | grep -q '"order_status": *200' && ok "market order accepted over HTTP" || bad "market order accepted over HTTP"
echo "$TRADE" | grep -q '"state": *"FILLED"\|"state":"FILLED"' && ok "order FILLED" || bad "order FILLED"
echo "$TRADE" | grep -q '"filled_ok": *"True"\|"filled_ok":"True"' \
  && ok "response reports filled_volume 0.10 (entity round-trip fixed)" \
  || bad "response reports filled_volume 0.10" "$(echo "$TRADE" | grep -o '"filled_volume": *"[^"]*"')"
# Prices come back on the platform's 8-digit volume/price scale ("1.23460000"),
# so compare numerically, not as strings.
AVG=$(echo "$TRADE" | python3 -c "
import json,sys
from decimal import Decimal
try:
    d=json.loads(sys.stdin.read())
    print('1' if Decimal(str(d.get('average_price','0'))) == Decimal('$FILL_ASK') else '0')
except Exception:
    print('0')")
[ "${AVG:-0}" = 1 ] \
  && ok "fill price == the ask pushed over the live WS socket ($FILL_ASK)" \
  || bad "fill price == WS ask ($FILL_ASK)"

# --------------------------------------------------------- 6. shutdown
step 6 "clean shutdown"
kill "$(cat "$PIDFILE")" 2>/dev/null; rm -f "$PIDFILE"
sleep 4
grep -q "TickIngestor stopped" "$LOG" && ok "TickIngestor stopped" || bad "TickIngestor stopped"
grep -q "Shutting down" "$LOG"        && ok "uvicorn shut down"    || bad "uvicorn shut down"

printf '\n=== M10 cloud WS proof: %d passed, %d failed ===\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] && echo "Live market data runs on the cloud stack." || echo "SEE FAILURES ABOVE"
exit "$FAIL"
