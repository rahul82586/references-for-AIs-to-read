"""
Admin REST API Router for Eclipse Theia UI & Backoffice Services

Protected via X-Admin-API-Key header authentication.
Exposes endpoints for group management, symbol specs, routing rules, and dealer intervention queue.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends

from api.auth.admin_dependencies import verify_admin_api_key

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin"],
    dependencies=[Depends(verify_admin_api_key)]
)


@router.get("/groups")
async def list_groups() -> List[Dict[str, Any]]:
    """List all account groups and risk profile configurations."""
    return [
        {
            "name": "demo_group",
            "leverage": 100,
            "margin_call_level": "60",
            "stop_out_level": "30",
            "execution_mode": "MARKET"
        },
        {
            "name": "real_group",
            "leverage": 100,
            "margin_call_level": "80",
            "stop_out_level": "50",
            "execution_mode": "MARKET"
        }
    ]


@router.get("/symbols")
async def list_symbols() -> List[Dict[str, Any]]:
    """List all tradable symbol specifications."""
    return [
        {"name": "EURUSD", "contract_size": "100000", "tick_size": "0.00001", "digits": 5},
        {"name": "GBPUSD", "contract_size": "100000", "tick_size": "0.00001", "digits": 5},
        {"name": "USDJPY", "contract_size": "100000", "tick_size": "0.001", "digits": 3},
        {"name": "XAUUSD", "contract_size": "100", "tick_size": "0.01", "digits": 2},
        {"name": "BTCUSD", "contract_size": "1", "tick_size": "0.01", "digits": 2}
    ]


@router.get("/dealer-queue")
async def list_dealer_queue() -> List[Dict[str, Any]]:
    """Query pending manual dealer intervention queue (MT5 dealer workflow)."""
    return []
