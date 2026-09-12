"""
Market Data Domain Models

Immutable value objects and entities representing market data concepts:
Ticks, Order Books (DOM), OHLCV Bars, and Tick Statistics.

Architectural Rule: Pure Python, zero framework imports, strict Decimal precision.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import List, Optional


@dataclass(frozen=True)
class Tick:
    """
    Immutable snapshot of a market price at a single moment in time.
    Mirrors MT5 IMTTick.
    """
    symbol: str
    bid: Decimal
    ask: Decimal
    spread: Decimal
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = "INTERNAL"

    def __post_init__(self):
        if not isinstance(self.bid, Decimal) or not isinstance(self.ask, Decimal):
            raise ValueError("Tick prices must be Decimal instances")
        if self.bid <= Decimal('0') or self.ask <= Decimal('0'):
            raise ValueError("Tick prices must be strictly positive")
        if self.ask < self.bid:
            raise ValueError(f"Ask ({self.ask}) must be greater than or equal to Bid ({self.bid})")

    @property
    def mid(self) -> Decimal:
        """Calculate the mid price."""
        return (self.bid + self.ask) / Decimal('2')


@dataclass(frozen=True)
class BookLevel:
    """
    Single price level within a Depth of Market (DOM) / Order Book.
    Mirrors MT5 MTBookItem.
    """
    price: Decimal
    volume: Decimal
    side: str  # "BID" or "ASK"
    source: str = ""

    def __post_init__(self):
        if not isinstance(self.price, Decimal) or not isinstance(self.volume, Decimal):
            raise ValueError("BookLevel price and volume must be Decimal instances")


@dataclass
class OrderBook:
    """
    Full order book (DOM) snapshot for a symbol.
    Contains multiple bid and ask price levels.
    Mirrors MT5 MTBook.
    """
    symbol: str
    bids: List[BookLevel] = field(default_factory=list)  # Sorted descending (best bid first)
    asks: List[BookLevel] = field(default_factory=list)  # Sorted ascending (best ask first)
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def best_bid(self) -> Optional[BookLevel]:
        """Return the best (highest) bid level."""
        return self.bids[0] if self.bids else None

    @property
    def best_ask(self) -> Optional[BookLevel]:
        """Return the best (lowest) ask level."""
        return self.asks[0] if self.asks else None

    @property
    def spread(self) -> Optional[Decimal]:
        """Calculate the top-of-book spread."""
        if self.best_bid and self.best_ask:
            return self.best_ask.price - self.best_bid.price
        return None

    def to_tick(self) -> Tick:
        """Convert top of book snapshot into a Tick object."""
        if not self.best_bid or not self.best_ask:
            raise ValueError(f"Order book for {self.symbol} is empty")
        return Tick(
            symbol=self.symbol,
            bid=self.best_bid.price,
            ask=self.best_ask.price,
            spread=self.spread,
            timestamp=self.updated_at,
            source="AGGREGATED"
        )


class BarTimeframe(Enum):
    """Standard bar aggregation timeframes."""
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"
    W1 = "1w"
    MN1 = "1M"


@dataclass
class Bar:
    """
    OHLCV rate bar aggregated from tick data.
    Mirrors MT5 MTRate.
    """
    symbol: str
    timeframe: BarTimeframe
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    tick_volume: int = 0
    open_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    close_time: Optional[datetime] = None

    def update(self, price: Decimal, volume: int = 1) -> None:
        """Update bar metrics with a new tick price."""
        self.close = price
        self.tick_volume += volume
        if price > self.high:
            self.high = price
        if price < self.low:
            self.low = price

    @property
    def is_complete(self) -> bool:
        """Return True if the bar period has closed."""
        return self.close_time is not None


@dataclass
class TickStat:
    """
    Per-symbol tick execution statistics for system monitoring.
    Mirrors MT5 IMTTickStat.
    """
    symbol: str
    bid_count: int = 0
    ask_count: int = 0
    tick_count: int = 0
    last_bid: Optional[Decimal] = None
    last_ask: Optional[Decimal] = None
    last_spread: Optional[Decimal] = None
    min_spread: Optional[Decimal] = None
    max_spread: Optional[Decimal] = None
    avg_spread: Optional[Decimal] = None
    last_update: Optional[datetime] = None
    ticks_per_second: Decimal = Decimal('0')
