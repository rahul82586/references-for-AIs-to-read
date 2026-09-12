"""D6 - the ingestion staleness filter was hard-coded to 10s and silently dropped
every tick from a real feed.

FOUND HOW
=========
Pointing the platform at a real MetaTrader 5 terminal (trade-server over a public
tunnel, live Neon + Upstash) produced:

    INFO  trade-server feed connected: wss://.../ws/marketdata (1 symbol(s))
    DEBUG Tick filtered for symbol EURUSD          <-- x497
    POST /api/v1/trade/orders -> 400
         {"detail":"No ask price available for EURUSD; cannot execute a market BUY"}

497 real ticks arrived and **all 497 were discarded**. Measured independently over
the same socket:

    frames=760  distinct ts values=14      (trade-server rebroadcasts each quote ~54x)
    tick age: min=0.4s  max=12.7s
    over the hard-coded 10s limit: 61/760 (8%)

`MarketDataEngine._is_stale` rejected anything older than **10.0 seconds**, a
literal in the method body with no configuration path. MT5 timestamps a tick with
the *broker's* quote time, so the age we measure includes the terminal's own lag
and any clock offset between the broker and this host. On a liquid weekday that
stays well under 10s; on a thin Friday evening it swings past it, and then EVERY
tick is dropped - the feed is connected, the socket is streaming, and the engine
has no price at all.

WHY NOTHING CAUGHT IT
=====================
* The mock feed stamps `datetime.now()`, so its ticks are always ~0s old and the
  filter never fires. Every test, the local E2E and `m10_proof_cloud_ws.sh` (which
  uses `m10_ws_simulator.py`, also stamping now()) pass unchanged.
* The drop was logged at `logger.debug`. Under bare uvicorn that is invisible, so
  the operator sees a healthy connected feed and a server that cannot price
  anything - the exact shape of M5 defect 9 ("a booted server had zero prices").
* It contradicts M7, which made the *pricing* staleness guard configurable at
  `PRICING_MAX_TICK_AGE_SECONDS` (default **60**). A tick aged 15s was discarded at
  ingestion and never reached the 60s guard that was supposed to decide.

THE FIX
=======
1. `MARKET_DATA_MAX_TICK_AGE_SECONDS`, default **60** - the same number M7 chose
   for the pricing guard, so ingestion and pricing now agree. `0` disables it,
   matching M7's convention. Read once in `__init__`, overridable per instance so
   tests can pin it.
2. A malformed value warns and falls back to the default rather than raising at
   boot or silently becoming 0 (which would disable the guard).
3. The drop is now visible: the FIRST rejection per symbol logs at WARNING with the
   actual age and the threshold, then every 200th. An operator can tell "no ticks
   arriving" from "ticks arriving and being rejected" in one log line.
4. `.env.example` documents it next to the trade-server block.

Idempotent: re-running detects already-applied anchors and skips them.
"""
import ast
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

applied = []


