import io

# ---------------------------------------------------------------------------
# The port: declare the async read the application layer actually calls
# ---------------------------------------------------------------------------
p = "core/ports/interfaces.py"
s = io.open(p, encoding="utf-8").read()

old = '''class ISymbolRepository(ABC, Generic[T]):
    """
    Contract for Symbol/Instrument persistence.

    Architectural Purpose:
    Provides access to instrument specifications (contract size, tick value, etc.)
    needed for margin and PnL calculations.
    """

    @abstractmethod
    def get_symbol(self, symbol_name: str) -> T:
        """Returns symbol specification by name."""
        pass
'''
assert old in s
new = '''class ISymbolRepository(ABC, Generic[T]):
    """
    Contract for Symbol/Instrument persistence.

    Architectural Purpose:
    Provides access to instrument specifications (contract size, tick value, etc.)
    needed for margin and PnL calculations.

    TWO READ SHAPES, ON PURPOSE. This is the one port in the platform with both, and
    conflating them is what broke the execution path:

      * `find_by_name` is the ASYNC database read. Application code - CreateOrderHandler,
        RecordDealHandler, LiquidationWorker, TickMarginPipeline, ConfigCache - awaits it.
      * `get_symbol` is the SYNCHRONOUS hot-path read. RiskEngine calls it while
        repricing every account on every tick and refuses a coroutine, because a margin
        snapshot cannot await. In production that is answered by ConfigCache, not by a
        repository; SqlSymbolRepository.get_symbol is async and RiskEngine rejects it,
        which is why build_trading_stack hands RiskEngine the cache.

    Before this was written down, the port declared only the synchronous `get_symbol`,
    the SQL repository implemented it as `async def`, and `find_by_name` was not declared
    at all - so five callers awaited a method the real repository did not have, and two
    others called the async one without awaiting and received a coroutine object instead
    of a Symbol.
    """

    @abstractmethod
    async def find_by_name(self, symbol_name: str) -> Optional[T]:
        """Async read of one symbol by name, or None if it is not configured."""
        pass

    @abstractmethod
    def get_symbol(self, symbol_name: str) -> T:
        """Synchronous hot-path read. Answered by ConfigCache in production."""
        pass
'''
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("port: find_by_name declared, sync/async split documented")

# ---------------------------------------------------------------------------
# The implementation: answer both names
# ---------------------------------------------------------------------------
p = "infrastructure/persistence/repositories/symbol_repository.py"
s = io.open(p, encoding="utf-8", newline="").read()
crlf = "\r\n" in s


def N(x):
    return x.replace("\n", "\r\n") if crlf else x


old = N('''    async def get_symbol(self, name: str) -> Optional[Symbol]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(SymbolModel).where(SymbolModel.name == name)
            )
            model = result.scalar_one_or_none()
            if not model:
                return None
            return db_to_symbol(model)
''')
assert old in s
new = N('''    async def get_symbol(self, name: str) -> Optional[Symbol]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(SymbolModel).where(SymbolModel.name == name)
            )
            model = result.scalar_one_or_none()
            if not model:
                return None
            return db_to_symbol(model)

    async def find_by_name(self, name: str, session: Optional[AsyncSession] = None) -> Optional[Symbol]:
        """The name the application layer calls: CreateOrderHandler, RecordDealHandler,
        LiquidationWorker, TickMarginPipeline and ConfigCache all await
        `symbol_repo.find_by_name(...)`.

        It did not exist here. The port declared only `get_symbol`, so this repository
        satisfied the contract while every one of those five callers raised
        AttributeError against it - which is why the order path had only ever been run
        against test doubles that defined the name the callers used. Same shape as the
        position repository's missing get_positions_by_account.

        Note this is ASYNC and so is not what RiskEngine wants on the hot path; it is
        given ConfigCache instead. See ISymbolRepository's docstring.
        """
        if session is not None:
            result = await session.execute(
                select(SymbolModel).where(SymbolModel.name == name)
            )
            model = result.scalar_one_or_none()
            return db_to_symbol(model) if model else None
        return await self.get_symbol(name)
''')
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="").write(s)
print("SqlSymbolRepository: find_by_name added")
