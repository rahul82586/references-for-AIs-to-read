from dataclasses import dataclass
from typing import Optional
import logging
from decimal import Decimal

from core.domains.ledger.models import BalanceOperation, BalanceOperationType
from core.domains.common.value_objects import Money
from core.domains.ledger.engine import LedgerEngine
from core.ports.interfaces import IEventBus
from core.events.domain_events import DomainEvent, EventType

logger = logging.getLogger(__name__)


@dataclass
class BalanceOperationCommand:
    """Command to perform a balance operation (deposit/withdrawal)."""
    account_login: str
    operation_type: BalanceOperationType
    amount: Money
    reference_id: Optional[str] = None
    comment: Optional[str] = None


class BalanceOperationCommandHandler:
    """Handles deposit and withdrawal operations."""

    def __init__(self, ledger_engine: LedgerEngine, event_bus: IEventBus):
        self.ledger_engine = ledger_engine
        self.event_bus = event_bus

    async def handle(self, command: BalanceOperationCommand) -> BalanceOperation:
        """
        Process a deposit or withdrawal.
        Validates sufficient balance for withdrawals.
        """
        amount = command.amount
        # Validate withdrawal
        if command.operation_type == BalanceOperationType.WITHDRAWAL:
            account = await self.ledger_engine.account_repo.find_by_login(command.account_login)
            if not account:
                raise ValueError(f"Account {command.account_login} not found")
            
            amount = Money(-abs(command.amount.amount), command.amount.currency)
            if account.balance.amount + amount.amount < Decimal('0'):
                raise ValueError("Insufficient balance for withdrawal")

        # Record operation
        operation = await self.ledger_engine.record_operation(
            account_login=command.account_login,
            operation_type=command.operation_type,
            amount=amount,
            reference_id=command.reference_id,
            comment=command.comment
        )

        # Emit event
        event_type_map = {
            BalanceOperationType.DEPOSIT: EventType.BALANCE_DEPOSITED,
            BalanceOperationType.WITHDRAWAL: EventType.BALANCE_WITHDRAWN,
            BalanceOperationType.COMMISSION: EventType.COMMISSION_CHARGED,
            BalanceOperationType.SWAP: EventType.SWAP_APPLIED,
            BalanceOperationType.CORRECTION: EventType.BALANCE_CORRECTED,
            BalanceOperationType.BONUS: EventType.BALANCE_DEPOSITED,
            BalanceOperationType.DEAL_PROFIT: EventType.BALANCE_DEPOSITED,
            BalanceOperationType.DEAL_LOSS: EventType.BALANCE_WITHDRAWN,
        }
        event_type = event_type_map.get(command.operation_type)
        if not event_type:
            raise ValueError(f"Unsupported operation type: {command.operation_type}")
        event = DomainEvent(
            event_type=event_type,
            aggregate_id=operation.operation_id,
            payload={
                'operation_id': operation.operation_id,
                'account_login': command.account_login,
                'amount': str(command.amount.amount),
                'currency': command.amount.currency,
                'balance_after': str(operation.balance_after.amount)
            }
        )
        await self.event_bus.publish(event)

        logger.info(f"Balance operation completed: {command.operation_type.value} {command.amount.amount} for account {command.account_login}")

        return operation
