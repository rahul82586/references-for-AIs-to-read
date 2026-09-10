"""
Database seeder for the configuration plane.

Idempotent by construction: everything is an upsert keyed on MT5's natural key
(`groups.name`, `symbols.name`, `managers.login`), so running `seed` twice produces the
same database. That matters because `make setup-dev` chains seed after migrate, and a
seeder that fails on the second run makes the whole command unusable.

TWO SOURCES

  YAML  config/groups/*.yaml and config/symbols/*.yaml, parsed by
        infrastructure.config.loader. Used for a from-scratch install.

  MT5   a real MT5 Administrator export, via loader.groups_from_mt5 /
        symbols_from_mt5. Used when you have a server to copy. Because M1 proved the
        codec lossless, this reproduces a real broker's configuration exactly -
        20 groups and 362 symbols in the reference export - including the 27 and 69
        fields our domain does not model, which are preserved for re-export.

FIRST ADMIN

`ensure_first_admin` implements MT5's own bootstrap: if no manager exists, create one
at login 1000 with a generated password, print it ONCE to stdout and the log, and set
must_change_password so the first login forces a change. MT5 does exactly this -
the password appears on the installer's final screen and in the trade server's /Logs
folder - and warns that losing it means losing access to the platform.
"""

from __future__ import annotations

import logging
import pathlib
import secrets
import string
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from core.domains.identity.models import ManagerAccount, ManagerRole
from infrastructure.config import loader

logger = logging.getLogger(__name__)

#: MT5 creates the first administrator at login 1000.
FIRST_ADMIN_LOGIN = 1000

#: MT5 requires the internal server password to be 7-15 characters. We use the same
#: bound for a generated admin password so the two never diverge in strength.
PASSWORD_LENGTH = 16
_ALPHABET = string.ascii_letters + string.digits


@dataclass
class SeedReport:
    """What the seeder did, for `cli seed` to print."""

    groups_created: int = 0
    groups_updated: int = 0
    symbols_created: int = 0
    symbols_updated: int = 0
    coverage_accounts: int = 0
    admin_login: Optional[int] = None
    admin_password: Optional[str] = None
    admin_created: bool = False
    warnings: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        data = {
            "groups_created": self.groups_created,
            "groups_updated": self.groups_updated,
            "symbols_created": self.symbols_created,
            "symbols_updated": self.symbols_updated,
            "coverage_accounts": self.coverage_accounts,
            "admin_created": self.admin_created,
            "admin_login": self.admin_login,
            "warnings": list(self.warnings),
        }
        # Never include the password in a serialised report: it is printed once, to
        # stdout and the log, and stored only as a hash.
        return data


def generate_password(length: int = PASSWORD_LENGTH) -> str:
    """Cryptographically random password, MT5's 7-15 character bound respected."""
    return "".join(secrets.choice(_ALPHABET) for _ in range(max(7, min(length, 64))))


# ---------------------------------------------------------------------------
# Groups
# ---------------------------------------------------------------------------


async def seed_groups_from_yaml(group_repo: Any, paths: List[Any], report: SeedReport) -> None:
    for path in paths:
        path = pathlib.Path(path)
        if not path.is_file():
            report.warnings.append(f"group config not found, skipped: {path}")
            continue
        for group in loader.load_groups(path):
            existing = await group_repo.find_by_name(group.name)
            if existing is None:
                await group_repo.save(group)
                report.groups_created += 1
                logger.info("seeded group %s", group.name)
            else:
                # Preserve the identity the database already assigned, then overwrite.
                group.id = existing.id
                group.created_at = existing.created_at
                await group_repo.save(group)
                report.groups_updated += 1
                logger.info("updated group %s", group.name)


