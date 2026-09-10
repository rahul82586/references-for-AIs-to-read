from typing import List, Optional
import json
from sqlalchemy import select
from core.domains.instruments.models import Symbol, TradingSession
from core.ports.interfaces import ISymbolRepository
from ..mappers import symbol_to_db, db_to_symbol
from ..db_models import SymbolModel
from datetime import time

class SqlSymbolRepository(ISymbolRepository):
    """PostgreSQL implementation of ISymbolRepository."""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def get_symbol(self, name: str) -> Optional[Symbol]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(SymbolModel).where(SymbolModel.name == name)
            )
            model = result.scalar_one_or_none()
            if not model:
                return None
            return db_to_symbol(model)

    async def save(self, symbol: Symbol) -> Symbol:
        async with self.session_factory() as session:
            model = symbol_to_db(symbol)
            await session.merge(model)
            await session.commit()
            return symbol

    async def get_all_symbols(self) -> List[Symbol]:
        async with self.session_factory() as session:
            result = await session.execute(select(SymbolModel))
            models = result.scalars().all()
            return [db_to_symbol(m) for m in models]
