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
    # PERCENT, matching MT5 (live export: MarginCall "50.00", MarginStopOut "30.00").
    # These were 0.8 / 0.5 fractions, which made every comparison against a
    # percent-scale margin level silently wrong in one direction or the other.
    margin_call_level: Decimal = field(default_factory=lambda: Decimal('80'))
    stop_out_level: Decimal = field(default_factory=lambda: Decimal('50'))
    stop_out_mode: StopOutMode = StopOutMode.PERCENT
    free_margin_mode: FreeMarginMode = FreeMarginMode.USE_PL
    leverage_default: int = 100
    leverage_max: int = 500
    margin_hedged: Decimal = field(default_factory=lambda: Decimal('0'))
    flags: int = 0


@dataclass
class CommissionRule:
    """One MT5 commission entry (ConfigGroupCommission).

    A group may hold several of these with different Path masks, and a deal can match
    more than one - MT5 stacks them, so Group.calculate_commission sums every match
    rather than returning the first.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    #: MT5 Path - the symbol mask, e.g. "FX\\*".
    symbol_pattern: str = "*"
    type: CommissionType = CommissionType.DEAL
    #: MT5 Value on a rule with no tiers.
    value: Decimal = field(default_factory=lambda: Decimal('0'))
    currency: str = "USD"
    percent: Decimal = field(default_factory=lambda: Decimal('0'))
    min_value: Decimal = field(default_factory=lambda: Decimal('0'))
    max_value: Optional[Decimal] = None
    #: MT5 Tiers - volume-banded rates. When present these take precedence over `value`.
    tiers: List["CommissionTier"] = field(default_factory=list)
    #: MT5 ChargeMode / EntryMode / ActionMode / ProfitMode / ReasonMode. Modelled as
    #: ints because their meanings are SDK enum values we have not mapped yet; keeping
    #: them means an imported commission can be re-exported unchanged.
    charge_mode: int = 0
    entry_mode: int = 0
    action_mode: int = 0
    profit_mode: int = 0
    reason_mode: int = 127


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
    """One volume band of an MT5 commission (MT5 ConfigGroupCommissionTier).

    MT5 fields: Mode, Type, Value, Minimal, Maximal, RangeFrom, RangeTo, Currency.
    ``RangeFrom``/``RangeTo`` band the tier by volume; ``Value`` is the rate;
    ``Minimal``/``Maximal`` cap the result. The live export's Forex commission is
    Value 3.5 over RangeFrom 0 / RangeTo 1000.
    """

    #: MT5 RangeFrom / RangeTo - the volume band this tier applies to.
    volume_min: Decimal = field(default_factory=lambda: Decimal('0'))
    volume_max: Decimal = field(default_factory=lambda: Decimal('0'))
    #: MT5 Value - the rate. Money per lot, pips, or percent, per CommissionType.
    rate: Decimal = field(default_factory=lambda: Decimal('0'))
    #: MT5 Minimal / Maximal - caps applied to this tier's result.
    min_value: Decimal = field(default_factory=lambda: Decimal('0'))
    max_value: Optional[Decimal] = None
    #: MT5 Type on the tier, and Currency for a money-denominated rate.
    tier_type: int = 0
    currency: str = ""

    def applies_to(self, volume: Decimal) -> bool:
        """Whether a volume falls in this band. An unbounded max matches everything."""
        if volume < self.volume_min:
            return False
        if self.volume_max and self.volume_max > 0:
            return volume <= self.volume_max
        return True
