"""
FastAPI Dependency Injection Providers

Container factory functions exposing instantiated application command handlers,
query handlers, repositories, and domain services to FastAPI routes via Depends().

Architectural Rule: Decouples API endpoints from concrete infrastructure instantiations.
"""
from typing import Any, Optional

from application.commands.cancel_order import CancelOrderHandler
from application.commands.modify_order import ModifyOrderHandler
from application.commands.modify_deal import ModifyDealHandler
from application.services.risk_service import PreTradeRiskService
from core.domains.risk.engine import RiskEngine

from application.commands.create_group import CreateGroupHandler
from core.ports.interfaces import (
    IGroupRepository,
    IEventBus,
    IAccountRepository,
    ISymbolRepository,
    IHolidayRepository,
    IPositionRepository,
    IOrderRepository,
    IDealRepository,
    IRoutingRuleRepository,
    ICoverageAccountRepository,
)

# Container storage for application instances initialized at app startup
_container: dict[str, Any] = {}


def register_di_providers(providers: dict[str, Any]) -> None:
    """Register runtime dependencies (repos, handlers, engines) into global container."""
    _container.update(providers)


# --- Appended by M0: DI container accessor -------------------------------
# _container is a plain dict keyed by string, but api/main.py resolves by port
# type. This view bridges the two without rewriting every call site, and it fails
# loudly on an unregistered port so a mis-wired server cannot start half-configured.

_PORT_TO_KEY: dict = {}


class _ContainerView:
    """Read-only, resolve()-style view over the process-wide provider dict."""

    def __init__(self, providers: dict) -> None:
        self._providers = providers

    def resolve(self, port: Any, key: Optional[str] = None) -> Any:
        lookup = key or _PORT_TO_KEY.get(port) or getattr(port, "__name__", str(port))
        if lookup not in self._providers:
            raise KeyError(
                f"no provider registered for {lookup!r}; "
                f"available: {sorted(self._providers)}"
            )
        return self._providers[lookup]

    def get(self, key: str, default: Any = None) -> Any:
        return self._providers.get(key, default)

    def __contains__(self, key: str) -> bool:
        return key in self._providers


def register_port_keys(mapping: dict) -> None:
    """Map port classes to container keys, e.g. {IGroupRepository: 'group_repo'}."""
    _PORT_TO_KEY.update(mapping)


def get_di_container() -> Any:
    """Return the process-wide DI container as a resolve()-capable view."""
    return _ContainerView(_container)


def get_group_repo() -> Any:
    """Provider for IGroupRepository."""
    return _container.get("group_repo")


def get_account_repo() -> Any:
    """Provider for IAccountRepository."""
    return _container.get("account_repo")


def get_position_repo() -> Any:
    """Provider for IPositionRepository."""
    repo = _container.get("position_repo")
    if not repo:
        raise RuntimeError("Position repository not registered in DI container")
    return repo


def get_symbol_repo() -> Any:
    """Provider for ISymbolRepository."""
    repo = _container.get("symbol_repo")
    if not repo:
        raise RuntimeError("Symbol repository not registered in DI container")
    return repo


def get_event_bus() -> Any:
    """Provider for IEventBus."""
    bus = _container.get("event_bus")
    if not bus:
        raise RuntimeError("Event bus not registered in DI container")
    return bus


def get_market_data_engine() -> Any:
    """Provider for MarketDataEngine."""
    return _container.get("market_data_engine")


def get_create_order_handler() -> Any:
    """Provider for CreateOrderCommandHandler.

    This used to return a FallbackCreateOrderHandler whose MockOrder answered every
    request with ticket 1001 and state 'FILLED'. On a server started without the trading
    plane wired, POST /api/v1/trade/orders therefore returned HTTP 200 and a filled
    ticket for an order that was never risk-checked, never priced, never persisted and
    never hedged - the client believed it held a position that did not exist, and no log
    line anywhere said so. A trade endpoint must fail loudly or trade; it must not
    simulate. Build the handler with build_trading_stack() at startup.
    """
    handler = _container.get("create_order_handler")
    if not handler:
        raise RuntimeError(
            "no create_order_handler is registered: the trading plane is not wired. "
            "Call application.di.trading_setup.build_trading_stack(container) at startup "
            "and register its providers before serving /api/v1/trade/orders."
        )
    return handler


