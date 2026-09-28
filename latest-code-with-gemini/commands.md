# To Run Manager Service :- Docs on swagger : Broker Platform API

```$env:SERVICE_MODE="manager"
  python -m uvicorn api.main:app --reload --port 8001
  ```

---
# This is the trade server For LP MT5 server startup

```
python -m uvicorn api.main:app --port 8000

"path": "C:\\\\\\\\Program Files\\\\\\\\MetaTrader 5\\\\\\\\terminal64.exe",
                "login": "50080",
                "password": "!o0Od289",
                "server": "86.104.251.194:443",
  ```

---
# Commands to open and close orders

```
close A-Book orders replace tacket id at last
curl.exe -s -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMDAwIiwibG9naW4iOjEwMDAsInJvbGUiOiJTVVBFUl9BRE1JTiIsImlzX21hbmFnZXIiOnRydWUsImV4cCI6MTc5MDUxNjQxMn0.c3xXZxe39zcoNnyAhITqVj6AU8iQCiLVd3nwE32-zIc" "http://127.0.0.1:8001/api/v1/manager/OrderDelete?ticket=5311321"
```

Viewed chat2.md:1850-1879
Edited chat2.md

Here are the exact, copy-pasteable `curl.exe` commands for placing market orders and closing positions:

---

### 1. Place A-Book Market BUY Order (0.01 Lot BTCUSD)
```bash
curl.exe -s -X POST -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMDAwIiwibG9naW4iOjEwMDAsInJvbGUiOiJTVVBFUl9BRE1JTiIsImlzX21hbmFnZXIiOnRydWUsImV4cCI6MTc5MDUxNjQxMn0.c3xXZxe39zcoNnyAhITqVj6AU8iQCiLVd3nwE32-zIc" \
  "http://127.0.0.1:8001/api/v1/manager/OrderSend?id=1&login=744209&symbol=BTCUSD&operation=buy&lots=0.01&price=84000&comment=market_buy_abook&fill_type=IOC&routing=A-Book"
```

---

### 2. Place A-Book Market SELL Order (0.01 Lot BTCUSD)
```bash
curl.exe -s -X POST -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMDAwIiwibG9naW4iOjEwMDAsInJvbGUiOiJTVVBFUl9BRE1JTiIsImlzX21hbmFnZXIiOnRydWUsImV4cCI6MTc5MDUxNjQxMn0.c3xXZxe39zcoNnyAhITqVj6AU8iQCiLVd3nwE32-zIc" \
  "http://127.0.0.1:8001/api/v1/manager/OrderSend?id=1&login=744209&symbol=BTCUSD&operation=sell&lots=0.01&price=84000&comment=market_sell_abook&fill_type=IOC&routing=A-Book"
```

---

### 3. Place B-Book Market BUY Order (Internalized Risk)
```bash
curl.exe -s -X POST -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMDAwIiwibG9naW4iOjEwMDAsInJvbGUiOiJTVVBFUl9BRE1JTiIsImlzX21hbmFnZXIiOnRydWUsImV4cCI6MTc5MDUxNjQxMn0.c3xXZxe39zcoNnyAhITqVj6AU8iQCiLVd3nwE32-zIc" \
  "http://127.0.0.1:8001/api/v1/manager/OrderSend?id=1&login=744209&symbol=BTCUSD&operation=buy&lots=0.01&price=84000&comment=market_bbook_test&fill_type=IOC&routing=B-Book"
```

---

### 4. Close Open Market Position (`/OrderClose`)
Replace `<TICKET_OR_POS_ID>` with your position ticket (e.g. `5311316` or `pos_744209_BTCUSD_f19f62`):
```bash
curl.exe -s -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMDAwIiwibG9naW4iOjEwMDAsInJvbGUiOiJTVVBFUl9BRE1JTiIsImlzX21hbmFnZXIiOnRydWUsImV4cCI6MTc5MDUxNjQxMn0.c3xXZxe39zcoNnyAhITqVj6AU8iQCiLVd3nwE32-zIc" \
  "http://127.0.0.1:8001/api/v1/manager/OrderClose?ticket=<TICKET_OR_POS_ID>&lots=0.01&price=84500"
```

All details have also been logged into turn `# 🟢 Ram #-87:` / `# 🔵 Gemini #-87:` in [`chat/chat2.md`](file:///e:/references-for-AIs-to-read-main/chat/chat2.md).

---
# Market order close command

```
curl.exe -s -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMDAwIiwibG9naW4iOjEwMDAsInJvbGUiOiJTVVBFUl9BRE1JTiIsImlzX21hbmFnZXIiOnRydWUsImV4cCI6MTc5MDUxNjQxMn0.c3xXZxe39zcoNnyAhITqVj6AU8iQCiLVd3nwE32-zIc" "http://127.0.0.1:8001/api/v1/manager/OrderClose?ticket=5311326"
```