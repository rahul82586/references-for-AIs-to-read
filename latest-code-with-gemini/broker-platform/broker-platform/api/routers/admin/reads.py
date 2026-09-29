"""Admin READ plane (plan step 8 / ENDPOINTS.md B2) - the reads the Theia UI
had no source for.

Three routers, each gated by the MT5 right that governs READING that section
(the writes keep their own, stronger bits - step 6/7):

    account_reads_router  RIGHT_ACC_READ (25)      "Access to accounts"
    client_reads_router   RIGHT_CLIENTS_ACCESS (96) "Access to the Clients section"
    trade_reads_router    RIGHT_TRADES_READ (29)   "Viewing trading orders, deals
                                                    and positions"

The manager list lives on the step-7 managers router (RIGHT_CFG_MANAGERS),
reusing its serializer - one builder per wire shape (the D18 lesson).

Response conventions, deliberate:

* LISTS are BARE ARRAYS with the total in `X-Total-Count`. The UI does
  `setPositions(data)` today (api.ts) - an envelope would break every page at
  once, and MT5's own Web API returns bare arrays. `limit`/`offset` page.
* Decimals are STRINGS, matching the admin plane's existing convention
  (admin_router.list_accounts) - a JSON float of 107.978 is how rounding lies
  reach the browser.
* Tickets follow the F9 rule: the venue's own number from `external_id` when
  there is one, else null - never 0, never a hash of our UUID. Our canonical
  ids ride alongside as strings.
* Credential material is NEVER serialized. The account Security tab is
  booleans (`master_password_set`), the client's deprecated password columns
  likewise. A GET that can return a hash is a GET that can leak one.
* `rights` on the account detail is DECODED server-side: names, bits, labels,
  tabs and the `inverted` flags - the 0/1 problem must not reach the browser.
"""
from __future__ import annotations

import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, Field

from api.auth.admin_dependencies import require_right
from api.di_providers import (
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
)

logger = logging.getLogger(__name__)

account_reads_router = APIRouter(
    prefix="/api/v1/admin/accounts",
    tags=["Admin - Account reads"],
    dependencies=[Depends(require_right("RIGHT_ACC_READ"))],
)

client_reads_router = APIRouter(
    prefix="/api/v1/admin/clients",
    tags=["Admin - Client reads"],
    dependencies=[Depends(require_right("RIGHT_CLIENTS_ACCESS"))],
)

trade_reads_router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin - Trade reads"],
    dependencies=[Depends(require_right("RIGHT_TRADES_READ"))],
)


# ---------------------------------------------------------------------------
# serializers - ONE builder per wire shape
# ---------------------------------------------------------------------------


def _dt(value: Optional[datetime]) -> Optional[str]:
    return value.isoformat() if value is not None else None


def _enum(value: Any) -> Any:
    return value.value if hasattr(value, "value") else (value.name if hasattr(value, "name") else value)


def external_ticket(external_id: Optional[str]) -> Optional[int]:
    """The F9 rule, in one place: a real venue ticket is numeric or it is
    null. Never 0 - a fabricated ticket collapses every internal row into one
    when a UI keys by it."""
    if external_id is not None and str(external_id).lstrip("-").isdigit():
        return int(external_id)
    return None


def account_summary(a: Any) -> Dict[str, Any]:
    """The Accounts-table row. A superset of the legacy admin_router shape
    (same keys, same string decimals) so the existing UI keeps working, plus
    the identity fields the page has always wanted."""
    group = a.group
    return {
        "login": str(a.login),
        "group": group.name if group is not None else None,
        "account_type": _enum(a.account_type),
        "currency": a.currency,
        "balance": str(a.balance.amount),
        "credit": str(a.credit.amount),
        "equity": str(a.equity.amount),
        "margin_used": str(a.margin_used.amount),
        "margin_free": str(a.margin_free.amount),
        "margin_level": str(a.margin_level),
        "so_activation": _enum(a.so_activation),
        # step-8 additions
        "name": a.display_name(),
        "client_id": a.client_id or None,
        "enabled": bool(a.is_enabled),
        # legacy key from admin_router's list (the UI may read either during
        # the transition; both come from the same property - one writer)
        "is_enabled": bool(a.is_enabled),
        "rights": int(a.rights),
        "leverage": int(a.effective_leverage()),
    }


