# 🚀 Broker Platform Complete API Test Report

**Swagger UI URL**: `http://localhost:8000/docs`  
**Auth Credentials**: Login ID: `100001` | Password: `password123`  
**Total Tested Endpoints**: `25`  

## 📊 Endpoint Test Summary

| Endpoint | Category | HTTP Status | Status |
|:---|:---|:---:|:---:|
| `POST /api/v1/auth/login` | Auth | `200` | ✅ PASS (200 OK) |
| `GET /health` | Health | `200` | ✅ PASS (200 OK) |
| `GET /api/v1/manager/Ping` | Service | `200` | ✅ PASS (200 OK) |
| `GET /api/v1/manager/Version` | Service | `200` | ✅ PASS (200 OK) |
| `GET /api/v1/manager/StartTimeUtc` | Service | `200` | ✅ PASS (200 OK) |
| `GET /api/v1/manager/MemoryUsage` | Service | `200` | ✅ PASS (200 OK) |
| `GET /api/v1/manager/IsConnected` | Connection | `200` | ✅ PASS (200 OK) |
| `GET /api/v1/manager/SessionInfo` | Connection | `200` | ✅ PASS (200 OK) |
| `POST /api/v1/manager/Connect` | Connection | `200` | ✅ PASS (200 OK) |
| `POST /api/v1/manager/Disconnect` | Connection | `200` | ✅ PASS (200 OK) |
| `GET /api/v1/manager/UserGet?login=100001` | Main Queries | `200` | ✅ PASS (200 OK) |
| `GET /api/v1/manager/PositionGet?login=100001` | Main Queries | `200` | ✅ PASS (200 OK) |
| `POST /api/v1/trade/orders` | Trade | `200` | ✅ PASS (200 OK) |
| `PUT /api/v1/trade/orders/1001` | Trade | `200` | ✅ PASS (200 OK) |
| `DELETE /api/v1/trade/orders/1001` | Trade | `200` | ✅ PASS (200 OK) |
| `GET /api/v1/account/info` | Account | `200` | ✅ PASS (200 OK) |
| `GET /api/v1/account/positions` | Account | `200` | ✅ PASS (200 OK) |
| `GET /api/v1/market-data/history/EURUSD/ticks` | Market Data | `200` | ✅ PASS (200 OK) |
| `GET /api/v1/market-data/history/EURUSD/bars` | Market Data | `200` | ✅ PASS (200 OK) |
| `GET /api/v1/admin/groups` | Admin | `200` | ✅ PASS (200 OK) |
| `GET /api/v1/admin/symbols` | Admin | `200` | ✅ PASS (200 OK) |
| `GET /api/v1/admin/dealer-queue` | Admin | `200` | ✅ PASS (200 OK) |
| `POST /api/v1/manager/OrderSend` | Manager Trading | `200` | ✅ PASS (200 OK) |
| `POST /api/v1/manager/OrderClose` | Manager Trading | `200` | ✅ PASS (200 OK) |
| `POST /api/v1/manager/OrderDelete` | Manager Trading | `200` | ✅ PASS (200 OK) |


## 📝 Detailed Response Logs

### `POST /api/v1/auth/login` (`HTTP 200`)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMDAwMDEiLCJleHAiOjE3ODg5OTUwMTN9._GnVAMuu6ykw6WFvF_8Qv53ykmKhnM7jcXM4gVSfHTs",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### `GET /health` (`HTTP 200`)
```json
{
  "status": "healthy",
  "service": "broker-platform-api",
  "version": "1.0.0"
}
```

### `GET /api/v1/manager/Ping` (`HTTP 200`)
```json
{
  "retcode": 0,
  "serverTime": "2026-09-08T23:03:33.139779Z",
  "status": "OK",
  "latencyMs": 0.0
}
```

### `GET /api/v1/manager/Version` (`HTTP 200`)
```json
{
  "serverName": "Broker Platform",
  "serverVersion": "1.0.0",
  "apiVersion": "5.0.0",
  "buildNumber": "2026.09.09",
  "pythonVersion": "3.14.3",
  "buildDate": null
}
```

