"""
SQLAlchemy model for the Manager / Administrator plane (MT5 ConfigManagers).

MT5 has no role enum. A manager's permissions are a FIXED-LENGTH 128-element array of
"0"/"1" strings, positionally indexed, plus a Groups scope array saying which client
groups the manager may administer. In the reference export all 9 managers have all 128
rights set, which is what an auto-created administrator looks like; a dealer or an
API-only manager would have most positions "0".

We store the bitmask as a single BigInteger pair rather than 128 columns, because MT5
itself treats it as an opaque positional array and we do not yet have the SDK's
right-index meanings. ``rights_json`` keeps the array form so an MT5 export reproduces
it exactly; ``rights_mask_lo`` / ``rights_mask_hi`` make individual rights queryable
in SQL without unpacking JSON.

The MT5 rule this model exists to enforce: a manager only administers accounts on the
trade server where its own account lives, and only within its Groups scope.
"""

from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB

from .database import Base

#: Number of rights in MT5's manager rights array.
MT5_RIGHTS_COUNT = 128


class ManagerModel(Base):
    """MT5 ConfigManagers record."""

    __tablename__ = "managers"

    # MT5 Login. Manager logins in the reference export are 1000, 2000, 3000, 19226,
    # 208011, 400034 ... so this is an integer, not a string.
    login = Column(BigInteger, primary_key=True, autoincrement=False)
    name = Column(String(256), nullable=False, default="")
    mailbox = Column(String(256), nullable=False, default="")
    server_id = Column(Integer, nullable=False, default=1)

    # The 128-position rights array, stored both ways. See the module docstring.
    # THREE masks of 43 bits, not two of 64: a BigInteger column is 64-bit SIGNED, so
    # bit 63 is the sign bit, and 128 - 63 = 65 rights will not fit in the remainder.
    # Splitting at 43 keeps every mask comfortably inside range on PostgreSQL and
    # SQLite alike (SQLite rejects an oversized int outright rather than wrapping).
    rights_json = Column(JSONB, nullable=False, default=list)
    rights_mask_0 = Column(BigInteger, nullable=False, default=0)  # rights 0..42
    rights_mask_1 = Column(BigInteger, nullable=False, default=0)  # rights 43..85
    rights_mask_2 = Column(BigInteger, nullable=False, default=0)  # rights 86..127

    # Which client groups this manager may administer. [{"Group": "*"}] means all.
    group_scope_json = Column(JSONB, nullable=False, default=list)

    request_limit_logs = Column(Integer, nullable=False, default=0)
    request_limit_reports = Column(Integer, nullable=False, default=0)

    # Our own additions, which MT5 does not carry in ConfigManagers.
    role = Column(String(32), nullable=False, default="READ_ONLY")
    password_hash = Column(String(512), nullable=False, default="")
    totp_secret = Column(String(64), nullable=True)
    is_2fa_enabled = Column(Boolean, nullable=False, default=False)
    # MT5 forces a password change on first connect for an auto-created administrator.
    # We do the same for a bootstrapped one.
    must_change_password = Column(Boolean, nullable=False, default=False)
    allowed_ips_json = Column(JSONB, nullable=False, default=list)
    certificate_fingerprint = Column(String(128), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # MT5 fields we do not model yet, preserved so an export stays lossless.
    mt5_extra = Column(JSONB, nullable=False, default=dict)
    mt5_source = Column(JSONB, nullable=True)


class ClientModel(Base):
    """MT5 IMTUser - the person or company, distinct from their trading accounts.

    One Client owns many Accounts. MT5 keeps KYC/personal data here and the financial
    state on the account, and so do we.
    """

    __tablename__ = "clients"

    id = Column(String(64), primary_key=True)
    client_id = Column(String(64), nullable=True, index=True)  # external KYC id
    mqid = Column(String(64), nullable=False, default="")

    full_name = Column(String(256), nullable=False, default="")
    company = Column(String(256), nullable=False, default="")
    country = Column(String(64), nullable=False, default="")
    city = Column(String(128), nullable=False, default="")
    zip_code = Column(String(32), nullable=False, default="")
    address = Column(Text, nullable=False, default="")
    phone = Column(String(64), nullable=False, default="")
    email = Column(String(256), nullable=False, default="")
    language = Column(String(16), nullable=False, default="en")

    password_hash = Column(String(512), nullable=False, default="")
    investor_password_hash = Column(String(512), nullable=False, default="")
    phone_password_hash = Column(String(512), nullable=False, default="")
    otp_secret = Column(String(64), nullable=True)
    certificate_fingerprint = Column(String(128), nullable=True)

    # MT5 ClientStatus is an integer scale (0 unregistered, 100 registered, 200 funded,
    # 300 active, 400 inactive, 500 suspended, 600 closed), not a string.
    status = Column(Integer, nullable=False, default=0)

    external_id = Column(String(64), nullable=True, index=True)
    agent_login = Column(BigInteger, nullable=True)
    comments = Column(Text, nullable=False, default="")
    registration_date = Column(DateTime(timezone=True), nullable=True)
    last_visit = Column(DateTime(timezone=True), nullable=True)
    last_pass_change = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    mt5_extra = Column(JSONB, nullable=False, default=dict)
