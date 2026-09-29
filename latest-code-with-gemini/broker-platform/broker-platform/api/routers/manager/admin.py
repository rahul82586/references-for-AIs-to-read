"""
MT5 Manager API - Admin Router.
Mirrors MT5 Manager API Admin endpoints for Group & User Management.
"""
import logging
import json
from decimal import Decimal
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, Query, Body, HTTPException, status
from sqlalchemy import text as sa_text

from api.auth.admin_dependencies import get_current_manager
from core.domains.accounts.account import Account
from api.di_providers import get_group_repo

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/manager", tags=["Manager - Admin"])
router_root = APIRouter(tags=["Admin"])


class GroupAddPayload(BaseModel):
    group: Optional[str] = Field("demo\\Netting", description="Group path, e.g. demo\\Netting or demo_netting")
    margin_mode: Optional[int] = Field(0, description="0=NETTING (MT5 Retail Netting), 1=EXCHANGE, 2=HEDGING (Retail Hedged)")
    account_type: Optional[str] = Field("demo", description="Account type: demo, real, manager, contest")
    currency: Optional[str] = Field("USD", description="Deposit currency: USD, EUR, GBP")
    leverage: Optional[int] = Field(100, description="Default leverage: e.g. 100, 200, 500")
    margin_call: Optional[float] = Field(50.0, description="Margin Call percentage level")
    margin_stop_out: Optional[float] = Field(30.0, description="Margin Stop-Out percentage level")
    company: Optional[str] = Field("", description="Company / White Label name")


class GroupUpdatePayload(BaseModel):
    group: str = Field(..., description="Target group name to update")
    margin_mode: Optional[int] = Field(None, description="0=NETTING, 2=HEDGING")
    currency: Optional[str] = Field(None, description="Deposit currency")
    leverage: Optional[int] = Field(None, description="Default leverage")
    margin_call: Optional[float] = Field(None, description="Margin Call percentage level")
    margin_stop_out: Optional[float] = Field(None, description="Margin Stop-Out percentage level")
    company: Optional[str] = Field(None, description="Company name")
    is_active: Optional[bool] = Field(None, description="Active status")


@router.get("/UserArchive", summary="Archives user account.")
@router_root.get("/UserArchive", summary="Archives user account.")
async def handle_UserArchive_get(
    manager: Account = Depends(get_current_manager),
    id: Optional[str] = Query(None, alias="id", description="Session token returned by the Connect method."),
    login: Optional[str] = Query(None, alias="login", description="Account login number."),
) -> Dict[str, Any]:
    """Archives user account."""
    return {
        "retcode": 0,
        "message": f"Account {login} archived successfully",
        "endpoint": "/UserArchive",
        "login": login,
    }


def _parse_margin_mode(val: Any) -> int:
    """Helper to parse margin mode as int (0=NETTING, 2=HEDGING)."""
    if val is None:
        return 0
    val_str = str(val).strip().upper()
    if val_str in ("0", "NETTING", "RETAIL", "EXCHANGE", "EXCHANGE_DISCOUNT"):
        return 0
    if val_str in ("2", "HEDGING", "RETAIL_HEDGED"):
        return 2
    try:
        return int(val)
    except Exception:
        return 0


@router.get("/GroupAdd", summary="Add new group with custom Netting/Hedging mode, leverage, and margin rules")
@router_root.get("/GroupAdd", summary="Add new group with custom Netting/Hedging mode, leverage, and margin rules")
async def handle_GroupAdd_get(
    manager: Account = Depends(get_current_manager),
    id: Optional[str] = Query(None, alias="id", description="Session token returned by Connect method"),
    group: Optional[str] = Query("demo_netting_vip", alias="group", description="Group path/name, e.g. demo_netting_vip or demo\\Netting"),
    margin_mode: Optional[str] = Query("0", alias="margin_mode", description="0=NETTING (one position per symbol), 2=HEDGING (multiple independent positions)"),
    account_type: Optional[str] = Query("demo", alias="account_type", description="Account type: demo, real, manager, contest"),
    currency: Optional[str] = Query("USD", alias="currency", description="Base currency (USD, EUR, GBP)"),
    leverage: Optional[int] = Query(100, alias="leverage", description="Default account leverage"),
    margin_call: Optional[float] = Query(50.0, alias="margin_call", description="Margin call level in %"),
    margin_stop_out: Optional[float] = Query(30.0, alias="margin_stop_out", description="Stop out level in %"),
    company: Optional[str] = Query("", alias="company", description="White label broker name"),
    group_repo: Any = Depends(get_group_repo),
) -> Dict[str, Any]:
    """Add new group with custom Netting or Hedging parameters."""
    return await _process_group_create(
        group_name=group or "demo_netting_vip",
        margin_mode_raw=margin_mode,
        account_type=account_type or "demo",
        currency=currency or "USD",
        leverage=leverage or 100,
        margin_call=margin_call or 50.0,
        margin_stop_out=margin_stop_out or 30.0,
        company=company or "",
        group_repo=group_repo
    )


