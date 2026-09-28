"""M10 proof: the real adapters run - live WS market data prices a real fill,
and the A-Book hedges over FIX through the real DI wiring.

Part A  trade-server WS feed over a REAL uvicorn socket (msgpack protocol):
        subscribe -> engine tick -> market fill at the socket's ask -> forced
        disconnect -> ingestor reconnects and re-subscribes.
Part B  BROKER_LP_GATEWAY=fix + simulator through trading_setup: A-Book order
        hedged, NOS on the wire, FILLED report back, cancel + LP quotes.
Part C  fail-hard semantics: no silent fallbacks anywhere in the new wiring.

Usage:  PYTHONPATH=. python3 scripts/m10_proof_adapters.py
"""
import asyncio
import json
import os
import queue as thread_queue
import socket
import sys
import threading
import time
from decimal import Decimal

sys.path.insert(0, os.getcwd())

import msgpack
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
from infrastructure.gateways.fix_gateway import FixLiquidityGateway, build_fix_gateway_from_env
from tests.integration.trading_harness import DEFAULT_LOGIN, build_harness, default_coverage

CHECKS = {"pass": 0, "fail": 0}


def check(name, ok, detail=""):
    CHECKS["pass" if ok else "fail"] += 1
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))
    return ok


# ---------------------------------------------------------------------------
# A trade-server-protocol WebSocket server (the real wire, not a fake object)
# ---------------------------------------------------------------------------

PUSH: "thread_queue.Queue" = thread_queue.Queue()
CONNS: list = []
KICK: threading.Event = threading.Event()


def build_server_app() -> FastAPI:
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        task = asyncio.create_task(broadcaster())
        yield
        PUSH.put(None)
        task.cancel()

    app = FastAPI(lifespan=lifespan)

    @app.websocket("/ws/marketdata")
    async def marketdata(ws: WebSocket):
        await ws.accept()
        entry = {"ws": ws, "subs": set()}
        CONNS.append(entry)
        try:
            while True:
                data = json.loads(await ws.receive_text())
                if data.get("action") == "sub":
                    entry["subs"].add(str(data.get("symbol") or "").upper())
        except (WebSocketDisconnect, RuntimeError):
            pass
        finally:
            if entry in CONNS:
                CONNS.remove(entry)

    return app


async def broadcaster():
    loop = asyncio.get_running_loop()
    while True:
        item = await loop.run_in_executor(None, PUSH.get)
        if item is None:
            return
        kind, symbol, payload = item
        if kind == "kick":
            for entry in list(CONNS):
                try:
                    await entry["ws"].close(code=1001)
                except Exception:
                    pass
            continue
        frame = msgpack.packb(payload, use_bin_type=True)
        for entry in list(CONNS):
            if symbol.upper() in entry["subs"]:
                try:
                    await entry["ws"].send_bytes(frame)
                except Exception:
                    pass


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def push_tick(symbol, bid, ask):
    PUSH.put(("tick", symbol, {"s": symbol, "p": float(bid), "b": float(bid),
                               "a": float(ask), "q": 1.0, "ts": int(time.time() * 1000)}))


async def wait_for_tick(h, symbol, bid, timeout=10.0, repush=None):
    end = time.time() + timeout
    while time.time() < end:
        if repush:
            repush()
        tick = h.latest_tick(symbol)
        if tick is not None and tick.bid == bid:
            return tick
        await asyncio.sleep(0.1)
    return None


# ---------------------------------------------------------------------------
# Part A - live WS feed over a real socket
# ---------------------------------------------------------------------------

