# MT5 Manager REST API — Quickstart

> **Source:** `https://mng5.mtapi.io/ReadMe` (offline mirror, scraped 2026-09-08)
> **Base URL:** `https://mng5.mtapi.io`
> **Full reference:** see `MT5-Manager-REST-API.md`
> **OpenAPI spec:** `swagger.json`

---

## Overview

Full functional trial version for 14 days. More details and full version available at:

- Main website: [https://mtapi.online](https://mtapi.online)
- Demo environment and documentation: [https://mt5mng.mtapi.io](https://mt5mng.mtapi.io)

---

## Installation (self-host)

```bash
docker pull mtapiio/mt5mng
docker run --rm -p 5000:80 mtapiio/mt5mng
```

After that open in browser: `http://localhost:5000`

---

## Step 1 — Connect to MT5 Server

To establish a connection with the MT5 Server, call the **Connect** endpoint. It requires broker host, port, MT4/MT5 account number, and password.

**Endpoint:** `GET /Connect`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user` | string | yes | MT account number |
| `password` | string | yes | Account password |
| `server` | string | yes | Broker host/IP (with optional port) |

**Example request:**

```
https://mt5mng.mtapi.io/Connect?user=999943&password=eanm3xtd&server=20.4.28.127
```

The response is a token (UUID). Use it as the `id` parameter in every subsequent request to the server.

---

## Step 2 — Trading (send orders)

To send different types of orders, use the **OrderSend** endpoint.

**Endpoint:** `GET /OrderSend`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | yes | Identification token from `Connect` |
| `symbol` | string | yes | Trading symbol (e.g., `EURUSD`) |
| `operation` | enum | yes | `Buy`, `Sell`, `BuyStop`, `SellStop`, `BuyLimit`, `SellLimit` |
| `volume` | number | yes | Trade volume in lots |
| `price` | number | conditional | Required for stop/limit orders |

**Market order:**

```
https://mt5mng.mtapi.io/OrderSend?id=<TOKEN>&symbol=EURUSD&operation=Buy&volume=0.01
```

**Stop order:**

```
https://mt5mng.mtapi.io/OrderSend?id=<TOKEN>&symbol=EURUSD&operation=BuyStop&volume=0.01&price=1.5
```

**Limit order:**

```
https://mt5mng.mtapi.io/OrderSend?id=<TOKEN>&symbol=EURUSD&operation=BuyLimit&volume=0.01&price=0.5
```

---

## Step 3 — Realtime quotes via WebSockets

1. Open the Swagger UI at [https://mt5mng.mtapi.io/index.html](https://mt5mng.mtapi.io/index.html).
2. Call `/Connect` to get an identification token.
3. In a WebSocket test client, open:

   ```
   wss://mt5mng.mtapi.io/events?id=<TOKEN>
   ```
4. Call the `/Subscribe` endpoint with the desired symbol.
5. Quotes should start to flow in the WebSocket client.

Recommended Chrome extension: [WebSocket Test Client](https://chrome.google.com/webstore/detail/websocket-test-client/fgponpodhbmadfljofbimhhlengambbn)

---

## Endpoint Categories (overview)

| Section | Count | Purpose |
|---|---|---|
| **Connection** | 4 | `Connect`, `Disconnect`, `IsConnected`, `ConnectionStatus` |
| **WebSockets** | 18 | `OnQuote`, `OnTick`, `OnOrderUpdate`, `OnPositionUpdate`, etc. |
| **Reports** | 13 | `DailyRequest*`, `Segregated` |
| **Trading** | 7 | `OrderSend`, `OrderClose`, `OrderModify`, `DealModify`, `OrderDelete` |
| **Service** | 4 | `Ping`, `ReadMe`, `MemoryUsage`, `StartTimeUtc` |
| **Main** | 66 | Account mgmt, users, deals, positions, symbols, ticks, charts |
| **Admin** | 1 | `UserArchive` |
| **Subscriptions** | 11 | `Subscribe*`, `Unsubscribe*` |

See the full reference for parameters, request bodies, response schemas, and enums.
