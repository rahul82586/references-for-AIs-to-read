"""
Pre-Trade Risk Service for validating orders before execution.
Encapsulates all margin, permission, and account state checks.
"""
import asyncio
import logging
from decimal import Decimal
from typing import Any, Dict, Optional

from core.domains.accounts.models import Account, Group
from core.domains.instruments.models import Symbol
from core.domains.oms.entities.order import Order, OrderType
from core.domains.common.value_objects import Money, Price, Volume
from core.events.domain_events import DomainEvent, OrderApproved, OrderRejected, EventType
from core.ports.interfaces import IEventBus, IPositionRepository

logger = logging.getLogger(__name__)


class PreTradeRiskService:
    """
    Service responsible for pre-trade validation.

    Architectural Purpose:
    Centralizes all risk checks required before an order can be accepted.
    Prevents race conditions using per-account asyncio.Lock context managers.
    """

    def __init__(
        self,
        event_bus: Optional[IEventBus] = None,
        position_repo: Optional[IPositionRepository] = None,
        risk_engine: Optional[Any] = None,
        symbol_repo: Optional[Any] = None,
        account_repo: Optional[Any] = None
    ):
        self.event_bus = event_bus
        self.position_repo = position_repo
        self.risk_engine = risk_engine
        self.symbol_repo = symbol_repo
        self.account_repo = account_repo
        self._account_locks: Dict[str, asyncio.Lock] = {}

    def get_account_lock(self, account_login: str) -> asyncio.Lock:
        """
        Returns the per-account lock to guarantee single-writer isolation
        during pre-trade risk checks and margin reservations.
        """
        login_key = str(account_login)
        if login_key not in self._account_locks:
            self._account_locks[login_key] = asyncio.Lock()
        return self._account_locks[login_key]

    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def account_lock(self, account_login: str):
        """
        Async context manager providing per-account locking.
        Usage: async with risk_service.account_lock(account_login): ...
        """
        lock = self.get_account_lock(account_login)
        async with lock:
            yield lock

    async def validate_order(
        self,
        order: Order,
        account: Account,
        symbol: Symbol,
        current_price: Price
    ) -> bool:
        """
        Performs all pre-trade checks under per-account lock protection.
        Uses 'async with' to guarantee lock release even if an exception occurs.
        Returns True if approved, False if rejected.
        """
        account_login = str(getattr(account, 'login', getattr(account, 'login_id', getattr(account, 'id', 'default'))))
        lock = self.get_account_lock(account_login)

        # CRITICAL: Use 'async with' to guarantee lock release on exception
        async with lock:
            logger.info(f"Running pre-trade checks under lock for Order {order.ticket_id} on Account {account_login}")

            # 1. Fetch LIVE account state if account_repo is available
            live_account = account
            if self.account_repo:
                try:
                    fetched = await self.account_repo.find_by_login(account_login)
                    if fetched:
                        live_account = fetched
                except Exception as e:
                    logger.warning(f"Could not refresh live account state for {account_login}: {e}")

            # 2. Account State Check
            if not live_account.can_trade():
                reason = "Account is disabled or pending KYC verification"
                logger.warning(f"Order {order.ticket_id} rejected: {reason}")
                await self._publish_rejection(order, reason)
                return False

            # 3. Symbol Permission Check (Group Rules)
            if not self._check_symbol_permission(live_account.group, symbol.name):
                reason = f"Symbol {symbol.name} is not allowed for Group {live_account.group.name if live_account.group else 'Unknown'}"
                logger.warning(f"Order {order.ticket_id} rejected: {reason}")
                await self._publish_rejection(order, reason)
                return False

            # 4. Trading Session Check
            from datetime import datetime, timezone
            current_time = datetime.now(timezone.utc).time()
            if not symbol.is_within_session(current_time):
                reason = f"Symbol {symbol.name} is currently outside trading sessions"
                logger.warning(f"Order {order.ticket_id} rejected: {reason}")
                await self._publish_rejection(order, reason)
                return False

            # 5. Volume Limits Check
            if not self._check_volume_limits(order.volume, symbol):
                reason = f"Volume {order.volume.value} exceeds limits for {symbol.name} (Min: {symbol.volume_min}, Max: {symbol.volume_max})"
                logger.warning(f"Order {order.ticket_id} rejected: {reason}")
                await self._publish_rejection(order, reason)
                return False

            # 6. Live Margin Requirement Check
            if not await self._check_margin_requirement(order, live_account, symbol, current_price):
                reason = "Insufficient free margin to open this position"
                logger.warning(f"Order {order.ticket_id} rejected: {reason}")
                await self._publish_rejection(order, reason)
                return False

            # All checks passed under lock protection
            logger.info(f"Order {order.ticket_id} approved by Pre-Trade Risk Service")
            await self._publish_approval(order)
            return True

    def _check_symbol_permission(self, group: Optional[Group], symbol_name: str) -> bool:
        """Checks if the group permissions allow trading this symbol."""
        if not group:
            return True
        return group.is_symbol_allowed(symbol_name)

    def _check_volume_limits(self, volume: Volume, symbol: Symbol) -> bool:
        """Validates volume against symbol min/max and step."""
        if volume.value < symbol.volume_min or volume.value > symbol.volume_max:
            return False
        if not volume.is_valid_step(symbol.volume_step):
            return False
        return True

    async def _check_margin_requirement(
        self,
        order: Order,
        account: Account,
        symbol: Symbol,
        price: Price
    ) -> bool:
        """
        Calculates required margin with group symbol overrides and compares against live Free Margin.
        
        MT5-Accurate Logic:
        1. Build base symbol config (contract_size, margin_rates, etc.)
        2. Apply group symbol overrides if available
        3. Use account's effective leverage (account > group > default)
        4. Calculate margin: (Volume * ContractSize * Price * MarginRate) / Leverage
        """
        volume = order.volume.value
        price_value = price.value
        
        # 1. Build base symbol configuration
        symbol_config = {
            "contract_size": symbol.contract_size,
            "tick_size": symbol.tick_size,
            "tick_value": symbol.tick_value,
            "base_currency": symbol.base_currency,
            "quote_currency": symbol.quote_currency,
            "margin_rate_initial_buy": symbol.margin_rates.initial_buy,
            "margin_rate_initial_sell": symbol.margin_rates.initial_sell,
        }
        
        # 2. Apply group symbol overrides if available
        if account.group:
            overrides = account.group.get_symbol_config(symbol.name)
            symbol_config.update(overrides)
        
        # 3. Determine effective leverage (account > group > default 100)
        effective_leverage = Decimal(str(
            account.effective_leverage() if hasattr(account, 'effective_leverage') 
            else (account.leverage if account.leverage and account.leverage > 0 
                else (account.group.margin.leverage_default if account.group else 100))
        ))
        if effective_leverage <= Decimal('0'):
            effective_leverage = Decimal('1.0')
        
        # 4. Calculate required margin
        contract_size = symbol_config.get("contract_size", Decimal('100000'))
        
        # Determine margin rate based on order side
        order_side = "BUY" if order.order_type.startswith("BUY") else "SELL"
        if order_side == "BUY":
            margin_rate = symbol_config.get("margin_rate_initial_buy", Decimal('1.0'))
        else:
            margin_rate = symbol_config.get("margin_rate_initial_sell", Decimal('1.0'))
        
        # Formula: (Volume * ContractSize * Price * MarginRate) / Leverage
        notional = volume * contract_size * price_value
        margin_required = (notional * margin_rate) / effective_leverage
        
        required_amount = margin_required
        
        # 5. Check live margin using RiskEngine if available
        available_free_margin = account.margin_free.amount
        if self.risk_engine and self.position_repo:
            try:
                open_positions = await self.position_repo.get_by_account(
                    account.login if hasattr(account, 'login') else account.id
                )
                snapshot = self.risk_engine.calculate_margin_level(account, open_positions)
                available_free_margin = snapshot.margin_free
            except Exception as e:
                logger.error(f"Failed live margin snapshot calculation: {e}", exc_info=True)
        
        # 6. Compare required vs available
        if required_amount > available_free_margin:
            logger.debug(
                f"Margin check failed: Required {required_amount}, Available {available_free_margin}"
            )
            return False
        
        return True

    async def _publish_approval(self, order: Order) -> None:
        """Publishes OrderApprovedEvent."""
        if not self.event_bus:
            return
        event = OrderApproved(
            aggregate_id=order.ticket_id,
            payload={
                "ticket_id": order.ticket_id,
                "account_login": getattr(order, 'account_login', getattr(order, 'account_id', '')),
                "symbol": order.symbol,
                "volume": str(order.volume.value),
                "approved_at": order.updated_at.isoformat()
            }
        )
        await self.event_bus.publish(event)

    async def _publish_rejection(self, order: Order, reason: str) -> None:
        """Publishes OrderRejectedEvent."""
        if not self.event_bus:
            return
        event = OrderRejected(
            aggregate_id=order.ticket_id,
            payload={
                "ticket_id": order.ticket_id,
                "account_login": getattr(order, 'account_login', getattr(order, 'account_id', '')),
                "reason": reason,
                "rejected_at": order.updated_at.isoformat()
            }
        )
        await self.event_bus.publish(event)
