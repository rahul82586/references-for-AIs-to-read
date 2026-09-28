#!/usr/bin/env python3
"""M18 B-tier patch part 2: the routing / quotes / risk / calculator / funds /
holiday / symbol-session routers, appended to reads.py, plus main.py mounts.

Idempotent; run from the bp root.
"""
import os
import sys

p = "api/routers/admin/reads.py"
s = open(p, encoding="utf-8").read()
if "routing_reads_router" in s:
    print("reads.py already extended"); sys.exit(0)

# extend the di_providers import in reads.py first
OLD_IMP = '''from api.di_providers import (
    get_account_repo,
    get_client_repo,
    get_deal_repo,
    get_group_repo,
    get_manager_repo,
    get_order_repo,
    get_position_repo,
)'''
NEW_IMP = '''from api.di_providers import (
    get_account_repo,
    get_break_repo,
    get_client_repo,
    get_coverage_repo,
    get_deal_repo,
    get_group_repo,
    get_holiday_repo,
    get_ledger_repo,
    get_manager_repo,
    get_mt5_routing_repo,
    get_order_repo,
    get_position_repo,
    get_symbol_repo,
    get_market_data_engine,
    get_risk_engine,
    get_routing_rule_repo,
    get_event_bus,
)'''
assert OLD_IMP in s, "reads.py import block"
s = s.replace(OLD_IMP, NEW_IMP, 1)

