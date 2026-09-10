from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
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
