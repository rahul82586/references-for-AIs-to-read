import io

p = "api/main.py"
s = io.open(p, encoding="utf-8", newline="").read()
crlf = "\r\n" in s


def N(x):
    return x.replace("\n", "\r\n") if crlf else x


# --- 1. a default container, so `uvicorn api.main:app` is a real server ------
old = N('''def create_app(container: Optional[Dict[str, Any]] = None) -> FastAPI:
    """FastAPI application factory function."""
    if container:
        register_di_providers(container)
''')
assert old in s
new = N('''def default_providers() -> Dict[str, Any]:
    """Build the persistence providers and an event bus, exactly as the CLI does.

    `cli start` runs `uvicorn api.main:app`, and the module-level `app = create_app()`
    at the bottom of this file passed NO container - so the process-wide provider dict
    was empty and startup died with KeyError('IGroupRepository'). The one command that
    is supposed to start the platform could not. Assembling the providers here does not
    connect to anything (DatabaseManager only builds an engine and a session factory),
    so importing this module stays side-effect free; the first query is what needs a
    reachable database, and that now fails with a database error instead of a confusing
    complaint about a missing repository.

    Shared with cli/main.py's _bootstrap() so a seeder and the server it seeds for
    cannot drift apart.
    """
    import os

    from infrastructure.persistence.database import DatabaseManager
    from infrastructure.persistence.di_setup import setup_persistence_di

    url = os.environ.get("DATABASE_URL")
    if not url:
        logger.warning(
            "DATABASE_URL is not set; using the development default "
            "postgres user/password on localhost:5432"
        )
        url = "postgresql+asyncpg://postgres:postgres@localhost:5432/broker_platform"

    manager = DatabaseManager(url)
    providers = setup_persistence_di(manager)

    redis_url = os.environ.get("REDIS_URL")
    if redis_url:
        from infrastructure.messaging.redis_event_bus import RedisEventBus

        providers["event_bus"] = RedisEventBus(redis_url)
    else:
        from infrastructure.messaging.inprocess_event_bus import InProcessEventBus

        providers["event_bus"] = InProcessEventBus()

    providers["database"] = manager
    return providers


def create_app(container: Optional[Dict[str, Any]] = None) -> FastAPI:
    """FastAPI application factory function."""
    if not container:
        container = default_providers()
    register_di_providers(container)
''')
s = s.replace(old, new, 1)

# --- 2. close the engine on shutdown ----------------------------------------
old = N('''        event_bridge = getattr(app.state, "event_bridge", None)
        if event_bridge:''')
assert old in s
new = N('''        database = _container_lookup("database")
        if database is not None and hasattr(database, "close"):
            try:
                await database.close()
                logger.info("✅ Database engine disposed")
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Error closing the database engine: {e}")

        event_bridge = getattr(app.state, "event_bridge", None)
        if event_bridge:''')
s = s.replace(old, new, 1)

# --- 3. small accessor for the shutdown hook --------------------------------
old = N('''def default_providers() -> Dict[str, Any]:''')
assert old in s
new = N('''def _container_lookup(key: str) -> Any:
    """Read a key from the process-wide provider dict without raising."""
    try:
        return get_di_container().get(key)
    except Exception:  # noqa: BLE001
        return None


def default_providers() -> Dict[str, Any]:''')
s = s.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="").write(s)
print("api/main: default providers; crlf =", crlf)
