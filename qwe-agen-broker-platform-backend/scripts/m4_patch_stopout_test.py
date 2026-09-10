import io

p = "tests/integration/test_order_execution_e2e.py"
s = io.open(p, encoding="utf-8").read()

start = s.index('async def test_stop_out_liquidates_the_worst_loss_first_and_books_it():')
end = s.index('# ===========================================================================\n# 9. Wiring honesty')

new = '''async def test_stop_out_liquidates_the_worst_loss_first_and_books_it():
    """Tick -> PnL -> equity -> margin call -> stop out -> LiquidationWorker -> close.

    Two long positions opened a tenth of a cent apart, so they carry almost - but not
    quite - the same loss, and "worst first" is a real decision rather than a coin toss.

    The numbers are worked by hand, because the shape of a stop-out is counter-intuitive:
    closing a position does NOT improve equity (the unrealised loss becomes a realised
    one and moves onto the balance). What improves is the DENOMINATOR - the margin the
    remaining positions need. So recovery is about how much margin is released, and the
    scenario has to be built so that releasing half of it is enough:

      balance 10,000, leverage 1:100, call 50%, stop out 30%, two 3.60-lot longs
      A entered at 1.10000, B entered at 1.10100

      tick 1  bid 1.09100 / ask 1.09110
              losses  A -3,240   B -3,600   equity 3,160
              margin  7,200 EUR * 1.09110 = 7,855.92      level 40.2%
              -> below the 50% call level, above the 30% stop-out: MARGIN CALL only

      tick 2  bid 1.08870 / ask 1.08880
              losses  A -4,068   B -4,428   equity 1,504
              margin  7,200 EUR * 1.08880 = 7,839.36      level 19.2%
              -> below 30%: STOP OUT. B is the worse loss, so B closes first.
              balance 10,000 - 4,428 = 5,572; equity unchanged at 1,504
              margin  3,600 EUR * 1.08880 = 3,919.68      level 38.4% -> recovered
    """
    group = make_group(leverage=100, margin_call=Decimal("50"), stop_out=Decimal("30"))
    h = await build_harness(
        groups=[group],
        symbols=[make_eurusd()],
        accounts=[make_account(group=group, balance=Decimal("10000"))],
        coverage=coverage(),
    )

    # A: the better entry
    await h.publish_tick("EURUSD", Decimal("1.09990"), Decimal("1.10000"))
    await buy(h, "3.60")
    # B: a tenth of a cent worse, so it loses slightly more in any fall
    await h.publish_tick("EURUSD", Decimal("1.10090"), Decimal("1.10100"))
    await buy(h, "3.60")

    opened = h.open_positions()
    assert len(opened) == 2
    better_entry = min(p.price_open.value for p in opened)
    worse_entry = max(p.price_open.value for p in opened)
    assert better_entry == Decimal("1.10000")
    assert worse_entry == Decimal("1.10100")

    # --- tick 1: margin call, and nothing may be closed yet -----------------
    await h.publish_tick("EURUSD", Decimal("1.09100"), Decimal("1.09110"))
    account = await h.account()
    assert Decimal("30") < account.margin_level < Decimal("50"), account.margin_level
    assert EventType.MARGIN_CALL_TRIGGERED.value in event_types(h)
    assert len(h.open_positions()) == 2, "a margin call must not close anything"
    assert EventType.STOP_OUT_INITIATED.value not in event_types(h)

    # --- tick 2: stop out. The MT5 state machine only reaches stop-out FROM a
    # --- margin call, so this second tick is what triggers the liquidation.
    await h.publish_tick("EURUSD", Decimal("1.08870"), Decimal("1.08880"))
    assert EventType.STOP_OUT_INITIATED.value in event_types(h)

    remaining = h.open_positions()
    assert len(remaining) == 1, (
        f"expected only the worst position closed, got {len(remaining)} still open"
    )
    # the survivor is the BETTER entry, i.e. the smaller loss
    assert remaining[0].price_open.value == better_entry
    assert worse_entry not in [p.price_open.value for p in remaining]

    account = await h.account()
    # the realised loss landed on the balance instead of vanishing with the position
    assert account.balance.amount == Decimal("5572"), account.balance.amount
    # and the released margin brought the level back above the 30% stop-out threshold
    assert account.margin_level >= Decimal("30"), account.margin_level
    assert EventType.POSITION_CLOSED.value in event_types(h)

    # a closing deal was written, marked as a stop-out and as an exit
    closing = [d for d in h.deal_repo.deals.values() if d.entry.name == "OUT"]
    assert len(closing) == 1
    assert closing[0].reason.name == "SO"
    assert closing[0].profit.amount == Decimal("-4428")


'''
s = s[:start] + new + s[end:]
io.open(p, "w", encoding="utf-8").write(s)
print("stop-out scenario rebuilt")
