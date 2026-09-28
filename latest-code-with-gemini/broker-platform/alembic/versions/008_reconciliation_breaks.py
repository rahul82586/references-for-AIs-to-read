"""reconciliation_breaks: the persisted difference between our book and the venue's.

Revision ID: 008_reconciliation_breaks
Revises: 007_mt5_routing_rules
Create Date: 2026-09-12

A break is a row an operator works through, so it carries its own lifecycle:
OPEN -> RESOLVED / IGNORED, with `occurrences` and `first_seen` ageing it. The
`identity` column is the dedupe key (kind|symbol|our_key|venue_key) so the same
difference found on consecutive sweeps updates one row instead of creating a pile
of duplicates - an operator needs to see how OLD a break is, not ten copies of it.

Quoted '::jsonb' server defaults per the M5 lesson: a bare '{}' is legal in
SQLite and rejected by PostgreSQL.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '008_reconciliation_breaks'
down_revision = '007_mt5_routing_rules'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'reconciliation_breaks',
        sa.Column('break_id', sa.String(length=64), primary_key=True),
        # kind|symbol|our_key|venue_key - the dedupe identity
        sa.Column('identity', sa.String(length=512), nullable=False),
        sa.Column('kind', sa.String(length=40), nullable=False),
        sa.Column('severity', sa.String(length=16), nullable=False,
                  server_default=sa.text("'MEDIUM'")),
        sa.Column('status', sa.String(length=16), nullable=False,
                  server_default=sa.text("'OPEN'")),
        sa.Column('symbol', sa.String(length=64), nullable=False,
                  server_default=sa.text("''")),
        sa.Column('venue', sa.String(length=64), nullable=False,
                  server_default=sa.text("''")),
        sa.Column('detail', sa.Text(), nullable=False, server_default=sa.text("''")),
        sa.Column('our_key', sa.String(length=128), nullable=True),
        sa.Column('venue_key', sa.String(length=128), nullable=True),
        sa.Column('our_volume', sa.NUMERIC(), nullable=True),
        sa.Column('venue_volume', sa.NUMERIC(), nullable=True),
        sa.Column('our_price', sa.NUMERIC(), nullable=True),
        sa.Column('venue_price', sa.NUMERIC(), nullable=True),
        sa.Column('account_login', sa.BigInteger(), nullable=True),
        sa.Column('occurrences', sa.Integer(), nullable=False,
                  server_default=sa.text("'1'")),
        sa.Column('first_seen', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_seen', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolution', sa.Text(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('(now())')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('(now())')),
    )
    # One open break per identity. A partial unique index would be ideal but
    # SQLite does not support it portably here, so uniqueness is enforced in the
    # repository and this index just makes the lookup fast.
    op.create_index('ix_recon_breaks_identity', 'reconciliation_breaks',
                    ['identity'], unique=False)
    op.create_index('ix_recon_breaks_status', 'reconciliation_breaks',
                    ['status', 'severity'])
    op.create_index('ix_recon_breaks_symbol', 'reconciliation_breaks', ['symbol'])

    # D9: the valuation sweep needs to know when an account was last revalued, so
    # a boot after a long shutdown can tell "current" from "frozen since Friday".
    op.add_column('accounts', sa.Column(
        'last_valuation_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('accounts', 'last_valuation_at')
    op.drop_index('ix_recon_breaks_symbol', table_name='reconciliation_breaks')
    op.drop_index('ix_recon_breaks_status', table_name='reconciliation_breaks')
    op.drop_index('ix_recon_breaks_identity', table_name='reconciliation_breaks')
    op.drop_table('reconciliation_breaks')
