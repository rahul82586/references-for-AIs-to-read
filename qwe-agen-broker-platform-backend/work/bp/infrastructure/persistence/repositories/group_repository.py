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
