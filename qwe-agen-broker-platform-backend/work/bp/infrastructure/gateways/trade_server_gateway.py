"""A-Book liquidity gateway that hedges through a trade-server box.

`refs/trade-server` is a FastAPI process with a real MetaTrader 5 terminal
attached. It exposes `POST /api/v1/place-order`, which calls `mt5.order_send` and
returns the terminal's own result. So it can hold a real hedge - which makes it an
`ILiquidityGateway`, and that is exactly how Centroid Bridge works: it hedges
client flow through MT5 terminals rather than through a bank FIX session.

This is the third adapter behind the same port:

    BROKER_LP_GATEWAY unset          StubLiquidityGateway   refuses (strict) or acks
    BROKER_LP_GATEWAY=fix            FixLiquidityGateway    FIX 4.4 to a real LP
    BROKER_LP_GATEWAY=trade_server   this one               REST to an MT5 terminal

`ExecutionOrchestrator._execute_a_book` is unchanged by all three, which is the
point of the port.

Wire contract (verified against refs/trade-server/connectors/mt5_connector.py)
=============================================================================
Request   POST /api/v1/place-order
          {"symbol","side":"buy"|"sell","volume","price","sl","tp","type_filling"}

Success   200 {"status":"success","data":{"success":true,"ticket":<int>,
                                          "price":<float>,"volume":<float>,
                                          "side":"buy"|"sell"}}
          `price` and `volume` are what the TERMINAL reports - the real execution
          price and the real filled size, so a partial fill is visible.

Failure   500 {"detail":"<MT5 comment> (<retcode>)"}   the terminal refused it
          400 {"detail":"No active trade connection"}   never reached the terminal

Outcome mapping - the part that matters
=======================================
M11 gives `_execute_a_book` four outcomes and this adapter has to feed all four
honestly. The distinction that cannot be blurred is *the terminal said no* versus
*we do not know*:

  200 + success                -> FILLED (or PARTIAL when volume < requested)
  500 with an MT5 retcode      -> the terminal refused: raise, orchestrator rejects
  400 no active connection     -> never sent: raise, orchestrator rejects
  timeout / DNS / bad JSON /   -> HedgeStateUnknown. The order MAY be at the
  5xx without a retcode           terminal. Raising anything else would make the
                                  orchestrator reject the client side of a hedge
                                  that may be live.

**No retries.** trade-server hardcodes `magic: 1001` and `comment: "trade-server"`
and accepts no client order id, so there is no idempotency key: a retry after an
unknown outcome could place a second hedge. The unknown path flags for
reconciliation instead, which is the only safe answer without a drop-copy.

Decimal discipline: every wire float converts via `Decimal(str(value))`, so a
price of 77310.83 reaches the engine as exactly that. No float touches a price.

No new runtime dependency: HTTP goes through `asyncio.to_thread` + urllib, so
`ops/docker/requirements-runtime.txt` is unchanged and the startup chain still
imports nothing it does not need.
"""
from __future__ import annotations

import asyncio
import json
import logging
import urllib.error
import urllib.request
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional

from core.domains.oms.entities.order import Order
from core.domains.oms.enums import OrderType
from core.ports.interfaces import ILiquidityGateway

logger = logging.getLogger(__name__)

__all__ = [
    "HedgeStateUnknown",
    "TradeServerLiquidityGateway",
    "TradeServerReject",
    "build_trade_server_gateway_from_env",
]

#: MT5 retcodes the trade-server worker treats as success: DONE and DONE_PARTIAL.
_MT5_DONE = 10009
_MT5_DONE_PARTIAL = 10008

_LIMIT_TYPES = {OrderType.BUY_LIMIT, OrderType.SELL_LIMIT}
_STOP_TYPES = {OrderType.BUY_STOP, OrderType.SELL_STOP}
_STOP_LIMIT_TYPES = {OrderType.BUY_STOP_LIMIT, OrderType.SELL_STOP_LIMIT}


