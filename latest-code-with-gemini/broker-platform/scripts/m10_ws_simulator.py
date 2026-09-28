"""M10 cloud-proof helper: a standalone trade-server-protocol WebSocket simulator.

Speaks exactly the wire protocol of refs/trade-server /ws/marketdata (JSON sub
actions in, msgpack tick frames out) at a constant price map, so a proof can
assert the fill price equals the price pushed over the socket.

This is NOT a MetaTrader5 terminal - it is the same protocol the real
trade-server speaks, for gates that need a deterministic upstream.

Usage:
  M10_SIM_PORT=8066 python3 scripts/m10_ws_simulator.py
  # prices via env: M10_SIM_PRICES='{"EURUSD": ["1.23450", "1.23460"]}'
"""
import asyncio
import json
import os
import time
from contextlib import asynccontextmanager

import msgpack
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

PRICES = json.loads(os.environ.get("M10_SIM_PRICES", '{"EURUSD": ["1.23450", "1.23460"]}'))
INTERVAL_S = float(os.environ.get("M10_SIM_INTERVAL_S", "0.4"))
CONNS: list = []


async def pusher():
    while True:
        await asyncio.sleep(INTERVAL_S)
        now_ms = int(time.time() * 1000)
        for entry in list(CONNS):
            for symbol in list(entry["subs"]):
                pair = PRICES.get(symbol.upper())
                if not pair:
                    continue
                bid, ask = float(pair[0]), float(pair[1])
                frame = msgpack.packb(
                    {"s": symbol.upper(), "p": bid, "b": bid, "a": ask, "q": 1.0, "ts": now_ms},
                    use_bin_type=True,
                )
                try:
                    await entry["ws"].send_bytes(frame)
                except Exception:
                    pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(pusher())
    yield
    task.cancel()


app = FastAPI(lifespan=lifespan)


@app.get("/healthz")
async def healthz():
    return {"ok": True, "connections": len(CONNS), "prices": PRICES}


@app.websocket("/ws/marketdata")
async def marketdata(ws: WebSocket):
    await ws.accept()
    entry = {"ws": ws, "subs": set()}
    CONNS.append(entry)
    print(f"client connected; total={len(CONNS)}", flush=True)
    try:
        while True:
            data = json.loads(await ws.receive_text())
            action = data.get("action")
            symbol = str(data.get("symbol") or "").upper()
            if action == "sub":
                entry["subs"].add(symbol)
                print(f"subscribed {symbol}; subs={sorted(entry['subs'])}", flush=True)
            elif action == "sub_book":
                entry["subs"].add(symbol)  # simulator pushes ticks for both
    except (WebSocketDisconnect, RuntimeError):
        pass
    finally:
        if entry in CONNS:
            CONNS.remove(entry)


if __name__ == "__main__":
    port = int(os.environ.get("M10_SIM_PORT", "8066"))
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")
