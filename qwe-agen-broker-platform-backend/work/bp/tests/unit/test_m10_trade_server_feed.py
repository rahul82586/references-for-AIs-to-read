"""M10: trade-server WebSocket feed adapter - the wire protocol decoded
(msgpack ticks/books per refs/trade-server ws/stream.py), subscription messages,
Tick invariants enforced, and the fault model (EOF raises so the ingestor backs off)."""
import asyncio
import json
from datetime import datetime, timezone
from decimal import Decimal

import msgpack
import pytest

from core.domains.market_data.models import Tick
from infrastructure.feeds.trade_server_feed import TradeServerTickFeed


class FakeWebSocket:
    """Mirrors the slice of the websockets client API the adapter uses."""

    def __init__(self, frames):
        self.frames = list(frames)
        self.sent = []
        self.closed = False
        self.recvd = []

    async def send(self, data):
        self.sent.append(data)

    def __aiter__(self):
        return self._iter()

    async def _iter(self):
        for frame in self.frames:
            if isinstance(frame, BaseException):
                raise frame
            self.recvd.append(frame)
            yield frame

    async def close(self):
        self.closed = True


def tick_frame(symbol="EURUSD", bid=1.10000, ask=1.10010, ts=1757577600000):
    return msgpack.packb(
        {"s": symbol, "p": bid, "b": bid, "a": ask, "q": 1.0, "ts": ts}, use_bin_type=True
    )


def book_frame(symbol="EURUSD", bids=((1.0999, 5.0),), asks=((1.1002, 7.0),)):
    return msgpack.packb(
        {
            "type": "book",
            "s": symbol,
            "bids": [{"price": p, "volume": v} for p, v in bids],
            "asks": [{"price": p, "volume": v} for p, v in asks],
        },
        use_bin_type=True,
    )


def make_feed(frames, symbols=("EURUSD", "GBPUSD")):
    conns = []

    async def connect(url):
        ws = FakeWebSocket(frames)
        conns.append(ws)
        return ws

    feed = TradeServerTickFeed(url="ws://test/ws/marketdata", symbols=list(symbols), connect=connect)
    return feed, conns


async def collect(agen, n):
    out = []
    async for item in agen:
        out.append(item)
        if len(out) >= n:
            break
    return out


# ---------------------------------------------------------------------------


async def test_subscribes_every_symbol_on_connect():
    feed, conns = make_feed([tick_frame()])
    await collect(feed.stream_ticks(), 1)
    subs = [json.loads(s) for s in conns[0].sent]
    assert subs == [
        {"action": "sub", "symbol": "EURUSD"},
        {"action": "sub", "symbol": "GBPUSD"},
    ]


async def test_msgpack_tick_becomes_decimal_tick():
    feed, _ = make_feed([tick_frame(bid=1.23456, ask=1.23466, ts=1757577600123)])
    (tick,) = await collect(feed.stream_ticks(), 1)
    assert isinstance(tick, Tick)
    assert tick.symbol == "EURUSD"
    assert tick.bid == Decimal("1.23456") and isinstance(tick.bid, Decimal)
    assert tick.ask == Decimal("1.23466")
    assert tick.spread == Decimal("0.0001")
    assert tick.source == "TRADE_SERVER"
    assert tick.timestamp == datetime.fromtimestamp(1757577600.123, tz=timezone.utc)


async def test_bad_frames_skipped_not_fatal():
    frames = [
        b"\xff\xfe not msgpack",
        json.dumps({"type": "heartbeat"}),  # text frame, no prices
        tick_frame(symbol="GBPUSD", bid=0.0, ask=0.0),  # zero tick: skip
        tick_frame(bid=1.10020, ask=1.10010),  # crossed: drop
        tick_frame(),  # the good one survives
    ]
    feed, _ = make_feed(frames)
    (tick,) = await collect(feed.stream_ticks(), 1)
    assert tick.bid == Decimal("1.10000")


async def test_one_sided_tick_normalised():
    feed, _ = make_feed([tick_frame(bid=0.0, ask=1.10010), tick_frame(bid=1.2, ask=0.0)])
    ticks = await collect(feed.stream_ticks(), 2)
    assert ticks[0].bid == Decimal("1.10010") == ticks[0].ask
    assert ticks[1].ask == Decimal("1.2") == ticks[1].bid


async def test_book_frames_ignored_by_tick_stream():
    feed, _ = make_feed([book_frame(), tick_frame()])
    (tick,) = await collect(feed.stream_ticks(), 1)
    assert tick.bid == Decimal("1.10000")


async def test_clean_eof_raises_so_ingestor_backs_off():
    feed, conns = make_feed([tick_frame()])
    gen = feed.stream_ticks()
    (tick,) = await collect(gen, 1)
    assert tick.bid == Decimal("1.10000")
    with pytest.raises(ConnectionError):
        async for _ in gen:
            pass
    assert conns[0].closed  # socket torn down even on the raise path


async def test_socket_error_propagates_and_socket_closed():
    feed, conns = make_feed([tick_frame(), asyncio.IncompleteReadError(b"", 10)])
    gen = feed.stream_ticks()
    await collect(gen, 1)
    with pytest.raises(asyncio.IncompleteReadError):
        async for _ in gen:
            pass
    assert conns[0].closed


async def test_stream_book_subscribes_and_parses_levels():
    feed, conns = make_feed([
        book_frame(bids=((1.0998, 3.0), (1.0999, 5.0)), asks=((1.1002, 7.0), (1.1003, 9.0))),
        tick_frame(),  # foreign frame type ignored on the book stream
    ], symbols=("EURUSD",))
    (book,) = await collect(feed.stream_book("EURUSD"), 1)
    assert [json.loads(s) for s in conns[0].sent] == [{"action": "sub_book", "symbol": "EURUSD"}]
    assert book.symbol == "EURUSD"
    # sorted best-first, Decimal throughout
    assert [lv.price for lv in book.bids] == [Decimal("1.0999"), Decimal("1.0998")]
    assert [lv.price for lv in book.asks] == [Decimal("1.1002"), Decimal("1.1003")]
    assert book.bids[0].side == "BID" and book.asks[0].side == "ASK"
    assert book.bids[0].volume == Decimal("5.0")
    assert book.best_bid.price == Decimal("1.0999")


async def test_book_frames_for_other_symbols_dropped():
    feed, _ = make_feed([book_frame(symbol="GBPUSD"), book_frame(symbol="EURUSD")], symbols=("EURUSD",))
    (book,) = await collect(feed.stream_book("EURUSD"), 1)
    assert book.symbol == "EURUSD"


async def test_url_required():
    with pytest.raises(ValueError):
        TradeServerTickFeed(url="", symbols=["EURUSD"])