class TradeServerReject(RuntimeError):
    """The terminal definitively refused the hedge. Safe to reject the client."""

    def __init__(self, detail: str, *, retcode: Optional[int] = None, body: Any = None):
        super().__init__(detail)
        self.detail = detail
        self.retcode = retcode
        self.body = body


class HedgeStateUnknown(RuntimeError):
    """The order may or may not be at the terminal. Do NOT reject the client.

    M11's orchestrator recognises this by the `hedge_state_unknown` attribute
    rather than by importing this class, so it stays correct for adapters that
    have never heard of trade-server.
    """

    hedge_state_unknown = True


def _dec(value: Any) -> Optional[Decimal]:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


class TradeServerLiquidityGateway(ILiquidityGateway):
    """Hedge client flow at a real MT5 terminal via trade-server's REST API."""

    #: what M10's FixLiquidityGateway returns, so _execute_a_book needs no changes
    name = "TradeServerMT5"

    def __init__(
        self,
        base_url: str,
        *,
        timeout_s: float = 20.0,
        quote_timeout_s: float = 15.0,
        type_filling: str = "FOK",
        magic_note: str = "broker-platform",
        session: Optional[Any] = None,
    ) -> None:
        url = (base_url or "").strip().rstrip("/")
        if not url:
            raise ValueError(
                "TRADE_SERVER_API_URL is required for BROKER_LP_GATEWAY=trade_server"
            )
        if not (url.startswith("http://") or url.startswith("https://")):
            raise ValueError(
                f"TRADE_SERVER_API_URL must be an http(s) URL, got {base_url!r}"
            )
        self.base_url = url
        self.timeout_s = float(timeout_s)
        self.quote_timeout_s = float(quote_timeout_s)
        self.type_filling = type_filling
        self.magic_note = magic_note
        #: injectable transport for tests: async (method, path, payload) -> (status, body)
        self._session = session
        #: audit trail of what this gateway actually sent
        self.sent_orders: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------ HTTP
    async def _request(self, method: str, path: str,
                       payload: Optional[dict] = None) -> tuple[int, Any]:
        """One HTTP call. Any transport-level failure is HedgeStateUnknown.

        This is the single place the "did it reach the terminal?" question is
        answered, so the mapping cannot drift between send and cancel.
        """
        if self._session is not None:
            return await self._session(method, path, payload)

        url = self.base_url + path
        data = json.dumps(payload).encode() if payload is not None else None

        def blocking() -> tuple[int, Any]:
            req = urllib.request.Request(
                url, data=data, method=method,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": self.magic_note,
                    # ngrok's free tier serves a browser interstitial without it
                    "ngrok-skip-browser-warning": "1",
                },
            )
            try:
                with urllib.request.urlopen(req, timeout=self.timeout_s) as r:
                    raw = r.read().decode("utf-8", "replace")
                    return r.status, _loads(raw)
            except urllib.error.HTTPError as e:
                # An HTTP error status IS an answer from trade-server, not a
                # transport failure - read the body, it carries the retcode.
                raw = e.read().decode("utf-8", "replace")
                return e.code, _loads(raw)

        try:
            return await asyncio.wait_for(
                asyncio.to_thread(blocking), timeout=self.timeout_s + 5.0
            )
        except asyncio.TimeoutError as exc:
            raise HedgeStateUnknown(
                f"trade-server did not answer {method} {path} within {self.timeout_s}s; "
                "the hedge state is UNKNOWN - reconcile against the terminal before "
                "retrying (this gateway has no idempotency key, so a blind retry "
                "could double-hedge)"
            ) from exc
        except (urllib.error.URLError, OSError, ValueError) as exc:
            # DNS, connection refused, TLS, socket reset: we cannot say whether the
            # request was written. Treat as unknown - the safe direction.
            raise HedgeStateUnknown(
                f"trade-server transport failure for {method} {path}: "
                f"{type(exc).__name__}: {exc}; hedge state is UNKNOWN"
            ) from exc

    # ------------------------------------------------------- ILiquidityGateway
    async def send_order(self, order: Order, gateway_id: str) -> dict:
        """Place the hedge at the terminal and return the normalised report."""
        side = "buy" if order.order_type.name.startswith("BUY") else "sell"
        volume = order.volume_current.value
        if volume <= 0:
            volume = order.volume_initial.value

        price: Optional[float] = None
        price_order = getattr(order, "price_order", None)
        px = getattr(price_order, "value", price_order)
        if order.order_type in (_LIMIT_TYPES | _STOP_TYPES | _STOP_LIMIT_TYPES):
            # trade-server passes `price` straight into the MT5 request; for a
            # pending order that is the trigger/limit price.
            price = float(px) if px else None

        sl = _dec(getattr(order, "price_sl", None))
        tp = _dec(getattr(order, "price_tp", None))
        sl = getattr(sl, "value", sl)
        tp = getattr(tp, "value", tp)

        payload = {
            "symbol": str(order.symbol).upper(),
            "side": side,
            "volume": float(volume),
            "price": price,
            "sl": float(sl) if sl else None,
            "tp": float(tp) if tp else None,
            "type_filling": self.type_filling,
        }
        self.sent_orders.append({"cl_ord_id": order.ticket_id, "gateway_id": gateway_id,
                                 **payload})
        logger.info(
            "hedging order %s at the MT5 terminal via %s: %s %s %s",
            order.ticket_id, self.base_url, side, volume, payload["symbol"],
        )

        status, body = await self._request("POST", "/api/v1/place-order", payload)
        return self._to_report(status, body, order=order, gateway_id=gateway_id,
                               requested_volume=volume, side=side)

    def _to_report(self, status: int, body: Any, *, order: Order, gateway_id: str,
                   requested_volume: Decimal, side: str) -> dict:
        """Map trade-server's answer onto M11's four outcomes."""
        if status == 400:
            # "No active trade connection" - the terminal was never asked.
            raise TradeServerReject(
                f"trade-server has no active MT5 connection: {_detail(body)}", body=body
            )

        if status == 200 and isinstance(body, dict):
            data = body.get("data") or {}
            if data.get("success"):
                filled = _dec(data.get("volume")) or requested_volume
                price = _dec(data.get("price"))
                partial = filled < requested_volume
                report = {
                    "status": "PARTIAL" if partial else "FILLED",
                    "cl_ord_id": order.ticket_id,
                    "order_id": str(data.get("ticket")) if data.get("ticket") is not None else None,
                    "gateway_id": gateway_id,
                    "symbol": str(order.symbol).upper(),
                    "side": side.upper(),
                    "volume": format(filled, "f"),
                    "price": format(price, "f") if price is not None else None,
                    "stub": False,
                    "venue": self.name,
                    "mt5_ticket": data.get("ticket"),
                }
                logger.info(
                    "hedge for order %s FILLED at the terminal: ticket=%s price=%s volume=%s",
                    order.ticket_id, report["order_id"], report["price"], report["volume"],
                )
                return report
            # 200 but success=false: the worker returned a structured refusal.
            raise TradeServerReject(
                f"terminal refused the hedge: {data.get('error') or _detail(body)}",
                body=body,
            )

        if status >= 500:
            detail = _detail(body)
            retcode = _retcode_from(detail)
            if retcode is not None:
                # The terminal answered with an MT5 retcode: a definite refusal.
                raise TradeServerReject(
                    f"terminal rejected the hedge (retcode {retcode}): {detail}",
                    retcode=retcode, body=body,
                )
            # A 5xx with no retcode is trade-server itself failing. We cannot say
            # whether order_send ran, so this is unknown, not a rejection.
            raise HedgeStateUnknown(
                f"trade-server returned {status} with no MT5 retcode ({detail}); "
                "hedge state is UNKNOWN"
            )

        # Anything else (404, 422, a non-dict body): the request was answered but
        # not by the trading path. Do not guess.
        raise HedgeStateUnknown(
            f"unexpected trade-server response {status}: {str(body)[:200]}; "
            "hedge state is UNKNOWN"
        )

    async def cancel_order(self, order_id: str, gateway_id: str) -> bool:
        """Cancel a resting order at the terminal; True only on a confirmed success."""
        status, body = await self._request(
            "POST", "/api/v1/cancel-order", {"ticket": str(order_id)}
        )
        if status == 200 and isinstance(body, dict) and (body.get("data") or {}).get("success"):
            return True
        if status == 400:
            raise TradeServerReject(
                f"trade-server has no active MT5 connection: {_detail(body)}", body=body
            )
        if status >= 500 and _retcode_from(_detail(body)) is not None:
            return False
        raise HedgeStateUnknown(
            f"cancel of {order_id} got {status}: {str(body)[:160]}; state UNKNOWN"
        )

    async def get_quotes(self, symbols: list[str]) -> Dict[str, Dict[str, Any]]:
        """Current bid/ask for the given symbols, read off the market-data socket.

        trade-server has no REST quote endpoint - `/api/v1/symbols` returns symbol
        *specs* with `bid`/`ask` absent - so the only source of a live price is the
        same `/ws/marketdata` socket `TradeServerTickFeed` uses. This subscribes,
        takes the first frame per symbol, and leaves.

        It reads the venue rather than deriving from `spread`, so it is a second
        consumer of one source, not a second source. Used by `cli sync` (D9):
        a CLI run has no feed attached, and a valuation sweep must not invent a
        price - so without this the sweep can only report "no price known".

        A symbol that does not quote within the timeout is simply absent from the
        result. The caller reports that honestly; nothing here guesses.
        """
        wanted = [str(s).upper() for s in (symbols or []) if s]
        if not wanted:
            return {}
        ws_url = self._ws_url()
        if ws_url is None:
            logger.warning(
                "get_quotes(%s) needs a market-data socket; TRADE_SERVER_WS_URL is "
                "not set and %s is not a ws(s) origin, so no prices are available",
                wanted, self.base_url,
            )
            return {}
        try:
            import msgpack  # noqa: F401  (fail early with a clear message)
        except ImportError:
            logger.error("msgpack is not installed; trade-server frames cannot be decoded")
            return {}

        out: Dict[str, Dict[str, Any]] = {}
        try:
            import websockets

            async with websockets.connect(ws_url, open_timeout=self.timeout_s) as ws:
                for sym in wanted:
                    await ws.send(json.dumps({"action": "sub", "symbol": sym}))
                deadline = asyncio.get_event_loop().time() + self.quote_timeout_s
                while len(out) < len(wanted) and asyncio.get_event_loop().time() < deadline:
                    remaining = deadline - asyncio.get_event_loop().time()
                    if remaining <= 0:
                        break
                    try:
                        raw = await asyncio.wait_for(ws.recv(), timeout=remaining)
                    except asyncio.TimeoutError:
                        break
                    data = self._decode(raw)
                    if not isinstance(data, dict) or data.get("type") == "book":
                        continue
                    sym = str(data.get("s") or "").upper()
                    if sym not in wanted or sym in out:
                        continue
                    bid, ask = data.get("b"), data.get("a")
                    if bid is None or ask is None:
                        continue
                    out[sym] = {"bid": str(bid), "ask": str(ask),
                                "ts": data.get("ts"), "source": self.name}
        except Exception as exc:  # noqa: BLE001
            logger.error("could not read quotes from %s: %s", ws_url, exc)
            return out
        missing = [s for s in wanted if s not in out]
        if missing:
            logger.warning(
                "no quote within %.0fs for: %s (market closed, or the symbol is not "
                "selected in the terminal)", self.quote_timeout_s, ", ".join(missing),
            )
        return out

    @staticmethod
    def _decode(raw: Any) -> Any:
        if isinstance(raw, (bytes, bytearray, memoryview)):
            import msgpack

            try:
                return msgpack.unpackb(bytes(raw), raw=False)
            except Exception:  # noqa: BLE001
                return None
        if isinstance(raw, str):
            try:
                return json.loads(raw)
            except ValueError:
                return None
        return None

    def _ws_url(self) -> Optional[str]:
        """The market-data socket for this box.

        Prefer the explicit TRADE_SERVER_WS_URL; otherwise derive it from an
        http(s) base, because both endpoints live on the same trade-server.
        """
        import os

        explicit = (os.environ.get("TRADE_SERVER_WS_URL") or "").strip()
        if explicit:
            return explicit
        base = self.base_url
        if base.startswith("https://"):
            return "wss://" + base[len("https://"):] + "/ws/marketdata"
        if base.startswith("http://"):
            return "ws://" + base[len("http://"):] + "/ws/marketdata"
        return None

    async def close_position(self, symbol: str, ticket: Any, volume: Decimal,
                             side: str) -> dict:
        """Close a hedge at the terminal. Not part of ILiquidityGateway, but an
        A-Book position has to be unwound somehow, and this is the only adapter
        that can reach the terminal that holds it."""
        payload = {"symbol": str(symbol).upper(), "ticket": str(ticket),
                   "volume": float(volume), "side": side}
        status, body = await self._request("POST", "/api/v1/close-position", payload)
        if status == 200 and isinstance(body, dict) and (body.get("data") or {}).get("success"):
            return {"status": "CLOSED", "venue": self.name, "raw": body.get("data")}
        if status >= 500 and _retcode_from(_detail(body)) is not None:
            raise TradeServerReject(f"terminal refused the close: {_detail(body)}", body=body)
        raise HedgeStateUnknown(
            f"close of ticket {ticket} got {status}: {str(body)[:160]}; state UNKNOWN"
        )

    async def positions(self) -> Any:
        """Read the terminal's own book - the reconciliation source of truth."""
        status, body = await self._request("GET", "/api/v1/positions")
        if status == 200 and isinstance(body, dict):
            return body.get("data") or []
        raise HedgeStateUnknown(f"could not read terminal positions ({status})")


