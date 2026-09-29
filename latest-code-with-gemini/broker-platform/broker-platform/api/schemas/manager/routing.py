"""
MT5 Manager API - Order Routing Schemas.
"""
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field


class RouteEvaluateRequest(BaseModel):
    login: int = Field(..., description="Account login number")
    symbol: str = Field(..., description="Trading symbol (e.g., EURUSD)")
    operation: str = Field(..., description="BUY, SELL, BUY_LIMIT, SELL_LIMIT, etc.")
    volume: Decimal = Field(..., gt=0, description="Order volume in lots")
    price: Optional[Decimal] = Field(None, description="Order price")


class RouteEvaluateResponse(BaseModel):
    retcode: int = 0
    destination: str = Field(..., description="B_BOOK, A_BOOK, DEALER, REJECT")
    matched_rule: Optional[str] = None
    delay_ms: int = 0
    clear_sl: bool = False
    clear_tp: bool = False
    message: str = "Route evaluated"


class NOPLimitCheckRequest(BaseModel):
    symbol: str = Field(..., description="Trading symbol")
    volume: Decimal = Field(..., gt=0, description="Order volume")


class NOPLimitCheckResponse(BaseModel):
    symbol: str
    current_nop: Decimal
    nop_limit: Decimal
    exceeds_limit: bool
    recommended_action: str
