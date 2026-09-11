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
def sync(node_id: str = typer.Option(..., "--node-id", "-n"), force: bool = typer.Option(False, "--force", "-f")) -> None:
    """Cluster synchronisation. NOT IMPLEMENTED - infrastructure/cluster/ is empty."""
    _not_built("cluster sync")


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
