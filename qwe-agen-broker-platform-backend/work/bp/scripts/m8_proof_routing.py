#!/usr/bin/env python3
"""M8 PROOF — does a request flow through the routing table the way MT5 does?

Pure replay against the REAL ConfigRouting export (the broker's own two rules)
plus synthetic rules for every executable action. No server, no database: the
engine is pure, so the proof is deterministic.

    PYTHONPATH=work/bp BROKER_MT5_FIXTURES=<decoded fixtures> \
        python3 scripts/m8_proof_routing.py

Steps
  1  the live table decodes: names, actions, masks, conditions, dealers
  2  byte-identical round trip through the codec (nested Conditions/Dealers)
  3  demo flow      -> Auto Execution (CONFIRM_CLIENT): normal execution
  4  real\\real      -> dealer rule (DEALER, skip-if-offline, gateway dealer)
  5  real\\real-A    -> dealer rule (the OR-within-type evidence)
  6  other groups   -> Auto Execution via the '*' catch-all
  7  synthetic REJECT: terminal, reason truncated to 31 chars
  8  synthetic DELAY+CLEAR: non-terminal, accumulate, next rule decides
  9  unsupported condition: rule skipped with a warning, never guessed
"""
import os
import sys
from datetime import datetime, timezone
from decimal import Decimal

sys.path.insert(0, os.getcwd())

PASS = FAIL = 0


def report(ok, what, extra=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"    [PASS] {what} {extra}")
    else:
        FAIL += 1
        print(f"    [FAIL] {what} {extra}")


