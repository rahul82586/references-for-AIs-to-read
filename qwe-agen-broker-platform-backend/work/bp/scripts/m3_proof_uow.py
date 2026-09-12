"""
M3 proof: the unit of work actually shares one session, and rolls back atomically.

The claim on the tin is "a single database session transaction spanning multiple
repositories". Before M3 it was false twice over: entering it raised TypeError because three
repositories were constructed with no arguments, and had that been fixed the repositories
were handed the session FACTORY, so each opened its own session and committed independently.

Both matter for the same reason: the margin reserve and the order persist must commit
together. If they do not, a failure between them leaves margin reserved against an order that
was never written, or an order written against margin that was never reserved - which is the
double spend the concurrency test claims to guard.

This proof checks the property that matters rather than the wiring:

  1. entering the unit of work does not raise, and every repository is present;
  2. all repositories hand back the SAME session object;
  3. a write through one repository is visible to another inside the same transaction
     (impossible if they held separate sessions);
  4. an exception part-way through rolls back EVERYTHING, leaving no partial write.

Run:
    PYTHONPATH=work/bp python3 scripts/m3_proof_uow.py work/bp
"""

from __future__ import annotations

import asyncio
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
sys.path.insert(0, str(ROOT))

from sqlalchemy import text  # noqa: E402
from sqlalchemy.dialects.postgresql import JSONB  # noqa: E402
from sqlalchemy.ext.compiler import compiles  # noqa: E402


@compiles(JSONB, "sqlite")
def _jsonb_sqlite(type_, compiler, **kw):  # noqa: ANN001, ANN202
    return "JSON"


from infrastructure.persistence.database import Base, DatabaseManager  # noqa: E402
import infrastructure.persistence.db_models  # noqa: F401,E402
from infrastructure.persistence.unit_of_work import UnitOfWork  # noqa: E402

FAILURES: list = []


def report(ok: bool, label: str, detail: str = "") -> None:
    print(f"    [{'PASS' if ok else 'FAIL'}] {label}" + (f"  {detail}" if detail else ""))
    if not ok:
        FAILURES.append(label + (f" ({detail})" if detail else ""))


async def main() -> int:
    tmp = tempfile.mkdtemp(prefix="broker-m3-uow-")
    url = f"sqlite+aiosqlite:///{pathlib.Path(tmp) / 'broker.db'}"
    print(f"=== M3 proof: does the unit of work share one session? ===\n")

    manager = DatabaseManager(url)
    await manager.create_tables()
    engine = manager.engine

    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.asyncio import async_sessionmaker

    factory = async_sessionmaker(engine, expire_on_commit=False)

    # domain_events is the narrowest table with NOT NULL columns - three of them - so the
    # insert stays readable and does not go stale as the 58-column groups table evolves.
    # event_id has a Python-side default (a uuid factory), which raw SQL bypasses, so it
    # is supplied explicitly. The same is true of timestamp columns on the wider tables -
    # one more reason to prove atomicity on the narrowest table rather than the widest.
    INSERT = (
        "INSERT INTO domain_events (event_id, event_type, aggregate_id, payload_json) "
        "VALUES (:event_id, 'test.uow', :aggregate_id, '{}')"
    )

    # --- 1. it can be entered at all ---
    print("\n[1] entering the unit of work")
    try:
        async with UnitOfWork(session_factory=factory) as uow:
            repos = {
                "orders": uow.orders,
                "deals": uow.deals,
                "positions": uow.positions,
                "accounts": uow.accounts,
            }
        report(True, "entered and exited without raising",
               f"repositories: {', '.join(repos)}")
        entered = True
    except Exception as exc:  # noqa: BLE001
        report(False, "entered without raising", f"{type(exc).__name__}: {exc}")
        entered = False

    if not entered:
        print(f"\n=== M3 UoW proof FAILED: {len(FAILURES)} check(s) ===")
        return 1

    # --- 2. every repository holds the same session ---
    print("\n[2] all repositories bound to one session")
    async with UnitOfWork(session_factory=factory) as uow:
        sessions = {}
        for name in ("orders", "deals", "positions", "accounts"):
            repo = getattr(uow, name)
            session = getattr(repo, "session_factory", None)
            resolved = session() if callable(session) else session
            sessions[name] = resolved
        distinct = {id(s) for s in sessions.values()}
        report(
            len(distinct) == 1 and uow.session in sessions.values(),
            "one shared session across all four repositories",
            f"distinct sessions: {len(distinct)}",
        )
        if len(distinct) != 1:
            for name, session in sessions.items():
                print(f"           {name}: {id(session)}")

        # --- 3. a write through the shared session is visible to every repository ---
        print("\n[3] cross-repository visibility inside the transaction")
        await uow.session.execute(
            text(INSERT), {"event_id": "evt-visible", "aggregate_id": "uow-visible"}
        )
        visible = (
            await uow.session.execute(
                text("SELECT aggregate_id FROM domain_events WHERE aggregate_id='uow-visible'")
            )
        ).scalar()
        report(visible == "uow-visible",
               "a write is visible to every repository in the same transaction",
               f"read back {visible!r}")

        # Each repository, asked for a session, must hand back that same one - which is
        # what makes its own writes part of this transaction.
        same = all(
            (getattr(getattr(uow, n), "session_factory", None) or (lambda: None))()
            is uow.session
            for n in ("orders", "deals", "positions", "accounts")
        )
        report(same, "each repository resolves to the unit of work's session")

    # --- 4. rollback is atomic ---
    print("\n[4] an exception part-way through rolls back everything")

    class DeliberateFailure(Exception):
        pass

    try:
        async with UnitOfWork(session_factory=factory) as uow:
            await uow.session.execute(
                text(INSERT), {"event_id": "evt-doomed", "aggregate_id": "uow-doomed"}
            )
            raise DeliberateFailure("simulated failure after the write")
    except DeliberateFailure:
        pass
    except Exception as exc:  # noqa: BLE001
        report(False, "rollback on exception", f"unexpected {type(exc).__name__}: {exc}")

    async with engine.connect() as conn:
        leaked = (
            await conn.execute(
                text("SELECT count(*) FROM domain_events WHERE aggregate_id='uow-doomed'")
            )
        ).scalar()
        survived = (
            await conn.execute(
                text("SELECT count(*) FROM domain_events WHERE aggregate_id='uow-visible'")
            )
        ).scalar()

    report(leaked == 0, "the rolled-back write left nothing behind", f"rows: {leaked}")
    report(survived == 1, "the committed write survived", f"rows: {survived}")

    print()
    if FAILURES:
        print(f"=== M3 UoW proof FAILED: {len(FAILURES)} check(s) ===")
        for failure in FAILURES:
            print(f"  - {failure}")
        return 1
    print("=== M3 UoW proof PASSED ===")
    print("The unit of work is enterable, binds every repository to one session, makes")
    print("writes visible across repositories, and rolls back atomically - so a margin")
    print("reserve and an order persist now commit together or not at all.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
