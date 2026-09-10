import io

p = "tests/integration/trading_harness.py"
s = io.open(p, encoding="utf-8").read()

# symbol repo: ConfigCache calls get_all()
s = s.replace('''    async def get_all_symbols(self, session: Any = None) -> List[Symbol]:
        return list(self.symbols.values())''', '''    async def get_all_symbols(self, session: Any = None) -> List[Symbol]:
        return list(self.symbols.values())

    async def get_all(self, session: Any = None) -> List[Symbol]:
        """The name ConfigCache.initialize() calls."""
        return list(self.symbols.values())''', 1)

s = s.replace('''    async def get_all(self, session: Any = None) -> List[Group]:
        return list(self.groups.values())''', '''    async def get_all(self, session: Any = None) -> List[Group]:
        return list(self.groups.values())

    async def find_by_id(self, group_id: str, session: Any = None) -> Optional[Group]:
        return next((g for g in self.groups.values() if g.id == group_id), None)''', 1)

s = s.replace('''class InMemoryHolidayRepository:
    async def get_active_holidays(self, session: Any = None) -> List[Any]:
        return []''', '''class InMemoryHolidayRepository:
    async def get_all(self, session: Any = None) -> List[Any]:
        """The name ConfigCache.initialize() calls."""
        return []

    async def get_active_holidays(self, session: Any = None) -> List[Any]:
        return []''', 1)

s = s.replace('''        self.event_bus = InProcessEventBus()
        self.lp_strict = lp_strict
        self.stack = None
        self.market_data_engine = None''', '''        self.event_bus = InProcessEventBus()
        self.lp_strict = lp_strict
        self.stack = None
        self.market_data_engine = None
        self.config_cache = None''', 1)

s = s.replace('''        self.market_data_engine = MarketDataEngine(
            event_bus=self.event_bus, symbol_repo=self.symbol_repo
        )
        self.stack = await build_trading_stack(
            self.container,
            market_data_engine=self.market_data_engine,
            lp_strict=self.lp_strict,
        )
        return self''', '''        self.market_data_engine = MarketDataEngine(
            event_bus=self.event_bus, symbol_repo=self.symbol_repo
        )

        # ConfigCache, exactly as api/main.py builds it. RiskEngine reads symbols
        # synchronously on the hot path and cannot await a repository; skipping this
        # would make the tests pass against a wiring the server does not actually use.
        from application.cache.config_cache import ConfigCache, set_config_cache

        self.config_cache = ConfigCache(
            group_repo=self.group_repo,
            account_repo=self.account_repo,
            symbol_repo=self.symbol_repo,
            holiday_repo=self.holiday_repo,
            position_repo=self.position_repo,
            event_bus=self.event_bus,
        )
        await self.config_cache.initialize()
        set_config_cache(self.config_cache)

        self.stack = await build_trading_stack(
            self.container,
            market_data_engine=self.market_data_engine,
            config_cache=self.config_cache,
            lp_strict=self.lp_strict,
        )
        return self''', 1)

io.open(p, "w", encoding="utf-8").write(s)
print("harness patched")