APPEND = '''

# ===========================================================================
# M18 B-tier: routing, quotes, risk, calculators, funds, holidays, sessions.
# Every route here WIRES EXISTING LOGIC - no new domain behaviour. The gates
# are the MT5 rights that own each section (RIGHT_CFG_REQUESTS for routing,
# RIGHT_QUOTES for ticks, RIGHT_RISK_MANAGER for risk reads and calculators,
# RIGHT_ACCOUNTANT for funds, RIGHT_CFG_HOLIDAYS, RIGHT_CFG_SYMBOLS).
# ===========================================================================

import dataclasses as _dataclasses
from datetime import timezone as _tz


def _jsonable(obj: Any) -> Any:
    """JSON-safe view of a domain dataclass tree: Decimals and datetimes as
    strings (the admin-plane convention), enums as their value, tuples as
    lists. One helper so the routing/serializers cannot each invent a shape."""
    if _dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: _jsonable(getattr(obj, f.name)) for f in _dataclasses.fields(obj)}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(x) for x in obj]
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    if hasattr(obj, "value") and not isinstance(obj, (str, int, float, bool)):
        return _jsonable(obj.value)
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    return str(obj)


routing_reads_router = APIRouter(
    prefix="/api/v1/admin/routing",
    tags=["Admin - Routing reads"],
    dependencies=[Depends(require_right("RIGHT_CFG_REQUESTS"))],
)

quotes_reads_router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin - Quote reads"],
    dependencies=[Depends(require_right("RIGHT_QUOTES"))],
)

risk_reads_router = APIRouter(
    prefix="/api/v1/admin/risk",
    tags=["Admin - Risk reads"],
    dependencies=[Depends(require_right("RIGHT_RISK_MANAGER"))],
)

calc_router = APIRouter(
    prefix="/api/v1/admin/trade",
    tags=["Admin - Trade calculators"],
    dependencies=[Depends(require_right("RIGHT_RISK_MANAGER"))],
)

funds_router = APIRouter(
    prefix="/api/v1/admin/accounts",
    tags=["Admin - Funds"],
    dependencies=[Depends(require_right("RIGHT_ACCOUNTANT"))],
)

holidays_router = APIRouter(
    prefix="/api/v1/admin/holidays",
    tags=["Admin - Holidays"],
    dependencies=[Depends(require_right("RIGHT_CFG_HOLIDAYS"))],
)

symbol_reads_router = APIRouter(
    prefix="/api/v1/admin/symbols",
    tags=["Admin - Symbol reads"],
    dependencies=[Depends(require_right("RIGHT_CFG_SYMBOLS"))],
)


def _paged_or_503(response: Response, rows: List[Any], total: int) -> List[Any]:
    return _paged(response, rows, total)


# ---------------------------------------------------------------------------
# routing (B5) - the M8 rule table, served in EVALUATION ORDER because for a
# top-down first-match engine, order IS the semantics
# ---------------------------------------------------------------------------


@routing_reads_router.get("")
async def list_routing(response: Response) -> Dict[str, Any]:
    """Both routing tables: the MT5-wire rules (replayed 18/18 by the M8
    proof) in their evaluation order, and the house rules. Read-only: the
    write side is an honest skeleton until the command layer exists."""
    mt5_repo = get_mt5_routing_repo()
    house_repo = get_routing_rule_repo()
    if mt5_repo is None and house_repo is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE,
                            "No routing repository is wired on this server")
    mt5_rules, house_rules = [], []
    if mt5_repo is not None:
        mt5_rules = [_jsonable(r) for r in await mt5_repo.get_all_ordered()]
    if house_repo is not None:
        house_rules = [_jsonable(r) for r in await house_repo.get_active_rules()]
    response.headers["X-Total-Count"] = str(len(mt5_rules) + len(house_rules))
    return {"mt5_rules": mt5_rules, "house_rules": house_rules}


# ---------------------------------------------------------------------------
# ticks snapshot (B6 / ENDPOINTS B3) - the engine already holds them
# ---------------------------------------------------------------------------


@quotes_reads_router.get("/ticks")
async def ticks_snapshot(
    symbol_repo: Any = Depends(get_symbol_repo),
    engine: Any = Depends(get_market_data_engine),
) -> List[Dict[str, Any]]:
    """Last known bid/ask/spread/age per symbol, with the SOURCE label (M5's
    self-labelling mock rule). A symbol with no tick is listed with nulls -
    an honest absence, never a fabricated zero. The Market Watch page's
    polling fallback while the WS story matures."""
    if engine is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE,
                            "No market data engine is wired on this server")
    symbols = []
    if symbol_repo is not None:
        symbols = await symbol_repo.get_all_symbols()
    now = datetime.now(_tz.utc)
    out = []
    for sym in symbols:
        tick = engine.get_latest_tick(sym.name)
        if tick is None:
            out.append({"symbol": sym.name, "bid": None, "ask": None, "spread": None,
                        "source": None, "timestamp": None, "age_seconds": None})
            continue
        age = (now - tick.timestamp).total_seconds() if tick.timestamp else None
        out.append({
            "symbol": tick.symbol, "bid": str(tick.bid), "ask": str(tick.ask),
            "spread": str(tick.spread), "source": tick.source,
            "timestamp": tick.timestamp.isoformat() if tick.timestamp else None,
            "age_seconds": round(age, 1) if age is not None else None,
        })
    return out


# ---------------------------------------------------------------------------
# risk reads (B7-B9 / ENDPOINTS B9)
# ---------------------------------------------------------------------------


@risk_reads_router.get("/exposure")
async def risk_exposure(
    position_repo: Any = Depends(get_position_repo),
    coverage_repo: Any = Depends(get_coverage_repo),
) -> Dict[str, Any]:
    """Net open position per symbol (the NOP view) plus the coverage account's
    maintained exposure - the two halves of "what is the broker holding?\""""
    if position_repo is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE,
                            "Position repository is not wired")
    positions = await position_repo.get_open_positions()
    net: Dict[str, Decimal] = {}
    for p in positions:
        signed = p.volume.value if str(p.action.value).upper().startswith("BUY") else -p.volume.value
        net[p.symbol] = net.get(p.symbol, Decimal("0")) + signed
    coverage = None
    if coverage_repo is not None:
        account = await coverage_repo.find_by_id("DEFAULT_COVERAGE")
        if account is not None:
            coverage = _jsonable(account)
    return {
        "net_open_position": {k: str(v) for k, v in sorted(net.items())},
        "open_positions": len(positions),
        "coverage_account": coverage,
    }


@risk_reads_router.get("/summary")
async def risk_summary(
    account_repo: Any = Depends(get_account_repo),
    position_repo: Any = Depends(get_position_repo),
    order_repo: Any = Depends(get_order_repo),
    break_repo: Any = Depends(get_break_repo),
) -> Dict[str, Any]:
    """The risk desk's one-glance panel, assembled from COUNTs - no row is
    loaded that is not served (the find_all()[:limit] trap, avoided)."""
    out: Dict[str, Any] = {}
    if account_repo is not None:
        _, out["accounts_total"] = await account_repo.find_page(limit=1)
        _, out["accounts_in_stop_out_state"] = await account_repo.find_page(limit=1, so_active=True)
        _, out["accounts_online"] = await account_repo.find_page(limit=1, online=True)
    if position_repo is not None:
        _, out["open_positions"] = await position_repo.find_page(limit=1)
    if order_repo is not None:
        _, out["active_orders"] = await order_repo.find_page(limit=1, history=False)
    if break_repo is not None:
        breaks = await break_repo.find_open()
        out["reconciliation_breaks_open"] = len(breaks)
    else:
        out["reconciliation_breaks_open"] = None   # honest absence, not 0
    return out


@risk_reads_router.get("/margin-calls")
async def margin_calls(
    response: Response,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    repo: Any = Depends(get_account_repo),
) -> List[Dict[str, Any]]:
    """Accounts inside the margin-call/stop-out state machine (so_activation
    != NONE) - the MT5 color-coded ticket list's data source."""
    if repo is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Account repository is not wired")
    from application.queries.list_accounts import ListAccountsQuery, ListAccountsQueryHandler

    rows, total = await ListAccountsQueryHandler(repo).handle(
        ListAccountsQuery(limit=limit, offset=offset, so_active=True))
    return _paged(response, [account_summary(a) for a in rows], total)


# ---------------------------------------------------------------------------
# trade calculators (B12) - MT5's trade/calc_* family, one authority: RiskEngine
# ---------------------------------------------------------------------------


class CalcMarginRequest(BaseModel):
    group_name: str
    symbol: str
    side: str
    volume: Decimal
    currency: Optional[str] = None


class CalcProfitRequest(BaseModel):
    symbol: str
    side: str
    volume: Decimal
    open_price: Decimal
    currency: Optional[str] = None


class CalcRateRequest(BaseModel):
    from_currency: str
    to_currency: str
    side: str = "BUY"


class CheckMarginRequest(BaseModel):
    login: int
    symbol: str
    side: str
    volume: Decimal


def _calculator() -> Any:
    from application.queries.trade_calculators import TradeCalculatorHandler

    engine = get_risk_engine()
    if engine is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE,
                            "Risk engine is not wired; the calculator refuses rather than approximates")
    return TradeCalculatorHandler(
        risk_engine=engine,
        group_repo=get_group_repo(),
        account_repo=get_account_repo(),
        position_repo=get_position_repo(),
    )


async def _calc(handle, query) -> Dict[str, Any]:
    from application.queries.trade_calculators import CalculatorRefusedError

    try:
        return await handle(query)
    except CalculatorRefusedError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))


@calc_router.post("/calc-margin")
async def calc_margin(body: CalcMarginRequest) -> Dict[str, Any]:
    from application.queries.trade_calculators import CalcMarginQuery

    calc = _calculator()
    return await _calc(calc.calc_margin, CalcMarginQuery(
        group_name=body.group_name, symbol=body.symbol, side=body.side,
        volume=body.volume, currency=body.currency))


@calc_router.post("/calc-profit")
async def calc_profit(body: CalcProfitRequest) -> Dict[str, Any]:
    from application.queries.trade_calculators import CalcProfitQuery

    calc = _calculator()
    return await _calc(calc.calc_profit, CalcProfitQuery(
        symbol=body.symbol, side=body.side, volume=body.volume,
        open_price=body.open_price, currency=body.currency))


@calc_router.post("/calc-rate")
async def calc_rate(body: CalcRateRequest) -> Dict[str, Any]:
    from application.queries.trade_calculators import CalcRateQuery

    calc = _calculator()
    return await _calc(calc.calc_rate, CalcRateQuery(
        from_currency=body.from_currency, to_currency=body.to_currency, side=body.side))


@calc_router.post("/check-margin")
async def check_margin(body: CheckMarginRequest) -> Dict[str, Any]:
    from application.queries.trade_calculators import CheckMarginQuery

    calc = _calculator()
    return await _calc(calc.check_margin, CheckMarginQuery(
        login=body.login, symbol=body.symbol, side=body.side, volume=body.volume))


# ---------------------------------------------------------------------------
# funds (B10) - the M16 ledger-backed balance operation, finally mounted.
# MT5's own right for "work with funds on accounts" is RIGHT_ACCOUNTANT (24),
# NOT RIGHT_ACC_MANAGER - an account editor must not thereby move money.
# ---------------------------------------------------------------------------


class BalanceRequest(BaseModel):
    operation: str = Field(..., description="DEPOSIT | WITHDRAWAL | CORRECTION | BONUS")
    amount: Decimal
    comment: Optional[str] = None
    reference_id: Optional[str] = None


@funds_router.post("/{login}/balance", status_code=status.HTTP_201_CREATED)
async def balance_operation(
    login: int,
    body: BalanceRequest,
    account_repo: Any = Depends(get_account_repo),
    ledger_repo: Any = Depends(get_ledger_repo),
) -> Dict[str, Any]:
    """Deposit/withdraw/correct/bonus with a ledger row - or refuse. The
    system-generated types (COMMISSION, SWAP, DEAL_PROFIT) are refused here:
    they belong to the engines that book them, and a manager typing SWAP into
    a deposit form is how a ledger stops being evidence."""
    from application.commands.balance_operation import (
        BalanceOperationCommand,
        BalanceOperationCommandHandler,
    )
    from core.domains.common.value_objects import Money
    from core.domains.ledger.engine import LedgerEngine
    from core.domains.ledger.models import BalanceOperationType

    allowed = {"DEPOSIT", "WITHDRAWAL", "CORRECTION", "BONUS"}
    op = body.operation.upper()
    if op not in allowed:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            f"operation must be one of {sorted(allowed)}; {op!r} is system-generated")
    if body.amount <= 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "amount must be positive; a negative deposit is a withdrawal - say which")
    if account_repo is None or ledger_repo is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE,
                            "Balance operations need the account and ledger repositories wired")
    account = await account_repo.find_by_login(login)
    if account is None:
        account = await account_repo.find_by_login(str(login))
    if account is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"no account with login {login}")

    handler = BalanceOperationCommandHandler(
        ledger_engine=LedgerEngine(ledger_repo=ledger_repo, account_repo=account_repo),
        event_bus=get_event_bus(),
    )
    result = await handler.handle(BalanceOperationCommand(
        account_login=str(account.login),
        operation_type=BalanceOperationType(op),
        amount=Money(body.amount, account.currency),
        reference_id=body.reference_id,
        comment=body.comment,
    ))
    return {
        "operation_id": result.operation_id,
        "login": int(account.login),
        "operation": result.operation_type.value,
        "amount": str(result.amount.amount),
        "currency": result.amount.currency,
        "balance_after": str(result.balance_after.amount),
        "comment": result.comment,
        "created_at": result.created_at.isoformat(),
    }


# ---------------------------------------------------------------------------
# holidays (B11) - the command and repo existed with ZERO routes
# ---------------------------------------------------------------------------


def _holiday_payload(h: Any) -> Dict[str, Any]:
    return {
        "id": h.id,
        "description": h.description,
        "mode": h.mode.value if hasattr(h.mode, "value") else str(h.mode),
        "year": int(h.year),          # 0 = every year (MT5's own convention)
        "month": int(h.month),
        "day": int(h.day),
        "work_from": str(h.work_from),
        "work_to": str(h.work_to),
        "symbols": list(h.symbols),   # empty = all symbols
        "created_at": _dt(h.created_at),
        "updated_at": _dt(h.updated_at),
    }


@holidays_router.get("")
async def list_holidays(
    symbol: Optional[str] = Query(None, description="Filter to one symbol's calendar"),
    year: Optional[int] = Query(None, description="With symbol: which year (default: current)"),
    active_on: Optional[str] = Query(None, description="ISO date: only holidays active that day"),
    repo: Any = Depends(get_holiday_repo),
) -> List[Dict[str, Any]]:
    """The holiday calendar. No filters = the whole table (the UI's Holidays
    tab); active_on = what applies that day; symbol+year = one symbol's
    calendar for a year."""
    if repo is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Holiday repository is not wired")
    if active_on:
        when = datetime.fromisoformat(active_on)
        rows = await repo.get_active_holidays(when)
    elif symbol:
        rows = await repo.get_holidays_for_symbol(symbol, year or datetime.now(_tz.utc).year)
    else:
        rows = await repo.get_all()
    return [_holiday_payload(h) for h in rows]


class HolidayCreateRequest(BaseModel):
    description: str
    year: int = 0
    month: int = Field(1, ge=1, le=12)
    day: int = Field(1, ge=1, le=31)
    work_from: str = "00:00:00"
    work_to: str = "23:59:59"
    symbols: Optional[List[str]] = None
    mode: str = "ENABLED"


@holidays_router.post("", status_code=status.HTTP_201_CREATED)
async def create_holiday(body: HolidayCreateRequest) -> Dict[str, Any]:
    from application.commands.create_holiday import CreateHolidayCommand, CreateHolidayHandler

    repo = get_holiday_repo()
    if repo is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Holiday repository is not wired")
    handler = CreateHolidayHandler(holiday_repo=repo, event_bus=get_event_bus())
    holiday = await handler.handle(CreateHolidayCommand(**body.model_dump()))
    return _holiday_payload(holiday)


@holidays_router.delete("/{holiday_id}")
async def delete_holiday(holiday_id: str) -> Dict[str, Any]:
    repo = get_holiday_repo()
    if repo is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Holiday repository is not wired")
    deleted = await repo.delete(holiday_id)
    if not deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"no holiday with id {holiday_id}")
    return {"deleted": holiday_id}


# ---------------------------------------------------------------------------
# symbol sessions (B16) - the session model exists and pre-trade already uses
# it; this just lets the UI ask the same question MT5's IsTradeSession asks
# ---------------------------------------------------------------------------


@symbol_reads_router.get("/{symbol_name}/sessions")
async def symbol_sessions(symbol_name: str) -> Dict[str, Any]:
    """The symbol's trade/quote session calendar plus the two live booleans
    (mtapi's IsTradeSession/IsQuoteSession) - answered by the SAME entity
    methods the pre-trade checks use, so the UI and the risk gate can never
    disagree about whether the market is open."""
    from api.di_providers import get_symbol_repo

    repo = get_symbol_repo()
    if repo is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Symbol repository is not wired")
    symbol = await repo.find_by_name(symbol_name)
    if symbol is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"no symbol {symbol_name}")
    now = datetime.now(_tz.utc)
    return {
        "symbol": symbol.name,
        "is_trade_session": bool(symbol.is_trade_session_active(now)),
        "is_quote_session": bool(symbol.is_quote_session_active(now)),
        "trade_sessions": _jsonable(symbol.trading_sessions),
        "quote_sessions": _jsonable(symbol.quote_sessions),
        "checked_at": now.isoformat(),
    }
'''

