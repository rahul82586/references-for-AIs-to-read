"""M5 deployment tests — no network, no Docker: pure units.

Covers the defects M5 found and fixed while standing the platform up on real
cloud infrastructure (Neon PostgreSQL 18.6, Upstash Redis over TLS):

1. `tick_from_event` dropped the PLAIN-DICT shape RedisEventBus delivers to
   cross-process subscribers — every tick over the wire was silently lost.
2. `RedisEventBus(url)` treated a redis://… URL as a hostname, and the class
   carried its real `disconnect` inside `_Subscription`, leaving it abstract
   and impossible to instantiate: the REDIS_URL path could never run.
3. `normalize_database_url` — provider URLs (Neon's `postgresql://…?sslmode=
   require&channel_binding=require`) must become something SQLAlchemy+asyncpg
   accepts; sqlite URLs must pass through untouched.
4. `check_server_secrets` / `mask_url` — the fail-hard gate and safe logging.
5. Server-default literals: migration 001 must not contain bare-word
   `sa.text('USD')` defaults that only SQLite tolerates.
"""
import io
import pathlib
import re

import pytest

from core.domains.market_data.feed_access import tick_from_event
from infrastructure.config.env import (
    check_server_secrets,
    mask_url,
    normalize_database_url,
)
from infrastructure.messaging.redis_event_bus import RedisEventBus, _mask_url


# ---------------------------------------------------------------------------
# 1. tick_from_event: the Redis wire shape
# ---------------------------------------------------------------------------

WIRE_EVENT = {
    "event_id": "e1",
    "timestamp": "2026-09-10T12:00:00+00:00",
    "aggregate_id": "EURUSD",
    "event_type": "market.tick_received",
    "payload": {"symbol": "EURUSD", "bid": "1.10000", "ask": "1.10010",
                "spread": "0.00010", "timestamp": "2026-09-10T12:00:00+00:00"},
}


def test_tick_from_event_accepts_the_redis_wire_dict():
    tick = tick_from_event(WIRE_EVENT)
    assert tick is not None, "a tick published by another process must not be dropped"
    assert tick.symbol == "EURUSD"
    assert str(tick.bid) == "1.10000"
    assert str(tick.ask) == "1.10010"


def test_tick_from_event_accepts_a_bare_payload_dict():
    """Some publishers pass the payload itself; both shapes must work."""
    tick = tick_from_event(WIRE_EVENT["payload"])
    assert tick is not None and tick.symbol == "EURUSD"


def test_tick_from_event_falls_back_to_aggregate_id_for_symbol():
    wire = dict(WIRE_EVENT)
    wire["payload"] = {"bid": "1.1", "ask": "1.2"}
    tick = tick_from_event(wire)
    assert tick is not None and tick.symbol == "EURUSD"


def test_tick_from_event_still_accepts_the_inprocess_object():
    class _Event:
        aggregate_id = "GBPUSD"
        payload = {"symbol": "GBPUSD", "bid": "1.26000", "ask": "1.26012"}

    tick = tick_from_event(_Event())
    assert tick is not None and tick.symbol == "GBPUSD"


def test_tick_from_event_returns_none_for_junk():
    assert tick_from_event("not-an-event") is None
    assert tick_from_event({}) is None
    assert tick_from_event({"payload": {"symbol": "EURUSD"}}) is None  # no bid/ask


# ---------------------------------------------------------------------------
# 2. RedisEventBus: URL mode, health ping, instantiability
# ---------------------------------------------------------------------------

def test_bus_is_instantiable_with_a_url():
    """Pre-M5 this raised TypeError: the real disconnect() sat in _Subscription,
    leaving RedisEventBus abstract — REDIS_URL startup could never run."""
    bus = RedisEventBus("rediss://default:token@redis.example:6379")
    assert bus._url == "rediss://default:token@redis.example:6379"


def test_bus_host_mode_unchanged():
    bus = RedisEventBus("localhost", 6380, 2)
    assert bus._url is None
    assert bus._host == "localhost" and bus._port == 6380 and bus._db == 2


@pytest.mark.asyncio
async def test_bus_ping_is_false_before_connect():
    bus = RedisEventBus("redis://localhost:6379")
    assert await bus.ping() is False


def test_bus_url_masking_never_leaks_the_token():
    assert _mask_url("rediss://default:s3cr3t@redis.example:6379") == "rediss://redis.example:6379"


