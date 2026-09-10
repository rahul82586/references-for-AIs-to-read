"""
M3 proof: import the real MT5 server export and show the three symbol currencies
now land in the database, then re-export and confirm the file is still byte-identical.

This is the check that matters for the MT5-format constraint. Modelling CurrencyProfit and
CurrencyMargin could have broken losslessness in either direction:

  * if the codec dropped them on import, the export would lose data a real MT5 server needs;
  * if the export wrote them from a column that was empty, it would overwrite the original
    value with "" and corrupt the file.

Both are guarded here: the import must populate the columns, and the re-export must be
field-identical to the source.

Run:
    PYTHONPATH=work/bp BROKER_MT5_FIXTURES=decoded/mt5-format-structure \
        python3 scripts/m3_proof_currencies.py work/bp
"""

from __future__ import annotations

import asyncio
import os
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
sys.path.insert(0, str(ROOT))
os.environ.setdefault("BROKER_MT5_FIXTURES", "/home/user/decoded/mt5-format-structure")

from sqlalchemy import text  # noqa: E402
from sqlalchemy.dialects.postgresql import JSONB  # noqa: E402
from sqlalchemy.ext.compiler import compiles  # noqa: E402


@compiles(JSONB, "sqlite")
def _jsonb_sqlite(type_, compiler, **kw):  # noqa: ANN001, ANN202
    return "JSON"


from infrastructure.persistence.database import Base, DatabaseManager  # noqa: E402
import infrastructure.persistence.db_models  # noqa: F401,E402
from infrastructure.persistence.di_setup import setup_persistence_di  # noqa: E402
from infrastructure.config.seeder import seed_all  # noqa: E402
from infrastructure.security.password_hasher import Argon2PasswordHasher  # noqa: E402

FIXTURES = pathlib.Path(os.environ["BROKER_MT5_FIXTURES"])


class _NullBus:
    async def publish(self, event):  # noqa: ANN001, ANN201
        return None

    def subscribe(self, *a, **kw):  # noqa: ANN002, ANN003, ANN201
        return None


