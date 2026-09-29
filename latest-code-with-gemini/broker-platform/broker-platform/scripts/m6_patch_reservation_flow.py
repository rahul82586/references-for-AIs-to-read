"""M6 patch: reservation at approval, release at fill and every rejection."""
import ast
import io
import pathlib


def read(path):
    p = pathlib.Path(path)
    src = io.open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in src else "\n"
    return src, nl


def write(path, src, nl):
    ast.parse(src.replace("\r\n", "\n") if nl == "\r\n" else src)
    io.open(path, "w", encoding="utf-8", newline="").write(src)


def apply(path, pairs):
    src, nl = read(path)
    for old, new in pairs:
        if nl == "\r\n":
            old = old.replace("\n", "\r\n")
            new = new.replace("\n", "\r\n")
        assert src.count(old) == 1, f"{path}: anchor {src.count(old)}x: {old[:70]!r}"
        src = src.replace(old, new)
    write(path, src, nl)
    print(f"{path}: {len(pairs)} patch(es)")


# ---------------------------------------------------------------------------
# risk_service: the check returns the requirement; approval reserves it
# ---------------------------------------------------------------------------
apply("application/services/risk_service.py", [
    (
        """    async def _check_margin_requirement(
        self,
        order: Order,
        account: Account,
        symbol: Symbol,
        price: Price,
    ) -> bool:
""",
        """    async def _check_margin_requirement(
        self,
        order: Order,
        account: Account,
        symbol: Symbol,
        price: Price,
    ) -> Optional[Decimal]:
""",
    ),
    (
        """            logger.warning(
                "margin check for order %s could not be computed: %s", order.ticket_id, exc
            )
            return False
""",
        """            logger.warning(
                "margin check for order %s could not be computed: %s", order.ticket_id, exc
            )
            return None
""",
    ),
    (
        """        # 4. Available margin. Use the live snapshot when we can build one, and treat a
        #    failure to build it as a rejection rather than silently degrading to a
        #    cached number.
        available = account.margin_free.amount
""",
        """        # 4. Available margin. Use the live snapshot when we can build one, and treat a
        #    failure to build it as a rejection rather than silently degrading to a
        #    cached number. In-flight reservations (M6) count against availability in
        #    BOTH paths: a second concurrent order must see the first one's hold
        #    whether or not it has filled yet.
        reserved_now = (
            account.margin_reserved.amount
            if getattr(account, "margin_reserved", None) is not None
            else Decimal("0")
        )
        available = account.margin_free.amount - reserved_now
""",
    ),
    (
        """                available = available_margin(
                    equity=snapshot.equity,
                    margin_used=snapshot.margin_used,
""",
        """                available = available_margin(
                    equity=snapshot.equity,
                    margin_used=snapshot.margin_used + reserved_now,
""",
    ),
    (
        """                logger.error(
                    "live margin snapshot failed for %s; rejecting rather than trusting "
                    "the stored free margin: %s",
                    account.login,
                    exc,
                )
                return False
""",
        """                logger.error(
                    "live margin snapshot failed for %s; rejecting rather than trusting "
                    "the stored free margin: %s",
                    account.login,
                    exc,
                )
                return None
""",
    ),
    (
        """        if required > available:
            logger.debug(
                "margin check failed for %s: required %s, available %s",
                order.ticket_id,
                required,
                available,
            )
            return False
        return True
""",
        """        if required > available:
            logger.debug(
                "margin check failed for %s: required %s, available %s (reserved in-flight %s)",
                order.ticket_id,
                required,
                available,
                reserved_now,
            )
            return None
        return required
""",
    ),
    (
        """            if not await self._check_margin_requirement(order, live_account, symbol, current_price):
                reason = "Insufficient free margin to open this position"
                logger.warning(f"Order {order.ticket_id} rejected: {reason}")
                self.last_rejection_reason = reason
                if publish_events:
                    await self._publish_rejection(order, reason)
                return False

            # All checks passed under lock protection
            logger.info(f"Order {order.ticket_id} approved by Pre-Trade Risk Service")
            self.last_rejection_reason = None
            if publish_events:
                await self._publish_approval(order)
            return True
""",
        """            required_margin = await self._check_margin_requirement(
                order, live_account, symbol, current_price
            )
            if required_margin is None:
                reason = "Insufficient free margin to open this position"
                logger.warning(f"Order {order.ticket_id} rejected: {reason}")
                self.last_rejection_reason = reason
                if publish_events:
                    await self._publish_rejection(order, reason)
                return False

            # M6 (M4 debt #1): hold the requirement before approving. Between
            # here and the fill nothing else moves a number the check reads, so
            # without the hold two concurrent orders - across a Redis bus, or
            # across two API nodes - could both pass the same free-margin check
            # and both book. The SQL repository does this as ONE conditional
            # UPDATE (the database serialises the racers); the amount held is
            # recorded on the order so the release at fill/reject is exact.
            from application.services.margin_reservation import (
                release_margin,
                reserve_margin,
            )

            if required_margin > 0:
                if not await reserve_margin(self.account_repo, live_account, required_margin):
                    reason = (
                        "Insufficient free margin to open this position "
                        "(reserved by concurrent in-flight orders)"
                    )
                    logger.warning(f"Order {order.ticket_id} rejected: {reason}")
                    self.last_rejection_reason = reason
                    if publish_events:
                        await self._publish_rejection(order, reason)
                    return False
                order.reserved_margin = required_margin

            # All checks passed under lock protection
            logger.info(f"Order {order.ticket_id} approved by Pre-Trade Risk Service")
            self.last_rejection_reason = None
            if publish_events:
                try:
                    await self._publish_approval(order)
                except Exception:
                    # the approval never reached the orchestrator: un-hold
                    if order.reserved_margin:
                        await release_margin(
                            self.account_repo, live_account.login,
                            order.reserved_margin, account=live_account,
                        )
                        order.reserved_margin = Decimal("0")
                    raise
            return True
""",
    ),
])

