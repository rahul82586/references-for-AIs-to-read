"""D9: after a restart, are the account figures current or frozen?

Observed live after a 10-hour shutdown: an account holding an open BTCUSD position
read `equity=100000, profit=0, margin_used=0`, while the venue's own book was
current. Equity, profit, margin_free and margin_level are recomputed by
TickMarginPipeline on TICK_RECEIVED *while the server runs* - and nothing
recomputes them at boot, so they stay frozen at the last tick before shutdown
until a tick arrives for a symbol that account holds. If the symbol is not
subscribed, never.

`cli sync` was an honest stub that exited 2. ValuationService is what it should
have called.

The rule this pins, and the reason it is not a one-line recompute: a sweep must
NEVER invent a price. An equity computed from nothing is worse than a stale
equity, because a stale number is at least a real number from a real moment - and
it is now stamped with when.
"""
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from application.services.reconciliation_service import ValuationService
from core.domains.accounts.account import MARGIN_LEVEL_UNLIMITED
from core.domains.common.value_objects import Money
from core.domains.market_data.engine import MarketDataEngine
from core.domains.market_data.models import Tick
from infrastructure.messaging.inprocess_event_bus import InProcessEventBus
from tests.integration.trading_harness import (
    build_harness, make_account, make_eurusd, make_group,
)


class _Position:
    def __init__(self, login, symbol="EURUSD", side="BUY", volume="0.10",
                 open_price="1.10000"):
        self.position_id = f"{login}_{symbol}"
        self.account_login = login
        self.symbol = symbol

        class _A:
            value = side
        self.action = _A()

        class _V:
            value = Decimal(volume)
        self.volume = _V()

        class _P:
            value = Decimal(open_price)
        self.price_open = _P()


class _Positions:
    def __init__(self, rows):
        self._rows = rows

    async def get_open_positions(self):
        return list(self._rows)


def _service(h, positions, engine=None):
    return ValuationService(
        account_repo=h.account_repo,
        position_repo=_Positions(positions),
        symbol_repo=h.symbol_repo,
        market_data_engine=engine if engine is not None else h.stack.market_data_engine,
        risk_engine=h.stack.risk_engine,
    )


@pytest.mark.asyncio
async def test_a_frozen_account_is_revalued_from_the_current_price():
    """The D9 complaint: profit 0 and equity == balance ten hours after a fill."""
    h = await build_harness()
    login = h.accounts[0].login
    account = await h.account_repo.find_by_login(login)

    # the frozen state: a position is open, but nothing has revalued it
    account.profit = Money(Decimal("0"), "USD")
    account.equity = Money(account.balance.amount, "USD")
    await h.account_repo.save(account)

    svc = _service(h, [_Position(login, open_price="1.10000")])
    # the market has moved up 200 points since the position was opened
    await h.publish_tick("EURUSD", Decimal("1.10200"), Decimal("1.10210"))

    stats = await svc.revalue_all()

    assert stats["accounts"] == 1 and stats["revalued"] == 1
    after = await h.account_repo.find_by_login(login)
    assert after.profit.amount > Decimal("0"), "a long position in a rising market is in profit"
    assert after.equity.amount == after.balance.amount + after.profit.amount
    assert after.margin_level != Decimal("0")
    assert after.margin_level != MARGIN_LEVEL_UNLIMITED or after.margin_used.amount == 0


@pytest.mark.asyncio
async def test_a_symbol_with_no_known_price_is_skipped_not_guessed():
    """The rule that matters more than the recompute: never invent a price."""
    h = await build_harness()
    login = h.accounts[0].login
    account = await h.account_repo.find_by_login(login)
    before_equity = account.equity.amount
    before_profit = account.profit.amount

    svc = _service(h, [_Position(login, symbol="NOSUCH", open_price="1.0")])
    stats = await svc.revalue_all()

    assert stats["revalued"] == 0
    assert stats["skipped_no_price"] == 1
    after = await h.account_repo.find_by_login(login)
    assert after.equity.amount == before_equity, "a skipped account must be untouched"
    assert after.profit.amount == before_profit