def account_rights_payload(a: Any) -> Dict[str, Any]:
    """The Limits tab's checkbox tree, decoded server-side. `inverted` marks
    the bits whose SDK sense is opposite to the UI label (TRADE_DISABLED vs
    "Enable trading") - the same metadata /schema serves, applied to THIS
    account so the UI renders state, not maths."""
    from core.domains.identity.rights import user_right_descriptors

    mask = int(a.rights)
    bits = []
    for d in user_right_descriptors():
        bit = int(d.bit)
        bits.append({
            "name": d.name,
            "bit": bit,
            "hex": hex(bit),
            "label": d.label,
            "tab": d.tab,
            "inverted": d.inverted,
            "description": d.description,
            "granted": bool(mask & bit),
        })
    return {
        "mask": mask,
        "hex": hex(mask),
        "names": [b["name"] for b in bits if b["granted"]],
        "bits": bits,
    }


def account_detail_payload(a: Any) -> Dict[str, Any]:
    """The whole six-tab Edit-Account payload in one read
    (ACCOUNT-GROUP-CREATION-SPEC §2b). Subscriptions is an honest empty list -
    the platform models no subscriptions yet, and inventing a shape now would
    be a schema the domain cannot fill."""
    group = a.group
    margin = group.margin if group is not None else None
    return {
        "login": int(a.login),
        "client_id": a.client_id or None,
        "group": (
            {
                "name": group.name,
                "account_type": _enum(group.account_type),
                "currency": group.currency,
                "currency_digits": group.currency_digits,
                "server_id": int(group.server_id or 1),
                "leverage_default": int(margin.leverage_default) if margin is not None else None,
                "leverage_max": int(margin.leverage_max) if margin is not None else None,
                "margin_call_level": str(margin.margin_call_level) if margin is not None else None,
                "stop_out_level": str(margin.stop_out_level) if margin is not None else None,
                "limit_orders": group.limit_orders,
                "auth_password_min": int(group.auth_password_min or 0),
            }
            if group is not None
            else None
        ),
        "account_type": _enum(a.account_type),
        "currency": a.currency,
        "currency_digits": int(a.currency_digits),
        # ---- Overview tab (read model; RIGHT_ACC_READ) ----
        "overview": {
            "balance": str(a.balance.amount),
            "credit": str(a.credit.amount),
            "equity": str(a.equity.amount),
            "margin_used": str(a.margin_used.amount),
            "margin_free": str(a.margin_free.amount),
            "margin_reserved": str(a.margin_reserved.amount),
            "margin_level": str(a.margin_level),
            "profit": str(a.profit.amount),
            "storage": str(a.storage.amount),
            "commission": str(a.commission.amount),
            "so_activation": _enum(a.so_activation),
            "so_time": _dt(a.so_time),
            "so_level": str(a.so_level) if a.so_level is not None else None,
            "so_equity": str(a.so_equity.amount) if a.so_equity is not None else None,
            "so_margin": str(a.so_margin.amount) if a.so_margin is not None else None,
            "is_online": bool(a.is_online),
            "last_login": _dt(a.last_login),
            "registration_date": _dt(a.registration_date),
            "created_at": _dt(a.created_at),
            "updated_at": _dt(a.updated_at),
        },
        # ---- Personal tab (Backoffice/KYC; bits 26/76-81) ----
        "personal": {
            "first_name": a.first_name,
            "last_name": a.last_name,
            "middle_name": a.middle_name,
            "display_name": a.display_name(),
            "company": a.company,
            "country": a.country,
            "state": a.state,
            "city": a.city,
            "zip_code": a.zip_code,
            "address": a.address,
            "phone": a.phone,
            "email": a.email,
            "language": a.language,
            "residency_status": a.residency_status,
            "id_number": a.id_number,
            "lead_source": a.lead_source,
            "lead_campaign": a.lead_campaign,
            "mqid": a.mqid,
            "visitor_id": a.visitor_id,
            "comment": a.comment,
        },
        # ---- Account tab (trading config; RIGHT_ACC_MANAGER) ----
        "account": {
            "leverage": int(a.effective_leverage()),
            "leverage_set": a.leverage,
            "color": a.color,
            "color_tag": a.color_tag,
            "dealer_notes": a.dealer_notes,
            "agent_login": a.agent_login,
            "bank_account": a.bank_account,
            "interest_rate": str(a.interest_rate),
        },
        # ---- Limits tab (RMS; bits 70/71 for the technical flags) ----
        "limits": {
            "enabled": bool(a.is_enabled),
            "limit_orders": a.limit_orders,
            "limit_orders_effective": a.effective_limit_orders(
                group.limit_orders if group is not None else None
            ),
            "limit_positions_value": (
                str(a.limit_positions_value) if a.limit_positions_value is not None else None
            ),
            "rights": account_rights_payload(a),
            "derived": {
                "may_trade": bool(a.may_trade),
                "trading_disabled": bool(a.trading_disabled),
                "must_change_password": bool(a.must_change_password),
                "is_technical": bool(a.is_technical),
                "is_investor_session": bool(a.is_investor_session),
            },
        },
        # ---- Subscriptions tab (billing; bits 52/53) ----
        "subscriptions": [],
        # ---- Security tab (booleans ONLY; hashes never leave the server) ----
        "security": {
            "master_password_set": bool(a.password_hash),
            "investor_password_set": bool(a.investor_password_hash),
            "phone_password_set": bool(a.phone_password_hash),
            "webapi_password_set": bool(a.webapi_password_hash),
            "otp_enabled": bool(a.otp_secret),
            "cert_serial_number": a.cert_serial_number,
            "last_pass_change": _dt(a.last_pass_change),
            "last_ip": a.last_ip or None,
        },
    }


