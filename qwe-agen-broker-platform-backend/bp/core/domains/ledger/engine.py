from typing import Optional
from decimal import Decimal
from core.domains.ledger.models import BalanceOperation, BalanceOperationType
from core.domains.common.value_objects import Money
from core.ports.interfaces import ILedgerRepository, IAccountRepository


class LedgerEngine:
    """
    Pure domain logic for double-entry bookkeeping.
    Every balance change must be recorded immutably.
    """

    def __init__(self, ledger_repo: ILedgerRepository, account_repo: IAccountRepository):
        self.ledger_repo = ledger_repo
        self.account_repo = account_repo

    async def record_operation(
        self,
        account_login: str,
        operation_type: BalanceOperationType,
        amount: Money,
        reference_id: Optional[str] = None,
        comment: Optional[str] = None
    ) -> BalanceOperation:
        """
        Record a balance operation and update account balance.
        Returns the immutable BalanceOperation record.
        """
        account = await self.account_repo.find_by_login(account_login)
        if not account:
            raise ValueError(f"Account {account_login} not found")

        # Calculate new balance
        new_balance = account.balance + amount  # Money handles +/-
        if operation_type == BalanceOperationType.WITHDRAWAL and new_balance.amount < Decimal('0'):
            raise ValueError(f"Insufficient funds for withdrawal on account {account_login}: available balance {account.balance.amount}, attempted {abs(amount.amount)}")

        # Create immutable operation record
        operation = BalanceOperation(
            account_login=account_login,
            operation_type=operation_type,
            amount=amount,
            balance_after=new_balance,
            reference_id=reference_id,
            comment=comment
        )

        # Persist operation
        await self.ledger_repo.save(operation)

        # Update account balance
        account.balance = new_balance
        await self.account_repo.save(account)

        return operation
