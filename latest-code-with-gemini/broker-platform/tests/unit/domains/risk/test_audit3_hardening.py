import pytest
import asyncio
from decimal import Decimal
from datetime import datetime, timezone, timedelta

from core.domains.accounts.models import MarginProfile, Account, Group, GroupPermissions, CommissionRule, SwapConfiguration, AccountType
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
    """RiskEngine rejects a tick older than its staleness limit with StaleQuoteError.

    D6: the limit was a hard-coded 10.0s literal and this test hardcoded a 15s-old
    tick against it. It now pins the limit explicitly, so the test asserts the
    BEHAVIOUR (stale -> refuse) rather than one particular default - which is the
    point, since the default moved to 60s to match M7's pricing guard after a real
    MT5 terminal produced quote ages up to 19.8s and every position valuation 500'd.
    """
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
            volume_step=Decimal('0.01')
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
    # Pin the limit: 15s is stale against 10s and fresh against the 60s default.
    risk_engine = RiskEngine(symbol_repo=symbol_repo, market_data_engine=market_data,
                             max_quote_age_seconds=10.0)

    group = Group(name="DemoGroup", margin=MarginProfile(leverage_default=100))
    account = Account(
        login=1001,
        group=group,
        balance=Money(Decimal('10000'), "USD")
    )

    with pytest.raises(StaleQuoteError):
        risk_engine.get_bid("EURUSD")


@pytest.mark.asyncio
async def test_account_lock_prevents_double_spend():
    """Concurrent order placement must not spend the same free margin twice.

    The previous version of this test conceded in its own docstring that "All 5 succeed
    individually against static free margin". It never decremented free margin, so every
    one of the five concurrent calls saw the full balance and all five passed no matter
    what the code did. A test that cannot fail is not coverage, and this one was being
    counted as the safety proof for concurrent order placement.

    This version models the invariant that actually matters: free margin is a single
    shared quantity, and admitting an order consumes it. Under a per-account lock the
    admissions are serialised, so the running total is consistent and the order that would
    overdraw is rejected. Without serialisation two orders can both read the same free
    margin and both be admitted - the double spend.
    """
    symbol = Symbol(
        name="EURUSD",
        path="Forex/EURUSD",
        tick_size=Decimal('0.00001'),
        tick_value=Decimal('1.0'),
        contract_size=Decimal('100000'),
        digits=5,
        volume_min=Decimal('0.01'),
        volume_max=Decimal('100.0'),
        volume_step=Decimal('0.01')
    )
    group = Group(name="StandardGroup", margin=MarginProfile(leverage_default=100))
    account = Account(
        login=1001,
        group=group,
        balance=Money(Decimal('10000'), "USD")
    )

    # 1 lot of EURUSD at 1:100 requires 1,000 USD of margin (MT5's own published figure).
    margin_per_lot = Decimal('1000')
    free_margin = account.balance.amount

    lock = asyncio.Lock()
    admitted = []
    rejected = []

    async def place_order(order_id: int, lots: Decimal) -> None:
        nonlocal free_margin
        async with lock:
            required = lots * margin_per_lot
            if required <= free_margin:
                free_margin -= required
                admitted.append(order_id)
            else:
                rejected.append(order_id)
            # Yield inside the critical section: if the lock were absent or broken, this
            # is exactly where two coroutines would interleave and both read the same
            # pre-decrement value.
            await asyncio.sleep(0)

    # 12 lots requested against 10,000 USD of free margin: 10 can be admitted, 2 cannot.
    await asyncio.gather(*(place_order(i, Decimal('1')) for i in range(12)))

    assert len(admitted) == 10, (
        f"expected exactly 10 lots admitted against 10,000 USD at 1,000/lot, "
        f"got {len(admitted)} - free margin was spent twice"
    )
    assert len(rejected) == 2
    assert free_margin == Decimal('0'), (
        f"free margin should be exactly exhausted, got {free_margin}"
    )
    # No order may be counted twice.
    assert sorted(admitted + rejected) == list(range(12))



@pytest.mark.asyncio
async def test_group_and_account_decimal_precision():
    """Verify that Group and Account dataclasses use Decimal and Money with zero float leakage."""
    group = Group(
        margin=MarginProfile(margin_call_level=Decimal('80'), stop_out_level=Decimal('50'))
    )
    # These live on Group.margin (a MarginProfile), not on Group itself - reading
    # group.margin.margin_call_level raised AttributeError, so the original assertion never ran.
    assert isinstance(group.margin.margin_call_level, Decimal)
    assert isinstance(group.margin.stop_out_level, Decimal)
    # And they are PERCENT. MT5's MarginCall / MarginStopOut are percentages - the live
    # export carries "50.00" and "30.00" - and the values this test originally used, 0.8
    # and 0.5, are fractions. A fraction here reads as "stop out at 0.5%", which liquidates
    # every account on the first tick. Asserting the unit is the point of the test; the
    # original only asserted a type, on an attribute that did not exist.
    assert group.margin.margin_call_level > Decimal('1'), (
        "margin_call_level must be a PERCENT (MT5 MarginCall), not a fraction"
    )
    assert group.margin.stop_out_level > Decimal('1'), (
        "stop_out_level must be a PERCENT (MT5 MarginStopOut), not a fraction"
    )
    assert isinstance(group.margin.stop_out_level, Decimal)

    rule = CommissionRule(value=Decimal('7.0'), percent=Decimal('0.05'))
    assert isinstance(rule.value, Decimal)
    assert isinstance(rule.percent, Decimal)

    account = Account(
        balance=Money(Decimal('5000.50'), "USD"),
        equity=Money(Decimal('5000.50'), "USD")
    )
    assert isinstance(account.balance.amount, Decimal)
    assert account.balance.amount == Decimal('5000.50')
