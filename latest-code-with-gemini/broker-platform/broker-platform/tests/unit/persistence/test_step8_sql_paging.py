"""Step 8 at the SQL layer: find_page really pages in the DATABASE.

The HTTP tests pin the wire contract on doubles; these pin the thing the
doubles cannot: WHERE/LIMIT/OFFSET/COUNT pushed into SQL against the real
repositories on SQLite (the same dialect the proofs use).

The two traps, each with a pin:

* **find_all()[:limit]** - every repository's find_all is POISONED here; if
  find_page secretly routes through it, the test explodes.
* **lexicographic login order** - accounts.login is String(32); ORDER BY the
  raw column serves 10, 1000, 885863, 9. The page must come back NUMERIC.

Writes go through the repositories' own save() - the same mappers production
uses - so a column the mapper drops fails here, not in front of the UI.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

T0 = datetime(2026, 9, 13, 10, 0, 0, tzinfo=timezone.utc)


@pytest.fixture()
def db(tmp_path):
    """A real SQLite database with the full schema, rows written via save()."""
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from sqlalchemy.pool import NullPool

    from infrastructure.persistence.database import Base
    import infrastructure.persistence.db_models  # noqa: F401 - registers every table

    # NullPool, NOT StaticPool: the fixture builds the database inside one
    # asyncio.run() and each test runs its own loop. A StaticPool connection is
    # bound to the loop that created it - reusing it across loops dies with
    # "attached to a different loop" (the same trap the live proofs hit).
    # A file-backed SQLite + NullPool gives every loop its own connection.
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path/'step8.db'}", poolclass=NullPool)
    SessionFactory = async_sessionmaker(engine, expire_on_commit=False)

    async def _build():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        from core.domains.accounts.account import Account
        from core.domains.accounts.client import Client
        from core.domains.accounts.enums import AccountType
        from core.domains.accounts.group import Group
        from core.domains.accounts.value_objects import MarginProfile
        from core.domains.common.value_objects import Money, Price, Volume
        from core.domains.identity.models import ManagerAccount, ManagerRole
        from core.domains.identity.rights import ManagerRightsMask, UserRight
        from core.domains.oms.entities.deal import Deal
        from core.domains.oms.entities.order import Order
        from core.domains.oms.entities.position import Position
        from core.domains.oms.enums import DealEntry, DealType, OrderState, OrderType, PositionAction
        from infrastructure.persistence.repositories.account_repository import SqlAccountRepository
        from infrastructure.persistence.repositories.deal_repository import SqlDealRepository
        from infrastructure.persistence.repositories.group_repository import SqlGroupRepository
        from infrastructure.persistence.repositories.manager_repository import (
            SqlClientRepository,
            SqlManagerRepository,
        )
        from infrastructure.persistence.repositories.order_repository import SqlOrderRepository
        from infrastructure.persistence.repositories.position_repository import SqlPositionRepository

        group_repo = SqlGroupRepository(session_factory=SessionFactory)
        demo = Group(name="demo\\Standard", account_type=AccountType.DEMO, server_id=1,
                     currency="USD", currency_digits=2, auth_password_min=8,
                     margin=MarginProfile(leverage_default=100, leverage_max=500))
        real = Group(name="real\\real", account_type=AccountType.REAL, server_id=1,
                     currency="USD", currency_digits=2, auth_password_min=8,
                     margin=MarginProfile(leverage_default=100, leverage_max=500))
        await group_repo.save(demo)
        await group_repo.save(real)

        account_repo = SqlAccountRepository(session_factory=SessionFactory, group_repo=group_repo)
        # 150 accounts; the four hand-placed logins pin NUMERIC ordering
        special = [9, 10, 1000, 885863]
        for i in range(150):
            login = special[i] if i < len(special) else 100000 + i
            grp = demo if i % 2 == 0 else real
            acc = Account(
                login=login, group=grp, group_id=grp.id,
                account_type=grp.account_type, currency="USD",
                balance=Money(Decimal("1000"), "USD"),
                **({"rights": UserRight(0), "is_enabled": False} if i % 50 == 49 else {}),
            )
            await account_repo.save(acc)

        client_repo = SqlClientRepository(session_factory=SessionFactory)
        for i in range(3):
            await client_repo.save(Client(id=f"cl-{i}", client_id=f"KYC-{i}", full_name=f"Client {i}"))

        manager_repo = SqlManagerRepository(session_factory=SessionFactory)
        for login in (1000, 208011):
            await manager_repo.save(ManagerAccount(
                manager_id=str(login), login=str(login), role=ManagerRole.READ_ONLY,
                rights=ManagerRightsMask.empty().grant("RIGHT_ACC_READ"),
                is_active=True, must_change_password=False, allowed_ips=[],
            ))

        deal_repo = SqlDealRepository(session_factory=SessionFactory)
        for i in range(6):
            await deal_repo.save(Deal(
                deal_id=f"deal-{i}", account_login=100000 + i,
                symbol="EURUSD" if i % 2 == 0 else "BTCUSD",
                deal_type=DealType.BUY, entry=DealEntry.IN if i < 4 else DealEntry.OUT,
                volume=Volume(Decimal("0.10")), price=Price(Decimal("1.07961")),
                profit=Money(Decimal("0"), "USD"),
                external_id=str(777000 + i) if i % 2 == 0 else None,
                created_at=T0 + timedelta(minutes=i),
            ))

        order_repo = SqlOrderRepository(session_factory=SessionFactory)
        states = [OrderState.PLACED, OrderState.FILLED, OrderState.REJECTED,
                  OrderState.CANCELLED, OrderState.STARTED]
        for i, st in enumerate(states):
            await order_repo.save(Order(
                ticket_id=f"order-{i}", account_login=100000 + i, symbol="EURUSD",
                order_type=OrderType.BUY, state=st,
                volume_initial=Volume(Decimal("0.10")), volume_current=Volume(Decimal("0.10")),
                # price_order is Optional on the ENTITY (M10) but the COLUMN is
                # NOT NULL and order_to_db dereferences it unconditionally -
                # a latent defect recorded in the M17 report; until migration
                # 010 makes the column honest, an order without a price cannot
                # be stored, so the fixture supplies one like production does.
                price_order=Price(Decimal("1.07961")),
                time_setup=T0 + timedelta(minutes=i),
            ))

        position_repo = SqlPositionRepository(session_factory=SessionFactory)
        for i in range(4):
            p = Position(
                position_id=f"pos-{i}", account_login=100000 + i,
                symbol="EURUSD" if i % 2 == 0 else "BTCUSD",
                action=PositionAction.BUY, external_id=str(529200 + i) if i == 0 else None,
                volume=Volume(Decimal("0.10")), price_open=Price(Decimal("1.07961")),
            )
            if i == 3:
                p.time_done = T0 + timedelta(hours=1)
            await position_repo.save(p)

        return {
            "engine": engine, "session_factory": SessionFactory,
            "account_repo": account_repo, "client_repo": client_repo,
            "manager_repo": manager_repo, "deal_repo": deal_repo,
            "order_repo": order_repo, "position_repo": position_repo,
        }

    world = asyncio.run(_build())

    # POISON find_all on every repository instance: the read plane must never
    # load every row to serve a page.
    for key, repo in world.items():
        if key.endswith("_repo"):
            async def _boom(*a, _k=key, **k):
                raise AssertionError(f"{_k}.find_all() was called - paging must happen in SQL")
            repo.find_all = _boom

    yield world
    asyncio.run(world["engine"].dispose())


def test_account_page_is_sql_level_and_numeric(db):
    async def _run():
        rows, total = await db["account_repo"].find_page(limit=100, offset=0)
        assert total == 150 and len(rows) == 100            # total counts ALL matches, not the page
        logins = [int(a.login) for a in rows]
        assert logins[:3] == [9, 10, 1000]                  # NUMERIC: lexicographic would open '10','1000','100004'
        assert logins == sorted(logins)                     # the whole page is in numeric order
        _, last_total = await db["account_repo"].find_page(limit=1, offset=149)
        assert last_total == 150
        tail, _ = await db["account_repo"].find_page(limit=100, offset=100)
        assert int(tail[-1].login) == 885863                # and 885863 sorts LAST numerically, never after '9'
        rows2, total2 = await db["account_repo"].find_page(limit=100, offset=100)
        assert total2 == 150 and len(rows2) == 50
        assert not ({int(a.login) for a in rows} & {int(a.login) for a in rows2})  # pages do not overlap
    asyncio.run(_run())


def test_account_filters_push_into_sql(db):
    async def _run():
        demo, total = await db["account_repo"].find_page(limit=1000, group_name="demo\\Standard")
        assert total == 75 and len(demo) == 75
        assert all(a.group is not None and a.group.name == "demo\\Standard" for a in demo)
        real, rtotal = await db["account_repo"].find_page(limit=1000, account_type="real")
        assert rtotal == 75
        off, ototal = await db["account_repo"].find_page(limit=1000, enabled=False)
        assert ototal == 3                                   # every 50th account was seeded disabled
        assert all(not a.is_enabled for a in off)
        both, btotal = await db["account_repo"].find_page(
            limit=1000, group_name="demo\\Standard", enabled=True)
        assert btotal == 75 - len([a for a in off if a.group and a.group.name == "demo\\Standard"])
        assert len(both) == btotal
    asyncio.run(_run())


def test_client_and_manager_pages(db):
    async def _run():
        rows, total = await db["client_repo"].find_page(limit=2)
        assert total == 3 and len(rows) == 2
        rows, total = await db["manager_repo"].find_page(limit=10)
        assert total == 2 and [int(m.login) for m in rows] == [1000, 208011]
    asyncio.run(_run())


def test_deal_page_filters_and_order(db):
    async def _run():
        rows, total = await db["deal_repo"].find_page(limit=100)
        assert total == 6
        times = [d.created_at for d in rows]
        assert times == sorted(times, reverse=True)          # newest first
        out, ototal = await db["deal_repo"].find_page(limit=100, entry="OUT")
        assert ototal == 2 and all(d.entry.value == "OUT" for d in out)
        btc, btotal = await db["deal_repo"].find_page(limit=100, symbol="BTCUSD")
        assert btotal == 3
        mine, mtotal = await db["deal_repo"].find_page(limit=100, account_login=100000)
        assert mtotal == 1 and mine[0].deal_id == "deal-0"
        assert mine[0].external_id == "777000"               # the mapper round-tripped the ticket
    asyncio.run(_run())


def test_order_history_split_is_the_state_machine(db):
    async def _run():
        everything, total = await db["order_repo"].find_page(limit=100)
        assert total == 5
        active, atotal = await db["order_repo"].find_page(limit=100, history=False)
        assert atotal == 2 and {o.state.value for o in active} == {"PLACED", "STARTED"}
        hist, htotal = await db["order_repo"].find_page(limit=100, history=True)
        assert htotal == 3 and {o.state.value for o in hist} == {"FILLED", "REJECTED", "CANCELLED"}
        with pytest.raises(ValueError):
            await db["order_repo"].find_page(limit=100, state="FILLED", history=False)  # contradiction refused
    asyncio.run(_run())


def test_position_page_defaults_to_the_open_book(db):
    async def _run():
        rows, total = await db["position_repo"].find_page(limit=100)
        assert total == 3 and all(p.time_done is None for p in rows)
        everything, etotal = await db["position_repo"].find_page(limit=100, include_closed=True)
        assert etotal == 4
        eur, eurtotal = await db["position_repo"].find_page(limit=100, symbol="EURUSD")
        assert eurtotal == 2
        assert rows[0].external_id or True                   # pos-0's ticket survives the round trip
        by_id = {p.position_id: p for p in everything}
        assert by_id["pos-0"].external_id == "529200"
    asyncio.run(_run())


def test_limit_and_offset_never_negative_crash(db):
    async def _run():
        rows, total = await db["account_repo"].find_page(limit=1, offset=149)
        assert total == 150 and len(rows) == 1
        rows, total = await db["account_repo"].find_page(limit=1, offset=1000)
        assert total == 150 and rows == []                    # past the end: empty page, honest total
    asyncio.run(_run())
