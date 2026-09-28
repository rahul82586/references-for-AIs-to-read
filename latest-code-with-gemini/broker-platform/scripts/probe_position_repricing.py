#!/usr/bin/env python3
"""Probe: does an OPEN position get repriced by the tick pipeline?

Not a milestone proof - a diagnostic. The D12 cloud proof found that a market
close had to fall back to the position's open price because `price_current` had
never been set, even though BTCUSD ticks were demonstrably arriving (the fill
priced without a STALE refusal, and the bus logged a tick every ~0.6s).

So: open a position against a running server, then watch the row for 30s.

    python3 scripts/probe_position_repricing.py BASE SYMBOL VOLUME
"""
from __future__ import annotations

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

PW = "Probe!2026"


def call(base, path, payload=None, token=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(base + path, data=data,
                                 method="POST" if data else "GET",
                                 headers={"Content-Type": "application/json"})
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            b = r.read()
            return r.status, (json.loads(b) if b else None)
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
    login = 850000 + (int(time.time()) % 49999)
    a = Account(login=login, client_id="CLIENT_PROBE", group=g, group_id=g.id,
                currency="USD", balance=Money(Decimal("100000"), "USD"),
                credit=Money(Decimal("0"), "USD"), equity=Money(Decimal("100000"), "USD"),
                margin_used=Money(Decimal("0"), "USD"),
                margin_free=Money(Decimal("100000"), "USD"))
    a.password_hash = Argon2PasswordHasher().hash_password(PW)
    await p["account_repo"].save(a)
    await db.close()
    return login


async def row(login, position_id):
    import asyncpg
    url = os.environ["DATABASE_URL"].replace("postgresql+asyncpg://", "postgresql://")
    url = url.replace("&channel_binding=require", "")
    c = await asyncpg.connect(url, ssl="require", timeout=30)
    try:
        r = await c.fetchrow(
            "select volume, price_open, price_current, profit, time_update from positions "
            "where position_id = $1", position_id)
        a = await c.fetchrow(
            "select equity, profit, margin_used, last_valuation_at from accounts where login = $1",
            str(login))
    finally:
        await c.close()
    return dict(r) if r else None, dict(a) if a else None


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8077"
    symbol = (sys.argv[2] if len(sys.argv) > 2 else "BTCUSD").upper()
    volume = sys.argv[3] if len(sys.argv) > 3 else "0.01"
    seconds = int(sys.argv[4] if len(sys.argv) > 4 else "30")

    login = asyncio.run(make_account())
    st, tok = call(base, "/api/v1/auth/login", {"login_id": str(login), "password": PW})
    assert st == 200, (st, tok)
    token = tok["access_token"]
    print(f"account {login}")

    st, order = call(base, "/api/v1/trade/orders",
                     {"symbol": symbol, "order_type": "BUY", "volume": volume}, token)
    print(f"order {st}: {json.dumps(order, default=str)[:220]}")
    assert st == 200, order
    st, positions = call(base, "/api/v1/account/positions", token=token)
    pid = [p for p in positions if p["symbol"] == symbol][0]["position_id"]
    print(f"position {pid}\n")

    seen = set()
    end = time.time() + seconds
    while time.time() < end:
        pos, acct = asyncio.run(row(login, pid))
        st, live = call(base, "/api/v1/account/positions", token=token)
        lpnl = live[0]["unrealized_pnl"] if st == 200 and live else "?"
        key = (str(pos["price_current"]), str(pos["profit"]))
        mark = "  <-- CHANGED" if key not in seen else ""
        seen.add(key)
        print(f"  row price_current={pos['price_current']} profit={pos['profit']} "
              f"time_update={pos['time_update']} | account profit={acct['profit']} "
              f"equity={acct['equity']} last_valuation_at={acct['last_valuation_at']} "
              f"| /positions unrealized_pnl={lpnl}{mark}")
        time.sleep(5)

    changed = len(seen) > 1
    print(f"\n=== the stored position row {'WAS' if changed else 'was NOT'} repriced by "
          f"the tick pipeline over {seconds}s ({len(seen)} distinct state(s)) ===")
    print("cleanup: close it")
    st, c = call(base, f"/api/v1/trade/positions/{pid}/close", {}, token)
    print(f"  close {st}: {json.dumps(c, default=str)[:260]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