### `GET /api/v1/manager/StartTimeUtc` (`HTTP 200`)
```json
{
  "serverName": "Broker Platform",
  "serverVersion": "1.0.0",
  "startTimeUtc": "2026-09-08T23:03:33.139767Z",
  "uptimeSeconds": 0,
  "uptimeHuman": "0s",
  "buildNumber": "2026.09.09",
  "apiVersion": "5.0.0",
  "pythonVersion": "3.14.3"
}
```

### `GET /api/v1/manager/MemoryUsage` (`HTTP 200`)
```json
{
  "retcode": 0,
  "rssMb": 69.74,
  "vmsMb": 56.56,
  "sharedMb": 0.0,
  "textMb": 0.0,
  "dataMb": 0.0,
  "percent": 0.44,
  "cpuPercent": 0.0,
  "openFiles": 1,
  "numThreads": 7
}
```

### `GET /api/v1/manager/IsConnected` (`HTTP 200`)
```json
{
  "connected": true,
  "sessionId": "session_100001",
  "userLogin": 100001,
  "serverTime": "2026-09-08T23:03:33.212162Z"
}
```

### `GET /api/v1/manager/SessionInfo` (`HTTP 200`)
```json
{
  "sessionId": "session_100001",
  "userLogin": 100001,
  "userGroup": null,
  "accessLevel": "FULL",
  "clientAgent": "testclient",
  "clientIP": "testclient",
  "connectedAt": "2026-09-08T23:03:33.215091Z",
  "lastActivity": "2026-09-08T23:03:33.215091Z",
  "expiresAt": "2026-09-09T23:03:33.215091Z"
}
```

### `POST /api/v1/manager/Connect` (`HTTP 200`)
```json
{
  "retcode": 0,
  "sessionId": "session_100001_1788908613",
  "accessLevel": "FULL",
  "userLogin": 100001,
  "userGroup": null,
  "userName": null,
  "userEmail": null,
  "permissions": [],
  "serverTime": "2026-09-08T23:03:33.218243Z",
  "message": "Connected successfully"
}
```

### `POST /api/v1/manager/Disconnect` (`HTTP 200`)
```json
{
  "retcode": 0,
  "message": "Disconnected successfully",
  "sessionId": "session_100001"
}
```

### `GET /api/v1/manager/UserGet?login=100001` (`HTTP 200`)
```json
{
  "login": 100001,
  "group": "REAL_STANDARD",
  "currency": "USD",
  "balance": "10000.00",
  "credit": "0",
  "equity": "10000.00",
  "margin": "0",
  "free_margin": "10000.00",
  "margin_level": "999999",
  "leverage": 100,
  "enable": true,
  "enable_charts": true,
  "enable_news": true,
  "enable_trades": true,
  "password_phone": null,
  "email": null,
  "country": null,
  "city": null,
  "address": null,
  "phone": null,
  "registration": null,
  "last_visit": null,
  "last_pass_change": null,
  "comment": null
}
```

### `GET /api/v1/manager/PositionGet?login=100001` (`HTTP 200`)
```json
[]
```

### `POST /api/v1/trade/orders` (`HTTP 200`)
```json
{
  "ticket_id": "1001",
  "symbol": "EURUSD",
  "order_type": "BUY",
  "volume": "0.1",
  "filled_volume": "0",
  "price": null,
  "state": "FILLED",
  "created_at": "2026-09-08T23:03:33.230845Z",
  "message": "Order placed successfully"
}
```

### `PUT /api/v1/trade/orders/1001` (`HTTP 200`)
```json
{
  "status": "modified",
  "ticket_id": "1001",
  "price": "1.086",
  "stop_loss": "1.08",
  "take_profit": "1.09"
}
```

### `DELETE /api/v1/trade/orders/1001` (`HTTP 200`)
```json
{
  "status": "cancelled",
  "ticket_id": "1001"
}
```

