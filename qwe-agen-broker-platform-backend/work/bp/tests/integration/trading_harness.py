"""
Shared harness for the trading-plane integration tests.

These doubles mirror the SIGNATURES of the real SQLAlchemy repositories - including the
optional `session` argument - because `RecordDealHandler` introspects them
(`_accepts_session()`, which inspects the signature) to decide how to call. A double that omits
the parameter makes the handler take a different branch than production does, and the
test then proves something about the double rather than the platform. That is how the
`get_positions_by_account` defect survived: every double defined the name the handler
probed for, and the real repository did not.

Everything here is in-process. No PostgreSQL, no Redis, no network - which is the point:
"can I set it up and run it" has to be answerable on one machine.
"""
from __future__ import annotations

import json
from datetime import datetime, time, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

import pytest

from core.domains.accounts.account import Account
from core.domains.accounts.group import Group
from core.domains.accounts.enums import MarginMode
from core.domains.accounts.value_objects import GroupPermissions, MarginProfile
from core.domains.common.value_objects import Money
from core.domains.execution.models import CoverageAccount, RoutingRule
from core.domains.instruments.symbol import Symbol
from core.domains.instruments.value_objects import TradingSession
from core.domains.market_data.models import Tick
from core.domains.oms.entities.deal import Deal
from core.domains.oms.entities.order import Order
from core.domains.oms.entities.position import Position
from core.domains.oms.enums import OrderState
from infrastructure.messaging.inprocess_event_bus import InProcessEventBus

#: MT5's demo\Standard group: 1:100, margin call 50%, stop out 30% (PERCENT).
DEFAULT_LOGIN = 100001


# ---------------------------------------------------------------------------
# In-memory repositories
# ---------------------------------------------------------------------------


class InMemoryAccountRepository:
    def __init__(self) -> None:
        self.accounts: Dict[Any, Account] = {}

    async def find_by_login(self, login_id: Any, session: Any = None) -> Optional[Account]:
        return self.accounts.get(login_id) or self.accounts.get(int(login_id))

    async def reserve_margin(self, login_id: Any, amount: Any, session: Any = None):
        """Mirrors SqlAccountRepository.reserve_margin: hold only while
        balance + credit + profit - margin_used - margin_reserved covers it.
        Returns the NEW total, or None when refused (the repository owns the
        stored state; the caller's helper syncs from the returned total)."""
        account = self.accounts.get(login_id)
        if account is None:
            try:
                account = self.accounts.get(int(login_id))
            except (TypeError, ValueError):
                account = None
        if account is None:
            return None
        amount = Decimal(str(amount))
        free = (
            account.balance.amount
            + account.credit.amount
            + account.profit.amount
            - account.margin_used.amount
            - account.margin_reserved.amount
        )
        if free < amount:
            return None
        account.margin_reserved = Money(account.margin_reserved.amount + amount, account.currency)
        return account.margin_reserved.amount

    async def release_margin(self, login_id: Any, amount: Any, session: Any = None):
        account = self.accounts.get(login_id)
        if account is None:
            try:
                account = self.accounts.get(int(login_id))
            except (TypeError, ValueError):
                account = None
        if account is None:
            return None
        amount = Decimal(str(amount))
        account.margin_reserved = Money(
            max(Decimal("0"), account.margin_reserved.amount - amount), account.currency
        )
        return account.margin_reserved.amount

    async def find_all(self, session: Any = None) -> List[Account]:
        return list(self.accounts.values())

    async def save(self, account: Account, session: Any = None) -> Account:
        self.accounts[account.login] = account
        return account


class InMemoryOrderRepository:
    def __init__(self) -> None:
        self.orders: Dict[str, Order] = {}
        self.save_count = 0

    async def find_expired_orders(self, before_time: Any, session: Any = None) -> List[Order]:
        """Mirrors SqlOrderRepository: pendings whose expiration has passed."""
        from core.domains.oms.enums import OrderState

        return [
            o for o in self.orders.values()
            if o.time_expiration is not None
            and o.time_expiration < before_time
            and o.state in (OrderState.PLACED, OrderState.PARTIALLY_FILLED)
        ]

    async def save(self, order: Order, session: Any = None) -> Order:
        self.save_count += 1
        self.orders[order.ticket_id] = order
        return order

    async def find_by_id(self, order_id: str, session: Any = None) -> Optional[Order]:
        return self.orders.get(str(order_id))

    async def find_by_account(self, account_login: int, session: Any = None) -> List[Order]:
        return [o for o in self.orders.values() if o.account_login == account_login]

    async def find_active_orders_by_account(self, account_login: int, session: Any = None) -> List[Order]:
        return [
            o for o in self.orders.values()
            if o.account_login == account_login and not o.is_terminal()
        ]


