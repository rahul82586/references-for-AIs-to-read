"""identity plane: the IMTUser-shaped account, the KYC client fields, the login allocator.

Revision ID: 009_identity_plane
Revises: 008_reconciliation_breaks
Create Date: 2026-09-13

RECONSTRUCTED MIGRATION. The original 009 was written inside a session that died
mid-build; it was applied to the live Neon database but its source file was never
pushed (the session-death protocol exists precisely for this). This file rebuilds
it DDL-faithful to what the live server carries - every column, type, nullability,
default and index below was read back from Neon's information_schema on
2026-09-13, not guessed - so a fresh database migrated to head and the production
database converge on the same schema.

Because production already records '009_identity_plane' in alembic_version, this
upgrade is a no-op there. Everywhere else it is IDEMPOTENT by inspection: each
column/table/index is added only when missing, so a half-applied database (or a
re-run after a crash) converges instead of erroring.

What it adds:
  accounts +33 columns  the IMTUser identity surface: names/company/location,
                        language, residency (RE/NR), ID number, lead source &
                        campaign, MetaQuotes ID, visitor ID, comment, colour
                        (MT5's AABBGGRR int), agent login, bank account,
                        interest rate, the per-account limits (NULL = inherit
                        the group; 0 would mean "nothing allowed" - a different
                        thing), the 16-bit UserRight mask, and the per-ACCOUNT
                        password material MT5 puts on IMTUser, not on the
                        person: investor / phone / Web-API hashes, OTP secret,
                        certificate serial, last IP, last password change.
  clients  +5 columns   middle name, state, ID number, lead source, campaign.
                        (The legacy password columns on clients STAY: the move
                        is additive until the entity/mapper layer owns the
                        account-side copies - one writer per number.)
  login_counters        the "Next" button's race-safe allocator: scope ->
                        next_login + login_floor, advanced by a single
                        conditional UPDATE ... RETURNING, never MAX(login)+1.

SQLite-safe by construction: no jsonb columns are added, every default is a
constant, and the partial index on the TECHNICAL bit uses an expression both
engines support. The models gain these columns in the same milestone as the
mappers that round-trip them - deliberately NOT here: a declared column with no
mapper support is a full-row save() waiting to blank it (the D8b/D15 class).
"""
from alembic import op
import sqlalchemy as sa


revision = '009_identity_plane'
down_revision = '008_reconciliation_breaks'
branch_labels = None
depends_on = None


NUMERIC = sa.Numeric(20, 8)

#: accounts: (name, type, nullable, server_default) - exactly the live shapes.
ACCOUNT_COLUMNS = [
    ('first_name', sa.String(length=128), False, "''"),
    ('last_name', sa.String(length=128), False, "''"),
    ('middle_name', sa.String(length=128), False, "''"),
    ('company', sa.String(length=256), False, "''"),
    ('country', sa.String(length=64), False, "''"),
    ('state', sa.String(length=64), False, "''"),
    ('city', sa.String(length=128), False, "''"),
    ('zip_code', sa.String(length=32), False, "''"),
    ('address', sa.Text(), False, "''"),
    ('phone', sa.String(length=64), False, "''"),
    ('email', sa.String(length=256), False, "''"),
    ('language', sa.String(length=16), False, "'en'"),
    ('residency_status', sa.String(length=8), False, "''"),
    ('id_number', sa.String(length=128), False, "''"),
    ('lead_source', sa.String(length=128), False, "''"),
    ('lead_campaign', sa.String(length=128), False, "''"),
    ('mqid', sa.String(length=64), False, "''"),
    ('visitor_id', sa.String(length=64), False, "''"),
    ('comment', sa.Text(), False, "''"),
    ('color', sa.BigInteger(), True, None),
    ('agent_login', sa.BigInteger(), True, None),
    ('bank_account', sa.String(length=128), False, "''"),
    ('interest_rate', NUMERIC, False, "'0'"),
    ('limit_orders', sa.Integer(), True, None),
    ('limit_positions_value', NUMERIC, True, None),
    ('rights', sa.BigInteger(), False, "'0'"),
    ('investor_password_hash', sa.String(length=512), False, "''"),
    ('phone_password_hash', sa.String(length=512), False, "''"),
    ('webapi_password_hash', sa.String(length=512), False, "''"),
    ('otp_secret', sa.String(length=64), True, None),
    ('cert_serial_number', sa.BigInteger(), True, None),
    ('last_ip', sa.String(length=64), False, "''"),
    ('last_pass_change', sa.DateTime(timezone=True), True, None),
]

