import io

p = "application/commands/record_deal.py"
s = io.open(p, encoding="utf-8", newline="").read()
crlf = "\r\n" in s


def N(x):
    return x.replace("\n", "\r\n") if crlf else x


# --- 1. import PositionAction ------------------------------------------------
old = N("from core.domains.oms.entities.position import Position\n")
assert old in s
s = s.replace(
    old,
    N("from core.domains.oms.entities.position import Position\n"
      "from core.domains.oms.enums import PositionAction\n"),
    1,
)

# --- 2. module-level conversion helper --------------------------------------
anchor = N("class RecordDealHandler:")
assert anchor in s
helper = N('''def position_action_for(deal_type: Any) -> PositionAction:
    """The PositionAction a deal opens, from its DealType.

    Position.action is a PositionAction, but this handler assigned it a DealType in
    hedging mode and an OrderType in netting mode. All three enums spell their members
    "BUY"/"SELL", so nothing raised - the values just were not equal:

      * Position.reverse() computed `SELL if self.action == PositionAction.BUY else BUY`
        and got BUY, so reversing a long produced another long;
      * the netting filter `pos.action == deal_side` never matched, so a netting account
        accumulated one position per deal instead of netting them;
      * LiquidationWorker's `p.action == PositionAction.BUY` was False for every position,
        so it valued longs at the ASK instead of the BID and picked the wrong one to close;
      * close_position chose the wrong closing side.

    Anything that is not a BUY is a SELL, which is the whole of PositionAction.
    """
    name = getattr(deal_type, "name", None) or str(deal_type)
    return PositionAction.BUY if str(name).upper().startswith("BUY") else PositionAction.SELL


''')
s = s.replace(anchor, helper + anchor, 1)

# --- 3. hedging mode ---------------------------------------------------------
old = N("            action=deal.deal_type,\n")
assert old in s
s = s.replace(old, N("            action=position_action_for(deal.deal_type),\n"), 1)

# --- 4. netting mode: one PositionAction, used for compare AND construct ------
old = N("        deal_side = OrderType.BUY if deal.deal_type == DealType.BUY else OrderType.SELL\n")
assert old in s
s = s.replace(
    old,
    N("        # PositionAction, not OrderType: this is compared against Position.action and\n"
      "        # assigned to it below. See position_action_for().\n"
      "        deal_side = position_action_for(deal.deal_type)\n"),
    1,
)

io.open(p, "w", encoding="utf-8", newline="").write(s)
print("record_deal: PositionAction fix; crlf =", crlf)
