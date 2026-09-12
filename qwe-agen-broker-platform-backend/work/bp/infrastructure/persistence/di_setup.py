from infrastructure.persistence.repositories.holiday_repository import SQLAlchemyHolidayRepository
from .database import DatabaseManager
from .repositories.account_repository import SqlAccountRepository
from .repositories.order_repository import SqlOrderRepository
from .repositories.deal_repository import SqlDealRepository
from .repositories.position_repository import SqlPositionRepository
from .repositories.ledger_repository import SqlLedgerRepository
from .repositories.routing_mt5_repository import SqlRoutingMt5Repository
from .repositories.routing_rule_repository import SqlRoutingRuleRepository
from .repositories.coverage_account_repository import SqlCoverageAccountRepository
from .repositories.symbol_repository import SqlSymbolRepository
from .repositories.group_repository import SqlGroupRepository
from .repositories.manager_repository import SqlClientRepository, SqlManagerRepository
from .event_store import SqlEventStore

def setup_persistence_di(database_manager: DatabaseManager) -> dict:
    """Wire all repositories and return them as a dictionary for injection."""
    session_factory = database_manager.session_factory

    # Initialize repositories in dependency order. The returned dict IS the container
    # payload: api/di_providers.register_di_providers() consumes it, and
    # get_di_container().resolve(IHolidayRepository) maps the port to 'holiday_repo'.
    holiday_repo = SQLAlchemyHolidayRepository(session_factory)
    group_repo = SqlGroupRepository(session_factory)
    account_repo = SqlAccountRepository(session_factory, group_repo)
    symbol_repo = SqlSymbolRepository(session_factory)
    order_repo = SqlOrderRepository(session_factory)
    deal_repo = SqlDealRepository(session_factory)
    position_repo = SqlPositionRepository(session_factory)
    ledger_repo = SqlLedgerRepository(session_factory)
    mt5_routing_repo = SqlRoutingMt5Repository(session_factory)
    routing_rule_repo = SqlRoutingRuleRepository(session_factory)
    coverage_repo = SqlCoverageAccountRepository(session_factory)
    manager_repo = SqlManagerRepository(session_factory)
    client_repo = SqlClientRepository(session_factory)
    event_store = SqlEventStore(session_factory)

    return {
        'holiday_repo': holiday_repo,
        'group_repo': group_repo,
        'account_repo': account_repo,
        'symbol_repo': symbol_repo,
        'order_repo': order_repo,
        'deal_repo': deal_repo,
        'position_repo': position_repo,
        'ledger_repo': ledger_repo,
        'mt5_routing_repo': mt5_routing_repo,
        'routing_rule_repo': routing_rule_repo,
        'coverage_repo': coverage_repo,
        'manager_repo': manager_repo,
        'client_repo': client_repo,
        'event_store': event_store,
    }
