"""M5 patches: cross-process tick shape + an opt-in, self-announcing price source.

Defect 1 (found by wiring real Redis in M5): RedisEventBus delivers the
serialised event to subscribers as a PLAIN DICT, but tick_from_event only read
`event.payload` as an attribute - so every tick arriving cross-process was
silently dropped by both the margin pipeline and the matching engine's
pending-order activation. In-process delivery hands over the event object,
which is why M4's proofs never saw this.

Defect 2: build_market_data_stack's docstring promises MockTickFeed ->
TickIngestor -> MarketDataEngine, but nothing ever started a feed. A running
server had NO price source at all: every market order was refused for lack of
a price. M5 wires an OPT-IN mock source (MARKET_DATA_SOURCE=mock). The default
stays "no feed": a server that cannot price must refuse orders, not invent
numbers - the same rule the A-Book stub follows.
"""
import ast
import io
import pathlib

# ---------------------------------------------------------------------------
# 1. feed_access.tick_from_event accepts the Redis wire shape (LF file)
# ---------------------------------------------------------------------------
p = pathlib.Path("core/domains/market_data/feed_access.py")
src = io.open(p, encoding="utf-8", newline="").read()

old = '''    payload = getattr(event, "payload", None)
    if not isinstance(payload, dict):
        return None

    tick = payload.get("tick")
    if tick is not None:
        return tick

    from decimal import Decimal, InvalidOperation

    from core.domains.market_data.models import Tick

    symbol = payload.get("symbol") or getattr(event, "aggregate_id", None)
'''
new = '''    payload = getattr(event, "payload", None)
    aggregate_id = getattr(event, "aggregate_id", None)
    if payload is None and isinstance(event, dict):
        # RedisEventBus delivers json.loads(event.to_dict()) - a plain dict -
        # to cross-process subscribers. Before M5 this function only knew the
        # in-process event OBJECT, so every tick that crossed a process
        # boundary was dropped silently by the margin pipeline and by the
        # matching engine's pending-order activation.
        inner = event.get("payload")
        payload = inner if isinstance(inner, dict) else event
        aggregate_id = event.get("aggregate_id", aggregate_id)
    if not isinstance(payload, dict):
        return None

    tick = payload.get("tick")
    if tick is not None:
        return tick

    from decimal import Decimal, InvalidOperation

    from core.domains.market_data.models import Tick

    symbol = payload.get("symbol") or aggregate_id
'''
assert src.count(old) == 1, "feed_access anchor not found"
src = src.replace(old, new)
ast.parse(src)
io.open(p, "w", encoding="utf-8", newline="").write(src)
print("feed_access.tick_from_event: dict (Redis wire) shape accepted")

# ---------------------------------------------------------------------------
# 2. api/main.py: MARKET_DATA_SOURCE=mock starts the feed; shutdown stops it
#    (CRLF file)
# ---------------------------------------------------------------------------
p = pathlib.Path("api/main.py")
src = io.open(p, encoding="utf-8", newline="").read()

old = (
    "            # 5. WebSocket Event Bridge\r\n"
)
new = (
    "            # 4b. Price source (M5). A server with no feed cannot price an\r\n"
    "            #     order, and refusing is correct - but a dev/test box needs\r\n"
    "            #     SOME source. MARKET_DATA_SOURCE=mock opts into the\r\n"
    "            #     self-labelled MockTickFeed (every tick carries source=MOCK).\r\n"
    "            #     Unset = no feed = orders refuse for lack of a price.\r\n"
    "            md_source = os.environ.get(\"MARKET_DATA_SOURCE\", \"\").strip().lower()\r\n"
    "            if md_source == \"mock\":\r\n"
    "                from application.services.tick_ingestor import TickIngestor\r\n"
    "                from infrastructure.feeds.mock_feed import MockTickFeed\r\n"
    "\r\n"
    "                symbol_names = [s.name for s in cache.get_all_symbols()]\r\n"
    "                rate_ms = int(os.environ.get(\"MOCK_TICK_RATE_MS\", \"250\"))\r\n"
    "                feed = MockTickFeed(symbols=symbol_names, tick_rate_ms=rate_ms)\r\n"
    "                ingestor = TickIngestor(\r\n"
    "                    market_data_engine=stack.market_data_engine, feeds=[feed]\r\n"
    "                )\r\n"
    "                await ingestor.start()\r\n"
    "                app.state.tick_ingestor = ingestor\r\n"
    "                logger.warning(\r\n"
    "                    \"MARKET_DATA_SOURCE=mock: prices are a simulated random walk \"\r\n"
    "                    \"over %d symbol(s) at %dms - NOT real market data\",\r\n"
    "                    len(symbol_names),\r\n"
    "                    rate_ms,\r\n"
    "                )\r\n"
    "            elif md_source:\r\n"
    "                raise RuntimeError(\r\n"
    "                    f\"unknown MARKET_DATA_SOURCE={md_source!r}; supported: 'mock' \"\r\n"
    "                    \"or unset (no price source)\"\r\n"
    "                )\r\n"
    "\r\n"
    "            # 5. WebSocket Event Bridge\r\n"
)
assert src.count(old) == 1, "startup anchor not found"
src = src.replace(old, new)

# `os` must be visible inside startup_event; default_providers imported it
# locally. Add a module-level import to be safe.
old_imp = "import logging\r\n"
new_imp = "import logging\r\nimport os\r\n"
assert src.count(old_imp) == 1
src = src.replace(old_imp, new_imp, 1)

# shutdown: stop the ingestor first (no new ticks), then the worker/db/bridge
old_shut = (
    "    @app.on_event(\"shutdown\")\r\n"
    "    async def shutdown_event():\r\n"
    "        stack = getattr(app.state, \"trading_stack\", None)\r\n"
)
new_shut = (
    "    @app.on_event(\"shutdown\")\r\n"
    "    async def shutdown_event():\r\n"
    "        ingestor = getattr(app.state, \"tick_ingestor\", None)\r\n"
    "        if ingestor is not None:\r\n"
    "            try:\r\n"
    "                await ingestor.stop()\r\n"
    "                logger.info(\"TickIngestor stopped\")\r\n"
    "            except Exception as e:  # noqa: BLE001\r\n"
    "                logger.warning(f\"Error stopping TickIngestor: {e}\")\r\n"
    "\r\n"
    "        stack = getattr(app.state, \"trading_stack\", None)\r\n"
)
assert src.count(old_shut) == 1, "shutdown anchor not found"
src = src.replace(old_shut, new_shut)
ast.parse(src)
io.open(p, "w", encoding="utf-8", newline="").write(src)
print("api/main.py: MARKET_DATA_SOURCE=mock wiring + ingestor shutdown")

# ---------------------------------------------------------------------------
# 3. .env.example: document the new variables
# ---------------------------------------------------------------------------
p = pathlib.Path(".env.example")
src = io.open(p, encoding="utf-8").read()
old = "# --- optional ----------------------------------------------------------------\n"
new = (
    "# --- optional ----------------------------------------------------------------\n"
    "# Price source. Unset = none: the server runs but refuses orders it cannot\n"
    "# price (honest). 'mock' = simulated random-walk ticks, every tick labelled\n"
    "# source=MOCK - development and testing only.\n"
    "MARKET_DATA_SOURCE=\n"
    "# MOCK_TICK_RATE_MS=250\n"
)
assert src.count(old) == 1
src = src.replace(old, new)
io.open(p, "w", encoding="utf-8").write(src)
print(".env.example: MARKET_DATA_SOURCE documented")
