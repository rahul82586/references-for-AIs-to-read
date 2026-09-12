"""accounts.password_hash: client login credentials (M6).

Before M6, POST /api/v1/auth/login issued a JWT to anyone who named an
existing, enabled login_id: the route parsed the body by hand and never read
the password, even though the LoginRequest schema declared one required. The
client API was authenticate-in-name-only. This column stores the Argon2 hash
(same hasher the manager bootstrap uses); the domain never holds plaintext,
and an unset hash REJECTS login (fail closed) rather than falling back.

Quoted server default: the M5 lesson.
"""
from alembic import op
import sqlalchemy as sa


revision = '005_accounts_password_hash'
down_revision = '004_margin_reservation'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'accounts',
        sa.Column(
            'password_hash',
            sa.String(length=512),
            nullable=False,
            server_default=sa.text("''"),
        ),
    )


def downgrade() -> None:
    op.drop_column('accounts', 'password_hash')
