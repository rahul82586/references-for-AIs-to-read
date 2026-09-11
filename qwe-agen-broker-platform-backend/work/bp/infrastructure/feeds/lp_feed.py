"""
Liquidity Provider (LP) Market Data Feed Adapter (Stub)

Adapter contract for connecting real FIX API / WebSocket Liquidity Provider feeds.

Architectural Rule: Infrastructure feed adapter implementing ITickFeed port.
"""
from typing import AsyncIterator
from core.ports.interfaces import ITickFeed
from core.domains.market_data.models import Tick, OrderBook


class LPTickFeed(ITickFeed):
    """
    Adapter for external Liquidity Providers (LMAX, Centroid Bridge, Binance, etc.).
    Will be populated with FIX/WebSocket client protocols in future integration phases.
    """
    def __init__(self, name: str, connection_config: dict):
        self._name = name
        self._config = connection_config

    @property
    def name(self) -> str:
        return self._name

    async def stream_ticks(self) -> AsyncIterator[Tick]:
        """Stream ticks from external LP feed."""
        raise NotImplementedError("Real LP feed integration is pending.")
        yield  # Make it an async generator function

    async def stream_book(self, symbol: str) -> AsyncIterator[OrderBook]:
        """Stream order book snapshots from external LP feed."""
        raise NotImplementedError("Real LP feed integration is pending.")
        yield  # Make it an async generator function
