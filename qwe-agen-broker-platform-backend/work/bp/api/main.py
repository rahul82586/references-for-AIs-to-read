"""
FastAPI Main Entrypoint - Broker Platform REST & WebSocket Server

Assembles FastAPI application, registers REST routers, WebSocket routes,
CORS middleware, health check endpoints, and dependency injection providers.
"""
import asyncio
import logging
import os

# M5: the wiring story (trading plane, Redis bus, price source) is logged at
# INFO. Under bare uvicorn the root logger only shows WARNING+, so an operator
# could not see what the server had assembled - or that it had fallen back to
# the in-process bus. LOG_LEVEL overrides.
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
from typing import Any, Dict, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.config.env import (
    check_server_secrets,
    load_environment,
    normalize_database_url,
)

# M5: load .env before anything reads os.environ, and refuse to boot without
# real secrets. Fail-hard at startup, not at the first request: a server that
# signs tokens with a placeholder key is worse than one that does not start.
load_environment()
_secret_problems = check_server_secrets()
if _secret_problems:
    raise RuntimeError(
        "Refusing to start: " + "; ".join(_secret_problems)
    )

from api.di_providers import (
    register_di_providers,
    get_di_container,
    get_event_bus,
    get_market_data_engine,
)
from api.routers import account, auth, trade, market_data
from api.routers.admin import admin_router
from api.routers.manager import (
    connection as manager_connection,
    main as manager_main,
    service as manager_service,
    subscriptions as manager_subscriptions,
    trading as manager_trading,
)
from api.websockets import endpoints as ws_endpoints
from api.websockets.event_bridge import WebSocketEventBridge

from application.cache.config_cache import ConfigCache, set_config_cache
from core.ports.interfaces import (
    IGroupRepository, IAccountRepository, ISymbolRepository, 
    IHolidayRepository, IPositionRepository, IEventBus, IOrderRepository
)

logger = logging.getLogger(__name__)


def _container_lookup(key: str) -> Any:
    """Read a key from the process-wide provider dict without raising."""
    try:
        return get_di_container().get(key)
    except Exception:  # noqa: BLE001
        return None


def default_providers() -> Dict[str, Any]:
    """Build the persistence providers and an event bus, exactly as the CLI does.

    `cli start` runs `uvicorn api.main:app`, and the module-level `app = create_app()`
    at the bottom of this file passed NO container - so the process-wide provider dict
    was empty and startup died with KeyError('IGroupRepository'). The one command that
    is supposed to start the platform could not. Assembling the providers here does not
    connect to anything (DatabaseManager only builds an engine and a session factory),
    so importing this module stays side-effect free; the first query is what needs a
    reachable database, and that now fails with a database error instead of a confusing
    complaint about a missing repository.

    Shared with cli/main.py's _bootstrap() so a seeder and the server it seeds for
    cannot drift apart.
    """
    import os

    from infrastructure.persistence.database import DatabaseManager
    from infrastructure.persistence.di_setup import setup_persistence_di

    url = os.environ.get("DATABASE_URL")
    if not url:
        logger.warning(
            "DATABASE_URL is not set; using the development default "
            "postgres user/password on localhost:5432"
        )
        url = "postgresql+asyncpg://postgres:postgres@localhost:5432/broker_platform"
    else:
        # accept a plain postgresql:// URL (Neon, Heroku, ...) and make it async
        url = normalize_database_url(url)

    manager = DatabaseManager(url)
    providers = setup_persistence_di(manager)

    redis_url = os.environ.get("REDIS_URL")
    if redis_url:
        from infrastructure.messaging.redis_event_bus import RedisEventBus

        providers["event_bus"] = RedisEventBus(redis_url)
    else:
        from infrastructure.messaging.inprocess_event_bus import InProcessEventBus

        providers["event_bus"] = InProcessEventBus()

    providers["database"] = manager
    return providers