class InMemoryDealRepository:
    def __init__(self) -> None:
        self.deals: Dict[str, Deal] = {}

    async def save(self, deal: Deal, session: Any = None) -> Deal:
        self.deals[deal.deal_id] = deal
        return deal

    async def find_by_id(self, deal_id: str, session: Any = None) -> Optional[Deal]:
        return self.deals.get(deal_id)

    async def find_by_order_id(self, order_id: str, session: Any = None) -> List[Deal]:
        return [d for d in self.deals.values() if d.order_id == str(order_id)]

    async def find_by_account(self, account_login: int, session: Any = None) -> List[Deal]:
        return [d for d in self.deals.values() if d.account_login == account_login]


class InMemoryPositionRepository:
    """Mirrors SqlPositionRepository: all three account-lookup names, all of them
    filtering on `time_done is None` the way the SQL does."""

    def __init__(self) -> None:
        self.positions: Dict[str, Position] = {}

    async def save(self, position: Position, session: Any = None) -> Position:
        self.positions[position.position_id] = position
        return position

    async def find_by_id(self, position_id: str, session: Any = None) -> Optional[Position]:
        return self.positions.get(position_id)

    def _open_for(self, account_login: int) -> List[Position]:
        return [
            p for p in self.positions.values()
            if p.account_login == account_login and p.time_done is None and p.volume.value > 0
        ]

    async def get_positions_by_account(self, account_login: int, session: Any = None) -> List[Position]:
        return self._open_for(account_login)

    async def get_by_account(self, account_login: int, session: Any = None) -> List[Position]:
        return await self.get_positions_by_account(account_login, session=session)

    async def find_by_account(self, account_login: int, session: Any = None) -> List[Position]:
        return await self.get_positions_by_account(account_login, session=session)

    async def get_by_symbol(self, symbol: str, session: Any = None) -> List[Position]:
        return [
            p for p in self.positions.values()
            if p.symbol == symbol and p.time_done is None and p.volume.value > 0
        ]

    async def get_by_account_and_symbol(self, account_login: int, symbol: str, session: Any = None) -> List[Position]:
        return [p for p in await self.get_by_symbol(symbol) if p.account_login == account_login]

    async def get_open_positions(self, session: Any = None) -> List[Position]:
        return [p for p in self.positions.values() if p.time_done is None and p.volume.value > 0]


class InMemorySymbolRepository:
    def __init__(self, symbols: Optional[List[Symbol]] = None) -> None:
        self.symbols: Dict[str, Symbol] = {s.name: s for s in (symbols or [])}

    async def find_by_name(self, name: str, session: Any = None) -> Optional[Symbol]:
        return self.symbols.get(name)

    async def get_all_symbols(self, session: Any = None) -> List[Symbol]:
        return list(self.symbols.values())

    async def get_all(self, session: Any = None) -> List[Symbol]:
        """The name ConfigCache.initialize() calls."""
        return list(self.symbols.values())


class InMemoryGroupRepository:
    def __init__(self, groups: Optional[List[Group]] = None) -> None:
        self.groups: Dict[str, Group] = {g.name: g for g in (groups or [])}

    async def find_by_name(self, name: str, session: Any = None) -> Optional[Group]:
        return self.groups.get(name)

    async def get_all(self, session: Any = None) -> List[Group]:
        return list(self.groups.values())

    async def find_by_id(self, group_id: str, session: Any = None) -> Optional[Group]:
        return next((g for g in self.groups.values() if g.id == group_id), None)

    async def save(self, group: Group, session: Any = None) -> Group:
        self.groups[group.name] = group
        return group


class InMemoryRoutingRuleRepository:
    def __init__(self, rules: Optional[List[RoutingRule]] = None) -> None:
        self.rules: Dict[str, RoutingRule] = {r.rule_id: r for r in (rules or [])}

    async def get_active_rules(self) -> List[RoutingRule]:
        return [r for r in self.rules.values() if r.is_enabled]

    async def save(self, rule: RoutingRule) -> RoutingRule:
        self.rules[rule.rule_id] = rule
        return rule

    async def find_by_id(self, rule_id: str) -> Optional[RoutingRule]:
        return self.rules.get(rule_id)


