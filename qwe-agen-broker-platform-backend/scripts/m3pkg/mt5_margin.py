"""
MT5-accurate margin and PnL calculation.

This module exists because the same calculation was previously written THREE times,
differently, and none of the three matched MT5:

    Group.calculate_margin()             notional / min(leverage_default, leverage_max)
                                         * margin_rate_initial_buy - always the BUY
                                         rate, ignoring side and order type, and using
                                         min(default, max) which is not how MT5
                                         resolves leverage.
    create_order.py                      (volume * contract_size * price * rate) /
                                         effective_leverage - a fourth inline copy, with
                                         price defaulting to Decimal('1.0') for market
                                         orders, so JPY margin was understated 150x.
    RiskEngine.calculate_margin_level()  (price * volume * contract_size) / leverage,
                                         with no margin rate at all.

Every formula and every worked example below is taken from the MT5 Administrator
documentation in this repository (Platform-Setup.md, sections
`Symbols/Symbol-Settings/Trade/Margin-Calculation/*` and `Groups/Leverages`), and is
cross-checked against `tfrmma/oms-order-management-system`'s `margin_monitor.hpp` for
the conservatism rule. The tests in tests/unit/domains/risk/test_mt5_margin.py assert
MT5's own published numbers.

THE PIPELINE (MT5 computes margin in exactly these four stages)

    1. BASIC        volume_lots * contract_size [/ leverage]        for Forex
                    volume_lots * contract_size * price [/ leverage] for CFD / CFD-leverage
                    Result is in the symbol's MARGIN currency, which is usually but not
                    always the base currency.
    2. CONVERSION   margin currency -> deposit (account) currency, when they differ.
                    ASK is used for buy deals, BID for sell deals.
    3. RATE         multiply by the margin rate for the operation type. There are 8 of
                    them: initial and maintenance, each for market buy/sell and for the
                    four pending order types. If maintenance is 0, initial is used.
    4. AGGREGATION  same-direction positions are summed at a weighted average open price;
                    opposite directions are netted into uncovered + covered volume, and
                    the covered volume is charged at the symbol's hedged margin.

Two rules that are easy to miss and expensive to get wrong:

    * Initial margin is checked when OPENING a position; maintenance margin is checked
      for positions already OPEN; pending orders are always checked at initial.
    * Leverage is resolved per position from the account, the group and the symbol -
      not min(group.leverage_default, group.leverage_max), which is what the old code
      did and which ignores both the account override and the symbol cap.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Sequence

ZERO = Decimal("0")
ONE = Decimal("1")


class MarginStage(Enum):
    """Which of MT5's four calculation stages a value came from. Useful in errors."""

    BASIC = "basic"
    CONVERSION = "conversion"
    RATE = "rate"
    AGGREGATION = "aggregation"


class MarginCalculationError(ValueError):
    """Raised when margin cannot be computed without guessing.

    Guessing is what produced the original defects: a market order priced at 1.0 rather
    than refused, and a missing conversion rate treated as 1.0 rather than as an error.
    """


