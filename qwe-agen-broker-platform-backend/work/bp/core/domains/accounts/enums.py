"""Account domain enumerations."""
from enum import Enum, IntFlag


class AccountType(Enum):
    """Account types as per MT5."""
    REAL = "real"
    DEMO = "demo"
    PRELIMINARY = "preliminary"  # KYC pending
    CONTEST = "contest"
    COVERAGE = "coverage"  # Internal hedge account
    MANAGER = "manager"
    DEALER = "dealer"


class ClientStatus(Enum):
    """Client status (IMTUser::EnClientStatus)."""
    UNREGISTERED = 0
    REGISTERED = 100
    FUNDED = 200
    ACTIVE = 300
    INACTIVE = 400
    SUSPENDED = 500
    CLOSED = 600
    TERMINATED = 700


class SOActivation(Enum):
    """Stop-out activation states (IMTAccount::EnSOActivation)."""
    NONE = 0
    MARGIN_CALL = 1
    STOP_OUT = 2


class MarginMode(Enum):
    """Group margin calculation modes."""
    RETAIL = "retail"
    EXCHANGE_DISCOUNT = "exchange_discount"
    RETAIL_HEDGED = "retail_hedged"


class ExecutionMode(Enum):
    """Order execution modes."""
    REQUEST = "request"
    INSTANT = "instant"
    MARKET = "market"
    EXCHANGE = "exchange"


class TradeMode(Enum):
    """Symbol trade modes."""
    DISABLED = "disabled"
    LONGONLY = "longonly"
    SHORTONLY = "shortonly"
    CLOSEONLY = "closeonly"
    FULL = "full"


class FreeMarginMode(Enum):
    """Free margin calculation modes."""
    NOT_USE_PL = 0
    USE_PL = 1
    PROFIT = 2
    LOSS = 3


class StopOutMode(Enum):
    """Stop-out calculation modes."""
    PERCENT = 0
    MONEY = 1


class CommissionType(Enum):
    """Commission calculation types."""
    DEAL = "deal"
    VOLUME = "volume"
    PERCENT = "percent"


class NewsMode(Enum):
    """News display modes."""
    DISABLED = "disabled"
    HEADERS = "headers"
    FULL = "full"


class TradeFlags(IntFlag):
    """Bitwise trade permission flags."""
    NONE = 0x00000000
    SWAPS = 0x00000001
    TRAILING = 0x00000002
    EXPERTS = 0x00000004
    EXPIRATION = 0x00000008
    SIGNALS_ALL = 0x00000010
    SIGNALS_OWN = 0x00000020
    SO_COMPENSATION = 0x00000040
    SO_FULLY_HEDGED = 0x00000080
    FIFO_CLOSE = 0x00000100
    HEDGE_PROHIBIT = 0x00000200
    #: Include.md EnTradeFlags: TRADEFLAGS_DEAL_COST = 0x400, "calculate and show
    #: deals cost". Missing before step 5, so a live group whose TradeFlags carried
    #: it could not be represented and int(TradeFlags(x)) != x on the way back.
    DEAL_COST = 0x00000400
    #: TRADEFLAGS_SO_COMPENSATION_CREDIT = 0x800, "allow credit compensation after
    #: stop out".
    SO_COMPENSATION_CREDIT = 0x00000800
    #: SDK TRADEFLAGS_DEFAULT = SWAPS|TRAILING|EXPERTS|EXPIRATION|SIGNALS_ALL.
    DEFAULT = 0x0000001F


CommissionMode = CommissionType


# ---------------------------------------------------------------------------
# Identity-plane enums, transcribed from Include.md (IMTConGroup / IMTClient /
# IMTConManager). The ints are MT5's exactly: they are what the wire carries and
# what migration 009's columns store, so a wrong value is a wrong export.
# ---------------------------------------------------------------------------


