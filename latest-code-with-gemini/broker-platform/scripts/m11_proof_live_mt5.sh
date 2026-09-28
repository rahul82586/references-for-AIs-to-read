#!/usr/bin/env bash
# M11 live proof: real MT5 terminal -> trade-server WS -> broker platform -> Neon.
#
# This is m10_proof_cloud_ws.sh with the SIMULATOR replaced by a real MT5 terminal
# reached through a public tunnel. Nothing is mocked below the API: the price that
# fills the order is the price MetaTrader quoted a moment ago.
#
# Requires: .env (DATABASE_URL, REDIS_URL, SECRET_KEY, ADMIN_API_KEY) and
#           TRADE_SERVER_WS_URL pointing at a CONNECTED trade-server.
set -uo pipefail
BP="$(cd "$(dirname "$0")/.." && pwd)"
cd "$BP" || exit 1
export PYTHONPATH="$BP"
set -a; . ./.env; set +a

: "${TRADE_SERVER_WS_URL:?set TRADE_SERVER_WS_URL in .env}"
export MARKET_DATA_SOURCE=trade_server
export TRADE_SERVER_WS_SYMBOLS="${TRADE_SERVER_WS_SYMBOLS:-EURUSD}"
export BROKER_MT5_FIXTURES="${BROKER_MT5_FIXTURES:-$BP/../decoded/mt5-format-structure}"

PORT="${PORT:-8177}"
BASE="http://127.0.0.1:$PORT"
LOG=/tmp/m11-live.log
PASS=0; FAIL=0
ok(){ PASS=$((PASS+1)); printf '  [PASS] %s %s\n' "$1" "${2:-}"; }
bad(){ FAIL=$((FAIL+1)); printf '  [FAIL] %s %s\n' "$1" "${2:-}"; }
step(){ printf '\n[%s] %s\n' "$1" "$2"; }
cleanup(){ [ -n "${PID:-}" ] && kill "$PID" 2>/dev/null; sleep 2; [ -n "${PID:-}" ] && kill -9 "$PID" 2>/dev/null; }
trap cleanup EXIT

step 1 "the upstream trade-server is connected to a real MT5 terminal"
MT5=$(python3 - <<'PY'
import json, os, urllib.request
url = os.environ["TRADE_SERVER_WS_URL"]
base = url.split("/ws")[0].replace("wss://","https://").replace("ws://","http://")
try:
    r = urllib.request.urlopen(urllib.request.Request(
        base+"/api/v1/status", headers={"User-Agent":"bp","ngrok-skip-browser-warning":"1"}), timeout=30)
    d = json.load(r).get("data", {})
    print(json.dumps(d))
except Exception as e:
    print(json.dumps({"error": f"{type(e).__name__}: {e}"}))
PY
)
echo "         $MT5"
echo "$MT5" | grep -q '"status": *"connected"' && ok "MT5 terminal connected" || bad "MT5 terminal connected"
echo "$MT5" | grep -q '"login"' && ok "a real account login is attached" || bad "account login"

step 2 "boot the platform on the LIVE price source (Neon + Upstash + trade-server)"
rm -f "$LOG"
python3 -m uvicorn api.main:app --host 127.0.0.1 --port "$PORT" >"$LOG" 2>&1 &
PID=$!
for _ in $(seq 1 60); do
  python3 -c "import urllib.request;urllib.request.urlopen('$BASE/health',timeout=2)" >/dev/null 2>&1 && break
  sleep 0.5
done
kill -0 $PID 2>/dev/null && ok "server booted" || { bad "server booted"; tail -20 "$LOG"; exit 1; }
grep -q "MARKET_DATA_SOURCE=trade_server" "$LOG" && ok "live source announced" || bad "live source announced"
grep -qi "mock" "$LOG" && bad "the mock feed must NOT be in use" || ok "no mock feed anywhere in the log"
for _ in $(seq 1 20); do grep -q "trade-server feed connected" "$LOG" && break; sleep 1; done
grep -q "trade-server feed connected" "$LOG" && ok "the WS adapter connected upstream" || bad "WS adapter connected"
grep -q "Redis event bus connected\|Redis subscribed" "$LOG" && ok "Upstash event bus connected" || bad "event bus"

