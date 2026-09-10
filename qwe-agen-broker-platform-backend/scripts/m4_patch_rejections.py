import io

# ---------------------------------------------------------------------------
# risk_service: remember WHY it rejected, so the caller can publish and log it
# ---------------------------------------------------------------------------
p = "application/services/risk_service.py"
s = io.open(p, encoding="utf-8", newline="").read()
crlf = "\r\n" in s


def N(x):
    return x.replace("\n", "\r\n") if crlf else x


old = N("        self._account_locks: Dict[str, asyncio.Lock] = {}\n")
assert old in s
s = s.replace(
    old,
    N("        self._account_locks: Dict[str, asyncio.Lock] = {}\n"
      "        #: reason for the most recent rejection. validate_order() returns a bool, so a\n"
      "        #: caller that suppresses event publishing (CreateOrderHandler does, to keep the\n"
      "        #: approval from firing inside the account lock) would otherwise have to invent\n"
      "        #: a reason for its own OrderRejected event and its log line.\n"
      "        self.last_rejection_reason: Optional[str] = None\n"),
    1,
)

# record the reason at every rejection site
s = s.replace(
    N('''                logger.warning(f"Order {order.ticket_id} rejected: {reason}")
                if publish_events:
                    await self._publish_rejection(order, reason)
                return False'''),
    N('''                logger.warning(f"Order {order.ticket_id} rejected: {reason}")
                self.last_rejection_reason = reason
                if publish_events:
                    await self._publish_rejection(order, reason)
                return False'''),
)
assert s.count(N("self.last_rejection_reason = reason")) == 5, s.count("self.last_rejection_reason = reason")

old = N('''            logger.info(f"Order {order.ticket_id} approved by Pre-Trade Risk Service")
            if publish_events:''')
assert old in s
s = s.replace(
    old,
    N('''            logger.info(f"Order {order.ticket_id} approved by Pre-Trade Risk Service")
            self.last_rejection_reason = None
            if publish_events:'''),
    1,
)
io.open(p, "w", encoding="utf-8", newline="").write(s)
print("risk_service: last_rejection_reason")

# ---------------------------------------------------------------------------
# create_order: a pricing failure must be audited like any other rejection
# ---------------------------------------------------------------------------
p = "application/commands/create_order.py"
s = io.open(p, encoding="utf-8", newline="").read()
crlf = "\r\n" in s

old = N('''        is_market = order.is_market()
        price_for_risk: Optional[Price] = None
        if is_market:
            price_for_risk = await self._market_price(command.symbol, side)
            order.price_order = price_for_risk
        elif command.price:
            price_for_risk = Price(command.price)
''')
assert old in s, "pricing block not found"
new = N('''        is_market = order.is_market()
        price_for_risk: Optional[Price] = None
        if is_market:
            try:
                price_for_risk = await self._market_price(command.symbol, side)
            except ValueError as exc:
                # No price means no trade. Reject and PERSIST it, the same as every other
                # rejection: an order that vanishes leaves no audit trail, and MT5 keeps
                # rejected orders in the history. Raising straight out of here - which is
                # what this did - lost the order entirely.
                await self._reject(order, str(exc))
                raise
            order.price_order = price_for_risk
        elif command.price:
            price_for_risk = Price(command.price)
''')
s = s.replace(old, new, 1)

old = N('''        if not approved:
            order.reject("Pre-trade risk check failed")
            await self.order_repo.save(order)
            logger.warning(f"Order {order.ticket_id} rejected by pre-trade risk")
            raise ValueError(f"Order rejected by pre-trade risk for {command.symbol}")
''')
assert old in s
new = N('''        if not approved:
            # validate_order was called with publish_events=False, so it did not publish
            # the rejection; do it here, with the reason it recorded, so subscribers and
            # the audit log see the same thing they would have seen otherwise.
            reason = getattr(self.risk_service, "last_rejection_reason", None) or (
                f"Pre-trade risk check failed for {command.symbol}"
            )
            await self._reject(order, reason)
            raise ValueError(f"Order rejected: {reason}")
''')
s = s.replace(old, new, 1)

# --- the shared reject helper ------------------------------------------------
anchor = N("    async def _market_price(self, symbol_name: str, side: str) -> Price:")
assert anchor in s
helper = N('''    async def _reject(self, order: Order, reason: str) -> None:
        """Move an order to REJECTED, persist it, and publish OrderRejected.

        One path for every rejection reason, so a rejected order is always recorded and
        always announced. Before this, an unpriceable market order raised out of step 4
        with nothing persisted, while an insufficient-margin order was persisted with no
        event - two different half-behaviours for the same outcome.
        """
        if not order.is_terminal():
            order.reject(reason)
        try:
            await self.order_repo.save(order)
        except Exception as exc:  # noqa: BLE001 - the rejection must still be published
            logger.error("could not persist rejected order %s: %s", order.ticket_id, exc)
        await self.event_bus.publish(OrderRejected(
            aggregate_id=order.ticket_id,
            payload={
                "order_id": order.ticket_id,
                "ticket_id": order.ticket_id,
                "account_login": order.account_login,
                "symbol": order.symbol,
                "reason": reason,
            },
        ))
        logger.warning("Order %s rejected: %s", order.ticket_id, reason)

''')
s = s.replace(anchor, helper + anchor, 1)

io.open(p, "w", encoding="utf-8", newline="").write(s)
print("create_order: rejection audit trail")

# ---------------------------------------------------------------------------
# test expectation: maintenance margin on two longs converts at the ASK
# ---------------------------------------------------------------------------
p = "tests/integration/test_order_execution_e2e.py"
s = io.open(p, encoding="utf-8").read()
old = '''    # (0.10 + 0.20) lots * 100,000 / 100 = 300 EUR, at the bid for maintenance on a
    # long: 300 * 1.10000 = 330.00
    assert account.margin_used.amount == Decimal("330.00")'''
assert old in s
new = '''    # (0.10 + 0.20) lots * 100,000 / 100 = 300 EUR, converted at the ASK because the
    # position is long (MT5: "the Ask price is used for buy deals"): 300 * 1.10010 = 330.03
    assert account.margin_used.amount == Decimal("330.03")'''
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("test expectation corrected")
