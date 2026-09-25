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
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from api.auth.admin_dependencies import require_right
from api.di_providers import (
    get_account_repo,
    get_client_repo,
    get_deal_repo,
    get_group_repo,
    get_manager_repo,
    get_order_repo,
    get_position_repo,
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


def position_payload(p: Any) -> Dict[str, Any]:
    """The admin-plane position row: the manager plane's serializer, dumped -
    one builder for one shape (F8/F9)."""
    from api.schemas.manager.main import position_to_info

    return position_to_info(p).model_dump(mode="json", by_alias=True)


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


@account_reads_router.get("/{login}")
async def get_account_detail(
    login: int,
    repo: Any = Depends(get_account_repo),
    group_repo: Any = Depends(get_group_repo),
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


@trade_reads_router.get("/positions")
async def list_positions(
    response: Response,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    login: Optional[int] = Query(None),
    symbol: Optional[str] = Query(None),
    include_closed: bool = Query(False),
    repo: Any = Depends(get_position_repo),
) -> List[Dict[str, Any]]:
    from application.queries.list_positions import ListPositionsQuery, ListPositionsQueryHandler

    handler = ListPositionsQueryHandler(repo)
    try:
        rows, total = await handler.handle(ListPositionsQuery(
            limit=limit, offset=offset, account_login=login,
            symbol=symbol, include_closed=include_closed,
        ))
    except Exception:
        logger.exception("list_positions failed")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Could not read positions")
    return _paged(response, [position_payload(p) for p in rows], total)


@trade_reads_router.get("/deals")
async def list_deals(
    response: Response,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    login: Optional[int] = Query(None),
    symbol: Optional[str] = Query(None),
    entry: Optional[str] = Query(None, description="IN | OUT | INOUT | OUT_BY"),
    repo: Any = Depends(get_deal_repo),
) -> List[Dict[str, Any]]:
    from application.queries.list_deals import ListDealsQuery, ListDealsQueryHandler

    if repo is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Deal repository is not wired")
    handler = ListDealsQueryHandler(repo)
    try:
        rows, total = await handler.handle(ListDealsQuery(
            limit=limit, offset=offset, account_login=login, symbol=symbol, entry=entry,
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
    symbol: Optional[str] = Query(None),
    state: Optional[str] = Query(None, description="A terminal state; contradicts nothing here"),
    repo: Any = Depends(get_order_repo),
) -> List[Dict[str, Any]]:
    """Terminal-state orders (CANCELLED/FILLED/REJECTED/EXPIRED). Declared
    BEFORE /orders/{...}-shaped paths and with history=True pinned, so the
    UI's getOrderHistory() cannot accidentally receive the active book."""
    from application.queries.list_orders import ListOrdersQuery, ListOrdersQueryHandler

    if repo is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Order repository is not wired")
    handler = ListOrdersQueryHandler(repo)
    try:
        rows, total = await handler.handle(ListOrdersQuery(
            limit=limit, offset=offset, account_login=login, symbol=symbol,
            state=state, history=True,
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
    symbol: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    history: Optional[bool] = Query(None, description="false = active book, true = terminal, omit = all"),
    repo: Any = Depends(get_order_repo),
) -> List[Dict[str, Any]]:
    from application.queries.list_orders import ListOrdersQuery, ListOrdersQueryHandler

    if repo is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Order repository is not wired")
    handler = ListOrdersQueryHandler(repo)
    try:
        rows, total = await handler.handle(ListOrdersQuery(
            limit=limit, offset=offset, account_login=login, symbol=symbol,
            state=state, history=history,
        ))
    except ValueError as exc:      # state contradicting history
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))
    except Exception:
        logger.exception("list_orders failed")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Could not read orders")
    return _paged(response, [order_payload(o) for o in rows], total)
