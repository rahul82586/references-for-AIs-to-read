"""
FIX Liquidity Gateway (M10) - the real ILiquidityGateway adapter for A-Book flow.

Replaces StubLiquidityGateway under the same DI key when BROKER_LP_GATEWAY=fix:
nothing above the gateway changes (ExecutionOrchestrator._execute_a_book keeps
calling send_order/cancel_order/get_quotes).

Design:
  * the gateway owns ONE session (transport: QuickFixSession for a real LP,
    SimulatedFixSession for dev/test) and a background read loop;
  * outbound orders are correlated to inbound ExecutionReports by ClOrdID(11)
    through per-request futures with a timeout - a missing report is a FAILURE
    (FixTimeout), never an assumed fill;
  * OrdStatus 4 (Canceled) / 8 (Rejected) responses raise FixReject, so the
    orchestrator's A-Book error path rejects the client order rather than
    believing it was hedged;
  * MarketData snapshots (35=W) resolve get_quotes and refresh a small cache.

SKELETON scope (documented, not hidden): no drop-copy (35=Z) reconciliation, no
allocation blocks, no bracket SL/TP (FIX 4.4 has no MT5-style paired brackets -
the server-side SlTpWorker owns those), no session-level resequencing (the
transport's job).
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Callable, Dict, List, Optional

from core.domains.oms.entities.order import Order
from core.domains.oms.enums import OrderType
from core.ports.interfaces import ILiquidityGateway
from infrastructure.fix import messages as fix
from infrastructure.fix.messages import FixMessage
from infrastructure.fix.session import FixSessionClosed, IFixSession

logger = logging.getLogger(__name__)


class FixGatewayError(RuntimeError):
    """Base error for the FIX gateway."""


class FixTimeout(FixGatewayError):
    """No ExecutionReport arrived inside the timeout - hedge state UNKNOWN."""


class FixReject(FixGatewayError):
    """The LP rejected or cancelled the order; carries the execution report."""

    def __init__(self, report: Dict[str, Any], message: str) -> None:
        super().__init__(message)
        self.report = report


SIDE_BY_ORDER_TYPE: Dict[OrderType, str] = {
    OrderType.BUY: fix.SIDE_BUY,
    OrderType.SELL: fix.SIDE_SELL,
    OrderType.BUY_LIMIT: fix.SIDE_BUY,
    OrderType.SELL_LIMIT: fix.SIDE_SELL,
    OrderType.BUY_STOP: fix.SIDE_BUY,
    OrderType.SELL_STOP: fix.SIDE_SELL,
    OrderType.BUY_STOP_LIMIT: fix.SIDE_BUY,
    OrderType.SELL_STOP_LIMIT: fix.SIDE_SELL,
}

_LIMIT_TYPES = {OrderType.BUY_LIMIT, OrderType.SELL_LIMIT}
_STOP_TYPES = {OrderType.BUY_STOP, OrderType.SELL_STOP}
_STOP_LIMIT_TYPES = {OrderType.BUY_STOP_LIMIT, OrderType.SELL_STOP_LIMIT}

#: OrdStatus values that END the wait for a report: Filled, PartiallyFilled,
#: Canceled, Replaced, PendingCancel, Rejected, Expired. New/PendingNew are
#: acks - the gateway waits a short grace for the outcome that follows.
_FINAL_STATUSES = frozenset({
    fix.ORD_STATUS_FILLED,
    fix.ORD_STATUS_PARTIALLY_FILLED,
    fix.ORD_STATUS_CANCELED,
    fix.ORD_STATUS_REPLACED,
    fix.ORD_STATUS_PENDING_CANCEL,
    fix.ORD_STATUS_REJECTED,
    "C",  # Expired
})


class FixLiquidityGateway(ILiquidityGateway):
    """A-Book LP connectivity over a FIX session."""

    def __init__(
        self,
        session_factory: Callable[[], IFixSession],
        *,
        sender_comp_id: str,
        target_comp_id: str,
        account: Optional[str] = None,
        timeout_s: float = 5.0,
        ack_grace_s: float = 0.25,
    ) -> None:
        self._session_factory = session_factory
        self.sender_comp_id = sender_comp_id
        self.target_comp_id = target_comp_id
        self.account = account
        self.timeout_s = timeout_s
        self.ack_grace_s = ack_grace_s
        self._session: Optional[IFixSession] = None
        self._read_task: Optional[asyncio.Task] = None
        self._stopping = False
        self._start_lock = asyncio.Lock()
        self._pending_er: Dict[str, asyncio.Future] = {}
        self._pending_md: Dict[str, asyncio.Future] = {}
        self._quote_cache: Dict[str, Dict[str, Any]] = {}
        #: audit trail: every execution report received, oldest first
        self.received_reports: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # lifecycle
    # ------------------------------------------------------------------

    @property
    def is_started(self) -> bool:
        return self._session is not None and self._session.is_connected

    async def start(self) -> None:
        async with self._start_lock:
            if self.is_started:
                return
            self._stopping = False
            self._session = self._session_factory()
            await self._session.connect()
            self._read_task = asyncio.create_task(self._read_loop())
            logger.info(
                "FIX gateway started: sender=%s target=%s (%s)",
                self.sender_comp_id, self.target_comp_id, type(self._session).__name__,
            )

    async def stop(self) -> None:
        self._stopping = True
        for fut in list(self._pending_er.values()) + list(self._pending_md.values()):
            if not fut.done():
                fut.set_exception(FixSessionClosed("FIX gateway stopped"))
        self._pending_er.clear()
        self._pending_md.clear()
        if self._read_task is not None:
            self._read_task.cancel()
            try:
                await self._read_task
            except asyncio.CancelledError:
                pass
            self._read_task = None
        if self._session is not None:
            await self._session.close()
            self._session = None
        logger.info("FIX gateway stopped")

    async def _ensure_started(self) -> IFixSession:
        if not self.is_started:
            await self.start()
        assert self._session is not None
        return self._session

    # ------------------------------------------------------------------
    # read loop
    # ------------------------------------------------------------------

    async def _read_loop(self) -> None:
        session = self._session
        assert session is not None
        while not self._stopping:
            try:
                msg = await session.recv()
            except FixSessionClosed as e:
                if not self._stopping:
                    logger.error("FIX session dropped: %s - pending requests will fail", e)
                    self._fail_pending(FixSessionClosed(str(e)))
                break
            except asyncio.CancelledError:
                raise
            except Exception as e:  # pragma: no cover - defensive
                logger.error("FIX read loop error: %s", e)
                break
            try:
                self._dispatch(msg)
            except Exception:  # pragma: no cover - defensive
                logger.exception("FIX dispatch failed for %r", msg)
        if not self._stopping and self._session is not None:
            self._session = None  # next send_order() re-runs start()

    def _fail_pending(self, exc: Exception) -> None:
        for fut in list(self._pending_er.values()) + list(self._pending_md.values()):
            if not fut.done():
                fut.set_exception(exc)
        self._pending_er.clear()
        self._pending_md.clear()

    def _dispatch(self, msg: FixMessage) -> None:
        msg_type = msg.get(fix.MSG_TYPE)
        if msg_type == fix.MSG_EXECUTION_REPORT:
            report = fix.parse_execution_report(msg)
            self.received_reports.append(report)
            key = report.get("cl_ord_id") or ""
            status = report.get("ord_status")
            fut = self._pending_er.get(key)
            if fut is None or fut.done():
                logger.warning("ExecutionReport for unknown ClOrdID %r (status=%s)",
                               key, status)
                return
            if status in _FINAL_STATUSES:
                # Filled / Partial / Rejected / Canceled / Replaced / Expired:
                # this report ends the wait (send_order raises on the rejects).
                self._pending_er.pop(key, None)
                fut.set_result(report)
            else:
                # New / PendingNew: an ack, not an outcome. A market order at a
                # real LP is usually followed within milliseconds by its fill
                # report - waiting the short ack grace keeps send_order from
                # returning ACK on an order that is actually FILLED.
                asyncio.create_task(self._delayed_ack(key, fut, report))
        elif msg_type == fix.MSG_MARKET_DATA_SNAPSHOT:
            snap = fix.parse_md_snapshot(msg)
            req_id = snap.get("md_req_id") or ""
            fut = self._pending_md.pop(req_id, None)
            if fut is not None and not fut.done():
                fut.set_result(snap)
            if snap.get("symbol") and snap.get("bid") and snap.get("ask"):
                self._quote_cache[snap["symbol"]] = {
                    "bid": snap["bid"],
                    "ask": snap["ask"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
        elif msg_type == fix.MSG_TEST_REQUEST:
            self._send_soon(fix.heartbeat(self.sender_comp_id, self.target_comp_id,
                                          test_req_id=msg.get(fix.TEST_REQ_ID)))
        elif msg_type in (fix.MSG_HEARTBEAT, fix.MSG_LOGON, fix.MSG_LOGOUT):
            logger.debug("FIX admin message 35=%s ignored by gateway", msg_type)
        else:
            logger.warning("unhandled FIX msg type %s", msg_type)

    def _send_soon(self, msg: FixMessage) -> None:
        session = self._session
        if session is None:
            return
        asyncio.create_task(session.send(msg))

    async def _delayed_ack(self, cl_ord_id: str, fut: asyncio.Future, ack_report: Dict[str, Any]) -> None:
        """Resolve an ack-only request once the short grace expires: if the LP
        sent no outcome (fill/reject/cancel) after its New report, the honest
        answer is the ack itself - the order is resting at the LP."""
        try:
            await asyncio.sleep(self.ack_grace_s)
        except asyncio.CancelledError:
            return
        pending = self._pending_er.get(cl_ord_id)
        if pending is fut and not fut.done():
            self._pending_er.pop(cl_ord_id, None)
            fut.set_result(ack_report)

    # ------------------------------------------------------------------
    # ILiquidityGateway
    # ------------------------------------------------------------------

    async def send_order(self, order: Order, gateway_id: str) -> dict:
        """Hedge a client order at the LP. Returns the normalised execution
        report; raises FixTimeout / FixReject / FixSessionClosed otherwise."""
        session = await self._ensure_started()
        cl_ord_id = order.ticket_id
        symbol = order.symbol.upper() if isinstance(order.symbol, str) else str(order.symbol)
        side = SIDE_BY_ORDER_TYPE.get(order.order_type)
        if side is None:  # pragma: no cover - enum is closed
            raise FixGatewayError(f"cannot map order type {order.order_type!r} to FIX Side")
        qty = order.volume_current.value
        if qty <= 0:
            qty = order.volume_initial.value
        ord_type = fix.ORD_TYPE_MARKET
        price: Optional[Decimal] = None
        stop_px: Optional[Decimal] = None
        price_order = getattr(order, "price_order", None)
        px_value = getattr(price_order, "value", price_order)
        if order.order_type in _LIMIT_TYPES:
            ord_type = fix.ORD_TYPE_LIMIT
            price = Decimal(str(px_value))
        elif order.order_type in _STOP_TYPES:
            ord_type = fix.ORD_TYPE_STOP
            stop_px = Decimal(str(px_value))
        elif order.order_type in _STOP_LIMIT_TYPES:
            # MT5 stop-limit carries one trigger; FIX StopLimit wants both. Send the
            # trigger as both fields and let the LP reject if it disagrees.
            ord_type = fix.ORD_TYPE_STOP_LIMIT
            price = Decimal(str(px_value))
            stop_px = Decimal(str(px_value))

        tif = None
        expire_time = None
        if order.time_expiration is not None:
            tif = "6"  # GTD
            expire_time = order.time_expiration

        msg = fix.new_order_single(
            sender=self.sender_comp_id,
            target=self.target_comp_id,
            cl_ord_id=cl_ord_id,
            symbol=symbol,
            side=side,
            order_qty=qty,
            ord_type=ord_type,
            price=price,
            stop_px=stop_px,
            account=self.account,
            time_in_force=tif,
            expire_time=expire_time,
        )

        fut: asyncio.Future = asyncio.get_running_loop().create_future()
        self._pending_er[cl_ord_id] = fut
        try:
            await session.send(msg)
            report = await asyncio.wait_for(fut, timeout=self.timeout_s)
        except asyncio.TimeoutError:
            self._pending_er.pop(cl_ord_id, None)
            raise FixTimeout(
                f"no ExecutionReport for ClOrdID {cl_ord_id} within {self.timeout_s}s - "
                "hedge state UNKNOWN; reconcile before retrying"
            ) from None
        except Exception:
            self._pending_er.pop(cl_ord_id, None)
            raise

        status = report.get("ord_status")
        if status in fix.TERMINAL_REJECT_STATUSES or status == fix.ORD_STATUS_PENDING_CANCEL:
            raise FixReject(
                report,
                f"LP returned OrdStatus={status} for {cl_ord_id}"
                + (f": {report['text']}" if report.get("text") else ""),
            )

        filled = status == fix.ORD_STATUS_FILLED
        partial = status == fix.ORD_STATUS_PARTIALLY_FILLED
        return {
            "status": "FILLED" if filled else ("PARTIAL" if partial else "ACK"),
            "cl_ord_id": cl_ord_id,
            "order_id": report.get("order_id"),
            "gateway_id": gateway_id,
            "symbol": symbol,
            "side": "BUY" if side == fix.SIDE_BUY else "SELL",
            "volume": report.get("cum_qty") or format(qty, "f"),
            "price": report.get("avg_px"),
            "ord_status": status,
            "transact_time": report.get("transact_time"),
            "fix_report": report,
            "stub": False,
        }

    async def cancel_order(self, order_id: str, gateway_id: str) -> bool:
        """Cancel a resting order at the LP; True when the LP confirms 39=4."""
        session = await self._ensure_started()
        cl_ord_id = f"CXL-{uuid.uuid4().hex[:12]}"
        report_seen = await self._find_report(order_id)
        symbol = (report_seen or {}).get("symbol") or ""
        side = (report_seen or {}).get("side") or fix.SIDE_BUY
        msg = fix.order_cancel_request(
            sender=self.sender_comp_id,
            target=self.target_comp_id,
            cl_ord_id=cl_ord_id,
            orig_cl_ord_id=order_id,
            symbol=symbol,
            side=side,
        )
        fut: asyncio.Future = asyncio.get_running_loop().create_future()
        self._pending_er[cl_ord_id] = fut
        try:
            await session.send(msg)
            report = await asyncio.wait_for(fut, timeout=self.timeout_s)
        except asyncio.TimeoutError:
            self._pending_er.pop(cl_ord_id, None)
            raise FixTimeout(f"no cancel report for {order_id} within {self.timeout_s}s") from None
        except Exception:
            self._pending_er.pop(cl_ord_id, None)
            raise
        return report.get("ord_status") == fix.ORD_STATUS_CANCELED

    async def _find_report(self, cl_ord_id: str) -> Optional[Dict[str, Any]]:
        for report in reversed(self.received_reports):
            if report.get("cl_ord_id") == cl_ord_id:
                return report
        return None

    async def get_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Snapshot quotes from the LP via MarketDataRequest(35=V)."""
        session = await self._ensure_started()
        out: Dict[str, Dict[str, Any]] = {}
        requests: Dict[str, tuple] = {}
        for symbol in symbols:
            req_id = uuid.uuid4().hex[:12]
            fut: asyncio.Future = asyncio.get_running_loop().create_future()
            self._pending_md[req_id] = fut
            requests[symbol.upper()] = (req_id, fut)
            await session.send(
                fix.market_data_request(
                    sender=self.sender_comp_id,
                    target=self.target_comp_id,
                    md_req_id=req_id,
                    symbol=symbol.upper(),
                )
            )
        for symbol, (req_id, fut) in requests.items():
            try:
                snap = await asyncio.wait_for(fut, timeout=self.timeout_s)
            except asyncio.TimeoutError:
                self._pending_md.pop(req_id, None)
                logger.warning("MD snapshot for %s timed out", symbol)
                cached = self._quote_cache.get(symbol)
                if cached:
                    out[symbol] = dict(cached)
                continue
            if snap.get("bid") and snap.get("ask"):
                out[symbol] = {
                    "bid": snap["bid"],
                    "ask": snap["ask"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
        return out


# ---------------------------------------------------------------------------
# Environment construction (used by trading_setup when BROKER_LP_GATEWAY=fix)
# ---------------------------------------------------------------------------

def build_fix_gateway_from_env() -> FixLiquidityGateway:
    """
    BROKER_LP_GATEWAY=fix selects this gateway. Settings:

      FIX_SENDER_COMP_ID  (default BROKER)
      FIX_TARGET_COMP_ID  (required for real sessions, default LP)
      FIX_ACCOUNT         (optional, tag 1)
      FIX_ORDER_TIMEOUT_S (default 5)
      BROKER_FIX_SIMULATOR=1 -> in-process SimulatedFixSession (dev/test)
      FIX_SIM_PRICES      JSON {"EURUSD": ["1.10000", "1.10010"]} (simulator
                          only; use STRINGS - JSON floats lose trailing zeros)
      otherwise: FIX_HOST (required) + FIX_PORT (default 5000) -> QuickFixSession
    """
    sender = os.environ.get("FIX_SENDER_COMP_ID", "BROKER").strip() or "BROKER"
    target = os.environ.get("FIX_TARGET_COMP_ID", "LP").strip() or "LP"
    account = os.environ.get("FIX_ACCOUNT", "").strip() or None
    timeout_s = float(os.environ.get("FIX_ORDER_TIMEOUT_S", "5"))
    simulate = os.environ.get("BROKER_FIX_SIMULATOR", "").strip().lower() in ("1", "true", "yes")

    if simulate:
        from decimal import Decimal as _D

        from infrastructure.fix.simulated_session import SimulatedFixSession

        prices: Dict[str, tuple] = {}
        raw = os.environ.get("FIX_SIM_PRICES", "").strip()
        if raw:
            for sym, pair in json.loads(raw).items():
                prices[sym.upper()] = (_D(str(pair[0])), _D(str(pair[1])))
        logger.warning(
            "BROKER_LP_GATEWAY=fix with BROKER_FIX_SIMULATOR=1: A-Book flow is hedged "
            "against an IN-PROCESS SIMULATED LP - no external hedge is placed"
        )
        return FixLiquidityGateway(
            lambda: SimulatedFixSession(sender_comp_id="SIMLP", target_comp_id=sender, prices=prices),
            sender_comp_id=sender,
            target_comp_id=target,
            account=account,
            timeout_s=timeout_s,
        )

    host = os.environ.get("FIX_HOST", "").strip()
    if not host:
        raise RuntimeError(
            "BROKER_LP_GATEWAY=fix requires FIX_HOST/FIX_PORT for a real LP session "
            "(or BROKER_FIX_SIMULATOR=1 for the in-process simulated LP)"
        )
    port = int(os.environ.get("FIX_PORT", "5000"))

    from infrastructure.fix.session import QuickFixSession

    def factory() -> QuickFixSession:
        return QuickFixSession(host=host, port=port, sender_comp_id=sender, target_comp_id=target)

    return FixLiquidityGateway(
        factory,
        sender_comp_id=sender,
        target_comp_id=target,
        account=account,
        timeout_s=timeout_s,
    )


__all__ = [
    "FixLiquidityGateway", "FixGatewayError", "FixTimeout", "FixReject",
    "build_fix_gateway_from_env",
]
