"""margin reservation: accounts.margin_reserved + orders.reserved_margin

Revision ID: 004_margin_reservation
Revises: 003_symbols_margin_currency
Create Date: 2026-09-11

M6 (M4 debt #1): between risk approval and the fill being booked there was no
hold on free margin - across a Redis bus or two API nodes, two concurrent
orders could both pass the same check. accounts.margin_reserved is the total
hold; orders.reserved_margin records how much each order holds so the release
on fill/reject is exact. Quoted server defaults: the M5 lesson (bare words are
a SQLite-ism PostgreSQL rejects).
"""
from alembic import op
import sqlalchemy as sa


revision = '004_margin_reservation'
down_revision = '003_symbols_margin_currency'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'accounts',
        sa.Column(
            'margin_reserved',
            sa.Numeric(20, 8),
            nullable=False,
            server_default=sa.text("'0'"),
        ),
    )
    op.add_column(
        'orders',
        sa.Column(
            'reserved_margin',
            sa.Numeric(20, 8),
            nullable=False,
            server_default=sa.text("'0'"),
        ),
    )


def downgrade() -> None:
    op.drop_column('orders', 'reserved_margin')
    op.drop_column('accounts', 'margin_reserved')
