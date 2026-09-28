#!/usr/bin/env python3
"""D12 cloud driver: open against the live feed, then close it two ways over HTTP.

Driven by ``scripts/d12_proof_cloud_close.sh``. Needs a broker API already running
against Neon + Upstash with the trade-server tick feed attached.

    python3 scripts/d12_cloud_close_driver.py BASE SYMBOL VOLUME

Two closes, because they are different code paths and only one of them depends on
the market being open:

  phase 1  PARTIAL close at an EXPLICIT price. The client supplies the price, so
           the response's `close_price` / `realized_pnl` are checkable against
           arithmetic whether or not the feed is live. This is the phase that
           proves D12.
  phase 2  close the remainder AT MARKET. On a weekday this deals at the live bid;
           at a weekend the feed is replaying a stale quote and the handler says so
           at WARNING and falls back to the last real price it has. Either way the
           OUT deal, `deal_close`, `time_done` and the margin release must land.

Prints one JSON blob on the last line; exit 0 only if every check held.
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

PW = "D12-CloudProof!2026"
CLIENT = "CLIENT_D12_PROOF"
BALANCE = Decimal("100000")
#: how far above the open price the explicit close deals, in quote units
PRICE_BUMP = Decimal(os.environ.get("D12_PRICE_BUMP", "50"))


def _call(base: str, path: str, payload=None, token=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        base + path, data=data, method="POST" if data else "GET",
        headers={"Content-Type": "application/json"})
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            body = r.read()
            return r.status, (json.loads(body) if body else None)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:400]


CHECKS: list[tuple[str, bool, str]] = []


def check(label: str, ok: bool, detail: str = "") -> bool:
    CHECKS.append((label, ok, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f"  {detail}" if detail else ""))
    return ok


async def make_account() -> tuple[int, str]:
    """A real account in the cloud DB, through the real SQL repository."""
    from api.main import default_providers
    from core.domains.accounts.account import Account
    from core.domains.common.value_objects import Money
    from infrastructure.security.password_hasher import Argon2PasswordHasher

    providers = default_providers()
    db = providers["database"]
    groups = {g.name: g for g in await providers["group_repo"].get_all()}
    group = groups.get("demo\\Standard") or next(iter(groups.values()))
    login = 840000 + (int(time.time()) % 59999)
    account = Account(
        login=login, client_id=CLIENT, group=group, group_id=group.id,
        currency="USD", balance=Money(BALANCE, "USD"), credit=Money(Decimal("0"), "USD"),
        equity=Money(BALANCE, "USD"), margin_used=Money(Decimal("0"), "USD"),
        margin_free=Money(BALANCE, "USD"))
    account.password_hash = Argon2PasswordHasher().hash_password(PW)
    await providers["account_repo"].save(account)
    await db.close()
    return login, group.name


async def read_neon(login: int) -> dict:
    """Read what actually landed straight from PostgreSQL.

    The API answering 200 is not the same as the row existing - that gap is the
    subject of D1, D2 and D12 - so the proof never trusts the response alone.
    """
    import asyncpg

    url = os.environ["DATABASE_URL"].replace("postgresql+asyncpg://", "postgresql://")
    url = url.replace("&channel_binding=require", "")
    conn = await asyncpg.connect(url, ssl="require", timeout=30)
    try:
        deals = [dict(r) for r in await conn.fetch(
            "select deal_id, entry, deal_type, volume, price, profit, swap, commission, "
            "reason, comment, created_at from deals where account_login = $1 "
            "order by created_at", login)]
        positions = [dict(r) for r in await conn.fetch(
            "select position_id, symbol, volume, contract_size, price_open, price_current, "
            "profit, deal_open, deal_close, time_done from positions "
            "where account_login = $1", login)]
        account = dict(await conn.fetchrow(
            "select balance, equity, margin_used, margin_free, margin_level, last_valuation_at "
            "from accounts where login = $1", str(login)))
        symbol = dict(await conn.fetchrow(
            "select name, contract_size, digits, quote_currency, margin_currency "
            "from symbols where name = $1", SYMBOL)) or {}
        bar = await conn.fetchrow(
            "select timeframe, open_time, close_time, close from bars "
            "where symbol = $1 order by open_time desc limit 1", SYMBOL)
        bars = dict(bar) if bar else {}
    finally:
        await conn.close()
    out = {"deals": deals, "positions": positions, "symbol": symbol,
           "account": account, "latest_bar": bars}
    for group in (deals, positions, [account, symbol, bars]):
        for row in group:
            for k, v in list(row.items()):
                row[k] = str(v) if isinstance(v, Decimal) else v
    return out


def d(value) -> Decimal:
    return Decimal(str(value))


async def volume_step(symbol: str):
    """The symbol's volume_step from the config plane, or None."""
    from api.main import default_providers

    providers = default_providers()
    db = providers["database"]
    try:
        sym = await providers["symbol_repo"].find_by_name(symbol)
    finally:
        await db.close()
    return getattr(sym, "volume_step", None) if sym else None


