"""
In-Memory Configuration Cache - MT5-Like Speed for Python.

Loads all configs into RAM at startup for sub-microsecond lookups.
Updates via Event Bus when configs change.
Persists to PostgreSQL as source of truth.
"""
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from core.domains.accounts.group import Group
from core.domains.accounts.client import Client
from core.domains.accounts.account import Account
from core.domains.instruments.symbol import Symbol
from core.domains.instruments.holiday import Holiday
from core.domains.oms.entities.position import Position
from core.ports.interfaces import (
    IGroupRepository,
    IAccountRepository,
    ISymbolRepository,
    IHolidayRepository,
    IPositionRepository,
    IEventBus,
)
from core.events.domain_events import (
    GroupCreated, GroupUpdated, GroupDeleted,
    SymbolCreated, SymbolUpdated, SymbolDeleted,
    HolidayCreated, HolidayUpdated, HolidayDeleted,
)

logger = logging.getLogger(__name__)


class ConfigCache:
    """
    In-memory cache for all configuration data.
    
    MT5 Parity:
    - Mirrors MT5's in-memory config model
    - Sub-microsecond lookups (vs PostgreSQL's milliseconds)
    - Event-driven updates (like MT5's Sink pattern)
    """
    
    def __init__(
        self,
        group_repo: IGroupRepository,
        account_repo: IAccountRepository,
        symbol_repo: ISymbolRepository,
        holiday_repo: IHolidayRepository,
        position_repo: IPositionRepository,
        event_bus: IEventBus,
    ):
        self.group_repo = group_repo
        self.account_repo = account_repo
        self.symbol_repo = symbol_repo
        self.holiday_repo = holiday_repo
        self.position_repo = position_repo
        self.event_bus = event_bus
        
        # In-memory caches (Python dicts = O(1) lookups)
        self._groups: Dict[str, Group] = {}
        self._accounts: Dict[int, Account] = {}
        self._symbols: Dict[str, Symbol] = {}
        self._holidays: Dict[str, Holiday] = {}  # holiday_id -> Holiday
        self._positions: Dict[str, Position] = {}
        
        # Secondary indexes for fast queries
        self._accounts_by_group: Dict[str, List[int]] = {}  # group_id -> [login]
        self._positions_by_account: Dict[int, List[str]] = {}  # login -> [position_id]
        self._positions_by_symbol: Dict[str, List[str]] = {}  # symbol -> [position_id]
        
        self._initialized = False
    
    async def initialize(self) -> None:
        """
        Load all configs from PostgreSQL into memory.
        Called once at startup.
        """
        logger.info("Initializing ConfigCache from PostgreSQL...")
        start = datetime.now(timezone.utc)
        
        # Load groups
        groups = await self.group_repo.get_all()
        for group in groups:
            self._groups[group.id] = group
        logger.info(f"Loaded {len(groups)} groups")
        
        # Load symbols
        symbols = await self.symbol_repo.get_all()
        for symbol in symbols:
            self._symbols[symbol.name] = symbol
        logger.info(f"Loaded {len(symbols)} symbols")
        
        # Load holidays
        holidays = await self.holiday_repo.get_all()
        for holiday in holidays:
            self._holidays[holiday.id] = holiday
        logger.info(f"Loaded {len(holidays)} holidays")
        
        # Load accounts
        accounts = await self.account_repo.find_all()
        for account in accounts:
            self._accounts[account.login] = account
            # Build secondary index
            if account.group_id not in self._accounts_by_group:
                self._accounts_by_group[account.group_id] = []
            self._accounts_by_group[account.group_id].append(account.login)
        logger.info(f"Loaded {len(accounts)} accounts")
        
        # Load open positions
        positions = await self.position_repo.get_open_positions()
        for position in positions:
            self._positions[position.position_id] = position
            # Build secondary indexes
            if position.account_login not in self._positions_by_account:
                self._positions_by_account[position.account_login] = []
            self._positions_by_account[position.account_login].append(position.position_id)
            
            if position.symbol not in self._positions_by_symbol:
                self._positions_by_symbol[position.symbol] = []
            self._positions_by_symbol[position.symbol].append(position.position_id)
        logger.info(f"Loaded {len(positions)} open positions")
        
        # Subscribe to config change events
        await self._subscribe_to_events()
        
        elapsed = (datetime.now(timezone.utc) - start).total_seconds()
        self._initialized = True
        logger.info(f"ConfigCache initialized in {elapsed:.2f}s")
    
    async def _subscribe_to_events(self) -> None:
        """Subscribe to domain events for cache invalidation."""
        self.event_bus.subscribe(GroupCreated, self._on_group_created)
        self.event_bus.subscribe(GroupUpdated, self._on_group_updated)
        self.event_bus.subscribe(GroupDeleted, self._on_group_deleted)
        self.event_bus.subscribe(SymbolCreated, self._on_symbol_updated)
        self.event_bus.subscribe(SymbolUpdated, self._on_symbol_updated)
        self.event_bus.subscribe(SymbolDeleted, self._on_symbol_deleted)
        self.event_bus.subscribe(HolidayCreated, self._on_holiday_updated)
        self.event_bus.subscribe(HolidayUpdated, self._on_holiday_updated)
        # M9: fills and closes refresh this account's positions slice, so the
        # synchronous reads (routing conditions 4005/4006, the positions API's
        # cache path) see the book as it is, not as it was at boot. Class-based
        # subscription reaches in-process publishers; cross-process cache
        # invalidation arrives with the cluster milestone (documented).
        from core.events.domain_events import DealCreated, PositionClosed

        self.event_bus.subscribe(DealCreated, self._on_positions_changed)
        self.event_bus.subscribe(PositionClosed, self._on_positions_changed)
        self.event_bus.subscribe(HolidayDeleted, self._on_holiday_deleted)
    
    # =========================================================================
    # FAST LOOKUPS (Sub-Microsecond)
    # =========================================================================
    
    def get_group(self, group_id: str) -> Optional[Group]:
        """Get group by ID (O(1) lookup)."""
        return self._groups.get(group_id)
    
    def get_all_groups(self) -> List[Group]:
        """Get all groups."""
        return list(self._groups.values())
    
    def get_symbol(self, symbol_name: str) -> Optional[Symbol]:
        """Get symbol by name (O(1) lookup)."""
        return self._symbols.get(symbol_name)
    
    def get_all_symbols(self) -> List[Symbol]:
        """Get all symbols."""
        return list(self._symbols.values())
    
    def get_account(self, login: int) -> Optional[Account]:
        """Get account by login (O(1) lookup)."""
        return self._accounts.get(login)
    
    def get_accounts_by_group(self, group_id: str) -> List[Account]:
        """Get all accounts in a group (O(1) via index)."""
        logins = self._accounts_by_group.get(group_id, [])
        return [self._accounts[login] for login in logins if login in self._accounts]
    
    async def _on_positions_changed(self, event: Any) -> None:
        """Re-read one account's open positions after a fill or a close."""
        login = self._login_from_event(event)
        if login is None:
            return
        try:
            positions = await self.position_repo.get_positions_by_account(login)
        except Exception:  # noqa: BLE001 - the cache must never kill the bus
            logger.exception("could not refresh positions for account %s", login)
            return
        for pid in self._positions_by_account.pop(login, []):
            stale = self._positions.pop(pid, None)
            if stale is not None:
                ids = self._positions_by_symbol.get(stale.symbol)
                if ids and pid in ids:
                    ids.remove(pid)
        for position in positions:
            self._positions[position.position_id] = position
            self._positions_by_account.setdefault(login, []).append(position.position_id)
            self._positions_by_symbol.setdefault(position.symbol, []).append(position.position_id)

    @staticmethod
    def _login_from_event(event: Any) -> Optional[int]:
        """account_login from either bus shape: the event object or the dict."""
        payload = getattr(event, "payload", None)
        if payload is None and isinstance(event, dict):
            inner = event.get("payload")
            payload = inner if isinstance(inner, dict) else event
        if not isinstance(payload, dict):
            return None
        raw = payload.get("account_login")
        try:
            return int(raw) if raw is not None else None
        except (TypeError, ValueError):
            return None

    def get_position(self, position_id: str) -> Optional[Position]:
        """Get position by ID (O(1) lookup)."""
        return self._positions.get(position_id)
    
    def get_positions_by_account(self, login: int) -> List[Position]:
        """Get all open positions for an account (O(1) via index)."""
        position_ids = self._positions_by_account.get(login, [])
        return [self._positions[pid] for pid in position_ids if pid in self._positions]
    
    def get_positions_by_symbol(self, symbol: str) -> List[Position]:
        """Get all open positions for a symbol (O(1) via index)."""
        position_ids = self._positions_by_symbol.get(symbol, [])
        return [self._positions[pid] for pid in position_ids if pid in self._positions]
    
    def get_holiday(self, holiday_id: str) -> Optional[Holiday]:
        """Get holiday by ID."""
        return self._holidays.get(holiday_id)
    
    def get_all_holidays(self) -> List[Holiday]:
        """Get all holidays."""
        return list(self._holidays.values())
    
    # =========================================================================
    # CACHE MUTATION (Called by Command Handlers)
    # =========================================================================
    
    def upsert_group(self, group: Group) -> None:
        """Insert or update a group in cache."""
        self._groups[group.id] = group
    
    def delete_group(self, group_id: str) -> None:
        """Delete a group from cache."""
        self._groups.pop(group_id, None)
    
    def upsert_symbol(self, symbol: Symbol) -> None:
        """Insert or update a symbol in cache."""
        self._symbols[symbol.name] = symbol
    
    def delete_symbol(self, symbol_name: str) -> None:
        """Delete a symbol from cache."""
        self._symbols.pop(symbol_name, None)
    
    def upsert_account(self, account: Account) -> None:
        """Insert or update an account in cache."""
        # Update secondary index if group changed
        old_account = self._accounts.get(account.login)
        if old_account and old_account.group_id != account.group_id:
            # Remove from old group index
            old_group_logins = self._accounts_by_group.get(old_account.group_id, [])
            if account.login in old_group_logins:
                old_group_logins.remove(account.login)
            
            # Add to new group index
            if account.group_id not in self._accounts_by_group:
                self._accounts_by_group[account.group_id] = []
            if account.login not in self._accounts_by_group[account.group_id]:
                self._accounts_by_group[account.group_id].append(account.login)
        
        self._accounts[account.login] = account
    
    def upsert_position(self, position: Position) -> None:
        """Insert or update a position in cache."""
        # Handle closed positions (remove from indexes)
        if position.time_done is not None:
            self._positions.pop(position.position_id, None)
            # Remove from indexes
            account_positions = self._positions_by_account.get(position.account_login, [])
            if position.position_id in account_positions:
                account_positions.remove(position.position_id)
            symbol_positions = self._positions_by_symbol.get(position.symbol, [])
            if position.position_id in symbol_positions:
                symbol_positions.remove(position.position_id)
            return
        
        # Open position: upsert + update indexes
        old_position = self._positions.get(position.position_id)
        if not old_position:
            # New position: add to indexes
            if position.account_login not in self._positions_by_account:
                self._positions_by_account[position.account_login] = []
            self._positions_by_account[position.account_login].append(position.position_id)
            
            if position.symbol not in self._positions_by_symbol:
                self._positions_by_symbol[position.symbol] = []
            self._positions_by_symbol[position.symbol].append(position.position_id)
        
        self._positions[position.position_id] = position
    
    # =========================================================================
    # EVENT HANDLERS (Cache Invalidation)
    # =========================================================================
    
    async def _on_group_created(self, event) -> None:
        group_id = event.payload.get("group_id")
        if group_id:
            group = await self.group_repo.find_by_id(group_id)
            if group:
                self.upsert_group(group)
                logger.debug(f"Cache: Group {group_id} created")
    
    async def _on_group_updated(self, event) -> None:
        await self._on_group_created(event)  # Same logic
    
    async def _on_group_deleted(self, event) -> None:
        group_id = event.payload.get("group_id")
        if group_id:
            self.delete_group(group_id)
            logger.debug(f"Cache: Group {group_id} deleted")
    
    async def _on_symbol_updated(self, event) -> None:
        symbol_name = event.payload.get("symbol_name")
        if symbol_name:
            symbol = await self.symbol_repo.find_by_name(symbol_name)
            if symbol:
                self.upsert_symbol(symbol)
    
    async def _on_symbol_deleted(self, event) -> None:
        symbol_name = event.payload.get("symbol_name")
        if symbol_name:
            self.delete_symbol(symbol_name)
    
    async def _on_holiday_updated(self, event) -> None:
        holiday_id = event.payload.get("holiday_id")
        if holiday_id:
            holiday = await self.holiday_repo.find_by_id(holiday_id)
            if holiday:
                self._holidays[holiday_id] = holiday
    
    async def _on_holiday_deleted(self, event) -> None:
        holiday_id = event.payload.get("holiday_id")
        if holiday_id:
            self._holidays.pop(holiday_id, None)
    
    # =========================================================================
    # DIAGNOSTICS
    # =========================================================================
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        return {
            "initialized": self._initialized,
            "groups": len(self._groups),
            "symbols": len(self._symbols),
            "accounts": len(self._accounts),
            "positions": len(self._positions),
            "holidays": len(self._holidays),
        }


# Singleton instance
_config_cache: Optional[ConfigCache] = None


def get_config_cache() -> ConfigCache:
    """Get the singleton ConfigCache instance."""
    global _config_cache
    if _config_cache is None:
        raise RuntimeError("ConfigCache not initialized. Call initialize() first.")
    return _config_cache


def set_config_cache(cache: ConfigCache) -> None:
    """Set the singleton ConfigCache instance (called at startup)."""
    global _config_cache
    _config_cache = cache