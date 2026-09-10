"""
Step M2 part 1 - make the repositories able to do what the seeder and ConfigCache need.

FOUR GAPS, all of which block "configuration can enter the system":

1. `ConfigCache.initialize()` calls `symbol_repo.get_all()` and
   `account_repo.find_all()`. NEITHER EXISTS. The symbol repository's method is
   `get_all_symbols`, and `find_all` was never implemented at all. So the cache - the
   whole hot path, the thing that makes reads MT5-fast - threw AttributeError at
   startup. `IAccountRepository` did not even declare `find_all`, so no implementation
   was ever obliged to provide it.

2. No repository could persist MT5 metadata. `save()` takes a domain object, and a
   domain Group cannot carry the 27 ConfigGroups fields we do not model, nor the wire
   scale, nor the imported baseline. Without a row-level save, importing a real MT5
   server and re-exporting it losslessly is impossible. `save_model()` is added to the
   group, symbol, account and manager repositories.

3. There was no manager or client persistence at all: no `ManagerModel`, no
   `ClientModel`, no repository. Stage 2 (admin/dealer credentials) had an entity and a
   port and nothing else, so no administrator could be created and no account could be
   linked to a person.

4. `SqlGroupRepository` was defined TWICE - once in group_repository.py and once in
   account_repository.py. The M0 CI gate checks for duplicate definitions within a
   file, not across files, so it did not catch this one. The copy in account_repository
   is removed and imported instead.
"""

from __future__ import annotations

import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
REPOS = ROOT / "infrastructure" / "persistence" / "repositories"
if not REPOS.is_dir():
    raise SystemExit(f"not a broker-platform root: {ROOT}")


def load(rel: str) -> str:
    with open(ROOT / rel, encoding="utf-8", newline="") as fh:
        return fh.read()


def save(rel: str, text: str, *, crlf: bool = True) -> None:
    norm = text.replace("\r\n", "\n")
    with open(ROOT / rel, "w", encoding="utf-8", newline="") as fh:
        fh.write(norm.replace("\n", "\r\n") if crlf else norm)


def sub(rel: str, old: str, new: str, why: str, *, required: bool = True) -> None:
    text = load(rel)
    crlf = "\r\n" in text
    work = text.replace("\r\n", "\n")
    if old not in work:
        if required:
            raise SystemExit(f"[FAIL] {rel}: pattern not found ({why}):\n{old[:240]!r}")
        print(f"  skip {rel}: {why}")
        return
    save(rel, work.replace(old, new, 1), crlf=crlf)
    print(f"  ok  {rel}: {why}")


def append(rel: str, block: str, why: str) -> None:
    text = load(rel)
    crlf = "\r\n" in text
    work = text.replace("\r\n", "\n").rstrip("\n") + "\n" + block.strip("\n") + "\n"
    save(rel, work, crlf=crlf)
    print(f"  ok  {rel}: {why}")


# ---------------------------------------------------------------------------
# 1. New models: Manager + Client, and the MT5-aligned Account
# ---------------------------------------------------------------------------

shutil.copyfile(HERE / "m2pkg" / "manager_models.py", ROOT / "infrastructure" / "persistence" / "manager_models.py")
print("  ok  infrastructure/persistence/manager_models.py: ManagerModel + ClientModel")

shutil.copyfile(HERE / "m2pkg" / "account_models.py", ROOT / "infrastructure" / "persistence" / "account_models.py")
print("  ok  infrastructure/persistence/account_models.py: MT5-aligned AccountModel + Account/Client/Manager mappers")

# ---------------------------------------------------------------------------
# 2. db_models must stop defining the stale AccountModel and re-export the new one
# ---------------------------------------------------------------------------

DBM = "infrastructure/persistence/db_models.py"
text = load(DBM)
work = text.replace("\r\n", "\n")
start = work.find("class AccountModel(Base):")
end = work.find("class OrderModel(Base):", start)
if start == -1 or end == -1:
    raise SystemExit("[FAIL] db_models.py: could not bound the stale AccountModel")
removed = work[start:end]
if "__tablename__" not in removed:
    raise SystemExit("[FAIL] db_models.py: the AccountModel region has no __tablename__")
work = work[:start] + work[end:]
save(DBM, work, crlf="\r\n" in text)
print(f"  ok  {DBM}: removed the stale 14-column AccountModel ({len(removed)} chars)")

