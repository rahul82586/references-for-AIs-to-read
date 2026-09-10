"""
Step M3 part 3 - RiskEngine, rewritten against the real domain entities.

FOUR DEFECTS, all of which made the risk engine return silently wrong numbers rather
than failing:

1. WRONG ENTITY API. It read `position.side.name`, `position.average_price.value` and
   `position.id`. The real Position has `action`, `price_open` and `position_id`. Every
   position therefore raised AttributeError, which the bare `except Exception` caught and
   turned into `has_calculation_error = True`, so margin and PnL came back as ZERO and
   the account was marked BLOCKED. A risk engine that reports zero margin never stops
   anything out.

   The stale names came from the duplicate PositionModel that M0 deleted - the engine was
   written against the old database model, not the domain entity.

2. `has_calculation_error` was assigned only inside `except`, so the happy path - no
   position raising - hit `NameError`/`UnboundLocalError` when it reached the line that
   read it.

3. NO CROSS-RATE TRIANGULATION. `get_conversion_rate` tried only `{quote}{account}`
   then `{account}{quote}`. For a EURJPY position on a USD account neither is EURUSD, so
   it raised - and both lookups were wrapped in `except Exception: pass`, making a
   genuine feed error indistinguishable from a missing pair. Measured: JPY->USD resolved,
   EUR->USD / AUD->USD / CHF->USD all raised. Cross pairs are exactly the case
   opencode_summery.md flagged in the original audit.

4. PnL was valued with `price_diff * volume * contract_size` and NO conversion, so every
   JPY/CHF/CAD and cross-pair position reported its PnL in the wrong currency - a JPY
   profit read as a USD profit, overstating equity by ~150x and making stop-outs
   unreachable.

The replacement delegates all arithmetic to core.domains.market_data.margin, which
carries MT5's formulas and is tested against MT5's own published examples. This module
now only does what a risk engine should: gather positions, resolve prices, and decide.

Also: exceptions are no longer swallowed. A position that cannot be valued raises, so an
account whose margin cannot be computed is rejected rather than approved on a zero.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
if not (ROOT / "core" / "domains" / "risk" / "engine.py").is_file():
    raise SystemExit(f"not a broker-platform root: {ROOT}")

ENGINE = '''"""
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
    ) -> Decimal:
        """Rate to convert an amount in ``from_currency`` into ``to_currency``.

        Tries, in order:
          1. the direct pair   {from}{to}   at its bid
          2. the inverse pair  {to}{from}   as 1 / ask
          3. TRIANGULATION through an intermediate currency: from->X and X->to, so that a
             EURJPY position on a USD account resolves via EURUSD. This is the case the
             original audit flagged and the previous implementation could not do at all.

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
            direct = self._pair_rate(from_currency, to_currency)
            if direct is not None:
                return direct

            for intermediate in TRIANGULATION_CURRENCIES:
                if intermediate in (from_currency, to_currency):
                    continue
                first = self._pair_rate(from_currency, intermediate)
                if first is None:
                    continue
                second = self._pair_rate(intermediate, to_currency)
                if second is None:
                    continue
                return first * second
        finally:
            self.market_data_engine = previous_engine

        raise CurrencyConversionError(
            f"no rate for {from_currency} -> {to_currency}, direct, inverse or via "
            f"{', '.join(TRIANGULATION_CURRENCIES)}"
        )

    def _pair_rate(self, from_currency: str, to_currency: str) -> Optional[Decimal]:
        """Direct or inverse rate for one currency pair, or None if unavailable."""
        direct = f"{from_currency}{to_currency}"
        try:
            bid = self._side_price(direct, "bid", fresh=False)
            if bid > 0:
                return bid
        except (PositionValuationError, StaleQuoteError):
            pass

        inverse = f"{to_currency}{from_currency}"
        try:
            ask = self._side_price(inverse, "ask", fresh=False)
            if ask > 0:
                return Decimal("1") / ask
        except (PositionValuationError, StaleQuoteError):
            pass
        return None

    def _rate_lookup(self, from_currency: str, to_currency: str, side: str) -> Decimal:
        """Adapter matching the callable signature core.domains.market_data.margin wants."""
        return self.get_conversion_rate(from_currency, to_currency)

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
            equity = account.balance.amount + account.credit.amount
            remaining_margin = account.margin_used.amount
            for pnl, position in valued:
                if remaining_margin <= Decimal("0"):
                    break
                level = compute_margin_level(equity, remaining_margin)
                if level >= stop_level:
                    # Margin has recovered; closing more would liquidate positions the
                    # client did not need to lose.
                    break
                selected.append(position)
                # Closing realises the loss, so equity does not improve; what improves is
                # the margin requirement. Recompute it over the positions still open.
                equity += pnl
                still_open = [p for _, p in valued if p not in selected]
                remaining_margin = self._maintenance_margin(account, still_open)
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
'''

path = ROOT / "core" / "domains" / "risk" / "engine.py"
path.write_text(ENGINE, encoding="utf-8")
print("  ok  core/domains/risk/engine.py: rewritten against the real entities + MT5 engine")

# liquidation_worker must stop hardcoding the conversion rate.
WORKER = "application/workers/liquidation_worker.py"
with open(ROOT / WORKER, encoding="utf-8", newline="") as fh:
    text = fh.read()
crlf = "\r\n" in text
work = text.replace("\r\n", "\n")

# The worker holds symbol_repo and market_data_feed but no RiskEngine, so build one from
# what it has. Constructed once per liquidation, not per symbol.
old_setup = """        conversion_rates = {}"""
new_setup = """        conversion_rates = {}
        # Built from the repositories this worker already holds. The engine is what
        # resolves cross rates, including the triangulation a JPY or AUD position needs
        # on a USD account; the hardcoded Decimal('1.0') it replaces assumed every
        # position's quote currency was the account currency.
        from core.domains.risk.engine import RiskEngine

        conversion_engine = RiskEngine(
            symbol_repo=self.symbol_repo, market_data_engine=self.market_data_feed
        )"""
if old_setup in work:
    work = work.replace(old_setup, new_setup, 1)
else:
    raise SystemExit("[FAIL] liquidation_worker.py: could not find the conversion_rates setup line")

OLD = '''            conversion_rates[symbol_name] = Decimal('1.0')  # Assume same currency for now'''
if OLD in work:
    NEW = '''            # Resolve the real rate. Hardcoding 1.0 here made worst-loss-first sort on
            # UNCONVERTED PnL, so on a USD account a -100,000 JPY loss (~-$667) ranked as
            # worse than a -$900 loss and the wrong position was closed first.
            try:
                conversion_rates[symbol_name] = conversion_engine.get_conversion_rate(
                    getattr(symbol, "quote_currency", "") or account.currency,
                    account.currency,
                )
            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "cannot resolve %s -> %s for liquidation of %s; skipping rather than "
                    "sorting on an unconverted PnL: %s",
                    getattr(symbol, "quote_currency", "?"),
                    account.currency,
                    symbol_name,
                    exc,
                )
                continue'''
    work = work.replace(OLD, NEW, 1)
    with open(ROOT / WORKER, "w", encoding="utf-8", newline="") as fh:
        fh.write(work.replace("\n", "\r\n") if crlf else work)
    print(f"  ok  {WORKER}: conversion rate resolved instead of hardcoded to 1.0")
else:
    print(f"  skip {WORKER}: the hardcoded 1.0 conversion was not found")