def client_payload(c: Any) -> Dict[str, Any]:
    """One client record. The four password columns on this row are the
    DEPRECATED location (step 5) - exposed as booleans, like the account's."""
    return {
        "id": c.id,
        "client_id": c.client_id or None,
        "mqid": c.mqid or None,
        "full_name": c.full_name,
        "middle_name": c.middle_name,
        "company": c.company,
        "country": c.country,
        "state": c.state,
        "city": c.city,
        "zip_code": c.zip_code,
        "address": c.address,
        "phone": c.phone,
        "email": c.email,
        "language": c.language,
        "id_number": c.id_number,
        "lead_source": c.lead_source,
        "lead_campaign": c.lead_campaign,
        "comments": c.comments,
        # ClientStatus is a domain ENUM (its own value mapping - not the raw
        # EnClientStatus ordinals); serve both the value and the name so the
        # UI never has to keep a second translation table.
        "status": c.status.value if hasattr(c.status, "value") else int(c.status or 0),
        "status_name": c.status.name if hasattr(c.status, "name") else None,
        "external_id": c.external_id or None,
        "agent_login": c.agent_login,
        "registration_date": _dt(c.registration_date),
        "last_visit": _dt(c.last_visit),
        "last_pass_change": _dt(c.last_pass_change),
        "created_at": _dt(c.created_at),
        "updated_at": _dt(c.updated_at),
        "security": {
            "password_set": bool(c.password_hash),
            "investor_password_set": bool(c.investor_password_hash),
            "phone_password_set": bool(c.phone_password_hash),
            "otp_enabled": bool(c.otp_secret),
            "certificate_fingerprint": c.certificate_fingerprint,
        },
    }


def deal_payload(d: Any) -> Dict[str, Any]:
    return {
        "ticket": external_ticket(d.external_id),
        "deal_id": str(d.deal_id),
        "order_id": d.order_id,
        "position_id": d.position_id,
        "login": int(d.account_login),
        "dealer_login": d.dealer_login,
        "symbol": d.symbol,
        "deal_type": _enum(d.deal_type),
        "entry": _enum(d.entry),
        "reason": _enum(d.reason),
        "volume": str(d.volume.value),
        "price": str(d.price.value),
        "profit": str(d.profit.amount),
        "swap": str(d.swap.amount),
        "commission": str(d.commission.amount),
        "comment": d.comment or None,
        "created_at": _dt(d.created_at),
    }


def order_payload(o: Any) -> Dict[str, Any]:
    return {
        "ticket": external_ticket(o.external_id),
        "order_id": str(o.ticket_id),
        "login": int(o.account_login),
        "dealer_login": o.dealer_login,
        "symbol": o.symbol,
        "order_type": _enum(o.order_type),
        "state": _enum(o.state),
        "reason": _enum(o.reason),
        "volume_initial": str(o.volume_initial.value),
        "volume_current": str(o.volume_current.value),
        "price_order": str(o.price_order.value) if o.price_order is not None else None,
        "price_sl": str(o.price_sl.value) if o.price_sl is not None else None,
        "price_tp": str(o.price_tp.value) if o.price_tp is not None else None,
        "time_setup": _dt(o.time_setup),
        "time_expiration": _dt(o.time_expiration),
        "time_done": _dt(o.time_done),
        "comment": o.comment or None,
    }


