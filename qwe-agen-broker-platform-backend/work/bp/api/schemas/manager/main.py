"""
MT5 Manager API - Main query response schemas.

Maps to MT5 response objects:
- AccountInfo (from UserGet)
- PositionInfo (from PositionGet)
- DealInfo (from DealGet)
- OrderInfo (from OrderGet)
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class AccountInfo(BaseModel):
    """MT5 Account information (from UserGet)."""
    login: int
    group: str
    currency: str
    balance: Decimal
    credit: Decimal = Decimal('0')
    equity: Decimal
    margin: Decimal
    free_margin: Decimal
    margin_level: Decimal
    leverage: int
    enable: bool = True
    enable_charts: bool = True
    enable_news: bool = True
    enable_trades: bool = True
    password_phone: Optional[str] = None
    email: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    registration: Optional[datetime] = None
    last_visit: Optional[datetime] = None
    last_pass_change: Optional[datetime] = None
    comment: Optional[str] = None


class PositionInfo(BaseModel):
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
    )


class DealInfo(BaseModel):
    """MT5 Deal information (from DealGet)."""
    ticket: int
    login: int
    symbol: str
    deal_type: str  # BUY, SELL, BALANCE, etc.
    entry: str  # IN, OUT, INOUT, OUT_BY
    volume: Decimal
    price: Decimal
    profit: Decimal
    swap: Decimal
    commission: Decimal
    comment: Optional[str] = None
    time: Optional[datetime] = None


class OrderInfo(BaseModel):
    """MT5 Order information (from OrderGet)."""
    ticket: int
    login: int
    symbol: str
    order_type: str  # BUY, SELL, BUY_LIMIT, etc.
    state: str  # NEW, PLACED, FILLED, etc.
    volume_initial: Decimal
    volume_current: Decimal
    price_order: Decimal
    price_sl: Optional[Decimal] = Field(None, alias="sl")
    price_tp: Optional[Decimal] = Field(None, alias="tp")
    time_setup: Optional[datetime] = None
    time_expiration: Optional[datetime] = None
    time_done: Optional[datetime] = None
    comment: Optional[str] = None

    class Config:
        populate_by_name = True