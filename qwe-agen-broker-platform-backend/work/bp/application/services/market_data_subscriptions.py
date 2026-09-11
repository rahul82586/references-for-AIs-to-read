"""
Market Data Subscriptions - Event Listener Orchestrator

Registers event handlers and wires downstream consumers (Risk Worker, Matching Engine, WebSockets)
to market data events (TICK_RECEIVED, BOOK_UPDATED, BAR_AGGREGATED).

Architectural Rule: Application orchestration layer.
"""
import logging
from typing import Callable, Dict, Optional

from core.domains.market_data.engine import MarketDataEngine
from core.events.domain_events import EventType
from core.ports.interfaces import IEventBus

logger = logging.getLogger(__name__)


class MarketDataSubscriptions:
    """
    Orchestrates market data event subscriptions across bounded contexts.
    """
    def __init__(self, event_bus: IEventBus, market_data_engine: MarketDataEngine):
        self.event_bus = event_bus
        self.market_data_engine = market_data_engine

    async def register(self, on_tick_callback: Optional[Callable[[Dict], None]] = None) -> None:
        """Register callbacks for market data domain events."""
        if on_tick_callback:
            await self.event_bus.subscribe(EventType.TICK_RECEIVED.value, on_tick_callback)
        logger.info("MarketDataSubscriptions event handlers successfully registered.")