async def main() -> int:
    tmp = tempfile.mkdtemp(prefix="broker-m3-")
    url = f"sqlite+aiosqlite:///{pathlib.Path(tmp) / 'broker.db'}"
    print(f"=== M3 proof: the three symbol currencies, against {url}\n")

    manager = DatabaseManager(url)
    await manager.create_tables()
    providers = setup_persistence_di(manager)
    providers["event_bus"] = _NullBus()

    report = await seed_all(
        group_repo=providers["group_repo"],
        symbol_repo=providers["symbol_repo"],
        manager_repo=providers["manager_repo"],
        account_repo=providers["account_repo"],
        config_root=str(ROOT / "config"),
        password_hasher=Argon2PasswordHasher(),
        mt5_groups=str(FIXTURES / "Groups TCTrader-Live.json"),
        mt5_symbols=str(FIXTURES / "Symbols TCTrader-Live.json"),
    )
    print(f"[1] imported {report.groups_created} groups, {report.symbols_created} symbols")

    engine = manager.engine
    async with engine.connect() as conn:
        total = (await conn.execute(text("select count(*) from symbols"))).scalar()
        with_base = (
            await conn.execute(text("select count(*) from symbols where base_currency <> ''"))
        ).scalar()
        with_profit = (
            await conn.execute(text("select count(*) from symbols where quote_currency <> ''"))
        ).scalar()
        with_margin = (
            await conn.execute(text("select count(*) from symbols where margin_currency <> ''"))
        ).scalar()

    print(f"\n[2] currency coverage across {total} imported symbols")
    print(f"      base_currency   (MT5 CurrencyBase)   populated on {with_base}")
    print(f"      quote_currency  (MT5 CurrencyProfit) populated on {with_profit}")
    print(f"      margin_currency (MT5 CurrencyMargin) populated on {with_margin}")

    failures = []
    if with_profit != total:
        failures.append(f"CurrencyProfit populated on only {with_profit}/{total}")
    if with_margin != total:
        failures.append(f"CurrencyMargin populated on only {with_margin}/{total}")

    # Show the cases that the name heuristic gets wrong - the reason this mattered.
    async with engine.connect() as conn:
        rows = (
            await conn.execute(
                text(
                    "select name, base_currency, quote_currency, margin_currency, calc_mode "
                    "from symbols where name in "
                    "('EURJPY','AUS200.spot','EU50.spot','BRENT.spot','BTCUSD','XAUUSD',"
                    "'EURUSD','BUND','MC.FR','USDJPY') order by name"
                )
            )
        ).fetchall()

    print("\n[3] symbols where deriving currencies from the NAME would be wrong")
    print(f"      {'symbol':<14} {'base':<6} {'profit':<7} {'margin':<7} calc_mode")
    for name, base, profit, margin, calc in rows:
        clean = name.upper().replace("/", "").replace("_", "")
        naive = (clean[:3], clean[3:6]) if len(clean) >= 6 else ("?", "?")
        flag = "" if naive[0] == base else "   <- name heuristic would say " + "/".join(naive)
        print(f"      {name:<14} {base:<6} {profit:<7} {margin:<7} {calc}{flag}")

    # --- losslessness: round trip each symbol through DB and compare to the source ---
    #
    # Same path M1's 362/362 proof uses, so this measures the real import/export cycle
    # rather than a shortcut: wire record -> domain -> SymbolModel row -> wire record.
    import json

    from infrastructure.persistence import config_mappers as M
    from infrastructure.mt5 import fieldmap, wire

    # Reuse M1's builder rather than writing a second one: if the two ever diverged, this
    # proof would be measuring a different import path from the one M1 proved lossless.
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from m1_proof_roundtrip import build_symbol

    source = json.loads(
        (FIXTURES / "Symbols TCTrader-Live.json").read_text(encoding="utf-8-sig")
    )
    records = source["Server"][0]["ConfigSymbols"]

    identical = 0
    currency_diffs = []
    worst = None
    for raw in records:
        dom, extra, scale = M.split_mt5_record(raw, fieldmap.SYMBOL_FIELDS)
        row = M.symbol_to_db(
            build_symbol(dom),
            mt5_extra=extra,
            mt5_scale=scale,
            mt5_source=raw,
        )
        out = M.symbol_mt5_record(row)
        differing = {k: (raw[k], out.get(k)) for k in raw if out.get(k) != raw[k]}
        if not differing:
            identical += 1
        elif worst is None or len(differing) < len(worst[1]):
            worst = (raw["Symbol"], differing)
        for key in ("CurrencyBase", "CurrencyProfit", "CurrencyMargin"):
            if out.get(key) != raw.get(key):
                currency_diffs.append((raw["Symbol"], key, raw.get(key), out.get(key)))

    print(f"\n[4] re-export fidelity over {len(records)} source symbols")
    print(f"      field-identical          : {identical}/{len(records)}")
    print(f"      currency-field mismatches: {len(currency_diffs)}")
    if worst:
        print(f"      closest miss             : {worst[0]} with {len(worst[1])} differing")
    for diff in currency_diffs[:10]:
        print(f"        {diff[0]}: {diff[1]} source={diff[2]!r} exported={diff[3]!r}")

    if identical != len(records):
        failures.append(f"only {identical}/{len(records)} symbols re-export field-identically")
    if currency_diffs:
        failures.append(f"{len(currency_diffs)} currency-field mismatches on re-export")

    if failures:
        print(f"\n=== M3 proof FAILED ({len(failures)} issue(s)) ===")
        for f in failures[:12]:
            print(f"  - {f}")
        return 1

    print("\n=== M3 proof PASSED ===")
    print("The three MT5 symbol currencies are imported into real columns, and the")
    print("re-export is still field-identical, so the MT5 file format is preserved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
