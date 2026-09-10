"""
Book Matching Engine - the IMatchingEngine implementation.

Scope, stated plainly
---------------------
This is a B-Book / internalisation engine plus a resting-order book for pending
orders. It is NOT a price-time-priority CLOB that nets client against client: the
user deferred the ECN, and a full CLOB is not what "can I place an order and get a
position" needs. What is here is honest about that:

  * a MARKET order fills immediately, against the broker, at the live quote;
  * a PENDING order rests, and `on_tick()` activates it when the market reaches its
    price, filling it at the price MT5 says it should fill at;
  * `execute_internal()` is the B-Book entry point the ExecutionOrchestrator calls.

Pricing rules (MT5)
-------------------
  * a client BUY is filled at the ASK, a client SELL at the BID. Getting this the
    other way round hands the client the spread on every trade and shows up as a
    broker that cannot lose money.
  * a BUY_LIMIT fills at its limit price or better; if the ask has already dropped to
    or below the limit, the client gets the better (lower) ask, not the limit.
  * a SELL_LIMIT fills at its limit price or better; if the bid has already risen to
    or above the limit, the client gets the better (higher) bid.
  * a BUY_STOP / SELL_STOP fills at the market price once triggered, never at the
    stop price - that is the point of a stop order.
  * a fill may not be worse than the requested price by more than `max_slippage`.
    Beyond that the order rests (or is rejected) rather than filled at a price the
    client never agreed to.

Where the price comes from
--------------------------
`market_feed.get_latest_tick(symbol)` when a feed is attached. With no feed the engine
still prices, from a configured quote or the symbol's own `spread` around the order
price, because the config plane is populated long before a price feed is - and an
engine that cannot price at all cannot be stood up and tested.
"""
from __future__ import annotations

import inspect
import itertools
import logging
from decimal import Decimal
from typing import Any, Callable, Dict, List, Optional

from core.domains.common.value_objects import Price, Volume
from core.domains.market_data.models import Tick
from core.domains.oms.entities.order import Order
from core.domains.oms.enums import OrderState, OrderType
from core.ports.interfaces import IMatchingEngine

logger = logging.getLogger(__name__)


class NoQuoteError(RuntimeError):
    """Raised when the engine cannot determine a fill price for a symbol.

    Deliberately not a silent fallback to the order price or to 1.0: an execution
    price invented by the engine is a position the client did not agree to.
    """


#: order types that fill against the market the moment they are accepted
_MARKET_TYPES = {OrderType.BUY, OrderType.SELL}

_BUY_SIDE = {OrderType.BUY, OrderType.BUY_LIMIT, OrderType.BUY_STOP, OrderType.BUY_STOP_LIMIT}


