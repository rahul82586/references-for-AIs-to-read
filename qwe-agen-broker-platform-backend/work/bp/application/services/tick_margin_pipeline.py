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
from core.domains.common.value_objects import Money, Price, Volume
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
        #: D15 - whether the full-row fallback warning has already been logged
        self._warned_full_row_save = False

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
        #
        # D13: these are the objects that hold the new numbers, so step 5 must use
        # them rather than the fresh copies its own read returns - a SQL repository
        # builds a new Position per fetch, so the second read came back with profit 0
        # and price_current NULL and the PnL computed here was silently dropped.
        repriced: Dict[str, Position] = {}
        #: set when the repository has no column-scoped write, so step 5 must persist
        legacy_write = False
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

            # D15: write the revaluation with a column-scoped statement instead of
            # a full-row save. The pipeline is holding an object it fetched before
            # it did any work, so `save()` races everything else that moves a
            # position - measured live as a partial close being undone by the next
            # tick, after which the following close dealt the ORIGINAL volume. The
            # statement computes profit from the volume the row holds at write time
            # and skips closed positions, and it hands back what it wrote, so the
            # in-memory object below carries the row's truth and not this pass's
            # stale snapshot.
            _update_valuation = getattr(self.position_repo, "update_valuation", None)
            if _update_valuation is not None:
                try:
                    written = await _update_valuation(
                        position.position_id, position.action.value, current_price_decimal)
                except Exception as exc:  # noqa: BLE001
                    logger.error(
                        "could not revalue position %s: %s - keeping the stored figures "
                        "rather than writing a guess", position.position_id, exc,
                    )
                    continue
                if written is None:
                    # closed or gone between this pass's read and its write. Dropping
                    # it is the point: keeping it would put a closed position's PnL
                    # back into its account's equity.
                    logger.debug(
                        "position %s was closed while a tick was revaluing it; skipped",
                        position.position_id,
                    )
                    continue
                position.volume = Volume(written["volume"])
                position.profit = Money(written["profit"], position.profit.currency)
                position.price_current = price_obj
                repriced[position.position_id] = position
                continue

            position.update_unrealized_pnl(price_obj, conversion_rate)
            repriced[position.position_id] = position
            legacy_write = True

        # 4b. What step 4 repriced, by id, for step 5 to overlay onto its own read.
        #
        # D13: step 5 fetches this account's positions AGAIN, and a SQL repository
        # builds a NEW Position per fetch (db_to_position(model)), so that second
        # read came back with the values still in the database - profit 0,
        # price_current NULL. Equity was summed from those, they were what got
        # saved, and the PnL step 4 had just computed was dropped on the floor.
        # Every test missed it because the mock repository handed back the SAME
        # objects from both fetches; the double was more coherent than the database.
        #
        # The overlay is what makes the two reads agree: positions of THIS symbol
        # come from the repriced objects, every other symbol comes from the fresh
        # read (and keeps the PnL its own last tick gave it). One fetch, one save,
        # no double write. Under D15 the dict is filled as each write lands, so it
        # holds what the DATABASE says - which after a concurrent partial close is
        # not what this pass computed.

        # 5. Update Account Equity and Evaluate Margin State
        for login, account in accounts.items():
            # Get ALL positions for this account (not just the current symbol),
            # then replace the ones this tick repriced with the objects that hold
            # the new numbers.
            fetched = await self.position_repo.get_by_account(login)
            seen = {x.position_id for x in fetched}
            all_positions = [repriced.get(x.position_id, x) for x in fetched]
            # A position this tick repriced that the account read did not return
            # (it closed between the two fetches) is not resurrected: it is no
            # longer part of this account's open exposure.
            all_positions.extend(
                p for pid, p in repriced.items()
                if p.account_login == login and pid not in seen and p.time_done is None
            )

            # Calculate total unrealized PnL in account currency
            # (Position.profit is already converted to account currency by update_unrealized_pnl)
            total_pnl_amount = sum(p.profit.amount for p in all_positions)
            total_pnl_money = Money(total_pnl_amount, account.currency)
            
            # Update equity and free margin based on Group's FreeMarginMode
            account.update_equity(total_pnl_money)
            
            # Evaluate the Stop-Out state machine
            # Returns a list of event dicts if state transitions occurred
            state_events = account.evaluate_margin_state()
            
            # Persist updates.
            #
            # D8b: NOT a full-row save. This pass loaded `account` before it did
            # its work, so a fill that landed in between would be overwritten by
            # the stale margin_used - observed live as margin_used=0 on an account
            # holding an open position, which also freezes margin_level at the
            # 999999 sentinel and makes stop-out unreachable. update_valuation
            # writes only the columns this pipeline owns and recomputes here.
            _update_valuation = getattr(self.account_repo, "update_valuation", None)
            _rows = await _update_valuation(account) if _update_valuation is not None else None
            if _rows is None:
                # A repository without the column-scoped write (it returned None).
                # Loud, because the fallback is the racy one and an operator should
                # know they are on it - but not fatal, so a custom repo still boots.
                logger.warning(
                    "account_repo %s has no update_valuation(); falling back to a "
                    "full-row save, which can lose a concurrent fill's margin",
                    type(self.account_repo).__name__,
                )
                await self.account_repo.save(account)
            if legacy_write:
                # No column-scoped write available (a custom or in-memory repo), so
                # the repriced objects have not been persisted yet. This is the racy
                # path - say so once rather than on every tick of every symbol.
                if not self._warned_full_row_save:
                    self._warned_full_row_save = True
                    logger.warning(
                        "position_repo %s has no update_valuation(); falling back to a "
                        "full-row save per tick, which can undo a concurrent close's "
                        "volume (D15)", type(self.position_repo).__name__,
                    )
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