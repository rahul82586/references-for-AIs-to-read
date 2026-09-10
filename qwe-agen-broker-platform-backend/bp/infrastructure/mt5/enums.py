"""
Bridge between MT5's integer enum constants and our domain enums.

WHY THIS MODULE EXISTS

Our two enum modules disagree with each other and with MT5:

  * ``core/domains/instruments/enums.py`` stores ints - the right shape, but several
    of the VALUES do not match MT5's.
  * ``core/domains/accounts/enums.py`` stores strings ("retail", "market"), which
    have no MT5 integer at all.

MT5's wire format is always an integer string ("2", "127"). Mapping by ordinal
position therefore silently misreads real server data. Measured against the live
export of 362 symbols:

  CalcMode   245 symbols are MT5 value 4 = CFDLEVERAGE.
             Our CalculationMode says 4 = BONDS.
              54 symbols are MT5 5 = FOREX_NO_LEVERAGE; ours says STOCKS.
              18 symbols are MT5 2 = CFD; ours says FUTURES.
  SwapMode   189 symbols are MT5 2 = BY_SYMBOL_CURRENCY; ours says CURRENCY (ok-ish).
               7 symbols are MT5 3 = BY_MARGIN_CURRENCY; ours says INTEREST_CURRENT.
               5 symbols are MT5 5 = INTEREST_CURRENT; ours says REOPEN_CURRENT.
               2 symbols are MT5 9 = BY_PROFIT_CURRENCY; ours has no member at all.
  OrderFlags Every one of the 362 symbols carries 127. MT5's EnOrderFlags is a
             BITMASK (MARKET|LIMIT|STOP|STOP_LIMIT|SL|TP|CLOSEBY = 1|2|4|8|16|32|64).
             Our OrderFlags enum (TRADE=1, TRADE_EXPERT=2, TRADE_PLUGIN=4) is a
             different taxonomy entirely - it describes WHO placed an order, not
             WHICH order types are allowed.
  GTCMode    MT5 is GTC=0, DAILY=1, DAILY_NO_STOPS=2. Ours is TRADE=0, CALENDAR=1.
             Value 0 happens to agree, so this one is safe by coincidence only.

Every mapping below is taken from ``Include.md`` (the MT5 SDK C++ headers), not
inferred. Where our domain has no equivalent, the value is preserved in mt5_extra
rather than coerced into a neighbouring member.

Authoritative MT5 values used here:

  EnMarginMode      RETAIL=0 EXCHANGE_DISCOUNT=1 RETAIL_HEDGED=2
  EnStopOutMode     PERCENT=0 MONEY=1
  EnFreeMarginMode  NOT_USE_PL=0 USE_PL=1 PROFIT=2 LOSS=3
  EnTradeMode       DISABLED=0 LONGONLY=1 SHORTONLY=2 CLOSEONLY=3 FULL=4
  EnExecutionMode   REQUEST=0 INSTANT=1 MARKET=2 EXCHANGE=3
  EnGTCMode         GTC=0 DAILY=1 DAILY_NO_STOPS=2
  EnFillingFlags    NONE=0 FOK=1 IOC=2 BOC=4                     (bitmask)
  EnExpirationFlags NONE=0 GTC=1 DAY=2 SPECIFIED=4 SPECIFIED_DAY=8 (bitmask)
  EnSwapMode        DISABLED=0 POINTS=1 SYMBOL_CURRENCY=2 MARGIN_CURRENCY=3
                    GROUP_CURRENCY=4 INTEREST_CURRENT=5 INTEREST_OPEN=6
                    REOPEN_CLOSE=7 REOPEN_BID=8 PROFIT_CURRENCY=9
  EnNewsMode        DISABLED=0 HEADERS=1 FULL=2
  EnCalcMode        FOREX=0 FUTURES=1 CFD=2 CFDINDEX=3 CFDLEVERAGE=4
                    FOREX_NO_LEVERAGE=5 EXCH_STOCKS=32 EXCH_FUTURES=33
                    EXCH_FUTURES_FORTS=34 EXCH_OPTIONS=35 EXCH_OPTIONS_MARGIN=36
                    EXCH_BONDS=37 EXCH_STOCKS_MOEX=38 EXCH_BONDS_MOEX=39
                    SERV_COLLATERAL=64
  EnOrderFlags      MARKET=1 LIMIT=2 STOP=4 STOP_LIMIT=8 SL=16 TP=32 CLOSEBY=64
  EnMarginFreeProfitMode  PL=0 LOSS=1
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Type, TypeVar

from core.domains.accounts import enums as acct
from core.domains.instruments import enums as inst

E = TypeVar("E")

# ---------------------------------------------------------------------------
# Bitmask fields
# ---------------------------------------------------------------------------

#: Fields whose MT5 value is a decimal bitmask, never a single choice.
BITMASK_FIELDS = frozenset(
    {
        "OrderFlags",
        "FillFlags",
        "ExpirFlags",
        "TradeFlags",
        "MarginFlags",
        "SwapFlags",
        "REFlags",
        "IEFlags",
        "PermissionsFlags",
        "TickFlags",
        "ReportsFlags",
        "ReasonMode",
    }
)

#: MT5 EnOrderFlags bit meanings, for decoding the field our enum mis-models.
MT5_ORDER_FLAGS: Dict[int, str] = {
    1: "MARKET",
    2: "LIMIT",
    4: "STOP",
    8: "STOP_LIMIT",
    16: "SL",
    32: "TP",
    64: "CLOSEBY",
}

#: MT5 EnFillingFlags bit meanings.
MT5_FILL_FLAGS: Dict[int, str] = {1: "FOK", 2: "IOC", 4: "BOC"}

#: MT5 EnExpirationFlags bit meanings.
MT5_EXPIRATION_FLAGS: Dict[int, str] = {
    1: "GTC",
    2: "DAY",
    4: "SPECIFIED",
    8: "SPECIFIED_DAY",
}


def decode_bitmask(value: int, meanings: Dict[int, str]) -> list:
    """Expand an MT5 bitmask into the names of the bits that are set."""
    return [name for bit, name in meanings.items() if value & bit]


def encode_bitmask(names: list, meanings: Dict[int, str]) -> int:
    """Collapse flag names back into an MT5 bitmask."""
    reverse = {name: bit for bit, name in meanings.items()}
    out = 0
    for name in names:
        out |= reverse[name]
    return out


# ---------------------------------------------------------------------------
# One-to-one enum bridges
# ---------------------------------------------------------------------------

# EnMarginMode <-> accounts.MarginMode (string-valued in our domain)
MARGIN_MODE_TO_MT5 = {
    acct.MarginMode.RETAIL: 0,
    acct.MarginMode.EXCHANGE_DISCOUNT: 1,
    acct.MarginMode.RETAIL_HEDGED: 2,
}
MARGIN_MODE_FROM_MT5 = {v: k for k, v in MARGIN_MODE_TO_MT5.items()}

# EnStopOutMode <-> accounts.StopOutMode (already int-aligned)
STOP_OUT_MODE_TO_MT5 = {
    acct.StopOutMode.PERCENT: 0,
    acct.StopOutMode.MONEY: 1,
}
STOP_OUT_MODE_FROM_MT5 = {v: k for k, v in STOP_OUT_MODE_TO_MT5.items()}

# EnFreeMarginMode <-> accounts.FreeMarginMode (already int-aligned)
FREE_MARGIN_MODE_TO_MT5 = {
    acct.FreeMarginMode.NOT_USE_PL: 0,
    acct.FreeMarginMode.USE_PL: 1,
    acct.FreeMarginMode.PROFIT: 2,
    acct.FreeMarginMode.LOSS: 3,
}
FREE_MARGIN_MODE_FROM_MT5 = {v: k for k, v in FREE_MARGIN_MODE_TO_MT5.items()}

# EnNewsMode <-> accounts.NewsMode (string-valued)
NEWS_MODE_TO_MT5 = {
    acct.NewsMode.DISABLED: 0,
    acct.NewsMode.HEADERS: 1,
    acct.NewsMode.FULL: 2,
}
NEWS_MODE_FROM_MT5 = {v: k for k, v in NEWS_MODE_TO_MT5.items()}

# EnTradeMode <-> instruments.TradeMode (already int-aligned with MT5)
TRADE_MODE_TO_MT5 = {
    inst.TradeMode.DISABLED: 0,
    inst.TradeMode.LONGONLY: 1,
    inst.TradeMode.SHORTONLY: 2,
    inst.TradeMode.CLOSEONLY: 3,
    inst.TradeMode.FULL: 4,
}
TRADE_MODE_FROM_MT5 = {v: k for k, v in TRADE_MODE_TO_MT5.items()}

# EnExecutionMode <-> instruments.ExecutionMode (already int-aligned with MT5)
EXECUTION_MODE_TO_MT5 = {
    inst.ExecutionMode.REQUEST: 0,
    inst.ExecutionMode.INSTANT: 1,
    inst.ExecutionMode.MARKET: 2,
    inst.ExecutionMode.EXCHANGE: 3,
}
EXECUTION_MODE_FROM_MT5 = {v: k for k, v in EXECUTION_MODE_TO_MT5.items()}

# EnExpirationFlags <-> instruments.ExpirationFlags (already int-aligned with MT5)
EXPIRATION_FLAGS_TO_MT5 = {
    inst.ExpirationFlags.NONE: 0,
    inst.ExpirationFlags.GTC: 1,
    inst.ExpirationFlags.DAY: 2,
    inst.ExpirationFlags.SPECIFIED: 4,
    inst.ExpirationFlags.SPECIFIED_DAY: 8,
}
EXPIRATION_FLAGS_FROM_MT5 = {v: k for k, v in EXPIRATION_FLAGS_TO_MT5.items()}

# EnFillingFlags <-> instruments.FillingFlags.
# MT5 calls bit 4 "BOC" (back of chain / return remainder); we call it RETURN.
# Same bit, different name - the numeric mapping is exact.
FILLING_FLAGS_TO_MT5 = {
    inst.FillingFlags.NONE: 0,
    inst.FillingFlags.FOK: 1,
    inst.FillingFlags.IOC: 2,
    inst.FillingFlags.RETURN: 4,
}
FILLING_FLAGS_FROM_MT5 = {v: k for k, v in FILLING_FLAGS_TO_MT5.items()}

# EnGTCMode <-> instruments.GTCMode, corrected to MT5's three members.
GTC_MODE_TO_MT5 = {m: int(m.value) for m in inst.GTCMode}
GTC_MODE_FROM_MT5 = {v: k for k, v in GTC_MODE_TO_MT5.items()}

# EnOrderFlags <-> instruments.OrderTypeFlags. A bitmask, so both directions are
# identity over the integer value.
ORDER_TYPE_FLAGS_TO_MT5 = {m: int(m.value) for m in inst.OrderTypeFlags}
ORDER_TYPE_FLAGS_FROM_MT5 = {int(m.value): m for m in inst.OrderTypeFlags}

# EnCalcMode <-> instruments.CalculationMode. The enum was corrected to MT5's own
# values in M1, so this is now an identity mapping over all 15 members. Before the
# correction only 4 values mapped and 299 of 362 real symbols had to be quarantined.
CALC_MODE_TO_MT5 = {m: int(m.value) for m in inst.CalculationMode}
CALC_MODE_FROM_MT5 = {v: k for k, v in CALC_MODE_TO_MT5.items()}

# EnSwapMode <-> instruments.SwapMode, likewise an identity mapping after correction.
# Built by value so that the deprecated aliases (CURRENCY, REOPEN_CURRENT) cannot
# collide with the canonical members that share their integer.
SWAP_MODE_TO_MT5 = {m: int(m.value) for m in inst.SwapMode}
SWAP_MODE_FROM_MT5 = {int(m.value): m for m in inst.SwapMode if not m.name.startswith("REOPEN_CURRENT") and m.name != "CURRENCY"}

# EnMarginFreeProfitMode - not modelled in our domain.
MARGIN_FREE_PROFIT_MODE_FROM_MT5: Dict[int, str] = {0: "PL", 1: "LOSS"}


# ---------------------------------------------------------------------------
# Account type: MT5 has no enum for this. It is encoded in the GROUP PATH.
# ---------------------------------------------------------------------------

#: Group path prefix -> AccountType. Observed in the reference export:
#: demo\\Standard, demo\\Challenge, real\\real, real\\real-SF, managers\\dealers,
#: managers\\administrators, managers\\API, preliminary.
GROUP_PATH_PREFIX_TO_ACCOUNT_TYPE = {
    "demo": acct.AccountType.DEMO,
    "real": acct.AccountType.REAL,
    "managers": acct.AccountType.MANAGER,
    "preliminary": acct.AccountType.PRELIMINARY,
    "contest": acct.AccountType.CONTEST,
    "coverage": acct.AccountType.COVERAGE,
}

ACCOUNT_TYPE_TO_GROUP_PATH_PREFIX = {v: k for k, v in GROUP_PATH_PREFIX_TO_ACCOUNT_TYPE.items()}


def account_type_from_group_path(path: str) -> Optional[Any]:
    """Derive the AccountType from an MT5 group path such as ``real\\real-SF``."""
    if not path:
        return None
    head = path.replace("/", "\\").split("\\", 1)[0].strip().lower()
    return GROUP_PATH_PREFIX_TO_ACCOUNT_TYPE.get(head)


def group_path_from_account_type(account_type: Any, leaf: str = "") -> str:
    """Build an MT5-style group path from an AccountType and a leaf name."""
    prefix = ACCOUNT_TYPE_TO_GROUP_PATH_PREFIX.get(account_type, "real")
    return f"{prefix}\\{leaf}" if leaf else prefix


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------


def to_mt5(mapping: Dict[Any, int], value: Any, field: str) -> int:
    """Domain enum -> MT5 integer. Raises rather than guessing."""
    try:
        return mapping[value]
    except (KeyError, TypeError):
        raise ValueError(
            f"{field}: {value!r} has no MT5 equivalent; refusing to guess. "
            f"Mappable values: {sorted((str(k) for k in mapping), key=str)}"
        ) from None


def from_mt5(mapping: Dict[int, Any], raw: Any, field: str) -> Optional[Any]:
    """MT5 integer -> domain enum, or None when MT5 has a value we do not model.

    Returning None is deliberate: the caller stores the raw integer in mt5_extra so
    an export can restore it. Coercing to the nearest member is what produced the
    245-symbols-read-as-BONDS defect this module exists to prevent.
    """
    if raw is None or raw == "":
        return None
    try:
        key = int(raw)
    except (TypeError, ValueError):
        return None
    return mapping.get(key)
