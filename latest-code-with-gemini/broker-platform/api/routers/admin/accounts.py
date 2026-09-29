"""Admin Account & Client creation - MT5's "New Account" dialog over HTTP.

Plan step 6. Mounted BEFORE admin_router for the same reason the groups router
is: both own paths under /api/v1/admin/accounts, and GET /accounts/schema must
resolve here instead of being swallowed by a /{login} route.

Auth: require_right("RIGHT_ACC_MANAGER") on the account routes and
require_right("RIGHT_CLIENTS_CREATE") on the client route - the same bits MT5's
own Permissions tree uses, enforced against the caller's 128-bit mask by the
M15 dependency. The bootstrap X-Admin-API-Key still works, because that is how a
fresh server provisions its first staff logins.

THE PASSWORD CONTRACT
---------------------
POST /accounts returns the three plaintext passwords **once**, in this response,
and never again:

* they are not logged (the handler logs the login and group only);
* they are not published on the event bus (AccountCreated carries no secret);
* they are not stored (the database holds Argon2 hashes);
* no GET ever returns them, and there is no "reveal" endpoint - MT5 has none
  either, which is why its dialog says "save it now".

A client that loses the response must rotate the password through the security
plane. That is the correct failure mode: a recoverable password is not a secret.

Error contract (ENDPOINTS.md §0): 400 the domain refused (bad password, taken
login, leverage over the group max, preliminary without the override); 404 no
such group/client; 503 a repository is not wired on this server. A 200 means the
account really exists.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from api.auth.admin_dependencies import require_right
from api.di_providers import get_account_repo, get_create_account_handler, get_create_client_handler

accounts_router = APIRouter(
    prefix="/api/v1/admin/accounts",
    tags=["Admin - Accounts"],
    dependencies=[Depends(require_right("RIGHT_ACC_MANAGER"))],
)

clients_router = APIRouter(
    prefix="/api/v1/admin/clients",
    tags=["Admin - Clients"],
    dependencies=[Depends(require_right("RIGHT_CLIENTS_CREATE"))],
)


# ---------------------------------------------------------------------------
# Request models. Field names mirror MT5's dialog; `serialization_alias` gives
# the exact SDK accessor names on the way out so a consumer written against the
# Manager API recognises them.
# ---------------------------------------------------------------------------


class ClientCreateRequest(BaseModel):
    """The KYC record - MT5 IMTClient. No password material: see create_client."""

    full_name: str = ""
    middle_name: str = ""
    company: str = ""
    country: str = ""
    state: str = ""
    city: str = ""
    zip_code: str = ""
    address: str = ""
    phone: str = ""
    email: str = ""
    language: str = "en"
    id_number: str = ""
    external_id: str = ""
    mqid: str = ""
    lead_source: str = ""
    lead_campaign: str = ""
    comments: str = ""
    agent_login: Optional[int] = None
    status: Optional[int] = None


class AccountCreateRequest(BaseModel):
    """MT5's New Account dialog: the Details box, the Passwords box, and the tabs."""

    group_name: str = Field("", description="MT5 group path, e.g. demo\\Standard")
    group: Optional[str] = None
    #: Details box. Omit `login` for MT5's "Next".
    login: Optional[int] = None
    name: Optional[str] = None
    first_name: str = ""
    last_name: str = ""
    middle_name: str = ""
    company: str = ""
    email: str = ""
    phone: str = ""
    country: str = ""
    state: str = ""
    city: str = ""
    zip: Optional[str] = None
    zip_code: str = ""
    address: str = ""
    client_id: Optional[str] = None
    client: Optional[ClientCreateRequest] = None
    #: Passwords box. Generated when omitted, returned exactly once.
    password: Optional[str] = None
    master_password: Optional[str] = None
    investor_password: Optional[str] = None
    phone_password: Optional[str] = None
    #: Account tab
    leverage: Optional[int] = None
    color: Optional[int] = None
    agent_login: Optional[int] = None
    bank_account: str = ""
    #: Limits tab. Omit to inherit the group; false/0 are real values.
    enable_trading: bool = True
    enable_experts: Optional[bool] = None
    enable_trailing: Optional[bool] = None
    enable_reports: Optional[bool] = None
    enable_otp: Optional[bool] = None
    technical_account: bool = False
    exclude_from_reports: bool = False
    show_to_regular_managers: Optional[bool] = None
    include_in_server_reports: Optional[bool] = None
    change_password_at_next_login: bool = False
    limit_orders: Optional[int] = None
    limit_positions_value: Optional[Decimal] = None
    #: Money
    initial_balance: Optional[Decimal] = None
    opening_deposit: Optional[Decimal] = None
    credit: Decimal = Decimal("0")
    #: Identity
    language: str = "en"
    residency_status: str = ""
    id_number: str = ""
    lead_source: str = ""
    lead_campaign: str = ""
    mqid: str = ""
    comment: str = ""
    allow_preliminary: bool = False


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@accounts_router.post("/schema", include_in_schema=False)
@accounts_router.get("/schema")
async def account_schema() -> Dict[str, Any]:
    """The descriptor list the UI renders the Account form FROM.

    Includes the USER_RIGHT_* members with their bits and which ones are
    INVERTED, so the two SDK bits whose sense is opposite to their label
    (TRADE_DISABLED, TECHNICAL) never reach the browser as a bare 0/1.
    """
    from application.queries.get_field_schema import UnknownSchemaError, get_field_schema
    from core.domains.identity.rights import (
        MT5_USER_RIGHT_DEFAULT,
        user_right_descriptors,
    )

    try:
        schema = get_field_schema("account")
    except UnknownSchemaError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    descriptors = user_right_descriptors()
    default = int(MT5_USER_RIGHT_DEFAULT)
    schema["user_rights"] = [
        {
            "name": d.name,
            # `bit` is the int; `flag` is the same value as a string. Send the
            # int - a UI that receives "0x4" cannot mask against it, and a mask
            # rendered from strings is how the 0/1 problem reaches the browser.
            "bit": int(d.bit),
            "hex": hex(int(d.bit)),
            "label": d.label,
            "tab": d.tab,
            "inverted": d.inverted,
            "description": d.description,
            "in_default": bool(default & int(d.bit)),
        }
        for d in descriptors
    ]
    schema["default_rights"] = default
    schema["default_rights_hex"] = hex(default)
    schema["default_rights_names"] = [
        d.name for d in descriptors if default & int(d.bit)
    ]
    return schema


