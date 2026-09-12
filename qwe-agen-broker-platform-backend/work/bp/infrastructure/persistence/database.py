from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# JSONB renders as JSON on SQLite so create_all works against the development
# and test database; PostgreSQL keeps the native type. This used to live inside
# the M4 proof script, which meant any OTHER sqlite consumer (tests, a fresh
# `create_tables()` call) died with "can't render element of type JSONB".
from sqlalchemy.dialects.postgresql import JSONB as _PG_JSONB
from sqlalchemy.ext.compiler import compiles as _sa_compiles


@_sa_compiles(_PG_JSONB, "sqlite")
def _compile_jsonb_sqlite(type_, compiler, **kw):  # noqa: ANN001
    return "JSON"
from sqlalchemy.orm import DeclarativeBase
import logging

logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

class DatabaseManager:
    """Manages PostgreSQL async connections."""

    def __init__(self, connection_string: str):
        self.engine = create_async_engine(
            connection_string,
            echo=False,
            pool_size=20,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800
        )
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def create_tables(self):
        """Create all tables (for development). Use Alembic for production."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self):
        await self.engine.dispose()
