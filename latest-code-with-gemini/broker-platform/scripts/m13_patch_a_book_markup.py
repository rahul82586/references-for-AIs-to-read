"""M13 part 2: the A-Book client price and the venue price are now different numbers.

BEFORE (measured, group SpreadDiff 20 points, raw ask 1.10010, venue ask 1.10000)
================================================================================
    price we SENT to the LP     1.10030   <- the CLIENT price, marked up
    price the LP FILLED at      1.10000
    price we BOOKED the client  1.10000   <- the VENUE's price
    broker margin on the hedge  0.00000   = 0 points

Two defects pulling in opposite directions and cancelling to exactly zero. That is
why nothing caught it: both numbers looked plausible, and no test asserted on the
difference.

  a) the marked-up CLIENT price was forwarded to the venue, so a price-limited
     instruction asked the LP to trade 20 points worse than the market;
  b) the client was booked at the VENUE's fill price, discarding the markup they
     were quoted - and which the risk check and the margin reservation were
     computed from.

AFTER
=====
MT5's ECN model, from the Administrator guide's own worked example:

    client quoted and filled at 1.15661  (the converted price)
    venue receives and fills at 1.15659  (the original)
    "The broker earns the profit of 2 pips"

  * the client is booked at the venue's fill +/- the group's configured markup, so
    the broker earns EXACTLY what the group says - 20 points in, 20 points out;
  * a PENDING order's trigger is converted BACK to source terms before it is sent,
    so the venue triggers at the level the client meant;
  * a MARKET order sends no price at all, as before - inventing one would turn a
    market order into a limit order at the venue.

WHO KEEPS THE VENUE'S IMPROVEMENT - configurable, default the CLIENT
====================================================================
`BROKER_ABOOK_IMPROVEMENT=client` (default): the broker earns its configured markup
and no more; whatever the venue filled at flows through. In the scenario above the
client is booked at 1.10020, not 1.10030, and the broker still earns 20 points.

`BROKER_ABOOK_IMPROVEMENT=broker`: the client pays their quoted price, so the broker
also keeps the venue's improvement - 30 points in the same scenario.

THE FLOOR, which is not configurable
====================================
The client is never booked worse than their quoted price plus their allowed
slippage. A venue fill that gapped through the quote is CAPPED and flagged for
reconciliation, with the broker absorbing the difference, because "the LP filled
badly" is not a price the client agreed to. Capping is logged loudly and carried on
the DEAL_CREATED event as a reconciliation flag.

Failure mode: if the client price cannot be derived honestly - no tick_size, no raw
quote to measure a configured markup against, a non-positive result - this raises
ABookQuoteError and the booking is flagged RECONCILIATION_REQUIRED rather than
falling back to the venue price. The hedge is already live at that point, so
silently booking at the raw venue price would be the quiet version of the original
bug: the broker earns nothing and nobody is told.

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
        o = old.replace("\n", nl) if nl == "\r\n" else old
        n = new.replace("\n", nl) if nl == "\r\n" else new
        if src.count(o) != 1:
            # Only treat it as already-applied when the OLD anchor is gone AND the
            # new text is present EXACTLY once as a whole block. Counting a
            # substring of `new` is not enough: a long replacement contains its own
            # leading lines, so a partial run re-applies the head and duplicates it.
            if src.count(o) == 0 and src.count(n) == 1:
                print(f"  skip (already patched): {path}")
                continue
            raise AssertionError(
                f"{path}: anchor found {src.count(o)}x (already-applied={src.count(n)}): "
                f"{old[:80]!r}")
        src = src.replace(o, n, 1)
        changed = True
    if changed:
        ast.parse(src.replace("\r\n", "\n"))
        io.open(path, "w", encoding="utf-8", newline="").write(src)
        applied.append(path)


ORCH = "application/services/execution_orchestrator.py"

# ------------------------------------------------------------------- imports
patch(ORCH, [(
    "from application.services.dealer_queue_service import DealerQueueService\n",
    "from application.services.dealer_queue_service import DealerQueueService\n"
    "from core.domains.market_data.feed_access import await_tick, tick_ask, tick_bid\n"
    "from core.domains.pricing.a_book import (\n"
    "    ABookQuoteError,\n"
    "    client_fill_price,\n"
    "    venue_price_for_instruction,\n"
    ")\n",
)])

# --------------------------------------------- the improvement policy + module
patch(ORCH, [(
    '_LP_FILL_STATUSES = frozenset({"FILLED", "PARTIAL", "PARTIALLY_FILLED"})\n',
    '''_LP_FILL_STATUSES = frozenset({"FILLED", "PARTIAL", "PARTIALLY_FILLED"})

#: M13: who keeps the venue's price improvement. "client" (the default) means the
#: broker earns exactly its configured markup and the venue's own movement flows
#: through to the client; "broker" means the client always pays their quoted price.
#: Configurable per deployment now, per group later - the resolution point is
#: _improvement_to_client(), which is the only place this is read.
_IMPROVEMENT_TO_CLIENT = frozenset({"", "client", "true", "1", "yes", "pass_through"})


def _improvement_to_client(account: Any = None) -> bool:
    """Resolve the improvement policy for this fill.

    Reads the account's group first so a per-group override can be added without
    touching any call site, then the environment. An unrecognised environment value
    fails LOUDLY at first use rather than silently defaulting: this setting decides
    who keeps real money, so a typo must not quietly change the answer.
    """
    import os as _os

    group = getattr(account, "group", None)
    override = getattr(group, "abook_improvement", None)
    if override is not None:
        return str(override).strip().lower() in _IMPROVEMENT_TO_CLIENT
    raw = (_os.environ.get("BROKER_ABOOK_IMPROVEMENT") or "").strip().lower()
    if raw and raw not in _IMPROVEMENT_TO_CLIENT and raw not in {"broker", "false", "0", "no"}:
        logger.error(
            "BROKER_ABOOK_IMPROVEMENT=%r is not recognised; using 'client'. Valid "
            "values are 'client' (default: the venue's improvement passes through) "
            "and 'broker' (the client pays their quoted price).", raw,
        )
        return True
    return raw in _IMPROVEMENT_TO_CLIENT
''',
)])

# ------------------------------------- replace _lp_fill_price with the derivation
patch(ORCH, [(
    '''    @staticmethod
    def _lp_fill_price(order: Order, report: dict, flags: list) -> Decimal:
        """The price the client fills at: the LP's average price.

        A FILLED report with no AvgPx is a malformed report, not a licence to pick
        a number. But the hedge is already live, so refusing to book is worse than
        booking at the client's instruction price and flagging it for the back
        office - which is what this does, loudly.
        """''',
    '''    @staticmethod
    def _lp_fill_price(order: Order, report: dict, flags: list) -> Decimal:
        """The price the VENUE filled at, or the order's own price if it did not say.

        M13: this is no longer the price the CLIENT is booked at - that is derived
        from it by `_client_fill_price`, which applies the group's markup. This
        method answers only "what did the venue charge us".

        A FILLED report with no AvgPx is a malformed report, not a licence to pick
        a number. But the hedge is already live, so refusing to book is worse than
        booking at the order's instruction price and flagging it for the back
        office - which is what this does, loudly.
        """''',
)])

# ------------------------------------------- the client-price derivation
patch(ORCH, [(
    '''    @staticmethod
    def _lp_fill_volume(order: Order, report: dict, flags: list) -> Decimal:''',
    '''    async def _client_fill_price(self, order: Order, account: Any, venue_price: Decimal,
                                 flags: list) -> Optional[Decimal]:
        """What the CLIENT is booked at, given what the venue filled at. M13.

        Returns None when it cannot be derived honestly; the caller treats that as a
        reconciliation break rather than falling back to the venue price, because
        booking the client at the raw venue price is the quiet version of the bug
        this fixes - the broker earns nothing and nobody is told.
        """
        symbol_cfg = None
        if self.symbol_repo is not None:
            try:
                symbol_cfg = await self.symbol_repo.find_by_name(order.symbol)
            except Exception as exc:  # noqa: BLE001
                logger.error("cannot load symbol %s to price an A-Book fill: %s",
                             order.symbol, exc)

        raw_bid = raw_ask = None
        tick = await await_tick(self.market_feed, order.symbol) if self.market_feed else None
        if tick is not None:
            raw_bid, raw_ask = tick_bid(tick), tick_ask(tick)

        is_buy = order.order_type.name.startswith("BUY")
        quoted = getattr(getattr(order, "price_order", None), "value", None)

        try:
            priced = client_fill_price(
                venue_price=venue_price,
                raw_bid=(Decimal(str(raw_bid)) if raw_bid is not None else None),
                raw_ask=(Decimal(str(raw_ask)) if raw_ask is not None else None),
                symbol=symbol_cfg,
                group=getattr(account, "group", None),
                side=("BUY" if is_buy else "SELL"),
                quoted_price=(Decimal(str(quoted)) if quoted else None),
                max_slippage_points=(
                    Decimal(str(order.deviation)) if getattr(order, "deviation", None) else None
                ),
                improvement_to_client=_improvement_to_client(account),
            )
        except ABookQuoteError as exc:
            logger.error(
                "cannot derive a client price for A-Book order %s: %s. The hedge is "
                "live at the venue and the client side is NOT booked - this is a "
                "reconciliation break, not a fallback.", order.ticket_id, exc,
            )
            flags.append(f"client price could not be derived: {exc}")
            return None
        except (ArithmeticError, ValueError, TypeError) as exc:
            logger.error(
                "pricing A-Book order %s raised %s: %s - treating as a break rather "
                "than guessing a price", order.ticket_id, type(exc).__name__, exc,
            )
            flags.append(f"client pricing failed: {type(exc).__name__}: {exc}")
            return None

        if priced.capped:
            flags.append(
                f"venue filled at {priced.venue_price} but the client was capped at "
                f"{priced.client_price} (their quote plus allowed slippage); the "
                f"broker absorbs the difference"
            )
        logger.info(
            "A-Book order %s: venue filled %s at %s, client booked at %s "
            "(markup %s, improvement passed to client %s, SpreadDiff %d)",
            order.ticket_id, order.symbol, priced.venue_price, priced.client_price,
            priced.markup_earned, priced.improvement_passed_through, priced.spread_diff,
        )
        self._last_a_book_pricing = priced
        return priced.client_price

    async def _venue_instruction_price(self, order: Order, account: Any) -> Optional[Decimal]:
        """The trigger price to send the venue for a PENDING order. M13.

        Converts the client's marked-up instruction back to source terms, per the
        guide: "The ECN converts the price to the original one 1.15659 and passes it
        to the external system." Without this the venue triggers a markup late, and
        the client's instruction is not honoured.

        Returns None for a market order - there is nothing to convert, and inventing
        a price would turn a market order into a limit order at the venue.
        """
        if order.is_market():
            return None
        client_px = getattr(getattr(order, "price_order", None), "value", None)
        if client_px is None:
            return None
        symbol_cfg = None
        if self.symbol_repo is not None:
            try:
                symbol_cfg = await self.symbol_repo.find_by_name(order.symbol)
            except Exception:  # noqa: BLE001
                symbol_cfg = None
        raw_bid = raw_ask = None
        tick = await await_tick(self.market_feed, order.symbol) if self.market_feed else None
        if tick is not None:
            raw_bid, raw_ask = tick_bid(tick), tick_ask(tick)
        try:
            return venue_price_for_instruction(
                client_instruction_price=Decimal(str(client_px)),
                raw_bid=(Decimal(str(raw_bid)) if raw_bid is not None else None),
                raw_ask=(Decimal(str(raw_ask)) if raw_ask is not None else None),
                symbol=symbol_cfg,
                group=getattr(account, "group", None),
                side=("BUY" if order.order_type.name.startswith("BUY") else "SELL"),
            )
        except (ABookQuoteError, ArithmeticError, ValueError, TypeError) as exc:
            logger.error(
                "cannot convert the instruction price for pending A-Book order %s: %s "
                "- sending the client price unchanged, so the venue trigger will be "
                "offset by the group's markup", order.ticket_id, exc,
            )
            return Decimal(str(client_px))

    @staticmethod
    def _lp_fill_volume(order: Order, report: dict, flags: list) -> Decimal:''',
)])

# ------------------------------------------- use it in the booking path
patch(ORCH, [(
    '''        flags = []
        fill_price = self._lp_fill_price(order, report, flags)
        fill_volume = self._lp_fill_volume(order, report, flags)''',
    '''        flags = []
        venue_price = self._lp_fill_price(order, report, flags)
        fill_volume = self._lp_fill_volume(order, report, flags)
        # M13: the client is booked at their price, not the venue's. The markup the
        # group configures is what the broker earns on hedged flow; before this the
        # venue's price was booked directly and the markup was discarded.
        fill_price = await self._client_fill_price(order, account, venue_price, flags)
        if fill_price is None:
            logger.error(
                "order %s was FILLED at gateway %s but no honest client price could be "
                "derived; the hedge is live and the client side is unbooked",
                order.ticket_id, gateway_id,
            )
            await self._publish_a_book_reconciliation(
                order, gateway_id, report, "CLIENT_PRICE_UNDERIVABLE")
            return''',
)])

# --------------------------------- carry the markup onto the routing event
patch(ORCH, [(
    '''                    "remaining_volume": str(order.volume_current.value),
                    "reconciliation_flags": list(flags),''',
    '''                    "remaining_volume": str(order.volume_current.value),
                    "reconciliation_flags": list(flags),
                    # M13: the venue's price and the client's are different numbers,
                    # and the gap is the broker's revenue. Both are carried so the
                    # markup is auditable per deal instead of being buried in a fill
                    # price that looks like any other.
                    "venue_price": str(venue_price),
                    "client_price": str(fill_price),
                    "markup_earned": str(
                        getattr(self, "_last_a_book_pricing", None)
                        and self._last_a_book_pricing.markup_earned or Decimal("0")
                    ),
                    "improvement_to_client": bool(
                        getattr(self, "_last_a_book_pricing", None)
                        and self._last_a_book_pricing.improvement_passed_through
                    ),''',
)])

# --------------------------------------- __init__: the per-fill pricing slot
patch(ORCH, [(
    "        self.uow_factory = uow_factory\n",
    "        self.uow_factory = uow_factory\n"
    "        #: M13: the last A-Book pricing decision, so the booking path can put the\n"
    "        #: venue price, the client price and the markup on the deal event. Set per\n"
    "        #: fill; read immediately after, on the same task.\n"
    "        self._last_a_book_pricing = None\n",
)])

print(f"applied to {len(set(applied))} file(s):")
for f in sorted(set(applied)):
    print("  ", f)
