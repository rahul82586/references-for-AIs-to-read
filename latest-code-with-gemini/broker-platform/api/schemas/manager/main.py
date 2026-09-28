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
from pydantic import BaseModel, Field, field_serializer


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

    @field_serializer("balance", "credit", "equity", "margin", "free_margin", "margin_level", mode="plain")
    def serialize_decimal(self, v: Optional[Decimal]) -> Optional[str]:
        if v is None:
            return None
        return f"{v:f}"


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
    external_id: Optional[str] = None
    routing_mode: str = "B-BOOK"
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

    @field_serializer("volume", "price_open", "price_current", "price_sl", "price_tp", "swap", "profit", "commission", mode="plain")
    def serialize_decimal(self, v: Optional[Decimal]) -> Optional[str]:
        if v is None:
            return None
        return f"{v:f}"


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
    r_mode = "A-BOOK" if external is not None else "B-BOOK"
    return PositionInfo(
        ticket=ticket,
        position_id=str(p.position_id),
        external_id=str(external) if external is not None else None,
        routing_mode=r_mode,
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
    """MT5 Deal information (from DealGet).

    M18: the F9 rule applies to deals too - `ticket` is the venue's own number
    from external_id or null (never 0), and `deal_id` rides alongside as the
    canonical row key.
    """
    ticket: Optional[int] = None
    deal_id: str
    order_id: Optional[str] = None
    position_id: Optional[str] = None
    login: int
    symbol: str
    deal_type: str  # BUY, SELL, BALANCE, etc.
    entry: str  # IN, OUT, INOUT, OUT_BY
    volume: Decimal
    volume_closed: Decimal = Decimal('0.00')
    price: Decimal
    profit: Decimal
    swap: Decimal
    commission: Decimal
    comment: Optional[str] = None
    time: Optional[datetime] = None


class OrderInfo(BaseModel):
    """MT5 Order information (from OrderGet).

    M18: same F9 rule - venue ticket or null, `order_id` as the canonical key,
    and `price_order` Optional because the entity declares it Optional (M10:
    a market order before its fill has no price; inventing 0 is a lie the
    NOT NULL column will die on anyway - see D20).
    """
    ticket: Optional[int] = None
    order_id: str
    login: int
    symbol: str
    order_type: str  # BUY, SELL, BUY_LIMIT, etc.
    state: str  # NEW, PLACED, FILLED, etc.
    volume_initial: Decimal
    volume_current: Decimal
    price_order: Optional[Decimal] = None
    price_sl: Optional[Decimal] = Field(None, alias="sl")
    price_tp: Optional[Decimal] = Field(None, alias="tp")
    time_setup: Optional[datetime] = None
    time_expiration: Optional[datetime] = None
    time_done: Optional[datetime] = None
    comment: Optional[str] = None

    class Config:
        populate_by_name = True


def deal_to_info(d) -> "DealInfo":
    """The ONE Deal -> DealInfo serializer for the manager dialect (M18).
    Volume/Price carry .value, Money carries .amount, the ticket follows the
    F9 rule via external_ticket's one implementation."""
    from api.routers.admin.reads import external_ticket

    entry_str = d.entry.value if hasattr(d.entry, "value") else str(d.entry)
    vol_closed = d.volume.value if str(entry_str).upper() in ("OUT", "OUT_BY", "1") else Decimal("0.00")

    return DealInfo(
        ticket=external_ticket(d.external_id),
        deal_id=str(d.deal_id),
        order_id=d.order_id,
        position_id=d.position_id,
        login=int(d.account_login),
        symbol=d.symbol,
        deal_type=d.deal_type.value if hasattr(d.deal_type, "value") else str(d.deal_type),
        entry=entry_str,
        volume=d.volume.value,
        volume_closed=vol_closed,
        price=d.price.value,
        profit=d.profit.amount,
        swap=d.swap.amount,
        commission=d.commission.amount,
        comment=d.comment or None,
        time=d.created_at,
    )


def order_to_info(o) -> "OrderInfo":
    """The ONE Order -> OrderInfo serializer for the manager dialect (M18)."""
    from api.routers.admin.reads import external_ticket

    return OrderInfo(
        ticket=external_ticket(o.external_id),
        order_id=str(o.ticket_id),
        login=int(o.account_login),
        symbol=o.symbol,
        order_type=o.order_type.value if hasattr(o.order_type, "value") else str(o.order_type),
        state=o.state.value if hasattr(o.state, "value") else str(o.state),
        volume_initial=o.volume_initial.value,
        volume_current=o.volume_current.value,
        price_order=o.price_order.value if o.price_order is not None else None,
        price_sl=o.price_sl.value if o.price_sl is not None else None,
        price_tp=o.price_tp.value if o.price_tp is not None else None,
        time_setup=o.time_setup,
        time_expiration=o.time_expiration,
        time_done=o.time_done,
        comment=o.comment or None,
    )