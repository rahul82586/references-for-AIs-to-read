"""
Domain Events - The Nervous System of the Platform

These immutable events are the only way different bounded contexts communicate,
preventing tight coupling and enabling independent evolution of services.
"""
import logging
import uuid
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)
from datetime import datetime, timezone
from typing import Any, Optional
from enum import Enum


class EventType(Enum):
    """Enumeration of all possible domain events."""
    # OMS Events
    ORDER_CREATED = "order.created"
    ORDER_MODIFIED = "order.modified"
    ORDER_CANCELLED = "order.cancelled"
    ORDER_REJECTED = "order.rejected"
    ORDER_APPROVED = "order.approved"  # Added for Phase 4

    DEAL_CREATED = "deal.created"
    DEAL_MODIFIED = "deal.modified"  # For MT5-style trade corrections
    TRADE_MODIFIED = "trade.modified"  # MT5 reversal + correction pair

    POSITION_OPENED = "position.opened"
    POSITION_CLOSED = "position.closed"
    POSITION_UPDATED = "position.updated"

    # Market Data Events
    TICK_RECEIVED = "market.tick_received"
    BOOK_UPDATED = "market.book_updated"
    BAR_AGGREGATED = "market.bar_aggregated"

    # System/Risk Events
    MARGIN_CALL = "risk.margin_call"
    STOP_OUT = "risk.stop_out"
    NODE_HEARTBEAT = "system.node_heartbeat"

    # Risk Events (Phase 6)
    MARGIN_CALL_TRIGGERED = "risk.margin_call_triggered"
    MARGIN_CALL_EXITED = "risk.margin_call_exited"
    STOP_OUT_INITIATED = "risk.stop_out_initiated"
    STOP_OUT_EXITED = "risk.stop_out_exited"
    POSITION_FORCE_CLOSED = "risk.position_force_closed"
    RISK_STATUS_UPDATED = "risk.status_updated"

    # Execution Events (Phase 5)
    ORDER_ROUTED = "execution.order_routed"
    ORDER_QUEUED_FOR_DEALER = "execution.order_queued_for_dealer"
    ORDER_DEALER_CONFIRMED = "execution.order_dealer_confirmed"
    ORDER_DEALER_REJECTED = "execution.order_dealer_rejected"
    ORDER_REQUOTED = "execution.order_requoted"
    COVERAGE_EXPOSURE_UPDATED = "execution.coverage_exposure_updated"

    # Ledger Events (Phase 7)
    COMMISSION_CHARGED = "ledger.commission_charged"
    SWAP_APPLIED = "ledger.swap_applied"
    BALANCE_DEPOSITED = "ledger.balance_deposited"
    BALANCE_WITHDRAWN = "ledger.balance_withdrawn"
    BALANCE_CORRECTED = "ledger.balance_corrected"

    # Configuration plane events (drive ConfigCache invalidation)
    GROUP_CREATED = "config.group_created"
    GROUP_UPDATED = "config.group_updated"
    GROUP_DELETED = "config.group_deleted"
    SYMBOL_CREATED = "config.symbol_created"
    SYMBOL_UPDATED = "config.symbol_updated"
    SYMBOL_DELETED = "config.symbol_deleted"
    HOLIDAY_CREATED = "config.holiday_created"
    HOLIDAY_UPDATED = "config.holiday_updated"
    HOLIDAY_DELETED = "config.holiday_deleted"


