"""
FIX 4.4 message encoding / decoding (M10 - A-Book LP gateway skeleton).

A dependency-free FIX message representation: ordered (tag, value) fields with
BeginString(8)/BodyLength(9)/CheckSum(10) computed on encode and verified on
parse. Repeating groups survive parsing because fields keep their wire ORDER
(no dict squashing) - MarketDataSnapshotFullRefresh entries are read off the
ordered list.

The gateway targets sessions whose transport handles sequencing/logon framing
(quickfixn, or the in-process simulator); sequence numbers (34) are the
transport's job, this layer does not manage them.
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

SOH = "\x01"


class FixParseError(ValueError):
    """A frame failed FIX structural validation."""


# ---------------------------------------------------------------------------
# Tag numbers (FIX 4.4). Only what the gateway skeleton actually uses.
# ---------------------------------------------------------------------------
BEGIN_STRING = 8
BODY_LENGTH = 9
CHECK_SUM = 10
MSG_SEQ_NUM = 34
SENDING_TIME = 52
ORIG_SENDING_TIME = 122
ENCRYPT_METHOD = 98
HEARTBEAT_INTERVAL = 108
TEST_REQ_ID = 112
MSG_TYPE = 35
SENDER_COMP_ID = 49
TARGET_COMP_ID = 56
ACCOUNT = 1
CL_ORD_ID = 11
ORIG_CL_ORD_ID = 41
ORDER_ID = 37
EXEC_ID = 17
EXEC_TYPE = 150
ORD_STATUS = 39
ORD_REJ_REASON = 103
CXL_REJ_REASON = 102
TEXT = 58
SYMBOL = 55
SIDE = 54
ORDER_QTY = 38
ORD_TYPE = 40
PRICE = 44
STOP_PX = 99
TIME_IN_FORCE = 59
EXPIRE_TIME = 126
TRANSACT_TIME = 60
LEAVES_QTY = 151
CUM_QTY = 14
AVG_PX = 6
MD_REQ_ID = 262
MD_ENTRY_TYPE = 269
MD_ENTRY_PX = 270
MD_ENTRY_SIZE = 271
SUBSCRIPTION_REQUEST_TYPE = 263
MARKET_DEPTH = 264
NO_RELATED_SYM = 146
NO_MD_ENTRY_TYPES = 267
NO_MD_ENTRIES = 268

# MsgType(35) values
MSG_HEARTBEAT = "0"
MSG_TEST_REQUEST = "1"
MSG_RESEND_REQUEST = "2"
MSG_REJECT = "3"
MSG_SEQUENCE_RESET = "4"
MSG_LOGOUT = "5"
MSG_EXECUTION_REPORT = "8"
MSG_ORDER_CANCEL_REJECT = "9"
MSG_LOGON = "A"
MSG_NEW_ORDER_SINGLE = "D"
MSG_ORDER_CANCEL_REQUEST = "F"
MSG_MARKET_DATA_REQUEST = "V"
MSG_MARKET_DATA_SNAPSHOT = "W"

# Side(54): 1=Buy, 2=Sell
SIDE_BUY = "1"
SIDE_SELL = "2"

# OrdType(40): 1=Market, 2=Limit, 3=Stop, 4=Stop-Limit
ORD_TYPE_MARKET = "1"
ORD_TYPE_LIMIT = "2"
ORD_TYPE_STOP = "3"
ORD_TYPE_STOP_LIMIT = "4"

# OrdStatus(39) / ExecType(150)
ORD_STATUS_NEW = "0"
ORD_STATUS_PARTIALLY_FILLED = "1"
ORD_STATUS_FILLED = "2"
ORD_STATUS_CANCELED = "4"
ORD_STATUS_REPLACED = "5"
ORD_STATUS_PENDING_CANCEL = "6"
ORD_STATUS_REJECTED = "8"

TERMINAL_REJECT_STATUSES = frozenset({ORD_STATUS_CANCELED, ORD_STATUS_REJECTED})


def fix_timestamp(dt: Optional[datetime] = None) -> str:
    """UTCTimestamp: YYYYMMDD-HH:MM:SS.sss"""
    dt = dt or datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y%m%d-%H:%M:%S.") + f"{dt.microsecond // 1000:03d}"


class FixMessage:
    """An ordered list of (tag, value) fields plus the FIX envelope."""

    __slots__ = ("begin_string", "fields")

    def __init__(
        self,
        msg_type: Optional[str] = None,
        fields: Optional[Iterable[Tuple[int, Any]]] = None,
        begin_string: str = "FIX.4.4",
    ) -> None:
        self.begin_string = begin_string
        self.fields: List[Tuple[int, str]] = []
        if msg_type is not None:
            self.set(MSG_TYPE, msg_type)
        for tag, value in fields or ():
            self.fields.append((int(tag), self._norm(value)))

    @staticmethod
    def _norm(value: Any) -> str:
        if isinstance(value, Decimal):
            # never scientific notation on the wire
            return format(value, "f")
        if isinstance(value, bool):
            return "Y" if value else "N"
        if isinstance(value, float):
            return repr(value)
        return str(value)

    # --- field access ------------------------------------------------------

    def set(self, tag: int, value: Any) -> "FixMessage":
        self.fields.append((int(tag), self._norm(value)))
        return self

    def replace(self, tag: int, value: Any) -> "FixMessage":
        """Set a single-valued tag, removing any previous occurrence(s)."""
        tag = int(tag)
        self.fields = [(t, v) for t, v in self.fields if t != tag]
        return self.set(tag, value)

    def get(self, tag: int, default: Optional[str] = None) -> Optional[str]:
        for t, v in self.fields:
            if t == tag:
                return v
        return default

    def values(self, tag: int) -> List[str]:
        return [v for t, v in self.fields if t == tag]

    def __getitem__(self, tag: int) -> Optional[str]:
        return self.get(tag)

    def __contains__(self, tag: int) -> bool:
        return any(t == tag for t, _ in self.fields)

    # --- envelope ----------------------------------------------------------

    def encode(self) -> str:
        """Full wire form: 8=..SOH 9=len SOH <body> SOH 10=cs SOH."""
        body = "".join(f"{t}={v}{SOH}" for t, v in self.fields if t not in (BEGIN_STRING, BODY_LENGTH, CHECK_SUM))
        head = f"{BEGIN_STRING}={self.begin_string}{SOH}{BODY_LENGTH}={len(body)}{SOH}"
        checksum = sum((head + body).encode("utf-8")) % 256
        return f"{head}{body}{CHECK_SUM}={checksum:03d}{SOH}"

    def to_bytes(self) -> bytes:
        return self.encode().encode("utf-8")

    @classmethod
    def parse(cls, data: Union[str, bytes, bytearray], *, verify: bool = True) -> "FixMessage":
        if isinstance(data, (bytes, bytearray)):
            data = data.decode("utf-8")
        data = data.replace("\x02", SOH)  # tolerate ^B escaped SOH
        parts = [p for p in data.split(SOH) if p]
        if len(parts) < 4:
            raise FixParseError(f"frame too short to be FIX: {data!r}")
        kv: List[Tuple[int, str]] = []
        for part in parts:
            if "=" not in part:
                raise FixParseError(f"malformed field {part!r}")
            tag_s, _, value = part.partition("=")
            try:
                kv.append((int(tag_s), value))
            except ValueError:
                raise FixParseError(f"non-numeric tag {tag_s!r}") from None
        if kv[0][0] != BEGIN_STRING:
            raise FixParseError(f"frame does not start with BeginString(8): {kv[0]}")
        msg = cls(begin_string=kv[0][1])
        msg.fields = [(t, v) for t, v in kv if t not in (BEGIN_STRING, BODY_LENGTH, CHECK_SUM)]
        if verify:
            msg._verify_envelope(parts)
        return msg

    def _verify_envelope(self, parts: List[str]) -> None:
        lengths = {int(t.partition("=")[0]): t.partition("=")[2] for t in parts[:2]}
        body_len = lengths.get(BODY_LENGTH)
        if body_len is None:
            raise FixParseError("missing BodyLength(9)")
        body = SOH.join(parts[2:-1]) + SOH if len(parts) > 3 else ""
        if len(body.encode("utf-8")) != int(body_len):
            raise FixParseError(f"BodyLength(9)={body_len} but body is {len(body.encode('utf-8'))} bytes")
        last_tag, _, last_val = parts[-1].partition("=")
        if int(last_tag) != CHECK_SUM:
            raise FixParseError("frame does not end with CheckSum(10)")
        expected = sum((SOH.join(parts[:-1]) + SOH).encode("utf-8")) % 256
        if f"{expected:03d}" != last_val:
            raise FixParseError(f"CheckSum(10)={last_val} but computed {expected:03d}")

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"FixMessage(35={self.get(MSG_TYPE)!r}, {self.encode()!r})"


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------

def _envelope(msg: FixMessage, sender: str, target: str) -> FixMessage:
    """Canonical header order: MsgType(35), SenderCompID(49), TargetCompID(56),
    SendingTime(52), then the body fields in the order they were set."""
    header = [
        (MSG_TYPE, msg.get(MSG_TYPE) or ""),
        (SENDER_COMP_ID, sender),
        (TARGET_COMP_ID, target),
        (SENDING_TIME, fix_timestamp()),
    ]
    body = [(t, v) for t, v in msg.fields if t != MSG_TYPE]
    msg.fields = header + body
    return msg


def logon(sender: str, target: str, heartbeat_interval: int = 30) -> FixMessage:
    msg = FixMessage(MSG_LOGON)
    msg.set(ENCRYPT_METHOD, 0).set(HEARTBEAT_INTERVAL, heartbeat_interval)
    return _envelope(msg, sender, target)


def heartbeat(sender: str, target: str, test_req_id: Optional[str] = None) -> FixMessage:
    msg = FixMessage(MSG_HEARTBEAT)
    if test_req_id is not None:
        msg.set(TEST_REQ_ID, test_req_id)
    return _envelope(msg, sender, target)


def logout(sender: str, target: str, text: Optional[str] = None) -> FixMessage:
    msg = FixMessage(MSG_LOGOUT)
    if text:
        msg.set(TEXT, text)
    return _envelope(msg, sender, target)


def new_order_single(
    *,
    sender: str,
    target: str,
    cl_ord_id: str,
    symbol: str,
    side: str,
    order_qty: Union[Decimal, str],
    ord_type: str,
    price: Optional[Union[Decimal, str]] = None,
    stop_px: Optional[Union[Decimal, str]] = None,
    account: Optional[str] = None,
    time_in_force: Optional[str] = None,
    expire_time: Optional[datetime] = None,
    transact_time: Optional[datetime] = None,
) -> FixMessage:
    msg = FixMessage(MSG_NEW_ORDER_SINGLE)
    msg.set(CL_ORD_ID, cl_ord_id)
    if account:
        msg.set(ACCOUNT, account)
    msg.set(SYMBOL, symbol).set(SIDE, side)
    msg.set(TRANSACT_TIME, fix_timestamp(transact_time))
    msg.set(ORDER_QTY, order_qty).set(ORD_TYPE, ord_type)
    if price is not None:
        msg.set(PRICE, price)
    if stop_px is not None:
        msg.set(STOP_PX, stop_px)
    if time_in_force:
        msg.set(TIME_IN_FORCE, time_in_force)
    if expire_time is not None:
        msg.set(EXPIRE_TIME, fix_timestamp(expire_time))
    return _envelope(msg, sender, target)


def order_cancel_request(
    *,
    sender: str,
    target: str,
    cl_ord_id: str,
    orig_cl_ord_id: str,
    symbol: str,
    side: str,
    order_qty: Union[Decimal, str] = Decimal("0"),
    transact_time: Optional[datetime] = None,
) -> FixMessage:
    msg = FixMessage(MSG_ORDER_CANCEL_REQUEST)
    msg.set(ORIG_CL_ORD_ID, orig_cl_ord_id).set(CL_ORD_ID, cl_ord_id)
    msg.set(SYMBOL, symbol).set(SIDE, side)
    msg.set(TRANSACT_TIME, fix_timestamp(transact_time))
    msg.set(ORDER_QTY, order_qty)
    return _envelope(msg, sender, target)


def market_data_request(
    *,
    sender: str,
    target: str,
    md_req_id: str,
    symbol: str,
    depth: int = 0,
    subscription_type: str = "1",
) -> FixMessage:
    """Snapshot request (263='1') for full depth (264=0), bid+ask entry types."""
    msg = FixMessage(MSG_MARKET_DATA_REQUEST)
    msg.set(MD_REQ_ID, md_req_id)
    msg.set(SUBSCRIPTION_REQUEST_TYPE, subscription_type)
    msg.set(MARKET_DEPTH, depth)
    msg.set(NO_RELATED_SYM, 1).set(SYMBOL, symbol)
    msg.set(NO_MD_ENTRY_TYPES, 2).set(MD_ENTRY_TYPE, "0").set(MD_ENTRY_TYPE, "1")
    return _envelope(msg, sender, target)


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def parse_execution_report(msg: FixMessage) -> Dict[str, Any]:
    """Normalise an ExecutionReport(35=8) into plain keys (values stay strings,
    so no float contamination reaches the domain)."""
    return {
        "cl_ord_id": msg.get(CL_ORD_ID),
        "orig_cl_ord_id": msg.get(ORIG_CL_ORD_ID),
        "order_id": msg.get(ORDER_ID),
        "exec_id": msg.get(EXEC_ID),
        "exec_type": msg.get(EXEC_TYPE),
        "ord_status": msg.get(ORD_STATUS),
        "symbol": msg.get(SYMBOL),
        "side": msg.get(SIDE),
        "order_qty": msg.get(ORDER_QTY),
        "leaves_qty": msg.get(LEAVES_QTY),
        "cum_qty": msg.get(CUM_QTY),
        "avg_px": msg.get(AVG_PX),
        "text": msg.get(TEXT),
        "transact_time": msg.get(TRANSACT_TIME),
        "account": msg.get(ACCOUNT),
    }


def parse_md_snapshot(msg: FixMessage) -> Dict[str, Any]:
    """Parse MarketDataSnapshotFullRefresh(35=W), walking the repeating group
    in wire order: each MD_ENTRY_TYPE(269) starts a new entry."""
    entries: List[Dict[str, Optional[str]]] = []
    current: Optional[Dict[str, Optional[str]]] = None
    for tag, value in msg.fields:
        if tag == MD_ENTRY_TYPE:
            current = {"type": value, "px": None, "size": None}
            entries.append(current)
        elif tag == MD_ENTRY_PX and current is not None:
            current["px"] = value
        elif tag == MD_ENTRY_SIZE and current is not None:
            current["size"] = value
    bid = next((e["px"] for e in entries if e["type"] == "0" and e["px"]), None)
    ask = next((e["px"] for e in entries if e["type"] == "1" and e["px"]), None)
    return {
        "md_req_id": msg.get(MD_REQ_ID),
        "symbol": msg.get(SYMBOL),
        "entries": entries,
        "bid": bid,
        "ask": ask,
    }


__all__ = [
    "SOH", "FixMessage", "FixParseError", "fix_timestamp",
    "logon", "heartbeat", "logout",
    "new_order_single", "order_cancel_request", "market_data_request",
    "parse_execution_report", "parse_md_snapshot",
]