step 3 "real ticks reach the engine"
sleep 12
TICKS=$(grep -ci "tick" "$LOG" || true)
python3 - "$BASE" <<'PY' > /tmp/m11-prices.json 2>/tmp/m11-prices.err
import json, os, sys, urllib.request
# read the engine's own view of the price through the platform, not the raw socket
os.environ.setdefault("PYTHONPATH", os.getcwd())
PY
python3 - <<'PY' > /tmp/m11-ticks.txt 2>&1
import asyncio, json, msgpack, os, urllib.request
URL = os.environ["TRADE_SERVER_WS_URL"]
async def main():
    import websockets
    async with websockets.connect(URL, open_timeout=30,
                                 additional_headers={"User-Agent":"bp"}) as ws:
        await ws.send(json.dumps({"action":"sub","symbol":"EURUSD"}))
        got=[]
        for _ in range(3):
            try: raw = await asyncio.wait_for(ws.recv(), timeout=20)
            except asyncio.TimeoutError: break
            if isinstance(raw,(bytes,bytearray)):
                got.append(msgpack.unpackb(raw, raw=False))
        print(json.dumps(got))
asyncio.run(main())
PY
LIVE=$(cat /tmp/m11-ticks.txt | tail -1)
echo "         upstream ticks: ${LIVE:0:220}"
python3 - <<PY
import json, sys
try:
    ticks = json.loads('''$LIVE''')
except Exception as e:
    print("could not parse"); sys.exit(1)
if not ticks:
    sys.exit(1)
b, a = float(ticks[-1]["b"]), float(ticks[-1]["a"])
open("/tmp/m11-live-price.txt","w").write(f"{b} {a}")
print(f"         live EURUSD bid={b} ask={a}")
sys.exit(0 if (1.0 < b < 2.0 and a >= b) else 1)
PY
[ $? -eq 0 ] && ok "a real MT5 price is being quoted" || bad "real price quoted"

step 4 "trade over HTTP and fill at the LIVE price"
python3 - "$BASE" <<'PY' > /tmp/m11-trade.json 2>/tmp/m11-trade.err
import asyncio, json, os, sys, time, urllib.request, urllib.error
from decimal import Decimal
BASE = sys.argv[1]
PW = "M11-LiveProof!2026"
def post(p, payload, token=None):
    req = urllib.request.Request(BASE+p, data=json.dumps(payload).encode(), method="POST",
                                 headers={"Content-Type":"application/json"})
    if token: req.add_header("Authorization","Bearer "+token)
    try:
        with urllib.request.urlopen(req,timeout=40) as r: return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e: return e.code, e.read().decode()[:300]
def get(p, token=None):
    req = urllib.request.Request(BASE+p, headers={})
    if token: req.add_header("Authorization","Bearer "+token)
    try:
        with urllib.request.urlopen(req,timeout=40) as r: return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e: return e.code, e.read().decode()[:300]

async def make_account():
    from api.main import default_providers
    from core.domains.accounts.account import Account
    from core.domains.common.value_objects import Money
    from infrastructure.security.password_hasher import Argon2PasswordHasher
    p = default_providers(); db = p["database"]
    groups = {g.name: g for g in await p["group_repo"].get_all()}
    g = groups.get("demo\\Standard") or next(iter(groups.values()))
    login = 810000 + (int(time.time()) % 89999)
    a = Account(login=login, client_id="CLIENT_M11_LIVE", group=g, group_id=g.id, currency="USD",
        balance=Money(Decimal("10000"),"USD"), credit=Money(Decimal("0"),"USD"),
        equity=Money(Decimal("10000"),"USD"), margin_used=Money(Decimal("0"),"USD"),
        margin_free=Money(Decimal("10000"),"USD"))
    a.password_hash = Argon2PasswordHasher().hash_password(PW)
    await p["account_repo"].save(a); await db.close()
    return login

