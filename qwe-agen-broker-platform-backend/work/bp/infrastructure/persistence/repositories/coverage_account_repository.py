from typing import Optional
from decimal import Decimal
import json
from sqlalchemy import select
from core.domains.execution.models import CoverageAccount
from core.ports.interfaces import ICoverageAccountRepository
from ..mappers import coverage_account_to_db, db_to_coverage_account
from ..db_models import CoverageAccountModel

class SqlCoverageAccountRepository(ICoverageAccountRepository):
    """PostgreSQL implementation of ICoverageAccountRepository."""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def find_by_id(self, account_id: str) -> Optional[CoverageAccount]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(CoverageAccountModel).where(CoverageAccountModel.account_id == account_id)
            )
            model = result.scalar_one_or_none()
            if not model:
                return None
            return db_to_coverage_account(model)

    async def save(self, account: CoverageAccount) -> CoverageAccount:
        async with self.session_factory() as session:
            model = coverage_account_to_db(account)
            await session.merge(model)
            await session.commit()
            return account

    async def update_exposure(self, account_id: str, symbol: str, volume_delta: Decimal) -> None:
        async with self.session_factory() as session:
            result = await session.execute(
                select(CoverageAccountModel).where(CoverageAccountModel.account_id == account_id)
            )
            model = result.scalar_one_or_none()
            if not model:
                raise ValueError(f"Coverage account {account_id} not found")

            # Parse existing exposure
            exposure = json.loads(model.net_exposure_json) if model.net_exposure_json else {}

            # Update exposure for symbol using Decimal
            current = Decimal(str(exposure.get(symbol, '0')))
            exposure[symbol] = str(current + Decimal(str(volume_delta)))

            # Save back
            model.net_exposure_json = json.dumps(exposure)
            await session.commit()