# ---------------------------------------------------------------------------
# 3. normalize_database_url
# ---------------------------------------------------------------------------

def test_neon_url_becomes_asyncpg_and_keeps_tls():
    url = normalize_database_url(
        "postgresql://user:pw@ep-x-pooler.aws.neon.tech/neondb"
        "?sslmode=require&channel_binding=require"
    )
    assert url.startswith("postgresql+asyncpg://")
    assert "ssl=require" in url
    # asyncpg.connect() has no channel_binding kwarg (it negotiates SCRAM
    # channel binding automatically over TLS); SQLAlchemy forwards query
    # params as kwargs, so it must be dropped, not passed.
    assert "channel_binding" not in url


def test_postgres_scheme_alias_normalized():
    assert normalize_database_url("postgres://u:p@h/db").startswith("postgresql+asyncpg://")


def test_sqlite_and_asyncpg_urls_pass_through_untouched():
    for url in ("sqlite+aiosqlite:///tmp/x.db", "postgresql+asyncpg://u:p@h:5432/db"):
        assert normalize_database_url(url) == url


# ---------------------------------------------------------------------------
# 4. secrets gate + masking
# ---------------------------------------------------------------------------

def test_check_server_secrets_flags_everything_when_empty(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("ADMIN_API_KEY", raising=False)
    problems = check_server_secrets()
    assert any("SECRET_KEY is not set" in p for p in problems)
    assert any("ADMIN_API_KEY is not set" in p for p in problems)


def test_check_server_secrets_flags_the_old_hardcoded_placeholder(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "BROKER_PLATFORM_SECRET_KEY_CHANGE_IN_PRODUCTION")
    monkeypatch.setenv("ADMIN_API_KEY", "x" * 32)
    problems = check_server_secrets()
    assert any("placeholder" in p for p in problems)


def test_check_server_secrets_flags_short_keys(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "tooshort")
    monkeypatch.setenv("ADMIN_API_KEY", "x" * 32)
    assert any("shorter than 32" in p for p in check_server_secrets())


def test_check_server_secrets_passes_a_real_environment(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "a" * 64)
    monkeypatch.setenv("ADMIN_API_KEY", "b" * 48)
    assert check_server_secrets() == []


def test_mask_url_hides_credentials():
    masked = mask_url("postgresql+asyncpg://neon_user:super-secret@ep-x.neon.tech/neondb?ssl=require")
    assert "super-secret" not in masked
    assert "ep-x.neon.tech" in masked


# ---------------------------------------------------------------------------
# 5. migration 001 must stay PostgreSQL-legal
# ---------------------------------------------------------------------------

def test_migration_001_has_no_bare_word_server_defaults():
    """`DEFAULT USD` / `DEFAULT real` / `DEFAULT ''`-as-empty-text are SQLite-isms
    that real PostgreSQL rejects (FeatureNotSupportedError / syntax error)."""
    path = pathlib.Path(__file__).resolve().parents[3] / "alembic" / "versions" / "001_initial_schema.py"
    src = io.open(path, encoding="utf-8").read()
    offenders = [
        m.group(1)
        for m in re.finditer(r"server_default=sa\.text\('([^']*)'\)", src)
        if not m.group(1).isdigit() and m.group(1) not in ("now()", "true", "false")
    ]
    assert offenders == [], f"bare-word server defaults: {offenders}"


def test_migration_chain_orders_groups_before_accounts():
    """accounts has FK -> groups.name; PostgreSQL validates at CREATE TABLE."""
    versions = pathlib.Path(__file__).resolve().parents[3] / "alembic" / "versions"
    src = io.open(versions / "001_initial_schema.py", encoding="utf-8").read()
    names = re.findall(r"op\.create_table\(\s*\n?\s*'([^']+)'", src)
    assert names.index("groups") < names.index("accounts")


def test_revision_ids_fit_alembics_32_char_column():
    """alembic_version.version_num is VARCHAR(32); SQLite never enforced it."""
    versions = pathlib.Path(__file__).resolve().parents[3] / "alembic" / "versions"
    for path in sorted(versions.glob("*.py")):
        src = io.open(path, encoding="utf-8").read()
        m = re.search(r"^revision = ['\"]([^'\"]+)['\"]", src, re.M)
        assert m, f"{path.name}: no revision id"
        assert len(m.group(1)) <= 32, f"{path.name}: revision id {m.group(1)!r} exceeds 32 chars"
