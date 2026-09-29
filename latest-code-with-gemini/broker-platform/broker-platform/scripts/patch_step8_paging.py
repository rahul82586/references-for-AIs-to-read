#!/usr/bin/env python3
"""Step 8 patch 1/4: SQL-level paging on the ports and the SQL repositories.

Adds find_page(limit, offset, **filters) -> (rows, total) to:
  ports     IAccountRepository, IClientRepository, IManagerRepository,
            IDealRepository, IOrderRepository, IPositionRepository
  sql       SqlAccountRepository, SqlClientRepository, SqlManagerRepository,
            SqlDealRepository, SqlOrderRepository, SqlPositionRepository

The rule (IDENTITY-BUILD-PLAN step 8): WHERE/LIMIT/OFFSET go into SQL and
`total` counts ALL matching rows - find_all()[:limit] loads every row then
throws most away, and a pager whose total is the page size is a lie.

Idempotent; run from the bp root.
"""
import os
import sys

WS = os.getcwd()
APPLIED = []


def patch(rel, pairs, required=True):
    path = os.path.join(WS, rel)
    src = open(path, encoding="utf-8", newline="").read()
    crlf = "\r\n" in src
    work = src.replace("\r\n", "\n")
    changed = False
    for old, new in pairs:
        if new.strip() and new.strip().splitlines()[0].strip() in work and old not in work:
            continue  # already applied
        if old not in work:
            if required:
                print(f"ANCHOR MISSING in {rel}: {old[:70]!r}")
                sys.exit(1)
            continue
        work = work.replace(old, new, 1)
        changed = True
    if changed:
        if crlf:
            work = work.replace("\n", "\r\n")
        open(path, "w", encoding="utf-8", newline="").write(work)
        APPLIED.append(rel)


# ---------------------------------------------------------------- ports ----
PORT_METHOD = '''
    async def find_page(
        self, limit: int = 100, offset: int = 0, **filters: Any
    ) -> Tuple[List[T], int]:
        """SQL-level page read (plan step 8): returns (rows, total_matching).

        `total` counts ALL rows matching the filters, not the page - that is
        what makes a pager honest. Implementations push WHERE/LIMIT/OFFSET into
        SQL; `find_all()[:limit]` loads every row then throws most away, the
        trap the build plan names. Accepted filters are documented on each
        implementation; an UNKNOWN filter is refused, never ignored - silently
        dropping a filter serves an unfiltered page that looks filtered.
        """
        raise NotImplementedError(
            "find_page is part of the step-8 read plane and is not implemented "
            "by this repository yet."
        )
'''

ports = [
    ("class IAccountRepository(ABC, Generic[T]):", "    @abstractmethod\n    async def find_by_login"),
    ("class IOrderRepository(ABC, Generic[T]):", None),
    ("class IDealRepository(ABC, Generic[T]):", None),
    ("class IPositionRepository(ABC, Generic[T]):", None),
    ("class IManagerRepository(ABC, Generic[T]):", None),
    ("class IClientRepository(ABC, Generic[T]):", None),
]

path = os.path.join(WS, "core", "ports", "interfaces.py")
src = open(path, encoding="utf-8", newline="").read()
if "async def find_page" not in src:
    import re
    for cls, _ in ports:
        m = re.search(re.escape(cls) + r"\n", src)
        if not m:
            print("port class not found:", cls); sys.exit(1)
        # find the end of the class docstring (or the class line itself)
        rest = src[m.end():]
        dm = re.match(r'    """[\s\S]*?"""\n', rest)
        insert_at = m.end() + (dm.end() if dm else 0)
        src = src[:insert_at] + PORT_METHOD + src[insert_at:]
# make sure Tuple is imported
src = open(path, encoding="utf-8").read()
import re as _re
_m = _re.search(r"from typing import [^\n]+", src)
if _m and "Tuple" not in _m.group(0):
    src = src.replace(_m.group(0), _m.group(0).rstrip() + "  # noqa", 1) if False else src
    line = _m.group(0)
    fixed = line.replace("from typing import ", "from typing import Tuple, ", 1)
    src = src.replace(line, fixed, 1)
    open(path, "w", encoding="utf-8").write(src)
    print("added Tuple import")