class InMemoryCoverageAccountRepository:
    """Mirrors SqlCoverageAccountRepository, including the JSON-encoded exposure map."""

    def __init__(self, accounts: Optional[List[CoverageAccount]] = None) -> None:
        self.accounts: Dict[str, CoverageAccount] = {a.account_id: a for a in (accounts or [])}
        self.exposure_updates: List[Dict[str, Any]] = []

    async def find_by_id(self, account_id: str, session: Any = None) -> Optional[CoverageAccount]:
        return self.accounts.get(account_id)

    async def save(self, account: CoverageAccount, session: Any = None) -> CoverageAccount:
        self.accounts[account.account_id] = account
        return account

    async def update_exposure(self, account_id: str, symbol: str, volume_delta: Decimal) -> None:
        account = self.accounts.get(account_id)
        if account is None:
            raise ValueError(f"Coverage account {account_id} not found")
        account.update_exposure(symbol, Decimal(str(volume_delta)))
        self.exposure_updates.append(
            {"account_id": account_id, "symbol": symbol, "volume_delta": Decimal(str(volume_delta))}
        )


class InMemoryRoutingMt5Repository:
    """Mirrors SqlRoutingMt5Repository: decoded rules in table order."""

    def __init__(self, rules=None) -> None:
        self.rules = list(rules or [])

    async def get_all_ordered(self, session: Any = None):
        return sorted(self.rules, key=lambda r: r.position)

    async def upsert(self, rule, record=None, session: Any = None):
        self.rules = [r for r in self.rules if r.name != rule.name]
        self.rules.append(rule)
        return rule


class InMemoryHolidayRepository:
    async def get_all(self, session: Any = None) -> List[Any]:
        """The name ConfigCache.initialize() calls."""
        return []

    async def get_active_holidays(self, session: Any = None) -> List[Any]:
        return []

    async def find_by_id(self, holiday_id: str, session: Any = None) -> Optional[Any]:
        return None


# ---------------------------------------------------------------------------
# Configuration builders - a real, tradable slice of an MT5 server
# ---------------------------------------------------------------------------


def always_open_sessions() -> Dict[int, List[TradingSession]]:
    """Sessions covering every day, 00:00-23:59.

    Populated for all seven indices because MT5 stores sessions SUNDAY-FIRST
    (0=Sunday) while `Symbol.is_trade_session_active` indexes them with Python's
    `weekday()` (0=Monday). Filling both conventions keeps the fixture honest about
    that mismatch instead of passing on Wednesdays and failing on Sundays.
    """
    return {day: [TradingSession(day_of_week=day, open_minutes=0, close_minutes=1439)] for day in range(7)}


def make_eurusd(name: str = "EURUSD") -> Symbol:
    """EURUSD as the live MT5 export carries it: 5 digits, 100k contract, EUR/USD/USD."""
    return Symbol(
        name=name,
        path=f"Forex\\{name}",
        description="Euro vs US Dollar",
        base_currency="EUR",
        quote_currency="USD",
        margin_currency="EUR",
        digits=5,
        tick_size=Decimal("0.00001"),
        contract_size=Decimal("100000"),
        spread=10,
        volume_min=Decimal("0.01"),
        volume_max=Decimal("100"),
        volume_step=Decimal("0.01"),
        trade_sessions=always_open_sessions(),
        quote_sessions=always_open_sessions(),
        is_trade_allowed=True,
    )


def make_usdjpy(name: str = "USDJPY") -> Symbol:
    """USDJPY: the cross-currency case, where profit is JPY and margin is USD."""
    return Symbol(
        name=name,
        path=f"Forex\\{name}",
        description="US Dollar vs Japanese Yen",
        base_currency="USD",
        quote_currency="JPY",
        margin_currency="USD",
        digits=3,
        tick_size=Decimal("0.001"),
        contract_size=Decimal("100000"),
        spread=12,
        volume_min=Decimal("0.01"),
        volume_max=Decimal("100"),
        volume_step=Decimal("0.01"),
        trade_sessions=always_open_sessions(),
        quote_sessions=always_open_sessions(),
        is_trade_allowed=True,
    )


