import pytest
from decimal import Decimal
from datetime import datetime, timezone

from core.domains.accounts.models import Account, Group, AccountType, MarginProfile
from core.domains.instruments.models import Symbol
from core.domains.oms.entities.position import Position
from core.domains.oms.enums import PositionAction
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
        volume_step=Decimal('0.01')
    )
    assert sym.base_currency == "EUR"
    assert sym.quote_currency == "JPY"


def test_cross_currency_pnl_calculation_eurjpy_on_usd_account():
    """A EURJPY position on a USD account must have its PnL converted from JPY.

    This is the case the original audit flagged and the reason CurrencyProfit /
    CurrencyMargin had to be modelled: the position's profit is denominated in JPY, the
    account is in USD, and neither EURUSD nor a direct JPYUSD symbol exists in the feed.
    The rate has to be resolved through the inverse USDJPY pair.

        BUY 1 lot EURJPY @ 160.000, bid 161.000, contract size 100,000
        PnL in JPY = (161.000 - 160.000) * 1 * 100,000 = 100,000 JPY
        JPY -> USD = 1 / 150.000   (from the feed's USDJPY ask, via the inverse pair)
        PnL in USD = 666.67
        equity     = 5,000.00 + 666.67 = 5,666.67

    A BUY position is valued at the BID, because the bid is what the broker transacts at
    to close it. Valuing at the ask would hand the spread to the client on every position.

    Note what this test does NOT do: it no longer calls
    select_positions_for_liquidation and asserts the position comes back. This position is
    profitable and the account has no margin used, so MT5's rule - "close worst-loss
    positions first until margin level recovers" - selects nothing. The previous assertion
    could only pass on an engine that liquidated positions regardless of whether
    liquidation was warranted.
    """
    eurjpy = Symbol(
        name="EURJPY",
        path="Forex" + chr(92) + "EURJPY",
        tick_size=Decimal('0.001'),
        tick_value=Decimal('1.0'),
        contract_size=Decimal('100000'),
        digits=3,
        # MT5's own values. CurrencyProfit is what PnL is denominated in - JPY here - and
        # CurrencyMargin is what the requirement is computed in. Neither is derivable from
        # the name for a cross pair, which is why the name heuristic is only a fallback.
        base_currency="EUR",
        quote_currency="JPY",
        margin_currency="EUR",
        volume_min=Decimal('0.01'),
        volume_max=Decimal('100.0'),
        volume_step=Decimal('0.01')
    )
    account = Account(
        login=200001,
        group=Group(name="REAL_STANDARD", margin=MarginProfile(leverage_default=100)),
        account_type=AccountType.REAL,
        currency="USD",
        balance=Money(Decimal('5000.00'), "USD")
    )
    position = Position(
        position_id="POS_EURJPY_1",
        account_login="200001",
        symbol="EURJPY",
        volume=Volume(Decimal('1.0')),
        action=PositionAction.BUY,
        price_open=Price(Decimal('160.000')),
        contract_size=Decimal('100000'),
        time_create=datetime.now(timezone.utc)
    )

    market_feed = MockMarketFeedWithCrossRates({
        "EURJPY": {"bid": "161.000", "ask": "161.005"},
        "USDJPY": {"bid": "149.990", "ask": "150.000"},
    })
    symbol_repo = MockSymbolRepository([eurjpy])
    risk_engine = RiskEngine(symbol_repo=symbol_repo, market_data_engine=market_feed)

    # The conversion resolves through the inverse pair: there is no JPYUSD symbol.
    # Inverting swaps the side of the spread - the broker's ask on USDJPY is the broker's
    # bid on JPYUSD - so a buy deal converts at 1/USDJPY.bid and a sell at 1/USDJPY.ask.
    buy_rate = risk_engine.get_conversion_rate("JPY", "USD", market_feed=market_feed, side="BUY")
    sell_rate = risk_engine.get_conversion_rate("JPY", "USD", market_feed=market_feed, side="SELL")
    assert buy_rate == Decimal('1.0') / Decimal('149.990')
    assert sell_rate == Decimal('1.0') / Decimal('150.000')
    assert buy_rate > sell_rate, (
        "buying the quote currency must cost more than selling it; if these are equal the "
        "spread is being ignored and every cross-currency margin is understated"
    )

    snapshot = risk_engine.calculate_margin_level(account, [position])

    # 100,000 JPY of profit. PnL converts at the PROFIT rate - one rate for gains and
    # losses alike, so equity does not depend on its own sign. This position is a BUY
    # EURJPY, closed by selling EUR, so the JPY proceeds convert as a SELL of JPY:
    # 1 / USDJPY.ask = 1 / 150.000. That is deliberately NOT the buy rate above.
    expected_pnl = (Decimal('100000') / Decimal('150.000')).quantize(Decimal('0.01'))
    assert expected_pnl == Decimal('666.67'), (
        "the audit's own table gives ~$6.67 per pip per lot on a JPY pair; 100 pips is 666.67"
    )
    assert expected_pnl != (Decimal('100000') / Decimal('149.990')).quantize(Decimal('0.01')), (
        "PnL must not convert at the buy rate; using it would make equity depend on the "
        "sign of its own PnL"
    )
    assert snapshot.equity.quantize(Decimal('0.01')) == Decimal('5000.00') + expected_pnl

    # The margin requirement is in EUR and must also be converted, not assumed to be USD.
    # 1 lot * 100,000 / 100 = 1,000 EUR, converted via EURUSD triangulated from USDJPY.
    # 1 lot * 100,000 / 100 = 1,000 EUR of maintenance margin, converted to USD through
    # EURUSD. It must be more than 1,000 at any plausible EURUSD, and nowhere near the
    # ~150,000 it would be if the JPY rate were applied by mistake.
    assert Decimal('1000') < snapshot.margin_used < Decimal('2000')

    # Nothing should be liquidated: the account is profitable and far from stop-out.
    to_close = risk_engine.select_positions_for_liquidation(
        account=account,
        positions=[position],
        symbol_repo=symbol_repo,
        market_feed=market_feed
    )
    assert to_close == [], (
        "a profitable position on an account with no margin pressure must not be selected "
        "for liquidation"
    )


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
        volume_step=Decimal('0.01')
    )

    account = Account(
        login=200001,
        group=Group(name="REAL_STANDARD"),
        account_type=AccountType.REAL,
        balance=Money(Decimal('5000.00'), "USD")
    )

    position = Position(
        position_id="POS_EURJPY_1",
        account_login="200001",
        symbol="EURJPY",
        volume=Volume(Decimal('1.0')),
        action=PositionAction.BUY,
        price_open=Price(Decimal('160.000')),
        contract_size=Decimal('100000'),
        time_create=datetime.now(timezone.utc)
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

    # The message names the pair and every route tried - direct, inverse, and each
    # triangulation currency - because an operator diagnosing a halted account needs to
    # know which pairs are missing, not merely that one is. The legacy wording
    # ("Missing exchange rate for JPY -> USD") carried less information.
    message = str(exc_info.value)
    assert "JPY -> USD" in message or ("JPY" in message and "USD" in message), (
        f"the error must name the unresolvable pair, got: {message}"
    )