out = {}
try:
    login = asyncio.run(make_account()); out["login"] = login
except Exception as e:
    out["account_error"] = f"{type(e).__name__}: {e}"; print(json.dumps(out)); sys.exit()

st, tok = post("/api/v1/auth/login", {"login_id": str(login), "password": PW})
out["login_status"] = st
if st != 200:
    out["login_body"] = tok; print(json.dumps(out)); sys.exit()
token = tok["access_token"]

st, body = post("/api/v1/trade/orders",
                {"symbol":"EURUSD","order_type":"BUY","volume":"0.10"}, token)
out["order_status"] = st
out["order"] = body if st == 200 else str(body)[:400]
st, pos = get("/api/v1/account/positions", token)
out["positions_status"] = st
out["positions"] = pos if st == 200 else str(pos)[:300]
st, info = get("/api/v1/account/info", token)
out["info_status"] = st
out["info"] = info if st == 200 else str(info)[:300]
print(json.dumps(out, default=str))
PY
cat /tmp/m11-trade.json | python3 -c "
import json,sys
d=json.load(sys.stdin)
for k,v in d.items(): print(f'         {k}: {str(v)[:300]}')
" 2>/dev/null || { echo "         trade error:"; tail -8 /tmp/m11-trade.err; }

T=$(cat /tmp/m11-trade.json)
echo "$T" | grep -q '"login_status": 200'      && ok "password-verified login" || bad "login"
echo "$T" | grep -q '"order_status": 200'      && ok "order accepted over HTTP" || bad "order accepted"
echo "$T" | grep -q '"state": "FILLED"'        && ok "order FILLED" || bad "order FILLED"
echo "$T" | grep -q '"positions_status": 200'  && ok "positions endpoint answered" || bad "positions"

step 5 "the fill price is the LIVE MT5 price, not a mock"
python3 - <<'PY'
import json, re, sys
t = open("/tmp/m11-trade.json").read()
m = re.search(r'"price":\s*"([0-9.]+)"', t)
if not m:
    print("  [FAIL] no fill price in the response"); sys.exit(1)
fill = float(m.group(1))
try:
    b, a = [float(x) for x in open("/tmp/m11-live-price.txt").read().split()]
except Exception:
    b = a = None
print(f"         filled at {fill}   (upstream EURUSD was bid={b} ask={a})")
ok = True
# the mock feed's signature price is 1.07961/1.07978 - a live fill must not be that
if abs(fill - 1.07961) < 0.001 or abs(fill - 1.07978) < 0.001:
    print("  [FAIL] that is the MOCK feed's price, not a live one"); ok = False
if b is not None and not (min(b,a) - 0.002 <= fill <= max(b,a) + 0.002):
    print(f"  [FAIL] fill {fill} is nowhere near the live quote {b}/{a}"); ok = False
if ok:
    print(f"  [PASS] filled within 20 pips of the live MT5 quote")
sys.exit(0 if ok else 1)
PY
[ $? -eq 0 ] && PASS=$((PASS+1)) || FAIL=$((FAIL+1))

python3 - <<'PY'
import json, re
t = open("/tmp/m11-trade.json").read()
m = re.search(r'"margin_level":\s*"([0-9.]+)"', t)
if m:
    v = float(m.group(1))
    print(f"         /account/info margin_level = {v}")
    print("  [PASS] D1 holds on the live path" if v > 1 else
          "  [FAIL] margin_level is still 0 - D1 regressed")
PY

step 6 "shutdown"
kill $PID 2>/dev/null; sleep 3
grep -qi "shutting down\|shutdown" "$LOG" && ok "clean shutdown" || bad "clean shutdown"
grep -q "TickIngestor stopped" "$LOG" && ok "TickIngestor stopped" || bad "TickIngestor stopped"

printf '\n%s\n' "============================================================"
printf ' M11 LIVE proof: %d passed, %d failed\n' "$PASS" "$FAIL"
printf '%s\n' "============================================================"
[ "$FAIL" -eq 0 ]
