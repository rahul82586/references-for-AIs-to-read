"""Server-side SL/TP execution — the triggers MT5 runs on the trade server.

Before M9 a position's Stop Loss and Take Profit were DECORATION: stored on
the order, sometimes on the position, fired by nothing. A client who set a
stop had no stop. This worker subscribes to TICK_RECEIVED and closes
triggered positions at MARKET, the way MT5 does:

  * BUY  position: SL fires when the BID reaches it (the price the client can
    sell at); TP fires when the BID reaches it.
  * SELL position: SL/TP fire against the ASK.
  * The fill is at the CURRENT market price, not the trigger level: "a market
    that has already moved past the trigger is the normal case" — a gapped
    market closes at the gap, and the realised loss is booked honestly
    (converted, through the M6 ClosePositionHandler + RiskEngine path).
  * The closing deal and order carry reason SL / TP (MT5 EnDealReason), so
    statements and the audit trail say WHY the position closed.

Routing note: MT5 feeds SL/TP activations through the routing table as
REQUEST_SL / REQUEST_TP. This worker closes directly instead — a REJECT rule
must not be able to stop a client's stop-loss, and the dealer-interception
variants of those request types need dealer sessions that do not exist yet.
The request bits are modelled (RouteRequest.SL/TP) for when they are.

Single-node note: the in-flight set de-duplicates within this process; two
NODES sharing a Redis bus would each fire the trigger (the same documented
cross-node caveat as the margin pipeline — dedupe belongs to the cluster
milestone, and the close itself is idempotent-ish: the second close finds the
position already done and the handler refuses it).
"""
import logging
from decimal import Decimal
from typing import Any, Optional, Set, Tuple

from application.commands.close_position import ClosePositionCommand
from core.domains.market_data.feed_access import tick_ask, tick_bid, tick_from_event
from core.domains.oms.entities.position import Position
from core.domains.oms.enums import PositionAction
from core.events.domain_events import EventType
from core.ports.interfaces import IEventBus, IPositionRepository

logger = logging.getLogger(__name__)


class SlTpWorker:
    """Fires SL/TP triggers off every tick for the ticked symbol."""

    def __init__(
        self,
        position_repo: IPositionRepository,
        close_position_handler: Any,
        event_bus: IEventBus,
    ):
        self.position_repo = position_repo
        self.close_handler = close_position_handler
        self.event_bus = event_bus
        self._running = False
        self._subscribed = False
        self._in_flight: Set[str] = set()

    async def start(self) -> None:
        """Subscribe to the tick stream (once). Registration is synchronous on both buses."""
        self._running = True
        if not self._subscribed:
            self.event_bus.subscribe(EventType.TICK_RECEIVED, self.on_tick_event)
            self._subscribed = True
        logger.info("SlTpWorker subscribed to TICK_RECEIVED (server-side SL/TP armed)")

    async def stop(self) -> None:
        self._running = False
        try:
            self.event_bus.unsubscribe(EventType.TICK_RECEIVED, self.on_tick_event)
        except Exception:  # noqa: BLE001 - shutdown must not raise
            pass
        logger.info("SlTpWorker stopped")

    async def on_tick_event(self, event: Any) -> None:
        if not self._running:
            return
        tick = tick_from_event(event)
        if tick is None:
            return
        bid, ask = tick_bid(tick), tick_ask(tick)
        if bid is None or ask is None:
            return
        try:
            bid, ask = Decimal(str(bid)), Decimal(str(ask))
            await self.process_tick(str(tick.symbol), bid, ask)
        except Exception:  # noqa: BLE001 - one bad tick must not kill the subscription
            logger.exception("SL/TP processing failed for tick %s", getattr(tick, "symbol", "?"))

    async def process_tick(self, symbol: str, bid: Decimal, ask: Decimal) -> int:
        """Check every open position in `symbol`; close the triggered ones.
        Returns the number of positions closed (public for tests/ops)."""
        getter = getattr(self.position_repo, "get_by_symbol", None)
        if getter is None:
            logger.error(
                "position repository has no get_by_symbol; SL/TP triggers cannot "
                "be evaluated for %s", symbol,
            )
            return 0
        positions = await getter(symbol)
        closed = 0
        for position in positions:
            if position.position_id in self._in_flight:
                continue
            trigger = self._trigger_for(position, bid, ask)
            if trigger is None:
                continue
            reason, exec_price = trigger
            self._in_flight.add(position.position_id)
            try:
                await self.close_handler.handle(
                    ClosePositionCommand(
                        account_login=position.account_login,
                        position_id=position.position_id,
                        volume=position.volume.value,
                        price=exec_price,
                        comment=f"{reason} triggered at {exec_price}",
                        reason=reason,
                    )
                )
                closed += 1
                logger.info(
                    "position %s (%s %s) closed by %s at %s",
                    position.position_id, position.action.name if hasattr(position.action, "name") else position.action,
                    position.symbol, reason, exec_price,
                )
            except Exception:  # noqa: BLE001 - a failed close must not stop the sweep
                logger.exception(
                    "%s close FAILED for position %s - the position is still open "
                    "and still triggering; it will be retried on the next tick",
                    reason, position.position_id,
                )
            finally:
                self._in_flight.discard(position.position_id)
        return closed

    @staticmethod
    def _trigger_for(position: Position, bid: Decimal, ask: Decimal) -> Optional[Tuple[str, Decimal]]:
        """('SL'|'TP', market price) when triggered, else None.

        SL is checked before TP: in a market wild enough to touch both, the
        stop is the conservative answer. Longs are valued at the bid, shorts
        at the ask — the same side convention the PnL engine uses.
        """
        is_buy = position.action == PositionAction.BUY
        sl = position.price_sl.value if position.price_sl else None
        tp = position.price_tp.value if position.price_tp else None
        if is_buy:
            if sl is not None and bid <= sl:
                return "SL", bid
            if tp is not None and bid >= tp:
                return "TP", bid
        else:
            if sl is not None and ask >= sl:
                return "SL", ask
            if tp is not None and ask <= tp:
                return "TP", ask
        return None
