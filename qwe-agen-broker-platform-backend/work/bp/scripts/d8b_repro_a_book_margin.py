#!/usr/bin/env python3
"""D8b reproduction: A-Book booking leaves margin_used = 0 against REAL SQL repos.

Observed live, twice, on Route A of scripts/m11_proof_live_hedge.py:

    account 887914  margin_used=0E-8  margin_level=999999  equity=100000
                    updated_at == created_at + 8us      <- the row was NEVER saved
    ...yet the Deal and the Position for that order both exist in Neon.

Route B, two minutes later through the same code path, stored 77.37413 correctly.
In the run BEFORE the D8 fix the two routes showed the opposite pattern, so it is
not route-specific - it is intermittent.

The in-memory harness cannot reproduce this (test_m11_a_book_completion.py says
so explicitly), so this drives the REAL Sql* repositories over SQLite, the same
way m4_proof_order_executes.py does, with a scripted ILiquidityGateway standing in
for the terminal. No network, no MT5, no credentials - which means it can run in
CI and be looped until the race shows.

    PYTHONPATH=$PWD python3 scripts/d8b_repro_a_book_margin.py [--loops N]
"""
import asyncio
import os
import pathlib
import sys
import tempfile
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
os.chdir(ROOT)

os.environ.setdefault("SECRET_KEY", "d8b-repro-secret-key-0123456789abcdef0123456789ab")
os.environ.setdefault("ADMIN_API_KEY", "d8b-repro-admin-key")

from application.cache.config_cache import ConfigCache, set_config_cache        # noqa: E402
from application.commands.create_order import CreateOrderCommand              # noqa: E402
from application.di.trading_setup import build_trading_stack                  # noqa: E402
from core.domains.accounts.account import Account                            # noqa: E402
from core.domains.common.value_objects import Money                          # noqa: E402
from core.domains.execution.models import (                                  # noqa: E402
    CoverageAccount, ExecutionDestination, RoutingRule,
)
from core.domains.market_data.engine import MarketDataEngine                 # noqa: E402
from core.domains.market_data.models import Tick                             # noqa: E402
from core.domains.oms.enums import OrderState, OrderType                     # noqa: E402
from infrastructure.config.seeder import seed_all                            # noqa: E402
from infrastructure.messaging.inprocess_event_bus import InProcessEventBus    # noqa: E402
from infrastructure.persistence.database import DatabaseManager              # noqa: E402
from infrastructure.security.password_hasher import Argon2PasswordHasher      # noqa: E402
import infrastructure.persistence.db_models  # noqa: F401,E402  registers every table

from infrastructure.persistence.di_setup import setup_persistence_di           # noqa: E402

SYMBOL = os.environ.get("D8B_SYMBOL", "BTCUSD")
VOLUME = Decimal(os.environ.get("D8B_VOLUME", "0.01"))
BID = Decimal(os.environ.get("D8B_BID", "77300.00"))
ASK = Decimal(os.environ.get("D8B_ASK", "77366.53"))
LOOPS = int(sys.argv[sys.argv.index("--loops") + 1]) if "--loops" in sys.argv else 5


class AlwaysFillGateway:
    """Stands in for TradeServerLiquidityGateway: always fills at the ask."""

    def __init__(self):
        self.calls = 0

    async def send_order(self, order, gateway_id):
        self.calls += 1
        return {
            "status": "FILLED", "cl_ord_id": order.ticket_id,
            "order_id": f"REPRO-{self.calls}", "gateway_id": gateway_id,
            "symbol": str(order.symbol).upper(), "side": "BUY",
            "volume": str(order.volume_current.value), "price": str(ASK),
            "stub": False, "venue": "REPRO",
        }

    async def cancel_order(self, order_id, gateway_id):
        return True

    async def get_quotes(self, symbols):
        return {}


