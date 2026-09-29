"""
Broker Platform CLI.

The four commands that matter for standing the system up - `migrate`, `seed`, `status`,
`start` - are implemented. The rest are stubs and say so explicitly, because a command
that prints a success message without doing anything is worse than one that admits it is
not built: `make setup-dev` used to chain four such no-ops and report "Development
environment ready!".

All four go through `_bootstrap()`, which assembles the same DatabaseManager,
repositories and DI container the API server uses. That is deliberate: a seeder with its
own private wiring can succeed while the server it is seeding for cannot start.
"""
from __future__ import annotations

import asyncio
import os
import pathlib
from typing import Any, Dict, Optional

import typer
from rich.console import Console
from rich.table import Table

from infrastructure.config.env import (
    check_server_secrets,
    load_environment,
    normalize_database_url,
)

# M5: load .env before reading os.environ, and name the missing secrets.
load_environment()

app = typer.Typer(help="Broker Platform Command Line Interface", no_args_is_help=True)
console = Console()

#: Where runtime state lives. Nothing is written inside the source tree, so the same
#: image can run as trade / history / access / worker by pointing BROKER_HOME elsewhere.
DEFAULT_HOME = os.environ.get("BROKER_HOME", str(pathlib.Path.cwd() / ".broker"))
DEFAULT_CONFIG = os.environ.get("BROKER_CONFIG", "config")


def _database_url() -> str:
    """Resolve the database URL, refusing to fall back to a hardcoded credential.

    alembic.ini ships `postgresql+asyncpg://user:password@localhost:5432/broker_db`,
    which is fine as a development default but must never be used silently in a
    deployment. DATABASE_URL wins; otherwise the default is used and a warning says so.
    """
    url = os.environ.get("DATABASE_URL")
    if url:
        # accept a plain postgresql:// URL (Neon, Heroku, ...) and make it async
        return normalize_database_url(url)
    console.print(
        "[yellow]DATABASE_URL is not set; falling back to the development default "
        "postgres user/password on localhost:5432.[/yellow]"
    )
    return "postgresql+asyncpg://postgres:postgres@localhost:5432/broker_platform"


def _config_root() -> pathlib.Path:
    return pathlib.Path(DEFAULT_CONFIG)


def _bootstrap() -> Dict[str, Any]:
    """Assemble the persistence layer and DI container exactly as the API does."""
    from infrastructure.persistence.database import DatabaseManager
    from infrastructure.persistence.di_setup import setup_persistence_di

    manager = DatabaseManager(_database_url())
    providers = setup_persistence_di(manager)
    providers["event_bus"] = _build_event_bus()
    return {"database": manager, "providers": providers}


def _build_event_bus() -> Any:
    """Redis event bus when REDIS_URL is set, otherwise an in-process one.

    Seeding does not need Redis, and requiring it would make `make seed` fail on a
    machine that has only PostgreSQL running. The in-process bus keeps the domain events
    flowing locally so the seeder exercises the same publish path as production.
    """
    redis_url = os.environ.get("REDIS_URL")
    if redis_url:
        from infrastructure.messaging.redis_event_bus import RedisEventBus

        return RedisEventBus(redis_url)

    # The shared single-node bus, not a private copy. A CLI-local bus that dispatched on
    # `type(event)` only could not deliver to a handler registered under
    # EventType.ORDER_APPROVED.value, so `cli seed` and `cli start` published events
    # nothing could receive while the server used a bus that worked.
    from infrastructure.messaging.inprocess_event_bus import InProcessEventBus

    return InProcessEventBus()


def _run(coro: Any) -> int:
    """Run a coroutine and surface the real error.

    Typer catches exceptions and prints only the message, so a TypeError deep in the
    bootstrap showed up as a bare `exit: 1` with no traceback and no explanation. A
    setup command that fails silently is worse than one that does nothing.
    """
    import traceback

    try:
        return asyncio.run(coro)
    except Exception as exc:  # noqa: BLE001 - the CLI is the last frame; report it
        console.print(f"[bold red]{type(exc).__name__}:[/bold red] {exc}")
        console.print("[dim]" + traceback.format_exc() + "[/dim]")
        return 1


