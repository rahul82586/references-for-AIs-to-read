# 📁 Return-Codes

- **Generated:** 2026-09-09 00:12
- **Total Files:** 14
- **Source:** `C:\Users\DELL\Downloads\server3\mt5_doc_dump\Documentation\MQ_Docs\Metatrader 5\MetaTrader5SDK\Return-Codes`

---

## 📑 Table of Contents

1. [API.md](#api-md)
2. [Authentication.md](#authentication-md)
3. [Common-errors.md](#common-errors-md)
4. [Configuration-Management.md](#configuration-management-md)
5. [Dealer.md](#dealer-md)
6. [Messengers.md](#messengers-md)
7. [Price-Data.md](#price-data-md)
8. [README.md](#readme-md)
9. [Report-Generation.md](#report-generation-md)
10. [Subscriptions.md](#subscriptions-md)
11. [Successful-completion.md](#successful-completion-md)
12. [Trade-Requests.md](#trade-requests-md)
13. [Trade-management.md](#trade-management-md)
14. [User-management.md](#user-management-md)

---

## 🌲 Project Structure

```
Return-Codes/
├── API.md
├── Authentication.md
├── Common-errors.md
├── Configuration-Management.md
├── Dealer.md
├── images/
│   ├── next.png
│   ├── next_1.png
│   ├── next_10.png
│   ├── next_11.png
│   ├── next_12.png
│   ├── next_13.png
│   ├── next_2.png
│   ├── next_3.png
│   ├── next_4.png
│   ├── next_5.png
│   ├── next_6.png
│   ├── next_7.png
│   ├── next_8.png
│   ├── next_9.png
│   ├── previous.png
│   ├── previous_1.png
│   ├── previous_10.png
│   ├── previous_11.png
│   ├── previous_12.png
│   ├── previous_13.png
│   ├── previous_2.png
│   ├── previous_3.png
│   ├── previous_4.png
│   ├── previous_5.png
│   ├── previous_6.png
│   ├── previous_7.png
│   ├── previous_8.png
│   └── previous_9.png
├── Messengers.md
├── Price-Data.md
├── README.md
├── Report-Generation.md
├── Subscriptions.md
├── Successful-completion.md
├── Trade-management.md
├── Trade-Requests.md
└── User-management.md
```

---

## 📄 Files

<a id='api-md'></a>
### 14. `API.md`

```markdown
[🏠 Document Start](../README.md) / [Return Codes](README.md) / API

[Previous](Dealer.md) | [Next](Messengers.md)

# API

This group of codes is returned by the server when working through the API:

Constant | Value | Description  
MT_RET_ERR_NOTIMPLEMENT | 12000 | Not yet implemented.  
MT_RET_ERR_NOTMAIN | 12001 | The operation should be performed on the main trading server.  
MT_RET_ERR_NOTSUPPORTED | 12002 | The command is not supported by this server.  
MT_RET_ERR_DEADLOCK | 12003 | The operation has been canceled due to a possible deadlock.  
MT_RET_ERR_LOCKED | 12004 | Working with a blocked object.

```

---

<a id='authentication-md'></a>
### 14. `Authentication.md`

```markdown
[🏠 Document Start](../README.md) / [Return Codes](README.md) / Authentication

[Previous](Common-errors.md) | [Next](Configuration-Management.md)

# Authentication

This group of codes is returned by the server during the authentication of users:

Constant | Value | Description  
MT_RET_AUTH_CLIENT_INVALID | 1000 | Invalid type of the terminal.  
MT_RET_AUTH_ACCOUNT_INVALID | 1001 | Invalid account.  
MT_RET_AUTH_ACCOUNT_DISABLED | 1002 | The account is disabled.  
MT_RET_AUTH_ADVANCED | 1003 | Extended authorization required.  
MT_RET_AUTH_CERTIFICATE | 1004 | Certificate required.  
MT_RET_AUTH_CERTIFICATE_BAD | 1005 | Invalid certificate.  
MT_RET_AUTH_NOTCONFIRMED | 1006 | The certificate is not confirmed.  
MT_RET_AUTH_SERVER_INTERNAL | 1007 | An attempt to connect to a server, which is not an access server.  
MT_RET_AUTH_SERVER_BAD | 1008 | Server is not authenticated.  
MT_RET_AUTH_UPDATE_ONLY | 1009 | Only update is available.  
MT_RET_AUTH_CLIENT_OLD | 1010 | Old client version.  
MT_RET_AUTH_MANAGER_NOCONFIG | 1011 | An appropriate manager configuration hasn't been created for the manager account.  
MT_RET_AUTH_MANAGER_IPBLOCK | 1012 | IP-address is not valid for the manager.  
MT_RET_AUTH_GROUP_INVALID | 1013 | The group is not initialized (you must restart the server).  
MT_RET_AUTH_CA_DISABLED | 1014 | Generation of certificates is disabled.  
MT_RET_AUTH_INVALID_ID | 1015 | Invalid ID or the server is disabled (the server ID should be checked).  
MT_RET_AUTH_INVALID_IP | 1016 | Invalid address (the server IP-address should be checked).  
MT_RET_AUTH_INVALID_TYPE | 1017 | Wrong type of server (server ID and type should be checked).  
MT_RET_AUTH_SERVER_BUSY | 1018 | The server is busy.  
MT_RET_AUTH_SERVER_CERT | 1019 | Invalid server certificate.  
MT_RET_AUTH_ACCOUNT_UNKNOWN | 1020 | Unknown account.  
MT_RET_AUTH_SERVER_OLD | 1021 | Outdated server version.  
MT_RET_AUTH_SERVER_LIMIT | 1022 | The server cannot be connected because of the license restrictions.  
MT_RET_AUTH_MOBILE_DISABLED | 1023 | Connections of mobile devices are not allowed in the license.  
MT_RET_AUTH_MANAGER_TYPE | 1024 | This type of connection is not permitted for manager.  
MT_RET_AUTH_DEMO_DISABLED | 1025 | Creation of demo accounts is disabled.  
MT_RET_AUTH_RESET_PASSWORD | 1026 | Master password must be changed.  
MT_RET_AUTH_OTP_INVALID | 1027 | Invalid [one-time password](https://support.metaquotes.net/en/docs/mt5/platform/administrator/getting_started/server_connect/otp).  
MT_RET_AUTH_OTP_NEED_SECRET | 1028 | No [secret key (#security)](https://support.metaquotes.net/en/docs/mt5/platform/administration/admin_accounts/account_edit#security) is specified for the one-time password.  
MT_RET_AUTH_MIGRATION_MT4 | 1029 | Password change is required after account import from the MetaTrader 4 server.  
MT_RET_AUTH_MIGRATION_MT5 | 1030 | Password change is required after account import from the MetaTrader 5 server.  
MT_RET_AUTH_INVALID_VERIFY | 1031 | Invalid or expired verification code.  
MT_RET_AUTH_VERIFY_BAD_EMAIL | 1032 | Unable to send email verification code.  
MT_RET_AUTH_VERIFY_BAD_PHONE | 1033 | Unable to send phone number verification code.  
MT_RET_AUTH_API_DISABLED | 1034 | Connection via the API is prohibited for the account ([IMTUser::USER_RIGHT_API_ENABLED (#enusersrights)](../Database-Interfaces/Users/IMTUser/Enumerations.md#enusersrights)).

```

---

<a id='common-errors-md'></a>
### 14. `Common-errors.md`

```markdown
[🏠 Document Start](../README.md) / [Return Codes](README.md) / Common errors

[Previous](Successful-completion.md) | [Next](Authentication.md)

# Common errors

These codes are returned by the server when common errors occur:

Constant | Value | Description  
MT_RET_ERROR | 2 | Common error.  
MT_RET_ERR_PARAMS | 3 | Invalid parameters.  
MT_RET_ERR_DATA | 4  | Invalid information.  
MT_RET_ERR_DISK | 5 | Hard disk error.  
MT_RET_ERR_MEM | 6 | Memory error.  
MT_RET_ERR_NETWORK | 7 | Network error.  
MT_RET_ERR_PERMISSIONS | 8 | Not enough permissions to perform the operation.  
MT_RET_ERR_TIMEOUT | 9 | Timeout expired.  
MT_RET_ERR_CONNECTION | 10 | No connection.  
MT_RET_ERR_NOSERVICE | 11 | Service is not available.  
MT_RET_ERR_FREQUENT | 12 | Too frequent requests.  
MT_RET_ERR_NOTFOUND | 13 | Not found.  
MT_RET_ERR_PARTIAL | 14 | Partial error.  
MT_RET_ERR_SHUTDOWN | 15 | Server shutdown in progress.  
MT_RET_ERR_CANCEL | 16 | The operation has been canceled.  
MT_RET_ERR_DUPLICATE | 17 | Duplicate information.

```

---

<a id='configuration-management-md'></a>
### 14. `Configuration-Management.md`

```markdown
[🏠 Document Start](../README.md) / [Return Codes](README.md) / Configuration Management

[Previous](Authentication.md) | [Next](User-management.md)

# Configuration Management

This group of codes is returned by the server in case [configurations](../Manager-API/Administrator-Interface/Configuration-Databases.md) are changed:

Constant | Value | Description  
MT_RET_CFG_LAST_ADMIN | 2000 | Deleting the last administrator configuration.  
MT_RET_CFG_LAST_ADMIN_GROUP | 2001 | The last group of administrators cannot be deleted.  
MT_RET_CFG_NOT_EMPTY | 2003 | The group contains accounts or trade operations.  
MT_RET_CFG_INVALID_RANGE | 2004 | Invalid range of accounts or trade operations.  
MT_RET_CFG_NOT_MANAGER_LOGIN | 2005 | The manager account does not belong to the manager group.  
MT_RET_CFG_BUILTIN | 2006 | Built-in protected configuration.  
MT_RET_CFG_DUPLICATE | 2007 | Duplicate configuration.  
MT_RET_CFG_LIMIT_REACHED | 2008 | Reached limit on the number of configurations.  
MT_RET_CFG_NO_ACCESS_TO_MAIN | 2009 | Incorrect network configuration.  
MT_RET_CFG_DEALER_ID_EXIST | 2010 | A dealer with the same ID (account number) already exists.  
MT_RET_CFG_BIND_ADDR_EXIST | 2011 | Connection address already exists.  
MT_RET_CFG_WORKING_TRADE | 2012 | An attempt to delete a working trade server.  
MT_RET_CFG_GATEWAY_NAME_EXIST | 2013 | Gateway with that name already exists.  
MT_RET_CFG_SWITCH_TO_BACKUP | 2014 | Switch to a backup server has been initiated for the Trade/History server.  
MT_RET_CFG_NO_BACKUP_MODULE | 2015 | No backup server.  
MT_RET_CFG_NO_TRADE_MODULE | 2016 | No trade server.  
MT_RET_CFG_NO_HISTORY_MODULE | 2017 | Ho history server.  
MT_RET_CFG_ANOTHER_SWITCH | 2018 | The process of switching to a backup server has already started.  
MT_RET_CFG_NO_LICENSE_FILE | 2019 | No license file.  
MT_RET_CFG_GATEWAY_LOGIN_EXIST | 2020 | Creating a manager configuration is not possible, because the login is already used by the gateway.  
MT_RET_CFG_INVALID_COMPANY | 2021 | The company name does not correspond to the license or White Label. The error is returned when you try to add or save a group with the [company name](../Configuration-Interfaces/Groups/IMTConGroup/Company.md) different from the one specified in the platform license as the main or additional White Label.

```

---

<a id='dealer-md'></a>
### 14. `Dealer.md`

```markdown
[🏠 Document Start](../README.md) / [Return Codes](README.md) / Dealer

[Previous](Trade-Requests.md) | [Next](API.md)

# Dealer

This group of codes is returned by the server during dealer's actions:

Constant | Value | Description  
MT_RET_REQUEST_RETURN | 11000 | Request returned to the queue.  
MT_RET_REQUEST_DONE_CANCEL | 11001 | Request has been partially filled, the remainder has been canceled.  
MT_RET_REQUEST_REQUOTE_RETURN | 11002 | The request has been requoted and returned to the queue with new prices.

```

---

<a id='messengers-md'></a>
### 14. `Messengers.md`

```markdown
[🏠 Document Start](../README.md) / [Return Codes](README.md) / Messengers

[Previous](API.md) | [Next](Subscriptions.md)

# Instant messengers

The server returns codes from this group when sending messages via instant messengers.

Constant | Value | Description  
MT_RET_MESSENGER_INVALID_PHONE | 14000 | An invalid phone number is specified. The number must be specified in the format +[country code][number], for example: +74951113594. The should be specified without spaces.  
MT_RET_MESSENGER_NOT_MOBILE | 14001 | A landline phone number is specified instead of a mobile one. Mobile phone numbers must be specified when sending messages. Messages cannot be delivered to other phone numbers.  
  
The codes are used for the following methods:

  * [IMTServerAPI::MessengerSend](../Server-API/Main-API-Interface/Configuration-Databases/Messengers/MessengerSend.md)
  * [IMTAdminAPI::MessengerSend](../Manager-API/Administrator-Interface/Configuration-Databases/Messengers/MessengerSend.md)
  * [IMTManagerAPI::MessengerSend](../Manager-API/Manager-Interface/Users/MessengerSend.md)
  * [/messenger_send](../Web-API/Manager-Interface-(Rest-API)/Configuration-Databases/Messengers/Send-Message.md)



```

---

<a id='price-data-md'></a>
### 14. `Price-Data.md`

```markdown
[🏠 Document Start](../README.md) / [Return Codes](README.md) / Price Data

[Previous](Report-Generation.md) | [Next](Trade-Requests.md)

# Price Data

This group of codes is returned by the server when working with [price data](../Database-Interfaces/Price-Data.md):

Constant | Value | Description  
MT_RET_HST_SYMBOL_NOTFOUND | 6001 | Symbol not found, try to restart the history server.

```

---

<a id='readme-md'></a>
### 14. `README.md`

```markdown
[🏠 Document Start](../README.md) / Return Codes

[Previous](../Journal-Constants/README.md) | [Next](Successful-completion.md)

# Return Codes

The vast majority of functions in the MetaTrader 5 API return a special code to notify of the results of their implementation To develop high-quality, stable applications, a programmer should check the return codes of functions of called API methods.

Return codes are contained in the EnMTAPIRetcode enumeration, in file MT5APIConstants.h and are divided into several groups:

Group of codes | Range of values | Description  
[Successful completion](Successful-completion.md) | 0-1 | Codes that are returned with the successful completion of an operation.  
[Common errors](Common-errors.md) | 2-999 | Codes returned when common errors occur.  
[Authentication](Authentication.md) | 1000-1999 | Codes returned during the authentication of users.  
[Configuration management](Configuration-Management.md) | 2000-2999 | Codes that are returned when changing configurations.  
[User management](User-management.md) | 3000-3999 | The codes returned when working with the database of users.  
[Trade management](Trade-management.md) | 4000-4999 | The codes returned when working with the trading database.  
[Report Generation](Report-Generation.md) | 5000-5999 | Codes that are returned when generating reports.  
[Price Data](Price-Data.md) | 6000-6999 | Codes that are returned when working with price data.  
[Trade Requests](Trade-Requests.md) | 10000-10999 | Codes returned while processing trade requests.  
[Dealer](Dealer.md) | 11000-11999 | Codes returned during the work of a dealer.  
[API](API.md) | 12000-12999 | Codes related to the operation of API.  
[Instant messengers](Messengers.md) | 14000-14999 | Codes related to message sending via instant messengers.  
[Subscriptions](Subscriptions.md) | 15000-15999 | Codes related to the operation of the [Subscriptions](https://support.metaquotes.net/en/docs/mt5/platform/administration/subscriptions) service.

```

---

<a id='report-generation-md'></a>
### 14. `Report-Generation.md`

```markdown
[🏠 Document Start](../README.md) / [Return Codes](README.md) / Report Generation

[Previous](Trade-management.md) | [Next](Price-Data.md)

# Report Generation

This group of codes is returned by the server during generation of reports:

Constant | Value | Description  
MT_RET_REPORT_SNAPSHOT | 5001 | Database snapshot error.  
MT_RET_REPORT_NOTSUPPORTED | 5002 | The method is not supported for this report.  
MT_RET_REPORT_NODATA | 5003 | No information for the report.  
MT_RET_REPORT_TEMPLATE_BAD | 5004 | Wrong template.  
MT_RET_REPORT_TEMPLATE_END | 5005 | The end of the template.  
MT_RET_REPORT_INVALID_ROW | 5006 | Invalid row size.  
MT_RET_REPORT_LIMIT_REPEAT | 5007 | Reached the limit of the number of duplicate tags.  
MT_RET_REPORT_LIMIT_REPORT | 5008 | Reached the limit of the report size.

```

---

<a id='subscriptions-md'></a>
### 14. `Subscriptions.md`

```markdown
[🏠 Document Start](../README.md) / [Return Codes](README.md) / Subscriptions

[Previous](Messengers.md) | [Next](../Structures/README.md)

# Subscriptions

This group of codes is returned by the server when working with [subscription configurations](../Configuration-Interfaces/Subscriptions.md) and [databases](../Database-Interfaces/Subscriptions.md):

Constant | Value | Description  
MT_RET_SUBS_NOT_FOUND | 15000 | [Subscription](../Database-Interfaces/Subscriptions/IMTSubscription.md) not found.  
MT_RET_SUBS_NOT_FOUND_CFG | 15001 | [Subscription configuration](../Configuration-Interfaces/Subscriptions/IMTConSubscription.md) not found.  
MT_RET_SUBS_NOT_FOUND_USER | 15002 | User from subscription not found.  
MT_RET_SUBS_DISABLED | 15003 | Subscription disabled. The current status can be obtained via [IMTSubscription::Status](../Database-Interfaces/Subscriptions/IMTSubscription/Status.md).  
MT_RET_SUBS_PERMISSION_USER | 15004 | Subscription not allowed for the user.  
MT_RET_SUBS_PERMISSION_SUBSCRIBE | 15005 | Subscription not allowed. The availability of a subscription option is determined by the [IMTConSubscription::ControlMode](../Configuration-Interfaces/Subscriptions/IMTConSubscription/ControlMode.md) property.  
MT_RET_SUBS_PERMISSION_UNSUBSCRIBE | 15006 | Unsubscribing not allowed. The ability to unsubscribe is determined by the [IMTConSubscription::ControlMode](../Configuration-Interfaces/Subscriptions/IMTConSubscription/ControlMode.md) property.  
MT_RET_SUBS_REAL_ONLY | 15007 | Subscription only allowed for real accounts.

```

---

<a id='successful-completion-md'></a>
### 14. `Successful-completion.md`

```markdown
[🏠 Document Start](../README.md) / [Return Codes](README.md) / Successful completion

[Previous](README.md) | [Next](Common-errors.md)

# Successful completion

These codes indicate successful operation:

Constant | Value | Description  
MT_RET_OK | 0 | Successful completion.  
MT_RET_OK_NONE | 1 | Successful completion with no information returned.

```

---

<a id='trade-requests-md'></a>
### 14. `Trade-Requests.md`

```markdown
[🏠 Document Start](../README.md) / [Return Codes](README.md) / Trade Requests

[Previous](Price-Data.md) | [Next](Dealer.md)

# Trade Requests

These codes are returned by the server during operations with [trade requests](../Manager-API/Administrator-Interface/Trade-Databases.md):

Constant | Value | Description  
MT_RET_REQUEST_INWAY | 10001 | Request is on the way.  
MT_RET_REQUEST_ACCEPTED | 10002 | Request accepted.  
MT_RET_REQUEST_PROCESS | 10003 | Request processed.  
MT_RET_REQUEST_REQUOTE | 10004 | Requote in response to the request.  
MT_RET_REQUEST_PRICES | 10005 | Prices in response to the request.  
MT_RET_REQUEST_REJECT | 10006 | Request rejected.  
MT_RET_REQUEST_CANCEL | 10007 | Request canceled.  
MT_RET_REQUEST_PLACED | 10008 | An order placed as a result of the request.  
MT_RET_REQUEST_DONE | 10009 | Request fulfilled.  
MT_RET_REQUEST_DONE_PARTIAL | 10010 | Request partially fulfilled.  
MT_RET_REQUEST_ERROR | 10011 | Common error of request.  
MT_RET_REQUEST_TIMEOUT | 10012 | Request timed out.  
MT_RET_REQUEST_INVALID | 10013 | Invalid request.  
MT_RET_REQUEST_INVALID_VOLUME | 10014 | Invalid volume.  
MT_RET_REQUEST_INVALID_PRICE | 10015 | Invalid price.  
MT_RET_REQUEST_INVALID_STOPS | 10016 | Wrong stop levels or price.  
MT_RET_REQUEST_TRADE_DISABLED | 10017 | Trade is disabled.  
MT_RET_REQUEST_MARKET_CLOSED | 10018 | Market is closed.  
MT_RET_REQUEST_NO_MONEY | 10019 | Not enough money.  
MT_RET_REQUEST_PRICE_CHANGED | 10020 | Price has changed.  
MT_RET_REQUEST_PRICE_OFF | 10021 | No price.  
MT_RET_REQUEST_INVALID_EXP | 10022 | Invalid order expiration.  
MT_RET_REQUEST_ORDER_CHANGED | 10023 | Order has been changed.  
MT_RET_REQUEST_TOO_MANY | 10024 | Too many trade requests. For example, this error can be returned in response to an attempt to send more than 128 trade requests from one Manager API instance.  
MT_RET_REQUEST_NO_CHANGES | 10025 | Request does not contain changes.  
MT_RET_REQUEST_AT_DISABLED_SERVER | 10026 | Autotrading disabled on the server.  
MT_RET_REQUEST_AT_DISABLED_CLIENT | 10027 | Autotrading disabled on the client side.  
MT_RET_REQUEST_LOCKED | 10028 | Request blocked by the dealer.  
MT_RET_REQUEST_FROZEN | 10029 | Modification failed due to order or position being close to market.  
MT_RET_REQUEST_INVALID_FILL | 10030 | Fill mode is not supported.  
MT_RET_REQUEST_CONNECTION | 10031 | No connection.  
MT_RET_REQUEST_ONLY_REAL | 10032 | Allowed only for real accounts.  
MT_RET_REQUEST_LIMIT_ORDERS | 10033 | Reached the limit on the number of orders.  
MT_RET_REQUEST_LIMIT_VOLUME | 10034 | Reached the volume limit.  
MT_RET_REQUEST_INVALID_ORDER | 10035 | Invalid or prohibited order type.  
MT_RET_REQUEST_POSITION_CLOSED | 10036 | Position is already closed. For example, this error appears when attempting to modify the stop levels of an already closed position.  
MT_RET_REQUEST_EXECUTION_SKIPPED | 10037 | Used for internal purposes.  
MT_RET_REQUEST_INVALID_CLOSE_VOLUME | 10038 | Volume to be closed exceeds the current volume of the position.  
MT_RET_REQUEST_CLOSE_ORDER_EXIST | 10039 | Order to close the position already exists. The error may appear in the hedging mode:

  * when trying to closed a position with an opposite one in case there's already an order to close that position
  * when trying to close the entire position or a part of it in case the total volume of existing orders to close it and the newly placed order exceeds the current volume of the position

  
MT_RET_REQUEST_LIMIT_POSITIONS | 10040 | The number of open positions simultaneously present on an account can be limited by the settings of a group. After a limit is reached, the server returns the MT_TRADE_RETCODE_REQUEST_LIMIT_POSITIONS error when attempting to place an order. The limitation operates differently depending on the position accounting type:

  * Netting — number of open positions is considered. When a limit is reached, the platform disables placing new orders whose execution may increase the number of open positions. In fact, the platform allows placing orders only for the symbols that already have open positions. The current pending orders are not considered since their execution may lead to changes in the current positions but it cannot increase their number.
  * Hedging — pending orders are considered together with open positions, since a pending order activation always leads to opening a new position. When a limit is reached, the platform disables placing both new market orders for opening positions and pending orders.

  
MT_RET_REQUEST_REJECT_CANCEL | 10041 | Request rejected, order canceled. This code is returned when the action [IMTConRoute::ACTION_CANCEL_ORDER (#enrouteaction)](../Configuration-Interfaces/Routing/IMTConRoute/Enumerations.md#enrouteaction) in a routing rule is applied.  
MT_RET_REQUEST_LONG_ONLY | 10042 | The request is rejected, because the "Only long positions are allowed" rule is set for the symbol ([IMTConSymbol::TRADE_LONGONLY (#entrademode)](../Configuration-Interfaces/Symbols/IMTConSymbol/Enumerations.md#entrademode)).  
MT_RET_REQUEST_SHORT_ONLY | 10043 | The request is rejected, because the "Only short positions are allowed" rule is set for the symbol ([IMTConSymbol::TRADE_SHORTONLY (#entrademode)](../Configuration-Interfaces/Symbols/IMTConSymbol/Enumerations.md#entrademode)).  
MT_RET_REQUEST_CLOSE_ONLY | 10044 | The request is rejected, because the "Only position closing is allowed" rule is set for the symbol ([IMTConSymbol::TRADE_CLOSEONLY (#entrademode)](../Configuration-Interfaces/Symbols/IMTConSymbol/Enumerations.md#entrademode)).  
MT_RET_REQUEST_PROHIBITED_BY_FIFO | 10045 | Position closure is not allowed by the FIFO rule. It is used for the groups with the enabled [IMTConGroup::TRADEFLAGS_FIFO_CLOSE (#entradeflags)](../Configuration-Interfaces/Groups/IMTConGroup/Enumerations.md#entradeflags) option, according to which all positions should be closed strictly in the order in which they were opened: the oldest one should be closed first, then the next one, etc.  
MT_RET_REQUEST_HEDGE_PROHIBITED | 10046 | Opening of a position or placing of a pending order is not possible because hedge positions are prohibited. The error is returned if a user tries to execute a trading operation in the case the [IMTConGroup::TRADEFLAGS_HEDGE_PROHIBIT (#entradeflags)](../Configuration-Interfaces/Groups/IMTConGroup/Enumerations.md#entradeflags) flag is enabled for the group and the user already has an opposite order or position for the same symbol.

```

---

<a id='trade-management-md'></a>
### 14. `Trade-management.md`

```markdown
[🏠 Document Start](../README.md) / [Return Codes](README.md) / Trade management

[Previous](User-management.md) | [Next](Report-Generation.md)

# Trade management

This group of codes is returned by the server when working with [a database of trades](../Manager-API/Administrator-Interface/Trade-Databases.md):

Constant | Value | Description  
MT_RET_TRADE_LIMIT_REACHED | 4001 | Reached the limit on the number of orders or deals.  
MT_RET_TRADE_ORDER_EXIST | 4002 | The order already exists.  
MT_RET_TRADE_ORDER_EXHAUSTED | 4003 | The range of orders has been exhausted.  
MT_RET_TRADE_DEAL_EXHAUSTED | 4004 | The range of deals has been exhausted.  
MT_RET_TRADE_MAX_MONEY | 4005 | Reached the limit on the amount of money.  
MT_RET_TRADE_DEAL_EXIST | 4006 | A deal with this ticket already exists on this trade server.  
MT_RET_TRADE_ORDER_PROHIBITED | 4007 | The order identifier is reserved for use on another trade server.  
MT_RET_TRADE_DEAL_PROHIBITED | 4008 | The deal identifier is reserved for use on another trade server.  
MT_RET_TRADE_SPLIT_VOLUME | 4009 | The position volume will become zero after the split operation. The error is used in the following methods:

  * [IMTServerAPI::PositionSplit](../Server-API/Main-API-Interface/Trade/Positions/PositionSplit.md)
  * [IMTAdmin::PositionSplit](../Manager-API/Administrator-Interface/Trade-Databases/Positions/PositionSplit.md)
  * [IMTManager::PositionSplit](../Manager-API/Manager-Interface/Trade-Databases/Positions/PositionSplit.md)

If the split operation will cause a position volume to become zero, the split will not be performed, and the MT_RET_TRADE_SPLIT_VOLUME error code will be added to the 'results' return array.

```

---

<a id='user-management-md'></a>
### 14. `User-management.md`

```markdown
[🏠 Document Start](../README.md) / [Return Codes](README.md) / User management

[Previous](Configuration-Management.md) | [Next](Trade-management.md)

# User management

This group of codes is returned by the server when working with a database of [users](../Database-Interfaces/Users.md):

Constant | Value | Description  
MT_RET_USR_LAST_ADMIN | 3001 | The last administrator account has been deleted.  
MT_RET_USR_LOGIN_EXHAUSTED | 3002 | The range of logins has been exhausted.  
MT_RET_USR_LOGIN_PROHIBITED | 3003 | The login is reserved on another server.  
MT_RET_USR_LOGIN_EXIST | 3004 | The account already exists.  
MT_RET_USR_SUICIDE | 3005 | An attempt of self-deletion.  
MT_RET_USR_INVALID_PASSWORD | 3006 | Incorrect account password.  
MT_RET_USR_LIMIT_REACHED | 3007 | Reached the limit on the number of users.  
MT_RET_USR_HAS_TRADES | 3008 | The accounts has open positions.  
MT_RET_USR_DIFFERENT_SERVERS | 3009 | An attempt to move an account to another server.  
MT_RET_USR_DIFFERENT_CURRENCY | 3010 | An attempt to move an accounts to a group with a different deposit currency.  
MT_RET_USR_IMPORT_BALANCE | 3011 | Failed to import account balance.  
MT_RET_USR_IMPORT_GROUP | 3012 | The account is imported with the wrong group.  
MT_RET_USR_ACCOUNT_EXIST | 3013 | [A trading account in an external system](../Database-Interfaces/Users/IMTUser/ExternalAccountAdd.md) already exists for a specified login.  
MT_RET_USR_IMPORT_ACCOUNT | 3014 | Failed to [import](https://support.metaquotes.net/en/docs/mt5/platform/administration/admin_accounts/accounts_import_mt) account's trading data.  
MT_RET_USR_IMPORT_POSITIONS | 3015 | Failed to import account's trading positions.  
MT_RET_USR_IMPORT_ORDERS | 3016 | Failed to import account's open orders.  
MT_RET_USR_IMPORT_DEALS | 3017 | Failed to import account's deal history.  
MT_RET_USR_IMPORT_HISTORY | 3018 | Failed to import account's order history.  
MT_RET_USR_API_LIMIT_REACHED | 3019 | Reached the limit on the number of users with the permission to connect via the API ([IMTUser::USER_RIGHT_API_ENABLED (#enusersrights)](../Database-Interfaces/Users/IMTUser/Enumerations.md#enusersrights)). The current limit is 100 users.

```

---
