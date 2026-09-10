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
        coverage_repo: Optional[Any] = None
    ):
        self.repo = routing_rule_repo
        self.default_destination = default_destination
        self.coverage_repo = coverage_repo
        self.rules: List[RoutingRule] = []
        #: distinguishes "no rules configured" from "nobody ever loaded the rules", which
        #: need opposite responses - see route().
        self._rules_loaded = False
        logger.info("SmartOrderRouter initialized with dynamic rule loading and NOP monitoring")

    async def refresh_rules(self):
        """Reload routing rules from repository. Call this on startup and periodically."""
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