# ------------------------------------------------------- SqlAccountRepository
ACCOUNT_FP = '''    async def find_page(
        self,
        limit: int = 100,
        offset: int = 0,
        group_name: Optional[str] = None,
        account_type: Optional[str] = None,
        enabled: Optional[bool] = None,
        session: Optional[AsyncSession] = None,
    ):
        """Paged account list. Filters: group_name (exact MT5 path),
        account_type (the derived enum value), enabled (the is_enabled MIRROR
        column - correct for legacy rights=0 rows AND for new rows, because
        step 5 made the mask write through to it).

        Ordered by login NUMERICALLY (login is stored as a string; lexicographic
        order would serve 1000, 10000, 100001, 885863 - a UI table that looks
        broken). CAST to BIGINT is legal on PostgreSQL and on SQLite.
        """
        async def _page(sess: AsyncSession):
            stmt = select(AccountModel)
            count_stmt = select(func.count()).select_from(AccountModel)
            if group_name is not None:
                stmt = stmt.where(AccountModel.group_name == group_name)
                count_stmt = count_stmt.where(AccountModel.group_name == group_name)
            if account_type is not None:
                stmt = stmt.where(AccountModel.account_type == account_type)
                count_stmt = count_stmt.where(AccountModel.account_type == account_type)
            if enabled is not None:
                stmt = stmt.where(AccountModel.is_enabled == bool(enabled))
                count_stmt = count_stmt.where(AccountModel.is_enabled == bool(enabled))
            total = (await sess.execute(count_stmt)).scalar() or 0
            stmt = stmt.order_by(cast(AccountModel.login, BigInteger)).limit(limit).offset(offset)
            models = (await sess.execute(stmt)).scalars().all()
            rows = []
            for model in models:
                group = None
                if self.group_repo is not None and model.group_name:
                    group = await self.group_repo.find_by_name(model.group_name)
                rows.append(db_to_account(model, group))
            return rows, int(total)

        if session:
            return await _page(session)
        async with self.session_factory() as sess:
            return await _page(sess)

'''
patch(
    "infrastructure/persistence/repositories/account_repository.py",
    [
        ("from sqlalchemy import select",
         "from sqlalchemy import BigInteger, cast, func, select"),
        ("    async def find_all(self):", ACCOUNT_FP + "    async def find_all(self):"),
    ],
)

# ------------------------------------- SqlManagerRepository + SqlClientRepository
MANAGER_FP = '''    async def find_page(self, limit: int = 100, offset: int = 0, **filters):
        """Paged manager list, ordered by login. No filters yet: the manager
        plane lists staff, it does not search them (MT5's own manager table
        filters client-side). An unknown filter is refused, not ignored."""
        if filters:
            raise ValueError(f"SqlManagerRepository.find_page: unknown filter(s) {sorted(filters)}")
        async def _page(sess: AsyncSession):
            total = (await sess.execute(select(func.count()).select_from(ManagerModel))).scalar() or 0
            stmt = select(ManagerModel).order_by(ManagerModel.login).limit(limit).offset(offset)
            models = (await sess.execute(stmt)).scalars().all()
            return [db_to_manager(m) for m in models], int(total)
        async with self.session_factory() as sess:
            return await _page(sess)

'''
CLIENT_FP = '''    async def find_page(self, limit: int = 100, offset: int = 0, **filters):
        """Paged client list, newest first (created_at desc, id as the stable
        tie-break). An unknown filter is refused, not ignored."""
        if filters:
            raise ValueError(f"SqlClientRepository.find_page: unknown filter(s) {sorted(filters)}")
        async def _page(sess: AsyncSession):
            total = (await sess.execute(select(func.count()).select_from(ClientModel))).scalar() or 0
            stmt = (
                select(ClientModel)
                .order_by(ClientModel.created_at.desc(), ClientModel.id)
                .limit(limit).offset(offset)
            )
            models = (await sess.execute(stmt)).scalars().all()
            return [db_to_client(m) for m in models], int(total)
        async with self.session_factory() as sess:
            return await _page(sess)

'''
patch(
    "infrastructure/persistence/repositories/manager_repository.py",
    [
        ("from sqlalchemy import select", "from sqlalchemy import func, select"),
        ("    async def find_all(self) -> List[ManagerAccount]:",
         MANAGER_FP + "    async def find_all(self) -> List[ManagerAccount]:"),
        ("    async def find_all(self) -> List[Client]:",
         CLIENT_FP + "    async def find_all(self) -> List[Client]:"),
    ],
)

# ------------------------------------------------------------ SqlDealRepository
DEAL_FP = '''    async def find_page(
        self,
        limit: int = 100,
        offset: int = 0,
        account_login: Optional[int] = None,
        symbol: Optional[str] = None,
        entry: Optional[str] = None,
        session: Optional[AsyncSession] = None,
    ):
        """Paged cross-account deal read (ENDPOINTS B2 - the UI's Deals page had
        NO data source on any plane). Filters: account_login, symbol, entry
        (IN/OUT/INOUT/OUT_BY). Newest first: created_at desc, deal_id tie-break.
        """
        async def _page(sess: AsyncSession):
            conds = []
            if account_login is not None:
                conds.append(DealModel.account_login == int(account_login))
            if symbol is not None:
                conds.append(DealModel.symbol == symbol)
            if entry is not None:
                conds.append(DealModel.entry == entry)
            count_stmt = select(func.count()).select_from(DealModel)
            stmt = select(DealModel)
            for c in conds:
                count_stmt = count_stmt.where(c)
                stmt = stmt.where(c)
            total = (await sess.execute(count_stmt)).scalar() or 0
            stmt = stmt.order_by(DealModel.created_at.desc(), DealModel.deal_id).limit(limit).offset(offset)
            models = (await sess.execute(stmt)).scalars().all()
            return [db_to_deal(m) for m in models], int(total)

        if session:
            return await _page(session)
        async with self.session_factory() as sess:
            return await _page(sess)

'''
patch(
    "infrastructure/persistence/repositories/deal_repository.py",
    [
        ("from sqlalchemy import select", "from sqlalchemy import func, select"),
        ("    async def find_by_order_id(self, order_id: str)",
         DEAL_FP + "    async def find_by_order_id(self, order_id: str)"),
    ],
)

