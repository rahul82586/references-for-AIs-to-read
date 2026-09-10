"""
MT5-aligned AccountModel, and mappers for Account, Client and Manager.

WHY AccountModel IS BEING REPLACED

The previous model had 14 columns. The domain Account has 29 fields. Eighteen of them
had nowhere to go, and the mapper silently dropped them on every save:

    the entire stop-out state machine   so_activation, so_time, so_level, so_equity,
                                        so_margin
    live financial state                margin_level, profit, commission, storage,
                                        credit (column existed, mapper ignored it)
    identity & linkage                  client_id, group_id
    dealer workflow                     color_tag, dealer_notes, is_online, last_login,
                                        registration_date, currency_digits

Losing the stop-out fields is the serious one. `Account.evaluate_margin_state()` moves
an account NONE -> MARGIN_CALL -> STOP_OUT and records the equity and margin at the
moment of stop-out. `TickMarginPipeline` calls it, then persists the account. On the
next tick the account is loaded from the database with `so_activation = NONE` again, so
the state machine restarts from the beginning every single tick: `MarginCallEntered`
would fire forever, `StopOutEntered` would fire repeatedly, and `StopOutExited` could
never be reached because the machine never remembered it had entered.

Also fixed: the old mapper read `account.login_id` and `account.kyc_verified`. Neither
exists - the field is `login`, and there is no `kyc_verified` on the domain - and
`AccountModel` had a `kyc_verified` column nothing could populate. So saving ANY
account raised AttributeError. This is the same refactor drift that broke RiskEngine
(it read `position.side` / `.average_price` from a stale PositionModel).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB

from core.domains.accounts.account import Account
from core.domains.accounts.client import Client
from core.domains.accounts.enums import AccountType, ClientStatus, SOActivation
from core.domains.common.value_objects import Money
from core.domains.identity.models import ManagerAccount, ManagerRole
from infrastructure.mt5.fieldmap import MANAGER_FIELDS

from .database import Base
from .manager_models import MT5_RIGHTS_COUNT

NUMERIC = Numeric(20, 8)


class AccountModel(Base):
    """MT5 IMTAccount - the trading account and its financial state.

    Every field of the domain Account has a column, so nothing is dropped on save.
    `group_name` stays the foreign key to `groups.name` (MT5's natural key for a group
    is its path, e.g. "real\\real"), and `group_id` is kept alongside it because the
    domain carries both.
    """

    __tablename__ = "accounts"

    login = Column(String(32), primary_key=True)
    client_id = Column(String(64), nullable=True, index=True)
    group_name = Column(String(128), ForeignKey("groups.name"), nullable=False)
    group_id = Column(String(64), nullable=True, index=True)
    account_type = Column(String(32), nullable=False, default="real")
    currency = Column(String(16), nullable=False, default="USD")
    currency_digits = Column(Integer, nullable=False, default=2)

    # Leverage. NULL or 0 means "inherit from the group"; Account.effective_leverage()
    # resolves account -> group -> 100 in that order.
    leverage = Column(Integer, nullable=True)

    # Financial state
    balance = Column(NUMERIC, nullable=False, default=0)
    credit = Column(NUMERIC, nullable=False, default=0)
    equity = Column(NUMERIC, nullable=False, default=0)
    margin_used = Column(NUMERIC, nullable=False, default=0)
    margin_free = Column(NUMERIC, nullable=False, default=0)
    # PERCENT, matching MT5 and the rest of the schema after M1.
    margin_level = Column(Numeric(12, 4), nullable=False, default=0)
    profit = Column(NUMERIC, nullable=False, default=0)
    storage = Column(NUMERIC, nullable=False, default=0)
    commission = Column(NUMERIC, nullable=False, default=0)

    # Stop-out state machine. Persisting these is what makes the machine survive a
    # restart and stop re-firing MarginCallEntered on every tick.
    so_activation = Column(Integer, nullable=False, default=0)
    so_time = Column(DateTime(timezone=True), nullable=True)
    so_level = Column(Numeric(12, 4), nullable=True)
    so_equity = Column(NUMERIC, nullable=True)
    so_margin = Column(NUMERIC, nullable=True)

    # Status & dealer workflow
    is_enabled = Column(Boolean, nullable=False, default=True)
    is_online = Column(Boolean, nullable=False, default=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    # MT5's dealer colour tag is a free-form label, and the domain types it
    # Optional[str], so it is a nullable string rather than an integer.
    color_tag = Column(String(32), nullable=True)
    dealer_notes = Column(Text, nullable=True)
    registration_date = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    mt5_extra = Column(JSONB, nullable=False, default=dict)

    __table_args__ = (
        Index("idx_accounts_group", "group_name"),
        Index("idx_accounts_client", "client_id"),
        Index("idx_accounts_type", "account_type"),
    )


# ---------------------------------------------------------------------------
# Account
# ---------------------------------------------------------------------------


def _money(value: Any, currency: str) -> Money:
    if isinstance(value, Money):
        return value
    return Money(Decimal(str(value or 0)), currency)


def account_to_db(account: Account) -> AccountModel:
    """Map the domain Account onto the MT5-aligned row. Loses nothing."""
    group_name = ""
    group_id = account.group_id
    if account.group is not None:
        group_name = account.group.name or ""
        group_id = group_id or account.group.id
    if not group_name:
        raise ValueError(
            f"account {account.login} has no group; groups.name is a NOT NULL foreign "
            "key, so an account cannot be persisted without one"
        )

    return AccountModel(
        login=str(account.login),
        client_id=account.client_id or None,
        group_name=group_name,
        group_id=group_id,
        account_type=(
            account.account_type.value
            if hasattr(account.account_type, "value")
            else str(account.account_type)
        ),
        currency=account.currency or account.balance.currency,
        currency_digits=_int(account.currency_digits, 2),
        leverage=account.leverage,
        balance=account.balance.amount,
        credit=account.credit.amount,
        equity=account.equity.amount,
        margin_used=account.margin_used.amount,
        margin_free=account.margin_free.amount,
        margin_level=account.margin_level,
        profit=account.profit.amount,
        storage=account.storage.amount if isinstance(account.storage, Money) else Decimal(0),
        commission=account.commission.amount
        if isinstance(account.commission, Money)
        else Decimal(0),
        so_activation=int(_so_activation_value(account.so_activation)),
        so_time=account.so_time,
        so_level=account.so_level,
        so_equity=account.so_equity.amount if isinstance(account.so_equity, Money) else None,
        so_margin=account.so_margin.amount if isinstance(account.so_margin, Money) else None,
        # storage and commission are Money on the domain, never None.
        is_enabled=bool(account.is_enabled),
        is_online=bool(account.is_online),
        last_login=account.last_login,
        color_tag=account.color_tag,
        dealer_notes=account.dealer_notes or None,
        registration_date=account.registration_date,
        created_at=account.created_at,
        updated_at=account.updated_at,
    )


def db_to_account(model: AccountModel, group: Any = None) -> Account:
    """Map a row back onto the domain Account, restoring the stop-out state machine."""
    if model is None:
        return None

    currency = model.currency or "USD"
    account = Account(
        login=model.login,
        client_id=model.client_id or "",
        group_id=model.group_id or "",
        group=group,
        account_type=_enum(AccountType, model.account_type, AccountType.REAL),
        currency=currency,
        currency_digits=_int(model.currency_digits, 2),
        leverage=model.leverage,
        balance=_money(model.balance, currency),
        credit=_money(model.credit, currency),
        equity=_money(model.equity, currency),
        margin_used=_money(model.margin_used, currency),
        margin_free=_money(model.margin_free, currency),
        profit=_money(model.profit, currency),
        storage=_money(model.storage, currency),
        commission=_money(model.commission, currency),
        is_enabled=bool(model.is_enabled),
        is_online=bool(model.is_online),
        last_login=model.last_login,
        color_tag=model.color_tag,
        dealer_notes=model.dealer_notes or "",
        registration_date=model.registration_date,
        created_at=model.created_at or datetime.now(timezone.utc),
        updated_at=model.updated_at or datetime.now(timezone.utc),
    )
    account.margin_level = _dec(model.margin_level, "0")
    account.so_activation = _so_activation_from_int(_int(model.so_activation, 0))
    account.so_time = model.so_time
    # These three are Optional on the domain and None means "no stop-out has happened
    # yet". Preserving None matters: a zero would read as a real snapshot of an account
    # that stopped out at equity 0.
    account.so_level = model.so_level
    account.so_equity = _money(model.so_equity, currency) if model.so_equity is not None else None
    account.so_margin = _money(model.so_margin, currency) if model.so_margin is not None else None
    return account


def _so_activation_value(value: Any) -> int:
    if isinstance(value, SOActivation):
        return int(value.value)
    return _int(value, 0)


def _so_activation_from_int(raw: int) -> SOActivation:
    for member in SOActivation:
        if int(member.value) == raw:
            return member
    return SOActivation.NONE


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


def client_to_db(client: Client):
    from .manager_models import ClientModel

    return ClientModel(
        id=client.id,
        client_id=client.client_id or None,
        mqid=client.mqid or "",
        full_name=client.full_name or "",
        company=client.company or "",
        country=client.country or "",
        city=client.city or "",
        zip_code=client.zip_code or "",
        address=client.address or "",
        phone=client.phone or "",
        email=client.email or "",
        language=client.language or "en",
        password_hash=client.password_hash or "",
        investor_password_hash=client.investor_password_hash or "",
        phone_password_hash=getattr(client, "phone_password_hash", "") or "",
        otp_secret=getattr(client, "otp_secret", None),
        certificate_fingerprint=getattr(client, "certificate_fingerprint", None),
        # ClientStatus is an int scale in MT5 (0/100/200/300/...), so store the value.
        status=int(client.status.value if hasattr(client.status, "value") else client.status or 0),
        external_id=getattr(client, "external_id", None),
        agent_login=getattr(client, "agent_login", None),
        comments=getattr(client, "comments", "") or "",
        registration_date=getattr(client, "registration_date", None),
        last_visit=getattr(client, "last_visit", None),
        last_pass_change=getattr(client, "last_pass_change", None),
        created_at=client.created_at,
        updated_at=client.updated_at,
    )


def db_to_client(model) -> Client:
    if model is None:
        return None
    return Client(
        id=model.id,
        client_id=model.client_id or "",
        mqid=model.mqid or "",
        full_name=model.full_name or "",
        company=model.company or "",
        country=model.country or "",
        city=model.city or "",
        zip_code=model.zip_code or "",
        address=model.address or "",
        phone=model.phone or "",
        email=model.email or "",
        language=model.language or "en",
        password_hash=model.password_hash or "",
        investor_password_hash=model.investor_password_hash or "",
        phone_password_hash=model.phone_password_hash or "",
        otp_secret=model.otp_secret,
        certificate_fingerprint=model.certificate_fingerprint,
        status=_enum(ClientStatus, model.status, ClientStatus.UNREGISTERED),
        external_id=model.external_id or "",
        agent_login=model.agent_login,
        comments=model.comments or "",
        registration_date=model.registration_date,
        last_visit=model.last_visit,
        last_pass_change=model.last_pass_change,
        created_at=model.created_at or datetime.now(timezone.utc),
        updated_at=model.updated_at or datetime.now(timezone.utc),
    )


# ---------------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------------


#: Rights per mask word. 128 does not divide evenly by a signed-64-bit-safe width, so
#: three words of 43 bits cover 0..128. A BigInteger column is 64-bit SIGNED, meaning
#: bit 63 is the sign bit: two words would leave 65 rights to fit in 63 bits, and
#: SQLite rejects the oversized value outright while PostgreSQL stores a negative
#: number. Three words keeps every mask well inside range on both.
RIGHTS_BITS_PER_WORD = 43
RIGHTS_WORDS = 3


def rights_to_masks(rights: List[Any]) -> List[int]:
    """Pack MT5's 128-position rights array into signed-64-bit-safe masks."""
    masks = [0] * RIGHTS_WORDS
    for index, value in enumerate(rights or []):
        if index >= MT5_RIGHTS_COUNT:
            break
        if str(value).strip() not in ("1", "true", "True"):
            continue
        word, bit = divmod(index, RIGHTS_BITS_PER_WORD)
        if word < RIGHTS_WORDS:
            masks[word] |= 1 << bit
    return masks