# Re-export everything the persistence layer owns, below Base, so that importing
# db_models registers every table on the single metadata and existing imports resolve.
text = load(DBM)
work = text.replace("\r\n", "\n")
REEXPORT = '''

# ---------------------------------------------------------------------------
# Re-exports
# ---------------------------------------------------------------------------
# Importing this module must register EVERY table on Base.metadata, or Alembic's
# autogenerate and DatabaseManager.create_tables() both miss tables. GroupModel and
# SymbolModel live in config_models.py, AccountModel/ManagerModel/ClientModel in
# account_models.py and manager_models.py; all are re-exported here because that is
# where the rest of the codebase has always imported them from.
from .config_models import GroupModel, SymbolModel  # noqa: E402,F401
from .account_models import AccountModel  # noqa: E402,F401
from .manager_models import ClientModel, ManagerModel  # noqa: E402,F401
'''
# Replace the existing config_models re-export with the fuller one.
OLD_REEXPORT = '''# GroupModel and SymbolModel live in config_models.py, aligned field-for-field
# with MT5 ConfigGroups / ConfigSymbols. Re-exported here so that
# Base.metadata sees every table and existing imports keep resolving.
from .config_models import GroupModel, SymbolModel  # noqa: E402,F401
'''
if OLD_REEXPORT in work:
    work = work.replace(OLD_REEXPORT, REEXPORT.strip("\n") + "\n")
else:
    work = work.rstrip("\n") + "\n" + REEXPORT
save(DBM, work, crlf="\r\n" in text)
print(f"  ok  {DBM}: re-exports every model so Base.metadata is complete")

# ---------------------------------------------------------------------------
# 3. mappers.py must delegate Account too
# ---------------------------------------------------------------------------

MAP = "infrastructure/persistence/mappers.py"
text = load(MAP)
work = text.replace("\r\n", "\n")


def cut_function(source: str, name: str) -> str:
    start = source.find(f"def {name}(")
    if start == -1:
        return source
    line_start = source.rfind("\n\n", 0, start)
    if line_start != -1 and "#" in source[line_start:start]:
        start = line_start + 2
    end = source.find("\ndef ", start + 1)
    if end == -1:
        end = source.find("\n# ====", start + 1)
    if end == -1:
        end = len(source)
    return source[:start] + source[end:]


before = len(work)
for fn in ("account_to_db", "db_to_account"):
    work = cut_function(work, fn)
if len(work) == before:
    raise SystemExit("[FAIL] mappers.py: the account mappers were not found")

DELEGATE = '''

# ============================================================================
# ACCOUNT / CLIENT / MANAGER MAPPERS
# ============================================================================
# Implemented in account_models.py, alongside the MT5-aligned AccountModel they map
# onto. The versions that used to live here read `account.login_id` and
# `account.kyc_verified`, neither of which exists on the domain Account, so saving any
# account raised AttributeError. Re-exported because repositories import them from here.
# ============================================================================

from .account_models import (  # noqa: E402,F401
    account_to_db,
    client_to_db,
    db_to_account,
    db_to_client,
    db_to_manager,
    manager_mt5_record,
    manager_to_db,
    mask_to_rights,
    masks_to_rights,
    rights_to_mask,
    rights_to_masks,
)
'''
work = work.rstrip("\n") + "\n" + DELEGATE
save(MAP, work, crlf="\r\n" in text)
print(f"  ok  {MAP}: account mappers replaced ({before - len(work)} chars) and delegated")

# ---------------------------------------------------------------------------
# 4. IAccountRepository gains find_all; ISymbolRepository gains get_all
# ---------------------------------------------------------------------------

IFACE = "core/ports/interfaces.py"
sub(
    IFACE,
    '''    @abstractmethod
    async def save(self, account: T, session: Optional[Any] = None) -> T:
        """Persists an account aggregate."""
        pass''',
    '''    @abstractmethod
    async def save(self, account: T, session: Optional[Any] = None) -> T:
        """Persists an account aggregate."""
        pass

    @abstractmethod
    async def find_all(self) -> List[T]:
        """Every account. ConfigCache loads this once at startup to warm the hot path."""
        pass''',
    "IAccountRepository declares find_all, which ConfigCache.initialize() already calls",
    required=False,
)

sub(
    IFACE,
    '''    @abstractmethod
    async def get_all_symbols(self) -> List[T]:
        """Returns all available symbols."""
        pass''',
    '''    @abstractmethod
    async def get_all_symbols(self) -> List[T]:
        """Returns all available symbols."""
        pass

    async def get_all(self) -> List[T]:
        """Alias of get_all_symbols.

        ConfigCache.initialize() calls get_all(); every other repository in this
        codebase uses that name. Provided concretely rather than abstractly so existing
        implementations do not have to change.
        """
        return await self.get_all_symbols()''',
    "ISymbolRepository.get_all resolves to get_all_symbols",
)

