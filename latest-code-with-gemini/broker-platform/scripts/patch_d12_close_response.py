#!/usr/bin/env python3
"""D12: a close must tell the client what it just did.  Idempotent.

The defect
----------
D11 gave the client a real close route. The route then built its response body by
reading the Position the handler returns - which by that point has `volume` 0 and,
in the normal "close at market" case, a `price_current` that no tick has set since
the position opened. So a close that genuinely booked an OUT deal answered::

    volume_closed 0E-8    close_price 0    realized_pnl 0E-8

Proven by `scripts/local_e2e.sh` gate 6b against a live local broker: margin was
released, the position was gone, the OUT deal existed - and the body described
none of it. A close is the exact moment a client learns its result, so those three
fields are the point of the endpoint. This is D1/D2 again: a value computed
correctly in one place (the OUT deal, the event payload, the balance) and served
empty from another.

The fix
-------
1. `ClosePositionHandler` stamps the close onto the position it returns and saves:
   on a FULL close, `price_current` becomes the price actually dealt and `profit`
   becomes the realised result - which is what MT5 itself reports for a position in
   history, and what `liquidation_worker` already assumes when it reads
   `position.profit.amount` as the realised figure. On a PARTIAL close the position
   stays open and floating, so `profit` is deliberately left alone: writing a
   realised number into a floating field would be the same lie in the other
   direction.
2. The route captures `volume` BEFORE calling the handler (after the call it is the
   remainder, 0 on a full close) and reports `volume_before - volume_after`, so a
   client that omits `volume` is still told what was closed.

Run:  python3 scripts/patch_d12_close_response.py
"""
from __future__ import annotations

import sys
from pathlib import Path

BP = Path(__file__).resolve().parent.parent

HANDLER = BP / "application" / "commands" / "close_position.py"
ROUTE = BP / "api" / "routers" / "trade.py"

# ---------------------------------------------------------------- handler patch

H_OLD = """        # 8. Update position\r
        position.volume = Volume(position.volume.value - close_volume)\r
        if position.volume.value == Decimal('0'):\r
            position.time_done = datetime.now(timezone.utc)\r
            position.deal_close = closing_deal.deal_id\r
        await self.position_repo.save(position)\r
"""

H_NEW = """        # 8. Update position\r
        #\r
        # D12: a FULL close also stamps the close onto the position, because this\r
        # object is what every caller sees afterwards - the client route builds its\r
        # response from it, the manager OrderClose endpoint reports from it, and\r
        # liquidation_worker already reads `position.profit.amount` as the realised\r
        # figure. Without this the route could only read volume 0 and a\r
        # `price_current` no tick had set since the position opened, so a close that\r
        # had genuinely dealt answered `volume_closed 0E-8 / close_price 0 /\r
        # realized_pnl 0E-8`. `profit` becoming the realised result on a closed\r
        # position is also what MT5 reports: a position in history shows its result,\r
        # not its last floating estimate.\r
        #\r
        # A PARTIAL close deliberately leaves `profit` alone. The position is still\r
        # open and still floating, so writing a realised number into a floating\r
        # field would be the same lie pointing the other way; the next tick reprices\r
        # the remainder.\r
        position.volume = Volume(position.volume.value - close_volume)\r
        # `price_current` is the last price this position dealt at, on a partial\r
        # close as much as on a full one - it is a fact about the trade, not an\r
        # estimate of the remainder.\r
        position.price_current = Price(current_price)\r
        if position.volume.value == Decimal('0'):\r
            position.time_done = datetime.now(timezone.utc)\r
            position.deal_close = closing_deal.deal_id\r
            position.profit = Money(realized_pnl, position.profit.currency)\r
        await self.position_repo.save(position)\r
"""

# ------------------------------------------------------------------ route patch

R_OLD = """    handler = _handler("close_position_handler", "Position closing")\r
    login = _login_of(current_user)\r
\r
    try:\r
        position = await handler.handle(ClosePositionCommand(\r
"""

R_NEW = """    handler = _handler("close_position_handler", "Position closing")\r
    login = _login_of(current_user)\r
\r
    # D12: the handler returns the position AFTER it reduced the volume, so the\r
    # amount actually closed has to be read before the call - on a full close the\r
    # returned volume is 0, and `request.volume` is None whenever the client asked\r
    # to close "all", which is the normal case. Both fallbacks below were therefore\r
    # empty exactly when the response mattered most.\r
    _before = await _position_repo_volume(handler, position_id)\r
\r
    try:\r
        position = await handler.handle(ClosePositionCommand(\r
"""

