"""M5 patch: make GET /api/v1/account/positions answer truthfully.

The cloud proof placed a real order (FILLED, margin 107.96 USD booked in Neon,
equity 9,999.00) and then asked the client API for open positions. It answered
`[]` - while the account demonstrably held one. Three independent layers, each
silently fatal, exactly the class M4 hunted:

1. Nothing ever registered "positions_query_handler" in the DI container, so
   the route's `if handler:` was false and it returned [] for EVERY caller.
2. The route swallowed handler exceptions with `except Exception: pass` and
   returned [] - "no positions" and "positions query is broken" looked identical.
3. GetPositionsQueryHandler was written against the PRE-M3 entity vocabulary
   (pos.side / pos.average_price / pos.id - all renamed to action / price_open /
   position_id) and computed PnL with NO currency conversion: the sixth
   independent formula M3's cleanup never reached, because nothing called it.

Fixes: RiskEngine gains calculate_position_pnl() (one position, deposit
currency, through margin.position_pnl - the single source of truth); the
handler is rewritten onto the real vocabulary and REFUSES to report zero PnL
when it has no engine; the route names its failures (503 unwired / 500 with a
logged traceback); api/main.py registers the handler with the live stack.
Also: root logging at INFO so the wiring log is visible under bare uvicorn.
"""
import ast
import io
import pathlib


def patch(path, pairs, newline_style=None):
    p = pathlib.Path(path)
    src = io.open(p, encoding="utf-8", newline="").read()
    for old, new in pairs:
        assert src.count(old) == 1, f"{path}: anchor not found or ambiguous: {old[:60]!r}"
        src = src.replace(old, new)
    ast.parse(src)
    io.open(p, "w", encoding="utf-8", newline="").write(src)
    print(f"{path}: {len(pairs)} patch(es)")


# ---------------------------------------------------------------------------
# 1. RiskEngine.calculate_position_pnl — single position, single formula
# ---------------------------------------------------------------------------
patch(
    "core/domains/risk/engine.py",
    [(
        "    def calculate_margin_level(\n",
        '''    def calculate_position_pnl(self, account: Account, position: Position) -> Decimal:
        """Unrealised PnL for ONE position, in the account's deposit currency.

        The same single source of truth calculate_margin_level uses
        (margin.position_pnl): side-correct bid/ask, the symbol's contract size,
        and quote->deposit conversion. Added in M5 because the client positions
        query carried its own PRE-M3 formula (pos.side / pos.average_price, no
        currency conversion) on an endpoint nothing had ever called - the sixth
        independent copy of the PnL maths, in the layer that reads money.
        """
        spec = self._spec(position.symbol)
        symbol = self._symbol(position.symbol)
        quote_currency = getattr(symbol, "quote_currency", "") or spec.margin_currency
        action = (
            position.action.value
            if hasattr(position.action, "value")
            else str(position.action)
        )
        return position_pnl(
            side=action,
            volume_lots=position.volume.value,
            open_price=position.price_open.value,
            bid=self._side_price(position.symbol, "bid"),
            ask=self._side_price(position.symbol, "ask"),
            contract_size=spec.contract_size,
            quote_currency=quote_currency,
            deposit_currency=account.currency,
            rate_lookup=self._rate_lookup,
        )

    def calculate_margin_level(
''',
    )],
)

