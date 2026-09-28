"""M10: FIX 4.4 message layer - encode/parse envelope integrity, builders, and the
ExecutionReport / MarketDataSnapshot parsers the gateway consumes."""
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from infrastructure.fix import messages as fix
from infrastructure.fix.messages import FixMessage, FixParseError


def test_encode_sets_body_length_and_checksum():
    msg = fix.new_order_single(
        sender="BROKER", target="LP", cl_ord_id="T1", symbol="EURUSD",
        side=fix.SIDE_BUY, order_qty=Decimal("0.10"), ord_type=fix.ORD_TYPE_MARKET,
    )
    raw = msg.encode()
    assert raw.startswith("8=FIX.4.4\x01")
    assert raw.endswith("\x01")
    parts = [p for p in raw.split("\x01") if p]
    assert parts[-1].startswith("10=")
    body_length = int(parts[1].split("=")[1])
    body = "\x01".join(parts[2:-1]) + "\x01"
    assert len(body) == body_length
    checksum = sum(("\x01".join(parts[:-1]) + "\x01").encode()) % 256
    assert parts[-1] == f"10={checksum:03d}"


def test_parse_roundtrip_preserves_values_and_order():
    msg = fix.new_order_single(
        sender="BROKER", target="LP", cl_ord_id="CL-42", symbol="EURUSD",
        side=fix.SIDE_SELL, order_qty=Decimal("1.25"), ord_type=fix.ORD_TYPE_LIMIT,
        price=Decimal("1.10500"),
    )
    parsed = FixMessage.parse(msg.encode())
    assert parsed.get(fix.MSG_TYPE) == "D"
    assert parsed.get(fix.CL_ORD_ID) == "CL-42"
    assert parsed.get(fix.SIDE) == "2"
    assert parsed.get(fix.ORD_TYPE) == "2"
    assert parsed.get(fix.PRICE) == "1.10500"
    assert parsed.get(fix.ORDER_QTY) == "1.25"
    # header order canonical: 35, 49, 56, 52
    tags = [t for t, _ in parsed.fields]
    assert tags[:4] == [35, 49, 56, 52]


def test_parse_rejects_corrupt_checksum_and_length():
    msg = fix.logon("BROKER", "LP")
    raw = msg.encode()
    with pytest.raises(FixParseError):
        FixMessage.parse(raw[:-4] + "999\x01")  # wrong checksum
    bad_len = raw.replace("9=", "9=999", 1)
    with pytest.raises(FixParseError):
        FixMessage.parse(bad_len)
    with pytest.raises(FixParseError):
        FixMessage.parse("not a fix frame")


def test_decimal_quantities_never_use_scientific_notation():
    msg = fix.new_order_single(
        sender="B", target="L", cl_ord_id="X", symbol="BTCUSD",
        side=fix.SIDE_BUY, order_qty=Decimal("1E+2"), ord_type=fix.ORD_TYPE_MARKET,
    )
    assert "38=100\x01" in msg.encode()
    assert "1E" not in msg.encode()


def test_gtd_expiration_and_stop_limit_fields():
    exp = datetime(2026, 9, 12, 15, 30, 0, tzinfo=timezone.utc)
    msg = fix.new_order_single(
        sender="B", target="L", cl_ord_id="X2", symbol="EURUSD",
        side=fix.SIDE_BUY, order_qty=Decimal("0.5"),
        ord_type=fix.ORD_TYPE_STOP_LIMIT, price=Decimal("1.10"),
        stop_px=Decimal("1.09"), time_in_force="6", expire_time=exp,
    )
    parsed = FixMessage.parse(msg.encode())
    assert parsed.get(fix.TIME_IN_FORCE) == "6"
    assert parsed.get(fix.EXPIRE_TIME) == "20260912-15:30:00.000"
    assert parsed.get(fix.STOP_PX) == "1.09"


def test_cancel_request_carries_orig_cl_ord_id():
    msg = fix.order_cancel_request(
        sender="B", target="L", cl_ord_id="CXL-1", orig_cl_ord_id="CL-42",
        symbol="EURUSD", side=fix.SIDE_BUY,
    )
    parsed = FixMessage.parse(msg.encode())
    assert parsed.get(fix.MSG_TYPE) == "F"
    assert parsed.get(fix.ORIG_CL_ORD_ID) == "CL-42"


def test_md_request_shape():
    msg = fix.market_data_request(sender="B", target="L", md_req_id="R1", symbol="EURUSD")
    parsed = FixMessage.parse(msg.encode())
    assert parsed.get(fix.MSG_TYPE) == "V"
    assert parsed.get(fix.MD_REQ_ID) == "R1"
    assert parsed.get(fix.SUBSCRIPTION_REQUEST_TYPE) == "1"
    assert parsed.values(fix.MD_ENTRY_TYPE) == ["0", "1"]


def test_parse_execution_report():
    er = (
        FixMessage("8")
        .set(49, "LP").set(56, "BROKER").set(52, fix.fix_timestamp())
        .set(11, "CL-42").set(37, "LP-ORD-1").set(17, "EX-1")
        .set(150, "2").set(39, "2")
        .set(55, "EURUSD").set(54, "1")
        .set(38, "0.10").set(151, "0").set(14, "0.10").set(6, "1.10010")
    )
    report = fix.parse_execution_report(FixMessage.parse(er.encode()))
    assert report["cl_ord_id"] == "CL-42"
    assert report["ord_status"] == "2"
    assert report["avg_px"] == "1.10010"
    assert report["cum_qty"] == "0.10"


def test_parse_md_snapshot_walks_repeating_group_in_order():
    snap = (
        FixMessage("W")
        .set(49, "LP").set(56, "BROKER").set(52, fix.fix_timestamp())
        .set(262, "R1").set(55, "EURUSD").set(264, 0).set(268, 2)
        .set(269, "0").set(270, "1.10000").set(271, "1000000")
        .set(269, "1").set(270, "1.10010").set(271, "2000000")
    )
    parsed = fix.parse_md_snapshot(FixMessage.parse(snap.encode()))
    assert parsed["symbol"] == "EURUSD"
    assert parsed["bid"] == "1.10000"
    assert parsed["ask"] == "1.10010"
    assert len(parsed["entries"]) == 2
    assert parsed["entries"][1] == {"type": "1", "px": "1.10010", "size": "2000000"}