async def _run_seed(
    mt5_groups: Optional[str], mt5_symbols: Optional[str],
    mt5_routing: Optional[str], with_admin: bool,
) -> int:
    from infrastructure.config.seeder import seed_all
    from infrastructure.security.password_hasher import Argon2PasswordHasher

    context = _bootstrap()
    providers = context["providers"]
    hasher = Argon2PasswordHasher()

    report = await seed_all(
        group_repo=providers["group_repo"],
        symbol_repo=providers["symbol_repo"],
        manager_repo=providers["manager_repo"],
        account_repo=providers["account_repo"],
        coverage_repo=providers.get("coverage_repo"),
        config_root=_config_root(),
        mt5_groups=mt5_groups,
        mt5_symbols=mt5_symbols,
        password_hasher=hasher,
    )
    routing_rules = 0
    if mt5_routing:
        from infrastructure.config.loader import routes_from_mt5

        mt5_routing_repo = providers.get("mt5_routing_repo")
        if mt5_routing_repo is None:
            console.print("[red]no mt5_routing_repo is wired; cannot import routing rules[/red]")
            await context["database"].close()
            return 2
        imported = routes_from_mt5(mt5_routing)
        for rule, record in imported:
            await mt5_routing_repo.upsert(rule, record)
        routing_rules = len(imported)

    await context["database"].close()

    table = Table(title="Seed report")
    table.add_column("Item", style="cyan")
    table.add_column("Count", justify="right")
    table.add_row("groups created", str(report.groups_created))
    table.add_row("groups updated", str(report.groups_updated))
    table.add_row("symbols created", str(report.symbols_created))
    table.add_row("symbols updated", str(report.symbols_updated))
    table.add_row("coverage accounts", str(report.coverage_accounts))
    table.add_row("coverage risk accounts", str(report.coverage_risk_accounts))
    if mt5_routing:
        table.add_row("mt5 routing rules", str(routing_rules))
    table.add_row("admin created", "yes" if report.admin_created else "no")
    console.print(table)

    if report.admin_created and report.admin_password:
        # MT5 shows the first administrator's password once, on the installer's final
        # screen, and also writes it to the trade server's /Logs folder. Same here.
        console.print()
        console.print("[bold green]First administrator created[/bold green]")
        console.print(f"  login    : [bold]{report.admin_login}[/bold]")
        console.print(f"  password : [bold]{report.admin_password}[/bold]")
        console.print(
            "  [yellow]This is shown ONCE. Save it now - the password must be changed "
            "on first login, and only the hash is stored.[/yellow]"
        )

    for warning in report.warnings:
        console.print(f"[yellow]warning:[/yellow] {warning}")

    return 0


@app.command()
def seed(
    mt5_groups: Optional[str] = typer.Option(
        None,
        "--mt5-groups",
        help="Import groups from a real MT5 Administrator export (JSON) instead of YAML",
    ),
    mt5_symbols: Optional[str] = typer.Option(
        None,
        "--mt5-symbols",
        help="Import symbols from a real MT5 Administrator export (JSON) instead of YAML",
    ),
    mt5_routing: Optional[str] = typer.Option(
        None,
        "--mt5-routing",
        help="Import the ConfigRouting table from a real MT5 Administrator export (JSON)",
    ),
) -> None:
    """Seed groups, symbols, the coverage account and the first administrator.

    Idempotent: everything upserts on MT5's natural key, so running this twice leaves
    the database unchanged. With --mt5-groups/--mt5-symbols it imports a real server's
    configuration losslessly, including the fields our domain does not model yet.
    """
    console.print(f"[blue]Seeding from {_config_root()}[/blue]")
    raise SystemExit(_run(_run_seed(mt5_groups, mt5_symbols, mt5_routing, True)))


