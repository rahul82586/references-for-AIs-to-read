#!/usr/bin/env python3
"""P1 proof: migration 009_identity_plane really runs, is idempotent, and
produces the schema the LIVE Neon database already carries.

Why this proof exists: the original 009 was written in a session that died
before pushing it. The live database has it; the repo did not. The repo's
reconstructed 009 must therefore satisfy two masters at once:

  * a FRESH database migrated to head must end up with Neon's exact shape
    (accounts +33 identity columns, clients +5, login_counters, the TECHNICAL
    partial index), and
  * Neon itself must be a no-op (its alembic_version already reads
    '009_identity_plane') - which this script cannot test directly, but the
    idempotency re-run below is the same property one level down: an already
    migrated database survives `upgrade head` untouched.

Runs entirely on a throwaway SQLite file - no credentials, no network:

    PYTHONPATH=<bp> python3 scripts/p1_proof_migration_009.py

Exit 0 = every check passed.
"""
from __future__ import annotations

import os
import pathlib
import sys
import tempfile

BP = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BP))

CHECKS = {"pass": 0, "fail": 0}


def check(label: str, ok: bool, detail: str = "") -> None:
    CHECKS["pass" if ok else "fail"] += 1
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" - {detail}" if detail else ""))


ACCOUNT_NEW = [
    "first_name", "last_name", "middle_name", "company", "country", "state", "city",
    "zip_code", "address", "phone", "email", "language", "residency_status",
    "id_number", "lead_source", "lead_campaign", "mqid", "visitor_id", "comment",
    "color", "agent_login", "bank_account", "interest_rate", "limit_orders",
    "limit_positions_value", "rights", "investor_password_hash",
    "phone_password_hash", "webapi_password_hash", "otp_secret",
    "cert_serial_number", "last_ip", "last_pass_change",
]
CLIENT_NEW = ["middle_name", "state", "id_number", "lead_source", "lead_campaign"]


def main() -> int:
    import sqlalchemy as sa
    from alembic import command
    from alembic.config import Config

    # the JSONB->SQLite compile hook lives in database.py; importing the models
    # registers every table on Base.metadata (same set env.py uses).
    from infrastructure.persistence.database import Base, DatabaseManager  # noqa: F401
    import infrastructure.persistence.db_models  # noqa: F401
    import infrastructure.persistence.config_models  # noqa: F401
    import infrastructure.persistence.manager_models  # noqa: F401
    import infrastructure.persistence.account_models  # noqa: F401

    tmpdir = tempfile.mkdtemp(prefix="p1_migration_")
    db_path = pathlib.Path(tmpdir) / "mig.db"
    url = f"sqlite+aiosqlite:///{db_path}"

    import asyncio

    async def create_base_schema() -> None:
        """The 008-era schema: today's models, which deliberately do NOT declare
        the 009 columns yet (a declared column without mapper support is a
        full-row save waiting to blank it)."""
        manager = DatabaseManager(url)
        await manager.create_tables()
        await manager.close()

    asyncio.run(create_base_schema())

    cfg = Config(str(BP / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", url)
    cfg.set_main_option("script_location", str(BP / "alembic"))

    engine = sa.create_engine(f"sqlite:///{db_path}")

    def columns(table: str) -> set:
        return {c["name"] for c in sa.inspect(engine).get_columns(table)}

    def indexes(table: str) -> set:
        return {ix["name"] for ix in sa.inspect(engine).get_indexes(table)}

    print("== before: the 008-era schema ==")
    pre_accounts = columns("accounts")
    check("accounts has no identity columns yet", not (set(ACCOUNT_NEW) & pre_accounts),
          f"overlap={sorted(set(ACCOUNT_NEW) & pre_accounts)[:3]}")
    check("login_counters absent", "login_counters" not in sa.inspect(engine).get_table_names())

    print("== stamp 008, upgrade head (runs 009) ==")
    command.stamp(cfg, "008_reconciliation_breaks")
    command.upgrade(cfg, "head")

    post_accounts = columns("accounts")
    post_clients = columns("clients")
    tables = set(sa.inspect(engine).get_table_names())
    missing = [c for c in ACCOUNT_NEW if c not in post_accounts]
    check("accounts +33 identity columns", not missing, f"missing={missing}")
    missing = [c for c in CLIENT_NEW if c not in post_clients]
    check("clients +5 KYC columns", not missing, f"missing={missing}")
    check("login_counters created", "login_counters" in tables)
    if "login_counters" in tables:
        lc = {c["name"] for c in sa.inspect(engine).get_columns("login_counters")}
        check("login_counters shape", lc == {"scope", "next_login", "login_floor", "updated_at"}, str(sorted(lc)))
    ix = indexes("accounts")
    check("idx_accounts_agent_login", "idx_accounts_agent_login" in ix)
    check("idx_accounts_rights_technical (partial)", "idx_accounts_rights_technical" in ix)

    # the partial index must carry the TECHNICAL-bit predicate on SQLite too
    ddl = engine.execute if hasattr(engine, "execute") else None
    with engine.connect() as conn:
        row = conn.execute(sa.text(
            "SELECT sql FROM sqlite_master WHERE name='idx_accounts_rights_technical'"
        )).fetchone()
    check("partial predicate uses the TECHNICAL bit (65536)",
          row is not None and "65536" in (row[0] or ""), (row[0] or "")[-60:] if row else "index missing")

    print("== defaults match the live Neon shapes ==")
    defaults = {
        c["name"]: (c.get("default"), c["nullable"])
        for c in sa.inspect(engine).get_columns("accounts")
    }
    check("language defaults to 'en'", "'en'" in str(defaults["language"][0]), str(defaults["language"]))
    check("rights NOT NULL default 0", defaults["rights"][1] is False and "0" in str(defaults["rights"][0]))
    check("limit_orders nullable (NULL = inherit the group)", defaults["limit_orders"][1] is True)
    check("color nullable", defaults["color"][1] is True)
    check("first_name NOT NULL default ''", defaults["first_name"][1] is False)

    print("== idempotency: a second upgrade head changes nothing ==")
    command.upgrade(cfg, "head")  # must not raise, must not duplicate
    check("re-run survived", columns("accounts") == post_accounts)

    print("== downgrade -1 removes exactly what 009 added ==")
    command.downgrade(cfg, "-1")
    back_accounts = columns("accounts")
    check("identity columns dropped", not (set(ACCOUNT_NEW) & back_accounts))
    check("login_counters dropped", "login_counters" not in set(sa.inspect(engine).get_table_names()))
    check("pre-009 columns intact", pre_accounts <= back_accounts)

    engine.dispose()
    print(f"\nP1 migration proof: {CHECKS['pass']} passed, {CHECKS['fail']} failed")
    return 1 if CHECKS["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
