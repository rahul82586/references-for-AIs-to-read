"""
Integration Test: Liquidation Worker

Proves that when an account enters stop-out state, the Liquidation Worker:
1. Receives the StopOutEntered event
2. Calculates which positions to close (worst loss first)
3. Executes the closure (creates Orders, Deals, updates Positions)
4. Recovers the account's margin level above stop_out_level
"""
import pytest
from decimal import Decimal
from datetime import datetime, timezone
from typing import List, Dict, Optional
from unittest.mock import AsyncMock

from core.domains.accounts.account import Account
from core.domains.accounts.group import Group, MarginProfile
from core.domains.accounts.enums import AccountType, MarginMode, FreeMarginMode, StopOutMode, SOActivation
from core.domains.common.value_objects import Money, Price, Volume
from core.domains.instruments.symbol import Symbol
from core.domains.market_data.models import Tick
from core.domains.oms.entities.position import Position
from core.domains.oms.enums import PositionAction
from core.domains.risk.liquidation_service import LiquidationService
from core.events.domain_events import StopOutEntered, PositionClosed
from application.workers.liquidation_worker import LiquidationWorker


# Mock repositories (reuse from test_margin_loop.py)
class MockAccountRepository:
    def __init__(self):
        self.accounts: Dict[int, Account] = {}
    
    async def save(self, account: Account, session=None) -> Account:
        self.accounts[account.login] = account
        return account
    
    async def find_by_login(self, login: int) -> Optional[Account]:
        return self.accounts.get(login)


class MockPositionRepository:
    def __init__(self):
        self.positions: Dict[str, Position] = {}
    
    async def save(self, position: Position, session=None) -> Position:
        self.positions[position.position_id] = position
        return position
    
    async def find_by_id(self, position_id: str) -> Optional[Position]:
        return self.positions.get(position_id)
    
    async def get_by_account(self, account_login: int) -> List[Position]:
        return [p for p in self.positions.values()
                if p.account_login == account_login and p.time_done is None]


class MockOrderRepository:
    def __init__(self):
        self.orders = []
    
    async def save(self, order, session=None):
        self.orders.append(order)
        return order


class MockDealRepository:
    def __init__(self):
        self.deals = []
    
    async def save(self, deal, session=None):
        self.deals.append(deal)
        return deal


class MockSymbolRepository:
    def __init__(self, symbols: List[Symbol] = None):
        self.symbols: Dict[str, Symbol] = {s.name: s for s in (symbols or [])}
    
    async def find_by_name(self, name: str) -> Optional[Symbol]:
        return self.symbols.get(name)


class MockMarketDataFeed:
    def __init__(self, ticks: Dict[str, Tick] = None):
        self.ticks = ticks or {}
    
    async def get_latest_tick(self, symbol: str) -> Optional[Tick]:
        return self.ticks.get(symbol)


class MockEventBus:
    def __init__(self):
        self.published_events = []
        self.subscriptions = {}
    
    async def publish(self, event):
        self.published_events.append(event)
    
    def subscribe(self, event_type, handler):
        self.subscriptions[event_type] = handler
    
    def unsubscribe(self, event_type, handler):
        if event_type in self.subscriptions:
            del self.subscriptions[event_type]


