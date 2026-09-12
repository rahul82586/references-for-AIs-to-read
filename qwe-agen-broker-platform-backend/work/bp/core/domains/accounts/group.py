"""Group entity - The MT5 Rule Engine."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional
import uuid

from .enums import AccountType, CommissionType, TradeFlags, NewsMode
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
    # MT5 numbers cluster servers from 1 (1=main trade, 2=access, 3=history,
    # 4=backup). A group that exports Server "0" matches no real cluster member.
    server_id: int = 1
    account_type: AccountType = AccountType.REAL
    currency: str = "USD"
    # MT5 ConfigGroups.CurrencyDigits: how many decimal places the account currency
    # displays, i.e. 2 for a USD account denominated in cents. Distinct from a
    # symbol's Digits, which is price precision.
    currency_digits: int = 2
    
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
    
    # ------------------------------------------------------------------
    # Margin spec memoisation
    # ------------------------------------------------------------------
    #
    # Building a SymbolMarginSpec from the caller's dict costs more than the margin
    # arithmetic itself (profiled: 0.429s per 20k calls, of which basic_margin is only
    # 0.064s). Symbol configuration does not change between calls in the normal case -
    # changing it is an admin operation that invalidates ConfigCache - so the work is
    # pure repetition on the pre-trade hot path.
    #
    # Keyed on id(symbol_config), with the dict itself held in the entry so its id cannot
    # be recycled while the entry lives. Bounded, so a caller that builds a fresh dict per
    # call cannot grow it without limit.

    _MARGIN_SPEC_CACHE_MAX = 256

    def _margin_spec(self, symbol_config: Dict[str, Any]):
        """The SymbolMarginSpec for a symbol config dict, memoised per Group."""
        from core.domains.market_data.margin import SymbolMarginSpec

        cache = self.__dict__.get("_margin_spec_cache")
        if cache is None:
            cache = {}
            self.__dict__["_margin_spec_cache"] = cache
        else:
            key = id(symbol_config)
            hit = cache.get(key)
            # The stored dict must BE the one passed in, not merely have had its id.
            if hit is not None and hit[0] is symbol_config:
                return hit[1]

        spec = SymbolMarginSpec(
            name=str(symbol_config.get("name", "")),
            contract_size=Decimal(str(symbol_config.get("contract_size", 100000))),
            calc_mode=int(symbol_config.get("calc_mode", 0) or 0),
            margin_currency=str(
                symbol_config.get("margin_currency")
                or symbol_config.get("base_currency")
                or self.currency
                or ""
            ),
            margin_hedged=Decimal(str(symbol_config.get("margin_hedged", 0) or 0)),
            rates={
                key: Decimal(str(value))
                for key, value in symbol_config.items()
                if key.startswith(("initial_", "maintenance_")) and value is not None
            },
        )
        # Accept the legacy key names this method was always called with.
        for legacy, canonical in (
            ("margin_rate_initial_buy", "initial_buy"),
            ("margin_rate_initial_sell", "initial_sell"),
        ):
            if legacy in symbol_config and canonical not in spec.rates:
                spec.rates[canonical] = Decimal(str(symbol_config[legacy]))

        if len(cache) >= self._MARGIN_SPEC_CACHE_MAX:
            cache.clear()
        cache[id(symbol_config)] = (symbol_config, spec)
        return spec

    def invalidate_margin_spec_cache(self) -> None:
        """Drop memoised specs. Call after changing a group's symbol configuration."""
        self.__dict__.pop("_margin_spec_cache", None)

    def calculate_margin(
        self,
        symbol_config: Dict[str, Any],
        volume: Decimal,
        price: Decimal,
        *,
        operation: str = "BUY",
        leverage: Optional[int] = None,
        deposit_currency: Optional[str] = None,
        rate_lookup: Optional[Any] = None,
        maintenance: bool = False,
    ) -> Decimal:
        """Required margin for a trade, via the MT5-accurate engine.

        This used to compute `(volume * contract_size * price * rate) / leverage`
        inline. That is the CFD formula, applied to every symbol: for Forex MT5's
        formula has no price term at all, so this over-charged EURUSD margin by ~1.1x,
        USDJPY by ~150x and BTCUSD by ~2000x. It also used
        `min(leverage_default, leverage_max)` as the effective leverage, which is not
        how MT5 resolves leverage, and always took the BUY margin rate regardless of
        side or order type.

        ``leverage`` should be the caller's resolved value (account -> group -> symbol
        cap); when omitted the group default applies, capped by leverage_max.
        """
        from core.domains.market_data.margin import (
            apply_rate,
            basic_margin,
            convert_to_deposit,
        )

        spec = self._margin_spec(symbol_config)

        if leverage is None:
            leverage = self.margin.leverage_default or 1
            if self.margin.leverage_max and self.margin.leverage_max > 0:
                leverage = min(leverage, self.margin.leverage_max)

        basic = basic_margin(
            spec, volume, price, leverage=leverage, maintenance=maintenance
        )
        side = "BUY" if str(operation).upper().startswith("BUY") else "SELL"
        converted = convert_to_deposit(
            basic,
            margin_currency=spec.margin_currency,
            deposit_currency=deposit_currency or self.currency,
            side=side,
            rate_lookup=rate_lookup,
        )
        return apply_rate(converted, spec, str(operation).upper(), maintenance)

    def calculate_commission(
        self,
        symbol: str,
        volume: Decimal,
        deal_value: Decimal,
    ) -> Decimal:
        """Total commission for a deal: the SUM of every matching rule.

        Three defects fixed here:

        * The discriminator compared against "per_lot"/"per_deal"/"percent" while
          CommissionType's values are "deal"/"volume"/"percent", so DEAL and VOLUME rules
          fell through to zero. A broker charging no commission is not a rounding error.
        * `return` inside the loop applied only the FIRST matching rule. MT5 stacks them:
          the live export's real\\real group has three Commissions with different Path
          masks, and a deal can match more than one.
        * Tiered commissions could not be represented at all.

        Comparison is against the enum's VALUE, and a rule whose type is given as a bare
        string is normalised first, so both `CommissionType.VOLUME` and `"volume"` work.
        """
        total = Decimal('0')
        for rule in self.commissions:
            if not self._matches_symbol_pattern(symbol, rule.symbol_pattern):
                continue
            total += self._commission_for_rule(rule, volume, deal_value)
        return total

    def _commission_for_rule(
        self, rule: "CommissionRule", volume: Decimal, deal_value: Decimal
    ) -> Decimal:
        """One rule's commission, tiered if it has tiers, plus its min/max caps."""
        rule_type = rule.type.value if hasattr(rule.type, "value") else str(rule.type)

        if rule.tiers:
            # Volume-banded. The first band the volume falls in applies; MT5's RangeFrom
            # / RangeTo are inclusive at the low end.
            rate = None
            tier_min = Decimal('0')
            tier_max = None
            for tier in rule.tiers:
                if tier.applies_to(volume):
                    rate = tier.rate
                    tier_min = tier.min_value
                    tier_max = tier.max_value
                    break
            if rate is None:
                return Decimal('0')
            commission = self._apply_rate(rule_type, rate, rule.percent, volume, deal_value)
            commission = max(commission, tier_min)
            if tier_max is not None and tier_max > 0:
                commission = min(commission, tier_max)
        else:
            commission = self._apply_rate(
                rule_type, rule.value, rule.percent, volume, deal_value
            )

        commission = max(commission, rule.min_value)
        if rule.max_value is not None:
            commission = min(commission, rule.max_value)
        return commission

    @staticmethod
    def _apply_rate(
        rule_type: str,
        rate: Decimal,
        percent: Decimal,
        volume: Decimal,
        deal_value: Decimal,
    ) -> Decimal:
        """Apply a rate according to CommissionType.

            VOLUME   per lot            -> volume * rate
            DEAL     flat per deal      -> rate (+ percent of deal value if configured)
            PERCENT  of the deal value  -> deal_value * percent / 100
        """
        if rule_type == CommissionType.VOLUME.value:
            return volume * rate
        if rule_type == CommissionType.DEAL.value:
            result = rate
            if percent:
                result += deal_value * percent / Decimal('100.0')
            return result
        if rule_type == CommissionType.PERCENT.value:
            basis = percent if percent else rate
            return deal_value * basis / Decimal('100.0')
        raise ValueError(
            f"unknown CommissionType {rule_type!r}; expected one of "
            f"{[m.value for m in CommissionType]}"
        )
    
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
            # How many per-symbol overrides this group carries. An operator needs this to
            # see whether a group's 60-odd MT5 group-symbol settings actually loaded; a
            # group that imported with zero overrides looks identical to one that failed.
            "symbol_overrides_count": len(self.symbol_overrides),
            "commissions_count": len(self.commissions),
            "margin": {
                "mode": self.margin.mode.value,
                "margin_call_level": str(self.margin.margin_call_level),
                "stop_out_level": str(self.margin.stop_out_level),
                "stop_out_mode": self.margin.stop_out_mode.value,
                "free_margin_mode": self.margin.free_margin_mode.value,
                "leverage_default": self.margin.leverage_default,
                "leverage_max": self.margin.leverage_max,
                        # How many per-symbol overrides this group carries. An
            # operator needs this to see whether a group's 60-odd MT5
            # group-symbol settings actually loaded.
            "symbol_overrides_count": len(self.symbol_overrides),
},
            "trade_flags": int(self.trade_flags),
            "limit_orders": self.limit_orders,
            "limit_positions": self.limit_positions,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }