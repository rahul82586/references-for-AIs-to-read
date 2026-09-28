"""
MT5 Manager API - Service Router.
"""
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional, Dict, Any

from api.auth.admin_dependencies import get_current_manager
from core.domains.accounts.account import Account

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/manager", tags=["Manager - Service"])
router_root = APIRouter(tags=["Service"])


@router.get("/ServerTime", summary="Server time (MT5 Sunday=0 convention)")
@router_root.get("/ServerTime", summary="Server time (MT5 Sunday=0 convention)")
async def server_time(
    manager: Account = Depends(get_current_manager),
) -> dict:
    """Get server time matching MT5 convention where Sunday is day 0."""
    now = datetime.now(timezone.utc)
    dow = (now.weekday() + 1) % 7
    return {
        "retcode": 0,
        "timestamp": int(now.timestamp()),
        "iso": now.isoformat(),
        "timezone": "UTC",
        "day_of_week": dow,
    }

@router.get("/Health", summary="Health check")
@router_root.get("/Health", summary="Health check")
async def health_check(
    manager: Account = Depends(get_current_manager),
) -> dict:
    return {"retcode": 0, "status": "healthy", "service": "manager-api"}

@router.get("/ReadMe", summary="Readme info")
@router_root.get("/ReadMe", summary="Readme info")
async def readme(
    manager: Account = Depends(get_current_manager),
) -> dict:
    return {"retcode": 0, "content": "<h1>Broker Platform MT5 Manager API</h1>"}

@router.get("/MemoryUsage", summary="Memory usage details")
@router_root.get("/MemoryUsage", summary="Memory usage details")
async def handle_MemoryUsage_get(
    manager: Account = Depends(get_current_manager),
) -> Dict[str, Any]:
    """Memory usage details"""
    return {
        "retcode": 0,
        "message": "Success",
        "endpoint": "/MemoryUsage",
        "data": []
    }


@router.get("/Ping", summary="Simple test without parameters")
@router_root.get("/Ping", summary="Simple test without parameters")
async def handle_Ping_get(
    manager: Account = Depends(get_current_manager),
) -> Dict[str, Any]:
    """Simple test without parameters"""
    return {
        "retcode": 0,
        "message": "Success",
        "endpoint": "/Ping",
        "data": []
    }


@router.get("/StartTimeUtc", summary="StartTimeUtc")
@router_root.get("/StartTimeUtc", summary="StartTimeUtc")
async def handle_StartTimeUtc_get(
    manager: Account = Depends(get_current_manager),
) -> Dict[str, Any]:
    """StartTimeUtc"""
    return {
        "retcode": 0,
        "message": "Success",
        "endpoint": "/StartTimeUtc",
        "data": []
    }

