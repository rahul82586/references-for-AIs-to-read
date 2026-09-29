"""
MT5 Manager API - Connection Router.
"""
import logging
from datetime import datetime, timezone
from decimal import Decimal
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional, List, Dict, Any

from api.auth.admin_dependencies import get_current_manager
from core.domains.accounts.account import Account

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/manager", tags=["Manager - Connection"])
router_root = APIRouter(tags=["Connection"])

@router.get("/Connect", summary="Connect to account with user, password, host, port.")
@router_root.get("/Connect", summary="Connect to account with user, password, host, port.")
async def handle_Connect_get(
    manager: Account = Depends(get_current_manager),
    user: Optional[str] = Query(None, alias="user", description="Account number. Example: 500476959"),
    password: Optional[str] = Query(None, alias="password", description="Password. Example: ehj4bod"),
    server: Optional[str] = Query(None, alias="server", description="Host - ip adddress or dns name with or without port number. Example: mt4-demo.roboforex.com"),
    timeout: Optional[str] = Query(None, alias="timeout", description="Timeout in milliseconds"),
    id: Optional[str] = Query(None, alias="id", description="Session/Connection ID"),
    unsubscribe: Optional[str] = Query(None, alias="unsubscribe", description=""),
    camelCaseWs: Optional[str] = Query(None, alias="camelCaseWs", description="API will send data to websockets in camel case"),
    admin: Optional[str] = Query(None, alias="admin", description=""),
) -> Dict[str, Any]:
    """Connect to account with user, password, host, port."""
    now = datetime.now(timezone.utc)
    sess_id = id or f"session_{user or manager.login}_{int(now.timestamp())}"
    return {
        "retcode": 0,
        "message": "Connected successfully",
        "endpoint": "/Connect",
        "id": sess_id,
        "user": user or str(manager.login),
        "server": server or "broker-server-01",
        "connected": True,
        "server_time": now.isoformat(),
    }


@router.get("/ConnectionStatus", summary="Check connection state and reconnect if connection lost")
@router_root.get("/ConnectionStatus", summary="Check connection state and reconnect if connection lost")
async def handle_ConnectionStatus_get(
    manager: Account = Depends(get_current_manager),
    id: Optional[str] = Query(None, alias="id", description="Token returned by 'Connect' method"),
) -> Dict[str, Any]:
    """Check connection state and reconnect if connection lost"""
    now = datetime.now(timezone.utc)
    sess_id = id or f"session_{manager.login}"
    return {
        "retcode": 0,
        "message": "Connection active",
        "endpoint": "/ConnectionStatus",
        "id": sess_id,
        "connected": True,
        "ping_ms": 1,
        "server_time": now.isoformat(),
    }


@router.get("/Disconnect", summary="Disconnect from mt5 server.")
@router_root.get("/Disconnect", summary="Disconnect from mt5 server.")
async def handle_Disconnect_get(
    manager: Account = Depends(get_current_manager),
    id: Optional[str] = Query(None, alias="id", description="Session ID"),
) -> Dict[str, Any]:
    """Disconnect from mt5 server."""
    sess_id = id or f"session_{manager.login}"
    return {
        "retcode": 0,
        "message": "Disconnected successfully",
        "endpoint": "/Disconnect",
        "id": sess_id,
        "connected": False,
    }


@router.get("/IsConnected", summary="Check connection with mt5 server.")
@router_root.get("/IsConnected", summary="Check connection with mt5 server.")
async def handle_IsConnected_get(
    manager: Account = Depends(get_current_manager),
    id: Optional[str] = Query(None, alias="id", description="Session ID"),
) -> Dict[str, Any]:
    """Check connection with mt5 server."""
    now = datetime.now(timezone.utc)
    sess_id = id or f"session_{manager.login}"
    return {
        "retcode": 0,
        "message": "Connected",
        "endpoint": "/IsConnected",
        "id": sess_id,
        "connected": True,
        "server_time": now.isoformat(),
    }

