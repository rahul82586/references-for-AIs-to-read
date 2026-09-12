"""M10: a filled order's zero volume must survive entity reconstruction.

Order.__post_init__ used to reset volume_current to volume_initial on EVERY
construction whenever it was zero - including db_to_order(), which rebuilds the
entity on every SQL read. A fully filled order legitimately carries
volume_current == 0, so every read of one resurrected phantom volume: the HTTP
layer reported filled_volume 0 for genuinely filled orders (caught by the M10
cloud gate; the in-memory harness never reconstructs entities and could not see
it). These tests pin the mapper round-trip itself.
"""
from decimal import Decimal

from core.domains.common.value_objects import Price, Volume
from core.domains.oms.entities.order import Order
from core.domains.oms.enums import OrderState, OrderType
from infrastructure.persistence.mappers import db_to_order, order_to_db


def make_order(state, vol_current):
    return Order(
        account_login=100001,
        symbol="EURUSD",
        order_type=OrderType.BUY,
        volume_initial=Volume(Decimal("0.10")),
        volume_current=Volume(Decimal(vol_current)),
        price_order=Price(Decimal("1.10010")),
        state=state,
    )


def test_new_order_still_gets_the_volume_default():
    order = Order(volume_initial=Volume(Decimal("0.10")))  # state STARTED, current 0
    assert order.volume_current.value == Decimal("0.10")


def test_filled_order_keeps_zero_volume():
    order = make_order(OrderState.FILLED, "0")
    assert order.volume_current.value == Decimal("0")


def test_db_roundtrip_preserves_a_filled_order():
    """The exact path the cloud reads take: domain -> row -> domain."""
    order = make_order(OrderState.FILLED, "0")
    rebuilt = db_to_order(order_to_db(order))
    assert rebuilt.state is OrderState.FILLED
    assert rebuilt.volume_current.value == Decimal("0")
    assert rebuilt.volume_initial.value == Decimal("0.10")


def test_db_roundtrip_preserves_partial_fill():
    order = make_order(OrderState.PARTIALLY_FILLED, "0.04")
    rebuilt = db_to_order(order_to_db(order))
    assert rebuilt.volume_current.value == Decimal("0.04")


def test_db_roundtrip_preserves_placed_pending():
    order = make_order(OrderState.PLACED, "0.10")
    rebuilt = db_to_order(order_to_db(order))
    assert rebuilt.volume_current.value == Decimal("0.10")