# ---------------------------------------------------------------------------
# 5. Concrete repositories: find_all, get_all, save_model
# ---------------------------------------------------------------------------

GROUP_REPO = "infrastructure/persistence/repositories/group_repository.py"
append(
    GROUP_REPO,
    '''
    async def save_model(self, model) -> None:
        """Persist a GroupModel row directly.

        Needed for MT5 import: the row carries mt5_extra, mt5_scale and mt5_source,
        which a domain Group cannot express. Going through save(group) would drop the
        27 ConfigGroups fields we do not model and make the group un-exportable.
        """
        async with self.session_factory() as session:
            await session.merge(model)
            await session.commit()
''',
    "SqlGroupRepository.save_model for MT5-metadata-bearing rows",
)

SYM_REPO = "infrastructure/persistence/repositories/symbol_repository.py"
append(
    SYM_REPO,
    '''
    async def get_all(self):
        """Alias used by ConfigCache.initialize()."""
        return await self.get_all_symbols()

    async def save_model(self, model) -> None:
        """Persist a SymbolModel row directly, preserving MT5 metadata.

        Our Symbol models 52 of MT5's 121 fields. The other 69 - CurrencyProfit,
        CurrencyMargin, the Filter* tick filtration, the IE*/RE* execution controls, the
        per-day SwapRate curve - live in mt5_extra and mt5_source, and only a row-level
        save can carry them.
        """
        async with self.session_factory() as session:
            await session.merge(model)
            await session.commit()
''',
    "SqlSymbolRepository.get_all + save_model",
)

ACC_REPO = "infrastructure/persistence/repositories/account_repository.py"
append(
    ACC_REPO,
    '''
    async def find_all(self):
        """Every account. ConfigCache loads this once at startup."""
        async with self.session_factory() as session:
            result = await session.execute(select(AccountModel))
            models = result.scalars().all()
            out = []
            for model in models:
                group = None
                if self.group_repo is not None and model.group_name:
                    group = await self.group_repo.find_by_name(model.group_name)
                out.append(db_to_account(model, group))
            return out

    async def save_model(self, model) -> None:
        """Persist an AccountModel row directly."""
        async with self.session_factory() as session:
            await session.merge(model)
            await session.commit()
''',
    "SqlAccountRepository.find_all + save_model (find_all is what ConfigCache calls)",
)

# account_repository must import the corrected mapper and select/AccountModel.
text = load(ACC_REPO)
work = text.replace("\r\n", "\n")
if "db_to_account" not in work.split("class ")[0]:
    work = work.replace(
        "from ..mappers import account_to_db, db_to_account",
        "from ..mappers import account_to_db, db_to_account",
    )
    if "from ..mappers import" not in work:
        work = (
            "from sqlalchemy import select\n"
            "from ..mappers import account_to_db, db_to_account\n"
            "from ..account_models import AccountModel\n"
            + work
        )
    save(ACC_REPO, work, crlf="\r\n" in text)
    print(f"  ok  {ACC_REPO}: ensured select / AccountModel / db_to_account are imported")

# ---------------------------------------------------------------------------
# 6. Remove the duplicate SqlGroupRepository from account_repository.py
# ---------------------------------------------------------------------------

text = load(ACC_REPO)
work = text.replace("\r\n", "\n")
start = work.find("class SqlGroupRepository(IGroupRepository):")
if start != -1:
    end = work.find("class SqlAccountRepository(", start)
    if end == -1:
        raise SystemExit("[FAIL] account_repository.py: could not bound the duplicate SqlGroupRepository")
    removed = work[start:end]
    work = work[:start] + work[end:]
    if "from .group_repository import SqlGroupRepository" not in work:
        work = work.replace(
            "from core.ports.interfaces import IAccountRepository, IGroupRepository",
            "from core.ports.interfaces import IAccountRepository, IGroupRepository\n"
            "# SqlGroupRepository lives in group_repository.py. It used to be defined\n"
            "# here as well, and the two copies drifted.\n"
            "from .group_repository import SqlGroupRepository  # noqa: F401",
            1,
        )
    save(ACC_REPO, work, crlf="\r\n" in text)
    print(f"  ok  {ACC_REPO}: removed the duplicate SqlGroupRepository ({len(removed)} chars)")

