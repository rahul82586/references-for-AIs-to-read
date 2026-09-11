"""M6 patch (item 7): client login verifies a password.

POST /api/v1/auth/login used to issue a JWT to anyone who named an existing,
enabled login_id. The LoginRequest schema declared `password` required, and the
route ignored it - it parsed the body by hand and defaulted login_id to
"100001" when absent. The client API was authenticate-in-name-only: the
largest open hole in the platform.

Now: the password is required, verified against the account's Argon2 hash, and
every failure returns the SAME generic 401 so responses do not disclose which
leg failed (unknown login vs wrong password vs disabled vs unset hash).
Accounts are provisioned without a password, so an unset hash REJECTS login
rather than falling back - fail closed. Managers already had Argon2 hashes and
a bootstrap that prints the password once; clients get the same hasher and an
admin endpoint to set/rotate it.
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
    print(f"{path}: {len(pairs)} patch(es)")


# --- 1. Account entity: the hash field --------------------------------------
apply("core/domains/accounts/account.py", [(
    "    last_login: Optional[datetime] = None\n",
    """    last_login: Optional[datetime] = None
    #: Argon2 hash of the trading password (MT5 IMTAccount::m_password main).
    #: The domain stores ONLY the hash - never the plaintext. Empty means
    #: "not yet provisioned": login refuses it rather than allowing it, because
    #: before M6 there was no password check at all and any caller who named an
    #: existing login_id was issued a token for that account.
    password_hash: str = ""
""",
)])

# --- 2. AccountModel column + mappers ---------------------------------------
apply("infrastructure/persistence/account_models.py", [
    (
        "    last_login = Column(DateTime(timezone=True), nullable=True)\n",
        "    last_login = Column(DateTime(timezone=True), nullable=True)\n"
        "    password_hash = Column(String(512), nullable=False, default=\"\")\n",
    ),
    (
        "        last_login=account.last_login,\n",
        "        last_login=account.last_login,\n"
        "        password_hash=getattr(account, \"password_hash\", \"\") or \"\",\n",
    ),
    (
        "        margin_reserved=_money(getattr(model, 'margin_reserved', None), currency),\n",
        "        margin_reserved=_money(getattr(model, 'margin_reserved', None), currency),\n"
        "        password_hash=getattr(model, 'password_hash', '') or '',\n",
    ),
])

# --- 3. The login route: verify, and fail closed -----------------------------
apply("api/routers/auth.py", [(
    '''@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request
):
    """Authenticate client login and issue JWT access token."""
    login_id = None
    
    # Parse login_id from JSON or form data or query params
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            data = await request.json()
            login_id = data.get("login_id") or data.get("username")
        except Exception:
            pass
    elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        try:
            form = await request.form()
            login_id = form.get("username") or form.get("login_id")
        except Exception:
            pass

    if not login_id:
        login_id = request.query_params.get("username") or "100001"

    # Try resolving account from repo if DI container is registered
    try:
        account_repo = get_account_repo()
        if account_repo:
            account = await account_repo.find_by_login(login_id)
            if account and not getattr(account, "is_enabled", True):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Account is disabled"
                )
    except RuntimeError:
        # DI container uninitialized (dev mode fallback)
        pass
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Account lookup error during login: {e}")

    # Generate JWT token
    access_token = create_access_token(data={"sub": str(login_id)})
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=86400
    )
''',
    '''@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request
):
    """Authenticate client login and issue a JWT access token.

    M6: the password is REQUIRED and verified. Before this, the route parsed
    login_id out of the body and issued a token for it - the `password` field
    the LoginRequest schema declared required was never read, and when no
    login_id was supplied it defaulted to "100001". Any caller who could reach
    the endpoint owned any account they could name.

    Every failure returns the SAME generic 401: an attacker must not be able to
    distinguish "no such login" from "wrong password" from "disabled" from
    "password not provisioned". The specific reason goes to the server log.
    """
    from infrastructure.security.password_hasher import Argon2PasswordHasher

    generic_failure = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    login_id = None
    password = None

    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            data = await request.json()
            login_id = data.get("login_id") or data.get("username")
            password = data.get("password")
        except Exception:
            pass
    elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        try:
            form = await request.form()
            login_id = form.get("username") or form.get("login_id")
            password = form.get("password")
        except Exception:
            pass

    if not login_id:
        login_id = request.query_params.get("username")
    if not password:
        password = request.query_params.get("password")

    if not login_id or not password:
        logger.info("login refused: login_id and password are both required")
        raise generic_failure

    try:
        account_repo = get_account_repo()
    except RuntimeError:
        account_repo = None
    if account_repo is None:
        # No repository means no account can be authenticated. Refusing is the
        # only safe answer; the old code minted a token anyway.
        logger.error("login refused: no account repository is wired")
        raise generic_failure

    try:
        account = await account_repo.find_by_login(login_id)
    except Exception as e:
        logger.warning(f"Account lookup error during login: {e}")
        raise generic_failure

    if account is None:
        logger.info("login refused: unknown login_id %s", login_id)
        raise generic_failure
    if not getattr(account, "is_enabled", True):
        logger.info("login refused: account %s is disabled", login_id)
        raise generic_failure

    stored_hash = getattr(account, "password_hash", "") or ""
    if not stored_hash:
        logger.warning(
            "login refused: account %s has no password provisioned; set one via "
            "POST /api/v1/admin/accounts/set-password", login_id,
        )
        raise generic_failure

    try:
        password_ok = Argon2PasswordHasher().verify_password(password, stored_hash)
    except Exception as e:
        logger.error("password verification errored for %s: %s", login_id, e)
        raise generic_failure
    if not password_ok:
        logger.info("login refused: wrong password for %s", login_id)
        raise generic_failure

    access_token = create_access_token(data={"sub": str(login_id), "role": "client"})
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=86400
    )
''',
)])

print("login password verification applied")