async def one_loop(n):
    tmp = tempfile.mkdtemp(prefix="d8b-")
    url = f"sqlite+aiosqlite:///{pathlib.Path(tmp) / 'broker.db'}"
    manager = DatabaseManager(url)
    await manager.create_tables()
    providers = setup_persistence_di(manager)
    bus = InProcessEventBus()
    providers["event_bus"] = bus

    await seed_all(
        group_repo=providers["group_repo"], symbol_repo=providers["symbol_repo"],
        manager_repo=providers["manager_repo"], account_repo=providers["account_repo"],
        coverage_repo=providers["coverage_repo"], config_root="config",
        password_hasher=Argon2PasswordHasher(),
    )
    await providers["coverage_repo"].save(CoverageAccount(
        account_id="DEFAULT_COVERAGE", name="house", currency="USD",
        nop_limit=Decimal("100")))

    groups = {g.name: g for g in await providers["group_repo"].get_all()}
    group = groups.get("demo\\Standard") or next(iter(groups.values()))
    login = 880000 + n
    account = Account(login=login, client_id=f"D8B_{n}", group=group, group_id=group.id,
                      currency="USD", balance=Money(Decimal("100000"), "USD"),
                      credit=Money(Decimal("0"), "USD"),
                      equity=Money(Decimal("100000"), "USD"),
                      margin_used=Money(Decimal("0"), "USD"),
                      margin_free=Money(Decimal("100000"), "USD"))
    await providers["account_repo"].save(account)

    # A-Book by routing rule, exactly as Route A does
    await providers["routing_rule_repo"].save(RoutingRule(
        rule_id="a-book-repro", priority=100, destination=ExecutionDestination.A_BOOK,
        symbol_filter=SYMBOL, gateway_id="REPRO-LP"))

    engine = MarketDataEngine(event_bus=bus, symbol_repo=providers["symbol_repo"])
    cache = ConfigCache(
        group_repo=providers["group_repo"], account_repo=providers["account_repo"],
        symbol_repo=providers["symbol_repo"], holiday_repo=providers["holiday_repo"],
        position_repo=providers["position_repo"], event_bus=bus,
    )
    await cache.initialize()
    set_config_cache(cache)

    providers["market_data_engine"] = engine
    gw = AlwaysFillGateway()
    providers["liquidity_gateway"] = gw
    stack = await build_trading_stack(providers, market_data_engine=engine,
                                      config_cache=cache)

    # a live price for the traded symbol AND for the margin conversion
    await engine.process_tick(Tick(symbol=SYMBOL, bid=BID, ask=ASK, spread=ASK - BID,
                                   source="REPRO"))

    # THE MISSING INGREDIENT: a live feed ticks continuously, so TickMarginPipeline
    # is load-modify-saving the account while the order is in flight. Without this
    # pump the repro is clean 12/12 and the bug never shows.
    stop = asyncio.Event()

    async def pump():
        i = 0
        while not stop.is_set():
            i += 1
            wob = Decimal(i % 3) * Decimal("0.01")
            try:
                await engine.process_tick(Tick(
                    symbol=SYMBOL, bid=BID + wob, ask=ASK + wob,
                    spread=ASK - BID, source="REPRO_PUMP"))
            except Exception:
                pass
            await asyncio.sleep(0)

    ticker = asyncio.create_task(pump())

    order = await stack.create_order_handler.handle(CreateOrderCommand(
        account_login=login, symbol=SYMBOL, order_type=OrderType.BUY, volume=VOLUME))

    stop.set()
    await ticker

    after = await providers["account_repo"].find_by_login(login)
    deals = await providers["deal_repo"].find_by_account(login)
    positions = await providers["position_repo"].get_by_account(login)

    result = dict(
        n=n, state=order.state.name, gateway_calls=gw.calls,
        deals=len(deals), positions=len(positions),
        margin_used=after.margin_used.amount,
        margin_reserved=after.margin_reserved.amount,
        margin_level=after.margin_level,
        equity=after.equity.amount,
        reserved_on_order=order.reserved_margin,
    )
    await manager.close()
    return result


def verdict(r):
    """What a correct A-Book booking looks like, and which part went wrong."""
    problems = []
    if r["state"] != "FILLED":
        problems.append(f"order not FILLED ({r['state']})")
    if r["deals"] != 1:
        problems.append(f"{r['deals']} deals, expected 1")
    if r["positions"] != 1:
        problems.append(f"{r['positions']} positions, expected 1")
    if r["margin_used"] <= 0:
        problems.append("margin_used == 0 with an open position  <-- D8b")
    if r["margin_reserved"] != 0:
        problems.append(f"reservation {r['margin_reserved']} still held after the fill")
    return problems


async def main():
    print("=" * 78)
    print("D8b reproduction: A-Book margin against the REAL Sql* repositories")
    print("=" * 78)
    print(f"  symbol={SYMBOL} volume={VOLUME} bid={BID} ask={ASK} loops={LOOPS}")
    print(f"  persistence: SQLite, the same Sql* repositories and mappers as PostgreSQL\n")
    bad = 0
    for n in range(1, LOOPS + 1):
        try:
            r = await one_loop(n)
        except Exception as exc:
            import traceback
            print(f"  loop {n}: RAISED {type(exc).__name__}: {exc}")
            traceback.print_exc()
            bad += 1
            continue
        problems = verdict(r)
        flag = "OK  " if not problems else "BAD "
        print(f"  loop {n} {flag} state={r['state']:<8} deals={r['deals']} pos={r['positions']} "
              f"margin_used={r['margin_used']} reserved={r['margin_reserved']} "
              f"level={r['margin_level']}")
        for p in problems:
            print(f"          ! {p}")
        if problems:
            bad += 1
    print("\n" + "=" * 78)
    print(f" {LOOPS - bad}/{LOOPS} loops clean, {bad} reproduced a problem")
    print("=" * 78)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
