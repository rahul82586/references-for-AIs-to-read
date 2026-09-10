import io

p = "tests/integration/trading_harness.py"
s = io.open(p, encoding="utf-8").read()

# --- container: a resolve()-capable view, like the API uses ------------------
old = '''    @property
    def container(self) -> Dict[str, Any]:
        """The DI container exactly as `setup_persistence_di` would have populated it."""
        return {
            "event_bus": self.event_bus,
            "group_repo": self.group_repo,
            "symbol_repo": self.symbol_repo,
            "account_repo": self.account_repo,
            "order_repo": self.order_repo,
            "deal_repo": self.deal_repo,
            "position_repo": self.position_repo,
            "routing_rule_repo": self.routing_rule_repo,
            "coverage_repo": self.coverage_repo,
            "holiday_repo": self.holiday_repo,
            "market_data_engine": self.market_data_engine,
        }
'''
assert old in s
new = '''    @property
    def providers(self) -> Dict[str, Any]:
        """The provider dict `setup_persistence_di` would have returned, plus whatever
        the trading stack registered back into it."""
        base = {
            "event_bus": self.event_bus,
            "group_repo": self.group_repo,
            "symbol_repo": self.symbol_repo,
            "account_repo": self.account_repo,
            "order_repo": self.order_repo,
            "deal_repo": self.deal_repo,
            "position_repo": self.position_repo,
            "routing_rule_repo": self.routing_rule_repo,
            "coverage_repo": self.coverage_repo,
            "holiday_repo": self.holiday_repo,
            "market_data_engine": self.market_data_engine,
        }
        base.update(self._registered)
        return base

    @property
    def container(self) -> Any:
        """A resolve()-capable view over the providers - the same class api/main.py uses.

        `build_market_data_stack` resolves by PORT CLASS (IPositionRepository, RiskEngine),
        so a plain dict is not enough. Using the real _ContainerView means these tests
        exercise the API's resolution path rather than a friendlier one invented for them.
        """
        from api.di_providers import _ContainerView

        return _ContainerView(self.providers)

    def register(self, providers: Dict[str, Any]) -> None:
        """Mirror register_di_providers(): put components back into the container."""
        self._registered.update(providers)
'''
s = s.replace(old, new, 1)

s = s.replace('''        self.config_cache = None''', '''        self.config_cache = None
        self._registered: Dict[str, Any] = {}
        self.tick_pipeline = None''', 1)

# --- build(): wire the market data plane too --------------------------------
old = '''        self.stack = await build_trading_stack(
            self.container,
            market_data_engine=self.market_data_engine,
            config_cache=self.config_cache,
            lp_strict=self.lp_strict,
        )
        return self'''
assert old in s
new = '''        self.stack = await build_trading_stack(
            self.container,
            market_data_engine=self.market_data_engine,
            config_cache=self.config_cache,
            lp_strict=self.lp_strict,
        )
        self.register(self.stack.as_providers())
        self.register({"market_data_engine": self.market_data_engine})

        # Market data plane, as api/main.py step 4 does it: tick -> position PnL ->
        # account equity -> the margin state machine -> MarginCallEntered/StopOutEntered.
        # Without it a crashing price updates nothing and the LiquidationWorker, which
        # only ever hears about a stop-out from this pipeline, never runs.
        from application.di.market_data_setup import build_market_data_stack

        components = build_market_data_stack(self.container)
        self.tick_pipeline = components.get("tick_pipeline")
        return self'''
s = s.replace(old, new, 1)

io.open(p, "w", encoding="utf-8").write(s)
print("harness: market data plane wired")
