"""
Stub Liquidity Gateway - the ILiquidityGateway implementation for A-Book routing.

This is a STUB and it is built to fail loudly rather than plausibly.

The A-Book path sends client flow to an external liquidity provider. Until a real
FIX/REST adapter exists, that call cannot be made - and the dangerous version of this
class is one that returns a filled execution report anyway, because the platform would
then believe it had hedged exposure it has not hedged. So:

  * every order is acknowledged, with an execution report that says it is a stub;
  * `strict=True` (the default in production wiring) raises instead, so an A-Book
    destination on a server with no LP connected rejects the order back to the client
    rather than pretending to hedge it;
  * every call is recorded, so a test can assert what would have been sent, and an
    operator can see what the router is trying to do.

Swapping in a real adapter means implementing the same three methods against
Centroid Bridge / FIX and registering it under the same DI key. Nothing above this
class changes.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

from core.domains.oms.entities.order import Order
from core.ports.interfaces import ILiquidityGateway

logger = logging.getLogger(__name__)


class LiquidityProviderUnavailable(RuntimeError):
    """Raised in strict mode: there is no LP behind this gateway."""


class StubLiquidityGateway(ILiquidityGateway):
    """Simulated LP connectivity. Moves no money and says so on every call."""

    def __init__(self, *, strict: bool = True, latency_ms: int = 0) -> None:
        self.strict = strict
        self.latency_ms = latency_ms
        #: every call made, oldest first - the audit trail of an unconnected LP
        self.sent_orders: List[Dict[str, Any]] = []
        self.cancelled_orders: List[Dict[str, str]] = []
        self.quote_requests: List[List[str]] = []
        #: gateway_id -> {symbol: {"bid":..,"ask":..}} installed for testing
        self._quotes: Dict[str, Dict[str, Dict[str, Decimal]]] = {}

    # ------------------------------------------------------------------
    # ILiquidityGateway
    # ------------------------------------------------------------------

    async def send_order(self, order: Order, gateway_id: str) -> dict:
        """Send to an external LP. Returns the execution report."""
        record = {
            "cl_ord_id": order.ticket_id,
            "gateway_id": gateway_id,
            "symbol": order.symbol,
            "side": order.order_type.value,
            "volume": str(order.volume_current.value),
            "price": str(order.price_order.value) if order.price_order else None,
            "account_login": order.account_login,
            "sent_at": datetime.now(timezone.utc).isoformat(),
        }
        self.sent_orders.append(record)

        if self.strict:
            logger.error(
                "A-Book order %s routed to gateway %s but no liquidity provider is "
                "connected; refusing to fake a hedge",
                order.ticket_id,
                gateway_id,
            )
            raise LiquidityProviderUnavailable(
                f"gateway {gateway_id!r} has no connected liquidity provider. Configure a "
                f"real ILiquidityGateway adapter, or route this flow to B-Book."
            )

        logger.warning(
            "STUB gateway %s acknowledged order %s - no external hedge was placed",
            gateway_id,
            order.ticket_id,
        )
        return {
            "status": "ACK_STUB",
            "cl_ord_id": order.ticket_id,
            "order_id": f"STUB-{uuid.uuid4().hex[:12]}",
            "gateway_id": gateway_id,
            "symbol": order.symbol,
            "side": order.order_type.value,
            "volume": str(order.volume_current.value),
            "price": str(order.price_order.value) if order.price_order else None,
            "stub": True,
            "warning": "no real liquidity provider is connected; exposure is NOT hedged",
            "transact_time": record["sent_at"],
        }

    async def cancel_order(self, order_id: str, gateway_id: str) -> bool:
        self.cancelled_orders.append({"order_id": order_id, "gateway_id": gateway_id})
        if self.strict:
            raise LiquidityProviderUnavailable(
                f"gateway {gateway_id!r} has no connected liquidity provider"
            )
        logger.warning("STUB gateway %s acknowledged cancel of %s", gateway_id, order_id)
        return True

    async def get_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        self.quote_requests.append(list(symbols))
        if self.strict:
            raise LiquidityProviderUnavailable(
                "no connected liquidity provider; cannot fetch LP quotes"
            )
        now = datetime.now(timezone.utc).isoformat()
        out: Dict[str, Dict[str, Any]] = {}
        for symbol in symbols:
            quote = self._quotes.get("*", {}).get(symbol)
            if quote:
                out[symbol] = {"bid": str(quote["bid"]), "ask": str(quote["ask"]), "timestamp": now}
        return out

    # ------------------------------------------------------------------
    # Test / configuration helpers
    # ------------------------------------------------------------------

    def install_quote(self, symbol: str, bid: Decimal, ask: Decimal, gateway_id: str = "*") -> None:
        """Provide a quote this stub will return (non-strict mode only)."""
        self._quotes.setdefault(gateway_id, {})[symbol] = {
            "bid": Decimal(str(bid)),
            "ask": Decimal(str(ask)),
        }


__all__ = ["StubLiquidityGateway", "LiquidityProviderUnavailable"]
