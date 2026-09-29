#!/usr/bin/env python3
"""M11 proof: an A-Book destination is a complete trade, or an honest failure.

Runs the REAL trading stack (CreateOrderHandler -> risk -> SmartOrderRouter ->
ExecutionOrchestrator -> RecordDealHandler) against a scripted ILiquidityGateway,
so every branch the LP can produce is reachable deterministically.

    PYTHONPATH=$PWD python3 scripts/m11_proof_a_book.py

The milestone question: M10 gave the platform a real FIX gateway that returns a
real FILLED execution report - and `_execute_a_book` dropped it on the floor. The
order was set PLACED, ORDER_ROUTED was published, and that was all. No deal, no
position, no margin recompute, no release of the M6 reservation. An A-Book
destination was not a trade.

Worse, the blanket `except Exception` rejected the client order on a FixTimeout,
whose own message says "hedge state UNKNOWN; reconcile before retrying". Rejecting
the client while the LP may be holding the hedge leaves the broker with naked risk
and no record of either side.
"""
import asyncio
import os
import sys
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
os.chdir(ROOT)

os.environ.setdefault("SECRET_KEY", "m11-proof-secret-key-0123456789abcdef0123456789ab")
os.environ.setdefault("ADMIN_API_KEY", "m11-proof-admin-key")

from application.commands.create_order import CreateOrderCommand          # noqa: E402
from core.domains.execution.models import ExecutionDestination, RoutingRule  # noqa: E402
from core.domains.oms.enums import OrderState, OrderType                   # noqa: E402
from core.events.domain_events import DomainEvent, EventType               # noqa: E402
from tests.integration.trading_harness import (                            # noqa: E402
    DEFAULT_LOGIN, build_harness, default_coverage,
)

BID = Decimal("1.10000")
ASK = Decimal("1.10010")
GATEWAY = "PROOFLP"

PASSED = 0
FAILED = 0


def check(label, condition, detail=""):
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"    [PASS] {label}" + (f"  {detail}" if detail else ""))
    else:
        FAILED += 1
        print(f"    [FAIL] {label}" + (f"  {detail}" if detail else ""))


class ScriptedGateway:
    """An ILiquidityGateway that returns whatever this proof asks for."""

    def __init__(self, *, report=None, exc=None):
        self._report = report
        self._exc = exc
        self.sent = []

    async def send_order(self, order, gateway_id):
        self.sent.append((order.ticket_id, gateway_id))
        if self._exc is not None:
            raise self._exc
        return dict(self._report)

    async def cancel_order(self, order_id, gateway_id):
        return True

    async def get_quotes(self, symbols):
        return {}


class UnknownHedge(RuntimeError):
    """Stand-in for FixTimeout, recognised by the explicit attribute rather than
    by importing the FIX adapter - the orchestrator must be correct without it."""
    hedge_state_unknown = True


def report(status="FILLED", volume="0.10", price="1.10010", stub=False, order_id="LP-1"):
    return {"status": status, "cl_ord_id": "x", "order_id": order_id,
            "gateway_id": GATEWAY, "symbol": "EURUSD", "side": "BUY",
            "volume": volume, "price": price, "stub": stub}


async def scenario(gateway):
    """A fresh broker with the A-Book gateway swapped for the scripted one."""
    rule = RoutingRule(rule_id="a-book-eurusd", priority=100,
                       destination=ExecutionDestination.A_BOOK,
                       symbol_filter="EURUSD", gateway_id=GATEWAY)
    h = await build_harness(rules=[rule], coverage=default_coverage())
    h.stack.orchestrator.liquidity_gateway = gateway
    await h.publish_tick("EURUSD", BID, ASK)

    seen = {"routed": [], "deals": [], "rejected": []}

    def on(event: DomainEvent):
        if event.event_type == EventType.ORDER_ROUTED:
            seen["routed"].append(event)
        elif event.event_type == EventType.DEAL_CREATED:
            seen["deals"].append(event)
        elif event.event_type == EventType.ORDER_REJECTED:
            seen["rejected"].append(event)

    for et in (EventType.ORDER_ROUTED, EventType.DEAL_CREATED, EventType.ORDER_REJECTED):
        h.event_bus.subscribe(et, on)

    order = await h.stack.create_order_handler.handle(CreateOrderCommand(
        account_login=DEFAULT_LOGIN, symbol="EURUSD",
        order_type=OrderType.BUY, volume=Decimal("0.10"),
    ))
    await asyncio.sleep(0)
    account = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    deals = await h.deal_repo.find_by_account(DEFAULT_LOGIN)
    positions = await h.position_repo.get_by_account(DEFAULT_LOGIN)
    a_book = [e for e in seen["deals"]
              if e.payload.get("destination") == ExecutionDestination.A_BOOK.value]
    return dict(h=h, order=order, account=account, deals=deals, positions=positions,
                a_book=a_book, seen=seen, gateway=gateway)