# ---------------------------------------------------------------------------
# 2. GetPositionsQueryHandler — real vocabulary, honest about valuation
# ---------------------------------------------------------------------------
gp = pathlib.Path("application/queries/get_positions.py")
src = io.open(gp, encoding="utf-8", newline="").read()
head_end = src.index("class GetPositionsQueryHandler:")
new_body = '''class GetPositionsQueryHandler:
    """Read-side query handler for active open positions.

    M5 rewrite: this handler was written against the pre-M3 Position vocabulary
    (pos.side / pos.average_price / pos.id) and computed PnL without currency
    conversion. The renames made every attribute access raise, and the route
    swallowed it into an empty list, so the endpoint reported "no positions"
    for accounts that held some. Valuation now goes through
    RiskEngine.calculate_position_pnl - the same single source of truth the
    margin loop and the liquidation worker use. Without an engine and an
    account it REFUSES to answer rather than reporting a comfortable zero.
    """

    def __init__(
        self,
        position_repo: IPositionRepository,
        market_data_engine: Optional[Any] = None,
        symbol_repo: Optional[ISymbolRepository] = None,
        account_repo: Optional[IAccountRepository] = None,
        risk_engine: Optional[Any] = None,
    ):
        self.position_repo = position_repo
        self.market_data_engine = market_data_engine
        self.symbol_repo = symbol_repo
        self.account_repo = account_repo
        self.risk_engine = risk_engine

    async def handle(self, query: GetPositionsQuery) -> List[dict]:
        """Process GetPositionsQuery and return open positions list."""
        positions = await self.position_repo.get_positions_by_account(query.account_login)
        if not positions:
            return []

        if self.risk_engine is None or self.account_repo is None:
            raise RuntimeError(
                "GetPositionsQueryHandler cannot value positions without a risk_engine "
                "and an account_repo; refusing to report unrealized_pnl=0 for real "
                "positions (register it with the trading stack, as api/main.py does)"
            )
        account = await self.account_repo.find_by_login(query.account_login)
        if account is None:
            raise RuntimeError(
                f"account {query.account_login} holds {len(positions)} position(s) "
                "but cannot be loaded; refusing to guess its deposit currency"
            )

        results = []
        for pos in positions:
            action = pos.action.value if hasattr(pos.action, "value") else str(pos.action)
            results.append(
                {
                    "position_id": str(pos.position_id),
                    "symbol": pos.symbol,
                    "side": action,
                    "volume": pos.volume.value,
                    "average_price": pos.price_open.value,
                    "unrealized_pnl": self.risk_engine.calculate_position_pnl(account, pos),
                    "swap": (
                        pos.swap.amount
                        if getattr(pos, "swap", None) is not None
                        and hasattr(pos.swap, "amount")
                        else Decimal("0")
                    ),
                }
            )
        return results
'''
src = src[:head_end] + new_body

# the rewritten body needs IAccountRepository in the header imports
if "IAccountRepository" not in src.split("class GetPositionsQueryHandler")[0]:
    old_imp = "from core.ports.interfaces import IPositionRepository, ISymbolRepository"
    new_imp = "from core.ports.interfaces import (\n    IAccountRepository,\n    IPositionRepository,\n    ISymbolRepository,\n)"
    if src.count(old_imp) == 1:
        src = src.replace(old_imp, new_imp)
    else:
        # header import shape differs; add a standalone import after the first import line
        marker = "from core.ports.interfaces import"
        idx = src.index(marker)
        end = src.index("\n", idx)
        src = src[: end + 1] + "from core.domains.accounts.account import Account  # noqa: F401\n" + src[end + 1 :]

# match the file's newline style (CRLF) so the file stays consistent
if "\r\n" in src[:head_end]:
    body_start = head_end
    head = src[:body_start]
    body = src[body_start:].replace("\r\n", "\n").replace("\n", "\r\n")
    src = head + body

ast.parse(src.replace("\r\n", "\n"))
io.open(gp, "w", encoding="utf-8", newline="").write(src)
print("application/queries/get_positions.py: handler rewritten")

