"""
Core Ports - The Contracts That Enable Swappable Infrastructure

These abstract base classes define the boundaries between the pure domain logic
and external concerns (databases, message brokers, matching engines).
Implementations live in the infrastructure layer and are injected at runtime.
"""
from abc import ABC, abstractmethod
from typing import Any, List, Optional, TypeVar, Generic, Callable, AsyncIterator
from datetime import datetime
from decimal import Decimal

from core.events.domain_events import DomainEvent

T = TypeVar('T')


def normalize_channel(channel: Any) -> str:
    """Reduce an event class, an EventType member or a string to one channel key.

    Call sites in this codebase use all three conventions, and a bus that keys on one
    will never deliver to a subscriber that registered with another. Normalising here
    means the convention stops mattering.
    """
    if isinstance(channel, str):
        return channel
    if hasattr(channel, "value") and isinstance(getattr(channel, "value"), str):
        return str(channel.value)
    if isinstance(channel, type):
        return channel.__name__
    return str(channel)


class IEventBus(ABC):
    """
    Contract for the internal messaging system.

    Architectural Purpose:
    Decouples the producer of an event (e.g., OMS Domain) from the consumers
    (e.g., ClickHouse Writer, AI Agent, Notification Service).
    Implementations can be Redis, Kafka, or an in-memory queue for testing.
    """

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """
        Publishes a domain event to the specified channel/topic.
        Must be non-blocking (fire-and-forget) to maintain high throughput.
        """
        pass

    @abstractmethod
    def subscribe(self, channel: Any, callback: Callable[[Any], None]) -> Any:
        """Register a handler for an event class, EventType or channel string.

        Registration happens IMMEDIATELY, and the return value is additionally awaitable,
        so both `bus.subscribe(...)` and `await bus.subscribe(...)` work. That matters:
        this method used to be `async def`, and 20 of its 24 call sites did not await it,
        so those subscriptions silently never happened - ConfigCache never invalidated,
        LiquidationWorker never saw a stop-out, and no WebSocket client ever received an
        update. An unawaited coroutine is a no-op; a self-registering object is not.
        """
        pass
        """
        Subscribes to a specific channel and invokes the callback upon message receipt.
        The callback receives a deserialized dictionary representation of the event.
        """
        pass

    def unsubscribe(self, channel: Any, callback: Callable[[Any], None]) -> bool:
        """Remove one registration. Returns True if something was removed.

        Not abstract, so the doubles already in the tree keep working - but declared,
        because LiquidationWorker.stop() calls it and RedisEventBus did not have it,
        which made graceful shutdown raise AttributeError. A worker that cannot be
        stopped cannot be restarted.
        """
        raise NotImplementedError(
            f"{type(self).__name__} does not implement unsubscribe; subscriptions "
            "registered with it cannot be removed"
        )

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Gracefully closes connections and cleans up resources.
        """
        pass


class IAccountRepository(ABC, Generic[T]):
    """Contract for Account persistence."""
    @abstractmethod
    async def find_by_login(self, login_id: str) -> Optional[T]:
        """Retrieves an account by its unique login ID."""
        pass

    @abstractmethod
    async def save(self, account: T) -> T:
        """Persists an account aggregate."""
        pass

    async def update_valuation(self, account: T, include_margin: bool = False) -> int:
        """D8b: persist only the valuation columns this caller owns.

        profit, equity, margin_free, margin_level and the so_* stop-out fields -
        never balance, margin_used or margin_reserved. The tick pipeline calls
        this on every tick with an account object it loaded earlier; a full-row
        save there overwrites whatever a concurrent fill wrote to margin_used.

        Optional by design. The base returns None to mean "this repository does
        not implement it", and callers then fall back to save(). It must NOT raise
        here: an abstract raise is inherited by every test double and adapter, so
        a capability probe would blow up instead of degrading.
        """
        return None

    async def reserve_margin(self, login_id: Any, amount: Any):
        """Atomically hold `amount` of free margin for an in-flight order (M6).

        Returns the NEW margin_reserved total, or None when the account no
        longer covers the amount. MUST be a single conditional UPDATE in SQL
        implementations, so two nodes racing the same account cannot both win.
        The base declaration raises NotImplementedError: callers
        (application.services.margin_reservation) fall back to the
        per-account-locked in-process path and log that they did.
        """
        raise NotImplementedError

    async def release_margin(self, login_id: Any, amount: Any):
        """Release a hold placed by reserve_margin (fill or rejection).

        Returns the NEW margin_reserved total (clamped at zero), or None when
        the account does not exist.
        """
        raise NotImplementedError


class IOrderRepository(ABC, Generic[T]):
    """
    Contract for Order persistence (MT5 IMTOrder).

    Architectural Purpose:
    Hides the database technology from the Domain. The OMS calls save() or
    find_by_id(), unaware of SQL or ORM, so the store can be swapped without
    touching business logic.
    """

    @abstractmethod
    async def save(self, order: T, session: Optional[Any] = None) -> T:
        """Persists an order aggregate. Handles both inserts and updates."""
        pass

    @abstractmethod
    async def find_by_id(self, order_id: str, session: Optional[Any] = None) -> Optional[T]:
        """Retrieves an order by its unique identifier, or None."""
        pass

    @abstractmethod
    async def find_by_account(self, account_login: int) -> List[T]:
        """Retrieves every order belonging to an account."""
        pass

    async def find_active_orders_by_account(self, account_login: int) -> List[T]:
        """Retrieves open/pending orders for an account. Used by risk checks and UI."""
        raise NotImplementedError(
            "IOrderRepository.find_active_orders_by_account is part of the extended MT5 query surface and is not "
            "implemented by this repository yet."
        )

    async def find_pending_orders(self, account_login: int) -> List[T]:
        """Get all pending orders (not filled/cancelled/rejected/expired)."""
        raise NotImplementedError(
            "IOrderRepository.find_pending_orders is part of the extended MT5 query surface and is not "
            "implemented by this repository yet."
        )

    async def find_by_symbol_and_state(self, symbol: str, state: str) -> List[T]:
        """Get orders by symbol and state."""
        raise NotImplementedError(
            "IOrderRepository.find_by_symbol_and_state is part of the extended MT5 query surface and is not "
            "implemented by this repository yet."
        )

    async def find_expired_orders(self, before_time: datetime) -> List[T]:
        """Get orders past their time_expiration, for the expiry sweeper."""
        raise NotImplementedError(
            "IOrderRepository.find_expired_orders is part of the extended MT5 query surface and is not "
            "implemented by this repository yet."
        )

    async def get_next_ticket_id(self) -> str:
        """Allocate the next sequential ticket id (MT5 style). Must be atomic."""
        raise NotImplementedError(
            "IOrderRepository.get_next_ticket_id is part of the extended MT5 query surface and is not "
            "implemented by this repository yet."
        )

    async def delete(self, order_id: str) -> bool:
        """Remove an order record. Returns True if a row was deleted."""
        raise NotImplementedError(
            "IOrderRepository.delete is part of the extended MT5 query surface and is not "
            "implemented by this repository yet."
        )
class IDealRepository(ABC, Generic[T]):
    """
    Contract for Deal persistence (MT5 IMTDeal).

    Deals are immutable execution records: an append-only log. MT5 trade
    modification is a reversal plus a correction deal chained through
    original_deal_id, never a mutation of an existing deal.
    """

    @abstractmethod
    async def save(self, deal: T, session: Optional[Any] = None) -> T:
        """Persists an immutable deal entity."""
        pass

    @abstractmethod
    async def find_by_id(self, deal_id: str, session: Optional[Any] = None) -> Optional[T]:
        """Retrieves a deal by its unique identifier."""
        pass

    async def find_by_order_id(self, order_id: str) -> List[T]:
        """Retrieves all deals generated by a given order."""
        raise NotImplementedError(
            "IDealRepository.find_by_order_id is part of the extended MT5 query surface and is not "
            "implemented by this repository yet."
        )

    async def find_by_position_id(self, position_id: str) -> List[T]:
        """Get all deals that make up a position."""
        raise NotImplementedError(
            "IDealRepository.find_by_position_id is part of the extended MT5 query surface and is not "
            "implemented by this repository yet."
        )

    @abstractmethod
    async def find_by_account(self, account_login: int) -> List[T]:
        """Retrieves all deals executed for an account."""
        pass

    async def find_by_account_and_symbol(self, account_login: int, symbol: str) -> List[T]:
        """Get deals for an account and symbol."""
        raise NotImplementedError(
            "IDealRepository.find_by_account_and_symbol is part of the extended MT5 query surface and is not "
            "implemented by this repository yet."
        )

    async def find_by_entry_type(self, account_login: int, entry: str) -> List[T]:
        """Get deals by entry type (IN, OUT, INOUT, OUT_BY)."""
        raise NotImplementedError(
            "IDealRepository.find_by_entry_type is part of the extended MT5 query surface and is not "
            "implemented by this repository yet."
        )

    async def find_trade_modifications(self, original_deal_id: str) -> List[T]:
        """Get reversal and correction deals chained to an original deal."""
        raise NotImplementedError(
            "IDealRepository.find_trade_modifications is part of the extended MT5 query surface and is not "
            "implemented by this repository yet."
        )
class IMatchingEngine(ABC, Generic[T]):
    """
    Contract for the core trading logic.

    Architectural Purpose:
    Defines how orders are processed against the market.
    Allows swapping the engine implementation (e.g., Python prototype -> Rust PyO3 module)
    via Dependency Injection without changing the OMS domain logic.
    """

    @abstractmethod
    async def submit_order(self, order: T) -> None:
        """
        Submits an order to the engine for processing.
        Triggers immediate matching logic or queues it.
        """
        pass

    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """
        Attempts to cancel an existing order.
        Returns True if successful, False otherwise.
        """
        pass

    @abstractmethod
    async def modify_order(self, order_id: str, new_price: Decimal, new_quantity: int) -> bool:
        """
        Modifies an existing order (Price/Quantity).
        In strict FIFO engines, this might be implemented as Cancel+Replace.
        """
        pass

    @abstractmethod
    def get_market_state(self, symbol: str) -> dict:
        """
        Returns the current state of the order book for a symbol.
        Used for pre-trade checks and visibility.
        """
        pass

    async def execute_internal(self, order: T, *, record: bool = True) -> Any:
        """Price and internalise a B-Book fill: the broker is the counterparty.

        Declared with a default that raises, rather than left off the port, because
        ExecutionOrchestrator._execute_b_book calls exactly this and no engine had it -
        the call went to an object with no such attribute and every B-Book order was
        rejected with "object has no attribute 'execute_internal'". A B-Book broker
        without internalisation has no execution path at all, so it belongs on the port.

        Returns the fill Price. `record=False` prices without touching the order or the
        engine's fill log, for a caller that owns the state transition itself.
        """
        raise NotImplementedError(
            f"{type(self).__name__} does not implement execute_internal; it cannot "
            "internalise B-Book flow"
        )

    async def on_tick(self, tick: Any) -> Any:
        """Walk resting pending orders against a new price, activating any that cross.

        Default no-op: an engine that only internalises market orders has no book to
        walk, and the tick pipeline should not have to know which kind it was given.
        """
        return []


class ILiquidityGateway(ABC, Generic[T]):
    """
    Port for external Liquidity Provider (LP) connectivity.

    Architectural Purpose:
    Abstracts away the specific protocol (FIX, REST, WebSocket) used to
    communicate with external LPs (LMAX, Binance, Centroid, etc.).
    Allows adding/removing LPs without changing core execution logic.
    """

    @abstractmethod
    async def send_order(self, order: T, gateway_id: str) -> dict:
        """
        Sends an order to an external LP.
        Returns an execution report/acknowledgment.
        """
        pass

    @abstractmethod
    async def cancel_order(self, order_id: str, gateway_id: str) -> bool:
        """
        Cancels an order at the external LP.
        Returns True if successful.
        """
        pass

    @abstractmethod
    async def get_quotes(self, symbols: list[str]) -> dict[str, dict]:
        """
        Fetches current bid/ask quotes for multiple symbols.
        Returns {symbol: {bid, ask, timestamp}}.
        """
        pass


class ICoverageAccountRepository(ABC, Generic[T]):
    """
    Contract for Coverage Account (Risk Account) persistence.

    Architectural Purpose:
    Manages the broker's internal hedge accounts used to offset B-Book exposure.
    Critical for risk management and regulatory reporting.
    """

    @abstractmethod
    async def find_by_id(self, account_id: str) -> Optional[T]:
        """Retrieves a coverage account by ID."""
        pass

    @abstractmethod
    async def save(self, account: T) -> T:
        """Persists a coverage account."""
        pass

    @abstractmethod
    async def update_exposure(
        self,
        account_id: str,
        symbol: str,
        volume_delta: 'Decimal'
    ) -> None:
        """
        Updates net exposure for a symbol.
        volume_delta > 0: Client sold (Broker bought).
        volume_delta < 0: Client bought (Broker sold).
        """
        pass


class IRoutingRuleRepository(ABC, Generic[T]):
    """
    Contract for Routing Rule persistence.

    Architectural Purpose:
    Manages the dynamic routing rules that determine A-Book vs B-Book allocation.
    Rules can be updated at runtime without restarting the server.
    """

    @abstractmethod
    async def get_active_rules(self) -> List[T]:
        """Returns all enabled routing rules sorted by priority."""
        pass

    @abstractmethod
    async def save(self, rule: T) -> T:
        """Creates or updates a routing rule."""
        pass

    @abstractmethod
    async def delete(self, rule_id: str) -> bool:
        """Deletes a routing rule."""
        pass


class IPositionRepository(ABC, Generic[T]):
    """
    Contract for Position persistence (MT5 IMTPosition).

    Used by the risk engine and the margin loop to fetch open positions.
    """

    @abstractmethod
    async def save(self, position: T, session: Optional[Any] = None) -> T:
        """Persists a position (create or update)."""
        pass

    @abstractmethod
    async def find_by_id(self, position_id: str, session: Optional[Any] = None) -> Optional[T]:
        """Retrieves a position by id."""
        pass

    async def get_open_positions(self, session: Optional[Any] = None) -> List[T]:
        """Returns all open positions across all accounts."""
        raise NotImplementedError(
            "IPositionRepository.get_open_positions is part of the extended MT5 query surface and is not "
            "implemented by this repository yet."
        )

    async def get_positions_by_account(self, account_login: int) -> List[T]:
        """Returns all open positions for one account."""
        raise NotImplementedError(
            "IPositionRepository.get_positions_by_account is part of the extended MT5 query surface and is not "
            "implemented by this repository yet."
        )

    @abstractmethod
    async def get_by_account(self, account_login: int) -> List[T]:
        """Alias of get_positions_by_account, kept so existing callers do not break."""
        pass

    async def get_by_account_and_symbol(self, account_login: int, symbol: str) -> List[T]:
        """Get positions for an account and symbol."""
        raise NotImplementedError(
            "IPositionRepository.get_by_account_and_symbol is part of the extended MT5 query surface and is not "
            "implemented by this repository yet."
        )

    @abstractmethod
    async def get_by_symbol(self, symbol: str) -> List[T]:
        """Get all open positions in a symbol, for NOP/exposure calculation."""
        pass

    async def get_closed_positions(
        self, account_login: int, from_time: datetime, to_time: datetime
    ) -> List[T]:
        """Get closed positions within a time range."""
        raise NotImplementedError(
            "IPositionRepository.get_closed_positions is part of the extended MT5 query surface and is not "
            "implemented by this repository yet."
        )

    async def close(self, position_id: str) -> bool:
        """Marks a position closed. Returns True on success."""
        raise NotImplementedError(
            "IPositionRepository.close is part of the extended MT5 query surface and is not "
            "implemented by this repository yet."
        )

    async def delete(self, position_id: str) -> bool:
        """Remove a position record."""
        raise NotImplementedError(
            "IPositionRepository.delete is part of the extended MT5 query surface and is not "
            "implemented by this repository yet."
        )
class IRiskNotifier(ABC):
    """
    Port for sending margin call / stop out notifications.

    Architectural Purpose:
    Abstracts the notification delivery mechanism (Email, SMS, Push, etc.).
    Implementations can send notifications via multiple channels without
    changing the core risk monitoring logic.
    """

    @abstractmethod
    async def send_margin_call_alert(self, account_login: str, margin_level: 'Decimal') -> None:
        """
        Sends a margin call alert to the client.

        Args:
            account_login: The client's account login
            margin_level: Current margin level percentage
        """
        pass

    @abstractmethod
    async def send_stop_out_alert(self, account_login: str, closed_positions: List[str]) -> None:
        """
        Sends a stop-out notification after positions have been closed.

        Args:
            account_login: The client's account login
            closed_positions: List of position IDs that were force-closed
        """
        pass


# =========================================================================
# GROUP REPOSITORY
# =========================================================================

class IGroupRepository(ABC, Generic[T]):
    """
    Contract for Group persistence.

    In MT5 a Group IS the rule engine: it carries leverage, margin call and
    stop-out levels, free-margin mode, commissions, swaps, trade permissions,
    per-symbol overrides and routing. This port is what ConfigCache loads at
    startup so the hot path never touches the database.
    """

    @abstractmethod
    async def save(self, group: T, session: Optional[Any] = None) -> T:
        """Persists a group (create or update)."""
        pass

    async def find_by_id(self, group_id: str) -> Optional[T]:
        """Retrieves a group by its surrogate id."""
        raise NotImplementedError(
            "IGroupRepository.find_by_id is part of the extended MT5 query surface and is not "
            "implemented by this repository yet."
        )

    @abstractmethod
    async def find_by_name(self, name: str) -> Optional[T]:
        """Retrieves a group by MT5 path-style name, e.g. 'real\\real'."""
        pass

    @abstractmethod
    async def get_all(self) -> List[T]:
        """Returns every group. Called once at startup to warm the ConfigCache."""
        pass

    async def get_all_groups(self) -> List[T]:
        """Alias of get_all, kept so existing callers do not break."""
        raise NotImplementedError(
            "IGroupRepository.get_all_groups is part of the extended MT5 query surface and is not "
            "implemented by this repository yet."
        )

    async def delete(self, group_id: str) -> bool:
        """Remove a group. Returns True on success."""
        raise NotImplementedError(
            "IGroupRepository.delete is part of the extended MT5 query surface and is not "
            "implemented by this repository yet."
        )


class ISymbolRepository(ABC, Generic[T]):
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

    @abstractmethod
    async def get_all_symbols(self) -> List[T]:
        """Returns all available symbols."""
        pass

    async def get_all(self) -> List[T]:
        """Alias of get_all_symbols.

        ConfigCache.initialize() calls get_all(); every other repository in this
        codebase uses that name. Provided concretely rather than abstractly so existing
        implementations do not have to change.
        """
        return await self.get_all_symbols()


IInstrumentRepository = ISymbolRepository

# =========================================================================
# HOLIDAY REPOSITORY
# =========================================================================

class IHolidayRepository(ABC, Generic[T]):
    """
    Contract for Holiday persistence.
    
    Architectural Purpose:
    Provides access to holiday configurations needed for
    session checking and market-open validation.
    """

    @abstractmethod
    async def save(self, holiday: T) -> T:
        """Persist a holiday configuration."""
        pass

    @abstractmethod
    async def find_by_id(self, holiday_id: str) -> Optional[T]:
        """Find a holiday by its ID."""
        pass

    @abstractmethod
    async def get_active_holidays(
        self, check_date: "datetime"
    ) -> List[T]:
        """
        Get all holidays that apply to a given date.
        Used by SessionService to check if market is open.
        """
        pass

    @abstractmethod
    async def get_holidays_for_symbol(
        self, symbol_name: str, year: int
    ) -> List[T]:
        """Get all holidays for a symbol in a given year."""
        pass

    @abstractmethod
    async def delete(self, holiday_id: str) -> bool:
        """Delete a holiday configuration."""
        pass

    @abstractmethod
    async def get_all(self) -> List[T]:
        """Return all holiday configurations."""
        pass


class IMarketDataFeed(ABC):
    """
    [DEPRECATED in Phase 9] Contract for real-time market data access.
    Note: Prefer using MarketDataEngine.get_latest_tick(symbol) directly for zero-latency in-memory tick lookup.
    """

    @abstractmethod
    def get_bid(self, symbol: str) -> 'Decimal':
        """Returns current bid price for a symbol."""
        pass

    @abstractmethod
    def get_ask(self, symbol: str) -> 'Decimal':
        """Returns current ask price for a symbol."""
        pass

    @abstractmethod
    async def get_quotes(self, symbols: List[str]) -> dict[str, dict]:
        """Returns quotes for multiple symbols."""
        pass


class ITickFeed(ABC):
    """Contract for an external or internal market data feed source."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the feed provider."""
        pass

    @abstractmethod
    def stream_ticks(self) -> AsyncIterator[T]:
        """Stream continuous Tick objects."""
        pass

    @abstractmethod
    def stream_book(self, symbol: str) -> AsyncIterator[T]:
        """Stream Depth of Market OrderBook snapshots for a symbol."""
        pass


