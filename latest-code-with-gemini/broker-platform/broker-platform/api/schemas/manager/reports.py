"""
MT5 Manager API - Reports Schemas.
"""
from decimal import Decimal
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class AccountStatementResponse(BaseModel):
    login: int
    group: str
    currency: str
    balance_initial: Decimal
    balance_final: Decimal
    total_deposit: Decimal
    total_withdrawal: Decimal
    closed_pnl: Decimal
    total_commission: Decimal
    total_swap: Decimal
    trades_count: int


class DailySummaryItem(BaseModel):
    date: str
    active_accounts: int
    total_volume_lots: Decimal
    gross_pnl: Decimal
    net_pnl: Decimal
    b_book_pnl: Decimal
    a_book_pnl: Decimal
