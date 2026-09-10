"""
Step M1 part 1 - correct the instruments enums and their call sites.

  * core/domains/instruments/enums.py is replaced with values taken from the MT5 SDK
    C++ headers. Four enums were wrong; see that file's docstring for the measured
    impact (245 symbols read as BONDS instead of CFDLEVERAGE, and so on).
  * symbol.py updated for GTCMode.GTC (was .TRADE) and OrderTypeFlags (was OrderFlags,
    whose members described who placed an order, not which order types are allowed).
    order_flags now defaults to the full bitmask, which is what all 362 symbols in the
    reference export carry (127).
  * TradingSession.open_time and is_within() raised AttributeError: the field is
    open_minutes (plural) but both read self.open_minute (singular). Every trading
    session check in the platform was broken. QuoteSession used the singular spelling
    and worked, which is why nobody noticed. Both are now open_minutes/close_minutes.
  * The value_objects docstring claimed MT5 indexes sessions 0=Monday, 6=Sunday. The
    live export is Sunday-first. Corrected, with the wire module as the authority.
"""

from __future__ import annotations

import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
if not (ROOT / "core" / "domains" / "instruments" / "symbol.py").is_file():
    raise SystemExit(f"not a broker-platform root: {ROOT}")


def load(rel: str) -> str:
    with open(ROOT / rel, encoding="utf-8", newline="") as fh:
        return fh.read()


def save(rel: str, text: str, *, crlf: bool) -> None:
    norm = text.replace("\r\n", "\n")
    with open(ROOT / rel, "w", encoding="utf-8", newline="") as fh:
        fh.write(norm.replace("\n", "\r\n") if crlf else norm)


def sub(rel: str, old: str, new: str, why: str) -> None:
    text = load(rel)
    crlf = "\r\n" in text
    work = text.replace("\r\n", "\n")
    if old not in work:
        raise SystemExit(f"[FAIL] {rel}: pattern not found ({why}):\n{old[:200]!r}")
    save(rel, work.replace(old, new, 1), crlf=crlf)
    print(f"  ok  {rel}: {why}")


# ---------------------------------------------------------------------------
# 1. Replace the instruments enums with MT5-header-accurate values
# ---------------------------------------------------------------------------

src = HERE / "m1pkg" / "instruments_enums.py"
dst = ROOT / "core" / "domains" / "instruments" / "enums.py"
shutil.copyfile(src, dst)
print("  ok  core/domains/instruments/enums.py: replaced with MT5 SDK header values")

# ---------------------------------------------------------------------------
# 2. symbol.py call sites
# ---------------------------------------------------------------------------

SYM = "core/domains/instruments/symbol.py"

sub(
    SYM,
    """from .enums import (
    CalculationMode, ExecutionMode, TradeMode, FillingFlags,
    ExpirationFlags, GTCMode, SwapMode, OrderFlags, OptionMode
)""",
    """from .enums import (
    CalculationMode, ExecutionMode, TradeMode, FillingFlags,
    ExpirationFlags, GTCMode, SwapMode, OrderTypeFlags, OptionMode
)""",
    "import OrderTypeFlags instead of the old OrderFlags",
)

sub(
    SYM,
    "    gtc_mode: GTCMode = GTCMode.TRADE",
    "    gtc_mode: GTCMode = GTCMode.GTC",
    "GTCMode.TRADE was renamed to GTC (MT5 ORDERS_GTC)",
)

sub(
    SYM,
    "    order_flags: OrderFlags = OrderFlags.TRADE",
    """    # MT5 EnOrderFlags is a bitmask of WHICH ORDER TYPES the symbol accepts, and
    # every symbol in the reference export carries 127 (all seven bits). The old
    # default of OrderFlags.TRADE came from an enum describing who placed an order.
    order_flags: OrderTypeFlags = OrderTypeFlags(127)""",
    "order_flags now defaults to the full MT5 bitmask (127), as real servers do",
)

# ---------------------------------------------------------------------------
# 3. TradingSession: open_minute -> open_minutes (the AttributeError)
# ---------------------------------------------------------------------------

VO = "core/domains/instruments/value_objects.py"

