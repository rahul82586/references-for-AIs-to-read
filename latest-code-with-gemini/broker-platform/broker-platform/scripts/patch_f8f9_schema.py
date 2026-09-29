#!/usr/bin/env python3
"""F8/F9 patch 1: PositionInfo schema + the ONE shared serializer.

Idempotent: skips if already applied. Preserves the file's CRLF endings.
"""
import os, sys

WS = os.getcwd()
path = os.path.join(WS, "api", "schemas", "manager", "main.py")
src = open(path, encoding="utf-8", newline="").read()

if "position_to_info" in src:
    print("already applied"); sys.exit(0)

OLD = '''class PositionInfo(BaseModel):
    """MT5 Position information (from PositionGet)."""
    ticket: int
    login: int
    symbol: str
    action: str  # BUY or SELL
    volume: Decimal
    price_open: Decimal
    price_current: Decimal
    price_sl: Optional[Decimal] = Field(None, alias="sl")
    price_tp: Optional[Decimal] = Field(None, alias="tp")
    swap: Decimal
    profit: Decimal
    commission: Decimal = Decimal('0')
    magic: int = 0
    comment: Optional[str] = None
    time_create: Optional[datetime] = None
    time_update: Optional[datetime] = None

    class Config:
        populate_by_name = True'''

NEW = '''class PositionInfo(BaseModel):
    """MT5 Position information (from PositionGet).

    F8/F9 contract, rebuilt from the entity's own declarations:

    * ``ticket`` is the REAL venue ticket and comes from ``external_id`` - the
      entity's ``position_id`` is a UUID or ``{login}_{SYMBOL}_{hex}``, never
      numeric, so the old ``int(position_id) if isdigit() else 0`` served
      ``ticket=0`` for every position (F9). A position with no external ticket
      reports ``null`` - 0 would be a fabricated ticket, and a UI keying rows
      by ticket would collapse them all into one.
    * ``position_id`` is exposed as the canonical row key (ENDPOINTS.md B0).
    * ``price_current`` is Optional because the entity declares it Optional:
      None until the first tick arrives (24 of the 31 live open positions are
      in exactly that state). The old required ``Decimal`` made every serialize
      raise into the blanket ``except`` -> ``[]`` (F8).
    """
    ticket: Optional[int] = None
    position_id: str
    login: int
    symbol: str
    action: str  # BUY or SELL
    volume: Decimal
    price_open: Decimal
    price_current: Optional[Decimal] = None
    price_sl: Optional[Decimal] = Field(None, alias="sl")
    price_tp: Optional[Decimal] = Field(None, alias="tp")
    swap: Decimal
    profit: Decimal
    commission: Decimal = Decimal('0')
    magic: int = 0
    comment: Optional[str] = None
    time_create: Optional[datetime] = None
    time_update: Optional[datetime] = None

    class Config:
        populate_by_name = True


def position_to_info(p) -> "PositionInfo":
    """The ONE Position -> PositionInfo serializer (F8/F9).

    Shared by every route that serves positions to the manager plane, so the
    wire shape cannot drift between them - the D18 lesson (two builders of one
    shape is how 17-of-44-field drift happens). Reads the entity's declared
    vocabulary exactly: Volume/Price carry ``.value``, Money carries
    ``.amount``. Optional prices stay None - never 0, never price_open:
    inventing a current price the market never sent is the D13/D16 class.
    """
    external = getattr(p, "external_id", None)
    ticket: Optional[int] = None
    if external is not None and str(external).lstrip("-").isdigit():
        ticket = int(external)
    return PositionInfo(
        ticket=ticket,
        position_id=str(p.position_id),
        login=int(p.account_login),
        symbol=p.symbol,
        action=p.action.value if hasattr(p.action, "value") else str(p.action),
        volume=p.volume.value,
        price_open=p.price_open.value,
        price_current=p.price_current.value if p.price_current is not None else None,
        price_sl=p.price_sl.value if p.price_sl is not None else None,
        price_tp=p.price_tp.value if p.price_tp is not None else None,
        swap=p.swap.amount,
        profit=p.profit.amount,
        commission=p.commission.amount,
        magic=int(p.magic_number),
        comment=p.comment or None,
        time_create=p.time_create,
        time_update=p.time_update,
    )'''

# normalize to LF for matching, remember the ending
crlf = "\r\n" in src
work = src.replace("\r\n", "\n")
if OLD not in work:
    print("PATTERN NOT FOUND"); sys.exit(1)
work = work.replace(OLD, NEW, 1)
if crlf:
    work = work.replace("\n", "\r\n")
open(path, "w", encoding="utf-8", newline="").write(work)
print("patched schemas/manager/main.py (CRLF preserved)" if crlf else "patched schemas/manager/main.py")
