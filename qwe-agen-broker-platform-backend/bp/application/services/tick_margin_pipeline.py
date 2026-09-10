"""
Tick & Margin Pipeline - The Heartbeat of the Broker.

Orchestrates the critical path:
Tick -> Position PnL Update -> Account Equity Recalculation -> Margin State Evaluation.

Mirrors MT5's IMTTickSink -> IMTAccountSink flow.
"""
import logging
from decimal import Decimal
from typing import Dict, List, Set
from datetime import datetime, timezone

from core.domains.market_data.models import Tick
from core.domains.accounts.account import Account
from core.domains.oms.entities.position import Position
from core.domains.common.value_objects import Money, Price
from core.ports.interfaces import (
    IPositionRepository, IAccountRepository, ISymbolRepository, 
    IMarketDataFeed, IEventBus
)
from core.domains.risk.engine import RiskEngine
from core.domains.risk.engine import CurrencyConversionError
from core.events.domain_events import (
    MarginCallEntered, MarginCallExited, 
    StopOutEntered, StopOutExited
)

logger = logging.getLogger(__name__)


class TickMarginPipeline:
    """
    Architectural Note:
    In a high-performance production system (10k+ TPS), this pipeline should NOT 
    hit the database on every tick. The `position_repo` and `account_repo` should 
    be backed by an in-memory cache (e.g., Redis or native Python dicts) that is 
    synchronized with the database asynchronously.
    """
    
    def __init__(
        self,
        position_repo: IPositionRepository,
        account_repo: IAccountRepository,
        symbol_repo: ISymbolRepository,
        risk_engine: RiskEngine,
        event_bus: IEventBus
    ):
        self.position_repo = position_repo
        self.account_repo = account_repo
        self.symbol_repo = symbol_repo
        self.risk_engine = risk_engine
        self.event_bus = event_bus

    async def process_tick(self, tick: Tick) -> None:
        """
        Main entry point. Called when a new Tick arrives.
        """
        symbol_name = tick.symbol
        
        # 1. Fetch all open positions for this symbol
        positions = await self.position_repo.get_by_symbol(symbol_name)
        if not positions:
            return  # No open positions, skip processing
            
        # 2. Fetch symbol info for currency conversion
        symbol = await self.symbol_repo.find_by_name(symbol_name)
        if not symbol:
            logger.error(f"Symbol {symbol_name} not found for tick processing")
            return
            
        # 3. Fetch all affected accounts (to get their currency and current state)
        account_logins = list(set(p.account_login for p in positions))
        accounts: Dict[int, Account] = {}
        for login in account_logins:
            acc = await self.account_repo.find_by_login(login)
            if acc:
                accounts[login] = acc
                
        # 4. Update PnL for each position
        for position in positions:
            account = accounts.get(position.account_login)
            if not account:
                continue
                
            # Get conversion rate from quote_currency to account_currency
            try:
                conversion_rate = self.risk_engine.get_conversion_rate(
                    symbol.quote_currency, 
                    account.currency,
                    market_feed=self.risk_engine.market_data_engine
                )
            except CurrencyConversionError as e:
                logger.error(f"Cannot calculate PnL for position {position.position_id}: {e}")
                continue  # Skip this position, keep old PnL rather than crashing
            
            # MT5 PnL Valuation Rule:
            # BUY positions are valued at BID (what we can sell at to close)
            # SELL positions are valued at ASK (what we can buy back at to close)
            if position.action.value == "BUY":
                current_price_decimal = tick.bid
            else:
                current_price_decimal = tick.ask
                
            price_obj = Price(current_price_decimal)
            position.update_unrealized_pnl(price_obj, conversion_rate)
            
        # 5. Update Account Equity and Evaluate Margin State
        for login, account in accounts.items():
            # Get ALL positions for this account (not just the current symbol)
            all_positions = await self.position_repo.get_by_account(login)
            
            # Calculate total unrealized PnL in account currency
            # (Position.profit is already converted to account currency by update_unrealized_pnl)
            total_pnl_amount = sum(p.profit.amount for p in all_positions)
            total_pnl_money = Money(total_pnl_amount, account.currency)
            
            # Update equity and free margin based on Group's FreeMarginMode
            account.update_equity(total_pnl_money)
            
            # Evaluate the Stop-Out state machine
            # Returns a list of event dicts if state transitions occurred
            state_events = account.evaluate_margin_state()
            
            # Persist updates
            await self.account_repo.save(account)
            for p in all_positions:
                await self.position_repo.save(p)
                
            # Emit domain events for UI/Notifications/Risk Workers
            for evt_dict in state_events:
                await self._emit_margin_event(evt_dict, account)

    async def _emit_margin_event(self, evt_dict: dict, account: Account) -> None:
        """Converts state machine dict to Domain Event and publishes."""
        event_type = evt_dict.get("event_type")
        
        # Map string event types to actual Domain Event classes
        event_map = {
            "MarginCallEntered": MarginCallEntered,
            "MarginCallExited": MarginCallExited,
            "StopOutEntered": StopOutEntered,
            "StopOutExited": StopOutExited,
        }
        
        event_class = event_map.get(event_type)
        if event_class:
            event = event_class(
                aggregate_id=str(account.login),
                payload=evt_dict
            )
            await self.event_bus.publish(event)
            logger.warning(
                f"Margin State Change: {event_type} for Account {account.login} | "
                f"Level: {evt_dict.get('margin_level')}"
            )