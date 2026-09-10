"""
Modify Deal Command Handler (MT5 Trade Modification).

Implements the MT5 Trade Modification pattern:
1. Fetches original deal
2. Creates REVERSAL deal (exact opposite)
3. Creates CORRECTION deal (with new parameters)
4. Updates account balance
5. Emits TradeModified event

This is the MT5-accurate way to modify a deal post-execution.
The original deal is NEVER modified — instead, two new deals are created.
"""
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from core.domains.accounts.account import Account
from core.domains.common.value_objects import Money, Price, Volume
from core.domains.oms.entities.deal import Deal
from core.domains.risk.liquidation_service import LiquidationService
from core.events.domain_events import TradeModified
from core.ports.interfaces import (
    IAccountRepository,
    IDealRepository,
    IEventBus,
)
from application.services.risk_service import PreTradeRiskService

logger = logging.getLogger(__name__)


@dataclass
class ModifyDealCommand:
    """Command to modify a deal (MT5 Trade Modification)."""
    account_login: int
    dealer_login: int
    original_deal_id: str
    new_price: Optional[Decimal] = None
    new_volume: Optional[Decimal] = None
    new_profit: Optional[Decimal] = None
    reason: str = "Dealer modification"


class ModifyDealHandler:
    """Handler for ModifyDealCommand."""

    def __init__(
        self,
        account_repo: IAccountRepository,
        deal_repo: IDealRepository,
        risk_service: PreTradeRiskService,
        event_bus: IEventBus,
    ):
        self.account_repo = account_repo
        self.deal_repo = deal_repo
        self.risk_service = risk_service
        self.event_bus = event_bus

    async def handle(self, command: ModifyDealCommand) -> dict:
        """
        Execute the modify deal command.
        
        Returns dict with reversal_deal and correction_deal.
        """
        # 1. Fetch original deal
        original = await self.deal_repo.find_by_id(command.original_deal_id)
        if not original:
            raise ValueError(f"Deal {command.original_deal_id} not found")

        # 2. Verify ownership
        if original.account_login != command.account_login:
            raise ValueError(
                f"Deal {command.original_deal_id} does not belong to account {command.account_login}"
            )

        # 3. Only trading deals can be modified
        from core.domains.oms.enums import DealType
        if original.deal_type not in [DealType.BUY, DealType.SELL]:
            raise ValueError(
                f"Cannot modify non-trading deal of type {original.deal_type.value}"
            )

        # 4. Create reversal and correction deals (inside per-account lock)
        async with self.risk_service.account_lock(command.account_login):
            # Create reversal deal (exact opposite)
            reversal = original.create_reversal(reason=command.reason)
            reversal.dealer_login = command.dealer_login

            # Create correction deal (with new parameters)
            new_volume = Volume(command.new_volume) if command.new_volume else None
            new_price = Price(command.new_price) if command.new_price else None
            new_profit = Money(command.new_profit, original.profit.currency) if command.new_profit else None

            correction = original.create_correction(
                new_volume=new_volume,
                new_price=new_price,
                new_profit=new_profit,
                reason=command.reason,
            )
            correction.dealer_login = command.dealer_login

            # Calculate balance adjustment
            # Balance change = correction.profit - original.profit
            balance_adjustment = correction.profit.amount - original.profit.amount

            # Update account balance
            account = await self.account_repo.find_by_login(command.account_login)
            if account:
                account.balance = Money(
                    account.balance.amount + balance_adjustment,
                    account.currency
                )
                account.equity = Money(
                    account.balance.amount + account.profit.amount,
                    account.currency
                )
                if account.margin_used.amount > Decimal('0'):
                    account.recompute_margin_level()
                await self.account_repo.save(account)

            # Persist both deals
            await self.deal_repo.save(reversal)
            await self.deal_repo.save(correction)

        # 5. Emit event
        event = TradeModified(
            aggregate_id=original.deal_id,
            payload={
                "original_deal_id": original.deal_id,
                "reversal_deal_id": reversal.deal_id,
                "correction_deal_id": correction.deal_id,
                "account_login": command.account_login,
                "dealer_login": command.dealer_login,
                "balance_adjustment": str(balance_adjustment),
                "reason": command.reason,
            }
        )
        await self.event_bus.publish(event)

        logger.info(
            f"Deal {command.original_deal_id} modified: "
            f"reversal={reversal.deal_id}, correction={correction.deal_id}"
        )

        return {
            "reversal_deal": reversal,
            "correction_deal": correction,
            "original_deal": original,
        }