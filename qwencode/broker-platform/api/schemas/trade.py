"""
Trade API Pydantic Schemas

Input and output validation models for trade order placement, modification, and query endpoints.

Architectural Rule: Strict Decimal precision for all prices and volumes.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class OrderRequest(BaseModel):
    """Client request schema to place a new order."""
    symbol: str = Field(..., min_length=1, max_length=32)
    order_type: str = Field(..., description="BUY, SELL, BUY_LIMIT, SELL_LIMIT, BUY_STOP, SELL_STOP")
    volume: Decimal = Field(..., gt=Decimal('0'))
    price: Optional[Decimal] = Field(None, description="Required for pending orders")
    type_filling: str = Field("FOK", description="FOK, IOC, RETURN")
    stop_loss: Optional[Decimal] = Field(None)
    take_profit: Optional[Decimal] = Field(None)
    comment: Optional[str] = Field(None, max_length=256)


class OrderResponse(BaseModel):
    """Response returned after order placement or query."""
    ticket_id: str
    symbol: str
    order_type: str
    volume: Decimal
    filled_volume: Decimal
    price: Optional[Decimal]
    state: str
    created_at: datetime
    message: Optional[str] = None


class ModifyOrderRequest(BaseModel):
    """Client request schema to modify a pending order."""
    price: Optional[Decimal] = Field(None)
    stop_loss: Optional[Decimal] = Field(None)
    take_profit: Optional[Decimal] = Field(None)
