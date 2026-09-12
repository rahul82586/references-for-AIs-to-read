"""
Liquidation Service - MT5-Accurate Position Selection & Closure Logic.

This service implements the institutional-grade liquidation algorithm:
1. Fetch all open positions for the account
2. Sort by worst floating loss first (MT5 standard)
3. Close positions one by one until margin_level recovers above stop_out_level
4. Return the list of positions to close (caller executes the actual closure)
"""
from decimal import Decimal
from typing import List, Optional
from dataclasses import dataclass

from core.domains.accounts.account import Account
from core.domains.oms.entities.position import Position
from core.domains.common.value_objects import Money, Price


@dataclass
class LiquidationPlan:
    """
    Plan of positions to close to recover margin.
    
    This is a PURE DATA STRUCTURE. It does not execute anything.
    The caller (LiquidationWorker) is responsible for execution.
    """
    account_login: int
    positions_to_close: List[Position]
    total_pnl_recovered: Money
    projected_margin_level_after: Decimal
    is_fully_liquidated: bool  # True if all positions were closed


class LiquidationService:
    """
    Pure domain logic for liquidation planning.
    
    Architectural Note:
    This service does NOT execute trades. It only calculates WHICH positions
    to close and in what order. The actual execution (creating Orders, Deals)
    is handled by the LiquidationWorker in the application layer.
    """
    
    def calculate_liquidation_plan(
        self,
        account: Account,
        open_positions: List[Position],
        current_prices: dict[str, Price],  # symbol -> current_price
        conversion_rates: dict[str, Decimal],  # symbol -> conversion_rate
    ) -> LiquidationPlan:
        """
        Calculate which positions to close to recover margin.
        
        MT5 Liquidation Algorithm:
        1. Sort positions by worst floating loss first
        2. Close positions one by one until margin_level >= stop_out_level
        3. If all positions closed and still below stop_out, mark as fully_liquidated
        
        Args:
            account: Account with current balance, margin_used, etc.
            open_positions: All open positions for this account
            current_prices: Current market prices for each symbol
            conversion_rates: Currency conversion rates for each symbol
            
        Returns:
            LiquidationPlan with positions to close and projected margin level
        """
        if not open_positions:
            return LiquidationPlan(
                account_login=account.login,
                positions_to_close=[],
                total_pnl_recovered=Money(Decimal('0'), account.currency),
                projected_margin_level_after=Decimal('0'),
                is_fully_liquidated=False,
            )
        
        # 1. Update PnL for all positions using current prices
        positions_with_pnl = []
        for position in open_positions:
            current_price = current_prices.get(position.symbol)
            conversion_rate = conversion_rates.get(position.symbol, Decimal('1.0'))
            
            if current_price:
                # Calculate unrealized PnL
                pnl = position.update_unrealized_pnl(current_price, conversion_rate)
                positions_with_pnl.append((position, pnl))
            else:
                # If no price available, use existing PnL
                positions_with_pnl.append((position, position.profit))
        
        # 2. Sort by worst loss first (most negative PnL first)
        # MT5 standard: close the positions that are losing the most
        positions_with_pnl.sort(key=lambda x: x[1].amount)
        
        # 3. Simulate closing positions until margin recovers
        # Percent fallback, matching MarginProfile's default.
        stop_out_level = account.group.margin.stop_out_level if account.group else Decimal('50')
        
        positions_to_close = []
        total_pnl_recovered = Decimal('0')
        
        # Total floating PnL across all positions
        total_floating_pnl = sum(pnl.amount for _, pnl in positions_with_pnl)
        current_equity = account.balance.amount + total_floating_pnl
        projected_margin_used = account.margin_used.amount
        
        for position, pnl in positions_with_pnl:
            # Check if current margin level is above stop_out
            if projected_margin_used > Decimal('0'):
                projected_margin_level = (current_equity / projected_margin_used) * Decimal('100')
            else:
                projected_margin_level = Decimal('999999')
            
            # If margin level is above stop_out, we're done
            if projected_margin_level >= stop_out_level:
                break
            
            # Close this position
            positions_to_close.append(position)
            total_pnl_recovered += pnl.amount
            margin_freed = position.calculate_margin_required(
                margin_rate=Decimal('1.0'),
                leverage=account.effective_leverage()
            )
            projected_margin_used = max(Decimal('0'), projected_margin_used - margin_freed)
        
        # Calculate final projected margin level
        if projected_margin_used > Decimal('0'):
            final_margin_level = (current_equity / projected_margin_used) * Decimal('100')
        else:
            final_margin_level = Decimal('999999')
        
        is_fully_liquidated = len(positions_to_close) == len(open_positions)
        
        return LiquidationPlan(
            account_login=account.login,
            positions_to_close=positions_to_close,
            total_pnl_recovered=Money(total_pnl_recovered, account.currency),
            projected_margin_level_after=final_margin_level,
            is_fully_liquidated=is_fully_liquidated,
        )
