"""MT5 routing rules — the request-level policy table, decoded and evaluated.

MT5 routes EVERY trade request through a table of rules before execution
(Administrator guide, Routing → Actions and Conditions; SDK IMTConRoute /
IMTConCondition). This module is the faithful, pure-domain implementation:
the wire taxonomy (enums below carry the SDK's numeric codes), a decoder from
the ConfigRouting record shape, and an evaluator with MT5's semantics:

  * rules evaluate TOP-DOWN; the first rule whose masks and conditions match
    decides the request;
  * within one rule, conditions of the SAME type are OR-ed (the Admin UI's
    multi-select fields — the live export's `dealer` rule carries two
    CONDITION_GROUP entries, `real\\real` and `real\\real-A`, and means either);
    conditions of DIFFERENT types are AND-ed;
  * DELAY and CLEAR actions are NON-TERMINAL: "after this action is performed,
    the request execution continues in accordance with the rules located
    below" — they accumulate onto the decision and evaluation continues;
  * every other action is terminal;
  * a rule whose Mode is 0 is disabled and skipped.

Condition/action codes are the SDK's (IMTConCondition::EnRouteCondition,
IMTConRoute::EnRouteAction, EnConditionRule, EnRouteFlags). Conditions this
build cannot evaluate honestly (client geography, colour tags, daily-deal
statistics, position age, gap mode, ...) are declared UNSUPPORTED: a rule that
carries one is SKIPPED with a recorded warning — it never silently matches and
never silently rejects.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
from enum import IntEnum, IntFlag
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

__all__ = [
    "RouteRequest",
    "RouteAction",
    "RouteCondition",
    "ConditionRule",
    "Mt5RouteCondition",
    "Mt5RouteDealer",
    "Mt5RouteRule",
    "RoutingRequestContext",
    "RoutingDecision",
    "RoutingEngine",
    "order_type_bit",
]


# ---------------------------------------------------------------------------
# Taxonomy (SDK numeric values)
# ---------------------------------------------------------------------------

class RouteRequest(IntFlag):
    """IMTConRoute::EnRouteFlags — the 'Where request is' bitmask."""
    NONE = 0x00000000
    PRICE = 0x00000001
    REQUEST = 0x00000002
    INSTANT = 0x00000004
    MARKET = 0x00000008
    EXCHANGE = 0x00000010
    PENDING = 0x00000020
    SLTP = 0x00000040
    MODIFY = 0x00000080
    REMOVE = 0x00000100
    ACTIVATE = 0x00000200
    STOPLIMIT = 0x00000400
    SL = 0x00000800
    TP = 0x00001000
    STOPOUT_ORDER = 0x00002000
    STOPOUT_POSITION = 0x00004000
    EXPIRATION = 0x00008000
    DEALER_POS_EXECUTE = 0x00010000
    DEALER_ORD_PENDING = 0x00020000
    DEALER_POS_MODIFY = 0x00040000
    DEALER_ORD_MODIFY = 0x00080000
    DEALER_ORD_REMOVE = 0x00100000
    DEALER_ORD_ACTIVATE = 0x00200000
    DEALER_ORD_SLIMIT = 0x00400000
    DEALER_CLOSE_BY = 0x00800000
    CLOSE_BY = 0x01000000
    ALL = 0x01FFFFFF


class RouteAction(IntEnum):
    """IMTConRoute::EnRouteAction."""
    DELAY_TIME = 0
    DELAY_TICK = 1
    CLEAR_TP = 2
    CLEAR_SL = 3
    CLEAR_SLTP = 4
    DEALER = 1001
    DEALER_ONLINE = 1002
    REJECT = 1003
    REQUOTE = 1004
    CONFIRM_CLIENT = 1005
    CONFIRM_MARKET = 1006
    CANCEL_ORDER = 1007


#: Actions that transform the request and let evaluation continue down the table.
NON_TERMINAL_ACTIONS = frozenset({
    RouteAction.DELAY_TIME, RouteAction.DELAY_TICK,
    RouteAction.CLEAR_TP, RouteAction.CLEAR_SL, RouteAction.CLEAR_SLTP,
})


class RouteCondition(IntEnum):
    """IMTConCondition::EnRouteCondition."""
    DATETIME = 0
    SYMBOL = 1
    VOLUME = 2
    MARKET_DEVIATION = 3
    TIME = 4
    WEEKDAY = 5
    COMMENT = 6
    EXPERT = 7
    SIGNAL = 8
    DEALER_LOGIN = 9
    SOURCE_LOGIN = 10
    MARKET_DEVIATION_SPR = 11
    GAP = 12
    PRICE = 13
    VALUE = 14
    LOGIN = 1000
    GROUP = 1001
    COUNTRY = 1002
    CITY = 1003
    COLOR = 1004
    LEVERAGE = 1005
    COMMENT_CLIENT = 1006
    ZIPCODE = 1007
    STATUS = 1008
    MARGIN = 2000
    MARGIN_LEVEL = 2001
    MARGIN_FREE = 2002
    EQUITY = 2003
    BALANCE = 2004
    PROFIT = 2005
    DAILY_DEALS = 3000
    DAILY_DEALS_PERIOD = 3001
    DAILY_PROFIT = 3002
    POSITION_VOLUME = 4000
    POSITION_PROFIT = 4001
    POSITION_AGE = 4002
    POSITION_MODIFY_TIME = 4003
    POSITION_AVERAGE_TIME = 4004
    POSITION_TOTAL = 4005
    POSITION_TOTAL_SYMBOL = 4006
    ORDER_TOTAL = 4007
    ORDER_TOTAL_SYMBOL = 4008
    POSITION_SL_TOUCHED = 4009
    POSITION_TP_TOUCHED = 4010
    ORDER_SL_TOUCHED = 4011
    SYMBOL_SPREAD = 5000


class ConditionRule(IntEnum):
    """IMTConCondition::EnConditionRule — comparison operators."""
    EQ = 0
    NOT_EQ = 1
    GREATER = 2
    NOT_LESS = 3   # >=
    LESS = 4
    NOT_GREATER = 5  # <=


#: Conditions this build evaluates. Everything else is UNSUPPORTED: rules
#: carrying one are skipped with a warning rather than guessed at — a guessed
#: condition on a REJECT rule is a client turned away for the wrong reason,
#: and on a DEALER rule it is flow an operator never asked for.
SUPPORTED_CONDITIONS = frozenset({
    RouteCondition.DATETIME, RouteCondition.SYMBOL, RouteCondition.VOLUME,
    RouteCondition.MARKET_DEVIATION, RouteCondition.TIME, RouteCondition.WEEKDAY,
    RouteCondition.COMMENT, RouteCondition.EXPERT, RouteCondition.SIGNAL,
    RouteCondition.PRICE, RouteCondition.LOGIN, RouteCondition.GROUP,
    RouteCondition.LEVERAGE, RouteCondition.MARGIN, RouteCondition.MARGIN_LEVEL,
    RouteCondition.MARGIN_FREE, RouteCondition.EQUITY, RouteCondition.BALANCE,
    RouteCondition.PROFIT, RouteCondition.POSITION_TOTAL,
    RouteCondition.POSITION_TOTAL_SYMBOL, RouteCondition.ORDER_TOTAL,
    RouteCondition.ORDER_TOTAL_SYMBOL, RouteCondition.SYMBOL_SPREAD,
})


def order_type_bit(order_type: Any) -> int:
    """MT5 order-type bit index: TA_BUY=0 … TA_SELL_STOP_LIMIT=7 (Type mask 255 = all)."""
    name = getattr(order_type, "name", str(order_type)).upper()
    order = ("BUY", "SELL", "BUY_LIMIT", "SELL_LIMIT", "BUY_STOP", "SELL_STOP",
             "BUY_STOP_LIMIT", "SELL_STOP_LIMIT")
    if name in order:
        return order.index(name)
    raise ValueError(f"order type {order_type!r} has no MT5 routing bit")


# ---------------------------------------------------------------------------
# Wire shape
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Mt5RouteCondition:
    code: int
    rule: int = 0
    value_int: int = 0
    value_uint: int = 0
    value_float: Decimal = Decimal("0")
    value_string: str = ""

    @classmethod
    def from_wire(cls, rec: Dict[str, Any]) -> "Mt5RouteCondition":
        return cls(
            code=_int(rec.get("Condition")),
            rule=_int(rec.get("Rule")),
            value_int=_int(rec.get("ValueInt")),
            value_uint=_int(rec.get("ValueUInt")),
            value_float=_dec(rec.get("ValueFloat")),
            value_string=str(rec.get("ValueString") or ""),
        )


@dataclass(frozen=True)
class Mt5RouteDealer:
    login: int
    name: str

    @classmethod
    def from_wire(cls, rec: Dict[str, Any]) -> "Mt5RouteDealer":
        return cls(login=_int(rec.get("Login")), name=str(rec.get("Name") or "").strip())


@dataclass(frozen=True)
class Mt5RouteRule:
    name: str
    mode: int
    request_mask: int
    type_mask: int
    flags: int
    action: int
    action_value_int: int
    action_value_uint: int
    action_value_float: Decimal
    action_value_string: str
    conditions: Tuple[Mt5RouteCondition, ...] = ()
    dealers: Tuple[Mt5RouteDealer, ...] = ()
    #: position in the table — evaluation order. Not part of the wire record;
    #: MT5 uses the record order.
    position: int = 0

    @property
    def enabled(self) -> bool:
        return self.mode != 0

    @classmethod
    def from_wire(cls, rec: Dict[str, Any], position: int = 0) -> "Mt5RouteRule":
        return cls(
            name=str(rec.get("Name") or ""),
            mode=_int(rec.get("Mode")),
            request_mask=_int(rec.get("Request")),
            type_mask=_int(rec.get("Type")),
            flags=_int(rec.get("Flags")),
            action=_int(rec.get("Action")),
            action_value_int=_int(rec.get("ActionValueInt")),
            action_value_uint=_int(rec.get("ActionValueUInt")),
            action_value_float=_dec(rec.get("ActionValueFloat")),
            action_value_string=str(rec.get("ActionValueString") or ""),
            conditions=tuple(Mt5RouteCondition.from_wire(c) for c in (rec.get("Conditions") or [])),
            dealers=tuple(Mt5RouteDealer.from_wire(d) for d in (rec.get("Dealers") or [])),
            position=position,
        )


@dataclass
class RoutingRequestContext:
    """Everything the conditions may look at, assembled by the caller.

    Prices are the CLIENT's (M7 pricing provider) — MT5 checks request
    conditions against what the client sees. Optional fields stay None when
    the caller cannot supply them; conditions needing a missing field make the
    rule NOT match (and say so in warnings), which is the safe direction: an
    unevaluable REJECT must not fire, an unevaluable execution rule must not
    divert flow.
    """
    request_flags: int
    order_type: Any
    group: str = ""
    symbol: str = ""
    volume: Optional[Decimal] = None
    price: Optional[Decimal] = None       # the client's request price, if any
    bid: Optional[Decimal] = None          # client quote
    ask: Optional[Decimal] = None
    point: Optional[Decimal] = None
    now: Optional[datetime] = None
    comment: str = ""
    is_expert: bool = False
    is_signal: bool = False
    login: Optional[int] = None
    leverage: Optional[int] = None
    balance: Optional[Decimal] = None
    equity: Optional[Decimal] = None
    profit: Optional[Decimal] = None
    margin_used: Optional[Decimal] = None
    margin_free: Optional[Decimal] = None
    margin_level: Optional[Decimal] = None
    positions_total: Optional[int] = None
    positions_symbol: Optional[int] = None
    orders_total: Optional[int] = None
    orders_symbol: Optional[int] = None


@dataclass
class RoutingDecision:
    """The table's verdict. `action is None` = no terminal rule matched and the
    caller proceeds with its own routing (the house rules / default destination)."""
    action: Optional[RouteAction] = None
    matched_rule: Optional[str] = None
    delay_ms: int = 0
    delay_ticks: int = 0
    clear_sl: bool = False
    clear_tp: bool = False
    reject_reason: str = ""
    dealers: Tuple[Mt5RouteDealer, ...] = ()
    skip_if_no_dealers_online: bool = False
    warnings: List[str] = field(default_factory=list)

    @property
    def terminal(self) -> bool:
        return self.action is not None


# ---------------------------------------------------------------------------
# The engine
# ---------------------------------------------------------------------------

class RoutingEngine:
    """Evaluates a request against an ordered MT5 rule table. Pure and
    synchronous: no I/O, no clock of its own (the context carries `now`)."""

    def evaluate(self, ctx: RoutingRequestContext, rules: List[Mt5RouteRule]) -> RoutingDecision:
        decision = RoutingDecision()
        try:
            type_bit = 1 << order_type_bit(ctx.order_type)
        except ValueError as exc:
            decision.warnings.append(str(exc))
            return decision

        for rule in sorted(rules, key=lambda r: r.position):
            if not rule.enabled:
                continue
            if rule.request_mask and not (rule.request_mask & ctx.request_flags):
                continue
            if rule.type_mask and not (rule.type_mask & type_bit):
                continue

            matched, warning = self._conditions_match(rule, ctx)
            if warning:
                decision.warnings.append(f"rule '{rule.name}': {warning}")
            if not matched:
                continue

            try:
                action = RouteAction(rule.action)
            except ValueError:
                decision.warnings.append(
                    f"rule '{rule.name}': unknown action code {rule.action}; skipped"
                )
                continue

            if action in (RouteAction.DELAY_TIME, RouteAction.DELAY_TICK):
                if action is RouteAction.DELAY_TIME:
                    decision.delay_ms += max(0, rule.action_value_int)
                else:
                    # SDK/guide: maximum 60 ticks
                    decision.delay_ticks += min(60, max(0, rule.action_value_int))
                continue  # non-terminal: evaluation continues down the table
            if action in (RouteAction.CLEAR_SL, RouteAction.CLEAR_TP, RouteAction.CLEAR_SLTP):
                if action is not RouteAction.CLEAR_TP:
                    decision.clear_sl = True
                if action is not RouteAction.CLEAR_SL:
                    decision.clear_tp = True
                continue  # non-terminal transform

            # terminal
            decision.action = action
            decision.matched_rule = rule.name
            decision.dealers = rule.dealers
            if action is RouteAction.REJECT:
                decision.reject_reason = rule.action_value_string[:31]  # guide: max 31 chars
            if action in (RouteAction.DEALER, RouteAction.DEALER_ONLINE):
                # "skip this rule if no dealers online" = nonzero ParamInt
                decision.skip_if_no_dealers_online = rule.action_value_int != 0
            return decision

        return decision

    # -- conditions ----------------------------------------------------------

    def _conditions_match(self, rule: Mt5RouteRule, ctx: RoutingRequestContext) -> Tuple[bool, Optional[str]]:
        """OR within a condition type, AND across types. Returns (matched, warning)."""
        by_code: Dict[int, List[Mt5RouteCondition]] = {}
        for cond in rule.conditions:
            by_code.setdefault(cond.code, []).append(cond)

        for code, group in by_code.items():
            try:
                kind = RouteCondition(code)
            except ValueError:
                return False, f"unknown condition code {code}; rule skipped"
            if kind not in SUPPORTED_CONDITIONS:
                return False, (
                    f"condition {kind.name} is not implemented in this build; "
                    "rule skipped rather than guessed"
                )
            if not any(self._condition_matches(kind, c, ctx) for c in group):
                return False, None
        return True, None

    def _condition_matches(self, kind: RouteCondition, c: Mt5RouteCondition, ctx: RoutingRequestContext) -> bool:
        rule = ConditionRule(c.rule) if c.rule in ConditionRule._value2member_map_ else ConditionRule.EQ

        if kind is RouteCondition.SYMBOL:
            return _mask_matches(c.value_string, ctx.symbol, rule)
        if kind is RouteCondition.GROUP:
            return _mask_matches(c.value_string, ctx.group, rule)
        if kind is RouteCondition.LOGIN:
            return _compare(ctx.login, _int_value(c), rule)
        if kind is RouteCondition.LEVERAGE:
            return _compare(ctx.leverage, _int_value(c), rule)
        if kind is RouteCondition.VOLUME:
            return _compare(ctx.volume, _float_value(c), rule)
        if kind is RouteCondition.PRICE:
            price = ctx.price
            if price is None:  # market execution: the current price is checked
                price = ctx.ask if _is_buy(ctx.order_type) else ctx.bid
            return _compare(price, _float_value(c), rule)
        if kind is RouteCondition.MARKET_DEVIATION:
            # guide: Buy -> (ask - request), Sell -> (request - bid), in points
            if ctx.price is None or ctx.point in (None, 0) or ctx.bid is None or ctx.ask is None:
                return False
            deviation = (
                (ctx.ask - ctx.price) if _is_buy(ctx.order_type) else (ctx.price - ctx.bid)
            ) / Decimal(str(ctx.point))
            return _compare(deviation, _float_value(c), rule)
        if kind is RouteCondition.SYMBOL_SPREAD:
            if ctx.bid is None or ctx.ask is None or not ctx.point:
                return False
            spread_points = (ctx.ask - ctx.bid) / Decimal(str(ctx.point))
            return _compare(spread_points, _float_value(c), rule)
        if kind is RouteCondition.TIME:
            if ctx.now is None:
                return False
            minutes = ctx.now.hour * 60 + ctx.now.minute
            return _compare(minutes, _int_value(c), rule)
        if kind is RouteCondition.WEEKDAY:
            if ctx.now is None:
                return False
            mt5_day = (ctx.now.weekday() + 1) % 7  # 0=Sunday (wire-verified in M6)
            mask = _int_value(c)
            return bool(mask & (1 << mt5_day))
        if kind is RouteCondition.DATETIME:
            if ctx.now is None:
                return False
            return _compare(int(ctx.now.timestamp()), _int_value(c), rule)
        if kind is RouteCondition.COMMENT:
            return _comment_matches(c, ctx.comment, rule)
        if kind is RouteCondition.EXPERT:
            return ctx.is_expert if _int_value(c) != 0 else not ctx.is_expert
        if kind is RouteCondition.SIGNAL:
            return ctx.is_signal if _int_value(c) != 0 else not ctx.is_signal
        money_fields = {
            RouteCondition.MARGIN: ctx.margin_used,
            RouteCondition.MARGIN_LEVEL: ctx.margin_level,
            RouteCondition.MARGIN_FREE: ctx.margin_free,
            RouteCondition.EQUITY: ctx.equity,
            RouteCondition.BALANCE: ctx.balance,
            RouteCondition.PROFIT: ctx.profit,
        }
        if kind in money_fields:
            return _compare(money_fields[kind], _float_value(c), rule)
        count_fields = {
            RouteCondition.POSITION_TOTAL: ctx.positions_total,
            RouteCondition.POSITION_TOTAL_SYMBOL: ctx.positions_symbol,
            RouteCondition.ORDER_TOTAL: ctx.orders_total,
            RouteCondition.ORDER_TOTAL_SYMBOL: ctx.orders_symbol,
        }
        if kind in count_fields:
            return _compare(count_fields[kind], _int_value(c), rule)

        return False  # unreachable while SUPPORTED_CONDITIONS gates the call


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _is_buy(order_type: Any) -> bool:
    return "BUY" in getattr(order_type, "name", str(order_type)).upper()


def _int(value: Any) -> int:
    try:
        return int(str(value).strip() or 0)
    except (ValueError, InvalidOperation, TypeError):
        return 0


def _dec(value: Any) -> Decimal:
    try:
        return Decimal(str(value).strip() or "0")
    except (InvalidOperation, ValueError, TypeError):
        return Decimal("0")


def _int_value(c: Mt5RouteCondition) -> int:
    return c.value_uint if c.value_uint else c.value_int


def _float_value(c: Mt5RouteCondition) -> Decimal:
    if c.value_float:
        return c.value_float
    return Decimal(_int_value(c))


def _mask_matches(pattern: str, value: str, rule: ConditionRule) -> bool:
    """Symbol/group masks: '*' = everything, trailing '*' = prefix, '!' prefix
    negation is documented in the guide but not implemented (a rule using it is
    safer skipped than mis-evaluated — the caller warns via unsupported paths).
    """
    if not pattern or pattern == "*":
        hit = True
    elif pattern.startswith("!"):
        return False  # negation masks: refuse to guess (documented gap)
    elif pattern.endswith("*"):
        hit = value.startswith(pattern[:-1])
    else:
        hit = value == pattern
    if rule is ConditionRule.NOT_EQ:
        return not hit
    return hit


def _comment_matches(c: Mt5RouteCondition, comment: str, rule: ConditionRule) -> bool:
    """Guide: '=' exact; '>'/'>=' look for the RULE's string inside the comment;
    '<'/'<=' look for the COMMENT inside the rule's string."""
    wanted = c.value_string
    if rule is ConditionRule.EQ:
        return comment == wanted
    if rule in (ConditionRule.GREATER, ConditionRule.NOT_LESS):
        return wanted in comment
    if rule in (ConditionRule.LESS, ConditionRule.NOT_GREATER):
        return bool(comment) and comment in wanted
    if rule is ConditionRule.NOT_EQ:
        return comment != wanted
    return False


def _compare(actual: Any, target: Any, rule: ConditionRule) -> bool:
    if actual is None:
        return False  # unevaluable -> does not match (the safe direction)
    try:
        a = Decimal(str(actual))
        t = Decimal(str(target))
    except (InvalidOperation, ValueError, TypeError):
        return str(actual) == str(target) if rule is ConditionRule.EQ else False
    if rule is ConditionRule.EQ:
        return a == t
    if rule is ConditionRule.NOT_EQ:
        return a != t
    if rule is ConditionRule.GREATER:
        return a > t
    if rule is ConditionRule.NOT_LESS:
        return a >= t
    if rule is ConditionRule.LESS:
        return a < t
    if rule is ConditionRule.NOT_GREATER:
        return a <= t
    return False
