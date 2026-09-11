"""
Account API Pydantic Schemas

Input and output validation models for login, authentication tokens, account metrics, and open positions.

Architectural Rule: Strict Decimal precision for monetary and balance fields.
"""
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Client authentication credentials schema."""
    login_id: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1, max_length=128)


class TokenResponse(BaseModel):
    """OAuth2 JWT access token response schema."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24 hours in seconds


class AccountInfo(BaseModel):
    """Account balance, equity, and margin level snapshot schema."""
    login_id: str
    group: str
    balance: Decimal
    equity: Decimal
    margin_used: Decimal
    margin_free: Decimal
    margin_level: Decimal
    currency: str = "USD"


class PositionResponse(BaseModel):
    """Open trading position details schema."""
    position_id: str
    symbol: str
    side: str  # "BUY" or "SELL"
    volume: Decimal
    average_price: Decimal
    unrealized_pnl: Decimal
    swap: Decimal = Decimal('0')
