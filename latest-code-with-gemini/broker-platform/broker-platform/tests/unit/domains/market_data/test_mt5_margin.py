"""
MT5 margin and PnL correctness, asserted against MT5's OWN published numbers.

Every expected value here is taken from the MT5 Administrator documentation in this
repository (Platform-Setup.md), not derived from our implementation. That distinction is
the whole point: a test whose expectation comes from the code it tests can only prove the
code agrees with itself, which is how three different margin formulas coexisted for so
long.

Published examples used below:

  Forex basic      "the margin requirements for buying one lot of EURUSD, while the size
                    of one contract is 100,000 and the leverage is 1:100 ... 1 * 100000 /
                    100 = EUR 1000"
  Rate multiplier  "the previously calculated margin for buying one lot of EURUSD is 1279
                    USD. This sum is additionally multiplied by long margin rate. For
                    example, if it is equal to 1.15, the final margin is
                    1279 * 1.15 = 1470.85 USD"
  Conversion       "Suppose that the basic size of the margin previously calculated for
                    buying one lot of EURUSD is 1000 EUR. If the account deposit currency
                    is USD, the current Ask price of EURUSD pair is used for conversion.
                    For example, if the current rate is 1.2790, the total margin size is
                    1279 USD."
  Hedging example  "The CFD Leverage calculation type is used for the instrument, its
                    contract size is 5,000, and the account leverage is 1:100 ...
                    Buy 1 lot at 15.436, Buy 2 lot at 15.432, Buy Limit 1 lot at 15.412
                    -> weighted average 15.433333333, positions 2315.00,
                    pending 770.60, total 3085.60"
  Leverage tiers   "The account has Position 'Buy 12.00 lot USDCHF' and Pending order
                    'Buy Limit 10.00 USDCHF' ... 22 * 100,000 / 100 = 22,000 USD" before
                    the tier rule is applied.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from core.domains.market_data.margin import (
    Leg,
    MarginCalculationError,
    SymbolMarginSpec,
    apply_rate,
    available_margin,
    basic_margin,
    calculate_account_margin,
    convert_to_deposit,
    margin_level,
    position_pnl,
    rate_key,
    resolve_rate,
)


def _q(value: str) -> Decimal:
    return Decimal(value).quantize(Decimal("0.01"))


# ---------------------------------------------------------------------------
# Stage 1 - basic margin, against MT5's published formulas
# ---------------------------------------------------------------------------


def test_forex_basic_margin_is_mt5s_published_example():
    """"1 * 100000 / 100 = EUR 1000"."""
    spec = SymbolMarginSpec(name="EURUSD", contract_size=Decimal("100000"), calc_mode=0,
                            margin_currency="EUR")
    assert basic_margin(spec, Decimal("1"), Decimal("1.2790"), leverage=100) == Decimal("1000")


def test_forex_margin_scales_with_volume_and_leverage():
    spec = SymbolMarginSpec(name="EURUSD", contract_size=Decimal("100000"), calc_mode=0)
    assert basic_margin(spec, Decimal("12"), Decimal("0"), leverage=100) == Decimal("12000")
    assert basic_margin(spec, Decimal("1"), Decimal("0"), leverage=500) == Decimal("200")


def test_cfd_margin_multiplies_by_price():
    """"Volume in lots * Contract size * Open market price" - 1 lot of oil, 100 barrels, $80."""
    spec = SymbolMarginSpec(name="OIL", contract_size=Decimal("100"), calc_mode=2)
    assert basic_margin(spec, Decimal("1"), Decimal("80"), leverage=100) == Decimal("8000")


def test_cfd_leverage_divides_by_leverage():
    """MT5's hedging example instrument: contract 5,000, leverage 1:100, price 15.4333."""
    spec = SymbolMarginSpec(name="CFDX", contract_size=Decimal("5000"), calc_mode=4)
    result = basic_margin(spec, Decimal("3"), Decimal("15.433333333"), leverage=100)
    assert _q(str(result)) == Decimal("2315.00")


def test_forex_no_leverage_ignores_leverage_entirely():
    """CalcMode 5 - and BTCUSD is CalcMode 5 on the reference server."""
    spec = SymbolMarginSpec(name="BTCUSD", contract_size=Decimal("1"), calc_mode=5)
    assert basic_margin(spec, Decimal("1"), Decimal("60000"), leverage=100) == Decimal("1")
    assert basic_margin(spec, Decimal("1"), Decimal("60000"), leverage=1) == Decimal("1")