def get_account_info_query_handler() -> Any:
    """Provider for GetAccountInfoQueryHandler."""
    return _container.get("account_info_query_handler")


def get_positions_query_handler() -> Any:
    """Provider for GetPositionsQueryHandler."""
    return _container.get("positions_query_handler")


def get_rate_limiter() -> Any:
    """Provider for IRateLimiter."""
    return _container.get("rate_limiter")


def get_token_blacklist() -> Any:
    """Provider for ITokenBlacklist."""
    return _container.get("token_blacklist")


def get_auth_service() -> Any:
    """Provider for AuthService."""
    return _container.get("auth_service")


def get_manager_repo() -> Any:
    """Provider for IManagerRepository."""
    return _container.get("manager_repo")


def get_totp_service() -> Any:
    """Provider for ITwoFactorService."""
    return _container.get("totp_service")


def get_ip_whitelist() -> Any:
    """Provider for IIPWhitelist."""
    return _container.get("ip_whitelist")


def get_historical_tick_repository() -> Any:
    """Provider for IHistoricalTickRepository."""
    return _container.get("historical_tick_repo")


def get_historical_bar_repository() -> Any:
    """Provider for IHistoricalBarRepository."""
    return _container.get("historical_bar_repo")




def get_close_position_handler() -> Any:
    """Provider for ClosePositionHandler. Fails loudly when unwired.

    Same defect as the order handler above: the fallback returned a MockPosition at a
    hardcoded 1.0860, so a client closing a position got a success response and kept the
    exposure.
    """
    handler = _container.get("close_position_handler")
    if not handler:
        raise RuntimeError(
            "no close_position_handler is registered: the trading plane is not wired. "
            "Call application.di.trading_setup.build_trading_stack(container) at startup."
        )
    return handler


# Backwards-compatible alias: some routers import the shorter name.
get_account_query_handler = get_account_info_query_handler


def get_cancel_order_handler() -> CancelOrderHandler:
    """FastAPI dependency provider for CancelOrderHandler."""
    container = get_di_container()
    return CancelOrderHandler(
        account_repo=container.resolve(IAccountRepository),
        order_repo=container.resolve(IOrderRepository),
        risk_service=container.resolve(PreTradeRiskService),
        event_bus=container.resolve(IEventBus),
    )


def get_modify_order_handler() -> ModifyOrderHandler:
    """FastAPI dependency provider for ModifyOrderHandler."""
    container = get_di_container()
    return ModifyOrderHandler(
        account_repo=container.resolve(IAccountRepository),
        order_repo=container.resolve(IOrderRepository),
        risk_service=container.resolve(PreTradeRiskService),
        event_bus=container.resolve(IEventBus),
    )


def get_modify_deal_handler() -> ModifyDealHandler:
    """FastAPI dependency provider for ModifyDealHandler."""
    container = get_di_container()
    return ModifyDealHandler(
        account_repo=container.resolve(IAccountRepository),
        deal_repo=container.resolve(IDealRepository),
        risk_service=container.resolve(PreTradeRiskService),
        event_bus=container.resolve(IEventBus),
    )

def get_create_group_handler() -> CreateGroupHandler:
    """Provider for CreateGroupHandler."""
    container = get_di_container()
    return CreateGroupHandler(
        group_repo=container.resolve(IGroupRepository),
        event_bus=container.resolve(IEventBus),
    )


# Port classes resolved through get_di_container().resolve(...), mapped to the
# string keys the dict container actually uses. Extending this table is how a new
# port becomes resolvable at startup.
register_port_keys(
    {
        IGroupRepository: "group_repo",
        IEventBus: "event_bus",
        IAccountRepository: "account_repo",
        ISymbolRepository: "symbol_repo",
        IHolidayRepository: "holiday_repo",
        IPositionRepository: "position_repo",
        IOrderRepository: "order_repo",
        IDealRepository: "deal_repo",
        IRoutingRuleRepository: "routing_rule_repo",
        ICoverageAccountRepository: "coverage_repo",
        # Not ports: concrete application services, resolved by class or by name.
        PreTradeRiskService: "risk_service",
        # build_tick_margin_pipeline() resolves the engine BY CLASS, and _ContainerView
        # turns that into the key "RiskEngine" - which nothing registered, so assembling
        # the market data stack raised KeyError at startup.
        RiskEngine: "risk_engine",
    }
)
