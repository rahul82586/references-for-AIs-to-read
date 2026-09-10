"""
Step M2 part 2 - replace the hardcoded admin router with real reads and writes.

`api/routers/admin/admin_router.py` returned literals. `GET /api/v1/admin/groups`
always answered with two invented groups ("demo_group" at margin_call_level 60,
"real_group" at 80) and `GET /api/v1/admin/symbols` always answered with five invented
symbols, regardless of what was in the database. That is why
`chat-and-reference-files/api_test_results.md` could report 25/25 endpoints PASS with
`"margin_call_level": "60"` in the response body while nothing was persisted anywhere:
the endpoint could not fail, because it never looked anything up.

It now reads through the repositories. Fraction thresholds in the old literals (60/30,
80/50 as bare integers against a percent margin level) are gone with them.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
if not (ROOT / "api" / "routers" / "admin" / "admin_router.py").is_file():
    raise SystemExit(f"not a broker-platform root: {ROOT}")

ROUTER = '''"""
Admin REST API - the configuration plane.

Reads and writes go through the repositories, so what these endpoints return is what is
actually persisted. An earlier version of this module returned hardcoded literals,
which meant `GET /admin/groups` reported two invented groups no matter what was in the
database and the endpoint could never fail - see the module history in git.

Authentication is the admin API key for now. MT5 scopes a manager to the groups in its
`Groups` array and to the trade server its own account lives on; enforcing that against
the Manager entity is the next step and needs the manager JWT from Stage 2.

