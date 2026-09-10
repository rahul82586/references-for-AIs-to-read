import io

p = "application/workers/liquidation_worker.py"
s = io.open(p, encoding="utf-8", newline="").read()
crlf = "\r\n" in s


def N(x):
    return x.replace("\n", "\r\n") if crlf else x


# --- 1. accept the platform's RiskEngine ------------------------------------
old = N('''        event_bus: IEventBus,
        liquidation_service: LiquidationService,
    ):''')
assert old in s
new = N('''        event_bus: IEventBus,
        liquidation_service: LiquidationService,
        risk_engine: Optional[Any] = None,
    ):''')
s = s.replace(old, new, 1)

old = N('''        self.liquidation_service = liquidation_service
        
        self._running = False''')
assert old in s
new = N('''        self.liquidation_service = liquidation_service
        #: The platform's RiskEngine, built against the synchronous ConfigCache symbol
        #: view. Optional only for backwards compatibility; without it this worker builds
        #: one from the async symbol repository, and RiskEngine._symbol() refuses an async
        #: lookup - so margin would fail to recompute after a liquidation.
        self.risk_engine = risk_engine

        self._running = False''')
s = s.replace(old, new, 1)

# --- 2. reuse it for conversion rates ---------------------------------------
old = N('''        from core.domains.risk.engine import RiskEngine

        conversion_engine = RiskEngine(
            symbol_repo=self.symbol_repo, market_data_engine=self.market_data_feed
        )''')
assert old in s
new = N('''        from core.domains.risk.engine import RiskEngine

        conversion_engine = self.risk_engine or RiskEngine(
            symbol_repo=self.symbol_repo, market_data_engine=self.market_data_feed
        )''')
s = s.replace(old, new, 1)

# --- 3. step 6: the engine, not a private formula ---------------------------
old = N('''        remaining_positions = await self.position_repo.get_by_account(account_login)
        total_margin_used = Decimal('0')
        total_pnl = Decimal('0')
        
        for pos in remaining_positions:
            # Simplified margin calculation
            margin_required = pos.calculate_margin_required(
                margin_rate=Decimal('1.0'),
                leverage=account.effective_leverage()
            )
            total_margin_used += margin_required
            total_pnl += pos.profit.amount
        
        account.margin_used = Money(total_margin_used, account.currency)
        account.equity = Money(account.balance.amount + total_pnl, account.currency)
        account.margin_free = Money(account.equity.amount - account.margin_used.amount, account.currency)
        
        if account.margin_used.amount > Decimal('0'):
            account.recompute_margin_level()
        else:
            account.margin_level = Decimal('999999')
''')
assert old in s, "step 6 block not found"
new = N('''        remaining_positions = await self.position_repo.get_by_account(account_login)

        # Recomputed through the same MT5-accurate engine every other margin figure in
        # the platform comes from. This used to sum Position.calculate_margin_required(),
        # a sixth independent formula: volume * contract * PRICE_OPEN / leverage. Three
        # things were wrong with it here - it valued margin at the entry price instead of
        # the current one, it applied no currency conversion at all (so a USDJPY position
        # on a USD account was margined in yen), and it ignored the maintenance rates and
        # the per-symbol aggregation the engine handles. The numbers it wrote are exactly
        # what the stop-out recovery check below compares against, so an account could be
        # declared recovered - or never recovered - on a figure nothing else agreed with.
        total_margin_used = Decimal('0')
        total_pnl = Decimal('0')
        snapshot = None
        try:
            snapshot = conversion_engine.calculate_margin_level(account, remaining_positions)
        except Exception as exc:  # noqa: BLE001 - fall back, but say so loudly
            logger.error(
                "could not recompute margin for %s through the risk engine after "
                "liquidation: %s. Falling back to per-position PnL with zero margin, "
                "which will read as fully recovered - verify this account manually.",
                account_login, exc,
            )

        if snapshot is not None:
            total_margin_used = snapshot.margin_used
            account.margin_used = Money(snapshot.margin_used, account.currency)
            account.equity = Money(snapshot.equity, account.currency)
            account.margin_free = Money(snapshot.margin_free, account.currency)
            account.margin_level = snapshot.margin_level
        else:
            for pos in remaining_positions:
                total_pnl += pos.profit.amount
            account.equity = Money(account.balance.amount + total_pnl, account.currency)
            account.margin_used = Money(Decimal('0'), account.currency)
            account.margin_free = Money(account.equity.amount, account.currency)
            account.margin_level = Decimal('999999')

        if snapshot is None and account.margin_used.amount > Decimal('0'):
            account.recompute_margin_level()
''')
s = s.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="").write(s)
print("liquidation_worker: engine-based margin; crlf =", crlf)

# --- 4. trading_setup passes the engine in ----------------------------------
p = "application/di/trading_setup.py"
s = io.open(p, encoding="utf-8").read()
old = '''        liquidation_service=liquidation_service,
    )'''
assert old in s
new = '''        liquidation_service=liquidation_service,
        risk_engine=risk_engine,
    )'''
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("trading_setup: risk_engine injected into the worker")