def make_group(
    name: str = "demo\\Standard",
    *,
    leverage: int = 100,
    margin_call: Decimal = Decimal("50"),
    stop_out: Decimal = Decimal("30"),
    margin_mode: MarginMode = MarginMode.RETAIL_HEDGED,
) -> Group:
    """A group with MT5's demo\\Standard margin thresholds. Levels are PERCENT.

    margin_mode defaults to RETAIL_HEDGED (MT5 MarginMode 2) because that is what
    every seeded YAML group carries and what the retail e2e suite exercises.
    MarginMode.RETAIL (0) is MT5's NETTING accounting (SDK EnMarginMode) - the
    M6 netting tests build their groups with it explicitly.
    """
    return Group(
        name=name,
        currency="USD",
        currency_digits=2,
        margin=MarginProfile(
            mode=margin_mode,
            leverage_default=leverage,
            leverage_max=500,
            margin_call_level=margin_call,
            stop_out_level=stop_out,
        ),
        permissions=GroupPermissions(allowed_symbols=["*"]),
    )


def make_account(
    login: int = DEFAULT_LOGIN,
    group: Optional[Group] = None,
    *,
    balance: Decimal = Decimal("10000"),
    currency: str = "USD",
    leverage: Optional[int] = None,
) -> Account:
    account = Account(
        login=login,
        group_id=group.name if group else "",
        group=group,
        currency=currency,
        leverage=leverage,
        balance=Money(balance, currency),
        credit=Money(Decimal("0"), currency),
    )
    account.equity = Money(balance, currency)
    account.margin_used = Money(Decimal("0"), currency)
    account.margin_free = Money(balance, currency)
    return account


def make_tick(symbol: str, bid: Decimal, ask: Decimal, *, source: str = "TEST") -> Tick:
    return Tick(
        symbol=symbol,
        bid=Decimal(str(bid)),
        ask=Decimal(str(ask)),
        spread=Decimal(str(ask)) - Decimal(str(bid)),
        timestamp=datetime.now(timezone.utc),
        source=source,
    )


# ---------------------------------------------------------------------------
# The assembled platform
# ---------------------------------------------------------------------------