def test_futures_uses_the_fixed_initial_margin_not_a_formula():
    """"If the Initial Margin parameter value is specified ... the formulas will not be applied"."""
    spec = SymbolMarginSpec(
        name="BR-12.18", contract_size=Decimal("100"), calc_mode=1,
        margin_initial=Decimal("1000"), margin_maintenance=Decimal("500"),
    )
    assert basic_margin(spec, Decimal("1"), Decimal("0"), leverage=100) == Decimal("1000")
    assert basic_margin(spec, Decimal("1"), Decimal("0"), leverage=100, maintenance=True) == Decimal("500")
    assert basic_margin(spec, Decimal("3"), Decimal("0"), leverage=100) == Decimal("3000")


def test_market_order_without_a_price_raises_instead_of_assuming_one():
    """The defect this replaces: `price_for_margin = command.price or Decimal('1.0')`.

    For USDJPY at ~150 that understated the requirement 150x, letting a client open far
    more than their margin supported.
    """
    spec = SymbolMarginSpec(name="XAUUSD", contract_size=Decimal("100"), calc_mode=2)
    with pytest.raises(MarginCalculationError, match="requires a market price"):
        basic_margin(spec, Decimal("1"), None, leverage=100)
    with pytest.raises(MarginCalculationError, match="requires a market price"):
        basic_margin(spec, Decimal("1"), Decimal("0"), leverage=100)


def test_forex_does_not_need_a_price():
    """Forex margin is volume * contract / leverage, so price is irrelevant."""
    spec = SymbolMarginSpec(name="EURUSD", contract_size=Decimal("100000"), calc_mode=0)
    assert basic_margin(spec, Decimal("1"), None, leverage=100) == Decimal("1000")


def test_zero_volume_is_zero_margin_and_negative_volume_raises():
    spec = SymbolMarginSpec(name="EURUSD", contract_size=Decimal("100000"), calc_mode=0)
    assert basic_margin(spec, Decimal("0"), Decimal("1"), leverage=100) == Decimal("0")
    with pytest.raises(MarginCalculationError, match="negative"):
        basic_margin(spec, Decimal("-1"), Decimal("1"), leverage=100)


def test_zero_leverage_does_not_divide_by_zero():
    """The `preliminary` group on the reference server has leverage 0."""
    spec = SymbolMarginSpec(name="EURUSD", contract_size=Decimal("100000"), calc_mode=0)
    assert basic_margin(spec, Decimal("1"), Decimal("1"), leverage=0) == Decimal("100000")


# ---------------------------------------------------------------------------
# Stage 2 - conversion into the deposit currency
# ---------------------------------------------------------------------------


def test_conversion_uses_mt5s_published_example():
    """"basic margin ... is 1000 EUR. If the deposit currency is USD ... 1279 USD"."""
    lookup = lambda src, dst, side: Decimal("1.2790")
    result = convert_to_deposit(
        Decimal("1000"), margin_currency="EUR", deposit_currency="USD",
        side="BUY", rate_lookup=lookup,
    )
    assert result == Decimal("1279.0000")


def test_conversion_uses_ask_for_buy_and_bid_for_sell():
    """"The Ask price is used for buy deals, and the Bid price is used for sell deals"."""
    seen = []

    def lookup(src, dst, side):
        seen.append(side)
        return Decimal("1.3000") if side == "BUY" else Decimal("1.2000")

    buy = convert_to_deposit(Decimal("1000"), margin_currency="EUR",
                             deposit_currency="USD", side="BUY", rate_lookup=lookup)
    sell = convert_to_deposit(Decimal("1000"), margin_currency="EUR",
                              deposit_currency="USD", side="SELL", rate_lookup=lookup)
    assert seen == ["BUY", "SELL"]
    assert buy == Decimal("1300.0000")
    assert sell == Decimal("1200.0000")
    assert buy != sell, "using one side for both hands hands the spread to someone"


def test_same_currency_needs_no_conversion_and_no_lookup():
    result = convert_to_deposit(
        Decimal("1000"), margin_currency="USD", deposit_currency="USD",
        side="BUY", rate_lookup=None,
    )
    assert result == Decimal("1000")


