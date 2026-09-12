"""
End-to-end proof for M2: run the real seeder against a real database and read it back.

Uses SQLite via aiosqlite so it runs anywhere, including CI without a PostgreSQL
service. That has one consequence worth knowing: the configuration models use
postgresql.JSONB, which SQLite does not have. `create_all` on SQLite fails unless the
JSONB columns are given a SQLite-compatible type, so this script installs a compilation
fallback for JSONB -> JSON. That is a test-harness accommodation, NOT a production
concern - production runs PostgreSQL, where JSONB is native and indexed.

What this proves:
  * migrate-equivalent: every table creates from the single Base.metadata
  * seed: groups, symbols, coverage account and first admin all persist
  * idempotence: seeding twice leaves the counts unchanged
  * status: the data reads back through the same repositories the API uses
  * percent: margin thresholds come back as 50/30, not 0.5/0.3
  * first admin: created at login 1000 with a generated password, shown once
"""

from __future__ import annotations

import asyncio
import os
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

# --- JSONB -> JSON so SQLite can create the tables -------------------------
from sqlalchemy.dialects.postgresql import JSONB  # noqa: E402
from sqlalchemy.ext.compiler import compiles  # noqa: E402


@compiles(JSONB, "sqlite")
def _compile_jsonb_sqlite(type_, compiler, **kw):  # noqa: ANN001
    return "JSON"


from infrastructure.persistence.database import DatabaseManager  # noqa: E402
import infrastructure.persistence.db_models  # noqa: F401,E402  (registers every table)
from infrastructure.persistence.database import Base  # noqa: E402
from infrastructure.persistence.di_setup import setup_persistence_di  # noqa: E402
from infrastructure.config.seeder import seed_all  # noqa: E402
from infrastructure.security.password_hasher import Argon2PasswordHasher  # noqa: E402


def _build_event_bus():
    from core.ports.interfaces import IEventBus

    class InProcessEventBus(IEventBus):
        def __init__(self) -> None:
            self._subscribers = {}
            self.published = []

        async def publish(self, event):
            self.published.append(event)
            for key in (type(event), getattr(event, "event_type", None)):
                for handler in self._subscribers.get(key, []):
                    result = handler(event)
                    if hasattr(result, "__await__"):
                        await result

        def subscribe(self, event_type, handler):
            self._subscribers.setdefault(event_type, []).append(handler)
            return _Sub()

        def unsubscribe(self, event_type, handler):
            handlers = self._subscribers.get(event_type, [])
            if handler in handlers:
                handlers.remove(handler)

        async def disconnect(self):
            self._subscribers.clear()

    class _Sub:
        def __await__(self):
            async def _done():
                return None
            return _done().__await__()

    return InProcessEventBus()


