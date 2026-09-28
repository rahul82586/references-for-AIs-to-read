"""M8: the MT5 routing table — decode, evaluate, round-trip.

The live export's two rules are the fixtures: `dealer` (ACTION_DEALER for
real\\real and real\\real-A, gateway dealer, skip-if-none-online) and
`Auto Execution` (ACTION_CONFIRM_CLIENT for every group). Their exact shapes
pin the semantics: OR within one condition type, top-down first match,
non-terminal delay/clear.
"""
import json
import os
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from core.domains.execution.routing_mt5 import (
    ConditionRule,
    Mt5RouteCondition,
    Mt5RouteDealer,
    Mt5RouteRule,
    RouteAction,
    RouteCondition,
    RouteRequest,
    RoutingEngine,
    RoutingRequestContext,
    order_type_bit,
)

FIXTURES = os.environ.get("BROKER_MT5_FIXTURES", "")
requires_fixtures = pytest.mark.skipif(
    not FIXTURES or not os.path.isdir(FIXTURES),
    reason="MT5 export fixtures not found; set BROKER_MT5_FIXTURES",
)

NOON_THURSDAY = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)  # Thu -> MT5 day 4


class _OT:
    def __init__(self, name):
        self.name = name


def ctx(**over):
    base = dict(
        request_flags=int(RouteRequest.MARKET), order_type=_OT("BUY"),
        group="demo\\Standard", symbol="EURUSD", volume=Decimal("0.10"),
        bid=Decimal("1.10000"), ask=Decimal("1.10010"), point=Decimal("0.00001"),
        now=NOON_THURSDAY, comment="", login=123, balance=Decimal("10000"),
    )
    base.update(over)
    return RoutingRequestContext(**base)


def rule(name="r", action=RouteAction.REJECT, conditions=(), position=0, mode=1,
         request_mask=int(RouteRequest.ALL), type_mask=255, dealers=(),
         action_value_int=0, action_value_string=""):
    return Mt5RouteRule(
        name=name, mode=mode, request_mask=request_mask, type_mask=type_mask,
        flags=0, action=int(action), action_value_int=action_value_int,
        action_value_uint=0, action_value_float=Decimal("0"),
        action_value_string=action_value_string,
        conditions=tuple(conditions), dealers=tuple(dealers), position=position,
    )


def group_cond(value, code=RouteCondition.GROUP, rule_op=ConditionRule.EQ):
    return Mt5RouteCondition(code=int(code), rule=int(rule_op), value_string=value)


# --- decode ---------------------------------------------------------------------

def test_from_wire_decodes_the_live_dealer_rule():
    rec = {
        "Name": "dealer", "Mode": "1", "Request": "33554431", "Type": "255", "Flags": "0",
        "Action": "1001", "ActionValueInt": "1", "ActionValueUInt": "0",
        "ActionValueFloat": "0.00", "ActionValueString": "",
        "Conditions": [
            {"Condition": "1001", "Rule": "0", "ValueInt": "0", "ValueUInt": "0",
             "ValueFloat": "0.00", "ValueString": "real\\real"},
            {"Condition": "1001", "Rule": "0", "ValueInt": "0", "ValueUInt": "0",
             "ValueFloat": "0.00", "ValueString": "real\\real-A"},
        ],
        "Dealers": [{"Login": "3", "Name": "MetaTrader 5 Gateway clone"}],
    }
    r = Mt5RouteRule.from_wire(rec, position=0)
    assert r.action == int(RouteAction.DEALER)
    assert r.request_mask == int(RouteRequest.ALL)
    assert r.action_value_int == 1  # skip if no dealers online
    assert [c.value_string for c in r.conditions] == ["real\\real", "real\\real-A"]
    assert r.dealers[0].name == "MetaTrader 5 Gateway clone"
    assert r.enabled


# --- evaluation semantics --------------------------------------------------------

def test_first_match_wins_top_down():
    engine = RoutingEngine()
    rules = [
        rule("first", RouteAction.REJECT, [group_cond("demo*")], position=0,
             action_value_string="nope"),
        rule("second", RouteAction.DEALER, [group_cond("demo*")], position=1),
    ]
    d = engine.evaluate(ctx(), rules)
    assert d.matched_rule == "first" and d.action is RouteAction.REJECT