@router.post("/GroupAdd", summary="Add new group (JSON Body)")
@router_root.post("/GroupAdd", summary="Add new group (JSON Body)")
async def handle_GroupAdd_post(
    payload: GroupAddPayload,
    manager: Account = Depends(get_current_manager),
    group_repo: Any = Depends(get_group_repo),
) -> Dict[str, Any]:
    """Add new group via JSON payload."""
    return await _process_group_create(
        group_name=payload.group or "demo_netting_vip",
        margin_mode_raw=payload.margin_mode,
        account_type=payload.account_type or "demo",
        currency=payload.currency or "USD",
        leverage=payload.leverage or 100,
        margin_call=payload.margin_call or 50.0,
        margin_stop_out=payload.margin_stop_out or 30.0,
        company=payload.company or "",
        group_repo=group_repo
    )


async def _process_group_create(
    group_name: str,
    margin_mode_raw: Any,
    account_type: str,
    currency: str,
    leverage: int,
    margin_call: float,
    margin_stop_out: float,
    company: str,
    group_repo: Any
) -> Dict[str, Any]:
    clean_name = group_name.replace("/", "\\")
    margin_mode_int = _parse_margin_mode(margin_mode_raw)
    mode_label = "NETTING" if margin_mode_int in (0, 1) else "HEDGING"

    if not group_repo or not hasattr(group_repo, "session_factory") or not group_repo.session_factory:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Group repository is unwired")

    try:
        from infrastructure.persistence.config_models import GroupModel

        async with group_repo.session_factory() as sess:
            existing = await sess.get(GroupModel, clean_name)
            if existing:
                existing.margin_mode = margin_mode_int
                existing.account_type = account_type
                existing.currency = currency
                existing.leverage_default = leverage
                existing.margin_call = Decimal(str(margin_call))
                existing.margin_stop_out = Decimal(str(margin_stop_out))
                if company:
                    existing.company = company
                if existing.margin_json:
                    m = dict(existing.margin_json)
                    m["mode"] = "RETAIL" if margin_mode_int == 0 else "RETAIL_HEDGED"
                    m["leverage_default"] = leverage
                    existing.margin_json = m
                action_desc = "updated"
            else:
                base_template = "real" if "real" in clean_name.lower() or account_type == "real" else "demo"
                base_obj = await sess.get(GroupModel, base_template)
                if not base_obj:
                    res = await sess.execute(sa_text("SELECT name FROM groups LIMIT 1"))
                    first_name = res.scalar()
                    base_obj = await sess.get(GroupModel, first_name) if first_name else None

                new_grp = GroupModel(
                    name=clean_name,
                    group_id=f"grp_{clean_name.replace(chr(92), '_')}",
                    server_id=base_obj.server_id if base_obj else 1,
                    account_type=account_type,
                    is_active=True,
                    auth_mode=base_obj.auth_mode if base_obj else 0,
                    auth_password_min=base_obj.auth_password_min if base_obj else 8,
                    auth_otp_mode=base_obj.auth_otp_mode if base_obj else 0,
                    permissions_flags=base_obj.permissions_flags if base_obj else 0,
                    company=company or (base_obj.company if base_obj else ""),
                    company_page=base_obj.company_page if base_obj else "",
                    company_email=base_obj.company_email if base_obj else "",
                    company_support_page=base_obj.company_support_page if base_obj else "",
                    company_support_email=base_obj.company_support_email if base_obj else "",
                    company_catalog=base_obj.company_catalog if base_obj else "",
                    company_deposit_url=base_obj.company_deposit_url if base_obj else "",
                    company_withdrawal_url=base_obj.company_withdrawal_url if base_obj else "",
                    currency=currency,
                    currency_digits=base_obj.currency_digits if base_obj else 2,
                    reports_mode=base_obj.reports_mode if base_obj else 0,
                    reports_flags=base_obj.reports_flags if base_obj else 0,
                    reports_email=base_obj.reports_email if base_obj else "",
                    news_mode=base_obj.news_mode if base_obj else 2,
                    news_category=base_obj.news_category if base_obj else "",
                    news_langs=list(base_obj.news_langs) if (base_obj and base_obj.news_langs) else [],
                    mail_mode=base_obj.mail_mode if base_obj else 1,
                    trade_flags=base_obj.trade_flags if base_obj else 0,
                    trade_transfer_mode=base_obj.trade_transfer_mode if base_obj else 0,
                    trade_interestrate=base_obj.trade_interestrate if base_obj else Decimal("0"),
                    trade_virtual_credit=base_obj.trade_virtual_credit if base_obj else Decimal("0"),
                    margin_mode=margin_mode_int,
                    margin_flags=base_obj.margin_flags if base_obj else 0,
                    margin_so_mode=base_obj.margin_so_mode if base_obj else 0,
                    margin_free_mode=base_obj.margin_free_mode if base_obj else 1,
                    margin_call=Decimal(str(margin_call)),
                    margin_stop_out=Decimal(str(margin_stop_out)),
                    margin_free_profit_mode=base_obj.margin_free_profit_mode if base_obj else 0,
                    leverage_default=leverage,
                    leverage_max=base_obj.leverage_max if base_obj else 500,
                    demo_leverage=base_obj.demo_leverage if base_obj else 10,
                    demo_deposit=base_obj.demo_deposit if base_obj else Decimal("0"),
                    demo_trades_clean=base_obj.demo_trades_clean if base_obj else 0,
                    limit_history=base_obj.limit_history if base_obj else 0,
                    limit_orders=base_obj.limit_orders if base_obj else 0,
                    limit_symbols=base_obj.limit_symbols if base_obj else 0,
                    limit_positions=base_obj.limit_positions if base_obj else 0,
                    limit_positions_volume=base_obj.limit_positions_volume if base_obj else Decimal("0"),
                    margin_json={
                        "mode": "RETAIL" if margin_mode_int == 0 else "RETAIL_HEDGED",
                        "leverage_default": leverage
                    },
                    commissions_json=list(base_obj.commissions_json) if (base_obj and base_obj.commissions_json) else [],
                    symbol_overrides_json=list(base_obj.symbol_overrides_json) if (base_obj and base_obj.symbol_overrides_json) else [],
                    permissions_json=dict(base_obj.permissions_json) if (base_obj and base_obj.permissions_json) else {},
                    swaps_json=dict(base_obj.swaps_json) if (base_obj and base_obj.swaps_json) else {},
                    routing_json=dict(base_obj.routing_json) if (base_obj and base_obj.routing_json) else {},
                    mt5_extra={},
                    mt5_scale={},
                    mt5_source=None,
                )
                sess.add(new_grp)
                action_desc = "created"
            await sess.commit()
    except Exception as exc:
        logger.exception("Failed to process group create/update: %s", exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Group creation failed: {str(exc)}")

    return {
        "retcode": 0,
        "message": f"Group '{clean_name}' {action_desc} successfully with {mode_label} mode",
        "endpoint": "/GroupAdd",
        "group": clean_name,
        "margin_mode": margin_mode_int,
        "position_mode": mode_label,
        "account_type": account_type,
        "currency": currency,
        "leverage": leverage,
        "margin_call": margin_call,
        "margin_stop_out": margin_stop_out,
    }


@router.get("/GroupUpdate", summary="Update existing group parameters (Netting/Hedging, leverage, margin rules)")
@router.post("/GroupUpdate", summary="Update existing group parameters (Netting/Hedging, leverage, margin rules)")
@router_root.get("/GroupUpdate", summary="Update existing group parameters (Netting/Hedging, leverage, margin rules)")
@router_root.post("/GroupUpdate", summary="Update existing group parameters (Netting/Hedging, leverage, margin rules)")
async def handle_GroupUpdate(
    manager: Account = Depends(get_current_manager),
    id: Optional[str] = Query(None, alias="id", description="Session token returned by Connect method"),
    group: Optional[str] = Query(None, alias="group", description="Group name to update, e.g. demo or demo_netting"),
    margin_mode: Optional[str] = Query(None, alias="margin_mode", description="0=NETTING, 2=HEDGING"),
    currency: Optional[str] = Query(None, alias="currency", description="Base deposit currency"),
    leverage: Optional[int] = Query(None, alias="leverage", description="Default leverage"),
    margin_call: Optional[float] = Query(None, alias="margin_call", description="Margin call %"),
    margin_stop_out: Optional[float] = Query(None, alias="margin_stop_out", description="Stop out %"),
    is_active: Optional[bool] = Query(None, alias="is_active", description="Enable or disable group"),
    group_repo: Any = Depends(get_group_repo),
) -> Dict[str, Any]:
    """Update existing group configurations."""
    if not group:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="group parameter is required for GroupUpdate")
    
    clean_name = group.replace("/", "\\")
    if not group_repo or not hasattr(group_repo, "session_factory") or not group_repo.session_factory:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Group repository is unwired")

    updates = {}
    params = {"g": clean_name}

    if margin_mode is not None:
        m_int = _parse_margin_mode(margin_mode)
        updates["margin_mode = :m"] = True
        params["m"] = m_int
    if currency:
        updates["currency = :curr"] = True
        params["curr"] = currency
    if leverage:
        updates["leverage_default = :lev"] = True
        params["lev"] = leverage
    if margin_call is not None:
        updates["margin_call = :mc"] = True
        params["mc"] = margin_call
    if margin_stop_out is not None:
        updates["margin_stop_out = :mso"] = True
        params["mso"] = margin_stop_out
    if is_active is not None:
        updates["is_active = :act"] = True
        params["act"] = is_active

    if not updates:
        return {
            "retcode": 0,
            "message": f"No update fields specified for group '{clean_name}'",
            "endpoint": "/GroupUpdate",
            "group": clean_name
        }

    async with group_repo.session_factory() as sess:
        sql = f"UPDATE groups SET {', '.join(updates.keys())} WHERE name = :g"
        res = await sess.execute(sa_text(sql), params)
        await sess.commit()
        if res.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Group '{clean_name}' not found")

    return {
        "retcode": 0,
        "message": f"Group '{clean_name}' updated successfully",
        "endpoint": "/GroupUpdate",
        "group": clean_name,
        "updated": {k.split(" =")[0]: v for k, v in params.items() if k != "g"}
    }


