"""
MT5 Manager API - Connection Router.

Exposes endpoints that mirror MT5 Manager API connection operations:
- POST /api/v1/manager/Connect
- POST /api/v1/manager/Disconnect
- GET /api/v1/manager/IsConnected
- GET /api/v1/manager/SessionInfo

Architectural Note:
While MT5 uses token-based authentication via /Connect, our system uses JWT.
These endpoints provide MT5-compatible session metadata while leveraging
our existing JWT infrastructure. The actual authentication happens via
the JWT middleware before these endpoints are reached.
"""
import logging
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import Optional

from api.auth.admin_dependencies import get_current_manager
from api.schemas.manager.connection import (
    ConnectRequest,
    ConnectResponse,
    ConnectionStatus,
    DisconnectResponse,
    SessionInfo,
)
from core.domains.accounts.account import Account

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/manager", tags=["Manager - Connection"])


# ============================================================================
# Connect - Establish session (MT5-compatible)
# ============================================================================

@router.post(
    "/Connect",
    response_model=ConnectResponse,
    summary="Establish manager session",
)
async def connect(
    request: ConnectRequest,
    manager: Account = Depends(get_current_manager),
    http_request: Request = None,
) -> ConnectResponse:
    """
    Establish a manager session.
    
    Mirrors MT5 Manager API `Connect` endpoint.
    
    Note: Actual authentication is handled by JWT middleware.
    This endpoint returns session metadata in MT5 format.
    """
    # Extract client IP from request
    client_ip = request.client_ip
    if not client_ip and http_request:
        # Try to get real IP from X-Forwarded-For header
        client_ip = http_request.headers.get("X-Forwarded-For", http_request.client.host)
    
    # Build MT5-compatible response
    # In MT5, access_level would be determined by manager permissions
    # For now, we use a simplified model
    access_level = "FULL"  # Could be: FULL, RISK, DEALER, READONLY
    
    # Extract permissions from manager account
    permissions = []
    if hasattr(manager, 'permissions'):
        permissions = manager.permissions if isinstance(manager.permissions, list) else []
    
    return ConnectResponse(
        retcode=0,
        session_id=f"session_{manager.login}_{int(datetime.now(timezone.utc).timestamp())}",
        access_level=access_level,
        user_login=manager.login,
        user_group=manager.group.name if manager.group else None,
        user_name=manager.full_name if hasattr(manager, 'full_name') else None,
        user_email=manager.email if hasattr(manager, 'email') else None,
        permissions=permissions,
        server_time=datetime.now(timezone.utc),
        message="Connected successfully",
    )


# ============================================================================
# Disconnect - Terminate session
# ============================================================================

@router.post(
    "/Disconnect",
    response_model=DisconnectResponse,
    summary="Terminate manager session",
)
async def disconnect(
    manager: Account = Depends(get_current_manager),
) -> DisconnectResponse:
    """
    Terminate the current manager session.
    
    Mirrors MT5 Manager API `Disconnect` endpoint.
    
    Note: In a stateless JWT system, disconnection is handled client-side
    by deleting the token. This endpoint provides MT5-compatible confirmation.
    """
    session_id = f"session_{manager.login}"
    
    logger.info(f"Manager {manager.login} disconnected")
    
    return DisconnectResponse(
        retcode=0,
        message="Disconnected successfully",
        session_id=session_id,
    )


# ============================================================================
# IsConnected - Check connection status
# ============================================================================

@router.get(
    "/IsConnected",
    response_model=ConnectionStatus,
    summary="Check connection status",
)
async def is_connected(
    manager: Account = Depends(get_current_manager),
) -> ConnectionStatus:
    """
    Check if the current session is connected.
    
    Mirrors MT5 Manager API `IsConnected` endpoint.
    
    If this endpoint returns successfully, the connection is active
    (JWT middleware would have rejected invalid tokens).
    """
    return ConnectionStatus(
        connected=True,
        session_id=f"session_{manager.login}",
        user_login=manager.login,
        server_time=datetime.now(timezone.utc),
    )


# ============================================================================
# SessionInfo - Get current session details
# ============================================================================

@router.get(
    "/SessionInfo",
    response_model=SessionInfo,
    summary="Get current session information",
)
async def session_info(
    manager: Account = Depends(get_current_manager),
    http_request: Request = None,
) -> SessionInfo:
    """
    Get detailed information about the current session.
    
    Mirrors MT5 Manager API `SessionInfo` endpoint.
    """
    # Extract client info
    client_ip = None
    client_agent = None
    if http_request:
        client_ip = http_request.headers.get("X-Forwarded-For", http_request.client.host)
        client_agent = http_request.headers.get("User-Agent")
    
    # Calculate session times
    now = datetime.now(timezone.utc)
    connected_at = now  # In stateless JWT, we don't track exact connect time
    last_activity = now
    expires_at = now + timedelta(days=1)
    
    return SessionInfo(
        session_id=f"session_{manager.login}",
        user_login=manager.login,
        user_group=manager.group.name if manager.group else None,
        access_level="FULL",
        client_agent=client_agent,
        client_ip=client_ip,
        connected_at=connected_at,
        last_activity=last_activity,
        expires_at=expires_at,
    )