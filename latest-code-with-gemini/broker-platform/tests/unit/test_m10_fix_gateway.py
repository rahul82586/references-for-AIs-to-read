"""M10: FIX liquidity gateway - the A-Book adapter over the IFixSession transport.

Exercised against SimulatedFixSession (in-process LP) and hostile fake sessions
(silence -> timeout, reject report -> FixReject): the gateway must never turn an
unanswered order into an assumed fill.
"""
import asyncio
from decimal import Decimal

import pytest

from core.domains.common.value_objects import Price, Volume
from core.domains.oms.entities.order import Order
from core.domains.oms.enums import OrderState, OrderType
from infrastructure.fix import messages as fix
from infrastructure.fix.messages import FixMessage
from infrastructure.fix.simulated_session import SimulatedFixSession
from infrastructure.fix.session import FixSessionClosed, IFixSession
from infrastructure.gateways.fix_gateway import (
    FixLiquidityGateway,
    FixReject,
    FixTimeout,
    build_fix_gateway_from_env,
)


def make_order(
    order_type=OrderType.BUY,
    volume="0.10",
    symbol="EURUSD",
    price=None,
    ticket="CL-1",
    expiration=None,
):
    # price_order must be passed explicitly: the entity's default_factory
    # (Price(Decimal('0'))) violates Price's own positivity guard - the same
    # defect create_order.py documents. None is "not yet priced".
    order = Order(
        ticket_id=ticket,
        account_login=100001,
        symbol=symbol,
        order_type=order_type,
        volume_initial=Volume(Decimal(volume)),
        volume_current=Volume(Decimal(volume)),
        price_order=Price(Decimal(price)) if price is not None else None,
        state=OrderState.PLACED,
        time_expiration=expiration,
    )
    return order


def sim_gateway(prices=None, timeout_s=2.0):
    sessions = []

    def factory():
        session = SimulatedFixSession(prices=prices)
        sessions.append(session)
        return session

    gw = FixLiquidityGateway(
        factory, sender_comp_id="BROKER", target_comp_id="SIMLP",
        account="HEDGE-1", timeout_s=timeout_s,
    )
    return gw, sessions


async def test_market_buy_fills_at_simulated_ask():
    gw, sessions = sim_gateway(prices={"EURUSD": (Decimal("1.10000"), Decimal("1.10010"))})
    try:
        report = await gw.send_order(make_order(OrderType.BUY), gateway_id="SIM")
        assert report["status"] == "FILLED"
        assert report["side"] == "BUY"
        assert report["volume"] == "0.10"
        assert Decimal(report["price"]) == Decimal("1.10010")  # client buys -> LP ask
        assert report["stub"] is False
        # the LP saw a well-formed NewOrderSingle
        nos = FixMessage.parse(sessions[0].received[0])
        assert nos.get(fix.MSG_TYPE) == "D"
        assert nos.get(fix.CL_ORD_ID) == "CL-1"
        assert nos.get(fix.SIDE) == "1"
        assert nos.get(fix.ORD_TYPE) == "1"
        assert nos.get(fix.ORDER_QTY) == "0.10"
        assert nos.get(fix.SYMBOL) == "EURUSD"
        assert nos.get(fix.ACCOUNT) == "HEDGE-1"
    finally:
        await gw.stop()


async def test_market_sell_fills_at_simulated_bid():
    gw, _ = sim_gateway(prices={"EURUSD": (Decimal("1.10000"), Decimal("1.10010"))})
    try:
        report = await gw.send_order(make_order(OrderType.SELL, ticket="CL-S"), gateway_id="SIM")
        assert Decimal(report["price"]) == Decimal("1.10000")
        assert report["side"] == "SELL"
    finally:
        await gw.stop()


async def test_resting_limit_then_cancel():
    gw, sessions = sim_gateway(prices={"EURUSD": (Decimal("1.10000"), Decimal("1.10010"))})
    try:
        # far-from-market limit: acked New, not filled
        report = await gw.send_order(
            make_order(OrderType.BUY_LIMIT, price="1.05000", ticket="CL-L"), gateway_id="SIM"
        )
        assert report["status"] == "ACK"
        assert report["ord_status"] == fix.ORD_STATUS_NEW
        nos = FixMessage.parse(sessions[0].received[0])
        assert nos.get(fix.ORD_TYPE) == "2"
        assert nos.get(fix.PRICE) == "1.05000"

        assert await gw.cancel_order("CL-L", gateway_id="SIM") is True
        # the cancel carried the original ClOrdID
        cancels = [FixMessage.parse(m) for m in sessions[0].received if "35=F" in m]
        assert cancels and cancels[0].get(fix.ORIG_CL_ORD_ID) == "CL-L"
    finally:
        await gw.stop()


async def test_crossing_limit_fills_immediately():
    gw, _ = sim_gateway(prices={"EURUSD": (Decimal("1.10000"), Decimal("1.10010"))})
    try:
        report = await gw.send_order(
            make_order(OrderType.BUY_LIMIT, price="1.10500", ticket="CL-X"), gateway_id="SIM"
        )
        assert report["status"] == "FILLED"
        assert Decimal(report["price"]) == Decimal("1.10010")
    finally:
        await gw.stop()


