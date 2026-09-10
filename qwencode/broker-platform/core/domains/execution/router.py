"""
Smart Order Router (SOR).

This module implements the logic to evaluate an approved Order against
active RoutingRules and determine the execution destination.

Architectural Purpose:
Decouples the decision logic (WHERE to send) from the execution logic (HOW to send).
Allows dynamic reconfiguration of routing rules without changing core code.
"""
from typing import List, Optional
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
        logger.info("SmartOrderRouter initialized with dynamic rule loading and NOP monitoring")

    async def refresh_rules(self):
        """Reload routing rules from repository. Call this on startup and periodically."""
        self.rules = await self.repo.get_active_rules()
        self.rules = sorted(self.rules, key=lambda r: r.priority, reverse=True)
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
        if not self.rules:
            # Auto-refresh if rules haven't been loaded yet
            raise RuntimeError("Routing rules not loaded. Call refresh_rules() first.")

        logger.debug(f"Routing order {order.ticket_id} for account {account.login_id}")

        for rule in self.rules:
            if not rule.is_enabled:
                continue

            if self._matches(rule, order, account):
                dest = rule.destination
                gateway_id = rule.gateway_id or self._select_lp_gateway(rule, account)
                coverage_id = rule.coverage_account_id or "DEFAULT_COVERAGE"

                # Check Coverage Account NOP limits if routing to B-Book
                if dest == ExecutionDestination.B_BOOK and coverage_account:
                    ratio = coverage_account.get_exposure_ratio(order.symbol, order.volume.value)

                    if ratio >= Decimal('0.95'):
                        logger.error(f"Order {order.ticket_id} blocked: NOP ratio {ratio:.2%} exceeded 95% threshold for {order.symbol}")
                        return ExecutionInstruction(
                            destination=ExecutionDestination.REJECT,
                            rule_id=rule.rule_id,
                            reason=f"NOP threshold 95% block limit exceeded ({ratio:.2%})"
                        )
                    elif ratio >= Decimal('0.85'):
                        logger.warning(f"Order {order.ticket_id} auto-hedged: NOP ratio {ratio:.2%} exceeded 85% trigger for {order.symbol}")
                        return ExecutionInstruction(
                            destination=ExecutionDestination.A_BOOK,
                            rule_id=rule.rule_id,
                            gateway_id=gateway_id,
                            coverage_account_id=coverage_id,
                            reason=f"NOP threshold 85% breached ({ratio:.2%}) -> Auto-Hedge to A-Book"
                        )
                    elif ratio >= Decimal('0.70'):
                        logger.warning(f"NOP warning: Order {order.ticket_id} ratio {ratio:.2%} reached 70% threshold for {order.symbol}")

                logger.info(
                    f"Order {order.ticket_id} matched rule '{rule.rule_id}' "
                    f"-> Destination: {dest.value}"
                )
                return ExecutionInstruction(
                    destination=dest,
                    rule_id=rule.rule_id,
                    gateway_id=gateway_id,
                    coverage_account_id=coverage_id,
                    reason=f"Matched rule: {rule.rule_id}"
                )

        # Fallback to default
        fallback_gateway = self._select_lp_gateway(None, account)
        logger.warning(
            f"No routing rule matched for order {order.ticket_id}. "
            f"Using default: {self.default_destination.value}"
        )
        return ExecutionInstruction(
            destination=self.default_destination,
            rule_id="DEFAULT_FALLBACK",
            gateway_id=fallback_gateway,
            reason="No matching rule found"
        )

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

