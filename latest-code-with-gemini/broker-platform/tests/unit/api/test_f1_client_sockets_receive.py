"""F1: the client-plane sockets must actually receive what they promise.

/ws/stream (public ticks) and /ws/user (private trade updates) accepted
connections, registered them, and then NEVER sent a frame: the
WebSocketEventBridge broadcast exclusively to the manager subscription
manager. A Market Watch page wired to /ws/stream showed a connected socket
and no prices - the exact shape of D6 and M5 defect 9 (healthy-looking
connection, silent absence of data).

These tests drive the bridge's handlers directly with a recording stand-in
for the ConnectionManager singleton, and pin:

* a tick reaches BOTH audiences (manager subscriptions and the public socket)
* trading events reach the account's PRIVATE socket, keyed by login
* an event with no login is delivered to NOBODY private - never broadcast to
  every connected user (that would be a leak, not a feature)
* the risk events (margin call / stop-out) the bridge never even subscribed
  to are subscribed AND delivered
* start() registers the two risk event types on the bus
"""
from __future__ import annotations

import pytest

import api.websockets.event_bridge as eb
from core.events.domain_events import (
    DealCreated,
    EventType,
    MarginCallEntered,
    OrderCreated,
    StopOutEntered,
    TickReceived,
)


class _Recorder:
    def __init__(self):
        self.ticks = []
        self.user_updates = []

    async def broadcast_tick(self, symbol, bid, ask, spread=None):
        self.ticks.append((symbol, bid, ask, spread))

    async def send_user_update(self, user_id, event_type, payload):
        self.user_updates.append((user_id, event_type, payload))


class _SubRecorder:
    def __init__(self):
        self.broadcasts = []

    async def broadcast(self, kind, payload):
        self.broadcasts.append((kind, payload))


class _BusRecorder:
    def __init__(self):
        self.subscribed = []

    def subscribe(self, event_type, handler):
        self.subscribed.append(event_type)


@pytest.fixture()
def bridge(monkeypatch):
    rec = _Recorder()
    subs = _SubRecorder()
    monkeypatch.setattr(eb, "client_sockets", rec)
    b = eb.WebSocketEventBridge(event_bus=_BusRecorder())
    b.subscription_manager = subs
    return b, rec, subs


@pytest.mark.asyncio
async def test_a_tick_reaches_both_audiences(bridge):
    b, rec, subs = bridge
    await b._on_tick_received(TickReceived(payload={
        "symbol": "EURUSD", "bid": "1.10200", "ask": "1.10210", "spread": "1.0",
    }))
    assert rec.ticks == [("EURUSD", "1.10200", "1.10210", "1.0")]   # the public socket
    assert subs.broadcasts and subs.broadcasts[0][0] == "ticks"      # and the manager plane


@pytest.mark.asyncio
async def test_a_tick_without_prices_does_not_reach_the_public_socket(bridge):
    b, rec, _ = bridge
    await b._on_tick_received(TickReceived(payload={"symbol": "EURUSD"}))
    assert rec.ticks == []          # never invent a frame from a half payload


@pytest.mark.asyncio
async def test_trading_events_reach_the_accounts_private_socket(bridge):
    b, rec, _ = bridge
    await b._on_order_created(OrderCreated(payload={"account_login": 886152, "symbol": "EURUSD"}))
    await b._on_deal_created(DealCreated(payload={"account_login": 886152, "deal_id": "d-1"}))
    assert [("886152", "order_created"), ("886152", "deal_created")] == [
        (u, t) for u, t, _ in rec.user_updates
    ]


@pytest.mark.asyncio
async def test_an_event_with_no_login_is_delivered_to_nobody_private(bridge):
    """No login -> no delivery. Broadcasting one account's trade event to
    every connected socket would be a leak, not a feature."""
    b, rec, subs = bridge
    await b._on_order_created(OrderCreated(payload={"symbol": "EURUSD"}))
    assert rec.user_updates == []
    assert subs.broadcasts, "the manager plane still receives it"


@pytest.mark.asyncio
async def test_risk_events_reach_the_private_socket(bridge):
    b, rec, _ = bridge
    await b._on_margin_call_triggered(MarginCallEntered(payload={"account_login": 900003}))
    await b._on_stop_out_initiated(StopOutEntered(payload={"login": 900003}))
    kinds = [t for _, t, _ in rec.user_updates]
    assert kinds == ["margin_call", "stop_out"]


@pytest.mark.asyncio
async def test_start_subscribes_the_risk_event_types(bridge):
    b, _, _ = bridge
    bus = _BusRecorder()
    b.event_bus = bus
    await b.start()
    assert EventType.MARGIN_CALL_TRIGGERED in bus.subscribed
    assert EventType.STOP_OUT_INITIATED in bus.subscribed
    assert EventType.TICK_RECEIVED in bus.subscribed