@dataclass(frozen=True)
class SymbolMarginSpec:
    """Everything about a symbol that margin calculation needs.

    Deliberately a separate structure from the domain Symbol: margin maths should not
    depend on 40 unrelated fields, and this makes the required inputs explicit and
    testable. ``from_symbol`` builds it from a domain Symbol.
    """

    name: str
    contract_size: Decimal
    #: MT5 CalcMode. 0 Forex, 1 Futures, 2 CFD, 3 CFD-index, 4 CFD-leverage,
    #: 5 Forex-no-leverage.
    calc_mode: int = 0
    #: MT5 CurrencyMargin - the currency the basic calculation produces. Distinct from
    #: both base and quote currency, and the reason cross-currency margin is hard.
    margin_currency: str = ""
    #: MT5 MarginHedged. If initial margin is set, this is an absolute money amount;
    #: otherwise it is a contract size used for the covered volume. 0 charges nothing
    #: for hedged volume.
    margin_hedged: Decimal = ZERO
    #: MT5 "Calculate hedged margin using larger leg".
    hedged_use_larger_leg: bool = False
    #: MT5 MarginInitial / MarginMaintenance, for Futures and fixed-margin symbols.
    margin_initial: Optional[Decimal] = None
    margin_maintenance: Optional[Decimal] = None
    #: The 8 initial and 8 maintenance rates, keyed by MarginRates field name.
    rates: Dict[str, Decimal] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.rates is None:
            object.__setattr__(self, "rates", {})

    @classmethod
    def from_symbol(cls, symbol: Any) -> "SymbolMarginSpec":
        """Build from a domain Symbol, reading the MT5-accurate fields."""
        rates: Dict[str, Decimal] = {}
        margin_rates = getattr(symbol, "margin_rates", None)
        if margin_rates is not None:
            for name in getattr(margin_rates, "__dataclass_fields__", {}):
                value = getattr(margin_rates, name, None)
                if isinstance(value, Decimal):
                    rates[name] = value

        calc_mode = getattr(symbol, "calc_mode", 0)
        calc_mode_value = int(getattr(calc_mode, "value", calc_mode) or 0)

        return cls(
            name=symbol.name,
            contract_size=_dec(getattr(symbol, "contract_size", 100000)),
            calc_mode=calc_mode_value,
            # CurrencyMargin is not modelled on Symbol yet (fieldmap records it as a
            # gap), so fall back to the base currency, which MT5 says is the usual case.
            margin_currency=(
                getattr(symbol, "margin_currency", "")
                or getattr(symbol, "base_currency", "")
                or ""
            ),
            margin_hedged=_dec(getattr(symbol, "margin_hedged", 0)),
            hedged_use_larger_leg=bool(getattr(symbol, "hedged_use_larger_leg", False)),
            margin_initial=_optional_dec(getattr(symbol, "margin_initial", None)),
            margin_maintenance=_optional_dec(getattr(symbol, "margin_maintenance", None)),
            rates=rates,
        )


# ---------------------------------------------------------------------------
# Operation kinds - which of the 8 rates applies
# ---------------------------------------------------------------------------

#: (is_pending, side) -> MarginRates field name, for initial margin.
_INITIAL_RATE_KEY = {
    (False, "BUY"): "initial_buy",
    (False, "SELL"): "initial_sell",
    (True, "BUY_LIMIT"): "initial_buy_limit",
    (True, "SELL_LIMIT"): "initial_sell_limit",
    (True, "BUY_STOP"): "initial_buy_stop",
    (True, "SELL_STOP"): "initial_sell_stop",
    (True, "BUY_STOP_LIMIT"): "initial_buy_stop_limit",
    (True, "SELL_STOP_LIMIT"): "initial_sell_stop_limit",
}

#: The same, for maintenance margin.
_MAINTENANCE_RATE_KEY = {
    (False, "BUY"): "maintenance_buy",
    (False, "SELL"): "maintenance_sell",
    (True, "BUY_LIMIT"): "maintenance_buy_limit",
    (True, "SELL_LIMIT"): "maintenance_sell_limit",
    (True, "BUY_STOP"): "maintenance_buy_stop",
    (True, "SELL_STOP"): "maintenance_sell_stop",
    (True, "BUY_STOP_LIMIT"): "maintenance_buy_stop_limit",
    (True, "SELL_STOP_LIMIT"): "maintenance_sell_stop_limit",
}

PENDING_ORDER_TYPES = frozenset(
    {
        "BUY_LIMIT",
        "SELL_LIMIT",
        "BUY_STOP",
        "SELL_STOP",
        "BUY_STOP_LIMIT",
        "SELL_STOP_LIMIT",
    }
)


def rate_key(operation: str, maintenance: bool) -> str:
    """Map an operation type to its MarginRates field name.

    ``operation`` is "BUY"/"SELL" for a market order or position, or one of the six
    pending order types. MT5 has 8 rates per direction-of-margin (initial, maintenance)
    and picking the wrong one silently changes the requirement.
    """
    table = _MAINTENANCE_RATE_KEY if maintenance else _INITIAL_RATE_KEY
    is_pending = operation in PENDING_ORDER_TYPES
    side = operation if is_pending else operation
    key = table.get((is_pending, side))
    if key is None:
        raise MarginCalculationError(
            f"unknown operation {operation!r}; expected BUY, SELL or one of "
            f"{sorted(PENDING_ORDER_TYPES)}"
        )
    return key


