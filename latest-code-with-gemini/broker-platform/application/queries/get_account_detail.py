"""Get Account Detail query (plan step 8) - the whole 6-tab payload in one read.

MT5's Edit Account dialog is six tabs (Overview, Personal, Account, Limits,
Subscriptions, Security - ACCOUNT-GROUP-CREATION-SPEC §2b), each gated by its
own rights bit. The read model serves all of it in ONE response and lets the
UI render what the caller's rights allow; credential material is never part
of it (the router's serializer pins that).
"""
from dataclasses import dataclass
from typing import Any, Optional


class AccountNotFoundError(ValueError):
    """No account with that login. 404 at the route - never a fabricated row."""


@dataclass(frozen=True)
class GetAccountDetailQuery:
    login: int


class GetAccountDetailQueryHandler:
    def __init__(self, account_repo: Any, group_repo: Any = None):
        self.account_repo = account_repo
        self.group_repo = group_repo

    async def handle(self, query: GetAccountDetailQuery) -> Any:
        if self.account_repo is None:
            raise RuntimeError("GetAccountDetailQueryHandler has no account repository")
        account = await self.account_repo.find_by_login(query.login)
        if account is None:
            # logins are stored as strings; retry the string form before giving up
            account = await self.account_repo.find_by_login(str(query.login))
        if account is None:
            raise AccountNotFoundError(f"no account with login {query.login}")
        # find_by_login already attaches the group when the repo has a
        # group_repo; this covers a detail read against a repo wired without
        # one. group_id is the group's ID (not its name) - find_by_id, never
        # find_by_name with the wrong key.
        if account.group is None and self.group_repo is not None and account.group_id:
            account.group = await self.group_repo.find_by_id(account.group_id)
        return account