class TradingHarness:
    """A whole broker, in memory: config plane, market data, trading plane, bus."""

    def __init__(
        self,
        *,
        groups: Optional[List[Group]] = None,
        symbols: Optional[List[Symbol]] = None,
        accounts: Optional[List[Account]] = None,
        rules: Optional[List[RoutingRule]] = None,
        coverage: Optional[List[CoverageAccount]] = None,
        lp_strict: bool = True,
        mt5_rules: Optional[List[Any]] = None,
    ) -> None:
        self.groups = groups if groups is not None else [make_group()]
        self.symbols = symbols if symbols is not None else [make_eurusd(), make_usdjpy()]
        self.accounts = accounts if accounts is not None else [make_account(group=self.groups[0])]

        self.group_repo = InMemoryGroupRepository(self.groups)
        self.symbol_repo = InMemorySymbolRepository(self.symbols)
        self.account_repo = InMemoryAccountRepository()
        for account in self.accounts:
            self.account_repo.accounts[account.login] = account

        self.order_repo = InMemoryOrderRepository()
        self.deal_repo = InMemoryDealRepository()
        self.position_repo = InMemoryPositionRepository()
        self.routing_rule_repo = InMemoryRoutingRuleRepository(rules)
        self.coverage_repo = InMemoryCoverageAccountRepository(coverage)
        self.holiday_repo = InMemoryHolidayRepository()
        self.mt5_routing_repo = InMemoryRoutingMt5Repository(mt5_rules)

        self.event_bus = InProcessEventBus()
        self.lp_strict = lp_strict
        self.stack = None
        self.market_data_engine = None
        self.config_cache = None
        self._registered: Dict[str, Any] = {}
        self.tick_pipeline = None

    @property
    def providers(self) -> Dict[str, Any]:
        """The provider dict `setup_persistence_di` would have returned, plus whatever
        the trading stack registered back into it."""
        base = {
            "event_bus": self.event_bus,
            "group_repo": self.group_repo,
            "symbol_repo": self.symbol_repo,
            "account_repo": self.account_repo,
            "order_repo": self.order_repo,
            "deal_repo": self.deal_repo,
            "position_repo": self.position_repo,
            "routing_rule_repo": self.routing_rule_repo,
            "coverage_repo": self.coverage_repo,
            "holiday_repo": self.holiday_repo,
            "mt5_routing_repo": self.mt5_routing_repo,
            "market_data_engine": self.market_data_engine,
        }
        base.update(self._registered)
        return base

    @property
    def container(self) -> Any:
        """A resolve()-capable view over the providers - the same class api/main.py uses.

        `build_market_data_stack` resolves by PORT CLASS (IPositionRepository, RiskEngine),
        so a plain dict is not enough. Using the real _ContainerView means these tests
        exercise the API's resolution path rather than a friendlier one invented for them.
        """
        from api.di_providers import _ContainerView

        return _ContainerView(self.providers)

    def register(self, providers: Dict[str, Any]) -> None:
        """Mirror register_di_providers(): put components back into the container."""
        self._registered.update(providers)

    async def build(self, *, wire_trading: bool = True) -> "TradingHarness":
        """Assemble market data + trading planes, the way api/main.py startup does.

        `wire_trading=False` stops after the config cache and the market data engine,
        leaving the trading plane to whoever consumes the container. The HTTP test uses
        it so FastAPI's own startup builds the stack: wiring it twice would subscribe two
        orchestrators to ORDER_APPROVED and execute every order twice.
        """
        from core.domains.market_data.engine import MarketDataEngine

        self.market_data_engine = MarketDataEngine(
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

        self.register({"market_data_engine": self.market_data_engine})
        if not wire_trading:
            return self

        from application.di.trading_setup import build_trading_stack

        self.stack = await build_trading_stack(
            self.container,
            market_data_engine=self.market_data_engine,
            config_cache=self.config_cache,
            lp_strict=self.lp_strict,
        )
        self.register(self.stack.as_providers())

        # Market data plane, as api/main.py step 4 does it: tick -> position PnL ->
        # account equity -> the margin state machine -> MarginCallEntered/StopOutEntered.
        # Without it a crashing price updates nothing and the LiquidationWorker, which
        # only ever hears about a stop-out from this pipeline, never runs.
        from application.di.market_data_setup import build_market_data_stack

        components = build_market_data_stack(self.container)
        self.tick_pipeline = components.get("tick_pipeline")
        return self

    # -- conveniences -------------------------------------------------------

    async def publish_tick(self, symbol: str, bid: Decimal, ask: Decimal) -> None:
        """Push a tick through the real MarketDataEngine, so it updates the price cache
        AND publishes TICK_RECEIVED to the margin pipeline and the resting book."""
        await self.market_data_engine.process_tick(make_tick(symbol, bid, ask))

    def latest_tick(self, symbol: str) -> Optional[Tick]:
        return self.market_data_engine.get_latest_tick(symbol)

    async def account(self, login: int = DEFAULT_LOGIN) -> Account:
        return await self.account_repo.find_by_login(login)

    def open_positions(self, login: int = DEFAULT_LOGIN) -> List[Position]:
        return [
            p for p in self.position_repo.positions.values()
            if p.account_login == login and p.time_done is None and p.volume.value > 0
        ]

    def deals_for(self, login: int = DEFAULT_LOGIN) -> List[Deal]:
        return [d for d in self.deal_repo.deals.values() if d.account_login == login]

    def orders(self) -> List[Order]:
        return list(self.order_repo.orders.values())

    def coverage_exposure(self, symbol: str, account_id: str = "DEFAULT_COVERAGE") -> Decimal:
        account = self.coverage_repo.accounts.get(account_id)
        if account is None:
            return Decimal("0")
        return account.net_exposure.get(symbol, Decimal("0"))


def default_coverage(nop_limit: str = "100") -> List[CoverageAccount]:
    """The DEFAULT_COVERAGE account `cli seed` creates, so B-Book exposure has somewhere
    to go. Without it the orchestrator logs that broker exposure is untracked."""
    return [
        CoverageAccount(
            account_id="DEFAULT_COVERAGE",
            name="Default Coverage",
            currency="USD",
            nop_limit=Decimal(nop_limit),
        )
    ]


async def build_harness(*, wire_trading: bool = True, **kwargs: Any) -> TradingHarness:
    return await TradingHarness(**kwargs).build(wire_trading=wire_trading)


@pytest.fixture
def harness_factory():
    """Fixture returning an async factory, so a test can build several harnesses."""
    return build_harness
