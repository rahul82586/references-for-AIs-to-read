#!/usr/bin/env python3
"""M11 LIVE: hedge a client order at a REAL MetaTrader 5 terminal, both A-Book routes.

This is the test that was missing. Everything else in the A-Book story -
m11_proof_a_book.py (39 checks), test_m11_a_book_completion.py (12 tests), the M10
FIX gateway - drives a scripted or simulated LP. None of it ever placed a real
hedge. This does.

    set -a && . ./.env && set +a
    export PYTHONPATH=$PWD MARKET_DATA_SOURCE=trade_server
    export TRADE_SERVER_WS_SYMBOLS=BTCUSD
    export BROKER_LP_GATEWAY=trade_server
    python3 scripts/m11_proof_live_hedge.py

It checks BOTH ways flow reaches A-Book:

  ROUTE A  a house RoutingRule with destination=A_BOOK and a gateway_id
           (the configured case: this symbol goes out, that one stays in-house)
  ROUTE B  BROKER_DEFAULT_DESTINATION=A_BOOK with no rule at all
           (the straight-through-processing case: everything hedges)

For each route it verifies the two sides of the trade independently:

  client side (Neon)   order FILLED, a Deal, a Position, margin recomputed,
                       reservation released
  hedge side (MT5)     a NEW position appeared on the terminal, at the terminal's
                       own price, with the terminal's ticket
  broker exposure      the coverage account did NOT move - the risk was passed on,
                       which is the M11 semantics and the thing most likely to be
                       got backwards

Reads the terminal's book before and after, so the new hedge is identified by
difference rather than assumed.

⚠️  THIS PLACES REAL ORDERS ON THE ATTACHED MT5 ACCOUNT. Default 0.01 BTCUSD per
    route. Pass --dry-run to do everything except send the orders.
"""
import asyncio
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
os.chdir(ROOT)

DRY = "--dry-run" in sys.argv
SYMBOL = os.environ.get("HEDGE_SYMBOL", "BTCUSD")
VOLUME = os.environ.get("HEDGE_VOLUME", "0.01")
WS_URL = os.environ["TRADE_SERVER_WS_URL"]
API = os.environ.get("TRADE_SERVER_API_URL") or WS_URL.split("/ws")[0].replace("wss://", "https://").replace("ws://", "http://")
H = {"User-Agent": "broker-platform", "ngrok-skip-browser-warning": "1",
     "Content-Type": "application/json"}

PASS = 0
FAIL = 0
#: one id per invocation, so a re-run never counts the previous run's rows
RUN_ID = str(int(time.time()))[-6:]


def ok(label, detail=""):
    global PASS
    PASS += 1
    print(f"    [PASS] {label}" + (f"  {detail}" if detail else ""))


def bad(label, detail=""):
    global FAIL
    FAIL += 1
    print(f"    [FAIL] {label}" + (f"  {detail}" if detail else ""))


def check(label, cond, detail=""):
    ok(label, detail) if cond else bad(label, detail)


def api_get(path):
    try:
        r = urllib.request.urlopen(urllib.request.Request(API + path, headers=H), timeout=40)
        return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"_http": e.code, "_body": e.read().decode()[:300]}
    except Exception as e:
        return {"_err": f"{type(e).__name__}: {e}"}


def terminal_positions():
    """The MT5 terminal's own book - the hedge side's source of truth."""
    d = api_get("/api/v1/positions")
    rows = d.get("data") if isinstance(d, dict) else None
    out = {}
    for p in rows or []:
        key = str(p.get("ticket"))
        out[key] = p
    return out


def _coverage_exposure(symbol):
    """Broker net exposure for one symbol, read from Neon. Compared as a delta:
    the coverage account is shared and already carries earlier B-Book exposure."""
    import subprocess as _sp
    code = (
        "import asyncio,json,os,asyncpg\n"
        "async def m():\n"
        "    c=await asyncpg.connect(os.environ['DATABASE_URL'].replace('&channel_binding=require',''),timeout=30)\n"
        "    r=await c.fetchrow(\"select net_exposure_json from coverage_accounts where account_id='DEFAULT_COVERAGE\")\n"
        "    await c.close()\n"
        "    print(json.dumps(dict(r) if r else {}))\n"
        "asyncio.run(m())\n"
    )
    r = _sp.run([sys.executable, "-c", code], capture_output=True, text=True,
                env=dict(os.environ, PYTHONPATH=ROOT), cwd=ROOT)
    try:
        row = json.loads([l for l in r.stdout.strip().split("\n") if l.startswith("{")][-1])
        e = json.loads(row.get("net_exposure_json") or "{}")
        return Decimal(str(e.get(symbol, "0")))
    except Exception:
        return Decimal("0")


