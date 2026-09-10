# 📁 List-of-Hooks

- **Generated:** 2026-09-09 00:11
- **Total Files:** 1
- **Source:** `C:\Users\DELL\Downloads\server3\mt5_doc_dump\Documentation\MQ_Docs\Metatrader 5\MetaTrader5SDK\List-of-Hooks`

---

## 📑 Table of Contents

1. [README.md](#readme-md)

---

## 🌲 Project Structure

```
List-of-Hooks/
├── images/
│   ├── next.png
│   └── previous.png
└── README.md
```

---

## 📄 Files

<a id='readme-md'></a>
### 1. `README.md`

```markdown
[🏠 Document Start](../README.md) / List of Hooks

[Previous](../List-of-Events/README.md) | [Next](../Technical-Support/README.md)

# List of Hooks

Server API  
---  
[HookManagerCommand](../Server-API/Interface-of-Custom-Events/HookManagerCommand.md) | A hook of an event of execution of a manager's custom command.  
[HookWebAPICommand](../Server-API/Interface-of-Custom-Events/HookWebAPICommand.md) | A hook of an event of execution of a web-client's command.  
[HookTradeRequestAdd](../Server-API/Interface-of-Trade-Events/HookTradeRequestAdd.md) | A hook for adding a checked trade request in the requests queue.  
[HookTradeRequestRoute](../Server-API/Interface-of-Trade-Events/HookTradeRequestRoute.md) | A hook of trade request routing in a requests queue.  
[HookTradeRequestProcess](../Server-API/Interface-of-Trade-Events/HookTradeRequestProcess.md) | A hook of trade request execution.  
[HookTradeRequestProcessCloseBy](../Server-API/Interface-of-Trade-Events/HookTradeRequestProcessCloseBy.md) | A hook of a Close By trade request execution.  
[HookTradeRollover](../Server-API/Interface-of-Trade-Events/HookTradeRollover.md) | A hook of rollover charging.  
[HookTradeInterest](../Server-API/Interface-of-Trade-Events/HookTradeInterest.md) | A hook of calculation of annual interest.  
[HookTradeInterestCharge](../Server-API/Interface-of-Trade-Events/HookTradeInterestCharge.md) | A hook of adding the calculated amount of the annual interest to a client's account.  
[HookTradeInterestChargeDeal](../Server-API/Interface-of-Trade-Events/HookTradeInterestChargeDeal.md) | A hook of a balance deal for charging annual interest.  
[HookTradeCommissionOrder](../Server-API/Interface-of-Trade-Events/HookTradeCommissionOrder.md) | A hook for calculating commissions that are locked on an account when conducting a trade operation.  
[HookTradeCommissionCharge](../Server-API/Interface-of-Trade-Events/HookTradeCommissionCharge.md) | Hook of final adding/withdrawal of commissions from an account at the end of a day/month.  
[HookTradeCommissionDeal](../Server-API/Interface-of-Trade-Events/HookTradeCommissionDeal.md) | A hook of commissions charged instantly at executing a deal (in the IMTConCommission::COMM_CHARGE_INSTANT mode).  
[HookTradeExecution](../Server-API/Interface-of-Trade-Events/HookTradeExecution.md) | A hook of applying a trade execution.  
[HookUserAdd](../Database-Interfaces/Users/IMTUserSink/HookUserAdd.md) | A hook of an event of adding a new client record.  
[HookUserUpdate](../Database-Interfaces/Users/IMTUserSink/HookUserUpdate.md) | A hook of an event of client record update.  
[HookUserDelete](../Database-Interfaces/Users/IMTUserSink/HookUserDelete.md) | A hook of an event of client record deletion.  
[HookUserLogin](../Database-Interfaces/Users/IMTUserSink/HookUserLogin.md) | A hook of a client's connection to the server.  
[HookTick](../Database-Interfaces/Price-Data/IMTTickSink/HookTick.md) | A hook of an event of new quote arrival.  
[HookTickStat](../Database-Interfaces/Price-Data/IMTTickSink/HookTickStat.md) | A hook of an event of update of the statistical information about a price.  
[HookMail](../Database-Interfaces/Mail-Database/IMTMailSink/HookMail.md) | A hook of the event of email receiving.  
[HookNews](../Database-Interfaces/News-Database/IMTNewsSink/HookNews.md) | A hook of the event of news receiving.  
Gateway API  
[HookServerConnect](../Gateway-API/Event-Interface/HookServerConnect.md) | The hook for managing MetaTrader 5 platform components connections to Gateway API.  
[HookGatewayPositionsRequest](../Gateway-API/Event-Interface/HookGatewayPositionsRequest.md) | The hook for receiving states of trading accounts used by the gateway to operate in an external system.  
[HookGatewayPositionsCheck](../Gateway-API/Event-Interface/HookGatewayPositionsCheck.md) | Hook for positions verification. This method is reserved for future use.  
[HookGatewayOrdersRequest](../Gateway-API/Event-Interface/HookGatewayOrdersRequest.md) | The hook for receiving the state of the client's current pending orders in an external trading system.  
[HookGatewayAccountRequest](../Gateway-API/Event-Interface/HookGatewayAccountRequest.md) | The hook for synchronizing client's trading data with an external trading system.

```

---
