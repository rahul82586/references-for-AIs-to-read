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
        #: reason for the most recent rejection. validate_order() returns a bool, so a
        #: caller that suppresses event publishing (CreateOrderHandler does, to keep the
        #: approval from firing inside the account lock) would otherwise have to invent
        #: a reason for its own OrderRejected event and its log line.
        self.last_rejection_reason: Optional[str] = None

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
        current_price: Price,
        publish_events: bool = True,
    ) -> bool:
        """
        Performs all pre-trade checks under per-account lock protection.
        Uses 'async with' to guarantee lock release even if an exception occurs.
        Returns True if approved, False if rejected.

        `publish_events=False` suppresses the OrderApproved/OrderRejected publish.
        CreateOrderHandler uses it, because an approval published from inside the
        per-account lock is delivered (the bus awaits handlers inline) to an
        ExecutionOrchestrator that then fetches the same account and takes the same
        lock - a self-deadlock - and it is published before the order is persisted, so
        the orchestrator's find_by_id returns None. The handler validates under the
        lock, persists, then publishes.
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
                self.last_rejection_reason = reason
                if publish_events:
                    await self._publish_rejection(order, reason)
                return False

            # 3. Symbol Permission Check (Group Rules)
            if not self._check_symbol_permission(live_account.group, symbol.name):
                reason = f"Symbol {symbol.name} is not allowed for Group {live_account.group.name if live_account.group else 'Unknown'}"
                logger.warning(f"Order {order.ticket_id} rejected: {reason}")
                self.last_rejection_reason = reason
                if publish_events:
                    await self._publish_rejection(order, reason)
                return False

            # 4. Trading Session Check
            # Symbol has is_trade_session_active(datetime); there is no is_within_session,
            # so this step raised AttributeError for every order that reached it.
            from datetime import datetime, timezone
            if not symbol.is_trade_session_active(datetime.now(timezone.utc)):
                reason = f"Symbol {symbol.name} is currently outside trading sessions"
                logger.warning(f"Order {order.ticket_id} rejected: {reason}")
                self.last_rejection_reason = reason
                if publish_events:
                    await self._publish_rejection(order, reason)
                return False

            # 5. Volume Limits Check
            if not self._check_volume_limits(order.volume, symbol):
                reason = f"Volume {order.volume.value} exceeds limits for {symbol.name} (Min: {symbol.volume_min}, Max: {symbol.volume_max})"
                logger.warning(f"Order {order.ticket_id} rejected: {reason}")
                self.last_rejection_reason = reason
                if publish_events:
                    await self._publish_rejection(order, reason)
                return False

            # 6. Live Margin Requirement Check
            required_margin = await self._check_margin_requirement(
                order, live_account, symbol, current_price
            )
            if required_margin is None:
                reason = "Insufficient free margin to open this position"
                logger.warning(f"Order {order.ticket_id} rejected: {reason}")
                self.last_rejection_reason = reason
                if publish_events:
                    await self._publish_rejection(order, reason)
                return False

            # M6 (M4 debt #1): hold the requirement before approving. Between
            # here and the fill nothing else moves a number the check reads, so
            # without the hold two concurrent orders - across a Redis bus, or
            # across two API nodes - could both pass the same free-margin check
            # and both book. The SQL repository does this as ONE conditional
            # UPDATE (the database serialises the racers); the amount held is
            # recorded on the order so the release at fill/reject is exact.
            from application.services.margin_reservation import (
                release_margin,
                reserve_margin,
            )

            if required_margin > 0:
                if not await reserve_margin(self.account_repo, live_account, required_margin):
                    reason = (
                        "Insufficient free margin to open this position "
                        "(reserved by concurrent in-flight orders)"
                    )
                    logger.warning(f"Order {order.ticket_id} rejected: {reason}")
                    self.last_rejection_reason = reason
                    if publish_events:
                        await self._publish_rejection(order, reason)
                    return False
                order.reserved_margin = required_margin

            # All checks passed under lock protection
            logger.info(f"Order {order.ticket_id} approved by Pre-Trade Risk Service")
            self.last_rejection_reason = None
            if publish_events:
                try:
                    await self._publish_approval(order)
                except Exception:
                    # the approval never reached the orchestrator: un-hold
                    if order.reserved_margin:
                        await release_margin(
                            self.account_repo, live_account.login,
                            order.reserved_margin, account=live_account,
                        )
                        order.reserved_margin = Decimal("0")
                    raise
            return True

    def _check_symbol_permission(self, group: Optional[Group], symbol_name: str) -> bool:
        """Checks if the group permissions allow trading this symbol."""
        if not group:
            return True
        return group.is_symbol_allowed(symbol_name)

    def _check_volume_limits(self, volume: Volume, symbol: Symbol) -> bool:
        """Validates volume against the symbol's min / max / step.

        Delegates to Symbol.validate_volume, which is the same rule
        CreateOrderHandler already applied a few lines earlier. This was a second
        implementation of it, and the two disagreed: this one compared against
        volume_min / volume_max unconditionally, so a symbol whose limits came back as 0
        from the database rejected every order, and it called is_valid_step(0) which
        raised decimal.InvalidOperation rather than returning a verdict.
        """
        ok, _reason = symbol.validate_volume(volume.value)
        return ok

    async def _check_margin_requirement(
        self,
        order: Order,
        account: Account,
        symbol: Symbol,
        price: Price,
    ) -> Optional[Decimal]:
        """Pre-trade initial margin check, using the MT5-accurate engine.

        MT5 checks INITIAL margin when opening a position and MAINTENANCE margin for
        positions already open; pending orders are always checked at initial. This is the
        opening path, so it uses initial.

        The calculation runs all four MT5 stages - basic, conversion to the deposit
        currency, the operation's rate multiplier, and aggregation - through
        core.domains.market_data.margin, which is where the formulas and MT5's own
        published worked examples are asserted. Nothing here re-derives a formula.
        """
        from core.domains.market_data.margin import (
            MarginCalculationError,
            SymbolMarginSpec,
            apply_rate,
            basic_margin,
            convert_to_deposit,
            available_margin,
        )

        order_type = order.order_type.value if hasattr(order.order_type, "value") else str(order.order_type)
        operation = order_type.upper()

        # 1. Symbol spec, then group overrides on top. MT5: "To avoid overriding the
        #    coefficient value for a group, leave the value set to Default" - so a None
        #    override means inherit, never zero.
        spec = SymbolMarginSpec.from_symbol(symbol)
        if account.group is not None:
            overrides = account.group.get_symbol_config(symbol.name)
            spec = self._apply_group_overrides(spec, overrides)

        # 2. Leverage resolves account -> group -> symbol cap, not
        #    min(group.default, group.max) which ignores both the account override and
        #    the per-symbol maximum.
        leverage = self._resolve_leverage(account, symbol)

        # 3. Stages 1-3. A market order with no price raises rather than defaulting to
        #    1.0 - that default understated JPY margin by ~150x.
        price_value = price.value if price is not None else None
        try:
            basic = basic_margin(spec, order.volume.value, price_value, leverage=leverage)
            converted = convert_to_deposit(
                basic,
                margin_currency=spec.margin_currency,
                deposit_currency=account.currency,
                side="BUY" if operation.startswith("BUY") else "SELL",
                rate_lookup=self._rate_lookup,
            )
            required = apply_rate(converted, spec, operation, maintenance=False)
        except MarginCalculationError as exc:
            # A margin requirement we cannot compute is a rejection, not an approval.
            # The previous code caught every exception here and fell back to a stored
            # free-margin figure, which approved trades on stale data.
            logger.warning(
                "margin check for order %s could not be computed: %s", order.ticket_id, exc
            )
            return None

        # 4. Available margin. Use the live snapshot when we can build one, and treat a
        #    failure to build it as a rejection rather than silently degrading to a
        #    cached number. In-flight reservations (M6) count against availability in
        #    BOTH paths: a second concurrent order must see the first one's hold
        #    whether or not it has filled yet.
        reserved_now = (
            account.margin_reserved.amount
            if getattr(account, "margin_reserved", None) is not None
            else Decimal("0")
        )
        available = account.margin_free.amount - reserved_now
        if self.risk_engine is not None and self.position_repo is not None:
            try:
                open_positions = await self.position_repo.get_by_account(account.login)
                snapshot = self.risk_engine.calculate_margin_level(account, open_positions)
                # Conservative: a positive unrealised gain is not trusted to authorise a
                # new position, only a loss reduces availability. This is the rule
                # tfrmma/oms margin_monitor.hpp documents - a local estimate that has
                # drifted optimistic must not open trades.
                available = available_margin(
                    equity=snapshot.equity,
                    margin_used=snapshot.margin_used + reserved_now,
                    unrealized_pnl=snapshot.equity - account.balance.amount,
                    conservative=True,
                )
            except Exception as exc:  # noqa: BLE001 - but do NOT approve on failure
                logger.error(
                    "live margin snapshot failed for %s; rejecting rather than trusting "
                    "the stored free margin: %s",
                    account.login,
                    exc,
                )
                return None

        if required > available:
            logger.debug(
                "margin check failed for %s: required %s, available %s (reserved in-flight %s)",
                order.ticket_id,
                required,
                available,
                reserved_now,
            )
            return None
        return required

    def _resolve_leverage(self, account: Account, symbol: Symbol) -> int:
        """Account override, then group, then the symbol cap. Never zero.

        MT5 applies the most restrictive of these. The previous code used
        min(group.leverage_default, group.leverage_max), which ignored the account's own
        override entirely.
        """
        candidates = []
        account_leverage = getattr(account, "leverage", None)
        if account_leverage and account_leverage > 0:
            candidates.append(int(account_leverage))
        group = getattr(account, "group", None)
        if group is not None:
            default = getattr(group.margin, "leverage_default", 0) or 0
            maximum = getattr(group.margin, "leverage_max", 0) or 0
            if default > 0:
                candidates.append(int(default))
            if maximum > 0:
                candidates.append(int(maximum))
        symbol_max = getattr(symbol, "leverage_max", 0) or 0
        if symbol_max > 0:
            candidates.append(int(symbol_max))
        if not candidates:
            return 1
        return min(candidates)

    def _apply_group_overrides(self, spec, overrides: dict):
        """Overlay a group's per-symbol overrides onto the symbol spec.

        An override value of None means "inherit from the symbol", which MT5 encodes on
        the wire as the string "default". It must never be read as zero: a zero margin
        rate means "no margin charged for this operation type", which is a real and
        dangerous setting, not an absent one.
        """
        from dataclasses import replace as _replace
        from decimal import Decimal as _Decimal

        rates = dict(spec.rates)
        changes = {}
        for key, value in (overrides or {}).items():
            if value is None:
                continue
            if key.startswith("margin_rate_initial_"):
                rates[key.replace("margin_rate_initial_", "initial_")] = _Decimal(str(value))
            elif key.startswith("margin_rate_maintenance_"):
                rates[key.replace("margin_rate_maintenance_", "maintenance_")] = _Decimal(str(value))
            elif key == "contract_size":
                changes["contract_size"] = _Decimal(str(value))
            elif key == "margin_hedged":
                changes["margin_hedged"] = _Decimal(str(value))
        return _replace(spec, rates=rates, **changes)

    def _rate_lookup(self, from_currency: str, to_currency: str, side: str):
        """Currency conversion for margin, delegating to the risk engine.

        Returns None when no rate is available, which convert_to_deposit turns into a
        rejection. Never returns 1.0 as a guess.
        """
        if self.risk_engine is None:
            return None
        getter = getattr(self.risk_engine, "get_conversion_rate", None)
        if getter is None:
            return None
        try:
            return getter(from_currency, to_currency)
        except Exception:  # noqa: BLE001 - an unresolvable rate is a rejection
            return None

    async def _publish_approval(self, order: Order) -> None:
        """Publishes OrderApprovedEvent.

        The payload carries the identifier under BOTH `order_id` and `ticket_id`.
        Risk published `ticket_id` while ExecutionOrchestrator read `order_id`, so the
        orchestrator logged "OrderApprovedEvent missing order_id" and returned - the
        approval and the execution never met. Carrying both is cheaper than picking a
        side, and `order_id` is the name the rest of the tree uses.
        """
        if not self.event_bus:
            return
        account_login = getattr(order, 'account_login', getattr(order, 'account_id', ''))
        event = OrderApproved(
            aggregate_id=order.ticket_id,
            payload={
                "order_id": order.ticket_id,
                "ticket_id": order.ticket_id,
                "account_login": account_login,
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
        account_login = getattr(order, 'account_login', getattr(order, 'account_id', ''))
        event = OrderRejected(
            aggregate_id=order.ticket_id,
            payload={
                "order_id": order.ticket_id,
                "ticket_id": order.ticket_id,
                "account_login": account_login,
                "reason": reason,
                "rejected_at": order.updated_at.isoformat()
            }
        )
        await self.event_bus.publish(event)