def test_conditions_or_within_a_type_and_across_types():
    engine = RoutingEngine()
    # OR within: either group matches
    r = rule("two-groups", RouteAction.REJECT,
             [group_cond("real\\real"), group_cond("real\\real-A")])
    assert engine.evaluate(ctx(group="real\\real-A"), [r]).matched_rule == "two-groups"
    # AND across: group matches but symbol does not -> no match
    r2 = rule("and", RouteAction.REJECT,
              [group_cond("demo*"), Mt5RouteCondition(code=int(RouteCondition.SYMBOL),
                                                      value_string="XAUUSD")])
    assert engine.evaluate(ctx(), [r2]).matched_rule is None


def test_disabled_rule_is_skipped():
    d = RoutingEngine().evaluate(ctx(), [rule(mode=0)])
    assert d.action is None


def test_request_and_type_masks_filter():
    engine = RoutingEngine()
    pending_only = rule("pend", request_mask=int(RouteRequest.PENDING))
    assert engine.evaluate(ctx(), [pending_only]).action is None          # market order
    assert engine.evaluate(
        ctx(request_flags=int(RouteRequest.PENDING)), [pending_only]).action is RouteAction.REJECT
    sell_only = rule("sells", type_mask=1 << order_type_bit(_OT("SELL")))
    assert engine.evaluate(ctx(), [sell_only]).action is None             # BUY
    assert engine.evaluate(ctx(order_type=_OT("SELL")), [sell_only]).action is RouteAction.REJECT


def test_delay_accumulates_and_continues_down_the_table():
    engine = RoutingEngine()
    rules = [
        rule("d1", RouteAction.DELAY_TIME, [group_cond("*")], position=0, action_value_int=100),
        rule("d2", RouteAction.DELAY_TIME, [group_cond("*")], position=1, action_value_int=50),
        rule("end", RouteAction.CONFIRM_MARKET, [group_cond("*")], position=2),
    ]
    d = engine.evaluate(ctx(), rules)
    assert d.delay_ms == 150
    assert d.action is RouteAction.CONFIRM_MARKET and d.matched_rule == "end"


def test_delay_ticks_are_capped_at_60():
    d = RoutingEngine().evaluate(
        ctx(), [rule("t", RouteAction.DELAY_TICK, action_value_int=500)])
    assert d.delay_ticks == 60


def test_clear_actions_are_non_terminal_transforms():
    engine = RoutingEngine()
    rules = [
        rule("strip", RouteAction.CLEAR_SLTP, [group_cond("*")], position=0),
        rule("then", RouteAction.DEALER, [group_cond("*")], position=1,
             dealers=(Mt5RouteDealer(9, "Desk"),)),
    ]
    d = engine.evaluate(ctx(), rules)
    assert d.clear_sl and d.clear_tp
    assert d.action is RouteAction.DEALER and d.matched_rule == "then"


def test_reject_reason_is_truncated_to_31_chars():
    d = RoutingEngine().evaluate(
        ctx(), [rule(action_value_string="x" * 100)])
    assert d.action is RouteAction.REJECT and len(d.reject_reason) == 31


def test_dealer_skip_flag_is_carried():
    d = RoutingEngine().evaluate(
        ctx(), [rule("dlr", RouteAction.DEALER, action_value_int=1,
                     dealers=(Mt5RouteDealer(3, "GW"),))])
    assert d.skip_if_no_dealers_online and d.dealers[0].name == "GW"


def test_market_deviation_uses_the_guides_formula():
    """Buy: (ask - request)/point; Sell: (request - bid)/point."""
    engine = RoutingEngine()
    cond = Mt5RouteCondition(code=int(RouteCondition.MARKET_DEVIATION),
                             rule=int(ConditionRule.NOT_LESS), value_float=Decimal("5"))
    r = rule("dev", RouteAction.REJECT, [cond])
    # request 5 points below the ask -> deviation +5 -> matches >= 5
    assert engine.evaluate(ctx(price=Decimal("1.10005")), [r]).matched_rule == "dev"
    # request at the ask -> deviation 0 -> no match
    assert engine.evaluate(ctx(price=Decimal("1.10010")), [r]).matched_rule is None


def test_weekday_is_a_bitmask_over_mt5_days():
    engine = RoutingEngine()
    thursday_bit = 1 << 4  # MT5: 0=Sunday (wire-verified in M6)
    r = rule("thu", RouteAction.REJECT,
             [Mt5RouteCondition(code=int(RouteCondition.WEEKDAY), value_int=thursday_bit)])
    assert engine.evaluate(ctx(now=NOON_THURSDAY), [r]).matched_rule == "thu"
    friday = datetime(2026, 9, 11, 12, 0, tzinfo=timezone.utc)
    assert engine.evaluate(ctx(now=friday), [r]).matched_rule is None