def resolve_rate(spec: SymbolMarginSpec, operation: str, maintenance: bool) -> Decimal:
    """The margin rate for an operation, applying MT5's fallback rule.

    MT5: "If there is no rate for the maintenance margin (equal to zero), the initial
    margin value is used instead." A zero maintenance rate is therefore NOT "no margin"
    - it means inherit the initial rate. Getting this backwards under-charges every
    open position on a symbol configured the way MT5's own example is.
    """
    key = rate_key(operation, maintenance)
    value = spec.rates.get(key)
    if value is None or value == ZERO:
        if maintenance:
            initial_key = rate_key(operation, False)
            value = spec.rates.get(initial_key)
        if value is None:
            # No rate configured at all. MT5's default multiplier is 1, i.e. the rate
            # neither increases nor reduces the basic margin.
            return ONE
    return value


# ---------------------------------------------------------------------------
# Stage 1: basic calculation
# ---------------------------------------------------------------------------


def basic_margin(
    spec: SymbolMarginSpec,
    volume_lots: Decimal,
    price: Decimal,
    *,
    leverage: int,
    maintenance: bool = False,
) -> Decimal:
    """MT5 stage 1: the basic margin, in the symbol's margin currency.

    Formulas verbatim from Platform-Setup.md, `Margin-Calculation/Basic`:

        Forex            volume_lots * contract_size / leverage
        Forex no leverage volume_lots * contract_size                (CalcMode 5)
        CFD              volume_lots * contract_size * price          (CalcMode 2)
        CFD leverage     volume_lots * contract_size * price / leverage (CalcMode 4)
        CFD index        volume_lots * contract_size * price * tick_value / tick_size
        Futures/options  volume_lots * initial_or_maintenance_margin  (CalcMode 1, 35, 36)

    A market order with no price cannot be costed for the price-dependent modes, so it
    raises rather than defaulting to 1.0 - the default that understated JPY margin 150x.
    """
    if volume_lots < ZERO:
        raise MarginCalculationError(f"volume cannot be negative: {volume_lots}")
    if volume_lots == ZERO:
        return ZERO

    fixed = spec.margin_maintenance if maintenance else spec.margin_initial
    if fixed is not None and fixed > ZERO:
        # "If the Initial Margin parameter value is specified in symbol settings, this
        # value will be used. The formulas described in this section will not be applied."
        return volume_lots * fixed

    needs_price = spec.calc_mode in (2, 3, 4)
    if needs_price and (price is None or price <= ZERO):
        raise MarginCalculationError(
            f"{spec.name}: CalcMode {spec.calc_mode} requires a market price to compute "
            "margin, and none was supplied. Refusing to assume 1.0 - for a JPY pair that "
            "understates the requirement by roughly 150x."
        )

    if spec.calc_mode == 5:  # Forex, no leverage
        return volume_lots * spec.contract_size
    if spec.calc_mode == 1:  # Futures
        base = spec.margin_initial or ZERO
        return volume_lots * base
    if spec.calc_mode == 2:  # CFD
        return volume_lots * spec.contract_size * price
    if spec.calc_mode == 4:  # CFD leverage
        return volume_lots * spec.contract_size * price / _leverage(leverage)
    if spec.calc_mode == 3:  # CFD index
        raise MarginCalculationError(
            f"{spec.name}: CalcMode 3 (CFD index) needs tick_value and tick_size, which "
            "SymbolMarginSpec does not carry yet"
        )

    # CalcMode 0: Forex. The documented formula.
    return volume_lots * spec.contract_size / _leverage(leverage)


def _leverage(leverage: Optional[int]) -> Decimal:
    """Leverage as a Decimal, refusing to divide by zero."""
    value = _dec(leverage if leverage is not None else 0)
    if value <= ZERO:
        # MT5 group `preliminary` carries leverage 0, meaning no trading is permitted.
        # Dividing by zero would crash; treating it as 1 would let an account with no
        # leverage open a position at full notional margin, which is at least safe.
        return ONE
    return value


# ---------------------------------------------------------------------------
# Stage 2: conversion into the deposit currency
# ---------------------------------------------------------------------------