def position_payload(p: Any, live_quotes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """The admin-plane position row: the manager plane's serializer, dumped -
    one builder for one shape (F8/F9)."""
    from api.schemas.manager.main import position_to_info

    info = position_to_info(p)
    action_upper = str(info.action).upper()
    clean_sym = info.symbol.split('\\')[-1].split('/')[-1].upper()
    q_bid = None
    q_ask = None

    if live_quotes:
        sym_quotes = live_quotes.get(info.symbol.upper()) or live_quotes.get(clean_sym) or {}
        q_bid = sym_quotes.get("bid")
        q_ask = sym_quotes.get("ask")

    if q_bid is None or q_ask is None:
        try:
            from api.di_providers import get_market_data_engine
            mde = get_market_data_engine()
            if mde is not None:
                t = mde.get_latest_tick(info.symbol.upper()) or mde.get_latest_tick(clean_sym)
                if t is not None:
                    q_bid = t.bid
                    q_ask = t.ask
        except Exception:
            pass

    live_price_str = q_bid if action_upper.startswith("BUY") else q_ask
    if live_price_str is not None:
        try:
            live_price = Decimal(str(live_price_str))
            info.price_current = live_price
            vol = Decimal(str(info.volume))
            price_open = Decimal(str(info.price_open))
            c_size = Decimal(str(getattr(p, 'contract_size', None) or getattr(info, 'contract_size', None) or 100))
            if action_upper.startswith("BUY"):
                info.profit = (live_price - price_open) * vol * c_size
            else:
                info.profit = (price_open - live_price) * vol * c_size
        except Exception:
            pass
    return info.model_dump(mode="json", by_alias=True)


def _paged(response: Response, rows: List[Any], total: int) -> List[Any]:
    """Bare array out, honest total in the header."""
    response.headers["X-Total-Count"] = str(total)
    return rows


# ---------------------------------------------------------------------------
# account reads
# ---------------------------------------------------------------------------


@account_reads_router.get("")
async def list_accounts_paged(
    response: Response,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    group: Optional[str] = Query(None, description="Exact MT5 group path, e.g. demo\\Standard"),
    account_type: Optional[str] = Query(None, description="real | demo | ..."),
    enabled: Optional[bool] = Query(None),
    repo: Any = Depends(get_account_repo),
) -> List[Dict[str, Any]]:
    """Paged account list (SQL-level; the legacy find_all()[:limit] is gone)."""
    from application.queries.list_accounts import ListAccountsQuery, ListAccountsQueryHandler

    if repo is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Account repository is not wired")
    handler = ListAccountsQueryHandler(repo)
    try:
        rows, total = await handler.handle(ListAccountsQuery(
            limit=limit, offset=offset, group_name=group,
            account_type=account_type, enabled=enabled,
        ))
    except ValueError as exc:      # a refused filter combination
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))
    except Exception:
        logger.exception("list_accounts failed")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Could not read accounts")
    return _paged(response, [account_summary(a) for a in rows], total)


@account_reads_router.get(
    "/online",
    dependencies=[Depends(require_right("RIGHT_ACC_ONLINE"))],
)
async def list_accounts_online(
    response: Response,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    repo: Any = Depends(get_account_repo),
) -> List[Dict[str, Any]]:
    """MT5's AccountsOnline (mtapi) - who is connected right now. Gated by
    RIGHT_ACC_ONLINE (28, "Getting the current client connections") ON TOP of
    the router's RIGHT_ACC_READ, exactly as MT5 keeps the two bits apart.
    Declared BEFORE /{login} or "online" would resolve as a login and 422."""
    from application.queries.list_accounts import ListAccountsQuery, ListAccountsQueryHandler

    if repo is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Account repository is not wired")
    rows, total = await ListAccountsQueryHandler(repo).handle(
        ListAccountsQuery(limit=limit, offset=offset, online=True))
    return _paged(response, [account_summary(a) for a in rows], total)


