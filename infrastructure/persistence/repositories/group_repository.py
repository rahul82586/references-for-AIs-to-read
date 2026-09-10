from typing import List, Optional
from decimal import Decimal
from sqlalchemy import select
from core.domains.accounts.models import Group, MarginProfile, CommissionProfile, ExecutionProfile, ExecutionMode
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

    async def get_all_groups(self) -> List[Group]:
        async with self.session_factory() as session:
            result = await session.execute(select(GroupModel))
            models = result.scalars().all()
            return [db_to_group(m) for m in models]
