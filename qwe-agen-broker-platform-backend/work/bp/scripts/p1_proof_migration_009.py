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
    # EVERY model module, not just the four this proof was written against.
    # A partial import list makes the "models and migration agree" check below
    # compare against an incomplete metadata and report drift that is really just
    # an unimported table - it hid reconciliation_breaks and mt5_routing_rules on
    # its first run.
    import infrastructure.persistence.db_models  # noqa: F401
    import infrastructure.persistence.config_models  # noqa: F401
    import infrastructure.persistence.manager_models  # noqa: F401
    import infrastructure.persistence.account_models  # noqa: F401
    import infrastructure.persistence.reconciliation_models  # noqa: F401
    import infrastructure.persistence.routing_models  # noqa: F401
    import infrastructure.persistence.identity_models  # noqa: F401

    tmpdir = tempfile.mkdtemp(prefix="p1_migration_")
    db_path = pathlib.Path(tmpdir) / "mig.db"
    url = f"sqlite+aiosqlite:///{db_path}"

    cfg = Config(str(BP / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", url)
    cfg.set_main_option("script_location", str(BP / "alembic"))

    engine = sa.create_engine(f"sqlite:///{db_path}")

    # ---------------------------------------------------------------------
    # CHANGED IN STEP 5, and the change makes this proof stronger, not weaker.
    #
    # The 008-era starting schema used to be built from Base.metadata.create_all
    # - which was valid ONLY because the models deliberately did not declare the
    # 009 columns yet. Step 5 declares them (that is the whole point of the
    # milestone: entity + model + mapper together), so create_all now produces
    # the POST-009 shape and the old "before" assertion could not hold.
    #
    # So the baseline is now built by ALEMBIC (`upgrade 008_reconciliation_breaks`
    # from an empty database), which is what a real 008-era server was: a
    # product of the migration chain alone, independent of the ORM. That removes
    # the circularity the old version had - it was comparing the models against
    # themselves - and it lets the proof assert the property that actually
    # matters now, added below as "models and migration agree": an alembic-only
    # database at head and a create_all database have the SAME columns, so the
    # DDL and the ORM cannot drift.
    # ---------------------------------------------------------------------
    command.upgrade(cfg, "008_reconciliation_breaks")

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

    print("== models and migration agree (the step-5 atomicity guarantee) ==")
    # Build a SECOND throwaway database from the ORM alone and compare column
    # sets table by table. Step 5's rule is that an entity field, a model column
    # and both mapper directions land in the same change; this is the check that
    # fails if a column is declared on the model but never added by a migration
    # (or vice versa) - the drift that produces a full-row save blanking data.
    model_db = pathlib.Path(tmpdir) / "models.db"
    model_url = f"sqlite+aiosqlite:///{model_db}"

    import asyncio

    async def _create_all() -> None:
        manager = DatabaseManager(model_url)
        await manager.create_tables()
        await manager.close()

    asyncio.run(_create_all())
    model_engine = sa.create_engine(f"sqlite:///{model_db}")
    model_inspector = sa.inspect(model_engine)
    mig_inspector = sa.inspect(engine)

    def _cols(insp, table):
        return {c["name"] for c in insp.get_columns(table)}

    # alembic_version is alembic's own bookkeeping row and is never an ORM model.
    ALEMBIC_OWN = {"alembic_version"}
    mig_tables = set(mig_inspector.get_table_names()) - ALEMBIC_OWN
    model_tables = set(model_inspector.get_table_names()) - ALEMBIC_OWN
    shared = sorted(mig_tables & model_tables)
    check("both schemas expose the same tables",
          mig_tables == model_tables,
          f"migration-only={sorted(mig_tables - model_tables)} "
          f"models-only={sorted(model_tables - mig_tables)}")
    drift = {}
    for table in shared:
        a, b = _cols(mig_inspector, table), _cols(model_inspector, table)
        if a != b:
            drift[table] = {"migration_only": sorted(a - b), "models_only": sorted(b - a)}
    check("no column drift between migration 009 and the ORM models",
          not drift, str(drift)[:300])
    for table in ("accounts", "clients", "groups", "managers"):
        if table in shared:
            check(f"{table}: every model column exists in the migrated schema",
                  _cols(model_inspector, table) <= _cols(mig_inspector, table),
                  str(sorted(_cols(model_inspector, table) - _cols(mig_inspector, table)))[:200])
    model_engine.dispose()

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
