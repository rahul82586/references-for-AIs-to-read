"""
Bar Aggregator - OHLCV Candle Aggregation Service

Aggregates continuous tick feeds into structured OHLCV bars across 9 standard timeframes.
Emits BAR_AGGREGATED events and persists completed bars.

Architectural Rule: Pure domain logic in core/, dependency-injected event bus & repository ports.
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from core.domains.market_data.models import Bar, BarTimeframe, Tick
from core.events.domain_events import BarAggregated, DomainEvent, EventType
from core.ports.interfaces import IBarRepository, IEventBus

logger = logging.getLogger(__name__)


class BarAggregator:
    """
    Aggregates ticks into OHLCV bars for a single symbol and timeframe.
    Mirrors MT5 rate aggregation engine.
    """
    def __init__(
        self,
        symbol: str,
        timeframe: BarTimeframe,
        event_bus: IEventBus,
        bar_repository: Optional[IBarRepository] = None
    ):
        self.symbol = symbol
        self.timeframe = timeframe
        self.event_bus = event_bus
        self.bar_repository = bar_repository
        self.current_bar: Optional[Bar] = None
        self.interval_seconds = self._timeframe_to_seconds(timeframe)

    def _timeframe_to_seconds(self, timeframe: BarTimeframe) -> int:
        """Map timeframe enum to interval duration in seconds."""
        mapping = {
            BarTimeframe.M1: 60,
            BarTimeframe.M5: 300,
            BarTimeframe.M15: 900,
            BarTimeframe.M30: 1800,
            BarTimeframe.H1: 3600,
            BarTimeframe.H4: 14400,
            BarTimeframe.D1: 86400,
            BarTimeframe.W1: 604800,
            BarTimeframe.MN1: 2592000,
        }
        return mapping[timeframe]

    def _get_period_start(self, timestamp: datetime) -> datetime:
        """Calculate the exact period start boundary for a given timestamp."""
        # Ensure UTC timezone
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        if self.timeframe == BarTimeframe.M1:
            return timestamp.replace(second=0, microsecond=0)
        elif self.timeframe == BarTimeframe.M5:
            return timestamp.replace(minute=(timestamp.minute // 5) * 5, second=0, microsecond=0)
        elif self.timeframe == BarTimeframe.M15:
            return timestamp.replace(minute=(timestamp.minute // 15) * 15, second=0, microsecond=0)
        elif self.timeframe == BarTimeframe.M30:
            return timestamp.replace(minute=(timestamp.minute // 30) * 30, second=0, microsecond=0)
        elif self.timeframe == BarTimeframe.H1:
            return timestamp.replace(minute=0, second=0, microsecond=0)
        elif self.timeframe == BarTimeframe.H4:
            return timestamp.replace(hour=(timestamp.hour // 4) * 4, minute=0, second=0, microsecond=0)
        elif self.timeframe == BarTimeframe.D1:
            return timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        elif self.timeframe == BarTimeframe.W1:
            # Align to start of week (Monday)
            days_since_monday = timestamp.weekday()
            start_of_week = timestamp - timedelta(days=days_since_monday)
            return start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        elif self.timeframe == BarTimeframe.MN1:
            return timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            return timestamp.replace(hour=0, minute=0, second=0, microsecond=0)

    async def process_tick(self, tick: Tick) -> None:
        """Process an incoming tick and aggregate into the active bar."""
        period_start = self._get_period_start(tick.timestamp)
        price = tick.mid  # OHLCV bars use the mid price

        if self.current_bar is None:
            # First tick for this symbol/timeframe
            self.current_bar = Bar(
                symbol=self.symbol,
                timeframe=self.timeframe,
                open=price,
                high=price,
                low=price,
                close=price,
                tick_volume=1,
                open_time=period_start
            )
        elif period_start > self.current_bar.open_time:
            # New period boundary crossed — flush completed bar and initialize next bar
            await self._flush_bar()
            self.current_bar = Bar(
                symbol=self.symbol,
                timeframe=self.timeframe,
                open=price,
                high=price,
                low=price,
                close=price,
                tick_volume=1,
                open_time=period_start
            )
        else:
            # Same period — update running bar values
            self.current_bar.update(price)

    async def _flush_bar(self) -> None:
        """Close current bar, persist via repository, and publish BAR_AGGREGATED event."""
        if self.current_bar is None:
            return

        self.current_bar.close_time = datetime.now(timezone.utc)
        bar = self.current_bar

        # Save bar to persistence if repository available
        if self.bar_repository:
            try:
                await self.bar_repository.save_bar(bar)
            except Exception as e:
                logger.error(f"Failed to persist bar {bar.symbol} {bar.timeframe.value}: {e}")

        # Emit domain event
        event = BarAggregated(
            aggregate_id=f"{bar.symbol}_{bar.timeframe.value}",
            payload={
                "symbol": bar.symbol,
                "timeframe": bar.timeframe.value,
                "open": str(bar.open),
                "high": str(bar.high),
                "low": str(bar.low),
                "close": str(bar.close),
                "tick_volume": bar.tick_volume,
                "open_time": bar.open_time.isoformat(),
                "close_time": bar.close_time.isoformat() if bar.close_time else None,
            }
        )
        await self.event_bus.publish(event)
