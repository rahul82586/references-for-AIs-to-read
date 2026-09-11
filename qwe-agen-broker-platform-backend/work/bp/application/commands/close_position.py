"""
Close Position Command Handler.

This handler closes an open position by:
1. Creating a closing order (opposite side)
2. Recording a deal with entry=OUT
3. Updating position volume to 0
4. Updating account balance with realized PnL
5. Emitting PositionClosed event
"""
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from core.domains.accounts.account import Account
from core.domains.common.value_objects import Money, Price, Volume
from core.domains.oms.entities.deal import Deal
from core.domains.oms.entities.order import Order
from core.domains.oms.entities.position import Position
from core.domains.oms.enums import (
    DealEntry, DealReason, OrderReason, OrderState, OrderType, PositionAction, DealType
)
from core.events.domain_events import PositionClosed
from core.ports.interfaces import (
    IAccountRepository,
    IDealRepository,
    IEventBus,
    IOrderRepository,
    IPositionRepository,
)

logger = logging.getLogger(__name__)


@dataclass
class ClosePositionCommand:
    """Command to close an open position."""
    account_login: int
    position_id: str
    volume: Optional[Decimal] = None  # None = close full position
    price: Optional[Decimal] = None  # None = use current market price
    comment: str = ""
    #: "SL" / "TP" / "SO" when a server-side trigger closed the position (M9);
    #: empty means a client/dealer close. Flows onto the closing deal AND order
    #: reasons, so statements say why the position closed.
    reason: str = ""


class ClosePositionHandler:
    """Handler for ClosePositionCommand."""

    def __init__(
        self,
        account_repo: IAccountRepository,
        position_repo: IPositionRepository,
        order_repo: IOrderRepository,
        deal_repo: IDealRepository,
        event_bus: IEventBus,
        risk_engine=None,
    ):
        self.account_repo = account_repo
        self.position_repo = position_repo
        self.order_repo = order_repo
        self.deal_repo = deal_repo
        self.event_bus = event_bus
        # Optional since M6: with an engine, the realised result is converted
        # quote->deposit (a USDJPY close used to add a raw JPY amount to a USD
        # balance). Without one, the legacy same-currency maths is kept and a
        # warning is logged, because the alternative - refusing - would break
        # single-currency setups that never needed conversion.
        self.risk_engine = risk_engine

    async def handle(self, command: ClosePositionCommand) -> Position:
        """Execute the close position command."""
        # 1. Fetch position
        position = await self.position_repo.find_by_id(command.position_id)
        if not position:
            raise ValueError(f"Position {command.position_id} not found")

        if position.account_login != command.account_login:
            raise ValueError(f"Position does not belong to account {command.account_login}")

        if position.time_done is not None:
            raise ValueError(f"Position {command.position_id} is already closed")

        # 2. Determine close volume
        close_volume = command.volume if command.volume else position.volume.value
        if close_volume > position.volume.value:
            raise ValueError(f"Close volume {close_volume} exceeds position volume {position.volume.value}")

        # 3. Determine closing side (opposite of position)
        if position.action == PositionAction.BUY:
            close_side = "SELL"
            deal_type = DealType.SELL
        else:
            close_side = "BUY"
            deal_type = DealType.BUY

        # 4. Get current price (or use provided price)
        # In production, fetch from market data feed
        current_price = command.price if command.price else position.price_current.value

        # 5. Create closing order
        reason_name = (command.reason or "").upper()
        deal_reason = (
            DealReason[reason_name] if reason_name in DealReason.__members__ else DealReason.CLIENT
        )
        order_reason = (
            OrderReason[reason_name] if reason_name in OrderReason.__members__ else OrderReason.CLIENT
        )
        closing_order = Order(
            account_login=command.account_login,
            symbol=position.symbol,
            order_type=OrderType[close_side],
            volume_initial=Volume(close_volume),
            volume_current=Volume(close_volume),
            price_order=Price(current_price),
            state=OrderState.FILLED,
            reason=order_reason,
            comment=f"[CLOSE] {command.comment}".strip(),
        )
        await self.order_repo.save(closing_order)

        # 6. Calculate realized PnL
        account_for_pnl = await self.account_repo.find_by_login(command.account_login)
        if self.risk_engine is not None and account_for_pnl is not None:
            # Converted, side-correct, single source of truth (margin.position_pnl).
            realized_pnl = self.risk_engine.realized_pnl(
                account_for_pnl, position, current_price, close_volume
            )
            realized_pnl_money = Money(realized_pnl, account_for_pnl.currency)
        else:
            if self.risk_engine is None:
                logger.warning(
                    "ClosePositionHandler has no risk_engine: realised PnL is NOT "
                    "currency-converted (correct only when quote == account currency)"
                )
            if position.action == PositionAction.BUY:
                price_diff = current_price - position.price_open.value
            else:
                price_diff = position.price_open.value - current_price
            realized_pnl = price_diff * close_volume * position.contract_size
            realized_pnl_money = Money(realized_pnl, position.profit.currency)

        # 7. Create closing deal
        closing_deal = Deal(
            order_id=closing_order.ticket_id,
            position_id=position.position_id,
            account_login=command.account_login,
            symbol=position.symbol,
            deal_type=deal_type,
            entry=DealEntry.OUT,
            reason=deal_reason,
            volume=Volume(close_volume),
            price=Price(current_price),
            profit=realized_pnl_money,
            swap=position.swap,
            commission=position.commission,
            comment=closing_order.comment,
        )
        await self.deal_repo.save(closing_deal)

        # 8. Update position
        position.volume = Volume(position.volume.value - close_volume)
        if position.volume.value == Decimal('0'):
            position.time_done = datetime.now(timezone.utc)
            position.deal_close = closing_deal.deal_id
        await self.position_repo.save(position)

        # 9. Update account balance with realized PnL
        account = account_for_pnl
        if account:
            account.balance = Money(account.balance.amount + realized_pnl, account.currency)
            account.equity = Money(account.balance.amount + account.profit.amount, account.currency)
            await self.account_repo.save(account)

        # 10. Emit PositionClosed event
        event = PositionClosed(
            aggregate_id=position.position_id,
            payload={
                "position_id": position.position_id,
                "account_login": command.account_login,
                "symbol": position.symbol,
                "volume_closed": str(close_volume),
                "close_price": str(current_price),
                "realized_pnl": str(realized_pnl),
                "deal_id": closing_deal.deal_id,
            }
        )
        await self.event_bus.publish(event)

        logger.info(f"Position {position.position_id} closed: volume={close_volume}, pnl={realized_pnl}")

        return position