sub(
    VO,
    """    MT5 stores sessions per day of week (0=Monday, 6=Sunday).
    Each day can have multiple sessions (e.g., morning + evening).
    Times are stored as minutes from midnight for efficiency.
    \"\"\"""",
    """    MT5 stores SessionsQuotes / SessionsTrades as a 7-element array indexed
    SUNDAY-FIRST: 0=Sunday .. 6=Saturday. This is NOT Python's weekday(), where
    0=Monday. infrastructure.mt5.wire.WEEKDAY_SUNDAY_FIRST is the authority.
    Each day can have multiple sessions (e.g. morning + evening).
    Times are stored as minutes from midnight (0..1440) for efficiency.
    \"\"\"""",
    "corrected the weekday-index docstring (MT5 is Sunday-first, not Monday-first)",
)

sub(
    VO,
    """    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    open_minutes: int = 0  # Minutes from midnight (e.g., 60 = 01:00)
    close_minute: int = 1440  # Minutes from midnight (1440 = 24:00)
    
    @property
    def open_time(self) -> time:
        \"\"\"Convert open_minutes to time object.\"\"\"
        hours = self.open_minute // 60
        minutes = self.open_minute % 60
        return time(hours, minutes)""",
    """    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    day_of_week: int = 0  # MT5 order: 0=Sunday .. 6=Saturday
    open_minutes: int = 0  # Minutes from midnight (e.g., 60 = 01:00)
    close_minutes: int = 1440  # Minutes from midnight (1440 = 24:00)

    @property
    def open_time(self) -> time:
        \"\"\"Convert open_minutes to a time object.\"\"\"
        return time(self.open_minutes // 60, self.open_minutes % 60)""",
    "TradingSession.open_time read self.open_minute but the field is open_minutes",
)

sub(
    VO,
    """    @property
    def close_time(self) -> time:
        \"\"\"Convert close_minute to time object.\"\"\"
        hours = self.close_minute // 60
        minutes = self.close_minute % 60
        # Handle midnight (24:00 = 00:00)
        if hours == 24:
            return time(23, 59, 59)
        return time(hours, minutes)
    
    def is_within(self, check_time: time) -> bool:
        \"\"\"Check if a time is within this session.\"\"\"
        # Handle overnight sessions (e.g., 22:00 to 06:00)
        if self.open_minute > self.close_minute:
            return check_time >= self.open_time or check_time <= self.close_time
        return self.open_time <= check_time <= self.close_time""",
    """    @property
    def close_time(self) -> time:
        \"\"\"Convert close_minutes to a time object.

        1440 means end of day, which time() cannot represent, so it clamps to
        23:59:59. Callers comparing against a bare midnight should compare
        close_minutes directly rather than close_time.
        \"\"\"
        hours = self.close_minutes // 60
        minutes = self.close_minutes % 60
        if hours >= 24:
            return time(23, 59, 59)
        return time(hours, minutes)

    def is_within(self, check_time: time) -> bool:
        \"\"\"Check whether a time falls inside this session.\"\"\"
        # Overnight sessions (e.g. 22:00 to 06:00) wrap past midnight.
        if self.open_minutes > self.close_minutes:
            return check_time >= self.open_time or check_time <= self.close_time
        return self.open_time <= check_time <= self.close_time""",
    "TradingSession.close_time / is_within read the singular field names too",
)

# QuoteSession used the singular spelling and worked; align it so the two classes
# agree, since both are fed from the same MT5 Sunday-first arrays.
sub(
    VO,
    """    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    open_minute: int = 0
    close_minute: int = 1440
    
    @property
    def open_time(self) -> time:
        hours = self.open_minute // 60
        minutes = self.open_minute % 60
        return time(hours, minutes)
    
    @property
    def close_time(self) -> time:
        hours = self.close_minute // 60
        minutes = self.close_minute % 60
        if hours == 24:
            return time(23, 59, 59)
        return time(hours, minutes)""",
    """    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    day_of_week: int = 0  # MT5 order: 0=Sunday .. 6=Saturday
    open_minutes: int = 0
    close_minutes: int = 1440

    @property
    def open_time(self) -> time:
        return time(self.open_minutes // 60, self.open_minutes % 60)

    @property
    def close_time(self) -> time:
        hours = self.close_minutes // 60
        minutes = self.close_minutes % 60
        if hours >= 24:
            return time(23, 59, 59)
        return time(hours, minutes)""",
    "aligned QuoteSession field names with TradingSession (open_minutes/close_minutes)",
)

print("\n  note: any code constructing QuoteSession(open_minute=...) or")
print("        TradingSession(close_minute=...) must switch to the plural names.")
