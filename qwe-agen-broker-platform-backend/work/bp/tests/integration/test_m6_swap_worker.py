"""M6: the swap worker charges overnight positions — faithfully and loudly.

Before M6 the worker spoke the pre-M3 vocabulary (position.side / .average_price
/ .id), constructed the base DomainEvent with an init=False event_type, used a
group-level swap profile MT5 does not have (swap is per SYMBOL with group
overrides), and was instantiated nowhere: nothing charged swap. Rewritten
against the MT5 Administrator guide (Symbols -> Swaps) and wired at startup.

These tests drive process_rollover() directly with a fixed clock: no sleeping
until 22:00 UTC, no dependence on the loop.
"""
from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from application.commands.create_order import CreateOrderCommand
from application.services.swap_worker import SwapWorker
from core.domains.execution.models import CoverageAccount
from core.domains.instruments.enums import SwapMode
from core.domains.ledger.engine import LedgerEngine
from core.domains.ledger.models import BalanceOperationType
from core.domains.oms.enums import OrderType
from tests.integration.trading_harness import (
    DEFAULT_LOGIN,
    build_harness,
    make_eurusd,
    make_group,
    make_usdjpy,
)

BID = Decimal("1.10000")
ASK = Decimal("1.10010")

# 2026-09-09 is a Wednesday, 09-11 a Friday, 09-12 a Saturday.
WEDNESDAY = datetime(2026, 9, 9, 22, 0, tzinfo=timezone.utc)
FRIDAY = datetime(2026, 9, 11, 22, 0, tzinfo=timezone.utc)
SATURDAY = datetime(2026, 9, 12, 22, 0, tzinfo=timezone.utc)


class InMemoryLedgerRepository:
    def __init__(self):
        self.operations = []

    async def save(self, operation, session=None):
        self.operations.append(operation)
        return operation


def swap_symbol_eurusd():
    """EURUSD as the reference server carries it: POINTS mode, -7.90 long,
    -0.83 short, triple day Friday (Swap3Day=5 with 0=Sunday)."""
    return replace(
        make_eurusd(),
        swap_mode=SwapMode.POINTS,
        swap_long=Decimal("-7.90"),
        swap_short=Decimal("-0.83"),
        swap_3day=5,
    )


def build_worker(h, ledger_repo):
    return SwapWorker(
        ledger_engine=LedgerEngine(ledger_repo=ledger_repo, account_repo=h.account_repo),
        position_repo=h.position_repo,
        account_repo=h.account_repo,
        symbol_repo=h.symbol_repo,
        event_bus=h.event_bus,
        market_data_engine=h.market_data_engine,
    )


async def buy(h, volume="0.10", symbol="EURUSD", order_type=OrderType.BUY):
    return await h.stack.create_order_handler.handle(
        CreateOrderCommand(
            account_login=DEFAULT_LOGIN, symbol=symbol, order_type=order_type,
            volume=Decimal(volume),
        )
    )


def coverage():
    return [CoverageAccount(account_id="DEFAULT_COVERAGE", name="c", currency="USD",
                            nop_limit=Decimal("100"))]


async def _harness_with_swaps(symbol):
    return await build_harness(symbols=[symbol], coverage=coverage())


async def test_points_swap_charges_the_guide_formula_on_a_weekday():
    """Guide's points formula: volume x contract x point, in the profit
    currency, converted, times the rate. EURUSD/USD needs no conversion:
    0.10 x 100000 x 0.00001 = 0.10 USD x (-7.90) = -0.79."""
    h = await _harness_with_swaps(swap_symbol_eurusd())
    await h.publish_tick("EURUSD", BID, ASK)
    await buy(h)
    ledger = InMemoryLedgerRepository()
    worker = build_worker(h, ledger)

    report = await worker.process_rollover(WEDNESDAY)

    assert report["charged"] == 1
    account = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    assert account.balance.amount == Decimal("10000") - Decimal("0.79")
    assert len(ledger.operations) == 1
    op = ledger.operations[0]
    assert op.operation_type == BalanceOperationType.SWAP
    assert op.amount.amount == Decimal("-0.79")

    positions = await h.position_repo.get_by_account(DEFAULT_LOGIN)
    assert positions[0].swap.amount == Decimal("-0.79")  # accumulates for statements
    assert positions[0].swap.currency == "USD"

    published = [
        e.event_type.value if hasattr(e.event_type, "value") else str(e.event_type)
        for e in h.event_bus.published
    ]
    assert "ledger.swap_applied" in published


