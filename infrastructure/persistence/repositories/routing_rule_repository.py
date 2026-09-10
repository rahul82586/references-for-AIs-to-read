from typing import List, Optional
from sqlalchemy import select
from core.domains.execution.models import RoutingRule
from core.ports.interfaces import IRoutingRuleRepository
from ..mappers import routing_rule_to_db, db_to_routing_rule
from ..db_models import RoutingRuleModel

class SqlRoutingRuleRepository(IRoutingRuleRepository):
    """PostgreSQL implementation of IRoutingRuleRepository."""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def get_active_rules(self) -> List[RoutingRule]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(RoutingRuleModel)
                .where(RoutingRuleModel.is_enabled == True)
                .order_by(RoutingRuleModel.priority.desc())
            )
            models = result.scalars().all()
            return [db_to_routing_rule(m) for m in models]

    async def save(self, rule: RoutingRule) -> RoutingRule:
        async with self.session_factory() as session:
            model = routing_rule_to_db(rule)
            await session.merge(model)
            await session.commit()
            return rule

    async def find_by_id(self, rule_id: str) -> Optional[RoutingRule]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(RoutingRuleModel).where(RoutingRuleModel.rule_id == rule_id)
            )
            model = result.scalar_one_or_none()
            if not model:
                return None
            return db_to_routing_rule(model)
