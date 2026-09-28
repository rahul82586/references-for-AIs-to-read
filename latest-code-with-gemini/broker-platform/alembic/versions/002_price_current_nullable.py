"""positions.price_current becomes nullable.

Revision ID: 002_price_current_nullable
Revises: 001_initial_schema
Create Date: 2026-09-10

Why
---
`Position.price_current` is `Optional[Price] = None` in the domain, and the entity says
why: a fresh position has no current price until the first tick reprices it, and a
sentinel of 0 or 1 would be a lie that some later calculation multiplies by. The column
was declared NOT NULL, so the two disagreed about the one state that ALWAYS occurs -
every position created by a fill starts with price_current = None.

The mapper papered over it by dereferencing `position.price_current.value`, which raised
AttributeError; making the mapper honest about None then hit the constraint instead:

    sqlite3.IntegrityError: NOT NULL constraint failed: positions.price_current

So no account could ever open its first position against the real schema. The domain is
right and the column was wrong, so the column changes.

`batch_alter_table` rather than a bare `alter_column` because SQLite cannot alter a
column in place; PostgreSQL takes the batch path as a no-op rewrite. Production is
PostgreSQL, and the M2/M4 proofs run on SQLite, so the migration has to work on both.
"""

from alembic import op
import sqlalchemy as sa

revision = "002_price_current_nullable"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("positions") as batch:
        batch.alter_column(
            "price_current",
            existing_type=sa.Numeric(precision=20, scale=8),
            nullable=True,
        )


def downgrade() -> None:
    # Not reversible in general: rows written while the column was nullable hold NULL,
    # and there is no honest value to backfill them with. Refuse rather than invent one.
    raise RuntimeError(
        "cannot downgrade 002: positions.price_current may hold NULLs that a NOT NULL "
        "constraint would reject. Backfill them from the latest tick before downgrading."
    )
