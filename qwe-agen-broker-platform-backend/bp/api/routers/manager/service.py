"""
MT5 Manager API - Service Router.

Exposes endpoints that mirror MT5 Manager API service operations:
- GET /api/v1/manager/Ping
- GET /api/v1/manager/StartTimeUtc
- GET /api/v1/manager/MemoryUsage
- GET /api/v1/manager/Version

These endpoints are used for:
- Health monitoring (Kubernetes liveness/readiness probes)
- Server diagnostics
- Client keep-alive
- Version compatibility checks

Architectural Note:
These endpoints do NOT require authentication for /Ping (health checks).
Other endpoints require manager authentication.
"""
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from typing import Optional

from api.auth.admin_dependencies import get_current_manager
from api.schemas.manager.service import (
    MemoryUsage,
    PingResponse,
    ServerInfo,
    VersionInfo,
)
from application.services.server_info_service import get_server_info_service
from core.domains.accounts.account import Account

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/manager", tags=["Manager - Service"])


# ============================================================================
# Ping - Health check (NO AUTH REQUIRED)
# ============================================================================

@router.get(
    "/Ping",
    response_model=PingResponse,
    summary="Health check / keep-alive",
)
async def ping() -> PingResponse:
    """
    Health check endpoint.
    
    Mirrors MT5 Manager API `Ping` endpoint.
    
    This endpoint does NOT require authentication and is used by:
    - Load balancers for health checks
    - Kubernetes liveness/readiness probes
    - Client keep-alive mechanisms
    """
    ping_data = get_server_info_service().get_ping()
    
    return PingResponse(
        retcode=0,
        server_time=ping_data["server_time"],
        status=ping_data["status"],
        latency_ms=ping_data.get("latency_ms"),
    )


# ============================================================================
# StartTimeUtc - Server start time
# ============================================================================

@router.get(
    "/StartTimeUtc",
    response_model=ServerInfo,
    summary="Get server start time and uptime",
)
async def start_time_utc(
    manager: Account = Depends(get_current_manager),
) -> ServerInfo:
    """
    Get server start time and uptime information.
    
    Mirrors MT5 Manager API `StartTimeUtc` endpoint.
    """
    server_info = get_server_info_service().get_server_info()
    
    return ServerInfo(**server_info)


# ============================================================================
# MemoryUsage - Process memory statistics
# ============================================================================

@router.get(
    "/MemoryUsage",
    response_model=MemoryUsage,
    summary="Get process memory usage statistics",
)
async def memory_usage(
    manager: Account = Depends(get_current_manager),
) -> MemoryUsage:
    """
    Get process memory usage statistics.
    
    Mirrors MT5 Manager API `MemoryUsage` endpoint.
    
    Returns:
    - RSS (Resident Set Size) - actual physical memory used
    - VMS (Virtual Memory Size) - total virtual memory
    - CPU usage percentage
    - Open file descriptors
    - Thread count
    """
    memory_data = get_server_info_service().get_memory_usage()
    
    return MemoryUsage(
        retcode=0,
        **memory_data,
    )


# ============================================================================
# Version - Server version information
# ============================================================================

@router.get(
    "/Version",
    response_model=VersionInfo,
    summary="Get server version information",
)
async def version(
    manager: Account = Depends(get_current_manager),
) -> VersionInfo:
    """
    Get server version information.
    
    Mirrors MT5 Manager API `Version` endpoint.
    
    Used by clients to:
    - Check API compatibility
    - Display version in UI
    - Validate feature availability
    """
    version_data = get_server_info_service().get_version_info()
    
    return VersionInfo(**version_data)