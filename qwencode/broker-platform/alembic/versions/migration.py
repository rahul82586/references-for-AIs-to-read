"""Add MT5-accurate OMS fields

Revision ID: add_mt5_oms_fields
Revises: previous_revision
Create Date: 2026-01-XX

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade() -> None:
    # Orders table - add new columns
    op.add_column('orders', sa.Column('external_id', sa.String(), nullable=True))
    op.add_column('orders', sa.Column('gateway_id', sa.String(), nullable=True))
    op.add_column('orders', sa.Column('dealer_login', sa.BigInteger(), nullable=True))
    op.add_column('orders', sa.Column('reason', sa.String(), nullable=False, server_default='CLIENT'))
    op.add_column('orders', sa.Column('volume_initial', sa.Numeric(20, 8), nullable=False, server_default='0'))
    op.add_column('orders', sa.Column('volume_current', sa.Numeric(20, 8), nullable=False, server_default='0'))
    op.add_column('orders', sa.Column('price_order', sa.Numeric(20, 8), nullable=False, server_default='0'))
    op.add_column('orders', sa.Column('price_trigger', sa.Numeric(20, 8), nullable=True))
    op.add_column('orders', sa.Column('time_setup_msc', sa.BigInteger(), nullable=False, server_default='0'))
    op.add_column('orders', sa.Column('time_in_force', sa.String(), nullable=False, server_default='GTC'))
    op.add_column('orders', sa.Column('activation_mode', sa.String(), nullable=False, server_default='NONE'))
    op.add_column('orders', sa.Column('activation_time', sa.DateTime(timezone=True), nullable=True))
    op.add_column('orders', sa.Column('activation_price', sa.Numeric(20, 8), nullable=True))
    op.add_column('orders', sa.Column('activation_flags', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('orders', sa.Column('digits', sa.Integer(), nullable=False, server_default='5'))
    op.add_column('orders', sa.Column('digits_currency', sa.Integer(), nullable=False, server_default='2'))
    op.add_column('orders', sa.Column('contract_size', sa.Numeric(20, 8), nullable=False, server_default='100000'))
    op.add_column('orders', sa.Column('expert_id', sa.String(), nullable=True))
    op.add_column('orders', sa.Column('expert_name', sa.String(), nullable=True))
    op.add_column('orders', sa.Column('order_matching', sa.String(), nullable=True))
    
    # Add new indexes
    op.create_index('idx_orders_account_state', 'orders', ['account_login', 'state'])
    op.create_index('idx_orders_symbol_state', 'orders', ['symbol', 'state'])
    
    # Deals table - add new columns
    op.add_column('deals', sa.Column('position_id', sa.String(), nullable=True))
    op.add_column('deals', sa.Column('entry', sa.String(), nullable=False, server_default='IN'))
    op.add_column('deals', sa.Column('reason', sa.String(), nullable=False, server_default='CLIENT'))
    op.add_column('deals', sa.Column('external_id', sa.String(), nullable=True))
    op.add_column('deals', sa.Column('order_ticket', sa.String(), nullable=True))
    op.add_column('deals', sa.Column('swap', sa.Numeric(20, 8), nullable=False, server_default='0'))
    op.add_column('deals', sa.Column('currency', sa.String(), nullable=False, server_default='USD'))
    op.add_column('deals', sa.Column('digits', sa.Integer(), nullable=False, server_default='5'))
    op.add_column('deals', sa.Column('digits_currency', sa.Integer(), nullable=False, server_default='2'))
    op.add_column('deals', sa.Column('contract_size', sa.Numeric(20, 8), nullable=False, server_default='100000'))
    
    # Add new indexes
    op.create_index('idx_deals_position', 'deals', ['position_id'])
    op.create_index('idx_deals_account_time', 'deals', ['account_login', 'created_at'])
    
    # Positions table - add new columns
    op.add_column('positions', sa.Column('external_id', sa.String(), nullable=True))
    op.add_column('positions', sa.Column('identifier', sa.String(), nullable=True))
    op.add_column('positions', sa.Column('action', sa.String(), nullable=False, server_default='BUY'))
    op.add_column('positions', sa.Column('reason', sa.String(), nullable=False, server_default='CLIENT'))
    op.add_column('positions', sa.Column('price_open', sa.Numeric(20, 8), nullable=False, server_default='0'))
    op.add_column('positions', sa.Column('price_current', sa.Numeric(20, 8), nullable=False, server_default='0'))
    op.add_column('positions', sa.Column('swap', sa.Numeric(20, 8), nullable=False, server_default='0'))
    op.add_column('positions', sa.Column('currency', sa.String(), nullable=False, server_default='USD'))
    op.add_column('positions', sa.Column('digits', sa.Integer(), nullable=False, server_default='5'))
    op.add_column('positions', sa.Column('digits_currency', sa.Integer(), nullable=False, server_default='2'))
    op.add_column('positions', sa.Column('contract_size', sa.Numeric(20, 8), nullable=False, server_default='100000'))
    op.add_column('positions', sa.Column('deal_open', sa.String(), nullable=True))
    op.add_column('positions', sa.Column('deal_close', sa.String(), nullable=True))
    op.add_column('positions', sa.Column('position_by_id', sa.String(), nullable=True))
    op.add_column('positions', sa.Column('time_create', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
    op.add_column('positions', sa.Column('time_update', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
    op.add_column('positions', sa.Column('comment', sa.Text(), nullable=True))
    op.add_column('positions', sa.Column('magic_number', sa.Integer(), nullable=False, server_default='0'))
    
    # Add new indexes
    op.create_index('idx_positions_identifier', 'positions', ['identifier'])
    op.create_index('idx_positions_account_symbol', 'positions', ['account_login', 'symbol'])
    op.create_index('idx_positions_action', 'positions', ['action'])


def downgrade() -> None:
    # Remove new indexes
    op.drop_index('idx_positions_action', table_name='positions')
    op.drop_index('idx_positions_account_symbol', table_name='positions')
    op.drop_index('idx_positions_identifier', table_name='positions')
    op.drop_index('idx_deals_account_time', table_name='deals')
    op.drop_index('idx_deals_position', table_name='deals')
    op.drop_index('idx_orders_symbol_state', table_name='orders')
    op.drop_index('idx_orders_account_state', table_name='orders')
    
    # Remove new columns from positions
    op.drop_column('positions', 'magic_number')
    op.drop_column('positions', 'comment')
    op.drop_column('positions', 'time_update')
    op.drop_column('positions', 'time_create')
    op.drop_column('positions', 'position_by_id')
    op.drop_column('positions', 'deal_close')
    op.drop_column('positions', 'deal_open')
    op.drop_column('positions', 'contract_size')
    op.drop_column('positions', 'digits_currency')
    op.drop_column('positions', 'digits')
    op.drop_column('positions', 'currency')
    op.drop_column('positions', 'swap')
    op.drop_column('positions', 'price_current')
    op.drop_column('positions', 'price_open')
    op.drop_column('positions', 'reason')
    op.drop_column('positions', 'action')
    op.drop_column('positions', 'identifier')
    op.drop_column('positions', 'external_id')
    
    # Remove new columns from deals
    op.drop_column('deals', 'contract_size')
    op.drop_column('deals', 'digits_currency')
    op.drop_column('deals', 'digits')
    op.drop_column('deals', 'currency')
    op.drop_column('deals', 'swap')
    op.drop_column('deals', 'order_ticket')
    op.drop_column('deals', 'external_id')
    op.drop_column('deals', 'reason')
    op.drop_column('deals', 'entry')
    op.drop_column('deals', 'position_id')
    
    # Remove new columns from orders
    op.drop_column('orders', 'order_matching')
    op.drop_column('orders', 'expert_name')
    op.drop_column('orders', 'expert_id')
    op.drop_column('orders', 'contract_size')
    op.drop_column('orders', 'digits_currency')
    op.drop_column('orders', 'digits')
    op.drop_column('orders', 'activation_flags')
    op.drop_column('orders', 'activation_price')
    op.drop_column('orders', 'activation_time')
    op.drop_column('orders', 'activation_mode')
    op.drop_column('orders', 'time_in_force')
    op.drop_column('orders', 'time_setup_msc')
    op.drop_column('orders', 'price_trigger')
    op.drop_column('orders', 'price_order')
    op.drop_column('orders', 'volume_current')
    op.drop_column('orders', 'volume_initial')
    op.drop_column('orders', 'reason')
    op.drop_column('orders', 'dealer_login')
    op.drop_column('orders', 'gateway_id')
    op.drop_column('orders', 'external_id')