# ---------------------------------------------------------------------------
# record_deal: the fill releases the hold (same transaction when there is one)
# ---------------------------------------------------------------------------
apply("application/commands/record_deal.py", [
    (
        """        await self._recalculate_account_margin(account, position_repo=position_repo, session=session)
""",
        """        # M6: the approval's reservation has done its job - the real requirement
        # is recomputed into margin_used next. Release the order's exact hold (in
        # the same transaction when we have one) and zero the order's field so a
        # replay or a second deal on the same order cannot release it twice.
        await self._release_order_reservation(order, account, session=session)

        await self._recalculate_account_margin(account, position_repo=position_repo, session=session)
""",
    ),
    (
        """    async def _book_netting_realized(
""",
        """    async def _release_order_reservation(self, order, account, session=None) -> None:
        \"\"\"Release the margin this order reserved at approval (M6).\"\"\"
        reserved = Decimal(str(getattr(order, "reserved_margin", 0) or 0))
        if reserved <= 0:
            return
        from application.services.margin_reservation import release_margin

        await release_margin(
            self.account_repo, account.login, reserved, account=account, session=session
        )
        order.reserved_margin = Decimal("0")
        order_repo = self.order_repo
        if hasattr(order_repo, "save"):
            if _accepts_session(order_repo.save):
                await order_repo.save(order, session=session)
            else:
                await order_repo.save(order)

    async def _book_netting_realized(
""",
    ),
])

