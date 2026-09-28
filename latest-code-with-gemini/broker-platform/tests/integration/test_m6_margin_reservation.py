"""M6: margin reservation — the hold between approval and fill (M4 debt #1).

Before M6 nothing moved any number the pre-trade check reads between approval
and the deal being booked. On one node with the in-process bus the orchestrator
runs inline and the window is closed; across a Redis bus or two API nodes, two
concurrent orders could both pass the same free-margin check and both book.

Now: approval reserves the exact requirement (accounts.margin_reserved via ONE
conditional UPDATE — the database serialises racers; orders.reserved_margin
records whose hold it is), the fill releases it inside the deal transaction,
and every rejection funnel releases it. These tests pin all four behaviours.
"""
import asyncio
from decimal import Decimal

import pytest

from application.commands.create_order import CreateOrderCommand
from core.domains.accounts.enums import MarginMode
from core.domains.common.value_objects import Price, Volume
from core.domains.oms.entities.order import Order
from core.domains.oms.enums import OrderState, OrderType
from tests.integration.trading_harness import (
    DEFAULT_LOGIN,
    build_harness,
    make_account,
    make_group,
)

BID = Decimal("1.10000")
ASK = Decimal("1.10010")


def coverage():
    from core.domains.execution.models import CoverageAccount

    return [CoverageAccount(account_id="DEFAULT_COVERAGE", name="c", currency="USD",
                            nop_limit=Decimal("100"))]


def make_order(login=DEFAULT_LOGIN, symbol="EURUSD", volume="1.0"):
    return Order(
        account_login=login,
        symbol=symbol,
        order_type=OrderType.BUY,
        volume_initial=Volume(Decimal(volume)),
        volume_current=Volume(Decimal(volume)),
        price_order=Price(ASK),
        state=OrderState.STARTED,
    )


async def test_two_concurrent_approvals_cannot_both_pass_the_same_free_margin():
    """The M4 debt-1 race, at the service level where it actually lives.

    Balance 1200 USD; one 1.0-lot EURUSD buy needs ~1100.10. Two validates run
    concurrently (asyncio.gather) with publish_events=False so no orchestrator
    fills anything: exactly one may be approved, because the first approval's
    reservation is visible to the second check.
    """
    group = make_group()
    account = make_account(group=group, balance=Decimal("1200"))
    h = await build_harness(groups=[group], accounts=[account], coverage=coverage())
    await h.publish_tick("EURUSD", BID, ASK)

    symbol = await h.symbol_repo.find_by_name("EURUSD")
    live = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    service = h.stack.risk_service

    order_a, order_b = make_order(), make_order()
    _validated = [order_a, order_b]
    results = await asyncio.gather(
        service.validate_order(order_a, live, symbol, Price(ASK), publish_events=False),
        service.validate_order(order_b, live, symbol, Price(ASK), publish_events=False),
    )
    assert sorted(results) == [False, True], "exactly one concurrent order may be approved"

    after = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    # exactly ONE hold, the winner's requirement - not two, not zero
    winner_hold = max(
        Decimal(str(getattr(o, "reserved_margin", 0) or 0)) for o in _validated
    )
    assert after.margin_reserved.amount == winner_hold
    assert winner_hold > Decimal("1000") and winner_hold < Decimal("1200")


async def test_a_fill_releases_the_reservation_exactly():
    """After the deal is booked, the hold is gone and margin_used carries the
    real requirement — the reservation must not linger and double-charge."""
    h = await build_harness(coverage=coverage())
    await h.publish_tick("EURUSD", BID, ASK)

    order = await h.stack.create_order_handler.handle(
        CreateOrderCommand(account_login=DEFAULT_LOGIN, symbol="EURUSD",
                           order_type=OrderType.BUY, volume=Decimal("0.10"))
    )
    assert order.state == OrderState.FILLED

    account = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    assert account.margin_reserved.amount == Decimal("0")
    assert account.margin_used.amount == Decimal("110.01")  # the M4 number, unchanged

    stored = await h.order_repo.find_by_id(order.ticket_id)
    assert Decimal(str(stored.reserved_margin)) == Decimal("0")  # zeroed so replays cannot re-release


async def test_a_rejected_a_book_order_releases_its_reservation():
    """The A-Book stub refuses (no LP connected) AFTER approval reserved the
    margin — the rejection funnel must give the hold back, or the account
    loses free margin forever."""
    from tests.integration.test_order_execution_e2e import a_book_rule

    h = await build_harness(rules=a_book_rule(), coverage=coverage(), lp_strict=True)
    await h.publish_tick("EURUSD", BID, ASK)

    order = await h.stack.create_order_handler.handle(
        CreateOrderCommand(account_login=DEFAULT_LOGIN, symbol="EURUSD",
                           order_type=OrderType.BUY, volume=Decimal("0.10"))
    )
    assert order.state == OrderState.REJECTED  # the stub refuses, honestly

    account = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    assert account.margin_reserved.amount == Decimal("0")  # hold released by the funnel
    assert Decimal(str(order.reserved_margin)) == Decimal("0")
    assert account.balance.amount == Decimal("10000")  # nothing was charged
    assert await h.position_repo.get_by_account(DEFAULT_LOGIN) == []


async def test_sql_reservation_is_one_atomic_conditional_update(tmp_path):
    """Two racers, one row, margin for exactly one: the database decides.

    This is the multi-node guarantee — the in-process lock cannot provide it,
    the conditional UPDATE's rowcount can.
    """
    from infrastructure.persistence.account_models import account_to_db
    from infrastructure.persistence.database import DatabaseManager
    from infrastructure.persistence.repositories.account_repository import SqlAccountRepository

    manager = DatabaseManager(f"sqlite+aiosqlite:///{tmp_path}/res.db")
    await manager.create_tables()

    group = make_group()
    account = make_account(group=group, balance=Decimal("1200"))
    async with manager.session_factory() as session:
        session.add(account_to_db(account))
        await session.commit()

    repo = SqlAccountRepository(manager.session_factory)
    results = await asyncio.gather(
        repo.reserve_margin(DEFAULT_LOGIN, Decimal("1100.10")),
        repo.reserve_margin(DEFAULT_LOGIN, Decimal("1100.10")),
    )
    totals = [r for r in results if r is not None]
    assert len(totals) == 1, "exactly one racer may win the row"
    assert totals[0] == Decimal("1100.10")

    assert await repo.release_margin(DEFAULT_LOGIN, Decimal("1100.10")) == Decimal("0")
    # a double release must clamp at zero, not go negative
    await repo.release_margin(DEFAULT_LOGIN, Decimal("1100.10"))

    from sqlalchemy import text

    async with manager.session_factory() as session:
        row = (await session.execute(
            text("SELECT margin_reserved FROM accounts WHERE login = :l"),
            {"l": str(DEFAULT_LOGIN)},
        )).first()
    assert Decimal(str(row[0])) == Decimal("0")
    await manager.close()