async def part_a():
    print("\n== Part A: trade-server WS feed, real socket ==")
    port = free_port()
    server = uvicorn.Server(uvicorn.Config(build_server_app(), host="127.0.0.1",
                                           port=port, log_level="error"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    end = time.time() + 5
    while not server.started and time.time() < end:
        time.sleep(0.02)
    check("A0 protocol-faithful WS server up", server.started, f"port {port}")

    h = await build_harness(coverage=default_coverage())
    feed = TradeServerTickFeed(url=f"ws://127.0.0.1:{port}/ws/marketdata", symbols=["EURUSD"])
    ingestor = TickIngestor(market_data_engine=h.market_data_engine, feeds=[feed])
    await ingestor.start()
    try:
        tick = await wait_for_tick(
            h, "EURUSD", Decimal("1.23450"),
            repush=lambda: push_tick("EURUSD", 1.23450, 1.23460),
        )
        check("A1 feed connected, subscribed, first tick in the engine", tick is not None)
        check("A2 tick carries Decimal prices from the wire",
              tick is not None and isinstance(tick.bid, Decimal)
              and tick.bid == Decimal("1.23450") and tick.ask == Decimal("1.23460"))
        check("A3 tick is labelled TRADE_SERVER (not MOCK)",
              tick is not None and tick.source == "TRADE_SERVER")

        await h.stack.create_order_handler.handle(
            CreateOrderCommand(account_login=DEFAULT_LOGIN, symbol="EURUSD",
                               order_type=OrderType.BUY, volume=Decimal("0.10"))
        )
        positions = h.open_positions()
        check("A4 market BUY filled at the ASK that arrived over the socket",
              len(positions) == 1 and positions[0].price_open.value == Decimal("1.23460")
              and h.orders()[0].state is OrderState.FILLED)
        account = await h.account()
        check("A5 fill moved real account state (margin held, balance intact until close)",
              account.margin_used.amount > Decimal("0") and account.balance.amount == Decimal("10000"))

        # force the upstream to drop us: the ingestor must reconnect on its own
        before = len(feed.subscribed)
        PUSH.put(("kick", "", None))
        tick2 = await wait_for_tick(
            h, "EURUSD", Decimal("1.24000"), timeout=20.0,
            repush=lambda: push_tick("EURUSD", 1.24000, 1.24010),
        )
        check("A6 upstream dropped the socket; ingestor reconnected and re-subscribed",
              tick2 is not None and tick2.bid == Decimal("1.24000"),
              f"re-pushed subs after {before} symbol(s)")
    finally:
        await ingestor.stop()
        server.should_exit = True
        thread.join(timeout=5)
        check("A7 ingestor and test server stopped clean", not thread.is_alive())


# ---------------------------------------------------------------------------
# Part B - A-Book hedge over FIX through the real DI wiring
# ---------------------------------------------------------------------------

async def part_b():
    print("\n== Part B: FIX gateway on the A-Book path ==")
    os.environ["BROKER_LP_GATEWAY"] = "fix"
    os.environ["BROKER_FIX_SIMULATOR"] = "1"
    os.environ["FIX_SENDER_COMP_ID"] = "BROKER"
    os.environ["FIX_TARGET_COMP_ID"] = "SIMLP"
    os.environ["FIX_ACCOUNT"] = "HEDGE-ACC"
    # prices as JSON STRINGS: JSON floats lose trailing zeros (1.10000 -> 1.1)
    os.environ["FIX_SIM_PRICES"] = '{"EURUSD": ["1.10000", "1.10010"]}'
    try:
        rule = RoutingRule(rule_id="a-book-eurusd", priority=100,
                           destination=ExecutionDestination.A_BOOK,
                           symbol_filter="EURUSD", gateway_id="SIMLP")
        h = await build_harness(rules=[rule], coverage=default_coverage())
        gateway = h.stack.liquidity_gateway
        check("B1 BROKER_LP_GATEWAY=fix replaced the stub in the real DI wiring",
              isinstance(gateway, FixLiquidityGateway))

        routed: list = []
        deal_events: list = []

        def _on_event(e):
            if e.event_type == EventType.ORDER_ROUTED:
                routed.append(e)
            elif e.event_type == EventType.DEAL_CREATED:
                deal_events.append(e)

        h.event_bus.subscribe(EventType.ORDER_ROUTED, _on_event)
        h.event_bus.subscribe(EventType.DEAL_CREATED, _on_event)

        await h.publish_tick("EURUSD", Decimal("1.10000"), Decimal("1.10010"))
        await h.stack.create_order_handler.handle(
            CreateOrderCommand(account_login=DEFAULT_LOGIN, symbol="EURUSD",
                               order_type=OrderType.BUY, volume=Decimal("0.10"))
        )
        await asyncio.sleep(0.1)

        # M11: a FILLED report now books the client side, so the evidence is the
        # A-Book DEAL_CREATED routing event plus a real deal and position - not an
        # ORDER_ROUTED carrying the raw report, which is what M10 asserted on while
        # the client received no trade at all.
        executions = [
            e for e in deal_events
            if isinstance(e, DomainEvent)
            and e.payload.get("destination") == ExecutionDestination.A_BOOK.value
        ]
        check("B2 A-Book leg executed and booked the client side", bool(executions))
        payload = executions[0].payload if executions else {}
        deals = await h.deal_repo.find_by_account(DEFAULT_LOGIN)
        positions = await h.position_repo.get_by_account(DEFAULT_LOGIN)
        check("B3 LP filled at its ask; client deal+position booked; hedge passed on",
              payload.get("hedged") is True
              and Decimal(payload.get("price", "0")) == Decimal("1.10010")
              and len(deals) == 1 and len(positions) == 1
              and h.coverage_exposure("EURUSD") == Decimal("0"))

        session = gateway._session
        nos = [FixMessage.parse(m) for m in (session.received if session else [])]
        order_msg = next((m for m in nos if m.get(fix.MSG_TYPE) == "D"), None)
        order = h.orders()[0]
        check("B4 the LP saw a well-formed NewOrderSingle (ClOrdID=ticket, account, side, qty)",
              order_msg is not None
              and order_msg.get(fix.CL_ORD_ID) == order.ticket_id
              and order_msg.get(fix.ACCOUNT) == "HEDGE-ACC"
              and order_msg.get(fix.SIDE) == "1"
              and order_msg.get(fix.ORDER_QTY) == "0.10")

        # resting limit far from market -> acked New, then cancelled at the LP
        limit = await gateway.send_order(_make_limit("CL-PR-1"), gateway_id="SIMLP")
        cancelled = await gateway.cancel_order("CL-PR-1", gateway_id="SIMLP")
        check("B5 resting limit acked New, cancel confirmed by the LP",
              limit["status"] == "ACK" and cancelled is True)

        quotes = await gateway.get_quotes(["EURUSD"])
        check("B6 LP quotes flow back through the same session",
              Decimal(quotes.get("EURUSD", {}).get("bid", "0")) == Decimal("1.10000")
              and Decimal(quotes.get("EURUSD", {}).get("ask", "0")) == Decimal("1.10010"))

        await gateway.stop()
        check("B7 gateway stopped clean", not gateway.is_started)
    finally:
        for key in ("BROKER_LP_GATEWAY", "BROKER_FIX_SIMULATOR", "FIX_SENDER_COMP_ID",
                    "FIX_TARGET_COMP_ID", "FIX_ACCOUNT", "FIX_SIM_PRICES"):
            os.environ.pop(key, None)


def _make_limit(ticket):
    from core.domains.common.value_objects import Price, Volume
    from core.domains.oms.entities.order import Order

    return Order(ticket_id=ticket, account_login=DEFAULT_LOGIN, symbol="EURUSD",
                 order_type=OrderType.BUY_LIMIT,
                 volume_initial=Volume(Decimal("0.10")), volume_current=Volume(Decimal("0.10")),
                 price_order=Price(Decimal("1.05000")), state=OrderState.PLACED)


# ---------------------------------------------------------------------------
# Part C - fail-hard semantics
# ---------------------------------------------------------------------------

async def part_c():
    print("\n== Part C: fail-hard, no silent fallbacks ==")
    os.environ["BROKER_LP_GATEWAY"] = "fix"
    os.environ.pop("BROKER_FIX_SIMULATOR", None)
    os.environ.pop("FIX_HOST", None)
    try:
        try:
            build_fix_gateway_from_env()
            check("C1 real FIX session without FIX_HOST refuses to build", False)
        except RuntimeError as e:
            check("C1 real FIX session without FIX_HOST refuses to build", "FIX_HOST" in str(e))
    finally:
        os.environ.pop("BROKER_LP_GATEWAY", None)

    os.environ["BROKER_LP_GATEWAY"] = "carrier-pigeon"
    try:
        try:
            await build_harness(coverage=default_coverage())
            check("C2 unknown BROKER_LP_GATEWAY value refuses to start the stack", False)
        except RuntimeError as e:
            check("C2 unknown BROKER_LP_GATEWAY value refuses to start the stack",
                  "carrier-pigeon" in str(e))
    finally:
        os.environ.pop("BROKER_LP_GATEWAY", None)

    try:
        TradeServerTickFeed(url="", symbols=["EURUSD"])
        check("C3 feed without a URL refuses to construct", False)
    except ValueError:
        check("C3 feed without a URL refuses to construct", True)

    import api.main as main_mod
    src = open(main_mod.__file__, encoding="utf-8").read()
    check("C4 server startup requires TRADE_SERVER_WS_URL for the live source",
          "MARKET_DATA_SOURCE=trade_server requires TRADE_SERVER_WS_URL" in src)


async def main():
    await part_a()
    await part_b()
    await part_c()
    total = CHECKS["pass"] + CHECKS["fail"]
    print(f"\nM10 proof: {CHECKS['pass']}/{total} checks passed")
    return 0 if CHECKS["fail"] == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
