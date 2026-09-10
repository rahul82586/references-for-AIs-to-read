import pytest
from decimal import Decimal
from datetime import datetime, timezone

from core.domains.accounts.models import Account, Group, AccountType
from core.domains.instruments.models import Symbol
from core.domains.oms.entities.position import Position
from core.domains.oms.entities.order import OrderType
from core.domains.common.value_objects import Money, Price, Volume
from core.domains.risk.engine import RiskEngine, CurrencyConversionError


class MockMarketFeedWithCrossRates:
    def __init__(self, ticks=None):
        self.ticks = ticks or {}

    def get_latest_tick(self, symbol: str):
        return self.ticks.get(symbol)


class MockSymbolRepository:
    def __init__(self, symbols):
        self.symbols = {s.name: s for s in symbols}

    def get_symbol(self, name: str):
        return self.symbols.get(name)

    def find_by_name(self, name: str):
        return self.symbols.get(name)


def test_symbol_currency_parsing():
    """Verify base and quote currency auto-parsing in Symbol model."""
    sym = Symbol(
        name="EURJPY",
        path="Forex\\EURJPY",
        tick_size=Decimal('0.001'),
        tick_value=Decimal('1.0'),
        contract_size=Decimal('100000'),
        digits=3,
        volume_min=Decimal('0.01'),
        volume_max=Decimal('100.0'),
        volume_step=Decimal('0.01'),
        margin_initial_percent=Decimal('1.0'),
        margin_maintenance_percent=Decimal('0.5')
    )
    assert sym.base_currency == "EUR"
    assert sym.quote_currency == "JPY"


def test_cross_currency_pnl_calculation_eurjpy_on_usd_account():
    """
    Test an EURJPY position on a USD account.
    Verifies PnL is correctly converted from JPY to USD using USDJPY exchange rate.
    """
    eurjpy = Symbol(
        name="EURJPY",
        path="Forex\\EURJPY",
        tick_size=Decimal('0.001'),
        tick_value=Decimal('1.0'),
        contract_size=Decimal('100000'),
        digits=3,
        volume_min=Decimal('0.01'),
        volume_max=Decimal('100.0'),
        volume_step=Decimal('0.01'),
        margin_initial_percent=Decimal('1.0'),
        margin_maintenance_percent=Decimal('0.5')
    )

    account = Account(
        login=200001,
        group=Group(name="REAL_STANDARD"),
        account_type=AccountType.REAL,
        balance=Money(Decimal('5000.00'), "USD")
    )

    position = Position(
        id="POS_EURJPY_1",
        account_login="200001",
        symbol="EURJPY",
        volume=Volume(Decimal('1.0')),  # 1 lot = 100,000 EUR
        side=OrderType.BUY,
        average_price=Price(Decimal('160.000')),
        contract_size=Decimal('100000'),
        opened_at=datetime.now(timezone.utc)
    )

    # Market feed has EURJPY bid = 161.000 (+1.000 JPY profit per unit * 100,000 = +100,000 JPY)
    # Market feed has USDJPY ask = 150.000 (Conversion rate to USD = 1 / 150.000 JPY per USD)
    market_feed = MockMarketFeedWithCrossRates({
        "EURJPY": {"bid": "161.000", "ask": "161.005"},
        "USDJPY": {"bid": "149.990", "ask": "150.000"}
    })

    symbol_repo = MockSymbolRepository([eurjpy])
    risk_engine = RiskEngine(symbol_repo=symbol_repo, market_data_engine=market_feed)

    positions_with_pnl = risk_engine.select_positions_for_liquidation(
        account=account,
        positions=[position],
        symbol_repo=symbol_repo,
        market_feed=market_feed
    )

    assert len(positions_with_pnl) == 1
    rate = risk_engine.get_conversion_rate("JPY", "USD", market_feed=market_feed)
    assert rate == Decimal('1.0') / Decimal('150.000')


def test_cross_currency_pnl_missing_rate_raises_error():
    """
    Assert that CurrencyConversionError is raised when no exchange rate is available for cross-currency trade.
    """
    eurjpy = Symbol(
        name="EURJPY",
        path="Forex\\EURJPY",
        tick_size=Decimal('0.001'),
        tick_value=Decimal('1.0'),
        contract_size=Decimal('100000'),
        digits=3,
        volume_min=Decimal('0.01'),
        volume_max=Decimal('100.0'),
        volume_step=Decimal('0.01'),
        margin_initial_percent=Decimal('1.0'),
        margin_maintenance_percent=Decimal('0.5')
    )

    account = Account(
        login=200001,
        group=Group(name="REAL_STANDARD"),
        account_type=AccountType.REAL,
        balance=Money(Decimal('5000.00'), "USD")
    )

    position = Position(
        id="POS_EURJPY_1",
        account_login="200001",
        symbol="EURJPY",
        volume=Volume(Decimal('1.0')),
        side=OrderType.BUY,
        average_price=Price(Decimal('160.000')),
        contract_size=Decimal('100000'),
        opened_at=datetime.now(timezone.utc)
    )

    # Market feed ONLY has EURJPY, NO USDJPY exchange rate!
    empty_feed = MockMarketFeedWithCrossRates({
        "EURJPY": {"bid": "161.000", "ask": "161.005"}
    })

    symbol_repo = MockSymbolRepository([eurjpy])
    risk_engine = RiskEngine(symbol_repo=symbol_repo, market_data_engine=empty_feed)

    with pytest.raises(CurrencyConversionError) as exc_info:
        risk_engine.select_positions_for_liquidation(
            account=account,
            positions=[position],
            symbol_repo=symbol_repo,
            market_feed=empty_feed
        )

    assert "Missing exchange rate for JPY -> USD" in str(exc_info.value)
