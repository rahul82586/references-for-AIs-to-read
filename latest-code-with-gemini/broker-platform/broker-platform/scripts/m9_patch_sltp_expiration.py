"""M9 patch: SL/TP carry + triggers, expiration, routing counts, wiring."""
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


# --- 0. worker: idempotent subscribe ------------------------------------------
if "_subscribed" not in io.open("application/workers/sltp_worker.py", encoding="utf-8").read():
        apply("application/workers/sltp_worker.py", [
        (
            "        self._running = False\n        self._in_flight: Set[str] = set()\n",
            "        self._running = False\n        self._subscribed = False\n        self._in_flight: Set[str] = set()\n",
        ),
        (
            """    async def start(self) -> None:
            \"\"\"Subscribe to the tick stream. Registration is synchronous on both buses.\"\"\"
            self._running = True
            self.event_bus.subscribe(EventType.TICK_RECEIVED, self.on_tick_event)
            logger.info("SlTpWorker subscribed to TICK_RECEIVED (server-side SL/TP armed)")
    """,
            """    async def start(self) -> None:
            \"\"\"Subscribe to the tick stream (once). Registration is synchronous on both buses.\"\"\"
            self._running = True
            if not self._subscribed:
                self.event_bus.subscribe(EventType.TICK_RECEIVED, self.on_tick_event)
                self._subscribed = True
            logger.info("SlTpWorker subscribed to TICK_RECEIVED (server-side SL/TP armed)")
    """,
        ),
    ])

# --- 1. OrderReason gains the trigger reasons (MT5 EnOrderReason) ---------------
apply("core/domains/oms/enums.py", [(
    '    MOBILE = "MOBILE"             # Mobile terminal\n',
    '''    MOBILE = "MOBILE"             # Mobile terminal
    SL = "SL"                   # Stop Loss triggered (server-side, M9)
    TP = "TP"                   # Take Profit triggered (server-side, M9)
    SO = "SO"                   # Stop Out (liquidation worker)
''',
)])

# --- 2. ClosePositionCommand carries the trigger reason -------------------------
apply("application/commands/close_position.py", [
    (
        '''    volume: Optional[Decimal] = None  # None = close full position
    price: Optional[Decimal] = None  # None = use current market price
    comment: str = ""
''',
        '''    volume: Optional[Decimal] = None  # None = close full position
    price: Optional[Decimal] = None  # None = use current market price
    comment: str = ""
    #: "SL" / "TP" / "SO" when a server-side trigger closed the position (M9);
    #: empty means a client/dealer close. Flows onto the closing deal AND order
    #: reasons, so statements say why the position closed.
    reason: str = ""
''',
    ),
    (
        '''        # 5. Create closing order
        closing_order = Order(
''',
        '''        # 5. Create closing order
        reason_name = (command.reason or "").upper()
        deal_reason = (
            DealReason[reason_name] if reason_name in DealReason.__members__ else DealReason.CLIENT
        )
        order_reason = (
            OrderReason[reason_name] if reason_name in OrderReason.__members__ else OrderReason.CLIENT
        )
        closing_order = Order(
''',
    ),
    (
        "            reason=OrderReason.CLIENT,\n",
        "            reason=order_reason,\n",
    ),
    (
        "            reason=DealReason.CLIENT,\n",
    "            reason=deal_reason,\n",
    ),
])