# ----------------------------------------------------------- SqlOrderRepository
ORDER_FP = '''    #: MT5 order states split: terminal states belong to HISTORY, the rest are
    #: the active book. Stored values are the enum's .value strings.
    _TERMINAL_STATES = ("CANCELLED", "FILLED", "REJECTED", "EXPIRED")
    _ACTIVE_STATES = ("STARTED", "PLACED", "PARTIALLY_FILLED")

    async def find_page(
        self,
        limit: int = 100,
        offset: int = 0,
        account_login: Optional[int] = None,
        symbol: Optional[str] = None,
        state: Optional[str] = None,
        history: Optional[bool] = None,
        session: Optional[AsyncSession] = None,
    ):
        """Paged cross-account order read (ENDPOINTS B2).

        `history` is a TRI-STATE, because the UI has two pages: None = every
        order, False = the active book (STARTED/PLACED/PARTIALLY_FILLED),
        True = history (CANCELLED/FILLED/REJECTED/EXPIRED). `state` narrows
        further and is refused if it contradicts `history` - serving the
        intersection of "active" and "FILLED" as an empty page that looks like
        a filter result would be the silent-lie pattern again.
        """
        if state is not None and history is not None:
            in_terminal = state in self._TERMINAL_STATES
            if in_terminal != bool(history):
                raise ValueError(
                    f"state={state!r} contradicts history={history!r}: "
                    f"terminal states are {self._TERMINAL_STATES}"
                )
        async def _page(sess: AsyncSession):
            conds = []
            if account_login is not None:
                conds.append(OrderModel.account_login == int(account_login))
            if symbol is not None:
                conds.append(OrderModel.symbol == symbol)
            if state is not None:
                conds.append(OrderModel.state == state)
            elif history is not None:
                states = self._TERMINAL_STATES if history else self._ACTIVE_STATES
                conds.append(OrderModel.state.in_(states))
            count_stmt = select(func.count()).select_from(OrderModel)
            stmt = select(OrderModel)
            for c in conds:
                count_stmt = count_stmt.where(c)
                stmt = stmt.where(c)
            total = (await sess.execute(count_stmt)).scalar() or 0
            stmt = stmt.order_by(OrderModel.time_setup.desc(), OrderModel.ticket_id).limit(limit).offset(offset)
            models = (await sess.execute(stmt)).scalars().all()
            return [db_to_order(m) for m in models], int(total)

        if session:
            return await _page(session)
        async with self.session_factory() as sess:
            return await _page(sess)

'''
patch(
    "infrastructure/persistence/repositories/order_repository.py",
    [
        ("from sqlalchemy import select", "from sqlalchemy import func, select"),
        ("    async def find_by_account(self, account_login: int)",
         ORDER_FP + "    async def find_by_account(self, account_login: int)"),
    ],
)

# ------------------------------------------------------- SqlPositionRepository
POS_FP = '''    async def find_page(
        self,
        limit: int = 100,
        offset: int = 0,
        account_login: Optional[int] = None,
        symbol: Optional[str] = None,
        include_closed: bool = False,
        session: Optional[AsyncSession] = None,
    ):
        """Paged cross-account position read (step 8's admin plane; the manager
        plane's PositionGet keeps its unfiltered contract from F8/F9).

        Open positions by default - `include_closed=True` adds the closed rows
        for a history view. Newest first: time_create desc, position_id
        tie-break.
        """
        async def _page(sess: AsyncSession):
            conds = []
            if not include_closed:
                conds.append(PositionModel.time_done.is_(None))
            if account_login is not None:
                conds.append(PositionModel.account_login == int(account_login))
            if symbol is not None:
                conds.append(PositionModel.symbol == symbol)
            count_stmt = select(func.count()).select_from(PositionModel)
            stmt = select(PositionModel)
            for c in conds:
                count_stmt = count_stmt.where(c)
                stmt = stmt.where(c)
            total = (await sess.execute(count_stmt)).scalar() or 0
            stmt = stmt.order_by(PositionModel.time_create.desc(), PositionModel.position_id).limit(limit).offset(offset)
            models = (await sess.execute(stmt)).scalars().all()
            return [db_to_position(m) for m in models], int(total)

        if session:
            return await _page(session)
        async with self.session_factory() as sess:
            return await _page(sess)

'''
patch(
    "infrastructure/persistence/repositories/position_repository.py",
    [
        ("from sqlalchemy import select", "from sqlalchemy import func, select"),
        ("    async def find_by_account(", POS_FP + "    async def find_by_account("),
    ],
)

print("patched:", APPLIED or "nothing (already applied)")