@dataclass(frozen=True)
class DomainEvent:
    """
    Base class for all domain events.

    Architectural Purpose:
    Acts as the standard envelope for communication between bounded contexts.
    Being frozen ensures immutability once created, guaranteeing event integrity
    as it travels through the Event Bus.
    """
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    aggregate_id: Optional[str] = None  # The ID of the main entity (e.g., OrderID, AccountID)
    payload: dict[str, Any] = field(default_factory=dict)
    event_type: EventType = EventType.ORDER_CREATED

    def to_dict(self) -> dict[str, Any]:
        """Serialize event for transport (e.g., JSON for Redis)."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "aggregate_id": self.aggregate_id,
            "event_type": self.event_type.value,
            "payload": self.payload
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DomainEvent":
        """Rehydrate what to_dict() produced.

        D5: without this, RedisEventBus had to hand subscribers the raw JSON dict
        while InProcessEventBus handed them a DomainEvent - so the same handler
        received a different type depending on which bus the server was configured
        with, and every consumer needed an isinstance branch to work on both.

        Unknown event_type values and unparseable timestamps are tolerated rather
        than raised: an event from a newer publisher, or one with a field this
        process does not know, must still be delivered. Losing the message because
        its envelope was unfamiliar is a worse failure than delivering it with a
        best-effort type.
        """
        raw_type = data.get("event_type")
        try:
            event_type = EventType(raw_type) if raw_type is not None else cls.event_type
        except ValueError:
            logger.warning("unknown event_type %r on the wire; keeping the raw value", raw_type)
            event_type = cls.event_type

        raw_ts = data.get("timestamp")
        try:
            timestamp = (datetime.fromisoformat(raw_ts) if isinstance(raw_ts, str)
                         else datetime.now(timezone.utc))
        except ValueError:
            logger.warning("unparseable timestamp %r; using receipt time", raw_ts)
            timestamp = datetime.now(timezone.utc)

        return cls(
            event_id=data.get("event_id") or str(uuid.uuid4()),
            timestamp=timestamp,
            aggregate_id=data.get("aggregate_id"),
            payload=data.get("payload") or {},
            event_type=event_type,
        )


# =============================================================================
# OMS (Order Management System) Events
# =============================================================================

@dataclass(frozen=True)
class OrderCreated(DomainEvent):
    """Published when a new order is created and accepted by the system."""
    event_type: EventType = field(default=EventType.ORDER_CREATED, init=False)
    # Payload expects: symbol, side, quantity, price, order_type, account_id


@dataclass(frozen=True)
class OrderModified(DomainEvent):
    """Published when an existing order is modified (price/quantity)."""
    event_type: EventType = field(default=EventType.ORDER_MODIFIED, init=False)
    # Payload expects: order_id, new_price, new_quantity, reason


@dataclass(frozen=True)
class OrderCancelled(DomainEvent):
    """Published when an order is cancelled."""
    event_type: EventType = field(default=EventType.ORDER_CANCELLED, init=False)
    # Payload expects: order_id, reason


@dataclass(frozen=True)
class OrderRejected(DomainEvent):
    """Published when an order is rejected (e.g., risk check failure)."""
    event_type: EventType = field(default=EventType.ORDER_REJECTED, init=False)
    # Payload expects: order_id, reason_code, message


@dataclass(frozen=True)
class OrderApproved(DomainEvent):
    """Published when an order passes all pre-trade risk checks."""
    event_type: EventType = field(default=EventType.ORDER_APPROVED, init=False)
    # Payload expects: order_id, account_login, symbol, volume, approved_at


@dataclass(frozen=True)
class DealCreated(DomainEvent):
    """Published when a new deal (trade) is executed."""
    event_type: EventType = field(default=EventType.DEAL_CREATED, init=False)
    # Payload expects: deal_id, order_id, price, quantity, commission, swap


@dataclass(frozen=True)
class DealModified(DomainEvent):
    """
    Specific to MT5-style trade corrections.
    Used when a dealer manually corrects a past deal.
    """
    event_type: EventType = field(default=EventType.DEAL_MODIFIED, init=False)
    # Payload expects: original_deal_id, correction_deal_id, reason, actor_id


@dataclass(frozen=True)
class PositionOpened(DomainEvent):
    """Published when a new position is opened."""
    event_type: EventType = field(default=EventType.POSITION_OPENED, init=False)


@dataclass(frozen=True)
class PositionClosed(DomainEvent):
    """Published when a position is closed."""
    event_type: EventType = field(default=EventType.POSITION_CLOSED, init=False)


@dataclass(frozen=True)
class PositionUpdated(DomainEvent):
    """Published when a position's P&L or margin changes."""
    event_type: EventType = field(default=EventType.POSITION_UPDATED, init=False)
    # Payload expects: position_id, current_price, unrealized_pnl, margin_used


@dataclass(frozen=True)
class HolidayCreated(DomainEvent):
    """Published when a new holiday configuration is created."""
    # Declared explicitly. Without it this class inherited DomainEvent's default of
    # EventType.ORDER_CREATED, so a margin call / stop-out was published on the
    # "order.created" channel. In-process subscribers registered by event CLASS
    # still received it, which is why nothing failed loudly - but the channel is
    # what Redis pub/sub routes on, so across processes a stopped-out account
    # notified every OrderCreated listener and reached no LiquidationWorker.
    event_type: EventType = field(default=EventType.HOLIDAY_CREATED, init=False)

# =============================================================================
# Market Data Events
# =============================================================================

@dataclass(frozen=True)
class TickReceived(DomainEvent):
    """Published when a new tick is received from a liquidity provider."""
    event_type: EventType = field(default=EventType.TICK_RECEIVED, init=False)
    # Payload expects: symbol, bid, ask, last_volume, exchange_timestamp


