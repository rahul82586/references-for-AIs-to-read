from typing import List, Optional
import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.domains.instruments.models import Symbol, TradingSession
from core.ports.interfaces import ISymbolRepository
from ..mappers import symbol_to_db, db_to_symbol
from ..db_models import SymbolModel
from datetime import time

class SqlSymbolRepository(ISymbolRepository):
    """PostgreSQL implementation of ISymbolRepository."""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    #: Columns that only an MT5 IMPORT can write. The domain cannot express them:
    #: mt5_source is the original wire record, mt5_scale the decimal scale each
    #: field arrived with, and mt5_extra the fields no entity models. save() goes
    #: through group_to_db(entity), which has no baseline to pass, so a full-row
    #: merge used to NULL all three - and with them the 392/392 byte-identical
    #: re-export guarantee for that group. This is defect D18: the same class as
    #: D8b/D15, a value written in one place and blanked from another.
    _IMPORT_OWNED_COLUMNS = ("mt5_source", "mt5_scale", "mt5_extra")

    async def _carry_import_owned(self, session, model):
        """Copy the import-owned columns off the stored row onto `model`.

        Read-modify-write inside the SAME session, so nothing races. A group that
        was created natively has no baseline and gains nothing here - correct,
        because there is nothing to preserve.
        """
        from sqlalchemy import select as _select

        result = await session.execute(
            _select(type(model)).where(type(model).name == model.name)
        )
        existing = result.scalar_one_or_none()
        if existing is None:
            return model
        for col in self._IMPORT_OWNED_COLUMNS:
            stored = getattr(existing, col, None)
            if col == "mt5_extra":
                # Merge, do not replace: the entity may legitimately carry new
                # quarantine of its own, and the stored row may hold fields the
                # entity never saw. Stored values win on conflict - they came
                # from a real server.
                merged = dict(getattr(model, col, None) or {})
                merged.update(stored or {})
                setattr(model, col, merged)
            elif stored is not None and not getattr(model, col, None):
                setattr(model, col, stored)
        return model


    async def get_symbol(self, name: str) -> Optional[Symbol]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(SymbolModel).where(SymbolModel.name == name)
            )
            model = result.scalar_one_or_none()
            if not model:
                return None
            return db_to_symbol(model)

    async def find_by_name(self, name: str, session: Optional[AsyncSession] = None) -> Optional[Symbol]:
        """The name the application layer calls: CreateOrderHandler, RecordDealHandler,
        LiquidationWorker, TickMarginPipeline and ConfigCache all await
        `symbol_repo.find_by_name(...)`.

        It did not exist here. The port declared only `get_symbol`, so this repository
        satisfied the contract while every one of those five callers raised
        AttributeError against it - which is why the order path had only ever been run
        against test doubles that defined the name the callers used. Same shape as the
        position repository's missing get_positions_by_account.

        Note this is ASYNC and so is not what RiskEngine wants on the hot path; it is
        given ConfigCache instead. See ISymbolRepository's docstring.
        """
        if session is not None:
            result = await session.execute(
                select(SymbolModel).where(SymbolModel.name == name)
            )
            model = result.scalar_one_or_none()
            return db_to_symbol(model) if model else None
        return await self.get_symbol(name)

    async def save(self, symbol: Symbol) -> Symbol:
        async with self.session_factory() as session:
            model = symbol_to_db(symbol)
            await self._carry_import_owned(session, model)
            await session.merge(model)
            await session.commit()
            return symbol

    async def get_all_symbols(self) -> List[Symbol]:
        async with self.session_factory() as session:
            result = await session.execute(select(SymbolModel))
            models = result.scalars().all()
            return [db_to_symbol(m) for m in models]
    async def get_all(self):
        """Alias used by ConfigCache.initialize()."""
        return await self.get_all_symbols()

    async def save_model(self, model) -> None:
        """Persist a SymbolModel row directly, preserving MT5 metadata.

        Our Symbol models 52 of MT5's 121 fields. The other 69 - CurrencyProfit,
        CurrencyMargin, the Filter* tick filtration, the IE*/RE* execution controls, the
        per-day SwapRate curve - live in mt5_extra and mt5_source, and only a row-level
        save can carry them.
        """
        async with self.session_factory() as session:
            await session.merge(model)
            await session.commit()
    async def find_row_by_name(self, name: str):
        """Return the raw SymbolModel row, for MT5 export. See the group equivalent."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(SymbolModel).where(SymbolModel.name == name)
            )
            return result.scalar_one_or_none()