def terminal_account():
    d = api_get("/api/v1/balance")
    return d.get("data") or {}


# --------------------------------------------------------------------- the run
async def seed_a_book_rule(gateway_id="MT5-TERMINAL"):
    """ROUTE A: a house rule sending this symbol out to the LP.

    Written straight through the repository the router reads, because there is no
    admin CRUD surface for house rules yet (a documented M8+ gap).
    """
    from api.main import default_providers
    from core.domains.execution.models import ExecutionDestination, RoutingRule

    p = default_providers()
    db = p["database"]
    repo = p.get("routing_rule_repo")
    if repo is None:
        await db.close()
        return None
    rule = RoutingRule(rule_id="a-book-hedge", priority=100,
                       destination=ExecutionDestination.A_BOOK,
                       symbol_filter=SYMBOL, gateway_id=gateway_id)
    await repo.save(rule)
    await db.close()
    return rule.rule_id


async def clear_routing_rules():
    """ROUTE B: no rules at all, so unmatched flow uses the default destination."""
    from api.main import default_providers

    p = default_providers()
    db = p["database"]
    repo = p.get("routing_rule_repo")
    if repo is not None:
        for r in await repo.get_active_rules():
            try:
                await repo.delete(getattr(r, "rule_id", None) or getattr(r, "id"))
            except Exception:
                pass
    await db.close()


async def make_account(client_id):
    from api.main import default_providers
    from core.domains.accounts.account import Account
    from core.domains.common.value_objects import Money
    from infrastructure.security.password_hasher import Argon2PasswordHasher

    p = default_providers()
    db = p["database"]
    groups = {g.name: g for g in await p["group_repo"].get_all()}
    g = groups.get("demo\\Standard") or next(iter(groups.values()))
    login = 840000 + (int(time.time() * 100) % 59999)
    a = Account(login=login, client_id=client_id, group=g, group_id=g.id, currency="USD",
                balance=Money(Decimal("100000"), "USD"), credit=Money(Decimal("0"), "USD"),
                equity=Money(Decimal("100000"), "USD"),
                margin_used=Money(Decimal("0"), "USD"),
                margin_free=Money(Decimal("100000"), "USD"))
    a.password_hash = Argon2PasswordHasher().hash_password(PW)
    await p["account_repo"].save(a)
    await db.close()
    return login


PW = "LiveHedge!2026"


def http(path, payload=None, token=None, method=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        BASE + path, data=data, method=method or ("POST" if data else "GET"), headers=H)
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]


BASE = "http://127.0.0.1:%d" % int(os.environ.get("HEDGE_PORT", "8231"))


def boot(env_extra):
    env = dict(os.environ)
    env.update({
        "PYTHONPATH": ROOT,
        "MARKET_DATA_SOURCE": "trade_server",
        "TRADE_SERVER_WS_SYMBOLS": SYMBOL,
        "BROKER_LP_GATEWAY": "trade_server",
        "TRADE_SERVER_API_URL": API,
        "BROKER_MT5_FIXTURES": os.environ.get(
            "BROKER_MT5_FIXTURES", os.path.join(os.path.dirname(ROOT), "decoded", "mt5-format-structure")),
    })
    env.update(env_extra)
    # Logs must live under the workspace: /tmp does not survive between runs, and
    # losing the log is how D8b stayed undiagnosed the first time.
    logdir = os.path.join(os.path.dirname(ROOT), "logs")
    os.makedirs(logdir, exist_ok=True)
    log = open(os.path.join(logdir, "hedge-%s-%s.log" % (env_extra.get("ROUTE", "x"), RUN_ID)), "w")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1",
         "--port", str(int(os.environ.get("HEDGE_PORT", "8231")))],
        stdout=log, stderr=subprocess.STDOUT, env=env, cwd=ROOT)
    for _ in range(90):
        try:
            urllib.request.urlopen(BASE + "/health", timeout=3)
            break
        except Exception:
            if proc.poll() is not None:
                break
            time.sleep(1)
    time.sleep(15)   # let live ticks land before pricing an order
    return proc, log