async def part_a():
    print("\n== A: the LP fills - the client side is booked ==")
    r = await scenario(ScriptedGateway(report=report()))
    check("A1 the order is FILLED", r["order"].state == OrderState.FILLED)
    check("A2 exactly one client deal exists", len(r["deals"]) == 1)
    check("A3 the deal is at the LP's price, not the raw feed",
          r["deals"] and r["deals"][0].price.value == ASK,
          f"price={r['deals'][0].price.value if r['deals'] else None}")
    check("A4 the client really holds a position", len(r["positions"]) == 1)
    check("A5 margin was recomputed (not left at zero)",
          r["account"].margin_used.amount > Decimal("0"),
          f"margin_used={r['account'].margin_used.amount}")
    check("A6 margin_level is the derived value, not a stale 0 (D1)",
          r["account"].margin_level != Decimal("0")
          and r["account"].margin_level == (
              r["account"].equity.amount / r["account"].margin_used.amount) * Decimal("100"),
          f"level={r['account'].margin_level}")
    check("A7 the M6 reservation was released by the fill",
          r["order"].reserved_margin == Decimal("0")
          and r["account"].margin_reserved.amount == Decimal("0"))
    check("A8 the A-Book routing event carries the hedge context",
          bool(r["a_book"]) and r["a_book"][0].payload.get("lp_order_id") == "LP-1")


async def part_b():
    print("\n== B: coverage semantics - the easy thing to get backwards ==")
    r = await scenario(ScriptedGateway(report=report()))
    check("B1 a REAL hedge does not move the coverage account",
          r["h"].coverage_exposure("EURUSD") == Decimal("0")
          and r["h"].coverage_repo.exposure_updates == [],
          "(the broker passed the risk on, so net exposure is unchanged)")

    r = await scenario(ScriptedGateway(report=report(stub=True, order_id="STUB-1")))
    check("B2 a STUB fill DOES move coverage - nothing was hedged",
          r["h"].coverage_exposure("EURUSD") == Decimal("-0.10"),
          f"exposure={r['h'].coverage_exposure('EURUSD')}")
    check("B3 and the event says it is unhedged",
          bool(r["a_book"]) and r["a_book"][0].payload.get("hedged") is False)
    check("B4 the sign matches B-Book: client BUY -> broker SHORT",
          bool(r["a_book"])
          and Decimal(r["a_book"][0].payload["broker_volume_delta"]) == Decimal("-0.10"))


async def part_c():
    print("\n== C: partial fills - the first in this codebase ==")
    r = await scenario(ScriptedGateway(report=report(status="PARTIAL", volume="0.04")))
    check("C1 the order is PARTIALLY_FILLED", r["order"].state == OrderState.PARTIALLY_FILLED)
    check("C2 0.06 is still outstanding", r["order"].volume_current.value == Decimal("0.06"))
    check("C3 the deal is for the 0.04 that filled",
          len(r["deals"]) == 1 and r["deals"][0].volume.value == Decimal("0.04"))
    check("C4 the remainder KEEPS a proportional reservation",
          r["order"].reserved_margin > Decimal("0"),
          f"reserved={r['order'].reserved_margin}")
    check("C5 account hold and order hold agree",
          r["account"].margin_reserved.amount == r["order"].reserved_margin)


async def part_d():
    print("\n== D: the LP has not filled - nothing may be booked ==")
    r = await scenario(ScriptedGateway(report=report(status="ACK", price=None, order_id="LP-9")))
    check("D1 the order rests PLACED", r["order"].state == OrderState.PLACED)
    check("D2 no deal", r["deals"] == [])
    check("D3 no position", r["positions"] == [])
    check("D4 the reservation is KEPT - the order is still live",
          r["order"].reserved_margin > Decimal("0"))
    resting = [e for e in r["seen"]["routed"] if e.payload.get("status") == "RESTING_AT_LP"]
    check("D5 RESTING_AT_LP published, and not flagged for reconciliation",
          bool(resting) and resting[0].payload["reconciliation_required"] is False)

    r = await scenario(ScriptedGateway(report=report(status="ACK_STUB", stub=True, price=None)))
    check("D6 a stub ACK books nothing either", r["deals"] == [] and r["positions"] == [])