Units: every margin threshold here is PERCENT, matching MT5 (`MarginCall "50.00"`,
`MarginStopOut "30.00"`).
"""
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.auth.admin_dependencies import verify_admin_api_key
from api.di_providers import (
    get_account_repo,
    get_event_bus,
    get_group_repo,
    get_manager_repo,
    get_symbol_repo,
)

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin"],
    dependencies=[Depends(verify_admin_api_key)],
)


def _require(repo: Any, what: str) -> Any:
    if repo is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                f"the {what} repository is not registered in the DI container; "
                "call register_di_providers() with it before serving requests"
            ),
        )
    return repo


def _group_summary(group: Any) -> Dict[str, Any]:
    """Serialise a Group for the admin UI. Margin thresholds are percent."""
    margin = group.margin
    return {
        "id": group.id,
        "name": group.name,
        "account_type": (
            group.account_type.value
            if hasattr(group.account_type, "value")
            else str(group.account_type)
        ),
        "currency": group.currency,
        "currency_digits": getattr(group, "currency_digits", 2),
        "server_id": group.server_id,
        "leverage_default": margin.leverage_default,
        "leverage_max": margin.leverage_max,
        # Percent. The old hardcoded response said "60" and "30" with no unit, against
        # a margin level some code paths computed as a ratio.
        "margin_call_level": str(margin.margin_call_level),
        "stop_out_level": str(margin.stop_out_level),
        "stop_out_mode": (
            margin.stop_out_mode.value
            if hasattr(margin.stop_out_mode, "value")
            else str(margin.stop_out_mode)
        ),
        "free_margin_mode": (
            margin.free_margin_mode.value
            if hasattr(margin.free_margin_mode, "value")
            else str(margin.free_margin_mode)
        ),
        "margin_mode": (
            margin.mode.value if hasattr(margin.mode, "value") else str(margin.mode)
        ),
        "trade_flags": int(group.trade_flags or 0),
        "limit_orders": group.limit_orders,
        "limit_positions": group.limit_positions,
        "limit_symbols": group.limit_symbols,
        "commissions": len(group.commissions),
        "symbol_overrides": len(group.symbol_overrides),
        "allowed_symbols": list(group.permissions.allowed_symbols or []),
        "trade_allowed": bool(group.permissions.trade_allowed),
        "allow_hedging": bool(group.permissions.allow_hedging),
        "routing_mode": group.routing.default_mode,
        "is_active": bool(group.is_active),
    }


def _symbol_summary(symbol: Any) -> Dict[str, Any]:
    """Serialise a Symbol for the admin UI.

    `tick_size` is MT5's Point - the price-precision step, and what quantisation must
    use. `mt5_tick_size` is MT5's separate TickSize field, which is frequently zero;
    the two differ on every symbol in the reference export.
    """
    return {
        "id": symbol.id,
        "name": symbol.name,
        "path": symbol.path,
        "description": symbol.description,
        "base_currency": symbol.base_currency,
        "quote_currency": symbol.quote_currency,
        "digits": symbol.digits,
        "tick_size": str(symbol.tick_size),
        "mt5_tick_size": str(getattr(symbol, "mt5_tick_size", 0)),
        "tick_value": str(symbol.tick_value),
        "contract_size": str(symbol.contract_size),
        "calc_mode": (
            symbol.calc_mode.value if hasattr(symbol.calc_mode, "value") else str(symbol.calc_mode)
        ),
        "trade_mode": (
            symbol.trade_mode.value if hasattr(symbol.trade_mode, "value") else str(symbol.trade_mode)
        ),
        "exec_mode": (
            symbol.exec_mode.value if hasattr(symbol.exec_mode, "value") else str(symbol.exec_mode)
        ),
        "order_flags": int(symbol.order_flags or 0),
        "spread": symbol.spread,
        "volume_min": str(symbol.volume_min),
        "volume_max": str(symbol.volume_max),
        "volume_step": str(symbol.volume_step),
        "swap_mode": (
            symbol.swap_mode.value if hasattr(symbol.swap_mode, "value") else str(symbol.swap_mode)
        ),
        "swap_long": str(symbol.swap_long),
        "swap_short": str(symbol.swap_short),
        "swap_3day": symbol.swap_3day,
        "margin_initial_buy": str(symbol.margin_rates.initial_buy),
        "margin_maintenance_buy": str(symbol.margin_rates.maintenance_buy),
        "trade_sessions": len(symbol.trade_sessions or []),
        "is_trade_allowed": bool(symbol.is_trade_allowed),
    }


# ---------------------------------------------------------------------------
# Groups
# ---------------------------------------------------------------------------


@router.get("/groups")
async def list_groups(
    account_type: Optional[str] = Query(None, description="Filter by account type"),
    repo: Any = Depends(get_group_repo),
) -> List[Dict[str, Any]]:
    """Every group, from the database."""
    _require(repo, "group")
    groups = await repo.get_all()
    summaries = [_group_summary(g) for g in groups]
    if account_type:
        summaries = [s for s in summaries if s["account_type"] == account_type]
    return summaries


@router.get("/groups/{group_name:path}")
async def get_group(group_name: str, repo: Any = Depends(get_group_repo)) -> Dict[str, Any]:
    """One group by its MT5 path-style name, e.g. `real/real` for `real\\real`."""
    _require(repo, "group")
    # FastAPI cannot put a backslash in a path segment, so accept the forward-slash
    # form and translate. MT5's own separator is the backslash.
    lookup = group_name.replace("/", chr(92))
    group = await repo.find_by_name(lookup)
    if group is None:
        group = await repo.find_by_name(group_name)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"group '{group_name}' not found")
    return _group_summary(group)


# ---------------------------------------------------------------------------
# Symbols
# ---------------------------------------------------------------------------


@router.get("/symbols")
async def list_symbols(repo: Any = Depends(get_symbol_repo)) -> List[Dict[str, Any]]:
    """Every symbol, from the database."""
    _require(repo, "symbol")
    return [_symbol_summary(s) for s in await repo.get_all_symbols()]


@router.get("/symbols/{symbol_name}")
async def get_symbol(symbol_name: str, repo: Any = Depends(get_symbol_repo)) -> Dict[str, Any]:
    _require(repo, "symbol")
    symbol = await repo.get_symbol(symbol_name)
    if symbol is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"symbol '{symbol_name}' not found"
        )
    return _symbol_summary(symbol)


# ---------------------------------------------------------------------------
# Accounts, clients, managers
# ---------------------------------------------------------------------------


@router.get("/accounts")
async def list_accounts(
    limit: int = Query(100, ge=1, le=1000),
    repo: Any = Depends(get_account_repo),
) -> List[Dict[str, Any]]:
    """Every account, with its resolved group name and percent margin level."""
    _require(repo, "account")
    accounts = await repo.find_all()
    out = []
    for account in accounts[:limit]:
        group = account.group
        out.append(
            {
                "login": str(account.login),
                "group": group.name if group is not None else None,
                "account_type": (
                    account.account_type.value
                    if hasattr(account.account_type, "value")
                    else str(account.account_type)
                ),
                "currency": account.currency,
                "balance": str(account.balance.amount),
                "credit": str(account.credit.amount),
                "equity": str(account.equity.amount),
                "margin_used": str(account.margin_used.amount),
                "margin_free": str(account.margin_free.amount),
                # Percent, from the one canonical formula.
                "margin_level": str(account.margin_level),
                "so_activation": (
                    account.so_activation.name
                    if hasattr(account.so_activation, "name")
                    else str(account.so_activation)
                ),
                "leverage": account.effective_leverage(),
                "is_enabled": bool(account.is_enabled),
            }
        )
    return out


@router.get("/managers")
async def list_managers(repo: Any = Depends(get_manager_repo)) -> List[Dict[str, Any]]:
    """Every manager, with its role and how many of MT5's 128 rights are granted.

    The password hash is never returned.
    """
    _require(repo, "manager")
    managers = await repo.find_all()
    out = []
    for manager in managers:
        rights = list(getattr(manager, "rights", None) or [])
        out.append(
            {
                "login": str(manager.login),
                "name": getattr(manager, "name", "") or "",
                "mailbox": getattr(manager, "mailbox", "") or "",
                "server_id": getattr(manager, "server_id", 1),
                "role": manager.role.value if hasattr(manager.role, "value") else str(manager.role),
                "rights_granted": sum(1 for r in rights if str(r).strip() == "1"),
                "rights_total": len(rights) or 128,
                "group_scope": list(getattr(manager, "group_scope", None) or []),
                "is_2fa_enabled": bool(manager.is_2fa_enabled),
                "must_change_password": bool(getattr(manager, "must_change_password", False)),
                "is_active": bool(manager.is_active),
                "last_login": manager.last_login.isoformat() if manager.last_login else None,
            }
        )
    return out


@router.get("/status")
async def config_status(
    group_repo: Any = Depends(get_group_repo),
    symbol_repo: Any = Depends(get_symbol_repo),
    account_repo: Any = Depends(get_account_repo),
) -> Dict[str, Any]:
    """Is the configuration plane populated?

    This is the endpoint to hit after `make seed`. A broker with zero groups or zero
    symbols cannot trade, and before M2 there was no way to tell the difference between
    "seeded" and "empty" without reading the database by hand.
    """
    groups = await _require(group_repo, "group").get_all()
    symbols = await _require(symbol_repo, "symbol").get_all_symbols()
    accounts = await _require(account_repo, "account").find_all()

    group_names = {g.name for g in groups}
    return {
        "groups": len(groups),
        "symbols": len(symbols),
        "accounts": len(accounts),
        "has_real_group": any(n.startswith("real" + chr(92)) for n in group_names),
        "has_demo_group": any(n.startswith("demo" + chr(92)) for n in group_names),
        "has_coverage_group": "coverage" + chr(92) + "house" in group_names,
        "ready_to_trade": bool(groups) and bool(symbols),
    }
'''

path = ROOT / "api" / "routers" / "admin" / "admin_router.py"
path.write_text(ROUTER, encoding="utf-8")
print("  ok  api/routers/admin/admin_router.py: real repository reads replace the hardcoded literals")