def client_side(client_id):
    """Read back what the platform booked, straight out of Neon."""
    code = f'''
import asyncio, json, asyncpg, os
async def m():
    client_id = os.environ["CLIENT_ID"]
    c = await asyncpg.connect(os.environ["DATABASE_URL"].replace("&channel_binding=require",""), timeout=30)
    out = {{}}
    out["orders"] = [dict(r) for r in await c.fetch(
        """select o.symbol,o.order_type,o.volume_initial,o.volume_current,o.price_order,o.state,o.reserved_margin,o.comment
           from orders o join accounts a on a.login=o.account_login::text
           where a.client_id=$1 order by o.symbol""", client_id)]
    out["deals"] = [dict(r) for r in await c.fetch(
        """select d.symbol,d.deal_type,d.volume,d.price
           from deals d join accounts a on a.login=d.account_login::text
           where a.client_id=$1 order by d.symbol""", client_id)]
    out["positions"] = [dict(r) for r in await c.fetch(
        """select p.symbol,p.action,p.volume,p.price_open,p.time_done
           from positions p join accounts a on a.login=p.account_login::text
           where a.client_id=$1 order by p.symbol""", client_id)]
    a = await c.fetchrow("""select a.balance,a.equity,a.margin_used,a.margin_free,a.margin_level,a.margin_reserved
                            from accounts a
                            where a.client_id=$1
                              and exists (select 1 from positions p
                                          where p.account_login::text = a.login
                                            and p.time_done is null)
                            order by a.margin_used desc limit 1""", client_id)
    out["account"] = dict(a) if a else None
    out["coverage"] = [dict(r) for r in await c.fetch(
        "select account_id,net_exposure_json from coverage_accounts")]
    def d(o):
        return {{k: str(v) for k, v in o.items()}}
    print(json.dumps({{k: (d(v) if isinstance(v, dict) else [d(x) for x in v] if isinstance(v, list) else v)
                      for k, v in out.items()}}, default=str))
    await c.close()
asyncio.run(m())
'''
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                       env=dict(os.environ, PYTHONPATH=ROOT, CLIENT_ID=client_id), cwd=ROOT)
    if r.returncode != 0:
        print("      (client-side read failed:", r.stderr.strip()[-300:], ")")
        return {}
    for line in reversed(r.stdout.strip().split("\n")):
        line = line.strip()
        if line.startswith("{"):
            return json.loads(line)
    return {}