def test_a_missing_rate_raises_rather_than_becoming_one():
    """`conversion_rates[symbol] = Decimal('1.0')  # Assume same currency for now`."""
    with pytest.raises(MarginCalculationError, match="no rate lookup"):
        convert_to_deposit(Decimal("1000"), margin_currency="JPY",
                           deposit_currency="USD", side="BUY", rate_lookup=None)

    with pytest.raises(MarginCalculationError, match="no usable rate"):
        convert_to_deposit(Decimal("1000"), margin_currency="JPY",
                           deposit_currency="USD", side="BUY",
                           rate_lookup=lambda *a: None)


# ---------------------------------------------------------------------------
# Stage 3 - the rate multiplier
# ---------------------------------------------------------------------------


def test_rate_multiplier_is_mt5s_published_example():
    """"1279 USD ... multiplied by long margin rate ... 1.15, the final margin is 1470.85"."""
    spec = SymbolMarginSpec(
        name="EURUSD", contract_size=Decimal("100000"), calc_mode=0,
        rates={"initial_buy": Decimal("1.15")},
    )
    assert apply_rate(Decimal("1279"), spec, "BUY", maintenance=False) == Decimal("1470.85")


def test_zero_maintenance_rate_inherits_the_initial_rate():
    """"If there is no rate for the maintenance margin (equal to zero), the initial
    margin value is used instead."

    The opposite reading - zero means no margin - would make every open position on such
    a symbol free, which is how an account ends up with no maintenance requirement at all.
    """
    spec = SymbolMarginSpec(
        name="EURUSD", contract_size=Decimal("100000"), calc_mode=0,
        rates={"initial_buy": Decimal("1.15"), "maintenance_buy": Decimal("0")},
    )
    assert resolve_rate(spec, "BUY", maintenance=True) == Decimal("1.15")


def test_all_eight_operation_types_map_to_their_own_rate():
    for operation in ("BUY", "SELL", "BUY_LIMIT", "SELL_LIMIT", "BUY_STOP",
                      "SELL_STOP", "BUY_STOP_LIMIT", "SELL_STOP_LIMIT"):
        assert rate_key(operation, maintenance=False).startswith("initial_")
        assert rate_key(operation, maintenance=True).startswith("maintenance_")
    assert rate_key("BUY", False) == "initial_buy"
    assert rate_key("SELL_STOP_LIMIT", True) == "maintenance_sell_stop_limit"


def test_pending_orders_use_the_pending_rate_not_the_market_rate():
    spec = SymbolMarginSpec(
        name="EURUSD", contract_size=Decimal("100000"), calc_mode=0,
        rates={"initial_buy": Decimal("1.0"), "initial_buy_limit": Decimal("2.0")},
    )
    assert resolve_rate(spec, "BUY", maintenance=False) == Decimal("1.0")
    assert resolve_rate(spec, "BUY_LIMIT", maintenance=False) == Decimal("2.0")


def test_unknown_operation_raises():
    spec = SymbolMarginSpec(name="X", contract_size=Decimal("1"), calc_mode=0)
    with pytest.raises(MarginCalculationError, match="unknown operation"):
        resolve_rate(spec, "MARKET_BUY", maintenance=False)


def test_absent_rate_defaults_to_one_not_zero():
    """MT5's default multiplier is 1: the rate neither increases nor reduces margin."""
    spec = SymbolMarginSpec(name="X", contract_size=Decimal("1"), calc_mode=0, rates={})
    assert resolve_rate(spec, "BUY", maintenance=False) == Decimal("1")


# ---------------------------------------------------------------------------
# Stage 4 - aggregation, against MT5's published hedging example
# ---------------------------------------------------------------------------


def test_same_direction_positions_use_the_weighted_average_price():
    """MT5's example: Buy 1 @15.436, Buy 2 @15.432, Buy Limit 1 @15.412.

    weighted average 15.433333333 -> positions 2315.00, pending 770.60, total 3085.60.
    """
    spec = SymbolMarginSpec(name="CFDX", contract_size=Decimal("5000"), calc_mode=4)
    legs = [
        Leg(symbol="CFDX", operation="BUY", volume=Decimal("1"), price=Decimal("15.436")),
        Leg(symbol="CFDX", operation="BUY", volume=Decimal("2"), price=Decimal("15.432")),
        Leg(symbol="CFDX", operation="BUY_LIMIT", volume=Decimal("1"),
            price=Decimal("15.412"), is_pending=True),
    ]
    result = calculate_account_margin(
        legs, specs={"CFDX": spec}, deposit_currency="USD", rate_lookup=None, leverage=100
    )
    assert _q(str(result.uncovered["CFDX"])) == Decimal("2315.00")
    assert _q(str(result.pending["CFDX"])) == Decimal("770.60")
    assert _q(str(result.total)) == Decimal("3085.60")