def test_comment_operators_follow_the_guide():
    engine = RoutingEngine()
    def comment_rule(rule_op, value):
        return rule("c", RouteAction.REJECT, [Mt5RouteCondition(
            code=int(RouteCondition.COMMENT), rule=int(rule_op), value_string=value)])
    # '=' exact
    assert engine.evaluate(ctx(comment="scalper"), [comment_rule(ConditionRule.EQ, "scalper")]).terminal
    assert not engine.evaluate(ctx(comment="scalper ea"), [comment_rule(ConditionRule.EQ, "scalper")]).terminal
    # '>=' : the RULE's string is searched INSIDE the comment
    assert engine.evaluate(ctx(comment="my scalper bot"), [comment_rule(ConditionRule.NOT_LESS, "scalper")]).terminal
    # '<=' : the COMMENT is searched inside the rule's string
    assert engine.evaluate(ctx(comment="scalp"), [comment_rule(ConditionRule.NOT_GREATER, "scalper-bot")]).terminal


def test_numeric_conditions_compare_with_their_operator():
    engine = RoutingEngine()
    big = rule("big", RouteAction.REJECT, [Mt5RouteCondition(
        code=int(RouteCondition.VOLUME), rule=int(ConditionRule.NOT_LESS),
        value_float=Decimal("1.0"))])
    assert engine.evaluate(ctx(volume=Decimal("1.0")), [big]).terminal
    assert not engine.evaluate(ctx(volume=Decimal("0.5")), [big]).terminal
    balance = rule("poor", RouteAction.REJECT, [Mt5RouteCondition(
        code=int(RouteCondition.BALANCE), rule=int(ConditionRule.LESS),
        value_float=Decimal("500"))])
    assert not engine.evaluate(ctx(balance=Decimal("10000")), [balance]).terminal


def test_unsupported_condition_skips_the_rule_with_a_warning():
    engine = RoutingEngine()
    r = rule("geo", RouteAction.REJECT, [Mt5RouteCondition(
        code=int(RouteCondition.COUNTRY), value_string="US")])
    d = engine.evaluate(ctx(), [r])
    assert d.action is None
    assert any("not implemented" in w for w in d.warnings)


def test_missing_context_never_matches_money_conditions():
    engine = RoutingEngine()
    r = rule("eq", RouteAction.REJECT, [Mt5RouteCondition(
        code=int(RouteCondition.EQUITY), rule=int(ConditionRule.EQ),
        value_float=Decimal("0"))])
    assert engine.evaluate(ctx(equity=None), [r]).action is None


# --- round-trip fidelity (fixtures) ------------------------------------------------

@requires_fixtures
def test_live_routing_records_round_trip_byte_identically():
    from infrastructure.mt5 import fieldmap, wire
    from infrastructure.mt5.codec import domain_to_record, record_to_domain

    payload = wire.decode_file(os.path.join(FIXTURES, "Routing TCTrader-Live.json"))
    records = wire.records(payload, "ConfigRouting")
    assert len(records) == 2
    for rec in records:
        dom = record_to_domain(rec, fieldmap.ROUTING_FIELDS)
        back = domain_to_record(dom, fieldmap.ROUTING_FIELDS)
        assert back == rec, f"{rec.get('Name')} did not round-trip"


@requires_fixtures
def test_live_table_replays_the_brokers_intent():
    """demo flow auto-executes; the two real groups go to the gateway dealer."""
    from infrastructure.config.loader import routes_from_mt5

    loaded = routes_from_mt5(os.path.join(FIXTURES, "Routing TCTrader-Live.json"))
    rules = [r for r, _ in loaded]
    engine = RoutingEngine()

    demo = engine.evaluate(ctx(group="demo\\Standard"), rules)
    assert demo.action is RouteAction.CONFIRM_CLIENT and demo.matched_rule == "Auto Execution"

    for real in ("real\\real", "real\\real-A"):
        d = engine.evaluate(ctx(group=real), rules)
        assert d.action is RouteAction.DEALER and d.matched_rule == "dealer"
        assert d.skip_if_no_dealers_online
        assert d.dealers[0].name == "MetaTrader 5 Gateway clone"

    other = engine.evaluate(ctx(group="preliminary"), rules)
    assert other.action is RouteAction.CONFIRM_CLIENT  # the '*' catch-all
