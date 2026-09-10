import io

# ---------------------------------------------------------------------------
# accounts.login is String(32); everything else in the platform identifies an
# account with an int. Coerce at the boundary, in both directions.
# ---------------------------------------------------------------------------

p = "infrastructure/persistence/repositories/account_repository.py"
s = io.open(p, encoding="utf-8", newline="").read()
crlf = "\r\n" in s


def N(x):
    return x.replace("\n", "\r\n") if crlf else x


old = N('''    async def find_by_login(self, login_id: str, session: Optional[AsyncSession] = None) -> Optional[Account]:
        if session is not None:''')
assert old in s
new = N('''    async def find_by_login(self, login_id: Any, session: Optional[AsyncSession] = None) -> Optional[Account]:
        # accounts.login is String(32) - MT5's natural key - but the rest of the platform
        # identifies an account with an int: Order.account_login, Position.account_login,
        # Deal.account_login and their BigInteger columns all are. Every caller on the
        # execution path therefore arrives with an int, and `session.get(AccountModel, 900101)`
        # binds an INTEGER against a TEXT primary key: SQLite compares the two as
        # different types and finds nothing, PostgreSQL raises "operator does not exist:
        # character varying = integer". Coercing here keeps the string key where it
        # belongs - at the storage boundary - instead of leaking into the domain.
        login_id = str(login_id)

        if session is not None:''')
s = s.replace(old, new, 1)

old = N("from typing import Optional, List\n")
if old in s:
    s = s.replace(old, N("from typing import Any, Optional, List\n"), 1)
else:
    old2 = N("from typing import Optional\n")
    assert old2 in s, "typing import not found"
    s = s.replace(old2, N("from typing import Any, Optional\n"), 1)

io.open(p, "w", encoding="utf-8", newline="").write(s)
print("account_repository: login coerced to the String key")

p = "infrastructure/persistence/account_models.py"
s = io.open(p, encoding="utf-8").read()
old = '''    account = Account(
        login=model.login,'''
assert old in s
new = '''    account = Account(
        # An int, matching Account.login's own declaration and the BigInteger
        # account_login columns on orders, deals and positions. Returning the raw
        # String(32) primary key made every downstream lookup a type mismatch:
        # position_repo.get_by_account(account.login) compared TEXT against a BIGINT
        # column and came back empty, which is the same silent "no positions" that
        # writes margin_used = 0 - reached by a different route.
        login=_int(model.login, 0),'''
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("db_to_account: login is an int")
