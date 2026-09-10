"""
Mock Market Data Feed - Random Walk Tick & Book Generator

Generates realistic random-walk price ticks and order book depth snapshots for testing.

Architectural Rule: Infrastructure feed adapter implementing ITickFeed port.
Decimal Precision Rule: All random-walk math converts floats via Decimal(str(value)).
"""
import asyncio
import random
from datetime import datetime, timezone
from decimal import Decimal
from typing import AsyncIterator, Dict, List

from core.domains.market_data.models import BookLevel, OrderBook, Tick
from core.ports.interfaces import ITickFeed


class MockTickFeed(ITickFeed):
    """
    Simulates a live liquidity provider feed emitting random walk ticks.
    Enforces strict Decimal conversion to prevent floating-point contamination.
    """
    def __init__(
        self,
        symbols: List[str],
        tick_rate_ms: int = 100,
        seed: int = 42
    ):
        self.symbols = symbols
        self.tick_rate_ms = tick_rate_ms
        self._rng = random.Random(seed)

        self._prices: Dict[str, Decimal] = {
            "EURUSD": Decimal('1.0800'),
            "GBPUSD": Decimal('1.2600'),
            "USDJPY": Decimal('150.00'),
            "XAUUSD": Decimal('2400.00'),
            "BTCUSD": Decimal('65000.00'),
        }
        self._spreads: Dict[str, Decimal] = {
            "EURUSD": Decimal('0.00010'),
            "GBPUSD": Decimal('0.00012'),
            "USDJPY": Decimal('0.010'),
            "XAUUSD": Decimal('0.30'),
            "BTCUSD": Decimal('10.00'),
        }

    @property
    def name(self) -> str:
        return "MockFeed"

    async def stream_ticks(self) -> AsyncIterator[Tick]:
        """Generate a continuous stream of random-walk Tick instances."""
        while True:
            symbol = self._rng.choice(self.symbols)
            base_price = self._prices.get(symbol, Decimal('1.0000'))
            spread = self._spreads.get(symbol, Decimal('0.00010'))

            # Compute random delta safely converting float to Decimal string
            raw_factor = self._rng.uniform(-0.0003, 0.0003)
            delta_factor = Decimal(str(round(raw_factor, 6)))
            price_delta = base_price * delta_factor

            new_bid = (base_price + price_delta).quantize(spread)
            if new_bid <= Decimal('0'):
                new_bid = base_price

            new_ask = new_bid + spread
            self._prices[symbol] = new_bid

            yield Tick(
                symbol=symbol,
                bid=new_bid,
                ask=new_ask,
                spread=spread,
                timestamp=datetime.now(timezone.utc),
                source="MOCK"
            )

            await asyncio.sleep(self.tick_rate_ms / 1000.0)

    async def stream_book(self, symbol: str) -> AsyncIterator[OrderBook]:
        """Generate order book DOM depth snapshots for a symbol."""
        while True:
            base_price = self._prices.get(symbol, Decimal('1.0000'))
            spread = self._spreads.get(symbol, Decimal('0.00010'))

            bids = []
            asks = []

            for i in range(5):
                step = Decimal(str(i)) * spread
                vol = Decimal(str(self._rng.randint(1, 50)))

                bids.append(BookLevel(
                    price=base_price - step,
                    volume=vol,
                    side="BID",
                    source="MOCK"
                ))
                asks.append(BookLevel(
                    price=base_price + spread + step,
                    volume=vol,
                    side="ASK",
                    source="MOCK"
                ))

            yield OrderBook(
                symbol=symbol,
                bids=bids,
                asks=asks,
                updated_at=datetime.now(timezone.utc)
            )

            await asyncio.sleep(0.5)
