"""
Core Ports - The Contracts That Enable Swappable Infrastructure

These abstract base classes define the boundaries between the pure domain logic
and external concerns (databases, message brokers, matching engines).
Implementations live in the infrastructure layer and are injected at runtime.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic, Callable, AsyncIterator
from datetime import datetime
from decimal import Decimal

from core.events.domain_events import DomainEvent

T = TypeVar('T')


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
    async def subscribe(self, channel: str, callback: Callable[[dict], None]) -> None:
        """
        Subscribes to a specific channel and invokes the callback upon message receipt.
        The callback receives a deserialized dictionary representation of the event.
        """
        pass

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


class IOrderRepository(ABC, Generic[T]):
    """
    Contract for Order persistence.

    Architectural Purpose:
    Hides the database technology (PostgreSQL, MongoDB, etc.) from the Domain.
    The OMS domain logic calls save() or find_by_id(), unaware of SQL or ORM.
    This enables swapping databases without touching core business logic.
    """

    @abstractmethod
    async def save(self, order: T) -> T:
        """
        Persists an order aggregate. Handles both inserts and updates.
        Returns the persisted object (often with updated DB IDs).
        """
        pass

    @abstractmethod
    async def find_by_id(self, order_id: str) -> Optional[T]:
        """
        Retrieves an order by its unique identifier.
        Returns None if not found.
        """
        pass

    @abstractmethod
    async def find_active_orders_by_account(self, account_id: str) -> List[T]:
        """
        Retrieves all open/pending orders for a specific account.
        Crucial for risk checks and UI display.
        """
        pass

    @abstractmethod
    async def get_next_ticket_id(self) -> str:
        """
        Generates a unique, sequential ticket ID (MT5 style).
        Implementation must ensure thread-safety/atomicity.
        """
        pass


class IDealRepository(ABC, Generic[T]):
    """
    Contract for Deal persistence.
    Deals are immutable execution records (append-only log).
    """

    @abstractmethod
    async def save(self, deal: T, session: Optional[Any] = None) -> T:
        """Persists an immutable deal entity."""
        pass

    @abstractmethod
    async def find_by_id(self, deal_id: str) -> Optional[T]:
        """Retrieves a deal by its unique identifier."""
        pass

    @abstractmethod
    async def find_by_order_id(self, order_id: str) -> List[T]:
        """Retrieves all deals associated with a given order."""
        pass

    @abstractmethod
    async def find_by_account(self, account_login: str) -> List[T]:
        """Retrieves all deals executed for a specific account."""
        pass


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
    Contract for Position persistence.

    Architectural Purpose:
    Manages open positions for margin calculations and risk monitoring.
    Used by the RiskWorker to fetch positions for stop-out checks.
    """

    @abstractmethod
    async def get_open_positions(self) -> List[T]:
        """Returns all open positions across all accounts."""
        pass

    @abstractmethod
    async def get_positions_by_account(self, account_login: str) -> List[T]:
        """Returns all open positions for a specific account."""
        pass

    @abstractmethod
    async def save(self, position: T) -> T:
        """Persists a position (create or update)."""
        pass

    @abstractmethod
    async def close(self, position_id: str) -> bool:
        """Marks a position as closed."""
        pass


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


class ISymbolRepository(ABC, Generic[T]):
    """
    Contract for Symbol/Instrument persistence.

    Architectural Purpose:
    Provides access to instrument specifications (contract size, tick value, etc.)
    needed for margin and PnL calculations.
    """

    @abstractmethod
    def get_symbol(self, symbol_name: str) -> T:
        """Returns symbol specification by name."""
        pass

    @abstractmethod
    async def get_all_symbols(self) -> List[T]:
        """Returns all available symbols."""
        pass


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



# ============================================================================
# ORDER REPOSITORY - Add these methods
# ============================================================================

class IOrderRepository(ABC, Generic[T]):
    """Contract for Order persistence."""

    @abstractmethod
    async def save(self, order: T) -> T:
        pass

    @abstractmethod
    async def find_by_id(self, order_id: str) -> Optional[T]:
        pass

    @abstractmethod
    async def find_by_account(self, account_login: int) -> List[T]:
        pass

    @abstractmethod
    async def find_pending_orders(self, account_login: int) -> List[T]:
        """Get all pending orders (not filled/cancelled) for an account."""
        pass

    @abstractmethod
    async def find_by_symbol_and_state(self, symbol: str, state: str) -> List[T]:
        """Get orders by symbol and state."""
        pass

    @abstractmethod
    async def find_expired_orders(self, before_time: datetime) -> List[T]:
        """Get orders that have expired (time_expiration < before_time)."""
        pass

    @abstractmethod
    async def delete(self, order_id: str) -> bool:
        pass


# ============================================================================
# DEAL REPOSITORY - Add these methods
# ============================================================================

class IDealRepository(ABC, Generic[T]):
    """Contract for Deal persistence."""

    @abstractmethod
    async def save(self, deal: T) -> T:
        pass

    @abstractmethod
    async def find_by_id(self, deal_id: str) -> Optional[T]:
        pass

    @abstractmethod
    async def find_by_order_id(self, order_id: str) -> List[T]:
        pass

    @abstractmethod
    async def find_by_position_id(self, position_id: str) -> List[T]:
        """Get all deals for a position."""
        pass

    @abstractmethod
    async def find_by_account(self, account_login: int) -> List[T]:
        pass

    @abstractmethod
    async def find_by_account_and_symbol(self, account_login: int, symbol: str) -> List[T]:
        """Get deals for a specific account and symbol."""
        pass

    @abstractmethod
    async def find_by_entry_type(self, account_login: int, entry: str) -> List[T]:
        """Get deals by entry type (IN, OUT, INOUT, OUT_BY)."""
        pass

    @abstractmethod
    async def find_trade_modifications(self, original_deal_id: str) -> List[T]:
        """Get reversal and correction deals linked to original deal."""
        pass


# ============================================================================
# POSITION REPOSITORY - Add these methods
# ============================================================================

class IPositionRepository(ABC, Generic[T]):
    """Contract for Position persistence."""

    @abstractmethod
    async def save(self, position: T) -> T:
        pass

    @abstractmethod
    async def find_by_id(self, position_id: str) -> Optional[T]:
        pass

    @abstractmethod
    async def get_open_positions(self, session: Optional[Any] = None) -> List[T]:
        pass

    @abstractmethod
    async def get_by_account(self, account_login: int) -> List[T]:
        """Get all open positions for an account."""
        pass

    @abstractmethod
    async def get_by_account_and_symbol(self, account_login: int, symbol: str) -> List[T]:
        """Get positions for a specific account and symbol."""
        pass

    @abstractmethod
    async def get_by_symbol(self, symbol: str) -> List[T]:
        """Get all open positions for a symbol (for exposure calculation)."""
        pass

    @abstractmethod
    async def get_closed_positions(self, account_login: int, from_time: datetime, to_time: datetime) -> List[T]:
        """Get closed positions within a time range."""
        pass

    @abstractmethod
    async def delete(self, position_id: str) -> bool:
        pass