@accounts_router.post("/next-login")
async def next_login(scope: Optional[str] = None) -> Dict[str, Any]:
    """What the "Next" button would show, WITHOUT reserving it.

    Advisory only: the authoritative allocation happens inside POST /accounts, so
    two administrators looking at the same suggested number cannot both get it.
    """
    handler = get_create_account_handler()
    try:
        login = await handler.login_allocator.peek(scope)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return {"login": login, "scope": scope or "global", "reserved": False}


@accounts_router.post("", status_code=status.HTTP_201_CREATED)
@accounts_router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_account(body: AccountCreateRequest) -> Dict[str, Any]:
    """Create a trading account. Returns the plaintext passwords ONCE."""
    from application.commands.create_account import (
        AccountRefusedError,
        CreateAccountCommand,
        GroupNotFoundError,
    )
    from application.commands.create_client import CreateClientCommand

    handler = get_create_account_handler()
    data = body.model_dump(exclude_none=False)

    # UI compatibility field normalization
    if data.get("group") and not data.get("group_name"):
        data["group_name"] = data["group"]
    if not data.get("group_name"):
        data["group_name"] = "demo"

    if data.get("password") and not data.get("master_password"):
        data["master_password"] = data["password"]
    if data.get("zip") and not data.get("zip_code"):
        data["zip_code"] = data["zip"]
    if data.get("name") and not data.get("first_name"):
        parts = data["name"].strip().split(" ", 1)
        data["first_name"] = parts[0]
        if len(parts) > 1 and not data.get("last_name"):
            data["last_name"] = parts[1]

    # Login normalization: 0 or non-positive treated as Next (login allocator)
    if data.get("login") is not None:
        try:
            if int(data["login"]) <= 0:
                data["login"] = None
            else:
                data["login"] = int(data["login"])
        except (ValueError, TypeError):
            data["login"] = None

    # Deposit normalization: 0 is not a deposit in domain ledger, so normalize <=0 to None
    if data.get("initial_balance") is not None and data.get("opening_deposit") is None:
        try:
            bal = Decimal(str(data["initial_balance"]))
            data["opening_deposit"] = bal if bal > 0 else None
        except Exception:
            data["opening_deposit"] = None
    elif data.get("opening_deposit") is not None:
        try:
            bal = Decimal(str(data["opening_deposit"]))
            if bal <= 0:
                data["opening_deposit"] = None
        except Exception:
            data["opening_deposit"] = None

    inline = data.pop("client", None)
    command = CreateAccountCommand(
        **{k: v for k, v in data.items() if k in CreateAccountCommand.__dataclass_fields__},
        client=CreateClientCommand(**inline) if inline else None,
    )
    try:
        result = await handler.handle(command)
    except GroupNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except AccountRefusedError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    account = result.account
    return {
        "status": "success",
        "login": result.login,
        "group": result.group_name,
        "group_name": result.group_name,
        "account_type": result.account_type,
        "currency": result.currency,
        "client_id": result.client_id,
        "rights": int(account.rights),
        "balance": str(account.balance.amount),
        "opening_deposit": result.opening_deposit,
        "logins_skipped": result.logins_skipped,
        # THE ONLY PLACE THE PLAINTEXT EXISTS. Not logged, not stored, not
        # retrievable again - there is deliberately no endpoint that returns it.
        "passwords": result.passwords,
        "master_password": result.passwords.get("master_password", ""),
        "investor_password": result.passwords.get("investor_password", ""),
        "phone_password": result.passwords.get("phone_password", ""),
        "warning": (
            "These passwords are shown exactly once and cannot be retrieved "
            "again. Save them now; use the security plane to rotate one."
        ),
    }


