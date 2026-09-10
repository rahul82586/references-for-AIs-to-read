"""Initial schema - all Phase 8 tables

Revision ID: 001
Revises:
Create Date: 2024-09-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create groups table
    op.create_table('groups',
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('leverage', sa.Integer(), nullable=False, default=100),
        sa.Column('margin_call_level', sa.Numeric(precision=6, scale=2), nullable=False, default=60),
        sa.Column('stop_out_level', sa.Numeric(precision=6, scale=2), nullable=False, default=30),
        sa.Column('stop_out_mode', sa.String(length=16), nullable=False, default='PERCENT'),
        sa.Column('commission_type', sa.String(length=16), nullable=False, default='MONEY'),
        sa.Column('commission_value', sa.Numeric(precision=18, scale=8), nullable=False, default=0),
        sa.Column('commission_currency', sa.String(length=3), nullable=False, default='USD'),
        sa.Column('execution_mode', sa.String(length=32), nullable=False, default='MARKET'),
        sa.Column('position_mode', sa.String(length=16), nullable=False, default='HEDGING'),
        sa.Column('allow_hedging', sa.Boolean(), default=True),
        sa.Column('allow_scalping', sa.Boolean(), default=True),
        sa.Column('slippage_points', sa.Integer(), default=0),
        sa.Column('permissions_json', sa.Text(), default='{}'),
        sa.Column('swap_enable', sa.Boolean(), default=True),
        sa.Column('swap_type', sa.String(length=16), default='POINTS'),
        sa.Column('swap_long', sa.Numeric(precision=18, scale=8), default=0),
        sa.Column('swap_short', sa.Numeric(precision=18, scale=8), default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('name')
    )

    # Create accounts table
    op.create_table('accounts',
        sa.Column('login', sa.String(length=32), nullable=False),
        sa.Column('group_name', sa.String(length=128), sa.ForeignKey('groups.name'), nullable=False),
        sa.Column('account_type', sa.String(length=32), nullable=False, default='REAL'),
        sa.Column('balance', sa.Numeric(precision=18, scale=8), nullable=False, default=0),
        sa.Column('credit', sa.Numeric(precision=18, scale=8), nullable=False, default=0),
        sa.Column('equity', sa.Numeric(precision=18, scale=8), nullable=False, default=0),
        sa.Column('margin_used', sa.Numeric(precision=18, scale=8), nullable=False, default=0),
        sa.Column('margin_free', sa.Numeric(precision=18, scale=8), nullable=False, default=0),
        sa.Column('leverage', sa.Integer(), nullable=False, default=100),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, default=True),
        sa.Column('kyc_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('currency', sa.String(length=3), nullable=False, default='USD'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('login')
    )

    # Create symbols table
    op.create_table('symbols',
        sa.Column('name', sa.String(length=32), nullable=False),
        sa.Column('path', sa.String(length=128), nullable=False),
        sa.Column('tick_size', sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column('tick_value', sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column('contract_size', sa.Numeric(precision=18, scale=8), nullable=False, default=100000),
        sa.Column('digits', sa.Integer(), nullable=False, default=5),
        sa.Column('volume_min', sa.Numeric(precision=18, scale=8), nullable=False, default=0.01),
        sa.Column('volume_max', sa.Numeric(precision=18, scale=8), nullable=False, default=100),
        sa.Column('volume_step', sa.Numeric(precision=18, scale=8), nullable=False, default=0.01),
        sa.Column('margin_initial_percent', sa.Numeric(precision=6, scale=2), nullable=False, default=3.33),
        sa.Column('margin_maintenance_percent', sa.Numeric(precision=6, scale=2), nullable=False, default=1.67),
        sa.Column('is_trade_allowed', sa.Boolean(), nullable=False, default=True),
        sa.Column('fill_mode', sa.String(length=16), nullable=False, default='FOK'),
        sa.Column('sessions_json', sa.Text(), default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('name')
    )

    # Create orders table
    op.create_table('orders',
        sa.Column('ticket_id', sa.String(length=32), nullable=False),
        sa.Column('account_login', sa.String(length=32), sa.ForeignKey('accounts.login'), nullable=False),
        sa.Column('symbol', sa.String(length=32), sa.ForeignKey('symbols.name'), nullable=False),
        sa.Column('order_type', sa.String(length=32), nullable=False),
        sa.Column('volume', sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column('filled_volume', sa.Numeric(precision=18, scale=8), nullable=False, default=0),
        sa.Column('price', sa.Numeric(precision=18, scale=8), nullable=True),
        sa.Column('average_fill_price', sa.Numeric(precision=18, scale=8), nullable=True),
        sa.Column('stop_loss', sa.Numeric(precision=18, scale=8), nullable=True),
        sa.Column('take_profit', sa.Numeric(precision=18, scale=8), nullable=True),
        sa.Column('state', sa.String(length=32), nullable=False, default='NEW'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('ticket_id')
    )
    op.create_index('idx_orders_login', 'orders', ['account_login'])
    op.create_index('idx_orders_symbol', 'orders', ['symbol'])
    op.create_index('idx_orders_state', 'orders', ['state'])

    # Create deals table
    op.create_table('deals',
        sa.Column('deal_id', sa.String(length=32), nullable=False),
        sa.Column('order_id', sa.String(length=32), sa.ForeignKey('orders.ticket_id'), nullable=False),
        sa.Column('account_login', sa.String(length=32), sa.ForeignKey('accounts.login'), nullable=False),
        sa.Column('symbol', sa.String(length=32), sa.ForeignKey('symbols.name'), nullable=False),
        sa.Column('deal_type', sa.String(length=32), nullable=False),
        sa.Column('volume', sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column('price', sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column('commission', sa.Numeric(precision=18, scale=8), nullable=False, default=0),
        sa.Column('swap', sa.Numeric(precision=18, scale=8), nullable=False, default=0),
        sa.Column('profit', sa.Numeric(precision=18, scale=8), nullable=False, default=0),
        sa.Column('currency', sa.String(length=3), nullable=False, default='USD'),
        sa.Column('original_deal_id', sa.String(length=32), nullable=True),
        sa.Column('reason', sa.String(length=256), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('deal_id')
    )
    op.create_index('idx_deals_login', 'deals', ['account_login'])
    op.create_index('idx_deals_order', 'deals', ['order_id'])
    op.create_index('idx_deals_symbol', 'deals', ['symbol'])

    # Create positions table
    op.create_table('positions',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('account_login', sa.String(length=32), sa.ForeignKey('accounts.login'), nullable=False),
        sa.Column('symbol', sa.String(length=32), sa.ForeignKey('symbols.name'), nullable=False),
        sa.Column('volume', sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column('side', sa.String(length=8), nullable=False),
        sa.Column('average_price', sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column('unrealized_pnl', sa.Numeric(precision=18, scale=8), nullable=False, default=0),
        sa.Column('swap_accumulated', sa.Numeric(precision=18, scale=8), nullable=False, default=0),
        sa.Column('contract_size', sa.Numeric(precision=18, scale=8), nullable=False, default=100000),
        sa.Column('opened_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_positions_login', 'positions', ['account_login'])
    op.create_index('idx_positions_symbol', 'positions', ['symbol'])

    # Create balance_operations table
    op.create_table('balance_operations',
        sa.Column('operation_id', sa.String(length=32), nullable=False),
        sa.Column('account_login', sa.String(length=32), sa.ForeignKey('accounts.login'), nullable=False),
        sa.Column('operation_type', sa.String(length=32), nullable=False),
        sa.Column('amount', sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, default='USD'),
        sa.Column('balance_after', sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column('reference_id', sa.String(length=64), nullable=True),
        sa.Column('comment', sa.String(length=256), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('operation_id')
    )
    op.create_index('idx_balance_ops_login', 'balance_operations', ['account_login'])
    op.create_index('idx_balance_ops_type', 'balance_operations', ['operation_type'])
    op.create_index('idx_balance_ops_reference', 'balance_operations', ['reference_id'])

    # Create routing_rules table
    op.create_table('routing_rules',
        sa.Column('rule_id', sa.String(length=32), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('destination', sa.String(length=32), nullable=False),
        sa.Column('group_filter', sa.String(length=128), nullable=True),
        sa.Column('symbol_filter', sa.String(length=64), nullable=True),
        sa.Column('volume_min', sa.Numeric(precision=18, scale=8), nullable=True),
        sa.Column('volume_max', sa.Numeric(precision=18, scale=8), nullable=True),
        sa.Column('gateway_id', sa.String(length=64), nullable=True),
        sa.Column('coverage_account_id', sa.String(length=64), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('rule_id')
    )

    # Create coverage_accounts table
    op.create_table('coverage_accounts',
        sa.Column('account_id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, default='USD'),
        sa.Column('net_exposure_json', sa.Text(), default='{}'),
        sa.Column('margin_level', sa.Numeric(precision=18, scale=8), nullable=False, default=0),
        sa.Column('trading_state', sa.String(length=32), nullable=False, default='NEUTRAL'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('account_id')
    )

    # Create domain_events table
    op.create_table('domain_events',
        sa.Column('event_id', sa.String(length=64), nullable=False),
        sa.Column('event_type', sa.String(length=64), nullable=False),
        sa.Column('aggregate_id', sa.String(length=64), nullable=False),
        sa.Column('payload_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('event_id')
    )
    op.create_index('idx_events_type', 'domain_events', ['event_type'])
    op.create_index('idx_events_aggregate', 'domain_events', ['aggregate_id'])


def downgrade() -> None:
    op.drop_table('domain_events')
    op.drop_table('coverage_accounts')
    op.drop_table('routing_rules')
    op.drop_table('balance_operations')
    op.drop_table('positions')
    op.drop_table('deals')
    op.drop_table('orders')
    op.drop_table('symbols')
    op.drop_table('accounts')
    op.drop_table('groups')
