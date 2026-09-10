"""Account domain value objects (nested configuration structures)."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional
import uuid

from core.domains.common.value_objects import Money
from .enums import (
    MarginMode, ExecutionMode, TradeMode, FreeMarginMode,
    StopOutMode, CommissionType
)


@dataclass
class StopOutSnapshot:
    """Snapshot of account state when stop-out was triggered."""
    margin_level: Decimal
    equity: Money
    margin: Money
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class MarginProfile:
    """Margin and leverage configuration (from Group)."""
    mode: MarginMode = MarginMode.RETAIL
    margin_call_level: Decimal = field(default_factory=lambda: Decimal('0.8'))
    stop_out_level: Decimal = field(default_factory=lambda: Decimal('0.5'))
    stop_out_mode: StopOutMode = StopOutMode.PERCENT
    free_margin_mode: FreeMarginMode = FreeMarginMode.USE_PL
    leverage_default: int = 100
    leverage_max: int = 500
    margin_hedged: Decimal = field(default_factory=lambda: Decimal('0'))
    flags: int = 0


@dataclass
class CommissionRule:
    """Commission configuration."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    symbol_pattern: str = "*"
    type: CommissionType = CommissionType.DEAL
    value: Decimal = field(default_factory=lambda: Decimal('0'))
    currency: str = "USD"
    percent: Decimal = field(default_factory=lambda: Decimal('0'))
    min_value: Decimal = field(default_factory=lambda: Decimal('0'))
    max_value: Optional[Decimal] = None


@dataclass
class SwapConfiguration:
    """Swap configuration."""
    calculation_mode: str = "points"
    rollover_time: str = "22:00"
    triple_swap_day: str = "Wednesday"
    enable_swaps: bool = True
    swap_type: str = "POINTS"
    swap_long: Decimal = field(default_factory=lambda: Decimal('0'))
    swap_short: Decimal = field(default_factory=lambda: Decimal('0'))


@dataclass
class GroupSymbolOverride:
    """Per-symbol configuration override."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    symbol_pattern: str = ""
    trade_mode: Optional[TradeMode] = None
    execution_mode: Optional[ExecutionMode] = None
    volume_min: Optional[Decimal] = None
    volume_max: Optional[Decimal] = None
    volume_limit: Optional[Decimal] = None
    spread_diff: Optional[int] = None
    margin_rate_initial_buy: Optional[Decimal] = None
    margin_rate_initial_sell: Optional[Decimal] = None
    swap_long: Optional[Decimal] = None
    swap_short: Optional[Decimal] = None


@dataclass
class RoutingRule:
    """Order routing configuration."""
    default_mode: str = "b_book"
    a_book_threshold_lots: Optional[Decimal] = None
    lp_priority: List[str] = field(default_factory=list)


@dataclass
class GroupPermissions:
    """Permissions for a group."""
    allowed_symbols: List[str] = field(default_factory=lambda: ["*"])
    max_positions: int = 200
    max_orders: int = 100
    allow_hedging: bool = True
    allow_short_selling: bool = True
    allow_pending_orders: bool = True
    deposit_allowed: bool = True
    withdraw_allowed: bool = True
    trade_allowed: bool = True
    view_only: bool = False
    internal_only: bool = False
    negative_balance_protection: bool = True
@dataclass
class CommissionTier:
    """Volume-based commission tier."""
    volume_min: Decimal = field(default_factory=lambda: Decimal('0'))
    volume_max: Decimal = field(default_factory=lambda: Decimal('0'))
    rate: Decimal = field(default_factory=lambda: Decimal('0'))