@account_reads_router.get("/{login}")
async def get_account_detail(
    login: int,
    repo: Any = Depends(get_account_repo),
    group_repo: Any = Depends(get_group_repo),
    position_repo: Any = Depends(get_position_repo),
    symbol_repo: Any = Depends(get_symbol_repo),
) -> Dict[str, Any]:
    """The six-tab account payload in one read."""
    from application.queries.get_account_detail import (
        AccountNotFoundError,
        GetAccountDetailQuery,
        GetAccountDetailQueryHandler,
    )

    if repo is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Account repository is not wired")

    handler = GetAccountDetailQueryHandler(repo, group_repo)
    try:
        account = await handler.handle(GetAccountDetailQuery(login=login))
    except AccountNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc))
    return account_detail_payload(account)


# ---------------------------------------------------------------------------
# client reads  (route order: /schema BEFORE /{client_id} - the M15 lesson)
# ---------------------------------------------------------------------------


@client_reads_router.get("/schema")
async def client_schema() -> Dict[str, Any]:
    """The descriptor list the UI renders the Client form FROM."""
    from application.queries.get_field_schema import UnknownSchemaError, get_field_schema

    try:
        return get_field_schema("client")
    except UnknownSchemaError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(exc))


@client_reads_router.get("")
async def list_clients(
    response: Response,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    repo: Any = Depends(get_client_repo),
) -> List[Dict[str, Any]]:
    """Paged client list. Live Neon holds 0 rows while 45 accounts carry
    client_ids that point at nothing - the backfill decision is pending; this
    read is honest either way (total included)."""
    from application.queries.list_clients import ListClientsQuery, ListClientsQueryHandler

    if repo is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Client repository is not wired")
    handler = ListClientsQueryHandler(repo)
    try:
        rows, total = await handler.handle(ListClientsQuery(limit=limit, offset=offset))
    except Exception:
        logger.exception("list_clients failed")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Could not read clients")
    return _paged(response, [client_payload(c) for c in rows], total)


@client_reads_router.get("/{client_id}/accounts")
async def list_client_accounts(
    client_id: str,
    response: Response,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    repo: Any = Depends(get_account_repo),
) -> List[Dict[str, Any]]:
    """One person's trading accounts (MT5's client/user link). Live Neon holds
    0 clients and 45 orphaned client_ids - this read answers honestly for
    whichever side of the backfill decision lands."""
    from application.queries.list_accounts import ListAccountsQuery, ListAccountsQueryHandler

    if repo is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Account repository is not wired")
    rows, total = await ListAccountsQueryHandler(repo).handle(
        ListAccountsQuery(limit=limit, offset=offset, client_id=client_id))
    return _paged(response, [account_summary(a) for a in rows], total)


@client_reads_router.get("/{client_id}")
async def get_client_detail(
    client_id: str,
    repo: Any = Depends(get_client_repo),
) -> Dict[str, Any]:
    """One client record, by its primary id."""
    from application.queries.get_client_detail import (
        ClientNotFoundError,
        GetClientDetailQuery,
        GetClientDetailQueryHandler,
    )

    if repo is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Client repository is not wired")
    handler = GetClientDetailQueryHandler(repo)
    try:
        client = await handler.handle(GetClientDetailQuery(client_id=client_id))
    except ClientNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc))
    return client_payload(client)


# ---------------------------------------------------------------------------
# trade reads (ENDPOINTS B2 - Orders/Deals/Positions pages had no source)
# ---------------------------------------------------------------------------


def _parse_mask_filters(
    mask: Optional[str],
    login: Optional[int],
    logins: Optional[str],
    ticket: Optional[str],
) -> Tuple[Optional[int], Optional[List[int]], Optional[str]]:
    acc_login = login
    acc_logins = [int(x.strip()) for x in logins.split(",") if x.strip().isdigit()] if logins else None
    tkt = ticket.strip() if ticket and ticket.strip() else None
    if mask and mask.strip() and mask.strip() != "*":
        m = mask.strip()
        if m.startswith("#"):
            tkt = m.lstrip("#").strip()
        elif "," in m:
            multi = [int(x.strip()) for x in m.split(",") if x.strip().isdigit()]
            if multi:
                acc_logins = multi
        elif m.isdigit():
            if acc_login is None and tkt is None:
                tkt = m
    return acc_login, acc_logins, tkt