@pytest.mark.asyncio
async def test_a_sweep_never_writes_margin_used():
    """D8b: valuation and margin have disjoint write sets. A sweep that recomputed
    margin_used could erase what a fill wrote."""
    h = await build_harness()
    login = h.accounts[0].login
    account = await h.account_repo.find_by_login(login)
    account.margin_used = Money(Decimal("110.01"), "USD")
    account.margin_reserved = Money(Decimal("55.00"), "USD")
    await h.account_repo.save(account)

    await h.publish_tick("EURUSD", Decimal("1.10200"), Decimal("1.10210"))
    svc = _service(h, [_Position(login, open_price="1.10000")])
    await svc.revalue_all()

    after = await h.account_repo.find_by_login(login)
    assert after.margin_used.amount == Decimal("110.01"), "the sweep touched margin_used"
    assert after.margin_reserved.amount == Decimal("55.00"), "the sweep touched a hold"


@pytest.mark.asyncio
async def test_several_accounts_are_valued_in_one_pass():
    group = make_group()
    h = await build_harness(groups=[group], accounts=[
        make_account(login=910001, group=group),
        make_account(login=910002, group=group),
    ])
    await h.publish_tick("EURUSD", Decimal("1.10200"), Decimal("1.10210"))
    svc = _service(h, [_Position(910001, open_price="1.10000"),
                       _Position(910002, open_price="1.10100")])
    stats = await svc.revalue_all()
    assert stats["accounts"] == 2
    assert stats["revalued"] == 2


@pytest.mark.asyncio
async def test_a_position_repository_with_no_lister_is_an_error_not_a_silent_noop():
    """"Nothing to revalue" and "could not look" must not report the same thing."""
    h = await build_harness()

    class Opaque:
        pass

    svc = ValuationService(account_repo=h.account_repo, position_repo=Opaque(),
                           symbol_repo=h.symbol_repo,
                           market_data_engine=h.stack.market_data_engine)
    stats = await svc.revalue_all()
    assert stats["errors"] >= 1
    assert stats["revalued"] == 0


@pytest.mark.asyncio
async def test_the_sweep_is_idempotent():
    """Running it twice must converge, not accumulate."""
    h = await build_harness()
    login = h.accounts[0].login
    await h.publish_tick("EURUSD", Decimal("1.10200"), Decimal("1.10210"))
    svc = _service(h, [_Position(login, open_price="1.10000")])

    await svc.revalue_all()
    first = await h.account_repo.find_by_login(login)
    await svc.revalue_all()
    second = await h.account_repo.find_by_login(login)

    assert first.profit.amount == second.profit.amount
    assert first.equity.amount == second.equity.amount


# --------------------------------------- the repair path (D8b's safety net)

@pytest.mark.asyncio
async def test_a_lost_margin_used_is_repaired_and_reported():
    """Open positions with margin_used = 0 is not a legitimate state.

    D8b was a fill's margin write being erased by a concurrent tick. The write
    path is fixed and tested, but an account already in that state stays
    under-margined and pinned at the 999999 sentinel, where stop-out can never
    fire. The sweep repairs it - and says so loudly, because a repair is evidence
    that the write path failed somewhere.
    """
    h = await build_harness()
    login = h.accounts[0].login
    account = await h.account_repo.find_by_login(login)
    account.margin_used = Money(Decimal("0"), "USD")     # the lost write
    account.margin_level = MARGIN_LEVEL_UNLIMITED
    await h.account_repo.save(account)

    await h.publish_tick("EURUSD", Decimal("1.10200"), Decimal("1.10210"))
    svc = _service(h, [_Position(login, open_price="1.10000")])
    stats = await svc.revalue_all()

    after = await h.account_repo.find_by_login(login)
    assert stats.get("margin_repaired") == 1
    assert after.margin_used.amount > Decimal("0"), "the repair did not run"
    assert after.margin_level != MARGIN_LEVEL_UNLIMITED, (
        "still pinned at the sentinel, so stop-out still cannot fire"
    )


@pytest.mark.asyncio
async def test_an_ordinary_sweep_still_does_not_touch_margin_used():
    """The repair is narrow: a healthy margin_used must survive untouched.

    This is the D8b guarantee, asserted from the other side.
    """
    h = await build_harness()
    login = h.accounts[0].login
    account = await h.account_repo.find_by_login(login)
    account.margin_used = Money(Decimal("110.01"), "USD")
    await h.account_repo.save(account)

    await h.publish_tick("EURUSD", Decimal("1.10200"), Decimal("1.10210"))
    svc = _service(h, [_Position(login, open_price="1.10000")])
    stats = await svc.revalue_all()

    after = await h.account_repo.find_by_login(login)
    assert stats.get("margin_repaired", 0) == 0
    assert after.margin_used.amount == Decimal("110.01")