# ---------------------------------------------------------------------------
# 7. Manager + Client repositories
# ---------------------------------------------------------------------------

MANAGER_REPO = '''"""
Repositories for the Manager (administrator/dealer) and Client planes.

MT5's model, which these follow: a Manager has a login, a positional 128-element rights
array, and a Groups scope limiting which client groups it may administer. A Client is
the person or company (MT5 IMTUser) and owns one or more trading Accounts (IMTAccount).
Keeping those two apart is what lets one person hold a demo, a real and a contest
account without duplicating their KYC data.
"""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.domains.accounts.client import Client
from core.domains.identity.models import ManagerAccount
from core.ports.interfaces import IManagerRepository

from ..account_models import (
    client_to_db,
    db_to_client,
    db_to_manager,
    manager_to_db,
)
from ..manager_models import ClientModel, ManagerModel


class SqlManagerRepository(IManagerRepository):
    """PostgreSQL implementation of IManagerRepository."""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def find_by_login(self, login: str) -> Optional[ManagerAccount]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(ManagerModel).where(ManagerModel.login == int(login))
            )
            model = result.scalar_one_or_none()
            return db_to_manager(model) if model else None

    async def save(self, manager: ManagerAccount) -> ManagerAccount:
        async with self.session_factory() as session:
            model = manager_to_db(manager)
            await session.merge(model)
            await session.commit()
            return manager

    async def save_model(self, model: ManagerModel) -> None:
        """Persist a ManagerModel row directly, preserving imported MT5 metadata."""
        async with self.session_factory() as session:
            await session.merge(model)
            await session.commit()

    async def find_all(self) -> List[ManagerAccount]:
        async with self.session_factory() as session:
            result = await session.execute(select(ManagerModel))
            return [db_to_manager(m) for m in result.scalars().all()]

    async def count(self) -> int:
        """How many managers exist. `seed` uses this to decide on first-admin bootstrap."""
        async with self.session_factory() as session:
            result = await session.execute(select(ManagerModel))
            return len(result.scalars().all())


class SqlClientRepository:
    """PostgreSQL persistence for Client (MT5 IMTUser).

    There is no IClientRepository port yet; adding one is part of wiring
    CreateClientHandler, which needs the port to be injectable.
    """

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def find_by_id(self, client_id: str) -> Optional[Client]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(ClientModel).where(ClientModel.id == client_id)
            )
            model = result.scalar_one_or_none()
            return db_to_client(model) if model else None

    async def save(self, client: Client) -> Client:
        async with self.session_factory() as session:
            model = client_to_db(client)
            await session.merge(model)
            await session.commit()
            return client

    async def find_all(self) -> List[Client]:
        async with self.session_factory() as session:
            result = await session.execute(select(ClientModel))
            return [db_to_client(m) for m in result.scalars().all()]
'''
save("infrastructure/persistence/repositories/manager_repository.py", MANAGER_REPO, crlf=True)
print("  ok  repositories/manager_repository.py: SqlManagerRepository + SqlClientRepository")

# ---------------------------------------------------------------------------
# 8. DI setup must provide the manager repository, or nothing can resolve it
# ---------------------------------------------------------------------------

DI = "infrastructure/persistence/di_setup.py"
sub(
    DI,
    "from .repositories.group_repository import SqlGroupRepository",
    "from .repositories.group_repository import SqlGroupRepository\n"
    "from .repositories.manager_repository import SqlClientRepository, SqlManagerRepository",
    "di_setup imports the manager and client repositories",
)
sub(
    DI,
    "    coverage_repo = SqlCoverageAccountRepository(session_factory)",
    "    coverage_repo = SqlCoverageAccountRepository(session_factory)\n"
    "    manager_repo = SqlManagerRepository(session_factory)\n"
    "    client_repo = SqlClientRepository(session_factory)",
    "di_setup constructs the manager and client repositories",
)
sub(
    DI,
    "        'coverage_repo': coverage_repo,",
    "        'coverage_repo': coverage_repo,\n"
    "        'manager_repo': manager_repo,\n"
    "        'client_repo': client_repo,",
    "di_setup returns manager_repo and client_repo in the container payload",
)

# ---------------------------------------------------------------------------
# 8a. SqlRoutingRuleRepository is missing delete(), which its port requires
# ---------------------------------------------------------------------------
# IRoutingRuleRepository declares get_active_rules / save / delete. The implementation
# had the first two, so instantiating it raised
# "Can't instantiate abstract class SqlRoutingRuleRepository with abstract method
# delete" - and setup_persistence_di() constructs it, which is what the CLI's
# _bootstrap() and the API's DI wiring both call. Nothing could start.