def masks_to_rights(masks: List[int]) -> List[str]:
    """Inverse of :func:`rights_to_masks`, in MT5's wire form (strings "0"/"1")."""
    out: List[str] = []
    for index in range(MT5_RIGHTS_COUNT):
        word, bit = divmod(index, RIGHTS_BITS_PER_WORD)
        value = masks[word] if word < len(masks) else 0
        out.append("1" if (value >> bit) & 1 else "0")
    return out


# Backwards-compatible two-argument names, kept because the round-trip test and any
# caller written against the first draft use them.
def rights_to_mask(rights: List[Any]) -> "tuple[int, int]":
    masks = rights_to_masks(rights)
    return masks[0], masks[1]


def mask_to_rights(lo: int, hi: int) -> List[str]:
    return masks_to_rights([lo, hi, 0])


def manager_to_db(manager: ManagerAccount, *, mt5_extra: Optional[Dict[str, Any]] = None,
                  mt5_source: Optional[Dict[str, Any]] = None):
    from .manager_models import ManagerModel

    rights = list(getattr(manager, "rights", None) or [])
    if not rights:
        # Derive the array from the role when a manager was created natively rather
        # than imported. An administrator gets every right, which is what MT5's own
        # auto-created login 1000 looks like.
        rights = ["1" if manager.role is ManagerRole.SUPER_ADMIN else "0"] * MT5_RIGHTS_COUNT
    masks = rights_to_masks(rights)

    return ManagerModel(
        login=_int(manager.login, 0),
        name=getattr(manager, "name", "") or "",
        mailbox=getattr(manager, "mailbox", "") or "",
        server_id=_int(getattr(manager, "server_id", 1), 1),
        rights_json=_json_safe(rights),
        rights_mask_0=masks[0],
        rights_mask_1=masks[1],
        rights_mask_2=masks[2],
        group_scope_json=_json_safe(list(getattr(manager, "group_scope", None) or [{"Group": "*"}])),
        request_limit_logs=_int(getattr(manager, "request_limit_logs", 0), 0),
        request_limit_reports=_int(getattr(manager, "request_limit_reports", 0), 0),
        role=manager.role.value if hasattr(manager.role, "value") else str(manager.role),
        password_hash=manager.password_hash or "",
        totp_secret=manager.totp_secret,
        is_2fa_enabled=bool(manager.is_2fa_enabled),
        must_change_password=bool(getattr(manager, "must_change_password", False)),
        allowed_ips_json=_json_safe(list(manager.allowed_ips or [])),
        certificate_fingerprint=manager.certificate_fingerprint,
        is_active=bool(manager.is_active),
        last_login=manager.last_login,
        created_at=manager.created_at,
        mt5_extra=_json_safe(dict(mt5_extra or {})),
        mt5_source=_json_safe(dict(mt5_source)) if mt5_source else None,
    )