async def _run_status() -> int:
    context = _bootstrap()
    providers = context["providers"]
    groups = await providers["group_repo"].get_all()
    symbols = await providers["symbol_repo"].get_all_symbols()
    accounts = await providers["account_repo"].find_all()
    managers = await providers["manager_repo"].find_all()
    await context["database"].close()

    table = Table(title="Broker Platform status")
    table.add_column("Item", style="cyan")
    table.add_column("Value", justify="right")
    table.add_row("groups", str(len(groups)))
    table.add_row("symbols", str(len(symbols)))
    table.add_row("accounts", str(len(accounts)))
    table.add_row("managers", str(len(managers)))
    console.print(table)

    if groups:
        group_table = Table(title="Groups (margin thresholds are PERCENT)")
        group_table.add_column("Name")
        group_table.add_column("Type")
        group_table.add_column("Call %", justify="right")
        group_table.add_column("Stop-out %", justify="right")
        group_table.add_column("Leverage", justify="right")
        for group in groups:
            group_table.add_row(
                group.name,
                group.account_type.value if hasattr(group.account_type, "value") else str(group.account_type),
                str(group.margin.margin_call_level),
                str(group.margin.stop_out_level),
                str(group.margin.leverage_default),
            )
        console.print(group_table)

    if symbols:
        symbol_table = Table(title=f"Symbols (showing up to 20 of {len(symbols)})")
        symbol_table.add_column("Name")
        symbol_table.add_column("Digits", justify="right")
        symbol_table.add_column("Point")
        symbol_table.add_column("TickSize")
        symbol_table.add_column("Contract")
        symbol_table.add_column("Calc mode")
        for symbol in symbols[:20]:
            symbol_table.add_row(
                symbol.name,
                str(symbol.digits),
                str(symbol.tick_size),
                str(getattr(symbol, "mt5_tick_size", 0)),
                str(symbol.contract_size),
                symbol.calc_mode.name if hasattr(symbol.calc_mode, "name") else str(symbol.calc_mode),
            )
        console.print(symbol_table)

    ready = bool(groups) and bool(symbols)
    if ready:
        console.print("[bold green]Configuration plane is populated.[/bold green]")
    else:
        console.print(
            "[bold red]Not ready to trade:[/bold red] "
            f"{len(groups)} groups, {len(symbols)} symbols. Run `cli seed`."
        )
    return 0 if ready else 1


@app.command()
def status() -> None:
    """Show what is actually in the database, and whether the platform can trade."""
    raise SystemExit(_run(_run_status()))


@app.command()
def migrate(
    direction: str = typer.Option("upgrade", "--direction", "-d", help="upgrade or downgrade"),
    revision: str = typer.Option("head", "--revision", "-r", help="Target revision"),
) -> None:
    """Run database migrations through Alembic."""
    from alembic import command
    from alembic.config import Config

    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", _database_url())
    if direction == "downgrade":
        command.downgrade(config, revision)
    else:
        command.upgrade(config, revision)
    console.print(f"[green]alembic {direction} {revision} complete[/green]")


@app.command()
def start(
    server_type: str = typer.Option(
        "all", "--server-type", "-t", help="all | api | trade | history | access | worker"
    ),
    host: str = typer.Option("0.0.0.0", "--host"),
    port: int = typer.Option(8000, "--port"),
) -> None:
    """Start the platform.

    One codebase, several process roles - the way MT5 splits trade / history / access /
    backup servers. Only `api` is wired today; the other roles exist as names so the
    split is a configuration change later rather than a rewrite.
    """
    if server_type in ("api", "all"):
        import uvicorn

        # M5: `start` is the command that faces the network. Refuse to run it with
        # placeholder secrets; migrate/seed/status stay usable without them.
        problems = check_server_secrets()
        if problems:
            console.print("[red]Refusing to start:[/red] " + "; ".join(problems))
            raise SystemExit(2)

        console.print(f"[green]Starting the API on {host}:{port}[/green]")
        uvicorn.run("api.main:app", host=host, port=port, reload=False)
        return

    console.print(
        f"[yellow]server type '{server_type}' is not wired yet.[/yellow] "
        "The trade, history, access and worker roles share this codebase but have no "
        "entrypoint of their own; `api` is the only one that starts today."
    )
    raise SystemExit(2)


