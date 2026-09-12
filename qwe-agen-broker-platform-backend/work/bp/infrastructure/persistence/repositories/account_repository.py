from typing import Any, Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.domains.accounts.models import Account, Group
from core.ports.interfaces import IAccountRepository, IGroupRepository
# SqlGroupRepository lives in group_repository.py. It used to be defined
# here as well, and the two copies drifted.
from .group_repository import SqlGroupRepository  # noqa: F401
from infrastructure.persistence.db_models import AccountModel, GroupModel
from infrastructure.persistence.mappers import account_to_db, db_to_account, group_to_db, db_to_group


class SqlAccountRepository(IAccountRepository):
    """PostgreSQL implementation of IAccountRepository."""

    def __init__(self, session_factory=None, group_repo: Optional[IGroupRepository] = None):
        self.session_factory = session_factory
        self.group_repo = group_repo

    async def find_by_login(self, login_id: Any, session: Optional[AsyncSession] = None) -> Optional[Account]:
        # accounts.login is String(32) - MT5's natural key - but the rest of the platform
        # identifies an account with an int: Order.account_login, Position.account_login,
        # Deal.account_login and their BigInteger columns all are. Every caller on the
        # execution path therefore arrives with an int, and `session.get(AccountModel, 900101)`
        # binds an INTEGER against a TEXT primary key: SQLite compares the two as
        # different types and finds nothing, PostgreSQL raises "operator does not exist:
        # character varying = integer". Coercing here keeps the string key where it
        # belongs - at the storage boundary - instead of leaking into the domain.
        login_id = str(login_id)

        if session is not None:
            model = await session.get(AccountModel, login_id)
            if not model:
                return None
            group = await self.group_repo.find_by_name(model.group_name) if self.group_repo else None
            return db_to_account(model, group)

        async with self.session_factory() as sess:
            model = await sess.get(AccountModel, login_id)
            if not model:
                return None
            group = await self.group_repo.find_by_name(model.group_name) if self.group_repo else None
            return db_to_account(model, group)

    async def reserve_margin(self, login_id: Any, amount: Any, session: Optional[AsyncSession] = None):
        """One conditional UPDATE: hold `amount` only while free margin covers it.

        free = balance + credit + profit - margin_used - margin_reserved. Two
        concurrent reservations cannot both succeed: the database serialises
        the row updates and the loser's WHERE no longer matches (no row
        returned). Returns the NEW margin_reserved total, or None when refused.
        """
        from decimal import Decimal as _D

        from sqlalchemy import text as sa_text

        stmt = sa_text(
            "UPDATE accounts SET margin_reserved = margin_reserved + CAST(:amt AS DECIMAL(20,8)) "
            "WHERE login = :login AND "
            "(balance + credit + profit - margin_used - margin_reserved) "
            ">= CAST(:amt AS DECIMAL(20,8)) "
            "RETURNING margin_reserved"
        )
        params = {"amt": str(_D(str(amount))), "login": str(login_id)}
        if session is not None:
            row = (await session.execute(stmt, params)).first()
        else:
            async with self.session_factory() as sess:
                row = (await sess.execute(stmt, params)).first()
                await sess.commit()
        return None if row is None else _D(str(row[0]))

    async def release_margin(self, login_id: Any, amount: Any, session: Optional[AsyncSession] = None):
        """Release a hold, clamped at zero (a double release must not go
        negative). Returns the NEW margin_reserved total, or None when the
        account row does not exist."""
        from decimal import Decimal as _D

        from sqlalchemy import text as sa_text

        stmt = sa_text(
            "UPDATE accounts SET margin_reserved = "
            "CASE WHEN margin_reserved >= CAST(:amt AS DECIMAL(20,8)) "
            "THEN margin_reserved - CAST(:amt AS DECIMAL(20,8)) ELSE 0 END "
            "WHERE login = :login RETURNING margin_reserved"
        )
        params = {"amt": str(_D(str(amount))), "login": str(login_id)}
        if session is not None:
            row = (await session.execute(stmt, params)).first()
        else:
            async with self.session_factory() as sess:
                row = (await sess.execute(stmt, params)).first()
                await sess.commit()
        return None if row is None else _D(str(row[0]))

    async def save(self, account: Account, session: Optional[AsyncSession] = None) -> Account:
        model = account_to_db(account)
        if session is not None:
            await session.merge(model)
            return account
        async with self.session_factory() as sess:
            await sess.merge(model)
            await sess.commit()
            return account

    async def update_valuation(self, account: Account, session: Optional[AsyncSession] = None,
                               include_margin: bool = False):
        """D8b: persist ONLY the tick pipeline's own columns.

        `save()` is a full-row merge. TickMarginPipeline used to call it on every
        tick with an account object loaded before the current pass, so a fill that
        landed in between had its `margin_used` overwritten by the stale snapshot -
        observed live as margin_used=0 and margin_level=999999 on an account
        holding an open position, which also disables the stop-out machine.

        This writes profit / equity / margin_free / margin_level and the five so_*
        stop-out fields, all of which the pipeline recomputes from a fresh position
        read, and deliberately NOT balance, margin_used or margin_reserved, which
        belong to record_deal and the reservation path. Disjoint write sets, so the
        two paths cannot lose each other's updates.

        `include_margin=True` adds margin_used to the write. It exists for exactly
        one caller: the valuation sweep repairing an account that holds open
        positions with margin_used = 0, which no legitimate state produces and
        which otherwise leaves the account under-margined and pinned at the 999999
        sentinel where stop-out can never fire. The ordinary tick path must not
        pass it - that is the D8b lost update.

        Returns the number of rows written (0 means the account vanished).
        """
        from datetime import datetime as _dt, timezone as _tz

        from sqlalchemy import text as sa_text

        margin_col = "margin_used = CAST(:margin_used AS DECIMAL(20,8)), " if include_margin else ""
        stmt = sa_text(
            "UPDATE accounts SET "
            + margin_col +
            "profit = CAST(:profit AS DECIMAL(20,8)), "
            "equity = CAST(:equity AS DECIMAL(20,8)), "
            "margin_free = CAST(:margin_free AS DECIMAL(20,8)), "
            "margin_level = CAST(:margin_level AS DECIMAL(20,8)), "
            "so_activation = :so_activation, "
            "so_time = :so_time, "
            "so_level = :so_level, "
            "so_equity = :so_equity, "
            "so_margin = :so_margin, "
            "updated_at = :updated_at "
            "WHERE login = :login"
        )

        def _amt(value) -> str:
            return str(getattr(value, "amount", value) or 0)

        so_act = account.so_activation
        params = {
            "margin_used": _amt(account.margin_used),
            "profit": _amt(account.profit),
            "equity": _amt(account.equity),
            "margin_free": _amt(account.margin_free),
            # margin_level is derived state (D1): write the value the domain
            # computed, and never let a stale 0 reach the column.
            "margin_level": str(account.margin_level or 0),
            "so_activation": int(getattr(so_act, "value", so_act or 0)),
            "so_time": account.so_time,
            "so_level": (None if account.so_level is None else str(account.so_level)),
            "so_equity": (None if account.so_equity is None else _amt(account.so_equity)),
            "so_margin": (None if account.so_margin is None else _amt(account.so_margin)),
            "updated_at": _dt.now(_tz.utc),
            "login": str(account.login),
        }
        if session is not None:
            result = await session.execute(stmt, params)
            return result.rowcount or 0
        async with self.session_factory() as sess:
            result = await sess.execute(stmt, params)
            await sess.commit()
            return result.rowcount or 0

    async def mark_valued(self, login_id: Any, when) -> bool:
        """D9: stamp when this account was last revalued.

        Its own statement rather than a field on save(), so a valuation sweep can
        record "I looked at this account at T" without touching balance, margin or
        the reservation - the write sets stay disjoint (D8b).
        """
        from sqlalchemy import text as sa_text

        stmt = sa_text(
            "UPDATE accounts SET last_valuation_at = :when WHERE login = :login"
        )
        params = {"when": when, "login": str(login_id)}
        async with self.session_factory() as sess:
            result = await sess.execute(stmt, params)
            await sess.commit()
            return bool(result.rowcount)

    async def get_all_accounts(self) -> List[Account]:
        async with self.session_factory() as session:
            result = await session.execute(select(AccountModel))
            models = result.scalars().all()
            accounts = []
            for model in models:
                group = await self.group_repo.find_by_name(model.group_name)
                accounts.append(db_to_account(model, group))
            return accounts

    async def get_all_with_positions(self) -> List[str]:
        """Return login IDs of all accounts that have open positions."""
        from infrastructure.persistence.db_models import PositionModel
        async with self.session_factory() as session:
            result = await session.execute(
                select(PositionModel.account_login).distinct()
            )
            return [row[0] for row in result.fetchall()]
    async def find_all(self):
        """Every account. ConfigCache loads this once at startup."""
        async with self.session_factory() as session:
            result = await session.execute(select(AccountModel))
            models = result.scalars().all()
            out = []
            for model in models:
                group = None
                if self.group_repo is not None and model.group_name:
                    group = await self.group_repo.find_by_name(model.group_name)
                out.append(db_to_account(model, group))
            return out

    async def save_model(self, model) -> None:
        """Persist an AccountModel row directly."""
        async with self.session_factory() as session:
            await session.merge(model)
            await session.commit()