def main():
    fixtures = os.environ.get("BROKER_MT5_FIXTURES")
    if not fixtures or not os.path.isdir(fixtures):
        print("BROKER_MT5_FIXTURES must point at the decoded MT5 export directory")
        return 2

    from core.domains.execution.routing_mt5 import (
        ConditionRule,
        Mt5RouteCondition,
        Mt5RouteRule,
        RouteAction,
        RouteCondition,
        RouteRequest,
        RoutingEngine,
        RoutingRequestContext,
    )
    from infrastructure.config.loader import routes_from_mt5
    from infrastructure.mt5 import fieldmap, wire
    from infrastructure.mt5.codec import domain_to_record, record_to_domain

    class OT:
        name = "BUY"

    def ctx(group):
        return RoutingRequestContext(
            request_flags=int(RouteRequest.MARKET), order_type=OT(), group=group,
            symbol="EURUSD", volume=Decimal("0.10"), bid=Decimal("1.10000"),
            ask=Decimal("1.10010"), point=Decimal("0.00001"),
            now=datetime(2026, 9, 11, 12, 0, tzinfo=timezone.utc),
            login=123, balance=Decimal("10000"),
        )

    engine = RoutingEngine()
    routing_file = os.path.join(fixtures, "Routing TCTrader-Live.json")

    print("[1] the live table decodes")
    loaded = routes_from_mt5(routing_file)
    rules = [r for r, _ in loaded]
    report(len(rules) == 2, "two rules imported", f"({', '.join(r.name for r in rules)})")
    dealer = next(r for r in rules if r.name == "dealer")
    auto = next(r for r in rules if r.name == "Auto Execution")
    report(dealer.action == int(RouteAction.DEALER), "dealer rule action is DEALER(1001)")
    report(dealer.action_value_int == 1, "dealer rule skips when no dealer is online")
    report(dealer.request_mask == int(RouteRequest.ALL), "dealer rule matches every request type")
    report([c.value_string for c in dealer.conditions] == ["real\\real", "real\\real-A"],
           "dealer rule targets the two real groups")
    report(dealer.dealers[0].name == "MetaTrader 5 Gateway clone", "its dealer is the gateway")
    report(auto.action == int(RouteAction.CONFIRM_CLIENT),
           "Auto Execution confirms at the requested price (1005)")

    print("[2] byte-identical round trip through the codec")
    payload = wire.decode_file(routing_file)
    identical = 0
    for rec in wire.records(payload, "ConfigRouting"):
        dom = record_to_domain(rec, fieldmap.ROUTING_FIELDS)
        if domain_to_record(dom, fieldmap.ROUTING_FIELDS) == rec:
            identical += 1
    report(identical == 2, "both records re-export exactly", f"({identical}/2)")

    print("[3] demo flow auto-executes")
    d = engine.evaluate(ctx("demo\\Standard"), rules)
    report(d.action is RouteAction.CONFIRM_CLIENT and d.matched_rule == "Auto Execution",
           "demo\\Standard -> CONFIRM_CLIENT via Auto Execution")

    print("[4-5] the real groups go to the gateway dealer")
    for group in ("real\\real", "real\\real-A"):
        d = engine.evaluate(ctx(group), rules)
        report(
            d.action is RouteAction.DEALER and d.matched_rule == "dealer"
            and d.skip_if_no_dealers_online,
            f"{group} -> DEALER (skip-if-offline)",
        )

    print("[6] everything else lands on the catch-all")
    for group in ("preliminary", "coverage\\house", "demo\\Challenge"):
        d = engine.evaluate(ctx(group), rules)
        report(d.action is RouteAction.CONFIRM_CLIENT, f"{group} -> Auto Execution")

    print("[7] synthetic REJECT is terminal and the reason is client-sized")
    reject = Mt5RouteRule(
        name="news-blackout", mode=1, request_mask=int(RouteRequest.ALL), type_mask=255,
        flags=0, action=int(RouteAction.REJECT), action_value_int=0, action_value_uint=0,
        action_value_float=Decimal("0"), action_value_string="NFP blackout: " + "x" * 40,
        conditions=(Mt5RouteCondition(code=int(RouteCondition.GROUP), value_string="*"),),
    )
    d = engine.evaluate(ctx("demo\\Standard"), [reject])
    report(d.action is RouteAction.REJECT and len(d.reject_reason) == 31,
           "rejected with a 31-char reason", f"({d.reject_reason!r})")

    print("[8] DELAY and CLEAR accumulate, the next rule decides")
    delay = Mt5RouteRule(
        name="slow", mode=1, request_mask=int(RouteRequest.ALL), type_mask=255, flags=0,
        action=int(RouteAction.DELAY_TIME), action_value_int=250, action_value_uint=0,
        action_value_float=Decimal("0"), action_value_string="",
        conditions=(Mt5RouteCondition(code=int(RouteCondition.GROUP), value_string="*"),),
    )
    clear = Mt5RouteRule(
        name="strip", mode=1, request_mask=int(RouteRequest.ALL), type_mask=255, flags=0,
        action=int(RouteAction.CLEAR_SLTP), action_value_int=0, action_value_uint=0,
        action_value_float=Decimal("0"), action_value_string="",
        conditions=(Mt5RouteCondition(code=int(RouteCondition.GROUP), value_string="*"),),
        position=1,
    )
    d = engine.evaluate(ctx("demo\\Standard"), [delay, clear] + rules)
    report(d.delay_ms == 250 and d.clear_sl and d.clear_tp,
           "250 ms delay + SL/TP cleared", "")
    report(d.action is RouteAction.CONFIRM_CLIENT and d.matched_rule == "Auto Execution",
           "evaluation continued to the live table's verdict")

    print("[9] an unsupported condition skips its rule - never guesses")
    geo = Mt5RouteRule(
        name="geo-block", mode=1, request_mask=int(RouteRequest.ALL), type_mask=255,
        flags=0, action=int(RouteAction.REJECT), action_value_int=0, action_value_uint=0,
        action_value_float=Decimal("0"), action_value_string="blocked",
        conditions=(Mt5RouteCondition(code=int(RouteCondition.COUNTRY), value_string="US"),),
    )
    d = engine.evaluate(ctx("demo\\Standard"), [geo])
    report(d.action is None and any("not implemented" in w for w in d.warnings),
           "COUNTRY condition: rule skipped with a recorded warning")

    print(f"\n=== M8 proof: {PASS} passed, {FAIL} failed ===")
    if FAIL == 0:
        print("The broker's own routing table replays with MT5's semantics.")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
