"""M8 patch C: wire the routing table + shared client quotes + CLI import."""
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


# --- 1. trading_setup: shared provider, mt5 repo, quote fn ---------------------
apply("application/di/trading_setup.py", [
    (
        """        quote_provider = build_client_quote_provider(
            config_cache=config_cache,
            market_data_engine=market_data_engine,
        )
""",
        """        quote_provider = build_client_quote_provider(
            config_cache=config_cache,
            market_data_engine=market_data_engine,
        )

        def _client_quote_with_point(symbol_name, account_login):
            \"\"\"(bid, ask, point) for the routing conditions that measure in points
            (MARKET_DEVIATION, SYMBOL_SPREAD). One resolver feeds the matching
            engine, the risk price and the router, so all three see ONE price.\"\"\"
            from decimal import Decimal as _Dec

            quote = quote_provider(symbol_name, account_login)
            if quote is None:
                return None
            sym = config_cache.get_symbol(symbol_name)
            point = getattr(sym, "tick_size", None) or _Dec("0.00001")
            return (quote[0], quote[1], _Dec(str(point)))
""",
    ),
    (
        """    router = SmartOrderRouter(
        routing_rule_repo=routing_rule_repo,
        default_destination=default_destination,
        coverage_repo=coverage_repo,
    )
""",
        """    router = SmartOrderRouter(
        routing_rule_repo=routing_rule_repo,
        default_destination=default_destination,
        coverage_repo=coverage_repo,
        mt5_routing_repo=_resolve(container, "mt5_routing_repo", required=False),
        client_quote_fn=(
            _client_quote_with_point if config_cache is not None and quote_provider is not None else None
        ),
    )
""",
    ),
    (
        """    create_order_handler = CreateOrderHandler(
        account_repo=account_repo,
        symbol_repo=symbol_repo,
        order_repo=order_repo,
        position_repo=position_repo,
        risk_service=risk_service,
        event_bus=event_bus,
        market_feed=market_data_engine,
    )
""",
        """    create_order_handler = CreateOrderHandler(
        account_repo=account_repo,
        symbol_repo=symbol_repo,
        order_repo=order_repo,
        position_repo=position_repo,
        risk_service=risk_service,
        event_bus=event_bus,
        market_feed=market_data_engine,
        quote_provider=quote_provider,
    )
""",
    ),
])

# --- 2. quote_provider must exist even without config_cache (name defined) ----
src, nl = read("application/di/trading_setup.py")
probe = "    quote_provider = None\n"
if src.count(probe) != 1:
    raise SystemExit(f"quote_provider init anchor found {src.count(probe)}x")
print("trading_setup: quote_provider initialised before the cache branch (ok)")

# --- 3. harness double ----------------------------------------------------------
apply("tests/integration/trading_harness.py", [
    (
        """class InMemoryHolidayRepository:""",
        """class InMemoryRoutingMt5Repository:
    \"\"\"Mirrors SqlRoutingMt5Repository: decoded rules in table order.\"\"\"

    def __init__(self, rules=None) -> None:
        self.rules = list(rules or [])

    async def get_all_ordered(self, session: Any = None):
        return sorted(self.rules, key=lambda r: r.position)

    async def upsert(self, rule, record=None, session: Any = None):
        self.rules = [r for r in self.rules if r.name != rule.name]
        self.rules.append(rule)
        return rule


class InMemoryHolidayRepository:""",
    ),
    (
        """        coverage: Optional[List[CoverageAccount]] = None,
        lp_strict: bool = True,
    ) -> None:
""",
        """        coverage: Optional[List[CoverageAccount]] = None,
        lp_strict: bool = True,
        mt5_rules: Optional[List[Any]] = None,
    ) -> None:
""",
    ),
    (
        """        self.holiday_repo = InMemoryHolidayRepository()
""",
        """        self.holiday_repo = InMemoryHolidayRepository()
        self.mt5_routing_repo = InMemoryRoutingMt5Repository(mt5_rules)
""",
    ),
    (
        '''            "holiday_repo": self.holiday_repo,
''',
        '''            "holiday_repo": self.holiday_repo,
            "mt5_routing_repo": self.mt5_routing_repo,
''',
    ),
])

# --- 4. cli seed --mt5-routing ---------------------------------------------------
apply("cli/main.py", [
    (
        '''    mt5_symbols: Optional[str] = typer.Option(
        None, "--mt5-symbols",
        help="Import symbols from a real MT5 Administrator export (JSON) instead of YAML",
    ),
) -> None:
''',
        '''    mt5_symbols: Optional[str] = typer.Option(
        None, "--mt5-symbols",
        help="Import symbols from a real MT5 Administrator export (JSON) instead of YAML",
    ),
    mt5_routing: Optional[str] = typer.Option(
        None, "--mt5-routing",
        help="Import the ConfigRouting table from a real MT5 Administrator export (JSON)",
    ),
) -> None:
''',
    ),
    (
        '    raise SystemExit(_run(_run_seed(mt5_groups, mt5_symbols, True)))\n',
        '    raise SystemExit(_run(_run_seed(mt5_groups, mt5_symbols, mt5_routing, True)))\n',
    ),
    (
        '''async def _run_seed(
    mt5_groups: Optional[str], mt5_symbols: Optional[str], with_admin: bool
) -> int:
''',
        '''async def _run_seed(
    mt5_groups: Optional[str], mt5_symbols: Optional[str],
    mt5_routing: Optional[str], with_admin: bool,
) -> int:
''',
    ),
    (
        '''    await context["database"].close()

    table = Table(title="Seed report")
''',
        '''    routing_rules = 0
    if mt5_routing:
        from infrastructure.config.loader import routes_from_mt5

        mt5_routing_repo = providers.get("mt5_routing_repo")
        if mt5_routing_repo is None:
            console.print("[red]no mt5_routing_repo is wired; cannot import routing rules[/red]")
            await context["database"].close()
            return 2
        imported = routes_from_mt5(mt5_routing)
        for rule, record in imported:
            await mt5_routing_repo.upsert(rule, record)
        routing_rules = len(imported)

    await context["database"].close()

    table = Table(title="Seed report")
''',
    ),
    (
        '''    table.add_row("coverage risk accounts", str(report.coverage_risk_accounts))
''',
        '''    table.add_row("coverage risk accounts", str(report.coverage_risk_accounts))
    if mt5_routing:
        table.add_row("mt5 routing rules", str(routing_rules))
''',
    ),
])

print("patch C applied")
