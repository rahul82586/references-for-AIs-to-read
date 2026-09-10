import asyncio
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from core.domains.oms.entities.position import Position
from core.domains.oms.enums import OrderType
from core.domains.ledger.models import BalanceOperationType
from core.domains.ledger.engine import LedgerEngine
from core.domains.common.value_objects import Money
from core.ports.interfaces import (
    IPositionRepository,
    IAccountRepository,
    ISymbolRepository,
    IEventBus
)
from core.events.domain_events import DomainEvent, EventType

logger = logging.getLogger(__name__)


class SwapWorker:
    """
    Background worker that runs daily at broker's rollover time (e.g., 5:00 PM EST).
    Calculates and applies swaps for all overnight positions.
    Mirrors MT5 swap modes: points, money, percent.
    """

    def __init__(self,
                 ledger_engine: LedgerEngine,
                 position_repo: IPositionRepository,
                 account_repo: IAccountRepository,
                 symbol_repo: ISymbolRepository,
                 event_bus: IEventBus,
                 rollover_hour_utc: int = 22):  # 5 PM EST = 22:00 UTC
        self.ledger_engine = ledger_engine
        self.position_repo = position_repo
        self.account_repo = account_repo
        self.symbol_repo = symbol_repo
        self.event_bus = event_bus
        self.rollover_hour_utc = rollover_hour_utc
        self._running = False

    async def start(self):
        """Main loop: wait for rollover time, then process all positions."""
        logger.info(f"SwapWorker started, rollover at {self.rollover_hour_utc}:00 UTC")
        self._running = True
        _last_processed_date = None
        while self._running:
            now = datetime.now(timezone.utc)
            if now.hour == self.rollover_hour_utc and _last_processed_date != now.date():
                logger.info("Rollover time reached, processing swaps...")
                await self._process_swaps()
                _last_processed_date = now.date()
                await asyncio.sleep(60)
            else:
                await asyncio.sleep(60)  # Check every minute

    async def _process_swaps(self):
        """Calculate and apply swaps for all open positions."""
        all_positions = await self.position_repo.get_open_positions()
        logger.info(f"Processing swaps for {len(all_positions)} positions")

        for position in all_positions:
            try:
                await self._apply_swap_for_position(position)
            except Exception as e:
                logger.error(f"Swap error for position {position.id}: {e}")
                continue

    async def _apply_swap_for_position(self, position: Position):
        """Calculate swap based on account's Group swap profile."""
        account = await self.account_repo.find_by_login(position.account_login)
        if not account:
            logger.warning(f"Account {position.account_login} not found for swap calculation")
            return

        # Check if swaps are enabled for this group
        swap_profile = getattr(account.group, 'swaps', getattr(account.group, 'swap', None))
        if not swap_profile or not getattr(swap_profile, 'enable_swaps', True):
            return

        symbol = await self.symbol_repo.get_symbol(position.symbol)
        if not symbol:
            logger.warning(f"Symbol {position.symbol} not found for swap calculation")
            return

        # Determine swap rate based on position side
        if position.side == OrderType.BUY or (hasattr(position.side, 'name') and position.side.name == "BUY"):
            swap_rate = swap_profile.swap_long
        else:
            swap_rate = swap_profile.swap_short

        # Calculate swap amount based on mode
        if swap_profile.swap_type == "POINTS":
            # Swap in points (e.g., -5 points per lot)
            swap_value = Money(
                Decimal(str(swap_rate)) * position.volume.value * symbol.tick_value,
                account.balance.currency
            )
        elif swap_profile.swap_type == "MONEY":
            # Fixed money per lot (e.g., -$2 per lot)
            swap_value = Money(
                Decimal(str(swap_rate)) * position.volume.value,
                account.balance.currency
            )
        elif swap_profile.swap_type == "PERCENT":
            # Percentage of position value
            position_value = position.volume.value * symbol.contract_size * position.average_price.value
            swap_value = Money(
                position_value * Decimal(str(swap_rate)) / Decimal('100') / Decimal('365'),
                account.balance.currency
            )
        else:
            swap_value = Money(Decimal('0'), account.balance.currency)

        # Record in ledger
        operation = await self.ledger_engine.record_operation(
            account_login=position.account_login,
            operation_type=BalanceOperationType.SWAP,
            amount=swap_value,
            reference_id=position.id,
            comment=f"Swap on position {position.symbol}"
        )

        # Emit event
        event = DomainEvent(
            event_type=EventType.SWAP_APPLIED,
            aggregate_id=position.id,
            payload={
                'position_id': position.id,
                'account_login': position.account_login,
                'symbol': position.symbol,
                'swap_amount': str(swap_value.amount),
                'currency': swap_value.currency
            }
        )
        await self.event_bus.publish(event)

        logger.info(f"Swap applied: {swap_value.amount} {swap_value.currency} for position {position.id}")

    def stop(self):
        self._running = False
