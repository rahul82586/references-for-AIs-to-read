"""
MT5 Manager API - Liquidity Allocation Schemas.
"""
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field


class LPBridgeConnectRequest(BaseModel):
    lp_name: str = Field(..., description="Liquidity Provider identifier (e.g. LMAX, Finalto)")
    protocol: str = Field("FIX4.4", description="Protocol version")
    target_comp_id: str = Field(..., description="FIX TargetCompID")


class LPBridgeConnectResponse(BaseModel):
    retcode: int = 0
    lp_name: str
    status: str = "CONNECTED"
    session_id: str
    message: str = "LP Bridge connected"


class ABookAllocationRequest(BaseModel):
    order_id: str = Field(..., description="Order Ticket ID")
    lp_name: str = Field(..., description="Target Liquidity Provider")
    volume: Decimal = Field(..., gt=0, description="Volume to route")


class ABookAllocationResponse(BaseModel):
    retcode: int = 0
    order_id: str
    lp_name: str
    fill_price: Optional[Decimal] = None
    status: str = "FILLED"
    message: str = "Order allocated to LP"