CLIENT_COLUMNS = [
    ('middle_name', sa.String(length=128), False, "''"),
    ('state', sa.String(length=64), False, "''"),
    ('id_number', sa.String(length=128), False, "''"),
    ('lead_source', sa.String(length=128), False, "''"),
    ('lead_campaign', sa.String(length=128), False, "''"),
]

#: USER_RIGHT_TECHNICAL - the bit the partial index exposes for the manager
#: terminal's "hide technical accounts" filter.
_TECHNICAL_BIT = 0x10000


def _existing_columns(table: str) -> set:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {c['name'] for c in inspector.get_columns(table)}


def _existing_indexes(table: str) -> set:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {ix['name'] for ix in inspector.get_indexes(table)}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    # --- accounts -----------------------------------------------------------
    have = _existing_columns('accounts')
    for name, type_, nullable, default in ACCOUNT_COLUMNS:
        if name in have:
            continue
        op.add_column(
            'accounts',
            sa.Column(
                name,
                type_,
                nullable=nullable,
                server_default=sa.text(default) if default is not None else None,
            ),
        )
    acct_ix = _existing_indexes('accounts')
    if 'idx_accounts_agent_login' not in acct_ix:
        op.create_index('idx_accounts_agent_login', 'accounts', ['agent_login'])
    if 'idx_accounts_rights_technical' not in acct_ix:
        # Partial index: only rows with the TECHNICAL bit pay for an index entry,
        # which is exactly the population the manager terminal filters on.
        predicate = sa.text(f'(rights & {_TECHNICAL_BIT}) <> 0')
        op.create_index(
            'idx_accounts_rights_technical',
            'accounts',
            ['rights'],
            postgresql_where=predicate,
            sqlite_where=predicate,
        )

    # --- clients --------------------------------------------------------------
    have = _existing_columns('clients')
    for name, type_, nullable, default in CLIENT_COLUMNS:
        if name in have:
            continue
        op.add_column(
            'clients',
            sa.Column(
                name,
                type_,
                nullable=nullable,
                server_default=sa.text(default) if default is not None else None,
            ),
        )

    # --- login allocator ------------------------------------------------------
    if 'login_counters' not in tables:
        op.create_table(
            'login_counters',
            sa.Column('scope', sa.String(length=64), primary_key=True),
            sa.Column('next_login', sa.BigInteger(), nullable=False, server_default=sa.text("'0'")),
            sa.Column('login_floor', sa.BigInteger(), nullable=False, server_default=sa.text("'0'")),
            sa.Column(
                'updated_at',
                sa.DateTime(timezone=True),
                nullable=True,
                server_default=sa.func.now(),
            ),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if 'login_counters' in tables:
        op.drop_table('login_counters')

    have = _existing_columns('clients')
    for name, *_ in reversed(CLIENT_COLUMNS):
        if name in have:
            op.drop_column('clients', name)

    acct_ix = _existing_indexes('accounts')
    for ix in ('idx_accounts_rights_technical', 'idx_accounts_agent_login'):
        if ix in acct_ix:
            op.drop_index(ix, table_name='accounts')
    have = _existing_columns('accounts')
    for name, *_ in reversed(ACCOUNT_COLUMNS):
        if name in have:
            op.drop_column('accounts', name)
