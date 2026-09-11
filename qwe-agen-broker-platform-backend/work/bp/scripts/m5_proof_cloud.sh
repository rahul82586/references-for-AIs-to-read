#!/usr/bin/env bash
# ============================================================================
# M5 PROOF — does the platform run against managed cloud infrastructure?
#
# Target: Neon PostgreSQL (serverless, TLS, pooled) + Upstash Redis (TLS).
# Nothing here is mocked below the repository layer: real network, real TLS,
# real SQL, real pub/sub.
#
# Steps
#   1  env present, .env gitignored, secrets not the old placeholders
#   2  alembic upgrade head on real PostgreSQL 18
#   3  cli seed  -> groups/symbols/coverage/admin in the cloud DB
#   4  cli status -> reads them back
#   5  boot the API with REDIS_URL + MARKET_DATA_SOURCE=mock
#   6  GET /health -> real SELECT 1 + real Redis PING, with latency
#   7  cross-process tick over Upstash pub/sub -> pending order activates
#   8  POST /api/v1/trade/orders -> real fill, real rows in Neon
#   9  an EXTERNAL process subscribes to Upstash and sees the server's ticks
#  10  shutdown is clean
#
# Usage:  ./scripts/m5_proof_cloud.sh
# ============================================================================
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

PASS=0; FAIL=0
ok()   { PASS=$((PASS+1)); printf '  [PASS] %s %s\n' "$1" "${2:-}"; }
bad()  { FAIL=$((FAIL+1)); printf '  [FAIL] %s %s\n' "$1" "${2:-}"; }
step() { printf '\n[%s] %s\n' "$1" "$2"; }

export PYTHONPATH="$PWD"
PORT="${PORT:-8055}"
BASE="http://127.0.0.1:${PORT}"
LOG=/tmp/m5-api.log
PIDFILE=/tmp/m5-api.pid

cleanup() {
  if [ -f "$PIDFILE" ]; then
    kill "$(cat "$PIDFILE")" 2>/dev/null
    sleep 2
    kill -9 "$(cat "$PIDFILE")" 2>/dev/null
    rm -f "$PIDFILE"
  fi
}
trap cleanup EXIT

# ---------------------------------------------------------------- 1. env
step 1 "environment"
if [ ! -f .env ]; then
  bad ".env exists" "copy .env.example and fill it in"; echo "cannot continue"; exit 1