class IBarRepository(ABC):
    """Contract for persisting and querying OHLCV rate bars."""

    @abstractmethod
    async def save_bar(self, bar: T) -> T:
        """Persist a completed OHLCV bar."""
        pass

    @abstractmethod
    async def get_bars(self, symbol: str, timeframe: T, count: int = 100) -> List[T]:
        """Retrieve recent historical bars for a symbol and timeframe."""
        pass

    @abstractmethod
    async def get_latest_bar(self, symbol: str, timeframe: T) -> Optional[T]:
        """Retrieve the latest completed or running bar for a symbol and timeframe."""
        pass


class ILedgerRepository(ABC):
    """Contract for BalanceOperation persistence."""
    @abstractmethod
    async def save(self, operation: T) -> T: ...

    @abstractmethod
    async def get_by_account(self, account_login: str) -> List[T]: ...

    @abstractmethod
    async def get_by_reference(self, reference_id: str) -> Optional[T]: ...


class IRateLimiter(ABC):
    """Contract for rate limiting (sliding window)."""
    @abstractmethod
    async def is_allowed(self, key: str, limit: int, window_seconds: int) -> bool:
        """Returns True if request within limit, False if rate limited."""
        pass


class ITwoFactorService(ABC):
    """Contract for 2FA / TOTP authentication."""
    @abstractmethod
    def generate_secret(self) -> str:
        """Generates a base32 TOTP secret key."""
        pass

    @abstractmethod
    def get_provisioning_uri(self, secret: str, account_name: str, issuer_name: str = "BrokerPlatform") -> str:
        """Returns otpauth:// URI for QR code generation."""
        pass

    @abstractmethod
    def verify_code(self, secret: str, code: str) -> bool:
        """Verifies a 6-digit TOTP code."""
        pass