# --- 3. record_deal: positions inherit the opening order's SL/TP ----------------
apply("application/commands/record_deal.py", [
    (
        "        await self._apply_deal_to_positions(account, deal, position_repo=position_repo, session=session)\n",
        "        await self._apply_deal_to_positions(account, deal, order=order, position_repo=position_repo, session=session)\n",
    ),
    (
        "    async def _apply_deal_to_positions(self, account: Account, deal: Deal, position_repo=None, session=None):\n",
        "    async def _apply_deal_to_positions(self, account: Account, deal: Deal, order=None, position_repo=None, session=None):\n",
    ),
    (
        "            await self._apply_deal_netting_mode(account, deal, symbol, position_repo=pos_repo, session=session)\n",
        "            await self._apply_deal_netting_mode(account, deal, symbol, order=order, position_repo=pos_repo, session=session)\n",
    ),
    (
        "            await self._apply_deal_hedging_mode(account, deal, symbol, position_repo=pos_repo, session=session)\n",
        "            await self._apply_deal_hedging_mode(account, deal, symbol, order=order, position_repo=pos_repo, session=session)\n",
    ),
    (
        "    async def _apply_deal_hedging_mode(self, account: Account, deal: Deal, symbol, position_repo=None, session=None):\n",
        "    async def _apply_deal_hedging_mode(self, account: Account, deal: Deal, symbol, order=None, position_repo=None, session=None):\n",
    ),
    (
        "    async def _apply_deal_netting_mode(self, account: Account, deal: Deal, symbol, position_repo=None, session=None):\n",
        "    async def _apply_deal_netting_mode(self, account: Account, deal: Deal, symbol, order=None, position_repo=None, session=None):\n",
    ),
    (
        """            action=position_action_for(deal.deal_type),
            price_open=deal.price,
            contract_size=symbol.contract_size,
            time_create=datetime.now(timezone.utc)
        )
""",
        """            action=position_action_for(deal.deal_type),
            price_open=deal.price,
            contract_size=symbol.contract_size,
            time_create=datetime.now(timezone.utc),
            # M9: the opening order's SL/TP transfer onto the position. They were
            # dropped here before - a client's stop existed on the order, never on
            # the position, and nothing server-side could ever fire it.
            price_sl=order.price_sl if order is not None else None,
            price_tp=order.price_tp if order is not None else None,
        )
""",
    ),
    (
        """                        volume=Volume(new_vol),
                        action=deal_side,
                        price_open=deal.price,
                        contract_size=symbol.contract_size,
                        time_create=datetime.now(timezone.utc)
""",
        """                        volume=Volume(new_vol),
                        action=deal_side,
                        price_open=deal.price,
                        contract_size=symbol.contract_size,
                        time_create=datetime.now(timezone.utc),
                        price_sl=order.price_sl if order is not None else None,
                        price_tp=order.price_tp if order is not None else None,
""",
    ),
])

# --- 4. ConfigCache: trading events refresh the positions slice ------------------
apply("application/cache/config_cache.py", [
    (
        "        self.event_bus.subscribe(HolidayUpdated, self._on_holiday_updated)\n",
        """        self.event_bus.subscribe(HolidayUpdated, self._on_holiday_updated)
        # M9: fills and closes refresh this account's positions slice, so the
        # synchronous reads (routing conditions 4005/4006, the positions API's
        # cache path) see the book as it is, not as it was at boot. Class-based
        # subscription reaches in-process publishers; cross-process cache
        # invalidation arrives with the cluster milestone (documented).
        from core.events.domain_events import DealCreated, PositionClosed

        self.event_bus.subscribe(DealCreated, self._on_positions_changed)
        self.event_bus.subscribe(PositionClosed, self._on_positions_changed)
""",
    ),
    (
        "    def get_position(self, position_id: str) -> Optional[Position]:\n",
        '''    async def _on_positions_changed(self, event: Any) -> None:
        """Re-read one account's open positions after a fill or a close."""
        login = self._login_from_event(event)
        if login is None:
            return
        try:
            positions = await self.position_repo.get_positions_by_account(login)
        except Exception:  # noqa: BLE001 - the cache must never kill the bus
            logger.exception("could not refresh positions for account %s", login)
            return
        for pid in self._positions_by_account.pop(login, []):
            stale = self._positions.pop(pid, None)
            if stale is not None:
                ids = self._positions_by_symbol.get(stale.symbol)
                if ids and pid in ids:
                    ids.remove(pid)
        for position in positions:
            self._positions[position.position_id] = position
            self._positions_by_account.setdefault(login, []).append(position.position_id)
            self._positions_by_symbol.setdefault(position.symbol, []).append(position.position_id)

    @staticmethod
    def _login_from_event(event: Any) -> Optional[int]:
        """account_login from either bus shape: the event object or the dict."""
        payload = getattr(event, "payload", None)
        if payload is None and isinstance(event, dict):
            inner = event.get("payload")
            payload = inner if isinstance(inner, dict) else event
        if not isinstance(payload, dict):
            return None
        raw = payload.get("account_login")
        try:
            return int(raw) if raw is not None else None
        except (TypeError, ValueError):
            return None

    def get_position(self, position_id: str) -> Optional[Position]:
''',
    ),
])

