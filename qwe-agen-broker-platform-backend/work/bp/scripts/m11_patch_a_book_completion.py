"""M11 - close the A-Book trade.

BEFORE
======
`ExecutionOrchestrator._execute_a_book` sent the order to the LP, set the order
PLACED, published ORDER_ROUTED, and stopped. The M10 `FixLiquidityGateway`
returns a real FILLED execution report that was then dropped on the floor:

  * no Deal
  * no Position
  * no margin recompute
  * no release of the M6 margin reservation
  * and - worst - the blanket `except Exception` rejected the client order on a
    `FixTimeout`, when the gateway's own message says "hedge state UNKNOWN;
    reconcile before retrying". Rejecting the client while the LP may be holding
    the hedge leaves the broker with naked risk and no record of it.

So an A-Book destination was not a trade. This is the largest functional hole
left after M10, and it is what M11 exists to close.

AFTER
=====
Four outcomes, each handled explicitly, none guessed:

  FILLED / PARTIAL   book the client side through the SAME path B-Book uses
                     (_apply_deal_to_account -> RecordDealHandler), at the LP's
                     own price and volume: deal, position, margin recompute and
                     reservation release all follow. Partials book the filled
                     volume and leave the remainder live at the LP.

  ACK / ACK_STUB     the order rests at the LP. Nothing is booked, the
                     reservation is KEPT (the order is still live and still
                     needs margin), and a stub says so loudly.

  FixTimeout         hedge state UNKNOWN. The order is neither rejected nor
                     booked: rejecting invents a client-side cancel of a hedge
                     that may exist, booking invents a client position against a
                     hedge that may not. It stays as it is, keeps its
                     reservation, logs an error and publishes
                     HEDGE_STATE_UNKNOWN with reconciliation_required so an
                     operator or a drop-copy reconciler can resolve it.

  anything else      the LP definitively did not take the order -> reject the
                     client order, which releases the reservation through the
                     existing single rejection funnel.

COVERAGE SEMANTICS (the part that is easy to get backwards)
===========================================================
B-Book: the broker IS the counterparty, so client BUY -> broker SHORT and the
coverage account moves. That is existing, correct behaviour.

A-Book with a real hedge: the broker passed the risk ON to the LP, so its net
exposure is unchanged and the coverage account must NOT move. Moving it would
double-count risk the broker no longer holds and would drive the NOP 70/85/95%
thresholds against a position that does not exist.

A-Book with `stub: True`: there is no hedge, so the broker has in fact kept the
client's risk - economically a B-Book fill. Coverage moves exactly as B-Book
does, and the log says the flow is unhedged. Silently booking it as "hedged"
would understate broker exposure, which is the dangerous direction.

Also fixed en route
===================
`_apply_deal_to_account` hard-coded `volume=order.volume_initial.value`, so it
could only ever book a complete fill; a second partial would raise
"fill volume exceeds remaining". It now takes the volume to book.

`RecordDealHandler._release_order_reservation` released the order's ENTIRE hold
on any deal. Correct for a full fill, wrong for a partial - the remainder is
still live at the LP and still needs margin. It now releases in proportion to
the volume that actually filled, which is identical to today's behaviour when
the order completes.

Idempotent: re-running detects already-applied anchors and skips them.
"""
import ast
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

applied = []


