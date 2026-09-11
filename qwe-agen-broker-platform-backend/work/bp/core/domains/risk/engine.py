"""
Risk engine - margin level, stop-out detection and liquidation selection.

All arithmetic lives in `core.domains.market_data.margin`, which implements MT5's
published formulas and is tested against MT5's own worked examples. This module gathers
positions, resolves prices and rates, and makes decisions. It does not re-derive a
formula, because three previous copies of the formula disagreed with each other and with
MT5.

TWO RULES THAT ARE EASY TO GET WRONG

  * A BUY position is valued at the BID and a SELL at the ASK - the price the broker
    would actually transact at to close it. Valuing both at the same side hands the
    spread to someone on every position.
  * PnL and margin are computed in the SYMBOL's quote/margin currency and then converted
    to the account's deposit currency. Assuming quote == deposit is what made every JPY,
    CHF, CAD and cross-pair figure wrong.

Nothing here swallows an exception. A position that cannot be valued makes the
calculation fail, because a margin figure of zero means "no stop-out ever fires".
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional, Sequence

from core.domains.market_data.margin import (
    Leg,
    MarginCalculationError,
    SymbolMarginSpec,
    calculate_account_margin,
    margin_level as compute_margin_level,
    position_pnl,
)

from ..accounts.models import Account
from ..oms.entities.position import Position
from ...ports.interfaces import IMarketDataFeed, ISymbolRepository
from .models import MarginSnapshot, RiskStatus

logger = logging.getLogger(__name__)

#: A quote older than this is not usable for margin or liquidation decisions.
MAX_QUOTE_AGE_SECONDS = 10.0


class StaleQuoteError(ValueError):
    """Raised when a market data quote is older than the allowed threshold."""


class CurrencyConversionError(Exception):
    """Raised when a required exchange rate cannot be resolved.

    Never silently treated as 1.0: that is the defect which made every non-USD-quote
    position report its PnL in the wrong currency.
    """


class PositionValuationError(Exception):
    """Raised when a position cannot be valued. Carries the symbol so it is actionable."""


#: Currencies tried as the intermediate leg when triangulating a cross rate.
#: Ordered by how commonly they are the quote leg of a real symbol list.
TRIANGULATION_CURRENCIES = ("USD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD")


class RiskEngine:
    """Margin and stop-out logic for a single account.

    Constructed with a symbol repository (for contract sizes, calc modes and margin
    rates) and something that can answer "what is the current bid/ask for X" - either a
    MarketDataEngine with `get_latest_tick`, or a legacy feed with `get_bid`/`get_ask`.
    """

    def __init__(
        self,
        symbol_repo: Optional[ISymbolRepository] = None,
        market_data_engine: Optional[Any] = None,
        *,
        max_quote_age_seconds: float = MAX_QUOTE_AGE_SECONDS,
    ) -> None:
        self.symbol_repo = symbol_repo
        self.market_data_engine = market_data_engine
        self.max_quote_age_seconds = max_quote_age_seconds

    # ------------------------------------------------------------------
    # Market data
    # ------------------------------------------------------------------

    def _tick(self, symbol: str) -> Optional[Any]:
        engine = self.market_data_engine
        if engine is None:
            return None
        getter = getattr(engine, "get_latest_tick", None)
        if getter is None:
            return None
        return getter(symbol)

    def _verify_tick_freshness(self, symbol: str, tick: Any) -> None:
        if tick is None:
            raise StaleQuoteError(f"no market tick available for symbol {symbol}")
        tick_ts = tick.get("timestamp") if isinstance(tick, dict) else getattr(tick, "timestamp", None)
        if tick_ts is None:
            return
        now = datetime.now(timezone.utc)
        if tick_ts.tzinfo is None:
            tick_ts = tick_ts.replace(tzinfo=timezone.utc)
        age = (now - tick_ts).total_seconds()
        if age > self.max_quote_age_seconds:
            raise StaleQuoteError(
                f"quote for {symbol} is stale ({age:.1f}s > {self.max_quote_age_seconds}s)"
            )

    def _side_price(self, symbol: str, side: str, *, fresh: bool = True) -> Decimal:
        """Current bid or ask for a symbol, as a Decimal.

        Raises rather than returning None or zero: a missing price means margin cannot be
        computed, and zero would read as "this position needs no margin".
        """
        tick = self._tick(symbol)
        if tick is not None:
            if fresh:
                self._verify_tick_freshness(symbol, tick)
            raw = tick.get(side) if isinstance(tick, dict) else getattr(tick, side, None)
            if raw is not None:
                value = Decimal(str(raw))
                if value > 0:
                    return value
        getter = getattr(self.market_data_engine, f"get_{side}", None)
        if getter is not None:
            raw = getter(symbol)
            if raw is not None:
                value = Decimal(str(raw))
                if value > 0:
                    return value
        raise PositionValuationError(f"no usable {side} price for {symbol}")

    def get_bid(self, symbol: str) -> Decimal:
        return self._side_price(symbol, "bid")

    def get_ask(self, symbol: str) -> Decimal:
        return self._side_price(symbol, "ask")

    # ------------------------------------------------------------------
    # Currency conversion, with triangulation
    # ------------------------------------------------------------------

    def get_conversion_rate(
        self,
        from_currency: str,
        to_currency: str,
        market_feed: Optional[Any] = None,
        side: str = "BUY",
    ) -> Decimal:
        """Rate to convert an amount in ``from_currency`` into ``to_currency``.

        Tries, in order:
          1. the direct pair   {from}{to}
          2. the inverse pair  {to}{from}, inverted
          3. TRIANGULATION through an intermediate currency: from->X and X->to, so that a
             EURJPY position on a USD account resolves via EURUSD. This is the case the
             original audit flagged and the previous implementation could not do at all.

        Which half of the spread is used depends on ``side``, per MT5: "The Ask price is
        used for buy deals, and the Bid price is used for sell deals." ``side="PROFIT"``
        is used for PnL conversion, where gains and losses must convert at the SAME rate
        or equity would depend on its own sign.

        Raises CurrencyConversionError when nothing resolves. It never returns 1.0 as a
        guess, and it no longer wraps lookups in `except Exception: pass`, which made a
        broken feed indistinguishable from a missing pair.
        """
        if not from_currency or not to_currency or from_currency == to_currency:
            return Decimal("1")

        feed = market_feed or self.market_data_engine
        if feed is None:
            raise CurrencyConversionError(
                f"cannot convert {from_currency} -> {to_currency}: no market feed"
            )
        previous_engine = self.market_data_engine
        if market_feed is not None:
            self.market_data_engine = market_feed
        try:
            direct = self._pair_rate(from_currency, to_currency, side)
            if direct is not None:
                return direct

            for intermediate in TRIANGULATION_CURRENCIES:
                if intermediate in (from_currency, to_currency):
                    continue
                first = self._pair_rate(from_currency, intermediate, side)
                if first is None:
                    continue
                second = self._pair_rate(intermediate, to_currency, side)
                if second is None:
                    continue
                return first * second
        finally:
            self.market_data_engine = previous_engine

        raise CurrencyConversionError(
            f"no rate for {from_currency} -> {to_currency}, direct, inverse or via "
            f"{', '.join(TRIANGULATION_CURRENCIES)}"
        )

    #: Suffixes some servers append to a bare currency pair. Tried after the plain name.
    PAIR_SUFFIXES = ("", ".spot", ".m", "_", "-")

    def _pair_rate(
        self, from_currency: str, to_currency: str, side: str = "BUY"
    ) -> Optional[Decimal]:
        """Direct or inverse rate for one currency pair, or None if unavailable.

        A symbol named exactly "{from}{to}" is the normal case - EURUSD for EUR -> USD -
        so this resolves most conversions with no triangulation.

        Which side of the spread is taken follows MT5: the ASK for buy deals, the BID for
        sell deals. Inverting the pair swaps the side, because the broker's ask on USDJPY
        is the broker's bid on JPYUSD - so an inverse lookup for a buy takes 1/BID.

        "PROFIT" is the PnL case: one rate for gains and losses alike, so that equity does
        not depend on its own sign.
        """
        want_ask = str(side).upper().startswith("BUY")
        for suffix in self.PAIR_SUFFIXES:
            direct = f"{from_currency}{to_currency}{suffix}"
            try:
                price = self._side_price(direct, "ask" if want_ask else "bid", fresh=False)
                if price > 0:
                    return price
            except (PositionValuationError, StaleQuoteError):
                pass

            inverse = f"{to_currency}{from_currency}{suffix}"
            try:
                price = self._side_price(inverse, "bid" if want_ask else "ask", fresh=False)
                if price > 0:
                    return Decimal("1") / price
            except (PositionValuationError, StaleQuoteError):
                pass
        return None

    def _rate_lookup(self, from_currency: str, to_currency: str, side: str) -> Decimal:
        """Adapter matching the callable signature core.domains.market_data.margin wants.

        ``side`` is not decoration. MT5 converts a BUY deal's margin at the ASK and a SELL
        deal's at the BID, so dropping it - as this did - understated every buy's margin
        requirement by the width of the spread.
        """
        return self.get_conversion_rate(from_currency, to_currency, side=side)

    # ------------------------------------------------------------------
    # Symbols
    # ------------------------------------------------------------------

    def _symbol(self, symbol_name: str) -> Optional[Any]:
        repo = self.symbol_repo
        if repo is None:
            return None
        for name in ("get_symbol", "find_by_name"):
            getter = getattr(repo, name, None)
            if getter is None:
                continue
            result = getter(symbol_name)
            if hasattr(result, "__await__"):
                raise PositionValuationError(
                    f"{name}() on the symbol repository is async; RiskEngine needs a "
                    "synchronous lookup on the hot path (this is what ConfigCache is for)"
                )
            if result is not None:
                return result
        return None

    def _spec(self, symbol_name: str) -> SymbolMarginSpec:
        symbol = self._symbol(symbol_name)
        if symbol is None:
            raise PositionValuationError(
                f"symbol {symbol_name} is not configured; cannot compute margin for it"
            )
        return SymbolMarginSpec.from_symbol(symbol)

    # ------------------------------------------------------------------
    # Margin level
    # ------------------------------------------------------------------

    def calculate_position_pnl(self, account: Account, position: Position) -> Decimal:
        """Unrealised PnL for ONE position, in the account's deposit currency.

        The same single source of truth calculate_margin_level uses
        (margin.position_pnl): side-correct bid/ask, the symbol's contract size,
        and quote->deposit conversion. Added in M5 because the client positions
        query carried its own PRE-M3 formula (pos.side / pos.average_price, no
        currency conversion) on an endpoint nothing had ever called - the sixth
        independent copy of the PnL maths, in the layer that reads money.
        """
        spec = self._spec(position.symbol)
        symbol = self._symbol(position.symbol)
        quote_currency = getattr(symbol, "quote_currency", "") or spec.margin_currency
        action = (
            position.action.value
            if hasattr(position.action, "value")
            else str(position.action)
        )
        return position_pnl(
            side=action,
            volume_lots=position.volume.value,
            open_price=position.price_open.value,
            bid=self._side_price(position.symbol, "bid"),
            ask=self._side_price(position.symbol, "ask"),
            contract_size=spec.contract_size,
            quote_currency=quote_currency,
            deposit_currency=account.currency,
            rate_lookup=self._rate_lookup,
        )

    def realized_pnl(
        self,
        account: Account,
        position: Position,
        close_price: Decimal,
        closed_volume: Decimal,
    ) -> Decimal:
        """PnL realised by closing `closed_volume` lots of `position` at `close_price`.

        Returned in the ACCOUNT's deposit currency. This is position_pnl with the
        deal price on the closing side (a long is closed by selling, at its bid;
        a short by buying, at its ask), so quote->deposit conversion uses exactly
        the machinery the margin loop uses - no second formula, and no raw
        quote-currency amount ever lands on a balance.
        """
        spec = self._spec(position.symbol)
        symbol = self._symbol(position.symbol)
        quote_currency = getattr(symbol, "quote_currency", "") or spec.margin_currency
        action = (
            position.action.value
            if hasattr(position.action, "value")
            else str(position.action)
        )
        return position_pnl(
            side=action,
            volume_lots=closed_volume,
            open_price=position.price_open.value,
            bid=close_price,
            ask=close_price,
            contract_size=spec.contract_size,
            quote_currency=quote_currency,
            deposit_currency=account.currency,
            rate_lookup=self._rate_lookup,
        )

    def calculate_margin_level(
        self, account: Account, positions: Sequence[Position]
    ) -> MarginSnapshot:
        """Real-time margin level for an account (the fast local layer).

        Equity is balance + credit + unrealised PnL, matching MT5 and matching what
        Account.update_equity already does - the previous implementation here omitted
        credit, so a client trading on broker credit looked poorer than they were.

        Margin is MT5 MAINTENANCE margin over the open positions, aggregated per symbol
        with netting and hedged volume handled by the engine.
        """
        unrealized = Decimal("0")
        legs: List[Leg] = []
        specs: Dict[str, SymbolMarginSpec] = {}

        for position in positions:
            symbol_name = position.symbol
            spec = self._spec(symbol_name)
            specs[symbol_name] = spec

            symbol = self._symbol(symbol_name)
            quote_currency = getattr(symbol, "quote_currency", "") or spec.margin_currency
            action = position.action.value if hasattr(position.action, "value") else str(position.action)

            bid = self._side_price(symbol_name, "bid")
            ask = self._side_price(symbol_name, "ask")
            pnl = position_pnl(
                side=action,
                volume_lots=position.volume.value,
                open_price=position.price_open.value,
                bid=bid,
                ask=ask,
                contract_size=spec.contract_size,
                quote_currency=quote_currency,
                deposit_currency=account.currency,
                rate_lookup=self._rate_lookup,
            )
            unrealized += pnl

            legs.append(
                Leg(
                    symbol=symbol_name,
                    operation=action,
                    volume=position.volume.value,
                    price=position.price_open.value,
                    is_pending=False,
                    spec=spec,
                )
            )

        leverage = account.effective_leverage()
        breakdown = calculate_account_margin(
            legs,
            specs=specs,
            deposit_currency=account.currency,
            rate_lookup=self._rate_lookup,
            leverage=leverage,
            maintenance=True,
        )

        equity = account.balance.amount + account.credit.amount + unrealized
        margin_used = breakdown.total
        level = compute_margin_level(equity, margin_used)
        margin_free = equity - margin_used

        if margin_used <= Decimal("0"):
            status = RiskStatus.NORMAL
        else:
            profile = getattr(account.group, "margin", None) if account.group else None
            call_level = Decimal(str(profile.margin_call_level)) if profile else Decimal("80")
            stop_level = Decimal(str(profile.stop_out_level)) if profile else Decimal("50")
            if level < stop_level:
                status = RiskStatus.STOPPED_OUT
            elif level < call_level:
                status = RiskStatus.MARGIN_CALL
            else:
                status = RiskStatus.NORMAL

        return MarginSnapshot(
            account_login=str(account.login),
            balance=account.balance.amount,
            equity=equity,
            margin_used=margin_used,
            margin_free=margin_free,
            margin_level=level,
            status=status,
        )

    # ------------------------------------------------------------------
    # Thresholds
    # ------------------------------------------------------------------

    def _thresholds(self, account: Account) -> "tuple[Decimal, Decimal]":
        """(margin_call, stop_out) in PERCENT, from group.margin.*.

        The previous code read `account.group.margin_call_level`, which does not exist -
        the fields live on the nested MarginProfile - so both detect_* methods raised
        AttributeError on every call and risk_worker was dead code.
        """
        profile = getattr(account.group, "margin", None) if account.group else None
        if profile is None:
            return Decimal("80"), Decimal("50")
        return Decimal(str(profile.margin_call_level)), Decimal(str(profile.stop_out_level))

    def detect_margin_call(self, account: Account, snapshot: MarginSnapshot) -> bool:
        call_level, _ = self._thresholds(account)
        return snapshot.margin_level < call_level

    def detect_stop_out(self, account: Account, snapshot: MarginSnapshot) -> bool:
        _, stop_level = self._thresholds(account)
        return snapshot.margin_level < stop_level

    # ------------------------------------------------------------------
    # Liquidation selection
    # ------------------------------------------------------------------

    def select_positions_for_liquidation(
        self,
        account: Account,
        positions: Sequence[Position],
        symbol_repo: Optional[ISymbolRepository] = None,
        market_feed: Optional[IMarketDataFeed] = None,
    ) -> List[Position]:
        """Positions to close, worst loss first, stopping once margin recovers.

        MT5: "Close worst-loss positions first until margin level recovers." The previous
        implementation sorted correctly but returned EVERY position, so any stop-out
        liquidated the whole account instead of the least of it.

        PnL is converted to the deposit currency before sorting. The previous version
        sorted on unconverted PnL, so on a USD account a -100,000 JPY loss (~-$667)
        ranked as worse than a -$900 loss and the wrong position was closed first.
        """
        previous_repo = self.symbol_repo
        previous_engine = self.market_data_engine
        if symbol_repo is not None:
            self.symbol_repo = symbol_repo
        if market_feed is not None:
            self.market_data_engine = market_feed
        try:
            _, stop_level = self._thresholds(account)

            valued: List["tuple[Decimal, Position]"] = []
            for position in positions:
                symbol_name = position.symbol
                spec = self._spec(symbol_name)
                symbol = self._symbol(symbol_name)
                quote_currency = getattr(symbol, "quote_currency", "") or spec.margin_currency
                action = (
                    position.action.value
                    if hasattr(position.action, "value")
                    else str(position.action)
                )
                bid = self._side_price(symbol_name, "bid")
                ask = self._side_price(symbol_name, "ask")
                pnl = position_pnl(
                    side=action,
                    volume_lots=position.volume.value,
                    open_price=position.price_open.value,
                    bid=bid,
                    ask=ask,
                    contract_size=spec.contract_size,
                    quote_currency=quote_currency,
                    deposit_currency=account.currency,
                    rate_lookup=self._rate_lookup,
                )
                valued.append((pnl, position))

            # Worst loss first.
            valued.sort(key=lambda item: item[0])

            selected: List[Position] = []
            # Start from the maintenance margin computed from the positions in front of
            # us, NOT from account.margin_used. That field is a stored figure - whatever
            # the last recalculation wrote - so it is zero on an account built outside the
            # deal-recording path and stale on a live one. Seeding from it made the loop's
            # first check, `remaining_margin <= 0`, break immediately and return an empty
            # selection: an account at -889% margin level liquidated nothing.
            #
            # Every position has already been valued above in order to sort worst-loss
            # first, so the requirement is available here at no extra cost.
            equity = account.balance.amount + account.credit.amount
            remaining_margin = self._maintenance_margin(account, list(positions))
            # Equity includes the unrealised PnL of the positions still open; that is
            # what MT5's margin level compares against the requirement.
            unrealized = sum((pnl for pnl, _ in valued), Decimal("0"))
            equity += unrealized

            for pnl, position in valued:
                if remaining_margin <= Decimal("0"):
                    break
                level = compute_margin_level(equity, remaining_margin)
                if level >= stop_level:
                    # Margin has recovered; closing more would liquidate positions the
                    # client did not need to lose.
                    break
                selected.append(position)
                # Closing REALISES the PnL: the unrealised amount already counted in
                # equity becomes a realised one, so equity is unchanged by the act of
                # closing. What improves is the margin requirement, which falls as the
                # position leaves the book. Adding pnl here again - as this did - counted
                # every loss twice and drove equity far below its real value, which would
                # have liquidated more positions than necessary.
                still_open = [p for _, p in valued if p not in selected]
                remaining_margin = self._maintenance_margin(account, still_open)
                unrealized -= pnl
            return selected
        finally:
            self.symbol_repo = previous_repo
            self.market_data_engine = previous_engine

    def _maintenance_margin(self, account: Account, positions: Sequence[Position]) -> Decimal:
        """Maintenance margin over a set of positions, for the recovery loop."""
        if not positions:
            return Decimal("0")
        legs: List[Leg] = []
        specs: Dict[str, SymbolMarginSpec] = {}
        for position in positions:
            spec = self._spec(position.symbol)
            specs[position.symbol] = spec
            action = (
                position.action.value if hasattr(position.action, "value") else str(position.action)
            )
            legs.append(
                Leg(
                    symbol=position.symbol,
                    operation=action,
                    volume=position.volume.value,
                    price=position.price_open.value,
                    is_pending=False,
                    spec=spec,
                )
            )
        breakdown = calculate_account_margin(
            legs,
            specs=specs,
            deposit_currency=account.currency,
            rate_lookup=self._rate_lookup,
            leverage=account.effective_leverage(),
            maintenance=True,
        )
        return breakdown.total