async def test_triple_day_charges_three_times_and_weekend_nothing():
    h = await _harness_with_swaps(swap_symbol_eurusd())
    await h.publish_tick("EURUSD", BID, ASK)
    await buy(h)
    ledger = InMemoryLedgerRepository()
    worker = build_worker(h, ledger)

    friday = await worker.process_rollover(FRIDAY)  # Swap3Day=5 -> x3
    assert friday["charged"] == 1
    account = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    assert account.balance.amount == Decimal("10000") - Decimal("2.37")

    saturday = await worker.process_rollover(SATURDAY)  # weekend -> no swap
    assert saturday["charged"] == 0
    account = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    assert account.balance.amount == Decimal("10000") - Decimal("2.37")  # unchanged
    assert len(ledger.operations) == 1


async def test_short_positions_use_the_short_rate():
    h = await _harness_with_swaps(swap_symbol_eurusd())
    await h.publish_tick("EURUSD", BID, ASK)
    await buy(h, order_type=OrderType.SELL)
    worker = build_worker(h, InMemoryLedgerRepository())

    await worker.process_rollover(WEDNESDAY)

    account = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    # point price = 0.10 x 100000 x 0.00001 = 0.10 USD; x (-0.83) = -0.083
    assert account.balance.amount == Decimal("10000") - Decimal("0.083")


async def test_group_disable_switch_stops_the_charge():
    h = await _harness_with_swaps(swap_symbol_eurusd())
    await h.publish_tick("EURUSD", BID, ASK)
    await buy(h)
    account = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    account.group.swaps.enable_swaps = False
    worker = build_worker(h, InMemoryLedgerRepository())

    report = await worker.process_rollover(WEDNESDAY)

    assert report["charged"] == 0
    account = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    assert account.balance.amount == Decimal("10000")


async def test_points_swap_converts_a_jpy_profit_currency_to_the_deposit():
    """USDJPY: point price is 0.10 x 100000 x 0.001 = 10 JPY, converted to USD
    at the PROFIT-side rate — the same machinery the PnL path uses. Before M6
    the worker multiplied raw quote-currency amounts onto the balance."""
    symbol = replace(
        make_usdjpy(),
        swap_mode=SwapMode.POINTS,
        swap_long=Decimal("-1.20"),
        swap_short=Decimal("0.10"),
        swap_3day=5,  # Friday is the triple day, so Wednesday charges x1
    )
    h = await _harness_with_swaps(symbol)
    await h.publish_tick("USDJPY", Decimal("150.00"), Decimal("150.02"))
    await buy(h, symbol="USDJPY")
    worker = build_worker(h, InMemoryLedgerRepository())

    await worker.process_rollover(WEDNESDAY)

    rate = worker._conversion.get_conversion_rate("JPY", "USD", side="PROFIT")
    expected = (Decimal("0.10") * Decimal("100000") * Decimal("0.001")) * rate * Decimal("-1.20")
    account = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    booked = account.balance.amount - Decimal("10000")
    # the worker quantizes the charge to 8 decimal places before booking
    assert booked == pytest.approx(expected, abs=Decimal("1e-8"))
    assert booked > Decimal("-0.10")  # 10 JPY is cents, not ten dollars


async def test_disabled_mode_charges_nothing():
    h = await _harness_with_swaps(replace(make_eurusd(), swap_mode=SwapMode.DISABLED,
                                          swap_long=Decimal("-7.9")))
    await h.publish_tick("EURUSD", BID, ASK)
    await buy(h)
    worker = build_worker(h, InMemoryLedgerRepository())
    report = await worker.process_rollover(WEDNESDAY)
    assert report["charged"] == 0
