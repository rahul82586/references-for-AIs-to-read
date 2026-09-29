"""M9 patch part 2: imports, counts wiring, ExpirationWorker, expiration passthrough."""
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


# --- 1. trading_setup imports ---------------------------------------------------
apply("application/di/trading_setup.py", [
    (
        "from application.commands.create_order import CreateOrderHandler\n",
        "from application.commands.close_position import ClosePositionHandler\n"
        "from application.commands.create_order import CreateOrderHandler\n",
    ),
    (
        "from application.workers.liquidation_worker import LiquidationWorker\n",
        "from application.workers.liquidation_worker import LiquidationWorker\n"
        "from application.workers.sltp_worker import SlTpWorker\n",
    ),
])

# --- 2. counts_fn definition + router wiring -------------------------------------
src, nl = read("application/di/trading_setup.py")


def rep(old, new):
    global src
    if nl == "\r\n":
        old = old.replace("\n", "\r\n")
        new = new.replace("\n", "\r\n")
    assert src.count(old) == 1, f"anchor {src.count(old)}x: {old[:70]!r}"
    src = src.replace(old, new)


rep(
    '        def _client_quote_with_point(symbol_name, account_login):\n',
    '''        def _position_counts(login, symbol_name):
            """(open positions total, open in symbol) from the ConfigCache -
            the synchronous counts view routing conditions 4005/4006 need (M9).
            The cache refreshes on DealCreated/PositionClosed (see config_cache)."""
            try:
                login = int(login)
            except (TypeError, ValueError):
                return None, None
            positions = config_cache.get_positions_by_account(login)
            return len(positions), sum(1 for p in positions if p.symbol == symbol_name)

        def _client_quote_with_point(symbol_name, account_login):
''',
)

rep(
    """        client_quote_fn=(
            _client_quote_with_point if config_cache is not None and quote_provider is not None else None
        ),
    )
""",
    """        client_quote_fn=(
            _client_quote_with_point if config_cache is not None and quote_provider is not None else None
        ),
        counts_fn=(_position_counts if config_cache is not None else None),
    )
""",
)
write("application/di/trading_setup.py", src, nl)
print("trading_setup: counts_fn wired")

# --- 3. api/main: ExpirationWorker ------------------------------------------------
apply("api/main.py", [
    (
        "from core.ports.interfaces import (\n"
        "    IGroupRepository, IAccountRepository, ISymbolRepository, \n"
        "    IHolidayRepository, IPositionRepository, IEventBus\n"
        ")\n",
        "from core.ports.interfaces import (\n"
        "    IGroupRepository, IAccountRepository, ISymbolRepository, \n"
        "    IHolidayRepository, IPositionRepository, IEventBus, IOrderRepository\n"
        ")\n",
    ),
    (
        "            # 4b. Price source (M5).",
        '''            # 4a2. Expiration worker (M9): pending orders carrying a GTD
            #      expiration are cancelled when their time passes - including
            #      times that passed while the server was down (the first sweep
            #      is immediate). Time-based, not tick-based: expirations must
            #      fire in a quiet market too.
            from application.workers.expiration_worker import ExpirationWorker

            expiration_worker = ExpirationWorker(
                order_repo=container.resolve(IOrderRepository),
                event_bus=event_bus,
            )
            app.state.expiration_worker = expiration_worker
            app.state.expiration_worker_task = asyncio.create_task(expiration_worker.start())

            # 4b. Price source (M5).''',
    ),
    (
        '        swap_worker = getattr(app.state, "swap_worker", None)',
        '''        expiration_worker = getattr(app.state, "expiration_worker", None)
        if expiration_worker is not None:
            try:
                await expiration_worker.stop()
                task = getattr(app.state, "expiration_worker_task", None)
                if task is not None and not task.done():
                    task.cancel()
                logger.info("ExpirationWorker stopped")
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Error stopping ExpirationWorker: {e}")

        swap_worker = getattr(app.state, "swap_worker", None)''',
    ),
])

# --- 4. expiration end-to-end: command -> entity -> schema -> router ---------------
apply("application/commands/create_order.py", [
    (
        '    comment: str = ""\n    reason: OrderReason = OrderReason.CLIENT\n',
        '    comment: str = ""\n    reason: OrderReason = OrderReason.CLIENT\n'
        "    #: GTD expiration (UTC). The ExpirationWorker cancels the pending order\n"
        "    #: when this time passes (M9); None = good-till-cancelled.\n"
        "    expiration: Optional[datetime] = None\n",
    ),
    (
        "            price_sl=Price(command.stop_loss) if command.stop_loss else None,\n"
        "            price_tp=Price(command.take_profit) if command.take_profit else None,\n",
        "            price_sl=Price(command.stop_loss) if command.stop_loss else None,\n"
        "            price_tp=Price(command.take_profit) if command.take_profit else None,\n"
        "            time_expiration=command.expiration,\n",
    ),
])

apply("api/schemas/trade.py", [(
    "    comment: Optional[str] = Field(None, max_length=256)\n",
    "    comment: Optional[str] = Field(None, max_length=256)\n"
    "    expiration: Optional[datetime] = Field(\n"
    '        None, description="GTD expiration (UTC): a pending order is cancelled when this time passes"\n'
    "    )\n",
)])

apply("api/routers/trade.py", [(
    "        comment=request.comment\n    )\n",
    "        comment=request.comment,\n        expiration=request.expiration\n    )\n",
)])

# --- 5. Sql find_expired_orders: the real state names ------------------------------
apply("infrastructure/persistence/repositories/order_repository.py", [(
    '                    (OrderModel.state.in_(["NEW", "PLACED", "PARTIALLY_FILLED"]))\n',
    '                    (OrderModel.state.in_(["STARTED", "NEW", "PLACED", "PARTIALLY_FILLED"]))\n',
)])

# --- 6. Harness double --------------------------------------------------------------
apply("tests/integration/trading_harness.py", [(
    '''class InMemoryOrderRepository:
    def __init__(self) -> None:
        self.orders: Dict[str, Order] = {}
        self.save_count = 0
''',
    '''class InMemoryOrderRepository:
    def __init__(self) -> None:
        self.orders: Dict[str, Order] = {}
        self.save_count = 0

    async def find_expired_orders(self, before_time: Any, session: Any = None) -> List[Order]:
        """Mirrors SqlOrderRepository: pendings whose expiration has passed."""
        from core.domains.oms.enums import OrderState

        return [
            o for o in self.orders.values()
            if o.time_expiration is not None
            and o.time_expiration < before_time
            and o.state in (OrderState.PLACED, OrderState.PARTIALLY_FILLED)
        ]
''',
)])

print("part 2 applied")