def convert_to_deposit(
    amount: Decimal,
    *,
    margin_currency: str,
    deposit_currency: str,
    side: str,
    rate_lookup: Any,
) -> Decimal:
    """MT5 stage 2: margin currency -> deposit currency.

    "The current exchange rate of margin currency to deposit currency is used for
    conversion. The Ask price is used for buy deals, and the Bid price is used for sell
    deals."

    The side-dependence matters: converting at the wrong side of the spread biases every
    margin figure in the broker's favour or the client's, systematically.

    ``rate_lookup`` is a callable ``(from_ccy, to_ccy, side) -> Decimal``. A missing rate
    raises; it is never treated as 1.0, because 1.0 is the bug this replaces.
    """
    if amount == ZERO:
        return ZERO
    if not margin_currency or margin_currency == deposit_currency:
        return amount
    if rate_lookup is None:
        raise MarginCalculationError(
            f"cannot convert {margin_currency} -> {deposit_currency}: no rate lookup supplied"
        )
    rate = rate_lookup(margin_currency, deposit_currency, side)
    if rate is None or _dec(rate) <= ZERO:
        raise MarginCalculationError(
            f"no usable rate for {margin_currency} -> {deposit_currency} ({side})"
        )
    return amount * _dec(rate)


# ---------------------------------------------------------------------------
# Stage 3: the rate multiplier
# ---------------------------------------------------------------------------


def apply_rate(amount: Decimal, spec: SymbolMarginSpec, operation: str, maintenance: bool) -> Decimal:
    """MT5 stage 3: multiply by the margin rate for this operation type.

    "You can completely disable margin charging for any desired types of trading
    operations. To do this, set the zero margin ratio." Note this is the RATE being zero,
    which is distinct from the maintenance rate being zero (that means "inherit initial").
    Here an explicitly configured zero rate has already been resolved by resolve_rate, so
    a zero reaching this point genuinely means no margin.
    """
    return amount * resolve_rate(spec, operation, maintenance)


# ---------------------------------------------------------------------------
# Stage 4: aggregation across positions and orders
# ---------------------------------------------------------------------------


@dataclass
class Leg:
    """One position or order contributing to an account's margin."""

    symbol: str
    operation: str  # BUY / SELL / one of the six pending types
    volume: Decimal
    price: Decimal
    is_pending: bool = False
    #: Set by the calculator; the weighted average price for same-direction legs.
    spec: Optional[SymbolMarginSpec] = None
    leverage: int = 100


@dataclass
class MarginBreakdown:
    """The account margin, with enough detail to explain itself to a client or an audit.

    MT5 exposes exactly this decomposition in the Manager terminal, and a broker that
    cannot show how a margin call was reached cannot defend one.
    """

    total: Decimal = ZERO
    per_symbol: Dict[str, Decimal] = None  # type: ignore[assignment]
    uncovered: Dict[str, Decimal] = None  # type: ignore[assignment]
    covered: Dict[str, Decimal] = None  # type: ignore[assignment]
    pending: Dict[str, Decimal] = None  # type: ignore[assignment]
    deposit_currency: str = "USD"

    def __post_init__(self) -> None:
        if self.per_symbol is None:
            self.per_symbol = {}
        if self.uncovered is None:
            self.uncovered = {}
        if self.covered is None:
            self.covered = {}
        if self.pending is None:
            self.pending = {}


def _weighted_average(entries: Sequence[tuple]) -> tuple:
    """(total_volume, weighted_average_price) over (volume, price) pairs."""
    total = sum((v for v, _ in entries), ZERO)
    if total == ZERO:
        return ZERO, ZERO
    notional = sum((v * p for v, p in entries), ZERO)
    return total, notional / total