R_BODY_OLD = """    remaining = getattr(getattr(position, "volume", None), "value", Decimal("0"))\r
    realized = getattr(getattr(position, "profit", None), "amount", Decimal("0"))\r
    price = getattr(getattr(position, "price_current", None), "value", None)\r
    fully = bool(getattr(position, "time_done", None))\r
\r
    return ClosePositionResponse(\r
        position_id=str(getattr(position, "position_id", position_id)),\r
        symbol=str(getattr(position, "symbol", "")),\r
        # a full close leaves volume 0, so report what was actually closed\r
        volume_closed=(request.volume if request.volume is not None else remaining),\r
        volume_remaining=remaining,\r
        close_price=(Decimal(str(price)) if price is not None\r
                     else (request.price or Decimal("0"))),\r
        realized_pnl=Decimal(str(realized)),\r
"""

R_BODY_NEW = """    remaining = getattr(getattr(position, "volume", None), "value", Decimal("0"))\r
    realized = getattr(getattr(position, "profit", None), "amount", Decimal("0"))\r
    price = getattr(getattr(position, "price_current", None), "value", None)\r
    fully = bool(getattr(position, "time_done", None))\r
\r
    # What was closed is the difference, not the remainder and not the request:\r
    # `request.volume` is None for a full close, and `remaining` is 0 after one.\r
    closed = request.volume\r
    if closed is None:\r
        closed = (_before - remaining) if _before is not None else remaining\r
\r
    return ClosePositionResponse(\r
        position_id=str(getattr(position, "position_id", position_id)),\r
        symbol=str(getattr(position, "symbol", "")),\r
        volume_closed=Decimal(str(closed)),\r
        volume_remaining=remaining,\r
        # `price_current` is the price this close dealt at (stamped by the handler\r
        # on a full close); the request price and 0 are fallbacks of last resort.\r
        close_price=(Decimal(str(price)) if price is not None\r
                     else (request.price or Decimal("0"))),\r
        realized_pnl=Decimal(str(realized)),\r
"""

HELPER = '''

async def _position_repo_volume(handler: Any, position_id: str) -> Optional[Decimal]:
    """The position's volume before a close, or None if it cannot be read.

    D12 needs the closed amount, and the only honest way to get it is
    `volume_before - volume_after`. This reads through the same repository the
    handler is bound to, so it sees the same world the close will act on. A failure
    here must not fail the close - the close is the thing that matters - so it
    degrades to None and the response falls back to what it can say.
    """
    repo = getattr(handler, "position_repo", None)
    finder = getattr(repo, "find_by_id", None)
    if finder is None:
        return None
    try:
        existing = await finder(position_id)
    except Exception:  # noqa: BLE001
        logger.warning("could not pre-read position %s for the close response", position_id)
        return None
    if existing is None:
        return None
    value = getattr(getattr(existing, "volume", None), "value", None)
    return Decimal(str(value)) if value is not None else None
'''

# the file is CRLF, so the anchor has to be too
ANCHOR_FOR_HELPER = "\r\n\r\n@router.post(\"/positions/{position_id}/close\""


def patch(path: Path, old: str, new: str, already: str, label: str) -> bool:
    # newline="" matters: universal-newline reading turns the file's CRLF into \n
    # and every \r\n anchor below silently fails to match.
    with path.open(newline="") as fh:
        text = fh.read()
    if already in text:
        print(f"  = {label}: already patched")
        return False
    if old not in text:
        print(f"  ! {label}: anchor not found - refusing to guess", file=sys.stderr)
        raise SystemExit(1)
    with path.open("w", newline="") as fh:
        fh.write(text.replace(old, new, 1))
    print(f"  + {label}")
    return True


def main() -> int:
    print(f"patching {HANDLER.relative_to(BP)}")
    patch(HANDLER, H_OLD, H_NEW, "D12: a FULL close also stamps", "handler stamps the close")

    print(f"patching {ROUTE.relative_to(BP)}")
    with ROUTE.open(newline="") as fh:
        route = fh.read()
    if "_position_repo_volume" not in route:
        if ANCHOR_FOR_HELPER not in route:
            print(f"  ! helper anchor not found: {ANCHOR_FOR_HELPER!r}", file=sys.stderr)
            return 1
        with ROUTE.open("w", newline="") as fh:
            fh.write(route.replace(ANCHOR_FOR_HELPER, HELPER + ANCHOR_FOR_HELPER, 1))
        print("  + helper _position_repo_volume")
    else:
        print("  = helper already present")
    patch(ROUTE, R_OLD, R_NEW, "_before = await _position_repo_volume", "route pre-reads volume")
    patch(ROUTE, R_BODY_OLD, R_BODY_NEW, "volume_closed=Decimal(str(closed))", "route reports the close")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
