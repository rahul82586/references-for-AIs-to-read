"""M18 C-tier: the HONEST SKELETONS.

Every route in this file exists so the surface is COMPLETE - the UI can be
written against the whole map, the mtapi/MT5 checklist maps 1:1 - and every
one of them REFUSES with a 501 naming exactly what is missing and which
milestone builds it. The contract, non-negotiable:

* 501, never 200-empty. An empty list that means "not built" is the F8
  disease that hid PositionGet's death for the endpoint's entire life.
* The refusal detail IS the roadmap text (M18-REPORT / ENDPOINTS Tier 3).
* `openapi_extra={"x-not-wired": True}` so Swagger UI and any codegen can
  see the honesty flag without calling.
* Each skeleton is gated by the right its REAL implementation will use, so
  the authorisation surface is already true - a manager without the bit gets
  403 today and 403 after the milestone lands.
* `p1_proof_surface_completion` walks the mounted route table and fails if
  any of these starts answering 200 without its logic existing.

When a milestone builds one of these for real, DELETE the skeleton route in
the same commit - two homes for one path is how the legacy admin_router
reads ended up shadowed.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Any, Dict

from api.auth.admin_dependencies import require_right
import json
import logging

logger = logging.getLogger(__name__)
from decimal import Decimal
from api.di_providers import get_symbol_repo, get_position_repo
from infrastructure.persistence.config_models import SymbolModel
from infrastructure.persistence.config_mappers import db_to_symbol
from application.cache.config_cache import get_config_cache
from api.routers.admin.admin_router import _symbol_summary


def _refuse(what: str, milestone: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"NOT WIRED: {what} - planned in {milestone}. "
               "This endpoint exists so the surface is complete; it refuses "
               "rather than serving an empty success (the F8 rule).",
    )


X_NOT_WIRED = {"x-not-wired": True}


def _skel_get(what: str, milestone: str):
    """A zero-parameter GET skeleton. FastAPI builds the request signature by
    introspection, so a (*args, **kwargs) endpoint becomes a 422 before the
    body ever runs - the refusal must be the ROUTE's answer, not a validation
    accident."""
    async def _route() -> Dict[str, Any]:
        raise _refuse(what, milestone)
    return _route


def _skel_write(what: str, milestone: str):
    async def _route(body: "_AnyBody" = None) -> Dict[str, Any]:
        raise _refuse(what, milestone)
    return _route


# ---------------------------------------------------------------------------
# account lifecycle (C1/C14) - RIGHT_ACC_MANAGER, delete also RIGHT_ACC_DELETE
# ---------------------------------------------------------------------------

accounts_skeleton = APIRouter(
    prefix="/api/v1/admin/accounts",
    tags=["Admin - NOT WIRED"],
    dependencies=[Depends(require_right("RIGHT_ACC_MANAGER"))],
)


class _AnyBody(BaseModel):
    """Skeletons accept and ignore a body so the UI can be written against
    the real shape from day one; nothing is parsed strictly, nothing stored."""
    model_config = {"extra": "allow"}





@accounts_skeleton.post("/{login}/archive", openapi_extra=X_NOT_WIRED)
async def archive_account(login: int) -> Dict[str, Any]:
    raise _refuse("account archiving (MT5 user/archive)", "the account-lifecycle milestone")


@accounts_skeleton.post("/{login}/restore", openapi_extra=X_NOT_WIRED)
async def restore_account(login: int) -> Dict[str, Any]:
    raise _refuse("account restore from archive (MT5 user/restore)", "the account-lifecycle milestone")


# ---------------------------------------------------------------------------
# symbol writes (C2) - RIGHT_CFG_SYMBOLS
# ---------------------------------------------------------------------------

symbols_skeleton = APIRouter(
    prefix="/api/v1/admin/symbols",
    tags=["Admin - Symbols"],
    dependencies=[Depends(require_right("RIGHT_CFG_SYMBOLS"))],
)


def _to_mode_int(val: Any, default: int, mapping: Dict[str, int]) -> int:
    if isinstance(val, int):
        return val
    if isinstance(val, str):
        val_upper = val.upper().replace(" ", "_").replace("-", "_")
        return mapping.get(val_upper, default)
    return default


_CALC_MODES = {
    "FOREX": 0, "FOREX_NO_LEVERAGE": 1, "CFD": 2, "CFD_INDEX": 3, "CFD_LEVERAGE": 4,
    "EXCHANGE_STOCKS": 5, "EXCHANGE_FUTURES": 6, "FORTS_FUTURES": 7, "EXCHANGE_BONDS": 8,
    "EXCHANGE_INDEX": 9, "EXCHANGE_OPTIONS": 10, "EXCHANGE_OPTIONS_MARGIN": 11,
    "EXCHANGE_FUTURES_INDEX": 12, "CFD_FUTURES": 13, "CRYPTO": 14, "CRYPTO_LEVERAGE": 15
}
_TRADE_MODES = {
    "DISABLED": 0, "LONGONLY": 1, "LONG_ONLY": 1, "SHORTONLY": 2, "SHORT_ONLY": 2,
    "CLOSEONLY": 3, "CLOSE_ONLY": 3, "FULL": 4
}
_EXEC_MODES = {
    "REQUEST": 0, "INSTANT": 1, "MARKET": 2, "EXCHANGE": 3
}


@symbols_skeleton.post("", status_code=status.HTTP_201_CREATED)
async def create_symbol(
    body: Dict[str, Any],
    symbol_repo: Any = Depends(get_symbol_repo),
) -> Dict[str, Any]:
    raw_symbol = str(body.get("symbol") or body.get("name") or "").strip()
    if not raw_symbol:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Symbol name is required")

    raw_symbol = raw_symbol.replace("/", "\\")
    if "\\" in raw_symbol:
        clean_name = raw_symbol.split("\\")[-1]
        full_path = raw_symbol
    else:
        clean_name = raw_symbol
        folder = str(body.get("path") or body.get("folder") or "").strip().replace("/", "\\")
        full_path = f"{folder}\\{clean_name}" if folder else clean_name

    # Dummy folder markers preserve their path as name so each folder marker is unique
    sym_name = full_path if clean_name == ".dummy" else clean_name

    existing = await symbol_repo.find_row_by_name(sym_name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Symbol '{sym_name}' already exists",
        )

    settings_dict = {}
    raw_settings = body.get("settings_json")
    if isinstance(raw_settings, str) and raw_settings:
        try:
            settings_dict = json.loads(raw_settings)
        except Exception:
            pass
    elif isinstance(raw_settings, dict):
        settings_dict = raw_settings

    digits = int(body.get("digits", settings_dict.get("digits", 5)))
    contract_size = Decimal(str(body.get("contract_size", settings_dict.get("contract_size", 100000))))
    quote_currency = str(body.get("currency") or settings_dict.get("quote_currency") or settings_dict.get("currency") or "USD")
    base_currency = str(settings_dict.get("base_currency") or (clean_name[:3] if len(clean_name) == 6 else "USD"))
    spread = int(body.get("spread_base", body.get("spread", settings_dict.get("spread", 0))))
    margin_initial = Decimal(str(body.get("margin_initial", settings_dict.get("margin_initial", 1.0))))
    margin_maintenance = Decimal(str(body.get("margin_maintenance", settings_dict.get("margin_maintenance", 1.0))))

    calc_mode_val = settings_dict.get("calc_mode", body.get("calc_mode", 0))
    trade_mode_val = settings_dict.get("trade_mode", body.get("trade_mode", 4))
    exec_mode_val = settings_dict.get("exec_mode", body.get("exec_mode", 2))

    calc_mode = _to_mode_int(calc_mode_val, 0, _CALC_MODES)
    trade_mode = _to_mode_int(trade_mode_val, 4, _TRADE_MODES)
    exec_mode = _to_mode_int(exec_mode_val, 2, _EXEC_MODES)

    fill_flags = 1  # Default FOK
    if "fill_flags" in body or "fill_flags" in settings_dict:
        try:
            fill_flags = int(body.get("fill_flags", settings_dict.get("fill_flags", 1)))
        except Exception:
            pass
    elif "filling_flags" in settings_dict or "filling_flags" in body:
        ff_val = body.get("filling_flags", settings_dict.get("filling_flags"))
        if isinstance(ff_val, list):
            mask = 0
            for item in ff_val:
                s_item = str(item).lower()
                if s_item == 'fok': mask |= 1
                elif s_item == 'ioc': mask |= 2
                elif s_item in ('boc', 'return'): mask |= 4
            fill_flags = mask

    volume_min = Decimal(str(settings_dict.get("volume_min", body.get("volume_min", 0.01))))
    volume_max = Decimal(str(settings_dict.get("volume_max", body.get("volume_max", 100.0))))
    volume_step = Decimal(str(settings_dict.get("volume_step", body.get("volume_step", 0.01))))
    volume_limit = Decimal(str(settings_dict.get("volume_limit", body.get("volume_limit", 0))))
    description = str(settings_dict.get("description", body.get("description", "")))
    is_trade_allowed = bool(settings_dict.get("is_trade_allowed", body.get("is_trade_allowed", True)))

    ts_input = body.get("tick_size", settings_dict.get("tick_size", body.get("point")))
    point = Decimal(str(ts_input)) if ts_input else (Decimal(10) ** -digits)
    tv_input = body.get("tick_value", settings_dict.get("tick_value", 1.0))
    tick_value = Decimal(str(tv_input)) if tv_input else Decimal("1")
    stops_level = int(body.get("stops_level", settings_dict.get("stops_level", body.get("limit_stop_level", settings_dict.get("limit_stop_level", 0)))))
    freeze_level = int(body.get("freeze_level", settings_dict.get("freeze_level", 0)))

    model = SymbolModel(
        name=sym_name,
        path=full_path,
        symbol_id=sym_name,
        description=description,
        base_currency=base_currency,
        quote_currency=quote_currency,
        margin_currency=quote_currency,
        digits=digits,
        point=point,
        mt5_tick_size=point,
        tick_value=tick_value,
        contract_size=contract_size,
        calc_mode=calc_mode,
        trade_mode=trade_mode,
        exec_mode=exec_mode,
        fill_flags=fill_flags,
        spread=spread,
        stops_level=stops_level,
        freeze_level=freeze_level,
        volume_min=volume_min,
        volume_max=volume_max,
        volume_step=volume_step,
        volume_limit=volume_limit,
        margin_initial_buy=margin_initial,
        margin_initial_sell=margin_initial,
        margin_maintenance_buy=margin_maintenance,
        margin_maintenance_sell=margin_maintenance,
        is_trade_allowed=is_trade_allowed,
        mt5_extra=settings_dict,
    )

    await symbol_repo.save_model(model)
    domain_sym = db_to_symbol(model)
    cache = get_config_cache()
    if cache:
        cache.upsert_symbol(domain_sym)

    return _symbol_summary(domain_sym)


@symbols_skeleton.put("/{symbol_name:path}")
async def update_symbol(
    symbol_name: str,
    body: Dict[str, Any],
    symbol_repo: Any = Depends(get_symbol_repo),
) -> Dict[str, Any]:
    norm_name = symbol_name.replace("/", "\\")
    clean_name = norm_name.split("\\")[-1] if "\\" in norm_name else norm_name

    model = await symbol_repo.find_row_by_name(norm_name)
    if not model and clean_name != norm_name:
        model = await symbol_repo.find_row_by_name(clean_name)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Symbol '{symbol_name}' not found",
        )

    settings_dict = {}
    raw_settings = body.get("settings_json")
    if isinstance(raw_settings, str) and raw_settings:
        try:
            settings_dict = json.loads(raw_settings)
        except Exception:
            pass
    elif isinstance(raw_settings, dict):
        settings_dict = raw_settings

    new_symbol = str(body.get("symbol", "")).strip().replace("/", "\\")
    if new_symbol and "\\" in new_symbol:
        model.path = new_symbol
    elif body.get("path"):
        p = str(body["path"]).strip().replace("/", "\\")
        model.path = f"{p}\\{model.name}" if not p.endswith(f"\\{model.name}") else p

    if "digits" in body or "digits" in settings_dict:
        d_val = body.get("digits") if "digits" in body else settings_dict.get("digits")
        digits = int(d_val)
        model.digits = digits
        if not ("tick_size" in body or "tick_size" in settings_dict):
            model.point = Decimal(10) ** -digits
            model.mt5_tick_size = model.point

    if "tick_size" in body or "tick_size" in settings_dict or "point" in body:
        ts = body.get("tick_size", settings_dict.get("tick_size", body.get("point")))
        if ts is not None and float(ts) > 0:
            ts_dec = Decimal(str(ts))
            model.point = ts_dec
            model.mt5_tick_size = ts_dec

    if "tick_value" in body or "tick_value" in settings_dict:
        tv = body.get("tick_value", settings_dict.get("tick_value"))
        if tv is not None:
            model.tick_value = Decimal(str(tv))

    if "contract_size" in body or "contract_size" in settings_dict:
        c_val = body.get("contract_size") if "contract_size" in body else settings_dict.get("contract_size")
        model.contract_size = Decimal(str(c_val))

    if "currency" in body or "currency" in settings_dict or "quote_currency" in settings_dict:
        curr = str(body.get("currency") or settings_dict.get("quote_currency") or settings_dict.get("currency"))
        model.quote_currency = curr
        model.margin_currency = curr

    if "base_currency" in settings_dict:
        model.base_currency = str(settings_dict["base_currency"])

    if "spread_base" in body or "spread" in body or "spread" in settings_dict:
        sp = body.get("spread_base", body.get("spread", settings_dict.get("spread", model.spread)))
        model.spread = int(sp)

    if "stops_level" in body or "stops_level" in settings_dict or "limit_stop_level" in body or "limit_stop_level" in settings_dict:
        sl = body.get("stops_level", settings_dict.get("stops_level", body.get("limit_stop_level", settings_dict.get("limit_stop_level"))))
        if sl is not None:
            model.stops_level = int(sl)

    if "freeze_level" in body or "freeze_level" in settings_dict:
        fl = body.get("freeze_level", settings_dict.get("freeze_level"))
        if fl is not None:
            model.freeze_level = int(fl)

    if "description" in body or "description" in settings_dict:
        model.description = str(body.get("description", settings_dict.get("description", model.description)))

    if "volume_min" in settings_dict or "volume_min" in body or "min_volume" in settings_dict:
        v_min = settings_dict.get("volume_min", body.get("volume_min", settings_dict.get("min_volume")))
        if v_min is not None: model.volume_min = Decimal(str(v_min))

    if "volume_max" in settings_dict or "volume_max" in body or "max_volume" in settings_dict:
        v_max = settings_dict.get("volume_max", body.get("volume_max", settings_dict.get("max_volume")))
        if v_max is not None: model.volume_max = Decimal(str(v_max))

    if "volume_step" in settings_dict or "volume_step" in body or "step_volume" in settings_dict:
        v_step = settings_dict.get("volume_step", body.get("volume_step", settings_dict.get("step_volume")))
        if v_step is not None: model.volume_step = Decimal(str(v_step))

    if "volume_limit" in settings_dict or "volume_limit" in body or "limit_volume" in settings_dict:
        v_lim = settings_dict.get("volume_limit", body.get("volume_limit", settings_dict.get("limit_volume")))
        if v_lim is not None: model.volume_limit = Decimal(str(v_lim))

    if "calc_mode" in settings_dict:
        model.calc_mode = _to_mode_int(settings_dict["calc_mode"], model.calc_mode, _CALC_MODES)

    if "trade_mode" in settings_dict:
        model.trade_mode = _to_mode_int(settings_dict["trade_mode"], model.trade_mode, _TRADE_MODES)

    if "exec_mode" in settings_dict:
        model.exec_mode = _to_mode_int(settings_dict["exec_mode"], model.exec_mode, _EXEC_MODES)

    if "is_trade_allowed" in settings_dict:
        model.is_trade_allowed = bool(settings_dict["is_trade_allowed"])

    # 16-way margin rate matrix
    rate_map = {
        "rate_market_buy_init": "margin_initial_buy",
        "rate_market_buy_maint": "margin_maintenance_buy",
        "rate_market_sell_init": "margin_initial_sell",
        "rate_market_sell_maint": "margin_maintenance_sell",
        "rate_limit_buy_init": "margin_initial_buy_limit",
        "rate_limit_buy_maint": "margin_maintenance_buy_limit",
        "rate_limit_sell_init": "margin_initial_sell_limit",
        "rate_limit_sell_maint": "margin_maintenance_sell_limit",
        "rate_stop_buy_init": "margin_initial_buy_stop",
        "rate_stop_buy_maint": "margin_maintenance_buy_stop",
        "rate_stop_sell_init": "margin_initial_sell_stop",
        "rate_stop_sell_maint": "margin_maintenance_sell_stop",
    }
    for ui_k, db_k in rate_map.items():
        if ui_k in settings_dict or ui_k in body:
            v = settings_dict.get(ui_k, body.get(ui_k))
            if v is not None:
                setattr(model, db_k, Decimal(str(v)))

    mr = body.get("margin_rates") or settings_dict.get("margin_rates")
    if isinstance(mr, dict):
        for k, v in mr.items():
            db_k = f"margin_{k}" if not k.startswith("margin_") else k
            if hasattr(model, db_k) and v is not None:
                setattr(model, db_k, Decimal(str(v)))

    if "fill_flags" in body or "fill_flags" in settings_dict:
        try:
            model.fill_flags = int(body.get("fill_flags", settings_dict.get("fill_flags", model.fill_flags)))
        except Exception:
            pass
    elif "filling_flags" in settings_dict or "filling_flags" in body:
        ff_val = body.get("filling_flags", settings_dict.get("filling_flags"))
        if isinstance(ff_val, list):
            mask = 0
            for item in ff_val:
                s_item = str(item).lower()
                if s_item == 'fok': mask |= 1
                elif s_item == 'ioc': mask |= 2
                elif s_item in ('boc', 'return'): mask |= 4
            model.fill_flags = mask

    extra = dict(model.mt5_extra or {})
    extra.update(settings_dict)
    extra["fill_flags"] = model.fill_flags
    if "margin_hedged" in body or "margin_hedged" in settings_dict:
        extra["margin_hedged"] = str(body.get("margin_hedged", settings_dict.get("margin_hedged", 0)))
    if "calc_hedged_larger_leg" in body or "calc_hedged_larger_leg" in settings_dict:
        extra["calc_hedged_larger_leg"] = bool(body.get("calc_hedged_larger_leg", settings_dict.get("calc_hedged_larger_leg", False)))
    if "margin_initial" in body or "margin_initial" in settings_dict:
        mi = body.get("margin_initial", settings_dict.get("margin_initial"))
        if mi is not None and float(mi) > 0:
            extra["margin_initial"] = str(mi)
        else:
            extra.pop("margin_initial", None)
    if "margin_maintenance" in body or "margin_maintenance" in settings_dict:
        mm = body.get("margin_maintenance", settings_dict.get("margin_maintenance"))
        if mm is not None and float(mm) > 0:
            extra["margin_maintenance"] = str(mm)
        else:
            extra.pop("margin_maintenance", None)
    model.mt5_extra = extra

    await symbol_repo.save_model(model)
    domain_sym = db_to_symbol(model)
    cache = get_config_cache()
    if cache:
        cache.upsert_symbol(domain_sym)

    try:
        from api.di_providers import get_account_repo, get_position_repo
        acc_repo = get_account_repo()
        pos_repo = get_position_repo()
        if pos_repo and acc_repo:
            from api.routers.manager.trading import recalculate_account_trading_state
            open_pos = await pos_repo.get_by_symbol(model.name)
            if not open_pos and clean_name != model.name:
                open_pos = await pos_repo.get_by_symbol(clean_name)
            if open_pos:
                logins = {int(p.account_login) for p in open_pos}
                for l in logins:
                    await recalculate_account_trading_state(l, acc_repo, pos_repo, symbol_repo)
    except Exception as exc:
        logger.warning(f"update_symbol account recalculation notice: {exc}")

    return _symbol_summary(domain_sym)


@symbols_skeleton.delete("/{symbol_name:path}")
async def delete_symbol(
    symbol_name: str,
    symbol_repo: Any = Depends(get_symbol_repo),
    position_repo: Any = Depends(get_position_repo),
) -> Dict[str, Any]:
    norm_name = symbol_name.replace("/", "\\")
    clean_name = norm_name.split("\\")[-1] if "\\" in norm_name else norm_name

    model = await symbol_repo.find_row_by_name(norm_name)
    if not model and clean_name != norm_name:
        model = await symbol_repo.find_row_by_name(clean_name)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Symbol '{symbol_name}' not found",
        )

    # Check for active positions holding this symbol
    if position_repo and clean_name != ".dummy":
        try:
            if hasattr(position_repo, "find_page"):
                _, total = await position_repo.find_page(limit=1, symbol=model.name)
                if total > 0:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Cannot delete symbol '{model.name}': {total} active positions exist in this symbol",
                    )
        except HTTPException:
            raise
        except Exception:
            pass

    deleted = await symbol_repo.delete_symbol(model.name)
    if not deleted:
        deleted = await symbol_repo.delete_symbol(norm_name)

    cache = get_config_cache()
    if cache:
        cache.delete_symbol(model.name)

    return {"status": "success", "message": f"Symbol '{model.name}' deleted successfully"}


# ---------------------------------------------------------------------------
# routing writes (C3) - RIGHT_CFG_REQUESTS
# ---------------------------------------------------------------------------

routing_skeleton = APIRouter(
    prefix="/api/v1/admin/routing",
    tags=["Admin - NOT WIRED"],
    dependencies=[Depends(require_right("RIGHT_CFG_REQUESTS"))],
)


@routing_skeleton.post("", status_code=status.HTTP_201_CREATED, openapi_extra=X_NOT_WIRED)
async def create_routing_rule(body: _AnyBody) -> Dict[str, Any]:
    raise _refuse("routing-rule writes (the M8 engine and loader exist; the "
                  "command layer does not)", "the routing-writes milestone (ENDPOINTS B7)")


@routing_skeleton.put("/{rule_id}", openapi_extra=X_NOT_WIRED)
async def update_routing_rule(rule_id: str, body: _AnyBody) -> Dict[str, Any]:
    raise _refuse("routing-rule update", "the routing-writes milestone")


@routing_skeleton.delete("/{rule_id}", openapi_extra=X_NOT_WIRED)
async def delete_routing_rule(rule_id: str) -> Dict[str, Any]:
    raise _refuse("routing-rule delete", "the routing-writes milestone")


@routing_skeleton.post("/reorder", openapi_extra=X_NOT_WIRED)
async def reorder_routing_rules(body: _AnyBody) -> Dict[str, Any]:
    raise _refuse("routing reorder - list order IS the semantics for a "
                  "top-down first-match engine, so this is the most "
                  "consequential routing write", "the routing-writes milestone")


# ---------------------------------------------------------------------------
# gateway + datafeed config planes (C4/C5) - migration 010
# ---------------------------------------------------------------------------

gateways_skeleton = APIRouter(
    prefix="/api/v1/admin/gateways",
    tags=["Admin - NOT WIRED"],
    dependencies=[Depends(require_right("RIGHT_CFG_GATEWAYS"))],
)

for _method, _path, _name in [
    ("get", "", "list_gateways"),
    ("post", "", "create_gateway"),
    ("put", "/{gateway_id}", "update_gateway"),
    ("delete", "/{gateway_id}", "delete_gateway"),
    ("post", "/{gateway_id}/test", "test_gateway"),
]:
    _what = f"gateway config plane ({_method.upper()} {_path or '/'})"
    _mile = ("migration 010 - the gateway config plane (mt5_gateways table; "
             "TRANSLATE_FIELDS and the markup maths exist since M13, there is "
             "nowhere to put a row)")
    _route = _skel_get(_what, _mile) if _method == "get" else _skel_write(_what, _mile)
    gateways_skeleton.add_api_route(
        _path, _route, methods=[_method.upper()], name=_name, openapi_extra=X_NOT_WIRED,
    )

datafeeds_skeleton = APIRouter(
    prefix="/api/v1/admin/datafeeds",
    tags=["Admin - NOT WIRED"],
    dependencies=[Depends(require_right("RIGHT_CFG_DATAFEEDS"))],
)

for _method, _path, _name in [
    ("get", "", "list_datafeeds"),
    ("post", "", "create_datafeed"),
    ("put", "/{feed_id}", "update_datafeed"),
    ("delete", "/{feed_id}", "delete_datafeed"),
]:
    _what = f"datafeed config plane ({_method.upper()} {_path or '/'})"
    _route = _skel_get(_what, "migration 010 - the datafeed config plane") if _method == "get" \
        else _skel_write(_what, "migration 010 - the datafeed config plane")
    datafeeds_skeleton.add_api_route(
        _path, _route, methods=[_method.upper()], name=_name, openapi_extra=X_NOT_WIRED,
    )

# ---------------------------------------------------------------------------
# allocations (C6) - plan step 9
# ---------------------------------------------------------------------------

allocations_skeleton = APIRouter(
    prefix="/api/v1/admin/allocations",
    tags=["Admin - NOT WIRED"],
    dependencies=[Depends(require_right("RIGHT_ACC_MANAGER"))],
)

for _method, _path, _name in [
    ("get", "", "list_allocations"),
    ("post", "", "create_allocation"),
    ("put", "/{allocation_id}", "update_allocation"),
    ("delete", "/{allocation_id}", "delete_allocation"),
]:
    _what = f"allocations ({_method.upper()} {_path or '/'})"
    _mile = ("IDENTITY-BUILD-PLAN step 9 - self-service account opening "
             "(groups, country filter, leverage lists, the demo-allocation URL rule)")
    _route = _skel_get(_what, _mile) if _method == "get" else _skel_write(_what, _mile)
    allocations_skeleton.add_api_route(
        _path, _route, methods=[_method.upper()], name=_name, openapi_extra=X_NOT_WIRED,
    )

# ---------------------------------------------------------------------------
# supervision & content (C7-C11, C12, C13)
# ---------------------------------------------------------------------------

misc_skeleton = APIRouter(prefix="/api/v1/admin", tags=["Admin - NOT WIRED"])


@misc_skeleton.get("/journal", dependencies=[Depends(require_right("RIGHT_SRV_JOURNALS"))],
                   openapi_extra=X_NOT_WIRED)
async def read_journal() -> Dict[str, Any]:
    raise _refuse("the audit journal - MT5 logs every manager query, export and "
                  "filter; this platform logs nothing queryable yet. The "
                  "compliance prerequisite for real operation",
                  "the audit-journal milestone (Tier 3 #4)")


@misc_skeleton.get("/reports", dependencies=[Depends(require_right("RIGHT_SRV_REPORTS"))],
                   openapi_extra=X_NOT_WIRED)
async def list_reports() -> Dict[str, Any]:
    raise _refuse("the report engine (statements, EOD, the DailyRequest family)",
                  "deferred by explicit decision; skeleton reserved")


@misc_skeleton.get("/charts/bars", dependencies=[Depends(require_right("RIGHT_CHARTS"))],
                   openapi_extra=X_NOT_WIRED)
async def chart_bars() -> Dict[str, Any]:
    raise _refuse("bar aggregation and storage - the bars table has 0 rows on "
                  "30+ fills; nothing aggregates ticks into bars yet",
                  "the history-plane milestone (Tier 3 #5)")


@misc_skeleton.get("/history/ticks", dependencies=[Depends(require_right("RIGHT_CHARTS"))],
                   openapi_extra=X_NOT_WIRED)
async def tick_history() -> Dict[str, Any]:
    raise _refuse("tick history storage (ClickHouse decision pending)",
                  "the history-plane milestone")


@misc_skeleton.post("/mail", dependencies=[Depends(require_right("RIGHT_EMAIL"))],
                    openapi_extra=X_NOT_WIRED)
async def send_mail(body: _AnyBody) -> Dict[str, Any]:
    raise _refuse("internal mail", "deferred by explicit decision")


@misc_skeleton.post("/news", dependencies=[Depends(require_right("RIGHT_NEWS"))],
                    openapi_extra=X_NOT_WIRED)
async def publish_news(body: _AnyBody) -> Dict[str, Any]:
    raise _refuse("news publishing", "deferred by explicit decision")


@misc_skeleton.post("/groups/{group_name}/symbols",
                    dependencies=[Depends(require_right("RIGHT_CFG_GROUPS"))],
                    openapi_extra=X_NOT_WIRED)
async def set_group_symbol_override(group_name: str, body: _AnyBody) -> Dict[str, Any]:
    raise _refuse("per-group symbol overrides - the SpreadDiff/SpreadDiffBalance "
                  "writes where B-Book markup lives (M7 maths, no write path). "
                  "GroupSymbolOverride models 11 of MT5's 64 fields; the write "
                  "must round-trip the rest or the wire guarantee dies",
                  "ENDPOINTS B6 (with the symbol-CRUD milestone)")


@misc_skeleton.delete("/managers/{login}",
                      dependencies=[Depends(require_right("RIGHT_CFG_MANAGERS"))],
                      openapi_extra=X_NOT_WIRED)
async def delete_manager(login: str) -> Dict[str, Any]:
    raise _refuse("manager deletion - MT5 keeps the underlying account; the "
                  "manager row and its mirror password_hash must go without "
                  "touching the account's credential (one writer per secret)",
                  "the manager-lifecycle addition (small; with B1)")


# ---------------------------------------------------------------------------
# dealer intervention (C11) - the manager dialect
# ---------------------------------------------------------------------------

dealer_skeleton = APIRouter(
    prefix="/api/v1/manager",
    tags=["Manager - NOT WIRED"],
    dependencies=[Depends(require_right("RIGHT_TRADES_DEALER"))],
)


@dealer_skeleton.post("/OrderRequote", openapi_extra=X_NOT_WIRED)
async def order_requote(body: _AnyBody) -> Dict[str, Any]:
    raise _refuse("dealer requote - the dealer_queue service exists internally; "
                  "the intervention workflow (request -> dealer -> new price -> "
                  "client accept/reject with the 30s timer) does not",
                  "the B1 dealer milestone")


@dealer_skeleton.post("/OrderConfirm", openapi_extra=X_NOT_WIRED)
async def order_confirm(body: _AnyBody) -> Dict[str, Any]:
    raise _refuse("dealer confirmation (request-policy CONFIRM modes are "
                  "modelled in the M8 routing table; the confirmation flow "
                  "is not)", "the B1 dealer milestone")


ALL_SKELETON_ROUTERS = [
    accounts_skeleton,
    symbols_skeleton,
    routing_skeleton,
    gateways_skeleton,
    datafeeds_skeleton,
    allocations_skeleton,
    misc_skeleton,
    dealer_skeleton,
]