@trade_reads_router.get("/positions")
async def list_positions(
    response: Response,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    login: Optional[int] = Query(None),
    logins: Optional[str] = Query(None),
    ticket: Optional[str] = Query(None),
    mask: Optional[str] = Query(None),
    symbol: Optional[str] = Query(None),
    include_closed: bool = Query(False),
    from_time: Optional[datetime] = Query(None, alias="from"),
    to_time: Optional[datetime] = Query(None, alias="to"),
    repo: Any = Depends(get_position_repo),
) -> List[Dict[str, Any]]:
    from application.queries.list_positions import ListPositionsQuery, ListPositionsQueryHandler

    acc_login, acc_logins, tkt = _parse_mask_filters(mask, login, logins, ticket)
    handler = ListPositionsQueryHandler(repo)
    try:
        rows, total = await handler.handle(ListPositionsQuery(
            limit=limit, offset=offset, account_login=acc_login,
            account_logins=acc_logins, ticket=tkt,
            symbol=symbol, include_closed=include_closed,
            from_time=from_time, to_time=to_time,
        ))
    except Exception:
        logger.exception("list_positions failed")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Could not read positions")

    live_quotes = {}
    try:
        from api.routers.manager.trading import get_live_quotes_map
        unique_syms = list({
            s for p in rows if getattr(p, "symbol", None)
            for s in (p.symbol.upper(), p.symbol.split('\\')[-1].split('/')[-1].upper())
        })
        if unique_syms:
            live_quotes = await get_live_quotes_map(unique_syms)
    except Exception:
        pass

    return _paged(response, [position_payload(p, live_quotes) for p in rows], total)


@trade_reads_router.get("/deals")
async def list_deals(
    response: Response,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    login: Optional[int] = Query(None),
    logins: Optional[str] = Query(None),
    ticket: Optional[str] = Query(None),
    mask: Optional[str] = Query(None),
    symbol: Optional[str] = Query(None),
    entry: Optional[str] = Query(None, description="IN | OUT | INOUT | OUT_BY"),
    from_time: Optional[datetime] = Query(None, alias="from"),
    to_time: Optional[datetime] = Query(None, alias="to"),
    repo: Any = Depends(get_deal_repo),
) -> List[Dict[str, Any]]:
    from application.queries.list_deals import ListDealsQuery, ListDealsQueryHandler

    if repo is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Deal repository is not wired")
    acc_login, acc_logins, tkt = _parse_mask_filters(mask, login, logins, ticket)
    handler = ListDealsQueryHandler(repo)
    try:
        rows, total = await handler.handle(ListDealsQuery(
            limit=limit, offset=offset, account_login=acc_login,
            account_logins=acc_logins, ticket=tkt,
            symbol=symbol, entry=entry,
            from_time=from_time, to_time=to_time,
        ))
    except Exception:
        logger.exception("list_deals failed")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Could not read deals")
    return _paged(response, [deal_payload(d) for d in rows], total)


@trade_reads_router.get("/orders/history")
async def list_order_history(
    response: Response,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    login: Optional[int] = Query(None),
    logins: Optional[str] = Query(None),
    ticket: Optional[str] = Query(None),
    mask: Optional[str] = Query(None),
    symbol: Optional[str] = Query(None),
    state: Optional[str] = Query(None, description="A terminal state; contradicts nothing here"),
    from_time: Optional[datetime] = Query(None, alias="from"),
    to_time: Optional[datetime] = Query(None, alias="to"),
    repo: Any = Depends(get_order_repo),
) -> List[Dict[str, Any]]:
    """Terminal-state orders (CANCELLED/FILLED/REJECTED/EXPIRED). Declared
    BEFORE /orders/{...}-shaped paths and with history=True pinned, so the
    UI's getOrderHistory() cannot accidentally receive the active book."""
    from application.queries.list_orders import ListOrdersQuery, ListOrdersQueryHandler

    if repo is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Order repository is not wired")
    acc_login, acc_logins, tkt = _parse_mask_filters(mask, login, logins, ticket)
    handler = ListOrdersQueryHandler(repo)
    try:
        rows, total = await handler.handle(ListOrdersQuery(
            limit=limit, offset=offset, account_login=acc_login,
            account_logins=acc_logins, ticket=tkt,
            symbol=symbol, state=state, history=True,
            from_time=from_time, to_time=to_time,
        ))
    except ValueError as exc:      # state contradicting history=True
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))
    except Exception:
        logger.exception("list_order_history failed")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Could not read order history")
    return _paged(response, [order_payload(o) for o in rows], total)


