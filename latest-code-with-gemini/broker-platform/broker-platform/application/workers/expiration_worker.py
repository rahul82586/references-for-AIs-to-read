"""Pending-order expiration (MT5's ORDER_TIME_SPECIFIED / REQUEST_EXPIRATION).

Before M9, `orders.time_expiration` was a column nothing read: a pending order
with an expiration rested in the book forever. This worker sweeps expired
pendings — immediately on start (orders that expired while the server was
down) and every EXPIRATION_SWEEP_SECONDS (default 15) — cancels them through
the order's own state machine, and publishes ORDER_CANCELLED so subscribers
(the WebSocket bridge, audit) see it.

Time-based, not tick-based: an expiration must fire in a quiet market too.
DAY-mode expiration (end of the trading day) needs the EOD/session schedule
and is a documented gap; SPECIFIED-time is what this implements.
"""
import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Any, Optional

from core.events.domain_events import OrderCancelled
from core.ports.interfaces import IEventBus, IOrderRepository

logger = logging.getLogger(__name__)

DEFAULT_SWEEP_SECONDS = 15


class ExpirationWorker:
    def __init__(
        self,
        order_repo: IOrderRepository,
        event_bus: IEventBus,
        sweep_seconds: Optional[int] = None,
    ):
        self.order_repo = order_repo
        self.event_bus = event_bus
        if sweep_seconds is None:
            raw = os.environ.get("EXPIRATION_SWEEP_SECONDS", "").strip()
            try:
                sweep_seconds = int(raw) if raw else DEFAULT_SWEEP_SECONDS
            except ValueError:
                logger.warning(
                    "EXPIRATION_SWEEP_SECONDS=%r is not an integer; using %d",
                    raw, DEFAULT_SWEEP_SECONDS,
                )
                sweep_seconds = DEFAULT_SWEEP_SECONDS
        self.sweep_seconds = max(1, sweep_seconds)
        self._running = False

    async def start(self) -> None:
        self._running = True
        logger.info("ExpirationWorker started (sweep every %ds)", self.sweep_seconds)
        while self._running:
            try:
                await self.sweep_once()
            except Exception:  # noqa: BLE001 - the loop must survive a bad sweep
                logger.exception("expiration sweep failed")
            await asyncio.sleep(self.sweep_seconds)

    async def stop(self) -> None:
        self._running = False

    async def sweep_once(self, now: Optional[datetime] = None) -> int:
        """Cancel every pending whose time_expiration has passed. Public for
        tests and for an ops 'sweep now' command."""
        now = now or datetime.now(timezone.utc)
        finder = getattr(self.order_repo, "find_expired_orders", None)
        if finder is None:
            logger.error(
                "order repository has no find_expired_orders; expirations cannot "
                "be enforced"
            )
            return 0
        expired = await finder(now)
        cancelled = 0
        for order in expired:
            try:
                order.cancel("expired")  # state machine: CANCELLED + time_done
                await self.order_repo.save(order)
                await self.event_bus.publish(
                    OrderCancelled(
                        aggregate_id=order.ticket_id,
                        payload={
                            "order_id": order.ticket_id,
                            "account_login": str(order.account_login),
                            "symbol": order.symbol,
                            "reason": "expired",
                            "expiration": order.time_expiration.isoformat()
                            if order.time_expiration
                            else None,
                        },
                    )
                )
                cancelled += 1
                logger.info(
                    "order %s (%s %s) cancelled: expired at %s",
                    order.ticket_id, order.symbol,
                    order.order_type.name if hasattr(order.order_type, "name") else order.order_type,
                    order.time_expiration,
                )
            except Exception:  # noqa: BLE001 - one bad order must not stop the sweep
                logger.exception("could not cancel expired order %s", order.ticket_id)
        if cancelled:
            logger.info("expiration sweep cancelled %d order(s)", cancelled)
        return cancelled
