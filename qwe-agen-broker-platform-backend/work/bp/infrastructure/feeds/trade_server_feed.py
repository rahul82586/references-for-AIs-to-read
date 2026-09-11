"""
Trade-Server WebSocket Market Data Feed (M10)

A live ITickFeed adapter for the trade-server prototype (refs/trade-server):
a FastAPI box with a real MetaTrader5 terminal attached, broadcasting ticks
over WebSocket. This replaces the mock as MARKET_DATA_SOURCE upstream when a
real terminal feed is available.

Wire protocol (mirrors trade-server/ws/stream.py MarketDataBroadcaster, endpoint
``/ws/marketdata``):

  client -> server (JSON text frames):
      {"action": "sub",      "symbol": "EURUSD"}   tick subscription
      {"action": "sub_book", "symbol": "EURUSD"}   DOM book subscription
      {"action": "unsub_book", "symbol": "EURUSD"}

  server -> client (msgpack binary frames):
      tick: {"s": SYM, "p": price, "b": bid, "a": ask, "q": vol, "ts": epoch_ms}
      book: {"type": "book", "s": SYM,
             "bids": [{"price": .., "volume": ..}, ...],
             "asks": [{"price": .., "volume": ..}, ...]}

Architectural Rule: Infrastructure feed adapter implementing the ITickFeed port.
Decimal Precision Rule: wire floats are converted via Decimal(str(value)) only.
Fault model: the generator EXITS (raises) when the socket closes - TickIngestor's
reconnect loop then re-opens and re-subscribes. Silently returning would leave the
ingestor spinning with no backoff.
"""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, AsyncIterator, Callable, Coroutine, List, Optional

from core.domains.market_data.models import BookLevel, OrderBook, Tick
from core.ports.interfaces import ITickFeed

logger = logging.getLogger(__name__)

#: async callable (url) -> websocket connection. Injectable for tests; defaults
#: to ``websockets.connect``.
ConnectFn = Callable[[str], Coroutine[Any, Any, Any]]


def _to_decimal(value: Any) -> Decimal:
    """Wire value (float/int/str) -> Decimal, via str() so floats stay exact."""
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _ts_to_datetime(ts: Any) -> datetime:
    """trade-server sends epoch milliseconds; fall back to 'now' if absent."""
    try:
        return datetime.fromtimestamp(int(ts) / 1000.0, tz=timezone.utc)
    except (TypeError, ValueError, OSError):
        return datetime.now(timezone.utc)