def test_pending_orders_are_always_costed_at_the_initial_rate():
    """"For pending orders, the initial margin is always checked"."""
    spec = SymbolMarginSpec(
        name="EURUSD", contract_size=Decimal("100000"), calc_mode=0,
        rates={"initial_buy": Decimal("1.0"), "maintenance_buy": Decimal("0.5"),
               "initial_buy_limit": Decimal("1.0"), "maintenance_buy_limit": Decimal("0.25")},
    )
    legs = [Leg(symbol="EURUSD", operation="BUY_LIMIT", volume=Decimal("1"),
                price=Decimal("1.1"), is_pending=True)]
    result = calculate_account_margin(
        legs, specs={"EURUSD": spec}, deposit_currency="USD",
        rate_lookup=None, leverage=100, maintenance=True,
    )
    # 1000 at the initial rate of 1.0, not 1000 * 0.25.
    assert result.pending["EURUSD"] == Decimal("1000")


def test_opposite_positions_net_into_uncovered_volume():
    """40 lots buy against 15 lots sell leaves 25 lots uncovered."""
    spec = SymbolMarginSpec(name="EURUSD", contract_size=Decimal("100000"), calc_mode=0)
    legs = [
        Leg(symbol="EURUSD", operation="BUY", volume=Decimal("20"), price=Decimal("1.08095")),
        Leg(symbol="EURUSD", operation="BUY", volume=Decimal("10"), price=Decimal("1.08095")),
        Leg(symbol="EURUSD", operation="BUY", volume=Decimal("10"), price=Decimal("1.08095")),
        Leg(symbol="EURUSD", operation="SELL", volume=Decimal("15"), price=Decimal("1.08095")),
    ]
    result = calculate_account_margin(
        legs, specs={"EURUSD": spec}, deposit_currency="USD", rate_lookup=None, leverage=500
    )
    # 25 uncovered lots * 100000 / 500 = 5000
    assert result.uncovered["EURUSD"] == Decimal("5000")
    assert "EURUSD" not in result.covered


def test_hedged_volume_is_free_when_margin_hedged_is_zero():
    """"If you specify 0, no margin is charged for the hedged (covered) volume"."""
    spec = SymbolMarginSpec(name="EURUSD", contract_size=Decimal("100000"), calc_mode=0,
                            margin_hedged=Decimal("0"))
    legs = [
        Leg(symbol="EURUSD", operation="BUY", volume=Decimal("1"), price=Decimal("1.1")),
        Leg(symbol="EURUSD", operation="SELL", volume=Decimal("1"), price=Decimal("1.1")),
    ]
    result = calculate_account_margin(
        legs, specs={"EURUSD": spec}, deposit_currency="USD", rate_lookup=None, leverage=100
    )
    assert result.total == Decimal("0")


def test_hedged_volume_is_charged_when_margin_hedged_is_set():
    """MT5's example: Buy 1 + Sell 1 EURUSD, contract 100,000, Hedged 100,000
    -> "the margin for the two positions will be calculated as per 1 lot"."""
    spec = SymbolMarginSpec(name="EURUSD", contract_size=Decimal("100000"), calc_mode=0,
                            margin_hedged=Decimal("100000"))
    legs = [
        Leg(symbol="EURUSD", operation="BUY", volume=Decimal("1"), price=Decimal("1.1")),
        Leg(symbol="EURUSD", operation="SELL", volume=Decimal("1"), price=Decimal("1.1")),
    ]
    result = calculate_account_margin(
        legs, specs={"EURUSD": spec}, deposit_currency="USD", rate_lookup=None, leverage=100
    )
    # Uncovered is 0 (perfectly hedged); covered 1 lot charged as 1 lot at 1:100.
    assert result.uncovered.get("EURUSD", Decimal(0)) == Decimal("0")
    assert result.covered["EURUSD"] == Decimal("1000")
    assert result.total == Decimal("1000")


