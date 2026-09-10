"""
Unit Tests for Phase 12a: Time-Series Persistence with ClickHouse.
"""
import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from core.domains.market_data.models import Tick, Bar, BarTimeframe
from core.events.domain_events import DomainEvent, EventType
from infrastructure.persistence.clickhouse_client import ClickHouseClient
from infrastructure.persistence.repositories.clickhouse_tick_repository import ClickHouseTickRepository
from infrastructure.persistence.repositories.clickhouse_bar_repository import ClickHouseBarRepository
from application.services.tick_persistence_worker import TickPersistenceWorker


class MockEventBus:
    def __init__(self):
        self.subscriptions = {}
        self.published_events = []

    async def publish(self, event: DomainEvent) -> None:
        self.published_events.append(event)
        callbacks = self.subscriptions.get(event.event_type.value, [])
        for cb in callbacks:
            await cb(event)

    async def subscribe(self, channel: str, callback) -> None:
        if channel not in self.subscriptions:
            self.subscriptions[channel] = []
        self.subscriptions[channel].append(callback)

    async def disconnect(self) -> None:
        pass


@pytest.mark.asyncio
async def test_clickhouse_client_in_memory_fallback():
    client = ClickHouseClient(host="invalid_host", port=9999)
    await client.connect()


    columns = ["symbol", "bid", "ask", "last", "volume", "timestamp"]
    now = datetime.now(timezone.utc)
    data = [("EURUSD", 1.0850, 1.0852, 1.0850, 0.0002, now)]

    await client.insert_batch("ticks", columns, data)
    rows = await client.execute("SELECT * FROM ticks WHERE symbol = 'EURUSD'", {"symbol": "EURUSD"})
    assert len(rows) == 1
    assert rows[0]["symbol"] == "EURUSD"
    assert rows[0]["bid"] == 1.0850

    await client.close()


@pytest.mark.asyncio
async def test_decimal_to_float_and_float_to_decimal_casting():
    client = ClickHouseClient(host="invalid_host", port=9999)
    await client.connect()
    tick_repo = ClickHouseTickRepository(client)
    bar_repo = ClickHouseBarRepository(client)

    now = datetime.now(timezone.utc)
    tick = Tick(
        symbol="GBPUSD",
        bid=Decimal("1.26543"),
        ask=Decimal("1.26563"),
        spread=Decimal("0.00020"),
        timestamp=now,
        source="TEST_FEED"
    )

    # Insert with Decimal values
    await tick_repo.save_tick(tick)

    # Read back and verify Decimal casting
    fetched_ticks = await tick_repo.get_ticks("GBPUSD", start=now - timedelta(seconds=10), end=now + timedelta(seconds=10))
    assert len(fetched_ticks) == 1
    retrieved_tick = fetched_ticks[0]

    assert isinstance(retrieved_tick.bid, Decimal)
    assert isinstance(retrieved_tick.ask, Decimal)
    assert retrieved_tick.bid == Decimal("1.26543")
    assert retrieved_tick.ask == Decimal("1.26563")

    # Bar Roundtrip
    bar = Bar(
        symbol="GBPUSD",
        timeframe=BarTimeframe.M1,
        open=Decimal("1.26500"),
        high=Decimal("1.26600"),
        low=Decimal("1.26450"),
        close=Decimal("1.26550"),
        tick_volume=150,
        open_time=now - timedelta(minutes=1),
        close_time=now
    )

    await bar_repo.save_bar(bar)
    fetched_bars = await bar_repo.get_bars("GBPUSD", timeframe=BarTimeframe.M1)
    assert len(fetched_bars) == 1
    retrieved_bar = fetched_bars[0]

    assert isinstance(retrieved_bar.open, Decimal)
    assert isinstance(retrieved_bar.high, Decimal)
    assert retrieved_bar.open == Decimal("1.265")
    assert retrieved_bar.high == Decimal("1.266")