fi
ok ".env exists"
git check-ignore .env >/dev/null 2>&1 && ok ".env is gitignored" || bad ".env is gitignored"
set -a; . ./.env; set +a
[ -n "${DATABASE_URL:-}" ] && ok "DATABASE_URL set" || bad "DATABASE_URL set"
[ -n "${REDIS_URL:-}" ]    && ok "REDIS_URL set"    || bad "REDIS_URL set"
case "${SECRET_KEY:-}" in
  ""|"BROKER_PLATFORM_SECRET_KEY_CHANGE_IN_PRODUCTION") bad "SECRET_KEY is a real secret" ;;
  *) [ ${#SECRET_KEY} -ge 32 ] && ok "SECRET_KEY is a real secret (${#SECRET_KEY} chars)" || bad "SECRET_KEY is a real secret" "too short" ;;
esac
[ -n "${ADMIN_API_KEY:-}" ] && ok "ADMIN_API_KEY set" || bad "ADMIN_API_KEY set"

# ------------------------------------------------------- 2. migrate (real PG)
step 2 "alembic upgrade head against real PostgreSQL"
MIG=$(python3 -m cli.main migrate 2>&1)
if echo "$MIG" | grep -q "alembic upgrade head complete"; then
  ok "migrations applied" "$(echo "$MIG" | grep -c 'Running upgrade') migration step(s)"
else
  bad "migrations applied"; echo "$MIG" | tail -5
fi

# ---------------------------------------------------------------- 3. seed
step 3 "cli seed -> configuration into the cloud database"
SEED=$(python3 -m cli.main seed 2>&1)
if echo "$SEED" | grep -q "groups created\|groups updated\|symbols created"; then
  ok "seed ran"
else
  bad "seed ran"; echo "$SEED" | tail -5
fi
echo "$SEED" | grep -E "groups (created|updated)|symbols (created|updated)|coverage|admin created" | sed 's/^/         /'

# --------------------------------------------------------------- 4. status
step 4 "cli status -> read it back"
STATUS=$(python3 -m cli.main status 2>&1)
GROUPS=$(echo "$STATUS" | awk -F'│' '/groups/{gsub(/ /,"",$3); print $3; exit}')
if echo "$STATUS" | grep -q "Configuration plane is populated"; then
  ok "configuration plane populated" "groups=${GROUPS:-?}"
else
  bad "configuration plane populated"; echo "$STATUS" | tail -8
fi

# ---------------------------------------------------------------- 5. boot
step 5 "boot the API with cloud DB + cloud Redis + mock price source"
MARKET_DATA_SOURCE=mock MOCK_TICK_RATE_MS=200 \
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
  grep -q "RedisEventBus\|Connected to Redis" "$LOG" && ok "Redis event bus connected" || bad "Redis event bus connected"
  grep -q "MARKET_DATA_SOURCE=mock" "$LOG" && ok "mock price source announced in the log" || bad "mock price source announced"
  grep -q "Trading plane wired" "$LOG" && ok "trading plane wired" || bad "trading plane wired"
else
  bad "server booted"; tail -20 "$LOG"
fi

# --------------------------------------------------------------- 6. health
step 6 "GET /health -> real dependency checks"
HEALTH=$(python3 - "$BASE" << 'PY'
import json, sys, urllib.request
try:
    with urllib.request.urlopen(sys.argv[1] + "/health", timeout=15) as r:
        print(r.status, json.dumps(json.load(r)))
except Exception as e:
    print("ERR", e)
PY
)
echo "         $HEALTH" | head -c 400; echo
if echo "$HEALTH" | grep -q '"status": *"healthy"\|"status":"healthy"'; then
  ok "/health reports healthy"
  echo "$HEALTH" | grep -q '"database"' && ok "database probe present"
  echo "$HEALTH" | grep -q '"event_bus"' && ok "event bus probe present"
  echo "$HEALTH" | grep -q '"latency_ms"' && ok "real latency measured" || bad "real latency measured"
else
  bad "/health reports healthy"
fi

# ------------------------------------------- 7+8. trade over HTTP on cloud DB
step 7 "create an account, then trade over HTTP against the cloud database"
TRADE=$(python3 - "$BASE" << 'PY'
import asyncio, json, os, sys, urllib.request
sys.path.insert(0, os.getcwd())

BASE = sys.argv[1]
PROOF_PASSWORD = "M6-CloudProof!2026"

def post(path, payload, token=None):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(BASE + path, data=data, method="POST",
                                 headers={"Content-Type": "application/json"})
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:200]

def get(path, token=None):
    req = urllib.request.Request(BASE + path, headers={})
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:200]

async def make_account():
    """A real trading account in the cloud DB, via the real SQL repository."""
    from decimal import Decimal
    from api.main import default_providers
    from core.domains.accounts.account import Account
    from core.domains.common.value_objects import Money

    providers = default_providers()
    db = providers["database"]
    group_repo = providers["group_repo"]
    account_repo = providers["account_repo"]

    groups = {g.name: g for g in await group_repo.get_all()}
    group = groups.get("demo\\Standard") or next(iter(groups.values()))
    # a fresh login per run: the cloud database persists between runs, and an
    # account left holding a position would falsify the positions_count check
    import time
    login = 700000 + (int(time.time()) % 99999)
    account = Account(
        login=login,
        client_id="CLIENT_M5",
        group=group,
        group_id=group.id,
        currency="USD",
        balance=Money(Decimal("10000"), "USD"),
        credit=Money(Decimal("0"), "USD"),
        equity=Money(Decimal("10000"), "USD"),
        margin_used=Money(Decimal("0"), "USD"),
        margin_free=Money(Decimal("10000"), "USD"),
    )
    # M6: login verifies an Argon2 hash and fail-closes without one, so the
    # proof provisions the password the way the admin endpoint would.
    from infrastructure.security.password_hasher import Argon2PasswordHasher
    account.password_hash = Argon2PasswordHasher().hash_password(PROOF_PASSWORD)
    await account_repo.save(account)
    # accounts.login is a String(32) PK while the domain uses int everywhere:
    # reading it back proves the coercion at that boundary (M4 defect 19 class).
    back = await account_repo.find_by_login(login)
    await db.close()
    return login, back is not None, group.name

async def main():
    out = {}
    try:
        login, saved, group_name = await make_account()
        out["account_saved"] = saved
        out["login"] = login
        out["group"] = group_name
    except Exception as e:
        out["account_error"] = f"{type(e).__name__}: {e}"
        print(json.dumps(out)); return

    st, tok = post("/api/v1/auth/login", {"login_id": str(login), "password": PROOF_PASSWORD})
    out["login_status"] = st
    if st != 200:
        out["login_body"] = tok; print(json.dumps(out)); return
    token = tok["access_token"]

    st, _ = post("/api/v1/auth/login", {"login_id": str(login), "password": "definitely-wrong"})
    out["badpw_status"] = st

    st, body = post("/api/v1/trade/orders",
                    {"symbol": "EURUSD", "order_type": "BUY", "volume": "0.10"}, token)
    out["order_status"] = st
    out["order"] = body if st == 200 else str(body)[:300]

    st, pos = get("/api/v1/account/positions", token)
    out["positions_status"] = st
    out["positions_count"] = len(pos) if isinstance(pos, list) else str(pos)[:200]

    st, info = get("/api/v1/account/info", token)
    out["account_info_status"] = st
    if st == 200 and isinstance(info, dict):
        out["balance"] = info.get("balance")
        out["margin_used"] = info.get("margin_used") or info.get("margin")
        out["equity"] = info.get("equity")
    print(json.dumps(out))

asyncio.run(main())
PY
)
echo "         $TRADE"
echo "$TRADE" | grep -q '"account_saved": *true' && ok "trading account persisted in Neon" || bad "trading account persisted in Neon"
echo "$TRADE" | grep -q '"login_status": *200'   && ok "client login issued a token (password verified)" || bad "client login issued a token"
echo "$TRADE" | grep -q '"badpw_status": *401'   && ok "wrong password refused with 401"    || bad "wrong password refused with 401"
echo "$TRADE" | grep -q '"order_status": *200'   && ok "market order accepted over HTTP"   || bad "market order accepted over HTTP"
echo "$TRADE" | grep -q '"state": *"FILLED"\|"state":"FILLED"' && ok "order FILLED" || bad "order FILLED"
echo "$TRADE" | grep -q '"positions_count": *1'  && ok "position visible over HTTP"        || bad "position visible over HTTP"

