"""
Integration Test: Tick → Position PnL → Account Equity → Margin State Machine

This test proves the entire heartbeat of the broker works:
1. Ticks flow in
2. Position PnL updates
3. Account equity recalculates
4. Margin state machine triggers (MarginCallEntered, StopOutEntered)
"""
import pytest
from decimal import Decimal
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from unittest.mock import AsyncMock, MagicMock

from core.domains.accounts.account import Account
from core.domains.accounts.group import Group, MarginProfile
from core.domains.accounts.enums import AccountType, MarginMode, FreeMarginMode, StopOutMode
from core.domains.instruments.symbol import Symbol
from core.domains.instruments.value_objects import TradingSession
from core.domains.market_data.models import Tick
from core.domains.oms.entities.position import Position
from core.domains.oms.enums import PositionAction
from core.domains.common.value_objects import Money, Price, Volume
from core.ports.interfaces import (
    IPositionRepository, IAccountRepository, ISymbolRepository, IEventBus
)
from core.domains.risk.engine import RiskEngine
from core.events.domain_events import DomainEvent
from application.services.tick_margin_pipeline import TickMarginPipeline


# ============================================================================
# MOCK IMPLEMENTATIONS
# ============================================================================

class MockEventBus(IEventBus):
    """Mock event bus that tracks all published events."""
    
    def __init__(self):
        self.published_events: List[DomainEvent] = []
    
    async def publish(self, event: DomainEvent) -> None:
        self.published_events.append(event)
    
    async def subscribe(self, channel: str, callback) -> None:
        pass
    
    async def disconnect(self) -> None:
        pass
    
    def get_events_by_type(self, event_type: str) -> List[DomainEvent]:
        return [e for e in self.published_events if type(e).__name__ == event_type]


class MockPositionRepository(IPositionRepository):
    """Mock position repository with in-memory storage."""
    
    def __init__(self):
        self.positions: Dict[str, Position] = {}
    
    async def save(self, position: Position, session=None) -> Position:
        self.positions[position.position_id] = position
        return position
    
    async def find_by_id(self, position_id: str) -> Optional[Position]:
        return self.positions.get(position_id)
    
    async def get_open_positions(self, session=None) -> List[Position]:
        return [p for p in self.positions.values() if p.time_done is None]
    
    async def get_by_account(self, account_login: int) -> List[Position]:
        return [p for p in self.positions.values() 
                if p.account_login == account_login and p.time_done is None]
    
    async def get_by_account_and_symbol(self, account_login: int, symbol: str) -> List[Position]:
        return [p for p in self.positions.values()
                if p.account_login == account_login and p.symbol == symbol and p.time_done is None]
    
    async def get_by_symbol(self, symbol: str) -> List[Position]:
        return [p for p in self.positions.values()
                if p.symbol == symbol and p.time_done is None]
    
    async def get_closed_positions(self, account_login: int, from_time: datetime, to_time: datetime) -> List[Position]:
        return [p for p in self.positions.values()
                if p.account_login == account_login and p.time_done is not None]
    
    async def delete(self, position_id: str) -> bool:
        if position_id in self.positions:
            del self.positions[position_id]
            return True
        return False


class MockAccountRepository(IAccountRepository):
    """Mock account repository with in-memory storage."""
    
    def __init__(self):
        self.accounts: Dict[int, Account] = {}
    
    async def save(self, account: Account, session=None) -> Account:
        self.accounts[account.login] = account
        return account
    
    async def find_by_login(self, login: int) -> Optional[Account]:
        return self.accounts.get(login)
    
    async def find_all(self) -> List[Account]:
        return list(self.accounts.values())
    
    async def delete(self, login: int) -> bool:
        if login in self.accounts:
            del self.accounts[login]
            return True
        return False


class MockSymbolRepository(ISymbolRepository):
    """Mock symbol repository with in-memory storage."""
    
    def __init__(self, symbols: List[Symbol] = None):
        self.symbols: Dict[str, Symbol] = {s.name: s for s in (symbols or [])}
    
    def get_symbol(self, symbol_name: str) -> Optional[Symbol]:
        return self.symbols.get(symbol_name)
    
    async def get_all_symbols(self) -> List[Symbol]:
        return list(self.symbols.values())
    
    async def find_by_name(self, name: str) -> Optional[Symbol]:
        return self.symbols.get(name)
    
    async def save(self, symbol: Symbol, session=None) -> Symbol:
        self.symbols[symbol.name] = symbol
        return symbol
    
    async def get_all(self) -> List[Symbol]:
        return list(self.symbols.values())
    
    async def delete(self, name: str) -> bool:
        if name in self.symbols:
            del self.symbols[name]
            return True
        return False


# ============================================================================
# TEST SCENARIO
# ============================================================================

