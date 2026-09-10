"""
FastAPI Main Entrypoint - Broker Platform REST & WebSocket Server

Assembles FastAPI application, registers REST routers, WebSocket routes,
CORS middleware, health check endpoints, and dependency injection providers.
"""
import logging
from typing import Any, Dict, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    IHolidayRepository, IPositionRepository, IEventBus
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
    
    app = FastAPI(
        title="Broker Platform API",
        description="Tier-1 Institutional Brokerage REST & WebSocket API",
        version="1.0.0"
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
    
    @app.on_event("startup")
    async def startup_event():
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
                import os

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

            stack = await build_trading_stack(
                container,
                market_data_engine=market_data_engine,
                config_cache=cache,
            )
            register_di_providers(stack.as_providers())
            register_di_providers({"market_data_engine": stack.market_data_engine})
            app.state.trading_stack = stack

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

    @app.on_event("shutdown")
    async def shutdown_event():
        stack = getattr(app.state, "trading_stack", None)
        if stack is not None:
            try:
                await stack.liquidation_worker.stop()
                logger.info("✅ LiquidationWorker stopped")
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Error stopping LiquidationWorker: {e}")

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
        """Health check endpoint for container orchestrators."""
        return {
            "status": "healthy",
            "service": "broker-platform-api",
            "version": "1.0.0"
        }

    return app


app = create_app()