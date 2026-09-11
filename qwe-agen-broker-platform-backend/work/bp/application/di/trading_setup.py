"""
Trading Plane Composition Root.

`setup_persistence_di()` builds the repositories. `build_market_data_stack()` builds the
tick pipeline. This module builds the thing that was missing entirely: the trading plane
- risk, routing, matching, execution, liquidation - and subscribes it to the event bus.

Why it matters
--------------
Before this, nothing constructed an ExecutionOrchestrator, a SmartOrderRouter, a
matching engine or a liquidity gateway outside a test. `api/main.py` started a
ConfigCache and a WebSocket bridge and stopped there, and `get_create_order_handler()`
returned a mock that answered every order with a fake FILLED ticket. So the platform
could be installed, seeded, started and queried - and an order placed against it did
nothing at all while reporting success.

`build_trading_stack(container)` is the single place that answers "what does it take to
execute an order here". It is a factory, not module state: nothing touches the database
or the bus at import time, and a test can build the same stack against in-memory
doubles, which is exactly what the end-to-end proof does.

Deliberate limits (documented, not hidden)
------------------------------------------
* The A-Book gateway is a stub. In strict mode it raises, so an order routed A-Book on a
  server with no LP connected is rejected back to the client rather than silently
  "hedged". Set BROKER_LP_STUB_NONSTRICT=1 to accept stub acknowledgements.
* There is no margin RESERVATION between risk approval and the deal being recorded.
  With the in-process bus the orchestrator runs inline, so the fill is booked before
  `handle()` returns and the window is closed. Across a Redis bus it is open, and two
  concurrent orders could both pass the same free-margin check. Closing that needs a
  reserved-margin column on the account; it is listed in the M4 report as known debt.
* Commission is charged from the group's rules at fill time. Swap is not - the swap
  worker owns that, and booking it twice would be worse than booking it late.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from application.commands.close_position import ClosePositionHandler
from application.commands.create_order import CreateOrderHandler
from application.commands.record_deal import RecordDealHandler
from application.services.dealer_queue_service import DealerQueueService
from application.services.execution_orchestrator import ExecutionOrchestrator
from application.services.risk_service import PreTradeRiskService
from application.workers.liquidation_worker import LiquidationWorker
from application.workers.sltp_worker import SlTpWorker
from core.domains.execution.models import ExecutionDestination
from core.domains.execution.router import SmartOrderRouter
from core.domains.market_data.engine import MarketDataEngine
from core.domains.market_data.feed_access import tick_from_event
from core.domains.risk.engine import RiskEngine
from core.domains.risk.liquidation_service import LiquidationService
from core.events.domain_events import EventType, StopOutEntered
from core.ports.interfaces import (
    IAccountRepository,
    ICoverageAccountRepository,
    IDealRepository,
    IEventBus,
    IGroupRepository,
    IHolidayRepository,
    IOrderRepository,
    IPositionRepository,
    IRoutingRuleRepository,
    ISymbolRepository,
)
from infrastructure.engines.book_matching_engine import BookMatchingEngine
from infrastructure.gateways.stub_liquidity_gateway import StubLiquidityGateway

logger = logging.getLogger(__name__)


@dataclass
class TradingStack:
    """The assembled trading plane, by name, so callers can register or test any part."""

    event_bus: Any
    risk_engine: RiskEngine
    risk_service: PreTradeRiskService
    matching_engine: BookMatchingEngine
    liquidity_gateway: Any
    router: SmartOrderRouter
    dealer_queue: DealerQueueService
    record_deal_handler: RecordDealHandler
    orchestrator: ExecutionOrchestrator
    create_order_handler: CreateOrderHandler
    liquidation_service: LiquidationService
    liquidation_worker: LiquidationWorker
    market_data_engine: Optional[Any] = None
    #: the synchronous symbol view RiskEngine was given (ConfigCache in production)
    symbol_view: Optional[Any] = None
    #: M9: server-side SL/TP triggers, and the risk-engine-carrying close
    #: handler they (and the manager OrderClose endpoint) fire through.
    sltp_worker: Optional[Any] = None
    close_position_handler: Optional[Any] = None
    warnings: list = field(default_factory=list)

    def as_providers(self) -> Dict[str, Any]:
        """Container keys, matching the naming `setup_persistence_di` established."""
        return {
            "risk_engine": self.risk_engine,
            # `_ContainerView.resolve(RiskEngine)` falls back to the class NAME as the
            # key, which is what build_tick_margin_pipeline() asks for. Without this the
            # market data stack could not be assembled at startup at all: it raised
            # KeyError('RiskEngine') before it ever subscribed to a tick.
            "RiskEngine": self.risk_engine,
            "risk_service": self.risk_service,
            "matching_engine": self.matching_engine,
            "liquidity_gateway": self.liquidity_gateway,
            "close_position_handler": self.close_position_handler,
            "sltp_worker": self.sltp_worker,
            "smart_order_router": self.router,
            "dealer_queue": self.dealer_queue,
            "record_deal_handler": self.record_deal_handler,
            "execution_orchestrator": self.orchestrator,
            "create_order_handler": self.create_order_handler,
            "liquidation_service": self.liquidation_service,
            "liquidation_worker": self.liquidation_worker,
        }


def _resolve(container: Any, key: str, required: bool = True, default: Any = None) -> Any:
    """Read a component out of a resolve()-capable container or a plain dict."""
    value = None
    if hasattr(container, "resolve"):
        try:
            value = container.resolve(key)
        except Exception:  # noqa: BLE001 - fall through to .get / default
            value = None
    if value is None and hasattr(container, "get"):
        value = container.get(key, None)
    if value is None:
        value = default
    if value is None and required:
        raise KeyError(
            f"trading stack requires {key!r} in the container; available: "
            f"{sorted(container) if hasattr(container, '__iter__') else '?'}"
        )
    return value


def _resolve_sync_symbol_view(
    container: Any,
    explicit: Optional[Any],
    symbol_repo: Any,
    warnings: list,
) -> Any:
    """Something RiskEngine can call `get_symbol(name)` on without awaiting.

    Resolution order: an explicit cache, one in the container, the process-wide
    ConfigCache singleton `api/main.py` installs, then the symbol repo itself if it
    happens to expose a synchronous `get_symbol`. Falling all the way through is
    reported as a warning rather than left silent, because the consequence is that
    pre-trade risk rejects every order from an account that already holds a position.
    """
    import inspect

    candidates = [explicit, _resolve(container, "config_cache", required=False)]

    try:
        from application.cache.config_cache import get_config_cache

        candidates.append(get_config_cache())
    except Exception:  # noqa: BLE001 - not initialised; that is a normal case here
        pass

    candidates.append(symbol_repo)

    for candidate in candidates:
        if candidate is None:
            continue
        getter = getattr(candidate, "get_symbol", None)
        if getter is None or inspect.iscoroutinefunction(getter):
            continue
        return candidate

    warnings.append(
        "no synchronous symbol lookup is available (ConfigCache not initialised and the "
        "symbol repository is async): RiskEngine cannot build a live margin snapshot, so "
        "pre-trade risk will REJECT every order from an account that already holds a "
        "position. Initialise ConfigCache before building the trading stack."
    )
    return symbol_repo


async def build_trading_stack(
    container: Any,
    *,
    market_data_engine: Optional[Any] = None,
    uow_factory: Optional[Any] = None,
    config_cache: Optional[Any] = None,
    default_destination: ExecutionDestination = ExecutionDestination.B_BOOK,
    lp_strict: Optional[bool] = None,
) -> TradingStack:
    """Assemble the trading plane from a populated DI container.

    Raises KeyError naming the missing component rather than building a half-wired
    stack: a server that starts without a matching engine and then reports orders as
    filled is worse than one that refuses to start.
    """
    warnings: list = []

    event_bus = _resolve(container, "event_bus")
    account_repo = _resolve(container, "account_repo")
    order_repo = _resolve(container, "order_repo")
    deal_repo = _resolve(container, "deal_repo")
    position_repo = _resolve(container, "position_repo")
    symbol_repo = _resolve(container, "symbol_repo")
    routing_rule_repo = _resolve(container, "routing_rule_repo")
    coverage_repo = _resolve(container, "coverage_repo", required=False)
    if coverage_repo is None:
        warnings.append(
            "no coverage_repo: B-Book exposure will not be tracked and NOP thresholds "
            "cannot fire"
        )

    # Market data: prefer an engine the caller already built (the tick pipeline owns one),
    # otherwise build one on the shared bus so pricing has somewhere to read from.
    if market_data_engine is None:
        market_data_engine = _resolve(container, "market_data_engine", required=False)
    if market_data_engine is None:
        market_data_engine = MarketDataEngine(event_bus=event_bus, symbol_repo=symbol_repo)
        warnings.append(
            "no market_data_engine in the container; built a bare one. Until a feed "
            "publishes ticks, orders price from the symbol's configured spread."
        )

    # RiskEngine reads symbols SYNCHRONOUSLY - `_symbol()` raises rather than await a
    # coroutine, because it sits on the hot path that reprices every account on every
    # tick. Every repository `setup_persistence_di` builds is async, including
    # SqlSymbolRepository.get_symbol, so handing it the symbol repo makes
    # calculate_margin_level() raise PositionValuationError - and
    # `_check_margin_requirement` treats a failed live snapshot as a REJECTION rather
    # than degrading to a stored number. The result: any account holding a position
    # could never open another one. ConfigCache is the synchronous view it wants, and
    # api/main.py already builds one at startup.
    symbol_view = _resolve_sync_symbol_view(container, config_cache, symbol_repo, warnings)

    risk_engine = _resolve(
        container, "risk_engine", required=False,
        default=RiskEngine(symbol_repo=symbol_view, market_data_engine=market_data_engine),
    )

    risk_service = PreTradeRiskService(
        event_bus=event_bus,
        position_repo=position_repo,
        risk_engine=risk_engine,
        symbol_repo=symbol_repo,
        account_repo=account_repo,
    )

    # M7: client pricing - group spread transforms (SpreadDiff/Balance, fixed
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

        def _position_counts(login, symbol_name):
            """(open positions total, open in symbol) from the ConfigCache -
            the synchronous counts view routing conditions 4005/4006 need (M9).
            The cache refreshes on DealCreated/PositionClosed (see config_cache)."""
            try:
                login = int(login)
            except (TypeError, ValueError):
                return None, None
            positions = config_cache.get_positions_by_account(login)
            return len(positions), sum(1 for p in positions if p.symbol == symbol_name)

        def _client_quote_with_point(symbol_name, account_login):
            """(bid, ask, point) for the routing conditions that measure in points
            (MARKET_DEVIATION, SYMBOL_SPREAD). One resolver feeds the matching
            engine, the risk price and the router, so all three see ONE price."""
            from decimal import Decimal as _Dec

            quote = quote_provider(symbol_name, account_login)
            if quote is None:
                return None
            sym = config_cache.get_symbol(symbol_name)
            point = getattr(sym, "tick_size", None) or _Dec("0.00001")
            return (quote[0], quote[1], _Dec(str(point)))
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

    if lp_strict is None:
        lp_strict = os.environ.get("BROKER_LP_STUB_NONSTRICT", "").lower() not in ("1", "true", "yes")
    # M10: BROKER_LP_GATEWAY=fix swaps the stub for the FIX adapter under the
    # SAME DI key - the orchestrator's A-Book path is unchanged.
    default_gateway: Any = StubLiquidityGateway(strict=lp_strict)
    lp_gateway_kind = os.environ.get("BROKER_LP_GATEWAY", "").strip().lower()
    if lp_gateway_kind == "fix":
        from infrastructure.gateways.fix_gateway import build_fix_gateway_from_env

        default_gateway = build_fix_gateway_from_env()
        logger.info(
            "A-Book liquidity gateway: FIX (sender=%s target=%s, session=%s)",
            default_gateway.sender_comp_id,
            default_gateway.target_comp_id,
            "simulated" if os.environ.get("BROKER_FIX_SIMULATOR", "").strip().lower()
            in ("1", "true", "yes") else "quickfixn",
        )
    elif lp_gateway_kind:
        raise RuntimeError(
            f"unknown BROKER_LP_GATEWAY={lp_gateway_kind!r}; supported: 'fix' or unset (stub)"
        )
    liquidity_gateway = _resolve(
        container, "liquidity_gateway", required=False,
        default=default_gateway,
    )
    if isinstance(liquidity_gateway, StubLiquidityGateway):
        warnings.append(
            "A-Book liquidity gateway is the STUB. strict="
            f"{liquidity_gateway.strict}: A-Book orders "
            + ("are rejected until a real adapter is registered."
               if liquidity_gateway.strict else
               "are acknowledged without any external hedge being placed.")
        )

    router = SmartOrderRouter(
        routing_rule_repo=routing_rule_repo,
        default_destination=default_destination,
        coverage_repo=coverage_repo,
        mt5_routing_repo=_resolve(container, "mt5_routing_repo", required=False),
        client_quote_fn=(
            _client_quote_with_point if config_cache is not None and quote_provider is not None else None
        ),
        counts_fn=(_position_counts if config_cache is not None else None),
    )

    dealer_queue = DealerQueueService(event_bus=event_bus, order_repo=order_repo)

    record_deal_handler = RecordDealHandler(
        order_repo=order_repo,
        account_repo=account_repo,
        position_repo=position_repo,
        event_bus=event_bus,
        symbol_repo=symbol_repo,
        market_feed=market_data_engine,
        deal_repo=deal_repo,
        uow_factory=uow_factory,
    )

    orchestrator = ExecutionOrchestrator(
        router=router,
        dealer_queue=dealer_queue,
        liquidity_gateway=liquidity_gateway,
        matching_engine=matching_engine,
        event_bus=event_bus,
        order_repo=order_repo,
        account_repo=account_repo,
        coverage_repo=coverage_repo,
        position_repo=position_repo,
        symbol_repo=symbol_repo,
        market_feed=market_data_engine,
        record_deal_handler=record_deal_handler,
        deal_repo=deal_repo,
        uow_factory=uow_factory,
    )

    create_order_handler = CreateOrderHandler(
        account_repo=account_repo,
        symbol_repo=symbol_repo,
        order_repo=order_repo,
        position_repo=position_repo,
        risk_service=risk_service,
        event_bus=event_bus,
        market_feed=market_data_engine,
        quote_provider=quote_provider,
    )

    # M9: the close handler with the risk engine (converted realised PnL) is
    # built ONCE, here: the SL/TP worker fires through it, and registering it
    # in as_providers finally gives the manager OrderClose endpoint a handler
    # (it fail-loud-refused before: nothing anywhere registered one).
    close_position_handler = ClosePositionHandler(
        account_repo=account_repo,
        position_repo=position_repo,
        order_repo=order_repo,
        deal_repo=deal_repo,
        event_bus=event_bus,
        risk_engine=risk_engine,
    )
    sltp_worker = SlTpWorker(
        position_repo=position_repo,
        close_position_handler=close_position_handler,
        event_bus=event_bus,
    )

    liquidation_service = _resolve(container, "liquidation_service", required=False, default=LiquidationService())
    liquidation_worker = LiquidationWorker(
        account_repo=account_repo,
        position_repo=position_repo,
        order_repo=order_repo,
        deal_repo=deal_repo,
        symbol_repo=symbol_repo,
        market_data_feed=market_data_engine,
        event_bus=event_bus,
        liquidation_service=liquidation_service,
        risk_engine=risk_engine,
    )

    stack = TradingStack(
        event_bus=event_bus,
        risk_engine=risk_engine,
        risk_service=risk_service,
        matching_engine=matching_engine,
        liquidity_gateway=liquidity_gateway,
        router=router,
        dealer_queue=dealer_queue,
        record_deal_handler=record_deal_handler,
        orchestrator=orchestrator,
        create_order_handler=create_order_handler,
        liquidation_service=liquidation_service,
        liquidation_worker=liquidation_worker,
        market_data_engine=market_data_engine,
        symbol_view=symbol_view,
        sltp_worker=sltp_worker,
        close_position_handler=close_position_handler,
        warnings=warnings,
    )

    await wire_trading_subscriptions(stack)
    return stack


async def wire_trading_subscriptions(stack: TradingStack) -> None:
    """Subscribe the trading plane to the bus, and load the routing rules.

    Three subscriptions make an order into a position:
      ORDER_APPROVED -> ExecutionOrchestrator  (route and execute)
      StopOutEntered -> LiquidationWorker      (close positions, worst loss first)
      TICK_RECEIVED  -> matching engine book   (activate resting pending orders)

    `refresh_rules()` is awaited here because SmartOrderRouter.route() raises when no
    rules are loaded - a router with an empty rule list is not a permissive router, it
    is a broken one, and failing at startup beats failing on the first order.
    """
    bus = stack.event_bus

    # M9: server-side SL/TP. The worker subscribes to TICK_RECEIVED (idempotent
    # start) and closes triggered positions through the close handler.
    if stack.sltp_worker is not None:
        await stack.sltp_worker.start()

    bus.subscribe(EventType.ORDER_APPROVED.value, stack.orchestrator.handle_order_approved)
    logger.info("ExecutionOrchestrator subscribed to ORDER_APPROVED")

    await stack.liquidation_worker.start()
    logger.info("LiquidationWorker subscribed to StopOutEntered")

    async def _on_tick(event: Any) -> None:
        # tick_from_event, not payload["tick"]: MarketDataEngine publishes flat string
        # fields so the event survives JSON onto Redis, and there is no "tick" key.
        tick = tick_from_event(event)
        if tick is None:
            return
        await stack.matching_engine.on_tick(tick)

    bus.subscribe(EventType.TICK_RECEIVED, _on_tick)
    logger.info("BookMatchingEngine subscribed to TICK_RECEIVED for pending-order activation")

    await stack.router.refresh_rules()

    # The B-Book books broker exposure on a coverage account, and `cli seed` creates
    # DEFAULT_COVERAGE. Check it is there rather than discovering it on the first fill:
    # a missing coverage account does not stop the trade (the orchestrator reports that
    # separately now), but it does mean NOP thresholds cannot see any exposure.
    coverage_repo = getattr(stack.orchestrator, "coverage_repo", None)
    if coverage_repo is not None:
        try:
            if await coverage_repo.find_by_id("DEFAULT_COVERAGE") is None:
                stack.warnings.append(
                    "no DEFAULT_COVERAGE account: B-Book fills will be booked but broker "
                    "exposure will not be tracked, so the 70/85/95% NOP thresholds cannot "
                    "fire. Run `cli seed`, which creates it."
                )
        except Exception as exc:  # noqa: BLE001 - a warning, not a startup failure
            stack.warnings.append(f"could not verify the coverage account: {exc}")

    for warning in stack.warnings:
        logger.warning("trading stack: %s", warning)


__all__ = ["TradingStack", "build_trading_stack", "wire_trading_subscriptions"]