async def test_get_quotes_returns_snapshot_bid_ask():
    gw, _ = sim_gateway(prices={"EURUSD": (Decimal("1.10000"), Decimal("1.10010")),
                                "GBPUSD": (Decimal("1.26000"), Decimal("1.26012"))})
    try:
        quotes = await gw.get_quotes(["EURUSD", "GBPUSD"])
        assert quotes["EURUSD"] == {"bid": "1.10000", "ask": "1.10010",
                                    "timestamp": quotes["EURUSD"]["timestamp"]}
        assert Decimal(quotes["GBPUSD"]["ask"]) == Decimal("1.26012")
    finally:
        await gw.stop()


async def test_expiration_maps_to_gtd():
    from datetime import datetime, timezone

    gw, sessions = sim_gateway()
    try:
        exp = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
        await gw.send_order(
            make_order(OrderType.BUY_LIMIT, price="1.05", ticket="CL-G", expiration=exp),
            gateway_id="SIM",
        )
        nos = FixMessage.parse(sessions[0].received[0])
        assert nos.get(fix.TIME_IN_FORCE) == "6"
        assert nos.get(fix.EXPIRE_TIME) == "20260912-12:00:00.000"
    finally:
        await gw.stop()


# ---------------------------------------------------------------------------
# hostile transports
# ---------------------------------------------------------------------------


class SilentSession(IFixSession):
    """Connects, accepts sends, never answers - the LP went dark."""

    def __init__(self):
        self.sent = []
        self._closed = asyncio.Event()

    @property
    def is_connected(self):
        return not self._closed.is_set()

    async def connect(self):
        pass

    async def send(self, msg):
        self.sent.append(msg)

    async def recv(self):
        await self._closed.wait()
        raise FixSessionClosed("silent session closed")

    async def close(self):
        self._closed.set()


class QueueRejectingSession(SilentSession):
    def __init__(self):
        super().__init__()
        self.out = asyncio.Queue()

    async def connect(self):
        pass

    async def send(self, msg):
        self.sent.append(msg)
        if msg.get(fix.MSG_TYPE) == "D":
            er = (
                FixMessage("8")
                .set(49, "LP").set(56, "BROKER").set(52, fix.fix_timestamp())
                .set(11, msg.get(fix.CL_ORD_ID)).set(37, "LP-1").set(17, "E1")
                .set(150, "8").set(39, "8").set(58, "insufficient liquidity")
                .set(55, msg.get(fix.SYMBOL)).set(54, msg.get(fix.SIDE))
                .set(38, msg.get(fix.ORDER_QTY)).set(151, msg.get(fix.ORDER_QTY))
                .set(14, "0").set(6, "0")
            )
            await self.out.put(er)

    async def recv(self):
        return await self.out.get()

    async def close(self):
        self._closed.set()


async def test_silence_is_a_timeout_not_a_fill():
    session = SilentSession()
    gw = FixLiquidityGateway(lambda: session, sender_comp_id="B", target_comp_id="L", timeout_s=0.2)
    try:
        with pytest.raises(FixTimeout):
            await gw.send_order(make_order(ticket="CL-T"), gateway_id="SIM")
        # the pending correlation entry was cleaned up
        assert not gw._pending_er
    finally:
        await gw.stop()


async def test_rejected_execution_report_raises_with_text():
    session = QueueRejectingSession()
    gw = FixLiquidityGateway(lambda: session, sender_comp_id="B", target_comp_id="L", timeout_s=1.0)
    try:
        with pytest.raises(FixReject) as excinfo:
            await gw.send_order(make_order(ticket="CL-R"), gateway_id="SIM")
        assert "insufficient liquidity" in str(excinfo.value)
        assert excinfo.value.report["ord_status"] == "8"
    finally:
        await gw.stop()


async def test_stop_releases_pending_with_session_error():
    session = SilentSession()
    gw = FixLiquidityGateway(lambda: session, sender_comp_id="B", target_comp_id="L", timeout_s=30)
    task = asyncio.create_task(gw.send_order(make_order(ticket="CL-P"), gateway_id="SIM"))
    await asyncio.sleep(0.05)  # let it register the pending future
    await gw.stop()
    with pytest.raises(FixSessionClosed):
        await task


async def test_env_builder_selects_simulator(monkeypatch):
    monkeypatch.setenv("BROKER_LP_GATEWAY", "fix")
    monkeypatch.setenv("BROKER_FIX_SIMULATOR", "1")
    monkeypatch.setenv("FIX_SENDER_COMP_ID", "BROKERX")
    monkeypatch.setenv("FIX_SIM_PRICES", '{"EURUSD": [1.5, 1.5001]}')
    gw = build_fix_gateway_from_env()
    assert isinstance(gw, FixLiquidityGateway)
    assert gw.sender_comp_id == "BROKERX"
    try:
        report = await gw.send_order(make_order(symbol="EURUSD", ticket="CL-E"), gateway_id="G")
        assert Decimal(report["price"]) == Decimal("1.5001")
    finally:
        await gw.stop()


async def test_env_builder_requires_host_for_real_session(monkeypatch):
    monkeypatch.setenv("BROKER_LP_GATEWAY", "fix")
    monkeypatch.delenv("BROKER_FIX_SIMULATOR", raising=False)
    monkeypatch.delenv("FIX_HOST", raising=False)
    with pytest.raises(RuntimeError, match="FIX_HOST"):
        build_fix_gateway_from_env()
