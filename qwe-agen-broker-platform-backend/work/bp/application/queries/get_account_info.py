"""
Get Account Info Query Handler - CQRS Read Side

Handles retrieving account balance, equity, margin usage, and margin level snapshot.

Architectural Rule: Application Query handler in application/queries/, pure Python logic.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Optional

from core.domains.market_data.margin import margin_level as compute_margin_level
from core.ports.interfaces import IAccountRepository, IPositionRepository


@dataclass(frozen=True)
class GetAccountInfoQuery:
    """Query payload to fetch account financial snapshot.

    D2: the field was `login_id` while both routers passed `account_login=`,
    so every construction raised TypeError - one of the four reasons this
    handler was unreachable. Renamed to match its sibling GetPositionsQuery.
    """
    account_login: str


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
        account = await self.account_repo.find_by_login(query.account_login)
        if not account:
            raise ValueError(f"Account '{query.account_login}' not found")

        balance = account.balance.amount if hasattr(account.balance, 'amount') else Decimal(str(account.balance))
        equity = account.equity.amount if hasattr(account.equity, 'amount') else Decimal(str(account.equity))
        margin_used = account.margin_used.amount if hasattr(account.margin_used, 'amount') else Decimal(str(account.margin_used))
        margin_free = account.margin_free.amount if hasattr(account.margin_free, 'amount') else Decimal(str(account.margin_free))

        # Single source of truth. This was the eighth hand-written copy of the
        # formula, and it returned 0 when the account was flat - the exact
        # "reads as fully exhausted" case MARGIN_LEVEL_UNLIMITED exists to
        # prevent (see Account.recompute_margin_level's docstring).
        margin_level = compute_margin_level(equity, margin_used)

        group_name = account.group.name if hasattr(account.group, 'name') else str(account.group)
        currency = account.balance.currency if hasattr(account.balance, 'currency') else "USD"
        credit = account.credit.amount if hasattr(account.credit, 'amount') else Decimal(str(account.credit))
        # The manager UserGet schema requires a leverage; it previously had no
        # source for one, which is part of why it fell back to the manager's own
        # account. effective_leverage() resolves account-then-group-then-100.
        leverage = account.effective_leverage()

        return {
            # D2: AccountInfo.login_id is a str and account.login is an int -
            # the same int<->String(32) boundary M5 met on the write side.
            # Constructing the schema raised ValidationError, so even once the
            # handler was registered and the query field renamed, this route
            # would still have 500d. The read side owns the DTO shape.
            "login_id": str(account.login),
            "group": group_name,
            "balance": balance,
            "equity": equity,
            "margin_used": margin_used,
            "margin_free": margin_free,
            "margin_level": margin_level,
            "currency": currency,
            "credit": credit,
            "leverage": leverage,
        }
