"""
Command to create or update a holiday configuration.
"""
import logging
from dataclasses import dataclass
from datetime import time, datetime, timezone
from typing import List, Optional

from core.domains.instruments.holiday import Holiday
from core.domains.instruments.enums import HolidayMode
from core.ports.interfaces import IHolidayRepository, IEventBus
from core.events.domain_events import HolidayCreated

logger = logging.getLogger(__name__)


@dataclass
class CreateHolidayCommand:
    """Command to create a holiday."""
    description: str
    year: int = 0  # 0 = every year
    month: int = 1
    day: int = 1
    work_from: str = "00:00:00"
    work_to: str = "23:59:59"
    symbols: Optional[List[str]] = None  # None = all symbols
    mode: str = "ENABLED"


class CreateHolidayHandler:
    """Handler for CreateHolidayCommand."""

    def __init__(
        self,
        holiday_repo: IHolidayRepository,
        event_bus: IEventBus,
    ):
        self.holiday_repo = holiday_repo
        self.event_bus = event_bus

    async def handle(self, command: CreateHolidayCommand) -> Holiday:
        """Create or update a holiday configuration."""

        # Validate date
        if not (1 <= command.month <= 12):
            raise ValueError(f"Invalid month: {command.month}")
        if not (1 <= command.day <= 31):
            raise ValueError(f"Invalid day: {command.day}")
        if command.year < 0:
            raise ValueError(f"Invalid year: {command.year}")

        # Parse times
        work_from = time.fromisoformat(command.work_from)
        work_to = time.fromisoformat(command.work_to)

        # Parse mode
        try:
            mode = HolidayMode[command.mode.upper()]
        except KeyError:
            raise ValueError(f"Invalid holiday mode: {command.mode}")

        # Create domain entity
        holiday = Holiday(
            description=command.description,
            mode=mode,
            year=command.year,
            month=command.month,
            day=command.day,
            work_from=work_from,
            work_to=work_to,
            symbols=command.symbols or [],
        )

        # Persist
        saved = await self.holiday_repo.save(holiday)
        logger.info(
            f"Holiday created: {saved.description} "
            f"({saved.year}-{saved.month}-{saved.day})"
        )

        # Publish event
        event = HolidayCreated(
            aggregate_id=saved.id,
            payload={
                "holiday_id": saved.id,
                "description": saved.description,
                "year": saved.year,
                "month": saved.month,
                "day": saved.day,
                "symbols": saved.symbols,
            },
        )
        await self.event_bus.publish(event)

        return saved