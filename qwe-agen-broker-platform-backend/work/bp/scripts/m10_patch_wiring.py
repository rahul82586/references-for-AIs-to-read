"""M10 patch part 1: api/main.py MARKET_DATA_SOURCE=trade_server + FIX gateway shutdown;
trading_setup.py BROKER_LP_GATEWAY=fix; pyproject msgpack + fix extra."""
import io
import sys

WS_BRANCH = '''            elif md_source in ("trade_server", "ws"):
                # M10: live upstream. The trade-server prototype keeps a real
                # MetaTrader5 terminal attached and broadcasts msgpack ticks over
                # WebSocket (/ws/marketdata). One feed adapter, same TickIngestor
                # and MarketDataEngine as the mock - only the source changes.
                from application.services.tick_ingestor import TickIngestor
                from infrastructure.feeds.trade_server_feed import TradeServerTickFeed

                ws_url = os.environ.get("TRADE_SERVER_WS_URL", "").strip()
                if not ws_url:
                    raise RuntimeError(
                        "MARKET_DATA_SOURCE=trade_server requires TRADE_SERVER_WS_URL "
                        "(e.g. ws://127.0.0.1:8000/ws/marketdata)"
                    )
                env_symbols = os.environ.get("TRADE_SERVER_WS_SYMBOLS", "").strip()
                if env_symbols:
                    ws_symbols = [s.strip().upper() for s in env_symbols.split(",") if s.strip()]
                else:
                    ws_symbols = [s.name for s in cache.get_all_symbols()]
                    cap = int(os.environ.get("TRADE_SERVER_WS_MAX_SYMBOLS", "50"))
                    if len(ws_symbols) > cap:
                        logger.warning(
                            "subscribing to the first %d of %d cached symbols "
                            "(raise TRADE_SERVER_WS_MAX_SYMBOLS or set "
                            "TRADE_SERVER_WS_SYMBOLS to choose them)",
                            cap, len(ws_symbols),
                        )
                        ws_symbols = ws_symbols[:cap]
                feed = TradeServerTickFeed(url=ws_url, symbols=ws_symbols)
                ingestor = TickIngestor(
                    market_data_engine=stack.market_data_engine, feeds=[feed]
                )
                await ingestor.start()
                app.state.tick_ingestor = ingestor
                logger.info(
                    "MARKET_DATA_SOURCE=trade_server: live ticks from %s (%d symbol(s))",
                    ws_url, len(ws_symbols),
                )
            elif md_source:
                raise RuntimeError(
                    f"unknown MARKET_DATA_SOURCE={md_source!r}; supported: 'mock', "
                    "'trade_server' (live WS upstream) or unset (no price source)"
                )
'''

OLD_BRANCH = '''            elif md_source:
                raise RuntimeError(
                    f"unknown MARKET_DATA_SOURCE={md_source!r}; supported: 'mock' "
                    "or unset (no price source)"
                )
'''

GW_SHUTDOWN = '''            # M10: the FIX liquidity gateway (when BROKER_LP_GATEWAY=fix) owns a
            # session + read loop; close it like every other worker.
            lp_gateway = getattr(stack, "liquidity_gateway", None)
            if lp_gateway is not None and hasattr(lp_gateway, "stop"):
              try:
                await lp_gateway.stop()
                logger.info("Liquidity gateway stopped")
              except Exception as e:  # noqa: BLE001
                logger.warning(f"Error stopping liquidity gateway: {e}")

'''

GW_SHUTDOWN_ANCHOR = '''            # M9: the SL/TP worker subscribes to the tick stream and closes
'''

TS_OLD = '''    if lp_strict is None:
        lp_strict = os.environ.get("BROKER_LP_STUB_NONSTRICT", "").lower() not in ("1", "true", "yes")
    liquidity_gateway = _resolve(
        container, "liquidity_gateway", required=False,
        default=StubLiquidityGateway(strict=lp_strict),
    )
    if isinstance(liquidity_gateway, StubLiquidityGateway):
'''

TS_NEW = '''    if lp_strict is None:
        lp_strict = os.environ.get("BROKER_LP_STUB_NONSTRICT", "").lower() not in ("1", "true", "yes")
    # M10: BROKER_LP_GATEWAY=fix swaps the stub for the FIX adapter under the
    # SAME DI key - the orchestrator's A-Book path is unchanged.
    default_gateway: Any = StubLiquidityGateway(strict=lp_strict)
    lp_gateway_kind = os.environ.get("BROKER_LP_GATEWAY", "").strip().lower()
    if lp_gateway_kind == "fix":
        from infrastructure.gateways.fix_gateway import build_fix_gateway_from_env

        default_gateway = build_fix_gateway_from_env()
        logger.info(
            "A-Book liquidity gateway: FIX (sender=%s target=%s, session=%s)",
            default_gateway.sender_comp_id,
            default_gateway.target_comp_id,
            "simulated" if os.environ.get("BROKER_FIX_SIMULATOR", "").strip().lower()
            in ("1", "true", "yes") else "quickfixn",
        )
    elif lp_gateway_kind:
        raise RuntimeError(
            f"unknown BROKER_LP_GATEWAY={lp_gateway_kind!r}; supported: 'fix' or unset (stub)"
        )
    liquidity_gateway = _resolve(
        container, "liquidity_gateway", required=False,
        default=default_gateway,
    )
    if isinstance(liquidity_gateway, StubLiquidityGateway):
'''


def patch(path, replacements):
    with io.open(path, "r", encoding="utf-8", newline="") as f:
        text = f.read()
    crlf = "\r\n" in text
    for old, new in replacements:
        if crlf:
            old = old.replace("\n", "\r\n")
            new = new.replace("\n", "\r\n")
        if old not in text:
            print(f"FAIL: pattern not found in {path}:\n{old[:120]}...")
            sys.exit(1)
        if text.count(old) != 1:
            print(f"FAIL: pattern occurs {text.count(old)}x in {path}")
            sys.exit(1)
        text = text.replace(old, new)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"patched {path} (crlf={crlf})")


patch("api/main.py", [
    (OLD_BRANCH, WS_BRANCH),
    (GW_SHUTDOWN_ANCHOR, GW_SHUTDOWN + GW_SHUTDOWN_ANCHOR),
])
patch("application/di/trading_setup.py", [(TS_OLD, TS_NEW)])
print("OK part1")
