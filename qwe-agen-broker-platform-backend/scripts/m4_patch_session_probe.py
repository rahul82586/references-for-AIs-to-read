import io
import re

# ---------------------------------------------------------------------------
# 1. the two repositories that violated their own port
# ---------------------------------------------------------------------------
p = "infrastructure/persistence/repositories/order_repository.py"
s = io.open(p, encoding="utf-8", newline="").read()
old = '''    async def find_by_id(self, order_id: str) -> Optional[Order]:\r
        async with self.session_factory() as session:\r
            result = await session.execute(\r
                select(OrderModel).where(OrderModel.ticket_id == order_id)\r
            )\r
            model = result.scalar_one_or_none()\r
            return db_to_order(model) if model else None\r
'''
assert old in s
new = '''    async def find_by_id(self, order_id: str, session: Optional[AsyncSession] = None) -> Optional[Order]:\r
        """One order by ticket. Accepts the unit-of-work session the port declares.\r
\r
        IOrderRepository declares `find_by_id(order_id, session=None)`, and this did not\r
        take the parameter. RecordDealHandler probes for it and passes it through when a\r
        unit of work is active, so recording a fill inside a transaction raised\r
        TypeError. The probe is what made this survivable outside a UoW - and the probe\r
        itself was broken, see _accepts_session().\r
        """\r
        async def _find(sess: AsyncSession):\r
            result = await sess.execute(\r
                select(OrderModel).where(OrderModel.ticket_id == order_id)\r
            )\r
            model = result.scalar_one_or_none()\r
            return db_to_order(model) if model else None\r
\r
        if session is not None:\r
            return await _find(session)\r
        async with self.session_factory() as sess:\r
            return await _find(sess)\r
'''
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="").write(s)
print("SqlOrderRepository.find_by_id accepts a session")

p = "infrastructure/persistence/repositories/deal_repository.py"
s = io.open(p, encoding="utf-8", newline="").read()
old = '''    async def find_by_id(self, deal_id: str) -> Optional[Deal]:\r
        async with self.session_factory() as session:\r
            result = await session.execute(\r
                select(DealModel).where(DealModel.deal_id == deal_id)\r
            )\r
            model = result.scalar_one_or_none()\r
            return db_to_deal(model) if model else None\r
'''
assert old in s
new = '''    async def find_by_id(self, deal_id: str, session: Optional[AsyncSession] = None) -> Optional[Deal]:\r
        """One deal by id. Accepts the unit-of-work session IDealRepository declares."""\r
        async def _find(sess: AsyncSession):\r
            result = await sess.execute(\r
                select(DealModel).where(DealModel.deal_id == deal_id)\r
            )\r
            model = result.scalar_one_or_none()\r
            return db_to_deal(model) if model else None\r
\r
        if session is not None:\r
            return await _find(session)\r
        async with self.session_factory() as sess:\r
            return await _find(sess)\r
'''
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="").write(s)
print("SqlDealRepository.find_by_id accepts a session")

# ---------------------------------------------------------------------------
# 2. the unsound probe, everywhere it appears
# ---------------------------------------------------------------------------
HELPER = '''def _accepts_session(method: Any) -> bool:
    """Does this repository method take a `session` keyword argument?

    The check this replaces was `'session' in method.__code__.co_varnames`, which reads
    the method's LOCAL VARIABLES as well as its parameters. SqlOrderRepository.find_by_id
    was declared `find_by_id(self, order_id)` but its body did
    `async with self.session_factory() as session:` - so the probe saw a name called
    "session", concluded the parameter existed, and passed `session=None` to a method
    that could not accept it: TypeError on the write path of every single fill.

    Signature inspection is the only reliable way to ask, and it also handles the
    **kwargs case the varnames probe would have got wrong in the other direction.
    """
    import inspect

    try:
        signature = inspect.signature(method)
    except (TypeError, ValueError):
        return False
    for name, parameter in signature.parameters.items():
        if name == "session":
            return True
        if parameter.kind is inspect.Parameter.VAR_KEYWORD:
            return True
    return False


'''

p = "application/commands/record_deal.py"
s = io.open(p, encoding="utf-8", newline="").read()
crlf = "\r\n" in s


def N(x):
    return x.replace("\n", "\r\n") if crlf else x


anchor = N("def position_action_for(deal_type: Any) -> PositionAction:")
assert anchor in s
s = s.replace(anchor, N(HELPER) + anchor, 1)

# every `'session' in <expr>.__code__.co_varnames` becomes `_accepts_session(<expr>)`
pattern = re.compile(r"'session' in ([A-Za-z_][A-Za-z0-9_.]*)\.__code__\.co_varnames")
found = pattern.findall(s)
s = pattern.sub(lambda m: f"_accepts_session({m.group(1)})", s)
io.open(p, "w", encoding="utf-8", newline="").write(s)
print(f"record_deal: replaced {len(found)} unsound probes -> {found}")

# the same pattern anywhere else in the tree
for other in ("application/commands/close_position.py", "application/commands/modify_deal.py",
              "application/commands/cancel_order.py", "application/commands/modify_order.py",
              "application/commands/balance_operation.py"):
    try:
        t = io.open(other, encoding="utf-8", newline="").read()
    except OSError:
        continue
    if "co_varnames" in t:
        print(f"  NOTE: {other} still probes co_varnames")
