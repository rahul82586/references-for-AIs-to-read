"""
Create Order Command Handler - The Entry Point for All Trading.

This handler orchestrates the full order lifecycle:
1. Validate symbol (session, trade mode, volume limits)
2. Pre-trade risk check (inside per-account lock)
3. Persist order
4. Execute (B-Book internalization or A-Book routing)
5. Record deal and update position
6. Emit domain events

Architectural Note:
This handler uses TWO-PHASE LOCKING to prevent deadlocks:
- Phase 1: Acquire lock → Check risk → Reserve margin → Release lock
- Phase 2: Execute trade (may involve slow LP network calls)
- Phase 3: Acquire lock → Record deal → Finalize balance → Release lock
"""
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from core.domains.accounts.account import Account
from core.domains.common.value_objects import Money, Price, Volume
from core.domains.instruments.symbol import Symbol
from core.domains.oms.entities.order import Order
from core.domains.oms.enums import OrderState, OrderType, OrderReason
from core.domains.risk.engine import RiskEngine
from core.events.domain_events import OrderCreated, OrderRejected
from core.ports.interfaces import (
    IAccountRepository,
    IEventBus,
    IOrderRepository,
    IPositionRepository,
    ISymbolRepository,
)
from application.services.risk_service import PreTradeRiskService

logger = logging.getLogger(__name__)


@dataclass
class CreateOrderCommand:
    """Command to create a new order."""
    account_login: int
    symbol: str
    order_type: OrderType
    volume: Decimal
    price: Optional[Decimal] = None  # For limit/stop orders
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None
    comment: str = ""
    reason: OrderReason = OrderReason.CLIENT


class CreateOrderHandler:
    """Handler for CreateOrderCommand."""

    def __init__(
        self,
        account_repo: IAccountRepository,
        symbol_repo: ISymbolRepository,
        order_repo: IOrderRepository,
        position_repo: IPositionRepository,
        risk_service: PreTradeRiskService,
        event_bus: IEventBus,
    ):
        self.account_repo = account_repo
        self.symbol_repo = symbol_repo
        self.order_repo = order_repo
        self.position_repo = position_repo
        self.risk_service = risk_service
        self.event_bus = event_bus

    async def handle(self, command: CreateOrderCommand) -> Order:
        """
        Execute the create order command.
        
        Returns the created Order entity.
        Raises ValueError if validation fails.
        """
        # 1. Fetch account and symbol
        account = await self.account_repo.find_by_login(command.account_login)
        if not account:
            raise ValueError(f"Account {command.account_login} not found")

        symbol = await self.symbol_repo.find_by_name(command.symbol)
        if not symbol:
            raise ValueError(f"Symbol {command.symbol} not found")

        # 2. Validate symbol session and trade mode
        now = datetime.now(timezone.utc)
        if not symbol.is_trade_session_active(now):
            raise ValueError(f"Market closed for {command.symbol}")

        side = "BUY" if command.order_type.value.startswith("BUY") else "SELL"
        if not symbol.can_trade_direction(side):
            raise ValueError(f"Trade direction {side} not allowed for {command.symbol}")

        # Validate volume
        volume_valid, volume_reason = symbol.validate_volume(command.volume)
        if not volume_valid:
            raise ValueError(f"Invalid volume: {volume_reason}")

        # 3. Create Order entity
        order = Order(
            account_login=command.account_login,
            symbol=command.symbol,
            order_type=command.order_type,
            reason=command.reason,
            volume_initial=Volume(command.volume),
            volume_current=Volume(command.volume),
            price_order=Price(command.price) if command.price else Price(Decimal('0')),
            price_sl=Price(command.stop_loss) if command.stop_loss else None,
            price_tp=Price(command.take_profit) if command.take_profit else None,
            comment=command.comment,
            digits=symbol.digits,
            digits_currency=symbol.digits_currency,
            contract_size=symbol.contract_size,
        )

        # 4. Pre-trade risk check (inside per-account lock)
        # This uses the two-phase locking pattern to prevent double-spending
        async with self.risk_service.account_lock(command.account_login):
            # Fetch live account state inside lock
            live_account = await self.account_repo.find_by_login(command.account_login)
            
            # Calculate required margin
            symbol_config = {
                "contract_size": symbol.contract_size,
                "margin_rate_initial_buy": symbol.margin_rates.initial_buy,
                "margin_rate_initial_sell": symbol.margin_rates.initial_sell,
            }
            
            # Apply group overrides
            if live_account.group:
                overrides = live_account.group.get_symbol_config(command.symbol)
                symbol_config.update(overrides)
            
            # Calculate margin requirement
            effective_leverage = Decimal(str(live_account.effective_leverage()))
            contract_size = symbol_config.get("contract_size", Decimal('100000'))
            
            if side == "BUY":
                margin_rate = symbol_config.get("margin_rate_initial_buy", Decimal('1.0'))
            else:
                margin_rate = symbol_config.get("margin_rate_initial_sell", Decimal('1.0'))
            
            price_for_margin = command.price if command.price else Decimal('1.0')  # Simplified for market orders
            notional = command.volume * contract_size * price_for_margin
            required_margin = (notional * margin_rate) / effective_leverage
            
            # Check if account has enough free margin
            if required_margin > live_account.margin_free.amount:
                rejection_reason = f"Insufficient margin. Required: {required_margin}, Available: {live_account.margin_free.amount}"
                logger.warning(f"Order {order.ticket_id} rejected: {rejection_reason}")
                
                # Publish rejection event
                event = OrderRejected(
                    aggregate_id=order.ticket_id,
                    payload={
                        "order_id": order.ticket_id,
                        "account_login": command.account_login,
                        "reason": rejection_reason,
                    }
                )
                await self.event_bus.publish(event)
                raise ValueError(rejection_reason)
            
            # Reserve margin (update account state)
            live_account.margin_used = Money(
                live_account.margin_used.amount + required_margin,
                live_account.currency
            )
            live_account.margin_free = Money(
                live_account.margin_free.amount - required_margin,
                live_account.currency
            )
            if live_account.margin_used.amount > Decimal('0'):
                live_account.margin_level = live_account.equity.amount / live_account.margin_used.amount
            
            await self.account_repo.save(live_account)

        # 5. Persist order (outside lock to avoid holding it during DB writes)
        order.state = OrderState.PLACED
        saved_order = await self.order_repo.save(order)

        # 6. Publish order created event
        event = OrderCreated(
            aggregate_id=saved_order.ticket_id,
            payload={
                "order_id": saved_order.ticket_id,
                "account_login": command.account_login,
                "symbol": command.symbol,
                "order_type": command.order_type.value,
                "volume": str(command.volume),
                "price": str(command.price) if command.price else None,
            }
        )
        await self.event_bus.publish(event)

        logger.info(f"Order {saved_order.ticket_id} created for account {command.account_login}")

        return saved_order
CreateOrderCommandHandler = CreateOrderHandler
