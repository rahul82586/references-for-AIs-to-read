"""SQL implementations of the identity plane's two new ports.

``SqlLoginAllocatorStore`` is the storage half of MT5's "Next" button. The whole
point of it is that allocation is ONE statement:

    UPDATE login_counters
       SET next_login = next_login + 1, updated_at = <now>
     WHERE scope = ?
    RETURNING next_login - 1

The database both decides and records the answer, so two administrators creating
accounts concurrently get different logins. A Python-side read-then-write would
give them the same one - and with merge-based repositories the second save would
overwrite the first account rather than raise.

``SqlClientRepository`` is ``SqlClientRepository`` promoted out of
``manager_repository.py`` and given the ``IClientRepository`` port its own
docstring said it was waiting for. Without the port, ``CreateClientHandler``
could only be wired by reaching into a concrete class, which is how the DI
container accumulated providers nothing declared.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select, text

from core.domains.accounts.client import Client
from core.domains.accounts.login_allocator import LoginAllocatorStore
from core.ports.interfaces import IClientRepository

from ..identity_models import DEFAULT_LOGIN_SCOPE, LoginCounterModel
from ..account_models import db_to_client, client_to_db
from ..manager_models import ClientModel

logger = logging.getLogger(__name__)


class SqlLoginAllocatorStore(LoginAllocatorStore):
    """Race-safe login allocation over the ``login_counters`` table."""

    def __init__(self, session_factory) -> None:
        self.session_factory = session_factory

    async def ensure_scope(self, scope: str, login_floor: int) -> None:
        """Insert the scope's counter if absent. Never lowers an existing floor.

        ``ON CONFLICT DO NOTHING`` rather than an upsert-that-sets: a scope whose
        counter already exists must keep its position, or restarting the server
        with a different configured floor would hand out logins it has already
        handed out.
        """
        scope = scope or DEFAULT_LOGIN_SCOPE
        async with self.session_factory() as session:
            existing = await session.execute(
                select(LoginCounterModel).where(LoginCounterModel.scope == scope)
            )
            row = existing.scalar_one_or_none()
            if row is not None:
                # Raise the floor if the config asks for a higher one, but never
                # move next_login backwards.
                if login_floor and int(row.login_floor or 0) < int(login_floor):
                    row.login_floor = int(login_floor)
                    if int(row.next_login or 0) < int(login_floor):
                        row.next_login = int(login_floor)
                    row.updated_at = datetime.now(timezone.utc)
                    await session.commit()
                return
            session.add(
                LoginCounterModel(
                    scope=scope,
                    next_login=int(login_floor or 0),
                    login_floor=int(login_floor or 0),
                    updated_at=datetime.now(timezone.utc),
                )
            )
            await session.commit()

    async def take_next(self, scope: str) -> int:
        """Atomically reserve one login. See the module docstring for why."""
        scope = scope or DEFAULT_LOGIN_SCOPE
        stmt = text(
            "UPDATE login_counters "
            "SET next_login = next_login + 1, updated_at = :now "
            "WHERE scope = :scope "
            "RETURNING next_login"
        )
        async with self.session_factory() as session:
            row = (
                await session.execute(stmt, {"scope": scope, "now": datetime.now(timezone.utc)})
            ).first()
            await session.commit()
        if row is None:
            # No row to update means ensure_scope was never called for this scope.
            # Refuse rather than inventing a login.
            raise RuntimeError(
                f"login_counters has no row for scope {scope!r}; ensure_scope must "
                "run first (the allocator does this, so this indicates a store used "
                "outside LoginAllocator)"
            )
        # RETURNING gives the post-increment value; the login we reserved is the
        # one before it.
        return int(row[0]) - 1

    async def is_taken(self, login: int) -> bool:
        """Is this login already an account? A COUNT, not find_all()+len."""
        from ..account_models import AccountModel

        async with self.session_factory() as session:
            result = await session.execute(
                select(AccountModel.login).where(AccountModel.login == str(login))
            )
            return result.first() is not None


class SqlClientRepository(IClientRepository):
    """PostgreSQL persistence for Client (MT5 IMTClient).

    Promoted from manager_repository.py, where it lived without a port and said
    so in its own docstring. The legacy password columns still round-trip - a
    stored value is never dropped - but nothing NEW writes them: MT5 keeps
    per-account password material on IMTUser, so CreateAccountHandler provisions
    the account side and CreateClientHandler leaves these empty.
    """

    def __init__(self, session_factory) -> None:
        self.session_factory = session_factory

    async def find_by_id(self, client_id: str) -> Optional[Client]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(ClientModel).where(ClientModel.id == client_id)
            )
            model = result.scalar_one_or_none()
            return db_to_client(model) if model else None

    async def find_by_client_id(self, client_id: str) -> Optional[Client]:
        """Look up by the external KYC id, which is what an operator searches on."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(ClientModel).where(ClientModel.client_id == client_id)
            )
            model = result.scalar_one_or_none()
            return db_to_client(model) if model else None

    async def save(self, client: Client, session=None) -> Client:
        """Persist a client. Pass `session` to join a caller's transaction.

        CreateAccountHandler writes the client, the account and the opening
        deposit's ledger row in ONE transaction: an account with a balance and no
        ledger entry is how a book becomes unreconcilable, and a client with no
        account is an orphan KYC record. Without the session parameter those
        three writes commit separately and a failure between them leaves exactly
        one of those two states.
        """
        model = client_to_db(client)
        if session is not None:
            await session.merge(model)
            return client
        async with self.session_factory() as own:
            await own.merge(model)
            await own.commit()
            return client

    async def delete(self, client_id: str) -> bool:
        async with self.session_factory() as session:
            result = await session.execute(
                select(ClientModel).where(ClientModel.id == client_id)
            )
            model = result.scalar_one_or_none()
            if model is None:
                return False
            await session.delete(model)
            await session.commit()
            return True

    async def find_all(self) -> List[Client]:
        async with self.session_factory() as session:
            result = await session.execute(select(ClientModel))
            return [db_to_client(m) for m in result.scalars().all()]

    async def count(self) -> int:
        from sqlalchemy import func

        async with self.session_factory() as session:
            return int((await session.execute(select(func.count()).select_from(ClientModel))).scalar() or 0)