def patch(path, pairs):
    src = io.open(path, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in src else "\n"
    changed = False
    for old, new in pairs:
        if nl == "\r\n":
            old = old.replace("\n", "\r\n")
            new = new.replace("\n", "\r\n")
        if src.count(old) != 1:
            if src.count(new) >= 1:
                print(f"  skip (already patched): {path}")
                continue
            raise AssertionError(f"{path}: anchor found {src.count(old)}x: {old[:80]!r}")
        src = src.replace(old, new, 1)
        changed = True
    if changed:
        if path.endswith(".py"):
            ast.parse(src.replace("\r\n", "\n"))
        io.open(path, "w", encoding="utf-8", newline="").write(src)
        applied.append(path)


ENGINE = "core/domains/market_data/engine.py"

# ------------------------------------------------------------------- __init__
patch(ENGINE, [(
    """    def __init__(
        self,
        event_bus: IEventBus,
        symbol_repo: Optional[ISymbolRepository] = None,
        redis_cache: Optional[Any] = None,
        bar_repository: Optional[IBarRepository] = None
    ):
        self.event_bus = event_bus
        self.symbol_repo = symbol_repo
        self.redis_cache = redis_cache
        self.bar_repository = bar_repository
""",
    """    #: D6: how old a tick may be and still be ingested. Default matches M7's
    #: PRICING_MAX_TICK_AGE_SECONDS so ingestion and pricing agree; 0 disables.
    DEFAULT_MAX_TICK_AGE_SECONDS = 60.0

    def __init__(
        self,
        event_bus: IEventBus,
        symbol_repo: Optional[ISymbolRepository] = None,
        redis_cache: Optional[Any] = None,
        bar_repository: Optional[IBarRepository] = None,
        max_tick_age_seconds: Optional[float] = None
    ):
        self.event_bus = event_bus
        self.symbol_repo = symbol_repo
        self.redis_cache = redis_cache
        self.bar_repository = bar_repository
        self.max_tick_age_seconds = self._resolve_max_tick_age(max_tick_age_seconds)
        #: per-symbol counters so a rejected feed is visible without flooding the log
        self._stale_dropped: Dict[str, int] = {}
""",
)])

# ------------------------------------------------------- the resolver + filter
patch(ENGINE, [(
    """    def _is_stale(self, tick: Tick) -> bool:
        \"\"\"
        Quote filtration check for stale prices.
        Rejects ticks older than 10.0 seconds.
        \"\"\"
        if not tick or not tick.timestamp:
            return True
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        tick_ts = tick.timestamp
        if tick_ts.tzinfo is None:
            tick_ts = tick_ts.replace(tzinfo=timezone.utc)
        age = (now - tick_ts).total_seconds()
        return age > 10.0
""",
    """    @classmethod
    def _resolve_max_tick_age(cls, explicit: Optional[float]) -> float:
        \"\"\"D6: configurable staleness limit, in seconds. 0 disables the check.

        An unparseable value warns and falls back to the default rather than
        raising at boot - and specifically rather than becoming 0, which would
        silently switch the guard off.
        \"\"\"
        if explicit is not None:
            try:
                return max(0.0, float(explicit))
            except (TypeError, ValueError):
                logger.warning(
                    "max_tick_age_seconds=%r is not a number; using %s",
                    explicit, cls.DEFAULT_MAX_TICK_AGE_SECONDS,
                )
                return cls.DEFAULT_MAX_TICK_AGE_SECONDS
        import os as _os
        raw = (_os.environ.get("MARKET_DATA_MAX_TICK_AGE_SECONDS") or "").strip()
        if not raw:
            return cls.DEFAULT_MAX_TICK_AGE_SECONDS
        try:
            return max(0.0, float(raw))
        except ValueError:
            logger.warning(
                "MARKET_DATA_MAX_TICK_AGE_SECONDS=%r is not a number; using %s",
                raw, cls.DEFAULT_MAX_TICK_AGE_SECONDS,
            )
            return cls.DEFAULT_MAX_TICK_AGE_SECONDS

    def _is_stale(self, tick: Tick) -> bool:
        \"\"\"Quote filtration: reject a tick older than `max_tick_age_seconds`.

        D6: this was a hard-coded 10.0s. MT5 stamps a tick with the BROKER's quote
        time, so the measured age carries the terminal's lag and any clock offset
        between the broker and this host. Measured against a real terminal over a
        public tunnel, ages ran 0.4s-12.7s - so on a thin Friday evening every
        tick exceeded 10s and the engine held no price at all, while the socket
        stayed happily connected. 497 of 497 ticks were dropped and the only
        evidence was a logger.debug line.
        \"\"\"
        if not tick or not tick.timestamp:
            return True
        limit = self.max_tick_age_seconds
        if not limit or limit <= 0:
            return False
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        tick_ts = tick.timestamp
        if tick_ts.tzinfo is None:
            tick_ts = tick_ts.replace(tzinfo=timezone.utc)
        age = (now - tick_ts).total_seconds()
        if age <= limit:
            return False
        self._report_stale(tick, age, limit)
        return True

    def _report_stale(self, tick: Tick, age: float, limit: float) -> None:
        \"\"\"Make a rejected feed visible.

        The first drop per symbol logs at WARNING with the actual age, then every
        200th. Without this an operator cannot distinguish \"no ticks arriving\"
        from \"ticks arriving and being rejected\" - and the second one looks
        exactly like a healthy, connected, useless feed.
        \"\"\"
        symbol = getattr(tick, "symbol", "?")
        n = self._stale_dropped.get(symbol, 0) + 1
        self._stale_dropped[symbol] = n
        if n == 1 or n % 200 == 0:
            logger.warning(
                "dropped %s tick(s) for %s as stale: newest age %.1fs exceeds "
                "MARKET_DATA_MAX_TICK_AGE_SECONDS=%.1f. The feed IS delivering - the "
                "quotes are older than the limit. Raise the limit (M7's pricing guard "
                "defaults to 60s) or check the broker terminal's clock.",
                n, symbol, age, limit,
            )
""",
)])

# ---------------------------------------------------------- the filtered log
patch(ENGINE, [(
    """        if self._is_stale(tick) or self._is_noise(tick):
            logger.debug(f"Tick filtered for symbol {tick.symbol}")
            return
""",
    """        if self._is_stale(tick) or self._is_noise(tick):
            # _is_stale already logged the actionable detail at WARNING (rate
            # limited); this stays at debug for the noise-filter path.
            logger.debug(f"Tick filtered for symbol {tick.symbol}")
            return
""",
)])

# ---------------------------------------------------------------- .env.example
patch(".env.example", [(
    "# --- live market data (MARKET_DATA_SOURCE=trade_server) ----------------------\n",
    """# --- live market data (MARKET_DATA_SOURCE=trade_server) ----------------------
# D6: how old an incoming tick may be and still be ingested, in seconds.
# Default 60, matching PRICING_MAX_TICK_AGE_SECONDS so ingestion and pricing
# agree; 0 disables the check. It used to be hard-coded to 10.0s, which silently
# discarded EVERY tick from a real MT5 terminal once quote age exceeded it - the
# socket stayed connected and the server simply had no prices.
# MARKET_DATA_MAX_TICK_AGE_SECONDS=60
""",
)])

print(f"applied to {len(set(applied))} file(s):")
for f in sorted(set(applied)):
    print("  ", f)
