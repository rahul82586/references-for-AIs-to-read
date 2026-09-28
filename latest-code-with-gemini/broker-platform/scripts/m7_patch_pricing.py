"""M7 patch: model the spread fields, inject the client quote provider.

1. Symbol entity + wire + columns + mappers: SpreadDiff/SpreadDiffBalance stop
   being quarantined (they were lossless on the wire but invisible to logic).
2. GroupSymbolOverride gains spread_diff_balance (the wire override records
   carry it; the loader's field iteration picks it up automatically).
3. BookMatchingEngine gains an optional quote_provider, consulted at the top
   of _quote_for - the single funnel every fill price flows through (market
   fills, limit/stop activation). The raw _quotes store stays raw: markup is
   per-group, the store is shared.
4. trading_setup wires the provider whenever a ConfigCache exists.
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


# --- 1. Symbol entity --------------------------------------------------------
apply("core/domains/instruments/symbol.py", [(
    """    spread: int = 0  # Current spread in points
    spread_balance: int = 0  # Balance spread in points
""",
    """    spread: int = 0  # Fixed spread in points; 0 = floating (MT5 Symbol Spread)
    spread_balance: int = 0  # Points of the FIXED spread placed below the bid
    #: MT5 SpreadDiff / SpreadDiffBalance at the SYMBOL level (group overrides
    #: live on GroupSymbolOverride). Modelled as of M7: before that they were
    #: quarantined - lossless on the wire, invisible to the pricing engine.
    spread_diff: int = 0
    spread_diff_balance: int = 0
""",
)])

# --- 2. GroupSymbolOverride VO ------------------------------------------------
apply("core/domains/accounts/value_objects.py", [(
    "    spread_diff: Optional[int] = None\n",
    """    spread_diff: Optional[int] = None
    #: Points of spread_diff placed on the BID side (the rest widen the ask).
    #: None = MT5's "default" sentinel = inherit the symbol's value.
    spread_diff_balance: Optional[int] = None
""",
)])

# --- 3. Fieldmap: un-quarantine (symbol table first, then the override table) --
apply("infrastructure/mt5/fieldmap.py", [
    (
        '    Field("SpreadDiff", "", INT),\n    Field("SpreadDiffBalance", "", INT),\n',
        '    Field("SpreadDiff", "spread_diff", INT),\n    Field("SpreadDiffBalance", "spread_diff_balance", INT),\n',
    ),
    (
        '    Field("SpreadDiffBalance", "", INT),\n',
        '    Field("SpreadDiffBalance", "spread_diff_balance", INT),\n',
    ),
])

# --- 4. Loader: YAML keys + parse ----------------------------------------------
apply("infrastructure/config/loader.py", [
    (
        '    "spread",\n    "spread_balance",\n',
        '    "spread",\n    "spread_balance",\n    "spread_diff",\n    "spread_diff_balance",\n',
    ),
    (
        '        spread_balance=_int(raw.get("spread_balance"), where, "spread_balance", 0),\n',
        '        spread_balance=_int(raw.get("spread_balance"), where, "spread_balance", 0),\n'
        '        spread_diff=_int(raw.get("spread_diff"), where, "spread_diff", 0),\n'
        '        spread_diff_balance=_int(raw.get("spread_diff_balance"), where, "spread_diff_balance", 0),\n',
    ),
])

# --- 5. SymbolModel columns -----------------------------------------------------
apply("infrastructure/persistence/config_models.py", [(
    "    spread = Column(Integer, nullable=False, default=0)\n"
    "    spread_balance = Column(Integer, nullable=False, default=0)\n",
    "    spread = Column(Integer, nullable=False, default=0)\n"
    "    spread_balance = Column(Integer, nullable=False, default=0)\n"
    "    spread_diff = Column(Integer, nullable=False, default=0)\n"
    "    spread_diff_balance = Column(Integer, nullable=False, default=0)\n",
)])

# --- 6. config_mappers: every hop of the round trip ------------------------------
apply("infrastructure/persistence/config_mappers.py", [
    (  # domain record for the codec
        '        "spread": _int(symbol.spread, 0),\n'
        '        "spread_balance": _int(symbol.spread_balance, 0),\n',
        '        "spread": _int(symbol.spread, 0),\n'
        '        "spread_balance": _int(symbol.spread_balance, 0),\n'
        '        "spread_diff": _int(symbol.spread_diff, 0),\n'
        '        "spread_diff_balance": _int(symbol.spread_diff_balance, 0),\n',
    ),
    (  # wire -> columns
        '        spread=_int(col("Spread", "0")),\n'
        '        spread_balance=_int(col("SpreadBalance", "0")),\n',
        '        spread=_int(col("Spread", "0")),\n'
        '        spread_balance=_int(col("SpreadBalance", "0")),\n'
        '        spread_diff=_int(col("SpreadDiff", "0")),\n'
        '        spread_diff_balance=_int(col("SpreadDiffBalance", "0")),\n',
    ),
    (  # owned wire keys
        '        "Spread",\n        "SpreadBalance",\n',
        '        "Spread",\n        "SpreadBalance",\n        "SpreadDiff",\n        "SpreadDiffBalance",\n',
    ),
    (  # columns -> wire record
        '        "Spread": str(_int(row.spread, 0)),\n'
        '        "SpreadBalance": str(_int(row.spread_balance, 0)),\n',
        '        "Spread": str(_int(row.spread, 0)),\n'
        '        "SpreadBalance": str(_int(row.spread_balance, 0)),\n'
        '        "SpreadDiff": str(_int(row.spread_diff, 0)),\n'
        '        "SpreadDiffBalance": str(_int(row.spread_diff_balance, 0)),\n',
    ),
    (  # wire record -> domain Symbol
        '        spread=_int(domain.get("spread"), 0),\n'
        '        spread_balance=_int(domain.get("spread_balance"), 0),\n',
        '        spread=_int(domain.get("spread"), 0),\n'
        '        spread_balance=_int(domain.get("spread_balance"), 0),\n'
        '        spread_diff=_int(domain.get("spread_diff"), 0),\n'
        '        spread_diff_balance=_int(domain.get("spread_diff_balance"), 0),\n',
    ),
    (  # group override serialization (domain shape -> codec)
        '                "spread_diff": INHERIT\n'
        '                if override.spread_diff is None\n'
        '                else _int(override.spread_diff, 0),\n',
        '                "spread_diff": INHERIT\n'
        '                if override.spread_diff is None\n'
        '                else _int(override.spread_diff, 0),\n'
        '                "spread_diff_balance": INHERIT\n'
        '                if override.spread_diff_balance is None\n'
        '                else _int(override.spread_diff_balance, 0),\n',
    ),
    (  # group override deserialization
        '                spread_diff=raw.get("spread_diff"),\n',
        '                spread_diff=raw.get("spread_diff"),\n'
        '                spread_diff_balance=raw.get("spread_diff_balance"),\n',
    ),
])

# --- 7. Matching engine: the provider hook --------------------------------------
apply("infrastructure/engines/book_matching_engine.py", [
    (
        """    def __init__(
        self,
        market_feed: Optional[Any] = None,
        symbol_repo: Optional[Any] = None,
        *,
        max_slippage_points: int = 0,
        event_bus: Optional[Any] = None,
    ) -> None:
        self.market_feed = market_feed
        self.symbol_repo = symbol_repo
