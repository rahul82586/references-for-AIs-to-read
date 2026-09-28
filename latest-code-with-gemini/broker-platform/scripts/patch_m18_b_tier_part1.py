#!/usr/bin/env python3
"""M18 B-tier patch: the 17 wired endpoints.

Adds to api/routers/admin/reads.py: the /online + client-accounts routes and
six new routers (routing, quotes/ticks, risk, trade calculators, funds,
holidays, symbol sessions); to accounts.py the check-password route; to
di_providers the risk-engine/break-repo getters; to main.py the mounts.

Idempotent; run from the bp root.
"""
import os
import sys


def load(p):
    raw = open(p, encoding="utf-8", newline="").read()
    return raw, ("\r\n" in raw), raw.replace("\r\n", "\n")


def save(p, s, crlf):
    open(p, "w", encoding="utf-8", newline="").write(s.replace("\n", "\r\n") if crlf else s)


def apply(p, pairs):
    raw, crlf, s = load(p)
    changed = False
    for old, new in pairs:
        if new.strip() and new.strip().splitlines()[0].strip() in s and old not in s:
            continue
        if old not in s:
            print(f"ANCHOR MISSING in {p}: {old[:60]!r}")
            sys.exit(1)
        s = s.replace(old, new, 1)
        changed = True
    if changed:
        save(p, s, crlf)
        print("patched", p)


# ------------------------------------------------------- di_providers: 2 getters
apply("api/di_providers.py", [(
    'def get_holiday_repo() -> Any:',
    '''def get_risk_engine() -> Any:
    """Provider for the RiskEngine (M18: the trade calculators)."""
    return _container.get("risk_engine")


def get_break_repo() -> Any:
    """Provider for the reconciliation-break repository (M18: risk summary)."""
    return _container.get("reconciliation_break_repo")


def get_holiday_repo() -> Any:''')])

# ------------------------------------------------------- holiday repo: get_all
apply("infrastructure/persistence/repositories/holiday_repository.py", [(
    "    async def get_active_holidays(self, check_date: datetime)",
    '''    async def get_all(self) -> List[Holiday]:
        """The whole holiday calendar (M18: GET /admin/holidays with no
        filters). Ordered by year/month/day so the UI table reads like the
        MT5 Holidays tab."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(HolidayModel).order_by(
                    HolidayModel.year, HolidayModel.month, HolidayModel.day)
            )
            return [db_to_holiday(m) for m in result.scalars().all()]

    async def get_active_holidays(self, check_date: datetime)''')])

# ------------------------------------------------------- reads.py: /online route
apply("api/routers/admin/reads.py", [(
    '''@account_reads_router.get("/{login}")
async def get_account_detail(''',
    '''@account_reads_router.get(
    "/online",
    dependencies=[Depends(require_right("RIGHT_ACC_ONLINE"))],
)
async def list_accounts_online(
    response: Response,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    repo: Any = Depends(get_account_repo),
) -> List[Dict[str, Any]]:
    """MT5's AccountsOnline (mtapi) - who is connected right now. Gated by
    RIGHT_ACC_ONLINE (28, "Getting the current client connections") ON TOP of
    the router's RIGHT_ACC_READ, exactly as MT5 keeps the two bits apart.
    Declared BEFORE /{login} or "online" would resolve as a login and 422."""
    from application.queries.list_accounts import ListAccountsQuery, ListAccountsQueryHandler

    if repo is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Account repository is not wired")
    rows, total = await ListAccountsQueryHandler(repo).handle(
        ListAccountsQuery(limit=limit, offset=offset, online=True))
    return _paged(response, [account_summary(a) for a in rows], total)


@account_reads_router.get("/{login}")
async def get_account_detail(''')])

# ------------------------------------------- reads.py: client -> accounts backlink
apply("api/routers/admin/reads.py", [(
    '''@client_reads_router.get("/{client_id}")
async def get_client_detail(''',
    '''@client_reads_router.get("/{client_id}/accounts")
async def list_client_accounts(
    client_id: str,
    response: Response,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    repo: Any = Depends(get_account_repo),
) -> List[Dict[str, Any]]:
    """One person's trading accounts (MT5's client/user link). Live Neon holds
    0 clients and 45 orphaned client_ids - this read answers honestly for
    whichever side of the backfill decision lands."""
    from application.queries.list_accounts import ListAccountsQuery, ListAccountsQueryHandler

    if repo is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Account repository is not wired")
    rows, total = await ListAccountsQueryHandler(repo).handle(
        ListAccountsQuery(limit=limit, offset=offset, client_id=client_id))
    return _paged(response, [account_summary(a) for a in rows], total)


@client_reads_router.get("/{client_id}")
async def get_client_detail(''')])

# ------------------------------------------------------- accounts.py: check-password
apply("api/routers/admin/accounts.py", [(
    '''@clients_router.post("", status_code=status.HTTP_201_CREATED)''',
    '''class PasswordCheckRequest(BaseModel):
    """MT5's UserPasswordCheck equivalent. The hash itself never leaves the
    server; an unprovisioned or corrupt hash is reported as invalid with a
    reason, never as a 500 and never as a silent false."""

    password: str


@accounts_router.post("/{login}/check-password")
async def check_account_password(
    login: int,
    body: PasswordCheckRequest,
    repo: Any = Depends(get_account_repo),
) -> Dict[str, Any]:
    """Verify a master password against the stored Argon2 hash (M18 B13)."""
    from core.domains.identity.password_policy import verify_password

    if repo is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Account repository is not wired")
    account = await repo.find_by_login(login)
    if account is None:
        account = await repo.find_by_login(str(login))
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"no account with login {login}")
    if not account.password_hash:
        return {"login": int(account.login), "valid": False,
                "reason": "no master password is provisioned on this account"}
    try:
        valid = verify_password(body.password, account.password_hash)
    except Exception:
        # a corrupt stored hash is a refusal, not a crash (password_policy's rule)
        return {"login": int(account.login), "valid": False,
                "reason": "the stored hash is unusable; rotate the password"}
    return {"login": int(account.login), "valid": bool(valid)}


@clients_router.post("", status_code=status.HTTP_201_CREATED)''')])

# accounts.py needs the get_account_repo import
apply("api/routers/admin/accounts.py", [(
    "from api.di_providers import get_create_account_handler, get_create_client_handler",
    "from api.di_providers import get_account_repo, get_create_account_handler, get_create_client_handler")])

print("part 1 done")
