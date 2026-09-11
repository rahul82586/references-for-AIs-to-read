"""M8 patch B: the execution flow consults the MT5 routing table.

Layering: the MT5 table is REQUEST POLICY (reject / dealer / confirm / delay /
clear SLTP) and runs FIRST, top-down, exactly as MT5 does; the house rules
(A/B/ECN destination + NOP exposure thresholds) run underneath it, unchanged.
CONFIRM_CLIENT/CONFIRM_MARKET fall through to normal execution - that is what
"confirm the execution of an order at the price requested in it" MEANS for a
market-execution platform (the live export's `Auto Execution` rule is exactly
this). Non-terminal actions (delay, clear) accumulate onto whatever instruction
finally wins.

Also here: CreateOrderHandler prices market orders for the RISK CHECK through
the same client-quote provider the matching engine fills through (M7 gap #1:
margin was checked against raw ticks while fills happened at marked-up prices).
"""
import ast
import io
import pathlib


def read(path):
    p = pathlib.Path(path)
    src = io.open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in src else "\n"
    return src, nl


def write(path, src, nl):
    ast.parse(src.replace("\r\n", "\n") if nl == "\r\n" else src)
    io.open(path, "w", encoding="utf-8", newline="").write(src)


def apply(path, pairs):
    src, nl = read(path)
    for old, new in pairs:
        if nl == "\r\n":
            old = old.replace("\n", "\r\n")
            new = new.replace("\n", "\r\n")
        assert src.count(old) == 1, f"{path}: anchor {src.count(old)}x: {old[:70]!r}"
        src = src.replace(old, new)
    write(path, src, nl)
    print(f"{path}: {len(pairs)} patch(es)")


# --- 1. ExecutionInstruction carries the table's non-terminal effects ---------
apply("core/domains/execution/models.py", [(
    """    destination: ExecutionDestination
    rule_id: str
    gateway_id: Optional[str] = None
    coverage_account_id: Optional[str] = None  # Which CoverageAccount to use for B-Book
    reason: Optional[str] = None
""",
    """    destination: ExecutionDestination
    rule_id: str
    gateway_id: Optional[str] = None
    coverage_account_id: Optional[str] = None  # Which CoverageAccount to use for B-Book
    reason: Optional[str] = None
    #: M8: non-terminal MT5 routing effects that travel with the instruction:
    #: ACTION_DELAY_TIME milliseconds the orchestrator must wait before
    #: executing, and ACTION_DELAY_TICK (modelled; not executable inline -
    #: the orchestrator says so loudly rather than silently skipping).
    delay_ms: int = 0
    delay_ticks: int = 0
    mt5_rule: Optional[str] = None
""",
)])

# --- 2. SmartOrderRouter: the MT5 layer ---------------------------------------
apply("core/domains/execution/router.py", [
    (
        """    def __init__(
        self,
        routing_rule_repo: IRoutingRuleRepository,
        default_destination: ExecutionDestination = ExecutionDestination.B_BOOK,
        coverage_repo: Optional[Any] = None
    ):
        self.repo = routing_rule_repo
        self.default_destination = default_destination
        self.coverage_repo = coverage_repo
        self.rules: List[RoutingRule] = []
""",
        """    def __init__(
        self,
        routing_rule_repo: IRoutingRuleRepository,
        default_destination: ExecutionDestination = ExecutionDestination.B_BOOK,
        coverage_repo: Optional[Any] = None,
        mt5_routing_repo: Optional[Any] = None,
        client_quote_fn: Optional[Any] = None,
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
""",
    ),
    (
        """    async def refresh_rules(self):
        \"\"\"Reload routing rules from repository. Call this on startup and periodically.\"\"\"
        self.rules = await self.repo.get_active_rules()
""",
        """    async def refresh_rules(self):
        \"\"\"Reload routing rules from repository. Call this on startup and periodically.\"\"\"
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
""",
    ),
    (
        """    def route(
        self,
        order: Order,
        account: Account,
        coverage_account: Optional[Any] = None
    ) -> ExecutionInstruction:
        \"\"\"
        Evaluate rules and return where this order should go.
""",
        """    def route(
        self,
        order: Order,
        account: Account,
        coverage_account: Optional[Any] = None
    ) -> ExecutionInstruction:
        \"\"\"Route one order: the MT5 request-policy table first, then the house
        rules (destination selection + NOP exposure governance).

        MT5 evaluates its routing table top-down before execution; delay and
        clear-SL/TP actions are non-terminal and accumulate onto whatever
        instruction finally wins; CONFIRM_* falls through to normal execution,
        which is what "confirm at the requested/market price" means here.
        \"\"\"
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

        try:
            login = int(account.login)
        except (TypeError, ValueError):
            login = None

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
            margin_level=getattr(account, "margin_level", None),
        )
        return RoutingEngine().evaluate(ctx, self.mt5_rules)

    def _instruction_from_mt5(self, order: Order, decision) -> Optional[ExecutionInstruction]:
        \"\"\"Map a terminal MT5 action onto an ExecutionInstruction, or None to
        continue with house routing (CONFIRM_*, and DEALER-with-skip when no
        dealer session infrastructure exists).\"\"\"
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
        \"\"\"
        Evaluate rules and return where this order should go.
""",
    ),
])