@trade_reads_router.get("/orders")
async def list_orders(
    response: Response,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    login: Optional[int] = Query(None),
    logins: Optional[str] = Query(None),
    ticket: Optional[str] = Query(None),
    mask: Optional[str] = Query(None),
    symbol: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    history: Optional[bool] = Query(None, description="false = active book, true = terminal, omit = all"),
    from_time: Optional[datetime] = Query(None, alias="from"),
    to_time: Optional[datetime] = Query(None, alias="to"),
    repo: Any = Depends(get_order_repo),
) -> List[Dict[str, Any]]:
    from application.queries.list_orders import ListOrdersQuery, ListOrdersQueryHandler

    if repo is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Order repository is not wired")
    acc_login, acc_logins, tkt = _parse_mask_filters(mask, login, logins, ticket)
    handler = ListOrdersQueryHandler(repo)
    try:
        rows, total = await handler.handle(ListOrdersQuery(
            limit=limit, offset=offset, account_login=acc_login,
            account_logins=acc_logins, ticket=tkt,
            symbol=symbol, state=state, history=history,
            from_time=from_time, to_time=to_time,
        ))
    except ValueError as exc:      # state contradicting history
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))
    except Exception:
        logger.exception("list_orders failed")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Could not read orders")
    return _paged(response, [order_payload(o) for o in rows], total)


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
    if isinstance(obj, dict):
        return {str(k): _jsonable(v) for k, v in obj.items()}
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


@risk_reads_router.get("/summary")
async def get_risk_summary(
    account_repo: Any = Depends(get_account_repo),
    position_repo: Any = Depends(get_position_repo),
) -> Dict[str, Any]:
    total_accs = 0
    at_risk = 0
    open_pos_count = 0
    total_margin = Decimal("0")
    total_profit = Decimal("0")
    total_equity = Decimal("0")
    
    if account_repo is not None:
        try:
            accounts = await account_repo.find_all()
            total_accs = len(accounts)
            for a in accounts:
                eq = a.equity.amount if hasattr(a.equity, "amount") else Decimal(str(a.equity))
                total_equity += eq
                lvl = float(getattr(a, 'margin_level', 0) or 0)
                if 0 < lvl < 300:
                    at_risk += 1
        except Exception:
            pass

    if position_repo is not None:
        try:
            positions = await position_repo.get_open_positions()
            open_pos_count = len(positions)
            for p in positions:
                prof = p.profit.amount if hasattr(p.profit, "amount") else Decimal(str(p.profit))
                total_profit += prof
                vol = p.volume.value if hasattr(p.volume, "value") else Decimal(str(p.volume))
                total_margin += vol * Decimal("100")
        except Exception:
            pass

    margin_lvl_avg = round(float(total_equity / total_margin * 100), 2) if total_margin > 0 else 0.0

    return {
        "total_accounts": total_accs,
        "open_positions": open_pos_count,
        "total_margin": float(total_margin),
        "total_profit": float(total_profit),
        "margin_level_avg": margin_lvl_avg,
        "at_risk_accounts": at_risk,
    }


@risk_reads_router.get("/exposure")
async def get_risk_exposure(
    position_repo: Any = Depends(get_position_repo),
) -> List[Dict[str, Any]]:
    if position_repo is None:
        return []
    try:
        positions = await position_repo.get_open_positions()
        by_sym: Dict[str, Dict[str, Any]] = {}
        for p in positions:
            sym = p.symbol
            if sym not in by_sym:
                by_sym[sym] = {"symbol": sym, "net_volume": 0.0, "count": 0}
            vol = float(p.volume.value if hasattr(p.volume, "value") else p.volume)
            action_str = str(getattr(p.action, 'value', p.action)).upper()
            by_sym[sym]["net_volume"] += (vol if action_str.startswith("BUY") else -vol)
            by_sym[sym]["count"] += 1
        return list(by_sym.values())
    except Exception:
        return []


