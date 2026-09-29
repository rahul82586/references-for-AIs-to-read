"""Login allocation — MT5's "Next" button, as a rule rather than a query.

Administrator guide, *Creating Accounts*:

    "Preferred Login - account number. If you specify 'Next' in this field the
     closest free number will be assigned to the account. **Do not use logins of
     deleted account when creating new ones.**"

Those are two separate requirements, and a naive ``MAX(login) + 1`` satisfies
neither:

* It is a read-then-write race. Two administrators pressing OK together read the
  same maximum and write the same login. With the merge-based repositories this
  codebase uses, the loser does not even get a primary-key violation - it
  silently overwrites the winner's account.
* It reuses a deleted login the moment the highest account is removed, which
  hands a real trading history, and every statement that ever referenced it, to a
  different person. That is the one thing the guide explicitly forbids.

So the rule here is: **a monotonic counter, advanced atomically, that also skips
any login already present.** Monotonicity is what makes a deleted login
unreachable; the presence check is what makes the number "free" for a database
that was populated by an import rather than by this allocator.

The counter state itself lives in the ``login_counters`` table created by
migration 009 and modelled by ``LoginCounterModel``. This module holds the RULE
and is deliberately free of SQLAlchemy, so the arithmetic can be tested without a
database and the same rule can later sit behind a different store.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

#: MT5 numbers client accounts from a base well above the staff range (the live
#: export's managers are 1000/2000/3000/19226 and its clients are 6-digit). A
#: five-digit floor keeps a client login from ever colliding with a manager login
#: allocated from its own scope.
DEFAULT_CLIENT_LOGIN_FLOOR = 100_000

#: How far the allocator will walk past logins that are already taken before it
#: refuses. Bounded so a database whose counter is far below its account table -
#: an import that never seeded the counter - fails loudly instead of spinning.
MAX_ALLOCATION_ATTEMPTS = 10_000


class LoginTakenError(RuntimeError):
    """No free login could be allocated within the attempt budget."""


class LoginAllocatorStore(Protocol):
    """The storage half of the allocator.

    ``take_next`` MUST be a single atomic statement that both decides and records
    the answer - ``UPDATE login_counters SET next_login = next_login + 1 WHERE
    scope = ? RETURNING next_login - 1``. Anything that reads the counter and
    then writes it back is the race this module exists to prevent.
    """

    async def ensure_scope(self, scope: str, login_floor: int) -> None:
        """Create the scope's counter row if absent, honouring the floor."""

    async def take_next(self, scope: str) -> int:
        """Atomically reserve and return the scope's next login."""

    async def is_taken(self, login: int) -> bool:
        """Is this login already present in the accounts table?"""


@dataclass(frozen=True)
class AllocatedLogin:
    """The outcome of one allocation, with enough context to explain itself."""

    login: int
    scope: str
    #: How many already-taken logins were stepped over. Zero in the normal case;
    #: non-zero means the counter and the account table disagree, which is worth
    #: surfacing rather than hiding.
    skipped: int = 0


class LoginAllocator:
    """Allocate the next free login for a scope.

    ``scope`` is how a deployment partitions its login ranges. The faithful MT5
    default is one pool per trade server, expressed here as a single ``"global"``
    scope; a broker that numbers each group from its own base passes the group
    path instead and configures that scope's floor.
    """

    def __init__(
        self,
        store: LoginAllocatorStore,
        *,
        default_scope: str = "global",
        default_floor: int = DEFAULT_CLIENT_LOGIN_FLOOR,
        max_attempts: int = MAX_ALLOCATION_ATTEMPTS,
    ) -> None:
        self.store = store
        self.default_scope = default_scope
        self.default_floor = default_floor
        self.max_attempts = max_attempts

    async def next_login(
        self,
        scope: Optional[str] = None,
        *,
        login_floor: Optional[int] = None,
    ) -> AllocatedLogin:
        """Reserve the closest free login above the scope's floor.

        Raises ``LoginTakenError`` rather than returning a colliding or negative
        number: refusing is better than handing out a login that already belongs
        to somebody's trade history.
        """
        scope = scope or self.default_scope
        floor = self.default_floor if login_floor is None else int(login_floor)
        if floor < 0:
            raise ValueError(f"login_floor must be >= 0, got {floor}")

        await self.store.ensure_scope(scope, floor)

        skipped = 0
        for _ in range(self.max_attempts):
            candidate = int(await self.store.take_next(scope))
            if candidate < floor:
                # The counter was seeded below the floor (an import, or a floor
                # raised after accounts existed). Keep walking; the counter
                # catches up and this branch stops firing.
                skipped += 1
                continue
            if not await self.store.is_taken(candidate):
                return AllocatedLogin(login=candidate, scope=scope, skipped=skipped)
            skipped += 1

        raise LoginTakenError(
            f"could not allocate a free login in scope {scope!r} after "
            f"{self.max_attempts} attempts (floor {floor}); the counter and the "
            "accounts table disagree by more than the attempt budget. Refusing "
            "rather than reusing a login."
        )

    async def peek(
        self, scope: Optional[str] = None, *, login_floor: Optional[int] = None
    ) -> int:
        """The login the "Next" button would show, WITHOUT reserving it.

        MT5's dialog displays the suggested number before OK is pressed. This is
        advisory: the authoritative allocation happens in ``next_login`` inside
        the create transaction, so two administrators looking at the same peeked
        number cannot both get it.
        """
        scope = scope or self.default_scope
        floor = self.default_floor if login_floor is None else int(login_floor)
        await self.store.ensure_scope(scope, floor)
        candidate = floor
        for _ in range(self.max_attempts):
            if not await self.store.is_taken(candidate):
                return candidate
            candidate += 1
        raise LoginTakenError(f"no free login near the floor in scope {scope!r}")