@pytest.mark.asyncio
async def test_liquidation_worker_closes_worst_loss_first():
    """
    LiquidationWorker closes the worst-loss position first, then stops once the
    account recovers above stop-out.

    Setup (all levels are PERCENT, the MT5 convention):
    - Account: balance $10,200, 1:100 leverage, margin call 80%, stop-out 60%
    - Position 1: 1.0 lot BUY EURUSD, margin $1,100, floating loss -$4,000
    - Position 2: 1.0 lot BUY GBPUSD, margin $1,100, floating loss -$5,000  <- worst

    LiquidationService computes equity as balance + floating PnL, so:
        equity = 10,200 - 9,000 = $1,200
        margin = $2,200
        level  = 1,200 / 2,200 = 54.55%   -> below the 60% stop-out, liquidate

    Closing a position REALISES its loss, so equity does not change; what changes is
    the margin requirement. Closing Position 2 frees $1,100:
        level  = 1,200 / 1,100 = 109.09%  -> above 60%, recovered, stop closing

    Expected: Position 2 closed, Position 1 still open, one closing order, one deal
    with reason SO, one PositionClosed event, account back to SOActivation.NONE.
    """
    
    # Setup Group
    group = Group(
        name="REAL_STANDARD",
        account_type=AccountType.REAL,
        currency="USD",
        margin=MarginProfile(
            mode=MarginMode.RETAIL,
            leverage_default=100,
            leverage_max=500,
            # PERCENT, the MT5 convention. The fixture account sits at 54.55%,
            # so stop-out has to be above that for the worker to act at all, and
            # below the 109.09% it recovers to once the worst position is closed,
            # or the worker would liquidate both positions.
            margin_call_level=Decimal('80'),
            stop_out_level=Decimal('60'),
            stop_out_mode=StopOutMode.PERCENT,
            free_margin_mode=FreeMarginMode.USE_PL,
        ),
    )
    
    # Setup Account
    account = Account(
        login=100001,
        client_id="CLIENT_001",
        group_id=group.id,
        group=group,
        account_type=AccountType.REAL,
        currency="USD",
        # balance + floating PnL must equal equity, because LiquidationService
        # recomputes equity that way: 10,200 + (-9,000) = 1,200.
        balance=Money(Decimal('10200.00'), "USD"),
        equity=Money(Decimal('1200.00'), "USD"),
        margin_used=Money(Decimal('2200.00'), "USD"),  # $1,100 per position
        margin_free=Money(Decimal('-1000.00'), "USD"),
        margin_level=Decimal('54.55'),  # percent: below the 60% stop-out
        so_activation=SOActivation.STOP_OUT,  # In stop-out state
    )
    
    # Setup Symbols
    eurusd = Symbol(
        name="EURUSD",
        base_currency="EUR",
        quote_currency="USD",
        contract_size=Decimal('100000'),
        digits=5,
    )
    
    gbpusd = Symbol(
        name="GBPUSD",
        base_currency="GBP",
        quote_currency="USD",
        contract_size=Decimal('100000'),
        digits=5,
    )
    
    # Setup Positions
    position1 = Position(
        position_id="POS_001",
        account_login=100001,
        symbol="EURUSD",
        action=PositionAction.BUY,
        volume=Volume(Decimal('1.0')),
        price_open=Price(Decimal('1.1000')),
        price_current=Price(Decimal('1.0600')),
        contract_size=Decimal('100000'),
        profit=Money(Decimal('-4000.00'), "USD"),  # Loss
    )
    
    position2 = Position(
        position_id="POS_002",
        account_login=100001,
        symbol="GBPUSD",
        action=PositionAction.BUY,
        volume=Volume(Decimal('1.0')),
        price_open=Price(Decimal('1.3000')),
        price_current=Price(Decimal('1.2500')),
        contract_size=Decimal('100000'),
        profit=Money(Decimal('-5000.00'), "USD"),  # Worst loss
    )
    
    # Setup Mock Repositories
    account_repo = MockAccountRepository()
    position_repo = MockPositionRepository()
    order_repo = MockOrderRepository()
    deal_repo = MockDealRepository()
    symbol_repo = MockSymbolRepository([eurusd, gbpusd])
    
    # Setup current prices
    tick_eurusd = Tick(
        symbol="EURUSD",
        bid=Decimal('1.0600'),
        ask=Decimal('1.0602'),
        spread=Decimal('0.0002'),
        timestamp=datetime.now(timezone.utc),
    )
    
    tick_gbpusd = Tick(
        symbol="GBPUSD",
        bid=Decimal('1.2500'),
        ask=Decimal('1.2502'),
        spread=Decimal('0.0002'),
        timestamp=datetime.now(timezone.utc),
    )
    
    market_data_feed = MockMarketDataFeed({
        "EURUSD": tick_eurusd,
        "GBPUSD": tick_gbpusd,
    })
    
    event_bus = MockEventBus()
    
    # Pre-populate repositories
    await account_repo.save(account)
    await position_repo.save(position1)
    await position_repo.save(position2)
    
    # Setup Liquidation Service and Worker
    liquidation_service = LiquidationService()
    
    worker = LiquidationWorker(
        account_repo=account_repo,
        position_repo=position_repo,
        order_repo=order_repo,
        deal_repo=deal_repo,
        symbol_repo=symbol_repo,
        market_data_feed=market_data_feed,
        event_bus=event_bus,
        liquidation_service=liquidation_service,
    )
    
    # Start worker
    await worker.start()
    
    # Simulate StopOutEntered event
    stop_out_event = StopOutEntered(
        aggregate_id="100001",
        payload={
            "account_login": 100001,
            "margin_level": "54.55",
            "equity": "1200.00",
            "margin": "2200.00",
        },
    )
    
    # Trigger the event handler
    await worker._on_stop_out_entered(stop_out_event)
    
    # =========================================================================
    # ASSERTIONS
    # =========================================================================
    
    # 1. Verify Position 2 (worst loss) was closed
    closed_position2 = await position_repo.find_by_id("POS_002")
    assert closed_position2 is not None
    assert closed_position2.volume.value == Decimal('0'), "Position 2 should be closed"
    assert closed_position2.time_done is not None, "Position 2 should have time_done set"
    assert closed_position2.deal_close is not None, "Position 2 should have deal_close set"
    
    # 2. Verify Position 1 (smaller loss) is still open
    open_position1 = await position_repo.find_by_id("POS_001")
    assert open_position1 is not None
    assert open_position1.volume.value == Decimal('1.0'), "Position 1 should still be open"
    assert open_position1.time_done is None, "Position 1 should not have time_done"
    
    # 3. Verify closing Order was created for Position 2
    assert len(order_repo.orders) == 1, "Should have created 1 closing order"
    closing_order = order_repo.orders[0]
    assert closing_order.symbol == "GBPUSD"
    assert closing_order.order_type.value == "SELL"  # Opposite of BUY
    assert closing_order.volume_initial.value == Decimal('1.0')
    assert closing_order.state.value == "FILLED"
    
    # 4. Verify closing Deal was created
    assert len(deal_repo.deals) == 1, "Should have created 1 closing deal"
    closing_deal = deal_repo.deals[0]
    assert closing_deal.symbol == "GBPUSD"
    assert closing_deal.deal_type.value == "SELL"
    assert closing_deal.entry.value == "OUT"
    assert closing_deal.reason.value == "SO"  # Stop-out
    assert closing_deal.volume.value == Decimal('1.0')
    
    # 5. Verify PositionClosed event was emitted
    position_closed_events = [e for e in event_bus.published_events if isinstance(e, PositionClosed)]
    assert len(position_closed_events) == 1, "Should have emitted 1 PositionClosed event"
    assert position_closed_events[0].payload["position_id"] == "POS_002"
    assert position_closed_events[0].payload["reason"] == "LIQUIDATION"
    
    # 6. Verify Account recovered from stop-out
    updated_account = await account_repo.find_by_login(100001)
    assert updated_account is not None
    assert updated_account.so_activation == SOActivation.NONE, "Account should recover from stop-out"
    assert updated_account.margin_level > Decimal('60'), \
        "Margin level should have recovered above the 60% stop-out"
    
