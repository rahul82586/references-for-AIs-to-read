# 📁 Journal-Constants

- **Generated:** 2026-09-09 00:10
- **Total Files:** 1
- **Source:** `C:\Users\DELL\Downloads\server3\mt5_doc_dump\Documentation\MQ_Docs\Metatrader 5\MetaTrader5SDK\Journal-Constants`

---

## 📑 Table of Contents

1. [README.md](#readme-md)

---

## 🌲 Project Structure

```
Journal-Constants/
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
[🏠 Document Start](../README.md) / Journal Constants

[Previous](../Internal-Data-Types/README.md) | [Next](../Return-Codes/README.md)

<a id="journal-constants"></a>
# Journal Constants (#journal-constants)

The MetaTrader 5 API provides access to server logs. A number of the constants described in the MT5APILogger.h file are available for working with the logs. The constants are described in the following enumerations:

  * [EnMTLogCode (#enmtlogcode)](README.md#enmtlogcode) — types of log messages.
  * [EnMTLogRequestMode (#enmtlogrequestmode)](README.md#enmtlogrequestmode) — types of events recorded in the log.
  * [EnMTLogType (#enmtlogtype)](README.md#enmtlogtype) — types of log requests.
  * [EnMTLogFlags (#enmtlogflags)](README.md#enmtlogflags) — flags of log entries.



<a id="enmtlogcode"></a>
## Message Types (#enmtlogcode)

Types of log messages are listed in the EnMTLogCode enumeration:

ID | Value | Description  
MTLogFolder | -1 | Folder.  
MTLogOK | 0 | Information message.  
MTLogWarn | 1 | Warning.  
MTLogErr | 2 | Error message.  
MTLogAtt | 3 | Critical error message.  
MTLogLogin | 4  | System login message.  
MTLogFirst |  | Beginning of enumeration. It corresponds to MTLogFolder.  
MTLogLast |  | End of the enumeration. It corresponds to MTLogLogin.  
  
This enumeration is used in the following methods:

  * [IMTAdminAPI::LoggerOut](../Manager-API/Administrator-Interface/Common-Functions/LoggerOut.md)
  * [IMTManagerAPI::LoggerOut](../Manager-API/Manager-Interface/Common-Functions/LoggerOut.md)
  * [IMTGatewayAPI::LoggerOut](../Gateway-API/Main-Interface/Common-Functions/LoggerOut.md)
  * [IMTSerserAPI::LoggerOut](../Server-API/Main-API-Interface/Common-Functions/LoggerOut.md)



<a id="enmtlogrequestmode"></a>
## Request Types (#enmtlogrequestmode)

The types of request of the server journal are listed in the EnMTLogRequestMode enumeration:

ID | Value | Description  
MTLogModeStd | 0 | A standard request mode. All messages except for user connection notifications are requested.  
MTLogModeErr | 1 | In this mode, only error messages ([MTLogErr (#enmtlogcode)](README.md#enmtlogcode)) are requested.  
MTLogModeFull | 2 | All types of log entries are requested when this mode is selected.  
MTLogModeFirst |  | Beginning of enumeration. It corresponds to MTLogModeStd.  
MTLogModeLast |  | End of enumeration. It corresponds to MTLogModeFull.  
  
This enumeration is used in the following methods:

  * [IMTAdminAPI::LoggerServerRequest](../Manager-API/Administrator-Interface/Common-Functions/LoggerServerRequest.md)
  * [IMTManagerAPI::LoggerServerRequest](../Manager-API/Manager-Interface/Common-Functions/LoggerServerRequest.md)
  * [IMTServerAPI::LoggerRequest](../Server-API/Main-API-Interface/Common-Functions/LoggerRequest.md)



<a id="enmtlogtype"></a>
## Event Types (#enmtlogtype)

Types of events that are reflected in the journal logs are listed in the enumeration EnMTLogType:

ID | Value | Description  
MTLogTypeAll | 0 | All types of events.  
MTLogTypeCfg | 1 | Events of [configuration](../Manager-API/Administrator-Interface/Configuration-Databases.md) changes.  
MTLogTypeSys | 2 | System events.  
MTLogTypeNet | 3 | Events related to the network activity.  
MTLogTypeHst | 4  | Events associated with [price data](../Database-Interfaces/Price-Data.md).  
MTLogTypeUser | 5 | Events associated with [users](../Database-Interfaces/Users.md).  
MTLogTypeTrade | 6 | [Trade](../Manager-API/Administrator-Interface/Trade-Databases.md) events.  
MTLogTypeAPI | 7 | Events associated with the Server API.  
MTLogTypeLiveUpdate | 16 | Events associated with the Live Update service.  
MTLogTypeSendMail | 17 | Events associated with email.  
MTLogTypeFirst |  | Beginning of enumeration. It corresponds to MTLogTypeAll.  
MTLogTypeLast |  | End of enumeration. It corresponds to MTLogTypeSendMail.  
  
The events of update (MTLogTypeLiveUpdate) and email (MTLogTypeSendMail) are generated not at the server side, but by separate applications — mt5srvupdater.exe and mt5sendmail.exe.

This enumeration is used in the following methods:

  * [IMTAdminAPI::LoggerServerRequest](../Manager-API/Administrator-Interface/Common-Functions/LoggerServerRequest.md)
  * [IMTManagerAPI::LoggerServerRequest](../Manager-API/Manager-Interface/Common-Functions/LoggerServerRequest.md)
  * [IMTServerAPI::LoggerRequest](../Server-API/Main-API-Interface/Common-Functions/LoggerRequest.md)



<a id="enmtlogflags"></a>
## Log Flags (#enmtlogflags)

Flags that journal entries may have are listed in EnMTLogFlags:

ID | Value | Description  
LOG_FLAGS_NONE | 0 | The log does not have flags.  
LOG_FLAGS_CORRUPTED | 1 | The log has an invalid checksum (damaged or changed from outside).  
LOG_FLAGS_FIRST |  | Beginning of enumeration. It corresponds to LOG_FLAGS_NONE.  
LOG_FLAGS_ALL |  | End of enumeration. It corresponds to LOG_FLAGS_CORRUPTED.

```

---
