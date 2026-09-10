"""
Step M3 part 24 - the UnitOfWork could not be entered, and would not have shared a session.

Two defects, both listed in the M3 scope and both still live:

1. `SqlOrderRepository()`, `SqlDealRepository()` and `SqlPositionRepository()` are
   constructed with NO ARGUMENTS, but each requires `session_factory`. Entering the unit of
   work raised

       TypeError: SqlOrderRepository.__init__() missing 1 required positional
                  argument: 'session_factory'

   so every `async with UnitOfWork(...)` block failed before executing a line. Any caller
   that wrapped it in try/except - and the command handlers do - silently skipped the
   transaction entirely.

2. Even with that fixed, the comment "Instantiate repositories bound to this shared
   session" was false. The repositories were handed `self.session_factory`, which makes
   each one open its OWN session. That defeats the entire purpose of a unit of work: the
   margin reserve and the order persist would commit independently, so a failure between
   them leaves margin reserved against an order that was never written - or an order
   written against margin that was never reserved. This is precisely the atomicity the
   concurrency test claims to verify.

Fixed by binding every repository to the single session the unit of work owns. A
`_SessionBound` shim adapts the session to the `session_factory` the repositories expect,
so their internals are untouched: they call the factory and receive the one shared session.
The session is not closed by the shim - the unit of work owns its lifecycle and closes it in
`__aexit__`, which is the difference between a shared session and four sessions that happen
to be opened at the same time.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
REL = "infrastructure/persistence/unit_of_work.py"
path = ROOT / REL
if not path.is_file():
    raise SystemExit(f"not found: {path}")

with open(path, encoding="utf-8", newline="") as fh:
    text = fh.read()
crlf = "\r\n" in text
work = text.replace("\r\n", "\n")

OLD = '''        # Instantiate repositories bound to this shared session
        self.orders = SqlOrderRepository()
        self.deals = SqlDealRepository()
        self.positions = SqlPositionRepository()
        group_repo = SqlGroupRepository(self.session_factory)
        self.accounts = SqlAccountRepository(group_repo=group_repo)

        return self'''

NEW = '''        if self.session is None:
            raise RuntimeError(
                "UnitOfWork entered with neither a session nor a session_factory; there is "
                "nothing to bind the repositories to"
            )

        # Bind every repository to THIS session, not to the factory. Handing them the
        # factory - as this did - makes each one open its own session, which defeats the
        # unit of work: the margin reserve and the order persist would commit separately,
        # so a failure between them leaves margin reserved against an order that was never
        # written. The shim adapts the session to the session_factory argument the
        # repositories expect, so their internals are untouched.
        shared = _SharedSessionFactory(self.session)
        self.orders = SqlOrderRepository(shared)
        self.deals = SqlDealRepository(shared)
        self.positions = SqlPositionRepository(shared)
        group_repo = SqlGroupRepository(shared)
        self.accounts = SqlAccountRepository(session_factory=shared, group_repo=group_repo)

        return self'''

if OLD not in work:
    raise SystemExit("[FAIL] unit_of_work.py: the repository-binding block was not found")
work = work.replace(OLD, NEW, 1)

# Insert the shim above the class.
ANCHOR = "class UnitOfWork:"
SHIM = '''class _SharedSessionFactory:
    """Adapts one AsyncSession to the ``session_factory`` repositories expect.

    Repositories call the factory to obtain a session. Returning the same session every
    time is what makes them participants in one transaction rather than four independent
    ones.

    The session's lifecycle is NOT owned here: ``UnitOfWork.__aexit__`` commits or rolls
    back and closes it. A factory that closed the session on first use would end the
    transaction part-way through, which is the failure mode this exists to prevent.
    """

    def __init__(self, session) -> None:
        self._session = session

    def __call__(self):
        return self._session

    def __getattr__(self, name):
        # Anything else a repository might expect of a sessionmaker (e.g. `.kw`) falls
        # through to the session itself rather than raising AttributeError.
        return getattr(self._session, name)


'''

if ANCHOR not in work:
    raise SystemExit("[FAIL] unit_of_work.py: the UnitOfWork class was not found")
work = work.replace(ANCHOR, SHIM + ANCHOR, 1)

with open(path, "w", encoding="utf-8", newline="") as fh:
    fh.write(work.replace("\n", "\r\n") if crlf else work)
print(f"  ok  {REL}: enterable, and every repository bound to the one shared session")
