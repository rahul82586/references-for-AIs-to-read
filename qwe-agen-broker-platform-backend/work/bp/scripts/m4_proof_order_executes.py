"""
M4 proof: does an order actually execute?

Every earlier milestone proved a layer. M0 proved the code imports, M1 proved the MT5
file format survives a round trip, M2 proved the configuration plane seeds and reads
back, M3 proved the risk maths matches MT5's own published examples. None of them
placed an order.

This proof places one, against the REAL persistence layer - SQLite standing in for
PostgreSQL, but the same SqlAccountRepository, SqlOrderRepository, SqlDealRepository,
SqlPositionRepository and SqlCoverageAccountRepository, the same mappers, the same
single Base.metadata schema, and the same configuration the seeder loads from config/.
That matters because two of the defects this milestone found only exist against real
repositories: their doubles in the unit tests happened to define the method names the
production code probes for, and the production repositories did not.

What it proves, in order:

  1. the platform assembles: seeder -> ConfigCache -> trading stack, with no mocks;
  2. a market BUY fills at the ASK, and the order, deal and position are all real rows;
  3. account margin is 110.01 USD read back FROM THE DATABASE - MT5 stage 1 (100 EUR)
     converted at the ask, not the bid and not 1.0;
  4. a second order recomputes margin over BOTH positions (330.03). This is the
     regression guard for the defect that wrote margin_used = 0 after every fill:
     `_recalculate_account_margin` probed the position repository for method names the
     SQL repository did not have and silently fell back to an empty list;
  5. the broker's own exposure moves the right way: client buys, broker is short;
  6. a pending order rests instead of filling, then activates when the market reaches
     it - and only then does the exposure move;
  7. an order routed A-Book with no liquidity provider connected is REJECTED rather
     than reported as hedged;
  8. an order too large for the account's free margin is rejected and books nothing.

Exit codes: 0 passed, 1 failed, 2 skipped because the FX market is closed (the seeded
EURUSD sessions are Monday-Friday, which is correct MT5 behaviour and would make this
proof fail confusingly on a weekend).

Run:
    PYTHONPATH=work/bp python3 scripts/m4_proof_order_executes.py work/bp
"""

from __future__ import annotations

import asyncio
import pathlib
import sys
import tempfile
from datetime import datetime, timezone
from decimal import Decimal

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
sys.path.insert(0, str(ROOT))

# --- JSONB -> JSON so SQLite can create the tables ---------------------------
# A test-harness accommodation, exactly as in the M2 proof. Production runs
# PostgreSQL, where JSONB is native.
from sqlalchemy.dialects.postgresql import JSONB  # noqa: E402
from sqlalchemy.ext.compiler import compiles  # noqa: E402


@compiles(JSONB, "sqlite")
def _compile_jsonb_sqlite(type_, compiler, **kw):  # noqa: ANN001
    return "JSON"


import os  # noqa: E402

os.chdir(ROOT)

from application.cache.config_cache import ConfigCache, set_config_cache  # noqa: E402
from application.commands.create_order import CreateOrderCommand  # noqa: E402
from application.di.trading_setup import build_trading_stack  # noqa: E402
from core.domains.accounts.account import Account  # noqa: E402
from core.domains.common.value_objects import Money  # noqa: E402
from core.domains.market_data.engine import MarketDataEngine  # noqa: E402
from core.domains.market_data.models import Tick  # noqa: E402
from core.domains.oms.enums import DealType, OrderState, OrderType, PositionAction  # noqa: E402
from core.events.domain_events import EventType  # noqa: E402
from infrastructure.config.seeder import seed_all  # noqa: E402
from infrastructure.messaging.inprocess_event_bus import InProcessEventBus  # noqa: E402
from infrastructure.persistence.database import Base, DatabaseManager  # noqa: E402
import infrastructure.persistence.db_models  # noqa: F401,E402  (registers every table)
from infrastructure.persistence.di_setup import setup_persistence_di  # noqa: E402
from infrastructure.security.password_hasher import Argon2PasswordHasher  # noqa: E402

FAILURES: list[str] = []
STEP = 0


def step(title: str) -> None:
    global STEP
    STEP += 1
    print(f"\n[{STEP}] {title}")


