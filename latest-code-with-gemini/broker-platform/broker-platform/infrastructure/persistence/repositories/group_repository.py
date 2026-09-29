from typing import List, Optional
from decimal import Decimal
from sqlalchemy import select
from core.domains.accounts.models import Group
from core.ports.interfaces import IGroupRepository
from ..mappers import group_to_db, db_to_group
from ..db_models import GroupModel
import json

class SqlGroupRepository(IGroupRepository):
    """PostgreSQL implementation of IGroupRepository."""

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


    async def find_by_name(self, name: str) -> Optional[Group]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(GroupModel).where(GroupModel.name == name)
            )
            model = result.scalar_one_or_none()
            if not model:
                return None
            return db_to_group(model)

    async def save(self, group: Group) -> Group:
        async with self.session_factory() as session:
            model = group_to_db(group)
            await self._carry_import_owned(session, model)
            await session.merge(model)
            await session.commit()
            return group

    async def get_all(self) -> List[Group]:
        """Every group. Called once at startup to warm the ConfigCache."""
        return await self.get_all_groups()

    async def find_by_id(self, group_id: str) -> Optional[Group]:
        """Look a group up by its surrogate id."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(GroupModel).where(GroupModel.group_id == group_id)
            )
            model = result.scalar_one_or_none()
            return db_to_group(model) if model else None

    async def delete(self, group_id: str) -> bool:
        async with self.session_factory() as session:
            result = await session.execute(
                select(GroupModel).where(GroupModel.group_id == group_id)
            )
            model = result.scalar_one_or_none()
            if model is None:
                return False
            await session.delete(model)
            await session.commit()
            return True

    async def delete_by_name(self, name: str) -> bool:
        """Delete by the MT5 path name - the natural key every group has.

        delete(group_id) cannot address an MT5-imported group whose surrogate
        group_id is NULL; the identity plane's DeleteGroupHandler needs this.
        """
        async with self.session_factory() as session:
            result = await session.execute(
                select(GroupModel).where(GroupModel.name == name)
            )
            model = result.scalar_one_or_none()
            if model is None:
                return False
            await session.delete(model)
            await session.commit()
            return True

    async def get_all_groups(self) -> List[Group]:
        async with self.session_factory() as session:
            result = await session.execute(select(GroupModel))
            models = result.scalars().all()
            return [db_to_group(m) for m in models]
    async def save_model(self, model) -> None:
        """Persist a GroupModel row directly.

        Needed for MT5 import: the row carries mt5_extra, mt5_scale and mt5_source,
        which a domain Group cannot express. Going through save(group) would drop the
        27 ConfigGroups fields we do not model and make the group un-exportable.
        """
        async with self.session_factory() as session:
            await session.merge(model)
            await session.commit()
    async def find_row_by_name(self, name: str):
        """Return the raw GroupModel row, for MT5 export.

        The row carries mt5_source, mt5_extra and mt5_scale, which a domain Group
        cannot express. Exporting needs them, so this returns the row rather than the
        mapped object.
        """
        async with self.session_factory() as session:
            result = await session.execute(
                select(GroupModel).where(GroupModel.name == name)
            )
            return result.scalar_one_or_none()