@pytest.mark.asyncio
async def test_tick_persistence_worker_batching_and_events():
    event_bus = MockEventBus()
    client = ClickHouseClient(host="invalid_host", port=9999)
    await client.connect()

    tick_repo = ClickHouseTickRepository(client)
    bar_repo = ClickHouseBarRepository(client)

    worker = TickPersistenceWorker(
        event_bus=event_bus,
        tick_repo=tick_repo,
        bar_repo=bar_repo,
        batch_size=5,
        flush_interval_seconds=1
    )

    await worker.start()
    now = datetime.now(timezone.utc)

    # Publish 4 ticks (under batch threshold 5)
    for i in range(4):
        event = DomainEvent(
            event_type=EventType.TICK_RECEIVED,
            aggregate_id="USDJPY",
            payload={
                "symbol": "USDJPY",
                "bid": f"155.1{i}",
                "ask": f"155.1{i+2}",
                "spread": "0.02",
                "timestamp": now.isoformat(),
                "source": "MOCK"
            }
        )
        await event_bus.publish(event)

    assert len(worker.tick_buffer) == 4

    # 5th tick triggers immediate threshold flush
    fifth_event = DomainEvent(
        event_type=EventType.TICK_RECEIVED,
        aggregate_id="USDJPY",
        payload={
            "symbol": "USDJPY",
            "bid": "155.15",
            "ask": "155.17",
            "spread": "0.02",
            "timestamp": now.isoformat(),
            "source": "MOCK"
        }
    )
    await event_bus.publish(fifth_event)
    assert len(worker.tick_buffer) == 0

    # Verify 5 ticks stored in repository
    stored_ticks = await tick_repo.get_ticks("USDJPY", start=now - timedelta(minutes=1), end=now + timedelta(minutes=1))
    assert len(stored_ticks) == 5

    # Test Bar Aggregated event
    bar_event = DomainEvent(
        event_type=EventType.BAR_AGGREGATED,
        aggregate_id="USDJPY",
        payload={
            "symbol": "USDJPY",
            "timeframe": "1m",
            "open": "155.10",
            "high": "155.20",
            "low": "155.05",
            "close": "155.15",
            "tick_volume": 42,
            "open_time": now.isoformat()
        }
    )
    await event_bus.publish(bar_event)

    await worker.stop()
    stored_bars = await bar_repo.get_bars("USDJPY", timeframe=BarTimeframe.M1)
    assert len(stored_bars) == 1
    assert stored_bars[0].tick_volume == 42


@pytest.mark.asyncio
async def test_historical_market_data_api_endpoints():
    from fastapi.testclient import TestClient
    from api.main import create_app

    client = ClickHouseClient(host="invalid_host", port=9999)
    await client.connect()
    tick_repo = ClickHouseTickRepository(client)
    bar_repo = ClickHouseBarRepository(client)

    now = datetime.now(timezone.utc)
    await tick_repo.save_tick(Tick(
        symbol="BTCUSD",
        bid=Decimal("95000.50"),
        ask=Decimal("95001.00"),
        spread=Decimal("0.50"),
        timestamp=now,
        source="TEST"
    ))

    await bar_repo.save_bar(Bar(
        symbol="BTCUSD",
        timeframe=BarTimeframe.M1,
        open=Decimal("94500.00"),
        high=Decimal("95500.00"),
        low=Decimal("94000.00"),
        close=Decimal("95000.00"),
        tick_volume=1200,
        open_time=now - timedelta(minutes=1),
        close_time=now
    ))

    container = {
        "historical_tick_repo": tick_repo,
        "historical_bar_repo": bar_repo,
    }

    app = create_app(container)
    test_client = TestClient(app)

    # Test tick history API
    resp_ticks = test_client.get("/api/v1/market-data/history/BTCUSD/ticks")
    assert resp_ticks.status_code == 200
    data_ticks = resp_ticks.json()
    assert data_ticks["symbol"] == "BTCUSD"
    assert data_ticks["count"] == 1
    assert Decimal(data_ticks["ticks"][0]["bid"]) == Decimal("95000.50")

    # Test bar history API
    resp_bars = test_client.get("/api/v1/market-data/history/BTCUSD/bars?timeframe=1m")
    assert resp_bars.status_code == 200
    data_bars = resp_bars.json()
    assert data_bars["symbol"] == "BTCUSD"
    assert data_bars["count"] == 1
    assert Decimal(data_bars["bars"][0]["high"]) == Decimal("95500.00")

