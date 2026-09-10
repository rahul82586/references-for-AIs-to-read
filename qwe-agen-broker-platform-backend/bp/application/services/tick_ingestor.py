"""
Tick Ingestion Service

Background application service that connects to market data feed sources
(Liquidity Providers, Exchanges, Mock feeds) and streams ticks into the MarketDataEngine.
Provides fault-tolerant reconnect loops for each feed stream.

Architectural Rule: Application orchestration service, uses Dependency Injection.
"""
import asyncio
import logging
from typing import List

from core.domains.market_data.engine import MarketDataEngine
from core.ports.interfaces import ITickFeed

logger = logging.getLogger(__name__)


class TickIngestor:
    """
    Background worker service that manages multiple price feeds.
    Runs each feed stream in an async task with automatic reconnection on failure.
    """
    def __init__(self, market_data_engine: MarketDataEngine, feeds: List[ITickFeed]):
        self.market_data_engine = market_data_engine
        self.feeds = feeds
        self._running = False
        self._tasks: List[asyncio.Task] = []

    async def start(self) -> None:
        """Start all feed connection tasks."""
        self._running = True
        logger.info(f"TickIngestor starting with {len(self.feeds)} feed(s)...")
        for feed in self.feeds:
            task = asyncio.create_task(self._run_feed(feed))
            self._tasks.append(task)

    async def _run_feed(self, feed: ITickFeed) -> None:
        """Stream ticks from a single feed with fault-tolerant reconnect handling."""
        while self._running:
            try:
                logger.info(f"Connecting to market data feed: {feed.name}")
                async for tick in feed.stream_ticks():
                    if not self._running:
                        break
                    await self.market_data_engine.process_tick(tick)
            except asyncio.CancelledError:
                logger.info(f"Feed stream cancelled: {feed.name}")
                break
            except Exception as e:
                logger.error(f"Error streaming from feed '{feed.name}': {e}. Reconnecting in 5s...")
                await asyncio.sleep(5)

    async def stop(self) -> None:
        """Stop all background feed streaming tasks gracefully."""
        self._running = False
        for task in self._tasks:
            if not task.done():
                task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        logger.info("TickIngestor stopped")