class PermissionsFlags(IntFlag):
    """IMTConGroup::EnPermissionsFlags - the group's Permissions tab."""

    NONE = 0x00000000
    CERT_CONFIRM = 0x00000001        # certificate confirmation necessary
    ENABLE_CONNECTION = 0x00000002   # clients connections allowed
    RESET_PASSWORD = 0x00000004      # reset password after first logon
    FORCED_OTP_USAGE = 0x00000008    # forced usage of OTP
    RISK_WARNING = 0x00000010        # show risk warning window on start
    REGULATION_PROTECT = 0x00000020  # country-specific regulatory protection
    NOTIFY_DEALS = 0x00000040        # push notification on deals
    NOTIFY_ORDERS = 0x00000080       # push notification on orders
    NOTIFY_BALANCES = 0x00000100     # push notification on balances


class AuthMode(Enum):
    """IMTConGroup::EnAuthMode - how a client authenticates into this group."""

    STANDARD = 0
    RSA1024 = 1
    RSA2048 = 2
    RSA_CUSTOM = 3


class AuthOTPMode(Enum):
    """IMTConGroup::EnAuthOTPMode."""

    DISABLED = 0
    TOTP_SHA256 = 1
    TOTP_SHA256_WEB = 2


class ReportsMode(Enum):
    """IMTConGroup::EnReportsMode."""

    DISABLED = 0
    FULL = 1        # End of Day & End of Month
    EOD_ONLY = 2
    EOM_ONLY = 3


class ReportsFlags(IntFlag):
    """IMTConGroup::EnReportsFlags."""

    NONE = 0
    EMAIL = 1        # send reports through email
    SUPPORT = 2      # copy reports to the support email
    STATEMENTS = 4   # generate reports


class MailMode(Enum):
    """IMTConGroup::EnMailMode - internal mail."""

    DISABLED = 0
    FULL = 1


class TransferMode(Enum):
    """IMTConGroup::EnTransferMode - who may transfer funds between accounts."""

    DISABLED = 0
    NAME = 1
    GROUP = 2
    NAME_GROUP = 3


class MarginFreeProfitMode(Enum):
    """IMTConGroup::EnMarginFreeProfitMode."""

    PL = 0     # both fixed loss and profit count toward free margin
    LOSS = 1   # only fixed loss counts


class HistoryLimit(Enum):
    """IMTConGroup::EnHistoryLimit - how much history a client may request."""

    ALL = 0
    MONTHS_1 = 1
    MONTHS_3 = 2
    MONTHS_6 = 3
    YEAR_1 = 4
    YEAR_2 = 5
    YEAR_3 = 6


class ManagerLimit(Enum):
    """IMTConManager::EnManagerLimit - a manager's logs/reports window.

    Same int scale as HistoryLimit; MT5 keeps them as separate enums and the
    strictest limit always applies (ManagerAccount.effective_report_window).
    """

    ALL = 0
    MONTHS_1 = 1
    MONTHS_3 = 2
    MONTHS_6 = 3
    YEAR_1 = 4
    YEAR_2 = 5
    YEAR_3 = 6


class ClientType(Enum):
    """IMTClient::EnClientType."""

    UNDEFINED = 0
    INDIVIDUAL = 1
    CORPORATE = 2
    FUND = 3


class Gender(Enum):
    """IMTClient::EnGender."""

    UNSPECIFIED = 0
    MALE = 1
    FEMALE = 2


class KYCStatus(Enum):
    """IMTClient::EnKYCStatus."""

    UNDEFINED = 0
    APPROVED = 1
    DECLINED = 2


class ClientOrigin(Enum):
    """IMTClient::EnClientOrigin - how the client record came to exist."""

    MANUAL = 0
    DEMO = 1
    CONTEST = 2
    PRELIMINARY = 3
    REAL = 4


class ResidencyStatus(str, Enum):
    """The Account tab's Status field: RE resident / NR non-resident.

    A STRING on the wire - IMTUser::Status() returns LPCWSTR, and the guide's
    Editing-Account tab lists exactly these two values. Not an int.
    """

    UNSET = ""
    RESIDENT = "RE"
    NON_RESIDENT = "NR"