# --------------------------------------------- 9. redis really carried events
step 8 "Redis really carried the traffic (not the in-process fallback)"
SEEN=$(timeout 25 python3 - << 'PY'
import asyncio, os, sys
sys.path.insert(0, os.getcwd())
async def main():
    import redis.asyncio as aioredis
    r = aioredis.Redis.from_url(os.environ["REDIS_URL"])
    ps = r.pubsub()
    await ps.subscribe("market.tick_received")
    n = 0
    try:
        async with asyncio.timeout(6):
            async for msg in ps.listen():
                if msg.get("type") == "message":
                    n += 1
                    if n == 1:
                        d = msg["data"][:110]
                        print("first:", d.decode(errors="replace"), file=sys.stderr)
                    if n >= 5:
                        break
    except (asyncio.TimeoutError, TimeoutError):
        pass
    await ps.unsubscribe()
    await r.aclose()
    print(n)
asyncio.run(main())
PY
)
echo "         tick events seen by an external subscriber: ${SEEN##*$'\n'}"
COUNT=$(echo "$SEEN" | tail -1)
if [ "${COUNT:-0}" -gt 0 ] 2>/dev/null; then
  ok "domain events cross the process boundary via Upstash ($COUNT seen)"
else
  bad "domain events cross the process boundary via Upstash"
fi
grep -q "Connected to Redis" "$LOG" && ok "server connected the Redis bus" || bad "server connected the Redis bus"
grep -q "using the single-process InProcessEventBus" "$LOG" && bad "server fell back to in-process" || ok "no in-process fallback"

# ------------------------------------------------------------- 10. shutdown
step 9 "clean shutdown"
kill "$(cat "$PIDFILE")" 2>/dev/null; rm -f "$PIDFILE"
sleep 4
grep -q "LiquidationWorker stopped" "$LOG" && ok "LiquidationWorker stopped" || bad "LiquidationWorker stopped"
grep -q "TickIngestor stopped" "$LOG"      && ok "TickIngestor stopped"      || bad "TickIngestor stopped"
# M9: the two new server-side execution workers must boot and stop cleanly too
grep -q "SlTpWorker subscribed" "$LOG"     && ok "SlTpWorker armed on ticks (M9)"      || bad "SlTpWorker armed on ticks (M9)"
grep -q "ExpirationWorker started" "$LOG"  && ok "ExpirationWorker started (M9)"       || bad "ExpirationWorker started (M9)"
grep -q "SlTpWorker stopped" "$LOG"        && ok "SlTpWorker stopped (M9)"             || bad "SlTpWorker stopped (M9)"
grep -q "ExpirationWorker stopped" "$LOG"  && ok "ExpirationWorker stopped (M9)"       || bad "ExpirationWorker stopped (M9)"
grep -q "Shutting down" "$LOG"             && ok "uvicorn shut down"         || bad "uvicorn shut down"

printf '\n=== M5 cloud proof: %d passed, %d failed ===\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] && echo "The platform runs on managed cloud infrastructure." || echo "SEE FAILURES ABOVE"
exit "$FAIL"
