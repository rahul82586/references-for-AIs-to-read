"""M10 integration: the two real adapters, driven end-to-end.

1. WS feed: a real uvicorn WebSocket server speaking the trade-server
   /ws/marketdata protocol (msgpack frames, JSON sub actions) feeds
   TradeServerTickFeed -> TickIngestor -> MarketDataEngine, and a client order
   fills at the price that arrived over the socket. No mocks in the path.

2. FIX gateway: BROKER_LP_GATEWAY=fix + BROKER_FIX_SIMULATOR=1 through the REAL
   trading_setup wiring, with an A_BOOK routing rule - a client order is hedged
   over the FIX adapter, the simulated LP receives the NewOrderSingle, and the
   ExecutionReport comes back through the orchestrator as OrderRouted.
"""
import asyncio
import json
import queue as thread_queue
import socket
import threading
from decimal import Decimal

import msgpack
import pytest
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from application.commands.create_order import CreateOrderCommand
from application.services.tick_ingestor import TickIngestor
from core.domains.execution.models import ExecutionDestination, RoutingRule
from core.domains.oms.enums import OrderState, OrderType
from core.events.domain_events import DomainEvent, EventType
from infrastructure.feeds.trade_server_feed import TradeServerTickFeed
from infrastructure.fix import messages as fix
from infrastructure.fix.messages import FixMessage
from infrastructure.gateways.fix_gateway import FixLiquidityGateway
from tests.integration.trading_harness import (
    DEFAULT_LOGIN,
    build_harness,
    default_coverage,
)

# ---------------------------------------------------------------------------
# A real WebSocket server speaking the trade-server protocol
# ---------------------------------------------------------------------------

PUSH: "thread_queue.Queue" = thread_queue.Queue()
CONNS: list = []


def _build_server_app() -> FastAPI:
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        task = asyncio.create_task(_broadcaster())
        yield
        PUSH.put(None)
        task.cancel()

    app = FastAPI(lifespan=lifespan)

    @app.websocket("/ws/marketdata")
    async def marketdata(ws: WebSocket):
        await ws.accept()
        entry = {"ws": ws, "subs": set(), "books": set()}
        CONNS.append(entry)
        try:
            while True:
                data = json.loads(await ws.receive_text())
                action = data.get("action")
                symbol = str(data.get("symbol") or "").upper()
                if action == "sub":
                    entry["subs"].add(symbol)
                elif action == "sub_book":
                    entry["books"].add(symbol)
        except (WebSocketDisconnect, RuntimeError):
            pass
        finally:
            if entry in CONNS:
                CONNS.remove(entry)

    return app


async def _broadcaster():
    loop = asyncio.get_running_loop()
    while True:
        item = await loop.run_in_executor(None, PUSH.get)
        if item is None:
            return
        kind, symbol, payload = item
        frame = msgpack.packb(payload, use_bin_type=True)
        for entry in list(CONNS):
            wanted = entry["subs"] if kind == "tick" else entry["books"]
            if symbol.upper() in wanted:
                try:
                    await entry["ws"].send_bytes(frame)
                except Exception:
                    pass


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture()
def trade_server():
    """Run the protocol-faithful WS server on a free port, in a daemon thread."""
    port = _free_port()
    app = _build_server_app()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    import time

    end = time.time() + 5
    while not server.started and time.time() < end:
        time.sleep(0.02)
    assert server.started, "test trade-server did not start"
    try:
        yield f"ws://127.0.0.1:{port}/ws/marketdata"
    finally:
        server.should_exit = True
        thread.join(timeout=5)
        CONNS.clear()


def push_tick(symbol: str, bid, ask, ts_ms: int = 0):
    import time as _time

    ts = ts_ms or int(_time.time() * 1000)
    PUSH.put(("tick", symbol, {"s": symbol, "p": float(bid), "b": float(bid),
                               "a": float(ask), "q": 1.0, "ts": ts}))


# ---------------------------------------------------------------------------
# 1. live WS feed -> engine -> fill
# ---------------------------------------------------------------------------


