"""
Server Information Service - Tracks server state for diagnostics.

Provides:
- Server start time and uptime
- Memory usage statistics
- Version information
- Health check data

Architectural Note:
This service is a singleton that tracks server-level state.
It is NOT part of the domain layer because server state is infrastructure concern.
"""
import logging
import platform
import sys
from datetime import datetime, timezone
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ServerInfoService:
    """
    Singleton service for server diagnostics.
    
    Provides MT5-compatible server information endpoints.
    """
    
    # Server metadata (set at startup)
    SERVER_NAME: str = "Broker Platform"
    SERVER_VERSION: str = "1.0.0"
    API_VERSION: str = "5.0.0"  # MT5 Manager API compatible
    BUILD_NUMBER: str = "2026.09.09"
    
    def __init__(self):
        self._start_time: datetime = datetime.now(timezone.utc)
        logger.info(
            f"ServerInfoService initialized: {self.SERVER_NAME} v{self.SERVER_VERSION}"
        )
    
    @property
    def start_time(self) -> datetime:
        """Server start time in UTC."""
        return self._start_time
    
    @property
    def uptime_seconds(self) -> int:
        """Server uptime in seconds."""
        now = datetime.now(timezone.utc)
        return int((now - self._start_time).total_seconds())
    
    @property
    def uptime_human(self) -> str:
        """Human-readable uptime string."""
        seconds = self.uptime_seconds
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{secs}s")
        
        return " ".join(parts)
    
    def get_ping(self) -> Dict[str, Any]:
        """Health check data."""
        return {
            "server_time": datetime.now(timezone.utc),
            "status": "OK",
            "latency_ms": 0.0,  # Could be measured via middleware
        }
    
    def get_server_info(self) -> Dict[str, Any]:
        """Full server information."""
        return {
            "server_name": self.SERVER_NAME,
            "server_version": self.SERVER_VERSION,
            "start_time_utc": self._start_time,
            "uptime_seconds": self.uptime_seconds,
            "uptime_human": self.uptime_human,
            "build_number": self.BUILD_NUMBER,
            "api_version": self.API_VERSION,
            "python_version": platform.python_version(),
        }
    
    def get_version_info(self) -> Dict[str, Any]:
        """Version information only."""
        return {
            "server_name": self.SERVER_NAME,
            "server_version": self.SERVER_VERSION,
            "api_version": self.API_VERSION,
            "build_number": self.BUILD_NUMBER,
            "python_version": platform.python_version(),
        }
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """
        Process memory usage statistics.
        
        Uses psutil if available, falls back to basic info.
        """
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            
            # Get total system memory
            virtual_memory = psutil.virtual_memory()
            
            return {
                "rss_mb": round(memory_info.rss / (1024 * 1024), 2),
                "vms_mb": round(memory_info.vms / (1024 * 1024), 2),
                "shared_mb": round(getattr(memory_info, 'shared', 0) / (1024 * 1024), 2),
                "text_mb": round(getattr(memory_info, 'text', 0) / (1024 * 1024), 2),
                "data_mb": round(getattr(memory_info, 'data', 0) / (1024 * 1024), 2),
                "percent": round(memory_info.rss / virtual_memory.total * 100, 2),
                "cpu_percent": process.cpu_percent(),
                "open_files": len(process.open_files()),
                "num_threads": process.num_threads(),
            }
        except ImportError:
            logger.warning("psutil not installed, returning basic memory info")
            return {
                "rss_mb": 0.0,
                "vms_mb": 0.0,
                "shared_mb": None,
                "text_mb": None,
                "data_mb": None,
                "percent": 0.0,
                "cpu_percent": 0.0,
                "open_files": 0,
                "num_threads": 0,
            }
        except Exception as e:
            logger.error(f"Failed to get memory usage: {e}")
            return {
                "rss_mb": 0.0,
                "vms_mb": 0.0,
                "shared_mb": None,
                "text_mb": None,
                "data_mb": None,
                "percent": 0.0,
                "cpu_percent": 0.0,
                "open_files": 0,
                "num_threads": 0,
            }


# Singleton instance
_server_info_service: ServerInfoService = None


def get_server_info_service() -> ServerInfoService:
    """Get or create the singleton ServerInfoService."""
    global _server_info_service
    if _server_info_service is None:
        _server_info_service = ServerInfoService()
    return _server_info_service