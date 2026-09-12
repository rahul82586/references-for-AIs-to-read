from typing import List, Optional
from sqlalchemy import select
from core.domains.ledger.models import BalanceOperation
from core.ports.interfaces import ILedgerRepository
from ..mappers import balance_operation_to_db, db_to_balance_operation
from ..db_models import BalanceOperationModel

class SqlLedgerRepository(ILedgerRepository):
    """PostgreSQL implementation of ILedgerRepository."""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def save(self, operation: BalanceOperation) -> BalanceOperation:
        async with self.session_factory() as session:
            model = balance_operation_to_db(operation)
            await session.merge(model)
            await session.commit()
            return operation

    async def get_by_account(self, account_login: str) -> List[BalanceOperation]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(BalanceOperationModel)
                .where(BalanceOperationModel.account_login == account_login)
                .order_by(BalanceOperationModel.created_at.desc())
            )
            models = result.scalars().all()
            return [db_to_balance_operation(m) for m in models]

    async def get_by_reference(self, reference_id: str) -> Optional[BalanceOperation]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(BalanceOperationModel).where(BalanceOperationModel.reference_id == reference_id)
            )
            model = result.scalar_one_or_none()
            if not model:
                return None
            return db_to_balance_operation(model)
