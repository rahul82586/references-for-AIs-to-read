"""
Market Data Historical Endpoints Router (Ticks & OHLCV Bars).
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status

from api.di_providers import get_historical_tick_repository, get_historical_bar_repository
from core.domains.market_data.models import BarTimeframe
from core.ports.interfaces import IHistoricalTickRepository, IHistoricalBarRepository

router = APIRouter(prefix="/api/v1/market-data", tags=["Market Data"])


@router.get("/history/{symbol}/ticks")
async def get_tick_history(
    symbol: str,
    start: Optional[datetime] = Query(None, description="Start timestamp in ISO format"),
    end: Optional[datetime] = Query(None, description="End timestamp in ISO format"),
    limit: int = Query(10000, ge=1, le=100000, description="Max number of ticks"),
    tick_repo: Optional[IHistoricalTickRepository] = Depends(get_historical_tick_repository),
):
    """Retrieve historical tick series for a symbol."""
    now = datetime.now(timezone.utc)
    if not end:
        end = now
    if not start:
        start = end - timedelta(days=1)

    ticks = []
    if tick_repo:
        try:
            ticks = await tick_repo.get_ticks(symbol=symbol.upper(), start=start, end=end, limit=limit)
        except Exception:
            pass

    return {
        "symbol": symbol.upper(),
        "count": len(ticks),
        "ticks": [
            {
                "bid": str(t.bid),
                "ask": str(t.ask),
                "spread": str(t.spread),
                "timestamp": t.timestamp.isoformat() if hasattr(t.timestamp, "isoformat") else str(t.timestamp),
                "source": t.source,
            }
            for t in ticks
        ],
    }


@router.get("/history/{symbol}/bars")
async def get_bar_history(
    symbol: str,
    timeframe: BarTimeframe = Query(BarTimeframe.M1, description="Bar timeframe e.g. 1m, 5m, 1h, 1d"),
    limit: int = Query(1000, ge=1, le=10000, description="Max number of OHLCV bars"),
    bar_repo: Optional[IHistoricalBarRepository] = Depends(get_historical_bar_repository),
):
    """Retrieve historical OHLCV rate bars for a symbol."""
    bars = []
    if bar_repo:
        try:
            bars = await bar_repo.get_bars(symbol=symbol.upper(), timeframe=timeframe, limit=limit)
        except Exception:
            pass

    return {
        "symbol": symbol.upper(),
        "timeframe": timeframe.value if hasattr(timeframe, "value") else str(timeframe),
        "count": len(bars),
        "bars": [
            {
                "open": str(b.open),
                "high": str(b.high),
                "low": str(b.low),
                "close": str(b.close),
                "volume": b.tick_volume,
                "open_time": b.open_time.isoformat() if hasattr(b.open_time, "isoformat") else str(b.open_time),
                "close_time": b.close_time.isoformat() if hasattr(b.close_time, "isoformat") else str(b.close_time) if b.close_time else None,
            }
            for b in bars
        ],
    }