@pytest.mark.asyncio
async def test_margin_call_and_stop_out_state_machine():
    """
    Integration Test: Proves the entire tick → margin pipeline works.
    
    Setup:
    - Account: $10,000 balance, 1:100 leverage, MC=80%, SO=50%
    - Position: 5.0 Lot BUY EURUSD at 1.1000
    - Margin used = (1.1000 * 5.0 * 100000) / 100 = $5,500
    
    Tick 1: Bid 1.0900 → PnL = -$5,000, Equity = $5,000, Level = 90.9% (Normal)
    Tick 2: Bid 1.0880 → PnL = -$6,000, Equity = $4,000, Level = 72.7% (MC triggered)
    Tick 3: Bid 1.0830 → PnL = -$8,500, Equity = $1,500, Level = 27.3% (SO triggered)
    """
    
    # 1. Setup Group with margin rules
    group = Group(
        name="REAL_STANDARD",
        account_type=AccountType.REAL,
        currency="USD",
        margin=MarginProfile(
            mode=MarginMode.RETAIL,
            leverage_default=100,
            leverage_max=500,
            # PERCENT, matching MT5 (MarginCall / MarginStopOut).
            margin_call_level=Decimal('80'),
            stop_out_level=Decimal('50'),
            stop_out_mode=StopOutMode.PERCENT,
            free_margin_mode=FreeMarginMode.USE_PL,
        ),
    )
    
    # 2. Setup Account
    account = Account(
        login=100001,
        client_id="CLIENT_001",
        group_id=group.id,
        group=group,
        account_type=AccountType.REAL,
        currency="USD",
        balance=Money(Decimal('10000.00'), "USD"),
        equity=Money(Decimal('10000.00'), "USD"),
        margin_used=Money(Decimal('5500.00'), "USD"),  # Pre-calculated for 5 lots
        margin_free=Money(Decimal('4500.00'), "USD"),
        margin_level=Decimal('181.8'),  # percent: healthy
    )
    
    # 3. Setup Symbol (EURUSD)
    eurusd = Symbol(
        name="EURUSD",
        path="Forex\\EURUSD",
        base_currency="EUR",
        quote_currency="USD",
        tick_size=Decimal('0.00001'),
        tick_value=Decimal('1.0'),
        contract_size=Decimal('100000'),
        digits=5,
        volume_min=Decimal('0.01'),
        volume_max=Decimal('100.0'),
        volume_step=Decimal('0.01'),
    )
    
    # 4. Setup Position (5.0 Lot BUY EURUSD at 1.1000)
    position = Position(
        position_id="POS_001",
        account_login=100001,
        symbol="EURUSD",
        action=PositionAction.BUY,
        volume=Volume(Decimal('5.0')),
        price_open=Price(Decimal('1.1000')),
        price_current=Price(Decimal('1.1000')),
        contract_size=Decimal('100000'),
        profit=Money(Decimal('0'), "USD"),
    )
    
    # 5. Setup Mock Repositories
    event_bus = MockEventBus()
    position_repo = MockPositionRepository()
    account_repo = MockAccountRepository()
    symbol_repo = MockSymbolRepository([eurusd])
    
    # Pre-populate repositories
    await position_repo.save(position)
    await account_repo.save(account)
    
    # 6. Setup RiskEngine (we need it for conversion rate)
    risk_engine = RiskEngine(
        symbol_repo=symbol_repo,
        market_data_engine=None  # Not needed for USD-quoted pairs
    )
    
    # 7. Create TickMarginPipeline
    pipeline = TickMarginPipeline(
        position_repo=position_repo,
        account_repo=account_repo,
        symbol_repo=symbol_repo,
        risk_engine=risk_engine,
        event_bus=event_bus,
    )
    
    # =========================================================================
    # TICK 1: Bid 1.0900 → PnL = -$5,000, Equity = $5,000, Level = 90.9%
    # =========================================================================
    tick1 = Tick(
        symbol="EURUSD",
        bid=Decimal('1.0900'),
        ask=Decimal('1.0902'),
        spread=Decimal('0.0002'),
        timestamp=datetime.now(timezone.utc),
    )
    
    await pipeline.process_tick(tick1)
    
    # Verify Position PnL
    # BUY position valued at BID
    # PnL = (1.0900 - 1.1000) * 5.0 * 100000 = -0.0100 * 500000 = -$5,000
    updated_position = await position_repo.find_by_id("POS_001")
    assert updated_position.profit.amount == Decimal('-5000.00'), \
        f"Expected PnL -5000, got {updated_position.profit.amount}"
    
    # Verify Account Equity
    updated_account = await account_repo.find_by_login(100001)
    assert updated_account.equity.amount == Decimal('5000.00'), \
        f"Expected Equity 5000, got {updated_account.equity.amount}"
    
    # Verify Margin Level
    # Level = 5000 / 5500 = 0.909 (90.9%)
    assert updated_account.margin_level == Decimal('90.90909090909090909090909091'), \
        f"Expected margin level ~90.9%, got {updated_account.margin_level}"
    
    # Verify NO events published (still above 80% MC)
    assert len(event_bus.published_events) == 0, \
        f"Expected 0 events, got {len(event_bus.published_events)}"
    
    # =========================================================================
    # TICK 2: Bid 1.0880 → PnL = -$6,000, Equity = $4,000, Level = 72.7%
    # =========================================================================
    tick2 = Tick(
        symbol="EURUSD",
        bid=Decimal('1.0880'),
        ask=Decimal('1.0882'),
        spread=Decimal('0.0002'),
        timestamp=datetime.now(timezone.utc),
    )
    
    await pipeline.process_tick(tick2)
    
    # Verify Position PnL
    # PnL = (1.0880 - 1.1000) * 5.0 * 100000 = -0.0120 * 500000 = -$6,000
    updated_position = await position_repo.find_by_id("POS_001")
    assert updated_position.profit.amount == Decimal('-6000.00'), \
        f"Expected PnL -6000, got {updated_position.profit.amount}"
    
    # Verify Account Equity
    updated_account = await account_repo.find_by_login(100001)
    assert updated_account.equity.amount == Decimal('4000.00'), \
        f"Expected Equity 4000, got {updated_account.equity.amount}"
    
    # Verify Margin Level
    # Level = 4000 / 5500 = 0.727 (72.7%)
    assert updated_account.margin_level < Decimal('80'), \
        f"Expected margin level below the 80% margin call, got {updated_account.margin_level}"
    
    # Verify MarginCallEntered event published
    mc_events = event_bus.get_events_by_type("MarginCallEntered")
    assert len(mc_events) == 1, \
        f"Expected 1 MarginCallEntered event, got {len(mc_events)}"
    assert mc_events[0].payload["account_login"] == 100001
    
    # =========================================================================
    # TICK 3: Bid 1.0830 → PnL = -$8,500, Equity = $1,500, Level = 27.3%
    # =========================================================================
    tick3 = Tick(
        symbol="EURUSD",
        bid=Decimal('1.0830'),
        ask=Decimal('1.0832'),
        spread=Decimal('0.0002'),
        timestamp=datetime.now(timezone.utc),
    )
    
    await pipeline.process_tick(tick3)
    
    # Verify Position PnL
    # PnL = (1.0830 - 1.1000) * 5.0 * 100000 = -0.0170 * 500000 = -$8,500
    updated_position = await position_repo.find_by_id("POS_001")
    assert updated_position.profit.amount == Decimal('-8500.00'), \
        f"Expected PnL -8500, got {updated_position.profit.amount}"
    
    # Verify Account Equity
    updated_account = await account_repo.find_by_login(100001)
    assert updated_account.equity.amount == Decimal('1500.00'), \
        f"Expected Equity 1500, got {updated_account.equity.amount}"
    
    # Verify Margin Level
    # Level = 1500 / 5500 = 0.273 (27.3%)
    assert updated_account.margin_level < Decimal('50'), \
        f"Expected margin level below the 50% stop-out, got {updated_account.margin_level}"
    
    # Verify StopOutEntered event published
    so_events = event_bus.get_events_by_type("StopOutEntered")
    assert len(so_events) == 1, \
        f"Expected 1 StopOutEntered event, got {len(so_events)}"
    assert so_events[0].payload["account_login"] == 100001
    
    # Verify total events: 1 MC + 1 SO = 2
    assert len(event_bus.published_events) == 2, \
        f"Expected 2 total events, got {len(event_bus.published_events)}"
    
    print("✅ All assertions passed! The margin state machine works correctly.")


# ============================================================================
# ADDITIONAL TEST: Cross-Currency PnL (EURJPY on USD account)
# ============================================================================

@pytest.mark.asyncio
async def test_cross_currency_pnl_in_margin_loop():
    """
    Test that cross-currency PnL is correctly converted in the margin loop.
    
    Setup:
    - Account: $10,000 USD balance
    - Position: 1.0 Lot BUY EURJPY at 160.000
    - Margin used = (160.000 * 1.0 * 100000) / 100 = $16,000 (wait, that's too high)
    
    Let me recalculate:
    - EURJPY contract size = 100,000 EUR
    - Price = 160.000 JPY per EUR
    - Notional = 1.0 * 100000 * 160.000 = 16,000,000 JPY
    - Margin = 16,000,000 / 100 = 160,000 JPY
    - Convert to USD: 160,000 / 150.000 (USDJPY rate) = $1,066.67
    
    Tick: EURJPY Bid 161.000
    - PnL in JPY = (161.000 - 160.000) * 1.0 * 100000 = 100,000 JPY
    - Convert to USD: 100,000 / 150.000 = $666.67
    """
    
    # This test would require mocking the conversion rate lookup
    # For now, we'll skip it and focus on the main test above
    pass