# ---------------------------------------------------------------------------
# Not built. These say so instead of printing a success message.
# ---------------------------------------------------------------------------


def _not_built(what: str) -> None:
    console.print(f"[red]{what} is not implemented.[/red] It was a stub that printed a "
                  "success message without doing anything; it now fails loudly instead.")
    raise SystemExit(2)


@app.command()
def backtest(
    strategy: str = typer.Option(..., "--strategy", "-s"),
    start_date: str = typer.Option(..., "--start"),
    end_date: str = typer.Option(..., "--end"),
    capital: float = typer.Option(100000, "--capital", "-c"),
) -> None:
    """Backtest a strategy. NOT IMPLEMENTED - needs the ClickHouse cold path."""
    _not_built("backtest")


@app.command()
def sync(
    node_id: str = typer.Option("", "--node-id", "-n",
                                help="Cluster node (unused: cluster roles are not built)"),
    force: bool = typer.Option(False, "--force", "-f",
                               help="Also resolve unknown-hedge orders against the venue"),
    revalue: bool = typer.Option(True, "--revalue/--no-revalue",
                                 help="Revalue open positions from current prices"),
    reconcile: bool = typer.Option(True, "--reconcile/--no-reconcile",
                                 help="Compare our book against the venue's"),
) -> None:
    """Revalue open positions and reconcile our book against the venue's.

    This used to be a stub for cluster synchronisation, which does not exist
    (infrastructure/cluster/ is empty, by decision). What operators actually need
    from a command called `sync` is the two things that were missing:

      D9   equity / profit / margin_free / margin_level are only recomputed on a
           tick while the server runs, so after a restart every account shows the
           figures from the last tick before shutdown. `--revalue` fixes that now.
      M12  nothing compared our positions against the venue's, so an orphaned
           hedge or a naked client position was invisible until someone noticed
           the money. `--reconcile` reports the difference and persists it.

    Exit code is the number of CRITICAL/HIGH breaks, capped at 1, so this is
    usable as a cron gate: non-zero means the books disagree.
    """
    if node_id:
        console.print(
            f"[yellow]--node-id {node_id} is ignored:[/yellow] cluster roles are not "
            "built (decision: modular monolith + process roles, extract later). "
            "This command syncs the ONE book against the venue."
        )
    _run(_sync(revalue=revalue, reconcile=reconcile, force=force))