def create_app(container: Optional[Dict[str, Any]] = None) -> FastAPI:
    """FastAPI application factory function."""
    if not container:
        container = default_providers()
    register_di_providers(container)
    
    # M6: FastAPI lifespan handlers replace the deprecated @app.on_event.
    # startup_event/shutdown_event are defined below (closures over `container`);
    # the context manager resolves them when the server actually starts.
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def _lifespan(lifespan_app: FastAPI):
        await startup_event(lifespan_app)
        yield
        await shutdown_event(lifespan_app)

    app = FastAPI(
        title="Broker Platform API",
        description="Tier-1 Institutional Brokerage REST & WebSocket API",
        version="1.0.0",
        lifespan=_lifespan,
    )

    # CORS configuration for Admin UI and Client Terminals
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # Restrict origins in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include REST Routers
    app.include_router(auth.router)
    app.include_router(trade.router)
    app.include_router(account.router)
    app.include_router(market_data.router)
    app.include_router(admin_router.router)

    # Include Manager API routers
    app.include_router(manager_trading.router)
    app.include_router(manager_main.router)
    app.include_router(manager_connection.router)
    app.include_router(manager_service.router)
    app.include_router(manager_subscriptions.router)

    # Include WebSocket Routes
    app.include_router(ws_endpoints.router)

    # =========================================================================
    # Startup & Shutdown Event Handlers
    # =========================================================================
    
    async def startup_event(app: FastAPI):
        try:
            # 1. Initialize ConfigCache (MT5-like speed)
            logger.info("Initializing ConfigCache from PostgreSQL...")
            container = get_di_container()
            
            cache = ConfigCache(
                group_repo=container.resolve(IGroupRepository),
                account_repo=container.resolve(IAccountRepository),
                symbol_repo=container.resolve(ISymbolRepository),
                holiday_repo=container.resolve(IHolidayRepository),
                position_repo=container.resolve(IPositionRepository),
                event_bus=container.resolve(IEventBus),
            )
            
            await cache.initialize()
            set_config_cache(cache)
            logger.info("✅ ConfigCache ready — MT5-like speed achieved")

            market_data_engine = get_market_data_engine()

            # 2. Event bus. Default to the in-process bus rather than requiring Redis:
            #    "set up and run" must work with PostgreSQL alone, and RedisEventBus
            #    raises on publish when no server is reachable. REDIS_URL opts into the
            #    distributed bus, which is the multi-node deployment path.
            event_bus = get_event_bus()
            if event_bus is None:
                redis_url = os.environ.get("REDIS_URL")
                if redis_url:
                    from infrastructure.messaging.redis_event_bus import RedisEventBus

                    event_bus = RedisEventBus(redis_url)
                    await event_bus.connect()
                    logger.info("✅ RedisEventBus connected at %s", redis_url)
                else:
                    from infrastructure.messaging.inprocess_event_bus import InProcessEventBus

                    event_bus = InProcessEventBus()
                    logger.warning(
                        "REDIS_URL is not set: using the single-process InProcessEventBus. "
                        "Domain events will not cross process boundaries, so run one node."
                    )
                register_di_providers({"event_bus": event_bus})

            # 3. Trading plane FIRST: risk -> routing -> matching -> execution ->
            #    liquidation. It builds the RiskEngine, which the market data stack
            #    resolves from the container, so the order matters - the reverse order
            #    raised KeyError('RiskEngine') before any tick could be processed.
            #    Without this step the trade endpoint has no handler and refuses orders,
            #    which is intended: it previously returned a mock FILLED ticket.
            from application.di.trading_setup import build_trading_stack

            # M11: BROKER_DEFAULT_DESTINATION picks where flow goes when no routing
            # rule matches. Default B_BOOK (the house internalises). Set A_BOOK to
            # run a straight-through-processing broker that hedges everything at
            # the LP, with no rule table needed. An unknown value is a startup
            # failure naming the variable - a typo must not silently change where
            # real money goes.
            from core.domains.execution.models import ExecutionDestination

            _dest_raw = os.environ.get("BROKER_DEFAULT_DESTINATION", "").strip().lower()
            _dest_map = {
                "": ExecutionDestination.B_BOOK,
                "b_book": ExecutionDestination.B_BOOK,
                "bbook": ExecutionDestination.B_BOOK,
                "a_book": ExecutionDestination.A_BOOK,
                "abook": ExecutionDestination.A_BOOK,
            }
            if _dest_raw not in _dest_map:
                raise RuntimeError(
                    f"unknown BROKER_DEFAULT_DESTINATION={_dest_raw!r}; "
                    "supported: B_BOOK (default) or A_BOOK"
                )
            _default_destination = _dest_map[_dest_raw]
            if _default_destination is not ExecutionDestination.B_BOOK:
                logger.warning(
                    "BROKER_DEFAULT_DESTINATION=%s: unmatched flow goes A-Book and will "
                    "be hedged externally", _default_destination.value,
                )

            stack = await build_trading_stack(
                container,
                market_data_engine=market_data_engine,
                config_cache=cache,
                default_destination=_default_destination,
            )
            register_di_providers(stack.as_providers())
            register_di_providers({"market_data_engine": stack.market_data_engine})
            app.state.trading_stack = stack

            # Read-side queries that need the LIVE trading plane (M5):
            # /account/positions returned [] for everyone because nothing
            # ever registered this handler. Valuation goes through the
            # stack's RiskEngine - the same single source of truth the
            # margin loop and the liquidation worker use.
            from application.queries.get_account_info import GetAccountInfoQueryHandler
            from application.queries.get_positions import GetPositionsQueryHandler

            register_di_providers(
                {
                    "positions_query_handler": GetPositionsQueryHandler(
                        position_repo=container.resolve(IPositionRepository),
                        account_repo=container.resolve(IAccountRepository),
                        symbol_repo=container.resolve(ISymbolRepository),
                        market_data_engine=stack.market_data_engine,
                        risk_engine=stack.risk_engine,
                    ),
                    # D2: /account/info and the manager UserGet both ask the
                    # container for this key. Nothing ever registered it, so
                    # Depends() resolved to None and both routes silently served
                    # whatever the JWT happened to carry.
                    "account_info_query_handler": GetAccountInfoQueryHandler(
                        account_repo=container.resolve(IAccountRepository),
                        position_repo=container.resolve(IPositionRepository),
                        market_data_engine=stack.market_data_engine,
                    ),
                }
            )

            # D9 + M12: valuation and reconciliation. Both are maintenance jobs,
            # so a failure to build either must not stop the server from trading -
            # but it must be loud, because "no sweep is running" looks exactly like
            # "everything is fine" from the outside.
            try:
                from application.services.reconciliation_service import (
                    ReconciliationService,
                    ValuationService,
                )
                from infrastructure.persistence.repositories.reconciliation_repository import (
                    SqlReconciliationRepository,
                )

                _valuation_interval = float(
                    os.environ.get("VALUATION_SWEEP_INTERVAL_S", "300") or 300)
                valuation_service = ValuationService(
                    account_repo=container.resolve(IAccountRepository),
                    position_repo=container.resolve(IPositionRepository),
                    symbol_repo=container.resolve(ISymbolRepository),
                    market_data_engine=stack.market_data_engine,
                    risk_engine=stack.risk_engine,
                    interval_s=_valuation_interval,
                )
                app.state.valuation_service = valuation_service
                await valuation_service.start()

                # Breaks persist only when a database is wired; without one the
                # service still runs and logs, which is better than not running.
                _break_repo = None
                try:
                    _db = container.resolve("database") if hasattr(container, "resolve") else None
                    if _db is not None and getattr(_db, "session_factory", None) is not None:
                        _break_repo = SqlReconciliationRepository(
                            session_factory=_db.session_factory)
                except Exception:  # noqa: BLE001
                    _break_repo = None
                if _break_repo is None:
                    logger.warning(
                        "no reconciliation break store is wired; reconciliation will "
                        "log but not persist breaks"
                    )

                _hedged = [x.strip().upper() for x in
                           (os.environ.get("RECONCILE_HEDGED_SYMBOLS") or "").split(",")
                           if x.strip()]
                reconciliation_service = ReconciliationService(
                    position_repo=container.resolve(IPositionRepository),
                    break_repo=_break_repo,
                    gateway=stack.liquidity_gateway,
                    hedged_symbols=_hedged,
                    event_bus=event_bus,
                    venue_name=os.environ.get("BROKER_LP_GATEWAY") or "LP",
                )
                app.state.reconciliation_service = reconciliation_service
                app.state.reconciliation_break_repo = _break_repo
                register_di_providers({
                    "valuation_service": valuation_service,
                    "reconciliation_service": reconciliation_service,
                    "reconciliation_break_repo": _break_repo,
                })
                logger.info(
                    "✅ ValuationService started (every %.0fs); reconciliation wired "
                    "against the %s gateway%s",
                    _valuation_interval,
                    type(stack.liquidity_gateway).__name__,
                    "" if _hedged else " (no RECONCILE_HEDGED_SYMBOLS set, so only "
                                      "venue-side orphans will be reported)",
                )
            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "valuation/reconciliation could not be wired: %s - the server will "
                    "still trade, but accounts will only revalue on ticks and breaks "
                    "will not be recorded", exc,
                )

            logger.info(
                "✅ Trading plane wired: router, matching engine, orchestrator, "
                "liquidation worker"
            )
            for warning in stack.warnings:
                logger.warning("⚠️  %s", warning)

            # 4. Market data plane: tick -> PnL -> equity -> margin state machine.
            #    Runs after the trading plane so it can resolve the RiskEngine, and so
            #    the resting-order book is subscribed before the first tick arrives.
            try:
                from application.di.market_data_setup import build_market_data_stack

                md_components = build_market_data_stack(container)
                app.state.tick_pipeline = md_components.get("tick_pipeline")
                logger.info("✅ TickMarginPipeline subscribed to TICK_RECEIVED")
            except Exception as exc:  # noqa: BLE001 - reported, not fatal to the API
                logger.error(
                    "market data stack could not be assembled: %s. Orders will still "
                    "execute, but equity and the stop-out state machine will not update "
                    "on incoming ticks.",
                    exc,
                    exc_info=True,
                )

            # 4a. Swap worker (M6): nothing charged swap before this. It needs
            #     the ledger repository; when one is not configured it says so
            #     loudly instead of pretending swaps are free.
            ledger_repo = _container_lookup("ledger_repo")
            if ledger_repo is None:
                logger.warning(
                    "no ledger_repo in the container: SwapWorker NOT started - "
                    "overnight positions will not be charged swap"
                )
            else:
                from application.services.swap_worker import SwapWorker
                from core.domains.ledger.engine import LedgerEngine

                ledger_engine = LedgerEngine(
                    ledger_repo=ledger_repo,
                    account_repo=container.resolve(IAccountRepository),
                )
                swap_worker = SwapWorker(
                    ledger_engine=ledger_engine,
                    position_repo=container.resolve(IPositionRepository),
                    account_repo=container.resolve(IAccountRepository),
                    symbol_repo=container.resolve(ISymbolRepository),
                    event_bus=event_bus,
                    market_data_engine=stack.market_data_engine,
                    rollover_hour_utc=int(os.environ.get("SWAP_ROLLOVER_HOUR_UTC", "22")),
                )
                app.state.swap_worker = swap_worker
                app.state.swap_worker_task = asyncio.create_task(swap_worker.start())
                logger.info("SwapWorker started (rollover %02d:00 UTC)", swap_worker.rollover_hour_utc)

            # 4a2. Expiration worker (M9): pending orders carrying a GTD
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

            # 4b. Price source (M5). A server with no feed cannot price an
            #     order, and refusing is correct - but a dev/test box needs
            #     SOME source. MARKET_DATA_SOURCE=mock opts into the
            #     self-labelled MockTickFeed (every tick carries source=MOCK).
            #     Unset = no feed = orders refuse for lack of a price.
            md_source = os.environ.get("MARKET_DATA_SOURCE", "").strip().lower()
            if md_source == "mock":
                from application.services.tick_ingestor import TickIngestor
                from infrastructure.feeds.mock_feed import MockTickFeed

                symbol_names = [s.name for s in cache.get_all_symbols()]
                rate_ms = int(os.environ.get("MOCK_TICK_RATE_MS", "250"))
                feed = MockTickFeed(symbols=symbol_names, tick_rate_ms=rate_ms)
                ingestor = TickIngestor(
                    market_data_engine=stack.market_data_engine, feeds=[feed]
                )
                await ingestor.start()
                app.state.tick_ingestor = ingestor
                logger.warning(
                    "MARKET_DATA_SOURCE=mock: prices are a simulated random walk "
                    "over %d symbol(s) at %dms - NOT real market data",
                    len(symbol_names),
                    rate_ms,
                )
            elif md_source in ("trade_server", "ws"):
                # M10: live upstream. The trade-server prototype keeps a real
                # MetaTrader5 terminal attached and broadcasts msgpack ticks over
                # WebSocket (/ws/marketdata). One feed adapter, same TickIngestor
                # and MarketDataEngine as the mock - only the source changes.
                from application.services.tick_ingestor import TickIngestor
                from infrastructure.feeds.trade_server_feed import TradeServerTickFeed

                ws_url = os.environ.get("TRADE_SERVER_WS_URL", "").strip()
                if not ws_url:
                    raise RuntimeError(
                        "MARKET_DATA_SOURCE=trade_server requires TRADE_SERVER_WS_URL "
                        "(e.g. ws://127.0.0.1:8000/ws/marketdata)"
                    )
                env_symbols = os.environ.get("TRADE_SERVER_WS_SYMBOLS", "").strip()
                if env_symbols:
                    ws_symbols = [s.strip().upper() for s in env_symbols.split(",") if s.strip()]
                else:
                    ws_symbols = [s.name for s in cache.get_all_symbols()]
                    cap = int(os.environ.get("TRADE_SERVER_WS_MAX_SYMBOLS", "50"))
                    if len(ws_symbols) > cap:
                        logger.warning(
                            "subscribing to the first %d of %d cached symbols "
                            "(raise TRADE_SERVER_WS_MAX_SYMBOLS or set "
                            "TRADE_SERVER_WS_SYMBOLS to choose them)",
                            cap, len(ws_symbols),
                        )
                        ws_symbols = ws_symbols[:cap]
                feed = TradeServerTickFeed(url=ws_url, symbols=ws_symbols)
                ingestor = TickIngestor(
                    market_data_engine=stack.market_data_engine, feeds=[feed]
                )
                await ingestor.start()
                app.state.tick_ingestor = ingestor
                logger.info(
                    "MARKET_DATA_SOURCE=trade_server: live ticks from %s (%d symbol(s))",
                    ws_url, len(ws_symbols),
                )
            elif md_source:
                raise RuntimeError(
                    f"unknown MARKET_DATA_SOURCE={md_source!r}; supported: 'mock', "
                    "'trade_server' (live WS upstream) or unset (no price source)"
                )

            # 5. WebSocket Event Bridge
            event_bridge = WebSocketEventBridge(event_bus)
            await event_bridge.start()
            app.state.event_bridge = event_bridge
            logger.info("✅ WebSocketEventBridge started")

        except KeyError as e:
            # A missing container component is a configuration error, and the message
            # names the component. Do not swallow it into the generic handler below.
            logger.error(
                "Startup failed: the trading plane is missing a dependency (%s). "
                "Register the persistence providers (setup_persistence_di) before create_app.",
                e,
            )
            raise
        except Exception as e:
            logger.error(f"Startup event failed: {e}", exc_info=True)
            raise  # Fail fast if cache or bridge fails to start

    async def shutdown_event(app: FastAPI):
        expiration_worker = getattr(app.state, "expiration_worker", None)
        if expiration_worker is not None:
            try:
                await expiration_worker.stop()
                task = getattr(app.state, "expiration_worker_task", None)
                if task is not None and not task.done():
                    task.cancel()
                logger.info("ExpirationWorker stopped")
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Error stopping ExpirationWorker: {e}")

        valuation_service = getattr(app.state, "valuation_service", None)
        if valuation_service is not None:
            try:
                await valuation_service.stop()
                logger.info("ValuationService stopped")
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Error stopping ValuationService: {e}")

        swap_worker = getattr(app.state, "swap_worker", None)
        if swap_worker is not None:
            try:
                await swap_worker.stop()
                task = getattr(app.state, "swap_worker_task", None)
                if task is not None and not task.done():
                    task.cancel()
                logger.info("SwapWorker stopped")
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Error stopping SwapWorker: {e}")

        ingestor = getattr(app.state, "tick_ingestor", None)
        if ingestor is not None:
            try:
                await ingestor.stop()
                logger.info("TickIngestor stopped")
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Error stopping TickIngestor: {e}")

        stack = getattr(app.state, "trading_stack", None)
        if stack is not None:
            try:
                await stack.liquidation_worker.stop()
                logger.info("✅ LiquidationWorker stopped")
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Error stopping LiquidationWorker: {e}")

            # M10: the FIX liquidity gateway (when BROKER_LP_GATEWAY=fix) owns a
            # session + read loop; close it like every other worker.
            lp_gateway = getattr(stack, "liquidity_gateway", None)
            if lp_gateway is not None and hasattr(lp_gateway, "stop"):
              try:
                await lp_gateway.stop()
                logger.info("Liquidity gateway stopped")
              except Exception as e:  # noqa: BLE001
                logger.warning(f"Error stopping liquidity gateway: {e}")

            # M9: the SL/TP worker subscribes to the tick stream and closes
            # triggered positions; it must unsubscribe on shutdown, not outlive
            # the bus it publishes closes onto.
            if getattr(stack, "sltp_worker", None) is not None:
              try:
                await stack.sltp_worker.stop()
                logger.info("SlTpWorker stopped")
              except Exception as e:  # noqa: BLE001
                logger.warning(f"Error stopping SlTpWorker: {e}")

        database = _container_lookup("database")
        if database is not None and hasattr(database, "close"):
            try:
                await database.close()
                logger.info("✅ Database engine disposed")
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Error closing the database engine: {e}")

        event_bridge = getattr(app.state, "event_bridge", None)
        if event_bridge:
            try:
                await event_bridge.stop()
                logger.info("✅ WebSocketEventBridge stopped")
            except Exception as e:
                logger.warning(f"Error stopping WebSocketEventBridge: {e}")

    @app.get("/health", tags=["Health"])
    async def health_check():
        """Liveness/readiness with REAL dependency checks.

        Pre-M5 this returned a hardcoded "healthy" whatever the state of the
        world, so a container with a dead database still reported green to the
        orchestrator. Now: SELECT 1 against the configured database, and a PING
        against Redis when the distributed bus is in use. Degraded answers carry
        503 so compose/Kubernetes/load balancers can act on them.
        """
        import asyncio
        import time

        from fastapi.responses import JSONResponse
        from sqlalchemy import text as sql_text

        async def _probe_database() -> Dict[str, Any]:
            database = _container_lookup("database")
            if database is None:
                return {"status": "not-configured"}
            started = time.monotonic()
            try:
                async def _select_one() -> None:
                    async with database.session_factory() as session:
                        await session.execute(sql_text("SELECT 1"))

                await asyncio.wait_for(_select_one(), timeout=4.0)
                return {
                    "status": "ok",
                    "latency_ms": round((time.monotonic() - started) * 1000, 1),
                }
            except asyncio.TimeoutError:
                return {"status": "error", "error": "timeout"}
            except Exception as exc:  # noqa: BLE001 - reported, never raised
                return {"status": "error", "error": type(exc).__name__}

        async def _probe_event_bus() -> Dict[str, Any]:
            bus = _container_lookup("event_bus")
            if bus is None or not hasattr(bus, "ping"):
                # InProcessEventBus: single-node by configuration, not an error.
                return {"status": "in-process"}
            started = time.monotonic()
            try:
                ok = await asyncio.wait_for(bus.ping(), timeout=4.0)
                if ok:
                    return {
                        "status": "ok",
                        "latency_ms": round((time.monotonic() - started) * 1000, 1),
                    }
                return {"status": "not-connected"}
            except asyncio.TimeoutError:
                return {"status": "error", "error": "timeout"}
            except Exception as exc:  # noqa: BLE001
                return {"status": "error", "error": type(exc).__name__}

        database = await _probe_database()
        event_bus = await _probe_event_bus()
        healthy = database.get("status") == "ok" and event_bus.get("status") in (
            "ok",
            "in-process",
        )
        payload = {
            "status": "healthy" if healthy else "degraded",
            "service": "broker-platform-api",
            "version": "1.0.0",
            "checks": {"database": database, "event_bus": event_bus},
        }
        return JSONResponse(status_code=200 if healthy else 503, content=payload)

    return app


app = create_app()