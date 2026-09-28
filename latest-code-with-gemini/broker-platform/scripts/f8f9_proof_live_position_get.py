#!/usr/bin/env python3
"""F8/F9 LIVE PROOF - PositionGet against the real Neon book (READ-ONLY).

The docs measured `[]` + `ticket=0` for the WHOLE book on live data; the unit
tests pin the HTTP contract on doubles. This is the definitive check: bind the
real SqlPositionRepository to Neon and drive the REAL route coroutine
(api.routers.manager.main.position_get) with the REAL handler and serializer.

Why not TestClient here: starlette's TestClient runs the app in a portal
thread with its OWN event loop, while asyncpg binds every connection to the
loop that created it - cross-loop use dies with "attached to a different
loop" and the route's honest 500 would hide it. One loop, real route function,
real repository: the same code path minus the ASGI transport (which the 19
HTTP-level unit tests already cover).

Usage:  DATABASE_URL=... python3 scripts/f8f9_proof_live_position_get.py
Exit 0 = green. Performs SELECTs only.

D17-safe: every path resolved at runtime; no sandbox literals.
"""
import asyncio
import os
import re
import secrets
import sys
from pathlib import Path

BP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BP))

PASSED = 0
FAILED = 0


def check(ok: bool, label: str, detail: str = "") -> None:
    global PASSED, FAILED
    if ok:
        PASSED += 1
        print(f"  [PASS] {label}" + (f"  ({detail})" if detail else ""))
    else:
        FAILED += 1
        print(f"  [FAIL] {label}" + (f"  ({detail})" if detail else ""))


async def main() -> int:
    db_url = os.environ.get("DATABASE_URL", "")
    if not db_url:
        print("DATABASE_URL not set - nothing to prove against.")
        return 2
    # asyncpg wants ssl= not sslmode= (session-6 lesson)
    pg_url = re.sub(r"[?&]sslmode=require", "", db_url)
    pg_url = re.sub(r"[?&]channel_binding=require", "", pg_url)
    sqlalchemy_url = pg_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    os.environ.setdefault("SECRET_KEY", secrets.token_hex(32))
    os.environ.setdefault("ADMIN_API_KEY", secrets.token_hex(24))

    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from infrastructure.persistence.repositories.position_repository import SqlPositionRepository

    engine = create_async_engine(sqlalchemy_url, pool_pre_ping=True)
    SessionFactory = async_sessionmaker(engine, expire_on_commit=False)
    repo = SqlPositionRepository(session_factory=SessionFactory)

    # ---- ground truth straight from SQL (read-only) ----
    async with SessionFactory() as sess:
        total_open = (await sess.execute(
            text("select count(*) from positions where time_done is null"))).scalar()
        null_price = (await sess.execute(
            text("select count(*) from positions where time_done is null "
                 "and price_current is null"))).scalar()
        with_ext = (await sess.execute(
            text("select count(*) from positions where time_done is null "
                 "and external_id ~ '^[0-9]+$'"))).scalar()
        per_symbol = (await sess.execute(
            text("select symbol, count(*) c from positions where time_done is null "
                 "group by symbol order by c desc"))).all()
        per_login = (await sess.execute(
            text("select account_login, count(*) c from positions where time_done is null "
                 "group by account_login order by c desc"))).all()

    print(f"live book: {total_open} open positions, {null_price} with NULL price_current, "
          f"{with_ext} with a numeric external_id")
    print("== driving the real route coroutine, one event loop ==")

    from api.routers.manager.main import position_get
    from application.queries.get_positions import GetManagerPositionsQueryHandler

    handler = GetManagerPositionsQueryHandler(position_repo=repo)
    manager = object()  # the route never reads the principal; auth is the dependency's job

    body = await position_get(login=None, symbol=None, manager=manager, handler=handler)
    infos = [b.model_dump(by_alias=False) for b in body]
    check(len(infos) == total_open, f"returns the WHOLE open book: {len(infos)} rows",
          f"SQL says {total_open}; pre-F8 this endpoint served []")

    tickets = [p["ticket"] for p in infos]
    numeric = [t for t in tickets if isinstance(t, int)]
    check(len(numeric) == with_ext, f"real venue tickets on {len(numeric)} rows",
          f"numeric external_id count {with_ext}; F9 served 0 for all")
    check(not any(t == 0 for t in tickets), "no fabricated ticket=0 anywhere")
    nulls = sum(1 for p in infos if p["price_current"] is None)
    check(nulls == null_price, f"price_current NULL stays null on {nulls} rows",
          f"SQL says {null_price} - honest None, never 0, never price_open")
    check(all(p["position_id"] for p in infos), "every row carries its canonical position_id")
    check(len({p["position_id"] for p in infos}) == len(infos), "position_ids are unique row keys")

    if per_symbol:
        sym, cnt = per_symbol[0][0], per_symbol[0][1]
        rows = await position_get(login=None, symbol=sym, manager=manager, handler=handler)
        check(len(rows) == cnt, f"?symbol={sym} filter matches SQL", f"{len(rows)} vs {cnt}")
    if per_login:
        login, cnt = int(per_login[0][0]), per_login[0][1]
        rows = await position_get(login=login, symbol=None, manager=manager, handler=handler)
        check(len(rows) == cnt and all(int(r.login) == login for r in rows),
              f"?login={login} filter is account-scoped", f"{len(rows)} vs {cnt}")
    check(len({int(p["login"]) for p in infos}) == len(per_login), "cross-account read",
          f"{len(per_login)} distinct logins in the book")

    # honest failure, live: a poisoned handler must produce the route's 500 path
    class _Poison:
        async def handle(self, q):
            raise RuntimeError("simulated failure")
    from fastapi import HTTPException
    try:
        await position_get(login=None, symbol=None, manager=manager, handler=_Poison())
        check(False, "route raises HTTPException on handler failure (not [])")
    except HTTPException as e:
        check(e.status_code == 500, "route raises HTTPException 500 on handler failure (not [])")

    await engine.dispose()
    print(f"\nF8/F9 live proof: {PASSED} passed, {FAILED} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
