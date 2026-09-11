"""OMS Domain - Order Management System (MT5-accurate)."""
from .enums import (
    OrderType, OrderState, OrderReason, TimeInForce, ActivationMode,
    DealType, DealEntry, DealReason, PositionAction, PositionReason,
    OrderFlags
)
from .entities.order import Order
from .entities.deal import Deal
from .entities.position import Position
from .services.trade_modification import TradeModificationService, TradeModificationResult
from .events import (
    OrderCreated, OrderStateChanged, OrderFilled,
    DealCreated, PositionOpened, PositionClosed,
    PositionModified, TradeModified
)

__all__ = [
    # Enums
    "OrderType", "OrderState", "OrderReason", "TimeInForce", "ActivationMode",
    "DealType", "DealEntry", "DealReason", "PositionAction", "PositionReason",
    "OrderFlags",
    # Entities
    "Order", "Deal", "Position",
    # Services
    "TradeModificationService", "TradeModificationResult",
    # Events
    "OrderCreated", "OrderStateChanged", "OrderFilled",
    "DealCreated", "PositionOpened", "PositionClosed",
    "PositionModified", "TradeModified",
]