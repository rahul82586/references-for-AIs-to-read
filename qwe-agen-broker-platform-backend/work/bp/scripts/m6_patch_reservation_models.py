"""M6 patch: margin reservation across the flow (M4 debt #1).

accounts.margin_reserved + orders.reserved_margin, an atomic conditional
UPDATE in the SQL repository, reservation at approval, release at fill and at
every rejection funnel. Every site goes through
application/services/margin_reservation.py.
"""
import ast
import io
import pathlib


def read(path):
    p = pathlib.Path(path)
    src = io.open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in src else "\n"
    return src, nl


def write(path, src, nl):
    ast.parse(src.replace("\r\n", "\n") if nl == "\r\n" else src)
    io.open(path, "w", encoding="utf-8", newline="").write(src)


def apply(path, pairs):
    src, nl = read(path)
    for old, new in pairs:
        if nl == "\r\n":
            old = old.replace("\n", "\r\n")
            new = new.replace("\n", "\r\n")
        assert src.count(old) == 1, f"{path}: anchor {src.count(old)}x: {old[:70]!r}"
        src = src.replace(old, new)
    write(path, src, nl)
    print(f"{path}: {len(pairs)} patch(es) [{nl.strip() or 'LF'}]")


# --- Account entity --------------------------------------------------------
apply("core/domains/accounts/account.py", [(
    """    margin_free: Money = field(default_factory=lambda: Money(Decimal('0'), "USD"))
""",
    """    margin_free: Money = field(default_factory=lambda: Money(Decimal('0'), "USD"))
    #: M6: margin held for in-flight (approved, not yet filled) orders. Counts
    #: against free margin in the pre-trade check; released exactly on fill or
    #: rejection via orders.reserved_margin.
    margin_reserved: Money = field(default_factory=lambda: Money(Decimal('0'), "USD"))
""",
)])

# --- Order entity ----------------------------------------------------------
apply("core/domains/oms/entities/order.py", [(
    "    reason: OrderReason = OrderReason.CLIENT\n",
    """    reason: OrderReason = OrderReason.CLIENT
    #: Margin held against the account's free margin while this order is in
    #: flight (M6). Set at approval by PreTradeRiskService, zeroed by the fill
    #: (RecordDealHandler) or the rejection (ExecutionOrchestrator).
    reserved_margin: Decimal = Decimal('0')
""",
)])

# --- AccountModel + account mappers ---------------------------------------
apply("infrastructure/persistence/account_models.py", [
    (
        "    margin_free = Column(NUMERIC, nullable=False, default=0)\n",
        "    margin_free = Column(NUMERIC, nullable=False, default=0)\n"
        "    margin_reserved = Column(NUMERIC, nullable=False, default=0)\n",
    ),
    (
        "        margin_free=account.margin_free.amount,\n",
        "        margin_free=account.margin_free.amount,\n"
        "        margin_reserved=account.margin_reserved.amount,\n",
    ),
    (
        "        margin_used=_money(model.margin_used, currency),\n",
        "        margin_used=_money(model.margin_used, currency),\n"
        "        margin_reserved=_money(getattr(model, 'margin_reserved', None), currency),\n",
    ),
])

# --- OrderModel + order mappers -------------------------------------------
apply("infrastructure/persistence/db_models.py", [(
    "    volume_initial = Column(Numeric(20, 8), nullable=False)\n"
    "    volume_current = Column(Numeric(20, 8), nullable=False)\n",
    "    volume_initial = Column(Numeric(20, 8), nullable=False)\n"
    "    volume_current = Column(Numeric(20, 8), nullable=False)\n"
    "    reserved_margin = Column(Numeric(20, 8), nullable=False, default=0)\n",
)])

apply("infrastructure/persistence/mappers.py", [
    (
        "        volume_initial=order.volume_initial.value,\n"
        "        volume_current=order.volume_current.value,\n",
        "        volume_initial=order.volume_initial.value,\n"
        "        volume_current=order.volume_current.value,\n"
        "        reserved_margin=order.reserved_margin,\n",
    ),
    (
        "        volume_initial=Volume(Decimal(str(model.volume_initial))),\n"
        "        volume_current=Volume(Decimal(str(model.volume_current))),\n",
        "        volume_initial=Volume(Decimal(str(model.volume_initial))),\n"
        "        volume_current=Volume(Decimal(str(model.volume_current))),\n"
        "        reserved_margin=Decimal(str(getattr(model, 'reserved_margin', 0) or 0)),\n",
    ),
])

# --- Port declaration ------------------------------------------------------
apply("core/ports/interfaces.py", [(
    """    @abstractmethod
    async def save(self, account: T) -> T:
        \"\"\"Persists an account aggregate.\"\"\"
        pass
""",
    """    @abstractmethod
    async def save(self, account: T) -> T:
        \"\"\"Persists an account aggregate.\"\"\"
        pass

    async def reserve_margin(self, login_id: Any, amount: Any) -> bool:
        \"\"\"Atomically hold `amount` of free margin for an in-flight order (M6).

        Returns False when the account no longer covers it. MUST be a single
        conditional UPDATE in SQL implementations, so two nodes racing the same
        account cannot both win. The base declaration raises NotImplementedError:
        callers (application.services.margin_reservation) fall back to the
        per-account-locked in-process path and log that they did.
        \"\"\"
        raise NotImplementedError

    async def release_margin(self, login_id: Any, amount: Any) -> None:
        \"\"\"Release a hold placed by reserve_margin (fill or rejection).\"\"\"
        raise NotImplementedError
""",
)])

# --- SQL implementation ----------------------------------------------------
apply("infrastructure/persistence/repositories/account_repository.py", [(
    "    async def save(self, account: Account, session: Optional[AsyncSession] = None) -> Account:\n",
    """    async def reserve_margin(self, login_id: Any, amount: Any, session: Optional[AsyncSession] = None) -> bool:
        \"\"\"One conditional UPDATE: hold `amount` only while free margin covers it.

        free = balance + credit + profit - margin_used - margin_reserved. Two
        concurrent reservations cannot both succeed: the database serialises
        the row updates and the loser's WHERE no longer matches (rowcount 0).
        \"\"\"
        from decimal import Decimal as _D

        from sqlalchemy import text as sa_text

        stmt = sa_text(
            "UPDATE accounts SET margin_reserved = margin_reserved + :amt "
            "WHERE login = :login AND "
            "(balance + credit + profit - margin_used - margin_reserved) >= :amt"
        )
        params = {"amt": _D(str(amount)), "login": str(login_id)}
        if session is not None:
            result = await session.execute(stmt, params)
        else:
            async with self.session_factory() as sess:
                result = await sess.execute(stmt, params)
                await sess.commit()
        return (result.rowcount or 0) == 1

    async def release_margin(self, login_id: Any, amount: Any, session: Optional[AsyncSession] = None) -> None:
        \"\"\"Release a hold, clamped at zero (a double release must not go negative).\"\"\"
        from decimal import Decimal as _D

        from sqlalchemy import text as sa_text

        stmt = sa_text(
            "UPDATE accounts SET margin_reserved = "
            "CASE WHEN margin_reserved >= :amt THEN margin_reserved - :amt ELSE 0 END "
            "WHERE login = :login"
        )
        params = {"amt": _D(str(amount)), "login": str(login_id)}
        if session is not None:
            await session.execute(stmt, params)
        else:
            async with self.session_factory() as sess:
                await sess.execute(stmt, params)
                await sess.commit()

    async def save(self, account: Account, session: Optional[AsyncSession] = None) -> Account:
""",
)])

print("model/entity/port/sql patches applied")