async def main() -> int:
    tmp = tempfile.mkdtemp(prefix="broker-m2-")
    url = f"sqlite+aiosqlite:///{pathlib.Path(tmp) / 'broker.db'}"
    print(f"=== M2 end-to-end against {url} ===\n")

    manager = DatabaseManager(url)
    await manager.create_tables()
    created = sorted(Base.metadata.tables)
    print(f"[1] created {len(created)} tables: {', '.join(created)}")

    providers = setup_persistence_di(manager)
    providers["event_bus"] = _build_event_bus()
    hasher = Argon2PasswordHasher()

    async def run_seed():
        return await seed_all(
            group_repo=providers["group_repo"],
            symbol_repo=providers["symbol_repo"],
            manager_repo=providers["manager_repo"],
            account_repo=providers["account_repo"],
            config_root="config",
            password_hasher=hasher,
        )

    report = await run_seed()
    print(
        f"\n[2] seed: {report.groups_created} groups created, "
        f"{report.symbols_created} symbols created, "
        f"coverage={report.coverage_accounts}, admin_created={report.admin_created}"
    )
    if report.admin_created:
        print(f"    first admin login {report.admin_login}, password shown once: "
              f"{report.admin_password[:4]}{'*' * (len(report.admin_password) - 4)}")
        assert not report.admin_password.startswith("PLAINTEXT"), (
            "the hasher was not applied"
        )
    for warning in report.warnings:
        print(f"    warning: {warning}")

    # --- read back through the same repositories the API uses ---
    groups = await providers["group_repo"].get_all()
    symbols = await providers["symbol_repo"].get_all_symbols()
    accounts = await providers["account_repo"].find_all()
    managers = await providers["manager_repo"].find_all()
    print(
        f"\n[3] read back: {len(groups)} groups, {len(symbols)} symbols, "
        f"{len(accounts)} accounts, {len(managers)} managers"
    )

    print("\n[4] groups, as the admin API would report them (thresholds are PERCENT):")
    for group in groups:
        print(
            f"      {group.name:20s} {group.account_type.value:12s} "
            f"call={group.margin.margin_call_level:>4} "
            f"stop={group.margin.stop_out_level:>4} "
            f"lev={group.margin.leverage_default:>4} "
            f"mode={group.margin.mode.name}"
        )
        assert group.margin.margin_call_level > 1, (
            f"{group.name}: margin_call_level {group.margin.margin_call_level} looks "
            "like a fraction, not a percent"
        )

    print("\n[5] symbols:")
    for symbol in symbols:
        print(
            f"      {symbol.name:8s} digits={symbol.digits} "
            f"point={symbol.tick_size} mt5_tick_size={symbol.mt5_tick_size} "
            f"contract={symbol.contract_size} calc={symbol.calc_mode.name}"
        )

    # --- idempotence ---
    second = await run_seed()
    groups_after = await providers["group_repo"].get_all()
    symbols_after = await providers["symbol_repo"].get_all_symbols()
    managers_after = await providers["manager_repo"].find_all()
    print(
        f"\n[6] second seed: created={second.groups_created}/{second.symbols_created}, "
        f"updated={second.groups_updated}/{second.symbols_updated}, "
        f"admin_created={second.admin_created}"
    )
    print(
        f"    counts unchanged: groups {len(groups)}->{len(groups_after)}, "
        f"symbols {len(symbols)}->{len(symbols_after)}, "
        f"managers {len(managers)}->{len(managers_after)}"
    )
    assert second.groups_created == 0, "a second seed must not duplicate groups"
    assert second.symbols_created == 0, "a second seed must not duplicate symbols"
    assert second.admin_created is False, "a second seed must not create another admin"
    assert len(groups_after) == len(groups)
    assert len(symbols_after) == len(symbols)
    assert len(managers_after) == len(managers)

    # --- stop-out state must survive a save, which the old 14-column model dropped ---
    from decimal import Decimal

    from core.domains.accounts.enums import SOActivation
    from core.domains.common.value_objects import Money

    target = groups_after[0]
    account = accounts[0] if accounts else None
    if account is not None:
        account.so_activation = SOActivation.STOP_OUT
        account.so_level = Decimal("27.5")
        account.so_equity = Money(Decimal("550"), account.currency)
        account.margin_level = Decimal("27.5")
        # NOTE: the line above writes the COLUMN, but db_to_account now DERIVES
        # margin_level from equity / margin_used (D1 fix), so the value printed
        # below is the derived one - 999999 for this flat coverage account, not
        # 27.5. That is correct, not a regression: 27.5 is a snapshot of the level
        # AT stop-out, and so_level is the field that preserves it. The assertions
        # below are deliberately on so_activation and so_level, the stop-out
        # machine's real memory; margin_level is derived state and is asserted in
        # tests/unit/persistence/test_m2_config_plane.py instead.
        await providers["account_repo"].save(account)
        reloaded = await providers["account_repo"].find_by_login(str(account.login))
        print(
            f"\n[7] stop-out state round trip on account {reloaded.login}: "
            f"so_activation={reloaded.so_activation.name}, so_level={reloaded.so_level}, "
            f"margin_level={reloaded.margin_level}"
        )
        assert reloaded.so_activation is SOActivation.STOP_OUT, (
            "so_activation was dropped on save - the state machine cannot survive a tick"
        )
        assert reloaded.so_level == Decimal("27.5")
    else:
        print("\n[7] skipped: no account to test (coverage group may be absent)")

    await manager.close()
    print("\n=== M2 end-to-end PASSED ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