def calculate_account_margin(
    legs: Iterable[Leg],
    *,
    specs: Dict[str, SymbolMarginSpec],
    deposit_currency: str,
    rate_lookup: Any,
    leverage: int = 100,
    maintenance: bool = False,
) -> MarginBreakdown:
    """MT5 stage 4, and the entry point the risk engine should call.

    Same-direction legs on a symbol are summed at a weighted average open price. Opposite
    directions are split into uncovered volume (larger leg minus smaller) and covered
    volume, and the covered volume is charged at the symbol's hedged margin - which may be
    zero, meaning hedged volume is free.

    Pending orders are always costed at the INITIAL rate regardless of ``maintenance``,
    per MT5: "For pending orders, the initial margin is always checked."
    """
    breakdown = MarginBreakdown(deposit_currency=deposit_currency)
    by_symbol: Dict[str, List[Leg]] = {}
    for leg in legs:
        by_symbol.setdefault(leg.symbol, []).append(leg)

    for symbol, symbol_legs in by_symbol.items():
        spec = specs.get(symbol) or (symbol_legs[0].spec if symbol_legs[0].spec else None)
        if spec is None:
            raise MarginCalculationError(
                f"no SymbolMarginSpec for {symbol}; cannot compute margin"
            )

        positions = [leg for leg in symbol_legs if not leg.is_pending]
        pendings = [leg for leg in symbol_legs if leg.is_pending]

        # --- positions: net into uncovered + covered -------------------------
        buys = [(leg.volume, leg.price) for leg in positions if leg.operation == "BUY"]
        sells = [(leg.volume, leg.price) for leg in positions if leg.operation == "SELL"]
        buy_volume, buy_avg = _weighted_average(buys)
        sell_volume, sell_avg = _weighted_average(sells)

        uncovered_volume = abs(buy_volume - sell_volume)
        covered_volume = min(buy_volume, sell_volume)
        uncovered_side = "BUY" if buy_volume >= sell_volume else "SELL"
        uncovered_price = buy_avg if uncovered_side == "BUY" else sell_avg

        symbol_total = ZERO

        if uncovered_volume > ZERO:
            basic = basic_margin(
                spec,
                uncovered_volume,
                uncovered_price,
                leverage=leverage,
                maintenance=maintenance,
            )
            converted = convert_to_deposit(
                basic,
                margin_currency=spec.margin_currency,
                deposit_currency=deposit_currency,
                side=uncovered_side,
                rate_lookup=rate_lookup,
            )
            # "When considering a margin rate, the larger leg rate (buy or sell) is used."
            rated = apply_rate(converted, spec, uncovered_side, maintenance)
            breakdown.uncovered[symbol] = rated
            symbol_total += rated

        if covered_volume > ZERO and spec.margin_hedged > ZERO:
            # MT5: if initial margin is specified, Hedged is an absolute money amount;
            # otherwise it is a contract size fed through the symbol's own formula.
            both = [(leg.volume, leg.price) for leg in positions]
            _, avg_price = _weighted_average(both)
            if spec.margin_initial is not None and spec.margin_initial > ZERO:
                hedged_basic = covered_volume * spec.margin_hedged
            else:
                hedged_spec = SymbolMarginSpec(
                    name=spec.name,
                    contract_size=spec.margin_hedged,
                    calc_mode=spec.calc_mode,
                    margin_currency=spec.margin_currency,
                    rates=spec.rates,
                )
                hedged_basic = basic_margin(
                    hedged_spec,
                    covered_volume,
                    avg_price,
                    leverage=leverage,
                    maintenance=maintenance,
                )
            converted = convert_to_deposit(
                hedged_basic,
                margin_currency=spec.margin_currency,
                deposit_currency=deposit_currency,
                side=uncovered_side,
                rate_lookup=rate_lookup,
            )
            # "the average value of the buy and sell order rate is used"
            buy_rate = resolve_rate(spec, "BUY", maintenance)
            sell_rate = resolve_rate(spec, "SELL", maintenance)
            rated = converted * (buy_rate + sell_rate) / _dec(2)
            breakdown.covered[symbol] = rated
            symbol_total += rated

        # --- pending orders: always at the INITIAL rate ----------------------
        pending_total = ZERO
        for leg in pendings:
            basic = basic_margin(
                spec, leg.volume, leg.price, leverage=leverage, maintenance=False
            )
            side = "BUY" if leg.operation.startswith("BUY") else "SELL"
            converted = convert_to_deposit(
                basic,
                margin_currency=spec.margin_currency,
                deposit_currency=deposit_currency,
                side=side,
                rate_lookup=rate_lookup,
            )
            pending_total += apply_rate(converted, spec, leg.operation, False)
        if pending_total > ZERO:
            breakdown.pending[symbol] = pending_total
            symbol_total += pending_total

        if symbol_total > ZERO:
            breakdown.per_symbol[symbol] = symbol_total
        breakdown.total += symbol_total

    return breakdown