@dataclass(frozen=True)
class BookUpdated(DomainEvent):
    """Published when the order book (DOM) is updated."""
    event_type: EventType = field(default=EventType.BOOK_UPDATED, init=False)
    # Payload expects: symbol, bids_list, asks_list, sequence_number


@dataclass(frozen=True)
class BarAggregated(DomainEvent):
    """Published when an OHLCV bar completed aggregation."""
    event_type: EventType = field(default=EventType.BAR_AGGREGATED, init=False)
    # Payload expects: symbol, timeframe, open, high, low, close, tick_volume, open_time



# =============================================================================
# Risk Events
# =============================================================================

@dataclass(frozen=True)
class MarginCallEvent(DomainEvent):
    """Published when an account hits margin call level."""
    event_type: EventType = field(default=EventType.MARGIN_CALL, init=False)
    # Payload expects: account_id, margin_level, required_margin


@dataclass(frozen=True)
class StopOutEvent(DomainEvent):
    """Published when positions are forcibly closed due to insufficient margin."""
    event_type: EventType = field(default=EventType.STOP_OUT, init=False)
    # Payload expects: account_id, position_id, close_price, reason


# =============================================================================
# Execution Events (Phase 5)
# =============================================================================

@dataclass(frozen=True)
class OrderRouted(DomainEvent):
    """Published when an order is routed to a specific execution destination."""
    event_type: EventType = field(default=EventType.ORDER_ROUTED, init=False)
    # Payload expects: order_id, destination, rule_id, gateway_id

@dataclass(frozen=True)
class OrderQueuedForDealer(DomainEvent):
    """Published when an order is placed in the dealer queue for manual intervention."""
    event_type: EventType = field(default=EventType.ORDER_QUEUED_FOR_DEALER, init=False)
    # Payload expects: order_id, account_login, symbol, volume, timeout_at

@dataclass(frozen=True)
class OrderDealerConfirmed(DomainEvent):
    """Published when a dealer manually confirms an order."""
    event_type: EventType = field(default=EventType.ORDER_DEALER_CONFIRMED, init=False)
    # Payload expects: order_id, dealer_id, confirmed_at

@dataclass(frozen=True)
class OrderDealerRejected(DomainEvent):
    """Published when a dealer manually rejects an order."""
    event_type: EventType = field(default=EventType.ORDER_DEALER_REJECTED, init=False)
    # Payload expects: order_id, dealer_id, reason

@dataclass(frozen=True)
class OrderRequoted(DomainEvent):
    """Published when a dealer offers a requote to the client."""
    event_type: EventType = field(default=EventType.ORDER_REQUOTED, init=False)
    # Payload expects: order_id, dealer_id, new_price, reason

@dataclass(frozen=True)
class CoverageExposureUpdated(DomainEvent):
    """Published when the broker's coverage account exposure is updated."""
    event_type: EventType = field(default=EventType.COVERAGE_EXPOSURE_UPDATED, init=False)
    # Payload expects: coverage_account_id, symbol, net_exposure, volume_delta


# Ledger Events (Phase 7)
COMMISSION_CHARGED = "ledger.commission_charged"
SWAP_APPLIED = "ledger.swap_applied"
BALANCE_DEPOSITED = "ledger.balance_deposited"
BALANCE_WITHDRAWN = "ledger.balance_withdrawn"
BALANCE_CORRECTED = "ledger.balance_corrected"


@dataclass(frozen=True)
class CommissionCharged(DomainEvent):
    event_type: EventType = field(default=EventType.COMMISSION_CHARGED, init=False)

@dataclass(frozen=True)
class SwapApplied(DomainEvent):
    event_type: EventType = field(default=EventType.SWAP_APPLIED, init=False)

@dataclass(frozen=True)
class BalanceDeposited(DomainEvent):
    event_type: EventType = field(default=EventType.BALANCE_DEPOSITED, init=False)

@dataclass(frozen=True)
class BalanceWithdrawn(DomainEvent):
    event_type: EventType = field(default=EventType.BALANCE_WITHDRAWN, init=False)


# Margin state machine transitions, published by TickMarginPipeline

@dataclass(frozen=True)
class MarginCallEntered(DomainEvent):
    """Published when account equity drops below margin call level."""
    # Declared explicitly. Without it this class inherited DomainEvent's default of
    # EventType.ORDER_CREATED, so a margin call / stop-out was published on the
    # "order.created" channel. In-process subscribers registered by event CLASS
    # still received it, which is why nothing failed loudly - but the channel is
    # what Redis pub/sub routes on, so across processes a stopped-out account
    # notified every OrderCreated listener and reached no LiquidationWorker.
    event_type: EventType = field(default=EventType.MARGIN_CALL_TRIGGERED, init=False)

