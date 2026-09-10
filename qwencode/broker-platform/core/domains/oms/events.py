"""OMS-specific domain events."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict
import uuid


@dataclass
class OMSDomainEvent:
    """Base class for OMS domain events."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    aggregate_id: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)




@dataclass
class OrderCreated(OMSDomainEvent):
    """Published when a new order is created."""
    pass


@dataclass
class OrderStateChanged(OMSDomainEvent):
    """Published when order state changes."""
    pass


@dataclass
class OrderFilled(OMSDomainEvent):
    """Published when an order is fully filled."""
    pass


@dataclass
class DealCreated(OMSDomainEvent):
    """Published when a new deal is recorded."""
    pass


@dataclass
class PositionOpened(OMSDomainEvent):
    """Published when a new position is opened."""
    pass


@dataclass
class PositionClosed(OMSDomainEvent):
    """Published when a position is closed."""
    pass


@dataclass
class PositionModified(OMSDomainEvent):
    """Published when a position is modified (SL/TP change)."""
    pass


@dataclass
class TradeModified(OMSDomainEvent):
    """Published when a deal is modified via reversal + correction."""
    pass