"""
Background Tick & Bar Persistence Worker for ClickHouse Time-Series Data.
"""
import asyncio
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

from core.domains.market_data.models import Bar, BarTimeframe, Tick
from core.events.domain_events import DomainEvent, EventType
from core.ports.interfaces import IEventBus, IHistoricalBarRepository, IHistoricalTickRepository

logger = logging.getLogger(__name__)


class TickPersistenceWorker:
    """
    Background worker listening to TICK_RECEIVED and BAR_AGGREGATED events,
    persisting market data to ClickHouse in fault-tolerant high-throughput batches.
    """

    def __init__(
        self,
        event_bus: IEventBus,
        tick_repo: IHistoricalTickRepository,
        bar_repo: IHistoricalBarRepository,
        batch_size: int = 1000,
        flush_interval_seconds: int = 5,
    ):
        self.event_bus = event_bus
        self.tick_repo = tick_repo
        self.bar_repo = bar_repo
        self.batch_size = batch_size
        self.flush_interval = flush_interval_seconds
        self.tick_buffer: List[Tick] = []
        self.bar_buffer: List[Bar] = []
        self._running = False
        self._flush_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Starts event subscriptions and periodic background flush task."""
        self._running = True
        logger.info("TickPersistenceWorker started.")

        # Subscribe to domain events
        await self.event_bus.subscribe(EventType.TICK_RECEIVED.value, self._on_tick_received)
        await self.event_bus.subscribe(EventType.BAR_AGGREGATED.value, self._on_bar_aggregated)

        # Start periodic flush loop task
        self._flush_task = asyncio.create_task(self._flush_loop())

    async def _on_tick_received(self, event: DomainEvent) -> None:
        """Buffers tick events for batch insert."""
        try:
            payload = event.payload
            ts = payload.get("timestamp")
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts)
            elif not isinstance(ts, datetime):
                ts = datetime.now(timezone.utc)

            tick = Tick(
                symbol=str(payload["symbol"]),
                bid=Decimal(str(payload["bid"])),
                ask=Decimal(str(payload["ask"])),
                spread=Decimal(str(payload.get("spread", Decimal(str(payload["ask"])) - Decimal(str(payload["bid"]))))),
                timestamp=ts,
                source=str(payload.get("source", "PERSISTENCE_WORKER")),
            )
            self.tick_buffer.append(tick)

            if len(self.tick_buffer) >= self.batch_size:
                await self._flush_ticks()
        except Exception as e:
            logger.error(f"Error handling TICK_RECEIVED event in TickPersistenceWorker: {e}")

    async def _on_bar_aggregated(self, event: DomainEvent) -> None:
        """Buffers aggregated bar events for batch insert."""
        try:
            payload = event.payload
            open_t = payload.get("open_time")
            if isinstance(open_t, str):
                open_t = datetime.fromisoformat(open_t)
            elif not isinstance(open_t, datetime):
                open_t = datetime.now(timezone.utc)

            close_t = payload.get("close_time")
            if isinstance(close_t, str):
                close_t = datetime.fromisoformat(close_t)
            elif not isinstance(close_t, datetime):
                close_t = datetime.now(timezone.utc)

            tf_val = str(payload.get("timeframe", "1m")).strip()
            tf_obj = BarTimeframe(tf_val) if tf_val in [str(e.value).strip() for e in BarTimeframe] else BarTimeframe.M1


            bar = Bar(
                symbol=str(payload["symbol"]),
                timeframe=tf_obj,
                open=Decimal(str(payload["open"])),
                high=Decimal(str(payload["high"])),
                low=Decimal(str(payload["low"])),
                close=Decimal(str(payload["close"])),
                tick_volume=int(payload.get("tick_volume", 1)),
                open_time=open_t,
                close_time=close_t,
            )
            self.bar_buffer.append(bar)

            if len(self.bar_buffer) >= self.batch_size:
                await self._flush_bars()
        except Exception as e:
            logger.error(f"Error handling BAR_AGGREGATED event in TickPersistenceWorker: {e}")

    async def _flush_loop(self) -> None:
        """Periodically flushes buffered market data to ClickHouse."""
        while self._running:
            try:
                await asyncio.sleep(self.flush_interval)
                if self.tick_buffer:
                    await self._flush_ticks()
                if self.bar_buffer:
                    await self._flush_bars()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Unexpected error in TickPersistenceWorker flush loop: {e}")

    async def _flush_ticks(self) -> None:
        """Flushes buffered ticks to ClickHouse repository."""
        if not self.tick_buffer:
            return
        to_flush = list(self.tick_buffer)
        self.tick_buffer.clear()
        try:
            await self.tick_repo.save_ticks_batch(to_flush)
            logger.debug(f"Flushed {len(to_flush)} ticks to ClickHouse.")
        except Exception as e:
            logger.error(f"Failed to flush {len(to_flush)} ticks to ClickHouse: {e}")

    async def _flush_bars(self) -> None:
        """Flushes buffered bars to ClickHouse repository."""
        if not self.bar_buffer:
            return
        to_flush = list(self.bar_buffer)
        self.bar_buffer.clear()
        try:
            await self.bar_repo.save_bars_batch(to_flush)
            logger.debug(f"Flushed {len(to_flush)} bars to ClickHouse.")
        except Exception as e:
            logger.error(f"Failed to flush {len(to_flush)} bars to ClickHouse: {e}")

    async def stop(self) -> None:
        """Stops the worker loop and flushes all remaining items."""
        self._running = False
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
        await self._flush_ticks()
        await self._flush_bars()
        logger.info("TickPersistenceWorker stopped.")