@dataclass(frozen=True)
class MarginCallExited(DomainEvent):
    """Published when account recovers above margin call level."""
    # Declared explicitly. Without it this class inherited DomainEvent's default of
    # EventType.ORDER_CREATED, so a margin call / stop-out was published on the
    # "order.created" channel. In-process subscribers registered by event CLASS
    # still received it, which is why nothing failed loudly - but the channel is
    # what Redis pub/sub routes on, so across processes a stopped-out account
    # notified every OrderCreated listener and reached no LiquidationWorker.
    event_type: EventType = field(default=EventType.MARGIN_CALL_EXITED, init=False)

@dataclass(frozen=True)
class StopOutEntered(DomainEvent):
    """Published when account equity drops below stop out level (liquidation starts)."""
    # Declared explicitly. Without it this class inherited DomainEvent's default of
    # EventType.ORDER_CREATED, so a margin call / stop-out was published on the
    # "order.created" channel. In-process subscribers registered by event CLASS
    # still received it, which is why nothing failed loudly - but the channel is
    # what Redis pub/sub routes on, so across processes a stopped-out account
    # notified every OrderCreated listener and reached no LiquidationWorker.
    event_type: EventType = field(default=EventType.STOP_OUT_INITIATED, init=False)

@dataclass(frozen=True)
class StopOutExited(DomainEvent):
    """Published when account recovers above stop out level after liquidation."""
    # Declared explicitly. Without it this class inherited DomainEvent's default of
    # EventType.ORDER_CREATED, so a margin call / stop-out was published on the
    # "order.created" channel. In-process subscribers registered by event CLASS
    # still received it, which is why nothing failed loudly - but the channel is
    # what Redis pub/sub routes on, so across processes a stopped-out account
    # notified every OrderCreated listener and reached no LiquidationWorker.
    event_type: EventType = field(default=EventType.STOP_OUT_EXITED, init=False)

# =============================================================================
# CONFIGURATION PLANE Events
# =============================================================================
# These drive ConfigCache invalidation. MT5's equivalent is the sink pattern:
# IMTConGroupSink::OnGroupUpdate, IMTConSymbolSink::OnSymbolUpdate and so on, which
# notify every connected manager terminal when a configuration object changes.
# Publishing them on the event bus is how our nodes stay in step.
# =============================================================================

@dataclass(frozen=True)
class GroupCreated(DomainEvent):
    """A new Group (rule engine) was created."""
    event_type: EventType = field(default=EventType.GROUP_CREATED, init=False)


@dataclass(frozen=True)
class GroupUpdated(DomainEvent):
    """A Group's configuration changed. Every node must invalidate its cache."""
    event_type: EventType = field(default=EventType.GROUP_UPDATED, init=False)


@dataclass(frozen=True)
class GroupDeleted(DomainEvent):
    """A Group was removed."""
    event_type: EventType = field(default=EventType.GROUP_DELETED, init=False)


@dataclass(frozen=True)
class SymbolCreated(DomainEvent):
    """A new Symbol was added to the price list."""
    event_type: EventType = field(default=EventType.SYMBOL_CREATED, init=False)


@dataclass(frozen=True)
class SymbolUpdated(DomainEvent):
    """A Symbol's specification changed (sessions, margin rates, swaps, limits)."""
    event_type: EventType = field(default=EventType.SYMBOL_UPDATED, init=False)


@dataclass(frozen=True)
class SymbolDeleted(DomainEvent):
    """A Symbol was removed from the price list."""
    event_type: EventType = field(default=EventType.SYMBOL_DELETED, init=False)


@dataclass(frozen=True)
class HolidayUpdated(DomainEvent):
    """A holiday was changed, affecting sessions and triple-swap scheduling."""
    event_type: EventType = field(default=EventType.HOLIDAY_UPDATED, init=False)


@dataclass(frozen=True)
class HolidayDeleted(DomainEvent):
    """A holiday was removed."""
    event_type: EventType = field(default=EventType.HOLIDAY_DELETED, init=False)


@dataclass(frozen=True)
class TradeModified(DomainEvent):
    """A dealer corrected a trade via the MT5 reversal + correction pattern."""
    event_type: EventType = field(default=EventType.TRADE_MODIFIED, init=False)