# ---------------------------------------------------------------------------
# 3. The route: name failures instead of returning []
# ---------------------------------------------------------------------------
patch(
    "api/routers/account.py",
    [
        (
            "from typing import List, Optional\r\n",
            "import logging\r\nfrom typing import List, Optional\r\n",
        ),
        (
            "router = APIRouter(",
            "logger = logging.getLogger(__name__)\r\n\r\nrouter = APIRouter(",
        ),
        (
            '''    login_val = current_user.login if hasattr(current_user, 'login') else getattr(current_user, 'login_id', 100001)\r
    if handler:\r
        try:\r
            query = GetPositionsQuery(account_login=login_val)\r
            positions_list = await handler.handle(query)\r
            return [PositionResponse(**p) for p in positions_list]\r
        except Exception:\r
            pass\r
\r
    return []\r'''.replace("\r\n", "\r").replace("\r", "\r\n"),
            '''    login_val = current_user.login if hasattr(current_user, 'login') else getattr(current_user, 'login_id', 100001)\r
    if handler is None:\r
        # Pre-M5 this silently returned []: "no open positions" and "the query\r
        # is not wired" looked identical to the client, whose account held a\r
        # real, margined position. A missing handler is a server misconfiguration.\r
        logger.error("positions_query_handler is not registered; /account/positions cannot answer")\r
        raise HTTPException(\r
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,\r
            detail="Positions query is not wired on this server",\r
        )\r
    try:\r
        query = GetPositionsQuery(account_login=login_val)\r
        positions_list = await handler.handle(query)\r
    except Exception:\r
        # Log the traceback and fail loudly. Swallowing into [] told the client\r
        # it was flat while its margin said otherwise.\r
        logger.exception("get_positions failed for login=%s", login_val)\r
        raise HTTPException(\r
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,\r
            detail="Could not value open positions",\r
        )\r
    return [PositionResponse(**p) for p in positions_list]\r'''.replace("\r\n", "\r").replace("\r", "\r\n"),
        ),
    ],
)

# ---------------------------------------------------------------------------
# 4. api/main.py: register the handler with the live stack + INFO logging
# ---------------------------------------------------------------------------
patch(
    "api/main.py",
    [
        (
            "import logging\r\nimport os\r\n",
            "import logging\r\nimport os\r\n\r\n"
            "# M5: the wiring story (trading plane, Redis bus, price source) is logged at\r\n"
            "# INFO. Under bare uvicorn the root logger only shows WARNING+, so an operator\r\n"
            "# could not see what the server had assembled - or that it had fallen back to\r\n"
            "# the in-process bus. LOG_LEVEL overrides.\r\n"
            "logging.basicConfig(\r\n"
            "    level=os.environ.get(\"LOG_LEVEL\", \"INFO\").upper(),\r\n"
            '    format="%(asctime)s %(levelname)s %(name)s: %(message)s",\r\n'
            ")\r\n",
        ),
        (
            '            register_di_providers({"market_data_engine": stack.market_data_engine})\r\n'
            "            app.state.trading_stack = stack\r\n",
            '            register_di_providers({"market_data_engine": stack.market_data_engine})\r\n'
            "            app.state.trading_stack = stack\r\n"
            "\r\n"
            "            # Read-side queries that need the LIVE trading plane (M5):\r\n"
            "            # /account/positions returned [] for everyone because nothing\r\n"
            "            # ever registered this handler. Valuation goes through the\r\n"
            "            # stack's RiskEngine - the same single source of truth the\r\n"
            "            # margin loop and the liquidation worker use.\r\n"
            "            from application.queries.get_positions import GetPositionsQueryHandler\r\n"
            "\r\n"
            "            register_di_providers(\r\n"
            "                {\r\n"
            "                    \"positions_query_handler\": GetPositionsQueryHandler(\r\n"
            "                        position_repo=container.resolve(IPositionRepository),\r\n"
            "                        account_repo=container.resolve(IAccountRepository),\r\n"
            "                        symbol_repo=container.resolve(ISymbolRepository),\r\n"
            "                        market_data_engine=stack.market_data_engine,\r\n"
            "                        risk_engine=stack.risk_engine,\r\n"
            "                    )\r\n"
            "                }\r\n"
            "            )\r\n",
        ),
    ],
)
print("all patches applied")
