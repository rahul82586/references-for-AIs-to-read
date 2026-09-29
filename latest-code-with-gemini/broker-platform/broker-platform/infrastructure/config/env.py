"""Environment loading, URL normalisation, and fail-hard secret checks.

M5: the platform must start on a machine that isn't the developer's, from a
`.env` file, and must REFUSE to start with unsafe configuration rather than
falling back to the old hardcoded defaults.

Layering note: this module reads `os.environ` and nothing else — no framework
imports — so any layer may use it.
"""
from __future__ import annotations

import os
from typing import List, Optional
from urllib.parse import urlsplit

__all__ = [
    "load_environment",
    "normalize_database_url",
    "check_server_secrets",
    "mask_url",
]

#: The pre-M5 hardcoded JWT secret. If this value ever appears in an
#: environment, it is a configuration error, not a secret.
_FORBIDDEN_SECRET_PREFIX = "BROKER_PLATFORM_SECRET_KEY"


def load_environment(path: Optional[str] = None) -> None:
    """Load `.env` into os.environ, idempotently, without overriding real env.

    Missing python-dotenv or a missing file are both fine: the process
    environment may already carry everything (containers, CI).
    """
    try:
        from dotenv import load_dotenv
    except ImportError:  # pragma: no cover - dependency is declared
        return
    load_dotenv(path, override=False)


def normalize_database_url(url: str) -> str:
    """Accept a plain postgres URL (as Neon/Heroku/etc. hand them out).

    SQLAlchemy's async engine needs an explicit driver; every caller wants
    asyncpg. Rewriting here means one paste of a provider URL works everywhere
    (CLI, API, alembic) instead of three places failing differently.

    Query-parameter translation for the asyncpg dialect:
    * `sslmode=` -> `ssl=`   (asyncpg.connect() has no `sslmode` kwarg; it only
      understands sslmode inside a DSN *it* parses, while SQLAlchemy forwards
      every query parameter as a connect kwarg — `ssl` IS a valid kwarg)
    * `channel_binding=` is dropped: asyncpg.connect() does not accept it as a
      kwarg either, and asyncpg negotiates SCRAM-SHA-256-PLUS channel binding
      automatically whenever the connection is TLS-protected (ssl=require).
    """
    if url.startswith(("postgresql://", "postgres://")):
        prefix, rest = url.split("://", 1)
        url = "postgresql+asyncpg://" + rest
    if "+asyncpg://" in url and "?" in url:
        head, sep, query = url.partition("?")
        params = []
        for p in query.split("&"):
            if p.startswith("sslmode="):
                params.append("ssl=" + p[len("sslmode="):])
            elif p.startswith("channel_binding="):
                continue  # negotiated automatically over TLS; not a kwarg
            else:
                params.append(p)
        url = head + sep + "&".join(params) if params else head
    return url


def check_server_secrets() -> List[str]:
    """Return human-readable problems with the secret configuration.

    Empty list = safe to start. Called at server startup; each problem names
    the variable and the fix, because a startup failure that doesn't say what
    to set is a support ticket.
    """
    problems: List[str] = []
    key = os.environ.get("SECRET_KEY")
    if not key:
        problems.append(
            "SECRET_KEY is not set (generate: python3 -c \"import secrets; print(secrets.token_hex(32))\")"
        )
    else:
        if key.startswith(_FORBIDDEN_SECRET_PREFIX):
            problems.append("SECRET_KEY is the old hardcoded placeholder — rotate it")
        if len(key) < 32:
            problems.append("SECRET_KEY is shorter than 32 characters")
    if not os.environ.get("ADMIN_API_KEY"):
        problems.append(
            "ADMIN_API_KEY is not set (generate: python3 -c \"import secrets; print(secrets.token_hex(24))\")"
        )
    return problems


def mask_url(url: str) -> str:
    """Strip credentials from a URL so it is safe to log."""
    try:
        parts = urlsplit(url)
        if not parts.netloc:
            return url
        host = parts.hostname or ""
        if parts.port:
            host = f"{host}:{parts.port}"
        return f"{parts.scheme}://{host}{parts.path}"
    except ValueError:  # pragma: no cover - never fail because of a log line
        return "<unparseable url>"