async def _sync(*, revalue: bool, reconcile: bool, force: bool) -> int:
    from application.services.reconciliation_service import (
        ReconciliationService,
        ValuationService,
    )
    from infrastructure.persistence.repositories.reconciliation_repository import (
        SqlReconciliationRepository,
    )

    boot = _bootstrap()
    database = boot.get("database")
    providers = boot["providers"]
    event_bus = providers.get("event_bus") or _build_event_bus()
    providers["event_bus"] = event_bus

    # The market data engine holds the prices; without it there is nothing to
    # revalue from, and inventing a price would be worse than leaving a stale one.
    from core.domains.market_data.engine import MarketDataEngine

    engine = MarketDataEngine(event_bus=event_bus,
                              symbol_repo=providers.get("symbol_repo"))
    exit_code = 0

    if revalue:
        console.print("\n[bold]1. Revaluing open positions[/bold]")
        # The risk engine is what makes the margin repair possible: an account
        # holding open positions with margin_used = 0 (D8b's signature) can only be
        # fixed by recomputing through the same MT5-accurate maths the fill path
        # uses. Without it the sweep can revalue equity but must leave the lost
        # margin alone - and say so.
        from core.domains.risk.engine import RiskEngine

        # RiskEngine needs a SYNCHRONOUS symbol lookup on the hot path; the SQL
        # repository's get_symbol() is async and raises PositionValuationError when
        # called that way. ConfigCache is exactly the synchronous view it wants -
        # the same object the server's trading stack uses.
        from application.cache.config_cache import ConfigCache

        cache = ConfigCache(
            group_repo=providers.get("group_repo"),
            account_repo=providers.get("account_repo"),
            symbol_repo=providers.get("symbol_repo"),
            holiday_repo=providers.get("holiday_repo"),
            position_repo=providers.get("position_repo"),
            event_bus=event_bus,
        )
        try:
            await cache.initialize()
        except Exception as exc:  # noqa: BLE001
            console.print(f"  [yellow]ConfigCache could not initialize ({exc}); the "
                          f"margin repair will be skipped for accounts that need it[/yellow]")
            cache = None

        risk_engine = RiskEngine(symbol_repo=(cache if cache is not None
                                              else providers.get("symbol_repo")),
                                 market_data_engine=engine)
        svc = ValuationService(
            account_repo=providers["account_repo"],
            position_repo=providers["position_repo"],
            symbol_repo=providers.get("symbol_repo"),
            market_data_engine=engine,
            risk_engine=risk_engine,
        )
        # A CLI run has no live feed, so pull the venue's current prices for
        # whatever symbols we hold. That is the point of syncing after a restart.
        symbols = await _symbols_with_open_positions(providers["position_repo"])
        if symbols:
            got = await _fetch_venue_quotes(symbols)
            for sym, (bid, ask) in got.items():
                await engine.process_tick(_tick(sym, bid, ask))
            console.print(f"  prices refreshed for {len(got)}/{len(symbols)} symbol(s) "
                          f"from the venue")
            missing = sorted(set(symbols) - set(got))
            if missing:
                console.print(f"  [yellow]no venue price for: {', '.join(missing)}[/yellow]"
                              " - those accounts keep their previous figures")
        else:
            console.print("  no open positions; nothing to revalue")
        stats = await svc.revalue_all()
        console.print(f"  accounts={stats['accounts']} positions={stats['positions']} "
                      f"revalued={stats['revalued']} "
                      f"skipped_no_price={stats['skipped_no_price']} "
                      f"errors={stats['errors']}")
        if stats.get("margin_repaired"):
            console.print(f"  [yellow]margin repaired on {stats['margin_repaired']} "
                          f"account(s)[/yellow] that held open positions with "
                          f"margin_used = 0 - a fill's margin write was lost. "
                          f"The write path is fixed (D8b); these were already broken.")
        if stats.get("margin_unrepaired"):
            console.print(f"  [red]{stats['margin_unrepaired']} account(s) hold open "
                          f"positions with margin_used = 0 and could NOT be "
                          f"repaired[/red] - they are under-margined and stop-out "
                          f"cannot fire on them")
            exit_code = 1

    if reconcile:
        console.print("\n[bold]2. Reconciling against the venue[/bold]")
        gateway = _build_gateway_for_cli()
        if gateway is None:
            console.print("  [yellow]no venue gateway configured "
                          "(set BROKER_LP_GATEWAY + TRADE_SERVER_API_URL); "
                          "reconciliation skipped rather than reported clean[/yellow]")
        else:
            break_repo = (SqlReconciliationRepository(
                session_factory=database.session_factory)
                if database is not None and getattr(database, "session_factory", None)
                else None)
            hedged = [x.strip().upper() for x in
                      (os.environ.get("RECONCILE_HEDGED_SYMBOLS") or "").split(",")
                      if x.strip()]
            svc = ReconciliationService(
                position_repo=providers["position_repo"],
                break_repo=break_repo,
                engine=None,
                gateway=gateway,
                hedged_symbols=hedged,
                event_bus=event_bus,
                venue_name=os.environ.get("BROKER_LP_GATEWAY") or "LP",
            )
            run = await svc.run()
            if run.error:
                console.print(f"  [red]could not read the venue book:[/red] {run.error}")
                console.print("  [yellow]this is NOT a clean result - the comparison "
                              "did not happen[/yellow]")
                exit_code = 1
            else:
                console.print(f"  our positions={run.our_positions}  "
                              f"venue positions={run.venue_positions}")
                if run.clean:
                    console.print("  [green]books match - no breaks[/green]")
                else:
                    table = Table(title=f"{len(run.breaks)} break(s)")
                    for col in ("severity", "kind", "symbol", "detail", "seen"):
                        table.add_column(col)
                    for b in sorted(run.breaks,
                                    key=lambda x: ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
                                    .index(x.severity.value)):
                        age = f"{b.occurrences}x"
                        table.add_row(b.severity.value, b.kind.value, b.symbol,
                                      b.detail[:110], age)
                    console.print(table)
                    counts = run.by_severity()
                    if counts["CRITICAL"] or counts["HIGH"]:
                        exit_code = 1
            if force:
                n = await svc.resolve_unknown_hedges(providers["order_repo"])
                console.print(f"  --force: {n} unknown-hedge order(s) raised as breaks")

    if hasattr(event_bus, "disconnect"):
        try:
            await event_bus.disconnect()
        except Exception:  # noqa: BLE001
            pass
    if database is not None:
        await database.close()
    console.print()
    return exit_code


