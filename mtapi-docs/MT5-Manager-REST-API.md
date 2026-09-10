# mt5 manager rest

**Version:** `v2026.08.21-08.02`

You can check test our MT5 Manager RESTfull API simply in browser. To connect to mt5 namager account you need to call method '/Connect'. It returns token that you need to use in further requests as 'id' parameter.

You can use your own account.

**Base URL:** `https://mng5.mtapi.io`  
**Alternative demo:** `https://mt5mng.mtapi.io`  
**OpenAPI Spec:** `https://mng5.mtapi.io/swagger/v1/swagger.json`

---

## Table of Contents

### Endpoint Sections
- [Connection](#connection)  (4 endpoints)
- [WebSockets](#websockets)  (18 endpoints)
- [Reports](#reports)  (13 endpoints)
- [Trading](#trading)  (7 endpoints)
- [Service](#service)  (4 endpoints)
- [Main](#main)  (66 endpoints)
- [Admin](#admin)  (1 endpoints)
- [Subscriptions](#subscriptions)  (11 endpoints)
- [Schemas](#schemas)  (128 models)

---

## Connection

_4 endpoint(s)_

### `GET /Connect`

**Summary:** Connect to account with user, password, host, port.

Returns Token that you need to use as "id" parameter for further reqests

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `user` | query | `integer(int64)` | yes | Account number. Example: 500476959 |
| `password` | query | `string` | yes | Password. Example: ehj4bod |
| `server` | query | `string` | yes | Host - ip adddress or dns name with or without port number. Example: mt4-demo.roboforex.com |
| `timeout` | query | `integer(int32)` | no | Timeout in milliseconds |
| `id` | query | `string` | no |  |
| `unsubscribe` | query | `boolean` | no |  |
| `camelCaseWs` | query | `boolean` | no | API will send data to websockets in camel case |
| `admin` | query | `boolean` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Token that need to use in futher requests as 'id' parameter | string |
| `201` | Some exception happened | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /ConnectionStatus`

**Summary:** Check connection state and reconnect if connection lost

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | ConnectionStatus object | ConnectionStatus |
| `201` | ExceptionResult object | ExceptionResult |

**Response `200` schema — `ConnectionStatus`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `isConnected` | `boolean` | no | Gets or sets a value indicating whether the terminal is currently connected. |
| `connectTimeUTC` | `string(date-time)` | no | Gets or sets the UTC timestamp of the most recent successful connection to the server. |
| `lastQuoteTimeUTC` | `string(date-time)` | no | Gets or sets the UTC timestamp of the last received market quote from the server. |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /Disconnect`

**Summary:** Connect to account with user, password, host, port.

Returns Token that you need to use as "id" parameter for further reqests

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Token that need to use in futher requests as 'id' parameter | string |
| `201` | Some exception happened | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /IsConnected`

**Summary:** Check connection with mt5 server.

Returns Token that you need to use as "id" parameter for further reqests

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Token that need to use in futher requests as 'id' parameter | boolean |
| `201` | Some exception happened | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

---

## WebSockets

_18 endpoint(s)_

### `GET /OnAccountUpdate`

**Summary:** MarginCallEnter, MarginCallLeave, StopOutEnter, StopOutLeave events

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | no | Token retuned by 'Connect' method |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | AccountUpdate |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `200` schema — `AccountUpdate`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | `AccountUpdateType` | no |  |
| `account` | `Account` | no |  |
| `group` | `ConGroup` | no |  |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /OnConnectDisconnect`

**Summary:** Connect/disconnect to mt5 server events

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | no | Token retuned by 'Connect' method |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | ConnectionState |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `200` schema — `ConnectionState`:**

**Enum:** `Connected, Disconnected`

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /OnDealUpdate`

**Summary:** Positions updates

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | no | Token retuned by 'Connect' method |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | DealUpdate |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `200` schema — `DealUpdate`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `action` | `DealUpdateAction` | no |  |
| `deal` | `Deal` | no |  |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /OnGroupUpdate`

**Summary:** Group updates

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | no | Token retuned by 'Connect' method |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | GroupUpdate |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `200` schema — `GroupUpdate`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `action` | `GroupUpdateAction` | no |  |
| `group` | `ConGroup` | no |  |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /OnMarketWatch`

**Summary:** Market watch.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | no | Token retuned by 'Connect' method |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | MarketWatch |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `200` schema — `MarketWatch`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `symbol` | `string` | no |  |
| `bid` | `number(double)` | no |  |
| `ask` | `number(double)` | no |  |
| `high` | `number(double)` | no |  |
| `low` | `number(double)` | no |  |
| `spread` | `integer(int32)` | no |  |
| `time` | `string(date-time)` | no |  |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /OnOrderProfit`

**Summary:** Order profit updates. Before first call of SubscribeOrderProfit OnOrderPorfit returns updates for all accounts.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `sendInitData` | query | `boolean` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | OrderProfitUpdate |
| `201` | ExceptionResult object | ExceptionResult |

**Response `200` schema — `OrderProfitUpdate`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `login` | `integer(int64)` | no | Account number |
| `balance` | `number(double)` | no | Balace |
| `equity` | `number(double)` | no | Equity |
| `margin` | `number(double)` | no | User margin |
| `freeMargin` | `number(double)` | no | Free margin |
| `profit` | `number(double)` | no |  |
| `orders` | `array<ProfitUpdateOrder>` | no | Opened orders |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /OnOrderProfitInterval`

**Summary:** Order profit updates. Call SubscribeOrderProfitInterval to subscibe.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | OrderProfitUpdate |
| `201` | ExceptionResult object | ExceptionResult |

**Response `200` schema — `OrderProfitUpdate`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `login` | `integer(int64)` | no | Account number |
| `balance` | `number(double)` | no | Balace |
| `equity` | `number(double)` | no | Equity |
| `margin` | `number(double)` | no | User margin |
| `freeMargin` | `number(double)` | no | Free margin |
| `profit` | `number(double)` | no |  |
| `orders` | `array<ProfitUpdateOrder>` | no | Opened orders |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /OnOrderProfitIntervalEx`

**Summary:** Order profit updates with one message. Call SubscribeOrderProfitInterval to subscibe.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | array |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /OnOrderUpdate`

**Summary:** Pending orders updates

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | no | Token retuned by 'Connect' method |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | OrderUpdate |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `200` schema — `OrderUpdate`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `action` | `OrderUpdateAction` | no |  |
| `order` | `Order` | no |  |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /OnPositionUpdate`

**Summary:** Positions updates

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | no | Token retuned by 'Connect' method |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | PositionUpdate |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `200` schema — `PositionUpdate`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `action` | `PositionUpdateAction` | no |  |
| `position` | `Position` | no |  |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /OnPositionUpdateMT4Format`

**Summary:** Positions updates

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | no | Token retuned by 'Connect' method |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | TradeRecord |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `200` schema — `TradeRecord`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `order` | `integer(int64)` | no | Order ticket |
| `login` | `integer(int64)` | no | Owner's login |
| `symbol` | `string` | no | Security |
| `digits` | `integer(int32)` | no | Security precision |
| `cmd` | `OrderType` | no |  |
| `volume` | `integer(int32)` | no | Volume |
| `openTime` | `string(date-time)` | no | Open time |
| `state` | `integer(int32)` | no | Reserved |
| `openPrice` | `number(double)` | no | Open price |
| `sl` | `number(double)` | no |  |
| `tp` | `number(double)` | no |  |
| `closeTime` | `string(date-time)` | no | Close time |
| `gwVolume` | `integer(int32)` | no | Gateway order volume |
| `expiration` | `string(date-time)` | no | Pending order's expiration time |
| `reason` | `OrderReason` | no |  |
| `convReserv` | `string` | no | Reserved fields |
| `convRates` | `array<number>` | no | Convertation rates from profit currency to group deposit currency |
| `commission` | `number(double)` | no | Commission |
| `commissionAgent` | `number(double)` | no | Agent commission |
| `storage` | `number(double)` | no | Order swaps |
| `closePrice` | `number(double)` | no | Close price |
| `profit` | `number(double)` | no | Profit |
| `taxes` | `number(double)` | no | Taxes |
| `magic` | `integer(int64)` | no | Special value used by client experts |
| `comment` | `string` | no | Comment |
| `gwOrder` | `integer(int32)` | no | Gateway order ticket |
| `activation` | `integer(int32)` | no | Used by MT Manager |
| `gwOpenPrice` | `integer(int32)` | no | Gateway order price deviation (pips) from order open price |
| `gwClosePrice` | `integer(int32)` | no | Gateway order price deviation (pips) from order close price |
| `marginRate` | `number(double)` | no | Margin convertation rate (rate of convertation from margin currency to deposit one) |
| `timestamp` | `string(date-time)` | no | Timestamp |
| `apiData` | `array<integer>` | no | For api usage |
| `action` | `DealAction` | no |  |
| `deals` | `array<Deal>` | no | Position deals |
| `lots` | `number(double)` | no | Lots |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /OnQuote`

**Summary:** Real time quotes.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | no | Token retuned by 'Connect' method |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | Quote |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `200` schema — `Quote`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `symbol` | `string` | no | Trading instrument. |
| `bid` | `number(double)` | no | Bid. |
| `ask` | `number(double)` | no | Ask. |
| `time` | `string(date-time)` | no | Server time. |
| `last` | `number(double)` | no | Last deal price. |
| `volume` | `integer(int64)` | no | Volume |
| `volumeExt` | `integer(int64)` | no | Volume ext |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /OnRequesUpdate`

**Summary:** Reqquests updates

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | no | Token retuned by 'Connect' method |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | RequestUpdate |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `200` schema — `RequestUpdate`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `action` | `RequestUpdateAction` | no |  |
| `request` | `Request` | no |  |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /OnSymbolUpdate`

**Summary:** Group updates

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | no | Token retuned by 'Connect' method |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | SymbolUpdate |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `200` schema — `SymbolUpdate`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `action` | `SymbolUpdateAction` | no |  |
| `symbol` | `ConSymbol` | no |  |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /OnTick`

**Summary:** Real time ticks.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | no | Token retuned by 'Connect' method |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | MTTick |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `200` schema — `MTTick`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `symbol` | `string` | no |  |
| `bank` | `string` | no |  |
| `datetime` | `integer(int64)` | no |  |
| `bid` | `number(double)` | no |  |
| `ask` | `number(double)` | no |  |
| `last` | `number(double)` | no |  |
| `volume` | `integer(int64)` | no |  |
| `datetime_msc` | `integer(int64)` | no |  |
| `flags` | `EnTickFlags` | no |  |
| `volume_ext` | `integer(int64)` | no |  |
| `reserved` | `array<integer>` | no |  |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /OnTickStat`

**Summary:** Tick stats.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | no | Token retuned by 'Connect' method |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | Quote |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `200` schema — `Quote`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `symbol` | `string` | no | Trading instrument. |
| `bid` | `number(double)` | no | Bid. |
| `ask` | `number(double)` | no | Ask. |
| `time` | `string(date-time)` | no | Server time. |
| `last` | `number(double)` | no | Last deal price. |
| `volume` | `integer(int64)` | no | Volume |
| `volumeExt` | `integer(int64)` | no | Volume ext |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /OnTradeDelete`

**Summary:** Deleted trades only. Fires when a position is deleted (closed or removed by admin, UpdateAction=Delete)
or when all positions of a login are cleaned (UpdateAction=Clean).
Payload is the same MT4-format trade record as /OnPositionUpdateMT4Format.
Note: deletion of history deals (e.g. DealDeleteBatch) is reported via /OnDealUpdate with Action=Delete.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | no | Token retuned by 'Connect' method |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | TradeRecord |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `200` schema — `TradeRecord`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `order` | `integer(int64)` | no | Order ticket |
| `login` | `integer(int64)` | no | Owner's login |
| `symbol` | `string` | no | Security |
| `digits` | `integer(int32)` | no | Security precision |
| `cmd` | `OrderType` | no |  |
| `volume` | `integer(int32)` | no | Volume |
| `openTime` | `string(date-time)` | no | Open time |
| `state` | `integer(int32)` | no | Reserved |
| `openPrice` | `number(double)` | no | Open price |
| `sl` | `number(double)` | no |  |
| `tp` | `number(double)` | no |  |
| `closeTime` | `string(date-time)` | no | Close time |
| `gwVolume` | `integer(int32)` | no | Gateway order volume |
| `expiration` | `string(date-time)` | no | Pending order's expiration time |
| `reason` | `OrderReason` | no |  |
| `convReserv` | `string` | no | Reserved fields |
| `convRates` | `array<number>` | no | Convertation rates from profit currency to group deposit currency |
| `commission` | `number(double)` | no | Commission |
| `commissionAgent` | `number(double)` | no | Agent commission |
| `storage` | `number(double)` | no | Order swaps |
| `closePrice` | `number(double)` | no | Close price |
| `profit` | `number(double)` | no | Profit |
| `taxes` | `number(double)` | no | Taxes |
| `magic` | `integer(int64)` | no | Special value used by client experts |
| `comment` | `string` | no | Comment |
| `gwOrder` | `integer(int32)` | no | Gateway order ticket |
| `activation` | `integer(int32)` | no | Used by MT Manager |
| `gwOpenPrice` | `integer(int32)` | no | Gateway order price deviation (pips) from order open price |
| `gwClosePrice` | `integer(int32)` | no | Gateway order price deviation (pips) from order close price |
| `marginRate` | `number(double)` | no | Margin convertation rate (rate of convertation from margin currency to deposit one) |
| `timestamp` | `string(date-time)` | no | Timestamp |
| `apiData` | `array<integer>` | no | For api usage |
| `action` | `DealAction` | no |  |
| `deals` | `array<Deal>` | no | Position deals |
| `lots` | `number(double)` | no | Lots |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /OnUserUpdate`

**Summary:** User updates

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | no | Token retuned by 'Connect' method |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | UserUpdate |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `200` schema — `UserUpdate`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `action` | `UserUpdateAction` | no |  |
| `user` | `User` | no |  |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

---

## Reports

_13 endpoint(s)_

### `GET /DailyRequest`

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes |  |
| `login` | query | `integer(int64)` | no |  |
| `from` | query | `integer(int64)` | no |  |
| `to` | query | `integer(int64)` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns Daily[] object | array |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /DailyRequestByGroup`

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes |  |
| `mask` | query | `string` | no |  |
| `from` | query | `integer(int64)` | no |  |
| `to` | query | `integer(int64)` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns Daily[] object | array |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /DailyRequestByGroupEx`

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes |  |
| `mask` | query | `string` | no |  |
| `from` | query | `string` | no |  |
| `to` | query | `string` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns Daily[] object | array |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /DailyRequestByLogins`

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes |  |
| `logins` | query | `array<integer>` | no |  |
| `from` | query | `integer(int64)` | no |  |
| `to` | query | `integer(int64)` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns Daily[] object | array |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /DailyRequestByLoginsEx`

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes |  |
| `logins` | query | `array<integer>` | no |  |
| `from` | query | `string` | no |  |
| `to` | query | `string` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns Daily[] object | array |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /DailyRequestEx`

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes |  |
| `login` | query | `integer(int64)` | no |  |
| `from` | query | `string` | no |  |
| `to` | query | `string` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns Daily[] object | array |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /DailyRequestLight`

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes |  |
| `login` | query | `integer(int64)` | no |  |
| `from` | query | `integer(int64)` | no |  |
| `to` | query | `integer(int64)` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns Daily[] object | array |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /DailyRequestLightByGroup`

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes |  |
| `mask` | query | `string` | no |  |
| `from` | query | `integer(int64)` | no |  |
| `to` | query | `integer(int64)` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns Daily[] object | array |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /DailyRequestLightByGroupEx`

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes |  |
| `mask` | query | `string` | no |  |
| `from` | query | `string` | no |  |
| `to` | query | `string` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns Daily[] object | array |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /DailyRequestLightByLogins`

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes |  |
| `logins` | query | `array<integer>` | no |  |
| `from` | query | `integer(int64)` | no |  |
| `to` | query | `integer(int64)` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns Daily[] object | array |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /DailyRequestLightByLoginsEx`

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes |  |
| `logins` | query | `array<integer>` | no |  |
| `from` | query | `string` | no |  |
| `to` | query | `string` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns Daily[] object | array |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /DailyRequestLightEx`

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes |  |
| `login` | query | `integer(int64)` | no |  |
| `from` | query | `string` | no |  |
| `to` | query | `string` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns Daily[] object | array |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /Segregated`

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes |  |
| `groupMask` | query | `string` | no |  |
| `logins` | query | `array<integer>` | no |  |
| `from` | query | `string` | no |  |
| `to` | query | `string` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns SegregatedRow[] | array |
| `201` | Returns ExceptionResult | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

---

## Trading

_7 endpoint(s)_

### `GET /DealModify`

**Summary:** Send market or pending order

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `ticket` | query | `integer(int64)` | yes | Order ticket |
| `stoploss` | query | `number(double)` | no | StopLoss |
| `takeprofit` | query | `number(double)` | no | TakeProfit |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | TradeResult |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `200` schema — `TradeResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `answer` | `Request` | no |  |
| `result` | `Confirm` | no |  |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /OrderActivate`

**Summary:** Activate order

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes |  |
| `ticket` | query | `integer(int64)` | no |  |
| `price` | query | `number(double)` | no |  |
| `lots` | query | `number(double)` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | string |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /OrderClose`

**Summary:** Close market or pending order

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `ticket` | query | `integer(int64)` | yes | Order ticket |
| `lots` | query | `number(double)` | no | Lots. Optional. |
| `price` | query | `number(double)` | no | Price. Optional, but required in case of Instant Execution. |
| `deviation` | query | `integer(int64)` | no | Slippage. Optional. |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Order object | TradeResult |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `200` schema — `TradeResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `answer` | `Request` | no |  |
| `result` | `Confirm` | no |  |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /OrderCloseAll`

**Summary:** Close market or pending order

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `logins` | query | `array<integer>` | yes | Accounts list |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Order object | string |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /OrderDelete`

**Summary:** Delete order

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes |  |
| `ticket` | query | `integer(int64)` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | string |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /OrderModify`

**Summary:** Send market or pending order

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `ticket` | query | `integer(int64)` | yes | Order ticket |
| `price` | query | `number(double)` | no | Price |
| `stoploss` | query | `number(double)` | no | StopLoss |
| `takeprofit` | query | `number(double)` | no | TakeProfit |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | TradeResult |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `200` schema — `TradeResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `answer` | `Request` | no |  |
| `result` | `Confirm` | no |  |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /OrderSend`

**Summary:** Send market or pending order

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `login` | query | `integer(int64)` | yes |  |
| `symbol` | query | `string` | yes | Symbol |
| `operation` | query | `OrderType` | yes | But or sell, market or pending |
| `lots` | query | `number(double)` | yes | Lots |
| `price` | query | `number(double)` | no | Price |
| `deviation` | query | `integer(int64)` | no | Slippage |
| `stoploss` | query | `number(double)` | no | StopLoss |
| `takeprofit` | query | `number(double)` | no | TakeProfit |
| `comment` | query | `string` | no | Comment |
| `priceTrigger` | query | `number(double)` | no |  |
| `expiration` | query | `string(date-time)` | no | Pending order expiartion time |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Server answer | TradeResult |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `200` schema — `TradeResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `answer` | `Request` | no |  |
| `result` | `Confirm` | no |  |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

---

## Service

_4 endpoint(s)_

### `GET /MemoryUsage`

**Summary:** Memory usage details

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns memory usage details | MemUsage |

**Response `200` schema — `MemUsage`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `is64BitProcess` | `boolean` | no |  |
| `physicalMemoryUsage` | `integer(int32)` | no |  |
| `basePriority` | `integer(int32)` | no |  |
| `priorityClass` | `string` | no |  |
| `userProcessorTime` | `string` | no |  |
| `privilegedProcessorTime` | `string` | no |  |
| `totalProcessorTime` | `string` | no |  |
| `pagedSystemMemorySize` | `integer(int32)` | no |  |
| `pagedMemorySize` | `integer(int32)` | no |  |
| `peakPagedMem` | `integer(int32)` | no |  |
| `peakVirtualMem` | `integer(int32)` | no |  |
| `peakWorkingSet` | `integer(int32)` | no |  |
| `memoryLoadBytes` | `integer(int32)` | no |  |
| `heapSizeBytes` | `integer(int32)` | no |  |
| `fragmentedBytes` | `integer(int32)` | no |  |
| `highMemoryLoadThresholdBytes` | `integer(int32)` | no |  |
| `totalAvailableMemoryBytes` | `integer(int32)` | no |  |
| `responding` | `boolean` | no |  |

### `GET /Ping`

**Summary:** Simple test without parameters

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | string |

### `GET /ReadMe`

**Summary:** readme.md as html

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | OK |  |

### `GET /StartTimeUtc`

**Summary:** StartTimeUtc

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns service start time in UTC timezone | string |

---

## Main

_66 endpoint(s)_

### `GET /AccountCreate`

**Summary:** Create new user. Need to specify at least first and last name, group and leverage.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes |  |
| `master_pass` | query | `string` | yes |  |
| `investor_pass` | query | `string` | yes |  |
| `enabled` | query | `boolean` | no |  |
| `ClientID` | query | `integer(int64)` | no |  |
| `FirstName` | query | `string` | no |  |
| `LastName` | query | `string` | no |  |
| `MiddleName` | query | `string` | no |  |
| `OTPSecret` | query | `string` | no |  |
| `LimitOrders` | query | `integer(int32)` | no |  |
| `LimitPositionsValue` | query | `number(double)` | no |  |
| `Login` | query | `integer(int64)` | no |  |
| `Group` | query | `string` | no |  |
| `CertSerialNumber` | query | `integer(int64)` | no |  |
| `Rights` | query | `UsersRights` | no |  |
| `Registration` | query | `integer(int64)` | no |  |
| `LastAccess` | query | `integer(int64)` | no |  |
| `LastIP` | query | `string` | no |  |
| `Name` | query | `string` | no |  |
| `Company` | query | `string` | no |  |
| `Account` | query | `string` | no |  |
| `Country` | query | `string` | no |  |
| `Language` | query | `integer(int32)` | no |  |
| `City` | query | `string` | no |  |
| `State` | query | `string` | no |  |
| `ZIPCode` | query | `string` | no |  |
| `Address` | query | `string` | no |  |
| `Phone` | query | `string` | no |  |
| `EMail` | query | `string` | no |  |
| `ID` | query | `string` | no |  |
| `Status` | query | `string` | no |  |
| `Comment` | query | `string` | no |  |
| `Color` | query | `integer(int32)` | no |  |
| `PhonePassword` | query | `string` | no |  |
| `Leverage` | query | `integer(int32)` | no |  |
| `Agent` | query | `integer(int64)` | no |  |
| `Balance` | query | `number(double)` | no |  |
| `Credit` | query | `number(double)` | no |  |
| `InterestRate` | query | `number(double)` | no |  |
| `CommissionDaily` | query | `number(double)` | no |  |
| `CommissionMonthly` | query | `number(double)` | no |  |
| `CommissionAgentDaily` | query | `number(double)` | no |  |
| `CommissionAgentMonthly` | query | `number(double)` | no |  |
| `BalancePrevDay` | query | `number(double)` | no |  |
| `BalancePrevMonth` | query | `number(double)` | no |  |
| `EquityPrevDay` | query | `number(double)` | no |  |
| `EquityPrevMonth` | query | `number(double)` | no |  |
| `LastPassChange` | query | `integer(int64)` | no |  |
| `LeadCampaign` | query | `string` | no |  |
| `LeadSource` | query | `string` | no |  |
| `ApiDataClearAll` | query | `MTRetCode` | no |  |
| `ExternalAccountClear` | query | `MTRetCode` | no |  |
| `ExternalAccountTotal` | query | `integer(int32)` | no |  |
| `MQID` | query | `string` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns user | User |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `200` schema — `User`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `clientID` | `integer(int64)` | no |  |
| `firstName` | `string` | no |  |
| `lastName` | `string` | no |  |
| `middleName` | `string` | no |  |
| `otpSecret` | `string` | no |  |
| `limitOrders` | `integer(int32)` | no |  |
| `limitPositionsValue` | `number(double)` | no |  |
| `login` | `integer(int64)` | no |  |
| `group` | `string` | no |  |
| `certSerialNumber` | `integer(int64)` | no |  |
| `rights` | `UsersRights` | no |  |
| `registration` | `integer(int64)` | no |  |
| `lastAccess` | `integer(int64)` | no |  |
| `lastIP` | `string` | no |  |
| `name` | `string` | no |  |
| `company` | `string` | no |  |
| `account` | `string` | no |  |
| `country` | `string` | no |  |
| `language` | `integer(int32)` | no |  |
| `city` | `string` | no |  |
| `state` | `string` | no |  |
| `zipCode` | `string` | no |  |
| `address` | `string` | no |  |
| `phone` | `string` | no |  |
| `eMail` | `string` | no |  |
| `id` | `string` | no |  |
| `status` | `string` | no |  |
| `comment` | `string` | no |  |
| `color` | `integer(int32)` | no |  |
| `phonePassword` | `string` | no |  |
| `leverage` | `integer(int32)` | no |  |
| `agent` | `integer(int64)` | no |  |
| `balance` | `number(double)` | no |  |
| `credit` | `number(double)` | no |  |
| `interestRate` | `number(double)` | no |  |
| `commissionDaily` | `number(double)` | no |  |
| `commissionMonthly` | `number(double)` | no |  |
| `commissionAgentDaily` | `number(double)` | no |  |
| `commissionAgentMonthly` | `number(double)` | no |  |
| `balancePrevDay` | `number(double)` | no |  |
| `balancePrevMonth` | `number(double)` | no |  |
| `equityPrevDay` | `number(double)` | no |  |
| `equityPrevMonth` | `number(double)` | no |  |
| `lastPassChange` | `integer(int64)` | no |  |
| `leadCampaign` | `string` | no |  |
| `leadSource` | `string` | no |  |
| `apiDataClearAll` | `MTRetCode` | no |  |
| `externalAccountClear` | `MTRetCode` | no |  |
| `externalAccountTotal` | `integer(int32)` | no |  |
| `mqid` | `string` | no |  |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /AccountCreateAndDeposit`

**Summary:** Create new user. Need to specify at least first and last name, group and leverage.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes |  |
| `master_pass` | query | `string` | yes |  |
| `investor_pass` | query | `string` | yes |  |
| `enabled` | query | `boolean` | no |  |
| `amount` | query | `number(double)` | no |  |
| `ClientID` | query | `integer(int64)` | no |  |
| `FirstName` | query | `string` | no |  |
| `LastName` | query | `string` | no |  |
| `MiddleName` | query | `string` | no |  |
| `OTPSecret` | query | `string` | no |  |
| `LimitOrders` | query | `integer(int32)` | no |  |
| `LimitPositionsValue` | query | `number(double)` | no |  |
| `Login` | query | `integer(int64)` | no |  |
| `Group` | query | `string` | no |  |
| `CertSerialNumber` | query | `integer(int64)` | no |  |
| `Rights` | query | `UsersRights` | no |  |
| `Registration` | query | `integer(int64)` | no |  |
| `LastAccess` | query | `integer(int64)` | no |  |
| `LastIP` | query | `string` | no |  |
| `Name` | query | `string` | no |  |
| `Company` | query | `string` | no |  |
| `Account` | query | `string` | no |  |
| `Country` | query | `string` | no |  |
| `Language` | query | `integer(int32)` | no |  |
| `City` | query | `string` | no |  |
| `State` | query | `string` | no |  |
| `ZIPCode` | query | `string` | no |  |
| `Address` | query | `string` | no |  |
| `Phone` | query | `string` | no |  |
| `EMail` | query | `string` | no |  |
| `ID` | query | `string` | no |  |
| `Status` | query | `string` | no |  |
| `Comment` | query | `string` | no |  |
| `Color` | query | `integer(int32)` | no |  |
| `PhonePassword` | query | `string` | no |  |
| `Leverage` | query | `integer(int32)` | no |  |
| `Agent` | query | `integer(int64)` | no |  |
| `Balance` | query | `number(double)` | no |  |
| `Credit` | query | `number(double)` | no |  |
| `InterestRate` | query | `number(double)` | no |  |
| `CommissionDaily` | query | `number(double)` | no |  |
| `CommissionMonthly` | query | `number(double)` | no |  |
| `CommissionAgentDaily` | query | `number(double)` | no |  |
| `CommissionAgentMonthly` | query | `number(double)` | no |  |
| `BalancePrevDay` | query | `number(double)` | no |  |
| `BalancePrevMonth` | query | `number(double)` | no |  |
| `EquityPrevDay` | query | `number(double)` | no |  |
| `EquityPrevMonth` | query | `number(double)` | no |  |
| `LastPassChange` | query | `integer(int64)` | no |  |
| `LeadCampaign` | query | `string` | no |  |
| `LeadSource` | query | `string` | no |  |
| `ApiDataClearAll` | query | `MTRetCode` | no |  |
| `ExternalAccountClear` | query | `MTRetCode` | no |  |
| `ExternalAccountTotal` | query | `integer(int32)` | no |  |
| `MQID` | query | `string` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns user | User |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `200` schema — `User`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `clientID` | `integer(int64)` | no |  |
| `firstName` | `string` | no |  |
| `lastName` | `string` | no |  |
| `middleName` | `string` | no |  |
| `otpSecret` | `string` | no |  |
| `limitOrders` | `integer(int32)` | no |  |
| `limitPositionsValue` | `number(double)` | no |  |
| `login` | `integer(int64)` | no |  |
| `group` | `string` | no |  |
| `certSerialNumber` | `integer(int64)` | no |  |
| `rights` | `UsersRights` | no |  |
| `registration` | `integer(int64)` | no |  |
| `lastAccess` | `integer(int64)` | no |  |
| `lastIP` | `string` | no |  |
| `name` | `string` | no |  |
| `company` | `string` | no |  |
| `account` | `string` | no |  |
| `country` | `string` | no |  |
| `language` | `integer(int32)` | no |  |
| `city` | `string` | no |  |
| `state` | `string` | no |  |
| `zipCode` | `string` | no |  |
| `address` | `string` | no |  |
| `phone` | `string` | no |  |
| `eMail` | `string` | no |  |
| `id` | `string` | no |  |
| `status` | `string` | no |  |
| `comment` | `string` | no |  |
| `color` | `integer(int32)` | no |  |
| `phonePassword` | `string` | no |  |
| `leverage` | `integer(int32)` | no |  |
| `agent` | `integer(int64)` | no |  |
| `balance` | `number(double)` | no |  |
| `credit` | `number(double)` | no |  |
| `interestRate` | `number(double)` | no |  |
| `commissionDaily` | `number(double)` | no |  |
| `commissionMonthly` | `number(double)` | no |  |
| `commissionAgentDaily` | `number(double)` | no |  |
| `commissionAgentMonthly` | `number(double)` | no |  |
| `balancePrevDay` | `number(double)` | no |  |
| `balancePrevMonth` | `number(double)` | no |  |
| `equityPrevDay` | `number(double)` | no |  |
| `equityPrevMonth` | `number(double)` | no |  |
| `lastPassChange` | `integer(int64)` | no |  |
| `leadCampaign` | `string` | no |  |
| `leadSource` | `string` | no |  |
| `apiDataClearAll` | `MTRetCode` | no |  |
| `externalAccountClear` | `MTRetCode` | no |  |
| `externalAccountTotal` | `integer(int32)` | no |  |
| `mqid` | `string` | no |  |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /AccountDelete`

**Summary:** Delete account

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `login` | query | `integer(int64)` | yes | Login number |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | 'OK' | string |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /AccountDetails`

**Summary:** Account details

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `login` | query | `integer(int64)` | no | Login number |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Account array | Account |
| `201` | ExceptionResult object | ExceptionResult |

**Response `200` schema — `Account`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `login` | `integer(int64)` | no |  |
| `currencyDigits` | `integer(int32)` | no |  |
| `balance` | `number(double)` | no |  |
| `credit` | `number(double)` | no |  |
| `margin` | `number(double)` | no |  |
| `marginFree` | `number(double)` | no |  |
| `marginLevel` | `number(double)` | no |  |
| `marginLeverage` | `integer(int32)` | no |  |
| `profit` | `number(double)` | no |  |
| `storage` | `number(double)` | no |  |
| `floating` | `number(double)` | no |  |
| `equity` | `number(double)` | no |  |
| `soActivation` | `EnSoActivation` | no |  |
| `soTime` | `integer(int64)` | no |  |
| `soLevel` | `number(double)` | no |  |
| `soEquity` | `number(double)` | no |  |
| `soMargin` | `number(double)` | no |  |
| `blockedCommission` | `number(double)` | no |  |
| `blockedProfit` | `number(double)` | no |  |
| `marginInitial` | `number(double)` | no |  |
| `marginMaintenance` | `number(double)` | no |  |
| `assets` | `number(double)` | no |  |
| `liabilities` | `number(double)` | no |  |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /AccountDetailsMany`

**Summary:** Accounts details. If logins not specifed reutns details for all accoungts.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `login` | query | `array<integer>` | no | Login number |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | AccountSummary array | array |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /Accounts`

**Summary:** Account numbers

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | AccountSummary array | array |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /AccountsOnline`

**Summary:** Online account details

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Online array | array |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /AccountsSummary`

**Summary:** Accounts Balance, Equity,Profit, etc

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `login` | query | `array<integer>` | no | User number |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | AccountSummary array | array |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /AdmTradeRecordModify`

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes |  |
| `ticket` | query | `integer(int64)` | yes |  |
| `openPrice` | query | `number(double)` | no |  |
| `closePrice` | query | `number(double)` | no |  |
| `volume` | query | `number(double)` | no |  |
| `sl` | query | `number(double)` | no |  |
| `tp` | query | `number(double)` | no |  |
| `comment` | query | `string` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns updated TradeRecord | TradeRecord |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `200` schema — `TradeRecord`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `order` | `integer(int64)` | no | Order ticket |
| `login` | `integer(int64)` | no | Owner's login |
| `symbol` | `string` | no | Security |
| `digits` | `integer(int32)` | no | Security precision |
| `cmd` | `OrderType` | no |  |
| `volume` | `integer(int32)` | no | Volume |
| `openTime` | `string(date-time)` | no | Open time |
| `state` | `integer(int32)` | no | Reserved |
| `openPrice` | `number(double)` | no | Open price |
| `sl` | `number(double)` | no |  |
| `tp` | `number(double)` | no |  |
| `closeTime` | `string(date-time)` | no | Close time |
| `gwVolume` | `integer(int32)` | no | Gateway order volume |
| `expiration` | `string(date-time)` | no | Pending order's expiration time |
| `reason` | `OrderReason` | no |  |
| `convReserv` | `string` | no | Reserved fields |
| `convRates` | `array<number>` | no | Convertation rates from profit currency to group deposit currency |
| `commission` | `number(double)` | no | Commission |
| `commissionAgent` | `number(double)` | no | Agent commission |
| `storage` | `number(double)` | no | Order swaps |
| `closePrice` | `number(double)` | no | Close price |
| `profit` | `number(double)` | no | Profit |
| `taxes` | `number(double)` | no | Taxes |
| `magic` | `integer(int64)` | no | Special value used by client experts |
| `comment` | `string` | no | Comment |
| `gwOrder` | `integer(int32)` | no | Gateway order ticket |
| `activation` | `integer(int32)` | no | Used by MT Manager |
| `gwOpenPrice` | `integer(int32)` | no | Gateway order price deviation (pips) from order open price |
| `gwClosePrice` | `integer(int32)` | no | Gateway order price deviation (pips) from order close price |
| `marginRate` | `number(double)` | no | Margin convertation rate (rate of convertation from margin currency to deposit one) |
| `timestamp` | `string(date-time)` | no | Timestamp |
| `apiData` | `array<integer>` | no | For api usage |
| `action` | `DealAction` | no |  |
| `deals` | `array<Deal>` | no | Position deals |
| `lots` | `number(double)` | no | Lots |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `POST /AdmTradeRecordModifyEx`

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes |  |

**Request Body**

**Content-Type:** `application/json-patch+json`


| Field | Type | Required | Description |
|---|---|---|---|
| `order` | `integer(int64)` | no | Order ticket |
| `login` | `integer(int64)` | no | Owner's login |
| `symbol` | `string` | no | Security |
| `digits` | `integer(int32)` | no | Security precision |
| `cmd` | `OrderType` | no |  |
| `volume` | `integer(int32)` | no | Volume |
| `openTime` | `string(date-time)` | no | Open time |
| `state` | `integer(int32)` | no | Reserved |
| `openPrice` | `number(double)` | no | Open price |
| `sl` | `number(double)` | no |  |
| `tp` | `number(double)` | no |  |
| `closeTime` | `string(date-time)` | no | Close time |
| `gwVolume` | `integer(int32)` | no | Gateway order volume |
| `expiration` | `string(date-time)` | no | Pending order's expiration time |
| `reason` | `OrderReason` | no |  |
| `convReserv` | `string` | no | Reserved fields |
| `convRates` | `array<number>` | no | Convertation rates from profit currency to group deposit currency |
| `commission` | `number(double)` | no | Commission |
| `commissionAgent` | `number(double)` | no | Agent commission |
| `storage` | `number(double)` | no | Order swaps |
| `closePrice` | `number(double)` | no | Close price |
| `profit` | `number(double)` | no | Profit |
| `taxes` | `number(double)` | no | Taxes |
| `magic` | `integer(int64)` | no | Special value used by client experts |
| `comment` | `string` | no | Comment |
| `gwOrder` | `integer(int32)` | no | Gateway order ticket |
| `activation` | `integer(int32)` | no | Used by MT Manager |
| `gwOpenPrice` | `integer(int32)` | no | Gateway order price deviation (pips) from order open price |
| `gwClosePrice` | `integer(int32)` | no | Gateway order price deviation (pips) from order close price |
| `marginRate` | `number(double)` | no | Margin convertation rate (rate of convertation from margin currency to deposit one) |
| `timestamp` | `string(date-time)` | no | Timestamp |
| `apiData` | `array<integer>` | no | For api usage |
| `action` | `DealAction` | no |  |
| `deals` | `array<Deal>` | no | Position deals |
| `lots` | `number(double)` | no | Lots |

See schema: `TradeRecord`

**Content-Type:** `application/json`


| Field | Type | Required | Description |
|---|---|---|---|
| `order` | `integer(int64)` | no | Order ticket |
| `login` | `integer(int64)` | no | Owner's login |
| `symbol` | `string` | no | Security |
| `digits` | `integer(int32)` | no | Security precision |
| `cmd` | `OrderType` | no |  |
| `volume` | `integer(int32)` | no | Volume |
| `openTime` | `string(date-time)` | no | Open time |
| `state` | `integer(int32)` | no | Reserved |
| `openPrice` | `number(double)` | no | Open price |
| `sl` | `number(double)` | no |  |
| `tp` | `number(double)` | no |  |
| `closeTime` | `string(date-time)` | no | Close time |
| `gwVolume` | `integer(int32)` | no | Gateway order volume |
| `expiration` | `string(date-time)` | no | Pending order's expiration time |
| `reason` | `OrderReason` | no |  |
| `convReserv` | `string` | no | Reserved fields |
| `convRates` | `array<number>` | no | Convertation rates from profit currency to group deposit currency |
| `commission` | `number(double)` | no | Commission |
| `commissionAgent` | `number(double)` | no | Agent commission |
| `storage` | `number(double)` | no | Order swaps |
| `closePrice` | `number(double)` | no | Close price |
| `profit` | `number(double)` | no | Profit |
| `taxes` | `number(double)` | no | Taxes |
| `magic` | `integer(int64)` | no | Special value used by client experts |
| `comment` | `string` | no | Comment |
| `gwOrder` | `integer(int32)` | no | Gateway order ticket |
| `activation` | `integer(int32)` | no | Used by MT Manager |
| `gwOpenPrice` | `integer(int32)` | no | Gateway order price deviation (pips) from order open price |
| `gwClosePrice` | `integer(int32)` | no | Gateway order price deviation (pips) from order close price |
| `marginRate` | `number(double)` | no | Margin convertation rate (rate of convertation from margin currency to deposit one) |
| `timestamp` | `string(date-time)` | no | Timestamp |
| `apiData` | `array<integer>` | no | For api usage |
| `action` | `DealAction` | no |  |
| `deals` | `array<Deal>` | no | Position deals |
| `lots` | `number(double)` | no | Lots |

See schema: `TradeRecord`

**Content-Type:** `text/json`


| Field | Type | Required | Description |
|---|---|---|---|
| `order` | `integer(int64)` | no | Order ticket |
| `login` | `integer(int64)` | no | Owner's login |
| `symbol` | `string` | no | Security |
| `digits` | `integer(int32)` | no | Security precision |
| `cmd` | `OrderType` | no |  |
| `volume` | `integer(int32)` | no | Volume |
| `openTime` | `string(date-time)` | no | Open time |
| `state` | `integer(int32)` | no | Reserved |
| `openPrice` | `number(double)` | no | Open price |
| `sl` | `number(double)` | no |  |
| `tp` | `number(double)` | no |  |
| `closeTime` | `string(date-time)` | no | Close time |
| `gwVolume` | `integer(int32)` | no | Gateway order volume |
| `expiration` | `string(date-time)` | no | Pending order's expiration time |
| `reason` | `OrderReason` | no |  |
| `convReserv` | `string` | no | Reserved fields |
| `convRates` | `array<number>` | no | Convertation rates from profit currency to group deposit currency |
| `commission` | `number(double)` | no | Commission |
| `commissionAgent` | `number(double)` | no | Agent commission |
| `storage` | `number(double)` | no | Order swaps |
| `closePrice` | `number(double)` | no | Close price |
| `profit` | `number(double)` | no | Profit |
| `taxes` | `number(double)` | no | Taxes |
| `magic` | `integer(int64)` | no | Special value used by client experts |
| `comment` | `string` | no | Comment |
| `gwOrder` | `integer(int32)` | no | Gateway order ticket |
| `activation` | `integer(int32)` | no | Used by MT Manager |
| `gwOpenPrice` | `integer(int32)` | no | Gateway order price deviation (pips) from order open price |
| `gwClosePrice` | `integer(int32)` | no | Gateway order price deviation (pips) from order close price |
| `marginRate` | `number(double)` | no | Margin convertation rate (rate of convertation from margin currency to deposit one) |
| `timestamp` | `string(date-time)` | no | Timestamp |
| `apiData` | `array<integer>` | no | For api usage |
| `action` | `DealAction` | no |  |
| `deals` | `array<Deal>` | no | Position deals |
| `lots` | `number(double)` | no | Lots |

See schema: `TradeRecord`

**Content-Type:** `application/*+json`


| Field | Type | Required | Description |
|---|---|---|---|
| `order` | `integer(int64)` | no | Order ticket |
| `login` | `integer(int64)` | no | Owner's login |
| `symbol` | `string` | no | Security |
| `digits` | `integer(int32)` | no | Security precision |
| `cmd` | `OrderType` | no |  |
| `volume` | `integer(int32)` | no | Volume |
| `openTime` | `string(date-time)` | no | Open time |
| `state` | `integer(int32)` | no | Reserved |
| `openPrice` | `number(double)` | no | Open price |
| `sl` | `number(double)` | no |  |
| `tp` | `number(double)` | no |  |
| `closeTime` | `string(date-time)` | no | Close time |
| `gwVolume` | `integer(int32)` | no | Gateway order volume |
| `expiration` | `string(date-time)` | no | Pending order's expiration time |
| `reason` | `OrderReason` | no |  |
| `convReserv` | `string` | no | Reserved fields |
| `convRates` | `array<number>` | no | Convertation rates from profit currency to group deposit currency |
| `commission` | `number(double)` | no | Commission |
| `commissionAgent` | `number(double)` | no | Agent commission |
| `storage` | `number(double)` | no | Order swaps |
| `closePrice` | `number(double)` | no | Close price |
| `profit` | `number(double)` | no | Profit |
| `taxes` | `number(double)` | no | Taxes |
| `magic` | `integer(int64)` | no | Special value used by client experts |
| `comment` | `string` | no | Comment |
| `gwOrder` | `integer(int32)` | no | Gateway order ticket |
| `activation` | `integer(int32)` | no | Used by MT Manager |
| `gwOpenPrice` | `integer(int32)` | no | Gateway order price deviation (pips) from order open price |
| `gwClosePrice` | `integer(int32)` | no | Gateway order price deviation (pips) from order close price |
| `marginRate` | `number(double)` | no | Margin convertation rate (rate of convertation from margin currency to deposit one) |
| `timestamp` | `string(date-time)` | no | Timestamp |
| `apiData` | `array<integer>` | no | For api usage |
| `action` | `DealAction` | no |  |
| `deals` | `array<Deal>` | no | Position deals |
| `lots` | `number(double)` | no | Lots |

See schema: `TradeRecord`

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns updated TradeRecord | TradeRecord |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `200` schema — `TradeRecord`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `order` | `integer(int64)` | no | Order ticket |
| `login` | `integer(int64)` | no | Owner's login |
| `symbol` | `string` | no | Security |
| `digits` | `integer(int32)` | no | Security precision |
| `cmd` | `OrderType` | no |  |
| `volume` | `integer(int32)` | no | Volume |
| `openTime` | `string(date-time)` | no | Open time |
| `state` | `integer(int32)` | no | Reserved |
| `openPrice` | `number(double)` | no | Open price |
| `sl` | `number(double)` | no |  |
| `tp` | `number(double)` | no |  |
| `closeTime` | `string(date-time)` | no | Close time |
| `gwVolume` | `integer(int32)` | no | Gateway order volume |
| `expiration` | `string(date-time)` | no | Pending order's expiration time |
| `reason` | `OrderReason` | no |  |
| `convReserv` | `string` | no | Reserved fields |
| `convRates` | `array<number>` | no | Convertation rates from profit currency to group deposit currency |
| `commission` | `number(double)` | no | Commission |
| `commissionAgent` | `number(double)` | no | Agent commission |
| `storage` | `number(double)` | no | Order swaps |
| `closePrice` | `number(double)` | no | Close price |
| `profit` | `number(double)` | no | Profit |
| `taxes` | `number(double)` | no | Taxes |
| `magic` | `integer(int64)` | no | Special value used by client experts |
| `comment` | `string` | no | Comment |
| `gwOrder` | `integer(int32)` | no | Gateway order ticket |
| `activation` | `integer(int32)` | no | Used by MT Manager |
| `gwOpenPrice` | `integer(int32)` | no | Gateway order price deviation (pips) from order open price |
| `gwClosePrice` | `integer(int32)` | no | Gateway order price deviation (pips) from order close price |
| `marginRate` | `number(double)` | no | Margin convertation rate (rate of convertation from margin currency to deposit one) |
| `timestamp` | `string(date-time)` | no | Timestamp |
| `apiData` | `array<integer>` | no | For api usage |
| `action` | `DealAction` | no |  |
| `deals` | `array<Deal>` | no | Position deals |
| `lots` | `number(double)` | no | Lots |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /AdmTradesDelete`

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes |  |
| `tickets` | query | `array<integer>` | yes |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | string |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /BalanceAdjustment`

**Summary:** Deposit/withdraw

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `login` | query | `integer(int64)` | yes | User account |
| `amount` | query | `number(double)` | yes | Amount. If negative - withdraw. |
| `action` | query | `EnDealAction` | yes |  |
| `comment` | query | `string` | yes | Comment |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Order object | integer |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /ChartRequest`

**Summary:** OHLC history

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `symbol` | query | `string` | yes | Symbol |
| `from` | query | `string` | yes | From date' in format: yyyy-MM-ddTHH:mm:ss |
| `to` | query | `string` | yes | To date' in format: yyyy-MM-ddTHH:mm:ss |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns MTChartBar[] object | array |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `POST /DealAdd`

**Summary:** Adds a new deal.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |

**Request Body**

**Content-Type:** `application/json-patch+json`


| Field | Type | Required | Description |
|---|---|---|---|
| `priceSL` | `number(double)` | no |  |
| `priceTP` | `number(double)` | no |  |
| `volumeExt` | `integer(int64)` | no |  |
| `volumeClosedExt` | `integer(int64)` | no |  |
| `fee` | `number(double)` | no |  |
| `value` | `number(double)` | no |  |
| `marketBid` | `number(double)` | no |  |
| `marketAsk` | `number(double)` | no |  |
| `marketLast` | `number(double)` | no |  |
| `print` | `string` | no |  |
| `dealTicket` | `integer(int64)` | no |  |
| `externalID` | `string` | no |  |
| `login` | `integer(int64)` | no |  |
| `dealer` | `integer(int64)` | no |  |
| `order` | `integer(int64)` | no |  |
| `action` | `DealAction` | no |  |
| `entry` | `EntryFlag` | no |  |
| `digits` | `integer(int32)` | no |  |
| `digitsCurrency` | `integer(int32)` | no |  |
| `contractSize` | `number(double)` | no |  |
| `time` | `integer(int64)` | no |  |
| `symbol` | `string` | no |  |
| `price` | `number(double)` | no |  |
| `volume` | `integer(int64)` | no |  |
| `profit` | `number(double)` | no |  |
| `storage` | `number(double)` | no |  |
| `commission` | `number(double)` | no |  |
| `obsoleteValue` | `number(double)` | no |  |
| `rateProfit` | `number(double)` | no |  |
| `rateMargin` | `number(double)` | no |  |
| `expertID` | `integer(int64)` | no |  |
| `positionID` | `integer(int64)` | no |  |
| `comment` | `string` | no |  |
| `apiDataClearAll` | `MTRetCode` | no |  |
| `profitRaw` | `number(double)` | no |  |
| `pricePosition` | `number(double)` | no |  |
| `volumeClosed` | `integer(int64)` | no |  |
| `tickValue` | `number(double)` | no |  |
| `tickSize` | `number(double)` | no |  |
| `flags` | `integer(int64)` | no |  |
| `timeMsc` | `integer(int64)` | no |  |
| `reason` | `OrderReason` | no |  |
| `gateway` | `string` | no |  |
| `priceGateway` | `number(double)` | no |  |
| `modificationFlags` | `integer(int32)` | no |  |
| `lots` | `number(double)` | no |  |

See schema: `Deal`

**Content-Type:** `application/json`


| Field | Type | Required | Description |
|---|---|---|---|
| `priceSL` | `number(double)` | no |  |
| `priceTP` | `number(double)` | no |  |
| `volumeExt` | `integer(int64)` | no |  |
| `volumeClosedExt` | `integer(int64)` | no |  |
| `fee` | `number(double)` | no |  |
| `value` | `number(double)` | no |  |
| `marketBid` | `number(double)` | no |  |
| `marketAsk` | `number(double)` | no |  |
| `marketLast` | `number(double)` | no |  |
| `print` | `string` | no |  |
| `dealTicket` | `integer(int64)` | no |  |
| `externalID` | `string` | no |  |
| `login` | `integer(int64)` | no |  |
| `dealer` | `integer(int64)` | no |  |
| `order` | `integer(int64)` | no |  |
| `action` | `DealAction` | no |  |
| `entry` | `EntryFlag` | no |  |
| `digits` | `integer(int32)` | no |  |
| `digitsCurrency` | `integer(int32)` | no |  |
| `contractSize` | `number(double)` | no |  |
| `time` | `integer(int64)` | no |  |
| `symbol` | `string` | no |  |
| `price` | `number(double)` | no |  |
| `volume` | `integer(int64)` | no |  |
| `profit` | `number(double)` | no |  |
| `storage` | `number(double)` | no |  |
| `commission` | `number(double)` | no |  |
| `obsoleteValue` | `number(double)` | no |  |
| `rateProfit` | `number(double)` | no |  |
| `rateMargin` | `number(double)` | no |  |
| `expertID` | `integer(int64)` | no |  |
| `positionID` | `integer(int64)` | no |  |
| `comment` | `string` | no |  |
| `apiDataClearAll` | `MTRetCode` | no |  |
| `profitRaw` | `number(double)` | no |  |
| `pricePosition` | `number(double)` | no |  |
| `volumeClosed` | `integer(int64)` | no |  |
| `tickValue` | `number(double)` | no |  |
| `tickSize` | `number(double)` | no |  |
| `flags` | `integer(int64)` | no |  |
| `timeMsc` | `integer(int64)` | no |  |
| `reason` | `OrderReason` | no |  |
| `gateway` | `string` | no |  |
| `priceGateway` | `number(double)` | no |  |
| `modificationFlags` | `integer(int32)` | no |  |
| `lots` | `number(double)` | no |  |

See schema: `Deal`

**Content-Type:** `text/json`


| Field | Type | Required | Description |
|---|---|---|---|
| `priceSL` | `number(double)` | no |  |
| `priceTP` | `number(double)` | no |  |
| `volumeExt` | `integer(int64)` | no |  |
| `volumeClosedExt` | `integer(int64)` | no |  |
| `fee` | `number(double)` | no |  |
| `value` | `number(double)` | no |  |
| `marketBid` | `number(double)` | no |  |
| `marketAsk` | `number(double)` | no |  |
| `marketLast` | `number(double)` | no |  |
| `print` | `string` | no |  |
| `dealTicket` | `integer(int64)` | no |  |
| `externalID` | `string` | no |  |
| `login` | `integer(int64)` | no |  |
| `dealer` | `integer(int64)` | no |  |
| `order` | `integer(int64)` | no |  |
| `action` | `DealAction` | no |  |
| `entry` | `EntryFlag` | no |  |
| `digits` | `integer(int32)` | no |  |
| `digitsCurrency` | `integer(int32)` | no |  |
| `contractSize` | `number(double)` | no |  |
| `time` | `integer(int64)` | no |  |
| `symbol` | `string` | no |  |
| `price` | `number(double)` | no |  |
| `volume` | `integer(int64)` | no |  |
| `profit` | `number(double)` | no |  |
| `storage` | `number(double)` | no |  |
| `commission` | `number(double)` | no |  |
| `obsoleteValue` | `number(double)` | no |  |
| `rateProfit` | `number(double)` | no |  |
| `rateMargin` | `number(double)` | no |  |
| `expertID` | `integer(int64)` | no |  |
| `positionID` | `integer(int64)` | no |  |
| `comment` | `string` | no |  |
| `apiDataClearAll` | `MTRetCode` | no |  |
| `profitRaw` | `number(double)` | no |  |
| `pricePosition` | `number(double)` | no |  |
| `volumeClosed` | `integer(int64)` | no |  |
| `tickValue` | `number(double)` | no |  |
| `tickSize` | `number(double)` | no |  |
| `flags` | `integer(int64)` | no |  |
| `timeMsc` | `integer(int64)` | no |  |
| `reason` | `OrderReason` | no |  |
| `gateway` | `string` | no |  |
| `priceGateway` | `number(double)` | no |  |
| `modificationFlags` | `integer(int32)` | no |  |
| `lots` | `number(double)` | no |  |

See schema: `Deal`

**Content-Type:** `application/*+json`


| Field | Type | Required | Description |
|---|---|---|---|
| `priceSL` | `number(double)` | no |  |
| `priceTP` | `number(double)` | no |  |
| `volumeExt` | `integer(int64)` | no |  |
| `volumeClosedExt` | `integer(int64)` | no |  |
| `fee` | `number(double)` | no |  |
| `value` | `number(double)` | no |  |
| `marketBid` | `number(double)` | no |  |
| `marketAsk` | `number(double)` | no |  |
| `marketLast` | `number(double)` | no |  |
| `print` | `string` | no |  |
| `dealTicket` | `integer(int64)` | no |  |
| `externalID` | `string` | no |  |
| `login` | `integer(int64)` | no |  |
| `dealer` | `integer(int64)` | no |  |
| `order` | `integer(int64)` | no |  |
| `action` | `DealAction` | no |  |
| `entry` | `EntryFlag` | no |  |
| `digits` | `integer(int32)` | no |  |
| `digitsCurrency` | `integer(int32)` | no |  |
| `contractSize` | `number(double)` | no |  |
| `time` | `integer(int64)` | no |  |
| `symbol` | `string` | no |  |
| `price` | `number(double)` | no |  |
| `volume` | `integer(int64)` | no |  |
| `profit` | `number(double)` | no |  |
| `storage` | `number(double)` | no |  |
| `commission` | `number(double)` | no |  |
| `obsoleteValue` | `number(double)` | no |  |
| `rateProfit` | `number(double)` | no |  |
| `rateMargin` | `number(double)` | no |  |
| `expertID` | `integer(int64)` | no |  |
| `positionID` | `integer(int64)` | no |  |
| `comment` | `string` | no |  |
| `apiDataClearAll` | `MTRetCode` | no |  |
| `profitRaw` | `number(double)` | no |  |
| `pricePosition` | `number(double)` | no |  |
| `volumeClosed` | `integer(int64)` | no |  |
| `tickValue` | `number(double)` | no |  |
| `tickSize` | `number(double)` | no |  |
| `flags` | `integer(int64)` | no |  |
| `timeMsc` | `integer(int64)` | no |  |
| `reason` | `OrderReason` | no |  |
| `gateway` | `string` | no |  |
| `priceGateway` | `number(double)` | no |  |
| `modificationFlags` | `integer(int32)` | no |  |
| `lots` | `number(double)` | no |  |

See schema: `Deal`

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | string |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `POST /DealAddBatch`

**Summary:** Adds multiple deals in batch.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |

**Request Body**

**Content-Type:** `application/json-patch+json`


**Type:** `array`

**Content-Type:** `application/json`


**Type:** `array`

**Content-Type:** `text/json`


**Type:** `array`

**Content-Type:** `application/*+json`


**Type:** `array`

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns array of MTRetCode results | array |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `POST /DealDeleteBatch`

**Summary:** Deletes multiple deals by ticket in batch.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |

**Request Body**

**Content-Type:** `application/json-patch+json`


**Type:** `array`

**Content-Type:** `application/json`


**Type:** `array`

**Content-Type:** `text/json`


**Type:** `array`

**Content-Type:** `application/*+json`


**Type:** `array`

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns array of MTRetCode results | array |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /DealHistory`

**Summary:** Order history

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `login` | query | `integer(int64)` | no |  |
| `from` | query | `string` | yes |  |
| `to` | query | `string` | yes |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Deal array | array |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `POST /DealPerform`

**Summary:** Performs a deal.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |

**Request Body**

**Content-Type:** `application/json-patch+json`


| Field | Type | Required | Description |
|---|---|---|---|
| `priceSL` | `number(double)` | no |  |
| `priceTP` | `number(double)` | no |  |
| `volumeExt` | `integer(int64)` | no |  |
| `volumeClosedExt` | `integer(int64)` | no |  |
| `fee` | `number(double)` | no |  |
| `value` | `number(double)` | no |  |
| `marketBid` | `number(double)` | no |  |
| `marketAsk` | `number(double)` | no |  |
| `marketLast` | `number(double)` | no |  |
| `print` | `string` | no |  |
| `dealTicket` | `integer(int64)` | no |  |
| `externalID` | `string` | no |  |
| `login` | `integer(int64)` | no |  |
| `dealer` | `integer(int64)` | no |  |
| `order` | `integer(int64)` | no |  |
| `action` | `DealAction` | no |  |
| `entry` | `EntryFlag` | no |  |
| `digits` | `integer(int32)` | no |  |
| `digitsCurrency` | `integer(int32)` | no |  |
| `contractSize` | `number(double)` | no |  |
| `time` | `integer(int64)` | no |  |
| `symbol` | `string` | no |  |
| `price` | `number(double)` | no |  |
| `volume` | `integer(int64)` | no |  |
| `profit` | `number(double)` | no |  |
| `storage` | `number(double)` | no |  |
| `commission` | `number(double)` | no |  |
| `obsoleteValue` | `number(double)` | no |  |
| `rateProfit` | `number(double)` | no |  |
| `rateMargin` | `number(double)` | no |  |
| `expertID` | `integer(int64)` | no |  |
| `positionID` | `integer(int64)` | no |  |
| `comment` | `string` | no |  |
| `apiDataClearAll` | `MTRetCode` | no |  |
| `profitRaw` | `number(double)` | no |  |
| `pricePosition` | `number(double)` | no |  |
| `volumeClosed` | `integer(int64)` | no |  |
| `tickValue` | `number(double)` | no |  |
| `tickSize` | `number(double)` | no |  |
| `flags` | `integer(int64)` | no |  |
| `timeMsc` | `integer(int64)` | no |  |
| `reason` | `OrderReason` | no |  |
| `gateway` | `string` | no |  |
| `priceGateway` | `number(double)` | no |  |
| `modificationFlags` | `integer(int32)` | no |  |
| `lots` | `number(double)` | no |  |

See schema: `Deal`

**Content-Type:** `application/json`


| Field | Type | Required | Description |
|---|---|---|---|
| `priceSL` | `number(double)` | no |  |
| `priceTP` | `number(double)` | no |  |
| `volumeExt` | `integer(int64)` | no |  |
| `volumeClosedExt` | `integer(int64)` | no |  |
| `fee` | `number(double)` | no |  |
| `value` | `number(double)` | no |  |
| `marketBid` | `number(double)` | no |  |
| `marketAsk` | `number(double)` | no |  |
| `marketLast` | `number(double)` | no |  |
| `print` | `string` | no |  |
| `dealTicket` | `integer(int64)` | no |  |
| `externalID` | `string` | no |  |
| `login` | `integer(int64)` | no |  |
| `dealer` | `integer(int64)` | no |  |
| `order` | `integer(int64)` | no |  |
| `action` | `DealAction` | no |  |
| `entry` | `EntryFlag` | no |  |
| `digits` | `integer(int32)` | no |  |
| `digitsCurrency` | `integer(int32)` | no |  |
| `contractSize` | `number(double)` | no |  |
| `time` | `integer(int64)` | no |  |
| `symbol` | `string` | no |  |
| `price` | `number(double)` | no |  |
| `volume` | `integer(int64)` | no |  |
| `profit` | `number(double)` | no |  |
| `storage` | `number(double)` | no |  |
| `commission` | `number(double)` | no |  |
| `obsoleteValue` | `number(double)` | no |  |
| `rateProfit` | `number(double)` | no |  |
| `rateMargin` | `number(double)` | no |  |
| `expertID` | `integer(int64)` | no |  |
| `positionID` | `integer(int64)` | no |  |
| `comment` | `string` | no |  |
| `apiDataClearAll` | `MTRetCode` | no |  |
| `profitRaw` | `number(double)` | no |  |
| `pricePosition` | `number(double)` | no |  |
| `volumeClosed` | `integer(int64)` | no |  |
| `tickValue` | `number(double)` | no |  |
| `tickSize` | `number(double)` | no |  |
| `flags` | `integer(int64)` | no |  |
| `timeMsc` | `integer(int64)` | no |  |
| `reason` | `OrderReason` | no |  |
| `gateway` | `string` | no |  |
| `priceGateway` | `number(double)` | no |  |
| `modificationFlags` | `integer(int32)` | no |  |
| `lots` | `number(double)` | no |  |

See schema: `Deal`

**Content-Type:** `text/json`


| Field | Type | Required | Description |
|---|---|---|---|
| `priceSL` | `number(double)` | no |  |
| `priceTP` | `number(double)` | no |  |
| `volumeExt` | `integer(int64)` | no |  |
| `volumeClosedExt` | `integer(int64)` | no |  |
| `fee` | `number(double)` | no |  |
| `value` | `number(double)` | no |  |
| `marketBid` | `number(double)` | no |  |
| `marketAsk` | `number(double)` | no |  |
| `marketLast` | `number(double)` | no |  |
| `print` | `string` | no |  |
| `dealTicket` | `integer(int64)` | no |  |
| `externalID` | `string` | no |  |
| `login` | `integer(int64)` | no |  |
| `dealer` | `integer(int64)` | no |  |
| `order` | `integer(int64)` | no |  |
| `action` | `DealAction` | no |  |
| `entry` | `EntryFlag` | no |  |
| `digits` | `integer(int32)` | no |  |
| `digitsCurrency` | `integer(int32)` | no |  |
| `contractSize` | `number(double)` | no |  |
| `time` | `integer(int64)` | no |  |
| `symbol` | `string` | no |  |
| `price` | `number(double)` | no |  |
| `volume` | `integer(int64)` | no |  |
| `profit` | `number(double)` | no |  |
| `storage` | `number(double)` | no |  |
| `commission` | `number(double)` | no |  |
| `obsoleteValue` | `number(double)` | no |  |
| `rateProfit` | `number(double)` | no |  |
| `rateMargin` | `number(double)` | no |  |
| `expertID` | `integer(int64)` | no |  |
| `positionID` | `integer(int64)` | no |  |
| `comment` | `string` | no |  |
| `apiDataClearAll` | `MTRetCode` | no |  |
| `profitRaw` | `number(double)` | no |  |
| `pricePosition` | `number(double)` | no |  |
| `volumeClosed` | `integer(int64)` | no |  |
| `tickValue` | `number(double)` | no |  |
| `tickSize` | `number(double)` | no |  |
| `flags` | `integer(int64)` | no |  |
| `timeMsc` | `integer(int64)` | no |  |
| `reason` | `OrderReason` | no |  |
| `gateway` | `string` | no |  |
| `priceGateway` | `number(double)` | no |  |
| `modificationFlags` | `integer(int32)` | no |  |
| `lots` | `number(double)` | no |  |

See schema: `Deal`

**Content-Type:** `application/*+json`


| Field | Type | Required | Description |
|---|---|---|---|
| `priceSL` | `number(double)` | no |  |
| `priceTP` | `number(double)` | no |  |
| `volumeExt` | `integer(int64)` | no |  |
| `volumeClosedExt` | `integer(int64)` | no |  |
| `fee` | `number(double)` | no |  |
| `value` | `number(double)` | no |  |
| `marketBid` | `number(double)` | no |  |
| `marketAsk` | `number(double)` | no |  |
| `marketLast` | `number(double)` | no |  |
| `print` | `string` | no |  |
| `dealTicket` | `integer(int64)` | no |  |
| `externalID` | `string` | no |  |
| `login` | `integer(int64)` | no |  |
| `dealer` | `integer(int64)` | no |  |
| `order` | `integer(int64)` | no |  |
| `action` | `DealAction` | no |  |
| `entry` | `EntryFlag` | no |  |
| `digits` | `integer(int32)` | no |  |
| `digitsCurrency` | `integer(int32)` | no |  |
| `contractSize` | `number(double)` | no |  |
| `time` | `integer(int64)` | no |  |
| `symbol` | `string` | no |  |
| `price` | `number(double)` | no |  |
| `volume` | `integer(int64)` | no |  |
| `profit` | `number(double)` | no |  |
| `storage` | `number(double)` | no |  |
| `commission` | `number(double)` | no |  |
| `obsoleteValue` | `number(double)` | no |  |
| `rateProfit` | `number(double)` | no |  |
| `rateMargin` | `number(double)` | no |  |
| `expertID` | `integer(int64)` | no |  |
| `positionID` | `integer(int64)` | no |  |
| `comment` | `string` | no |  |
| `apiDataClearAll` | `MTRetCode` | no |  |
| `profitRaw` | `number(double)` | no |  |
| `pricePosition` | `number(double)` | no |  |
| `volumeClosed` | `integer(int64)` | no |  |
| `tickValue` | `number(double)` | no |  |
| `tickSize` | `number(double)` | no |  |
| `flags` | `integer(int64)` | no |  |
| `timeMsc` | `integer(int64)` | no |  |
| `reason` | `OrderReason` | no |  |
| `gateway` | `string` | no |  |
| `priceGateway` | `number(double)` | no |  |
| `modificationFlags` | `integer(int32)` | no |  |
| `lots` | `number(double)` | no |  |

See schema: `Deal`

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | string |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `POST /DealPerformBatch`

**Summary:** Performs multiple deals in batch.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |

**Request Body**

**Content-Type:** `application/json-patch+json`


**Type:** `array`

**Content-Type:** `application/json`


**Type:** `array`

**Content-Type:** `text/json`


**Type:** `array`

**Content-Type:** `application/*+json`


**Type:** `array`

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns array of MTRetCode results | array |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `POST /DealRequestByLogins`

**Summary:** Gets the deal history for multiple trading accounts (logins) within the specified time period.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Session token returned by the `Connect` method. Required. |
| `from` | query | `string` | yes | Start of the time range in ISO format (`yyyy-MM-ddTHH:mm:ss`). Example: `2023-07-04T00:00:00`. |
| `to` | query | `string` | yes | End of the time range in ISO format (`yyyy-MM-ddTHH:mm:ss`). Example: `2023-07-05T00:00:00`. |

**Request Body**

**Content-Type:** `application/json-patch+json`


**Type:** `array`

**Content-Type:** `application/json`


**Type:** `array`

**Content-Type:** `text/json`


**Type:** `array`

**Content-Type:** `application/*+json`


**Type:** `array`

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Deal array | array |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `POST /DealUpdate`

**Summary:** Updates a single deal.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |

**Request Body**

**Content-Type:** `application/json-patch+json`


| Field | Type | Required | Description |
|---|---|---|---|
| `priceSL` | `number(double)` | no |  |
| `priceTP` | `number(double)` | no |  |
| `volumeExt` | `integer(int64)` | no |  |
| `volumeClosedExt` | `integer(int64)` | no |  |
| `fee` | `number(double)` | no |  |
| `value` | `number(double)` | no |  |
| `marketBid` | `number(double)` | no |  |
| `marketAsk` | `number(double)` | no |  |
| `marketLast` | `number(double)` | no |  |
| `print` | `string` | no |  |
| `dealTicket` | `integer(int64)` | no |  |
| `externalID` | `string` | no |  |
| `login` | `integer(int64)` | no |  |
| `dealer` | `integer(int64)` | no |  |
| `order` | `integer(int64)` | no |  |
| `action` | `DealAction` | no |  |
| `entry` | `EntryFlag` | no |  |
| `digits` | `integer(int32)` | no |  |
| `digitsCurrency` | `integer(int32)` | no |  |
| `contractSize` | `number(double)` | no |  |
| `time` | `integer(int64)` | no |  |
| `symbol` | `string` | no |  |
| `price` | `number(double)` | no |  |
| `volume` | `integer(int64)` | no |  |
| `profit` | `number(double)` | no |  |
| `storage` | `number(double)` | no |  |
| `commission` | `number(double)` | no |  |
| `obsoleteValue` | `number(double)` | no |  |
| `rateProfit` | `number(double)` | no |  |
| `rateMargin` | `number(double)` | no |  |
| `expertID` | `integer(int64)` | no |  |
| `positionID` | `integer(int64)` | no |  |
| `comment` | `string` | no |  |
| `apiDataClearAll` | `MTRetCode` | no |  |
| `profitRaw` | `number(double)` | no |  |
| `pricePosition` | `number(double)` | no |  |
| `volumeClosed` | `integer(int64)` | no |  |
| `tickValue` | `number(double)` | no |  |
| `tickSize` | `number(double)` | no |  |
| `flags` | `integer(int64)` | no |  |
| `timeMsc` | `integer(int64)` | no |  |
| `reason` | `OrderReason` | no |  |
| `gateway` | `string` | no |  |
| `priceGateway` | `number(double)` | no |  |
| `modificationFlags` | `integer(int32)` | no |  |
| `lots` | `number(double)` | no |  |

See schema: `Deal`

**Content-Type:** `application/json`


| Field | Type | Required | Description |
|---|---|---|---|
| `priceSL` | `number(double)` | no |  |
| `priceTP` | `number(double)` | no |  |
| `volumeExt` | `integer(int64)` | no |  |
| `volumeClosedExt` | `integer(int64)` | no |  |
| `fee` | `number(double)` | no |  |
| `value` | `number(double)` | no |  |
| `marketBid` | `number(double)` | no |  |
| `marketAsk` | `number(double)` | no |  |
| `marketLast` | `number(double)` | no |  |
| `print` | `string` | no |  |
| `dealTicket` | `integer(int64)` | no |  |
| `externalID` | `string` | no |  |
| `login` | `integer(int64)` | no |  |
| `dealer` | `integer(int64)` | no |  |
| `order` | `integer(int64)` | no |  |
| `action` | `DealAction` | no |  |
| `entry` | `EntryFlag` | no |  |
| `digits` | `integer(int32)` | no |  |
| `digitsCurrency` | `integer(int32)` | no |  |
| `contractSize` | `number(double)` | no |  |
| `time` | `integer(int64)` | no |  |
| `symbol` | `string` | no |  |
| `price` | `number(double)` | no |  |
| `volume` | `integer(int64)` | no |  |
| `profit` | `number(double)` | no |  |
| `storage` | `number(double)` | no |  |
| `commission` | `number(double)` | no |  |
| `obsoleteValue` | `number(double)` | no |  |
| `rateProfit` | `number(double)` | no |  |
| `rateMargin` | `number(double)` | no |  |
| `expertID` | `integer(int64)` | no |  |
| `positionID` | `integer(int64)` | no |  |
| `comment` | `string` | no |  |
| `apiDataClearAll` | `MTRetCode` | no |  |
| `profitRaw` | `number(double)` | no |  |
| `pricePosition` | `number(double)` | no |  |
| `volumeClosed` | `integer(int64)` | no |  |
| `tickValue` | `number(double)` | no |  |
| `tickSize` | `number(double)` | no |  |
| `flags` | `integer(int64)` | no |  |
| `timeMsc` | `integer(int64)` | no |  |
| `reason` | `OrderReason` | no |  |
| `gateway` | `string` | no |  |
| `priceGateway` | `number(double)` | no |  |
| `modificationFlags` | `integer(int32)` | no |  |
| `lots` | `number(double)` | no |  |

See schema: `Deal`

**Content-Type:** `text/json`


| Field | Type | Required | Description |
|---|---|---|---|
| `priceSL` | `number(double)` | no |  |
| `priceTP` | `number(double)` | no |  |
| `volumeExt` | `integer(int64)` | no |  |
| `volumeClosedExt` | `integer(int64)` | no |  |
| `fee` | `number(double)` | no |  |
| `value` | `number(double)` | no |  |
| `marketBid` | `number(double)` | no |  |
| `marketAsk` | `number(double)` | no |  |
| `marketLast` | `number(double)` | no |  |
| `print` | `string` | no |  |
| `dealTicket` | `integer(int64)` | no |  |
| `externalID` | `string` | no |  |
| `login` | `integer(int64)` | no |  |
| `dealer` | `integer(int64)` | no |  |
| `order` | `integer(int64)` | no |  |
| `action` | `DealAction` | no |  |
| `entry` | `EntryFlag` | no |  |
| `digits` | `integer(int32)` | no |  |
| `digitsCurrency` | `integer(int32)` | no |  |
| `contractSize` | `number(double)` | no |  |
| `time` | `integer(int64)` | no |  |
| `symbol` | `string` | no |  |
| `price` | `number(double)` | no |  |
| `volume` | `integer(int64)` | no |  |
| `profit` | `number(double)` | no |  |
| `storage` | `number(double)` | no |  |
| `commission` | `number(double)` | no |  |
| `obsoleteValue` | `number(double)` | no |  |
| `rateProfit` | `number(double)` | no |  |
| `rateMargin` | `number(double)` | no |  |
| `expertID` | `integer(int64)` | no |  |
| `positionID` | `integer(int64)` | no |  |
| `comment` | `string` | no |  |
| `apiDataClearAll` | `MTRetCode` | no |  |
| `profitRaw` | `number(double)` | no |  |
| `pricePosition` | `number(double)` | no |  |
| `volumeClosed` | `integer(int64)` | no |  |
| `tickValue` | `number(double)` | no |  |
| `tickSize` | `number(double)` | no |  |
| `flags` | `integer(int64)` | no |  |
| `timeMsc` | `integer(int64)` | no |  |
| `reason` | `OrderReason` | no |  |
| `gateway` | `string` | no |  |
| `priceGateway` | `number(double)` | no |  |
| `modificationFlags` | `integer(int32)` | no |  |
| `lots` | `number(double)` | no |  |

See schema: `Deal`

**Content-Type:** `application/*+json`


| Field | Type | Required | Description |
|---|---|---|---|
| `priceSL` | `number(double)` | no |  |
| `priceTP` | `number(double)` | no |  |
| `volumeExt` | `integer(int64)` | no |  |
| `volumeClosedExt` | `integer(int64)` | no |  |
| `fee` | `number(double)` | no |  |
| `value` | `number(double)` | no |  |
| `marketBid` | `number(double)` | no |  |
| `marketAsk` | `number(double)` | no |  |
| `marketLast` | `number(double)` | no |  |
| `print` | `string` | no |  |
| `dealTicket` | `integer(int64)` | no |  |
| `externalID` | `string` | no |  |
| `login` | `integer(int64)` | no |  |
| `dealer` | `integer(int64)` | no |  |
| `order` | `integer(int64)` | no |  |
| `action` | `DealAction` | no |  |
| `entry` | `EntryFlag` | no |  |
| `digits` | `integer(int32)` | no |  |
| `digitsCurrency` | `integer(int32)` | no |  |
| `contractSize` | `number(double)` | no |  |
| `time` | `integer(int64)` | no |  |
| `symbol` | `string` | no |  |
| `price` | `number(double)` | no |  |
| `volume` | `integer(int64)` | no |  |
| `profit` | `number(double)` | no |  |
| `storage` | `number(double)` | no |  |
| `commission` | `number(double)` | no |  |
| `obsoleteValue` | `number(double)` | no |  |
| `rateProfit` | `number(double)` | no |  |
| `rateMargin` | `number(double)` | no |  |
| `expertID` | `integer(int64)` | no |  |
| `positionID` | `integer(int64)` | no |  |
| `comment` | `string` | no |  |
| `apiDataClearAll` | `MTRetCode` | no |  |
| `profitRaw` | `number(double)` | no |  |
| `pricePosition` | `number(double)` | no |  |
| `volumeClosed` | `integer(int64)` | no |  |
| `tickValue` | `number(double)` | no |  |
| `tickSize` | `number(double)` | no |  |
| `flags` | `integer(int64)` | no |  |
| `timeMsc` | `integer(int64)` | no |  |
| `reason` | `OrderReason` | no |  |
| `gateway` | `string` | no |  |
| `priceGateway` | `number(double)` | no |  |
| `modificationFlags` | `integer(int32)` | no |  |
| `lots` | `number(double)` | no |  |

See schema: `Deal`

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | string |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `POST /DealUpdateBatch`

**Summary:** Updates multiple deals in batch.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |

**Request Body**

**Content-Type:** `application/json-patch+json`


**Type:** `array`

**Content-Type:** `application/json`


**Type:** `array`

**Content-Type:** `text/json`


**Type:** `array`

**Content-Type:** `application/*+json`


**Type:** `array`

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns array of MTRetCode results | array |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /Deposit`

**Summary:** Deposit/withdraw

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `login` | query | `integer(int64)` | yes | User account |
| `amount` | query | `number(double)` | yes | Amount. If negative - withdraw. |
| `comment` | query | `string` | yes | Comment |
| `credit` | query | `boolean` | no | Set true if credit |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Order object | integer |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /EmailSend`

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes |  |
| `account` | query | `string` | no |  |
| `to` | query | `string` | no |  |
| `to_name` | query | `string` | no |  |
| `subject` | query | `string` | no |  |
| `body` | query | `string` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | string |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /Health`

**Summary:** Check Connection.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Not connected / Connected | string |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /Holidays`

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns ConHoliday array | array |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /IsQuoteSession`

**Summary:** Check market open or not for specified symbol.

Returns an array of avaliable symbols

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `symbols` | query | `array<string>` | yes |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns SessionState array | array |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /IsTradeSession`

**Summary:** Check market open or not for specified symbol.

Returns an array of avaliable symbols

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `symbols` | query | `array<string>` | no | Symbols. If not specified - all symbols. |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns SessionState array | array |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /MessengerSend`

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes |  |
| `destination` | query | `string` | no |  |
| `group` | query | `string` | no |  |
| `sender` | query | `string` | no |  |
| `text` | query | `string` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | string |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /ModifyDeal`

**Summary:** Modify deal

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `ticket` | query | `integer(int64)` | yes | Ticket |
| `stoploss` | query | `number(double)` | no | Stop loss |
| `takeprofit` | query | `number(double)` | no | Take profit |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns Request object | TradeResult |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `200` schema — `TradeResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `answer` | `Request` | no |  |
| `result` | `Confirm` | no |  |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /ModifyOrder`

**Summary:** Modify order

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `ticket` | query | `integer(int64)` | yes | Ticket |
| `price` | query | `number(double)` | no | Order price |
| `stoploss` | query | `number(double)` | no | Stop loss |
| `takeprofit` | query | `number(double)` | no | Take profit |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns MTRequest object | TradeResult |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `200` schema — `TradeResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `answer` | `Request` | no |  |
| `result` | `Confirm` | no |  |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /News`

**Summary:** Get all news items.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns News array | array |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /OpenedOrders`

**Summary:** Position hsitory the same as in client API

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `logins` | query | `array<integer>` | no | List of logins. Null - all open orders. |
| `sort` | query | `OrderSort` | no | Sort by open time or close time |
| `ascending` | query | `boolean` | no | Ascending sort |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | ClientOrder array array | array |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /OpenedOrdersPagination`

**Summary:** Paginated variant of 'OpenedOrders' with an optional open-time date filter.
Login search works the same way as in 'OpenedOrders': null logins - all open orders.
Data is fetched live on every call (open orders change constantly), only sliced for the requested page.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `logins` | query | `array<integer>` | no | List of logins. Null - all open orders. |
| `from` | query | `string` | no | Open time filter, from (server time) |
| `to` | query | `string` | no | Open time filter, to (server time) |
| `sort` | query | `OrderSort` | no | Sort by open time or close time |
| `ascending` | query | `boolean` | no | Ascending sort |
| `page` | query | `integer(int32)` | no | Zero-based page index |
| `pageSize` | query | `integer(int32)` | no | Page size, default 100 |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Paginated ClientOrder result | ClientOrderPaginatedResult |
| `201` | ExceptionResult object | ExceptionResult |

**Response `200` schema — `ClientOrderPaginatedResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `page` | `integer(int32)` | no |  |
| `pageSize` | `integer(int32)` | no |  |
| `totalCount` | `integer(int32)` | no |  |
| `totalPages` | `integer(int32)` | no |  |
| `items` | `array<ClientOrder>` | no |  |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /OrderHistory`

**Summary:** Position hsitory the same as in client API

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `login` | query | `integer(int64)` | no | Login |
| `from` | query | `string` | no | From time |
| `to` | query | `string` | no | To time |
| `sort` | query | `OrderSort` | no | Sort by open time or close time |
| `ascending` | query | `boolean` | no | Ascending sort |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | ClientOrder array | array |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /OrderHistoryPagination`

**Summary:** Paginated variant of 'OrderHistory' (per-login position history) with the same date filter.
The full result set is cached (sliding TTL), so subsequent pages of the same query do not re-query the server.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `login` | query | `integer(int64)` | no | Login |
| `from` | query | `string` | no | From time |
| `to` | query | `string` | no | To time |
| `sort` | query | `OrderSort` | no | Sort by open time or close time |
| `ascending` | query | `boolean` | no | Ascending sort |
| `page` | query | `integer(int32)` | no | Zero-based page index |
| `pageSize` | query | `integer(int32)` | no | Page size, default 100 |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Paginated ClientOrder result | ClientOrderPaginatedResult |
| `201` | ExceptionResult object | ExceptionResult |

**Response `200` schema — `ClientOrderPaginatedResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `page` | `integer(int32)` | no |  |
| `pageSize` | `integer(int32)` | no |  |
| `totalCount` | `integer(int32)` | no |  |
| `totalPages` | `integer(int32)` | no |  |
| `items` | `array<ClientOrder>` | no |  |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /Orders`

**Summary:** Opened positions.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `logins` | query | `array<integer>` | no | Logins |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns Order[] object | array |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `POST /OrderUpdate`

**Summary:** Updates a single deal.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |

**Request Body**

**Content-Type:** `application/json-patch+json`


| Field | Type | Required | Description |
|---|---|---|---|
| `positionByID` | `integer(int64)` | no |  |
| `modificationFlags` | `integer(int32)` | no |  |
| `volumeInitialExt` | `integer(int64)` | no |  |
| `volumeCurrentExt` | `integer(int64)` | no |  |
| `print` | `string` | no |  |
| `orderTicket` | `integer(int64)` | no |  |
| `externalID` | `string` | no |  |
| `login` | `integer(int64)` | no |  |
| `dealer` | `integer(int64)` | no |  |
| `symbol` | `string` | no |  |
| `digits` | `integer(int32)` | no |  |
| `digitsCurrency` | `integer(int32)` | no |  |
| `contractSize` | `number(double)` | no |  |
| `state` | `OrderState` | no |  |
| `reason` | `OrderReason` | no |  |
| `timeSetup` | `integer(int64)` | no |  |
| `timeExpiration` | `integer(int64)` | no |  |
| `timeDone` | `integer(int64)` | no |  |
| `type` | `OrderType` | no |  |
| `typeFill` | `OrderFilling` | no |  |
| `typeTime` | `OrderTime` | no |  |
| `priceOrder` | `number(double)` | no |  |
| `priceTrigger` | `number(double)` | no |  |
| `priceCurrent` | `number(double)` | no |  |
| `priceSL` | `number(double)` | no |  |
| `priceTP` | `number(double)` | no |  |
| `volumeInitial` | `integer(int64)` | no |  |
| `volumeCurrent` | `integer(int64)` | no |  |
| `expertID` | `integer(int64)` | no |  |
| `positionID` | `integer(int64)` | no |  |
| `comment` | `string` | no |  |
| `activationMode` | `OrderActivation` | no |  |
| `activationTime` | `integer(int64)` | no |  |
| `activationPrice` | `number(double)` | no |  |
| `activationFlags` | `TradeActivationFlags` | no |  |
| `apiDataClearAll` | `MTRetCode` | no |  |
| `timeSetupMsc` | `integer(int64)` | no |  |
| `timeDoneMsc` | `integer(int64)` | no |  |
| `rateMargin` | `number(double)` | no |  |
| `lots` | `number(double)` | no |  |

See schema: `Order`

**Content-Type:** `application/json`


| Field | Type | Required | Description |
|---|---|---|---|
| `positionByID` | `integer(int64)` | no |  |
| `modificationFlags` | `integer(int32)` | no |  |
| `volumeInitialExt` | `integer(int64)` | no |  |
| `volumeCurrentExt` | `integer(int64)` | no |  |
| `print` | `string` | no |  |
| `orderTicket` | `integer(int64)` | no |  |
| `externalID` | `string` | no |  |
| `login` | `integer(int64)` | no |  |
| `dealer` | `integer(int64)` | no |  |
| `symbol` | `string` | no |  |
| `digits` | `integer(int32)` | no |  |
| `digitsCurrency` | `integer(int32)` | no |  |
| `contractSize` | `number(double)` | no |  |
| `state` | `OrderState` | no |  |
| `reason` | `OrderReason` | no |  |
| `timeSetup` | `integer(int64)` | no |  |
| `timeExpiration` | `integer(int64)` | no |  |
| `timeDone` | `integer(int64)` | no |  |
| `type` | `OrderType` | no |  |
| `typeFill` | `OrderFilling` | no |  |
| `typeTime` | `OrderTime` | no |  |
| `priceOrder` | `number(double)` | no |  |
| `priceTrigger` | `number(double)` | no |  |
| `priceCurrent` | `number(double)` | no |  |
| `priceSL` | `number(double)` | no |  |
| `priceTP` | `number(double)` | no |  |
| `volumeInitial` | `integer(int64)` | no |  |
| `volumeCurrent` | `integer(int64)` | no |  |
| `expertID` | `integer(int64)` | no |  |
| `positionID` | `integer(int64)` | no |  |
| `comment` | `string` | no |  |
| `activationMode` | `OrderActivation` | no |  |
| `activationTime` | `integer(int64)` | no |  |
| `activationPrice` | `number(double)` | no |  |
| `activationFlags` | `TradeActivationFlags` | no |  |
| `apiDataClearAll` | `MTRetCode` | no |  |
| `timeSetupMsc` | `integer(int64)` | no |  |
| `timeDoneMsc` | `integer(int64)` | no |  |
| `rateMargin` | `number(double)` | no |  |
| `lots` | `number(double)` | no |  |

See schema: `Order`

**Content-Type:** `text/json`


| Field | Type | Required | Description |
|---|---|---|---|
| `positionByID` | `integer(int64)` | no |  |
| `modificationFlags` | `integer(int32)` | no |  |
| `volumeInitialExt` | `integer(int64)` | no |  |
| `volumeCurrentExt` | `integer(int64)` | no |  |
| `print` | `string` | no |  |
| `orderTicket` | `integer(int64)` | no |  |
| `externalID` | `string` | no |  |
| `login` | `integer(int64)` | no |  |
| `dealer` | `integer(int64)` | no |  |
| `symbol` | `string` | no |  |
| `digits` | `integer(int32)` | no |  |
| `digitsCurrency` | `integer(int32)` | no |  |
| `contractSize` | `number(double)` | no |  |
| `state` | `OrderState` | no |  |
| `reason` | `OrderReason` | no |  |
| `timeSetup` | `integer(int64)` | no |  |
| `timeExpiration` | `integer(int64)` | no |  |
| `timeDone` | `integer(int64)` | no |  |
| `type` | `OrderType` | no |  |
| `typeFill` | `OrderFilling` | no |  |
| `typeTime` | `OrderTime` | no |  |
| `priceOrder` | `number(double)` | no |  |
| `priceTrigger` | `number(double)` | no |  |
| `priceCurrent` | `number(double)` | no |  |
| `priceSL` | `number(double)` | no |  |
| `priceTP` | `number(double)` | no |  |
| `volumeInitial` | `integer(int64)` | no |  |
| `volumeCurrent` | `integer(int64)` | no |  |
| `expertID` | `integer(int64)` | no |  |
| `positionID` | `integer(int64)` | no |  |
| `comment` | `string` | no |  |
| `activationMode` | `OrderActivation` | no |  |
| `activationTime` | `integer(int64)` | no |  |
| `activationPrice` | `number(double)` | no |  |
| `activationFlags` | `TradeActivationFlags` | no |  |
| `apiDataClearAll` | `MTRetCode` | no |  |
| `timeSetupMsc` | `integer(int64)` | no |  |
| `timeDoneMsc` | `integer(int64)` | no |  |
| `rateMargin` | `number(double)` | no |  |
| `lots` | `number(double)` | no |  |

See schema: `Order`

**Content-Type:** `application/*+json`


| Field | Type | Required | Description |
|---|---|---|---|
| `positionByID` | `integer(int64)` | no |  |
| `modificationFlags` | `integer(int32)` | no |  |
| `volumeInitialExt` | `integer(int64)` | no |  |
| `volumeCurrentExt` | `integer(int64)` | no |  |
| `print` | `string` | no |  |
| `orderTicket` | `integer(int64)` | no |  |
| `externalID` | `string` | no |  |
| `login` | `integer(int64)` | no |  |
| `dealer` | `integer(int64)` | no |  |
| `symbol` | `string` | no |  |
| `digits` | `integer(int32)` | no |  |
| `digitsCurrency` | `integer(int32)` | no |  |
| `contractSize` | `number(double)` | no |  |
| `state` | `OrderState` | no |  |
| `reason` | `OrderReason` | no |  |
| `timeSetup` | `integer(int64)` | no |  |
| `timeExpiration` | `integer(int64)` | no |  |
| `timeDone` | `integer(int64)` | no |  |
| `type` | `OrderType` | no |  |
| `typeFill` | `OrderFilling` | no |  |
| `typeTime` | `OrderTime` | no |  |
| `priceOrder` | `number(double)` | no |  |
| `priceTrigger` | `number(double)` | no |  |
| `priceCurrent` | `number(double)` | no |  |
| `priceSL` | `number(double)` | no |  |
| `priceTP` | `number(double)` | no |  |
| `volumeInitial` | `integer(int64)` | no |  |
| `volumeCurrent` | `integer(int64)` | no |  |
| `expertID` | `integer(int64)` | no |  |
| `positionID` | `integer(int64)` | no |  |
| `comment` | `string` | no |  |
| `activationMode` | `OrderActivation` | no |  |
| `activationTime` | `integer(int64)` | no |  |
| `activationPrice` | `number(double)` | no |  |
| `activationFlags` | `TradeActivationFlags` | no |  |
| `apiDataClearAll` | `MTRetCode` | no |  |
| `timeSetupMsc` | `integer(int64)` | no |  |
| `timeDoneMsc` | `integer(int64)` | no |  |
| `rateMargin` | `number(double)` | no |  |
| `lots` | `number(double)` | no |  |

See schema: `Order`

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | string |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /PendingOrderHistory`

**Summary:** Order history

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `login` | query | `integer(int64)` | no |  |
| `from` | query | `string` | yes |  |
| `to` | query | `string` | yes |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Order array | array |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /PositionHistoryMT4Format`

**Summary:** Order history

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `login` | query | `integer(int64)` | no |  |
| `from` | query | `string` | no |  |
| `to` | query | `string` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Order array | array |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /Positions`

**Summary:** Opened positions.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `logins` | query | `array<integer>` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Position array | array |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /PositionsMT4Format`

**Summary:** Poition list in MT4 format.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `logins` | query | `array<integer>` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Position array | array |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /ServerTimezone`

**Summary:** Server timezone details

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | ConTime |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `200` schema — `ConTime`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `daylight` | `boolean` | no |  |
| `timeZone` | `integer(int32)` | no |  |
| `timeServer` | `string` | no |  |
| `daylightState` | `integer(int32)` | no |  |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /SummaryGet`

**Summary:** Get summary for symbol

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `symbol` | query | `string` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns Summary object | Summary |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `200` schema — `Summary`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `symbol` | `string` | no |  |
| `digits` | `integer(int32)` | no |  |
| `positionClients` | `integer(int32)` | no |  |
| `positionCoverage` | `integer(int32)` | no |  |
| `volumeBuyClients` | `integer(int64)` | no |  |
| `volumeBuyCoverage` | `integer(int64)` | no |  |
| `volumeSellClients` | `integer(int64)` | no |  |
| `volumeSellCoverage` | `integer(int64)` | no |  |
| `volumeNet` | `number(double)` | no |  |
| `priceBuyClients` | `number(double)` | no |  |
| `priceBuyCoverage` | `number(double)` | no |  |
| `priceSellClients` | `number(double)` | no |  |
| `priceSellCoverage` | `number(double)` | no |  |
| `profitClients` | `number(double)` | no |  |
| `profitCoverage` | `number(double)` | no |  |
| `profitFullClients` | `number(double)` | no |  |
| `profitFullCoverage` | `number(double)` | no |  |
| `profitUncovered` | `number(double)` | no |  |
| `profitUncoveredFull` | `number(double)` | no |  |
| `volumeBuyClientsExt` | `integer(int64)` | no |  |
| `volumeBuyCoverageExt` | `integer(int64)` | no |  |
| `volumeSellClientsExt` | `integer(int64)` | no |  |
| `volumeSellCoverageExt` | `integer(int64)` | no |  |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /SummaryGetAll`

**Summary:** Get summary for all symbols

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns Summary[] object | array |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /SymbolGet`

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes |  |
| `name` | query | `string` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns ConSymbol object | ConSymbol |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `200` schema — `ConSymbol`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `priceStrike` | `number(double)` | no |  |
| `marginRateLiquidity` | `number(double)` | no |  |
| `faceValue` | `number(double)` | no |  |
| `accruedInterest` | `number(double)` | no |  |
| `spliceType` | `EnSpliceType` | no |  |
| `spliceTimeType` | `EnSpliceTimeType` | no |  |
| `spliceTimeDays` | `integer(int32)` | no |  |
| `marginHedged` | `number(double)` | no |  |
| `marginRateCurrency` | `number(double)` | no |  |
| `filterGap` | `integer(int32)` | no |  |
| `filterGapTicks` | `integer(int32)` | no |  |
| `chartMode` | `EnChartMode` | no |  |
| `ieFlags` | `integer(int32)` | no |  |
| `volumeMinExt` | `integer(int64)` | no |  |
| `volumeMaxExt` | `integer(int64)` | no |  |
| `volumeStepExt` | `integer(int64)` | no |  |
| `volumeLimitExt` | `integer(int64)` | no |  |
| `ieVolumeMaxExt` | `integer(int64)` | no |  |
| `category` | `string` | no |  |
| `exchange` | `string` | no |  |
| `cfi` | `string` | no |  |
| `sector` | `EnSectors` | no |  |
| `industry` | `EnIndustries` | no |  |
| `country` | `string` | no |  |
| `subscriptionsDelay` | `integer(int32)` | no |  |
| `swapYearDays` | `integer(int32)` | no |  |
| `swapFlags` | `integer(int32)` | no |  |
| `swapRateSunday` | `number(double)` | no |  |
| `swapRateMonday` | `number(double)` | no |  |
| `swapRateTuesday` | `number(double)` | no |  |
| `swapRateWednesday` | `number(double)` | no |  |
| `swapRateThursday` | `number(double)` | no |  |
| `swapRateFriday` | `number(double)` | no |  |
| `swapRateSaturday` | `number(double)` | no |  |
| `freezeLevel` | `integer(int32)` | no |  |
| `quotesTimeout` | `integer(int32)` | no |  |
| `volumeMin` | `integer(int64)` | no |  |
| `volumeMax` | `integer(int64)` | no |  |
| `volumeStep` | `integer(int64)` | no |  |
| `volumeLimit` | `integer(int64)` | no |  |
| `marginFlags` | `EnMarginFlags` | no |  |
| `marginInitial` | `number(double)` | no |  |
| `marginMaintenance` | `number(double)` | no |  |
| `marginLong` | `number(double)` | no |  |
| `marginShort` | `number(double)` | no |  |
| `marginLimit` | `number(double)` | no |  |
| `marginStop` | `number(double)` | no |  |
| `marginStopLimit` | `number(double)` | no |  |
| `swapMode` | `integer(int32)` | no |  |
| `swapLong` | `number(double)` | no |  |
| `swapShort` | `number(double)` | no |  |
| `swap3Day` | `integer(int32)` | no |  |
| `timeStart` | `integer(int64)` | no |  |
| `timeExpiration` | `integer(int64)` | no |  |
| `reFlags` | `integer(int32)` | no |  |
| `reTimeout` | `integer(int32)` | no |  |
| `ieCheckMode` | `integer(int32)` | no |  |
| `ieTimeout` | `integer(int32)` | no |  |
| `ieSlipProfit` | `integer(int32)` | no |  |
| `ieSlipLosing` | `integer(int32)` | no |  |
| `ieVolumeMax` | `integer(int64)` | no |  |
| `priceSettle` | `number(double)` | no |  |
| `priceLimitMax` | `number(double)` | no |  |
| `priceLimitMin` | `number(double)` | no |  |
| `tradeFlags` | `EnTradeFlags` | no |  |
| `orderFlags` | `EnOrderFlags` | no |  |
| `optionsMode` | `EnOptionMode` | no |  |
| `symbol` | `string` | no |  |
| `path` | `string` | no |  |
| `isin` | `string` | no |  |
| `description` | `string` | no |  |
| `international` | `string` | no |  |
| `basis` | `string` | no |  |
| `source` | `string` | no |  |
| `page` | `string` | no |  |
| `currencyBase` | `string` | no |  |
| `currencyBaseDigits` | `integer(int32)` | no |  |
| `currencyProfit` | `string` | no |  |
| `currencyProfitDigits` | `integer(int32)` | no |  |
| `currencyMargin` | `string` | no |  |
| `currencyMarginDigits` | `integer(int32)` | no |  |
| `color` | `integer(int32)` | no |  |
| `colorBackground` | `integer(int32)` | no |  |
| `digits` | `integer(int32)` | no |  |
| `point` | `number(double)` | no |  |
| `multiply` | `number(double)` | no |  |
| `tickFlags` | `EnTickFlagsSym` | no |  |
| `tickBookDepth` | `integer(int32)` | no |  |
| `filterSoft` | `integer(int32)` | no |  |
| `filterSoftTicks` | `integer(int32)` | no |  |
| `filterHard` | `integer(int32)` | no |  |
| `filterHardTicks` | `integer(int32)` | no |  |
| `filterDiscard` | `integer(int32)` | no |  |
| `filterSpreadMax` | `integer(int32)` | no |  |
| `filterSpreadMin` | `integer(int32)` | no |  |
| `tradeMode` | `EnTradeMode` | no |  |
| `calcMode` | `EnCalcMode` | no |  |
| `execMode` | `EnExecutionMode` | no |  |
| `gtcMode` | `EnGTCMode` | no |  |
| `fillFlags` | `EnFillingFlags` | no |  |
| `expirFlags` | `EnExpirationFlags` | no |  |
| `spread` | `integer(int32)` | no |  |
| `spreadBalance` | `integer(int32)` | no |  |
| `spreadDiff` | `integer(int32)` | no |  |
| `spreadDiffBalance` | `integer(int32)` | no |  |
| `tickValue` | `number(double)` | no |  |
| `tickSize` | `number(double)` | no |  |
| `contractSize` | `number(double)` | no |  |
| `stopsLevel` | `integer(int32)` | no |  |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /SymbolGroupExecutionSet`

**Summary:** Set symbol group execution

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `userGroup` | query | `string` | yes | User group path |
| `symbolGroup` | query | `string` | yes | Symbol group path |
| `execution` | query | `ExecutionMode` | yes | Execution mode |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Symbols array | string |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /SymbolGroups`

**Summary:** Symbol groups

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `userGroup` | query | `string` | yes | User group path |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Symbols array | array |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /SymbolGroupsForUserGroup`

**Summary:** Symbol groups for user group

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `group` | query | `string` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | ConGroupSymbol array | array |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /SymbolSessions`

**Summary:** Symbol quote and trade sessions

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `symbols` | query | `array<string>` | no | Symbol |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns QuoteAndTradeSessions array | array |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /SymbolsList`

**Summary:** List of symbols

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Symbols array | array |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /SymbolsParams`

**Summary:** Symbol parameters

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `symbols` | query | `array<string>` | no | List of requered symbols, if not specified - all symbols |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Symbols array | array |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /TickAdd`

**Summary:** Last tick details

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `symbol` | query | `string` | no | Symbol |
| `bid` | query | `number(double)` | no |  |
| `ask` | query | `number(double)` | no |  |
| `volume` | query | `integer(int64)` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | string |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /TickHistory`

**Summary:** Tick history within a specified time period

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `symbol` | query | `string` | yes | Symbol name |
| `from` | query | `string` | yes | Start time in ISO format (yyyy-MM-ddTHH:mm:ss) |
| `to` | query | `string` | yes | End time in ISO format (yyyy-MM-ddTHH:mm:ss) |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns MTTickShort[] | array |
| `201` | Returns ExceptionResult | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /TickHistoryByTime`

**Summary:** Nearest tick to specified time (searches a short window first; if empty, expands to ±2 days)

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes |  |
| `symbol` | query | `string` | yes |  |
| `time` | query | `string` | yes |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns MTTickShort | MTTickShort |
| `404` | Tick not found | ExceptionResult |
| `201` | Returns ExceptionResult | ExceptionResult |

**Response `200` schema — `MTTickShort`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `datetime` | `integer(int64)` | no |  |
| `bid` | `number(double)` | no |  |
| `ask` | `number(double)` | no |  |
| `last` | `number(double)` | no |  |
| `volume` | `integer(int64)` | no |  |
| `datetime_msc` | `integer(int64)` | no |  |
| `flags` | `EnTickShortFlags` | no |  |
| `volume_ext` | `integer(int64)` | no |  |
| `reserved` | `array<integer>` | no |  |

**Response `404` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /TickLast`

**Summary:** Last tick details

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `symbols` | query | `array<string>` | no | Symbols |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns MTTickShort object | array |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /TickStat`

**Summary:** Last tick details

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `symbols` | query | `array<string>` | no | Symbols |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns MTTickStat object | array |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /TradeJournal`

**Summary:** Get Trade Journal.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `mode` | query | `EnMTLogRequestMode` | no | full: 0 host: 4 user: 5 Trade: 6 |
| `type` | query | `EnMTLogType` | no |  |
| `from` | query | `string` | no |  |
| `to` | query | `string` | no |  |
| `filter` | query | `string` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Log Record array | array |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /UserBalanceCheck`

**Summary:** Checks user balance against history and optionally fixes it.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `login` | query | `integer(int64)` | yes | Login number |
| `fixflag` | query | `boolean` | no | false = check only, true = check and fix |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns UserBalanceCheckResult | UserBalanceCheckResult |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `200` schema — `UserBalanceCheckResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `login` | `integer(int64)` | no | Account login |
| `fixFlag` | `boolean` | no | false = check only, true = check and fix |
| `balanceUser` | `number(double)` | no | Current user balance |
| `balanceHistory` | `number(double)` | no | Balance calculated from history |
| `creditUser` | `number(double)` | no | Current user credit |
| `creditHistory` | `number(double)` | no | Credit calculated from history |
| `balanceDifference` | `number(double)` | no | BalanceUser - BalanceHistory |
| `creditDifference` | `number(double)` | no | CreditUser - CreditHistory |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /UserDetails`

**Summary:** User details

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `login` | query | `integer(int64)` | no | Login number |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | User | User |
| `201` | ExceptionResult object | ExceptionResult |

**Response `200` schema — `User`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `clientID` | `integer(int64)` | no |  |
| `firstName` | `string` | no |  |
| `lastName` | `string` | no |  |
| `middleName` | `string` | no |  |
| `otpSecret` | `string` | no |  |
| `limitOrders` | `integer(int32)` | no |  |
| `limitPositionsValue` | `number(double)` | no |  |
| `login` | `integer(int64)` | no |  |
| `group` | `string` | no |  |
| `certSerialNumber` | `integer(int64)` | no |  |
| `rights` | `UsersRights` | no |  |
| `registration` | `integer(int64)` | no |  |
| `lastAccess` | `integer(int64)` | no |  |
| `lastIP` | `string` | no |  |
| `name` | `string` | no |  |
| `company` | `string` | no |  |
| `account` | `string` | no |  |
| `country` | `string` | no |  |
| `language` | `integer(int32)` | no |  |
| `city` | `string` | no |  |
| `state` | `string` | no |  |
| `zipCode` | `string` | no |  |
| `address` | `string` | no |  |
| `phone` | `string` | no |  |
| `eMail` | `string` | no |  |
| `id` | `string` | no |  |
| `status` | `string` | no |  |
| `comment` | `string` | no |  |
| `color` | `integer(int32)` | no |  |
| `phonePassword` | `string` | no |  |
| `leverage` | `integer(int32)` | no |  |
| `agent` | `integer(int64)` | no |  |
| `balance` | `number(double)` | no |  |
| `credit` | `number(double)` | no |  |
| `interestRate` | `number(double)` | no |  |
| `commissionDaily` | `number(double)` | no |  |
| `commissionMonthly` | `number(double)` | no |  |
| `commissionAgentDaily` | `number(double)` | no |  |
| `commissionAgentMonthly` | `number(double)` | no |  |
| `balancePrevDay` | `number(double)` | no |  |
| `balancePrevMonth` | `number(double)` | no |  |
| `equityPrevDay` | `number(double)` | no |  |
| `equityPrevMonth` | `number(double)` | no |  |
| `lastPassChange` | `integer(int64)` | no |  |
| `leadCampaign` | `string` | no |  |
| `leadSource` | `string` | no |  |
| `apiDataClearAll` | `MTRetCode` | no |  |
| `externalAccountClear` | `MTRetCode` | no |  |
| `externalAccountTotal` | `integer(int32)` | no |  |
| `mqid` | `string` | no |  |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /UserDetailsMany`

**Summary:** Accounts details. If logins not specifed reutns details for all accoungts.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `login` | query | `array<integer>` | no | Login number |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | AccountSummary array | array |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /UserDetailsManyPagination`

**Summary:** Paginated variant of 'UserDetailsMany' with an optional registration-date filter.
Login search works the same way as in 'UserDetailsMany': if logins are not specified, returns all accounts.
The full result set is cached (sliding TTL), so subsequent pages of the same query do not re-query the server.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `login` | query | `array<integer>` | no | Login numbers. Null - all accounts. |
| `from` | query | `string` | no | Registration date filter, from (server time) |
| `to` | query | `string` | no | Registration date filter, to (server time) |
| `page` | query | `integer(int32)` | no | Zero-based page index |
| `pageSize` | query | `integer(int32)` | no | Page size, default 100 |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Paginated User result | UserPaginatedResult |
| `201` | ExceptionResult object | ExceptionResult |

**Response `200` schema — `UserPaginatedResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `page` | `integer(int32)` | no |  |
| `pageSize` | `integer(int32)` | no |  |
| `totalCount` | `integer(int32)` | no |  |
| `totalPages` | `integer(int32)` | no |  |
| `items` | `array<User>` | no |  |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /UserGroups`

**Summary:** All user groups

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `assignSymbolGroups` | query | `boolean` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Symbols array | array |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /UserPasswordChange`

**Summary:** Change user passsord

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `type` | query | `EnUsersPasswords` | yes | Type |
| `login` | query | `integer(int64)` | yes | Login |
| `password` | query | `string` | yes | Passowrd |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | string |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /UserPasswordCheck`

**Summary:** Check user password

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `type` | query | `EnUsersPasswords` | yes | Type |
| `login` | query | `integer(int64)` | yes | Login |
| `password` | query | `string` | yes | Passowrd |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | string |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /UserUpdate`

**Summary:** Update user. Only specified fields are updated. Use enableRights/disableRights to toggle individual rights without affecting others.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `enabled` | query | `boolean` | no | Enable or disable user |
| `enableRights` | query | `string` | no | Comma-separated right names to enable (OR into existing). Values: enabled,password,trade_disabled,investor,confirmed,trailing,expert,reports,readonly,reset_pass,otp_enabled,sponsored_hosting,api_enabled,push_notification |
| `disableRights` | query | `string` | no | Comma-separated right names to disable (remove from existing). Same values as enableRights. |
| `ClientID` | query | `integer(int64)` | no |  |
| `FirstName` | query | `string` | no |  |
| `LastName` | query | `string` | no |  |
| `MiddleName` | query | `string` | no |  |
| `OTPSecret` | query | `string` | no |  |
| `LimitOrders` | query | `integer(int32)` | no |  |
| `LimitPositionsValue` | query | `number(double)` | no |  |
| `Login` | query | `integer(int64)` | no |  |
| `Group` | query | `string` | no |  |
| `CertSerialNumber` | query | `integer(int64)` | no |  |
| `Rights` | query | `UsersRights` | no |  |
| `Registration` | query | `integer(int64)` | no |  |
| `LastAccess` | query | `integer(int64)` | no |  |
| `LastIP` | query | `string` | no |  |
| `Name` | query | `string` | no |  |
| `Company` | query | `string` | no |  |
| `Account` | query | `string` | no |  |
| `Country` | query | `string` | no |  |
| `Language` | query | `integer(int32)` | no |  |
| `City` | query | `string` | no |  |
| `State` | query | `string` | no |  |
| `ZIPCode` | query | `string` | no |  |
| `Address` | query | `string` | no |  |
| `Phone` | query | `string` | no |  |
| `EMail` | query | `string` | no |  |
| `ID` | query | `string` | no |  |
| `Status` | query | `string` | no |  |
| `Comment` | query | `string` | no |  |
| `Color` | query | `integer(int32)` | no |  |
| `PhonePassword` | query | `string` | no |  |
| `Leverage` | query | `integer(int32)` | no |  |
| `Agent` | query | `integer(int64)` | no |  |
| `Balance` | query | `number(double)` | no |  |
| `Credit` | query | `number(double)` | no |  |
| `InterestRate` | query | `number(double)` | no |  |
| `CommissionDaily` | query | `number(double)` | no |  |
| `CommissionMonthly` | query | `number(double)` | no |  |
| `CommissionAgentDaily` | query | `number(double)` | no |  |
| `CommissionAgentMonthly` | query | `number(double)` | no |  |
| `BalancePrevDay` | query | `number(double)` | no |  |
| `BalancePrevMonth` | query | `number(double)` | no |  |
| `EquityPrevDay` | query | `number(double)` | no |  |
| `EquityPrevMonth` | query | `number(double)` | no |  |
| `LastPassChange` | query | `integer(int64)` | no |  |
| `LeadCampaign` | query | `string` | no |  |
| `LeadSource` | query | `string` | no |  |
| `ApiDataClearAll` | query | `MTRetCode` | no |  |
| `ExternalAccountClear` | query | `MTRetCode` | no |  |
| `ExternalAccountTotal` | query | `integer(int32)` | no |  |
| `MQID` | query | `string` | no |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | string |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

---

## Admin

_1 endpoint(s)_

### `GET /UserArchive`

**Summary:** Archives user account.

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes |  |
| `login` | query | `integer(int64)` | yes |  |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | ConTime |
| `201` | Returns ExceptionResult object | ExceptionResult |

**Response `200` schema — `ConTime`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `daylight` | `boolean` | no |  |
| `timeZone` | `integer(int32)` | no |  |
| `timeServer` | `string` | no |  |
| `daylightState` | `integer(int32)` | no |  |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

---

## Subscriptions

_11 endpoint(s)_

### `GET /Subscribe`

**Summary:** Subscribe symbol for real time quotes and get results via /events socket connection

Use /events or /OnQuote websocket to get result

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `symbol` | query | `string` | yes | Symbol |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | string |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /SubscribeMany`

**Summary:** Subscribe several symbols for real time quotes and get results via /events or /OnQuote websocket

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `symbol` | query | `array<string>` | no | Symbol |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | string |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /SubscribeMarketWatch`

**Summary:** Subscribe symbol for real time quotes and get results via /events socket connection

Use /OnMarketWatch websocket to get result

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `symbol` | query | `string` | yes | Symbol |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | string |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /SubscribeOrderProfit`

**Summary:** Subscribe order profit updates. Use /OnOrderProfit ws to get result.

Use /events or /OnOrderProfit websocket to get result

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `logins` | query | `array<integer>` | no | Required accounts. Null or empty - subscribe to ALL accounts. |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | string |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /SubscribeOrderProfitInterval`

**Summary:** Subscribe order profit updates with reuquired interval to send uddates. Use /OnOrderProfitInterval ws to get result.

Use /events or /OnOrderProfitInterval websocket to get result

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `logins` | query | `array<integer>` | no | Required accounts. Null or empty - subscribe to ALL accounts. |
| `intervalMs` | query | `integer(int32)` | no | Interval in milliseconds to send updates |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | string |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `POST /SubscribeOrderProfitIntervalPost`

**Summary:** Subscribe order profit updates with reuquired interval to send uddates. Use /OnOrderProfitInterval ws to get result.

Use /events or /OnOrderProfitInterval websocket to get result

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `intervalMs` | query | `integer(int32)` | no | Interval in milliseconds to send updates |

**Request Body**

**Content-Type:** `application/json-patch+json`


**Type:** `array`

**Content-Type:** `application/json`


**Type:** `array`

**Content-Type:** `text/json`


**Type:** `array`

**Content-Type:** `application/*+json`


**Type:** `array`

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | string |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /Unsubscribe`

**Summary:** Unsubscribe symbol for real time quotes and get results via /events or /OnQuote websocket

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `symbol` | query | `string` | yes | Symbol |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | string |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /UnsubscribeMany`

**Summary:** Unsubscribe several symbols for real time quotes and get results via /events or /OnQuote websocket

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `symbol` | query | `array<string>` | yes | Symbol |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | string |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /UnsubscribeOrderProfit`

**Summary:** Subscribe symbol for real time quotes and get results via /events socket connection

Use /events or /OnQuote websocket to get result

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `logins` | query | `array<integer>` | no | Accounts to remove |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | string |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `GET /UnsubscribeOrderProfitInterval`

**Summary:** Subscribe symbol for real time quotes and get results via /events socket connection

Use /events or /OnQuote websocket to get result

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `logins` | query | `array<integer>` | no | Accounts to remove |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | string |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

### `POST /UnsubscribeOrderProfitIntervalPost`

**Summary:** Subscribe symbol for real time quotes and get results via /events socket connection

Use /events or /OnQuote websocket to get result

**Parameters**

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | query | `string` | yes | Token returned by 'Connect' method |
| `logins` | query | `array<integer>` | no | Accounts to remove |

**Responses**

| Status | Description | Schema |
|---|---|---|
| `200` | Returns 'OK' | string |
| `201` | ExceptionResult object | ExceptionResult |

**Response `201` schema — `ExceptionResult`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

---

## Schemas

_128 data models_

Each schema below corresponds to a `components.schemas.<Name>` entry in the OpenAPI spec. Endpoints reference these models in their request/response bodies.

### `Account`

| Field | Type | Required | Description |
|---|---|---|---|
| `login` | `integer(int64)` | no |  |
| `currencyDigits` | `integer(int32)` | no |  |
| `balance` | `number(double)` | no |  |
| `credit` | `number(double)` | no |  |
| `margin` | `number(double)` | no |  |
| `marginFree` | `number(double)` | no |  |
| `marginLevel` | `number(double)` | no |  |
| `marginLeverage` | `integer(int32)` | no |  |
| `profit` | `number(double)` | no |  |
| `storage` | `number(double)` | no |  |
| `floating` | `number(double)` | no |  |
| `equity` | `number(double)` | no |  |
| `soActivation` | `EnSoActivation` | no |  |
| `soTime` | `integer(int64)` | no |  |
| `soLevel` | `number(double)` | no |  |
| `soEquity` | `number(double)` | no |  |
| `soMargin` | `number(double)` | no |  |
| `blockedCommission` | `number(double)` | no |  |
| `blockedProfit` | `number(double)` | no |  |
| `marginInitial` | `number(double)` | no |  |
| `marginMaintenance` | `number(double)` | no |  |
| `assets` | `number(double)` | no |  |
| `liabilities` | `number(double)` | no |  |

---

### `AccountSummary`

Account summary trading information

| Field | Type | Required | Description |
|---|---|---|---|
| `login` | `integer(int64)` | no | Balance |
| `balance` | `number(double)` | no | Balance |
| `profit` | `number(double)` | no | Profit |
| `equity` | `number(double)` | no | Equity |
| `margin` | `number(double)` | no | Margin |
| `freeMargin` | `number(double)` | no | Free margin |

---

### `AccountUpdate`

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | `AccountUpdateType` | no |  |
| `account` | `Account` | no |  |
| `group` | `ConGroup` | no |  |

---

### `AccountUpdateType`

**Allowed values:**

- `MarginCallEnter`
- `MarginCallLeave`
- `StopOutEnter`
- `StopOutLeave`

### `Order`

| Field | Type | Required | Description |
|---|---|---|---|
| `positionByID` | `integer(int64)` | no |  |
| `modificationFlags` | `integer(int32)` | no |  |
| `volumeInitialExt` | `integer(int64)` | no |  |
| `volumeCurrentExt` | `integer(int64)` | no |  |
| `print` | `string` | no |  |
| `orderTicket` | `integer(int64)` | no |  |
| `externalID` | `string` | no |  |
| `login` | `integer(int64)` | no |  |
| `dealer` | `integer(int64)` | no |  |
| `symbol` | `string` | no |  |
| `digits` | `integer(int32)` | no |  |
| `digitsCurrency` | `integer(int32)` | no |  |
| `contractSize` | `number(double)` | no |  |
| `state` | `OrderState` | no |  |
| `reason` | `OrderReason` | no |  |
| `timeSetup` | `integer(int64)` | no |  |
| `timeExpiration` | `integer(int64)` | no |  |
| `timeDone` | `integer(int64)` | no |  |
| `type` | `OrderType` | no |  |
| `typeFill` | `OrderFilling` | no |  |
| `typeTime` | `OrderTime` | no |  |
| `priceOrder` | `number(double)` | no |  |
| `priceTrigger` | `number(double)` | no |  |
| `priceCurrent` | `number(double)` | no |  |
| `priceSL` | `number(double)` | no |  |
| `priceTP` | `number(double)` | no |  |
| `volumeInitial` | `integer(int64)` | no |  |
| `volumeCurrent` | `integer(int64)` | no |  |
| `expertID` | `integer(int64)` | no |  |
| `positionID` | `integer(int64)` | no |  |
| `comment` | `string` | no |  |
| `activationMode` | `OrderActivation` | no |  |
| `activationTime` | `integer(int64)` | no |  |
| `activationPrice` | `number(double)` | no |  |
| `activationFlags` | `TradeActivationFlags` | no |  |
| `apiDataClearAll` | `MTRetCode` | no |  |
| `timeSetupMsc` | `integer(int64)` | no |  |
| `timeDoneMsc` | `integer(int64)` | no |  |
| `rateMargin` | `number(double)` | no |  |
| `lots` | `number(double)` | no |  |

---

### `OrderActivation`

**Allowed values:**

- `NONE`
- `PENDING`
- `STOPLIMIT`
- `EXPIRATION`
- `STOPOUT`

### `OrderFilling`

**Allowed values:**

- `FOK`
- `IOC`
- `RETURN`
- `BOC`

### `OrderFlags`

**Allowed values:**

- `None`
- `Market`
- `Limit`
- `Stop`
- `StopLimit`
- `Sl`
- `Tp`
- `Closeby`
- `All`

### `OrderProfitUpdate`

Profit update message

| Field | Type | Required | Description |
|---|---|---|---|
| `login` | `integer(int64)` | no | Account number |
| `balance` | `number(double)` | no | Balace |
| `equity` | `number(double)` | no | Equity |
| `margin` | `number(double)` | no | User margin |
| `freeMargin` | `number(double)` | no | Free margin |
| `profit` | `number(double)` | no |  |
| `orders` | `array<ProfitUpdateOrder>` | no | Opened orders |

---

### `OrderReason`

**Allowed values:**

- `CLIENT`
- `EXPERT`
- `DEALER`
- `SL`
- `TP`
- `SO`
- `ROLLOVER`
- `EXTERNAL_CLIENT`
- `VMARGIN`
- `GATEWAY`
- `SIGNAL`
- `SETTLEMENT`
- `TRANSFER`
- `SYNC`
- `EXTERNAL_SERVICE`
- `MIGRATION`
- `MOBILE`
- `WEB`
- `SPLIT`

### `OrderSort`

How to sort order history orders

**Allowed values:**

- `OpenTime`
- `CloseTime`

### `OrderState`

**Allowed values:**

- `STARTED`
- `PLACED`
- `CANCELED`
- `PARTIAL`
- `FILLED`
- `REJECTED`
- `EXPIRED`
- `REQUEST_ADD`
- `REQUEST_MODIFY`
- `REQUEST_CANCEL`

### `OrderTime`

**Allowed values:**

- `GTC`
- `DAY`
- `SPECIFIED`
- `SPECIFIED_DAY`

### `OrderType`

**Allowed values:**

- `BUY`
- `SELL`
- `BUY_LIMIT`
- `SELL_LIMIT`
- `BUY_STOP`
- `SELL_STOP`
- `BUY_STLIMIT`
- `SELL_STLIMIT`
- `CLOSE_BY`

### `OrderUpdate`

| Field | Type | Required | Description |
|---|---|---|---|
| `action` | `OrderUpdateAction` | no |  |
| `order` | `Order` | no |  |

---

### `OrderUpdateAction`

**Allowed values:**

- `Add`
- `Update`
- `Delete`

### `Deal`

| Field | Type | Required | Description |
|---|---|---|---|
| `priceSL` | `number(double)` | no |  |
| `priceTP` | `number(double)` | no |  |
| `volumeExt` | `integer(int64)` | no |  |
| `volumeClosedExt` | `integer(int64)` | no |  |
| `fee` | `number(double)` | no |  |
| `value` | `number(double)` | no |  |
| `marketBid` | `number(double)` | no |  |
| `marketAsk` | `number(double)` | no |  |
| `marketLast` | `number(double)` | no |  |
| `print` | `string` | no |  |
| `dealTicket` | `integer(int64)` | no |  |
| `externalID` | `string` | no |  |
| `login` | `integer(int64)` | no |  |
| `dealer` | `integer(int64)` | no |  |
| `order` | `integer(int64)` | no |  |
| `action` | `DealAction` | no |  |
| `entry` | `EntryFlag` | no |  |
| `digits` | `integer(int32)` | no |  |
| `digitsCurrency` | `integer(int32)` | no |  |
| `contractSize` | `number(double)` | no |  |
| `time` | `integer(int64)` | no |  |
| `symbol` | `string` | no |  |
| `price` | `number(double)` | no |  |
| `volume` | `integer(int64)` | no |  |
| `profit` | `number(double)` | no |  |
| `storage` | `number(double)` | no |  |
| `commission` | `number(double)` | no |  |
| `obsoleteValue` | `number(double)` | no |  |
| `rateProfit` | `number(double)` | no |  |
| `rateMargin` | `number(double)` | no |  |
| `expertID` | `integer(int64)` | no |  |
| `positionID` | `integer(int64)` | no |  |
| `comment` | `string` | no |  |
| `apiDataClearAll` | `MTRetCode` | no |  |
| `profitRaw` | `number(double)` | no |  |
| `pricePosition` | `number(double)` | no |  |
| `volumeClosed` | `integer(int64)` | no |  |
| `tickValue` | `number(double)` | no |  |
| `tickSize` | `number(double)` | no |  |
| `flags` | `integer(int64)` | no |  |
| `timeMsc` | `integer(int64)` | no |  |
| `reason` | `OrderReason` | no |  |
| `gateway` | `string` | no |  |
| `priceGateway` | `number(double)` | no |  |
| `modificationFlags` | `integer(int32)` | no |  |
| `lots` | `number(double)` | no |  |

---

### `DealAction`

**Allowed values:**

- `BUY`
- `SELL`
- `BALANCE`
- `CREDIT`
- `CHARGE`
- `CORRECTION`
- `BONUS`
- `COMMISSION`
- `COMMISSION_DAILY`
- `COMMISSION_MONTHLY`
- `AGENT_DAILY`
- `AGENT_MONTHLY`
- `INTERESTRATE`
- `BUY_CANCELED`
- `SELL_CANCELED`
- `DIVIDEND`
- `DIVIDEND_FRANKED`
- `TAX`
- `AGENT`
- `SO_COMPENSATION`
- `SO_COMPENSATION_CREDIT`

### `DealUpdate`

| Field | Type | Required | Description |
|---|---|---|---|
| `action` | `DealUpdateAction` | no |  |
| `deal` | `Deal` | no |  |

---

### `DealUpdateAction`

**Allowed values:**

- `Add`
- `Update`
- `Delete`
- `Clean`
- `Sync`
- `Perform`

### `Position`

| Field | Type | Required | Description |
|---|---|---|---|
| `print` | `string` | no |  |
| `login` | `integer(int64)` | no |  |
| `symbol` | `string` | no |  |
| `action` | `PositionAction` | no |  |
| `digits` | `integer(int32)` | no |  |
| `digitsCurrency` | `integer(int32)` | no |  |
| `contractSize` | `number(double)` | no |  |
| `timeCreate` | `integer(int64)` | no |  |
| `timeUpdate` | `integer(int64)` | no |  |
| `priceOpen` | `number(double)` | no |  |
| `priceCurrent` | `number(double)` | no |  |
| `priceSL` | `number(double)` | no |  |
| `priceTP` | `number(double)` | no |  |
| `volume` | `integer(int64)` | no |  |
| `profit` | `number(double)` | no |  |
| `storage` | `number(double)` | no |  |
| `obsoleteValue` | `number(double)` | no |  |
| `rateProfit` | `number(double)` | no |  |
| `rateMargin` | `number(double)` | no |  |
| `expertID` | `integer(int64)` | no |  |
| `expertPositionID` | `integer(int64)` | no |  |
| `comment` | `string` | no |  |
| `activationMode` | `integer(int32)` | no |  |
| `activationTime` | `integer(int64)` | no |  |
| `activationPrice` | `number(double)` | no |  |
| `activationFlags` | `integer(int32)` | no |  |
| `apiDataClearAll` | `MTRetCode` | no |  |
| `timeCreateMsc` | `integer(int64)` | no |  |
| `timeUpdateMsc` | `integer(int64)` | no |  |
| `dealer` | `integer(int64)` | no |  |
| `positionTicket` | `integer(int64)` | no |  |
| `externalID` | `string` | no |  |
| `modificationFlags` | `integer(int32)` | no |  |
| `reason` | `OrderReason` | no |  |
| `volumeExt` | `integer(int64)` | no |  |
| `lots` | `number(double)` | no |  |

---

### `PositionAction`

**Allowed values:**

- `BUY`
- `SELL`

### `PositionUpdate`

| Field | Type | Required | Description |
|---|---|---|---|
| `action` | `PositionUpdateAction` | no |  |
| `position` | `Position` | no |  |

---

### `PositionUpdateAction`

**Allowed values:**

- `Add`
- `Update`
- `Delete`
- `Clean`

### `User`

| Field | Type | Required | Description |
|---|---|---|---|
| `clientID` | `integer(int64)` | no |  |
| `firstName` | `string` | no |  |
| `lastName` | `string` | no |  |
| `middleName` | `string` | no |  |
| `otpSecret` | `string` | no |  |
| `limitOrders` | `integer(int32)` | no |  |
| `limitPositionsValue` | `number(double)` | no |  |
| `login` | `integer(int64)` | no |  |
| `group` | `string` | no |  |
| `certSerialNumber` | `integer(int64)` | no |  |
| `rights` | `UsersRights` | no |  |
| `registration` | `integer(int64)` | no |  |
| `lastAccess` | `integer(int64)` | no |  |
| `lastIP` | `string` | no |  |
| `name` | `string` | no |  |
| `company` | `string` | no |  |
| `account` | `string` | no |  |
| `country` | `string` | no |  |
| `language` | `integer(int32)` | no |  |
| `city` | `string` | no |  |
| `state` | `string` | no |  |
| `zipCode` | `string` | no |  |
| `address` | `string` | no |  |
| `phone` | `string` | no |  |
| `eMail` | `string` | no |  |
| `id` | `string` | no |  |
| `status` | `string` | no |  |
| `comment` | `string` | no |  |
| `color` | `integer(int32)` | no |  |
| `phonePassword` | `string` | no |  |
| `leverage` | `integer(int32)` | no |  |
| `agent` | `integer(int64)` | no |  |
| `balance` | `number(double)` | no |  |
| `credit` | `number(double)` | no |  |
| `interestRate` | `number(double)` | no |  |
| `commissionDaily` | `number(double)` | no |  |
| `commissionMonthly` | `number(double)` | no |  |
| `commissionAgentDaily` | `number(double)` | no |  |
| `commissionAgentMonthly` | `number(double)` | no |  |
| `balancePrevDay` | `number(double)` | no |  |
| `balancePrevMonth` | `number(double)` | no |  |
| `equityPrevDay` | `number(double)` | no |  |
| `equityPrevMonth` | `number(double)` | no |  |
| `lastPassChange` | `integer(int64)` | no |  |
| `leadCampaign` | `string` | no |  |
| `leadSource` | `string` | no |  |
| `apiDataClearAll` | `MTRetCode` | no |  |
| `externalAccountClear` | `MTRetCode` | no |  |
| `externalAccountTotal` | `integer(int32)` | no |  |
| `mqid` | `string` | no |  |

---

### `UserBalanceCheckResult`

Result of MT5 UserBalanceCheck

| Field | Type | Required | Description |
|---|---|---|---|
| `login` | `integer(int64)` | no | Account login |
| `fixFlag` | `boolean` | no | false = check only, true = check and fix |
| `balanceUser` | `number(double)` | no | Current user balance |
| `balanceHistory` | `number(double)` | no | Balance calculated from history |
| `creditUser` | `number(double)` | no | Current user credit |
| `creditHistory` | `number(double)` | no | Credit calculated from history |
| `balanceDifference` | `number(double)` | no | BalanceUser - BalanceHistory |
| `creditDifference` | `number(double)` | no | CreditUser - CreditHistory |

---

### `UserPaginatedResult`

Generic pagination envelope. Mirrors the mt4-manager-rest implementation
so both APIs expose the same paging contract.

| Field | Type | Required | Description |
|---|---|---|---|
| `page` | `integer(int32)` | no |  |
| `pageSize` | `integer(int32)` | no |  |
| `totalCount` | `integer(int32)` | no |  |
| `totalPages` | `integer(int32)` | no |  |
| `items` | `array<User>` | no |  |

---

### `UserUpdate`

| Field | Type | Required | Description |
|---|---|---|---|
| `action` | `UserUpdateAction` | no |  |
| `user` | `User` | no |  |

---

### `UserUpdateAction`

**Allowed values:**

- `Add`
- `Update`
- `Delete`
- `Clean`

### `UsersRights`

**Allowed values:**

- `USER_RIGHT_NONE`
- `USER_RIGHT_ENABLED`
- `USER_RIGHT_PASSWORD`
- `USER_RIGHT_TRADE_DISABLED`
- `USER_RIGHT_INVESTOR`
- `USER_RIGHT_CONFIRMED`
- `USER_RIGHT_TRAILING`
- `USER_RIGHT_EXPERT`
- `USER_RIGHT_OBSOLETE`
- `USER_RIGHT_REPORTS`
- `USER_RIGHT_DEFAULT`
- `USER_RIGHT_READONLY`
- `USER_RIGHT_RESET_PASS`
- `USER_RIGHT_OTP_ENABLED`
- `USER_RIGHT_UNKNOWN_FLAG`
- `USER_RIGHT_SPONSORED_HOSTING`
- `USER_RIGHT_API_ENABLED`
- `USER_RIGHT_PUSH_NOTIFICATION`
- `USER_RIGHT_ALL`

### `SymbolUpdate`

| Field | Type | Required | Description |
|---|---|---|---|
| `action` | `SymbolUpdateAction` | no |  |
| `symbol` | `ConSymbol` | no |  |

---

### `SymbolUpdateAction`

**Allowed values:**

- `Add`
- `Update`
- `Delete`

### `Quote`

New quote event arguments.

| Field | Type | Required | Description |
|---|---|---|---|
| `symbol` | `string` | no | Trading instrument. |
| `bid` | `number(double)` | no | Bid. |
| `ask` | `number(double)` | no | Ask. |
| `time` | `string(date-time)` | no | Server time. |
| `last` | `number(double)` | no | Last deal price. |
| `volume` | `integer(int64)` | no | Volume |
| `volumeExt` | `integer(int64)` | no | Volume ext |

---

### `QuoteAndTradeSessions`

| Field | Type | Required | Description |
|---|---|---|---|
| `symbol` | `string` | no |  |
| `quote` | `WeekSessions` | no |  |
| `trade` | `WeekSessions` | no |  |

---

### `TickShort`

| Field | Type | Required | Description |
|---|---|---|---|
| `symbol` | `string` | no |  |
| `datetime` | `integer(int64)` | no |  |
| `bid` | `number(double)` | no |  |
| `ask` | `number(double)` | no |  |
| `last` | `number(double)` | no |  |
| `volume` | `integer(int64)` | no |  |
| `datetime_msc` | `integer(int64)` | no |  |
| `flags` | `TickShortFlags` | no |  |
| `volume_ext` | `integer(int64)` | no |  |
| `reserved` | `array<integer>` | no |  |
| `serverTime` | `string(date-time)` | no | Tick time in broker SERVER time. |

---

### `TickShortFlags`

**Allowed values:**

- `TICK_SHORT_FLAG_NONE`
- `TICK_SHORT_FLAG_RAW`
- `TICK_SHORT_FLAG_BID`
- `TICK_SHORT_FLAG_ASK`
- `TICK_SHORT_FLAG_LAST`
- `TICK_SHORT_FLAG_VOLUME`
- `TICK_SHORT_FLAG_BUY`
- `TICK_SHORT_FLAG_SELL`

### `GroupUpdate`

| Field | Type | Required | Description |
|---|---|---|---|
| `action` | `GroupUpdateAction` | no |  |
| `group` | `ConGroup` | no |  |

---

### `GroupUpdateAction`

**Allowed values:**

- `Add`
- `Update`
- `Delete`

### `ConGroup`

| Field | Type | Required | Description |
|---|---|---|---|
| `commissionTotal` | `integer(int32)` | no |  |
| `symbolGroupsTotal` | `integer(int32)` | no |  |
| `marginFreeProfitMode` | `integer(int32)` | no |  |
| `marginMode` | `EnMarginMode` | no |  |
| `authOTPMode` | `EnAuthOTPMode` | no |  |
| `tradeTransferMode` | `EnTransferMode` | no |  |
| `marginFlags` | `EnMarginFlagsGroup` | no |  |
| `limitPositions` | `integer(int32)` | no |  |
| `reportsEmail` | `string` | no |  |
| `demoInactivityPeriod` | `integer(int32)` | no |  |
| `group` | `string` | no |  |
| `server` | `integer(int64)` | no |  |
| `permissionsFlags` | `EnPermissionsFlags` | no |  |
| `authMode` | `EnAuthMode` | no |  |
| `authPasswordMin` | `integer(int32)` | no |  |
| `company` | `string` | no |  |
| `companyPage` | `string` | no |  |
| `companyEmail` | `string` | no |  |
| `companySupportPage` | `string` | no |  |
| `companySupportEmail` | `string` | no |  |
| `companyCatalog` | `string` | no |  |
| `companyDepositPage` | `string` | no |  |
| `companyWithdrawalPage` | `string` | no |  |
| `currency` | `string` | no |  |
| `currencyDigits` | `integer(int32)` | no |  |
| `reportsMode` | `EnReportsMode` | no |  |
| `reportsFlags` | `EnReportsFlags` | no |  |
| `reportsSMTP` | `string` | no |  |
| `reportsSMTPLogin` | `string` | no |  |
| `reportsSMTPPass` | `string` | no |  |
| `newsMode` | `EnNewsMode` | no |  |
| `newsCategory` | `string` | no |  |
| `newsLangClear` | `MTRetCode` | no |  |
| `newsLangTotal` | `integer(int32)` | no |  |
| `mailMode` | `EnMailMode` | no |  |
| `tradeFlags` | `EnTradeFlagsGroup` | no |  |
| `tradeInterestrate` | `number(double)` | no |  |
| `tradeVirtualCredit` | `number(double)` | no |  |
| `marginFreeMode` | `EnFreeMarginMode` | no |  |
| `marginSOMode` | `EnStopOutMode` | no |  |
| `marginCall` | `number(double)` | no |  |
| `marginStopOut` | `number(double)` | no |  |
| `demoLeverage` | `integer(int32)` | no |  |
| `demoDeposit` | `number(double)` | no |  |
| `limitHistory` | `EnHistoryLimit` | no |  |
| `limitOrders` | `integer(int32)` | no |  |
| `limitSymbols` | `integer(int32)` | no |  |
| `symbolGroups` | `array<ConGroupSymbol>` | no |  |

---

### `ConGroupSymbol`

| Field | Type | Required | Description |
|---|---|---|---|
| `ieCheckMode` | `integer(int32)` | no |  |
| `ieCheckModeDefault` | `integer(int32)` | no |  |
| `ieTimeout` | `integer(int32)` | no |  |
| `ieTimeoutDefault` | `integer(int32)` | no |  |
| `ieSlipProfit` | `integer(int32)` | no |  |
| `ieSlipProfitDefault` | `integer(int32)` | no |  |
| `ieSlipLosing` | `integer(int32)` | no |  |
| `ieSlipLosingDefault` | `integer(int32)` | no |  |
| `ieVolumeMax` | `integer(int64)` | no |  |
| `ieVolumeMaxDefault` | `integer(int64)` | no |  |
| `orderFlags` | `OrderFlags` | no |  |
| `orderFlagsDefault` | `OrderFlags` | no |  |
| `marginRateInitialDefault` | `number(double)` | no |  |
| `marginRateMaintenanceDefault` | `number(double)` | no |  |
| `marginRateLiquidity` | `number(double)` | no |  |
| `marginRateLiquidityDefault` | `number(double)` | no |  |
| `reFlags` | `REFlags` | no |  |
| `reFlagsDefault` | `REFlags` | no |  |
| `marginHedged` | `number(double)` | no |  |
| `marginHedgedDefault` | `number(double)` | no |  |
| `permissionsFlags` | `PermissionsFlags` | no |  |
| `marginRateCurrency` | `number(double)` | no |  |
| `marginRateCurrencyDefault` | `number(double)` | no |  |
| `bookDepthLimit` | `integer(int32)` | no |  |
| `ieFlags` | `integer(int32)` | no |  |
| `ieFlagsDefault` | `integer(int32)` | no |  |
| `volumeMinExt` | `integer(int64)` | no |  |
| `volumeMinExtDefault` | `integer(int64)` | no |  |
| `volumeMaxExt` | `integer(int64)` | no |  |
| `volumeMaxExtDefault` | `integer(int64)` | no |  |
| `volumeStepExt` | `integer(int64)` | no |  |
| `volumeStepExtDefault` | `integer(int64)` | no |  |
| `volumeLimitExt` | `integer(int64)` | no |  |
| `volumeLimitExtDefault` | `integer(int64)` | no |  |
| `ieVolumeMaxExt` | `integer(int64)` | no |  |
| `ieVolumeMaxExtDefault` | `integer(int64)` | no |  |
| `swapYearDays` | `integer(int32)` | no |  |
| `swapYearDaysDefault` | `integer(int32)` | no |  |
| `swapFlags` | `integer(int32)` | no |  |
| `swapFlagsDefault` | `integer(int32)` | no |  |
| `swapRateSunday` | `number(double)` | no |  |
| `swapRateSundayDefault` | `number(double)` | no |  |
| `swapRateMonday` | `number(double)` | no |  |
| `swapRateMondayDefault` | `number(double)` | no |  |
| `swapRateTuesday` | `number(double)` | no |  |
| `swapRateTuesdayDefault` | `number(double)` | no |  |
| `swapRateWednesday` | `number(double)` | no |  |
| `swapRateWednesdayDefault` | `number(double)` | no |  |
| `swapRateThursday` | `number(double)` | no |  |
| `swapRateThursdayDefault` | `number(double)` | no |  |
| `swapRateFriday` | `number(double)` | no |  |
| `swapRateFridayDefault` | `number(double)` | no |  |
| `swapRateSaturday` | `number(double)` | no |  |
| `swapRateSaturdayDefault` | `number(double)` | no |  |
| `path` | `string` | no |  |
| `tradeMode` | `TradeMode` | no |  |
| `tradeModeDefault` | `TradeMode` | no |  |
| `execMode` | `ExecutionMode` | no |  |
| `execModeDefault` | `ExecutionMode` | no |  |
| `fillFlags` | `FillingFlags` | no |  |
| `fillFlagsDefault` | `FillingFlags` | no |  |
| `expirFlags` | `ExpirationFlags` | no |  |
| `expirFlagsDefault` | `ExpirationFlags` | no |  |
| `spreadDiff` | `integer(int32)` | no |  |
| `spreadDiffDefault` | `integer(int32)` | no |  |
| `spreadDiffBalance` | `integer(int32)` | no |  |
| `spreadDiffBalanceDefault` | `integer(int32)` | no |  |
| `stopsLevel` | `integer(int32)` | no |  |
| `stopsLevelDefault` | `integer(int32)` | no |  |
| `freezeLevel` | `integer(int32)` | no |  |
| `freezeLevelDefault` | `integer(int32)` | no |  |
| `volumeMin` | `integer(int64)` | no |  |
| `volumeMinDefault` | `integer(int64)` | no |  |
| `volumeMax` | `integer(int64)` | no |  |
| `volumeMaxDefault` | `integer(int64)` | no |  |
| `volumeStep` | `integer(int64)` | no |  |
| `volumeStepDefault` | `integer(int64)` | no |  |
| `volumeLimit` | `integer(int64)` | no |  |
| `volumeLimitDefault` | `integer(int64)` | no |  |
| `marginFlags` | `MarginFlags` | no |  |
| `marginFlagsDefault` | `MarginFlags` | no |  |
| `marginInitial` | `number(double)` | no |  |
| `marginInitialDefault` | `number(double)` | no |  |
| `marginMaintenance` | `number(double)` | no |  |
| `marginMaintenanceDefault` | `number(double)` | no |  |
| `marginLong` | `number(double)` | no |  |
| `marginLongDefault` | `number(double)` | no |  |
| `marginShort` | `number(double)` | no |  |
| `marginShortDefault` | `number(double)` | no |  |
| `marginLimit` | `number(double)` | no |  |
| `marginLimitDefault` | `number(double)` | no |  |
| `marginStop` | `number(double)` | no |  |
| `marginStopDefault` | `number(double)` | no |  |
| `marginStopLimit` | `number(double)` | no |  |
| `marginStopLimitDefault` | `number(double)` | no |  |
| `swapMode` | `SwapMode` | no |  |
| `swapModeDefault` | `SwapMode` | no |  |
| `swapLong` | `number(double)` | no |  |
| `swapLongDefault` | `number(double)` | no |  |
| `swapShort` | `number(double)` | no |  |
| `swapShortDefault` | `number(double)` | no |  |
| `swap3Day` | `integer(int32)` | no |  |
| `swap3DayDefault` | `integer(int32)` | no |  |
| `reTimeout` | `integer(int32)` | no |  |
| `reTimeoutDefault` | `integer(int32)` | no |  |
| `marginRateInitialBuyMarket` | `number(double)` | no |  |
| `marginRateInitialSellMarket` | `number(double)` | no |  |
| `marginRateInitialBuyLimit` | `number(double)` | no |  |
| `marginRateInitialSellLimit` | `number(double)` | no |  |
| `marginRateInitialBuyStop` | `number(double)` | no |  |
| `marginRateInitialSellStop` | `number(double)` | no |  |
| `marginRateMaintenanceBuyMarket` | `number(double)` | no |  |
| `marginRateMaintenanceSellMarket` | `number(double)` | no |  |
| `marginRateMaintenanceBuyLimit` | `number(double)` | no |  |
| `marginRateMaintenanceSellLimit` | `number(double)` | no |  |
| `marginRateMaintenanceBuyStop` | `number(double)` | no |  |
| `marginRateMaintenanceSellStop` | `number(double)` | no |  |

---

### `ConHoliday`

| Field | Type | Required | Description |
|---|---|---|---|
| `description` | `string` | no |  |
| `mode` | `EnHolidayMode` | no |  |
| `year` | `integer(int32)` | no |  |
| `month` | `integer(int32)` | no |  |
| `day` | `integer(int32)` | no |  |
| `workFrom` | `integer(int32)` | no |  |
| `workFromHours` | `integer(int32)` | no |  |
| `workFromMinutes` | `integer(int32)` | no |  |
| `workTo` | `integer(int32)` | no |  |
| `workToHours` | `integer(int32)` | no |  |
| `workToMinutes` | `integer(int32)` | no |  |
| `symbols` | `array<string>` | no |  |

---

### `ConSymbol`

| Field | Type | Required | Description |
|---|---|---|---|
| `priceStrike` | `number(double)` | no |  |
| `marginRateLiquidity` | `number(double)` | no |  |
| `faceValue` | `number(double)` | no |  |
| `accruedInterest` | `number(double)` | no |  |
| `spliceType` | `EnSpliceType` | no |  |
| `spliceTimeType` | `EnSpliceTimeType` | no |  |
| `spliceTimeDays` | `integer(int32)` | no |  |
| `marginHedged` | `number(double)` | no |  |
| `marginRateCurrency` | `number(double)` | no |  |
| `filterGap` | `integer(int32)` | no |  |
| `filterGapTicks` | `integer(int32)` | no |  |
| `chartMode` | `EnChartMode` | no |  |
| `ieFlags` | `integer(int32)` | no |  |
| `volumeMinExt` | `integer(int64)` | no |  |
| `volumeMaxExt` | `integer(int64)` | no |  |
| `volumeStepExt` | `integer(int64)` | no |  |
| `volumeLimitExt` | `integer(int64)` | no |  |
| `ieVolumeMaxExt` | `integer(int64)` | no |  |
| `category` | `string` | no |  |
| `exchange` | `string` | no |  |
| `cfi` | `string` | no |  |
| `sector` | `EnSectors` | no |  |
| `industry` | `EnIndustries` | no |  |
| `country` | `string` | no |  |
| `subscriptionsDelay` | `integer(int32)` | no |  |
| `swapYearDays` | `integer(int32)` | no |  |
| `swapFlags` | `integer(int32)` | no |  |
| `swapRateSunday` | `number(double)` | no |  |
| `swapRateMonday` | `number(double)` | no |  |
| `swapRateTuesday` | `number(double)` | no |  |
| `swapRateWednesday` | `number(double)` | no |  |
| `swapRateThursday` | `number(double)` | no |  |
| `swapRateFriday` | `number(double)` | no |  |
| `swapRateSaturday` | `number(double)` | no |  |
| `freezeLevel` | `integer(int32)` | no |  |
| `quotesTimeout` | `integer(int32)` | no |  |
| `volumeMin` | `integer(int64)` | no |  |
| `volumeMax` | `integer(int64)` | no |  |
| `volumeStep` | `integer(int64)` | no |  |
| `volumeLimit` | `integer(int64)` | no |  |
| `marginFlags` | `EnMarginFlags` | no |  |
| `marginInitial` | `number(double)` | no |  |
| `marginMaintenance` | `number(double)` | no |  |
| `marginLong` | `number(double)` | no |  |
| `marginShort` | `number(double)` | no |  |
| `marginLimit` | `number(double)` | no |  |
| `marginStop` | `number(double)` | no |  |
| `marginStopLimit` | `number(double)` | no |  |
| `swapMode` | `integer(int32)` | no |  |
| `swapLong` | `number(double)` | no |  |
| `swapShort` | `number(double)` | no |  |
| `swap3Day` | `integer(int32)` | no |  |
| `timeStart` | `integer(int64)` | no |  |
| `timeExpiration` | `integer(int64)` | no |  |
| `reFlags` | `integer(int32)` | no |  |
| `reTimeout` | `integer(int32)` | no |  |
| `ieCheckMode` | `integer(int32)` | no |  |
| `ieTimeout` | `integer(int32)` | no |  |
| `ieSlipProfit` | `integer(int32)` | no |  |
| `ieSlipLosing` | `integer(int32)` | no |  |
| `ieVolumeMax` | `integer(int64)` | no |  |
| `priceSettle` | `number(double)` | no |  |
| `priceLimitMax` | `number(double)` | no |  |
| `priceLimitMin` | `number(double)` | no |  |
| `tradeFlags` | `EnTradeFlags` | no |  |
| `orderFlags` | `EnOrderFlags` | no |  |
| `optionsMode` | `EnOptionMode` | no |  |
| `symbol` | `string` | no |  |
| `path` | `string` | no |  |
| `isin` | `string` | no |  |
| `description` | `string` | no |  |
| `international` | `string` | no |  |
| `basis` | `string` | no |  |
| `source` | `string` | no |  |
| `page` | `string` | no |  |
| `currencyBase` | `string` | no |  |
| `currencyBaseDigits` | `integer(int32)` | no |  |
| `currencyProfit` | `string` | no |  |
| `currencyProfitDigits` | `integer(int32)` | no |  |
| `currencyMargin` | `string` | no |  |
| `currencyMarginDigits` | `integer(int32)` | no |  |
| `color` | `integer(int32)` | no |  |
| `colorBackground` | `integer(int32)` | no |  |
| `digits` | `integer(int32)` | no |  |
| `point` | `number(double)` | no |  |
| `multiply` | `number(double)` | no |  |
| `tickFlags` | `EnTickFlagsSym` | no |  |
| `tickBookDepth` | `integer(int32)` | no |  |
| `filterSoft` | `integer(int32)` | no |  |
| `filterSoftTicks` | `integer(int32)` | no |  |
| `filterHard` | `integer(int32)` | no |  |
| `filterHardTicks` | `integer(int32)` | no |  |
| `filterDiscard` | `integer(int32)` | no |  |
| `filterSpreadMax` | `integer(int32)` | no |  |
| `filterSpreadMin` | `integer(int32)` | no |  |
| `tradeMode` | `EnTradeMode` | no |  |
| `calcMode` | `EnCalcMode` | no |  |
| `execMode` | `EnExecutionMode` | no |  |
| `gtcMode` | `EnGTCMode` | no |  |
| `fillFlags` | `EnFillingFlags` | no |  |
| `expirFlags` | `EnExpirationFlags` | no |  |
| `spread` | `integer(int32)` | no |  |
| `spreadBalance` | `integer(int32)` | no |  |
| `spreadDiff` | `integer(int32)` | no |  |
| `spreadDiffBalance` | `integer(int32)` | no |  |
| `tickValue` | `number(double)` | no |  |
| `tickSize` | `number(double)` | no |  |
| `contractSize` | `number(double)` | no |  |
| `stopsLevel` | `integer(int32)` | no |  |

---

### `ConSymbolSession`

| Field | Type | Required | Description |
|---|---|---|---|
| `open` | `integer(int32)` | no |  |
| `openHours` | `integer(int32)` | no |  |
| `openMinutes` | `integer(int32)` | no |  |
| `close` | `integer(int32)` | no |  |
| `closeHours` | `integer(int32)` | no |  |
| `closeMinutes` | `integer(int32)` | no |  |

---

### `ConTime`

| Field | Type | Required | Description |
|---|---|---|---|
| `daylight` | `boolean` | no |  |
| `timeZone` | `integer(int32)` | no |  |
| `timeServer` | `string` | no |  |
| `daylightState` | `integer(int32)` | no |  |

---

### `Confirm`

| Field | Type | Required | Description |
|---|---|---|---|
| `print` | `string` | no |  |
| `id` | `integer(int32)` | no |  |
| `retcode` | `MTRetCode` | no |  |
| `volume` | `integer(int64)` | no |  |
| `price` | `number(double)` | no |  |
| `tickBid` | `number(double)` | no |  |
| `tickAsk` | `number(double)` | no |  |
| `tickLast` | `number(double)` | no |  |
| `comment` | `string` | no |  |
| `flags` | `integer(int32)` | no |  |
| `dealID` | `string` | no |  |
| `orderID` | `string` | no |  |
| `priceGateway` | `number(double)` | no |  |
| `positionExternalID` | `string` | no |  |
| `externalRetcode` | `integer(int32)` | no |  |
| `volumeExt` | `integer(int64)` | no |  |

---

### `ConnectionState`

**Allowed values:**

- `Connected`
- `Disconnected`

### `ConnectionStatus`

Represents the connection status of a trading terminal,
including connectivity state and key timestamps.

| Field | Type | Required | Description |
|---|---|---|---|
| `isConnected` | `boolean` | no | Gets or sets a value indicating whether the terminal is currently connected. |
| `connectTimeUTC` | `string(date-time)` | no | Gets or sets the UTC timestamp of the most recent successful connection to the server. |
| `lastQuoteTimeUTC` | `string(date-time)` | no | Gets or sets the UTC timestamp of the last received market quote from the server. |

---

### `MTChartBar`

| Field | Type | Required | Description |
|---|---|---|---|
| `datetime` | `integer(int64)` | no |  |
| `open` | `number(double)` | no |  |
| `high` | `number(double)` | no |  |
| `low` | `number(double)` | no |  |
| `close` | `number(double)` | no |  |
| `tick_volume` | `integer(int64)` | no |  |
| `spread` | `integer(int32)` | no |  |
| `volume` | `integer(int64)` | no |  |

---

### `MTLogRecord`

| Field | Type | Required | Description |
|---|---|---|---|
| `flags` | `EnMTLogFlags` | no |  |
| `code` | `EnMTLogCode` | no |  |
| `type` | `EnMTLogType` | no |  |
| `datetime` | `integer(int64)` | no |  |
| `source` | `string` | no |  |
| `message` | `string` | no |  |
| `datetime_msc` | `integer(int64)` | no |  |
| `reserved` | `array<integer>` | no |  |

---

### `MTRetCode`

**Allowed values:**

- `MT_RET_OK`
- `MT_RET_OK_NONE`
- `MT_RET_ERROR`
- `MT_RET_ERR_PARAMS`
- `MT_RET_ERR_DATA`
- `MT_RET_ERR_DISK`
- `MT_RET_ERR_MEM`
- `MT_RET_ERR_NETWORK`
- `MT_RET_ERR_PERMISSIONS`
- `MT_RET_ERR_TIMEOUT`
- `MT_RET_ERR_CONNECTION`
- `MT_RET_ERR_NOSERVICE`
- `MT_RET_ERR_FREQUENT`
- `MT_RET_ERR_NOTFOUND`
- `MT_RET_ERR_PARTIAL`
- `MT_RET_ERR_SHUTDOWN`
- `MT_RET_ERR_CANCEL`
- `MT_RET_ERR_DUPLICATE`
- `MT_RET_AUTH_CLIENT_INVALID`
- `MT_RET_AUTH_ACCOUNT_INVALID`
- `MT_RET_AUTH_ACCOUNT_DISABLED`
- `MT_RET_AUTH_ADVANCED`
- `MT_RET_AUTH_CERTIFICATE`
- `MT_RET_AUTH_CERTIFICATE_BAD`
- `MT_RET_AUTH_NOTCONFIRMED`
- `MT_RET_AUTH_SERVER_INTERNAL`
- `MT_RET_AUTH_SERVER_BAD`
- `MT_RET_AUTH_UPDATE_ONLY`
- `MT_RET_AUTH_CLIENT_OLD`
- `MT_RET_AUTH_MANAGER_NOCONFIG`
- `MT_RET_AUTH_MANAGER_IPBLOCK`
- `MT_RET_AUTH_GROUP_INVALID`
- `MT_RET_AUTH_CA_DISABLED`
- `MT_RET_AUTH_INVALID_ID`
- `MT_RET_AUTH_INVALID_IP`
- `MT_RET_AUTH_INVALID_TYPE`
- `MT_RET_AUTH_SERVER_BUSY`
- `MT_RET_AUTH_SERVER_CERT`
- `MT_RET_AUTH_ACCOUNT_UNKNOWN`
- `MT_RET_AUTH_SERVER_OLD`
- `MT_RET_AUTH_SERVER_LIMIT`
- `MT_RET_AUTH_MOBILE_DISABLED`
- `MT_RET_AUTH_MANAGER_TYPE`
- `MT_RET_AUTH_DEMO_DISABLED`
- `MT_RET_AUTH_RESET_PASSWORD`
- `MT_RET_AUTH_OTP_INVALID`
- `MT_RET_AUTH_OTP_NEED_SECRET`
- `MT_RET_AUTH_MIGRATION_MT4`
- `MT_RET_AUTH_MIGRATION_MT5`
- `MT_RET_AUTH_INVALID_VERIFY`
- `MT_RET_AUTH_VERIFY_BAD_EMAIL`
- `MT_RET_AUTH_VERIFY_BAD_PHONE`
- `MT_RET_AUTH_API_DISABLED`
- `MT_RET_CFG_LAST_ADMIN`
- `MT_RET_CFG_LAST_ADMIN_GROUP`
- `MT_RET_CFG_NOT_EMPTY`
- `MT_RET_CFG_INVALID_RANGE`
- `MT_RET_CFG_NOT_MANAGER_LOGIN`
- `MT_RET_CFG_BUILTIN`
- `MT_RET_CFG_DUPLICATE`
- `MT_RET_CFG_LIMIT_REACHED`
- `MT_RET_CFG_NO_ACCESS_TO_MAIN`
- `MT_RET_CFG_DEALER_ID_EXIST`
- `MT_RET_CFG_BIND_ADDR_EXIST`
- `MT_RET_CFG_WORKING_TRADE`
- `MT_RET_CFG_GATEWAY_NAME_EXIST`
- `MT_RET_CFG_SWITCH_TO_BACKUP`
- `MT_RET_CFG_NO_BACKUP_MODULE`
- `MT_RET_CFG_NO_TRADE_MODULE`
- `MT_RET_CFG_NO_HISTORY_MODULE`
- `MT_RET_CFG_ANOTHER_SWITCH`
- `MT_RET_CFG_NO_LICENSE_FILE`
- `MT_RET_CFG_GATEWAY_LOGIN_EXIST`
- `MT_RET_CFG_INVALID_COMPANY`
- `MT_RET_USR_LAST_ADMIN`
- `MT_RET_USR_LOGIN_EXHAUSTED`
- `MT_RET_USR_LOGIN_PROHIBITED`
- `MT_RET_USR_LOGIN_EXIST`
- `MT_RET_USR_SUICIDE`
- `MT_RET_USR_INVALID_PASSWORD`
- `MT_RET_USR_LIMIT_REACHED`
- `MT_RET_USR_HAS_TRADES`
- `MT_RET_USR_DIFFERENT_SERVERS`
- `MT_RET_USR_DIFFERENT_CURRENCY`
- `MT_RET_USR_IMPORT_BALANCE`
- `MT_RET_USR_IMPORT_GROUP`
- `MT_RET_USR_ACCOUNT_EXIST`
- `MT_RET_USR_IMPORT_ACCOUNT`
- `MT_RET_USR_IMPORT_POSITIONS`
- `MT_RET_USR_IMPORT_ORDERS`
- `MT_RET_USR_IMPORT_DEALS`
- `MT_RET_USR_IMPORT_HISTORY`
- `MT_RET_USR_API_LIMIT_REACHED`
- `MT_RET_TRADE_LIMIT_REACHED`
- `MT_RET_TRADE_ORDER_EXIST`
- `MT_RET_TRADE_ORDER_EXHAUSTED`
- `MT_RET_TRADE_DEAL_EXHAUSTED`
- `MT_RET_TRADE_MAX_MONEY`
- `MT_RET_TRADE_DEAL_EXIST`
- `MT_RET_TRADE_ORDER_PROHIBITED`
- `MT_RET_TRADE_DEAL_PROHIBITED`
- `MT_RET_TRADE_SPLIT_VOLUME`
- `MT_RET_REPORT_SNAPSHOT`
- `MT_RET_REPORT_NOTSUPPORTED`
- `MT_RET_REPORT_NODATA`
- `MT_RET_REPORT_TEMPLATE_BAD`
- `MT_RET_REPORT_TEMPLATE_END`
- `MT_RET_REPORT_INVALID_ROW`
- `MT_RET_REPORT_LIMIT_REPEAT`
- `MT_RET_REPORT_LIMIT_REPORT`
- `MT_RET_HST_SYMBOL_NOTFOUND`
- `MT_RET_REQUEST_INWAY`
- `MT_RET_REQUEST_ACCEPTED`
- `MT_RET_REQUEST_PROCESS`
- `MT_RET_REQUEST_REQUOTE`
- `MT_RET_REQUEST_PRICES`
- `MT_RET_REQUEST_REJECT`
- `MT_RET_REQUEST_CANCEL`
- `MT_RET_REQUEST_PLACED`
- `MT_RET_REQUEST_DONE`
- `MT_RET_REQUEST_DONE_PARTIAL`
- `MT_RET_REQUEST_ERROR`
- `MT_RET_REQUEST_TIMEOUT`
- `MT_RET_REQUEST_INVALID`
- `MT_RET_REQUEST_INVALID_VOLUME`
- `MT_RET_REQUEST_INVALID_PRICE`
- `MT_RET_REQUEST_INVALID_STOPS`
- `MT_RET_REQUEST_TRADE_DISABLED`
- `MT_RET_REQUEST_MARKET_CLOSED`
- `MT_RET_REQUEST_NO_MONEY`
- `MT_RET_REQUEST_PRICE_CHANGED`
- `MT_RET_REQUEST_PRICE_OFF`
- `MT_RET_REQUEST_INVALID_EXP`
- `MT_RET_REQUEST_ORDER_CHANGED`
- `MT_RET_REQUEST_TOO_MANY`
- `MT_RET_REQUEST_NO_CHANGES`
- `MT_RET_REQUEST_AT_DISABLED_SERVER`
- `MT_RET_REQUEST_AT_DISABLED_CLIENT`
- `MT_RET_REQUEST_LOCKED`
- `MT_RET_REQUEST_FROZEN`
- `MT_RET_REQUEST_INVALID_FILL`
- `MT_RET_REQUEST_CONNECTION`
- `MT_RET_REQUEST_ONLY_REAL`
- `MT_RET_REQUEST_LIMIT_ORDERS`
- `MT_RET_REQUEST_LIMIT_VOLUME`
- `MT_RET_REQUEST_INVALID_ORDER`
- `MT_RET_REQUEST_POSITION_CLOSED`
- `MT_RET_REQUEST_EXECUTION_SKIPPED`
- `MT_RET_REQUEST_INVALID_CLOSE_VOLUME`
- `MT_RET_REQUEST_CLOSE_ORDER_EXIST`
- `MT_RET_REQUEST_LIMIT_POSITIONS`
- `MT_RET_REQUEST_REJECT_CANCEL`
- `MT_RET_REQUEST_LONG_ONLY`
- `MT_RET_REQUEST_SHORT_ONLY`
- `MT_RET_REQUEST_CLOSE_ONLY`
- `MT_RET_REQUEST_PROHIBITED_BY_FIFO`
- `MT_RET_REQUEST_HEDGE_PROHIBITED`
- `MT_RET_REQUEST_RETURN`
- `MT_RET_REQUEST_DONE_CANCEL`
- `MT_RET_REQUEST_REQUOTE_RETURN`
- `MT_RET_ERR_NOTIMPLEMENT`
- `MT_RET_ERR_NOTMAIN`
- `MT_RET_ERR_NOTSUPPORTED`
- `MT_RET_ERR_DEADLOCK`
- `MT_RET_ERR_LOCKED`
- `MT_RET_MESSENGER_INVALID_PHONE`
- `MT_RET_MESSENGER_NOT_MOBILE`
- `MT_RET_SUBS_NOT_FOUND`
- `MT_RET_SUBS_NOT_FOUND_CFG`
- `MT_RET_SUBS_NOT_FOUND_USER`
- `MT_RET_SUBS_DISABLED`
- `MT_RET_SUBS_PERMISSION_USER`
- `MT_RET_SUBS_PERMISSION_SUBSCRIBE`
- `MT_RET_SUBS_PERMISSION_UNSUBSCRIBE`
- `MT_RET_SUBS_REAL_ONLY`
- `MT_RET_SUBS_PAYMENT_METHOD`

### `MTTick`

| Field | Type | Required | Description |
|---|---|---|---|
| `symbol` | `string` | no |  |
| `bank` | `string` | no |  |
| `datetime` | `integer(int64)` | no |  |
| `bid` | `number(double)` | no |  |
| `ask` | `number(double)` | no |  |
| `last` | `number(double)` | no |  |
| `volume` | `integer(int64)` | no |  |
| `datetime_msc` | `integer(int64)` | no |  |
| `flags` | `EnTickFlags` | no |  |
| `volume_ext` | `integer(int64)` | no |  |
| `reserved` | `array<integer>` | no |  |

---

### `MTTickShort`

| Field | Type | Required | Description |
|---|---|---|---|
| `datetime` | `integer(int64)` | no |  |
| `bid` | `number(double)` | no |  |
| `ask` | `number(double)` | no |  |
| `last` | `number(double)` | no |  |
| `volume` | `integer(int64)` | no |  |
| `datetime_msc` | `integer(int64)` | no |  |
| `flags` | `EnTickShortFlags` | no |  |
| `volume_ext` | `integer(int64)` | no |  |
| `reserved` | `array<integer>` | no |  |

---

### `MTTickStat`

| Field | Type | Required | Description |
|---|---|---|---|
| `symbol` | `string` | no |  |
| `datetime` | `integer(int64)` | no |  |
| `bid_high` | `number(double)` | no |  |
| `bid_low` | `number(double)` | no |  |
| `ask_high` | `number(double)` | no |  |
| `ask_low` | `number(double)` | no |  |
| `last_high` | `number(double)` | no |  |
| `last_low` | `number(double)` | no |  |
| `vol_high` | `integer(int64)` | no |  |
| `vol_low` | `integer(int64)` | no |  |
| `trade_deals` | `integer(int64)` | no |  |
| `trade_volume` | `integer(int64)` | no |  |
| `trade_turnover` | `integer(int64)` | no |  |
| `trade_interest` | `integer(int64)` | no |  |
| `trade_buy_orders` | `integer(int64)` | no |  |
| `trade_buy_volume` | `integer(int64)` | no |  |
| `trade_sell_orders` | `integer(int64)` | no |  |
| `trade_sell_volume` | `integer(int64)` | no |  |
| `trade_volume_ext` | `integer(int64)` | no |  |
| `trade_buy_volume_ext` | `integer(int64)` | no |  |
| `trade_sell_volume_ext` | `integer(int64)` | no |  |
| `vol_high_ext` | `integer(int64)` | no |  |
| `vol_low_ext` | `integer(int64)` | no |  |
| `trade_reserved` | `array<integer>` | no |  |
| `datetime_msc` | `integer(int64)` | no |  |
| `price_open` | `number(double)` | no |  |
| `price_close` | `number(double)` | no |  |
| `price_aw` | `number(double)` | no |  |
| `price_obsolete` | `number(double)` | no |  |
| `price_volatility` | `number(double)` | no |  |
| `price_theoretical` | `number(double)` | no |  |
| `price_greeks_delta` | `number(double)` | no |  |
| `price_greeks_theta` | `number(double)` | no |  |
| `price_greeks_gamma` | `number(double)` | no |  |
| `price_greeks_vega` | `number(double)` | no |  |
| `price_greeks_rho` | `number(double)` | no |  |
| `price_greeks_omega` | `number(double)` | no |  |
| `price_sensitivity` | `number(double)` | no |  |
| `price_reserved` | `array<integer>` | no |  |

---

### `ClientOrder`

Pending, market or history order

| Field | Type | Required | Description |
|---|---|---|---|
| `ticket` | `integer(int64)` | no |  |
| `login` | `integer(int64)` | no |  |
| `profit` | `number(double)` | no |  |
| `swap` | `number(double)` | no |  |
| `commission` | `number(double)` | no |  |
| `fee` | `number(double)` | no |  |
| `closePrice` | `number(double)` | no |  |
| `closeTime` | `string(date-time)` | no |  |
| `closeLots` | `number(double)` | no |  |
| `closeComment` | `string` | no |  |
| `openPrice` | `number(double)` | no |  |
| `openTime` | `string(date-time)` | no |  |
| `lots` | `number(double)` | no |  |
| `contractSize` | `number(double)` | no |  |
| `expertId` | `integer(int64)` | no |  |
| `placedType` | `OrderReason` | no |  |
| `orderType` | `OrderType` | no |  |
| `dealType` | `DealAction` | no |  |
| `symbol` | `string` | no |  |
| `comment` | `string` | no |  |
| `state` | `OrderState` | no |  |
| `stopLoss` | `number(double)` | no |  |
| `takeProfit` | `number(double)` | no |  |
| `requestId` | `integer(int32)` | no |  |
| `digits` | `integer(int32)` | no |  |
| `profitRate` | `number(double)` | no |  |
| `stopLimitPrice` | `number(double)` | no |  |
| `dealInternalIn` | `Deal` | no |  |
| `dealInternalOut` | `Deal` | no |  |
| `orderInternal` | `Order` | no |  |
| `accountCurrency` | `string` | no |  |
| `serverTimezone` | `integer(int32)` | no |  |
| `closeVolume` | `integer(int64)` | no |  |
| `volume` | `integer(int64)` | no |  |
| `expirationType` | `OrderTime` | no |  |
| `expirationTime` | `string(date-time)` | no |  |
| `fillPolicy` | `OrderFilling` | no |  |
| `openTimestampUTC` | `integer(int64)` | no | Open timestamp in milliseconds |
| `closeTimestampUTC` | `integer(int64)` | no | Close timestamp in milliseconds |

---

### `ClientOrderPaginatedResult`

Generic pagination envelope. Mirrors the mt4-manager-rest implementation
so both APIs expose the same paging contract.

| Field | Type | Required | Description |
|---|---|---|---|
| `page` | `integer(int32)` | no |  |
| `pageSize` | `integer(int32)` | no |  |
| `totalCount` | `integer(int32)` | no |  |
| `totalPages` | `integer(int32)` | no |  |
| `items` | `array<ClientOrder>` | no |  |

---

### `Daily`

| Field | Type | Required | Description |
|---|---|---|---|
| `positionTotal` | `integer(int32)` | no |  |
| `orderClear` | `MTRetCode` | no |  |
| `orderTotal` | `integer(int32)` | no |  |
| `profitAssets` | `number(double)` | no |  |
| `profitLiabilities` | `number(double)` | no |  |
| `dailyDividend` | `number(double)` | no |  |
| `dailyTaxes` | `number(double)` | no |  |
| `dailySOCompensation` | `number(double)` | no |  |
| `dailyCommFee` | `number(double)` | no |  |
| `dailySOCompensationCredit` | `number(double)` | no |  |
| `datetime` | `integer(int64)` | no |  |
| `datetimePrev` | `integer(int64)` | no |  |
| `login` | `integer(int64)` | no |  |
| `name` | `string` | no |  |
| `group` | `string` | no |  |
| `currency` | `string` | no |  |
| `currencyDigits` | `integer(int32)` | no |  |
| `company` | `string` | no |  |
| `eMail` | `string` | no |  |
| `balance` | `number(double)` | no |  |
| `credit` | `number(double)` | no |  |
| `interestRate` | `number(double)` | no |  |
| `commissionDaily` | `number(double)` | no |  |
| `commissionMonthly` | `number(double)` | no |  |
| `agentDaily` | `number(double)` | no |  |
| `agentMonthly` | `number(double)` | no |  |
| `balancePrevDay` | `number(double)` | no |  |
| `balancePrevMonth` | `number(double)` | no |  |
| `equityPrevDay` | `number(double)` | no |  |
| `equityPrevMonth` | `number(double)` | no |  |
| `margin` | `number(double)` | no |  |
| `marginFree` | `number(double)` | no |  |
| `marginLevel` | `number(double)` | no |  |
| `marginLeverage` | `integer(int32)` | no |  |
| `profit` | `number(double)` | no |  |
| `profitStorage` | `number(double)` | no |  |
| `profitEquity` | `number(double)` | no |  |
| `dailyProfit` | `number(double)` | no |  |
| `dailyBalance` | `number(double)` | no |  |
| `dailyCredit` | `number(double)` | no |  |
| `dailyCharge` | `number(double)` | no |  |
| `dailyCorrection` | `number(double)` | no |  |
| `dailyBonus` | `number(double)` | no |  |
| `dailyStorage` | `number(double)` | no |  |
| `dailyCommInstant` | `number(double)` | no |  |
| `dailyCommRound` | `number(double)` | no |  |
| `dailyAgent` | `number(double)` | no |  |
| `dailyInterest` | `number(double)` | no |  |
| `positions` | `array<Position>` | no |  |
| `orders` | `array<Order>` | no |  |

---

### `EnAuthMode`

**Allowed values:**

- `AUTH_STANDARD`
- `AUTH_RSA1024`
- `AUTH_LAST`
- `AUTH_RSA_CUSTOM`

### `EnAuthOTPMode`

**Allowed values:**

- `AUTH_OTP_DISABLED`
- `AUTH_OTP_TOTP_SHA256`

### `EnCalcMode`

**Allowed values:**

- `TRADE_MODE_FOREX`
- `TRADE_MODE_FUTURES`
- `TRADE_MODE_CFD`
- `TRADE_MODE_CFDINDEX`
- `TRADE_MODE_CFDLEVERAGE`
- `TRADE_MODE_FOREX_NO_LEVERAGE`
- `TRADE_MODE_EXCH_FIRST`
- `TRADE_MODE_EXCH_FUTURES`
- `TRADE_MODE_EXCH_FUTURES_FORTS`
- `TRADE_MODE_EXCH_OPTIONS`
- `TRADE_MODE_EXCH_OPTIONS_MARGIN`
- `TRADE_MODE_EXCH_BONDS`
- `TRADE_MODE_EXCH_STOCKS_MOEX`
- `TRADE_MODE_EXCH_LAST`
- `TRADE_MODE_SERV_FIRST`

### `EnChartMode`

**Allowed values:**

- `CHART_MODE_BID_PRICE`
- `CHART_MODE_LAST_PRICE`
- `CHART_MODE_OLD`

### `EnDealAction`

**Allowed values:**

- `DEAL_BUY`
- `DEAL_SELL`
- `DEAL_BALANCE`
- `DEAL_CREDIT`
- `DEAL_CHARGE`
- `DEAL_CORRECTION`
- `DEAL_BONUS`
- `DEAL_COMMISSION`
- `DEAL_COMMISSION_DAILY`
- `DEAL_COMMISSION_MONTHLY`
- `DEAL_AGENT_DAILY`
- `DEAL_AGENT_MONTHLY`
- `DEAL_INTERESTRATE`
- `DEAL_BUY_CANCELED`
- `DEAL_SELL_CANCELED`
- `DEAL_DIVIDEND`
- `DEAL_DIVIDEND_FRANKED`
- `DEAL_TAX`
- `DEAL_AGENT`
- `DEAL_SO_COMPENSATION`
- `DEAL_SO_COMPENSATION_CREDIT`

### `EnExecutionMode`

**Allowed values:**

- `EXECUTION_REQUEST`
- `EXECUTION_INSTANT`
- `EXECUTION_MARKET`
- `EXECUTION_EXCHANGE`

### `EnExpirationFlags`

**Allowed values:**

- `TIME_FLAGS_NONE`
- `TIME_FLAGS_GTC`
- `TIME_FLAGS_DAY`
- `TIME_FLAGS_SPECIFIED`
- `TIME_FLAGS_SPECIFIED_DAY`
- `TIME_FLAGS_ALL`

### `EnFillingFlags`

**Allowed values:**

- `FILL_FLAGS_NONE`
- `FILL_FLAGS_FIRST`
- `FILL_FLAGS_IOC`
- `FILL_FLAGS_ALL`

### `EnFreeMarginMode`

**Allowed values:**

- `FREE_MARGIN_NOT_USE_PL`
- `FREE_MARGIN_USE_PL`
- `FREE_MARGIN_PROFIT`
- `FREE_MARGIN_LOSS`

### `EnGTCMode`

**Allowed values:**

- `ORDERS_GTC`
- `ORDERS_DAILY`
- `ORDERS_DAILY_NO_STOPS`

### `EnHistoryLimit`

**Allowed values:**

- `TRADE_HISTORY_ALL`
- `TRADE_HISTORY_MONTHS_1`
- `TRADE_HISTORY_MONTHS_3`
- `TRADE_HISTORY_MONTHS_6`
- `TRADE_HISTORY_YEAR_1`
- `TRADE_HISTORY_YEAR_2`
- `TRADE_HISTORY_YEAR_3`

### `EnHolidayMode`

**Allowed values:**

- `HOLIDAY_DISABLED`
- `HOLIDAY_ENABLED`

### `EnIndustries`

**Allowed values:**

- `INDUSTRY_FIRST`
- `INDUSTRY_AGRICULTURAL_INPUTS`
- `INDUSTRY_ALUMINIUM`
- `INDUSTRY_BUILDING_MATERIALS`
- `INDUSTRY_CHEMICALS`
- `INDUSTRY_COKING_COAL`
- `INDUSTRY_COPPER`
- `INDUSTRY_GOLD`
- `INDUSTRY_LUMBER_WOOD`
- `INDUSTRY_INDUSTRIAL_METALS`
- `INDUSTRY_PRECIOUS_METALS`
- `INDUSTRY_PAPER`
- `INDUSTRY_SILVER`
- `INDUSTRY_SPECIALTY_CHEMICALS`
- `INDUSTRY_STEEL`
- `INDUSTRY_BASIC_MATERIALS_END`
- `INDUSTRY_COMMUNICATION_FIRST`
- `INDUSTRY_BROADCASTING`
- `INDUSTRY_GAMING_MULTIMEDIA`
- `INDUSTRY_ENTERTAINMENT`
- `INDUSTRY_INTERNET_CONTENT`
- `INDUSTRY_PUBLISHING`
- `INDUSTRY_TELECOM`
- `INDUSTRY_COMMUNICATION_END`
- `INDUSTRY_APPAREL_MANUFACTURING`
- `INDUSTRY_APPAREL_RETAIL`
- `INDUSTRY_AUTO_MANUFACTURERS`
- `INDUSTRY_AUTO_PARTS`
- `INDUSTRY_AUTO_DEALERSHIP`
- `INDUSTRY_DEPARTMENT_STORES`
- `INDUSTRY_FOOTWEAR_ACCESSORIES`
- `INDUSTRY_FURNISHINGS`
- `INDUSTRY_GAMBLING`
- `INDUSTRY_HOME_IMPROV_RETAIL`
- `INDUSTRY_INTERNET_RETAIL`
- `INDUSTRY_LEISURE`
- `INDUSTRY_LODGING`
- `INDUSTRY_LUXURY_GOODS`
- `INDUSTRY_PACKAGING_CONTAINERS`
- `INDUSTRY_PERSONAL_SERVICES`
- `INDUSTRY_RECREATIONAL_VEHICLES`
- `INDUSTRY_RESIDENT_CONSTRUCTION`
- `INDUSTRY_RESORTS_CASINOS`
- `INDUSTRY_RESTAURANTS`
- `INDUSTRY_SPECIALTY_RETAIL`
- `INDUSTRY_TEXTILE_MANUFACTURING`
- `INDUSTRY_TRAVEL_SERVICES`
- `INDUSTRY_CONSUMER_CYCL_END`
- `INDUSTRY_CONSUMER_DEF_FIRST`
- `INDUSTRY_BEVERAGES_NON_ALCO`
- `INDUSTRY_BEVERAGES_WINERIES`
- `INDUSTRY_CONFECTIONERS`
- `INDUSTRY_DISCOUNT_STORES`
- `INDUSTRY_EDUCATION_TRAINIG`
- `INDUSTRY_FARM_PRODUCTS`
- `INDUSTRY_FOOD_DISTRIBUTION`
- `INDUSTRY_GROCERY_STORES`
- `INDUSTRY_HOUSEHOLD_PRODUCTS`
- `INDUSTRY_PACKAGED_FOODS`
- `INDUSTRY_TOBACCO`
- `INDUSTRY_CONSUMER_DEF_END`
- `INDUSTRY_ENERGY_FIRST`
- `INDUSTRY_OIL_GAS_EP`
- `INDUSTRY_OIL_GAS_EQUIPMENT`
- `INDUSTRY_OIL_GAS_INTEGRATED`
- `INDUSTRY_OIL_GAS_MIDSTREAM`
- `INDUSTRY_OIL_GAS_REFINING`
- `INDUSTRY_THERMAL_COAL`
- `INDUSTRY_ENERGY_LAST`
- `INDUSTRY_ENERGY_END`
- `INDUSTRY_FINANCIAL_FIRST`
- `INDUSTRY_ASSETS_MANAGEMENT`
- `INDUSTRY_BANKS_DIVERSIFIED`
- `INDUSTRY_BANKS_REGIONAL`
- `INDUSTRY_CAPITAL_MARKETS`
- `INDUSTRY_CLOSE_END_FUND_DEBT`
- `INDUSTRY_CLOSE_END_FUND_EQUITY`
- `INDUSTRY_CLOSE_END_FUND_FOREIGN`
- `INDUSTRY_CREDIT_SERVICES`
- `INDUSTRY_FINANCIAL_CONGLOMERATE`
- `INDUSTRY_FINANCIAL_DATA_EXCHANGE`
- `INDUSTRY_INSURANCE_BROKERS`
- `INDUSTRY_INSURANCE_DIVERSIFIED`
- `INDUSTRY_INSURANCE_LIFE`
- `INDUSTRY_INSURANCE_PROPERTY`
- `INDUSTRY_INSURANCE_REINSURANCE`
- `INDUSTRY_INSURANCE_SPECIALTY`
- `INDUSTRY_MORTGAGE_FINANCE`
- `INDUSTRY_SHELL_COMPANIES`
- `INDUSTRY_FINANCIAL_END`
- `INDUSTRY_BIOTECHNOLOGY`
- `INDUSTRY_DIAGNOSTICS_RESEARCH`
- `INDUSTRY_DRUGS_MANUFACTURERS`
- `INDUSTRY_DRUGS_MANUFACTURERS_SPEC`
- `INDUSTRY_HEALTHCARE_PLANS`
- `INDUSTRY_HEALTH_INFORMATION`
- `INDUSTRY_MEDICAL_FACILITIES`
- `INDUSTRY_MEDICAL_DEVICES`
- `INDUSTRY_MEDICAL_DISTRIBUTION`
- `INDUSTRY_MEDICAL_INSTRUMENTS`
- `INDUSTRY_HEALTHCARE_LAST`
- `INDUSTRY_HEALTHCARE_END`
- `INDUSTRY_INDUSTRIALS_FIRST`
- `INDUSTRY_AIRLINES`
- `INDUSTRY_AIRPORTS_SERVICES`
- `INDUSTRY_BUILDING_PRODUCTS`
- `INDUSTRY_BUSINESS_EQUIPMENT`
- `INDUSTRY_CONGLOMERATES`
- `INDUSTRY_CONSULTING_SERVICES`
- `INDUSTRY_ELECTRICAL_EQUIPMENT`
- `INDUSTRY_ENGINEERING_CONSTRUCTION`
- `INDUSTRY_FARM_HEAVY_MACHINERY`
- `INDUSTRY_INDUSTRIAL_DISTRIBUTION`
- `INDUSTRY_INFRASTRUCTURE_OPERATIONS`
- `INDUSTRY_FREIGHT_LOGISTICS`
- `INDUSTRY_MARINE_SHIPPING`
- `INDUSTRY_METAL_FABRICATION`
- `INDUSTRY_POLLUTION_CONTROL`
- `INDUSTRY_RAILROADS`
- `INDUSTRY_RENTAL_LEASING`
- `INDUSTRY_SECURITY_PROTECTION`
- `INDUSTRY_SPEALITY_BUSINESS_SERVICES`
- `INDUSTRY_SPEALITY_MACHINERY`
- `INDUSTRY_STUFFING_EMPLOYMENT`
- `INDUSTRY_TOOLS_ACCESSORIES`
- `INDUSTRY_TRUCKING`
- `INDUSTRY_INDUSTRIALS_LAST`
- `INDUSTRY_INDUSTRIALS_END`
- `INDUSTRY_REAL_ESTATE_FIRST`
- `INDUSTRY_REAL_ESTATE_DIVERSIFIED`
- `INDUSTRY_REAL_ESTATE_SERVICES`
- `INDUSTRY_REIT_DIVERSIFIED`
- `INDUSTRY_REIT_HEALTCARE`
- `INDUSTRY_REIT_HOTEL_MOTEL`
- `INDUSTRY_REIT_INDUSTRIAL`
- `INDUSTRY_REIT_MORTAGE`
- `INDUSTRY_REIT_OFFICE`
- `INDUSTRY_REIT_RESIDENTAL`
- `INDUSTRY_REIT_RETAIL`
- `INDUSTRY_REIT_SPECIALITY`
- `INDUSTRY_REAL_ESTATE_END`
- `INDUSTRY_TECHNOLOGY_FIRST`
- `INDUSTRY_COMPUTER_HARDWARE`
- `INDUSTRY_CONSUMER_ELECTRONICS`
- `INDUSTRY_ELECTRONIC_COMPONENTS`
- `INDUSTRY_ELECTRONIC_DISTRIBUTION`
- `INDUSTRY_IT_SERVICES`
- `INDUSTRY_SCIENTIFIC_INSTRUMENTS`
- `INDUSTRY_SEMICONDUCTOR_EQUIPMENT`
- `INDUSTRY_SEMICONDUCTORS`
- `INDUSTRY_SOFTWARE_APPLICATION`
- `INDUSTRY_SOFTWARE_INFRASTRUCTURE`
- `INDUSTRY_SOLAR`
- `INDUSTRY_TECHNOLOGY_END`
- `INDUSTRY_UTILITIES_FIRST`
- `INDUSTRY_UTILITIES_POWERPRODUCERS`
- `INDUSTRY_UTILITIES_RENEWABLE`
- `INDUSTRY_UTILITIES_REGULATED_ELECTRIC`
- `INDUSTRY_UTILITIES_REGULATED_GAS`
- `INDUSTRY_UTILITIES_REGULATED_WATER`
- `INDUSTRY_UTILITIES_END`
- `INDUSTRY_COMMODITIES_FIRST`
- `INDUSTRY_COMMODITIES_ENERGY`
- `INDUSTRY_COMMODITIES_METALS`
- `INDUSTRY_COMMODITIES_PRECIOUS`
- `INDUSTRY_COMMODITIES_END`

### `EnMTLogCode`

**Allowed values:**

- `MTLogOK`
- `MTLogWarn`
- `MTLogErr`
- `MTLogAtt`
- `MTLogLast`
- `MTLogFirst`

### `EnMTLogFlags`

**Allowed values:**

- `LOG_FLAGS_NONE`
- `LOG_FLAGS_CORRUPTED`

### `EnMTLogRequestMode`

**Allowed values:**

- `MTLogModeStd`
- `MTLogModeErr`
- `MTLogModeFull`

### `EnMTLogType`

**Allowed values:**

- `MTLogTypeFirst`
- `MTLogTypeCfg`
- `MTLogTypeSys`
- `MTLogTypeNet`
- `MTLogTypeHst`
- `MTLogTypeUser`
- `MTLogTypeTrade`
- `MTLogTypeAPI`
- `MTLogTypeNotify`
- `MTLogTypeLiveUpdate`
- `MTLogTypeSendMail`

### `EnMailMode`

**Allowed values:**

- `MAIL_MODE_DISABLED`
- `MAIL_MODE_FULL`

### `EnMarginFlags`

**Allowed values:**

- `MARGIN_FLAGS_NONE`
- `MARGIN_FLAGS_CHECK_PROCESS`
- `MARGIN_FLAGS_CHECK_SLTP`
- `MARGIN_FLAGS_HEDGE_LARGE_LEG`
- `MARGIN_FLAGS_EXCLUDE_PL`
- `MARGIN_FLAGS_ALL`

### `EnMarginFlagsGroup`

**Allowed values:**

- `MARGIN_FLAGS_NONE`
- `MARGIN_FLAGS_CLEAR_ACC`

### `EnMarginMode`

**Allowed values:**

- `MARGIN_MODE_RETAIL`
- `MARGIN_MODE_EXCHANGE_DISCOUNT`
- `MARGIN_MODE_RETAIL_HEDGED`

### `EnNewsFlags`

**Allowed values:**

- `NEWS_FLAGS_NONE`
- `NEWS_FLAGS_PRIORITY`
- `NEWS_FLAGS_READ`
- `NEWS_FLAGS_NOBODY`
- `NEWS_FLAGS_CALENDAR`
- `NEWS_FLAGS_ALL`

### `EnNewsMode`

**Allowed values:**

- `NEWS_MODE_DISABLED`
- `NEWS_MODE_HEADERS`
- `NEWS_MODE_FULL`

### `EnOptionMode`

**Allowed values:**

- `OPTION_MODE_EUROPEAN_CALL`
- `OPTION_MODE_EUROPEAN_PUT`
- `OPTION_MODE_AMERICAN_CALL`
- `OPTION_MODE_AMERICAN_PUT`

### `EnOrderFilling`

**Allowed values:**

- `ORDER_FILL_FOK`
- `ORDER_FILL_IOC`
- `ORDER_FILL_RETURN`
- `ORDER_FILL_BOC`

### `EnOrderFlags`

**Allowed values:**

- `ORDER_FLAGS_NONE`
- `ORDER_FLAGS_MARKET`
- `ORDER_FLAGS_LIMIT`
- `ORDER_FLAGS_STOP`
- `ORDER_FLAGS_STOP_LIMIT`
- `ORDER_FLAGS_SL`
- `ORDER_FLAGS_TP`
- `ORDER_FLAGS_CLOSEBY`
- `ORDER_FLAGS_ALL`

### `EnOrderTime`

**Allowed values:**

- `ORDER_TIME_GTC`
- `ORDER_TIME_DAY`
- `ORDER_TIME_SPECIFIED`
- `ORDER_TIME_SPECIFIED_DAY`

### `EnOrderType`

**Allowed values:**

- `OP_FIRST`
- `OP_SELL`
- `OP_BUY_LIMIT`
- `OP_SELL_LIMIT`
- `OP_BUY_STOP`
- `OP_SELL_STOP`
- `OP_BUY_STOP_LIMIT`
- `OP_SELL_STOP_LIMIT`
- `OP_CLOSE_BY`

### `EnPermissionsFlags`

**Allowed values:**

- `PERMISSION_NONE`
- `PERMISSION_CERT_CONFIRM`
- `PERMISSION_ENABLE_CONNECTION`
- `PERMISSION_RESET_PASSWORD`
- `PERMISSION_FORCED_OTP_USAGE`
- `PERMISSION_RISK_WARNING`
- `PERMISSION_REGULATION_PROTECT`
- `PERMISSION_NOTIFY_DEALS`
- `PERMISSION_NOTIFY_ORDERS`
- `PERMISSION_NOTIFY_BALANCES`
- `PERMISSION_NOTIFY_ALL`
- `PERMISSION_ALL`

### `EnReportsFlags`

**Allowed values:**

- `REPORTSFLAGS_NONE`
- `REPORTSFLAGS_EMAIL`
- `REPORTSFLAGS_SUPPORT`
- `REPORTSFLAGS_STATEMENTS`
- `REPORTSFLAGS_ALL`

### `EnReportsMode`

**Allowed values:**

- `REPORTS_DISABLED`
- `REPORTS_STANDARD`

### `EnSectors`

**Allowed values:**

- `SECTOR_FIRST`
- `SECTOR_BASIC_MATERIALS`
- `SECTOR_COMMUNICATION_SERVICES`
- `SECTOR_CONSUMER_CYCLICAL`
- `SECTOR_CONSUMER_DEFENSIVE`
- `SECTOR_ENERGY`
- `SECTOR_FINANCIAL`
- `SECTOR_HEALTHCARE`
- `SECTOR_INDUSTRIALS`
- `SECTOR_REAL_ESTATE`
- `SECTOR_TECHNOLOGY`
- `SECTOR_UTILITIES`
- `SECTOR_CURRENCY`
- `SECTOR_CURRENCY_CRYPTO`
- `SECTOR_INDEXES`
- `SECTOR_COMMODITIES`

### `EnSoActivation`

**Allowed values:**

- `ACTIVATION_NONE`
- `ACTIVATION_MARGIN_CALL`
- `ACTIVATION_STOP_OUT`

### `EnSpliceTimeType`

**Allowed values:**

- `SPLICE_TIME_FIRST`

### `EnSpliceType`

**Allowed values:**

- `SPLICE_NONE`
- `SPLICE_UNADJUSTED`
- `SPLICE_ADJUSTED`

### `EnStopOutMode`

**Allowed values:**

- `STOPOUT_PERCENT`
- `STOPOUT_MONEY`

### `EnTickFlags`

**Allowed values:**

- `FLAG_TICK_NONE`
- `FLAG_TICK_BUY`
- `FLAG_TICK_SELL`
- `FLAG_TICK_ALL`

### `EnTickFlagsSym`

**Allowed values:**

- `TICK_NONE`
- `TICK_REALTIME`
- `TICK_COLLECTRAW`
- `TICK_FEED_STATS`
- `TICK_NEGATIVE_PRICES`
- `TICK_ALL`

### `EnTickShortFlags`

**Allowed values:**

- `TICK_SHORT_FLAG_NONE`
- `TICK_SHORT_FLAG_RAW`
- `TICK_SHORT_FLAG_BID`
- `TICK_SHORT_FLAG_ASK`
- `TICK_SHORT_FLAG_LAST`
- `TICK_SHORT_FLAG_VOLUME`
- `TICK_SHORT_FLAG_BUY`
- `TICK_SHORT_FLAG_SELL`

### `EnTradeActionFlags`

**Allowed values:**

- `TA_FLAG_NONE`
- `TA_FLAG_CLOSE`
- `TA_FLAG_MARKET`
- `TA_FLAG_CHANGED_PRICE`
- `TA_FLAG_CHANGED_TRIGGER`
- `TA_FLAG_CHANGED_SL`
- `TA_FLAG_CHANGED_TP`
- `TA_FLAG_CHANGED_EXP_TYPE`
- `TA_FLAG_CHANGED_EXP_TIME`
- `TA_FLAG_EXPERT`
- `TA_FLAG_SIGNAL`
- `TA_FLAG_SKIP_MARGIN_CHECK`
- `TA_FLAG_ALL`

### `EnTradeActions`

**Allowed values:**

- `TA_CLIENT_FIRST`
- `TA_REQUEST`
- `TA_INSTANT`
- `TA_MARKET`
- `TA_EXCHANGE`
- `TA_PENDING`
- `TA_SLTP`
- `TA_MODIFY`
- `TA_REMOVE`
- `TA_TRANSFER`
- `TA_CLOSE_BY`
- `TA_SERVER_FIRST`
- `TA_ACTIVATE_SL`
- `TA_ACTIVATE_TP`
- `TA_ACTIVATE_STOPLIMIT`
- `TA_STOPOUT_ORDER`
- `TA_STOPOUT_POSITION`
- `TA_EXPIRATION`
- `TA_DEALER_POS_EXECUTE`
- `TA_DEALER_ORD_PENDING`
- `TA_DEALER_POS_MODIFY`
- `TA_DEALER_ORD_MODIFY`
- `TA_DEALER_ORD_REMOVE`
- `TA_DEALER_ORD_ACTIVATE`
- `TA_DEALER_BALANCE`
- `TA_DEALER_ORD_SLIMIT`
- `TA_LAST`
- `TA_END`

### `EnTradeFlags`

**Allowed values:**

- `TRADE_FLAGS_NONE`
- `TRADE_FLAGS_PROFIT_BY_MARKET`
- `TRADE_FLAGS_ALLOW_SIGNALS`
- `TRADE_FLAGS_ALL`

### `EnTradeFlagsGroup`

**Allowed values:**

- `TRADEFLAGS_NONE`
- `TRADEFLAGS_SWAPS`
- `TRADEFLAGS_TRAILING`
- `TRADEFLAGS_EXPERTS`
- `TRADEFLAGS_EXPIRATION`
- `TRADEFLAGS_SIGNALS_ALL`
- `TRADEFLAGS_DEFAULT`
- `TRADEFLAGS_SIGNALS_OWN`
- `TRADEFLAGS_SO_COMPENSATION`
- `TRADEFLAGS_SO_FULLY_HEDGED`
- `TRADEFLAGS_FIFO_CLOSE`
- `TRADEFLAGS_HEDGE_PROHIBIT`
- `TRADEFLAGS_DEAL_COST`
- `TRADEFLAGS_SO_COMPENSATION_CREDIT`
- `TRADEFLAGS_ALL`

### `EnTradeMode`

**Allowed values:**

- `TRADE_FIRST`
- `TRADE_LONGONLY`
- `TRADE_SHORTONLY`
- `TRADE_CLOSEONLY`
- `TRADE_FULL`

### `EnTransferMode`

**Allowed values:**

- `TRANSFER_MODE_DISABLED`
- `TRANSFER_MODE_NAME`
- `TRANSFER_MODE_GROUP`
- `TRANSFER_MODE_NAME_GROUP`

### `EnUsersConnectionTypes`

**Allowed values:**

- `USER_TYPE_CLIENT`
- `USER_TYPE_CLIENT_WINMOBILE`
- `USER_TYPE_CLIENT_WINPHONE`
- `USER_TYPE_CLIENT_API_WEB`
- `USER_TYPE_CLIENT_IPHONE`
- `USER_TYPE_CLIENT_ANDROID`
- `USER_TYPE_CLIENT_BLACKBERRY`
- `USER_TYPE_CLIENT_WEB`
- `USER_TYPE_ADMIN`
- `USER_TYPE_MANAGER`
- `USER_TYPE_MANAGER_API`
- `USER_TYPE_ADMIN_API`
- `USER_TYPE_MANAGER_API_WEB`

### `EnUsersPasswords`

**Allowed values:**

- `USER_PASS_MAIN`
- `USER_PASS_INVESTOR`
- `USER_PASS_API`

### `EntryFlag`

**Allowed values:**

- `IN`
- `OUT`
- `INOUT`
- `OUT_BY`

### `ExceptionResult`

Result in case of exception(StatusCode == 202)

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | no | Exception message |
| `code` | `MTRetCode` | no |  |
| `stackTrace` | `string` | no | Stack trace |

---

### `ExecutionMode`

**Allowed values:**

- `Request`
- `Instant`
- `Market`
- `Exchange`

### `ExpirationFlags`

**Allowed values:**

- `None`
- `Gtc`
- `Day`
- `Specified`
- `SpecifiedDay`
- `All`

### `FillingFlags`

**Allowed values:**

- `None`
- `Fok`
- `Ioc`
- `All`

### `MarginFlags`

**Allowed values:**

- `None`
- `CheckProcess`
- `CheckSltp`
- `HedgeLargeLeg`
- `ExcludePl`
- `All`

### `MarketWatch`

| Field | Type | Required | Description |
|---|---|---|---|
| `symbol` | `string` | no |  |
| `bid` | `number(double)` | no |  |
| `ask` | `number(double)` | no |  |
| `high` | `number(double)` | no |  |
| `low` | `number(double)` | no |  |
| `spread` | `integer(int32)` | no |  |
| `time` | `string(date-time)` | no |  |

---

### `MemUsage`

| Field | Type | Required | Description |
|---|---|---|---|
| `is64BitProcess` | `boolean` | no |  |
| `physicalMemoryUsage` | `integer(int32)` | no |  |
| `basePriority` | `integer(int32)` | no |  |
| `priorityClass` | `string` | no |  |
| `userProcessorTime` | `string` | no |  |
| `privilegedProcessorTime` | `string` | no |  |
| `totalProcessorTime` | `string` | no |  |
| `pagedSystemMemorySize` | `integer(int32)` | no |  |
| `pagedMemorySize` | `integer(int32)` | no |  |
| `peakPagedMem` | `integer(int32)` | no |  |
| `peakVirtualMem` | `integer(int32)` | no |  |
| `peakWorkingSet` | `integer(int32)` | no |  |
| `memoryLoadBytes` | `integer(int32)` | no |  |
| `heapSizeBytes` | `integer(int32)` | no |  |
| `fragmentedBytes` | `integer(int32)` | no |  |
| `highMemoryLoadThresholdBytes` | `integer(int32)` | no |  |
| `totalAvailableMemoryBytes` | `integer(int32)` | no |  |
| `responding` | `boolean` | no |  |

---

### `News`

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | `integer(int64)` | no |  |
| `subject` | `string` | no |  |
| `category` | `string` | no |  |
| `time` | `integer(int64)` | no |  |
| `language` | `integer(int32)` | no |  |
| `flags` | `EnNewsFlags` | no |  |
| `body` | `string(byte)` | no |  |
| `bodySize` | `integer(int32)` | no |  |

---

### `Online`

| Field | Type | Required | Description |
|---|---|---|---|
| `sessionID` | `integer(int64)` | no |  |
| `login` | `integer(int64)` | no |  |
| `group` | `string` | no |  |
| `address` | `string` | no |  |
| `type` | `EnUsersConnectionTypes` | no |  |
| `build` | `integer(int32)` | no |  |
| `time` | `integer(int64)` | no |  |
| `computerID` | `string` | no |  |

---

### `PermissionsFlags`

**Allowed values:**

- `None`
- `Book`

### `ProfitUpdateOrder`

ProfitUpdate order parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `ticket` | `integer(int64)` | no | Ticket |
| `profit` | `number(double)` | no | Profit |

---

### `REFlags`

**Allowed values:**

- `None`
- `Order`

### `Request`

| Field | Type | Required | Description |
|---|---|---|---|
| `apiDataClearAll` | `MTRetCode` | no |  |
| `volumeCurrent` | `integer(int64)` | no |  |
| `volumeCurrentExt` | `integer(int64)` | no |  |
| `symbolOriginal` | `string` | no |  |
| `print` | `string` | no |  |
| `id` | `integer(int32)` | no |  |
| `login` | `integer(int64)` | no |  |
| `group` | `string` | no |  |
| `symbol` | `string` | no |  |
| `digits` | `integer(int32)` | no |  |
| `action` | `EnTradeActions` | no |  |
| `timeExpiration` | `integer(int64)` | no |  |
| `type` | `EnOrderType` | no |  |
| `typeFill` | `EnOrderFilling` | no |  |
| `typeTime` | `EnOrderTime` | no |  |
| `flags` | `EnTradeActionFlags` | no |  |
| `volume` | `integer(int64)` | no |  |
| `order` | `integer(int64)` | no |  |
| `orderExternalID` | `string` | no |  |
| `priceOrder` | `number(double)` | no |  |
| `priceTrigger` | `number(double)` | no |  |
| `priceSL` | `number(double)` | no |  |
| `priceTP` | `number(double)` | no |  |
| `priceDeviation` | `integer(int64)` | no |  |
| `priceDeviationTop` | `number(double)` | no |  |
| `priceDeviationBottom` | `number(double)` | no |  |
| `comment` | `string` | no |  |
| `resultRetcode` | `MTRetCode` | no |  |
| `resultDealer` | `integer(int64)` | no |  |
| `resultDeal` | `integer(int64)` | no |  |
| `resultOrder` | `integer(int64)` | no |  |
| `resultVolume` | `integer(int64)` | no |  |
| `resultPrice` | `number(double)` | no |  |
| `resultDealerBid` | `number(double)` | no |  |
| `resultDealerAsk` | `number(double)` | no |  |
| `resultDealerLast` | `number(double)` | no |  |
| `resultMarketBid` | `number(double)` | no |  |
| `resultMarketAsk` | `number(double)` | no |  |
| `resultMarketLast` | `number(double)` | no |  |
| `resultComment` | `string` | no |  |
| `externalAccount` | `string` | no |  |
| `idClient` | `integer(int32)` | no |  |
| `ip` | `string` | no |  |
| `sourceLogin` | `integer(int64)` | no |  |
| `position` | `integer(int64)` | no |  |
| `positionBy` | `integer(int64)` | no |  |
| `positionExternalID` | `string` | no |  |
| `positionByExternalID` | `string` | no |  |
| `volumeExt` | `integer(int64)` | no |  |
| `resultVolumeExt` | `integer(int64)` | no |  |

---

### `RequestUpdate`

| Field | Type | Required | Description |
|---|---|---|---|
| `action` | `RequestUpdateAction` | no |  |
| `request` | `Request` | no |  |

---

### `RequestUpdateAction`

**Allowed values:**

- `Add`
- `Update`
- `Delete`

### `SegregatedRow`

| Field | Type | Required | Description |
|---|---|---|---|
| `login` | `integer(int64)` | no |  |
| `name` | `string` | no |  |
| `deposit` | `number(double)` | no |  |
| `credit` | `number(double)` | no |  |
| `commission` | `number(double)` | no |  |
| `swap` | `number(double)` | no |  |
| `profit` | `number(double)` | no |  |
| `interest` | `number(double)` | no |  |
| `balance` | `number(double)` | no |  |
| `floatingPL` | `number(double)` | no |  |
| `equity` | `number(double)` | no |  |
| `currency` | `string` | no |  |

---

### `SessionState`

True or false for current symbol for now

| Field | Type | Required | Description |
|---|---|---|---|
| `symbol` | `string` | no | Symbol |
| `active` | `boolean` | no | Active or not |

---

### `Summary`

| Field | Type | Required | Description |
|---|---|---|---|
| `symbol` | `string` | no |  |
| `digits` | `integer(int32)` | no |  |
| `positionClients` | `integer(int32)` | no |  |
| `positionCoverage` | `integer(int32)` | no |  |
| `volumeBuyClients` | `integer(int64)` | no |  |
| `volumeBuyCoverage` | `integer(int64)` | no |  |
| `volumeSellClients` | `integer(int64)` | no |  |
| `volumeSellCoverage` | `integer(int64)` | no |  |
| `volumeNet` | `number(double)` | no |  |
| `priceBuyClients` | `number(double)` | no |  |
| `priceBuyCoverage` | `number(double)` | no |  |
| `priceSellClients` | `number(double)` | no |  |
| `priceSellCoverage` | `number(double)` | no |  |
| `profitClients` | `number(double)` | no |  |
| `profitCoverage` | `number(double)` | no |  |
| `profitFullClients` | `number(double)` | no |  |
| `profitFullCoverage` | `number(double)` | no |  |
| `profitUncovered` | `number(double)` | no |  |
| `profitUncoveredFull` | `number(double)` | no |  |
| `volumeBuyClientsExt` | `integer(int64)` | no |  |
| `volumeBuyCoverageExt` | `integer(int64)` | no |  |
| `volumeSellClientsExt` | `integer(int64)` | no |  |
| `volumeSellCoverageExt` | `integer(int64)` | no |  |

---

### `SwapMode`

**Allowed values:**

- `Disabled`
- `ByPoints`
- `BySymbolCurrency`
- `ByMarginCurrency`
- `ByGroupCurrency`
- `ByInterestCurrent`
- `ByInterestOpen`
- `ReopenByClosePrice`
- `ReopenByBid`
- `ByProfitCurrency`

### `TradeActivationFlags`

**Allowed values:**

- `NONE`
- `FLAGS_NO_LIMIT`
- `NO_STOP`
- `NO_SLIMIT`
- `NO_SL`
- `NO_TP`
- `NO_SO`
- `NO_EXPIRATION`
- `ALL`

### `TradeMode`

**Allowed values:**

- `Disabled`
- `Longonly`
- `Shortonly`
- `Closeonly`
- `Full`

### `TradeRecord`

Order in MT4 format

| Field | Type | Required | Description |
|---|---|---|---|
| `order` | `integer(int64)` | no | Order ticket |
| `login` | `integer(int64)` | no | Owner's login |
| `symbol` | `string` | no | Security |
| `digits` | `integer(int32)` | no | Security precision |
| `cmd` | `OrderType` | no |  |
| `volume` | `integer(int32)` | no | Volume |
| `openTime` | `string(date-time)` | no | Open time |
| `state` | `integer(int32)` | no | Reserved |
| `openPrice` | `number(double)` | no | Open price |
| `sl` | `number(double)` | no |  |
| `tp` | `number(double)` | no |  |
| `closeTime` | `string(date-time)` | no | Close time |
| `gwVolume` | `integer(int32)` | no | Gateway order volume |
| `expiration` | `string(date-time)` | no | Pending order's expiration time |
| `reason` | `OrderReason` | no |  |
| `convReserv` | `string` | no | Reserved fields |
| `convRates` | `array<number>` | no | Convertation rates from profit currency to group deposit currency |
| `commission` | `number(double)` | no | Commission |
| `commissionAgent` | `number(double)` | no | Agent commission |
| `storage` | `number(double)` | no | Order swaps |
| `closePrice` | `number(double)` | no | Close price |
| `profit` | `number(double)` | no | Profit |
| `taxes` | `number(double)` | no | Taxes |
| `magic` | `integer(int64)` | no | Special value used by client experts |
| `comment` | `string` | no | Comment |
| `gwOrder` | `integer(int32)` | no | Gateway order ticket |
| `activation` | `integer(int32)` | no | Used by MT Manager |
| `gwOpenPrice` | `integer(int32)` | no | Gateway order price deviation (pips) from order open price |
| `gwClosePrice` | `integer(int32)` | no | Gateway order price deviation (pips) from order close price |
| `marginRate` | `number(double)` | no | Margin convertation rate (rate of convertation from margin currency to deposit one) |
| `timestamp` | `string(date-time)` | no | Timestamp |
| `apiData` | `array<integer>` | no | For api usage |
| `action` | `DealAction` | no |  |
| `deals` | `array<Deal>` | no | Position deals |
| `lots` | `number(double)` | no | Lots |

---

### `TradeResult`

| Field | Type | Required | Description |
|---|---|---|---|
| `answer` | `Request` | no |  |
| `result` | `Confirm` | no |  |

---

### `WeekSessions`

| Field | Type | Required | Description |
|---|---|---|---|
| `sunday` | `array<ConSymbolSession>` | no |  |
| `monday` | `array<ConSymbolSession>` | no |  |
| `tuesday` | `array<ConSymbolSession>` | no |  |
| `wednesday` | `array<ConSymbolSession>` | no |  |
| `thursday` | `array<ConSymbolSession>` | no |  |
| `friday` | `array<ConSymbolSession>` | no |  |
| `saturday` | `array<ConSymbolSession>` | no |  |

---