def patch(path, pairs):
    src = io.open(path, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in src else "\n"
    changed = False
    for old, new in pairs:
        if nl == "\r\n":
            old = old.replace("\n", "\r\n")
            new = new.replace("\n", "\r\n")
        if src.count(old) != 1:
            if src.count(new) >= 1:
                print(f"  skip (already patched): {path}")
                continue
            raise AssertionError(f"{path}: anchor found {src.count(old)}x: {old[:80]!r}")
        src = src.replace(old, new, 1)
        changed = True
    if changed:
        ast.parse(src.replace("\r\n", "\n"))
        io.open(path, "w", encoding="utf-8", newline="").write(src)
        applied.append(path)


def replace_method(path, name, next_name, new_body):
    """Replace one whole method, delimited by the following method's def line."""
    src = io.open(path, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in src else "\n"
    start_marker = f"    async def {name}("
    end_marker = f"    async def {next_name}("
    i = src.find(start_marker)
    if i < 0:
        raise AssertionError(f"{path}: {name} not found")
    j = src.find(end_marker, i)
    if j < 0:
        raise AssertionError(f"{path}: {next_name} not found after {name}")
    body = new_body
    if nl == "\r\n":
        body = body.replace("\n", "\r\n")
    src = src[:i] + body + src[j:]
    ast.parse(src.replace("\r\n", "\n"))
    io.open(path, "w", encoding="utf-8", newline="").write(src)
    applied.append(path)


ORCH = "application/services/execution_orchestrator.py"

# ---------------------------------------------------------------- dispatch site
patch(ORCH, [(
    "            await self._execute_a_book(order, instruction)\n",
    "            await self._execute_a_book(order, instruction, account)\n",
)])

# ------------------------------------------------------- the new A-Book path
NEW_A_BOOK = '''    async def _execute_a_book(self, order: Order, instruction: ExecutionInstruction,
                              account: Optional[Account] = None):
        """Hedge the client's flow at an external LP, then book the client side.

        M11: this used to send the order and publish ORDER_ROUTED, dropping the
        LP's execution report - so an A-Book destination produced no deal, no
        position, no margin move and no reservation release. Every outcome the
        gateway can return is now handled explicitly, and none is guessed.
        """
        gateway_id = instruction.gateway_id
        logger.info(f"Executing order {order.ticket_id} via A-Book gateway {gateway_id}")

        try:
            report = await self.liquidity_gateway.send_order(
                order=order,
                gateway_id=gateway_id,
            )
        except Exception as exc:  # noqa: BLE001 - the gateway's contract is by exception
            if _hedge_state_unknown(exc):
                # The order reached the LP and we cannot say what happened there.
                await self._a_book_hedge_unknown(order, gateway_id, exc)
                return
            # The LP definitively did not take it. Rejecting is honest, and the
            # single rejection funnel releases the margin reservation.
            logger.error(f"A-Book execution failed for {order.ticket_id}: {exc}")
            await self._reject_order(order, f"A-Book gateway error: {exc}")
            return

        if not isinstance(report, dict):
            logger.error(
                "gateway %s returned a non-dict execution report for %s (%r); cannot "
                "book a fill from it", gateway_id, order.ticket_id, type(report).__name__,
            )
            await self._a_book_hedge_unknown(
                order, gateway_id,
                RuntimeError(f"malformed execution report: {type(report).__name__}"),
            )
            return

        status = str(report.get("status") or "").upper()
        if status in _LP_FILL_STATUSES:
            await self._book_a_book_fill(order, report, account, gateway_id)
        else:
            await self._a_book_resting(order, report, gateway_id, status)

    async def _book_a_book_fill(self, order: Order, report: dict,
                                account: Optional[Account], gateway_id: str) -> None:
        """The LP filled (fully or partly): book the client side at the LP's numbers."""
        if account is None:
            account = await self.account_repo.find_by_login(order.account_login)
        if account is None:
            # The LP holds a hedge and we cannot find the client. Do NOT reject:
            # that would cancel the client side of a live hedge. Loud, and flagged.
            logger.error(
                "order %s was FILLED at gateway %s but account %s cannot be loaded; "
                "the client side is unbooked and the hedge is live - reconcile manually",
                order.ticket_id, gateway_id, order.account_login,
            )
            await self._publish_a_book_reconciliation(order, gateway_id, report,
                                                      "ACCOUNT_NOT_FOUND")
            return

        flags = []
        fill_price = self._lp_fill_price(order, report, flags)
        fill_volume = self._lp_fill_volume(order, report, flags)
        if fill_volume <= 0:
            logger.error(
                "gateway %s reported status=%s for %s with no usable volume (%r); "
                "nothing booked", gateway_id, report.get("status"), order.ticket_id,
                report.get("volume"),
            )
            await self._publish_a_book_reconciliation(order, gateway_id, report,
                                                      "NO_FILLED_VOLUME")
            return

        try:
            deal = await self._apply_deal_to_account(
                order, fill_price, account, volume=fill_volume
            )
            if deal is None:
                raise RuntimeError(
                    "no deal-recording path is wired: the orchestrator needs either a "
                    "record_deal_handler or a position_repo to build one"
                )
        except Exception as exc:  # noqa: BLE001
            # Same rule as above: the hedge is live, so the client order must not be
            # rejected. This is a break for the back office, not a trading decision.
            logger.error(
                "order %s FILLED at gateway %s but booking the client side failed: %s - "
                "the hedge is live and the client has no position", order.ticket_id,
                gateway_id, exc, exc_info=True,
            )
            await self._publish_a_book_reconciliation(order, gateway_id, report,
                                                      "BOOKING_FAILED")
            return

        # --- Coverage. A REAL hedge means the broker passed the risk on, so its net
        # --- exposure is unchanged and the coverage account must NOT move; moving it
        # --- would double-count risk the broker no longer holds and drive the NOP
        # --- thresholds against a position that does not exist. A `stub` gateway has
        # --- hedged nothing, so the broker kept the client's risk - economically a
        # --- B-Book fill - and coverage moves exactly as B-Book does.
        hedged = not bool(report.get("stub"))
        volume_delta = Decimal("0")
        coverage_updated = False
        coverage_account_id = getattr(order, "coverage_account_id", None) or "DEFAULT_COVERAGE"
        if not hedged:
            logger.warning(
                "order %s booked as A-Book but gateway %s is a STUB - the flow is NOT "
                "hedged, so broker exposure moves as it would for B-Book",
                order.ticket_id, gateway_id,
            )
            is_buy = order.order_type.name.startswith("BUY")
            volume_delta = -fill_volume if is_buy else fill_volume
            if self.coverage_repo is not None:
                try:
                    await self.coverage_repo.update_exposure(
                        account_id=coverage_account_id,
                        symbol=order.symbol,
                        volume_delta=volume_delta,
                    )
                    coverage_updated = True
                except Exception as exc:  # noqa: BLE001
                    logger.error(
                        "order %s booked but coverage exposure could not be updated on "
                        "%s: %s - broker exposure is understated", order.ticket_id,
                        coverage_account_id, exc,
                    )
                    volume_delta = Decimal("0")

        for flag in flags:
            logger.error("order %s filled at gateway %s: %s", order.ticket_id, gateway_id, flag)

        try:
            await self.event_bus.publish(DomainEvent(
                event_type=EventType.DEAL_CREATED,
                aggregate_id=order.ticket_id,
                payload={
                    "order_id": order.ticket_id,
                    "deal_id": deal.deal_id,
                    "deal_type": deal.deal_type.value,
                    "price": str(fill_price),
                    "volume": str(fill_volume),
                    "destination": ExecutionDestination.A_BOOK.value,
                    "gateway_id": gateway_id,
                    "lp_order_id": report.get("order_id"),
                    "hedged": hedged,
                    "coverage_updated": coverage_updated,
                    "coverage_account_id": coverage_account_id,
                    "broker_volume_delta": str(volume_delta),
                    "remaining_volume": str(order.volume_current.value),
                    "reconciliation_flags": list(flags),
                },
            ))
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "order %s filled at the LP but the DEAL_CREATED routing event could not "
                "be published: %s", order.ticket_id, exc,
            )

    @staticmethod
    def _lp_fill_price(order: Order, report: dict, flags: list) -> Decimal:
        """The price the client fills at: the LP's average price.

        A FILLED report with no AvgPx is a malformed report, not a licence to pick
        a number. But the hedge is already live, so refusing to book is worse than
        booking at the client's instruction price and flagging it for the back
        office - which is what this does, loudly.
        """
        raw = report.get("price")
        if raw is not None:
            try:
                price = Decimal(str(raw))
                if price > 0:
                    return price
            except Exception:  # noqa: BLE001
                pass
        flags.append(
            "LP reported a fill with no usable AvgPx; booked at the order's own price "
            "and flagged for reconciliation"
        )
        price_order = getattr(order, "price_order", None)
        value = getattr(price_order, "value", price_order)
        return Decimal(str(value)) if value is not None else Decimal("0")

    @staticmethod
    def _lp_fill_volume(order: Order, report: dict, flags: list) -> Decimal:
        """The volume that actually filled, clamped to what is still outstanding.

        The LP is authoritative about its own fill, but it may not book more than
        the client asked for: an over-report is clamped and flagged rather than
        trusted, because trusting it would create client volume nobody requested.
        """
        remaining = order.volume_current.value
        raw = report.get("volume")
        try:
            filled = Decimal(str(raw)) if raw is not None else remaining
        except Exception:  # noqa: BLE001
            filled = Decimal("0")
        if filled <= 0:
            return Decimal("0")
        if filled > remaining:
            flags.append(
                f"LP reported {filled} filled against {remaining} outstanding; clamped "
                "to the outstanding volume and flagged for reconciliation"
            )
            return remaining
        return filled

    async def _a_book_resting(self, order: Order, report: dict, gateway_id: str,
                              status: str) -> None:
        """The LP acknowledged but has not filled: the order rests there.

        Nothing is booked and the margin reservation is KEPT - the order is still
        live and still needs its hold. This is the A-Book analogue of the B-Book
        RESTING_IN_BOOK path.
        """
        if report.get("stub"):
            logger.warning(
                "STUB gateway %s acknowledged order %s - no external hedge was placed, "
                "so the order is resting at a liquidity provider that does not exist",
                gateway_id, order.ticket_id,
            )
        else:
            logger.info(
                "order %s is resting at gateway %s (LP status %s); it will fill when "
                "the LP reports an execution", order.ticket_id, gateway_id, status,
            )
        try:
            if order.state is not OrderState.PLACED and not order.is_terminal():
                order.transition_to(OrderState.PLACED)
            await self.order_repo.save(order)
        except Exception as exc:  # noqa: BLE001
            logger.error("could not persist order %s as PLACED at the LP: %s",
                         order.ticket_id, exc)
        await self._publish_order_routed(order, gateway_id, report, "RESTING_AT_LP")

    async def _a_book_hedge_unknown(self, order: Order, gateway_id: str,
                                    exc: BaseException) -> None:
        """The order reached the LP and its fate is unknown.

        Neither reject nor book. Rejecting cancels the client side of a hedge that
        may be live; booking creates a client position against a hedge that may
        not be. The order is left exactly as it is, keeps its reservation, and is
        flagged for reconciliation - the only honest outcome, and the one the
        gateway's own FixTimeout message asks for.
        """
        logger.error(
            "order %s was sent to gateway %s and the hedge state is UNKNOWN: %s. The "
            "order is left PLACED with its margin reservation intact; reconcile against "
            "the LP (drop-copy or a status request) before retrying or cancelling.",
            order.ticket_id, gateway_id, exc,
        )
        try:
            if order.state is OrderState.STARTED and not order.is_terminal():
                order.transition_to(OrderState.PLACED)
            await self.order_repo.save(order)
        except Exception as save_exc:  # noqa: BLE001
            logger.error("could not persist order %s in the unknown-hedge state: %s",
                         order.ticket_id, save_exc)
        await self._publish_order_routed(
            order, gateway_id, {"error": str(exc)}, "HEDGE_STATE_UNKNOWN",
            reconciliation_required=True,
        )

    async def _publish_a_book_reconciliation(self, order: Order, gateway_id: str,
                                             report: dict, reason: str) -> None:
        """Publish an ORDER_ROUTED carrying a reconciliation flag for a break."""
        await self._publish_order_routed(
            order, gateway_id, report, "RECONCILIATION_REQUIRED",
            reconciliation_required=True, reconciliation_reason=reason,
        )

    async def _publish_order_routed(self, order: Order, gateway_id: str, report: dict,
                                    status: str, *, reconciliation_required: bool = False,
                                    reconciliation_reason: Optional[str] = None) -> None:
        payload = {
            "order_id": order.ticket_id,
            "destination": ExecutionDestination.A_BOOK.value,
            "gateway_id": gateway_id,
            "status": status,
            "lp_status": report.get("status"),
            "lp_order_id": report.get("order_id"),
            "stub": bool(report.get("stub")),
            "reconciliation_required": reconciliation_required,
        }
        if reconciliation_reason:
            payload["reconciliation_reason"] = reconciliation_reason
        try:
            await self.event_bus.publish(DomainEvent(
                event_type=EventType.ORDER_ROUTED,
                aggregate_id=order.ticket_id,
                payload=payload,
            ))
        except Exception as exc:  # noqa: BLE001
            logger.error("could not publish ORDER_ROUTED (%s) for %s: %s",
                         status, order.ticket_id, exc)

'''

replace_method(ORCH, "_execute_a_book", "_execute_b_book", NEW_A_BOOK)

# --------------------------------------------- _apply_deal_to_account: volume
patch(ORCH, [
    (
        "    async def _apply_deal_to_account(self, order: Order, fill_price, account) -> Optional[Any]:\n"
        '        """Record the fill: order state, immutable Deal, Position, account margin.\n'
        "\n"
        "        Returns the Deal, or None when no recording path is wired - which the caller\n"
        "        treats as a failure rather than a silent success.\n"
        '        """\n',
        "    async def _apply_deal_to_account(self, order: Order, fill_price, account,\n"
        "                                   volume: Optional[Decimal] = None) -> Optional[Any]:\n"
        '        """Record the fill: order state, immutable Deal, Position, account margin.\n'
        "\n"
        "        Returns the Deal, or None when no recording path is wired - which the caller\n"
        "        treats as a failure rather than a silent success.\n"
        "\n"
        "        `volume` defaults to the order's full initial volume, which is what a B-Book\n"
        "        crossing produces. M11: an LP partial fill passes the volume that actually\n"
        "        filled, because Order.apply_fill rejects a volume larger than what is still\n"
        "        outstanding.\n"
        '        """\n',
    ),
    (
        "            volume=order.volume_initial.value,\n",
        "            volume=order.volume_initial.value if volume is None else Decimal(str(volume)),\n",
    ),
])

# ------------------------------------ module constants + the unknown predicate
patch(ORCH, [(
    "from application.services.dealer_queue_service import DealerQueueService\n",
    "from application.services.dealer_queue_service import DealerQueueService\n"
    "\n"
    "# M11: the LP report statuses that mean volume actually filled. Anything else\n"
    "# (ACK, ACK_STUB, NEW) means the order is resting at the LP and nothing may be\n"
    "# booked.\n"
    '_LP_FILL_STATUSES = frozenset({"FILLED", "PARTIAL", "PARTIALLY_FILLED"})\n'
    "\n"
    "\n"
    "def _hedge_state_unknown(exc: BaseException) -> bool:\n"
    '    """True when the order reached the LP and its fate there cannot be known.\n'
    "\n"
    "    Deliberately not an import of FixTimeout: the orchestrator must not depend on\n"
    "    the FIX adapter to be correct, and a stub-only or REST deployment has no such\n"
    "    class. The gateway's own exception is recognised by name, and any adapter can\n"
    "    opt in explicitly by setting `hedge_state_unknown = True` on the exception it\n"
    "    raises - which is the honest signal, since only the adapter knows whether it\n"
    "    had already written to the socket.\n"
    '    """\n'
    "    if getattr(exc, \"hedge_state_unknown\", False):\n"
    "        return True\n"
    '    return type(exc).__name__ == "FixTimeout"\n'
    "\n"
)])

# ------------------------------- record_deal: proportional reservation release
patch("application/commands/record_deal.py", [(
    '    async def _release_order_reservation(self, order, account, session=None) -> None:\n'
    '        """Release the margin this order reserved at approval (M6)."""\n'
    '        reserved = Decimal(str(getattr(order, "reserved_margin", 0) or 0))\n'
    '        if reserved <= 0:\n'
    '            return\n'
    '        from application.services.margin_reservation import release_margin\n'
    '\n'
    '        await release_margin(\n'
    '            self.account_repo, account.login, reserved, account=account, session=session\n'
    '        )\n'
    '        order.reserved_margin = Decimal("0")\n',

    '    async def _release_order_reservation(self, order, account, session=None) -> None:\n'
    '        """Release the margin this order reserved at approval (M6).\n'
    "\n"
    "        M11: proportional to the volume that actually filled. A complete fill\n"
    "        releases the whole hold, exactly as before. A PARTIAL fill releases only\n"
    "        its share and leaves the rest, because the remainder is still live (at the\n"
    "        LP, for an A-Book order) and still needs margin - releasing the entire hold\n"
    "        on the first partial would leave the outstanding volume unhedged by any\n"
    "        reservation at all.\n"
    '        """\n'
    '        reserved = Decimal(str(getattr(order, "reserved_margin", 0) or 0))\n'
    '        if reserved <= 0:\n'
    '            return\n'
    '        from application.services.margin_reservation import release_margin\n'
    '\n'
    '        initial = Decimal(str(order.volume_initial.value))\n'
    '        remaining = Decimal(str(order.volume_current.value))\n'
    '        if initial > 0 and remaining > 0:\n'
    '            filled = initial - remaining\n'
    '            released = (reserved * filled / initial) if filled > 0 else Decimal("0")\n'
    '        else:\n'
    '            released = reserved\n'
    '        if released <= 0:\n'
    '            return\n'
    '\n'
    '        await release_margin(\n'
    '            self.account_repo, account.login, released, account=account, session=session\n'
    '        )\n'
    '        order.reserved_margin = reserved - released\n'
    '        if order.reserved_margin <= 0:\n'
    '            order.reserved_margin = Decimal("0")\n',
)])

print(f"applied to {len(set(applied))} file(s):")
for f in sorted(set(applied)):
    print("  ", f)
