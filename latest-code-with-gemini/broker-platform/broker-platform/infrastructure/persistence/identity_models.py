"""Identity-plane persistence: the login allocator behind MT5's "Next" button.

Migration ``009_identity_plane`` created the ``login_counters`` table but no ORM
model existed for it, so the table was reachable only through raw SQL and the
step-5 "models and migration agree" proof failed on it. This module closes that
gap and is the storage half of plan step 6 (``CreateAccountHandler``).

WHY A COUNTER TABLE AND NOT ``MAX(login) + 1``
---------------------------------------------
The Administrator guide, *Creating Accounts*:

    "Preferred Login - account number. If you specify 'Next' in this field the
     closest free number will be assigned to the account. **Do not use logins of
     deleted account when creating new ones.**"

Two requirements, and a naive read of the accounts table satisfies neither:

* ``MAX(login) + 1`` is a read-then-write race. Two administrators clicking OK at
  the same moment both read the same maximum and both write the same login; the
  second gets a primary-key violation at best, and at worst - with the merge-based
  repositories this codebase uses - silently overwrites the first account. The
  allocation has to be atomic in the database, not in Python.
* A deleted account's login must never be reused. ``MAX + 1`` reuses one the
  moment the highest account is deleted, which reassigns a real trading history
  and every statement that ever referenced it to a different person.

So the counter is monotonic and lives in its own row per scope, advanced by a
single conditional ``UPDATE ... RETURNING``. That statement is the one writer of
``next_login``: it both decides and records the answer in one round trip, so two
concurrent allocations cannot see the same value.

The table also carries ``login_floor`` because MT5 numbers accounts from a
per-group base (the live export's groups are ``demo\\...``, ``real\\...``,
``managers\\...`` and each range starts somewhere different). The floor is the
group's, the counter is the server's.
"""
from __future__ import annotations

from sqlalchemy import BigInteger, Column, DateTime, String, func

from .database import Base

#: The scope used when a deployment does not partition login ranges. MT5 numbers
#: from one pool per trade server, so a single global scope is the faithful
#: default; a per-group floor is expressed by giving each group its own scope.
DEFAULT_LOGIN_SCOPE = "global"


class LoginCounterModel(Base):
    """One monotonic login allocator per scope.

    ``scope`` is the primary key, so "allocate the next login" is a single-row
    conditional update - the narrowest possible lock, and the reason two admins
    creating accounts concurrently get different numbers instead of the same one.
    """

    __tablename__ = "login_counters"

    #: Which range this counter serves: "global", or a group path, or a server id.
    scope = Column(String(64), primary_key=True)
    #: The next login to hand out. Advanced atomically; never read-then-written
    #: from Python.
    next_login = Column(BigInteger, nullable=False, default=0, server_default="0")
    #: The lowest login this scope may issue. MT5's "closest free number" is
    #: closest *above the group's floor*, not above zero.
    login_floor = Column(BigInteger, nullable=False, default=0, server_default="0")
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return (
            f"<LoginCounter scope={self.scope!r} next_login={self.next_login} "
            f"login_floor={self.login_floor}>"
        )
