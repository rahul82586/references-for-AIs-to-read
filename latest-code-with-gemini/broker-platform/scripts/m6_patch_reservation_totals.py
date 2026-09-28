"""M6 patch 2: reservation totals contract + SQLite JSONB hook + test fixes.

Bug found by the new concurrency test: the reserve helper ADDED the amount to
the in-flight account object after the repository method had already mutated
the same object (in-memory doubles store the domain object itself) — every
reservation double-counted. The contract is now: repository methods OWN the
stored state and RETURN the new margin_reserved total; helpers SET the
in-flight object from that total (identity-safe for doubles, staleness-safe
for SQL). reserve_margin returns None when refused; release_margin returns the
new total (None when the account row is gone).

Also: the JSONB->JSON SQLite compile hook moves from the M4 proof script into
infrastructure/persistence/database.py, so ANY sqlite create_all works —
tests included — without importing proof-script magic.
"""
import ast
import io
import pathlib


def read(path):
    p = pathlib.Path(path)
    src = io.open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in src else "\n"
    return src, nl


def write(path, src, nl):
    ast.parse(src.replace("\r\n", "\n") if nl == "\r\n" else src)
    io.open(path, "w", encoding="utf-8", newline="").write(src)


def apply(path, pairs):
    src, nl = read(path)
    for old, new in pairs:
        if nl == "\r\n":
            old = old.replace("\n", "\r\n")
            new = new.replace("\n", "\r\n")
        assert src.count(old) == 1, f"{path}: anchor {src.count(old)}x: {old[:70]!r}"
        src = src.replace(old, new)
    write(path, src, nl)
    print(f"{path}: {len(pairs)} patch(es)")


# --- 1. SQLite JSONB hook, permanently --------------------------------------
apply("infrastructure/persistence/database.py", [(
    "from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession\n",
    """from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# JSONB renders as JSON on SQLite so create_all works against the development
# and test database; PostgreSQL keeps the native type. This used to live inside
# the M4 proof script, which meant any OTHER sqlite consumer (tests, a fresh
# `create_tables()` call) died with "can't render element of type JSONB".
from sqlalchemy.dialects.postgresql import JSONB as _PG_JSONB
from sqlalchemy.ext.compiler import compiles as _sa_compiles


@_sa_compiles(_PG_JSONB, "sqlite")
def _compile_jsonb_sqlite(type_, compiler, **kw):  # noqa: ANN001
    return "JSON"
""",
)])

# --- 2. SQL repository: RETURNING the new total ------------------------------
apply("infrastructure/persistence/repositories/account_repository.py", [
    (
        '''    async def reserve_margin(self, login_id: Any, amount: Any, session: Optional[AsyncSession] = None) -> bool:
        """One conditional UPDATE: hold `amount` only while free margin covers it.

        free = balance + credit + profit - margin_used - margin_reserved. Two
        concurrent reservations cannot both succeed: the database serialises
        the row updates and the loser's WHERE no longer matches (rowcount 0).
        """
        from decimal import Decimal as _D

        from sqlalchemy import text as sa_text

        stmt = sa_text(
            "UPDATE accounts SET margin_reserved = margin_reserved + :amt "
            "WHERE login = :login AND "
            "(balance + credit + profit - margin_used - margin_reserved) >= :amt"
        )
        params = {"amt": _D(str(amount)), "login": str(login_id)}
        if session is not None:
            result = await session.execute(stmt, params)
        else:
            async with self.session_factory() as sess:
                result = await sess.execute(stmt, params)
                await sess.commit()
        return (result.rowcount or 0) == 1
''',
        '''    async def reserve_margin(self, login_id: Any, amount: Any, session: Optional[AsyncSession] = None):
        """One conditional UPDATE: hold `amount` only while free margin covers it.

        free = balance + credit + profit - margin_used - margin_reserved. Two
        concurrent reservations cannot both succeed: the database serialises
        the row updates and the loser's WHERE no longer matches (no row
        returned). Returns the NEW margin_reserved total, or None when refused.
        """
        from decimal import Decimal as _D

        from sqlalchemy import text as sa_text

        stmt = sa_text(
            "UPDATE accounts SET margin_reserved = margin_reserved + :amt "
            "WHERE login = :login AND "
            "(balance + credit + profit - margin_used - margin_reserved) >= :amt "
            "RETURNING margin_reserved"
        )
        params = {"amt": _D(str(amount)), "login": str(login_id)}
        if session is not None:
            row = (await session.execute(stmt, params)).first()
        else:
            async with self.session_factory() as sess:
                row = (await sess.execute(stmt, params)).first()
                await sess.commit()
        return None if row is None else _D(str(row[0]))
''',
    ),
    (
        '''    async def release_margin(self, login_id: Any, amount: Any, session: Optional[AsyncSession] = None) -> None:
        """Release a hold, clamped at zero (a double release must not go negative)."""
        from decimal import Decimal as _D

        from sqlalchemy import text as sa_text

        stmt = sa_text(
            "UPDATE accounts SET margin_reserved = "
            "CASE WHEN margin_reserved >= :amt THEN margin_reserved - :amt ELSE 0 END "
            "WHERE login = :login"
        )
        params = {"amt": _D(str(amount)), "login": str(login_id)}
        if session is not None:
            await session.execute(stmt, params)
        else:
            async with self.session_factory() as sess:
                await sess.execute(stmt, params)
                await sess.commit()
''',
        '''    async def release_margin(self, login_id: Any, amount: Any, session: Optional[AsyncSession] = None):
        """Release a hold, clamped at zero (a double release must not go
        negative). Returns the NEW margin_reserved total, or None when the
        account row does not exist."""
        from decimal import Decimal as _D

        from sqlalchemy import text as sa_text

        stmt = sa_text(
            "UPDATE accounts SET margin_reserved = "
            "CASE WHEN margin_reserved >= :amt THEN margin_reserved - :amt ELSE 0 END "
            "WHERE login = :login RETURNING margin_reserved"
        )
        params = {"amt": _D(str(amount)), "login": str(login_id)}
        if session is not None:
            row = (await session.execute(stmt, params)).first()
        else:
            async with self.session_factory() as sess:
                row = (await sess.execute(stmt, params)).first()
                await sess.commit()
        return None if row is None else _D(str(row[0]))
''',
    ),
])

