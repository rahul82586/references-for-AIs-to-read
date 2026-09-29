"""
MT5 Manager API - Risk Engine Schemas.
"""
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field


class MarginCheckRequest(BaseModel):
    login: int = Field(..., description="Account login number")
    symbol: str = Field(..., description="Trading symbol")
    operation: str = Field(..., description="BUY or SELL")
    volume: Decimal = Field(..., gt=0, description="Order volume in lots")


class MarginCheckResponse(BaseModel):
    retcode: int = 0
    margin_required: Decimal
    margin_free: Decimal
    margin_level_after: Decimal
    is_sufficient: bool
    message: str = "Margin check evaluated"


class ForceLiquidationRequest(BaseModel):
    login: int = Field(..., description="Account login number")
    comment: str = Field("Dealer forced stop-out", description="Liquidation reason")


class ForceLiquidationResponse(BaseModel):
    retcode: int = 0
    login: int
    liquidated_positions_count: int
    closed_tickets: List[str]
    message: str = "Force liquidation executed"
