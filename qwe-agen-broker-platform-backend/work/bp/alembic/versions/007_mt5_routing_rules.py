"""mt5_routing_rules: the MT5 request-policy table (M8).

Revision ID: 007_mt5_routing_rules
Revises: 006_symbol_spread_diff
Create Date: 2026-09-11

The wire record is stored verbatim (JSONB) so rules re-export byte-identically;
typed hot columns mirror name/position/mode/action/masks for listing and
ordering. Quoted/'::jsonb' server defaults per the M5 lesson.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '007_mt5_routing_rules'
down_revision = '006_symbol_spread_diff'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'mt5_routing_rules',
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False, server_default=sa.text("'0'")),
        sa.Column('mode', sa.Integer(), nullable=False, server_default=sa.text("'1'")),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column('action', sa.Integer(), nullable=False, server_default=sa.text("'0'")),
        sa.Column('request_mask', sa.BigInteger(), nullable=False, server_default=sa.text("'0'")),
        sa.Column('type_mask', sa.Integer(), nullable=False, server_default=sa.text("'0'")),
        sa.Column('record', postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.PrimaryKeyConstraint('name'),
    )
    op.create_index('idx_mt5_routing_position', 'mt5_routing_rules', ['position'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_mt5_routing_position', table_name='mt5_routing_rules')
    op.drop_table('mt5_routing_rules')
