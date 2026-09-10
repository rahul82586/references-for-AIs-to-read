"""
Step M0 part 6 - the last four import/NameError defects.

Two of these are chat-transcript snippets pasted into module scope, where they execute
on import and reference names that were never defined:

  application/di/market_data_setup.py
      Module-level `tick_pipeline = TickMarginPipeline(container.resolve(...))` and
      `event_bus.subscribe(...)` - container, event_bus, IPositionRepository,
      IAccountRepository, ISymbolRepository and RiskEngine were all undefined, and the
      "# 1. Instantiate the Pipeline" / "# 2. Subscribe to Tick events" comments are
      the original chat instructions still sitting in the source. Turned into a factory
      function, which is what the module's own docstring says it is.

  infrastructure/persistence/di_setup.py
      `container.register(IHolidayRepository, holiday_repo)` inside a function that
      builds and RETURNS a dict. `container` and `IHolidayRepository` were undefined, so
      the entire persistence layer blew up the moment it was called - and holiday_repo
      was built but never returned, so it could not be injected either.

  infrastructure/persistence/repositories/position_repository.py
      AsyncSession used in signatures but never imported.

  infrastructure/persistence/unit_of_work.py
      No defect of its own; it failed only because it imports position_repository.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
if not (ROOT / "application" / "di" / "market_data_setup.py").is_file():
    raise SystemExit(f"not a broker-platform root: {ROOT}")


def load(rel: str) -> str:
    with open(ROOT / rel, encoding="utf-8", newline="") as fh:
        return fh.read()


def save(rel: str, text: str, *, crlf: bool) -> None:
    normalised = text.replace("\r\n", "\n")
    with open(ROOT / rel, "w", encoding="utf-8", newline="") as fh:
        fh.write(normalised.replace("\n", "\r\n") if crlf else normalised)


# ===========================================================================
# position_repository.py - AsyncSession used but never imported
# ===========================================================================

REL = "infrastructure/persistence/repositories/position_repository.py"
text = load(REL)
crlf = "\r\n" in text
# Part 1 already inserted the datetime import, so anchor on typing + sqlalchemy.
old = "from typing import List, Optional\nfrom sqlalchemy import select"
new = (
    "from typing import List, Optional\n"
    "from sqlalchemy import select\n"
    "from sqlalchemy.ext.asyncio import AsyncSession"
)
if old.replace("\n", "\r\n") in text:
    text = text.replace(old.replace("\n", "\r\n"), new.replace("\n", "\r\n"), 1)
elif old in text:
    text = text.replace(old, new, 1)
else:
    raise SystemExit(f"[FAIL] {REL}: import block not found")
save(REL, text, crlf=crlf)
print(f"  ok  {REL}: imported AsyncSession")

# ===========================================================================
# di_setup.py - undefined `container`, and holiday_repo built but not returned
# ===========================================================================

REL = "infrastructure/persistence/di_setup.py"
text = load(REL)
crlf = "\r\n" in text
work = text.replace("\r\n", "\n")

old = """    # Initialize repositories in dependency order
    # Inside your DI setup function, add:
    holiday_repo = SQLAlchemyHolidayRepository(session_factory)
    container.register(IHolidayRepository, holiday_repo)
    group_repo = SqlGroupRepository(session_factory)"""
new = """    # Initialize repositories in dependency order. The returned dict IS the container
    # payload: api/di_providers.register_di_providers() consumes it, and
    # get_di_container().resolve(IHolidayRepository) maps the port to 'holiday_repo'.
    holiday_repo = SQLAlchemyHolidayRepository(session_factory)
    group_repo = SqlGroupRepository(session_factory)"""
if old not in work:
    raise SystemExit(f"[FAIL] {REL}: register block not found")
work = work.replace(old, new, 1)

old_ret = """    return {
        'group_repo': group_repo,"""
new_ret = """    return {
        'holiday_repo': holiday_repo,
        'group_repo': group_repo,"""
if old_ret not in work:
    raise SystemExit(f"[FAIL] {REL}: return block not found")
work = work.replace(old_ret, new_ret, 1)

save(REL, work, crlf=crlf)
print(f"  ok  {REL}: removed undefined container.register, returned holiday_repo")

# ===========================================================================
# market_data_setup.py - chat snippet at module scope
# ===========================================================================

REL = "application/di/market_data_setup.py"
MARKET_DATA_SETUP = '''"""
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
    """Bridge a TickReceived domain event into the margin pipeline."""
    tick = event.payload.get("tick") if hasattr(event, "payload") else None
    if tick:
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
'''
save(REL, MARKET_DATA_SETUP, crlf=True)
print(f"  ok  {REL}: module-scope chat snippet replaced with factories")
