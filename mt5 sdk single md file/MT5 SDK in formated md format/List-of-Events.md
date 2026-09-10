# 📁 List-of-Events

- **Generated:** 2026-09-09 00:11
- **Total Files:** 1
- **Source:** `C:\Users\DELL\Downloads\server3\mt5_doc_dump\Documentation\MQ_Docs\Metatrader 5\MetaTrader5SDK\List-of-Events`

---

## 📑 Table of Contents

1. [README.md](#readme-md)

---

## 🌲 Project Structure

```
List-of-Events/
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
[🏠 Document Start](../README.md) / List of Events

[Previous](../Development-Features/README.md) | [Next](../List-of-Hooks/README.md)

# List of Events

Server API  
---  
[OnTradeRequestAdd](../Server-API/Interface-of-Trade-Events/OnTradeRequestAdd.md) | A handler of the event of adding a checked trade request in the requests queue.  
[OnTradeRequestUpdate](../Server-API/Interface-of-Trade-Events/OnTradeRequestUpdate.md) | A handler of the event of a changed state of a trade request.  
[OnTradeRequestDelete](../Server-API/Interface-of-Trade-Events/OnTradeRequestDelete.md) | A handler of the event of a trade request deletion.  
[OnTradeRequestProcess](../Server-API/Interface-of-Trade-Events/OnTradeRequestProcess.md) | A handler of the event of a successful execution of a trade request.  
[OnTradeRequestProcessCloseBy](../Server-API/Interface-of-Trade-Events/OnTradeRequestProcessCloseBy.md) | A handler of the event of a successful execution of a Close By trade request.  
[OnTradeRequestRefuse](../Server-API/Interface-of-Trade-Events/OnTradeRequestRefuse.md) | A handler of the event of refusal to execute a trade request before it is added to the queue.  
[OnTradeExecution](../Server-API/Interface-of-Trade-Events/OnTradeExecution.md) | A handler of the event of receiving a trade execution from a gateway.  
[OnEODStart](../Server-API/Interface-of-End-of-Day-Events/OnEODStart.md) | A handler of the event of start of operations associated with the end of the trading day.  
[OnEODGroupStart](../Server-API/Interface-of-End-of-Day-Events/OnEODGroupStart.md) | A handler of the event of start of operations associated with the end of the trading day for the specified group.  
[OnEODGroupCommissions](../Server-API/Interface-of-End-of-Day-Events/OnEODGroupCommissions.md) | A handler of the event of start of commission charging for the specified group at the end of the trading day.  
[OnEODGroupInterest](../Server-API/Interface-of-End-of-Day-Events/OnEODGroupInterest.md) | A handler of the event of start of annual interest charging for the specified group at the end of the trading day.  
[OnEODGroupStatements](../Server-API/Interface-of-End-of-Day-Events/OnEODGroupStatements.md) | A handler of the event of start of daily report generation for the specified group at the end of the trading day.  
[OnEODGroupRollovers](../Server-API/Interface-of-End-of-Day-Events/OnEODGroupRollovers.md) | A handler of the event of start of rollover charging for the specified group at the end of the trading day.  
[OnEODGroupFinish](../Server-API/Interface-of-End-of-Day-Events/OnEODGroupFinish.md) | A handler of the event of completion of operations associated with the end of the trading day for the specified group.  
[OnEODFinish](../Server-API/Interface-of-End-of-Day-Events/OnEODFinish.md) | A handler of the event of completion of operations associated with the end of the trading day.  
[OnEOMStart](../Server-API/Interface-of-End-of-Day-Events/OnEOMStart.md) | A handler of the event of start of operations associated with the end of the trading month.  
[OnEOMGroupStart](../Server-API/Interface-of-End-of-Day-Events/OnEOMGroupStart.md) | A handler of the event of start of operations associated with the end of the trading month for the specified group.  
[OnEOMGroupCommissions](../Server-API/Interface-of-End-of-Day-Events/OnEOMGroupCommissions.md) | A handler of the event of start of commission charging for the specified group at the end of the trading month.  
[OnEOMGroupInterest](../Server-API/Interface-of-End-of-Day-Events/OnEOMGroupInterest.md) | A handler of the event of start of annual interest charging for the specified group at the end of the trading month.  
[OnEOMGroupStatements](../Server-API/Interface-of-End-of-Day-Events/OnEOMGroupStatements.md) | A handler of the event of start of daily report generation for the specified group at the end of the trading month.  
[OnEOMGroupFinish](../Server-API/Interface-of-End-of-Day-Events/OnEOMGroupFinish.md) | A handler of the event of completion of operations associated with the end of the trading month for the specified group.  
[OnEOMFinish](../Server-API/Interface-of-End-of-Day-Events/OnEOMFinish.md) | A handler of the event of completion of operations associated with the end of the trading month.  
[OnServerLog](../Server-API/Interface-of-Server-Events/OnServerLog.md) | A handler of the event of adding a record to the server journal.  
Manager API  
[OnDealerResult](../Manager-API/Dealer-Interface/OnDealerResult.md) | Asynchronous answer to a dealer's trade request in the form of the object of confirmation.  
[OnDealerAnswer](../Manager-API/Dealer-Interface/OnDealerAnswer.md) | Asynchronous answer to a dealer's trade request in the form of the object of request.  
[OnConnect](../Manager-API/Interface-of-Manager-API-Events/Interface-of-Events-OnConnect.md) | A handler that notifies of establishing/restoring a connection between the manager or administrator terminal and the server.  
[OnDisconnect](../Manager-API/Interface-of-Manager-API-Events/Interface-of-Events-OnDisconnect.md) | A handler that notifies of loss of connection between the manager or administrator terminal and the server.  
[OnTradeAccountSet](../Manager-API/Interface-of-Manager-API-Events/Interface-of-Events-OnTradeAccountSet.md) | This handler receives [IMTManagerAPI::TradeAccountSet](../Manager-API/Manager-Interface/Trade-Activity/Monitoring-Account-States/TradeAccountSet.md) method execution result, as well as the final status of a client entry (after the passed changes have been applied).  
Gateway API  
[OnServerDisconnect](../Gateway-API/Event-Interface/OnServerDisconnect.md) | A handler of the event of the end of connection to one of the MetaTrader 5 platform components (server).  
[OnGatewayConfig](../Gateway-API/Event-Interface/OnGatewayConfig.md) | A handler of the event of passing a gateway/data feed own configuration from a history server connected to it.  
[OnGatewayStart](../Gateway-API/Event-Interface/OnGatewayStart.md) | A handler of the following event: Gateway API is synchronized with the platform and is ready for work.  
[OnGatewayStop](../Gateway-API/Event-Interface/OnGatewayStop.md) | OnGatewayStart inverse events hadler. Notifies on the fact that Gateway API is not synchronized with the platform and not ready for work.  
[OnGatewayShutdown](../Gateway-API/Event-Interface/OnGatewayShutdown.md) | A handler of the event notifying on a trading platform operation end.  
[OnDealerLock](../Gateway-API/Event-Interface/OnDealerLock.md) | A handler of the event of capturing (blocking) of a successive trade request from a requests queue.  
[OnDealerAnswer](../Gateway-API/Event-Interface/OnDealerAnswer.md) | A handler of the event notifying on a request confirmation or execution result.  
[OnGatewayAccountSet](../Gateway-API/Event-Interface/OnGatewayAccountSet.md) | A handler of the event of requesting information about a client from MetaTrader 5 platform.  
[OnGatewayAccountAnswer](../Gateway-API/Event-Interface/OnGatewayAccountAnswer.md) | A handler of the event of modifying information about a client via [IMTGatewayAPI::GatewayAccountSet](../Gateway-API/Main-Interface/Synchronizing-Trading-Data/GatewayAccountSet.md) method.  
[OnServerSymbolAdd](../Gateway-API/Event-Interface/OnServerSymbolAdd.md) | A handler of the event of symbol adding.  
[OnServerSymbolDelete](../Gateway-API/Event-Interface/OnServerSymbolDelete.md) | A handler of the event of symbol removal.  
Common events of configurations  
[OnCommonUpdate](../Configuration-Interfaces/Common/IMTConCommonSink/IMTConSink-OnUpdate.md) | The handler of the event of common configuration update.  
[OnCommonSync](../Configuration-Interfaces/Common/IMTConCommonSink/IMTConSink-OnSync.md) | This method is called by the API to notify that a common configuration has been updated.  
[OnConServerAdd](../Configuration-Interfaces/Network/IMTConServerSink/OnConServerAdd.md) | A handler of the event of adding a new server configuration.  
[OnConServerUpdate](../Configuration-Interfaces/Network/IMTConServerSink/OnConServerUpdate.md) | A handler of the event of updating a server configuration.  
[OnConServerDelete](../Configuration-Interfaces/Network/IMTConServerSink/OnConServerDelete.md) | A handler of the event of removing a server configuration.  
[OnConServerSync](../Configuration-Interfaces/Network/IMTConServerSink/OnConServerSync.md) | A handler of the event of synchronization of a server configuration.  
[OnPluginAdd](../Configuration-Interfaces/Plugins/IMTConPluginSink/OnPluginAdd.md) | A handler of the event of adding a new plugin configuration.  
[OnPluginUpdate](../Configuration-Interfaces/Plugins/IMTConPluginSink/OnPluginUpdate.md) | A handler of the event of updating a plugin configuration.  
[OnPluginDelete](../Configuration-Interfaces/Plugins/IMTConPluginSink/OnPluginDelete.md) | A handler of the event of removing a plugin configuration.  
[OnPluginSync](../Configuration-Interfaces/Plugins/IMTConPluginSink/OnPluginSync.md) | A handler of the event of synchronization of plugin configuration.  
[OnFeederAdd](../Configuration-Interfaces/Data-Feeds/IMTConFeederSink/OnFeederAdd.md) | A handler of the event of adding a new data feed configuration.  
[OnFeederUpdate](../Configuration-Interfaces/Data-Feeds/IMTConFeederSink/OnFeederUpdate.md) | A handler of the event of updating a data feed configuration.  
[OnFeederDelete](../Configuration-Interfaces/Data-Feeds/IMTConFeederSink/OnFeederDelete.md) | A handler of the event of removing a data feed configuration.  
[OnFeederSync](../Configuration-Interfaces/Data-Feeds/IMTConFeederSink/OnFeederSync.md) | A handler of the event of synchronization of a data feed configuration.  
[OnTimeUpdate](../Configuration-Interfaces/Time/IMTConTimeSink/IMTConSink-OnUpdate.md) | A handler of the event of update of the platform time settings.  
[OnTimeSync](../Configuration-Interfaces/Time/IMTConTimeSink/IMTConSink-OnSync.md) | A handler of the event of synchronization of the platform time settings.  
[OnHolidayAdd](../Configuration-Interfaces/Holidays/IMTConHolidaySink/OnHolidayAdd.md) | A handler of the event of adding a new holiday configuration.  
[OnHolidayUpdate](../Configuration-Interfaces/Holidays/IMTConHolidaySink/OnHolidayUpdate.md) | A handler of the event of updating a holiday configuration.  
[OnHolidayDelete](../Configuration-Interfaces/Holidays/IMTConHolidaySink/OnHolidayDelete.md) | A handler of the event of removing a holiday configuration.  
[OnHolidaySync](../Configuration-Interfaces/Holidays/IMTConHolidaySink/OnHolidaySync.md) | A handler of the event of synchronization of holiday configuration.  
[OnFirewallAdd](../Configuration-Interfaces/Firewall/IMTConFirewallSink/IMTConSink-OnAdd.md) | A handler of the event of adding a new firewall rule.  
[OnFirewallUpdate](../Configuration-Interfaces/Firewall/IMTConFirewallSink/IMTConSink-OnUpdate.md) | A handler of the event of update of a firewall rule.  
[OnFirewallDelete](../Configuration-Interfaces/Firewall/IMTConFirewallSink/IMTConSink-OnDelete.md) | A handler of the event of deletion of a firewall rule.  
[OnFirewallSync](../Configuration-Interfaces/Firewall/IMTConFirewallSink/IMTConSink-OnSync.md) | A handler of the firewall rules synchronization event.  
[OnSymbolAdd](../Configuration-Interfaces/Symbols/IMTConSymbolSink/OnSymbolAdd.md) | A handler of the event of adding a new symbol.  
[OnSymbolUpdate](../Configuration-Interfaces/Symbols/IMTConSymbolSink/OnSymbolUpdate.md) | A handler of the event of updating symbol settings.  
[OnSymbolDelete](../Configuration-Interfaces/Symbols/IMTConSymbolSink/OnSymbolDelete.md) | A handler of the event of symbol removal.  
[OnSymbolSync](../Configuration-Interfaces/Symbols/IMTConSymbolSink/OnSymbolSync.md) | A handler of the event of symbols synchronization.  
[OnSpreadAdd](../Configuration-Interfaces/Spreads/IMTConSpreadSink/OnSpreadAdd.md) | A handler of the event of adding a new spread configuration.  
[OnSpreadUpdate](../Configuration-Interfaces/Spreads/IMTConSpreadSink/OnSpreadUpdate.md) | A handler of the event of updating spread settings.  
[OnSpreadDelete](../Configuration-Interfaces/Spreads/IMTConSpreadSink/OnSpreadDelete.md) | A handler of the event of removing a spread configuration.  
[OnSpreadSync](../Configuration-Interfaces/Spreads/IMTConSpreadSink/OnSpreadSync.md) | A handler of the event of synchronization of spread configurations.  
[OnGroupAdd](../Configuration-Interfaces/Groups/IMTConGroupSink/OnGroupAdd.md) | A handler of the event of adding a new group.  
[OnGroupUpdate](../Configuration-Interfaces/Groups/IMTConGroupSink/OnGroupUpdate.md) | A handler of the event of updating group settings.  
[OnGroupDelete](../Configuration-Interfaces/Groups/IMTConGroupSink/OnGroupDelete.md) | A handler of the event of group removal.  
[OnGroupSync](../Configuration-Interfaces/Groups/IMTConGroupSink/OnGroupSync.md) | A handler of the event of groups synchronization.  
[OnManagerAdd](../Configuration-Interfaces/Managers/IMTConManagerSink/OnManagerAdd.md) | A handler of the event of adding a new manager configuration.  
[OnManagerUpdate](../Configuration-Interfaces/Managers/IMTConManagerSink/OnManagerUpdate.md) | A handler of the event of updating manager settings.  
[OnManagerDelete](../Configuration-Interfaces/Managers/IMTConManagerSink/OnManagerDelete.md) | A handler of the event of removing a manager configuration.  
[OnManagerSync](../Configuration-Interfaces/Managers/IMTConManagerSink/OnManagerSync.md) | A handler of the event of synchronization of manager configurations.  
[OnHistorySyncAdd](../Configuration-Interfaces/History-Synchronization/IMTConHistorySyncSink/OnHistorySyncAdd.md) | A handler of the event of adding a new configuration of history data synchronization.  
[OnHistorySyncUpdate](../Configuration-Interfaces/History-Synchronization/IMTConHistorySyncSink/OnHistorySyncUpdate.md) | A handler of the event of update of a configuration of history data synchronization.  
[OnHistorySyncDelete](../Configuration-Interfaces/History-Synchronization/IMTConHistorySyncSink/OnHistorySyncDelete.md) | A handler of the event of deletion of a configuration of history data synchronization.  
[OnHistorySyncSync](../Configuration-Interfaces/History-Synchronization/IMTConHistorySyncSink/OnHistorySyncSync.md) | A handler of the event of synchronization of configurations of history data synchronization.  
[OnGatewayAdd](../Configuration-Interfaces/Gateways/IMTConGatewaySink/OnGatewayAdd.md) | A handler of the event of adding a new gateway configuration.  
[OnGatewayUpdate](../Configuration-Interfaces/Gateways/IMTConGatewaySink/OnGatewayUpdate.md) | A handler of the event of updating a gateway configuration.  
[OnGatewayDelete](../Configuration-Interfaces/Gateways/IMTConGatewaySink/OnGatewayDelete.md) | A handler of the event of removing a gateway configuration.  
[OnGatewaySync](../Configuration-Interfaces/Gateways/IMTConGatewaySink/OnGatewaySync.md) | A handler of the event of synchronization of gateway configuration.  
[OnRouteAdd](../Configuration-Interfaces/Routing/IMTConRouteSink/OnRouteAdd.md) | A handler of the event of adding a new routing rule.  
[OnRouteUpdate](../Configuration-Interfaces/Routing/IMTConRouteSink/OnRouteUpdate.md) | A handler of the event of updating a routing rule.  
[OnRouteDelete](../Configuration-Interfaces/Routing/IMTConRouteSink/OnRouteDelete.md) | A handler of the event of deletion of a routing rule.  
[OnRouteSync](../Configuration-Interfaces/Routing/IMTConRouteSink/OnRouteSync.md) | A handler of the event of synchronization of routing rules.  
[OnReportAdd](../Configuration-Interfaces/Reports/IMTConReportSink/OnReportAdd.md) | A handler of the event of adding a new report configuration.  
[OnReportUpdate](../Configuration-Interfaces/Reports/IMTConReportSink/OnReportUpdate.md) | A handler of the event of updating a report configuration.  
[OnReportDelete](../Configuration-Interfaces/Reports/IMTConReportSink/OnReportDelete.md) | A handler of the event of removing a report configuration.  
[OnReportSync](../Configuration-Interfaces/Reports/IMTConReportSink/OnReportSync.md) | A handler of the event of synchronization of report configurations.  
Common events of databases  
[OnOrderAdd](../Database-Interfaces/Trade/Orders/IMTOrderSink/OnOrderAdd.md) | A handler of the event of adding an open order.  
[OnOrderUpdate](../Database-Interfaces/Trade/Orders/IMTOrderSink/OnOrderUpdate.md) | A handler of the event of modifying an open order.  
[OnOrderDelete](../Database-Interfaces/Trade/Orders/IMTOrderSink/OnOrderDelete.md) | A handler of the event of deleting an open order.  
[OnOrderClean](../Database-Interfaces/Trade/Orders/IMTOrderSink/OnOrderClean.md) | A handler of the event of clearing open orders of a client.  
[OnOrderSync](../Database-Interfaces/Trade/Orders/IMTOrderSink/OnOrderSync.md) | A handler of the event of synchronization of a database of open orders.  
[OnHistoryAdd](../Database-Interfaces/Trade/Orders/IMTHistorySink/OnHistoryAdd.md) | A handler of the event of adding a closed order.  
[OnHisotryUpdate](../Database-Interfaces/Trade/Orders/IMTHistorySink/OnHistoryUpdate.md) | A handler of the event of modifying a closed order.  
[OnHistoryDelete](../Database-Interfaces/Trade/Orders/IMTHistorySink/OnHistoryDelete.md) | A handler of the event of deleting a closed order.  
[OnHistoryClean](../Database-Interfaces/Trade/Orders/IMTHistorySink/OnHistoryClean.md) | A handler of the event of clearing closed orders of a client.  
[OnHistorySync](../Database-Interfaces/Trade/Orders/IMTHistorySink/OnHistorySync.md) | A handler of the event of synchronization of a database of closed orders.  
[OnDealAdd](../Database-Interfaces/Trade/Deals/IMTDealSink/OnDealAdd.md) | A handler of the event of adding a deal.  
[OnDealUpdate](../Database-Interfaces/Trade/Deals/IMTDealSink/OnDealUpdate.md) | A handler of the event of updating a deal.  
[OnDealDelete](../Database-Interfaces/Trade/Deals/IMTDealSink/OnDealDelete.md) | A handler of the event of deal removal.  
[OnDealClean](../Database-Interfaces/Trade/Deals/IMTDealSink/OnDealClean.md) | A handler of the event of clearing of a client's deals.  
[OnDealSync](../Database-Interfaces/Trade/Deals/IMTDealSink/OnDealSync.md) | A handler of the event of a deal database synchronization.  
[OnDealPerform](../Database-Interfaces/Trade/Deals/IMTDealSink/OnDealPerform.md) | A handler of the event of deal execution (only in MetaTrader 5 Server API).  
[OnPositionAdd](../Database-Interfaces/Trade/Positions/IMTPositionSink/OnPositionAdd.md) | A handler of the event of adding a position.  
[OnPositionUpdate](../Database-Interfaces/Trade/Positions/IMTPositionSink/OnPositionUpdate.md) | A handler of an event of trade position modification.  
[OnPositionDelete](../Database-Interfaces/Trade/Positions/IMTPositionSink/OnPositionDelete.md) | A handler of an event of trade position deletion.  
[OnPositionClean](../Database-Interfaces/Trade/Positions/IMTPositionSink/OnPositionClean.md) | A handler of the event of clearing trade positions of a client.  
[OnPositionSync](../Database-Interfaces/Trade/Positions/IMTPositionSink/OnPositionSync.md) | A handler of the event of synchronization of a database of trade positions.  
[OnRequestAdd](../Database-Interfaces/Trade/Trade-Requests/IMTRequestSink/Requests-OnRequestAdd.md) | A handler of the event of adding a trade request.  
[OnRequestUpdate](../Database-Interfaces/Trade/Trade-Requests/IMTRequestSink/Requests-OnRequestUpdate.md) | A handler of the event of trade request change.  
[OnRequestDelete](../Database-Interfaces/Trade/Trade-Requests/IMTRequestSink/Requests-OnRequestDelete.md) | A handler of the event of a trade request deletion.  
[OnRequestSync](../Database-Interfaces/Trade/Trade-Requests/IMTRequestSink/Requests-OnRequestSync.md) | A handler of the event of synchronization of a queue of trade requests.  
[OnSummaryUpdate](../Database-Interfaces/Trade/Summary-Positions/IMTSummarySink/OnSummaryUpdate.md) | A handler of an event of update of summary positions.  
[OnExposureUpdate](../Database-Interfaces/Trade/Assets/IMTExposureSink/OnExposureUpdate.md) | A handler of the exposure modification event.  
[OnDailyAdd](../Database-Interfaces/Trade/Daily-Reports/IMTDailySink/OnDailyAdd.md) | A handler of the event of adding a new daily report.  
[OnDailyUpdate](../Database-Interfaces/Trade/Daily-Reports/IMTDailySink/OnDailyUpdate.md) | A handler of the event of updating a daily report.  
[OnDailyDelete](../Database-Interfaces/Trade/Daily-Reports/IMTDailySink/OnDailyDelete.md) | A handler of the event of removing a daily report.  
[OnDailyClear](../Database-Interfaces/Trade/Daily-Reports/IMTDailySink/OnDailyClear.md) | A handler of the event of clearing of a client's daily reports.  
[OnDailySync](../Database-Interfaces/Trade/Daily-Reports/IMTDailySink/OnDailySync.md) | A handler of the event of synchronization of a database of daily reports.  
[OnUserAdd](../Database-Interfaces/Users/IMTUserSink/OnUserAdd.md) | A handler of the event of adding a new client record.  
[OnUserUpdate](../Database-Interfaces/Users/IMTUserSink/OnUserUpdate.md) | A handler of an event of client record update.  
[OnUserDelete](../Database-Interfaces/Users/IMTUserSink/OnUserDelete.md) | A handler of an event of client record deletion.  
[OnUserClean](../Database-Interfaces/Users/IMTUserSink/OnUserClean.md) | A handler of the event of deletion of obsolete demo account on a trade server.  
[OnUserLogin](../Database-Interfaces/Users/IMTUserSink/OnUserLogin.md) | A pointer of a client's connection to the server.  
[OnUserLogout](../Database-Interfaces/Users/IMTUserSink/OnUserLogout.md) | A handler of the event of a client's disconnection from the server.  
[OnUserSync](../Database-Interfaces/Users/IMTUserSink/OnUserSync.md) | A handler of the event of a client base synchronization.  
[OnTick](../Database-Interfaces/Price-Data/IMTTickSink/OnTick.md) | A handler of the event of new quote arrival.  
[OnTickStat](../Database-Interfaces/Price-Data/IMTTickSink/OnTickStat.md) | A handler of the event of update of the statistical information about a price.  
[OnBook](../Database-Interfaces/Depth-of-Market/IMTBookSink/OnBook.md) | A handler of the event of the received update of the Depth of Market.  
[OnMail](../Database-Interfaces/Mail-Database/IMTMailSink/OnMail.md) | A handler of the event of email receiving.  
[OnNews](../Database-Interfaces/News-Database/IMTNewsSink/OnNews.md) | A handler of the event of news receiving.

```

---