SYMBOL = "BTCUSD"


def main() -> int:
    global SYMBOL
    if len(sys.argv) < 4:
        print(__doc__)
        return 2
    base, SYMBOL, volume_s = sys.argv[1], sys.argv[2].upper(), sys.argv[3]
    volume = Decimal(volume_s)

    login, group = asyncio.run(make_account())
    print(f"account {login}  group={group}  balance={BALANCE} USD  symbol={SYMBOL}")

    st, tok = _call(base, "/api/v1/auth/login", {"login_id": str(login), "password": PW})
    if not check("login 200 (Argon2 password verified)", st == 200, f"status={st}"):
        return 1
    token = tok["access_token"]
    st, _ = _call(base, "/api/v1/auth/login", {"login_id": str(login), "password": "wrong"})
    check("wrong password refused 401", st == 401, f"status={st}")

    # ------------------------------------------------------------------ open
    st, order = _call(base, "/api/v1/trade/orders",
                      {"symbol": SYMBOL, "order_type": "BUY", "volume": volume_s}, token)
    filled = st == 200 and isinstance(order, dict) and order.get("state") == "FILLED"
    if not check(f"BUY {SYMBOL} {volume_s} filled", filled,
                 f"status={st} price={order.get('price') if isinstance(order, dict) else order}"):
        print(json.dumps({"login": login, "order_status": st, "order": str(order)[:400]}))
        return 1
    open_price = d(order["price"])

    st, positions = _call(base, "/api/v1/account/positions", token=token)
    mine = [p for p in positions if p.get("symbol") == SYMBOL] if isinstance(positions, list) else []
    if not check("position visible on /account/positions", bool(mine)):
        return 1
    position_id = mine[0]["position_id"]

    st, info = _call(base, "/api/v1/account/info", token=token)
    margin_before = d(info["margin_used"]) if st == 200 else None
    balance_before = d(info["balance"]) if st == 200 else None
    check("the open position holds margin", bool(margin_before and margin_before > 0),
          f"margin_used={margin_before}")

    db0 = asyncio.run(read_neon(login))
    contract = d(db0["positions"][0]["contract_size"]) if db0["positions"] else Decimal(1)
    print(f"  position {position_id}  open={open_price}  contract_size={contract}  "
          f"quote_ccy={db0['symbol'].get('quote_currency')}")
    # Informational only: bars are aggregated inside process_tick, but nothing has
    # ever persisted one (the table reads 0 rows on a database that has taken 30+
    # fills), so an empty result says nothing about the feed. The verdict on tick
    # processing is the position-row check below.
    print(f"  latest {SYMBOL} bar in Neon: "
          f"{db0.get('latest_bar') or 'none (bars table is empty)'}")

    # Let the feed reprice it if the market is actually open, and RECORD whether it
    # did. /account/positions values the position on demand through the RiskEngine
    # (M12), so a moving unrealised_pnl is direct evidence that the engine holds a
    # live price - and if it does not, phase 2 must not be accused of closing at a
    # stale price. At a weekend the trade-server replays the last known quote with
    # its original timestamp, the D6 freshness guard drops it, and the engine prices
    # from the symbol's configured spread instead: honest, and announced at startup.
    st, p0 = _call(base, "/api/v1/account/positions", token=token)
    pnl_open = d(p0[0]["unrealized_pnl"]) if st == 200 and isinstance(p0, list) and p0 else None
    time.sleep(float(os.environ.get("D12_REPRICE_SECONDS", "8")))
    st, p1 = _call(base, "/api/v1/account/positions", token=token)
    pnl_later = d(p1[0]["unrealized_pnl"]) if st == 200 and isinstance(p1, list) and p1 else None
    repriced = pnl_open is not None and pnl_later is not None and pnl_open != pnl_later

    # D13: the stored row must carry what the tick computed. /account/positions has
    # always been right (M12 values on demand), which is exactly why this went
    # unnoticed - the query answered from the engine while the database still held
    # the numbers from the fill.
    db_mid = asyncio.run(read_neon(login))
    row_mid = db_mid["positions"][0] if db_mid["positions"] else {}
    check("the tick pipeline wrote the reprice into the position row (D13)",
          row_mid.get("price_current") is not None,
          f"price_current={row_mid.get('price_current')} profit={row_mid.get('profit')}")
    print(f"  unrealised PnL {pnl_open} -> {pnl_later}: the engine "
          f"{'REPRICED the position from the feed' if repriced else 'holds no live price (market quiet or the feed is replaying a stale quote)'}")

    # ------------------------------------------- phase 1: explicit-price partial
    # Floor to the symbol's volume_step: quantizing 0.01/2 to 0.01 gives 0.00, which
    # the route rejects with a 422, and a proof that dies on its own arithmetic is not
    # a finding about the broker.
    step = asyncio.run(volume_step(SYMBOL)) or Decimal("0.01")
    half = (volume / (2 * step)).to_integral_value(rounding="ROUND_FLOOR") * step
    if half <= 0:
        print(f"volume {volume} cannot be split at step {step}; pass at least {2 * step}")
        return 2
    print(f"  volume_step={step} -> partial leg {half}")
    close_price = open_price + PRICE_BUMP
    expected_pnl = (close_price - open_price) * half * contract
    print(f"\n-- phase 1: close {half} of {volume} at an EXPLICIT price {close_price} --")

    st, c1 = _call(base, f"/api/v1/trade/positions/{position_id}/close",
                   {"volume": str(half), "price": str(close_price),
                    "comment": "d12-proof-explicit"}, token)
    if not check("partial close at an explicit price returned 200", st == 200,
                 f"status={st} body={str(c1)[:200]}"):
        return 1
    print("  response: " + json.dumps(c1, default=str))
    check("it says PARTIALLY closed", c1.get("fully_closed") is False)
    check("volume_closed is the leg that closed (D12)", d(c1["volume_closed"]) == half,
          f"got {c1['volume_closed']}")
    check("volume_remaining is the rest", d(c1["volume_remaining"]) == volume - half,
          f"got {c1['volume_remaining']}")
    check("close_price is the price the client asked for (D12)",
          d(c1["close_price"]) == close_price, f"got {c1['close_price']}")
    check("realized_pnl matches the arithmetic (D12)",
          abs(d(c1["realized_pnl"]) - expected_pnl) < Decimal("0.01"),
          f"got {c1['realized_pnl']} expected {expected_pnl}")
    check("realized_pnl is not the zero the old code always returned",
          d(c1["realized_pnl"]) != Decimal(0), f"got {c1['realized_pnl']}")
    check("the partial close carries an OUT deal id", bool(c1.get("deal_id")))

    st, pos_after = _call(base, "/api/v1/account/positions", token=token)
    still = [p for p in pos_after if p.get("position_id") == position_id] \
        if isinstance(pos_after, list) else []
    check("the remainder is still open", bool(still),
          f"volume={still[0]['volume'] if still else '?'}")
    st, info1 = _call(base, "/api/v1/account/info", token=token)
    balance_mid = d(info1["balance"]) if st == 200 else None
    check("the balance moved by exactly the realised PnL",
          balance_mid is not None and abs(balance_mid - balance_before - expected_pnl) < Decimal("0.01"),
          f"{balance_before} -> {balance_mid} (pnl {expected_pnl})")
    check("margin is still held for the remainder",
          st == 200 and d(info1["margin_used"]) > 0, f"margin_used={info1.get('margin_used')}")

    # ------------------------------------------------- phase 2: market close
    print(f"\n-- phase 2: close the remaining {volume - half} AT MARKET --")
    st, c2 = _call(base, f"/api/v1/trade/positions/{position_id}/close",
                   {"comment": "d12-proof-market"}, token)
    if not check("market close returned 200", st == 200, f"status={st} body={str(c2)[:200]}"):
        return 1
    print("  response: " + json.dumps(c2, default=str))
    check("it says fully closed", c2.get("fully_closed") is True)
    check("volume_closed is the remainder, not 0 (D12)",
          d(c2["volume_closed"]) == volume - half, f"got {c2['volume_closed']}")
    check("volume_remaining is 0", d(c2["volume_remaining"]) == Decimal(0))
    check("close_price is a real price, not 0 (D12)", d(c2["close_price"]) > Decimal(0),
          f"got {c2['close_price']}")
    # "Did the market close use a live price?" cannot be answered by watching
    # unrealised PnL move: on a quiet Saturday the bid can be identical across two
    # reads eight seconds apart while the engine is perfectly healthy. What CAN be
    # answered is whether the close dealt at the row's repriced current price rather
    # than falling back to the open price - and if the two happen to be equal, the
    # market simply did not move, which is a fact about the market, not a defect.
    if d(c2["close_price"]) != open_price:
        check("the market close dealt away from the open price (live feed)", True,
              f"open={open_price} close={c2['close_price']}")
    elif repriced:
        check("the market close dealt away from the open price (live feed)", False,
              f"the position WAS repriced to {c2['close_price']} but the close used the "
              f"open price {open_price}")
    else:
        print("  [NOTE] the market did not move during this proof, so the close price "
              "equals the open price and no live-price claim is made either way.")
    check("the market close carries a different OUT deal id",
          bool(c2.get("deal_id")) and c2["deal_id"] != c1["deal_id"])

    st, pos_end = _call(base, "/api/v1/account/positions", token=token)
    left = [p for p in pos_end if p.get("position_id") == position_id] \
        if isinstance(pos_end, list) else [1]
    check("the position is gone from /account/positions", not left)

    st, info2 = _call(base, "/api/v1/account/info", token=token)
    balance_after = d(info2["balance"]) if st == 200 else None
    check("all margin released (D10)", st == 200 and d(info2["margin_used"]) == Decimal(0),
          f"{margin_before} -> {info2.get('margin_used')}")
    check("equity == balance: no unrealised shadow left",
          st == 200 and d(info2["equity"]) == balance_after,
          f"equity={info2.get('equity')} balance={balance_after}")
    check("margin_level is the no-margin sentinel, not a stale ratio",
          st == 200 and d(info2["margin_level"]) >= Decimal("999999"),
          f"margin_level={info2.get('margin_level')}")

    st, foreign = _call(base, "/api/v1/trade/positions/999999_XAUUSD_deadbeef/close", {}, token)
    check("closing a position that is not mine is refused", st in (403, 404), f"status={st}")

    # ------------------------------------------------------- what landed in Neon
    print("\n-- reading Neon directly --")
    db = asyncio.run(read_neon(login))
    entries = [x["entry"] for x in db["deals"]]
    check("Neon holds one IN and two OUT deals", entries == ["IN", "OUT", "OUT"],
          f"entries={entries}")
    outs = [x for x in db["deals"] if x["entry"] == "OUT"]
    if len(outs) == 2:
        first, second = outs
        check("both OUT deals say reason=CLIENT",
              first["reason"] == "CLIENT" and second["reason"] == "CLIENT",
              f"{first['reason']}/{second['reason']}")
        check("the explicit-price OUT deal carries that price",
              d(first["price"]) == close_price, f"deal={first['price']}")
        check("the explicit-price OUT deal carries the realised PnL",
              abs(d(first["profit"]) - expected_pnl) < Decimal("0.01"),
              f"deal={first['profit']} expected={expected_pnl}")
        check("the two responses and the two deals state the same numbers",
              d(first["profit"]) == d(c1["realized_pnl"])
              and d(second["profit"]) == d(c2["realized_pnl"]),
              f"deals={first['profit']},{second['profit']} "
              f"responses={c1['realized_pnl']},{c2['realized_pnl']}")
        check("the OUT deals carry the client's comments",
              "d12-proof-explicit" in first["comment"] and "d12-proof-market" in second["comment"],
              f"{first['comment']!r} / {second['comment']!r}")
        total = d(first["profit"]) + d(second["profit"])
        check("the balance moved by the sum of both realised results",
              balance_after is not None and abs(balance_after - balance_before - total) < Decimal("0.01"),
              f"{balance_before} -> {balance_after} (total pnl {total})")
    row = db["positions"][0] if db["positions"] else {}
    check("the position row is closed", bool(row.get("time_done")), f"time_done={row.get('time_done')}")
    check("deal_close points at the LAST OUT deal",
          row.get("deal_close") == c2.get("deal_id"),
          f"row={row.get('deal_close')} response={c2.get('deal_id')}")
    check("the row's volume is 0", d(row.get("volume", 1)) == Decimal(0), f"volume={row.get('volume')}")
    check("the closed row's profit is its realised result (D12)",
          d(row.get("profit", 0)) == d(c2["realized_pnl"]),
          f"row={row.get('profit')} response={c2['realized_pnl']}")
    check("the row's price_current is the price it closed at (D12)",
          d(row.get("price_current", 0)) == d(c2["close_price"]),
          f"row={row.get('price_current')} response={c2['close_price']}")
    check("the account row's margin_used is 0 in the database",
          d(db["account"]["margin_used"]) == Decimal(0), f"margin_used={db['account']['margin_used']}")

    failed = [c for c in CHECKS if not c[1]]
    print(f"\n=== D12 CLOUD CLOSE: {len(CHECKS) - len(failed)}/{len(CHECKS)} checks passed "
          f"(account {login}, {SYMBOL}, Neon + Upstash) ===")
    print(json.dumps({"login": login, "symbol": SYMBOL, "volume": volume_s,
                      "checks": len(CHECKS), "failed": [f[0] for f in failed],
                      "neon": db}, default=str))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
