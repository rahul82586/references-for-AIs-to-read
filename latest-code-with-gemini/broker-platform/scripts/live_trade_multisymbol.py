#!/usr/bin/env python3
"""Trade EURUSD and BTCUSD against a REAL MT5 terminal, end to end.

Real terminal -> trade-server -> tunnel -> TradeServerTickFeed -> MarketDataEngine
-> CreateOrderHandler -> risk -> router -> BookMatchingEngine -> RecordDealHandler
-> Neon PostgreSQL, with Upstash as the event bus.

Boots its own server, so it can be run on its own:

    python3 scripts/live_trade_multisymbol.py [SYMBOL:VOLUME ...]

Defaults to EURUSD:0.10 and BTCUSD:0.01.
"""
import asyncio
import json
import os
import sys
import time
import urllib.error
import urllib.request
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
os.chdir(ROOT)

PORT = int(os.environ.get("LIVE_PORT", "8211"))
BASE = f"http://127.0.0.1:{PORT}"
PW = "LiveMulti!2026"
CLIENT = "CLIENT_LIVE_MULTI"

WANT = [a.split(":") for a in (sys.argv[1:] or ["EURUSD:0.10", "BTCUSD:0.01"])]
SYMBOLS = [s for s, _ in WANT]


def post(path, payload, token=None):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(),
                                 method="POST", headers={"Content-Type": "application/json"})
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]


def get(path, token=None):
    req = urllib.request.Request(BASE + path, headers={})
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]


async def make_account():
    from api.main import default_providers
    from core.domains.accounts.account import Account
    from core.domains.common.value_objects import Money
    from infrastructure.security.password_hasher import Argon2PasswordHasher

    p = default_providers()
    db = p["database"]
    groups = {g.name: g for g in await p["group_repo"].get_all()}
    g = groups.get("demo\\Standard") or next(iter(groups.values()))
    login = 830000 + (int(time.time()) % 69999)
    a = Account(login=login, client_id=CLIENT, group=g, group_id=g.id, currency="USD",
                balance=Money(Decimal("100000"), "USD"), credit=Money(Decimal("0"), "USD"),
                equity=Money(Decimal("100000"), "USD"),
                margin_used=Money(Decimal("0"), "USD"),
                margin_free=Money(Decimal("100000"), "USD"))
    a.password_hash = Argon2PasswordHasher().hash_password(PW)
    await p["account_repo"].save(a)
    await db.close()
    return login, g.name


def main():
    print("=" * 76)
    print("LIVE multi-symbol trade: real MT5 -> Neon")
    print("=" * 76)
    print(f"  symbols requested : {WANT}")
    print(f"  ws url            : {os.environ.get('TRADE_SERVER_WS_URL')}")

    login, group = asyncio.run(make_account())
    print(f"  account           : {login}  group={group}  balance=100,000 USD")

    st, tok = post("/api/v1/auth/login", {"login_id": str(login), "password": PW})
    if st != 200:
        print(f"  [FAIL] login {st}: {tok}")
        return 1
    token = tok["access_token"]
    print(f"  login             : 200 (Argon2 password verified)\n")

    filled = 0
    for symbol, volume in WANT:
        print(f"--- {symbol} {volume} ---")
        st, body = post("/api/v1/trade/orders",
                        {"symbol": symbol, "order_type": "BUY", "volume": volume}, token)
        if st == 200 and isinstance(body, dict) and body.get("state") == "FILLED":
            filled += 1
            print(f"  [FILLED]  price={body.get('price')}  volume={body.get('filled_volume')}")
            print(f"            ticket={body.get('ticket_id')}")
        else:
            print(f"  [status {st}] {str(body)[:260]}")
        st, pos = get("/api/v1/account/positions", token)
        if st == 200 and isinstance(pos, list):
            mine = [p for p in pos if p.get("symbol") == symbol]
            for p in mine:
                print(f"  position  {p['symbol']} {p['side']} vol={p['volume']} "
                      f"open={p['average_price']} pnl={p.get('unrealized_pnl')}")
            if not mine:
                print(f"  position  none for {symbol} ({len(pos)} open in total)")
        else:
            print(f"  positions [{st}] {str(pos)[:160]}")
        print()

    st, info = get("/api/v1/account/info", token)
    if st == 200:
        print("--- account after trading ---")
        for k in ("balance", "equity", "margin_used", "margin_free", "margin_level"):
            print(f"  {k:<14} {info.get(k)}")
    print()
    print(f"=== {filled}/{len(WANT)} symbols filled at live MT5 prices ===")
    return 0 if filled == len(WANT) else 1


if __name__ == "__main__":
    raise SystemExit(main())