s = s.rstrip("\n") + "\n" + APPEND

# reads.py needs BaseModel/Field + Decimal imports
s = s.replace("from fastapi import APIRouter, Depends, HTTPException, Query, Response, status",
              "from fastapi import APIRouter, Depends, HTTPException, Query, Response, status\nfrom pydantic import BaseModel, Field", 1)
if "from decimal import Decimal" not in s:
    s = s.replace("from datetime import datetime\n", "from datetime import datetime\nfrom decimal import Decimal\n", 1)
open(p, "w", encoding="utf-8").write(s)
print("reads.py: 7 routers appended")

# --------------------------------------------------------------- main.py mounts
p = "api/main.py"
s = open(p, encoding="utf-8").read()
if "routing_reads_router" not in s:
    OLD = "    app.include_router(admin_reads.trade_reads_router)"
    NEW = '''    app.include_router(admin_reads.trade_reads_router)
    # M18: the rest of the read surface - routing, quotes, risk, calculators,
    # funds, holidays, symbol sessions. All additive paths; funds shares the
    # /accounts prefix but only POST /{login}/balance, which no other router
    # declares.
    app.include_router(admin_reads.routing_reads_router)
    app.include_router(admin_reads.quotes_reads_router)
    app.include_router(admin_reads.risk_reads_router)
    app.include_router(admin_reads.calc_router)
    app.include_router(admin_reads.funds_router)
    app.include_router(admin_reads.holidays_router)
    app.include_router(admin_reads.symbol_reads_router)'''
    assert OLD in s, "main.py mount anchor"
    s = s.replace(OLD, NEW, 1)
    open(p, "w", encoding="utf-8").write(s)
    print("main.py: 7 routers mounted")
else:
    print("main.py already mounted")