append(
    "infrastructure/persistence/repositories/routing_rule_repository.py",
    '''
    async def delete(self, rule_id: str) -> bool:
        """Delete a routing rule. Required by IRoutingRuleRepository."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(RoutingRuleModel).where(RoutingRuleModel.rule_id == rule_id)
            )
            model = result.scalar_one_or_none()
            if model is None:
                return False
            await session.delete(model)
            await session.commit()
            return True
''',
    "SqlRoutingRuleRepository.delete implemented (its port has always required it)",
)

# ---------------------------------------------------------------------------
# 8b. api/di_providers must expose get_group_repo for the admin router
# ---------------------------------------------------------------------------

DI2 = "api/di_providers.py"
text = load(DI2)
work = text.replace("\r\n", "\n")
if "def get_group_repo(" not in work:
    block = (
        'def get_group_repo() -> Any:\n'
        '    """Provider for IGroupRepository."""\n'
        '    return _container.get("group_repo")\n'
        '\n'
        '\n'
    )
    anchor = "def get_account_repo() -> Any:"
    if anchor not in work:
        raise SystemExit("[FAIL] di_providers.py: get_account_repo anchor not found")
    work = work.replace(anchor, block + anchor, 1)
    save(DI2, work, crlf="\r\n" in text)
    print("  ok  api/di_providers.py: added get_group_repo")

# ---------------------------------------------------------------------------
# 8c. Repositories need a row-level lookup, or an MT5 import cannot be re-exported
# ---------------------------------------------------------------------------
# group_mt5_record / symbol_mt5_record take the ROW, because only the row carries
# mt5_source and mt5_extra. The repositories only exposed domain-level finders, so
# there was no supported way to get the row back for an export.

append(
    "infrastructure/persistence/repositories/group_repository.py",
    '''
    async def find_row_by_name(self, name: str):
        """Return the raw GroupModel row, for MT5 export.

        The row carries mt5_source, mt5_extra and mt5_scale, which a domain Group
        cannot express. Exporting needs them, so this returns the row rather than the
        mapped object.
        """
        async with self.session_factory() as session:
            result = await session.execute(
                select(GroupModel).where(GroupModel.name == name)
            )
            return result.scalar_one_or_none()
''',
    "SqlGroupRepository.find_row_by_name for MT5 export",
)

append(
    "infrastructure/persistence/repositories/symbol_repository.py",
    '''
    async def find_row_by_name(self, name: str):
        """Return the raw SymbolModel row, for MT5 export. See the group equivalent."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(SymbolModel).where(SymbolModel.name == name)
            )
            return result.scalar_one_or_none()
''',
    "SqlSymbolRepository.find_row_by_name for MT5 export",
)

# ---------------------------------------------------------------------------
# 9. Config loader package
# ---------------------------------------------------------------------------

(ROOT / "infrastructure" / "config").mkdir(parents=True, exist_ok=True)
shutil.copyfile(HERE / "m2pkg" / "config_loader.py", ROOT / "infrastructure" / "config" / "loader.py")
(ROOT / "infrastructure" / "config" / "__init__.py").write_text(
    '"""Configuration loading for the configuration plane.\n\n'
    '`loader` parses typed YAML and real MT5 Administrator exports into domain\n'
    'objects, and rejects anything it does not recognise rather than falling back\n'
    'to a default nobody chose.\n"""\n',
    encoding="utf-8",
)
print("  ok  infrastructure/config/loader.py: strict YAML + MT5 JSON loader")

# ---------------------------------------------------------------------------
# 10. Seeder
# ---------------------------------------------------------------------------

shutil.copyfile(HERE / "m2pkg" / "seeder.py", ROOT / "infrastructure" / "config" / "seeder.py")
print("  ok  infrastructure/config/seeder.py: idempotent seeder + first-admin bootstrap")

# ---------------------------------------------------------------------------
# 11. The rewritten YAML config, with real MT5 values
# ---------------------------------------------------------------------------

shutil.copyfile(HERE / "m2pkg" / "default_groups.yaml", ROOT / "config" / "groups" / "default_groups.yaml")
shutil.copyfile(HERE / "m2pkg" / "instruments.yaml", ROOT / "config" / "symbols" / "instruments.yaml")
print("  ok  config/groups/default_groups.yaml: nested shape, percent thresholds, MT5 group paths")
print("  ok  config/symbols/instruments.yaml: values taken from the real server export")
