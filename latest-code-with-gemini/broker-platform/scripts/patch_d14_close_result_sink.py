#!/usr/bin/env python3
"""D14: a partial close reported the remainder's floating PnL and no deal id.  Idempotent.

Measured live against Neon by `scripts/d12_proof_cloud_close.sh`:

    response: realized_pnl -1.01920000   deal_id ""
    OUT deal: profit        +0.50000000  deal_id 29681303-d6e1-4b02-8742-9eb1e412e666

Two fields, one cause: the route described the close by reading the POSITION, and a
partial close leaves that position open and floating.

* `realized_pnl` came from `position.profit`, which on a partial close is the
  unrealised PnL of the remainder - so a client that closed half of a losing
  position was handed the loss it had NOT realised, while the balance moved by the
  leg's own +0.50. D12 fixed this for a FULL close by stamping the realised result
  onto the closed position (which is what MT5 reports); the same stamp must not be
  applied to a position that is still open, so the partial path had nothing to read.
* `deal_id` came from `position.deal_close`, which only a full close sets, so every
  partial close looked like it had booked no deal at all.

The handler knows all of it - it builds the deal - but its contract is "return the
Position". Rather than change that return type under the SL/TP worker, the
liquidation worker and the manager route, the command grows an optional result sink
the handler fills. Callers that do not pass one are unaffected.

Run:  python3 scripts/patch_d14_close_result_sink.py
"""
from __future__ import annotations

import sys
from pathlib import Path

BP = Path(__file__).resolve().parent.parent
HANDLER = BP / "application" / "commands" / "close_position.py"
ROUTE = BP / "api" / "routers" / "trade.py"

# ---------------------------------------------------------------------- handler

H_IMPORT_OLD = "from typing import Any, Optional\r\n"
H_IMPORT_NEW = "from typing import Any, Dict, Optional\r\n"

H_CMD_OLD = '''    #: "SL" / "TP" / "SO" when a server-side trigger closed the position (M9);\r
    #: empty means a client/dealer close. Flows onto the closing deal AND order\r
    #: reasons, so statements say why the position closed.\r
    reason: str = ""\r
'''
H_CMD_NEW = '''    #: "SL" / "TP" / "SO" when a server-side trigger closed the position (M9);\r
    #: empty means a client/dealer close. Flows onto the closing deal AND order\r
    #: reasons, so statements say why the position closed.\r
    reason: str = ""\r
    #: D14: an optional sink the handler fills with what THIS close did -\r
    #: `deal_id`, `price`, `realized_pnl`, `volume_closed`. The handler's contract\r
    #: is "return the Position", and a partial close leaves that position open and\r
    #: floating, so a caller cannot read the leg's own result off it: `profit` is\r
    #: the remainder's unrealised PnL and `deal_close` is only set by a full close.\r
    #: Callers that do not pass a sink are unaffected.\r
    result: Optional[Dict[str, Any]] = None\r
'''

H_FILL_OLD = '''        await self.deal_repo.save(closing_deal)\r
'''
H_FILL_NEW = '''        await self.deal_repo.save(closing_deal)\r
\r
        # D14: report the leg, from the deal that was just booked rather than from\r
        # the position - which on a partial close is still open, still floating,\r
        # and still carrying whatever the last tick wrote into `profit`.\r
        if command.result is not None:\r
            command.result.update({\r
                "deal_id": closing_deal.deal_id,\r
                "price": current_price,\r
                "realized_pnl": realized_pnl,\r
                "volume_closed": close_volume,\r
            })\r
'''

# ------------------------------------------------------------------------- route

R_IMPORT_OLD = "from typing import Any, Optional\r\n"
R_IMPORT_NEW = "from typing import Any, Dict, Optional\r\n"

R_CALL_OLD = '''    try:\r
        position = await handler.handle(ClosePositionCommand(\r
            account_login=login,\r
            position_id=position_id,\r
            volume=request.volume,\r
            price=request.price,\r
            comment=request.comment or "",\r
            reason="CLIENT",\r
        ))\r
'''
R_CALL_NEW = '''    # D14: the handler fills this with what the close actually did. Reading the\r
    # returned Position instead is what made a partial close report the remainder's\r
    # floating PnL and an empty deal id.\r
    result: Dict[str, Any] = {}\r
\r
    try:\r
        position = await handler.handle(ClosePositionCommand(\r
            account_login=login,\r
            position_id=position_id,\r
            volume=request.volume,\r
            price=request.price,\r
            comment=request.comment or "",\r
            reason="CLIENT",\r
            result=result,\r
        ))\r
'''

R_BODY_OLD = '''    remaining = getattr(getattr(position, "volume", None), "value", Decimal("0"))\r
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
        deal_id=str(getattr(position, "deal_close", None) or ""),\r
'''
R_BODY_NEW = '''    remaining = getattr(getattr(position, "volume", None), "value", Decimal("0"))\r
    fully = bool(getattr(position, "time_done", None))\r
\r
    # Every figure below comes from the deal the handler booked, so a partial and a\r
    # full close are described the same way. The position-derived reads stay as\r
    # fallbacks for a handler that does not fill the sink (a double, or a caller\r
    # wired before D14) - they are right for a full close and wrong for a partial,\r
    # which is the defect.\r
    realized = result.get("realized_pnl")\r
    if realized is None:\r
        realized = getattr(getattr(position, "profit", None), "amount", Decimal("0"))\r
    price = result.get("price")\r
    if price is None:\r
        price = getattr(getattr(position, "price_current", None), "value", None)\r
    deal_id = result.get("deal_id") or getattr(position, "deal_close", None) or ""\r
\r
    # What was closed is the difference, not the remainder and not the request:\r
    # `request.volume` is None for a full close, and `remaining` is 0 after one.\r
    closed = result.get("volume_closed")\r
    if closed is None:\r
        closed = request.volume\r
    if closed is None:\r
        closed = (_before - remaining) if _before is not None else remaining\r
\r
    return ClosePositionResponse(\r
        position_id=str(getattr(position, "position_id", position_id)),\r
        symbol=str(getattr(position, "symbol", "")),\r
        volume_closed=Decimal(str(closed)),\r
        volume_remaining=remaining,\r
        close_price=(Decimal(str(price)) if price is not None\r
                     else (request.price or Decimal("0"))),\r
        realized_pnl=Decimal(str(realized)),\r
        deal_id=str(deal_id),\r
'''


def patch(path: Path, old: str, new: str, label: str, *, done: str) -> bool:
    # newline="" : both files are CRLF and universal-newline reading would turn every
    # \r\n into \n, so the anchors could never match.
    with path.open(newline="") as fh:
        text = fh.read()
    if done in text:
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
    patch(HANDLER, H_IMPORT_OLD, H_IMPORT_NEW, "Dict import",
          done="from typing import Any, Dict, Optional")
    patch(HANDLER, H_CMD_OLD, H_CMD_NEW, "command grows a result sink",
          done="result: Optional[Dict[str, Any]] = None")
    patch(HANDLER, H_FILL_OLD, H_FILL_NEW, "handler fills the sink from the deal",
          done="D14: report the leg, from the deal that was just booked")

    print(f"patching {ROUTE.relative_to(BP)}")
    patch(ROUTE, R_IMPORT_OLD, R_IMPORT_NEW, "Dict import",
          done="from typing import Any, Dict, Optional")
    patch(ROUTE, R_CALL_OLD, R_CALL_NEW, "route passes the sink",
          done="result=result,")
    patch(ROUTE, R_BODY_OLD, R_BODY_NEW, "route reads the sink, not the position",
          done='deal_id = result.get("deal_id")')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
