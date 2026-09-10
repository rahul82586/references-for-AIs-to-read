import json
import logging
from typing import List, Optional
from sqlalchemy import select
from core.events.domain_events import DomainEvent
from .db_models import DomainEventModel

logger = logging.getLogger(__name__)

class SqlEventStore:
    """Persists all domain events for audit trail."""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def append(self, event: DomainEvent) -> None:
        """Store a domain event immutably."""
        async with self.session_factory() as session:
            model = DomainEventModel(
                event_id=event.event_id,
                event_type=event.event_type.value,
                aggregate_id=event.aggregate_id,
                payload_json=json.dumps(event.payload),
                created_at=event.timestamp
            )
            session.add(model)
            await session.commit()
            logger.debug(f"Event {event.event_id} stored")

    async def get_events_for_aggregate(self, aggregate_id: str) -> List[DomainEvent]:
        """Retrieve all events for an entity (audit trail)."""
        from core.events.domain_events import EventType
        async with self.session_factory() as session:
            result = await session.execute(
                select(DomainEventModel).where(DomainEventModel.aggregate_id == aggregate_id)
            )
            models = result.scalars().all()
            events = []
            for m in models:
                try:
                    et = EventType(m.event_type)
                except ValueError:
                    et = EventType.ORDER_CREATED
                events.append(DomainEvent(
                    event_id=m.event_id,
                    event_type=et,
                    aggregate_id=m.aggregate_id,
                    payload=json.loads(m.payload_json or "{}"),
                    timestamp=m.created_at
                ))
            return events

    async def get_events_by_type(self, event_type: str) -> List[DomainEventModel]:
        """Retrieve all events of a specific type."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(DomainEventModel).where(DomainEventModel.event_type == event_type)
            )
            return result.scalars().all()
