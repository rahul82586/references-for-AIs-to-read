"""Account entity - Trading state & financials (IMTAccount)."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

from core.domains.common.value_objects import Money
from .enums import AccountType, SOActivation, FreeMarginMode
from .value_objects import StopOutSnapshot
from .group import Group


@dataclass
class Account:
    """
    Account Entity - Trading State & Financials (IMTAccount)
    
    Represents a trading account linked to a Client and Group.
    """
    # Identity
    login: int = 0
    client_id: str = ""
    group_id: str = ""
    group: Optional[Group] = None
    
    # Type
    account_type: AccountType = AccountType.REAL
    currency: str = "USD"
    currency_digits: int = 2
    
    # Leverage (can override Group's leverage)
    leverage: Optional[int] = None
    
    # Financial state (Money value objects)
    balance: Money = field(default_factory=lambda: Money(Decimal('0'), "USD"))
    credit: Money = field(default_factory=lambda: Money(Decimal('0'), "USD"))
    equity: Money = field(default_factory=lambda: Money(Decimal('0'), "USD"))
    margin_used: Money = field(default_factory=lambda: Money(Decimal('0'), "USD"))
    margin_free: Money = field(default_factory=lambda: Money(Decimal('0'), "USD"))
    margin_level: Decimal = field(default_factory=lambda: Decimal('0'))
    
    # Floating values
    profit: Money = field(default_factory=lambda: Money(Decimal('0'), "USD"))
    storage: Money = field(default_factory=lambda: Money(Decimal('0'), "USD"))
    commission: Money = field(default_factory=lambda: Money(Decimal('0'), "USD"))
    
    # Stop-out state machine
    so_activation: SOActivation = SOActivation.NONE
    so_time: Optional[datetime] = None
    so_level: Optional[Decimal] = None
    so_equity: Optional[Money] = None
    so_margin: Optional[Money] = None
    
    # Flags
    is_enabled: bool = True
    is_online: bool = False
    last_login: Optional[datetime] = None
    
    # UI
    color_tag: Optional[str] = None
    dealer_notes: str = ""
    
    # Dates
    registration_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def effective_leverage(self) -> int:
        """Get effective leverage (Account > Group > Default)."""
        if self.leverage is not None and self.leverage > 0:
            return self.leverage
        if self.group and self.group.margin.leverage_default > 0:
            return self.group.margin.leverage_default
        return 100
    
    def update_equity(self, unrealized_pnl: Money) -> None:
        """Update equity based on unrealized P&L."""
        self.profit = unrealized_pnl
        self.equity = Money(
            self.balance.amount + self.credit.amount + unrealized_pnl.amount,
            self.currency
        )
        
        # Update free margin based on Group's free_margin_mode
        if self.group:
            mode = self.group.margin.free_margin_mode
            if mode == FreeMarginMode.USE_PL:
                self.margin_free = Money(
                    self.equity.amount - self.margin_used.amount,
                    self.currency
                )
            elif mode == FreeMarginMode.NOT_USE_PL:
                self.margin_free = Money(
                    self.balance.amount + self.credit.amount - self.margin_used.amount,
                    self.currency
                )
            elif mode == FreeMarginMode.PROFIT:
                pnl_amount = max(unrealized_pnl.amount, Decimal('0'))
                self.margin_free = Money(
                    self.balance.amount + self.credit.amount + pnl_amount - self.margin_used.amount,
                    self.currency
                )
            elif mode == FreeMarginMode.LOSS:
                loss_amount = min(unrealized_pnl.amount, Decimal('0'))
                self.margin_free = Money(
                    self.balance.amount + self.credit.amount + loss_amount - self.margin_used.amount,
                    self.currency
                )
        else:
            self.margin_free = Money(
                self.equity.amount - self.margin_used.amount,
                self.currency
            )
        
        # Update margin level
        if self.margin_used.amount > Decimal('0'):
            self.margin_level = self.equity.amount / self.margin_used.amount
        else:
            self.margin_level = Decimal('0')
    
    def evaluate_margin_state(self) -> List[Dict[str, Any]]:
        """
        Evaluate margin state and return list of events to emit.
        Implements the MT5 Stop-Out state machine.
        """
        events = []
        
        if not self.group:
            return events
        
        margin_call_level = self.group.margin.margin_call_level
        stop_out_level = self.group.margin.stop_out_level
        
        # Check if we should enter margin call
        if self.so_activation == SOActivation.NONE:
            if self.margin_level < margin_call_level:
                self.so_activation = SOActivation.MARGIN_CALL
                events.append({
                    "event_type": "MarginCallEntered",
                    "account_login": self.login,
                    "margin_level": str(self.margin_level),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
        
        # Check if we should exit margin call
        elif self.so_activation == SOActivation.MARGIN_CALL:
            if self.margin_level >= margin_call_level:
                self.so_activation = SOActivation.NONE
                events.append({
                    "event_type": "MarginCallExited",
                    "account_login": self.login,
                    "margin_level": str(self.margin_level),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            
            # Check if we should enter stop-out
            elif self.margin_level < stop_out_level:
                self.so_activation = SOActivation.STOP_OUT
                self.so_time = datetime.now(timezone.utc)
                self.so_level = self.margin_level
                self.so_equity = self.equity
                self.so_margin = self.margin_used
                
                events.append({
                    "event_type": "StopOutEntered",
                    "account_login": self.login,
                    "margin_level": str(self.margin_level),
                    "equity": str(self.equity.amount),
                    "margin": str(self.margin_used.amount),
                    "timestamp": self.so_time.isoformat()
                })
        
        # Check if we should exit stop-out
        elif self.so_activation == SOActivation.STOP_OUT:
            if self.margin_level >= stop_out_level:
                self.so_activation = SOActivation.NONE
                events.append({
                    "event_type": "StopOutExited",
                    "account_login": self.login,
                    "margin_level": str(self.margin_level),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
        
        return events
    
    def can_trade(self) -> bool:
        """Check if account is enabled and group allows trading."""
        if not self.is_enabled:
            return False
        if self.group and not self.group.can_trade():
            return False
        return True
    
    def can_open_position(
        self,
        symbol: str,
        volume: Decimal,
        required_margin: Money
    ) -> tuple:
        """Check if account can open a position."""
        if not self.is_enabled:
            return False, "Account is disabled"
        
        if not self.group:
            return False, "No group assigned"
        
        if not self.group.can_trade():
            return False, "Trading not allowed for this account"
        
        if not self.group.is_symbol_allowed(symbol):
            return False, f"Symbol {symbol} not allowed for this account"
        
        if required_margin.amount > self.margin_free.amount:
            return False, "Insufficient free margin"
        
        return True, "OK"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert account to dictionary."""
        return {
            "login": self.login,
            "client_id": self.client_id,
            "group_id": self.group_id,
            "group_name": self.group.name if self.group else None,
            "account_type": self.account_type.value,
            "currency": self.currency,
            "currency_digits": self.currency_digits,
            "leverage": self.effective_leverage(),
            "balance": str(self.balance.amount),
            "credit": str(self.credit.amount),
            "equity": str(self.equity.amount),
            "margin_used": str(self.margin_used.amount),
            "margin_free": str(self.margin_free.amount),
            "margin_level": str(self.margin_level),
            "profit": str(self.profit.amount),
            "storage": str(self.storage.amount),
            "commission": str(self.commission.amount),
            "so_activation": self.so_activation.name,
            "so_time": self.so_time.isoformat() if self.so_time else None,
            "so_level": str(self.so_level) if self.so_level else None,
            "is_enabled": self.is_enabled,
            "is_online": self.is_online,
            "color_tag": self.color_tag,
            "dealer_notes": self.dealer_notes,
            "registration_date": self.registration_date.isoformat(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }