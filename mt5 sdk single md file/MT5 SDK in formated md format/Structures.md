# 📁 Structures

- **Generated:** 2026-09-09 00:12
- **Total Files:** 21
- **Source:** `C:\Users\DELL\Downloads\server3\mt5_doc_dump\Documentation\MQ_Docs\Metatrader 5\MetaTrader5SDK\Structures`

---

## 📑 Table of Contents

1. [MTBookItem.md](#mtbookitem-md)
2. [MTBookMTBookDiff.md](#mtbookmtbookdiff-md)
3. [MTChartBar.md](#mtchartbar-md)
4. [MTEconomicEvent.md](#mteconomicevent-md)
5. [MTGatewayInfo.md](#mtgatewayinfo-md)
6. [MTLicenseCheck.md](#mtlicensecheck-md)
7. [MTLogRecord.md](#mtlogrecord-md)
8. [MTMailRange.md](#mtmailrange-md)
9. [MTNews.md](#mtnews-md)
10. [MTPluginInfo.md](#mtplugininfo-md)
11. [MTPluginParam.md](#mtpluginparam-md)
12. [MTProxyInfo.md](#mtproxyinfo-md)
13. [MTReportInfo.md](#mtreportinfo-md)
14. [MTReportParam.md](#mtreportparam-md)
15. [MTReportServerInfo.md](#mtreportserverinfo-md)
16. [MTServerInfo.md](#mtserverinfo-md)
17. [MTTick.md](#mttick-md)
18. [MTTickRate.md](#mttickrate-md)
19. [MTTickShort.md](#mttickshort-md)
20. [MTTickStat.md](#mttickstat-md)
21. [README.md](#readme-md)

---

## 🌲 Project Structure

```
Structures/
├── images/
│   ├── next.png
│   ├── next_1.png
│   ├── next_10.png
│   ├── next_11.png
│   ├── next_12.png
│   ├── next_13.png
│   ├── next_14.png
│   ├── next_15.png
│   ├── next_16.png
│   ├── next_17.png
│   ├── next_18.png
│   ├── next_19.png
│   ├── next_2.png
│   ├── next_20.png
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
│   ├── previous_14.png
│   ├── previous_15.png
│   ├── previous_16.png
│   ├── previous_17.png
│   ├── previous_18.png
│   ├── previous_19.png
│   ├── previous_2.png
│   ├── previous_20.png
│   ├── previous_3.png
│   ├── previous_4.png
│   ├── previous_5.png
│   ├── previous_6.png
│   ├── previous_7.png
│   ├── previous_8.png
│   └── previous_9.png
├── MTBookItem.md
├── MTBookMTBookDiff.md
├── MTChartBar.md
├── MTEconomicEvent.md
├── MTGatewayInfo.md
├── MTLicenseCheck.md
├── MTLogRecord.md
├── MTMailRange.md
├── MTNews.md
├── MTPluginInfo.md
├── MTPluginParam.md
├── MTProxyInfo.md
├── MTReportInfo.md
├── MTReportParam.md
├── MTReportServerInfo.md
├── MTServerInfo.md
├── MTTick.md
├── MTTickRate.md
├── MTTickShort.md
├── MTTickStat.md
└── README.md
```

---

## 📄 Files

<a id='mtbookitem-md'></a>
### 21. `MTBookItem.md`

```markdown
[🏠 Document Start](../README.md) / [Structures](README.md) / MTBookItem

[Previous](MTChartBar.md) | [Next](MTBookMTBookDiff.md)

<a id="mtbookitem"></a>
# MTBookItem (#mtbookitem)

The MTBookItem describes an entry of the Depth of Market. The structure is defined with the one-byte alignment.
    
    
    #pragma pack(push,1)
    struct MTBookItem
      {
       //--- Type of entry
       enum EnBookItem
         {
          ItemReset      =0,                                    // Reset an entry in the Depth of Market
          ItemSell       =1,                                    // Sell request
          ItemBuy        =2                                     // Buy request
          ItemSellMarket =3,                                    // Market sell request
          ItemBuyMarket  =4                                     // Market buy request
         };
       UINT              type;                                  // Type of entry
       double            price;                                 // Deal price
       INT64             volume;                                // Deal volume
       INT64             volume_ext;                            // deal volume with extended accuracy
       UINT              reserved[8];                           // A reserved field
      };
    #pragma pack(pop)

MTBookItem is used for filling the[MTBook/MTBookDiff](MTBookMTBookDiff.md) structure.

<a id="parameters"></a>
## Parameters (#parameters)

The structure contains the following parameters:

Field | Type | Description  
type | UINT | Type of entry that is passed using the EnBookItem enumeration.  
price | double | Deal price. All the symbol prices delivered into the platform are rounded in accordance with the [IMTConSymbol::Digits](../Configuration-Interfaces/Symbols/IMTConSymbol/Digits.md) parameter of the symbol. When broadcasting prices with higher accuracy, different levels can be combined into one rounded level. To avoid collisions, set the precision of the symbols in accordance with the precision of transmitted data.  
volume | INT64 | Deal volume. The volume is recorded in the same form as it is passed by a data provider. A data provider may pass volumes as amounts of contracts (in lots) or as amounts of money. On the trading platform side, this value is interpreted depending on the type of calculation of profit and margin set for a symbol ([IMTConSymbol::CalcMode](../Configuration-Interfaces/Symbols/IMTConSymbol/CalcMode.md)):

  * For the [IMTConSymbol::TRADE_MODE_FOREX (#encalcmode)](../Configuration-Interfaces/Symbols/IMTConSymbol/Enumerations.md#encalcmode) type, the volume is interpreted as the amount of base currency units of a symbol.
  * For all the other types, the volume is interpreted as the amount of contracts (lots).

Unlike all other API methods and fields, in which the volume is specified as a fixed-precision value with 4 digits (where 10000 is 1 lot), the volume in this field is specified as is, with the precision of 0 digits. For example, for all financial instruments except Forex, the value of 1 means 1 lot. For operations with [extended-precision volumes (#volume)](../Development-Features/README.md#volume), use the 'volume_ext' field.

  * The 'volume_ext' value has a higher priority than 'volume'. The server will use this value if specified.
  * When returning volume values, the server fills both fields: with standard and extended precision.

  
volume_ext | INT64 | Deal volume with [extended precision (#volume)](../Development-Features/README.md#volume). It is similar to the 'volume' field, but the value is passed with the fixed number of decimal places (8).

  * The 'volume_ext' value has a higher priority than 'volume'. The server will use this value if specified.
  * When returning volume values, the server fills both fields: with standard and extended precision.

  
reserved | UINT | A reserved field for future use.  
  
<a id="enumerations"></a>
## Enumerations (#enumerations)

The structure contains one enumeration:

<a id="enbookitem"></a>
### EnBookItem (#enbookitem)

Types of entries of the Depth of Market are described in EnBookItem.

ID | Value | Description  
ItemReset | 0 | Reset an entry of the Depth of Market. This type is not used in Manager API.  
ItemSell | 1 | Sell request.  
ItemBuy | 2 | Buy request.  
ItemMarketSell | 3 | Used for displaying aggregated market sell requests.  
ItemMarketBuy | 4 | Used for displaying aggregated market buy requests.

```

---

<a id='mtbookmtbookdiff-md'></a>
### 21. `MTBookMTBookDiff.md`

```markdown
[🏠 Document Start](../README.md) / [Structures](README.md) / MTBookMTBookDiff

[Previous](MTBookItem.md) | [Next](MTGatewayInfo.md)

<a id="mtbookmtbookdiff"></a>
# MTBook/MTBookDiff (#mtbookmtbookdiff)

> The MTBook and MTBookDiff structures are identical. The difference is that the former is used in the Server API and Manager API, and the latter is used in the Gateway API. The name emphasizes the fundamental difference in passing the Depth of Market data. In the Server API Manager API, the entire Depth of Market is passed each time, while in the Gateway API only changes are passed.

The MTBook/MTBookDiff structure describes changes of the [Depth of Market](../Database-Interfaces/Depth-of-Market.md). The structure is defined with the one-byte alignment.
    
    
    #pragma pack(push,1)
    struct MTBook
      {
       //--- Depth of market flags
       enum EnBookFlags
         {
          FLAG_PRE_AUCTION =1,                                   // Pre-auction flag
          FLAG_SNAPSHOT    =2,                                   // Flag for internal use
          //--- Enumeration borders
          FLAG_NONE        =0                                    // No flags
          FLAG_ALL         =FLAG_PRE_AUCTION                     // All flags
         };
       wchar_t           symbol[32];                             // Symbol
       MTBookItem        items[32*4];                            // Change elements
       UINT              items_total;                            // Number of the change elements
       UINT64            flags;                                  // Depth of market flags
       INT64             datetime;                               // Time of Depth of market change
       INT64             datetime_msc;                           // Time of Depth of market change in milliseconds
       UINT              reserved[64];                           // Reserved field
      };
    #pragma pack(pop)
    typedef MTBook MTBookDiff;

This structure is used in the following methods:

  * [IMTManagerAPI::BookGet](../Manager-API/Manager-Interface/Market-Depth/BookGet.md)
  * [IMTBookSink::OnBook](../Database-Interfaces/Depth-of-Market/IMTBookSink/OnBook.md)
  * [IMTGatewayAPI::SendBookDiffs](../Gateway-API/Main-Interface/Quote-and-News-Feeds/SendBookDiffs.md)
  * [IMTGatewayAPI::SendBooks](../Gateway-API/Main-Interface/Quote-and-News-Feeds/SendBooks.md)
  * [IMTServerAPI::BookGet](../Server-API/Main-API-Interface/Depth-of-Market/BookGet.md)



<a id="enumerations"></a>
## Enumerations (#enumerations)

The following enumerations are described in the structure:

<a id="enbookflags"></a>
### EnBookFlags (#enbookflags)

The following Depth of Market flags are listed in EnBookFlags:

ID | Value | Description  
FLAG_PRE_AUCTION | 1 | The flag for using the Depth of Market in the absence of the auction. In the absence of the auction, traders' requests are not matched. Thus, the automatic tick data generation based on the best Depth of Market bid and ask prices is disabled in MetaTrader 5 platform. One of the typical examples of this flag application is Pre-Market period before trading actually starts when traders place their orders but they are not matched. In this case, buy offers may be displayed above sell ones or vice versa in the terminal Depth of Market. [MTBookItem.ItemSellMarket](MTBookItem.md) and [MTBookItem.ItemBuyMarket](MTBookItem.md) elements are used to display aggregate market requests.  
FLAG_SNAPSHOT | 2 | Flag for internal use only.  
FLAG_NONE | 0 | Beginning of enumeration. It corresponds to the absence of flags.  
FLAG_ALL |  | End of enumeration. All flags are enabled.  
  
The structure contains the following parameters:

Field | Type | Description  
symbol | wchar_t | The symbol, for which the change is applied.  
items | MTBookItem | The array of the Depth of Market changing elements of the [MTBookItem](MTBookItem.md) type. The trading platform analyzes the items elements sent in the MTBookDiff structure strictly from the beginning to the end, consequently applying changes to the Market Depth.  
items_total | UINT | The number of the transmitted elements in the items parameter.  
flags | UINT64 | Depth of market flags. The enumeration [EnBookFlags (#enbookflags)](MTBookMTBookDiff.md#enbookflags) is used for passing the flags.  
datetime | INT64 | Date and time of the depth of market change in seconds passed since 01.01.1970. This fields is not filled in by default (equal to 0) - the history server inserts the server's current trading time when receiving the data. If necessary, the gateway developer can set this date on their own. Using this feature implies 100% correctness of the transferred data time. Therefore, it should be used only when necessary.

  * datetime_msc has a higher priority than datetime. The server will use this value if it it specified.
  * If datetime_msc is specified only, datetime value will be filled automatically on its basis (without milliseconds).
  * If datetime is specified only, datetime_msc value will be filled automatically on its basis (with zero value for milliseconds).

  
datetime_msc | INT64 | Date and time of the depth of market change in milliseconds passed since 01.01.1970. This fields is not filled in by default (equal to 0) - the history server inserts the server's current trading time when receiving the data. If necessary, the gateway developer can set this date on their own. Using this feature implies 100% correctness of the transferred data time. Therefore, it should be used only when necessary.

  * datetime_msc has a higher priority than datetime. The server will use this value if it it specified.
  * If datetime_msc is specified only, datetime value will be filled automatically on its basis (without milliseconds).
  * If datetime is specified only, datetime_msc value will be filled automatically on its basis (with zero value for milliseconds).

  
reserved | UINT | A reserved parameter.

```

---

<a id='mtchartbar-md'></a>
### 21. `MTChartBar.md`

```markdown
[🏠 Document Start](../README.md) / [Structures](README.md) / MTChartBar

[Previous](MTLogRecord.md) | [Next](MTBookItem.md)

# MTChartBar

The MTChartBar structure describes the bar of a chart. The structure is defined with the one-byte alignment.
    
    
    #pragma pack(push,1)
    struct MTChartBar
      {
       INT64             datetime;                               // Date and time
       //--- prices
       double            open;                                   // The Open price
       double            high;                                   // The High price
       double            low;                                    // The Low price
       double            close;                                  // The Close price
       //--- volume
       UINT64            tick_volume;                            // Tick volume
       INT32             spread;                                 // Spread
       UINT64            volume;                                 // Volume
      };
    #pragma pack(pop)

This structure is used in the following methods:

  * [IMTAdminAPI::ChartRequest](../Manager-API/Administrator-Interface/History-Data/ChartRequest.md)
  * [IMTAdminAPI::ChartDelete](../Manager-API/Administrator-Interface/History-Data/ChartDelete.md)
  * [IMTAdminAPI::ChartUpdate](../Manager-API/Administrator-Interface/History-Data/ChartUpdate.md)
  * [IMTGatewayAPI::ChartRequest](../Gateway-API/Main-Interface/History-Data/ChartRequest.md)
  * [IMT](../Gateway-API/Main-Interface/History-Data/ChartDelete.md)[Gateway](../Gateway-API/Main-Interface/History-Data/ChartRequest.md)[API::ChartDelete](../Gateway-API/Main-Interface/History-Data/ChartDelete.md)
  * [IMT](../Gateway-API/Main-Interface/History-Data/ChartUpdate.md)[Gateway](../Gateway-API/Main-Interface/History-Data/ChartRequest.md)[API::ChartUpdate](../Gateway-API/Main-Interface/History-Data/ChartUpdate.md)
  * [IMTReportAPI::ChartHistoryGet](../Report-API/Main-Interface-of-Reports/Price-Data/ChartHistoryGet.md)
  * [IMTServerAPI::ChartGet](../Server-API/Main-API-Interface/History-Data/ChartGet.md)
  * [IMTServerAPI::ChartDelete](../Server-API/Main-API-Interface/History-Data/ChartDelete.md)
  * [IMTServerAPI::ChartUpdate](../Server-API/Main-API-Interface/History-Data/ChartUpdate.md)



The structure contains the following parameters:

Field | Type | Description  
datetime | INT64 | Date and time of a bar in seconds that have elapsed since 01.01.1970.  
open | double | Bar open price — price at the beginning of bar formation (beginning of a minute).  
high | double | The highest price inside the bar.  
low | double | The lowest price inside the bar.  
close | double | Bar close price — price at the end of bar formation (end of the minute).  
tick_volume | UINT64 | Tick volume — number of ticks received during bar formation. The variable only counts the ticks that change the price based on which the bar is constructed (Bid or Last, depending on symbol settings). Several ticks in a row with the same price will be counted as one.  
spread | INT32 | The lowest symbol spread recorded during the bar formation time.  
volume | UINT64 | The real volume of trades executed during bar formation.  
  
For more information about working with price data in the platform, please see the [Price Data](https://support.metaquotes.net/en/docs/mt5/platform/administration/common_info/price_data) and [Charts](https://support.metaquotes.net/en/docs/mt5/platform/administration/admin_charts) sections.

```

---

<a id='mteconomicevent-md'></a>
### 21. `MTEconomicEvent.md`

```markdown
[🏠 Document Start](../README.md) / [Structures](README.md) / MTEconomicEvent

[Previous](MTNews.md) | [Next](MTReportInfo.md)

<a id="mteconomicevent"></a>
# MTEconomicEvent (#mteconomicevent)

The structure of the event (news) of an economic calendar is described in MTEconomicEvent. The structure is defined with the one-byte alignment.
    
    
    #pragma pack(push,1)
    struct MTEconomicEvent
      {
       //--- Flags
       enum EnEconomicEventPriority
         {
          PRIORITY_LOW =0,                                       // Low priority of an event
          PRIORITY_NORMAL =1,                                    // Normal priority of an event
          PRIORITY_HIGH =2                                       // High priority of an event
         };
       INT64             eventtime;                              // Date and time of an event
       wchar_t           name[128];                              // Event name
       wchar_t           currency[32];                           // Event currency
       UINT              priority;                               // Event priority
       wchar_t           period[128];                            // Event frequency
       wchar_t           val_previous[32];                       // Previous value
       wchar_t           val_forecast[32];                       // Predicted value
       wchar_t           val_actual[32];                         // Current value
       UINT              reserved[64];                           // Reserved field
      };
    #pragma pack(pop)

This structure is used in the [IMTGatewayAPI::SendEconomicEvents](../Gateway-API/Main-Interface/Quote-and-News-Feeds/SendEconomicEvents.md) method.

<a id="enumerations"></a>
## Enumerations (#enumerations)

The structure contains one enumeration:

<a id="eneconomiceventpriority"></a>
### EnEconomicEventPriority (#eneconomiceventpriority)

Flags of events of the economic calendar are listed in EnEconomicEventPriority:

ID | Value | Description  
PRIORITY_LOW | 0 | Low priority of an event. The event priority is shown with icons in terminals.  
PRIORITY_NORMAL | 1 | Normal priority of an event.  
PRIORITY_HIGH | 2 | High priority of an event.  
  
<a id="parameters"></a>
## Parameters (#parameters)

The MTEconomicEvent structure contains the following parameters:

Field | Type | Description  
eventtime | INT64 | Date and time of an event in seconds that have elapsed since 01.01.1970.  
name | wchar_t | Event name.  
currency | wchar_t | The currency of the country/region of the economic event;  
priority | UINT | Event priority. Transfered using the MTEconomicEvent::EnEconomicEventPriority enumeration.  
period | wchar_t | Period, for which the economic indicator is released, or its release date.  
val_previous | wchar_t | Previous value of the indicator. To specify an empty value an empty string is specified.  
val_forecast | wchar_t | Predicted value of the indicator. To specify an empty value an empty string is specified.  
val_actual | wchar_t | Current value of the indicator. To specify an empty value an empty string is specified.  
reserved | UINT | A reserved field for future use.

```

---

<a id='mtgatewayinfo-md'></a>
### 21. `MTGatewayInfo.md`

```markdown
[🏠 Document Start](../README.md) / [Structures](README.md) / MTGatewayInfo

[Previous](MTBookMTBookDiff.md) | [Next](MTNews.md)

<a id="mtgatewayinfo"></a>
# MTGatewayInfo (#mtgatewayinfo)

MTGatewayInfo structure is used for setting a gateway/data feed module parameters. The structure is defined with the one-byte alignment.
    
    
    #pragma pack(push,1)
    struct MTGatewayInfo
      {
       //--- Gateway/data feed module operation modes
       enum EnModes
         {
          GATEWAY_MODE_QUOTES     =1,                            // Receiving quotes
          GATEWAY_MODE_NEWS       =2,                            // Receiving news
          GATEWAY_MODE_POSITIONS  =4,                            // Ability to get the state of positions
          GATEWAY_MODE_NONE       =0,
          GATEWAY_MODE_ALL        =GATEWAY_MODE_QUOTES|GATEWAY_MODE_NEWS|GATEWAY_MODE_POSITIONS
         };
       //--- Flags of the fields available for setting
       enum EnFields
         {
          GATEWAY_FIELD_SERVER    =1,                            // The Server field
          GATEWAY_FIELD_LOGIN     =2,                            // The Login field
          GATEWAY_FIELD_PASSWORD  =4,                            // The Password field
          GATEWAY_FIELD_PARAMS    =8,                            // The Parameters field
          GATEWAY_FIELD_NONE      =0,
          GATEWAY_FIELD_ALL       =GATEWAY_FIELD_SERVER|GATEWAY_FIELD_LOGIN|GATEWAY_FIELD_PASSWORD|GATEWAY_FIELD_PARAMS
         };
       //--- Gateway/data feed module description
       UINT              version;                                // Gateway/data feed version
       UINT              version_api;                            // Gateway API version
       wchar_t           name_default[128];                      // Default name
       wchar_t           copyright[128];                         // Copyright
       wchar_t           server_default[128];                    // Default server address
       wchar_t           login_default[64];                      // Default login
       wchar_t           password_default[64];                   // Default password
       wchar_t           parameters_default[512];                // Default additional parameters
       UINT              mode;                                   // Operation mode
       UINT              fields;                                 // Mandatory fields
       wchar_t           description[512];                       // Description
       wchar_t           module_id[16];                          // Gateway module identifier
       wchar_t           build_date[16];                         // Build date of the gateway/data feed
       wchar_t           build_api_date[16];                     // Build date of Gateway API
       UINT              reserved[32];                           // Reserved field
      };
    #pragma pack(pop)

<a id="enumerations"></a>
## Enumerations (#enumerations)

This structure contains the following enumerations:

  * EnModes
  * EnFields



<a id="enmodes"></a>
### EnModes (#enmodes)

Gateway operation modes are described in EnModes:

ID | Value | Description  
GATEWAY_MODE_QUOTES | 1 | Gateway/data feed can transmit the quotes.  
GATEWAY_MODE_NEWS | 2 | Gateway/data feed can transmit the news.  
GATEWAY_MODE_POSITIONS | 4  | The gateway supports [requesting the state of external trading system positions](../Gateway-API/Main-Interface/Controlling-Positions-in-External-System.md). The request can be made from "Positions" tab of the gateway in MetaTrader 5 Administrator.  
GATEWAY_MODE_NONE | 0 | Beginning of enumeration. It corresponds to the absence of any operation modes.  
GATEWAY_MODE_ALL |  | End of enumeration. It corresponds to the support of all operation modes.  
  
<a id="enfields"></a>
### EnFields (#enfields)

EnFields contains descriptions of the flags of the fields that will be available for a gateway/data feed setting through MetaTrader 5 Administrator:

ID | Value | Description  
GATEWAY_FIELD_SERVER | 1 | The field of the address of an external server for connection.  
GATEWAY_FIELD_LOGIN | 2 | Login field.  
GATEWAY_FIELD_PASSWORD | 4  | Password field.  
GATEWAY_FIELD_PARAMS | 8 | Additional external parameters.  
GATEWAY_FIELD_NONE | 0 | Beginning of enumeration. It corresponds to the absence of required fields.  
GATEWAY_FIELD_ALL |  | End of enumeration. Corresponds to enabling of all fields.  
  
<a id="parameters"></a>
## Parameters (#parameters)

MTGatewayInfo structure contains the following parameters:

Field | Type | Description  
version | UINT | In this parameter information about the gateway/data feed module version is passed to the server. Information about the build number and date of the application and of the used Gateway API will be displayed on the Staus page of gateways and data feeds in MetaTrader 5 Administrator.  
version_API | UINT | This field is used to pass the version of Gateway API, in which the gateway/data feed has been compiled. Filled with a value of MTGatewayAPIVersion specified MT5APIGateway.h by default. Required parameter.  
name | wchar_t | This parameter serves for passing the name that is placed in the configuration by default during the selection of a gateway/data feed module in the "File" field of MetaTrader 5 Administrator.  
copyright | wchar_t | This parameter is used to pass the copyright. Copyright is shown on the ["Information"](../Gateway-API/Main-Interface/External-Connection-State.md) tab of the gateway/data feed in MetaTrader 5 Administrator.  
server_default | wchar_t | This parameter serves for passing the server address (in address:port format) that is placed in the configuration by default during the selection of a gateway/data feed module in the "File" field.  
login_default | wchar_t | This parameter serves for passing the login that is placed in the configuration by default during the selection of a gateway/data feed module in the "File" field.  
password_default | wchar_t | This parameter serves for passing the password that is placed in the configuration by default during the selection of a gateway/data feed module in the "File" field.  
parameters_default | wchar_t | This parameter serves for passing the parameters that are placed in the configuration by default during the selection of a gateway/data feed module in the "File" field. The parameters are passed in the following format: Parameter1=Value1\\\nParameter2=Value2\\\n...\\\nParametrN=ValueN\\\n. For example: | TradingCalendarHolidays=\\\nFIXTargetCompId=\\\nFIXSenderCompId=\\\nFIXSenderSubId=\\\nFIXDeliverToCompID=\\\nLimitOrdersCoverage=Gateway  
\\\nStopOrdersCoverage=N\\\nLimitOrdersCoverageTimeout=5\\\nWeekTimeBegin=17:00\\\nWeekTimeEnd=17:00\\\nMinQtySet=N\nFIXQuotesLogEnabled=N\\\n  
---  
  
mode | UINT | Gateway/data feed operation modes are passed in this field. To pass the options, the EnModes enumeration is used.  
fields | UINT | Flags of the fields available for a gateway/data feed setting in MetaTrader 5 Administrator are passed in this field. To pass the options, the EnFields enumeration is used.  
description | wchar_t | This parameter is used to pass the gateway/data feed module description. Description is shown on the ["Information"](../Gateway-API/Main-Interface/External-Connection-State.md) Description is shown on the.  
module_id | wchar_t | Identifier of the gateway module. It used to bind deals to a specific gateway ([IMTDeal::Gateway](../Database-Interfaces/Trade/Deals/IMTDeal/Gateway.md)). For example, if several instances (configurations) of the same gateway are created within the trading platform, deals processed by that gateway instances can be grouped by this identifier in reports. The field is required.  
build_date | wchar_t | The build date of the gateway/data feed.  
build_api_date | wchar_t | The build date of the Gateway API, that was used to create the current version of the gateway/data feed. Filled with a value of MTGatewayAPIDate specified MT5APIGateway.h by default.  
reserved | UINT | A reserved field for future use.

```

---

<a id='mtlicensecheck-md'></a>
### 21. `MTLicenseCheck.md`

```markdown
[🏠 Document Start](../README.md) / [Structures](README.md) / MTLicenseCheck

[Previous](MTProxyInfo.md) | [Next](MTTick.md)

# MTLicenseCheck

The MTLicenseCheck structure is used for checking the license. The structure is defined with the one-byte alignment.
    
    
    #pragma pack(push,1)
    struct MTLicenseCheck
      {
       wchar_t           name[128];                             // Name of the license
       int               data_reserved[128];                    // A reserved field for future use
       char              random[256];                           // A random sequence for signature verification
       UINT              random_size;                           // Size of the random sequence
       MTAPIRES          retcode;                               // Result of the license check
       int               result_reserved[128];                  // A reserved field for future use
       char              sign[1024];                            // Signature of the license check results
       UINT              sign_size;                             // Size of the signature to check the license
       int               sign_reserved[64];                     // A reserved field for future use
      };
    #pragma pack(pop)

This structure is used in the following methods:

  * [IMTAdminAPI::LicenseCheck](../Manager-API/Administrator-Interface/Common-Functions/LicenseCheck.md)
  * [IMTManagerAPI::LicenseCheck](../Manager-API/Manager-Interface/Common-Functions/LicenseCheck.md)
  * [IMTGatewayAPI::LicenseCheck](../Gateway-API/Main-Interface/Common-Functions/LicenseCheck.md)



The structure contains the following parameters:

Field | Type | Description  
name | wchar_t | License name. It is filled in by a programmer before the call of LicenseCheck.  
data_reserved | int | A reserved field for future use.  
random | char | A random sequence to check the license. It is filled in by a programmer before the call of LicenseCheck. The length of the random sequence must be at least 64 bytes.  
random_size | UINT | The size of a random sequence. It is filled in by a programmer before the call of LicenseCheck.  
retcode | MTAPIRES | The result of license verification. It is filled in by a MetaTrader 5 server after the call of LicenseCheck.  
result_reserved | int | A reserved field for future use.  
sign | char | Signature of the license check results. It is filled in by a MetaTrader 5 server after the call of LicenseCheck.  
sign_size | UINT | The size of the signature to check the license. It is filled in by a MetaTrader 5 server after the call of LicenseCheck.  
sign_reserved | int | A reserved field for future use.  
  
> [Server API](../Server-API/Main-API-Interface/Common-Functions/LicenseCheck.md) and [Report API](../Server-API/Main-API-Interface/Common-Functions/LicenseCheck.md) also provide the possibility to control the licenses using LicenseCheck methods; MTLicenseCheck structure is not used in them, only the license name is passed. Plugins and reports work directly on the server, and thus they do not need to transmit data over the network to verify the license. Therefore, there is no need to additionally sign data using random sequences.

```

---

<a id='mtlogrecord-md'></a>
### 21. `MTLogRecord.md`

```markdown
[🏠 Document Start](../README.md) / [Structures](README.md) / MTLogRecord

[Previous](MTMailRange.md) | [Next](MTChartBar.md)

# MTLogRecord

This structure describes the [Server log](../Manager-API/Administrator-Interface/Common-Functions.md) entry. The structure is defined with the one-byte alignment.
    
    
    #pragma pack(push,1)
    struct MTLogRecord
      {
       UINT              flags;                                  // Flags EnMTLogFlags
       UINT              code;                                   // Message types EnMTLogCode
       INT               type;                                   // Types of events EnMTLogType
       INT64             datetime;                               // Date and time in seconds
       wchar_t           source[64];                             // Source
       wchar_t           message[512];                           // Message text
       INT64             datetime_msc;                           // Date and time in milliseconds
       int               reserved[2];                            // A reserved field
      };
    #pragma pack(pop)

This structure is used in the following methods:

  * [IMTAdminAPI::LoggerServerRequest](../Manager-API/Administrator-Interface/Common-Functions/LoggerServerRequest.md)
  * [IMTManagerAPI::LoggerServerRequest](../Manager-API/Manager-Interface/Common-Functions/LoggerServerRequest.md)
  * [IMTReportAPI::LoggerRequest](../Report-API/Main-Interface-of-Reports/Common-Functions/LoggerRequest.md)
  * [IMTServerAPI::LoggerRequest](../Server-API/Main-API-Interface/Common-Functions/LoggerRequest.md)



The structure contains the following parameters:

Field | Type | Description  
flags | UINT | Log [entry flags (#enmtlogflags)](../Journal-Constants/README.md#enmtlogflags).  
code | UINT | Log [message type (#enmtlogcode)](../Journal-Constants/README.md#enmtlogcode).  
type | INT | [Event type (#enmtlogtype)](../Journal-Constants/README.md#enmtlogtype).  
datetime | INT64 | Date and time of a message in seconds that have elapsed since 01.01.1970.  
source | wchar_t | Source of the message.  
message | wchar_t | Message text.  
datetime_msc | INT64 | Date and time of a message in milliseconds that have elapsed since 01.01.1970.  
reserved | int | A reserved parameter.

```

---

<a id='mtmailrange-md'></a>
### 21. `MTMailRange.md`

```markdown
[🏠 Document Start](../README.md) / [Structures](README.md) / MTMailRange

[Previous](MTTickStat.md) | [Next](MTLogRecord.md)

# MTMailRange

This structure is used to describe the range of recipients of the mailing list. The structure is defined with the one-byte alignment.
    
    
    #pragma pack(push,1)
    struct MTMailRange
      {
       UINT64            first_login;                           // The first login in the range
       UINT64            last_login;                            // The last login in the range
       UINT              reserved[4];                           // A reserved field
      };
    #pragma pack(pop)

This structure is used in the following methods:

  * [IMTMail::ToRangesAdd](../Database-Interfaces/Mail-Database/IMTMail/ToRangesAdd.md)
  * [IMTMail::ToRangesNext](../Database-Interfaces/Mail-Database/IMTMail/ToRangesNext.md)



The structure contains the following parameters:

Field | Type | Description  
first_login | UINT64 | A login with which the range of the mailing list begins.  
last_login | UINT64 | A login with which the range of the mailing list ends.  
reserved | UINT | A reserved field for future use.

```

---

<a id='mtnews-md'></a>
### 21. `MTNews.md`

```markdown
[🏠 Document Start](../README.md) / [Structures](README.md) / MTNews

[Previous](MTGatewayInfo.md) | [Next](MTEconomicEvent.md)

<a id="mtnews"></a>
# MTNews (#mtnews)

The news structure is described in MTNews. The structure is defined with the one-byte alignment.
    
    
    #pragma pack(push,1)
    struct MTNews
      {
       //--- Constants
       enum constants
         {
          MAX_NEWS_BODY_LEN=1024*1024                           // max. body length
         };
       //--- News flags
       enum EnNewsFlags
         {
          FLAG_PRIORITY    =1,                                  // Priority flag
          FLAG_CALENDAR    =2                                   // Calendar news flag
          FLAG_MIME        =4,                                  // MIME content flag
          FLAG_CALENDAR    =8                                   // Flag to allow full news
         };
       UINT              language;                              // Language
       wchar_t           subject[256];                          // News subject
       wchar_t           category[256];                         // News category
       UINT              flags;                                 // News flags
       wchar_t          *body;                                  // Body
       UINT              body_len;                              // Body length
       UINT              languages_list[32];                    // The list of languages
       INT64             datetime;                              // Publication time
       UINT              reserved[64];                          // A reserved field
      };
    #pragma pack(pop)

This structure is used in the [IMTGatewayAPI::SendNews](../Gateway-API/Main-Interface/Quote-and-News-Feeds/SendNews.md) method.

<a id="enumerations"></a>
## Enumerations (#enumerations)

The following enumerations are described in the structure:

  * constants
  * EnNewsFlags



<a id="constants"></a>
### constants (#constants)

Used constants are described in this enumeration.

ID | Value | Description  
MAX_NEWS_BODY_LEN | 1024*1024 | The maximum allowable news size.  
  
<a id="ennewsflags"></a>
### EnNewsFlags (#ennewsflags)

News flags are listed in EnNewsFlags.

ID | Value | Description  
FLAG_PRIORITY | 1 | If the flag is set, the newsletter appears as important.  
FLAG_CALENDAR | 2 | If this flag is enabled, the news should be formed as an element of the economic calendar. At the moment, the flag is obsolete and supported only for backward compatibility. For the the economic calendar, one should use structure [MTEconomicEvent](MTEconomicEvent.md) and method [IMTGatewayAPI::SendEconomicEvents](../Gateway-API/Main-Interface/Quote-and-News-Feeds/SendEconomicEvents.md).  
FLAG_MIME | 4  | This flag determines how the news is interpreted. If there is no flag, the news is considered to have the UTF-16 encoding. If the flag is not set, the news is believed to be in UTF-16. If the flag is enabled, the news is believed to be in UTF-8. Regardless of the news encoding, the news length (body_len) must be specified in the number of wchart_t characters.  
FLAG_ALLOW_DEMO | 8 | Enabling this flag allow receiving the news entirely (including the body) for the groups that are allowed to receive news headers only ([EnNewsMode::NEWS_MODE_HEADERS (#ennewsmode)](../Configuration-Interfaces/Groups/IMTConGroup/Enumerations.md#ennewsmode)).  
  
<a id="parameters"></a>
## Parameters (#parameters)

MTNews structure contains the following parameters:

Field | Type | Description  
language | UINT | News language. Specified in the standard used in [MS Windows](https://msdn.microsoft.com/en-us/library/windows/desktop/dd318693) (a value from Prim.lang.identifier). The language code can also be retrieved using the WinAPI function:   
LCID LocaleNameToLCID(LPCWSTR lpName,DWORD dwFlags); The language ID is stored in the last two bytes of a received LCID.  
subject | wchar_t | The news subject in the UTF-16 encoding. An example of copying a news subject:   
CMTStr::Copy(news.subject,L"Asia stocks, euro hit as ECB takes hard line on Greek debt");  
category | wchar_t | The category in UTF-16, to which the news belongs. The tree structure of the news categories is created automatically on the client terminal side. A separator character '\' is used for dividing categories into subcategories. An example of news category:   
CMTStr::Copy(news.category,L"Markets\\\ Asian Markets News");  
flags | UINT | News flags. Specified using the EnNewsFlags enumeration.  
body | wchar_t | News body. The memory for a news body is reserved and prepared by a programmer. HTML is supported in newsletter. To send an HTML newsletter, start its body with the <html> tag and end with the </html> tag.  
body_len | UINT | News size. Limited by a value of MAX_NEWS_BODY_LEN.For example, if FLAG_MIME is ysed and the MIME size of the news is 800*1024 bytes, then in body_len one should specify (800*1024)/sizeof(wchar_t) = 400*1024 symbols.  
languages_list | UINT | An array containing the list of languages. The language is used to filter news when receiving them in terminals (in the settings of the terminal one can select news in what languages should be received) and when sending them to different client [groups](../Configuration-Interfaces/Groups/IMTConGroup/NewsLangAdd.md). The language is specified in the LANGID format used in [MS Windows](https://msdn.microsoft.com/en-us/library/windows/desktop/dd318693) systems (a value from Prim.lang.identifier).  
datetime | INT64 | The date/time of the news release in the number of seconds since January 01, 1970. This date is displayed in the "Time" filed of a newsletter in client terminals. The date/time value should be specified in the time zone of the trade server. Time zone parameters are passed to a data feed in a command line when the application is run. Command line parameter: /timezone:<time zone in minutes>, /timecorrect (if the parameter is set, daylight saving time correction should be taken into account).  
reserved | UINT | A reserved field for future use.

```

---

<a id='mtplugininfo-md'></a>
### 21. `MTPluginInfo.md`

```markdown
[🏠 Document Start](../README.md) / [Structures](README.md) / MTPluginInfo

[Previous](MTReportServerInfo.md) | [Next](MTPluginParam.md)

# MTPluginInfo

The MTPluginInfo structure is used for transmitting the primary data of a plugin to a server. The structure is defined with the one-byte alignment.
    
    
    #pragma pack(push,1)
    struct MTPluginInfo
      {
       UINT              version;                               // Plugin Version
       UINT              version_api;                           // Server API version
       wchar_t           name[64];                              // Name of the plugin
       wchar_t           copyright[128];                        // Copyright
       wchar_t           description[256];                      // Description
       MTPluginParam     defaults[128];                         // Default parameters
       UINT              defaults_total;                        // Number of default parameters
       UINT              reserved[128];                         // A reserved field
      };
    #pragma pack(pop)

The structure is passed to the server via the entry point [MTServerAbout](../Server-API/Entry-Points/MTServerAbout.md). It contains the following parameters:

Field | Type | Description  
version | UINT | In this parameter, information about the plugin version is passed to the server.  
version_API | UINT | This field is used to pass the version of the Server API, in which the plugin has been compiled.  
name | wchar_t | This parameter is used to pass the name of the plugin.  
copyright | wchar_t | This parameter is used to pass the copyright.  
description | wchar_t | This parameter is used to pass the plugin description.  
defaults | MTPluginParam | An array of default parameters described by the [MTPluginParam](MTPluginParam.md) structure.  
defaults_total | UINT | The total number of passed default parameters.  
reserved | UINT | A reserved field for future use.

```

---

<a id='mtpluginparam-md'></a>
### 21. `MTPluginParam.md`

```markdown
[🏠 Document Start](../README.md) / [Structures](README.md) / MTPluginParam

[Previous](MTPluginInfo.md) | [Next](MTServerInfo.md)

# MTPluginParam

This structure is used for describing default parameters of a plugin. Default parameters are passed through the default parameter of the [MTPluginInfo](MTPluginInfo.md) structure. The MTPluginParam structure is defined with the one-byte alignment.
    
    
    #pragma pack(push,1)
    struct MTPluginParam
      {
       //--- parameter types
       enum EnParamType
         {
          TYPE_STRING    =0,                                     // String
          TYPE_INT       =1,                                     // Integer
          TYPE_FLOAT     =2,                                     // Floating-point number
          TYPE_TIME      =3,                                     // Time
          TYPE_DATE      =4,                                     // Date
          TYPE_DATETIME  =5,                                     // Date and time
          TYPE_GROUPS    =6,                                     // List of groups
          TYPE_SYMBOLS   =7,                                     // List of symbols
          TYPE_BOOL      =8,                                     // Boolean
          //---
          TYPE_FIRST     =TYPE_STRING,
          TYPE_LAST      =TYPE_BOOL
         };
       //---
       UINT              type;                                   // Parameter type (EnParamType)
       wchar_t           name[64];                               // Parameter name
       wchar_t           value[256];                             // Parameter value
       UINT              reserved[16];                           // Reserved field
      };
    #pragma pack(pop)

The MTPluginParam structure contains the EnParamType enumeration that contains description of possible types of parameters:

ID | Value | Description  
TYPE_STRING | 0 | A string parameter.  
TYPE_INT | 1 | An integer parameter.  
TYPE_FLOAT | 2 | A floating-point number.  
TYPE_TIME | 3 | A parameter, in which time is specified (HH:MM:SS).  
TYPE_DATE | 4  | A parameter, in which date is specified (YYYY.MM.DD).  
TYPE_DATETIME | 5 | A parameter, in which date and time are specified (YYYY.MM.DD HH:MM:SS).  
TYPE_GROUPS | 6 | List of groups.  
TYPE_SYMBOLS | 7 | List of symbols.  
TYPE_BOOL | 8 | A boolean parameter.  
TYPE_FIRST |  | Beginning of enumeration. It corresponds to TYPE_STRING.  
TYPE_LAST |  | End of enumeration. It corresponds to TYPE_BOOL.  
  
The structure contains the following parameters:

Field | Type | Description  
type | UINT | Parameter type. To pass the type, the EnParamType enumeration is used.  
name | wchar_t | The name of the parameter.  
value | wchar_t | The value of the parameter.  
reserved | UINT | A reserved field for future use.

```

---

<a id='mtproxyinfo-md'></a>
### 21. `MTProxyInfo.md`

```markdown
[🏠 Document Start](../README.md) / [Structures](README.md) / MTProxyInfo

[Previous](README.md) | [Next](MTLicenseCheck.md)

# MTProxyInfo

The MTProxyInfo structure is used for passing parameters of a proxy server. The structure is defined with the one-byte alignment.
    
    
    #pragma pack(push,1)
    struct MTProxyInfo
      {
       //--- Types of proxy servers
       enum
         {
          PROXY_SOCKS4   =0,                                     // SOCKS4
          PROXY_SOCKS5   =1,                                     // SOCKS5
          PROXY_HTTP     =2,                                     // HTTP (including NTLM)
          PROXY_FIRST    =PROXY_SOCKS4,                          // First type
          PROXY_LAST     =PROXY_HTTP                             // Last type
         };
       //--- Description of a proxy server
       int               enable;                                 // Flag of proxy server using
       int               type;                                   // Type of a proxy server
       wchar_t           address[64];                            // IP-address:Port of a proxy server
       wchar_t           auth[64];                               // Login:Password
      };
    #pragma pack(pop)

This structure is used in the following methods:

  * [IMTAdminAPI::ProxySet](../Manager-API/Administrator-Interface/Connection-to-the-Server/ProxySet.md)
  * [IMTManagerAPI:ProxySet](../Manager-API/Manager-Interface/Connection-to-the-Server/ProxySet.md)



This structure contains an enumeration, in which types of proxy servers passed in the type parameter are described:

ID | Value | Description  
PROXY_SOCKS4 | 0 | Type SOCKS4.  
PROXY_SOCKS5 | 1 | Type SOCKS5.  
PROXY_HTTP | 2 | Type HTTP, including NTLM authentication.  
PROXY_FIRST |  | Beginning of enumeration. Corresponds to PROXY_SOCKS4.  
PROXY_LAST |  | End of enumeration. Corresponds to PROXY_HTTP.  
  
The structure contains the following parameters:

Field | Type | Description  
enable | int | A flag of connection through a proxy server. 0 — proxy server is not used, 1 — connection through a proxy server.  
type | int | Proxy server type passed using the enumeration described above.  
address | wchart_t | The IP address of the proxy server and the port number separated by a colon. For example, 192.168.0.1:3180.  
auth | wchart_t | The login and password for connecting to the proxy server, separated by a colon.

```

---

<a id='mtreportinfo-md'></a>
### 21. `MTReportInfo.md`

```markdown
[🏠 Document Start](../README.md) / [Structures](README.md) / MTReportInfo

[Previous](MTEconomicEvent.md) | [Next](MTReportParam.md)

<a id="mtreportinfo"></a>
# MTReportInfo (#mtreportinfo)

The MTReportInfo structure is used for transmitting the primary data of a reports module to a server. The structure is defined with the one-byte alignment.
    
    
    #pragma pack(push,1)
    struct MTReportInfo
      {
       //--- databases snapshots flags
       enum EnSnapshots
         {
          SNAPSHOT_NONE          =0x0,                          // Without a snapshot
          SNAPSHOT_USERS         =0x1,                          // Requested users database snapshot
          SNAPSHOT_USERS_FULL    =0x2,                          // A snapshot of the entire database of users
          SNAPSHOT_ACCOUNTS      =0x4,                          // Requested accounts state snapshot
          SNAPSHOT_ACCOUNTS_FULL =0x8,                          // A snapshot of the entire database of trading accounts
          SNAPSHOT_ORDERS        =0x10,                         // Requested orders database snapshot
          SNAPSHOT_ORDERS_FULL   =0x20,                         // A snapshot of the entire database of orders
          SNAPSHOT_POSITIONS     =0x40,                         // Requested positions database snapshot
          SNAPSHOT_POSITIONS_FULL=0x80,                         // A snapshot of the entire database of positions
          SNAPSHOT_NO_GROUPS_LOGINS=0x100,                      // Do not form a list of logins by groups
          //---
          SNAPSHOT_ALL =SNAPSHOT_USERS|SNAPSHOT_ACCOUNTS|SNAPSHOT_ORDERS|SNAPSHOT_POSITIONS,
          SNAPSHOT_ALL_FULL =SNAPSHOT_USERS_FULL|SNAPSHOT_ACCOUNTS_FULL|SNAPSHOT_ORDERS_FULL|SNAPSHOT_POSITIONS_FULL, 
         };
       //--- Types of reports
       enum EnTypes
         {
          TYPE_NONE              =0x0,                          // Reports are not supported
          TYPE_HTML              =0x1,                          // HTML report
          TYPE_TABLE             =0x2,                          // Binary table
          //---
          TYPE_ALL               =TYPE_HTML|TYPE_TABLE
         };
       //--- Internet Explorer minimum version
       enum EnIEVersion
         {
          IE_VERSION_ANY         =0x0000,                       // Any version of IE
          IE_VERSION_9           =0x0900,                       // not older than IE 9
          //---
          IE_VERSION_FIRST       =IE_VERSION_ANY,
          IE_VERSION_LAST        =IE_VERSION_9,
         };
       //--- Information about the module
       UINT              version;                               // Module version
       UINT              version_api;                           // Report API version
       UINT              version_ie;                            // IE minimum version
       wchar_t           name[64];                              // Module name
       wchar_t           copyright[128];                        // Copyright
       wchar_t           description[256];                      // Description
       UINT              snapshots;                             // Snapshots modes
       UINT              types;                                 // Types of reports
       wchar_t           category[64];                          // Report category
       MTReportParam     params[64];                            // Parameters of request
       UINT              params_total;                          // Number of request parameters
       MTReportParam     config[64];                            // Module parameters
       UINT              config_total;                          // Number of module parameters
       UINT              reserved[64];                          // A reserved field
      };
    #pragma pack(pop)

The structure is passed to the server via the [MTReportAbout](../Report-API/Entry-Points/MTReportAbout.md) entry point.

<a id="enumerations"></a>
## Enumerations (#enumerations)

The structure contains the following enumerations:

  * EnSnapshots
  * EnTypes
  * EnIEVersion



<a id="ensnapshots"></a>
### EnSnapshots (#ensnapshots)

Possible modes for creating snapshots of databases when generating reports are enumerated in EnSnapshots. Database snapshots allow you to quickly save a particular database, which helps to avoid the discrepancy between the beginning and end of the report that may occur due to changes in the market environment during the report generation time.

ID | Value | Description  
SNAPSHOT_NONE | 0x0 | No snapshots.  
SNAPSHOT_USERS | 0x1 | A snapshot of the database of users [requested by a manager](../Report-API/Request-for-Reports.md) during report generation. To request a report by groups/users, the report module must have the [MTReportParam::TYPE_GROUPS (#enparamtype)](MTReportParam.md#enparamtype) parameter turned on.  
SNAPSHOT_USERS_FULL | 0x2 | A snapshot of the entire database of users.  
SNAPSHOT_ACCOUNTS | 0x4 | A snapshot of the database of trading accounts requested by a manager during report generation. To request a report by groups/users, the report module must have the [MTReportParam::TYPE_GROUPS (#enparamtype)](MTReportParam.md#enparamtype) parameter enabled.  
SNAPSHOT_ACCOUNTS_FULL | 0x8 | A snapshot of the entire database of trading accounts.  
SNAPSHOT_ORDERS | 0x10 | A snapshot of the database of orders of clients requested by a manager during report generation. To request a report by groups/users, the report module must have the [MTReportParam::TYPE_GROUPS (#enparamtype)](MTReportParam.md#enparamtype) parameter enabled.  
SNAPSHOT_ORDERS_FULL | 0x20 | A snapshot of the entire database of orders.  
SNAPSHOT_POSITIONS | 0x40 | A snapshot of the database of positions of clients requested by a manager during report generation. To request a report by groups/users, the report module must have the [MTReportParam::TYPE_GROUPS (#enparamtype)](MTReportParam.md#enparamtype) parameter enabled.  
SNAPSHOT_POSITIONS_FULL | 0x80 | A snapshot of the entire database of positions.  
SNAPSHOT_NO_GROUPS_LOGINS | 0x100 | Disable automatic generation of a list of logins if a list of groups is passed in a report request. Many reports available in the platform package use the standard "Groups" parameter, indicating the list of groups for which a report should be generated. Every time when a report is generated with this parameter, the API generates the appropriate list of logins (it can be obtained via the [IMTReportAPI::ParamLogins](../Report-API/Main-Interface-of-Reports/Report-Parameters/ParamLogins.md) and [IMTReportAPI::KeySetParamLogins](../Report-API/Main-Interface-of-Reports/Data-cache/KeySetParamLogins.md) methods). This is a time consuming operation. If your report can handle the "Groups" parameter directly, disabled the generation of the list of logins using the SNAPSHOT_NO_GROUPS_LOGINS flag and save computing resources.  
SNAPSHOT_ALL |  | Enabling all eased snapshots of databases (only the data requested by a manager).  
SNAPSHOT_ALL_FULL |  | Enabling all full snapshots of databases (*_FULL).  
  
<a id="entypes"></a>
### EnTypes (#entypes)

Types of reports that can be supported by the module are enumerated in EnTypes:

ID | Value | Description  
TYPE_NONE | 0x0 | None of the types is supported.  
TYPE_HTML | 0x1 | Generation of HTML reports.  
TYPE_TABLE | 0x2 | Generation of reports as binary tables.  
TYPE_ALL |  | All types of reports are supported.  
  
This enumeration is used in the [IMTReportContext::Generate](../Report-API/Report-Plugin-Interface/Generate.md) method.

<a id="enieversion"></a>
### EnIEVersion (#enieversion)

Internet Explorer minimum version is indicated using EnIEVersion for correct display of HTML reports.

ID | Value | Description  
IE_VERSION_ANY | 0x0000 | Any Internet Explorer version is supported.  
IE_VERSION_9 | 0x0900 | Internet Explorer version should be no older than 9.  
IE_VERSION_FIRST |  | Beginning of enumeration. Corresponds to IE_VERSION_ANY.  
IE_VERSION_LAST |  | End of enumeration. Corresponds to IE_VERSION_9.  
  
<a id="parameters"></a>
## Parameters (#parameters)

The structure contains the following parameters:

Field | Type | Description  
version | UINT | In this parameter, information about the reports module version is passed to the server.  
version_api | UINT | This field is used to pass the version of the Report API, in which the module has been compiled.  
version_ie | UINT | The Internet Explorer minimum version is passed in this field for the correct display of reports. To pass the version, the EnIEVersion enumeration is used.  
name | wchar_t | This parameter is used to pass the name of the module.  
copyright | wchar_t | This parameter is used to pass the copyright.  
description | wchar_t | This parameter is used to pass the module description.  
snapshots | UINT | Databases snapshots flags are passed in this parameter. To pass the options, the EnSnapshots enumeration is used.  
types | UINT | Reports types supported by the module are passed in this parameter. EnTypes enumeration is used for passing.  
category | wchar_t | Report category. It is used for grouping reports in a tree view in the Manager and Administrator terminals.  
params | MTReportParam | The array of the reports request parameters from this module. The parameters are described by the [MTReportParam](MTReportParam.md) structure.  
params_total | UINT | The total number of request parameters.  
config | MTReportParam | The array of external module parameters that can be changed during the configuration in MetaTrader 5 Administrator. The parameters are described by the [MTReportParam](MTReportParam.md) structure.  
config_total | UINT | The total number of external parameters.  
reserved | UINT | A reserved field for future use.

```

---

<a id='mtreportparam-md'></a>
### 21. `MTReportParam.md`

```markdown
[🏠 Document Start](../README.md) / [Structures](README.md) / MTReportParam

[Previous](MTReportInfo.md) | [Next](MTReportServerInfo.md)

<a id="mtreportparam"></a>
# MTReportParam (#mtreportparam)

This structure is used for describing a reports module parameters. It describes both reports request parameters from a manager terminal and module parameters that are set during the configuration in MetaTrader 5 Administrator. Requests parameters are passed through the params field and external parameters are passed through the config field of the [MTReportInfo](MTReportInfo.md) structure. The MTReportParam structure is defined with the one-byte alignment.
    
    
    #pragma pack(push,1)
    struct MTReportParam
      {
       //--- parameter types
       enum EnParamType
         {
          TYPE_STRING    =0,                                     // String
          TYPE_INT       =1,                                     // Integer
          TYPE_FLOAT     =2,                                     // Floating-point number
          TYPE_TIME      =3,                                     // Time
          TYPE_DATE      =4,                                     // Date
          TYPE_DATETIME  =5,                                     // Date and time
          TYPE_GROUPS    =6,                                     // List of groups
          TYPE_SYMBOLS   =7,                                     // List of symbols
          TYPE_BOOL      =8,                                     // Boolean
          //---
          TYPE_FIRST     =TYPE_STRING,
          TYPE_LAST      =TYPE_BOOL
         };
       //---
       UINT              type;                                   // Parameter type (EnParamType)
       wchar_t           name[64];                               // Parameter name
       wchar_t           value[256];                             // Parameter value
       UINT              reserved[16];                           // Reserved field
      };
    #pragma pack(pop)

<a id="enparamtype"></a>
## Enumerations (#enparamtype)

The MTReportParam structure contains the EnParamType enumeration that contains description of possible types of parameters:

ID | Value | Description  
TYPE_STRING | 0 | A string parameter.  
TYPE_INT | 1 | An integer parameter.  
TYPE_FLOAT | 2 | A floating-point number.  
TYPE_TIME | 3 | A parameter, in which time is specified (HH:MM:SS).  
TYPE_DATE | 4  | A parameter, in which date is specified (YYYY.MM.DD).  
TYPE_DATETIME | 5 | A parameter, in which date and time are specified (YYYY.MM.DD HH:MM:SS).  
TYPE_GROUPS | 6 | List of groups.  
TYPE_SYMBOLS | 7 | List of symbols.  
TYPE_BOOL | 8 | A boolean parameter.  
TYPE_FIRST |  | Beginning of enumeration. It corresponds to TYPE_STRING.  
TYPE_LAST |  | End of enumeration. It corresponds to TYPE_BOOL.  
  
<a id="parameters"></a>
## Parameters (#parameters)

The structure contains the following parameters:

Field | Type | Description  
type | UINT | Parameter type. To pass the type, the EnParamType enumeration is used.  
name | wchar_t | The name of the parameter. The following macroses are used to pass the reports request parameters name from the MetaTrader 5 Manager terminal:

  * MTAPI_PARAM_GROUPS — "Groups" field;
  * MTAPI_PARAM_SYMBOLS — "Symbols" field;
  * MTAPI_PARAM_FROM — "From" parameter in the "Period" field;
  * MTAPI_PARAM_TO — "To" parameter in the "Period" field.

In case another name is specified for a parameter, it will be displayed in the additional parameters block of a manager terminal.  
value | wchar_t | The value of the parameter.  
reserved | UINT | A reserved field for future use.

```

---

<a id='mtreportserverinfo-md'></a>
### 21. `MTReportServerInfo.md`

```markdown
[🏠 Document Start](../README.md) / [Structures](README.md) / MTReportServerInfo

[Previous](MTReportParam.md) | [Next](MTPluginInfo.md)

# MTReportServerInfo

Using the MTReportServerInfo structure, the server provides the module with the information about the trading platform and the server on which it is running. The structure is defined with the one-byte alignment.
    
    
    #pragma pack(push,1)
    struct MTServerInfo
      {
       wchar_t           platform_name[64];                     // Name of the platform
       wchar_t           platform_owner[128];                   // Owner of th eplatform
       UINT              server_version;                        // Server version
       UINT              server_build;                          // Server build
       UINT              server_type;                           // Server type
       UINT64            server_id;                             // Server ID
       UINT              reserverd[32];                         // A reserved field
      };
    #pragma pack(pop)

This structure is used in the IMTReportAPI::About method.

The structure contains the following parameters:

Field | Type | Description  
platform_name | wchar_t | Name of the platform.  
platform_owner | wchar_t | The name of the platform owner.  
server_version | UINT | Version of the server, on which the module is running.  
server_build | UINT | The build of the server on which the module is running.  
server_type | UINT | Type of the server on which the module is running. To pass the server type, the [IMTConServer::EnServerTypes (#enservertypes)](../Configuration-Interfaces/Network/IMTConServer/Enumerations.md#enservertypes) enumeration is used.  
server_id | UINT64 | ID of the server, on which the module is running.  
reserved | UINT | A reserved field for future use.

```

---

<a id='mtserverinfo-md'></a>
### 21. `MTServerInfo.md`

```markdown
[🏠 Document Start](../README.md) / [Structures](README.md) / MTServerInfo

[Previous](MTPluginParam.md) | [Next](../Configuration-Interfaces/README.md)

# MTServerInfo

Using the MTServerInfo structure, the server provides the plugin with the information about the trading platform and the server on which it is running. The structure is defined with the one-byte alignment.
    
    
    #pragma pack(push,1)
    struct MTServerInfo
      {
       wchar_t           platform_name[64];                     // Name of the platform
       wchar_t           platform_owner[128];                   // Owner of th eplatform
       UINT              server_version;                        // Server version
       UINT              server_build;                          // Server build
       UINT              server_type;                           // Server type
       UINT64            server_id;                             // Server ID
       UINT              reserverd[32];                         // A reserved field
      };
    #pragma pack(pop)

This structure is used in the [IMTServerAPI::About](../Server-API/Main-API-Interface/Common-Functions/About.md) method.

The structure contains the following parameters:

Field | Type | Description  
platform_name | wchar_t | Name of the platform.  
platform_owner | wchar_t | The name of the platform owner.  
server_version | UINT | Version of the server on which the plugin is running.  
server_build | UINT | Build of the server on which the plugin is running.  
server_type | UINT | Type of the server on which the plugin is running. To pass the server type, the [IMTConServer::EnServerTypes (#enservertypes)](../Configuration-Interfaces/Network/IMTConServer/Enumerations.md#enservertypes) enumeration is used.  
server_id | UINT64 | The ID of the server on which the plugin is running.  
reserved | UINT | A reserved field for future use.

```

---

<a id='mttick-md'></a>
### 21. `MTTick.md`

```markdown
[🏠 Document Start](../README.md) / [Structures](README.md) / MTTick

[Previous](MTLicenseCheck.md) | [Next](MTTickShort.md)

<a id="mttick"></a>
# MTTick (#mttick)

This structure describes the full information about a tick. The structure is defined with the one-byte alignment.
    
    
    #pragma pack(push,1)
    struct MTTick
      {
       //--- Tick flags
       enum EnTickFlags
         {
          TICK_FLAG_BUY  =1,                                    // Created as a result of buy operation
          TICK_FLAG_SELL =2,                                    // Created as a result of sell operation
          //--- Enumeration borders
          TYPE_FIRST     =0,                                    // No flags
          TYPE_LAST      =TICK_FLAG_BUY|TICK_FLAG_SELL          // All flags
         };
       //---
       wchar_t           symbol[32];                            // Symbol
       wchar_t           bank[32];                              // Source
       INT64             datetime;                              // Date and time
       double            bid;                                   // The bid price
       double            ask;                                   // The ask price
       double            last;                                  // The last price
       UINT64            volume;                                // The last deal volume
       INT64             datetime_msc;                          // Date and time in milliseconds
       UINT64            flags;                                 // Flags
       UINT64            volume_ext;                            // Last deal volume with extended accuracy
       UINT              reserved[26];                          // Reserved field
      };
    #pragma pack(pop)

This structure is used in the following methods:

  * [IMTManagerAPI::TickAdd](../Manager-API/Manager-Interface/Tick-Data/TickAdd.md)
  * [IMTGatewayAPI::SendTicks](../Gateway-API/Main-Interface/Quote-and-News-Feeds/SendTicks.md)
  * [IMTServerAPI::TickAdd](../Server-API/Main-API-Interface/Tick-Data/TickAdd.md)
  * [IMTTickSink::HookTick](../Database-Interfaces/Price-Data/IMTTickSink/HookTick.md)



The structure contains the following parameters:

Field | Type | Description  
symbol | wchar_t | Symbol name.  
bank | wchar_t | The price source (Liquidity provider).  
datetime | INT64 | Date and time of the tick in seconds passed since 01.01.1970. This fields is not filled in by default (equal to 0) - the history server inserts the server's current trading time when receiving the data. If necessary, the gateway developer can set this date on their own. Using this feature implies 100% correctness of the transferred data time. Therefore, it should be used only when necessary.

  * datetime_msc has a higher priority than datetime. The server will use this value if it it specified.
  * If datetime_msc is specified only, datetime value will be filled automatically on its basis (without milliseconds).
  * If datetime is specified only, datetime_msc value will be filled automatically on its basis (with zero value for milliseconds).

If you specify the time yourself, consider the time zone of the trade server ([IMTConTime::TimeZone](../Configuration-Interfaces/Time/IMTConTime/IMTCon-Zone.md)). For example, if the data feed passes the UNIX time (GMT 0), while the trading server works in GMT+2 time zone, the value should be increased by 60*60*2 (2 hours in seconds).  
bid | double | The Bid price.  
ask | double | The Ask price.  
last | double | The price of the last committed transaction.  
volume | UINT64 | Volume of a last deal. The volume is recorded in the same form as it is passed by a data provider. A data provider may pass volumes as amounts of contracts (in lots) or as amounts of money. On the trading platform side, this value is interpreted depending on the type of calculation of profit and margin set for a symbol ([IMTConSymbol::CalcMode](../Configuration-Interfaces/Symbols/IMTConSymbol/CalcMode.md)):

  * For the [IMTConSymbol::TRADE_MODE_FOREX (#encalcmode)](../Configuration-Interfaces/Symbols/IMTConSymbol/Enumerations.md#encalcmode) type, the volumes are interpreted as amounts of money.
  * For all the other type, the volumes are interpreted as amounts of contracts (lots).

For operations with [extended volume accuracy (#volume)](../Development-Features/README.md#volume), use the 'volume_ext' field.

  * The 'volume_ext' value has a higher priority than 'volume'. The server will use this value if specified.
  * When returning volume values, the server fills both fields: with standard and extended accuracy.

  
datetime_msc | INT64 | Date and time of the tick in milliseconds passed since 01.01.1970. This fields is not filled in by default (equal to 0) - the history server inserts the server's current trading time when receiving the data. If necessary, the gateway developer can set this date on their own. Using this feature implies 100% correctness of the transferred data time. Therefore, it should be used only when necessary.

  * datetime_msc has a higher priority than datetime. The server will use this value if it it specified.
  * If datetime_msc is specified only, datetime value will be filled automatically on its basis (without milliseconds).
  * If datetime is specified only, datetime_msc value will be filled automatically on its basis (with zero value for milliseconds).

If you specify the time yourself, consider the time zone of the trade server ([IMTConTime::TimeZone](../Configuration-Interfaces/Time/IMTConTime/IMTCon-Zone.md)). For example, if the data feed passes the UNIX time (GMT 0), while the trading server works in GMT+2 time zone, the value should be increased by 60*60*1000*2 (2 hours in milliseconds).  
flags | UINT64 | Tick flats passed using the EnTickFlags enumeration.  
volume_ext | UINT64 | Last deal volume with [extended accuracy (#volume)](../Development-Features/README.md#volume). It is similar to the 'volume' field, but the value is passed with the fixed number of decimal places (8).

  * The 'volume_ext' value has a higher priority than 'volume'. The server will use this value if specified.
  * When returning volume values, the server fills both fields: with standard and extended accuracy.

  
reserved | UINT | A reserved field for future use.  
  
<a id="enmtfeederconstants"></a>
## EnMTFeederConstants (#enmtfeederconstants)

Indexes are used for specifying the data source, from which the price was received. The type of the data source, from which the information has been received, is determined in accordance with the constants described in the EnMTFeederConstants enumeration.

ID | Value | Description  
MT_FEEDER_DEALER | -1 | Information added manually from a manager terminal or API.  
MT_FEEDER_OFFSET | 64 | This value defines the start of the range of [data feed](../Configuration-Interfaces/Data-Feeds.md) indexes. Values ​​from 0 to 63 mean that the information was received from a [gateway](../Configuration-Interfaces/Gateways.md). Values ​​of 64 or greater indicate that the information was received from a data feed.  
  
The enumeration is used in the following methods:

  * [IMTTickSink::OnTick](../Database-Interfaces/Price-Data/IMTTickSink/OnTick.md)
  * [IMTTickSink::OnTickStat](../Database-Interfaces/Price-Data/IMTTickSink/OnTickStat.md)



<a id="entickflags"></a>
## EnTickFlags (#entickflags)

Tick flags are described in EnTickFlags.

ID | Value | Description  
TICK_FLAG_BUY | 1 | Tick created as a result of a buy operation.  
TICK_FLAG_SELL | 2 | Tick created as a result of a sell operation.  
TICK_FLAG_NONE | 0 | Beginning of enumeration. It corresponds to the absence of flags.  
TICK_FLAG_ALL |  | End of enumeration. All flags are enabled.  
  
Data on direction is generally filled by the source of ticks, i.e. a gateway or a data feed. If the data source does not provide such information, the history server fills the direction automatically using the following algorithm:

  * If the Last deal price is greater than or equal to the last Ask price, the price is considered to be the result of a buy deal (TICK_FLAG_BUY).
  * If the Last deal price is less than or equal to the last Bid price, the price is considered to be the result of a sell deal (TICK_FLAG_SELL).
  * In other cases, it is considered that the direction cannot be determined, and both flags are set for a tick (TICK_FLAG_BUY | TICK_FLAG_SELL).



```

---

<a id='mttickrate-md'></a>
### 21. `MTTickRate.md`

```markdown
[🏠 Document Start](../README.md) / [Structures](README.md) / MTTickRate

[Previous](MTTickShort.md) | [Next](MTTickStat.md)

<a id="mttickrate"></a>
# MTTickRate (#mttickrate)

This structure describes brief information about a tick. It differs from the [MTTick](MTTick.md) abd [MTTickShort](MTTickShort.md) structures by a reduced number of fields. The structure is defined with the one-byte alignment.
    
    
    #pragma pack(push,1)
    struct MTTickRate
      {
       //--- tick flags
       enum EnTickShortFlags
         {
          TICK_SHORT_FLAG_RAW   =0x00000001,                    // source ticks
          TICK_SHORT_FLAG_BID   =0x00000002,                    // the tick changed the bid price
          TICK_SHORT_FLAG_ASK   =0x00000004,                    // the tick changed the ask price
          TICK_SHORT_FLAG_LAST  =0x00000008,                    // the tick changed the last price
          TICK_SHORT_FLAG_VOLUME=0x00000010,                    // the tick changed the volume
          TICK_SHORT_FLAG_BUY   =0x00000020,                    // the tick appeared as a result of a buy operation
          TICK_SHORT_FLAG_SELL  =0x00000040,                    // the tick appeared as a result of a sell operation
          //--- enumeration borders
          TICK_SHORT_FLAG_NONE  =0x00000000,                    // no flags
         };
       INT64             datetime_msc;                          // date and time in milliseconds
       double            bid;                                   // bid price
       double            ask;                                   // ask price
       double            last;                                  // last price
       UINT64            flags;                                 // flags
       UINT64            volume_ext;                            // last deal volume
       UINT              reserved[2];                           // reserved field
      };
    #pragma pack(pop)

This structure is used in the following methods:

  * [IMTGatewayAPI::TickHistoryRequest](../Gateway-API/Main-Interface/Tick-Data/TickHistoryRequest.md)
  * [IMTGatewayAPI::TickHistoryRequestRaw](../Gateway-API/Main-Interface/Tick-Data/TickHistoryRequestRaw.md)
  * [IMTGatewayAPI::TickHistoryAdd](../Gateway-API/Main-Interface/Tick-Data/TickHistoryAdd.md)
  * [IMTGatewayAPI::TickHistoryReplace](../Gateway-API/Main-Interface/Tick-Data/TickHistoryReplace.md)



The structure contains the following parameters:

Field | Type | Description  
datetime_msc | INT64 | The date and time of a tick as a number of milliseconds since 01.01.1970. This field is empty by default (the value is 0), while the historical server adds the current server trading time when receiving data. If necessary, the gateway developer can set this parameter on his own. Using this feature implies 100% correctness of the transferred data time. Therefore, it should be used only when necessary. If you specify the time yourself, consider the time zone of the trade server ([IMTConTime::TimeZone](../Configuration-Interfaces/Time/IMTConTime/IMTCon-Zone.md)). For example, if the data feed passes the UNIX time (GMT 0), while the trading server works in GMT+2 time zone, the value should be increased by 60*60*1000*2 (2 hours in milliseconds).  
bid | double | The Bid price.  
ask | double | The Ask price.  
last | double | The price of the last committed transaction.  
flags | UINT64 | Tick flags specified using the EnTickShortFlags enumeration. The flags reveal additional information about the tick and the data it has changed.  
volume_ext | UINT64 | Last deal volume. The value is passed with a fixed number of decimal places (8). The volume is recorded in the same form, in which it is passed by the data provider. The data provider can broadcast it both in the form of the number of lots (contracts) and as a monetary amount. On the trading platform side, this value is interpreted depending on the profit calculation and margin calculation type, which is specified for the symbol ([IMTConSymbol :: CalcMode](../Configuration-Interfaces/Symbols/IMTConSymbol/CalcMode.md)):

  * For the [IMTConSymbol::TRADE_MODE_FOREX (#encalcmode)](../Configuration-Interfaces/Symbols/IMTConSymbol/Enumerations.md#encalcmode) type, the volume is interpreted as a monetary amount.
  * For all other types the volume is interpreted as the number of contracts (lots).

  
reserved | UINT | A reserved field for future use.  
  
<a id="entickshortflags"></a>
## EnTickShortFlags (#entickshortflags)

EnTickShortFlags contains the tick flags.

Identifier | Value | Description  
TICK_SHORT_FLAG_RAW | 0x00000001 | Initial tick obtained from a data source/gateway. The tick was not transformed (for example, according to the symbol spread balance — [IMTConSymbol::SpreadBalance](../Configuration-Interfaces/Symbols/IMTConSymbol/SpreadBalance.md)).  
TICK_SHORT_FLAG_BID | 0x00000002 | The tick changed the Bid price.  
TICK_SHORT_FLAG_ASK | 0x00000004 | The tick changed the Ask price.  
TICK_SHORT_FLAG_LAST | 0x00000008 | The tick changed the Last price.  
TICK_SHORT_FLAG_VOLUME | 0x00000010 | The tick changed the volume.  
TICK_FLAG_BUY | 0x00000020 | The tick was created as a result of a buy operation.  
TICK_FLAG_SELL | 0x00000040 | The tick was created as a result of a sell operation.  
TICK_FLAG_NONE | 0x00000000 | No flags.

```

---

<a id='mttickshort-md'></a>
### 21. `MTTickShort.md`

```markdown
[🏠 Document Start](../README.md) / [Structures](README.md) / MTTickShort

[Previous](MTTick.md) | [Next](MTTickRate.md)

<a id="mttickshort"></a>
# MTTickShort (#mttickshort)

This structure describes a summary information about a tick. It differs from the [MTTick](MTTick.md) structure by a reduced number of fields. The structure is defined with the one-byte alignment.
    
    
    #pragma pack(push,1)
    struct MTTickShort
      {
       //--- Tick flags
       enum EnTickShortFlags
         {
          TICK_SHORT_FLAG_RAW   =0x00000001,                    // Raw tick
          TICK_SHORT_FLAG_BID   =0x00000002,                    // Tick changes bid price value
          TICK_SHORT_FLAG_ASK   =0x00000004,                    // Tick changes ask price value
          TICK_SHORT_FLAG_LAST  =0x00000008,                    // Tick changes last price value
          TICK_SHORT_FLAG_VOLUME=0x00000010,                    // Tick changes volume value
          TICK_SHORT_FLAG_BUY   =0x00000020,                    // Tick created due to a buy operation
          TICK_SHORT_FLAG_SELL  =0x00000040,                    // Tick created due to a sell operation
          //--- Enumeration borders
          TICK_SHORT_FLAG_NONE  =0x00000000,                    // none
         };
       INT64             datetime;                              // Date and time
       double            bid;                                   // The bid price
       double            ask;                                   // The ask price
       double            last;                                  // The last price
       UINT64            volume;                                // The tick volume
       INT64             datetime_msc;                          // Date and time in milliseconds
       UINT64            flags;                                 // Flags
       UINT64            volume_ext;                            // Last deal volume with extended accuracy
       UINT              reserved[26];                          // Reserved field
      };
    #pragma pack(pop)

This structure is used in the following methods:

  * [IMTManagerAPI::TickLast](../Manager-API/Manager-Interface/Tick-Data/TickLast.md)
  * [IMTManagerAPI::TickHistoryRequest](../Manager-API/Manager-Interface/Tick-Data/TickHistoryRequest.md)
  * [IMTAdminAPI::TickRequest](../Manager-API/Administrator-Interface/Tick-Data/TickRequest.md)
  * [IMTAdminAPI::TickRequestRaw](../Manager-API/Administrator-Interface/Tick-Data/TickRequestRaw.md)
  * [IMTAdminAPI::TickAdd](../Manager-API/Administrator-Interface/Tick-Data/TickAdd.md)
  * [IMTAdminAPI::TickReplace](../Manager-API/Administrator-Interface/Tick-Data/TickReplace.md)
  * [IMTTickSink::OnTick](../Database-Interfaces/Price-Data/IMTTickSink/OnTick.md)
  * [IMTReportAPI::TickHistoryGet](../Report-API/Main-Interface-of-Reports/Price-Data/TickHistoryGet.md)
  * [IMTReportAPI::TickHistoryGetRaw](../Report-API/Main-Interface-of-Reports/Price-Data/TickHistoryGetRaw.md)
  * [IMTServerAPI::TickLast](../Server-API/Main-API-Interface/Tick-Data/TickLast.md)
  * [IMTServerAPI::TickGet](../Server-API/Main-API-Interface/Tick-Data/TickGet.md)
  * [IMTServerAPI::TickGetRaw](../Server-API/Main-API-Interface/Tick-Data/TickHistoryGetRaw.md)



The structure contains the following parameters:

Field | Type | Description  
datetime | INT64 | Date and time of the tick in seconds passed since 01.01.1970. This fields is not filled in by default (equal to 0) - the history server inserts the server's current trading time when receiving the data. If necessary, the gateway developer can set this date on their own. Using this feature implies 100% correctness of the transferred data time. Therefore, it should be used only when necessary.

  * datetime_msc has a higher priority than datetime. The server will use this value if it it specified.
  * If datetime_msc is specified only, datetime value will be filled automatically on its basis (without milliseconds).
  * If datetime is specified only, datetime_msc value will be filled automatically on its basis (with zero value for milliseconds).

If you specify the time yourself, consider the time zone of the trade server ([IMTConTime::TimeZone](../Configuration-Interfaces/Time/IMTConTime/IMTCon-Zone.md)). For example, if the data feed passes the UNIX time (GMT 0), while the trading server works in GMT+2 time zone, the value should be increased by 60*60*2 (2 hours in seconds).  
bid | double | The Bid price.  
ask | double | The Ask price.  
last | double | The price of the last committed transaction.  
volume | UINT64 | Volume. The volume is recorded in the same form as it is passed by a data provider. A data provider may pass volumes as amounts of contracts (in lots) or as amounts of money. On the trading platform side, this value is interpreted depending on the type of calculation of profit and margin set for a symbol ([IMTConSymbol::CalcMode](../Configuration-Interfaces/Symbols/IMTConSymbol/CalcMode.md)):

  * For the [IMTConSymbol::TRADE_MODE_FOREX (#encalcmode)](../Configuration-Interfaces/Symbols/IMTConSymbol/Enumerations.md#encalcmode) type, the volumes are interpreted as amounts of money.
  * For all the other type, the volumes are interpreted as amounts of contracts (lots).

For operations with [extended volume accuracy (#volume)](../Development-Features/README.md#volume), use the 'volume_ext' field.

  * The 'volume_ext' value has a higher priority than 'volume'. The server will use this value if specified.
  * When returning volume values, the server fills both fields: with standard and extended accuracy.

  
datetime_msc | INT64 | Date and time of the tick in milliseconds passed since 01.01.1970. This fields is not filled in by default (equal to 0) - the history server inserts the server's current trading time when receiving the data. If necessary, the gateway developer can set this date on their own. Using this feature implies 100% correctness of the transferred data time. Therefore, it should be used only when necessary.

  * datetime_msc has a higher priority than datetime. The server will use this value if it it specified.
  * If datetime_msc is specified only, datetime value will be filled automatically on its basis (without milliseconds).
  * If datetime is specified only, datetime_msc value will be filled automatically on its basis (with zero value for milliseconds).

If you specify the time yourself, consider the time zone of the trade server ([IMTConTime::TimeZone](../Configuration-Interfaces/Time/IMTConTime/IMTCon-Zone.md)). For example, if the data feed passes the UNIX time (GMT 0), while the trading server works in GMT+2 time zone, the value should be increased by 60*60*1000*2 (2 hours in milliseconds).  
flags | UINT64 | Tick flags passed using the EnTickShortFlags enumeration. The flags reveal additional information about the tick and the data it has changed.  
volume_ext | UINT64 | Last deal volume with [extended accuracy (#volume)](../Development-Features/README.md#volume). It is similar to the 'volume' field, but the value is passed with the fixed number of decimal places (8).

  * The 'volume_ext' value has a higher priority than 'volume'. The server will use this value if specified.
  * When returning volume values, the server fills both fields: with standard and extended accuracy.

  
reserved | UINT | A reserved field for future use.  
  
<a id="entickshortflags"></a>
## EnTickShortFlags (#entickshortflags)

EnTickShortFlags contains the tick flags.

ID | Value | Description  
TICK_SHORT_FLAG_RAW | 0x00000001 | Initial tick obtained from a data source/gateway. The tick has not been transformed (for example, according to the symbol spread balance — [IMTConSymbol::SpreadBalance](../Configuration-Interfaces/Symbols/IMTConSymbol/SpreadBalance.md)).  
TICK_SHORT_FLAG_BID | 0x00000002 | Tick has changed the Bid price.  
TICK_SHORT_FLAG_ASK | 0x00000004 | Tick has changed the Ask price.  
TICK_SHORT_FLAG_LAST | 0x00000008 | Tick has changed the Last price.  
TICK_SHORT_FLAG_VOLUME | 0x00000010 | Tick has changed the volume.  
TICK_FLAG_BUY | 0x00000020 | Tick has been created as a result of a buy operation.  
TICK_FLAG_SELL | 0x00000040 | Tick has been created as a result of a sell operation.  
TICK_FLAG_NONE | 0x00000000 | No flags.

```

---

<a id='mttickstat-md'></a>
### 21. `MTTickStat.md`

```markdown
[🏠 Document Start](../README.md) / [Structures](README.md) / MTTickStat

[Previous](MTTickRate.md) | [Next](MTMailRange.md)

<a id="mttickstat"></a>
# MTTickStat (#mttickstat)

This structure describes the statistical information about a symbol. The structure is defined with the one-byte alignment.
    
    
    #pragma pack(push,1)
    struct MTTickStat
      {
       wchar_t           symbol[32];                            // Symbol
       INT64             datetime;                              // Date and time
       //--- bid
       double            bid_high;                              // max. bid
       double            bid_low;                               // min. bid
       //--- ask
       double            ask_high;                              // max. ask
       double            ask_low;                               // min. ask
       //--- last price
       double            last_high;                             // max. last
       double            last_low;                              // min. last
       //--- trade volume
       UINT64            vol_high;                              // max. volume
       UINT64            vol_low;                               // min. volume
       //--- Trade session statistics
       UINT64            trade_deals;                           // The number of deals during a session
       UINT64            trade_volume;                          // The volume of deals during a session
       UINT64            trade_turnover;                        // Turnover for a session
       UINT64            trade_interest;                        // The volume of effective contracts
       UINT64            trade_buy_orders;                      // The number of buy orders
       UINT64            trade_buy_volume;                      // The volume of buy orders
       UINT64            trade_sell_orders;                     // The number of sell orders
       UINT64            trade_sell_volume;                     // The volume of sell orders
       UINT64            trade_volume_ext;                      // The volume of deals within the session, with extended accuracy
       UINT64            trade_buy_volume_ext;                  // The volume of buy requests with extended accuracy
       UINT64            trade_sell_volume_ext;                 // The volume of sell requests with extended accuracy
       UINT64            vol_high_ext;                          // Max volume with extended accuracy
       UINT64            vol_low_ext;                           // Min volume with extended accuracy
       int               trade_reserved[20];                    // Reserved field
       //--- Date and time
       INT64             datetime_msc;                          // Date and time in milliseconds
       //--- Quotation session statistics
       double            price_open;                            // Session open price
       double            price_close;                           // Session close price
       double            price_aw;                              // Average weighted price
       double            price_obsolete;                        // Obsolete field
       double            price_volatility;                      // Price volatility
       double            price_theortical;                      // Theoretical price of an option
       double            price_greeks_delta;                    // Option delta
       double            price_greeks_theta;                    // Option theta
       double            price_greeks_gamma;                    // Option gamma
       double            price_greeks_vega;                     // Option vega
       double            price_greeks_rho;                      // Option rho
       double            price_greeks_omega;                    // Option omega
       double            price_sensitivity;                     // Option sensitivity
       int               price_reserved[14];                    // Reserved field
      };
    #pragma pack(pop)

This structure is used in the following methods:

  * [IMTManagerAPI::TickAddStat](../Manager-API/Manager-Interface/Tick-Data/TickAddStat.md)
  * [IMTManagerAPI::TickStat](../Manager-API/Manager-Interface/Tick-Data/TickStat.md)
  * [IMTTickSink::OnTickStat](../Database-Interfaces/Price-Data/IMTTickSink/OnTickStat.md)
  * [IMTTickSink::HookTickStat](../Database-Interfaces/Price-Data/IMTTickSink/HookTickStat.md)
  * [IMTGatewayAPI::SendTickStats](../Gateway-API/Main-Interface/Quote-and-News-Feeds/SendTickStats.md)
  * [IMTServerAPI::TickAddStat](../Server-API/Main-API-Interface/Tick-Data/TickAddStat.md)
  * [IMTServerAPI::TickStat](../Server-API/Main-API-Interface/Tick-Data/TickStat.md)



The structure contains the following parameters:

Field | Type | Description  
news | wchar_t | Symbol name.  
datetime | INT64 | Date and time of the tick in seconds passed since 01.01.1970. This fields is not filled in by default (equal to 0) - the history server inserts the server's current trading time when receiving the data. If necessary, the gateway developer can set this date on their own. Using this feature implies 100% correctness of the transferred data time. Therefore, it should be used only when necessary.

  * datetime_msc has a higher priority than datetime. The server will use this value if it it specified.
  * If datetime_msc is specified only, datetime value will be filled automatically on its basis (without milliseconds).
  * If datetime is specified only, datetime_msc value will be filled automatically on its basis (with zero value for milliseconds).

If you specify the time yourself, consider the time zone of the trade server ([IMTConTime::TimeZone](../Configuration-Interfaces/Time/IMTConTime/IMTCon-Zone.md)). For example, if the data feed passes the UNIX time (GMT 0), while the trading server works in GMT+2 time zone, the value should be increased by 60*60*2 (2 hours in seconds).  
bid_high | double | The highest bid price for the current day.  
bid_low | double | The lowest bid price for the current day.  
ask_high | double | The highest ask price for the current day.  
ask_low | double | The highest and lowest ask prices for the current day.  
last_high | double | The highest price at which a deal has been conducted for the current day.  
last_low | double | The lowest price at which a deal has been conducted for the current day.  
vol_high | UINT64 | The maximum volume of a deal for the current day. When specifying a value pay attention to the peculiarities of working with volume. For operations with [extended volume accuracy (#volume)](../Development-Features/README.md#volume), use the vol_high_ext field.  
vol_low | UINT64 | The minimum volume of a deal for the current day. When specifying a value pay attention to the peculiarities of working with volume. For operations with [extended volume accuracy (#volume)](../Development-Features/README.md#volume), use the vol_low_ext field.  
trade_deals | UINT64 | The total number of deals executed for the current session.  
trade_volume | UINT64 | The total volume of deals executed for the current session. When specifying a value pay attention to the peculiarities of working with volume. For operations with [extended volume accuracy (#volume)](../Development-Features/README.md#volume), use the trade_volume_ext field.  
trade_turnover | UINT64 | Money turnover for a symbol for the current session.  
trade_interest | UINT64 | The total volume of effective contracts (futures, options) for which there have been no calculations yet.  
trade_buy_orders | UINT64 | The total number of buy requests.  
trade_buy_volume | UINT64 | The total volume of buy requests. When specifying a value pay attention to the peculiarities of working with volume. For operations with [extended volume accuracy (#volume)](../Development-Features/README.md#volume), use the trade_buy_volume_ext field.  
trade_sell_orders | UINT64 | The total number of sell requests.  
trade_sell_volume | UINT64 | The total volume of buy sell requests. When specifying a value pay attention to the peculiarities of working with volume. For operations with [extended volume accuracy (#volume)](../Development-Features/README.md#volume), use the trade_sell_volume_ext field.  
trade_volume_ext | UINT64 | The total volume of deals within a session, with [extended accuracy (#volume)](../Development-Features/README.md#volume). It is similar to the 'trade_volume' field, but the value is passed with the fixed number of decimal places (8). The 'trade_volume_ext' value has a higher priority than 'trade_volume'.  
trade_buy_volume_ext | UINT64 | The total volume of buy requests with [extended accuracy (#volume)](../Development-Features/README.md#volume). It is similar to the 'trade_buy_volume' field, but the value is passed with the fixed number of decimal places (8). The 'trade_buy_volume_ext' value has a higher priority than 'trade_buy_volume'.  
trade_sell_volume_ext | UINT64 | The total volume of sell requests with [extended accuracy (#volume)](../Development-Features/README.md#volume). It is similar to the 'trade_sell_volume' field, but the value is passed with the fixed number of decimal places (8). The 'trade_sell_volume_ext' value has a higher priority than 'trade_sell_volume'.  
vol_high_ext | UINT64 | The maximum deal volume doe a day, with [extended accuracy (#volume)](../Development-Features/README.md#volume). It is similar to the 'vol_high' field, but the value is passed with the fixed number of decimal places (8). The 'vol_high_ext' value has a higher priority than 'vol_high'.  
vol_low_ext | UINT64 | The minimum deal volume doe a day, with [extended accuracy (#volume)](../Development-Features/README.md#volume). It is similar to the 'vol_low' field, but the value is passed with the fixed number of decimal places (8). The 'vol_low_ext' value has a higher priority than 'vol_low'.  
trade_reserved | int | A reserved field for future use.  
datetime_msc | INT64 | Date and time of the tick in milliseconds passed since 01.01.1970. This fields is not filled in by default (equal to 0) - the history server inserts the server's current trading time when receiving the data. If necessary, the gateway developer can set this date on their own. Using this feature implies 100% correctness of the transferred data time. Therefore, it should be used only when necessary.

  * datetime_msc has a higher priority than datetime. The server will use this value if it it specified.
  * If datetime_msc is specified only, datetime value will be filled automatically on its basis (without milliseconds).
  * If datetime is specified only, datetime_msc value will be filled automatically on its basis (with zero value for milliseconds).

If you specify the time yourself, consider the time zone of the trade server ([IMTConTime::TimeZone](../Configuration-Interfaces/Time/IMTConTime/IMTCon-Zone.md)). For example, if the data feed passes the UNIX time (GMT 0), while the trading server works in GMT+2 time zone, the value should be increased by 60*60*1000*2 (2 hours in milliseconds).  
price_open | double | The Open price of the current (last active) session.  
price_close | double | The Close price of the previous session (of the last session of the previous trading day).  
price_aw | double | The weighted average price for a session.  
price_obsolete | double | This is a deprecated field which was previously used to pass the price change in percentage terms (price_change). The server no longer accepts the value of this field.  
price_volatility | double | The implied volatility. It is specified as a percentage, and characterizes the expectations of market participants about the value of the underlying asset of the option.  
price_theoretical | double | The theoretical (fair) price of an option calculated for the specified strike based on historical data.  
price_greeks_delta | double | Option delta. "[The Greeks (#greeks)](https://www.metatrader5.com/ru/terminal/help/trading/options_board#greeks)", which include Delta, Theta, Gamma, Vega, Po and Omega, are quantities representing the sensitivity of the option price to changes in various parameters: strike prices, volatility, etc.  
price_greeks_theta | double | Option theta.  
price_greeks_gamma | double | Option gamma.  
price_greeks_vega | double | Option vega.  
price_greeks_rho | double | Option rho.  
price_greeks_omega | double | Option omega.  
price_sensitivity | double | Option sensitivity. It shows by how many points the price of the option's underlying asset should change so that the price of the option changes by one point.  
price_reserved | int | A reserved field for future use.  
  
<a id="volume"></a>
## Peculiarities of working with volume (#volume)

Volume (for example, in the parameters like trade_sell_volume, trade_buy_volume etc.) is recorded in the same form as it is passed by a data provider. A data provider may pass volumes as amounts of contracts (in lots) or as amounts of money. On the trading platform side, this value is interpreted depending on the type of calculation of profit and margin set for a symbol ([IMTConSymbol::CalcMode](../Configuration-Interfaces/Symbols/IMTConSymbol/CalcMode.md)):

  * For the [IMTConSymbol::TRADE_MODE_FOREX (#encalcmode)](../Configuration-Interfaces/Symbols/IMTConSymbol/Enumerations.md#encalcmode) type, the volumes are interpreted as amounts of money.
  * For all the other type, the volumes are interpreted as amounts of contracts (lots).



Notes on extended volume accuracy operations:

  * The *_volume_ext value always has a higher priority than *_volume. The server will use this value if specified.
  * If only the '*_volume_ext' value is specified, the '*_volume' field will be filled automatically based on the extended accuracy value (without milliseconds).
  * If only '*_volume' is specified, the '*_volume_ext' field will be filled automatically on the bases of the standard accuracy value (with zero milliseconds).



```

---

<a id='readme-md'></a>
### 21. `README.md`

```markdown
[🏠 Document Start](../README.md) / Structures

[Previous](../Return-Codes/Subscriptions.md) | [Next](MTProxyInfo.md)

# Structures

The MetaTrader 5 API provides several pre-defined structures that are designed for storing and passing of service information: Virtually all APIs use the same structures.

  * [MTProxyInfo](MTProxyInfo.md) — parameters of connection through a proxy server.
  * [MTLicenseCheck](MTLicenseCheck.md) — Information for verifying the license.
  * [MTTick](MTTick.md) — a full description of a tick.
  * [MTTickShort](MTTickShort.md) — a brief description of a tick.
  * [MTTickRate](MTTickRate.md) — a brief description of a tick.
  * [MTTickStat](MTTickStat.md) — description of statistical information about ticks.
  * [MTMailRange](MTMailRange.md) — a range of recipients of a mailing list.
  * [MTLogRecord](MTLogRecord.md) — description of a log entry.
  * [MTChartBar](MTChartBar.md) — description of a chart bar.
  * [MTBookItem](MTBookItem.md) — description of an element of the Depth of Market.
  * [MTBook/MTBookDiff](MTBookMTBookDiff.md) — description of the Depth of Market.
  * [MTGatewayInfo](MTGatewayInfo.md) — gateway/data feed module parameters.
  * [MTNews](MTNews.md) — news description.
  * [MTEconomicEvent](MTEconomicEvent.md) — description of a news of the economic calendar.
  * [MTReportInfo](MTReportInfo.md) — initial information about the report module.
  * [MTReportParam](MTReportParam.md) — module parameters.
  * [MTReportServerInfo](MTReportServerInfo.md) — information about the trading platform and the server.
  * [MTPluginInfo](MTPluginInfo.md) — initial information about the plugin.
  * [MTPluginParam](MTPluginParam.md) — default parameters of the plugin.
  * [MTServerInfo](MTServerInfo.md) — information about the trading platform and the server.



```

---