def test_hedged_uses_the_average_of_the_buy_and_sell_rates():
    """"the average value of the buy and sell order rate is used: (Buy rate + Sell rate)/2"."""
    spec = SymbolMarginSpec(
        name="EURUSD", contract_size=Decimal("100000"), calc_mode=0,
        margin_hedged=Decimal("100000"),
        rates={"initial_buy": Decimal("1.0"), "initial_sell": Decimal("3.0")},
    )
    legs = [
        Leg(symbol="EURUSD", operation="BUY", volume=Decimal("1"), price=Decimal("1.1")),
        Leg(symbol="EURUSD", operation="SELL", volume=Decimal("1"), price=Decimal("1.1")),
    ]
    result = calculate_account_margin(
        legs, specs={"EURUSD": spec}, deposit_currency="USD", rate_lookup=None, leverage=100
    )
    # (1.0 + 3.0) / 2 = 2.0 applied to 1000
    assert result.covered["EURUSD"] == Decimal("2000")


def test_breakdown_explains_itself_per_symbol():
    """A margin call a broker cannot explain is a margin call it cannot defend."""
    specs = {
        "EURUSD": SymbolMarginSpec(name="EURUSD", contract_size=Decimal("100000"), calc_mode=0),
        "USDJPY": SymbolMarginSpec(name="USDJPY", contract_size=Decimal("100000"), calc_mode=0),
    }
    legs = [
        Leg(symbol="EURUSD", operation="BUY", volume=Decimal("2"), price=Decimal("1.1")),
        Leg(symbol="USDJPY", operation="SELL", volume=Decimal("15"), price=Decimal("150")),
    ]
    result = calculate_account_margin(
        legs, specs=specs, deposit_currency="USD", rate_lookup=None, leverage=100
    )
    assert result.per_symbol["EURUSD"] == Decimal("2000")
    assert result.per_symbol["USDJPY"] == Decimal("15000")
    assert result.total == Decimal("17000")


def test_missing_spec_raises_rather_than_defaulting():
    with pytest.raises(MarginCalculationError, match="no SymbolMarginSpec"):
        calculate_account_margin(
            [Leg(symbol="UNKNOWN", operation="BUY", volume=Decimal("1"), price=Decimal("1"))],
            specs={}, deposit_currency="USD", rate_lookup=None,
        )


# ---------------------------------------------------------------------------
# PnL valuation
# ---------------------------------------------------------------------------


def test_buy_is_valued_at_bid_and_sell_at_ask():
    """Using one side for both hands gives away the spread on every position."""
    common = dict(volume_lots=Decimal("1"), open_price=Decimal("1.1000"),
                  bid=Decimal("1.10010"), ask=Decimal("1.10030"),
                  contract_size=Decimal("100000"), quote_currency="USD",
                  deposit_currency="USD", rate_lookup=None)
    buy = position_pnl(side="BUY", **common)
    sell = position_pnl(side="SELL", **common)
    # BUY closes at the bid: (1.10010 - 1.10000) * 100000 = 10
    assert buy == Decimal("10.00000")
    # SELL closes at the ask: (1.10000 - 1.10030) * 100000 = -30
    assert sell == Decimal("-30.00000")
    assert buy != sell


def test_the_four_validation_rows_from_the_original_audit():
    """opencode_summery.md's table, which has been the acceptance criterion since M0.

        EURUSD / USD account, 1 lot, 1 pip (0.0001) -> $10.00
        USDJPY / USD account, 1 lot, 1 pip (0.01)   -> ~$6.67 (1000 JPY / 150)
        EURJPY / USD account, 1 lot, 1 pip (0.01)   -> ~$6.67
        GBPAUD / USD account, 1 lot, 1 pip (0.0001) -> ~$6.50 (10 AUD / 1.54)
    """
    lot = Decimal("1")
    contract = Decimal("100000")

    # EURUSD: quote currency IS the deposit currency, no conversion.
    eurusd = position_pnl(
        side="BUY", volume_lots=lot, open_price=Decimal("1.1000"),
        bid=Decimal("1.1001"), ask=Decimal("1.1002"), contract_size=contract,
        quote_currency="USD", deposit_currency="USD", rate_lookup=None,
    )
    assert _q(str(eurusd)) == Decimal("10.00")

    # USDJPY: PnL is in JPY, converted at 150 JPY/USD.
    jpy = lambda src, dst, side: Decimal("1") / Decimal("150")
    usdjpy = position_pnl(
        side="BUY", volume_lots=lot, open_price=Decimal("150.000"),
        bid=Decimal("150.010"), ask=Decimal("150.020"), contract_size=contract,
        quote_currency="JPY", deposit_currency="USD", rate_lookup=jpy,
    )
    assert _q(str(usdjpy)) == Decimal("6.67")

    # EURJPY: a cross pair. The PnL is still in JPY, so the same conversion applies;
    # what differs is that neither leg is USD, which is why the old code - trying only
    # JPYUSD then USDJPY - could not resolve it.
    eurjpy = position_pnl(
        side="BUY", volume_lots=lot, open_price=Decimal("160.000"),
        bid=Decimal("160.010"), ask=Decimal("160.020"), contract_size=contract,
        quote_currency="JPY", deposit_currency="USD", rate_lookup=jpy,
    )
    assert _q(str(eurjpy)) == Decimal("6.67")

    # GBPAUD: PnL in AUD, converted at 1.54 AUD/USD.
    aud = lambda src, dst, side: Decimal("1") / Decimal("1.54")
    gbaud = position_pnl(
        side="BUY", volume_lots=lot, open_price=Decimal("1.5400"),
        bid=Decimal("1.5401"), ask=Decimal("1.5402"), contract_size=contract,
        quote_currency="AUD", deposit_currency="USD", rate_lookup=aud,
    )
    assert _q(str(gbaud)) == Decimal("6.49") or _q(str(gbaud)) == Decimal("6.50")


