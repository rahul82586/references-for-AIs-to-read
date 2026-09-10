import threading
import logging
from typing import Dict, List, Callable, Any

logger = logging.getLogger(__name__)

class EventBus:
    """
    A thread-safe singleton Event Bus for decoupled communication.
    Supports simple publish/subscribe patterns.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EventBus, cls).__new__(cls)
                cls._instance._subscribers: Dict[str, List[Callable]] = {}
                cls._instance._sub_lock = threading.Lock()
        return cls._instance
    
    def subscribe(self, event_type: str, callback: Callable[[Any], None]):
        """Registers a callback for a specific event type."""
        with self._sub_lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            if callback not in self._subscribers[event_type]:
                self._subscribers[event_type].append(callback)
                logger.debug(f"Subscribed {callback.__name__} to {event_type}")

    def unsubscribe(self, event_type: str, callback: Callable[[Any], None]):
        """Removes a callback for a specific event type."""
        with self._sub_lock:
            if event_type in self._subscribers and callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)
                logger.debug(f"Unsubscribed {callback.__name__} from {event_type}")

    def publish(self, event_type: str, data: Any = None):
        """Notifies all subscribers of an event."""
        with self._sub_lock:
            callbacks = list(self._subscribers.get(event_type, []))
        
        for callback in callbacks:
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Error in EventBus callback {callback.__name__} for {event_type}: {e}")

# Global instance for convenience
bus = EventBus()