### `GET /api/v1/account/info` (`HTTP 200`)
```json
{
  "login_id": "100001",
  "group": "REAL_STANDARD",
  "balance": "10000.00",
  "equity": "10000.00",
  "margin_used": "0",
  "margin_free": "10000.00",
  "margin_level": "999999",
  "currency": "USD"
}
```

### `GET /api/v1/account/positions` (`HTTP 200`)
```json
[]
```

### `GET /api/v1/market-data/history/EURUSD/ticks` (`HTTP 200`)
```json
{
  "symbol": "EURUSD",
  "count": 0,
  "ticks": []
}
```

### `GET /api/v1/market-data/history/EURUSD/bars` (`HTTP 200`)
```json
{
  "symbol": "EURUSD",
  "timeframe": "1m",
  "count": 0,
  "bars": []
}
```

### `GET /api/v1/admin/groups` (`HTTP 200`)
```json
[
  {
    "name": "demo_group",
    "leverage": 100,
    "margin_call_level": "60",
    "stop_out_level": "30",
    "execution_mode": "MARKET"
  },
  {
    "name": "real_group",
    "leverage": 100,
    "margin_call_level": "80",
    "stop_out_level": "50",
    "execution_mode": "MARKET"
  }
]
```

### `GET /api/v1/admin/symbols` (`HTTP 200`)
```json
[
  {
    "name": "EURUSD",
    "contract_size": "100000",
    "tick_size": "0.00001",
    "digits": 5
  },
  {
    "name": "GBPUSD",
    "contract_size": "100000",
    "tick_size": "0.00001",
    "digits": 5
  },
  {
    "name": "USDJPY",
    "contract_size": "100000",
    "tick_size": "0.001",
    "digits": 3
  },
  {
    "name": "XAUUSD",
    "contract_size": "100",
    "tick_size": "0.01",
    "digits": 2
  },
  {
    "name": "BTCUSD",
    "contract_size": "1",
    "tick_size": "0.01",
    "digits": 2
  }
]
```

### `GET /api/v1/admin/dealer-queue` (`HTTP 200`)
```json
[]
```

### `POST /api/v1/manager/OrderSend` (`HTTP 200`)
```json
{
  "answer": {
    "action": "Buy",
    "symbol": "EURUSD",
    "volume": "0.1",
    "price": "1.085",
    "stop_loss": null,
    "take_profit": null,
    "comment": null
  },
  "result": {
    "request_id": "1001",
    "order_ticket": 1001,
    "deal_ticket": null,
    "position_ticket": null,
    "price": "1.085",
    "volume": "0.1",
    "retcode": 0,
    "comment": "Order placed successfully",
    "timestamp": "2026-09-08T23:03:33.258991"
  }
}
```

### `POST /api/v1/manager/OrderClose` (`HTTP 200`)
```json
{
  "answer": {
    "action": "CLOSE",
    "symbol": "EURUSD",
    "volume": "0.1",
    "price": "1.086",
    "stop_loss": null,
    "take_profit": null,
    "comment": null
  },
  "result": {
    "request_id": "1001",
    "order_ticket": null,
    "deal_ticket": null,
    "position_ticket": 1001,
    "price": "1.086",
    "volume": "0.1",
    "retcode": 0,
    "comment": "Position closed successfully",
    "timestamp": "2026-09-08T23:03:33.262429"
  }
}
```

### `POST /api/v1/manager/OrderDelete` (`HTTP 200`)
```json
{
  "answer": {
    "action": "DELETE",
    "symbol": null,
    "volume": null,
    "price": null,
    "stop_loss": null,
    "take_profit": null,
    "comment": null
  },
  "result": {
    "request_id": "1001",
    "order_ticket": 1001,
    "deal_ticket": null,
    "position_ticket": null,
    "price": null,
    "volume": null,
    "retcode": 0,
    "comment": "Pending order cancelled successfully",
    "timestamp": "2026-09-08T23:03:33.265483"
  }
}
```