class BookMatchingEngine(IMatchingEngine):
    """Internalising matching engine with a resting book for pending orders."""

    def __init__(
        self,
        market_feed: Optional[Any] = None,
        symbol_repo: Optional[Any] = None,
        *,
        max_slippage_points: int = 0,
        event_bus: Optional[Any] = None,
    ) -> None:
        self.market_feed = market_feed
        self.symbol_repo = symbol_repo
        #: Slippage tolerance for stop orders, in points. ZERO MEANS NO LIMIT, the same
        #: convention Symbol.stops_level uses: a stop order becomes a market order when it
        #: triggers, and a market that has already moved past the trigger is the normal
        #: case, not an error. Treating 0 as "no tolerance" rejected every stop order that
        #: ever filled more than a point through its trigger.
        self.max_slippage_points = int(max_slippage_points)
        self.event_bus = event_bus

        #: symbol -> resting pending orders, in arrival order (price/time priority)
        self._books: Dict[str, List[Order]] = {}
        #: symbol -> (bid, ask) used when no live feed is attached
        self._quotes: Dict[str, tuple] = {}
        #: symbol -> spread in points, used to widen a mid into bid/ask
        self._spreads: Dict[str, int] = {}
        #: symbol -> tick_size, for converting points to price
        self._tick_sizes: Dict[str, Decimal] = {}
        #: notified with (order, fill_price) on every fill; the orchestrator registers
        #: the deal-recording handler here so ECN fills reach the ledger too
        self._fill_listeners: List[Callable[[Order, Decimal], Any]] = []

        self._sequence = itertools.count(1)
        self.fills: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Quotes
    # ------------------------------------------------------------------

    def set_quote(self, symbol: str, bid: Decimal, ask: Decimal, tick_size: Optional[Decimal] = None) -> None:
        """Install a quote for a symbol. Used when there is no live feed."""
        bid, ask = Decimal(str(bid)), Decimal(str(ask))
        if ask < bid:
            raise ValueError(f"ask {ask} below bid {bid} for {symbol}")
        self._quotes[symbol] = (bid, ask)
        if tick_size is not None:
            self._tick_sizes[symbol] = Decimal(str(tick_size))

    def set_spread(self, symbol: str, points: int, tick_size: Optional[Decimal] = None) -> None:
        """Configure the spread used to widen a mid price into bid/ask."""
        self._spreads[symbol] = int(points)
        if tick_size is not None:
            self._tick_sizes[symbol] = Decimal(str(tick_size))

    def _tick_size_for(self, symbol: str) -> Decimal:
        if symbol in self._tick_sizes:
            return self._tick_sizes[symbol]
        return Decimal("0.00001")

    def _tick(self, symbol: str) -> Optional[Any]:
        """Latest tick from whatever feed is attached, sync or async."""
        feed = self.market_feed
        if feed is None:
            return None
        getter = getattr(feed, "get_latest_tick", None)
        if getter is None:
            return None
        try:
            tick = getter(symbol)
        except Exception as exc:  # noqa: BLE001
            logger.warning("feed raised for %s: %s", symbol, exc)
            return None
        if inspect.isawaitable(tick):
            # price_order() is synchronous, so it cannot drain an async feed - but it does
            # not need to. Every async entry point calls _prime_quote() first, which
            # awaits the tick and installs it, so by the time this runs the quote is
            # already cached. Close the coroutine rather than leaking a RuntimeWarning.
            tick.close()
            return None
        return tick

    async def _prime_quote(self, symbol: str) -> None:
        """Refresh the cached quote from the feed, awaiting it if the feed is async.

        Called by every async entry point before pricing. This is what lets the engine
        work with both MarketDataEngine (synchronous, in-memory - the hot path) and an
        adapter whose get_latest_tick is a coroutine, without price_order() having to
        know which it was given.
        """
        from core.domains.market_data.feed_access import await_tick, tick_ask, tick_bid

        tick = await await_tick(self.market_feed, symbol)
        if tick is None:
            return
        bid, ask = tick_bid(tick), tick_ask(tick)
        if bid is None or ask is None:
            return
        bid, ask = Decimal(str(bid)), Decimal(str(ask))
        if bid > 0 and ask >= bid:
            self._quotes[symbol] = (bid, ask)

    def _quote_for(self, symbol: str, order: Optional[Order] = None) -> tuple:
        """Resolve (bid, ask) for a symbol, or raise NoQuoteError."""
        tick = self._tick(symbol)
        if tick is not None:
            bid = getattr(tick, "bid", None)
            ask = getattr(tick, "ask", None)
            if isinstance(tick, dict):
                bid = bid if bid is not None else tick.get("bid")
                ask = ask if ask is not None else tick.get("ask")
            if bid is not None and ask is not None:
                bid, ask = Decimal(str(bid)), Decimal(str(ask))
                if bid > 0 and ask >= bid:
                    self._quotes[symbol] = (bid, ask)
                    return bid, ask

        if symbol in self._quotes:
            return self._quotes[symbol]

        # No live tick and no installed quote: derive one from the symbol's configured
        # spread around the order price, so a freshly seeded server can still execute.
        mid: Optional[Decimal] = None
        if order is not None and order.price_order and order.price_order.value > 0:
            mid = order.price_order.value
        if mid is None and self.symbol_repo is not None:
            mid = self._symbol_reference_price(symbol)
        if mid is None:
            raise NoQuoteError(
                f"no quote for {symbol}: no tick on the feed, no configured quote, and no "
                f"order price to derive one from. Attach a feed or call set_quote()."
            )

        points = self._spreads.get(symbol)
        if points is None and self.symbol_repo is not None:
            points = self._symbol_spread(symbol)
        points = points or 0
        step = self._tick_size_for(symbol)
        half = (Decimal(points) * step) / Decimal(2)
        bid, ask = mid - half, mid + half
        if points == 0:
            bid = ask = mid
        if bid <= 0:
            raise NoQuoteError(f"derived bid for {symbol} is not positive ({bid})")
        self._quotes[symbol] = (bid, ask)
        return bid, ask

    def _symbol_reference_price(self, symbol_name: str) -> Optional[Decimal]:
        """Best-effort mid from the symbol config (async repo aware)."""
        getter = getattr(self.symbol_repo, "find_by_name", None)
        if getter is None:
            return None
        try:
            symbol = getter(symbol_name)
            if inspect.isawaitable(symbol):
                return None
        except Exception:  # noqa: BLE001
            return None
        return None

    def _symbol_spread(self, symbol_name: str) -> Optional[int]:
        getter = getattr(self.symbol_repo, "find_by_name_sync", None)
        if getter is None:
            return None
        try:
            symbol = getter(symbol_name)
        except Exception:  # noqa: BLE001
            return None
        return getattr(symbol, "spread", None)

    # ------------------------------------------------------------------
    # Pricing
    # ------------------------------------------------------------------

    def price_order(self, order: Order) -> Optional[Price]:
        """Fill price for this order right now, or None if it should rest.

        Returns None rather than raising for a pending order the market has not
        reached: resting is a normal outcome, not an error. Raises NoQuoteError only
        when no price at all can be determined.
        """
        bid, ask = self._quote_for(order.symbol, order)
        step = self._tick_size_for(order.symbol)
        # 0 = unlimited (see the constructor note); a positive value is a real tolerance.
        slip = (
            Decimal(self.max_slippage_points) * step
            if self.max_slippage_points > 0
            else None
        )
        otype = order.order_type
        limit = order.price_order.value if order.price_order else Decimal("0")
        trigger = order.price_trigger.value if order.price_trigger else limit

        if otype in _MARKET_TYPES:
            return Price(ask if otype in _BUY_SIDE else bid)

        # A LIMIT order has a hard price ceiling (buy) or floor (sell) and no slippage
        # tolerance applies to it: filling a limit worse than its limit is not slippage,
        # it is a breach of the client's instruction. Only the STOP branches below use
        # `slip`, because a stop becomes a market order and the market has already moved.
        if otype == OrderType.BUY_LIMIT:
            if limit <= 0:
                raise ValueError(f"BUY_LIMIT {order.ticket_id} has no limit price")
            if ask <= limit:
                # better of the two: the client never pays more than the limit
                return Price(min(ask, limit))
            return None

        if otype == OrderType.SELL_LIMIT:
            if limit <= 0:
                raise ValueError(f"SELL_LIMIT {order.ticket_id} has no limit price")
            if bid >= limit:
                return Price(max(bid, limit))
            return None

        if otype == OrderType.BUY_STOP:
            if trigger <= 0:
                raise ValueError(f"BUY_STOP {order.ticket_id} has no stop price")
            if ask >= trigger:
                if slip is not None and ask > trigger + slip:
                    raise NoQuoteError(
                        f"BUY_STOP {order.ticket_id} would fill at {ask}, more than "
                        f"{self.max_slippage_points} points beyond its stop {trigger}"
                    )
                return Price(ask)
            return None

        if otype == OrderType.SELL_STOP:
            if trigger <= 0:
                raise ValueError(f"SELL_STOP {order.ticket_id} has no stop price")
            if bid <= trigger:
                if slip is not None and bid + slip < trigger:
                    raise NoQuoteError(
                        f"SELL_STOP {order.ticket_id} would fill at {bid}, more than "
                        f"{self.max_slippage_points} points beyond its stop {trigger}"
                    )
                return Price(bid)
            return None

        if otype in (OrderType.BUY_STOP_LIMIT, OrderType.SELL_STOP_LIMIT):
            # Armed once the trigger is reached, then it behaves as the corresponding
            # limit. Modelled as one step: arm and price in the same call.
            if otype == OrderType.BUY_STOP_LIMIT:
                if ask >= trigger:
                    # armed: now a limit, so the limit price still caps it
                    if limit > 0 and ask > limit:
                        return None
                    return Price(min(ask, limit)) if limit > 0 else Price(ask)
                return None
            if bid <= trigger:
                if limit > 0 and bid < limit:
                    return None
                return Price(max(bid, limit)) if limit > 0 else Price(bid)
            return None

        raise ValueError(f"matching engine cannot price order type {otype}")

    # ------------------------------------------------------------------
    # IMatchingEngine
    # ------------------------------------------------------------------

    async def execute_internal(self, order: Order, *, record: bool = True) -> Price:
        """B-Book fill price: the broker is the counterparty, so it is immediate.

        This is the method the ExecutionOrchestrator calls for a B_BOOK destination.
        It is not on the original IMatchingEngine port - the orchestrator called a
        method no engine had, which is why the execution path had never run.

        `record=False` prices without touching the order or the fill log, for a caller
        that owns the state transition itself (the orchestrator does: RecordDealHandler
        applies the fill and moves the order to FILLED). Pricing twice, or letting the
        engine and the handler each half-apply a fill, is how an order ends up
        PARTIALLY_FILLED with no deal behind it.
        """
        await self._prime_quote(order.symbol)
        price = self.price_order(order)
        if price is None:
            raise NoQuoteError(
                f"order {order.ticket_id} ({order.order_type.value}) cannot be internalised: "
                f"the market has not reached its price"
            )
        if record:
            self._record_fill(order, price, venue="B_BOOK")
        return price

    async def submit_order(self, order: Order) -> None:
        """Submit to the book: fill immediately if it crosses, otherwise rest it."""
        await self._prime_quote(order.symbol)
        try:
            price = self.price_order(order)
        except NoQuoteError as exc:
            logger.error("cannot price order %s: %s", order.ticket_id, exc)
            raise

        if price is not None:
            self._record_fill(order, price, venue="IN_HOUSE")
            await self._notify_listeners(order, price)
            return

        book = self._books.setdefault(order.symbol, [])
        book.append(order)
        if order.state in (OrderState.STARTED, OrderState.NEW):
            order.state = OrderState.PLACED
        logger.info(
            "order %s resting in book for %s at %s",
            order.ticket_id,
            order.symbol,
            order.price_order.value if order.price_order else None,
        )

    async def cancel_order(self, order_id: str) -> bool:
        """Remove a resting order. Returns False if it was not in the book."""
        for symbol, book in self._books.items():
            for order in list(book):
                if order.ticket_id == order_id:
                    book.remove(order)
                    logger.info("order %s cancelled out of the %s book", order_id, symbol)
                    return True
        return False

    async def modify_order(self, order_id: str, new_price: Decimal, new_quantity: int) -> bool:
        """Cancel/replace a resting order, the way a strict FIFO engine must.

        MT5 does not move an order in the book: modifying it loses its queue position.
        Doing the same here keeps the book's price/time priority meaningful.
        """
        target: Optional[Order] = None
        for book in self._books.values():
            for order in book:
                if order.ticket_id == order_id:
                    target = order
                    break
            if target:
                break
        if target is None:
            return False

        await self.cancel_order(order_id)
        target.price_order = Price(Decimal(str(new_price)))
        if new_quantity:
            target.volume_initial = Volume(Decimal(str(new_quantity)))
            target.volume_current = Volume(Decimal(str(new_quantity)))
        await self.submit_order(target)
        return True

    def get_market_state(self, symbol: str) -> dict:
        """Current book state for a symbol, for pre-trade checks and visibility."""
        resting = self._books.get(symbol, [])
        bid, ask = self._quotes.get(symbol, (None, None))
        return {
            "symbol": symbol,
            "bid": str(bid) if bid is not None else None,
            "ask": str(ask) if ask is not None else None,
            "resting_orders": len(resting),
            "buy_orders": sum(1 for o in resting if o.order_type in _BUY_SIDE),
            "sell_orders": sum(1 for o in resting if o.order_type not in _BUY_SIDE),
            "total_resting_volume": str(sum((o.volume_current.value for o in resting), Decimal("0"))),
        }

    # ------------------------------------------------------------------
    # Tick-driven activation of resting orders
    # ------------------------------------------------------------------

    async def on_tick(self, tick: Any) -> List[tuple]:
        """Walk the resting book for this symbol against a new price.

        Returns the (order, fill_price) pairs that filled, in book order. Called by
        the tick pipeline; a server with no pending orders does no work here.
        """
        symbol = getattr(tick, "symbol", None) or (tick.get("symbol") if isinstance(tick, dict) else None)
        if not symbol:
            return []

        bid = getattr(tick, "bid", None)
        ask = getattr(tick, "ask", None)
        if isinstance(tick, dict):
            bid = bid if bid is not None else tick.get("bid")
            ask = ask if ask is not None else tick.get("ask")
        if bid is None or ask is None:
            return []
        self._quotes[symbol] = (Decimal(str(bid)), Decimal(str(ask)))

        book = self._books.get(symbol)
        if not book:
            return []

        filled: List[tuple] = []
        for order in list(book):
            try:
                price = self.price_order(order)
            except NoQuoteError as exc:
                # A stop that gaps through its trigger is not the book's fault, but it
                # must not be silently dropped either: leave it resting and say so.
                logger.error("resting order %s could not fill on tick: %s", order.ticket_id, exc)
                continue
            if price is None:
                continue
            book.remove(order)
            self._record_fill(order, price, venue="IN_HOUSE")
            await self._notify_listeners(order, price)
            filled.append((order, price))
        return filled

    # ------------------------------------------------------------------
    # Fill plumbing
    # ------------------------------------------------------------------

    def on_fill(self, listener: Callable[[Order, Decimal], Any]) -> None:
        """Register a listener invoked with (order, fill_price) on every fill."""
        self._fill_listeners.append(listener)

    def _record_fill(self, order: Order, price: Price, venue: str) -> None:
        self.fills.append(
            {
                "sequence": next(self._sequence),
                "order_id": order.ticket_id,
                "account_login": order.account_login,
                "symbol": order.symbol,
                "side": order.order_type.value,
                "volume": str(order.volume_current.value),
                "price": str(price.value),
                "venue": venue,
            }
        )
        logger.info(
            "filled %s %s %s lots at %s (%s)",
            order.ticket_id,
            order.order_type.value,
            order.volume_current.value,
            price.value,
            venue,
        )

    async def _notify_listeners(self, order: Order, price: Price) -> None:
        for listener in list(self._fill_listeners):
            try:
                result = listener(order, price.value)
                if inspect.isawaitable(result):
                    await result
            except Exception as exc:  # noqa: BLE001
                logger.error("fill listener raised for %s: %s", order.ticket_id, exc, exc_info=True)


__all__ = ["BookMatchingEngine", "NoQuoteError"]
