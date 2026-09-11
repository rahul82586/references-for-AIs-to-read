"""
Get Account Info Query Handler - CQRS Read Side

Handles retrieving account balance, equity, margin usage, and margin level snapshot.

Architectural Rule: Application Query handler in application/queries/, pure Python logic.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Optional

from core.ports.interfaces import IAccountRepository, IPositionRepository


@dataclass(frozen=True)
class GetAccountInfoQuery:
    """Query payload to fetch account financial snapshot."""
    login_id: str


class GetAccountInfoQueryHandler:
    """Read-side query handler for client account snapshots."""

    def __init__(
        self,
        account_repo: IAccountRepository,
        position_repo: Optional[IPositionRepository] = None,
        market_data_engine: Optional[Any] = None
    ):
        self.account_repo = account_repo
        self.position_repo = position_repo
        self.market_data_engine = market_data_engine

    async def handle(self, query: GetAccountInfoQuery) -> dict:
        """Process GetAccountInfoQuery and return account metrics."""
        account = await self.account_repo.find_by_login(query.login_id)
        if not account:
            raise ValueError(f"Account '{query.login_id}' not found")

        balance = account.balance.amount if hasattr(account.balance, 'amount') else Decimal(str(account.balance))
        equity = account.equity.amount if hasattr(account.equity, 'amount') else Decimal(str(account.equity))
        margin_used = account.margin_used.amount if hasattr(account.margin_used, 'amount') else Decimal(str(account.margin_used))
        margin_free = account.margin_free.amount if hasattr(account.margin_free, 'amount') else Decimal(str(account.margin_free))

        # Calculate margin level percentage
        if margin_used > Decimal('0'):
            margin_level = (equity / margin_used) * Decimal('100')
        else:
            margin_level = Decimal('0')

        group_name = account.group.name if hasattr(account.group, 'name') else str(account.group)
        currency = account.balance.currency if hasattr(account.balance, 'currency') else "USD"

        return {
            "login_id": account.login,
            "group": group_name,
            "balance": balance,
            "equity": equity,
            "margin_used": margin_used,
            "margin_free": margin_free,
            "margin_level": margin_level,
            "currency": currency,
        }
