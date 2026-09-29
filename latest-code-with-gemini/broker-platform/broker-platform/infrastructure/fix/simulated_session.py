"""
SimulatedFixSession - an in-process FIX liquidity provider for dev/test (M10).

Honest scope statement: this is NOT a connection to a real LP. It exists so the
FIX gateway skeleton can be exercised end-to-end (order in, ExecutionReport out;
cancel in, canceled report out; MarketDataRequest in, snapshot out) without a
network counterparty. It moves no money.

Behaviour of the simulated LP:
  * NewOrderSingle market -> ExecutionReport New(39=0), then Filled(39=2) at the
    simulated ask (client buys) / bid (client sells).
  * NewOrderSingle limit -> New(39=0); filled immediately only when the limit
    price crosses the simulated book; otherwise it stays New (resting).
  * OrderCancelRequest -> ExecutionReport Canceled(39=4).
  * MarketDataRequest -> MarketDataSnapshotFullRefresh(35=W) from its price map.
  * TestRequest -> Heartbeat echoing the id.

Prices default to EURUSD 1.10000/1.10010; pass ``prices={SYM: (bid, ask)}``.
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Optional, Tuple

from infrastructure.fix.messages import (
    ACCOUNT,
    AVG_PX,
    CL_ORD_ID,
    CUM_QTY,
    EXEC_ID,
    EXEC_TYPE,
    LEAVES_QTY,
    MSG_EXECUTION_REPORT,
    MSG_HEARTBEAT,
    MSG_MARKET_DATA_SNAPSHOT,
    MSG_NEW_ORDER_SINGLE,
    MSG_ORDER_CANCEL_REQUEST,
    MSG_TEST_REQUEST,
    MSG_MARKET_DATA_REQUEST,
    MD_ENTRY_PX,
    MD_ENTRY_SIZE,
    MD_ENTRY_TYPE,
    MD_REQ_ID,
    NO_MD_ENTRIES,
    ORD_STATUS,
    ORD_STATUS_CANCELED,
    ORD_STATUS_FILLED,
    ORD_STATUS_NEW,
    ORDER_ID,
    ORDER_QTY,
    ORD_TYPE,
    ORD_TYPE_MARKET,
    ORIG_CL_ORD_ID,
    PRICE,
    SIDE,
    SIDE_BUY,
    SIDE_SELL,
    SYMBOL,
    TEST_REQ_ID,
    TRANSACT_TIME,
    FixMessage,
    SOH,
    fix_timestamp,
)
from infrastructure.fix.session import FixSessionClosed, IFixSession

logger = logging.getLogger(__name__)

DEFAULT_PRICES: Dict[str, Tuple[Decimal, Decimal]] = {
    "EURUSD": (Decimal("1.10000"), Decimal("1.10010")),
    "GBPUSD": (Decimal("1.26000"), Decimal("1.26012")),
    "USDJPY": (Decimal("150.000"), Decimal("150.010")),
}
DEFAULT_SIZE = Decimal("1000000")


class SimulatedFixSession(IFixSession):
    """In-process LP simulator implementing the IFixSession transport port."""

    def __init__(
        self,
        sender_comp_id: str = "SIMLP",
        target_comp_id: str = "BROKER",
        *,
        prices: Optional[Dict[str, Tuple[Decimal, Decimal]]] = None,
        latency_s: float = 0.0,
        fill_market: bool = True,
    ) -> None:
        self.sender_comp_id = sender_comp_id
        self.target_comp_id = target_comp_id
        self.prices: Dict[str, Tuple[Decimal, Decimal]] = dict(DEFAULT_PRICES)
        for sym, (bid, ask) in (prices or {}).items():
            self.prices[sym.upper()] = (Decimal(str(bid)), Decimal(str(ask)))
        self.latency_s = latency_s
        self.fill_market = fill_market
        self._connected = False
        self._inbox: "asyncio.Queue[Optional[FixMessage]]" = asyncio.Queue()   # gateway -> LP
        self._outbox: "asyncio.Queue[Optional[FixMessage]]" = asyncio.Queue()  # LP -> gateway
        self._task: Optional[asyncio.Task] = None
        #: audit trail of everything the "LP" received, for tests/proofs
        self.received: list = []

    # --- IFixSession --------------------------------------------------------

    @property
    def is_connected(self) -> bool:
        return self._connected

    async def connect(self) -> None:
        self._connected = True
        self._task = asyncio.create_task(self._lp_loop())
        logger.info("SimulatedFixSession connected (sender=%s)", self.sender_comp_id)

    async def send(self, msg: FixMessage) -> None:
        if not self._connected:
            raise FixSessionClosed("simulated FIX session is not connected")
        await self._inbox.put(msg)

    async def recv(self) -> FixMessage:
        item = await self._outbox.get()
        if item is None:
            raise FixSessionClosed("simulated FIX session closed")
        return item

    async def close(self) -> None:
        self._connected = False
        await self._inbox.put(None)
        await self._outbox.put(None)
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    # --- the simulated LP ---------------------------------------------------

    async def _lp_loop(self) -> None:
        while True:
            msg = await self._inbox.get()
            if msg is None:
                return
            self.received.append(msg.encode())
            if self.latency_s:
                await asyncio.sleep(self.latency_s)
            try:
                await self._handle(msg)
            except Exception:  # pragma: no cover - defensive
                logger.exception("simulated LP failed handling %r", msg)

    def _reply(self, msg: FixMessage) -> None:
        self._outbox.put_nowait(msg)

    def _book(self, symbol: str) -> Tuple[Decimal, Decimal]:
        return self.prices.get(symbol.upper(), (Decimal("1.00000"), Decimal("1.00010")))

    async def _handle(self, msg: FixMessage) -> None:
        msg_type = msg.get(35)
        if msg_type == MSG_NEW_ORDER_SINGLE:
            self._handle_new_order(msg)
        elif msg_type == MSG_ORDER_CANCEL_REQUEST:
            self._handle_cancel(msg)
        elif msg_type == MSG_MARKET_DATA_REQUEST:
            self._handle_md_request(msg)
        elif msg_type == MSG_TEST_REQUEST:
            self._reply(self._header(MSG_HEARTBEAT).set(TEST_REQ_ID, msg.get(TEST_REQ_ID, "")))
        elif msg_type == MSG_HEARTBEAT:
            pass
        else:  # pragma: no cover - simulator scope
            logger.warning("simulated LP ignoring msg type %s", msg_type)

    def _header(self, msg_type: str) -> FixMessage:
        msg = FixMessage(msg_type)
        msg.set(49, self.sender_comp_id).set(56, self.target_comp_id)
        msg.set(52, fix_timestamp())
        return msg

    def _execution_report(self, msg: FixMessage, overrides: Optional[Dict[int, object]] = None) -> FixMessage:
        er = self._header(MSG_EXECUTION_REPORT)
        if msg.get(ACCOUNT):
            er.set(ACCOUNT, msg.get(ACCOUNT))
        er.set(CL_ORD_ID, msg.get(CL_ORD_ID, ""))
        er.set(ORDER_ID, f"SIMLP-{uuid.uuid4().hex[:10]}")
        er.set(EXEC_ID, uuid.uuid4().hex[:8])
        er.set(SYMBOL, msg.get(SYMBOL, ""))
        er.set(SIDE, msg.get(SIDE, ""))
        er.set(ORDER_QTY, msg.get(ORDER_QTY, "0"))
        er.set(TRANSACT_TIME, fix_timestamp())
        er.set(EXEC_TYPE, ORD_STATUS_NEW)
        er.set(ORD_STATUS, ORD_STATUS_NEW)
        er.set(LEAVES_QTY, msg.get(ORDER_QTY, "0"))
        er.set(CUM_QTY, "0")
        er.set(AVG_PX, "0")
        for tag, value in (overrides or {}).items():
            er.replace(int(tag), value)
        return er

    def _handle_new_order(self, msg: FixMessage) -> None:
        symbol = (msg.get(SYMBOL) or "").upper()
        side = msg.get(SIDE) or SIDE_BUY
        qty = Decimal(msg.get(ORDER_QTY) or "0")
        ord_type = msg.get(ORD_TYPE) or ORD_TYPE_MARKET
        bid, ask = self._book(symbol)
        px = Decimal(msg.get(PRICE) or "0") if msg.get(PRICE) else None

        # 1) New ack
        self._reply(self._execution_report(msg))

        # 2) fill decision
        fill_px: Optional[Decimal] = None
        if ord_type == ORD_TYPE_MARKET and self.fill_market:
            fill_px = ask if side == SIDE_BUY else bid
        elif ord_type == "2" and px is not None:
            crosses = (side == SIDE_BUY and px >= ask) or (side == SIDE_SELL and px <= bid)
            if crosses:
                fill_px = ask if side == SIDE_BUY else bid

        if fill_px is not None:
            self._reply(
                self._execution_report(
                    msg,
                    {
                        150: ORD_STATUS_FILLED,
                        39: ORD_STATUS_FILLED,
                        151: "0",
                        14: format(qty, "f"),
                        6: format(fill_px, "f"),
                    },
                )
            )

    def _handle_cancel(self, msg: FixMessage) -> None:
        er = self._execution_report(
            msg,
            {
                150: ORD_STATUS_CANCELED,
                39: ORD_STATUS_CANCELED,
                151: "0",
                14: msg.get(ORDER_QTY, "0"),
            },
        )
        er.set(ORIG_CL_ORD_ID, msg.get(ORIG_CL_ORD_ID, ""))
        self._reply(er)

    def _handle_md_request(self, msg: FixMessage) -> None:
        symbol = (msg.get(SYMBOL) or "").upper()
        bid, ask = self._book(symbol)
        snap = self._header(MSG_MARKET_DATA_SNAPSHOT)
        snap.set(MD_REQ_ID, msg.get(MD_REQ_ID, ""))
        snap.set(SYMBOL, symbol)
        snap.set(264, 0)
        snap.set(NO_MD_ENTRIES, 2)
        snap.set(MD_ENTRY_TYPE, "0").set(MD_ENTRY_PX, format(bid, "f")).set(MD_ENTRY_SIZE, format(DEFAULT_SIZE, "f"))
        snap.set(MD_ENTRY_TYPE, "1").set(MD_ENTRY_PX, format(ask, "f")).set(MD_ENTRY_SIZE, format(DEFAULT_SIZE, "f"))
        self._reply(snap)


__all__ = ["SimulatedFixSession", "DEFAULT_PRICES"]