# ---------------------------------------------------------------------------
# orchestrator: every rejection funnel releases the hold
# ---------------------------------------------------------------------------
apply("application/services/execution_orchestrator.py", [
    (
        """    async def _reject_order(self, order: Order, reason: str):
        \"\"\"
        Reject the order and emit OrderRejectedEvent.
        \"\"\"
        if not order.is_terminal():
""",
        """    async def _reject_order(self, order: Order, reason: str):
        \"\"\"
        Reject the order and emit OrderRejectedEvent.
        \"\"\"
        # M6: a rejected order releases its margin reservation - the hold must
        # not outlive the order, or the account loses free margin forever. This
        # is the single rejection funnel (routing block, A-Book refusal, B-Book
        # error, ECN error, dealer error), so one release here covers them all.
        from decimal import Decimal as _Dec

        reserved = _Dec(str(getattr(order, "reserved_margin", 0) or 0))
        if reserved > 0:
            from application.services.margin_reservation import release_margin

            await release_margin(self.account_repo, order.account_login, reserved)
            order.reserved_margin = _Dec("0")
        if not order.is_terminal():
""",
    ),
])

# ---------------------------------------------------------------------------
# create_order: a failed persist must not strand the hold
# ---------------------------------------------------------------------------
apply("application/commands/create_order.py", [
    (
        """        # 6. Persist the order.
        order.state = OrderState.PLACED
        saved_order = await self.order_repo.save(order)
""",
        """        # 6. Persist the order. The approval reserved margin (M6); if the
        #    persistence fails, the reservation must not strand.
        order.state = OrderState.PLACED
        try:
            saved_order = await self.order_repo.save(order)
        except Exception:
            await self._release_reservation(order, account)
            raise
""",
    ),
    (
        """    async def _reject(""",
        """    async def _release_reservation(self, order, account) -> None:
        \"\"\"Un-hold the margin an approval reserved when the flow dies before
        the orchestrator can own the order (M6).\"\"\"
        from decimal import Decimal as _Dec

        reserved = _Dec(str(getattr(order, "reserved_margin", 0) or 0))
        if reserved <= 0:
            return
        from application.services.margin_reservation import release_margin

        await release_margin(self.account_repo, order.account_login, reserved, account=account)
        order.reserved_margin = _Dec("0")

    async def _reject(""",
    ),
])

# ---------------------------------------------------------------------------
# harness double: mirror the SQL semantics so the e2e fleet exercises the
# real reservation path (M4's lesson: doubles that lack the production methods
# let defects hide)
# ---------------------------------------------------------------------------
apply("tests/integration/trading_harness.py", [
    (
        """    async def find_by_login(self, login_id: Any, session: Any = None) -> Optional[Account]:
        return self.accounts.get(login_id) or self.accounts.get(int(login_id))
""",
        """    async def find_by_login(self, login_id: Any, session: Any = None) -> Optional[Account]:
        return self.accounts.get(login_id) or self.accounts.get(int(login_id))

    async def reserve_margin(self, login_id: Any, amount: Any, session: Any = None) -> bool:
        \"\"\"Mirrors SqlAccountRepository.reserve_margin: hold only while
        balance + credit + profit - margin_used - margin_reserved covers it.\"\"\"
        account = self.accounts.get(login_id)
        if account is None:
            try:
                account = self.accounts.get(int(login_id))
            except (TypeError, ValueError):
                account = None
        if account is None:
            return False
        amount = Decimal(str(amount))
        free = (
            account.balance.amount
            + account.credit.amount
            + account.profit.amount
            - account.margin_used.amount
            - account.margin_reserved.amount
        )
        if free < amount:
            return False
        account.margin_reserved = Money(account.margin_reserved.amount + amount, account.currency)
        return True

    async def release_margin(self, login_id: Any, amount: Any, session: Any = None) -> None:
        account = self.accounts.get(login_id)
        if account is None:
            try:
                account = self.accounts.get(int(login_id))
            except (TypeError, ValueError):
                account = None
        if account is None:
            return
        amount = Decimal(str(amount))
        account.margin_reserved = Money(
            max(Decimal("0"), account.margin_reserved.amount - amount), account.currency
        )
""",
    ),
])

print("flow patches applied")
