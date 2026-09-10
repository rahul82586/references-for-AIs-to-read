"""
Market Data Dependency Injection Container & Setup Factory

Assembles and wires the full Market Data Layer pipeline:
MockTickFeed -> TickIngestor -> MarketDataEngine -> RedisMarketDataCache & BarRepository,
then attaches the TickMarginPipeline so that a tick drives PnL, equity and the margin
state machine.

Architectural Rule: Application DI factory. Nothing in this module runs at import time;
call build_market_data_stack() from the process entrypoint that owns the event bus.
"""
import logging
from typing import Any, Dict

from application.services.market_data_subscriptions import MarketDataSubscriptions
from application.services.tick_ingestor import TickIngestor
from application.services.tick_margin_pipeline import TickMarginPipeline
from core.domains.market_data.engine import MarketDataEngine
from core.domains.market_data.feed_access import tick_from_event
from core.domains.risk.engine import RiskEngine
from core.events.domain_events import EventType
from core.ports.interfaces import (
    IAccountRepository,
    IBarRepository,
    IEventBus,
    IPositionRepository,
    ISymbolRepository,
)
from infrastructure.feeds.mock_feed import MockTickFeed
from infrastructure.persistence.redis_market_data import RedisMarketDataCache

logger = logging.getLogger(__name__)


async def on_tick_received(event: Any, tick_pipeline: TickMarginPipeline) -> None:
    """Bridge a TickReceived domain event into the margin pipeline.

    This looked for `payload["tick"]`. MarketDataEngine publishes the tick as flat
    string fields - symbol, bid, ask, spread, timestamp - so that the event survives
    JSON serialisation onto Redis, and there is no "tick" key to find. The bridge
    therefore returned on every tick and the margin-call / stop-out state machine never
    ran, silently: an empty payload and an account with no open positions look the same
    from in here. tick_from_event rebuilds the Tick from either shape.
    """
    tick = tick_from_event(event)
    if tick is not None:
        await tick_pipeline.process_tick(tick)


def build_tick_margin_pipeline(container: Any) -> TickMarginPipeline:
    """Instantiate the margin pipeline from a resolve()-capable DI container.

    This is the heartbeat of the broker: Tick -> Position PnL -> Account Equity ->
    Margin State Machine -> StopOutEntered. It is deliberately a factory rather than
    module-level state, so that nothing touches the database or the event bus at
    import time and so that tests can build one against mocks.
    """
    return TickMarginPipeline(
        position_repo=container.resolve(IPositionRepository),
        account_repo=container.resolve(IAccountRepository),
        symbol_repo=container.resolve(ISymbolRepository),
        risk_engine=container.resolve(RiskEngine),
        event_bus=container.resolve(IEventBus),
    )


def wire_tick_subscriptions(container: Any, tick_pipeline: TickMarginPipeline) -> None:
    """Subscribe the pipeline to TICK_RECEIVED on the shared event bus."""
    event_bus = container.resolve(IEventBus)

    async def _handler(event: Any) -> None:
        await on_tick_received(event, tick_pipeline)

    event_bus.subscribe(EventType.TICK_RECEIVED, _handler)
    logger.info("TickMarginPipeline subscribed to TICK_RECEIVED")


def build_market_data_stack(container: Any) -> Dict[str, Any]:
    """Assemble the market data stack and return its components by name.

    Called once, from the process entrypoint that owns the event bus - not at import
    time. Returns the pieces so the caller can register them back into the container.
    """
    tick_pipeline = build_tick_margin_pipeline(container)
    wire_tick_subscriptions(container, tick_pipeline)

    components: Dict[str, Any] = {"tick_pipeline": tick_pipeline}
    logger.info("Market Data Layer components successfully assembled via DI container.")
    return components