def report(ok: bool, claim: str, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"    [{mark}] {claim}" + (f"  {detail}" if detail else ""))
    if not ok:
        FAILURES.append(claim)


def money(value) -> Decimal:
    return value.amount if hasattr(value, "amount") else Decimal(str(value))


BID = Decimal("1.10000")
ASK = Decimal("1.10010")
LOGIN = 900101
GROUP = "demo\\Standard"


async def main() -> int:
    tmp = tempfile.mkdtemp(prefix="broker-m4-")
    url = f"sqlite+aiosqlite:///{pathlib.Path(tmp) / 'broker.db'}"
    print("=== M4 proof: does an order actually execute? ===")
    print(f"    persistence : {url}")
    print(f"    repositories: the real Sql* ones, not doubles")

    manager = DatabaseManager(url)
    await manager.create_tables()
    providers = setup_persistence_di(manager)
    bus = InProcessEventBus()
    providers["event_bus"] = bus

    # ------------------------------------------------------------------
    step("seed the configuration plane from config/ (the same files `cli seed` uses)")
    seeded = await seed_all(
        group_repo=providers["group_repo"],
        symbol_repo=providers["symbol_repo"],
        manager_repo=providers["manager_repo"],
        account_repo=providers["account_repo"],
        coverage_repo=providers["coverage_repo"],
        config_root="config",
        password_hasher=Argon2PasswordHasher(),
    )
    groups = await providers["group_repo"].get_all()
    symbols = await providers["symbol_repo"].get_all_symbols()
    report(len(groups) >= 7, "groups seeded", f"{len(groups)}")
    report(len(symbols) >= 5, "symbols seeded", f"{len(symbols)}")
    report(
        seeded.coverage_risk_accounts == 1,
        "the DEFAULT_COVERAGE risk account exists",
        "B-Book exposure has somewhere to be booked",
    )

    group = await providers["group_repo"].find_by_name(GROUP)
    eurusd = await providers["symbol_repo"].find_by_name("EURUSD")
    report(group is not None, f"group {GROUP!r} loaded from the database")
    report(eurusd is not None, "symbol EURUSD loaded from the database")
    if group is None or eurusd is None:
        print("\n=== M4 proof FAILED: configuration did not seed ===")
        return 1

    # ------------------------------------------------------------------
    step("market hours")
    now = datetime.now(timezone.utc)
    if not eurusd.is_trade_session_active(now):
        print(
            f"\n=== M4 proof SKIPPED: EURUSD is outside its trading session "
            f"({now:%A %H:%M} UTC) ===\n"
            "The seeded sessions are Monday-Friday, which is correct MT5 behaviour.\n"
            "Re-run on a weekday; nothing is broken."
        )
        await manager.close()
        return 2
    report(True, "EURUSD session is open", f"{now:%A %H:%M} UTC")
    report(
        group.margin.margin_call_level == Decimal("10"),
        f"{GROUP} margin call level is 10 PERCENT",
        f"stop out {group.margin.stop_out_level}",
    )

    # ------------------------------------------------------------------
    step("open a trading account with 10,000 USD, through the real repository")
    account = Account(
        login=LOGIN,
        client_id="CLIENT_M4",
        group=group,
        group_id=group.id,
        currency="USD",
        balance=Money(Decimal("10000"), "USD"),
        credit=Money(Decimal("0"), "USD"),
        equity=Money(Decimal("10000"), "USD"),
        margin_used=Money(Decimal("0"), "USD"),
        margin_free=Money(Decimal("10000"), "USD"),
    )
    await providers["account_repo"].save(account)
    # accounts.login is a String(32) primary key; the domain uses an int everywhere else.
    # Reading it back is what proves the coercion at that boundary works in both
    # directions - a mismatch here returns None, and the whole path dies with
    # "Account not found".
    reread = await providers["account_repo"].find_by_login(LOGIN)
    report(reread is not None, "the account reads back by its int login", f"login={LOGIN}")
    report(
        reread is not None and reread.group is not None,
        "its group came back with it",
        GROUP if reread and reread.group else "",
    )
    if reread is None:
        print("\n=== M4 proof FAILED: account round trip ===")
        await manager.close()
        return 1

    # ------------------------------------------------------------------
    step("assemble the trading plane (no mocks anywhere below this line)")
    engine = MarketDataEngine(event_bus=bus, symbol_repo=providers["symbol_repo"])
    cache = ConfigCache(
        group_repo=providers["group_repo"],
        account_repo=providers["account_repo"],
        symbol_repo=providers["symbol_repo"],
        holiday_repo=providers["holiday_repo"],
        position_repo=providers["position_repo"],
        event_bus=bus,
    )
    await cache.initialize()
    set_config_cache(cache)

    providers["market_data_engine"] = engine
    stack = await build_trading_stack(providers, market_data_engine=engine, config_cache=cache)
    report(stack.orchestrator is not None, "ExecutionOrchestrator constructed")
    report(stack.router._rules_loaded, "SmartOrderRouter loaded its rule table")
    report(
        bus.handler_count(EventType.ORDER_APPROVED.value) == 1,
        "exactly one orchestrator is subscribed to ORDER_APPROVED",
        f"{bus.handler_count(EventType.ORDER_APPROVED.value)}",
    )
    for warning in stack.warnings:
        print(f"    [note] {warning}")

    # ------------------------------------------------------------------
    step("a price appears, and a client buys 0.10 lots of EURUSD")
    await engine.process_tick(
        Tick(symbol="EURUSD", bid=BID, ask=ASK, spread=ASK - BID, source="M4_PROOF")
    )
    report(engine.get_latest_tick("EURUSD") is not None, "the engine cached the tick")

    order = await stack.create_order_handler.handle(
        CreateOrderCommand(
            account_login=LOGIN, symbol="EURUSD", order_type=OrderType.BUY, volume=Decimal("0.10")
        )
    )
    report(order.state == OrderState.FILLED, "the order is FILLED", str(order.state))
    report(
        order.price_order.value == ASK,
        "it filled at the ASK, not the bid",
        f"{order.price_order.value} (bid was {BID})",
    )

    # ------------------------------------------------------------------
    step("the fill is real: rows in orders, deals and positions")
    db_order = await providers["order_repo"].find_by_id(order.ticket_id)
    report(db_order is not None, "the order row exists", f"ticket {order.ticket_id[:8]}")
    report(
        db_order is not None and db_order.state == OrderState.FILLED,
        "the order row says FILLED",
        str(db_order.state) if db_order else "",
    )

    deals = await providers["deal_repo"].find_by_account(LOGIN)
    report(len(deals) == 1, "exactly one deal row", f"{len(deals)}")
    if deals:
        report(deals[0].deal_type == DealType.BUY, "the deal is a BUY", deals[0].deal_type.value)
        report(deals[0].price.value == ASK, "the deal price is the ask", str(deals[0].price.value))

    positions = await providers["position_repo"].get_positions_by_account(LOGIN)
    report(len(positions) == 1, "exactly one open position row", f"{len(positions)}")
    if positions:
        report(
            positions[0].action == PositionAction.BUY,
            "the position side is PositionAction.BUY",
            "a DealType or OrderType here would fail every later comparison",
        )
        report(
            positions[0].price_open.value == ASK, "opened at the ask", str(positions[0].price_open.value)
        )

    # ------------------------------------------------------------------
    step("margin, read back from the database, to the cent")
    after_first = await providers["account_repo"].find_by_login(LOGIN)
    margin_1 = money(after_first.margin_used)
    # MT5 stage 1: 0.10 * 100,000 / 100 = 100 EUR
    # MT5 stage 2: margin currency EUR -> deposit USD at the ASK (a buy converts at the
    #              ask): 100 * 1.10010 = 110.01
    report(margin_1 == Decimal("110.01"), "margin_used is 110.01 USD", str(margin_1))
    report(
        margin_1 != Decimal("110.00"),
        "...and not 110.00, which is what converting at the bid would give",
    )
    report(
        money(after_first.equity) == Decimal("9999.00"),
        "equity is 9,999.00 - the client is down the spread",
        str(money(after_first.equity)),
    )

    # ------------------------------------------------------------------
    step("the broker's own exposure moved the other way")
    cov = await providers["coverage_repo"].find_by_id("DEFAULT_COVERAGE")
    exposure = cov.net_exposure.get("EURUSD", Decimal("0")) if cov else None
    report(exposure == Decimal("-0.10"), "coverage exposure is -0.10 (broker is SHORT)", str(exposure))

    # ------------------------------------------------------------------
    step("a second order: margin must recompute over BOTH positions")
    await stack.create_order_handler.handle(
        CreateOrderCommand(
            account_login=LOGIN, symbol="EURUSD", order_type=OrderType.BUY, volume=Decimal("0.20")
        )
    )
    after_second = await providers["account_repo"].find_by_login(LOGIN)
    margin_2 = money(after_second.margin_used)
    # (0.10 + 0.20) * 100,000 / 100 = 300 EUR, at the ask: 300 * 1.10010 = 330.03
    report(margin_2 == Decimal("330.03"), "margin_used is 330.03 USD", str(margin_2))
    report(margin_2 != Decimal("0"), "...and it is not 0")
    report(
        margin_2 > margin_1,
        "margin went UP when a position was added, not back to zero",
        f"{margin_1} -> {margin_2}",
    )
    open_now = await providers["position_repo"].get_positions_by_account(LOGIN)
    report(len(open_now) == 2, "two open positions in hedging mode", f"{len(open_now)}")
    cov = await providers["coverage_repo"].find_by_id("DEFAULT_COVERAGE")
    report(
        cov.net_exposure.get("EURUSD") == Decimal("-0.30"),
        "coverage exposure is now -0.30",
        str(cov.net_exposure.get("EURUSD")),
    )

    # ------------------------------------------------------------------
    step("a pending order rests, and does not move exposure until it fills")
    limit = await stack.create_order_handler.handle(
        CreateOrderCommand(
            account_login=LOGIN,
            symbol="EURUSD",
            order_type=OrderType.BUY_LIMIT,
            volume=Decimal("0.10"),
            price=Decimal("1.09000"),
        )
    )
    report(limit.state == OrderState.PLACED, "the limit order is PLACED, not filled", str(limit.state))
    report(
        stack.matching_engine.get_market_state("EURUSD")["resting_orders"] == 1,
        "it is resting in the book",
    )
    limit_deals = await providers["deal_repo"].find_by_order_id(limit.ticket_id)
    report(len(limit_deals) == 0, "it produced no deal yet", f"{len(limit_deals)}")
    cov = await providers["coverage_repo"].find_by_id("DEFAULT_COVERAGE")
    report(
        cov.net_exposure.get("EURUSD") == Decimal("-0.30"),
        "exposure did not move for a resting order",
        str(cov.net_exposure.get("EURUSD")),
    )

    await engine.process_tick(
        Tick(
            symbol="EURUSD",
            bid=Decimal("1.08900"),
            ask=Decimal("1.08910"),
            spread=Decimal("0.00010"),
            source="M4_PROOF",
        )
    )
    report(
        stack.matching_engine.get_market_state("EURUSD")["resting_orders"] == 0,
        "the market came down to it and it left the book",
    )
    limit_deals = await providers["deal_repo"].find_by_order_id(limit.ticket_id)
    report(len(limit_deals) == 1, "and it produced exactly one deal", f"{len(limit_deals)}")
    if limit_deals:
        report(
            limit_deals[0].price.value == Decimal("1.08910"),
            "filled at the better ask, not at the limit",
            str(limit_deals[0].price.value),
        )
    cov = await providers["coverage_repo"].find_by_id("DEFAULT_COVERAGE")
    report(
        cov.net_exposure.get("EURUSD") == Decimal("-0.40"),
        "exposure moved only on the fill: -0.40",
        str(cov.net_exposure.get("EURUSD")),
    )

    # ------------------------------------------------------------------
    step("an A-Book order with no liquidity provider connected must not fake a hedge")
    from core.domains.execution.models import ExecutionDestination, RoutingRule

    await providers["routing_rule_repo"].save(
        RoutingRule(
            rule_id="M4-A-BOOK",
            priority=500,
            destination=ExecutionDestination.A_BOOK,
            symbol_filter="GBP*",
            gateway_id="LP_NONE",
        )
    )
    await stack.router.refresh_rules()
    gbp = await providers["symbol_repo"].find_by_name("GBPUSD")
    if gbp is None:
        report(False, "GBPUSD is seeded, so the A-Book rule can be exercised")
    else:
        await engine.process_tick(
            Tick(
                symbol="GBPUSD",
                bid=Decimal("1.27000"),
                ask=Decimal("1.27010"),
                spread=Decimal("0.00010"),
                source="M4_PROOF",
            )
        )
        abook = await stack.create_order_handler.handle(
            CreateOrderCommand(
                account_login=LOGIN, symbol="GBPUSD", order_type=OrderType.BUY, volume=Decimal("0.10")
            )
        )
        report(abook.state == OrderState.REJECTED, "the A-Book order was REJECTED", str(abook.state))
        report(
            len(stack.liquidity_gateway.sent_orders) == 1,
            "...after genuinely attempting to send it",
            f"gateway {stack.liquidity_gateway.sent_orders[0]['gateway_id']}",
        )
        gbp_positions = [
            p for p in await providers["position_repo"].get_positions_by_account(LOGIN)
            if p.symbol == "GBPUSD"
        ]
        report(len(gbp_positions) == 0, "and no position was invented for it")

    # ------------------------------------------------------------------
    step("an order the account cannot margin is rejected and books nothing")
    before = await providers["account_repo"].find_by_login(LOGIN)
    balance_before = money(before.balance)
    positions_before = len(await providers["position_repo"].get_positions_by_account(LOGIN))
    try:
        await stack.create_order_handler.handle(
            CreateOrderCommand(
                account_login=LOGIN, symbol="EURUSD", order_type=OrderType.BUY, volume=Decimal("9.00")
            )
        )
        report(False, "a 9-lot order against the remaining free margin was refused")
    except ValueError as exc:
        report(True, "a 9-lot order against the remaining free margin was refused", str(exc)[:60])
    after = await providers["account_repo"].find_by_login(LOGIN)
    report(money(after.balance) == balance_before, "the balance did not move", str(money(after.balance)))
    report(
        len(await providers["position_repo"].get_positions_by_account(LOGIN)) == positions_before,
        "no position was opened",
        f"{positions_before}",
    )

    # ------------------------------------------------------------------
    step("event chain, in causal order")
    seen = [
        e.event_type.value if hasattr(e.event_type, "value") else str(e.event_type)
        for e in bus.published
    ]
    for expected in (
        EventType.ORDER_CREATED.value,
        EventType.ORDER_APPROVED.value,
        EventType.ORDER_ROUTED.value,
        EventType.DEAL_CREATED.value,
    ):
        report(expected in seen, f"{expected} was published")
    report(
        seen.index(EventType.ORDER_APPROVED.value) < seen.index(EventType.ORDER_ROUTED.value),
        "approval preceded routing",
    )
    # MarginCallEntered / StopOutEntered used to inherit DomainEvent's default
    # event_type, which is ORDER_CREATED - so a stop-out was published on the
    # "order.created" channel. In-process subscribers registered by class still heard
    # it, which is why nothing failed; Redis routes on the channel string, so across
    # processes the liquidation worker would never have been told.
    risk_events = [
        e for e in bus.published
        if type(e).__name__ in ("MarginCallEntered", "MarginCallExited", "StopOutEntered", "StopOutExited")
    ]
    report(
        all(e.event_type.value != EventType.ORDER_CREATED.value for e in risk_events),
        "no risk event travels on the order.created channel",
        f"{len(risk_events)} risk events observed",
    )

    await manager.close()

    print()
    if FAILURES:
        print(f"=== M4 proof FAILED: {len(FAILURES)} check(s) ===")
        for failure in FAILURES:
            print(f"  - {failure}")
        return 1
    print("=== M4 proof PASSED ===")
    print("An order placed against the real repositories fills at the correct side of the")
    print("spread, writes an order row, a deal row and a position row, recomputes account")
    print("margin over every open position, moves the broker's exposure the opposite way,")
    print("rests a pending order until the market reaches it, and refuses - rather than")
    print("fakes - an A-Book fill with no liquidity provider connected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
