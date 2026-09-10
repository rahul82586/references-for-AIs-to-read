import logging
from decimal import Decimal
from core.domains.oms.entities.deal import Deal
from core.domains.accounts.models import Account
from core.domains.ledger.models import BalanceOperationType
from core.domains.ledger.engine import LedgerEngine
from core.domains.common.value_objects import Money
from core.ports.interfaces import IEventBus
from core.events.domain_events import DomainEvent, EventType

logger = logging.getLogger(__name__)


class CommissionService:
    """
    Calculates and applies commissions on every deal.
    Mirrors MT5 commission modes: per-lot, per-volume, percentage.
    """

    def __init__(self, ledger_engine: LedgerEngine, event_bus: IEventBus, symbol_repo: Optional[Any] = None):
        self.ledger_engine = ledger_engine
        self.event_bus = event_bus
        self.symbol_repo = symbol_repo

    async def apply_commission(self, deal: Deal, account: Account) -> Money:
        """
        Calculate commission based on account's Group commission profile.
        Deduct from account balance and record as BalanceOperation.
        Returns the commission amount (always negative for client).
        """
        commission_profile = account.group.commissions[0] if (account.group and account.group.commissions) else None

        if not commission_profile:
            return Money(Decimal('0'), "USD")

        # Calculate commission amount based on mode
        if commission_profile.type == "MONEY":
            # Fixed amount per deal
            commission_amount = Money(Decimal(str(commission_profile.value)), commission_profile.currency)
        elif commission_profile.type == "LOTS" or commission_profile.type == "per_lot":
            # Per lot (e.g., $7 per 1 lot)
            commission_amount = Money(
                Decimal(str(commission_profile.value)) * deal.volume.value,
                commission_profile.currency
            )
        elif commission_profile.type == "VOLUME":
            # Per volume unit using dynamic symbol contract size
            contract_size = Decimal('100000')
            if self.symbol_repo:
                try:
                    sym = self.symbol_repo.get_symbol(deal.symbol)
                    if sym:
                        contract_size = Decimal(str(sym.contract_size))
                except Exception:
                    pass
            commission_amount = Money(
                Decimal(str(commission_profile.value)) * deal.volume.value * contract_size,
                commission_profile.currency
            )
        else:
            commission_amount = Money(Decimal('0'), "USD")

        # Commission is always a charge (negative for client)
        commission_charge = Money(-commission_amount.amount, commission_amount.currency)
        account_login_str = str(getattr(account, 'login', getattr(account, 'login_id', account.id)))

        # Record in ledger
        operation = await self.ledger_engine.record_operation(
            account_login=account_login_str,
            operation_type=BalanceOperationType.COMMISSION,
            amount=commission_charge,
            reference_id=deal.deal_id,
            comment=f"Commission on deal {deal.deal_id}"
        )

        # Emit event
        event = DomainEvent(
            event_type=EventType.COMMISSION_CHARGED,
            aggregate_id=deal.deal_id,
            payload={
                'deal_id': deal.deal_id,
                'account_login': account_login_str,
                'commission_amount': str(commission_charge.amount),
                'currency': commission_charge.currency
            }
        )
        await self.event_bus.publish(event)

        logger.info(f"Commission applied: {commission_charge.amount} {commission_charge.currency} for account {account_login_str}")

        return commission_charge