class TradeServerTickFeed(ITickFeed):
    """
    Streams ticks (and DOM books) from a trade-server ``/ws/marketdata`` endpoint.

    One connection per stream: ``stream_ticks`` opens a socket and subscribes to
    every configured symbol; ``stream_book(symbol)`` opens its own socket with a
    ``sub_book`` request, because the trade-server tracks tick and book
    subscriptions per WebSocket connection.
    """

    def __init__(
        self,
        url: str,
        symbols: List[str],
        *,
        name: str = "TradeServerWS",
        source: str = "TRADE_SERVER",
        connect: Optional[ConnectFn] = None,
    ) -> None:
        if not url:
            raise ValueError("TradeServerTickFeed requires a non-empty url")
        self.url = url
        self.symbols = [s.upper() for s in symbols]
        self._name = name
        self._source = source
        self._connect_fn = connect
        self.connected = False
        self.subscribed: List[str] = []

    @property
    def name(self) -> str:
        return self._name

    # ------------------------------------------------------------------
    # connection
    # ------------------------------------------------------------------

    async def _open(self) -> Any:
        if self._connect_fn is not None:
            ws = await self._connect_fn(self.url)
        else:
            import websockets  # lazy: the port must import without the dep

            ws = await websockets.connect(self.url)
        self.connected = True
        return ws

    @staticmethod
    async def _safe_close(ws: Any) -> None:
        try:
            await ws.close()
        except Exception:  # pragma: no cover - best-effort teardown
            pass

    async def _subscribe(self, ws: Any, symbols: List[str], action: str = "sub") -> None:
        for symbol in symbols:
            await ws.send(json.dumps({"action": action, "symbol": symbol}))
        self.subscribed = list(symbols)

    @staticmethod
    def _decode_frame(raw: Any) -> Optional[dict]:
        """Binary frames are msgpack; text frames (if any) are JSON. Anything
        else - or anything unparseable - is None (skip, don't kill the stream)."""
        data: Any = None
        if isinstance(raw, (bytes, bytearray, memoryview)):
            import msgpack

            try:
                data = msgpack.unpackb(bytes(raw), raw=False)
            except Exception as e:
                logger.warning("undecodable msgpack frame (%d bytes): %s", len(raw), e)
                return None
        elif isinstance(raw, str):
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                return None
        if not isinstance(data, dict):
            return None
        return data

    # ------------------------------------------------------------------
    # ITickFeed
    # ------------------------------------------------------------------

    def _frame_to_tick(self, data: dict) -> Optional[Tick]:
        if data.get("type") == "book":
            return None  # book frames belong to stream_book
        symbol = str(data.get("s") or "").upper()
        if not symbol:
            return None
        try:
            bid = _to_decimal(data.get("b") or 0)
            ask = _to_decimal(data.get("a") or 0)
        except (ArithmeticError, ValueError):
            logger.warning("tick for %s carries non-numeric prices: %r", symbol, data)
            return None
        # trade-server skips all-zero ticks; one-sided ticks (market just opened)
        # are normalised so the Tick invariants hold.
        if bid <= 0 and ask <= 0:
            return None
        if bid <= 0:
            bid = ask
        if ask <= 0:
            ask = bid
        if ask < bid:
            logger.warning("crossed tick for %s (bid=%s ask=%s) dropped", symbol, bid, ask)
            return None
        try:
            return Tick(
                symbol=symbol,
                bid=bid,
                ask=ask,
                spread=ask - bid,
                timestamp=_ts_to_datetime(data.get("ts")),
                source=self._source,
            )
        except ValueError as e:  # domain guard rejected the tick
            logger.warning("invalid tick for %s dropped: %s", symbol, e)
            return None

    async def stream_ticks(self) -> AsyncIterator[Tick]:
        ws = await self._open()
        try:
            await self._subscribe(ws, self.symbols, action="sub")
            logger.info(
                "trade-server feed connected: %s (%d symbol(s))", self.url, len(self.symbols)
            )
            async for raw in ws:
                data = self._decode_frame(raw)
                if data is None:
                    continue
                tick = self._frame_to_tick(data)
                if tick is not None:
                    yield tick
        finally:
            self.connected = False
            await self._safe_close(ws)
        # Clean EOF: raise so TickIngestor backs off 5s instead of hot-looping
        # a reconnect against a server that just closed us.
        raise ConnectionError(f"trade-server closed the market-data socket at {self.url}")

    def _frame_to_book(self, data: dict, symbol: str) -> Optional[OrderBook]:
        if data.get("type") != "book":
            return None
        if str(data.get("s") or "").upper() != symbol:
            return None
        bids: List[BookLevel] = []
        asks: List[BookLevel] = []
        try:
            for entry in data.get("bids") or []:
                bids.append(
                    BookLevel(
                        price=_to_decimal(entry["price"]),
                        volume=_to_decimal(entry.get("volume", 0)),
                        side="BID",
                        source=self._source,
                    )
                )
            for entry in data.get("asks") or []:
                asks.append(
                    BookLevel(
                        price=_to_decimal(entry["price"]),
                        volume=_to_decimal(entry.get("volume", 0)),
                        side="ASK",
                        source=self._source,
                    )
                )
        except (KeyError, ArithmeticError, ValueError, TypeError) as e:
            logger.warning("invalid book frame for %s dropped: %s", symbol, e)
            return None
        bids.sort(key=lambda lv: lv.price, reverse=True)  # best bid first
        asks.sort(key=lambda lv: lv.price)  # best ask first
        return OrderBook(symbol=symbol, bids=bids, asks=asks, updated_at=datetime.now(timezone.utc))

    async def stream_book(self, symbol: str) -> AsyncIterator[OrderBook]:
        symbol = symbol.upper()
        ws = await self._open()
        try:
            await self._subscribe(ws, [symbol], action="sub_book")
            async for raw in ws:
                data = self._decode_frame(raw)
                if data is None:
                    continue
                book = self._frame_to_book(data, symbol)
                if book is not None:
                    yield book
        finally:
            self.connected = False
            await self._safe_close(ws)
        raise ConnectionError(f"trade-server closed the book socket for {symbol} at {self.url}")


__all__ = ["TradeServerTickFeed"]