# --- 3. orchestrator honours the delay ----------------------------------------
apply("application/services/execution_orchestrator.py", [(
    "        instruction = self.router.route(order, account, coverage_account=coverage_account)\n",
    """        instruction = self.router.route(order, account, coverage_account=coverage_account)

        # M8: ACTION_DELAY_TIME from the MT5 routing table. The delay happens
        # AFTER risk approval and BEFORE execution, which is where MT5 places it.
        if getattr(instruction, "delay_ms", 0):
            logger.info(
                "routing rule delays order %s by %d ms before execution",
                order_id, instruction.delay_ms,
            )
            await asyncio.sleep(instruction.delay_ms / 1000.0)
        if getattr(instruction, "delay_ticks", 0):
            logger.warning(
                "routing rule requested a %d-tick delay for order %s; tick delays "
                "are not executable inline and were skipped",
                instruction.delay_ticks, order_id,
            )
""",
)])
# orchestrator asyncio import
src = io.open("application/services/execution_orchestrator.py", encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in src else "\n"
if "import asyncio" not in src:
    src = src.replace("import logging" + nl, "import asyncio" + nl + "import logging" + nl, 1)
    ast.parse(src.replace(nl, "\n"))
    io.open("application/services/execution_orchestrator.py", "w", encoding="utf-8", newline="").write(src)
    print("orchestrator: asyncio imported")

# --- 4. create_order: the risk price is the CLIENT price ----------------------
apply("application/commands/create_order.py", [
    (
        """        event_bus: IEventBus,
        market_feed: Optional[Any] = None,
    ):""",
        """        event_bus: IEventBus,
        market_feed: Optional[Any] = None,
        quote_provider: Optional[Any] = None,
    ):""",
    ),
    (
        "        self.market_feed = market_feed\n",
        """        self.market_feed = market_feed
        #: M8 (closing M7 gap #1): the same client-quote provider the matching
        #: engine fills through, so pre-trade margin is checked against the
        #: price THIS client will actually trade at, not the raw feed.
        self._quote_provider = quote_provider
""",
    ),
    (
        """    async def _market_price(self, symbol_name: str, side: str) -> Price:
        \"\"\"Current execution price for a market order: BUY at the ask, SELL at the bid.

        Raises when there is no price. Filling at the order's own (zero) price, or at
        1.0, creates a position the client never agreed to and a margin requirement
        that is wrong by orders of magnitude.
        \"\"\"
        tick = await await_tick(self.market_feed, symbol_name)
""",
        """    async def _market_price(self, symbol_name: str, side: str, account_login: Optional[Any] = None) -> Price:
        \"\"\"Current execution price for a market order: BUY at the ask, SELL at the bid.

        Raises when there is no price. Filling at the order's own (zero) price, or at
        1.0, creates a position the client never agreed to and a margin requirement
        that is wrong by orders of magnitude.

        With a quote provider (M7/M8) the CLIENT price for this account is used:
        the risk check must see what the fill will charge. A provider refusal
        (stale quote) propagates - the order is rejected rather than risk-checked
        against a price the matching engine will not honour.
        \"\"\"
        if self._quote_provider is not None and account_login is not None:
            quote = self._quote_provider(symbol_name, account_login)
            if quote is not None:
                q_bid, q_ask = Decimal(str(quote[0])), Decimal(str(quote[1]))
                if side == "BUY" and q_ask > 0:
                    return Price(q_ask)
                if side != "BUY" and q_bid > 0:
                    return Price(q_bid)
        tick = await await_tick(self.market_feed, symbol_name)
""",
    ),
    (
        "                price_for_risk = await self._market_price(command.symbol, side)\n",
        "                price_for_risk = await self._market_price(command.symbol, side, command.account_login)\n",
    ),
])

print("patch B applied")
