"""M6 patch (item 2+3): netting books its realised PnL, and the mode dispatch
follows the MT5 SDK instead of an attribute that does not exist.

Defects:
1. `_apply_deal_to_positions` dispatched on `account.group.execution.mode` —
   Group has no `execution` attribute, so the hasattr guard yielded None and
   EVERY account ran the hedging branch. The netting branch was unreachable
   dead code — which is why nobody noticed defect 2.
2. `_apply_deal_netting_mode` reduced or deleted positions WITHOUT booking the
   realised result: the client's profit/loss vanished (M4 debt #2, "the same
   class of defect as #16, on the netting branch").
3. `ClosePositionHandler` added raw PnL to the balance with no currency
   conversion — a USDJPY close would add a JPY amount to a USD balance.

Authoritative mapping (MT5 SDK, IMTConGroup::EnMarginMode):
    MARGIN_MODE_RETAIL (0)          -> netting position accounting
    MARGIN_MODE_EXCHANGE_DISCOUNT   -> netting (exchange)
    MARGIN_MODE_RETAIL_HEDGED (2)   -> hedging position accounting
The group's MarginProfile.mode already carries this from the wire (MarginMode).
Unknown/absent mode keeps the historical default: HEDGING.

Realised PnL goes through RiskEngine.realized_pnl -> margin.position_pnl: the
same single source of truth the margin loop uses, with quote->deposit
conversion at the profit-currency rate. No new formula is introduced.
"""
import ast
import io
import pathlib


def read(path):
    p = pathlib.Path(path)
    src = io.open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in src else "\n"
    return src, nl


def write(path, src):
    ast.parse(src.replace("\r\n", "\n"))
    io.open(path, "w", encoding="utf-8", newline="").write(src)


def apply(path, pairs):
    src, nl = read(path)
    for old, new in pairs:
        old = old.replace("\n", nl) if nl == "\r\n" else old
        new = new.replace("\n", nl) if nl == "\r\n" else new
        assert src.count(old) == 1, f"{path}: anchor not found/ambiguous: {old[:70]!r}"
        src = src.replace(old, new)
    write(path, src)
    print(f"{path}: {len(pairs)} patch(es)")


# ---------------------------------------------------------------------------
# 1. RiskEngine.realized_pnl — the one place realised results are computed
# ---------------------------------------------------------------------------
import pathlib as _pl
if "def realized_pnl(" not in io.open("core/domains/risk/engine.py", encoding="utf-8").read():
        apply(
            "core/domains/risk/engine.py",
            [(
            """    def calculate_margin_level(
    """,
            """    def realized_pnl(
            self,
            account: Account,
            position: Position,
            close_price: Decimal,
            closed_volume: Decimal,
        ) -> Decimal:
            \"\"\"PnL realised by closing `closed_volume` lots of `position` at `close_price`.

            Returned in the ACCOUNT's deposit currency. This is position_pnl with the
            deal price on the closing side (a long is closed by selling, at its bid;
            a short by buying, at its ask), so quote->deposit conversion uses exactly
            the machinery the margin loop uses - no second formula, and no raw
            quote-currency amount ever lands on a balance.
            \"\"\"
            spec = self._spec(position.symbol)
            symbol = self._symbol(position.symbol)
            quote_currency = getattr(symbol, \"quote_currency\", \"\") or spec.margin_currency
            action = (
                position.action.value
                if hasattr(position.action, \"value\")
                else str(position.action)
            )
            return position_pnl(
                side=action,
                volume_lots=closed_volume,
                open_price=position.price_open.value,
                bid=close_price,
                ask=close_price,
                contract_size=spec.contract_size,
                quote_currency=quote_currency,
                deposit_currency=account.currency,
                rate_lookup=self._rate_lookup,
            )

        def calculate_margin_level(
    """,
        )],
    )