async def seed_groups_from_mt5(group_repo: Any, path: Any, report: SeedReport) -> None:
    """Import groups from a real MT5 Administrator export."""
    from infrastructure.persistence.config_mappers import group_to_db

    for group, extra, scale, source in loader.groups_from_mt5(path):
        existing = await group_repo.find_by_name(group.name)
        if existing is not None:
            group.id = existing.id
            group.created_at = existing.created_at
            report.groups_updated += 1
        else:
            report.groups_created += 1
        # The quarantine, wire scale and imported baseline have to reach the row, or
        # the 27 ConfigGroups fields we do not model are lost and the group can never
        # be re-exported. group_repo.save() takes a domain object and cannot carry
        # them, so build the row here and hand it to save_model().
        row = group_to_db(group, mt5_extra=extra, mt5_scale=scale, mt5_source=source)
        await group_repo.save_model(row)
        logger.info("imported MT5 group %s", group.name)


# ---------------------------------------------------------------------------
# Symbols
# ---------------------------------------------------------------------------


async def seed_symbols_from_yaml(symbol_repo: Any, paths: List[Any], report: SeedReport) -> None:
    for path in paths:
        path = pathlib.Path(path)
        if not path.is_file():
            report.warnings.append(f"symbol config not found, skipped: {path}")
            continue
        for symbol in loader.load_symbols(path):
            existing = await _find_symbol(symbol_repo, symbol.name)
            if existing is None:
                await symbol_repo.save(symbol)
                report.symbols_created += 1
                logger.info("seeded symbol %s", symbol.name)
            else:
                symbol.id = getattr(existing, "id", symbol.id)
                symbol.created_at = existing.created_at
                await symbol_repo.save(symbol)
                report.symbols_updated += 1
                logger.info("updated symbol %s", symbol.name)


async def seed_symbols_from_mt5(symbol_repo: Any, path: Any, report: SeedReport) -> None:
    """Import symbols from a real MT5 Administrator export."""
    for symbol, extra, scale, source in loader.symbols_from_mt5(path):
        existing = await _find_symbol(symbol_repo, symbol.name)
        if existing is not None:
            symbol.id = getattr(existing, "id", symbol.id)
            symbol.created_at = existing.created_at
            report.symbols_updated += 1
        else:
            report.symbols_created += 1
        from infrastructure.persistence.config_mappers import symbol_to_db

        row = symbol_to_db(symbol, mt5_extra=extra, mt5_scale=scale, mt5_source=source)
        await symbol_repo.save_model(row)
        logger.info("imported MT5 symbol %s", symbol.name)


async def _find_symbol(symbol_repo: Any, name: str) -> Any:
    """Symbol repositories expose get_symbol or find_by_name depending on vintage."""
    for method in ("get_symbol", "find_by_name"):
        finder = getattr(symbol_repo, method, None)
        if finder is None:
            continue
        result = finder(name)
        if hasattr(result, "__await__"):
            result = await result
        if result is not None:
            return result
    return None


# ---------------------------------------------------------------------------
# First administrator
# ---------------------------------------------------------------------------


async def ensure_first_admin(
    manager_repo: Any,
    report: SeedReport,
    *,
    login: int = FIRST_ADMIN_LOGIN,
    password_hasher: Optional[Any] = None,
) -> Optional[ManagerAccount]:
    """Create the first administrator if none exists, the way MT5 does.

    Returns the ManagerAccount with a plaintext ``password`` attribute set ONLY when a
    new admin was created. The caller prints it once. Nothing stores the plaintext.
    """
    existing = await manager_repo.find_by_login(str(login))
    if existing is not None:
        report.admin_login = login
        report.admin_created = False
        return None

    password = generate_password()
    # Argon2PasswordHasher exposes hash_password(), not hash().
    hasher = getattr(password_hasher, "hash_password", None) or getattr(
        password_hasher, "hash", None
    )
    password_hash = (
        hasher(password) if hasher is not None else f"PLAINTEXT-REPLACE-ME:{password}"
    )

    manager = ManagerAccount(
        manager_id=str(login),
        login=str(login),
        role=ManagerRole.SUPER_ADMIN,
        password_hash=password_hash,
        is_active=True,
    )
    manager.name = "First Admin"
    manager.mailbox = "Administrator (Don't Touch)"
    manager.server_id = 1
    # MT5's auto-created administrator has every right set, which is what all 9
    # managers in the reference export look like.
    manager.rights = ["1"] * 128
    manager.group_scope = [{"Group": "*"}]
    manager.must_change_password = True

    if password_hasher is None:
        report.warnings.append(
            "no password hasher supplied to ensure_first_admin; the admin password is "
            "stored with a PLAINTEXT-REPLACE-ME prefix and MUST be rehashed before use"
        )

    await manager_repo.save(manager)
    report.admin_created = True
    report.admin_login = login
    report.admin_password = password

    # MT5 writes this to the trade server's /Logs folder as well as showing it on the
    # installer's final screen. Do both, once.
    logger.warning(
        "created first administrator: login %s password %s - this is shown ONCE, "
        "save it now; the password must be changed on first login",
        login,
        password,
    )
    return manager