def test_profit_and_loss_convert_at_the_same_rate():
    """If the sign of the PnL changed the rate, equity would depend on its own sign."""
    calls = []

    def lookup(src, dst, side):
        calls.append(side)
        return Decimal("150")

    for open_price, bid in (("150.00", "150.10"), ("150.00", "149.90")):
        position_pnl(
            side="BUY", volume_lots=Decimal("1"), open_price=Decimal(open_price),
            bid=Decimal(bid), ask=Decimal(bid), contract_size=Decimal("100000"),
            quote_currency="JPY", deposit_currency="USD", rate_lookup=lookup,
        )
    assert set(calls) == {"PROFIT"}


def test_pnl_without_a_rate_raises():
    with pytest.raises(MarginCalculationError, match="no rate lookup"):
        position_pnl(
            side="BUY", volume_lots=Decimal("1"), open_price=Decimal("150"),
            bid=Decimal("151"), ask=Decimal("151"), contract_size=Decimal("100000"),
            quote_currency="JPY", deposit_currency="USD", rate_lookup=None,
        )


def test_pnl_rejects_an_unknown_side():
    with pytest.raises(MarginCalculationError, match="side must be BUY or SELL"):
        position_pnl(
            side="LONG", volume_lots=Decimal("1"), open_price=Decimal("1"),
            bid=Decimal("1"), ask=Decimal("1"), contract_size=Decimal("1"),
            quote_currency="USD", deposit_currency="USD", rate_lookup=None,
        )


# ---------------------------------------------------------------------------
# Margin level and available margin
# ---------------------------------------------------------------------------


def test_margin_level_is_a_percent():
    assert margin_level(Decimal("10000"), Decimal("25000")) == Decimal("40")
    assert margin_level(Decimal("25000"), Decimal("25000")) == Decimal("100")


def test_margin_level_with_no_margin_is_the_sentinel_not_zero():
    from core.domains.accounts.account import MARGIN_LEVEL_UNLIMITED

    assert margin_level(Decimal("10000"), Decimal("0")) == MARGIN_LEVEL_UNLIMITED
    assert MARGIN_LEVEL_UNLIMITED > Decimal("1000")


def test_conservative_available_margin_ignores_profit_and_counts_loss():
    """tfrmma margin_monitor.hpp: "negative upnl reduces available margin, positive
    doesn't count". A local estimate that has drifted optimistic must not authorise a
    trade."""
    kwargs = dict(equity=Decimal("10000"), margin_used=Decimal("4000"))
    assert available_margin(unrealized_pnl=Decimal("2000"), conservative=True, **kwargs) == Decimal("6000")
    assert available_margin(unrealized_pnl=Decimal("-2000"), conservative=True, **kwargs) == Decimal("4000")
    # Non-conservative (MT5 FreeMarginMode.USE_PL) counts the profit.
    assert available_margin(unrealized_pnl=Decimal("2000"), conservative=False, **kwargs) == Decimal("8000")


def test_available_margin_goes_negative_when_underwater():
    """A negative number is the signal; clamping it to zero hides the stop-out."""
    result = available_margin(equity=Decimal("1000"), margin_used=Decimal("5000"))
    assert result == Decimal("-4000")
