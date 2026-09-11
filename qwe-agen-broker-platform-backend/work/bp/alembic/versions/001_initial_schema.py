"""Initial schema, generated from the SQLAlchemy models.

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-09-10

DO NOT EDIT BY HAND. This file is generated from Base.metadata by
scripts/m1_generate_migration.py, because the models are the single source of truth
for the schema. The revision it replaces had drifted: it created
symbols.margin_initial_percent (a field the Symbol entity no longer has) and a groups
table whose margin thresholds were DECIMAL(5,4) fractions here but Numeric(6,2)
percents in the model, while ops/docker/init.sql used a UUID primary key and the model
used the group name. Four competing definitions of the same table.

Units worth restating because they were the source of that drift:
  groups.margin_call / groups.margin_stop_out are PERCENT (MT5 MarginCall "50.00",
  MarginStopOut "30.00"). There is no 0.8 / 0.5 anywhere in this schema.
  symbols.point and symbols.tick_size are SEPARATE columns. MT5's Point is the
  price-precision step; TickSize is a different, frequently-zero field.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Alembic revision graph. Both identifiers are required: without down_revision Alembic
# cannot build the graph and `alembic upgrade head` fails outright, which is what the
# deleted migration.py did (it had prose in the docstring instead of variables).
revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None



def upgrade() -> None:

    op.create_table(
        'groups',
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('group_id', sa.String(length=64), nullable=True),
        sa.Column('server_id', sa.Integer(), nullable=False, server_default=sa.text('1')),
        sa.Column('account_type', sa.String(length=32), nullable=False, server_default=sa.text("'real'")),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('auth_mode', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('auth_password_min', sa.Integer(), nullable=False, server_default=sa.text('8')),
        sa.Column('auth_otp_mode', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('permissions_flags', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('company', sa.String(length=256), nullable=False, server_default=sa.text("''")),
        sa.Column('company_page', sa.String(length=256), nullable=False, server_default=sa.text("''")),
        sa.Column('company_email', sa.String(length=256), nullable=False, server_default=sa.text("''")),
        sa.Column('company_support_page', sa.String(length=512), nullable=False, server_default=sa.text("''")),
        sa.Column('company_support_email', sa.String(length=256), nullable=False, server_default=sa.text("''")),
        sa.Column('company_catalog', sa.String(length=256), nullable=False, server_default=sa.text("''")),
        sa.Column('company_deposit_url', sa.String(length=512), nullable=False, server_default=sa.text("''")),
        sa.Column('company_withdrawal_url', sa.String(length=512), nullable=False, server_default=sa.text("''")),
        sa.Column('currency', sa.String(length=16), nullable=False, server_default=sa.text("'USD'")),
        sa.Column('currency_digits', sa.Integer(), nullable=False, server_default=sa.text('2')),
        sa.Column('reports_mode', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('reports_flags', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('reports_email', sa.String(length=256), nullable=False, server_default=sa.text("''")),
        sa.Column('news_mode', sa.Integer(), nullable=False, server_default=sa.text('2')),
        sa.Column('news_category', sa.String(length=256), nullable=False, server_default=sa.text("''")),
        sa.Column('news_langs', postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('mail_mode', sa.Integer(), nullable=False, server_default=sa.text('1')),
        sa.Column('trade_flags', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('trade_transfer_mode', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('trade_interestrate', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('0')),
        sa.Column('trade_virtual_credit', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('0')),
        sa.Column('margin_mode', sa.Integer(), nullable=False, server_default=sa.text('2')),
        sa.Column('margin_flags', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('margin_so_mode', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('margin_free_mode', sa.Integer(), nullable=False, server_default=sa.text('1')),
        sa.Column('margin_call', sa.Numeric(precision=6, scale=2), nullable=False, server_default=sa.text('50')),
        sa.Column('margin_stop_out', sa.Numeric(precision=6, scale=2), nullable=False, server_default=sa.text('30')),
        sa.Column('margin_free_profit_mode', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('leverage_default', sa.Integer(), nullable=False, server_default=sa.text('100')),
        sa.Column('leverage_max', sa.Integer(), nullable=False, server_default=sa.text('500')),
        sa.Column('demo_leverage', sa.Integer(), nullable=False, server_default=sa.text('10')),
        sa.Column('demo_deposit', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('0')),
        sa.Column('demo_trades_clean', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('limit_history', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('limit_orders', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('limit_symbols', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('limit_positions', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('limit_positions_volume', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('0')),
        sa.Column('margin_json', postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('commissions_json', postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('symbol_overrides_json', postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('permissions_json', postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('swaps_json', postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('routing_json', postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('mt5_extra', postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('mt5_scale', postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('mt5_source', postgresql.JSONB(), nullable=True, server_default=sa.text("'{}'::jsonb")),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('name'),
    )
    op.create_index('idx_groups_server', 'groups', ['server_id'], unique=False)
    op.create_index('ix_groups_group_id', 'groups', ['group_id'], unique=True)
    op.create_index('idx_groups_account_type', 'groups', ['account_type'], unique=False)

    op.create_table(
        'accounts',
        sa.Column('login', sa.String(length=32), nullable=False),
        sa.Column('client_id', sa.String(length=64), nullable=True),
        sa.Column('group_name', sa.String(length=128), nullable=False),
        sa.Column('group_id', sa.String(length=64), nullable=True),
        sa.Column('account_type', sa.String(length=32), nullable=False, server_default=sa.text("'real'")),
        sa.Column('currency', sa.String(length=16), nullable=False, server_default=sa.text("'USD'")),
        sa.Column('currency_digits', sa.Integer(), nullable=False, server_default=sa.text('2')),
        sa.Column('leverage', sa.Integer(), nullable=True),
        sa.Column('balance', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('0')),
        sa.Column('credit', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('0')),
        sa.Column('equity', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('0')),
        sa.Column('margin_used', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('0')),
        sa.Column('margin_free', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('0')),
        sa.Column('margin_level', sa.Numeric(precision=12, scale=4), nullable=False, server_default=sa.text('0')),
        sa.Column('profit', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('0')),
        sa.Column('storage', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('0')),
        sa.Column('commission', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('0')),
        sa.Column('so_activation', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('so_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('so_level', sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column('so_equity', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('so_margin', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('is_online', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('color_tag', sa.String(length=32), nullable=True),
        sa.Column('dealer_notes', sa.Text(), nullable=True),
        sa.Column('registration_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
        sa.Column('mt5_extra', postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.PrimaryKeyConstraint('login'),
        sa.ForeignKeyConstraint(['group_name'], ['groups.name']),
    )
    op.create_index('idx_accounts_client', 'accounts', ['client_id'], unique=False)
    op.create_index('ix_accounts_group_id', 'accounts', ['group_id'], unique=False)
    op.create_index('ix_accounts_client_id', 'accounts', ['client_id'], unique=False)
    op.create_index('idx_accounts_group', 'accounts', ['group_name'], unique=False)
    op.create_index('idx_accounts_type', 'accounts', ['account_type'], unique=False)

    op.create_table(
        'balance_operations',
        sa.Column('operation_id', sa.String(length=32), nullable=False),
        sa.Column('account_login', sa.String(length=32), nullable=False),
        sa.Column('operation_type', sa.String(length=32), nullable=False),
        sa.Column('amount', sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default=sa.text("'USD'")),
        sa.Column('balance_after', sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column('reference_id', sa.String(length=64), nullable=True),
        sa.Column('comment', sa.String(length=256), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('operation_id'),
        sa.ForeignKeyConstraint(['account_login'], ['accounts.login']),
    )
    op.create_index('idx_balance_ops_reference', 'balance_operations', ['reference_id'], unique=False)
    op.create_index('idx_balance_ops_type', 'balance_operations', ['operation_type'], unique=False)
    op.create_index('idx_balance_ops_login', 'balance_operations', ['account_login'], unique=False)

    op.create_table(
        'bars',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=32), nullable=False),
        sa.Column('timeframe', sa.String(length=10), nullable=False),
        sa.Column('open', sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column('high', sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column('low', sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column('close', sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column('tick_volume', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('open_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('close_time', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_bars_open_time', 'bars', ['open_time'], unique=False)
    op.create_index('idx_bars_symbol_timeframe_time', 'bars', ['symbol', 'timeframe', 'open_time'], unique=False)
    op.create_index('ix_bars_symbol', 'bars', ['symbol'], unique=False)
    op.create_index('ix_bars_timeframe', 'bars', ['timeframe'], unique=False)

    op.create_table(
        'clients',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('client_id', sa.String(length=64), nullable=True),
        sa.Column('mqid', sa.String(length=64), nullable=False, server_default=sa.text("''")),
        sa.Column('full_name', sa.String(length=256), nullable=False, server_default=sa.text("''")),
        sa.Column('company', sa.String(length=256), nullable=False, server_default=sa.text("''")),
        sa.Column('country', sa.String(length=64), nullable=False, server_default=sa.text("''")),
        sa.Column('city', sa.String(length=128), nullable=False, server_default=sa.text("''")),
        sa.Column('zip_code', sa.String(length=32), nullable=False, server_default=sa.text("''")),
        sa.Column('address', sa.Text(), nullable=False, server_default=sa.text("''")),
        sa.Column('phone', sa.String(length=64), nullable=False, server_default=sa.text("''")),
        sa.Column('email', sa.String(length=256), nullable=False, server_default=sa.text("''")),
        sa.Column('language', sa.String(length=16), nullable=False, server_default=sa.text("'en'")),
        sa.Column('password_hash', sa.String(length=512), nullable=False, server_default=sa.text("''")),
        sa.Column('investor_password_hash', sa.String(length=512), nullable=False, server_default=sa.text("''")),
        sa.Column('phone_password_hash', sa.String(length=512), nullable=False, server_default=sa.text("''")),
        sa.Column('otp_secret', sa.String(length=64), nullable=True),
        sa.Column('certificate_fingerprint', sa.String(length=128), nullable=True),
        sa.Column('status', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('external_id', sa.String(length=64), nullable=True),
        sa.Column('agent_login', sa.BigInteger(), nullable=True),
        sa.Column('comments', sa.Text(), nullable=False, server_default=sa.text("''")),
        sa.Column('registration_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_visit', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_pass_change', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
        sa.Column('mt5_extra', postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_clients_external_id', 'clients', ['external_id'], unique=False)
    op.create_index('ix_clients_client_id', 'clients', ['client_id'], unique=False)

    op.create_table(
        'coverage_accounts',
        sa.Column('account_id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default=sa.text("'USD'")),
        sa.Column('net_exposure_json', sa.Text(), nullable=True, server_default=sa.text("'{}'")),
        sa.Column('margin_level', sa.Numeric(precision=18, scale=8), nullable=False, server_default=sa.text('0')),
        sa.Column('trading_state', sa.String(length=32), nullable=False, server_default=sa.text("'NEUTRAL'")),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('account_id'),
    )

    op.create_table(
        'deals',
        sa.Column('deal_id', sa.String(), nullable=False),
        sa.Column('order_id', sa.String(), nullable=True),
        sa.Column('position_id', sa.String(), nullable=True),
        sa.Column('account_login', sa.BigInteger(), nullable=False),
        sa.Column('dealer_login', sa.BigInteger(), nullable=True),
        sa.Column('symbol', sa.String(), nullable=False),
        sa.Column('deal_type', sa.String(), nullable=False),
        sa.Column('entry', sa.String(), nullable=False, server_default=sa.text("'IN'")),
        sa.Column('reason', sa.String(), nullable=False, server_default=sa.text("'CLIENT'")),
        sa.Column('volume', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('price', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('external_id', sa.String(), nullable=True),
        sa.Column('order_ticket', sa.String(), nullable=True),
        sa.Column('original_deal_id', sa.String(), nullable=True),
        sa.Column('profit', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('0')),
        sa.Column('swap', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('0')),
        sa.Column('commission', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('0')),
        sa.Column('currency', sa.String(), nullable=False, server_default=sa.text("'USD'")),
        sa.Column('digits', sa.Integer(), nullable=False, server_default=sa.text('5')),
        sa.Column('digits_currency', sa.Integer(), nullable=False, server_default=sa.text('2')),
        sa.Column('contract_size', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('100000')),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('deal_id'),
    )
    op.create_index('idx_deals_symbol_time', 'deals', ['symbol', 'created_at'], unique=False)
    op.create_index('ix_deals_position_id', 'deals', ['position_id'], unique=False)
    op.create_index('idx_deals_account_time', 'deals', ['account_login', 'created_at'], unique=False)
    op.create_index('idx_deals_type', 'deals', ['deal_type'], unique=False)
    op.create_index('ix_deals_symbol', 'deals', ['symbol'], unique=False)
    op.create_index('ix_deals_order_id', 'deals', ['order_id'], unique=False)
    op.create_index('ix_deals_account_login', 'deals', ['account_login'], unique=False)
    op.create_index('ix_deals_original_deal_id', 'deals', ['original_deal_id'], unique=False)

    op.create_table(
        'domain_events',
        sa.Column('event_id', sa.String(length=64), nullable=False),
        sa.Column('event_type', sa.String(length=64), nullable=False),
        sa.Column('aggregate_id', sa.String(length=64), nullable=False),
        sa.Column('payload_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('event_id'),
    )
    op.create_index('idx_events_type', 'domain_events', ['event_type'], unique=False)
    op.create_index('idx_events_aggregate', 'domain_events', ['aggregate_id'], unique=False)

    op.create_table(
        'holidays',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True, server_default=sa.text("''")),
        sa.Column('mode', sa.String(), nullable=False, server_default=sa.text("'ENABLED'")),
        sa.Column('year', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('month', sa.Integer(), nullable=False, server_default=sa.text('1')),
        sa.Column('day', sa.Integer(), nullable=False, server_default=sa.text('1')),
        sa.Column('work_from', sa.String(), nullable=False, server_default=sa.text("'00:00:00'")),
        sa.Column('work_to', sa.String(), nullable=False, server_default=sa.text("'23:59:59'")),
        sa.Column('symbols', sa.Text(), nullable=True, server_default=sa.text("''")),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_holidays_date', 'holidays', ['year', 'month', 'day'], unique=False)
    op.create_index('idx_holidays_mode', 'holidays', ['mode'], unique=False)

    op.create_table(
        'managers',
        sa.Column('login', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=False, server_default=sa.text("''")),
        sa.Column('mailbox', sa.String(length=256), nullable=False, server_default=sa.text("''")),
        sa.Column('server_id', sa.Integer(), nullable=False, server_default=sa.text('1')),
        sa.Column('rights_json', postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('rights_mask_0', sa.BigInteger(), nullable=False, server_default=sa.text('0')),
        sa.Column('rights_mask_1', sa.BigInteger(), nullable=False, server_default=sa.text('0')),
        sa.Column('rights_mask_2', sa.BigInteger(), nullable=False, server_default=sa.text('0')),
        sa.Column('group_scope_json', postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('request_limit_logs', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('request_limit_reports', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('role', sa.String(length=32), nullable=False, server_default=sa.text("'READ_ONLY'")),
        sa.Column('password_hash', sa.String(length=512), nullable=False, server_default=sa.text("''")),
        sa.Column('totp_secret', sa.String(length=64), nullable=True),
        sa.Column('is_2fa_enabled', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('must_change_password', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('allowed_ips_json', postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('certificate_fingerprint', sa.String(length=128), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
        sa.Column('mt5_extra', postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('mt5_source', postgresql.JSONB(), nullable=True, server_default=sa.text("'{}'::jsonb")),
        sa.PrimaryKeyConstraint('login'),
    )

    op.create_table(
        'orders',
        sa.Column('ticket_id', sa.String(), nullable=False),
        sa.Column('external_id', sa.String(), nullable=True),
        sa.Column('gateway_id', sa.String(), nullable=True),
        sa.Column('account_login', sa.BigInteger(), nullable=False),
        sa.Column('dealer_login', sa.BigInteger(), nullable=True),
        sa.Column('symbol', sa.String(), nullable=False),
        sa.Column('order_type', sa.String(), nullable=False),
        sa.Column('reason', sa.String(), nullable=False, server_default=sa.text("'CLIENT'")),
        sa.Column('state', sa.String(), nullable=False, server_default=sa.text("'NEW'")),
        sa.Column('volume_initial', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('volume_current', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('price_order', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('price_sl', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('price_tp', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('price_trigger', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('time_setup', sa.DateTime(timezone=True), nullable=False),
        sa.Column('time_setup_msc', sa.BigInteger(), nullable=False, server_default=sa.text('0')),
        sa.Column('time_expiration', sa.DateTime(timezone=True), nullable=True),
        sa.Column('time_done', sa.DateTime(timezone=True), nullable=True),
        sa.Column('time_in_force', sa.String(), nullable=False, server_default=sa.text("'GTC'")),
        sa.Column('activation_mode', sa.String(), nullable=False, server_default=sa.text("'NONE'")),
        sa.Column('activation_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('activation_price', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('activation_flags', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('digits', sa.Integer(), nullable=False, server_default=sa.text('5')),
        sa.Column('digits_currency', sa.Integer(), nullable=False, server_default=sa.text('2')),
        sa.Column('contract_size', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('100000')),
        sa.Column('expert_id', sa.String(), nullable=True),
        sa.Column('expert_name', sa.String(), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('order_matching', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('ticket_id'),
    )
    op.create_index('ix_orders_account_login', 'orders', ['account_login'], unique=False)
    op.create_index('idx_orders_symbol_state', 'orders', ['symbol', 'state'], unique=False)
    op.create_index('idx_orders_time_setup', 'orders', ['time_setup'], unique=False)
    op.create_index('idx_orders_account_state', 'orders', ['account_login', 'state'], unique=False)
    op.create_index('ix_orders_symbol', 'orders', ['symbol'], unique=False)

    op.create_table(
        'positions',
        sa.Column('position_id', sa.String(), nullable=False),
        sa.Column('external_id', sa.String(), nullable=True),
        sa.Column('identifier', sa.String(), nullable=True),
        sa.Column('account_login', sa.BigInteger(), nullable=False),
        sa.Column('symbol', sa.String(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('reason', sa.String(), nullable=False, server_default=sa.text("'CLIENT'")),
        sa.Column('volume', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('price_open', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('price_current', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('price_sl', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('price_tp', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('profit', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('0')),
        sa.Column('swap', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('0')),
        sa.Column('commission', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('0')),
        sa.Column('currency', sa.String(), nullable=False, server_default=sa.text("'USD'")),
        sa.Column('digits', sa.Integer(), nullable=False, server_default=sa.text('5')),
        sa.Column('digits_currency', sa.Integer(), nullable=False, server_default=sa.text('2')),
        sa.Column('contract_size', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('100000')),
        sa.Column('deal_open', sa.String(), nullable=True),
        sa.Column('deal_close', sa.String(), nullable=True),
        sa.Column('position_by_id', sa.String(), nullable=True),
        sa.Column('time_create', sa.DateTime(timezone=True), nullable=False),
        sa.Column('time_update', sa.DateTime(timezone=True), nullable=False),
        sa.Column('time_done', sa.DateTime(timezone=True), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('magic_number', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.PrimaryKeyConstraint('position_id'),
    )
    op.create_index('ix_positions_account_login', 'positions', ['account_login'], unique=False)
    op.create_index('idx_positions_account_symbol', 'positions', ['account_login', 'symbol'], unique=False)
    op.create_index('ix_positions_symbol', 'positions', ['symbol'], unique=False)
    op.create_index('idx_positions_time_create', 'positions', ['time_create'], unique=False)
    op.create_index('ix_positions_identifier', 'positions', ['identifier'], unique=False)
    op.create_index('idx_positions_action', 'positions', ['action'], unique=False)

    op.create_table(
        'routing_rules',
        sa.Column('rule_id', sa.String(length=32), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('destination', sa.String(length=32), nullable=False),
        sa.Column('group_filter', sa.String(length=128), nullable=True),
        sa.Column('symbol_filter', sa.String(length=64), nullable=True),
        sa.Column('volume_min', sa.Numeric(precision=18, scale=8), nullable=True),
        sa.Column('volume_max', sa.Numeric(precision=18, scale=8), nullable=True),
        sa.Column('gateway_id', sa.String(length=64), nullable=True),
        sa.Column('coverage_account_id', sa.String(length=64), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('rule_id'),
    )

    op.create_table(
        'symbols',
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('path', sa.String(length=256), nullable=False, server_default=sa.text("''")),
        sa.Column('symbol_id', sa.String(length=64), nullable=True),
        sa.Column('description', sa.String(length=256), nullable=False, server_default=sa.text("''")),
        sa.Column('base_currency', sa.String(length=8), nullable=False, server_default=sa.text("'USD'")),
        sa.Column('quote_currency', sa.String(length=8), nullable=False, server_default=sa.text("'USD'")),
        sa.Column('digits', sa.Integer(), nullable=False, server_default=sa.text('5')),
        sa.Column('point', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('0')),
        sa.Column('mt5_tick_size', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('0')),
        sa.Column('tick_value', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('0')),
        sa.Column('contract_size', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('100000')),
        sa.Column('calc_mode', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('trade_mode', sa.Integer(), nullable=False, server_default=sa.text('4')),
        sa.Column('exec_mode', sa.Integer(), nullable=False, server_default=sa.text('2')),
        sa.Column('gtc_mode', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('fill_flags', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('expiration_flags', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('order_flags', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('is_trade_allowed', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('spread', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('spread_balance', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('stops_level', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('freeze_level', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('volume_min', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('0')),
        sa.Column('volume_max', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('0')),
        sa.Column('volume_step', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('0')),
        sa.Column('volume_limit', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('0')),
        sa.Column('margin_initial_buy', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('1')),
        sa.Column('margin_initial_sell', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('1')),
        sa.Column('margin_initial_buy_limit', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('1')),
        sa.Column('margin_initial_sell_limit', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('1')),
        sa.Column('margin_initial_buy_stop', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('1')),
        sa.Column('margin_initial_sell_stop', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('1')),
        sa.Column('margin_initial_buy_stop_limit', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('1')),
        sa.Column('margin_initial_sell_stop_limit', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('1')),
        sa.Column('margin_maintenance_buy', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('1')),
        sa.Column('margin_maintenance_sell', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('1')),
        sa.Column('margin_maintenance_buy_limit', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('1')),
        sa.Column('margin_maintenance_sell_limit', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('1')),
        sa.Column('margin_maintenance_buy_stop', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('1')),
        sa.Column('margin_maintenance_sell_stop', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('1')),
        sa.Column('margin_maintenance_buy_stop_limit', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('1')),
        sa.Column('margin_maintenance_sell_stop_limit', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('1')),
        sa.Column('swap_mode', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('swap_long', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('0')),
        sa.Column('swap_short', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('0')),
        sa.Column('swap_3day', sa.Integer(), nullable=False, server_default=sa.text('3')),
        sa.Column('swap_year_days', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('sessions_quotes_json', postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('sessions_trades_json', postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('time_start', sa.BigInteger(), nullable=False, server_default=sa.text('0')),
        sa.Column('time_expiration', sa.BigInteger(), nullable=False, server_default=sa.text('0')),
        sa.Column('option_mode', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('strike_price', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('0')),
        sa.Column('face_value', sa.Numeric(precision=20, scale=8), nullable=False, server_default=sa.text('0')),
        sa.Column('face_value_currency', sa.String(length=8), nullable=False, server_default=sa.text("'USD'")),
        sa.Column('mt5_extra', postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('mt5_scale', postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('mt5_source', postgresql.JSONB(), nullable=True, server_default=sa.text("'{}'::jsonb")),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('name'),
    )
    op.create_index('ix_symbols_symbol_id', 'symbols', ['symbol_id'], unique=True)
    op.create_index('idx_symbols_path', 'symbols', ['path'], unique=False)


def downgrade() -> None:

    op.drop_index('idx_symbols_path', table_name='symbols')
    op.drop_index('ix_symbols_symbol_id', table_name='symbols')
    op.drop_table('symbols')

    op.drop_table('routing_rules')

    op.drop_index('idx_positions_account_symbol', table_name='positions')
    op.drop_index('idx_positions_action', table_name='positions')
    op.drop_index('idx_positions_time_create', table_name='positions')
    op.drop_index('ix_positions_account_login', table_name='positions')
    op.drop_index('ix_positions_identifier', table_name='positions')
    op.drop_index('ix_positions_symbol', table_name='positions')
    op.drop_table('positions')

    op.drop_index('idx_orders_account_state', table_name='orders')
    op.drop_index('idx_orders_symbol_state', table_name='orders')
    op.drop_index('idx_orders_time_setup', table_name='orders')
    op.drop_index('ix_orders_account_login', table_name='orders')
    op.drop_index('ix_orders_symbol', table_name='orders')
    op.drop_table('orders')

    op.drop_table('managers')

    op.drop_index('idx_holidays_date', table_name='holidays')
    op.drop_index('idx_holidays_mode', table_name='holidays')
    op.drop_table('holidays')

    op.drop_index('idx_groups_account_type', table_name='groups')
    op.drop_index('idx_groups_server', table_name='groups')
    op.drop_index('ix_groups_group_id', table_name='groups')
    op.drop_table('groups')

    op.drop_index('idx_events_aggregate', table_name='domain_events')
    op.drop_index('idx_events_type', table_name='domain_events')
    op.drop_table('domain_events')

    op.drop_index('idx_deals_account_time', table_name='deals')
    op.drop_index('idx_deals_symbol_time', table_name='deals')
    op.drop_index('idx_deals_type', table_name='deals')
    op.drop_index('ix_deals_account_login', table_name='deals')
    op.drop_index('ix_deals_order_id', table_name='deals')
    op.drop_index('ix_deals_original_deal_id', table_name='deals')
    op.drop_index('ix_deals_position_id', table_name='deals')
    op.drop_index('ix_deals_symbol', table_name='deals')
    op.drop_table('deals')

    op.drop_table('coverage_accounts')

    op.drop_index('ix_clients_client_id', table_name='clients')
    op.drop_index('ix_clients_external_id', table_name='clients')
    op.drop_table('clients')

    op.drop_index('idx_bars_symbol_timeframe_time', table_name='bars')
    op.drop_index('ix_bars_open_time', table_name='bars')
    op.drop_index('ix_bars_symbol', table_name='bars')
    op.drop_index('ix_bars_timeframe', table_name='bars')
    op.drop_table('bars')

    op.drop_index('idx_balance_ops_login', table_name='balance_operations')
    op.drop_index('idx_balance_ops_reference', table_name='balance_operations')
    op.drop_index('idx_balance_ops_type', table_name='balance_operations')
    op.drop_table('balance_operations')

    op.drop_index('idx_accounts_client', table_name='accounts')
    op.drop_index('idx_accounts_group', table_name='accounts')
    op.drop_index('idx_accounts_type', table_name='accounts')
    op.drop_index('ix_accounts_client_id', table_name='accounts')
    op.drop_index('ix_accounts_group_id', table_name='accounts')
    op.drop_table('accounts')
