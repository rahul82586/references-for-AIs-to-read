"""010_sync_schema

Revision ID: c8f8333980f2
Revises: 009_identity_plane
Create Date: 2026-09-28 19:30:12.980624

"""
from alembic import op
import sqlalchemy as sa


revision = '010_sync_schema'
down_revision = '009_identity_plane'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('managers', sa.Column('group_name', sa.String(length=128), nullable=True))
    bind = op.get_bind()
    if bind.dialect.name != 'sqlite':
        op.create_foreign_key('fk_managers_group_name', 'managers', 'groups', ['group_name'], ['name'])
    op.execute(
        "UPDATE managers SET group_name = ("
        "  SELECT group_name FROM accounts WHERE accounts.login = managers.login"
        ") WHERE group_name IS NULL"
    )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != 'sqlite':
        op.drop_constraint('fk_managers_group_name', 'managers', type_='foreignkey')
    op.drop_column('managers', 'group_name')