# ---------------------------------------------------------------------------
# 2. record_deal: SDK-based dispatch + netting books realised PnL
# ---------------------------------------------------------------------------
apply(
    "application/commands/record_deal.py",
    [
        (
            """        group_mode = account.group.execution.mode if hasattr(account.group, 'execution') and hasattr(account.group.execution, 'mode') else None  # HEDGING or NETTING
""",
            """        # MT5 SDK, IMTConGroup::EnMarginMode: MARGIN_MODE_RETAIL (0) and the
        # exchange modes use NETTING position accounting; MARGIN_MODE_RETAIL_HEDGED
        # (2) uses HEDGING. The group's MarginProfile.mode carries this straight
        # off the wire (MarginMode). This previously read
        # `account.group.execution.mode` - an attribute Group does not have - so
        # the guard yielded None and every account silently ran hedging: the
        # netting branch was unreachable code.
        margin_mode = getattr(getattr(account.group, 'margin', None), 'mode', None)
        group_mode = margin_mode  # HEDGING or NETTING, per EnMarginMode
""",
        ),
        (
            """        if (hasattr(group_mode, 'name') and group_mode.name in ["EXCHANGE", "NETTING"]):
""",
            """        mode_name = getattr(group_mode, 'name', str(group_mode) if group_mode else "")
        if mode_name in ("RETAIL", "EXCHANGE_DISCOUNT", "EXCHANGE", "NETTING"):
            # MarginMode.RETAIL is MT5's netting accounting (SDK: "The netting
            # position accounting system is used"); EXCHANGE_DISCOUNT likewise.
""",
        ),
        (
            """    async def _apply_deal_netting_mode(self, account: Account, deal: Deal, symbol, position_repo=None, session=None):
        \"\"\"
        Netting: Opposite deals reduce/close existing positions.
        Same direction adds to position.
        \"\"\"
""",
            """    async def _apply_deal_netting_mode(self, account: Account, deal: Deal, symbol, position_repo=None, session=None):
        \"\"\"
        Netting: Opposite deals reduce/close existing positions.
        Same direction adds to position.

        Every reduction books its realised PnL to the balance (M6): before this,
        the closed volume - and the client's profit or loss with it - simply
        disappeared, and the account kept trading with money it had already lost
        or earned. The result is computed by RiskEngine.realized_pnl, i.e. the
        same converted, side-correct maths the margin loop uses.
        \"\"\"
""",
        ),
        (
            """            if opposite_positions:
                opp_pos = opposite_positions[0]
                if deal.volume.value < opp_pos.volume.value:
                    opp_pos.volume = Volume(opp_pos.volume.value - deal.volume.value)
""",
            """            if opposite_positions:
                opp_pos = opposite_positions[0]
                if deal.volume.value < opp_pos.volume.value:
                    await self._book_netting_realized(
                        account, deal, opp_pos, deal.volume.value, session=session
                    )
                    opp_pos.volume = Volume(opp_pos.volume.value - deal.volume.value)
""",
        ),
        (
            """                elif deal.volume.value == opp_pos.volume.value:
                    if hasattr(pos_repo, 'delete'):
                        await pos_repo.delete(opp_pos.position_id)
                    logger.debug(f"Position {opp_pos.position_id} fully closed (Netting)")
""",
            """                elif deal.volume.value == opp_pos.volume.value:
                    await self._book_netting_realized(
                        account, deal, opp_pos, opp_pos.volume.value, session=session
                    )
                    if hasattr(pos_repo, 'delete'):
                        await pos_repo.delete(opp_pos.position_id)
                    logger.debug(f"Position {opp_pos.position_id} fully closed (Netting)")
""",
        ),
        (
            """                else:
                    if hasattr(pos_repo, 'delete'):
                        await pos_repo.delete(opp_pos.position_id)
                    position_id = f"{account.login}_{deal.symbol}_{str(uuid.uuid4())[:8]}"
""",
            """                else:
                    # Reversal: the whole old position closes at the deal price
                    # (its PnL is realised), and the remainder reopens flat.
                    await self._book_netting_realized(
                        account, deal, opp_pos, opp_pos.volume.value, session=session
                    )
                    if hasattr(pos_repo, 'delete'):
                        await pos_repo.delete(opp_pos.position_id)
                    position_id = f"{account.login}_{deal.symbol}_{str(uuid.uuid4())[:8]}"
""",
        ),
        (
            """    @staticmethod
    async def _positions_for_account(pos_repo, account_login: int, session=None) -> List[Position]:
""",
            """    async def _book_netting_realized(
        self, account: Account, deal: Deal, position: Position,
        closed_volume: Decimal, session=None,
    ) -> None:
        \"\"\"Book the realised result of a netting close onto the balance.

        The OUT deal also carries the realised profit, the way MT5's statements
        show it, and is re-saved so the ledger matches the balance movement.
        The account itself is persisted by the caller's flow (margin
        recalculation runs after this and the account save follows it).
        \"\"\"
        from core.domains.risk.engine import RiskEngine

        engine = RiskEngine(symbol_repo=self.symbol_repo, market_data_engine=self.market_feed)
        realized = engine.realized_pnl(
            account, position, deal.price.value, Decimal(str(closed_volume))
        )
        account.balance = Money(account.balance.amount + realized, account.currency)
        deal.profit = Money(realized, account.currency)
        if hasattr(self.deal_repo, 'save'):
            if _accepts_session(self.deal_repo.save):
                await self.deal_repo.save(deal, session=session)
            else:
                await self.deal_repo.save(deal)
        logger.info(
            "netting close: %s %s of %s realised %s %s",
            closed_volume, position.action, position.symbol, realized, account.currency,
        )

    @staticmethod
    async def _positions_for_account(pos_repo, account_login: int, session=None) -> List[Position]:
""",
        ),
    ],
)

