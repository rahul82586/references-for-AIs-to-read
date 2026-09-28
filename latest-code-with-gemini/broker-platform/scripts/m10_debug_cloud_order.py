"""M10 debug: reproduce the cloud filled_volume defect against real Neon,
with every order save/find instrumented. Not a gate - a diagnostic."""
import asyncio
import logging
import os
import sys
import time
from decimal import Decimal

sys.path.insert(0, os.getcwd())
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
for noisy in ("sqlalchemy", "asyncio", "httpx", "urllib3", "redis"):
    logging.getLogger(noisy).setErrorLevel = None  # noqa
    logging.getLogger(noisy).setLevel(logging.ERROR)

from dotenv import load_dotenv

load_dotenv(".env")


async def main():
    from api.main import default_providers
    from application.commands.create_order import CreateOrderCommand
    from core.domains.accounts.account import Account
    from core.domains.common.value_objects import Money
    from core.domains.market_data.models import Tick
    from core.domains.oms.enums import OrderType
    from infrastructure.security.password_hasher import Argon2PasswordHasher

    providers = default_providers()
    db = providers["database"]
    order_repo = providers["order_repo"]
    account_repo = providers["account_repo"]
    group_repo = providers["group_repo"]

    # instrument every save + read of an order
    orig_save = order_repo.save
    orig_find = order_repo.find_by_id

    async def save(order, session=None):
        print(f"  SAVE  t={time.strftime('%H:%M:%S')}+{time.time()%1:.3f} state={order.state.value} "
              f"vol_cur={order.volume_current.value} ticket={order.ticket_id[:8]} sess={'uow' if session else 'own'}",
              flush=True)
        return await orig_save(order, session=session)

    async def find(order_id, session=None):
        o = await orig_find(order_id, session=session)
        if o is not None:
            print(f"  READ  t={time.strftime('%H:%M:%S')}+{time.time()%1:.3f} state={o.state.value} "
                  f"vol_cur={o.volume_current.value} ticket={o.ticket_id[:8]} sess={'uow' if session else 'own'}",
                  flush=True)
        return o

    order_repo.save = save
    order_repo.find_by_id = find

    groups = {g.name: g for g in await group_repo.get_all()}
    group = groups.get("demo\\Standard") or next(iter(groups.values()))
    login = 810000 + (int(time.time()) % 9999)
    account = Account(login=login, client_id="DBG", group=group, group_id=group.id,
                      currency="USD", balance=Money(Decimal("10000"), "USD"),
                      credit=Money(Decimal("0"), "USD"), equity=Money(Decimal("10000"), "USD"),
                      margin_used=Money(Decimal("0"), "USD"), margin_free=Money(Decimal("10000"), "USD"))
    account.password_hash = Argon2PasswordHasher().hash_password("x")
    await account_repo.save(account)

    # the trading plane, exactly as api/main.py wires it (Redis bus included)
    from application.cache.config_cache import ConfigCache, set_config_cache
    from application.di.market_data_setup import build_market_data_stack
    from application.di.trading_setup import build_trading_stack
    from api.di_providers import _ContainerView

    market_data_engine = providers.get("market_data_engine")
    from core.domains.market_data.engine import MarketDataEngine
    event_bus = providers["event_bus"]
    if market_data_engine is None:
        market_data_engine = MarketDataEngine(event_bus=event_bus, symbol_repo=providers["symbol_repo"])
    config_cache = ConfigCache(
        group_repo=group_repo, account_repo=account_repo,
        symbol_repo=providers["symbol_repo"], holiday_repo=providers["holiday_repo"],
        position_repo=providers["position_repo"], event_bus=event_bus,
    )
    await config_cache.initialize()
    set_config_cache(config_cache)
    container = _ContainerView({**providers, "market_data_engine": market_data_engine})
    stack = await build_trading_stack(container, market_data_engine=market_data_engine,
                                      config_cache=config_cache)
    from api.di_providers import register_di_providers
    register_di_providers(stack.as_providers())
    components = build_market_data_stack(_ContainerView({**providers, **stack.as_providers(),
                                                         "market_data_engine": market_data_engine}))

    # instrument the handler the stack actually uses
    handler = stack.create_order_handler
    handler.order_repo = order_repo

    await market_data_engine.process_tick(Tick(symbol="EURUSD", bid=Decimal("1.23450"),
                                               ask=Decimal("1.23460"), spread=Decimal("0.00010"),
                                               source="DEBUG"))
    print("=== handle() ===", flush=True)
    t0 = time.time()
    order = await handler.handle(CreateOrderCommand(account_login=login, symbol="EURUSD",
                                                    order_type=OrderType.BUY,
                                                    volume=Decimal("0.10")))
    print(f"=== returned after {time.time()-t0:.2f}s: state={order.state.value} "
          f"vol_cur={order.volume_current.value}", flush=True)
    row = await orig_find(order.ticket_id)
    print(f"=== db row now: state={row.state.value} vol_cur={row.volume_current.value}", flush=True)
    await asyncio.sleep(2)
    row = await orig_find(order.ticket_id)
    print(f"=== db row +2s: state={row.state.value} vol_cur={row.volume_current.value}", flush=True)
    await db.close()


asyncio.run(main())