def _loads(raw: str) -> Any:
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return {"_raw": raw[:400]}


def _detail(body: Any) -> str:
    if isinstance(body, dict):
        for key in ("detail", "error", "message"):
            if body.get(key):
                return str(body[key])
        return json.dumps(body)[:200]
    return str(body)[:200]


def _retcode_from(detail: str) -> Optional[int]:
    """Pull the MT5 retcode out of trade-server's "<comment> (<retcode>)" string."""
    if not detail:
        return None
    tail = detail.rstrip().rstrip(")")
    if "(" not in tail:
        return None
    candidate = tail.rsplit("(", 1)[-1].strip()
    try:
        code = int(candidate)
    except ValueError:
        return None
    # MT5 trade retcodes live in the 10000-10045 band; anything else is not one.
    return code if 10000 <= code <= 10999 else None


def build_trade_server_gateway_from_env() -> TradeServerLiquidityGateway:
    """Construct from the environment, failing loudly on a missing/invalid URL.

    Same rule M10 set for the feed: booting this gateway without a URL is a
    startup failure naming the missing variable, not a silent fall back to the
    stub - a stub that quietly does not hedge is how a broker ends up naked.
    """
    import os

    url = (os.environ.get("TRADE_SERVER_API_URL") or "").strip()
    if not url:
        # Fall back to the WS URL's origin, since both live on the same box. That
        # keeps one variable to configure; an explicit API URL still wins.
        ws = (os.environ.get("TRADE_SERVER_WS_URL") or "").strip()
        if ws:
            url = ws.split("/ws")[0].replace("wss://", "https://").replace("ws://", "http://")
    if not url:
        raise RuntimeError(
            "BROKER_LP_GATEWAY=trade_server requires TRADE_SERVER_API_URL (or "
            "TRADE_SERVER_WS_URL, whose origin is reused); refusing to start with "
            "no way to reach the hedging terminal"
        )
    timeout_s = float(os.environ.get("TRADE_SERVER_ORDER_TIMEOUT_S", "20") or 20)
    filling = (os.environ.get("TRADE_SERVER_TYPE_FILLING") or "FOK").strip()
    return TradeServerLiquidityGateway(
        url, timeout_s=timeout_s,
        quote_timeout_s=float(os.environ.get("TRADE_SERVER_QUOTE_TIMEOUT_S", "15") or 15),
        type_filling=filling,
        magic_note=(os.environ.get("TRADE_SERVER_MAGIC_NOTE") or "broker-platform"),
    )
