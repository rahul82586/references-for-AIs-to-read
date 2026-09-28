"""M10: the market-order response re-read survives an async-bus race.

On Redis the orchestrator executes in another task/process, so the create
handler's post-publish re-read can catch the order row mid-flight: state
already FILLED while volume_current has not been zeroed. The response used to
report filled_volume 0 for a genuinely filled order (observed on the M10 cloud
gate). The handler now retries until the row is self-consistent.

The double below reproduces the race deterministically: the FIRST read that
sees a FILLED order returns an inconsistent snapshot (FILLED + full volume),
exactly what the cloud row looked like mid-write.
"""
import asyncio
from decimal import Decimal

from application.commands.create_order import CreateOrderCommand
from core.domains.oms.enums import OrderState, OrderType
from tests.integration.trading_harness import (
    DEFAULT_LOGIN,
    build_harness,
    default_coverage,
)


class RacingOrderRepo:
    """Delegates to the real repo, but hands out ONE inconsistent snapshot:
    the first read after the fill lands - the handler's refresh."""

    def __init__(self, inner):
        self.inner = inner
        self.inconsistent_served = 0

    def __getattr__(self, name):
        return getattr(self.inner, name)

    async def find_by_id(self, order_id, session=None):
        order = await self.inner.find_by_id(order_id, session=session)
        if (
            order is not None
            and self.inconsistent_served == 0
            and order.state is OrderState.FILLED
        ):
            self.inconsistent_served += 1
            # a COPY: the in-memory repo shares instances, and corrupting the
            # stored order would falsify the very state the test asserts on
            import copy

            snapshot = copy.copy(order)
            snapshot.volume_current = order.volume_initial  # the mid-write row
            return snapshot
        return order


async def test_refresh_waits_for_a_consistent_row():
    h = await build_harness(coverage=default_coverage())
    h.order_repo = RacingOrderRepo(h.order_repo)
    # the stack resolved the repo at build time; point it at the wrapper too
    h.stack.create_order_handler.order_repo = h.order_repo
    h.stack.orchestrator.order_repo = h.order_repo

    await h.publish_tick("EURUSD", Decimal("1.10000"), Decimal("1.10010"))
    order = await h.stack.create_order_handler.handle(
        CreateOrderCommand(account_login=DEFAULT_LOGIN, symbol="EURUSD",
                           order_type=OrderType.BUY, volume=Decimal("0.10"))
    )

    assert h.order_repo.inconsistent_served == 1, "the race was never exercised"
    assert order.state is OrderState.FILLED
    # the returned entity is the CONSISTENT row, not the mid-write snapshot
    assert order.volume_current.value == Decimal("0")
    filled_volume = order.volume_initial.value - order.volume_current.value
    assert filled_volume == Decimal("0.10")
    # and the fill itself is real
    assert len(h.open_positions()) == 1
    assert h.deals_for(DEFAULT_LOGIN)
