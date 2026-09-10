"""Group entity - The MT5 Rule Engine."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional
import uuid

from .enums import AccountType, TradeFlags, NewsMode
from .value_objects import (
    MarginProfile, CommissionRule, SwapConfiguration,
    GroupSymbolOverride, RoutingRule, GroupPermissions
)


@dataclass
class Group:
    """
    Group Entity - The MT5 Rule Engine
    
    Controls ALL aspects of accounts assigned to it.
    """
    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    server_id: int = 0
    account_type: AccountType = AccountType.REAL
    currency: str = "USD"
    
    # Margin & Leverage
    margin: MarginProfile = field(default_factory=MarginProfile)
    
    # Commissions
    commissions: List[CommissionRule] = field(default_factory=list)
    
    # Per-symbol overrides
    symbol_overrides: List[GroupSymbolOverride] = field(default_factory=list)
    
    # Trade permissions (bitwise flags)
    trade_flags: TradeFlags = field(
        default_factory=lambda: (
            TradeFlags.SWAPS |
            TradeFlags.TRAILING |
            TradeFlags.EXPERTS |
            TradeFlags.EXPIRATION
        )
    )
    
    # Limits
    limit_orders: int = 200
    limit_positions: int = 200
    limit_symbols: int = 100
    
    # Routing
    routing: RoutingRule = field(default_factory=RoutingRule)
    
    # Permissions
    permissions: GroupPermissions = field(default_factory=GroupPermissions)
    
    # Swaps
    swaps: SwapConfiguration = field(default_factory=SwapConfiguration)
    
    # Advanced features
    news_mode: NewsMode = NewsMode.FULL
    
    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True
    
    def get_symbol_config(self, symbol_name: str) -> Dict[str, Any]:
        """Get effective symbol configuration for this Group."""
        config = {}
        for override in self.symbol_overrides:
            if self._matches_symbol_pattern(symbol_name, override.symbol_pattern):
                if override.trade_mode is not None:
                    config['trade_mode'] = override.trade_mode
                if override.execution_mode is not None:
                    config['execution_mode'] = override.execution_mode
                if override.volume_min is not None:
                    config['volume_min'] = override.volume_min
                if override.volume_max is not None:
                    config['volume_max'] = override.volume_max
                if override.volume_limit is not None:
                    config['volume_limit'] = override.volume_limit
                if override.spread_diff is not None:
                    config['spread_diff'] = override.spread_diff
                if override.margin_rate_initial_buy is not None:
                    config['margin_rate_initial_buy'] = override.margin_rate_initial_buy
                if override.margin_rate_initial_sell is not None:
                    config['margin_rate_initial_sell'] = override.margin_rate_initial_sell
                if override.swap_long is not None:
                    config['swap_long'] = override.swap_long
                if override.swap_short is not None:
                    config['swap_short'] = override.swap_short
                break
        return config
    
    def _matches_symbol_pattern(self, symbol: str, pattern: str) -> bool:
        """Check if symbol matches pattern (supports wildcards)."""
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            return symbol.startswith(prefix)
        return symbol == pattern
    
    def is_symbol_allowed(self, symbol: str) -> bool:
        """Check if a symbol is allowed for this group."""
        allowed = self.permissions.allowed_symbols
        if "*" in allowed:
            return True
        for pattern in allowed:
            if pattern.endswith("*"):
                prefix = pattern[:-1]
                if symbol.startswith(prefix):
                    return True
            elif symbol == pattern:
                return True
        return False
    
    def calculate_margin(
        self,
        symbol_config: Dict[str, Any],
        volume: Decimal,
        price: Decimal
    ) -> Decimal:
        """Calculate required margin for a trade."""
        contract_size = Decimal(str(symbol_config.get("contract_size", 100000)))
        margin_rate = Decimal(str(symbol_config.get("margin_rate_initial_buy", 1.0)))
        
        effective_leverage = Decimal(str(min(
            self.margin.leverage_default,
            self.margin.leverage_max
        )))
        if effective_leverage <= Decimal('0'):
            effective_leverage = Decimal('1.0')
        
        notional = volume * contract_size * price
        margin = (notional / effective_leverage) * margin_rate
        
        return margin
    
    def calculate_commission(
        self,
        symbol: str,
        volume: Decimal,
        deal_value: Decimal
    ) -> Decimal:
        """Calculate commission for a deal."""
        for rule in self.commissions:
            if not self._matches_symbol_pattern(symbol, rule.symbol_pattern):
                continue
            
            if rule.type == "per_lot":
                commission = volume * rule.value
            elif rule.type == "per_deal":
                commission = rule.value + (deal_value * rule.percent / Decimal('100.0'))
            elif rule.type == "percent":
                commission = deal_value * rule.percent / Decimal('100.0')
            else:
                commission = Decimal('0')
            
            commission = max(commission, rule.min_value)
            if rule.max_value is not None:
                commission = min(commission, rule.max_value)
            
            return commission
        
        return Decimal('0')
    
    def can_trade(self) -> bool:
        """Check if accounts in this group can trade."""
        return self.is_active and self.permissions.trade_allowed
    
    def has_trade_flag(self, flag: TradeFlags) -> bool:
        """Check if a specific trade flag is enabled."""
        return bool(self.trade_flags & flag)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert group to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "server_id": self.server_id,
            "account_type": self.account_type.value,
            "currency": self.currency,
            "margin": {
                "mode": self.margin.mode.value,
                "margin_call_level": str(self.margin.margin_call_level),
                "stop_out_level": str(self.margin.stop_out_level),
                "stop_out_mode": self.margin.stop_out_mode.value,
                "free_margin_mode": self.margin.free_margin_mode.value,
                "leverage_default": self.margin.leverage_default,
                "leverage_max": self.margin.leverage_max,
            },
            "trade_flags": int(self.trade_flags),
            "limit_orders": self.limit_orders,
            "limit_positions": self.limit_positions,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }