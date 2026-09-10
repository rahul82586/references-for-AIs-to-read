[🏠 Document Start](README.md) / MetaTrader 5 API

[Next](Getting-Started.md)

# MetaTrader 5 Platform API Guide

The MetaTrader 5 platform features open APIs which allow further expanding the platform capabilities, integrating with other trading systems and back-office components, as well as customizing the platform to fit specific business needs.

The platform provides five APIs and an additional option enabling real-time data export to an SQL database.

### ![server-api](images/server-api.png)

**[Server API](Server-API/README.md)**

**Languages:** C++

Set of tools for expanding functionality and customizing the MetaTrader 5 server operation logic: custom commissioning and swap calculation algorithms, routing of financial operations, and more. [Ready-made examples](Server-API/Ready-made-Examples.md) for expanding the Web and Manager API protocols

### ![manager-api](images/manager-api.png)

**[Manager API](Manager-API/README.md)**

**Languages:** C++, C#, .NET, Python

Set of functions for developing and editing accounts, depositing and withdrawing funds, processing trade requests and managing the server settings. The API is provided as C++ interfaces (32 and 64-bit DLL library) with [sample source codes](Manager-API/Ready-made-Examples.md).

### ![gateway-api](images/gateway-api.png)

**[Gateway API](Gateway-API/README.md)**

**Languages:** C++, C#, .NET

Allows for the development of custom [gateways](Gateway-API/Development-and-Debugging-of-Gateways.md) and [data sources](Gateway-API/Development-of-Data-Feeds.md) for integrating the MetaTrader 5 platform with other trading systems. The main objectives are executing and synchronizing orders and positions with an external system, developing and modifying [trading symbols](Gateway-API/Symbol-and-Price-Translation.md), providing quotes, etc.

### ![report-api](images/report-api.png)

**[Report API](Report-API/README.md)**

**Languages:** C++

Set of tools for developing custom MetaTrader 5 Manager reports. To use these features, you need to write specially designed reports modules as DLLs. The API supports [multithreading](Report-API/Multithreading.md) and [memory management](Report-API/Memory-Management.md), allows generation of [HTML reports](Report-API/HTML-Reports.md) and contains [ready-made application examples](Report-API/Ready-made-Examples.md).

### ![web-api](images/web-api.png)

**[Web API](Web-API/README.md)**

**Languages:** Any language

Provides an open text-based [protocol](Web-API/Manager-Interface-(Rest-API)/Text-Protocol-(Raw-API)/Format-of-Packages.md) for integrating the MetaTrader 5 platform with web resources and other services of a company. The API allows creating and editing client trade accounts via a website, as well as deposit and withdraw funds directly from a trader's room in real time

### ![export-to-sql](images/export-to-sql.png)

**[Export to SQL](SQL-Export/README.md)**

**Languages:** MySQL, MS SQL, Oracle, FireBird

The standard real-time export of data to an SQL database allows for generating various reports:


  * Matching orders, trades and positions with external trading systems
  * Reports sent to regulators
  * Risk management reports

This functionality is enabled by simple specification of settings for connection to DBMS via MetaTrader 5 Administrator  
  
MetaTrader 5 API additionally provides interfaces for accessing [configurations](Configuration-Interfaces/README.md) and [databases](Database-Interfaces/README.md), assistant [tools](Tools/README.md) for facilitating routine operations, and [structures](Structures/README.md) for transmitting data.

© 2000-2025, [MetaQuotes Ltd](https://www.metaquotes.net/ru)
