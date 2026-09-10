"""
Feed access helpers - the one place that knows how to read a price.

Why this module exists
----------------------
Two shapes of "market data feed" are in circulation and the call sites disagree about
them:

  * `MarketDataEngine.get_latest_tick(symbol)` is SYNCHRONOUS - it reads an in-memory
    dict, which is the whole point of the hot path;
  * the test doubles and some adapters declare `async def get_latest_tick(symbol)`.

`record_deal` and `liquidation_worker` both did `await feed.get_latest_tick(symbol)`.
Against the real engine that awaits a `Tick` (or `None`), which raises
`TypeError: object Tick can't be used in 'await' expression` - on the write path that
records every fill, and on the path that closes positions at stop-out. Neither had
ever run against a real engine.

`await_tick()` accepts either shape, so the callers stop having to know which feed
they were given. It also tolerates the legacy `get_bid`/`get_ask` interface, which is
what `IMarketDataFeed` still declares.
"""
from __future__ import annotations

import inspect
from typing import Any, Optional

__all__ = ["await_tick", "tick_bid", "tick_ask", "tick_from_event"]


async def _resolve(value: Any) -> Any:
    """Await if awaitable, otherwise pass through."""
    if inspect.isawaitable(value):
        return await value
    return value


async def await_tick(feed: Any, symbol: str) -> Optional[Any]:
    """Latest tick for `symbol` from any feed shape, or None when unavailable.

    Never raises for a missing or unusable feed: a caller that cannot price a symbol
    must decide what that means for its own domain (skip the position, reject the
    order), and a TypeError from an await is not a decision.
    """
    if feed is None:
        return None

    getter = getattr(feed, "get_latest_tick", None)
    if getter is not None:
        try:
            tick = await _resolve(getter(symbol))
        except Exception:  # noqa: BLE001 - the caller handles "no price" itself
            return None
        if tick is not None:
            return tick

    # Legacy IMarketDataFeed: separate bid/ask accessors.
    get_bid = getattr(feed, "get_bid", None)
    get_ask = getattr(feed, "get_ask", None)
    if get_bid is None or get_ask is None:
        return None
    try:
        bid = await _resolve(get_bid(symbol))
        ask = await _resolve(get_ask(symbol))
    except Exception:  # noqa: BLE001
        return None
    if bid is None or ask is None:
        return None
    return {"symbol": symbol, "bid": bid, "ask": ask}


def tick_bid(tick: Any) -> Optional[Any]:
    """Bid from a Tick object or a dict-shaped quote."""
    if tick is None:
        return None
    if isinstance(tick, dict):
        return tick.get("bid")
    return getattr(tick, "bid", None)


def tick_ask(tick: Any) -> Optional[Any]:
    """Ask from a Tick object or a dict-shaped quote."""
    if tick is None:
        return None
    if isinstance(tick, dict):
        return tick.get("ask")
    return getattr(tick, "ask", None)


def tick_from_event(event: Any) -> Optional[Any]:
    """Recover a Tick from a TICK_RECEIVED domain event, or None.

    MarketDataEngine publishes the tick as FLAT STRING FIELDS - symbol, bid, ask,
    spread, timestamp - because the event has to survive JSON serialisation onto Redis.
    Both consumers of that event looked for `payload["tick"]` instead, found nothing,
    and returned: the TickMarginPipeline that drives the margin-call / stop-out state
    machine, and the matching engine's pending-order activation. Neither ever ran, and
    neither logged anything, because "no tick in the payload" and "no open positions"
    look identical from the inside.

    Accepting both shapes means an in-process publisher that attaches the Tick object
    directly also works.
    """
    payload = getattr(event, "payload", None)
    if not isinstance(payload, dict):
        return None

    tick = payload.get("tick")
    if tick is not None:
        return tick

    from decimal import Decimal, InvalidOperation

    from core.domains.market_data.models import Tick

    symbol = payload.get("symbol") or getattr(event, "aggregate_id", None)
    if not symbol:
        return None
    try:
        bid = Decimal(str(payload["bid"]))
        ask = Decimal(str(payload["ask"]))
    except (KeyError, InvalidOperation, TypeError, ValueError):
        return None
    try:
        spread = Decimal(str(payload.get("spread", ask - bid)))
    except (InvalidOperation, TypeError, ValueError):
        spread = ask - bid

    timestamp = None
    raw_ts = payload.get("timestamp")
    if isinstance(raw_ts, str):
        from datetime import datetime

        try:
            timestamp = datetime.fromisoformat(raw_ts)
        except ValueError:
            timestamp = None

    kwargs = {"symbol": str(symbol), "bid": bid, "ask": ask, "spread": spread}
    if timestamp is not None:
        kwargs["timestamp"] = timestamp
    if payload.get("source"):
        kwargs["source"] = str(payload["source"])
    try:
        return Tick(**kwargs)
    except (TypeError, ValueError):
        return None