# --- 3. In-memory double: same contract --------------------------------------
apply("tests/integration/trading_harness.py", [
    (
        '''    async def reserve_margin(self, login_id: Any, amount: Any, session: Any = None) -> bool:
        """Mirrors SqlAccountRepository.reserve_margin: hold only while
        balance + credit + profit - margin_used - margin_reserved covers it."""
        account = self.accounts.get(login_id)
        if account is None:
            try:
                account = self.accounts.get(int(login_id))
            except (TypeError, ValueError):
                account = None
        if account is None:
            return False
        amount = Decimal(str(amount))
        free = (
            account.balance.amount
            + account.credit.amount
            + account.profit.amount
            - account.margin_used.amount
            - account.margin_reserved.amount
        )
        if free < amount:
            return False
        account.margin_reserved = Money(account.margin_reserved.amount + amount, account.currency)
        return True

    async def release_margin(self, login_id: Any, amount: Any, session: Any = None) -> None:
        account = self.accounts.get(login_id)
        if account is None:
            try:
                account = self.accounts.get(int(login_id))
            except (TypeError, ValueError):
                account = None
        if account is None:
            return
        amount = Decimal(str(amount))
        account.margin_reserved = Money(
            max(Decimal("0"), account.margin_reserved.amount - amount), account.currency
        )
''',
        '''    async def reserve_margin(self, login_id: Any, amount: Any, session: Any = None):
        """Mirrors SqlAccountRepository.reserve_margin: hold only while
        balance + credit + profit - margin_used - margin_reserved covers it.
        Returns the NEW total, or None when refused (the repository owns the
        stored state; the caller's helper syncs from the returned total)."""
        account = self.accounts.get(login_id)
        if account is None:
            try:
                account = self.accounts.get(int(login_id))
            except (TypeError, ValueError):
                account = None
        if account is None:
            return None
        amount = Decimal(str(amount))
        free = (
            account.balance.amount
            + account.credit.amount
            + account.profit.amount
            - account.margin_used.amount
            - account.margin_reserved.amount
        )
        if free < amount:
            return None
        account.margin_reserved = Money(account.margin_reserved.amount + amount, account.currency)
        return account.margin_reserved.amount

    async def release_margin(self, login_id: Any, amount: Any, session: Any = None):
        account = self.accounts.get(login_id)
        if account is None:
            try:
                account = self.accounts.get(int(login_id))
            except (TypeError, ValueError):
                account = None
        if account is None:
            return None
        amount = Decimal(str(amount))
        account.margin_reserved = Money(
            max(Decimal("0"), account.margin_reserved.amount - amount), account.currency
        )
        return account.margin_reserved.amount
''',
    ),
])

# --- 4. Port docstrings: the contract ----------------------------------------
apply("core/ports/interfaces.py", [(
    '''    async def reserve_margin(self, login_id: Any, amount: Any) -> bool:
        """Atomically hold `amount` of free margin for an in-flight order (M6).

        Returns False when the account no longer covers it. MUST be a single
        conditional UPDATE in SQL implementations, so two nodes racing the same
        account cannot both win. The base declaration raises NotImplementedError:
        callers (application.services.margin_reservation) fall back to the
        per-account-locked in-process path and log that they did.
        """
        raise NotImplementedError

    async def release_margin(self, login_id: Any, amount: Any) -> None:
        """Release a hold placed by reserve_margin (fill or rejection)."""
        raise NotImplementedError
''',
    '''    async def reserve_margin(self, login_id: Any, amount: Any):
        """Atomically hold `amount` of free margin for an in-flight order (M6).

        Returns the NEW margin_reserved total, or None when the account no
        longer covers the amount. MUST be a single conditional UPDATE in SQL
        implementations, so two nodes racing the same account cannot both win.
        The base declaration raises NotImplementedError: callers
        (application.services.margin_reservation) fall back to the
        per-account-locked in-process path and log that they did.
        """
        raise NotImplementedError

    async def release_margin(self, login_id: Any, amount: Any):
        """Release a hold placed by reserve_margin (fill or rejection).

        Returns the NEW margin_reserved total (clamped at zero), or None when
        the account does not exist.
        """
        raise NotImplementedError
''',
)])

print("contract patches applied")
