"""
MT5 Manager API - Main query response schemas.

Maps to MT5 response objects:
- AccountInfo (from UserGet)
- PositionInfo (from PositionGet)
- DealInfo (from DealGet)
- OrderInfo (from OrderGet)
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class AccountInfo(BaseModel):
    """MT5 Account information (from UserGet)."""
    login: int
    group: str
    currency: str
    balance: Decimal
    credit: Decimal = Decimal('0')
    equity: Decimal
    margin: Decimal
    free_margin: Decimal
    margin_level: Decimal
    leverage: int
    enable: bool = True
    enable_charts: bool = True
    enable_news: bool = True
    enable_trades: bool = True
    password_phone: Optional[str] = None
    email: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    registration: Optional[datetime] = None
    last_visit: Optional[datetime] = None
    last_pass_change: Optional[datetime] = None
    comment: Optional[str] = None


class PositionInfo(BaseModel):
    """MT5 Position information (from PositionGet)."""
    ticket: int
    login: int
    symbol: str
    action: str  # BUY or SELL
    volume: Decimal
    price_open: Decimal
    price_current: Decimal
    price_sl: Optional[Decimal] = Field(None, alias="sl")
    price_tp: Optional[Decimal] = Field(None, alias="tp")
    swap: Decimal
    profit: Decimal
    commission: Decimal = Decimal('0')
    magic: int = 0
    comment: Optional[str] = None
    time_create: Optional[datetime] = None
    time_update: Optional[datetime] = None

    class Config:
        populate_by_name = True


class DealInfo(BaseModel):
    """MT5 Deal information (from DealGet)."""
    ticket: int
    login: int
    symbol: str
    deal_type: str  # BUY, SELL, BALANCE, etc.
    entry: str  # IN, OUT, INOUT, OUT_BY
    volume: Decimal
    price: Decimal
    profit: Decimal
    swap: Decimal
    commission: Decimal
    comment: Optional[str] = None
    time: Optional[datetime] = None


class OrderInfo(BaseModel):
    """MT5 Order information (from OrderGet)."""
    ticket: int
    login: int
    symbol: str
    order_type: str  # BUY, SELL, BUY_LIMIT, etc.
    state: str  # NEW, PLACED, FILLED, etc.
    volume_initial: Decimal
    volume_current: Decimal
    price_order: Decimal
    price_sl: Optional[Decimal] = Field(None, alias="sl")
    price_tp: Optional[Decimal] = Field(None, alias="tp")
    time_setup: Optional[datetime] = None
    time_expiration: Optional[datetime] = None
    time_done: Optional[datetime] = None
    comment: Optional[str] = None

    class Config:
        populate_by_name = True