# --- 5. Router: synchronous counts for the position conditions -------------------
apply("core/domains/execution/router.py", [
    (
        "        mt5_routing_repo: Optional[Any] = None,\n        client_quote_fn: Optional[Any] = None,\n    ):\n",
        "        mt5_routing_repo: Optional[Any] = None,\n        client_quote_fn: Optional[Any] = None,\n        counts_fn: Optional[Any] = None,\n    ):\n",
    ),
    (
        "        self._client_quote_fn = client_quote_fn\n",
        """        self._client_quote_fn = client_quote_fn
        #: (login, symbol) -> (open positions total, open positions in symbol),
        #: synchronous, for routing conditions 4005/4006. Order counts (4007/8)
        #: have no synchronous source yet and stay unmatched (documented).
        self._counts_fn = counts_fn
""",
    ),
    (
        """        ctx = RoutingRequestContext(
            request_flags=int(
""",
        """        positions_total = positions_symbol = None
        if self._counts_fn is not None:
            try:
                positions_total, positions_symbol = self._counts_fn(account.login, order.symbol)
            except Exception as exc:  # noqa: BLE001 - counts degrade to unmatched
                logger.warning("position counts for routing failed: %s", exc)

        ctx = RoutingRequestContext(
            request_flags=int(
""",
    ),
    (
        "            margin_level=getattr(account, \"margin_level\", None),\n        )\n        return RoutingEngine().evaluate(ctx, self.mt5_rules)\n",
        "            margin_level=getattr(account, \"margin_level\", None),\n            positions_total=positions_total,\n            positions_symbol=positions_symbol,\n        )\n        return RoutingEngine().evaluate(ctx, self.mt5_rules)\n",
    ),
])

# --- 6. trading_setup: close handler + SL/TP worker + counts ---------------------
apply("application/di/trading_setup.py", [
    (
        """        market_feed=market_data_engine,
        quote_provider=quote_provider,
    )
""",
        """        market_feed=market_data_engine,
        quote_provider=quote_provider,
    )

    # M9: the close handler with the risk engine (converted realised PnL) is
    # built ONCE, here: the SL/TP worker fires through it, and registering it
    # in as_providers finally gives the manager OrderClose endpoint a handler
    # (it fail-loud-refused before: nothing anywhere registered one).
    close_position_handler = ClosePositionHandler(
        account_repo=account_repo,
        position_repo=position_repo,
        order_repo=order_repo,
        deal_repo=deal_repo,
        event_bus=event_bus,
        risk_engine=risk_engine,
    )
    sltp_worker = SlTpWorker(
        position_repo=position_repo,
        close_position_handler=close_position_handler,
        event_bus=event_bus,
    )
""",
    ),
    (
        """    symbol_view: Optional[Any] = None
""",
        """    symbol_view: Optional[Any] = None
    #: M9: server-side SL/TP triggers, and the risk-engine-carrying close
    #: handler they (and the manager OrderClose endpoint) fire through.
    sltp_worker: Optional[Any] = None
    close_position_handler: Optional[Any] = None
""",
    ),
    (
        """            "matching_engine": self.matching_engine,
            "liquidity_gateway": self.liquidity_gateway,
""",
        """            "matching_engine": self.matching_engine,
            "liquidity_gateway": self.liquidity_gateway,
            "close_position_handler": self.close_position_handler,
            "sltp_worker": self.sltp_worker,
""",
    ),
    (
        """        market_data_engine=market_data_engine,
        symbol_view=symbol_view,
        warnings=warnings,
    )
""",
        """        market_data_engine=market_data_engine,
        symbol_view=symbol_view,
        sltp_worker=sltp_worker,
        close_position_handler=close_position_handler,
        warnings=warnings,
    )
""",
    ),
    (
        """    bus = stack.event_bus
""",
        """    bus = stack.event_bus

    # M9: server-side SL/TP. The worker subscribes to TICK_RECEIVED (idempotent
    # start) and closes triggered positions through the close handler.
    if stack.sltp_worker is not None:
        await stack.sltp_worker.start()
""",
    ),
])

print("part 1 applied")