class IIPWhitelist(ABC):
    """Contract for CIDR IP Whitelisting."""
    @abstractmethod
    def is_allowed(self, client_ip: str, allowed_cidrs: List[str]) -> bool:
        """Returns True if client_ip matches any CIDR or exact IP in allowed_cidrs."""
        pass


class ITokenBlacklist(ABC):
    """Contract for JWT Token Blacklisting / Revocation."""
    @abstractmethod
    async def add(self, token: str, expires_at: datetime) -> None:
        """Blacklists a token until expires_at."""
        pass

    @abstractmethod
    async def is_blacklisted(self, token: str) -> bool:
        """Returns True if token has been revoked."""
        pass


class IManagerRepository(ABC, Generic[T]):
    """Contract for Manager Account persistence."""
    @abstractmethod
    async def find_by_login(self, login: str) -> Optional[T]:
        """Retrieves a manager account by login."""
        pass

    @abstractmethod
    async def save(self, manager: T) -> T:
        """Persists a manager account."""
        pass


class IHistoricalTickRepository(ABC):
    """Contract for historical tick persistence (ClickHouse)."""
    @abstractmethod
    async def save_tick(self, tick: T) -> None:
        """Saves a single tick."""
        pass

    @abstractmethod
    async def save_ticks_batch(self, ticks: List[T]) -> None:
        """Saves multiple ticks in batch."""
        pass

    @abstractmethod
    async def get_ticks(self, symbol: str, start: datetime, end: datetime, limit: int = 10000) -> List[T]:
        """Retrieves historical ticks for a symbol within time window."""
        pass


class IHistoricalBarRepository(ABC):
    """Contract for historical OHLCV bar persistence (ClickHouse)."""
    @abstractmethod
    async def save_bar(self, bar: T) -> T:
        """Saves a completed OHLCV bar."""
        pass

    @abstractmethod
    async def save_bars_batch(self, bars: List[T]) -> None:
        """Saves multiple OHLCV bars in batch."""
        pass

    @abstractmethod
    async def get_bars(self, symbol: str, timeframe: Any, limit: int = 1000) -> List[T]:
        """Retrieves historical OHLCV bars for a symbol and timeframe."""
        pass



