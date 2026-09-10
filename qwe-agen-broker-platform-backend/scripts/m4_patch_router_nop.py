import io

p = "core/domains/execution/router.py"
s = io.open(p, encoding="utf-8", newline="").read()
crlf = "\r\n" in s


def N(x):
    return x.replace("\n", "\r\n") if crlf else x


# --- 1. lift the NOP evaluation out of the rule loop -------------------------
old = N('''                dest = rule.destination
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
''')
assert old in s, "route() body not found"

new = N('''                gateway_id = rule.gateway_id or self._select_lp_gateway(rule, account)
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
''')
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="").write(s)
print("router: NOP applies to the fallback too")

# --- 2. the 85% test must start from a B-BOOK rule ---------------------------
p = "tests/integration/test_order_execution_e2e.py"
s = io.open(p, encoding="utf-8").read()
old = '''async def test_nop_at_85_percent_auto_hedges_to_a_book():
    """0.90 lots against a 1.0 lot NOP limit is 90% - past the 85% auto-hedge trigger."""
    h = await build_harness(
        rules=a_book_rule(gateway="LP_HEDGE"), coverage=coverage(nop_limit="1.0"), lp_strict=False
    )'''
assert old in s
new = '''async def test_nop_at_85_percent_auto_hedges_to_a_book():
    """0.90 lots against a 1.0 lot NOP limit is 90% - past the 85% auto-hedge trigger.

    The rule says B-Book; the coverage account overrides it. An A-Book rule would never
    reach the threshold check at all, since there is nothing to divert.
    """
    h = await build_harness(
        rules=[
            RoutingRule(
                rule_id="R-B-BOOK-EUR",
                priority=100,
                destination=ExecutionDestination.B_BOOK,
                symbol_filter="EUR*",
                gateway_id="LP_HEDGE",
            )
        ],
        coverage=coverage(nop_limit="1.0"),
        lp_strict=False,
    )'''
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("nop test corrected")