# ---------------------------------------------------------------------------
# 3. ClosePositionHandler: converted PnL when it has an engine
# ---------------------------------------------------------------------------
apply(
    "application/commands/close_position.py",
    [
        (
            """    def __init__(
        self,
        account_repo: IAccountRepository,
        position_repo: IPositionRepository,
        order_repo: IOrderRepository,
        deal_repo: IDealRepository,
        event_bus: IEventBus,
    ):
        self.account_repo = account_repo
        self.position_repo = position_repo
        self.order_repo = order_repo
        self.deal_repo = deal_repo
        self.event_bus = event_bus
""",
            """    def __init__(
        self,
        account_repo: IAccountRepository,
        position_repo: IPositionRepository,
        order_repo: IOrderRepository,
        deal_repo: IDealRepository,
        event_bus: IEventBus,
        risk_engine=None,
    ):
        self.account_repo = account_repo
        self.position_repo = position_repo
        self.order_repo = order_repo
        self.deal_repo = deal_repo
        self.event_bus = event_bus
        # Optional since M6: with an engine, the realised result is converted
        # quote->deposit (a USDJPY close used to add a raw JPY amount to a USD
        # balance). Without one, the legacy same-currency maths is kept and a
        # warning is logged, because the alternative - refusing - would break
        # single-currency setups that never needed conversion.
        self.risk_engine = risk_engine
""",
        ),
        (
            """        # 6. Calculate realized PnL
        if position.action == PositionAction.BUY:
            price_diff = current_price - position.price_open.value
        else:
            price_diff = position.price_open.value - current_price

        realized_pnl = price_diff * close_volume * position.contract_size
        realized_pnl_money = Money(realized_pnl, position.profit.currency)
""",
            """        # 6. Calculate realized PnL
        account_for_pnl = await self.account_repo.find_by_login(command.account_login)
        if self.risk_engine is not None and account_for_pnl is not None:
            # Converted, side-correct, single source of truth (margin.position_pnl).
            realized_pnl = self.risk_engine.realized_pnl(
                account_for_pnl, position, current_price, close_volume
            )
            realized_pnl_money = Money(realized_pnl, account_for_pnl.currency)
        else:
            if self.risk_engine is None:
                logger.warning(
                    "ClosePositionHandler has no risk_engine: realised PnL is NOT "
                    "currency-converted (correct only when quote == account currency)"
                )
            if position.action == PositionAction.BUY:
                price_diff = current_price - position.price_open.value
            else:
                price_diff = position.price_open.value - current_price
            realized_pnl = price_diff * close_volume * position.contract_size
            realized_pnl_money = Money(realized_pnl, position.profit.currency)
""",
        ),
        (
            """        account = await self.account_repo.find_by_login(command.account_login)
        if account:
            account.balance = Money(account.balance.amount + realized_pnl, account.currency)
""",
            """        account = account_for_pnl
        if account:
            account.balance = Money(account.balance.amount + realized_pnl, account.currency)
""",
        ),
    ],
)

print("all item-2 patches applied")