""",
        """    def __init__(
        self,
        market_feed: Optional[Any] = None,
        symbol_repo: Optional[Any] = None,
        *,
        max_slippage_points: int = 0,
        event_bus: Optional[Any] = None,
        quote_provider: Optional[Any] = None,
    ) -> None:
        self.market_feed = market_feed
        self.symbol_repo = symbol_repo
        #: M7: optional (symbol, account_login) -> (client_bid, client_ask).
        #: Applies the group's spread transformation to the raw feed tick and
        #: refuses stale quotes. None keeps the pre-M7 behaviour: raw feed
        #: prices. The raw _quotes store is never marked up - the transform is
        #: per group, the store is shared.
        self._quote_provider = quote_provider
""",
    ),
    (
        '''    def _quote_for(self, symbol: str, order: Optional[Order] = None) -> tuple:
        """Resolve (bid, ask) for a symbol, or raise NoQuoteError."""
        tick = self._tick(symbol)
''',
        '''    def _quote_for(self, symbol: str, order: Optional[Order] = None) -> tuple:
        """Resolve (bid, ask) for a symbol, or raise NoQuoteError."""
        # M7: the client quote wins when a provider is wired. It may raise
        # NoQuoteError (a stale quote is a refusal, not a fallback); returning
        # None means "cannot tell" and the raw path below still raises its
        # honest error when there is genuinely nothing to trade on.
        if self._quote_provider is not None and order is not None:
            priced = self._quote_provider(symbol, getattr(order, "account_login", None))
            if priced is not None:
                client_bid, client_ask = Decimal(str(priced[0])), Decimal(str(priced[1]))
                if client_bid > 0 and client_ask >= client_bid:
                    return client_bid, client_ask

        tick = self._tick(symbol)
''',
    ),
])

# --- 8. trading_setup: wire it ---------------------------------------------------
apply("application/di/trading_setup.py", [(
    """    matching_engine = BookMatchingEngine(
        market_feed=market_data_engine,
        symbol_repo=symbol_repo,
        event_bus=event_bus,
    )
""",
    """    # M7: client pricing - group spread transforms (SpreadDiff/Balance, fixed
    # spreads) and stale-quote refusal, applied at the single funnel every fill
    # price flows through. Needs the ConfigCache for the synchronous group and
    # symbol lookups; without one the engine trades at raw feed prices, as
    # before, rather than guessing markups.
    quote_provider = None
    if config_cache is not None:
        from application.di.pricing_setup import build_client_quote_provider

        quote_provider = build_client_quote_provider(
            config_cache=config_cache,
            market_data_engine=market_data_engine,
        )
        logger.info(
            "client pricing enabled: spread transforms + stale-quote refusal "
            "(PRICING_MAX_TICK_AGE_SECONDS=%s)",
            os.environ.get("PRICING_MAX_TICK_AGE_SECONDS", "60 (default)"),
        )

    matching_engine = BookMatchingEngine(
        market_feed=market_data_engine,
        symbol_repo=symbol_repo,
        event_bus=event_bus,
        quote_provider=quote_provider,
    )
""",
)])

print("all M7 patches applied")
