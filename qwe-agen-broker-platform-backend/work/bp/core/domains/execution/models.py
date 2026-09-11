"""
Core Execution Domain Models.

This module defines the entities for Smart Order Routing (SOR),
Dealer Workflow, and Coverage Accounts (Risk Accounts).

Architectural Purpose:
Encapsulates the logic for WHERE an order should be executed (A-Book vs B-Book)
and HOW manual dealer interventions are handled.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional
import fnmatch


class ExecutionDestination(Enum):
    """
    Target destination for order execution.
    Mirrors MT5 Execution Modes and Centroid Taker Execution Models.
    """
    A_BOOK = "A_BOOK"             # Route to external LP via gateway
    B_BOOK = "B_BOOK"             # Internalize — broker is counterparty
    IN_HOUSE_ECN = "IN_HOUSE_ECN" # Match client vs client internally (CLOB)
    TO_DEALER = "TO_DEALER"       # Manual dealer confirmation required
    REJECT = "REJECT"             # Block the order immediately


@dataclass
class RoutingRule:
    """
    Mirrors MT5 IMTConRoute. Evaluated in priority order (highest first).
    First matching rule wins.

    Attributes:
        rule_id: Unique identifier for the rule.
        priority: Higher value = evaluated first.
        group_filter: Group name or None (match all groups). Supports wildcards like 'real_*'.
        symbol_filter: Symbol name or None (match all symbols). Supports wildcards like 'EUR*'.
        volume_min: Minimum volume to trigger this rule.
        volume_max: Maximum volume to trigger this rule.
        destination: Where to send the order if matched.
        gateway_id: Specific LP gateway ID (required for A_BOOK).
        coverage_account_id: Which CoverageAccount to use for B-Book hedging (optional).
        is_enabled: Active status of the rule.
    """
    rule_id: str
    priority: int
    destination: ExecutionDestination

    # Filters (None = match all)
    group_filter: Optional[str] = None
    symbol_filter: Optional[str] = None
    volume_min: Optional[Decimal] = None
    volume_max: Optional[Decimal] = None

    # Action details
    gateway_id: Optional[str] = None
    coverage_account_id: Optional[str] = None  # For B-Book: which coverage account to update
    is_enabled: bool = True


@dataclass
class CoverageAccount:
    """
    Mirrors Centroid 'Risk Account'. Tracks broker's net exposure
    from B-Book trades. Used for hedging decisions.

    Attributes:
        account_id: Unique internal ID for the coverage account.
        name: Human-readable name (e.g., "EURUSD_Hedge_Account").
        currency: Account currency.
        net_exposure: {symbol: net_volume}.
            Positive = broker is long (clients are net short).
            Negative = broker is short (clients are net long).
        margin_level: Current margin level percentage.
        trading_state: NEUTRAL, MARGIN_CALL, STOPPED_OUT.
    """
    account_id: str
    name: str
    currency: str

    # Net exposure per symbol: {symbol: net_volume}
    net_exposure: Dict[str, Decimal] = field(default_factory=dict)
    nop_limit: Decimal = Decimal('100.0')  # Max Net Open Position limit per symbol

    margin_level: Decimal = Decimal('0')
    trading_state: str = "NEUTRAL"  # NEUTRAL, MARGIN_CALL, STOPPED_OUT

    def update_exposure(self, symbol: str, volume_delta: Decimal):
        """
        Updates net exposure for a symbol.

        SIGN CONVENTION (CRITICAL):
        - volume_delta > 0: Client SOLD → Broker BOUGHT → Broker is LONG → exposure INCREASES (positive)
        - volume_delta < 0: Client BOUGHT → Broker SOLD → Broker is SHORT → exposure DECREASES (negative)

        This matches the class docstring: Positive = broker is long (clients are net short).
        """
        current = self.net_exposure.get(symbol, Decimal('0'))
        self.net_exposure[symbol] = current + volume_delta

    def get_exposure_ratio(self, symbol: str, additional_volume: Decimal = Decimal('0')) -> Decimal:
        """
        Returns the net exposure ratio relative to nop_limit (0.0 to 1.0+).
        Used for NOP threshold alerts (70%), auto-hedging (85%), and blocking (95%).
        """
        if self.nop_limit <= Decimal('0'):
            return Decimal('0')
        current_abs = abs(self.net_exposure.get(symbol, Decimal('0'))) + abs(additional_volume)
        return current_abs / self.nop_limit

    def get_total_exposure(self) -> Decimal:
        """Returns absolute total exposure across all symbols."""
        return sum(abs(v) for v in self.net_exposure.values())



@dataclass
class ExecutionInstruction:
    """
    The result of the Smart Order Router.
    Tells the Execution Orchestrator exactly what to do.
    """
    destination: ExecutionDestination
    rule_id: str
    gateway_id: Optional[str] = None
    coverage_account_id: Optional[str] = None  # Which CoverageAccount to use for B-Book
    reason: Optional[str] = None
    #: M8: non-terminal MT5 routing effects that travel with the instruction:
    #: ACTION_DELAY_TIME milliseconds the orchestrator must wait before
    #: executing, and ACTION_DELAY_TICK (modelled; not executable inline -
    #: the orchestrator says so loudly rather than silently skipping).
    delay_ms: int = 0
    delay_ticks: int = 0
    mt5_rule: Optional[str] = None


@dataclass
class DealerDecision:
    """
    Represents a dealer's manual intervention decision.
    Mirrors MT5 DealerAnswer.
    """
    dealer_id: str
    order_ticket: str
    action: str  # CONFIRM, REJECT, REQUOTE
    requote_price: Optional[Decimal] = None
    reason: Optional[str] = None
    decided_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
