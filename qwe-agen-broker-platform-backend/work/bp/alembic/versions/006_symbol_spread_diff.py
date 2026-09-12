"""symbols.spread_diff + spread_diff_balance: model the quarantined MT5 fields.

Revision ID: 006_symbol_spread_diff
Revises: 005_accounts_password_hash
Create Date: 2026-09-11

M7: MT5's symbol-level SpreadDiff and SpreadDiffBalance were quarantined
(lossless on the wire, invisible to the domain), so the pricing engine had
nothing to read. Both are integer point counts; quoted server defaults per the
M5 lesson.
"""
from alembic import op
import sqlalchemy as sa


revision = '006_symbol_spread_diff'
down_revision = '005_accounts_password_hash'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'symbols',
        sa.Column('spread_diff', sa.Integer(), nullable=False, server_default=sa.text("'0'")),
    )
    op.add_column(
        'symbols',
        sa.Column('spread_diff_balance', sa.Integer(), nullable=False, server_default=sa.text("'0'")),
    )


def downgrade() -> None:
    op.drop_column('symbols', 'spread_diff_balance')
    op.drop_column('symbols', 'spread_diff')