def db_to_manager(model) -> ManagerAccount:
    if model is None:
        return None
    manager = ManagerAccount(
        manager_id=str(model.login),
        login=str(model.login),
        role=_enum(ManagerRole, model.role, ManagerRole.READ_ONLY),
        password_hash=model.password_hash or "",
        totp_secret=model.totp_secret,
        is_2fa_enabled=bool(model.is_2fa_enabled),
        allowed_ips=list(model.allowed_ips_json or []),
        certificate_fingerprint=model.certificate_fingerprint,
        is_active=bool(model.is_active),
        last_login=model.last_login,
        created_at=model.created_at or datetime.now(timezone.utc),
    )
    # MT5-side fields the domain dataclass does not declare yet. Attached rather than
    # dropped so an export can reproduce the record.
    manager.name = model.name or ""
    manager.mailbox = model.mailbox or ""
    manager.server_id = _int(model.server_id, 1)
    manager.rights = list(model.rights_json or [])
    manager.group_scope = list(model.group_scope_json or [])
    manager.request_limit_logs = _int(model.request_limit_logs, 0)
    manager.request_limit_reports = _int(model.request_limit_reports, 0)
    manager.must_change_password = bool(model.must_change_password)
    return manager


def manager_mt5_record(row) -> Dict[str, Any]:
    """Rebuild the MT5 ConfigManagers wire record for a stored manager."""
    baseline = row.mt5_source if isinstance(row.mt5_source, dict) else None
    record: Dict[str, Any] = dict(baseline) if baseline else {}
    owned = {
        "Login": str(_int(row.login, 0)),
        "Name": row.name or "",
        "Mailbox": row.mailbox or "",
        "Server": str(_int(row.server_id, 1)),
        "Rights": list(
            row.rights_json
            or masks_to_rights(
                [
                    _int(row.rights_mask_0, 0),
                    _int(row.rights_mask_1, 0),
                    _int(row.rights_mask_2, 0),
                ]
            )
        ),
        "RequestLimitLogs": str(_int(row.request_limit_logs, 0)),
        "RequestLimitReports": str(_int(row.request_limit_reports, 0)),
        "Groups": list(row.group_scope_json or []),
    }
    if baseline:
        owned = {k: v for k, v in owned.items() if k in {f.mt5 for f in MANAGER_FIELDS}}
    record.update(owned)
    for key, value in (row.mt5_extra or {}).items():
        record.setdefault(key, value)
    return record


# ---------------------------------------------------------------------------
# Shared coercion helpers
# ---------------------------------------------------------------------------


def _json_safe(value: Any) -> Any:
    """Recursively make a structure storable in a JSONB column.

    Decimals become strings - which is also MT5's own wire representation, so a stored
    value re-exports byte-identically instead of coming back as a rounded float.
    """
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    return str(value)


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _dec(value: Any, default: str = "0") -> Decimal:
    if value is None:
        return Decimal(default)
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _enum(enum_cls: Any, raw: Any, fallback: Any) -> Any:
    if raw is None:
        return fallback
    try:
        return enum_cls(raw)
    except ValueError:
        try:
            return enum_cls(int(raw))
        except (ValueError, TypeError):
            return fallback
