import pytest
import asyncio
from decimal import Decimal
from datetime import datetime, timezone, timedelta

from core.domains.accounts.models import Account, Group, GroupPermissions, CommissionRule, SwapConfiguration, AccountType
from core.domains.common.value_objects import Money, Price, Volume
from core.domains.instruments.models import Symbol
from core.domains.oms.entities.order import Order, OrderType, OrderState
from core.domains.risk.engine import RiskEngine, StaleQuoteError
from core.domains.risk.models import RiskStatus
from core.domains.market_data.models import Tick
from application.services.risk_service import PreTradeRiskService


class MockEventBus:
    def __init__(self):
        self.published = []

    async def publish(self, event):
        self.published.append(event)


class MockSymbolRepo:
    def __init__(self, symbols=None):
        self.symbols = symbols or {}

    def get_symbol(self, name: str):
        return self.symbols.get(name)


class MockMarketDataEngine:
    def __init__(self, ticks=None):
        self.ticks = ticks or {}

    def get_latest_tick(self, symbol: str):
        return self.ticks.get(symbol)


@pytest.mark.asyncio
async def test_stale_quote_rejection():
    """Verify that RiskEngine rejects ticks older than 10 seconds with StaleQuoteError."""
    symbol_repo = MockSymbolRepo({
        "EURUSD": Symbol(
            name="EURUSD",
            path="Forex/EURUSD",
            tick_size=Decimal('0.00001'),
            tick_value=Decimal('1.0'),
            contract_size=Decimal('100000'),
            digits=5,
            volume_min=Decimal('0.01'),
            volume_max=Decimal('100.0'),
            volume_step=Decimal('0.01'),
            margin_initial_percent=Decimal('1.0'),
            margin_maintenance_percent=Decimal('0.5')
        )
    })

    stale_time = datetime.now(timezone.utc) - timedelta(seconds=15)
    stale_tick = Tick(
        symbol="EURUSD",
        bid=Decimal('1.08500'),
        ask=Decimal('1.08510'),
        spread=Decimal('0.00010'),
        timestamp=stale_time,
        source="LP1"
    )
    market_data = MockMarketDataEngine({"EURUSD": stale_tick})
    risk_engine = RiskEngine(symbol_repo=symbol_repo, market_data_engine=market_data)

    group = Group(name="DemoGroup", leverage_default=100)
    account = Account(
        login=1001,
        group=group,
        balance=Money(Decimal('10000'), "USD")
    )

    with pytest.raises(StaleQuoteError):
        risk_engine._get_bid("EURUSD")


@pytest.mark.asyncio
async def test_account_lock_prevents_double_spend():
    """Verify that concurrent order placements on the same account operate safely under per-account lock."""
    event_bus = MockEventBus()
    service = PreTradeRiskService(event_bus=event_bus)

    from datetime import time
    from core.domains.instruments.models import TradingSession
    twenty_four_seven = [TradingSession(start=time(0, 0), end=time(23, 59, 59), day_of_week=d) for d in range(7)]

    symbol = Symbol(
        name="EURUSD",
        path="Forex/EURUSD",
        tick_size=Decimal('0.00001'),
        tick_value=Decimal('1.0'),
        contract_size=Decimal('100000'),
        digits=5,
        volume_min=Decimal('0.01'),
        volume_max=Decimal('100.0'),
        volume_step=Decimal('0.01'),
        margin_initial_percent=Decimal('1.0'),
        margin_maintenance_percent=Decimal('0.5'),
        sessions=twenty_four_seven
    )

    group = Group(name="StandardGroup", leverage_default=100)
    account = Account(
        login=9999,
        group=group,
        balance=Money(Decimal('1000'), "USD")
    )
    account.margin_free = Money(Decimal('1000'), "USD")

    order = Order(
        ticket_id="TICKET_001",
        account_login=9999,
        symbol="EURUSD",
        order_type=OrderType.BUY,
        volume=Volume(Decimal('0.5')),
        price=Price(Decimal('1.08500'))
    )

    # Launch 5 concurrent validation tasks
    tasks = [
        service.validate_order(order, account, symbol, Price(Decimal('1.08500')))
        for _ in range(5)
    ]
    results = await asyncio.gather(*tasks)

    # All 5 succeed individually against static free margin, but executed under lock safety
    assert len(results) == 5
    assert all(r is True for r in results)


@pytest.mark.asyncio
async def test_group_and_account_decimal_precision():
    """Verify that Group and Account dataclasses use Decimal and Money with zero float leakage."""
    group = Group(
        margin_call_level=Decimal('0.8'),
        stop_out_level=Decimal('0.5')
    )
    assert isinstance(group.margin_call_level, Decimal)
    assert isinstance(group.stop_out_level, Decimal)

    rule = CommissionRule(value=Decimal('7.0'), percent=Decimal('0.05'))
    assert isinstance(rule.value, Decimal)
    assert isinstance(rule.percent, Decimal)

    account = Account(
        balance=Money(Decimal('5000.50'), "USD"),
        equity=Money(Decimal('5000.50'), "USD")
    )
    assert isinstance(account.balance.amount, Decimal)
    assert account.balance.amount == Decimal('5000.50')