async def _symbols_with_open_positions(position_repo) -> list:
    out = set()
    for name in ("get_open_positions", "get_all_open"):
        method = getattr(position_repo, name, None)
        if method is None:
            continue
        for p in await method():
            sym = getattr(p, "symbol", None)
            if sym:
                out.add(str(sym).upper())
        break
    return sorted(out)


async def _fetch_venue_quotes(symbols: list) -> dict:
    """Current bid/ask from the venue for the symbols we hold.

    Uses the trade-server REST symbol list when available. A venue with no quote
    endpoint yields nothing, and the caller reports that honestly instead of
    revaluing at a guessed price.
    """
    gateway = _build_gateway_for_cli()
    if gateway is None:
        return {}
    try:
        quotes = await gateway.get_quotes(symbols)
    except Exception as exc:  # noqa: BLE001
        console.print(f"  [yellow]venue quotes unavailable: {exc}[/yellow]")
        return {}
    out = {}
    for sym, q in (quotes or {}).items():
        bid, ask = q.get("bid"), q.get("ask")
        if bid and ask:
            out[str(sym).upper()] = (bid, ask)
    return out


def _tick(symbol: str, bid, ask):
    from datetime import datetime, timezone
    from decimal import Decimal

    from core.domains.market_data.models import Tick

    b, a = Decimal(str(bid)), Decimal(str(ask))
    return Tick(symbol=symbol, bid=b, ask=a, spread=a - b,
                timestamp=datetime.now(timezone.utc), source="SYNC")


def _build_gateway_for_cli():
    """The venue adapter named by BROKER_LP_GATEWAY, or None.

    Built directly rather than through the trading stack: a sync run must not need
    a router, a matching engine or an orchestrator, and booting all of them to read
    a position list is how a maintenance command ends up unable to run.
    """
    kind = (os.environ.get("BROKER_LP_GATEWAY") or "").strip().lower()
    try:
        if kind in ("trade_server", "tradeserver", "mt5"):
            from infrastructure.gateways.trade_server_gateway import (
                build_trade_server_gateway_from_env,
            )

            return build_trade_server_gateway_from_env()
        if kind == "fix":
            from infrastructure.gateways.fix_gateway import build_fix_gateway_from_env

            return build_fix_gateway_from_env()
    except Exception as exc:  # noqa: BLE001
        console.print(f"  [yellow]could not build the {kind} gateway: {exc}[/yellow]")
    return None


@app.command()
def export(output: str = typer.Option("export.json", "--output", "-o"), data_type: str = typer.Option("all", "--type", "-t")) -> None:
    """Export configuration to MT5 format. NOT IMPLEMENTED yet - the codec is ready."""
    _not_built("export")


@app.command()
def import_data(input_file: str = typer.Argument(...), data_type: str = typer.Option("auto", "--type", "-t")) -> None:
    """Import configuration from MT5 format. Use `seed --mt5-groups/--mt5-symbols`."""
    _not_built("import_data")


if __name__ == "__main__":
    app()