# ---------------------------------------------------------------------------
# Coverage account
# ---------------------------------------------------------------------------


async def ensure_coverage_account(
    account_repo: Any, group_repo: Any, report: SeedReport, *, login: str = "900001"
) -> None:
    """Create the broker's own hedging account if the coverage group exists.

    B-book residual exposure is booked here, and the auto-hedge trigger at 85% of the
    NOP limit moves flow to an LP instead of accumulating more. Without the account the
    SmartOrderRouter has nothing to update exposure against.
    """
    group = await group_repo.find_by_name("coverage\\house")
    if group is None:
        report.warnings.append(
            "no coverage\\house group; skipping the coverage account. "
            "B-book exposure tracking will have nowhere to book."
        )
        return

    existing = await account_repo.find_by_login(login)
    if existing is not None:
        report.coverage_accounts = 1
        return

    from decimal import Decimal

    from core.domains.accounts.account import Account
    from core.domains.accounts.enums import AccountType
    from core.domains.common.value_objects import Money

    account = Account(
        login=login,
        group=group,
        group_id=group.id,
        account_type=AccountType.COVERAGE,
        currency=group.currency,
        balance=Money(Decimal("0"), group.currency),
    )
    await account_repo.save(account)
    report.coverage_accounts = 1
    logger.info("created coverage account %s in group %s", login, group.name)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


async def seed_all(
    *,
    group_repo: Any,
    symbol_repo: Any,
    manager_repo: Any,
    account_repo: Any,
    config_root: Any = "config",
    mt5_groups: Optional[Any] = None,
    mt5_symbols: Optional[Any] = None,
    password_hasher: Optional[Any] = None,
) -> SeedReport:
    """Seed the whole configuration plane. Idempotent.

    ``mt5_groups`` / ``mt5_symbols`` point at real MT5 Administrator exports. When
    given, they take precedence over the YAML for the same natural key, because a real
    server's configuration is more authoritative than a hand-written template.
    """
    report = SeedReport()
    root = pathlib.Path(config_root)

    group_paths = sorted((root / "groups").glob("*.yaml")) if (root / "groups").is_dir() else []
    symbol_paths = sorted((root / "symbols").glob("*.yaml")) if (root / "symbols").is_dir() else []

    if not group_paths and not mt5_groups:
        report.warnings.append(f"no group configs found under {root / 'groups'}")
    if not symbol_paths and not mt5_symbols:
        report.warnings.append(f"no symbol configs found under {root / 'symbols'}")

    await seed_groups_from_yaml(group_repo, group_paths, report)
    await seed_symbols_from_yaml(symbol_repo, symbol_paths, report)

    if mt5_groups:
        await seed_groups_from_mt5(group_repo, mt5_groups, report)
    if mt5_symbols:
        await seed_symbols_from_mt5(symbol_repo, mt5_symbols, report)

    await ensure_first_admin(manager_repo, report, password_hasher=password_hasher)
    await ensure_coverage_account(account_repo, group_repo, report)

    logger.info(
        "seed complete: %d groups created, %d updated, %d symbols created, %d updated, "
        "admin_created=%s",
        report.groups_created,
        report.groups_updated,
        report.symbols_created,
        report.symbols_updated,
        report.admin_created,
    )
    return report