class AccountUpdateRequest(BaseModel):
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    company: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    zip_code: Optional[str] = None
    zip: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    group: Optional[str] = None
    group_name: Optional[str] = None
    leverage: Optional[int] = None
    is_enabled: Optional[bool] = None
    comment: Optional[str] = None


@accounts_router.put("/{login}")
@accounts_router.patch("/{login}")
async def update_account_endpoint(
    login: int,
    body: AccountUpdateRequest,
    repo: Any = Depends(get_account_repo),
) -> Dict[str, Any]:
    """Update editable details on an account."""
    if repo is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Account repository is not wired",
        )
    account = await repo.find_by_login(login)
    if account is None:
        account = await repo.find_by_login(str(login))
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no account with login {login}",
        )

    # Apply updates
    if body.name is not None:
        parts = body.name.strip().split(" ", 1)
        account.first_name = parts[0]
        if len(parts) > 1:
            account.last_name = parts[1]
    if body.first_name is not None:
        account.first_name = body.first_name
    if body.last_name is not None:
        account.last_name = body.last_name
    if body.middle_name is not None:
        account.middle_name = body.middle_name
    if body.company is not None:
        account.company = body.company
    if body.country is not None:
        account.country = body.country
    if body.state is not None:
        account.state = body.state
    if body.city is not None:
        account.city = body.city
    if body.zip_code is not None:
        account.zip_code = body.zip_code
    elif body.zip is not None:
        account.zip_code = body.zip
    if body.address is not None:
        account.address = body.address
    if body.phone is not None:
        account.phone = body.phone
    if body.email is not None:
        account.email = body.email
    if body.leverage is not None and body.leverage > 0:
        account.leverage = body.leverage
    if body.is_enabled is not None:
        account.is_enabled = body.is_enabled
    if body.comment is not None:
        account.comment = body.comment

    await repo.save(account)
    return {"status": "success", "login": login, "message": f"Account {login} updated"}


@accounts_router.delete("/{login}")
async def delete_account_endpoint(
    login: int,
    repo: Any = Depends(get_account_repo),
) -> Dict[str, Any]:
    """Delete / soft-disable an account."""
    if repo is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Account repository is not wired",
        )
    account = await repo.find_by_login(login)
    if account is None:
        account = await repo.find_by_login(str(login))
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no account with login {login}",
        )

    account.is_enabled = False
    account.comment = (account.comment or "") + " [DELETED]"
    await repo.save(account)
    return {"status": "success", "login": login, "message": f"Account {login} deleted"}


class PasswordCheckRequest(BaseModel):
    """MT5's UserPasswordCheck equivalent. The hash itself never leaves the
    server; an unprovisioned or corrupt hash is reported as invalid with a
    reason, never as a 500 and never as a silent false."""

    password: str


@accounts_router.post("/{login}/check-password")
async def check_account_password(
    login: int,
    body: PasswordCheckRequest,
    repo: Any = Depends(get_account_repo),
) -> Dict[str, Any]:
    """Verify a master password against the stored Argon2 hash (M18 B13)."""
    from core.domains.identity.password_policy import verify_password

    if repo is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Account repository is not wired")
    account = await repo.find_by_login(login)
    if account is None:
        account = await repo.find_by_login(str(login))
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"no account with login {login}")
    if not account.password_hash:
        return {"login": int(account.login), "valid": False,
                "reason": "no master password is provisioned on this account"}
    try:
        valid = verify_password(body.password, account.password_hash)
    except Exception:
        # a corrupt stored hash is a refusal, not a crash (password_policy's rule)
        return {"login": int(account.login), "valid": False,
                "reason": "the stored hash is unusable; rotate the password"}
    return {"login": int(account.login), "valid": bool(valid)}


@clients_router.post("", status_code=status.HTTP_201_CREATED)
@clients_router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_client(body: ClientCreateRequest) -> Dict[str, Any]:
    """Create a person/company record (MT5 IMTClient) to link accounts to."""
    from application.commands.create_client import ClientRefusedError, CreateClientCommand

    handler = get_create_client_handler()
    data = body.model_dump(exclude_none=True)
    status_value = data.pop("status", None)
    if status_value is not None:
        from core.domains.accounts.enums import ClientStatus

        try:
            data["status"] = ClientStatus(int(status_value))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"status {status_value!r} is not an IMTClient::EnClientStatus value; "
                    f"valid: {[m.value for m in ClientStatus]}"
                ),
            )
    try:
        client = await handler.handle(CreateClientCommand(**data))
    except ClientRefusedError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return {
        "id": client.id,
        "client_id": client.client_id,
        "external_id": client.external_id,
        "full_name": client.full_name,
        "middle_name": client.middle_name,
        "company": client.company,
        "country": client.country,
        "state": client.state,
        "city": client.city,
        "id_number": client.id_number,
        "email": client.email,
        "phone": client.phone,
        "status": client.status.name if hasattr(client.status, "name") else str(client.status),
    }
