"""
Common MT5 Manager API response schemas.

Mirrors MT5's response structure:
- TradeResult: { answer: Request, result: Confirm }
- ExceptionResult: { message, code, stackTrace }
"""
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Confirm(BaseModel):
    """MT5 Confirm object - result of a trade operation."""
    request_id: str = Field(..., description="Original request ID")
    order_ticket: Optional[int] = Field(None, description="Order ticket (if applicable)")
    deal_ticket: Optional[int] = Field(None, description="Deal ticket (if applicable)")
    position_ticket: Optional[int] = Field(None, description="Position ticket (if applicable)")
    price: Optional[Decimal] = Field(None, description="Execution price")
    volume: Optional[Decimal] = Field(None, description="Filled volume")
    retcode: int = Field(0, description="MT5 return code (0 = OK)")
    comment: str = Field("", description="Execution comment")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Request(BaseModel):
    """MT5 Request object - echo of the original request."""
    action: str = Field(..., description="Trade action (BUY, SELL, CLOSE, etc.)")
    symbol: Optional[str] = None
    volume: Optional[Decimal] = None
    price: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None
    comment: Optional[str] = None


class TradeResult(BaseModel):
    """MT5 TradeResult - standard response for trade operations."""
    answer: Request = Field(..., description="Echo of original request")
    result: Confirm = Field(..., description="Execution result")


class ExceptionResult(BaseModel):
    """MT5 ExceptionResult - error response."""
    message: str
    code: int = Field(..., description="MT5 error code")
    stack_trace: Optional[str] = Field(None, alias="stackTrace")

    class Config:
        populate_by_name = True


class PaginatedResult(BaseModel):
    """Generic paginated response for list queries."""
    total: int
    page: int
    page_size: int
    items: List[Any]