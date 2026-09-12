"""
MT5 Manager API Trading schemas.

Maps to MT5 endpoints:
- OrderSend (market/pending orders)
- OrderClose
- OrderModify
- DealModify
- OrderDelete
"""
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class OrderSendRequest(BaseModel):
    """MT5 OrderSend request body."""
    symbol: str = Field(..., description="Trading symbol (e.g., EURUSD)")
    operation: str = Field(
        ...,
        description="Buy, Sell, BuyStop, SellStop, BuyLimit, SellLimit"
    )
    volume: Decimal = Field(..., description="Trade volume in lots", gt=0)
    price: Optional[Decimal] = Field(
        None,
        description="Required for stop/limit orders"
    )
    stop_loss: Optional[Decimal] = Field(None, alias="stoploss")
    take_profit: Optional[Decimal] = Field(None, alias="takeprofit")
    deviation: Optional[int] = Field(
        None,
        description="Slippage in points"
    )
    comment: Optional[str] = Field(None, max_length=255)

    class Config:
        populate_by_name = True


class OrderCloseRequest(BaseModel):
    """MT5 OrderClose request."""
    ticket: int = Field(..., description="Order/position ticket")
    volume: Optional[Decimal] = Field(
        None,
        description="Lots to close (None = full close)"
    )
    price: Optional[Decimal] = Field(
        None,
        description="Required for Instant Execution"
    )
    deviation: Optional[int] = Field(None, description="Slippage in points")


class OrderModifyRequest(BaseModel):
    """MT5 OrderModify request."""
    ticket: int = Field(..., description="Order ticket")
    price: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = Field(None, alias="stoploss")
    take_profit: Optional[Decimal] = Field(None, alias="takeprofit")
    expiration: Optional[str] = Field(
        None,
        description="ISO 8601 datetime for pending order expiration"
    )

    class Config:
        populate_by_name = True


class DealModifyRequest(BaseModel):
    """MT5 DealModify request (modify SL/TP of open position)."""
    ticket: int = Field(..., description="Position ticket")
    stop_loss: Optional[Decimal] = Field(None, alias="stoploss")
    take_profit: Optional[Decimal] = Field(None, alias="takeprofit")

    class Config:
        populate_by_name = True


class OrderDeleteRequest(BaseModel):
    """MT5 OrderDelete request (cancel pending order)."""
    ticket: int = Field(..., description="Pending order ticket")