import asyncio
import os
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
sys.path.insert(0, str(ROOT))

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles


@compiles(JSONB, "sqlite")
def _c(t, c, **k):
    return "JSON"


os.chdir(ROOT)

from infrastructure.persistence.database import DatabaseManager
import infrastructure.persistence.db_models  # noqa
from infrastructure.persistence.di_setup import setup_persistence_di
from infrastructure.config.seeder import seed_all
from infrastructure.security.password_hasher import Argon2PasswordHasher
from infrastructure.messaging.inprocess_event_bus import InProcessEventBus


async def main():
    tmp = tempfile.mkdtemp()
    m = DatabaseManager(f"sqlite+aiosqlite:///{pathlib.Path(tmp) / 'b.db'}")
    await m.create_tables()
    p = setup_persistence_di(m)
    p["event_bus"] = InProcessEventBus()
    await seed_all(
        group_repo=p["group_repo"], symbol_repo=p["symbol_repo"], manager_repo=p["manager_repo"],
        account_repo=p["account_repo"], coverage_repo=p["coverage_repo"], config_root="config",
        password_hasher=Argon2PasswordHasher(),
    )
    s = await p["symbol_repo"].find_by_name("EURUSD")
    fields = ("name", "digits", "tick_size", "mt5_tick_size", "contract_size", "volume_min",
              "volume_max", "volume_step", "volume_limit", "spread", "base_currency",
              "quote_currency", "margin_currency", "calc_mode", "trade_mode", "swap_long")
    for f in fields:
        print(f"  {f:18s} {getattr(s, f, '<MISSING>')!r}")
    print("  trade_sessions    :", type(s.trade_sessions).__name__, "len", len(s.trade_sessions or []))
    if s.trade_sessions:
        first = s.trade_sessions[0] if isinstance(s.trade_sessions, list) else None
        print("  first session     :", first)
    g = await p["group_repo"].find_by_name("demo\\Standard")
    print("  group margin_call :", g.margin.margin_call_level, " stop_out:", g.margin.stop_out_level,
          " lev:", g.margin.leverage_default)
    await m.close()


asyncio.run(main())
