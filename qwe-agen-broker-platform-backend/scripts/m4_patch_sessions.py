import io

p = "core/domains/instruments/symbol.py"
s = io.open(p, encoding="utf-8", newline="").read()
crlf = "\r\n" in s


def N(x):
    return x.replace("\n", "\r\n") if crlf else x


# --- module-level helpers ---------------------------------------------------
anchor = N("class Symbol:")
assert anchor in s
helpers = N('''def mt5_day_index(check_datetime: datetime) -> int:
    """MT5's Sunday-first day index for a datetime.

    MT5 stores SessionsQuotes / SessionsTrades as a 7-element array indexed
    SUNDAY-FIRST (0=Sunday .. 6=Saturday); Python's weekday() is MONDAY-first
    (0=Monday .. 6=Sunday). infrastructure.mt5.wire.WEEKDAY_SUNDAY_FIRST is the
    authority and TradingSession's own docstring says so explicitly.

    Both session checks below used `check_datetime.weekday()` directly as the MT5 index,
    which looked up the WRONG DAY for every symbol: a Monday order consulted the Sunday
    session, a Friday order consulted Thursday. On a configuration that closes the
    market at the weekend - which is every real FX server - that meant Monday trading
    was refused and Saturday trading was allowed.
    """
    return (check_datetime.weekday() + 1) % 7


def sessions_for_day(container: Any, day_index: int) -> list:
    """The sessions for one day, from either shape the field actually holds.

    Symbol declares `Dict[int, List[TradingSession]]`, but every producer of real
    symbols - the YAML loader's parse_sessions(), the MT5 importer, and the database
    mapper's sessions_from_days() - builds a FLAT LIST whose members carry
    `day_of_week`. Both session checks called `container.get(day)`, so against any
    symbol loaded from configuration or from the database they raised
    `AttributeError: 'list' object has no attribute 'get'`.

    That is not a corner case: CreateOrderHandler checks the session at step 2 and
    PreTradeRiskService checks it at step 4, so no order could be placed against a real
    configuration at all. Accepting both shapes means the declared default keeps working
    and the three real producers start working.
    """
    if not container:
        return []
    if isinstance(container, dict):
        return list(container.get(day_index) or [])
    out = []
    for session in container:
        try:
            index = int(getattr(session, "day_of_week", 0))
        except (TypeError, ValueError):
            index = 0
        if index == day_index:
            out.append(session)
    return out


def _session_covers(session: Any, check_time: Any) -> bool:
    """Does one session cover this time? Prefers is_within, which handles overnight."""
    is_within = getattr(session, "is_within", None)
    if callable(is_within):
        return bool(is_within(check_time))
    open_time = getattr(session, "open_time", None)
    close_time = getattr(session, "close_time", None)
    if open_time is None or close_time is None:
        return False
    if open_time > close_time:  # wraps past midnight
        return check_time >= open_time or check_time <= close_time
    return open_time <= check_time <= close_time


''')
s = s.replace(anchor, helpers + anchor, 1)

# --- is_quote_session_active ------------------------------------------------
old = N('''        day_of_week = check_datetime.weekday()  # 0=Monday, 6=Sunday
        check_time = check_datetime.time()
        
        sessions = self.quote_sessions.get(day_of_week, [])
        if not sessions:
            return False
        
        return any(session.open_time <= check_time <= session.close_time 
                   for session in sessions)''')
assert old in s
new = N('''        check_time = check_datetime.time()

        sessions = sessions_for_day(self.quote_sessions, mt5_day_index(check_datetime))
        if not sessions:
            return False

        return any(_session_covers(session, check_time) for session in sessions)''')
s = s.replace(old, new, 1)

# --- is_trade_session_active ------------------------------------------------
old = N('''        day_of_week = check_datetime.weekday()
        check_time = check_datetime.time()
        
        sessions = self.trade_sessions.get(day_of_week, [])
        if not sessions:
            return False
        
        return any(session.is_within(check_time) for session in sessions)''')
assert old in s
new = N('''        check_time = check_datetime.time()

        sessions = sessions_for_day(self.trade_sessions, mt5_day_index(check_datetime))
        if not sessions:
            return False

        return any(_session_covers(session, check_time) for session in sessions)''')
s = s.replace(old, new, 1)

# --- make sure Any is imported ----------------------------------------------
if "from typing import" in s:
    import re
    m = re.search(r"from typing import ([^\r\n]+)", s)
    names = [n.strip() for n in m.group(1).split(",")]
    if "Any" not in names:
        names.append("Any")
        s = s.replace(m.group(0), "from typing import " + ", ".join(names), 1)
else:
    s = s.replace(N("from decimal import Decimal"), N("from decimal import Decimal\nfrom typing import Any"), 1)

io.open(p, "w", encoding="utf-8", newline="").write(s)
print("symbol sessions fixed; crlf =", crlf)