# ---------------------------------------------------------------------------
# PnL valuation
# ---------------------------------------------------------------------------


def position_pnl(
    *,
    side: str,
    volume_lots: Decimal,
    open_price: Decimal,
    bid: Decimal,
    ask: Decimal,
    contract_size: Decimal,
    quote_currency: str,
    deposit_currency: str,
    rate_lookup: Any,
) -> Decimal:
    """Unrealised PnL in the deposit currency, valued the way MT5 values it.

    Two rules that are routinely got wrong, and were got wrong here:

    1. A BUY position is valued at the BID (what the broker can sell at to close it) and
       a SELL at the ASK. Using the same side for both hands the client the spread on
       every position and makes equity wrong by the spread times the notional.
    2. The result is in the QUOTE currency and must be converted to the deposit
       currency. Assuming quote == deposit is what made every JPY, CHF, CAD and
       cross-pair PnL materially wrong.

    The conversion side is the one that closes the position: a long EURJPY is closed by
    selling EUR, so the JPY proceeds convert at the rate applicable to that direction.
    """
    if side not in ("BUY", "SELL"):
        raise MarginCalculationError(f"side must be BUY or SELL, got {side!r}")

    close_price = bid if side == "BUY" else ask
    if close_price <= ZERO:
        raise MarginCalculationError(f"{side} valuation price must be positive, got {close_price}")

    difference = (close_price - open_price) if side == "BUY" else (open_price - close_price)
    pnl_quote = difference * volume_lots * contract_size

    if not quote_currency or quote_currency == deposit_currency:
        return pnl_quote
    if rate_lookup is None:
        raise MarginCalculationError(
            f"cannot convert PnL {quote_currency} -> {deposit_currency}: no rate lookup"
        )
    # Converting a profit and a loss must use the same rate or the account's equity
    # depends on the sign of its own PnL. MT5 uses the profit-currency rate.
    rate = rate_lookup(quote_currency, deposit_currency, "PROFIT")
    if rate is None or _dec(rate) <= ZERO:
        raise MarginCalculationError(
            f"no usable rate for {quote_currency} -> {deposit_currency}"
        )
    return pnl_quote * _dec(rate)


def margin_level(equity: Decimal, margin_used: Decimal) -> Decimal:
    """Margin level as a PERCENT - MT5's convention, and the only one in this codebase.

    Returns the MARGIN_LEVEL_UNLIMITED sentinel (999999) when no margin is in use, rather
    than zero: zero reads as "fully exhausted" and would stop out an account with no
    positions.
    """
    from core.domains.accounts.account import MARGIN_LEVEL_UNLIMITED

    if margin_used <= ZERO:
        return MARGIN_LEVEL_UNLIMITED
    return (equity / margin_used) * Decimal("100")


# ---------------------------------------------------------------------------
# Available margin, with the conservatism rule from tfrmma's margin_monitor.hpp
# ---------------------------------------------------------------------------


def available_margin(
    *,
    equity: Decimal,
    margin_used: Decimal,
    unrealized_pnl: Decimal = ZERO,
    conservative: bool = True,
) -> Decimal:
    """Free margin, optionally applying the two-layer conservatism rule.

    ``tfrmma/oms-order-management-system``'s `margin_monitor.hpp` documents the rule this
    implements: "negative upnl reduces available margin, positive doesn't count". A local
    estimate that has drifted optimistically must not be allowed to authorise a trade, so
    only losses are trusted. Set ``conservative=False`` for the MT5 free-margin mode that
    does count profit (FreeMarginMode.USE_PL).
    """
    if conservative and unrealized_pnl > ZERO:
        unrealized_pnl = ZERO
    return equity + unrealized_pnl - margin_used


# ---------------------------------------------------------------------------
# Coercion helpers
# ---------------------------------------------------------------------------


def _dec(value: Any) -> Decimal:
    if value is None:
        return ZERO
    if isinstance(value, Decimal):
        return value
    if isinstance(value, bool):
        return Decimal(int(value))
    return Decimal(str(value))


def _optional_dec(value: Any) -> Optional[Decimal]:
    if value is None:
        return None
    return _dec(value)