@risk_reads_router.get("/margin-calls")
async def get_risk_margin_calls(
    account_repo: Any = Depends(get_account_repo),
) -> List[Dict[str, Any]]:
    if account_repo is None:
        return []
    try:
        accounts = await account_repo.find_all()
        res = []
        for a in accounts:
            lvl = float(getattr(a, 'margin_level', 0) or 0)
            if 0 < lvl < 300:
                res.append({
                    "login": int(a.login),
                    "group": getattr(a, "group_name", getattr(a, "group", "")),
                    "margin_level": lvl,
                    "state": "STOP_OUT_PENDING" if lvl < 150 else "MARGIN_CALL",
                })
        return res
    except Exception:
        return []


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
        clean_name = sym.name.split('\\')[-1].split('/')[-1].upper()
        tick = engine.get_latest_tick(sym.name) or engine.get_latest_tick(clean_name)
        if tick is None:
            out.append({"symbol": sym.name, "bid": None, "ask": None, "spread": None,
                        "source": None, "timestamp": None, "age_seconds": None})
            continue
        age = (now - tick.timestamp).total_seconds() if tick.timestamp else None
        out.append({
            "symbol": sym.name, "bid": str(tick.bid), "ask": str(tick.ask),
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
    """Net open position per symbol (the NOP view) plus the coverage
    account's maintained exposure - the two halves of the broker's book."""
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
    deal_repo: Any = Depends(get_deal_repo),
) -> Dict[str, Any]:
    """Deposit/withdraw/correct/bonus/credit/charge with a ledger row and MT5 deal record."""
    from application.commands.balance_operation import (
        BalanceOperationCommand,
        BalanceOperationCommandHandler,
    )
    from core.domains.common.value_objects import Money
    from core.domains.ledger.engine import LedgerEngine
    from core.domains.ledger.models import BalanceOperationType

    raw_op = body.operation.upper()
    allowed = {"DEPOSIT", "WITHDRAWAL", "CORRECTION", "BONUS", "CREDIT", "CHARGE", "BALANCE"}
    if raw_op not in allowed:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            f"operation must be one of {sorted(allowed)}; {raw_op!r} is invalid")
    if body.amount <= 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "amount must be positive")
    
    # Normalize op to domain BalanceOperationType
    if raw_op == "BALANCE":
        op = "DEPOSIT"
    elif raw_op == "CHARGE":
        op = "CHARGE"
    else:
        op = raw_op

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
    try:
        result = await handler.handle(BalanceOperationCommand(
            account_login=str(account.login),
            operation_type=BalanceOperationType(op),
            amount=Money(body.amount, account.currency),
            reference_id=body.reference_id,
            comment=body.comment,
        ))
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))

    # In MT5, every balance operation writes an immutable deal to the deals ledger
    deal_ticket: Optional[int] = None
    if deal_repo is not None:
        try:
            from api.routers.manager.trading import get_next_deal_ticket
            from core.domains.oms.entities.deal import Deal
            from core.domains.oms.enums import DealType, DealEntry, DealReason
            from core.domains.common.value_objects import Money, Price, Volume
            from datetime import timezone

            new_ticket = await get_next_deal_ticket(deal_repo)
            d_type = DealType[raw_op] if raw_op in DealType.__members__ else DealType.BALANCE
            delta_profit = body.amount if op in ("DEPOSIT", "BONUS", "CREDIT") else -abs(body.amount)
            deal_obj = Deal(
                deal_id=str(new_ticket),
                account_login=int(account.login),
                order_id="0",
                position_id=None,
                symbol="",
                deal_type=d_type,
                entry=DealEntry.IN,
                reason=DealReason.DEALER,
                volume=Volume(Decimal("0.0")),
                price=Price(Decimal("0.0")),
                profit=Money(delta_profit, "USD"),
                swap=Money(Decimal("0.0"), "USD"),
                commission=Money(Decimal("0.0"), "USD"),
                comment=body.comment or f"Balance operation ({raw_op.lower()})",
                created_at=datetime.now(timezone.utc),
            )

            await deal_repo.save(deal_obj)
            deal_ticket = new_ticket
        except Exception as deal_err:
            logger.warning(f"Could not record deal for balance operation: {deal_err}")



    return {
        "operation_id": result.operation_id,
        "deal_ticket": deal_ticket,
        "login": int(account.login),
        "operation": raw_op,
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
    try:
        holiday = await handler.handle(CreateHolidayCommand(**body.model_dump()))
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))
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
        "trade_sessions": _jsonable(symbol.trade_sessions),
        "quote_sessions": _jsonable(symbol.quote_sessions),
        "checked_at": now.isoformat(),
    }
