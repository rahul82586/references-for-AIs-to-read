"""
Smart Order Router (SOR).

This module implements the logic to evaluate an approved Order against
active RoutingRules and determine the execution destination.

Architectural Purpose:
Decouples the decision logic (WHERE to send) from the execution logic (HOW to send).
Allows dynamic reconfiguration of routing rules without changing core code.
"""
from typing import Any, List, Optional
from decimal import Decimal
import logging
import fnmatch

from core.domains.market_data.margin import margin_level as compute_margin_level
from core.domains.execution.models import (
    RoutingRule,
    ExecutionInstruction,
    ExecutionDestination
)
from core.domains.oms.entities.order import Order
from core.domains.accounts.models import Account
from core.ports.interfaces import IRoutingRuleRepository

logger = logging.getLogger(__name__)


class SmartOrderRouter:
    """
    Evaluates an approved Order against active RoutingRules.
    Returns an ExecutionInstruction telling the orchestrator where to send it.

    Rules are evaluated by priority (highest first). First match wins.
    If no rule matches, falls back to a server default (configurable).

    Supports dynamic rule reloading via IRoutingRuleRepository.
    """

    def __init__(
        self,
        routing_rule_repo: IRoutingRuleRepository,
        default_destination: ExecutionDestination = ExecutionDestination.B_BOOK,
        coverage_repo: Optional[Any] = None,
        mt5_routing_repo: Optional[Any] = None,
        client_quote_fn: Optional[Any] = None,
        counts_fn: Optional[Any] = None,
    ):
        self.repo = routing_rule_repo
        self.default_destination = default_destination
        self.coverage_repo = coverage_repo
        self.rules: List[RoutingRule] = []
        #: M8: the MT5 request-policy table (IMTConRoute records) and a
        #: synchronous (symbol, login) -> (client bid, ask, point) resolver for
        #: the deviation/spread conditions. Both optional: without them the
        #: router behaves exactly as before M8.
        self.mt5_routing_repo = mt5_routing_repo
        self.mt5_rules: List[Any] = []
        self._client_quote_fn = client_quote_fn
        #: (login, symbol) -> (open positions total, open positions in symbol),
        #: synchronous, for routing conditions 4005/4006. Order counts (4007/8)
        #: have no synchronous source yet and stay unmatched (documented).
        self._counts_fn = counts_fn
        #: distinguishes "no rules configured" from "nobody ever loaded the rules", which
        #: need opposite responses - see route().
        self._rules_loaded = False
        logger.info("SmartOrderRouter initialized with dynamic rule loading and NOP monitoring")

    async def refresh_rules(self):
        """Reload routing rules from repository. Call this on startup and periodically."""
        if self.mt5_routing_repo is not None:
            try:
                self.mt5_rules = await self.mt5_routing_repo.get_all_ordered()
                if self.mt5_rules:
                    logger.info(
                        "SmartOrderRouter loaded %d MT5 routing rule(s): %s",
                        len(self.mt5_rules),
                        ", ".join(r.name for r in self.mt5_rules),
                    )
            except Exception as exc:  # noqa: BLE001 - house routing must still work
                self.mt5_rules = []
                logger.error("could not load the MT5 routing table: %s", exc)
        self.rules = await self.repo.get_active_rules()
        self.rules = sorted(self.rules, key=lambda r: r.priority, reverse=True)
        self._rules_loaded = True
        if not self.rules:
            logger.warning(
                "no active routing rules configured; every order falls back to the "
                "default destination %s. A production server should define at least one "
                "rule per group.",
                self.default_destination.value,
            )
        else:
            logger.info(f"SmartOrderRouter loaded {len(self.rules)} active rules")

    def route(
        self,
        order: Order,
        account: Account,
        coverage_account: Optional[Any] = None
    ) -> ExecutionInstruction:
        """Route one order: the MT5 request-policy table first, then the house
        rules (destination selection + NOP exposure governance).

        MT5 evaluates its routing table top-down before execution; delay and
        clear-SL/TP actions are non-terminal and accumulate onto whatever
        instruction finally wins; CONFIRM_* falls through to normal execution,
        which is what "confirm at the requested/market price" means here.
        """
        delay_ms = 0
        delay_ticks = 0
        if self.mt5_rules:
            from core.domains.execution.routing_mt5 import RouteAction

            decision = self._evaluate_mt5(order, account)
            for warning in decision.warnings:
                logger.warning("MT5 routing: %s", warning)
            if decision.clear_sl and order.price_sl is not None:
                order.price_sl = None
                logger.info("MT5 routing cleared the SL of order %s", order.ticket_id)
            if decision.clear_tp and order.price_tp is not None:
                order.price_tp = None
                logger.info("MT5 routing cleared the TP of order %s", order.ticket_id)
            delay_ms, delay_ticks = decision.delay_ms, decision.delay_ticks
            if decision.terminal:
                instruction = self._instruction_from_mt5(order, decision)
                if instruction is not None:
                    instruction.delay_ms = delay_ms
                    instruction.delay_ticks = delay_ticks
                    instruction.mt5_rule = decision.matched_rule
                    return instruction

        instruction = self._route_house(order, account, coverage_account=coverage_account)
        instruction.delay_ms = delay_ms
        instruction.delay_ticks = delay_ticks
        return instruction

    def _evaluate_mt5(self, order: Order, account: Account):
        from datetime import datetime, timezone

        from core.domains.execution.routing_mt5 import (
            RouteRequest,
            RoutingEngine,
            RoutingRequestContext,
        )

        group = ""
        attached = getattr(account, "group", None)
        if attached is not None:
            group = getattr(attached, "name", "") or ""
        if not group:
            group = str(getattr(account, "group_id", "") or "")

        bid = ask = point = None
        if self._client_quote_fn is not None:
            try:
                quote = self._client_quote_fn(order.symbol, account.login)
                if quote is not None:
                    bid, ask, point = quote[0], quote[1], quote[2]
            except Exception as exc:  # noqa: BLE001 - conditions degrade to unmatched
                logger.warning("client quote for routing of %s failed: %s", order.ticket_id, exc)

        def _amount(attr):
            value = getattr(account, attr, None)
            return getattr(value, "amount", None)

        def _margin_level():
            # D1: DERIVED, never read from account.margin_level. That field is a
            # persisted column refreshed only by whichever write path remembered
            # to call recompute_margin_level(); a routing decision cannot depend
            # on that. A stale Decimal('0') is worse than None here - None makes
            # M8's missing-context guard skip the condition, while 0 makes a
            # MARGIN_LEVEL comparison really fire against zero.
            equity = _amount("equity")
            used = _amount("margin_used")
            if equity is None or used is None:
                return None
            return compute_margin_level(equity, used)

        try:
            login = int(account.login)
        except (TypeError, ValueError):
            login = None

        positions_total = positions_symbol = None
        if self._counts_fn is not None:
            try:
                positions_total, positions_symbol = self._counts_fn(account.login, order.symbol)
            except Exception as exc:  # noqa: BLE001 - counts degrade to unmatched
                logger.warning("position counts for routing failed: %s", exc)

        ctx = RoutingRequestContext(
            request_flags=int(
                RouteRequest.PENDING if not order.is_market() else RouteRequest.MARKET
            ),
            order_type=order.order_type,
            group=group,
            symbol=order.symbol,
            volume=order.volume_current.value if order.volume_current else None,
            price=(
                order.price_order.value
                if order.price_order and order.price_order.value > 0
                else None
            ),
            bid=bid,
            ask=ask,
            point=point,
            now=datetime.now(timezone.utc),
            comment=order.comment or "",
            login=login,
            leverage=getattr(account, "leverage", None),
            balance=_amount("balance"),
            equity=_amount("equity"),
            profit=_amount("profit"),
            margin_used=_amount("margin_used"),
            margin_free=_amount("margin_free"),
            margin_level=_margin_level(),
            positions_total=positions_total,
            positions_symbol=positions_symbol,
        )
        return RoutingEngine().evaluate(ctx, self.mt5_rules)

    def _instruction_from_mt5(self, order: Order, decision) -> Optional[ExecutionInstruction]:
        """Map a terminal MT5 action onto an ExecutionInstruction, or None to
        continue with house routing (CONFIRM_*, and DEALER-with-skip when no
        dealer session infrastructure exists)."""
        from core.domains.execution.routing_mt5 import RouteAction

        action = decision.action
        name = decision.matched_rule or "?"

        if action is RouteAction.REJECT:
            reason = decision.reject_reason or f"rejected by rule '{name}'"
            return ExecutionInstruction(
                destination=ExecutionDestination.REJECT,
                rule_id=f"mt5:{name}",
                reason=reason[:31],  # guide: the client-visible reason is <= 31 chars
            )
        if action in (RouteAction.DEALER, RouteAction.DEALER_ONLINE):
            if decision.skip_if_no_dealers_online:
                # MT5 skips the rule when none of the listed dealers is online.
                # No dealer SESSION infrastructure exists in this build, so
                # nobody is online: skipping (rather than parking the order in a
                # queue nobody services) is the faithful - and safe - behaviour.
                logger.warning(
                    "MT5 routing rule '%s' sends order %s to dealers with "
                    "skip-if-none-online and no dealer sessions exist; continuing "
                    "to normal execution", name, order.ticket_id,
                )
                return None
            dealers = ", ".join(d.name for d in decision.dealers) or "any online dealer"
            return ExecutionInstruction(
                destination=ExecutionDestination.TO_DEALER,
                rule_id=f"mt5:{name}",
                reason=f"routing rule '{name}' -> {dealers}",
            )
        if action is RouteAction.REQUOTE:
            return ExecutionInstruction(
                destination=ExecutionDestination.REJECT,
                rule_id=f"mt5:{name}",
                reason="requote: no dealer terminal",
            )
        if action is RouteAction.CANCEL_ORDER:
            return ExecutionInstruction(
                destination=ExecutionDestination.REJECT,
                rule_id=f"mt5:{name}",
                reason=f"canceled by rule '{name}'",
            )
        if action in (RouteAction.CONFIRM_CLIENT, RouteAction.CONFIRM_MARKET):
            logger.info(
                "MT5 routing rule '%s' confirms execution (%s) for order %s; "
                "proceeding to normal routing", name, action.name, order.ticket_id,
            )
            return None
        return None

    def _route_house(
        self,
        order: Order,
        account: Account,
        coverage_account: Optional[Any] = None
    ) -> ExecutionInstruction:
        """
        Evaluate rules and return where this order should go.
        Includes NOP (Net Open Position) threshold triggers:
        - 70%: Warning Alert
        - 85%: Auto-Hedge (Divert B-Book to A-Book LP Gateway)
        - 95%: Block B-Book Order (Reject)
        """
        if not self._rules_loaded:
            # Never loaded: a wiring bug, and a loud one. Loading here would need an
            # event loop the caller may not have (route() is synchronous), so it fails
            # instead - build_trading_stack() awaits refresh_rules() at startup.
            raise RuntimeError("Routing rules not loaded. Call refresh_rules() first.")

        # Loaded, and the table is empty. That is a legitimate configuration for a
        # freshly seeded server, and MT5's own behaviour is to fall back to the server's
        # default execution mode - so that is what happens below. Refusing to route made
        # "install, seed, start, place an order" impossible without hand-writing a
        # routing rule first, and the failure surfaced as an unhandled RuntimeError
        # inside an event handler rather than a rejected order.

        # Account has `login`; there is no `login_id`. This line raised AttributeError on
        # every call, which is the clearest evidence the routing path had never executed.
        logger.debug(
            "Routing order %s for account %s",
            order.ticket_id,
            getattr(account, "login", getattr(account, "login_id", "?")),
        )

        for rule in self.rules:
            if not rule.is_enabled:
                continue

            if self._matches(rule, order, account):
                gateway_id = rule.gateway_id or self._select_lp_gateway(rule, account)
                coverage_id = rule.coverage_account_id or "DEFAULT_COVERAGE"

                logger.info(
                    f"Order {order.ticket_id} matched rule '{rule.rule_id}' "
                    f"-> Destination: {rule.destination.value}"
                )
                return self._apply_nop_thresholds(
                    order=order,
                    destination=rule.destination,
                    rule_id=rule.rule_id,
                    gateway_id=gateway_id,
                    coverage_id=coverage_id,
                    coverage_account=coverage_account,
                    reason=f"Matched rule: {rule.rule_id}",
                )

        # Fallback to default
        fallback_gateway = self._select_lp_gateway(None, account)
        logger.warning(
            f"No routing rule matched for order {order.ticket_id}. "
            f"Using default: {self.default_destination.value}"
        )
        return self._apply_nop_thresholds(
            order=order,
            destination=self.default_destination,
            rule_id="DEFAULT_FALLBACK",
            gateway_id=fallback_gateway,
            coverage_id="DEFAULT_COVERAGE",
            coverage_account=coverage_account,
            reason="No matching rule found",
        )

    def _apply_nop_thresholds(
        self,
        order: Order,
        destination: ExecutionDestination,
        rule_id: str,
        gateway_id: Optional[str],
        coverage_id: str,
        coverage_account: Optional[Any],
        reason: str,
    ) -> ExecutionInstruction:
        """Net Open Position limits, applied to WHATEVER destination was decided.

        This used to live inside the rule-matching loop, which meant it only ran for an
        order that matched a rule. A server with no routing rules configured - the state
        a freshly seeded one is in - falls through to `default_destination` and returned
        an instruction that had never been checked against the coverage account at all.
        The broker's 70/85/95% exposure limits therefore did not apply to exactly the
        configuration someone stands up first, and an unlimited B-Book position could be
        accumulated with no warning, no auto-hedge and no block.

        Thresholds, per the coverage account policy:
          70% -> warn, keep internalising
          85% -> divert to the A-Book LP gateway (auto-hedge)
          95% -> block the order
        """
        instruction = ExecutionInstruction(
            destination=destination,
            rule_id=rule_id,
            gateway_id=gateway_id,
            coverage_account_id=coverage_id,
            reason=reason,
        )

        if destination != ExecutionDestination.B_BOOK or coverage_account is None:
            return instruction

        ratio = coverage_account.get_exposure_ratio(order.symbol, order.volume.value)

        if ratio >= Decimal('0.95'):
            logger.error(
                f"Order {order.ticket_id} blocked: NOP ratio {ratio:.2%} exceeded 95% "
                f"threshold for {order.symbol}"
            )
            return ExecutionInstruction(
                destination=ExecutionDestination.REJECT,
                rule_id=rule_id,
                gateway_id=gateway_id,
                coverage_account_id=coverage_id,
                reason=f"NOP threshold 95% block limit exceeded ({ratio:.2%})",
            )

        if ratio >= Decimal('0.85'):
            logger.warning(
                f"Order {order.ticket_id} auto-hedged: NOP ratio {ratio:.2%} exceeded 85% "
                f"trigger for {order.symbol}"
            )
            return ExecutionInstruction(
                destination=ExecutionDestination.A_BOOK,
                rule_id=rule_id,
                gateway_id=gateway_id,
                coverage_account_id=coverage_id,
                reason=f"NOP threshold 85% breached ({ratio:.2%}) -> Auto-Hedge to A-Book",
            )

        if ratio >= Decimal('0.70'):
            logger.warning(
                f"NOP warning: Order {order.ticket_id} ratio {ratio:.2%} reached 70% "
                f"threshold for {order.symbol}"
            )

        return instruction

    def _select_lp_gateway(self, rule: Optional[RoutingRule], account: Account) -> str:
        """Selects LP gateway based on rule or group LP priority list."""
        if rule and rule.gateway_id:
            return rule.gateway_id
        if account and account.group and hasattr(account.group, 'routing') and account.group.routing.lp_priority:
            return account.group.routing.lp_priority[0]
        return "DEFAULT_LP_GATEWAY"

    def _matches(self, rule: RoutingRule, order: Order, account: Account) -> bool:
        """
        Check if order/account matches all rule filters.

        Returns True only if ALL specified filters match.
        None filters are ignored (wildcard).
        Supports MT5-style wildcards like 'real_*' and 'EUR*' using fnmatch.
        """
        # 1. Group Filter (supports wildcards)
        if rule.group_filter is not None:
            if not fnmatch.fnmatch(account.group.name, rule.group_filter):
                return False

        # 2. Symbol Filter (supports wildcards)
        if rule.symbol_filter is not None:
            if not fnmatch.fnmatch(order.symbol, rule.symbol_filter):
                return False

        # 3. Volume Min Filter
        if rule.volume_min is not None:
            if order.volume.value < rule.volume_min:
                return False

        # 4. Volume Max Filter
        if rule.volume_max is not None:
            if order.volume.value > rule.volume_max:
                return False

        return True

