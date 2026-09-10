"""
FastAPI Main Entrypoint - Broker Platform REST & WebSocket Server

Assembles FastAPI application, registers REST routers, WebSocket routes,
CORS middleware, health check endpoints, and dependency injection providers.
"""
import logging
from typing import Any, Dict, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.di_providers import register_di_providers, get_event_bus, get_di_container
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


def create_app(container: Optional[Dict[str, Any]] = None) -> FastAPI:
    """FastAPI application factory function."""
    if container:
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

            # 2. Initialize WebSocket Event Bridge
            event_bus = get_event_bus()
            if event_bus:
                event_bridge = WebSocketEventBridge(event_bus)
                await event_bridge.start()
                app.state.event_bridge = event_bridge
                logger.info("✅ WebSocketEventBridge started")
                
        except Exception as e:
            logger.error(f"Startup event failed: {e}", exc_info=True)
            raise  # Fail fast if cache or bridge fails to start

    @app.on_event("shutdown")
    async def shutdown_event():
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