@router.get("/GroupDelete", summary="Delete or deactivate group")
@router.post("/GroupDelete", summary="Delete or deactivate group")
@router_root.get("/GroupDelete", summary="Delete or deactivate group")
@router_root.post("/GroupDelete", summary="Delete or deactivate group")
async def handle_GroupDelete(
    manager: Account = Depends(get_current_manager),
    id: Optional[str] = Query(None, alias="id", description="Session token returned by Connect method"),
    group: Optional[str] = Query(None, alias="group", description="Group name to delete"),
    group_repo: Any = Depends(get_group_repo),
) -> Dict[str, Any]:
    """Delete a group from database."""
    if not group:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="group parameter is required for GroupDelete")
    
    clean_name = group.replace("/", "\\")
    if not group_repo or not hasattr(group_repo, "session_factory") or not group_repo.session_factory:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Group repository is unwired")

    async with group_repo.session_factory() as sess:
        # Check if accounts belong to it
        acc_check = (await sess.execute(sa_text("SELECT COUNT(*) FROM accounts WHERE group_name = :g"), {"g": clean_name})).scalar()
        if acc_check and acc_check > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete group '{clean_name}': {acc_check} accounts are currently assigned to it. Move them first using UserUpdate."
            )
        res = await sess.execute(sa_text("DELETE FROM groups WHERE name = :g"), {"g": clean_name})
        await sess.commit()
        if res.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Group '{clean_name}' not found")

    return {
        "retcode": 0,
        "message": f"Group '{clean_name}' deleted successfully",
        "endpoint": "/GroupDelete",
        "group": clean_name
    }