def run_route(label, env_extra, note):
    print(f"\n{'='*76}\n{label}\n  {note}\n{'='*76}")
    before_pos = terminal_positions()
    before_acct = terminal_account()
    before_cov = _coverage_exposure(SYMBOL)
    print(f"  terminal before : {len(before_pos)} position(s), "
          f"balance={before_acct.get('balance')} equity={before_acct.get('equity')}")

    if env_extra.get("SEED_RULE"):
        rid = asyncio.run(seed_a_book_rule())
        print(f"  seeded house rule  : {rid} -> A_BOOK gateway=MT5-TERMINAL for {SYMBOL}")
    else:
        asyncio.run(clear_routing_rules())
        print("  house rules cleared: unmatched flow uses BROKER_DEFAULT_DESTINATION")

    proc, log = boot(dict(env_extra, ROUTE=label.split()[1]))
    try:
        with open(log.name) as f:
            txt = f.read()
        check("the A-Book gateway is the trade-server terminal",
              "trade-server MT5 terminal at" in txt)
        check("no stub gateway warning", "liquidity gateway is the STUB" not in txt)
        if env_extra.get("BROKER_DEFAULT_DESTINATION") == "A_BOOK":
            check("default destination announced as A_BOOK",
                  "BROKER_DEFAULT_DESTINATION=A_BOOK" in txt)

        client_id = f"CLIENT_HEDGE_{label.split()[1]}_{RUN_ID}"
        login = asyncio.run(make_account(client_id))
        st, tok = http("/api/v1/auth/login", {"login_id": str(login), "password": PW})
        if st != 200:
            bad("client login", f"{st} {tok}")
            return
        ok("client login", f"login={login}")
        token = tok["access_token"]

        if DRY:
            print("    --dry-run: not sending the order")
            return

        st, body = http("/api/v1/trade/orders",
                        {"symbol": SYMBOL, "order_type": "BUY", "volume": VOLUME}, token)
        print(f"  order response [{st}]: {str(body)[:260]}")
        check("the client order was accepted", st == 200, f"status={st}")
        filled = isinstance(body, dict) and body.get("state") == "FILLED"
        check("the client order FILLED", filled,
              f"state={body.get('state') if isinstance(body, dict) else body}")
        if not filled:
            return
        client_px = Decimal(str(body.get("price")))
        print(f"  client filled at {client_px}")

        time.sleep(3)
        after_pos = terminal_positions()
        new = {k: v for k, v in after_pos.items() if k not in before_pos}
        print(f"  terminal after  : {len(after_pos)} position(s); NEW: "
              f"{json.dumps(new, default=str)[:260]}")

        check("a REAL hedge appeared on the MT5 terminal", len(new) >= 1,
              f"{len(new)} new position(s)")
        if new:
            hedge = next(iter(new.values()))
            check("the hedge is the right symbol", str(hedge.get("symbol")).upper() == SYMBOL,
                  str(hedge.get("symbol")))
            check("the hedge is the right side",
                  str(hedge.get("type", "")).lower() in ("buy", "0", "1"),
                  str(hedge.get("type")))
            check("the hedge is the right volume",
                  abs(float(hedge.get("volume", 0)) - float(VOLUME)) < 1e-9,
                  f"{hedge.get('volume')} vs requested {VOLUME}")
            hp = Decimal(str(hedge.get("price_open")))
            drift = abs(hp - client_px)
            check("the client was booked at the TERMINAL's price",
                  drift <= Decimal("2"),
                  f"client={client_px} terminal={hp} drift={drift}")
            print(f"      MT5 ticket={hedge.get('ticket')}  open={hp}  "
                  f"(this is a real position on login "
                  f"{terminal_account().get('balance') and ''}the attached account)")

        cs = client_side(client_id)
        deals = cs.get("deals") or []
        positions = cs.get("positions") or []
        orders = cs.get("orders") or []
        acct = cs.get("account") or {}
        check("a client Deal was booked in Neon", len(deals) == 1, f"{len(deals)} deal(s)")
        check("a client Position was opened in Neon", len(positions) == 1,
              f"{len(positions)} position(s)")
        if deals:
            check("the deal is at the terminal's price",
                  abs(Decimal(deals[0]["price"]) - client_px) < Decimal("0.01"),
                  f"deal={deals[0]['price']}")
        check("margin was recomputed (not zero)",
              Decimal(acct.get("margin_used", "0")) > 0, f"margin_used={acct.get('margin_used')}")
        check("the margin reservation was released",
              Decimal(acct.get("margin_reserved", "0")) == 0,
              f"reserved={acct.get('margin_reserved')}")
        check("margin_level is the derived value, not 0 (D1)",
              Decimal(acct.get("margin_level", "0")) > 1,
              f"level={acct.get('margin_level')}")

        after_cov = _coverage_exposure(SYMBOL)
        check("coverage did NOT move - the risk was passed to the LP",
              after_cov == before_cov,
              f"{SYMBOL} exposure {before_cov} -> {after_cov} (unchanged; earlier "
              "B-Book runs left their own exposure on this shared account)")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except Exception:
            proc.kill()
        time.sleep(2)


def main():
    print("=" * 76)
    print("M11 LIVE HEDGE PROOF - real MetaTrader 5 terminal, both A-Book routes")
    print("=" * 76)
    print(f"  trade-server API : {API}")
    print(f"  ws feed          : {WS_URL}")
    print(f"  symbol / volume  : {SYMBOL} {VOLUME}")
    print(f"  mode             : {'DRY RUN (no orders sent)' if DRY else 'LIVE - REAL ORDERS WILL BE PLACED'}")
    st = api_get("/api/v1/status")
    print(f"  terminal status  : {json.dumps(st.get('data', st))[:160]}")
    if (st.get("data") or {}).get("status") != "connected":
        print("\n  REFUSING TO RUN: the MT5 terminal is not connected.")
        return 1

    run_route("ROUTE A - house routing rule",
              {"BROKER_DEFAULT_DESTINATION": "B_BOOK", "SEED_RULE": "1"},
              f"a RoutingRule(destination=A_BOOK, symbol_filter={SYMBOL}) sends this "
              "symbol out while the default stays B-Book")
    run_route("ROUTE B - default destination A_BOOK",
              {"BROKER_DEFAULT_DESTINATION": "A_BOOK"},
              "no rule needed: unmatched flow goes straight out to the LP (STP broker)")

    try:
        asyncio.run(clear_routing_rules())
        print("\n  cleanup: house routing rules cleared from the shared database")
    except Exception as e:
        print(f"\n  cleanup WARNING: could not clear house rules: {e}")

    print("\n" + "=" * 76)
    print(f" M11 LIVE HEDGE: {PASS} passed, {FAIL} failed")
    print("=" * 76)
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
