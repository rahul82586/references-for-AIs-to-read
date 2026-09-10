"""Backward compatibility module re-exporting account domain entities & enums."""
from core.domains.accounts import (
    AccountType, ClientStatus, SOActivation, MarginMode,
    ExecutionMode, TradeMode, FreeMarginMode, StopOutMode,
    CommissionType, CommissionMode, NewsMode, TradeFlags,
    StopOutSnapshot, MarginProfile, CommissionRule,
    SwapConfiguration, GroupSymbolOverride, RoutingRule,
    GroupPermissions, CommissionTier,
    Group, Client, Account
)

__all__ = [
    "AccountType", "ClientStatus", "SOActivation", "MarginMode",
    "ExecutionMode", "TradeMode", "FreeMarginMode", "StopOutMode",
    "CommissionType", "CommissionMode", "NewsMode", "TradeFlags",
    "StopOutSnapshot", "MarginProfile", "CommissionRule",
    "SwapConfiguration", "GroupSymbolOverride", "RoutingRule",
    "GroupPermissions", "CommissionTier",
    "Group", "Client", "Account",
]
