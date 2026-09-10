from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class BaseConnector(ABC):
    """
    Abstract base class for all exchange/data connectors.
    Follows SFA architecture patterns.
    """

    display_name: str = "Base Connector"
    connector_id: str = "base"
    required_params: List[str] = []

    def __init__(self, config: Dict[str, Any], tag: Optional[str] = None):
        self.config = config
        self.tag = tag
        self.is_connected = False
        # The unique ID from the database or simulation
        self.instance_id = config.get("id", self.connector_id)
        self._last_ticks: Dict[str, Dict] = {}

    @abstractmethod
    def connect(self) -> bool:
        """Establishes connection to the exchange/data source."""
        pass

    @abstractmethod
    def disconnect(self):
        """Closes the connection."""
        pass

    def get_tick(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Retrieves the latest price data for a symbol from the local cache."""
        return self._last_ticks.get(symbol)

    @abstractmethod
    def place_order(self, symbol: str, side: str, volume: float,
                    price: Optional[float] = None) -> Dict[str, Any]:
        """Places a buy or sell order."""
        pass

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Cancels an existing order."""
        pass

    @abstractmethod
    def get_balance(self) -> Dict[str, float]:
        """Retrieves account balances."""
        pass
    
    @abstractmethod
    def get_positions(self) -> List[Dict[str, Any]]:
        """Retrieves open positions."""
        pass

    # ── Non-abstract helpers (subclasses override as needed) ──────────────────

    def get_symbol_list(self) -> List[Dict]:
        """Returns tradeable symbols on this connector.
        Each dict: {symbol, description, asset_class, currency, contract_size, unit}
        Override in subclass. Default returns empty list.
        """
        return []

    def subscribe_symbol(self, symbol: str):
        """Subscribe/activate a symbol for streaming.
        Default is no-op — subclass overrides if it supports dynamic subscriptions.
        """
        pass

    def unsubscribe_symbol(self, symbol: str) -> None:
        """Unsubscribe a symbol from streaming.
        Default is no-op — subclass overrides if it supports dynamic subscriptions.
        """
        pass

