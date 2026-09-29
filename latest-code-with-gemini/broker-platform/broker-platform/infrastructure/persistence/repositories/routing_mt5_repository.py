"""MT5 routing rule repository (M8).

`get_all_ordered` returns decoded Mt5RouteRule objects in table order — the
SmartOrderRouter loads them at startup (and on refresh). `upsert` stores the
verbatim wire record alongside the typed hot columns, so an imported rule
re-exports byte-identically and survives schema evolution of the domain model.
"""
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.domains.execution.routing_mt5 import Mt5RouteRule
from infrastructure.persistence.routing_models import Mt5RoutingRuleModel

logger = logging.getLogger(__name__)


class SqlRoutingMt5Repository:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def get_all_ordered(self, session: Optional[AsyncSession] = None) -> List[Mt5RouteRule]:
        stmt = select(Mt5RoutingRuleModel).order_by(
            Mt5RoutingRuleModel.position, Mt5RoutingRuleModel.name
        )
        if session is not None:
            rows = (await session.execute(stmt)).scalars().all()
        else:
            async with self.session_factory() as sess:
                rows = (await sess.execute(stmt)).scalars().all()
        rules = []
        for row in rows:
            record = row.record or {}
            rule = Mt5RouteRule.from_wire(record, position=row.position)
            if not row.enabled:
                # the column wins over the wire Mode: an operator can disable a
                # rule without rewriting the record
                rule = Mt5RouteRule(**{**rule.__dict__, "mode": 0})
            rules.append(rule)
        return rules

    async def upsert(
        self,
        rule: Mt5RouteRule,
        record: Dict[str, Any],
        session: Optional[AsyncSession] = None,
    ) -> Mt5RoutingRuleModel:
        model = Mt5RoutingRuleModel(
            name=rule.name,
            position=rule.position,
            mode=rule.mode,
            enabled=rule.enabled,
            action=rule.action,
            request_mask=rule.request_mask,
            type_mask=rule.type_mask,
            record=record,
        )
        if session is not None:
            await session.merge(model)
        else:
            async with self.session_factory() as sess:
                await sess.merge(model)
                await sess.commit()
        return model

    async def count(self, session: Optional[AsyncSession] = None) -> int:
        from sqlalchemy import func

        stmt = select(func.count()).select_from(Mt5RoutingRuleModel)
        if session is not None:
            return int((await session.execute(stmt)).scalar() or 0)
        async with self.session_factory() as sess:
            return int((await sess.execute(stmt)).scalar() or 0)