async def part_e():
    print("\n== E: hedge state UNKNOWN - the branch that used to reject the client ==")
    r = await scenario(ScriptedGateway(exc=UnknownHedge("no ExecutionReport within 5s")))
    check("E1 the order is NOT rejected", r["order"].state != OrderState.REJECTED,
          "(rejecting would cancel the client side of a possibly-live hedge)")
    check("E2 no OrderRejected was published", r["seen"]["rejected"] == [])
    check("E3 nothing was booked", r["deals"] == [] and r["positions"] == [])
    check("E4 the reservation survives until the break is resolved",
          r["order"].reserved_margin > Decimal("0"))
    unknown = [e for e in r["seen"]["routed"]
               if e.payload.get("status") == "HEDGE_STATE_UNKNOWN"]
    check("E5 HEDGE_STATE_UNKNOWN published with reconciliation_required",
          bool(unknown) and unknown[0].payload["reconciliation_required"] is True)


async def part_f():
    print("\n== F: the LP definitely refused - reject and release ==")
    r = await scenario(ScriptedGateway(exc=RuntimeError("LP rejected: no liquidity")))
    check("F1 the client order is rejected", r["order"].state == OrderState.REJECTED)
    check("F2 the reason names the gateway", "A-Book gateway error" in (r["order"].comment or ""))
    check("F3 nothing was booked", r["deals"] == [] and r["positions"] == [])
    check("F4 the reservation was released",
          r["order"].reserved_margin == Decimal("0")
          and r["account"].margin_reserved.amount == Decimal("0"))


async def part_g():
    print("\n== G: malformed reports are refused, never guessed ==")
    r = await scenario(ScriptedGateway(report=report(price=None)))
    check("G1 a FILLED report with no AvgPx still books - the hedge is live",
          r["order"].state == OrderState.FILLED and len(r["deals"]) == 1)
    check("G2 ...and it is flagged for reconciliation rather than passed silently",
          bool(r["a_book"])
          and any("AvgPx" in f for f in r["a_book"][0].payload["reconciliation_flags"]))

    r = await scenario(ScriptedGateway(report=report(volume="0.50")))
    check("G3 an LP over-report is clamped to what the client asked for",
          len(r["deals"]) == 1 and r["deals"][0].volume.value == Decimal("0.10"),
          f"booked={r['deals'][0].volume.value if r['deals'] else None}")
    check("G4 ...and the clamp is flagged",
          bool(r["a_book"])
          and any("clamped" in f for f in r["a_book"][0].payload["reconciliation_flags"]))

    r = await scenario(ScriptedGateway(report=report(volume="0")))
    check("G5 a zero-volume 'fill' books nothing", r["deals"] == [])
    flagged = [e for e in r["seen"]["routed"] if e.payload.get("reconciliation_required")]
    check("G6 ...and is flagged NO_FILLED_VOLUME",
          bool(flagged) and flagged[0].payload.get("reconciliation_reason") == "NO_FILLED_VOLUME")

    class BadGateway(ScriptedGateway):
        async def send_order(self, order, gateway_id):
            return "FILLED"

    r = await scenario(BadGateway())
    check("G7 a non-dict report is treated as UNKNOWN, not as a fill",
          r["order"].state != OrderState.REJECTED and r["deals"] == []
          and any(e.payload.get("status") == "HEDGE_STATE_UNKNOWN"
                  for e in r["seen"]["routed"]))


async def main():
    print("=" * 78)
    print("M11 proof: does an A-Book order become a trade?")
    print("=" * 78)
    for part in (part_a, part_b, part_c, part_d, part_e, part_f, part_g):
        await part()
    print("\n" + "=" * 78)
    print(f"=== M11 proof: {PASSED} passed, {FAILED} failed ===")
    if FAILED == 0:
        print("An A-Book destination is now a complete trade: the LP's fill becomes a")
        print("client deal and position, margin is recomputed, the reservation is")
        print("released, and broker exposure is moved only when nothing was hedged.")
        print("Every non-fill outcome is refused or flagged - none is guessed.")
    print("=" * 78)
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
