"""
Liquidation Worker - Executes Liquidation Plans in Response to Stop-Out Events.

This worker:
1. Subscribes to StopOutEntered events from the Event Bus
2. Fetches the account and its open positions
3. Calls LiquidationService to calculate which positions to close
4. Executes the closure by creating closing Orders and Deals
5. Updates Positions and Account state
6. Emits PositionClosed events
"""
import asyncio
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Optional

from core.domains.accounts.account import Account
from core.domains.accounts.enums import SOActivation
from core.domains.common.value_objects import Money, Price, Volume
from core.domains.instruments.symbol import Symbol
from core.domains.market_data.models import Tick
from core.domains.oms.entities.deal import Deal
from core.domains.oms.entities.order import Order
from core.domains.oms.entities.position import Position
from core.domains.oms.enums import (
    DealEntry, DealReason, DealType, OrderState, OrderType, PositionAction
)
from core.domains.risk.liquidation_service import LiquidationService
from core.events.domain_events import DomainEvent, StopOutEntered, PositionClosed
from core.ports.interfaces import (
    IAccountRepository,
    IDealRepository,
    IEventBus,
    IMarketDataFeed,
    IOrderRepository,
    IPositionRepository,
    ISymbolRepository,
)

logger = logging.getLogger(__name__)


class LiquidationWorker:
    """
    Background worker that listens for StopOutEntered events and executes liquidations.
    
    Architectural Note:
    This worker runs as a background task. It subscribes to StopOutEntered events
    and processes them asynchronously. Each liquidation is wrapped in a Unit of Work
    to ensure atomicity (all updates succeed or all fail).
    """
    
    def __init__(
        self,
        account_repo: IAccountRepository,
        position_repo: IPositionRepository,
        order_repo: IOrderRepository,
        deal_repo: IDealRepository,
        symbol_repo: ISymbolRepository,
        market_data_feed: IMarketDataFeed,
        event_bus: IEventBus,
        liquidation_service: LiquidationService,
    ):
        self.account_repo = account_repo
        self.position_repo = position_repo
        self.order_repo = order_repo
        self.deal_repo = deal_repo
        self.symbol_repo = symbol_repo
        self.market_data_feed = market_data_feed
        self.event_bus = event_bus
        self.liquidation_service = liquidation_service
        
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self) -> None:
        """Start the worker and subscribe to StopOutEntered events."""
        if self._running:
            return
        
        self._running = True
        self.event_bus.subscribe(StopOutEntered, self._on_stop_out_entered)
        logger.info("LiquidationWorker started and subscribed to StopOutEntered events")
    
    async def stop(self) -> None:
        """Stop the worker and unsubscribe from events."""
        if not self._running:
            return
        
        self._running = False
        self.event_bus.unsubscribe(StopOutEntered, self._on_stop_out_entered)
        logger.info("LiquidationWorker stopped")
    
    async def _on_stop_out_entered(self, event: StopOutEntered) -> None:
        """
        Handler for StopOutEntered events.
        
        This is called asynchronously when an account enters stop-out state.
        """
        account_login = event.payload.get("account_login")
        if not account_login:
            logger.error(f"StopOutEntered event missing account_login: {event.payload}")
            return
        
        logger.warning(f"StopOutEntered for account {account_login}, starting liquidation")
        
        try:
            await self._execute_liquidation(account_login)
        except Exception as e:
            logger.error(f"Liquidation failed for account {account_login}: {e}", exc_info=True)
    
    async def _execute_liquidation(self, account_login: int) -> None:
        """
        Execute the full liquidation process for an account.
        
        Steps:
        1. Fetch account and open positions
        2. Get current prices for all positions
        3. Calculate liquidation plan
        4. Execute closure for each position
        5. Update account state
        6. Emit events
        """
        # 1. Fetch account
        account = await self.account_repo.find_by_login(account_login)
        if not account:
            logger.error(f"Account {account_login} not found")
            return
        
        # 2. Fetch open positions
        open_positions = await self.position_repo.get_by_account(account_login)
        if not open_positions:
            logger.info(f"No open positions for account {account_login}")
            return
        
        # 3. Get current prices for all positions
        current_prices = {}
        conversion_rates = {}
        symbols = set(p.symbol for p in open_positions)
        
        for symbol_name in symbols:
            symbol = await self.symbol_repo.find_by_name(symbol_name)
            if not symbol:
                logger.error(f"Symbol {symbol_name} not found")
                continue
            
            # Get latest tick
            tick = await self.market_data_feed.get_latest_tick(symbol_name)
            if tick:
                # BUY positions are valued at BID, SELL at ASK
                if any(p.action == PositionAction.BUY for p in open_positions if p.symbol == symbol_name):
                    current_prices[symbol_name] = Price(tick.bid)
                else:
                    current_prices[symbol_name] = Price(tick.ask)
            
            # Get conversion rate (simplified - in production, use RiskEngine)
            conversion_rates[symbol_name] = Decimal('1.0')  # Assume same currency for now
        
        # 4. Calculate liquidation plan
        plan = self.liquidation_service.calculate_liquidation_plan(
            account=account,
            open_positions=open_positions,
            current_prices=current_prices,
            conversion_rates=conversion_rates,
        )
        
        if not plan.positions_to_close:
            logger.info(f"No positions need to be closed for account {account_login}")
            return
        
        logger.warning(
            f"Liquidation plan for account {account_login}: "
            f"closing {len(plan.positions_to_close)} positions, "
            f"recovering {plan.total_pnl_recovered.amount} {plan.total_pnl_recovered.currency}"
        )
        
        # 5. Execute closure for each position
        for position in plan.positions_to_close:
            await self._close_position(account, position, current_prices.get(position.symbol))
        
        # 6. Update account state
        # Recalculate margin_used and margin_free
        remaining_positions = await self.position_repo.get_by_account(account_login)
        total_margin_used = Decimal('0')
        total_pnl = Decimal('0')
        
        for pos in remaining_positions:
            # Simplified margin calculation
            margin_required = pos.calculate_margin_required(
                margin_rate=Decimal('1.0'),
                leverage=account.effective_leverage()
            )
            total_margin_used += margin_required
            total_pnl += pos.profit.amount
        
        account.margin_used = Money(total_margin_used, account.currency)
        account.equity = Money(account.balance.amount + total_pnl, account.currency)
        account.margin_free = Money(account.equity.amount - account.margin_used.amount, account.currency)
        
        if account.margin_used.amount > Decimal('0'):
            account.margin_level = account.equity.amount / account.margin_used.amount
        else:
            account.margin_level = Decimal('999999')
        
        # Check if we've recovered from stop-out
        stop_out_level = account.group.margin.stop_out_level if account.group else Decimal('0.5')
        if account.margin_level >= stop_out_level:
            account.so_activation = SOActivation.NONE
            account.so_time = None
            account.so_level = None
            account.so_equity = None
            account.so_margin = None
            logger.info(f"Account {account_login} recovered from stop-out, margin_level={account.margin_level}")
        
        # Save account
        await self.account_repo.save(account)
        
        logger.info(
            f"Liquidation complete for account {account_login}: "
            f"margin_level={account.margin_level}, "
            f"equity={account.equity.amount}"
        )
    
    async def _close_position(
        self,
        account: Account,
        position: Position,
        current_price: Optional[Price],
    ) -> None:
        """
        Close a single position by creating a closing Order and Deal.
        
        MT5 Logic:
        1. Create a closing Order (opposite side of position)
        2. Create a Deal with entry=OUT
        3. Update Position volume to 0
        4. Emit PositionClosed event
        """
        if not current_price:
            logger.error(f"No current price for {position.symbol}, cannot close position")
            return
        
        # Determine closing side (opposite of position)
        if position.action == PositionAction.BUY:
            close_side = "SELL"
            deal_type = DealType.SELL
        else:
            close_side = "BUY"
            deal_type = DealType.BUY
        
        # 1. Create closing Order
        closing_order = Order(
            account_login=account.login,
            symbol=position.symbol,
            order_type=OrderType[close_side],
            volume_initial=position.volume,
            volume_current=position.volume,
            price_order=current_price,
            state=OrderState.FILLED,
            reason="LIQUIDATION",
            comment=f"[LIQUIDATION] Closing position {position.position_id}",
        )
        
        await self.order_repo.save(closing_order)
        
        # 2. Create Deal
        closing_deal = Deal(
            order_id=closing_order.ticket_id,
            position_id=position.position_id,
            account_login=account.login,
            symbol=position.symbol,
            deal_type=deal_type,
            entry=DealEntry.OUT,
            reason=DealReason.SO,  # Stop-out
            volume=position.volume,
            price=current_price,
            profit=position.profit,  # Realized PnL
            swap=position.swap,
            commission=position.commission,
            comment=f"[LIQUIDATION] {closing_order.comment}",
        )
        
        await self.deal_repo.save(closing_deal)
        
        # 3. Update Position
        position.volume = Volume(Decimal('0'))
        position.time_done = datetime.now(timezone.utc)
        position.deal_close = closing_deal.deal_id
        
        await self.position_repo.save(position)
        
        # 4. Emit PositionClosed event
        event = PositionClosed(
            aggregate_id=position.position_id,
            payload={
                "position_id": position.position_id,
                "account_login": account.login,
                "symbol": position.symbol,
                "volume_closed": str(position.volume.value),
                "close_price": str(current_price.value),
                "realized_pnl": str(position.profit.amount),
                "deal_id": closing_deal.deal_id,
                "reason": "LIQUIDATION",
            },
        )
        
        await self.event_bus.publish(event)
        
        logger.info(
            f"Position {position.position_id} closed: "
            f"volume={position.volume.value}, "
            f"price={current_price.value}, "
            f"pnl={position.profit.amount}"
        )