async def test_live_ws_feed_prices_a_real_fill(trade_server):
    h = await build_harness(coverage=default_coverage())
    feed = TradeServerTickFeed(url=trade_server, symbols=["EURUSD"])
    ingestor = TickIngestor(market_data_engine=h.market_data_engine, feeds=[feed])
    await ingestor.start()
    try:
        # push until the tick has crossed the socket into the engine
        tick = None
        for _ in range(100):
            push_tick("EURUSD", 1.23450, 1.23460)
            await asyncio.sleep(0.05)
            tick = h.latest_tick("EURUSD")
            if tick is not None and tick.bid == Decimal("1.23450"):
                break
        assert tick is not None, "no tick arrived over the live WebSocket"
        assert tick.bid == Decimal("1.23450")
        assert tick.ask == Decimal("1.23460")
        assert tick.source == "TRADE_SERVER"
        assert isinstance(tick.bid, Decimal)

        # the server saw the protocol-level subscription
        assert any("EURUSD" in c["subs"] for c in CONNS)

        # a market BUY fills at the ASK that arrived over the socket
        await h.stack.create_order_handler.handle(
            CreateOrderCommand(account_login=DEFAULT_LOGIN, symbol="EURUSD",
                               order_type=OrderType.BUY, volume=Decimal("0.10"))
        )
        positions = h.open_positions()
        assert len(positions) == 1
        assert positions[0].price_open.value == Decimal("1.23460")
        orders = h.orders()
        assert orders[0].state is OrderState.FILLED

        # a fresh tick over the socket updates the engine (feed still live)
        for _ in range(100):
            push_tick("EURUSD", 1.24000, 1.24010)
            await asyncio.sleep(0.05)
            tick = h.latest_tick("EURUSD")
            if tick is not None and tick.bid == Decimal("1.24000"):
                break
        assert h.latest_tick("EURUSD").bid == Decimal("1.24000")
    finally:
        await ingestor.stop()


# ---------------------------------------------------------------------------
# 2. FIX gateway on the A-Book path, through the real DI wiring
# ---------------------------------------------------------------------------


async def test_a_book_order_hedges_over_fix(monkeypatch):
    monkeypatch.setenv("BROKER_LP_GATEWAY", "fix")
    monkeypatch.setenv("BROKER_FIX_SIMULATOR", "1")
    monkeypatch.setenv("FIX_SENDER_COMP_ID", "BROKER")
    monkeypatch.setenv("FIX_TARGET_COMP_ID", "SIMLP")
    monkeypatch.setenv("FIX_ACCOUNT", "HEDGE-ACC")
    monkeypatch.delenv("FIX_SIM_PRICES", raising=False)

    rule = RoutingRule(
        rule_id="a-book-eurusd",
        priority=100,
        destination=ExecutionDestination.A_BOOK,
        symbol_filter="EURUSD",
        gateway_id="SIMLP",
    )
    h = await build_harness(rules=[rule], coverage=default_coverage())
    gateway = h.stack.liquidity_gateway
    assert isinstance(gateway, FixLiquidityGateway), \
        "BROKER_LP_GATEWAY=fix must replace the stub in the real DI wiring"

    routed: list = []

    def on_routed(event: DomainEvent):
        if event.event_type == EventType.ORDER_ROUTED:
            routed.append(event)

    h.event_bus.subscribe(EventType.ORDER_ROUTED, on_routed)

    try:
        await h.publish_tick("EURUSD", Decimal("1.10000"), Decimal("1.10010"))
        await h.stack.create_order_handler.handle(
            CreateOrderCommand(account_login=DEFAULT_LOGIN, symbol="EURUSD",
                               order_type=OrderType.BUY, volume=Decimal("0.10"))
        )
        await asyncio.sleep(0.1)  # let the orchestrator finish the A-Book leg

        assert routed, "no OrderRouted event: the A-Book leg did not run"
        # the orchestrator emits ORDER_ROUTED twice: the routing decision, then
        # the A-Book execution carrying the report. Assert on the execution one.
        executions = [e for e in routed if "execution_report" in e.payload]
        assert executions, "routing decided but the A-Book execution event never came"
        payload = executions[0].payload
        assert payload["destination"] == ExecutionDestination.A_BOOK.value
        assert payload["stub"] is False
        report = payload["execution_report"]
        assert report["status"] == "FILLED"
        assert Decimal(report["price"]) == Decimal("1.10010")  # simulated LP ask

        # the simulated LP received our NewOrderSingle with the order's ticket as ClOrdID
        session = gateway._session
        assert session is not None
        nos = [FixMessage.parse(m) for m in session.received]
        assert any(m.get(fix.MSG_TYPE) == "D" for m in nos)
        order_msg = next(m for m in nos if m.get(fix.MSG_TYPE) == "D")
        order = h.orders()[0]
        assert order_msg.get(fix.CL_ORD_ID) == order.ticket_id
        assert order_msg.get(fix.SYMBOL) == "EURUSD"
        assert order_msg.get(fix.SIDE) == "1"
        assert order_msg.get(fix.ORDER_QTY) == "0.10"
        assert order_msg.get(fix.ACCOUNT) == "HEDGE-ACC"

        # the LP quotes flow back through the same session
        quotes = await gateway.get_quotes(["EURUSD"])
        assert quotes["EURUSD"]["bid"] == "1.10000"
        assert quotes["EURUSD"]["ask"] == "1.10010"
    finally:
        await gateway.stop()
