# 📁 Migration-from-MetaTrader-4

- **Generated:** 2026-09-10 12:31
- **Total Files:** 6
- **Source:** `C:\Users\DELL\Desktop\New folder (2)\MT5-Administrator\MetaTrader5Administrator\MetaTrader-5-Trading-Platform\Migration-from-MetaTrader-4`

---

## 📑 Table of Contents

1. [Data-Feeds.md](#data-feeds-md)
2. [Financial-Instruments.md](#financial-instruments-md)
3. [General-Settings.md](#general-settings-md)
4. [Import-of-Accounts-and-Trades.md](#import-of-accounts-and-trades-md)
5. [Manager-Accounts.md](#manager-accounts-md)
6. [Trade-Groups.md](#trade-groups-md)

---

## 🌲 Project Structure

```
Migration-from-MetaTrader-4/
├── Data-Feeds.md
├── Financial-Instruments.md
├── General-Settings.md
├── images/
│   ├── access_block_icon.png
│   ├── data_feeds_common.png
│   ├── data_feeds_parameters.png
│   ├── data_feeds_parameters_uni.png
│   ├── data_feeds_server_uni.png
│   ├── migration_accounts.png
│   ├── migration_client_side.png
│   ├── migration_common_demo.png
│   ├── migration_dc.png
│   ├── migration_group.png
│   ├── migration_group_commission.png
│   ├── migration_group_import.png
│   ├── migration_group_import2.png
│   ├── migration_group_routing.png
│   ├── migration_group_symbol.png
│   ├── migration_holiday.png
│   ├── migration_ip.png
│   ├── migration_manager.png
│   ├── migration_manager_routing.png
│   ├── migration_manager_routing2.png
│   ├── migration_reports.png
│   ├── migration_result.png
│   ├── migration_server.png
│   ├── migration_start.png
│   ├── migration_symbol.png
│   ├── migration_symbol_filter.png
│   ├── migration_symbol_import.png
│   ├── migration_symbol_margin.png
│   ├── migration_sync.png
│   ├── migration_ticket.png
│   ├── migration_time.png
│   ├── migration_worktime.png
│   ├── network_add_access.png
│   ├── network_add_history.png
│   ├── network_add_network.png
│   ├── network_add_service.png
│   ├── next.png
│   ├── next_1.png
│   ├── next_2.png
│   ├── next_3.png
│   ├── next_4.png
│   ├── next_5.png
│   ├── previous.png
│   ├── previous_1.png
│   ├── previous_2.png
│   ├── previous_3.png
│   ├── previous_4.png
│   ├── previous_5.png
│   └── synchronization_scheme.png
├── Import-of-Accounts-and-Trades.md
├── Manager-Accounts.md
└── Trade-Groups.md
```

---

## 📄 Files

<a id='data-feeds-md'></a>
### 6. `Data-Feeds.md`

```markdown
[🏠 Document Start](../../README.md) / [MetaTrader 5 Trading Platform](../../MetaTrader-5-Trading-Platform.md) / [Migration from MetaTrader 4](../Migration-from-MetaTrader-4.md) / Data Feeds

[Previous](Manager-Accounts.md) | [Next](../MetaTrader-5-Administrator.md)

# Data Feeds

Any sources of quotes and news used in the MetaTrader 4 platform can be easily moved to MetaTrader 5. There are three options to receive a stream of quotes:

  * From the MetaTrader 4 server having a trading account via [MetaTrader 4 Feeder](../Platform-Components/Data-Feeds/MetaTrader-4-Feeder.md).
  * From other data terminals via [UniDDE Connector](../Platform-Components/Data-Feeds/Universal-DDE-Connector.md).



Apart from quote and news already working in the MetaTrader 4 platform, you can receive data via the new feeders designed specifically for MetaTrader 5. You can find out the details in the [Data Feeds](../Platform-Components/Data-Feeds.md) section.

## Receiving Quotes from the MetaTrader 4 Server

If both platforms work simultaneously, use [MetaTrader 4 Feeder](../Platform-Components/Data-Feeds/MetaTrader-4-Feeder.md) to receive quotes and news from the MetaTrader 4 server. Add the new [data source](../Platform-Setup/Data-Feeds.md):

![Receiving quotes and news via MetaTrader 4 Feeder](images/data_feeds_common.png)

Select MetaTrader4Feeder in the Module field and enter server's IP address and port, as well as account login and password in the Feed server, Feed login and Password fields to connect to the MetaTrader 4 server.

MetaTrader 5 allows sorting out news by language. To do this, set the Language parameter on the Parameters tab:

![Receiving quotes and news via MetaTrader 4 Feeder](images/data_feeds_parameters.png)

News coming from MetaTrader 4 servers can be in text or HTML formats. In case of a text format, setting the Language parameter is desirable for a proper language recognition and correct news display.

The news language in HTML format is automatically defined by the "charset" attribute built in the news. The language name is specified in the format that is standard for Windows operating systems without defining the dialectical features by geographic location, for example, English, Russian, etc.

## Receiving Quotes via UniDDE Connector

If your MetaTrader 4 server receives quotes via [UniDDE Connector](../Platform-Components/Data-Feeds/Universal-DDE-Connector.md), you can use MetaTrader5UniFeeder component to receive them in MetaTrader 5.

DDE Connector allows collecting quotes from various data sources that support the DDE (Dynamic Data Exchange) protocol. The feeder translates quotes received from it to the MetaTrader 5 History Server.

Add the necessary data source via the corresponding section of MetaTrader 5 Administrator:

![Receiving quotes via UniDDE Connector](images/data_feeds_server_uni.png)

Set the server address where UniDDE Connector is installed, as well as connection port and account preliminarily created in UniDDE Connector (login and password) in the source settings.

MetaTrader5UniFeeder allows receiving quotes for the symbol data not transmitted via UniDDE Connector. This is achieved by mathematical conversion of other symbols' quotes transmitted via UniDDE Connector. This method of calculation can be applied to non-freely convertible currencies with their exchange rates to the major world currencies defined by the central bank.

To receive quotes for such symbols, specify the quote calculation equations on the Parameters tab of a data source:

![Receiving quotes via UniDDE Connector](images/data_feeds_parameters_uni.png)

```

---

<a id='financial-instruments-md'></a>
### 6. `Financial-Instruments.md`

```markdown
[🏠 Document Start](../../README.md) / [MetaTrader 5 Trading Platform](../../MetaTrader-5-Trading-Platform.md) / [Migration from MetaTrader 4](../Migration-from-MetaTrader-4.md) / Financial Instruments

[Previous](General-Settings.md) | [Next](Trade-Groups.md)

# Importing and Setting Financial Instruments

Please keep in mind the following when working with MetaTrader 5 symbols:

  * Unlike MetaTrader 4, the fifth version allows you to create symbol groups (similar to Securities in MetaTrader 4) directly in Symbols section. Moreover, you can create a tree-like symbol structure.
  * In MetaTrader 5, it is not necessary to collect individual symbol into groups. However, it is still recommended to divide symbols into some logical groups to make system administration more convenient.
  * MetaTrader 5 has no limitations on the number of financial instruments and their groups.



## Importing Symbols

Use the [import of symbols](../Platform-Setup/Symbols/Import-of.md) to copy all symbols and their settings from MetaTrader 4 server to the MetaTrader 5 platform.

> When you import symbols, existing settings are converted and default values are assigned to missing settings.

![Importing symbols from MetaTrader 4 server](images/migration_symbol.png)

Select "MetaTrader 4" server type and specify connection data: IP address and server port, as well as account login and password. The account used for importing symbols may be opened in any group except for a manager one ("manager"). The group, in which the account is opened, should have access to all symbols to be imported from MetaTrader 4 server.

![Importing symbols from MetaTrader 4 server](images/migration_symbol_import.png)

The next window shows the list of all symbols that can be imported from MetaTrader 4 server. Selected symbols are imported to MetaTrader 5 platform after pressing Import button.

In case of successful import, the symbols appear in the Symbols section of the group, from which the import command has been called.

  * By default, all imported symbols are not available for trading.
  * Check the settings carefully before making any symbol available for trading.

  
---  
  
In order to distribute imported symbols among symbol groups, select the necessary symbols and drag them by mouse to a necessary group (or subgroup).

## Configuring the Symbols

All symbol settings from MetaTrader 4 are automatically converted to the appropriate symbol settings for MetaTrader 5. Since the MetaTrader 5 platform features the new parameters that are not present in MetaTrader 4, such parameter values are set to default ones for each symbols imported from MetaTrader 4.

"Percentage" value used to calculate the margin in the MetaTrader 4 symbol settings (Calculation tab) has been redefined and expanded in MetaTrader 5. Therefore, it is not imported. In MetaTrader 5, you can assign the necessary ratio for each trading operation type and direction separately:

![Margin ratios for a symbol in MetaTrader 5](images/migration_symbol_margin.png)

> Due to differences in [hedged margin (#hedged)](../Platform-Setup/Symbols/Symbol-Settings/Trade/Margin-Calculation/Retail-Forex-CFD-Futures-—-Hedging.md#hedged) calculation between the platforms, the hedged margin value is doubled during the import making margin calculation in MetaTrader 5 similar to the one in MetaTrader 4.

"Filtration level" in MetaTrader 4 symbol filtration settings is inserted into "Soft filtration level" in the MetaTrader 5 symbol settings. Its five-fold value is used as "hard filtration level" parameter, while the hundred-fold one — as "Discard filtration level".

![Importing filtration settings to MetaTrader 5](images/migration_symbol_filter.png)

The minimum and maximum volume, as well as step in MetaTrader 5 are set by default.

## History Data Synchronization between MetaTrader 5 and MetaTrader 4

After importing the symbols, you can download history data for them from your MetaTrader 4 Server. There are some synchronization features to be considered before the start of the process:

  * In order to synchronize history data with MetaTrader 4 server, the latter should have at least one demo group. The group can be disabled.
  * MetaTrader 5 history data is stored only as 1-minute data and converted programmatically into larger timeframes on request from the client terminal, while MetaTrader 4 stores different timeframes.
  * When synchronizing with MetaTrader 4 servers, the system consistently selects the most complete data beginning from one-minute timeframe.  
M1 data is fully taken first. Next, the system attempts to receive the missing part from H1 data. MetaTrader 4 server's hour reading is recorded to the first minute of an hour at MetaTrader 5 server. After that, the attempt is made to receive missing data from D1 timeframe. Daily data of MetaTrader 4 server (for example, 01.03.2009) is recorded to the first minute of a day at MetaTrader 5 server (for example, 01.03.2009 00:00).  
Therefore, clients will be able to receive a complete chart for a historical period only on the timeframe, from which the data has been imported.



![Synchronization scheme](images/synchronization_scheme.png)

Before launching synchronization, specify the source server (your MetaTrader 4 Server) in [Synchronization](../Platform-Setup/Synchronization.md) section of MetaTrader 5 Administrator. The Symbols tab allows you to specify the symbols, the data for which is to be synchronized.

![Synchronizing history data with MetaTrader 4 server](images/migration_sync.png)

To start synchronization, select Services -> Synchronize History in the terminal's main menu.

Data synchronization process can be tracked in the history server [journal](../Platform-Setup/Network-cluster/Journal.md). To do this, enter "Synchronization" (without the quotes) in the search bar of the filtration settings, set Full for a request type and All for an event type, specify the current day and click Request. The following journal entry indicates the completion of a synchronization process:

history synchronization with xxx.xxx.xxx.xxx:xxx finished  
---  
  
Synchronized data can be seen in [Charts](../Platform-Setup/1-Minute-History-Charts.md) section of MetaTrader 5 Administrator.

> MetaTrader 5 has no limitations on the depth of history data and the number of symbols.

```

---

<a id='general-settings-md'></a>
### 6. `General-Settings.md`

```markdown
[🏠 Document Start](../../README.md) / [MetaTrader 5 Trading Platform](../../MetaTrader-5-Trading-Platform.md) / [Migration from MetaTrader 4](../Migration-from-MetaTrader-4.md) / General Settings

[Previous](../Migration-from-MetaTrader-4.md) | [Next](Financial-Instruments.md)

# Migrating the Platform General Settings

Here you can find out how to relocate the general settings of the platform.

## Common

The Common section of MetaTrader 4 contains quite a large number of various platform settings. In MetaTrader 5 these settings are allocated among different sections depending on their destination.

### License data and server name

You can view license data and set the server name to be displayed to clients at the [start page](../Platform-Setup/Start-Page.md) of the platform.

### Server IP address and communication port

It is specified separately for each of the platform servers on the [Network (#network)](../Platform-Setup/Network-cluster/Configuring-Servers.md#network) tab:

![Network](images/network_add_network.png)

### Demo accounts

Demo account settings are specified separately for each [trade server (#demo)](../Platform-Setup/Network-cluster/Configuring-Servers/Trade-Server.md#demo) of the platform:

![Demo account settings](images/migration_common_demo.png)

Account allocation URL is set at the platform [start page](../Platform-Setup/Start-Page.md). From there you can also specify certain groups, in which clients are to open demo accounts via the terminals.

### Time zone and daylight saving time

General time settings are specified together with the operation schedule in the [Time](../Platform-Setup/Time.md) section:

![Relocating time settings](images/migration_time.png)

### End of day, swap operation and report generation

Trading days and months closing settings are located in the [trade server (#end-of-day)](../Platform-Setup/Network-cluster/Configuring-Servers/Trade-Server.md#end-of-day). The main distinguishing feature of the settings block is that swap operation method in MetaTrader 5 is defined separately for each [trading instrument](../Platform-Setup/Symbols/Symbol-Settings/Swaps.md), rather than for the entire server.

![Relocating end of day and report generation](images/migration_reports.png)

### Storing emails and ticks

MetaTrader 5 does not allow specifying email and tick data storage parameters. This data is always stored without depth limitations.

### Time optimization

The time of conducting all operations necessary to increase performance and reliability is set separately for each platform server on the [Service (#service)](../Platform-Setup/Network-cluster/Configuring-Servers.md#service) tab.

### Protection against DDoS attacks

These settings are located in the [access server (#antiflood)](../Platform-Setup/Network-cluster/Configuring-Servers/Access-Server.md#antiflood). Apart from the number of allowed connections, MetaTrader 5 enables you to configure the number of connection errors.

![Access](images/network_add_access.png)

### Data feed switch timeout

This parameter is located in the [history server](../Platform-Setup/Network-cluster/Configuring-Servers/History-Server.md):

![Data feed switch timeout](images/network_add_history.png)

### Version update mode

The mode is set at the platform [start page](../Platform-Setup/Start-Page.md). In MetaTrader 5, the update settings are similar: you can disable them completely, allow updates to release versions or allow updates both to release and beta versions.

### List of IPs for access of Web services

There is no such parameter in MetaTrader 5. In order to connect to the trade platform via Web API, create a special manager account having the right to ["Enable API/FIX connection" (#account)](../Platform-Setup/Accounts/Editing-Account.md#account) and an [API password (#security)](../Platform-Setup/Accounts/Editing-Account.md#security).

### Paths to databases

In MetaTrader 5, these parameters are not available since data storage has been allocated among different platform components. If you need to allocate the databases, simply install the platform components on different servers.

  * Trade and client databases — [trade server directory]\bases\
  * History data — [history server directory]\history\
  * Logs — [server directory]\logs\



### Network adapter for monitoring

The network controller for monitoring is set separately for each platform server on the [Service (#service)](../Platform-Setup/Network-cluster/Configuring-Servers.md#service) tab:

![Network adapter for monitoring](images/network_add_service.png)

## Data Centers

MetaTrader 5 [Access Servers](../Platform-Setup/Network-cluster/Configuring-Servers/Access-Server.md) are similar to data centers. They also act as intermediate servers reducing the load on the main one and protecting it against DDoS attacks. Access servers can also be installed on dedicated PCs and enabled as a new access point via MetaTrader 5 Administrator. 

> Unlike MetaTrader 4, the fifth version of the platform does not allow direct connection to the trade server. You need at least one access server to do that.

![Relocating data center settings](images/migration_dc.png)

Each access server can run at multiple IP addresses of a dedicated server (if the server provides such an ability) and listen to multiple ports. If the system has multiple access servers, you can set MetaTrader 5 access server priorities on the Access tab.

In MetaTrader 5, all users (administrators, managers and traders) can connect to and work in the system only via MetaTrader 5 Access Server. Permissions tab allows you to configure access to the system to various connection types, thus allocating manager and client connections among different access servers.

Servers tab allows you to specify trade servers the current access server is used with.

In MetaTrader 5, the number of access servers is not limited.

## Access by IP

Relocation of settings for [access by an IP address](../Platform-Setup/Security/Firewall.md) from MetaTrader 4 Server to MetaTrader 5 is simple since the settings are similar in both systems.

![Relocation of settings for access by IP addresses](images/migration_ip.png)

## Working Time

The [working time](../Platform-Setup/Time.md) settings in MetaTrader 4 and MetaTrader 5 are similar:

![Relocating working time settings](images/migration_worktime.png)

## Holidays

[Holiday](../Platform-Setup/Holidays.md) settings in MetaTrader 4 and MetaTrader 5 are similar.

![Relocating holiday settings](images/migration_holiday.png)

```

---

<a id='import-of-accounts-and-trades-md'></a>
### 6. `Import-of-Accounts-and-Trades.md`

```markdown
[🏠 Document Start](../../README.md) / [MetaTrader 5 Trading Platform](../../MetaTrader-5-Trading-Platform.md) / [Migration from MetaTrader 4](../Migration-from-MetaTrader-4.md) / Import of Accounts and Trades

[Previous](Trade-Groups.md) | [Next](Manager-Accounts.md)

<a id="import-of-accounts-and-trades-from-metatrader-4"></a>
# Import of Accounts and Trades from MetaTrader 4 (#import-of-accounts-and-trades-from-metatrader-4)

You can easily import your client database from MetaTrader 4 to MetaTrader 5, including clients' trading operations and history. You will need Administrator accounts in MetaTrader 4 and MetaTrader 5 with permissions to access clients, groups and trading operations.

  * When importing accounts and orders from MetaTrader 4, all related data is transferred as well. Some new order and trade fields that were not present in MetaTrader 4 [are filled with default values (#order-features)](Import-of-Accounts-and-Trades.md#order-features).
  * Before importing clients and trading operations, be sure to configure/import all required [trading instruments](Financial-Instruments.md) and [groups](Trade-Groups.md).

  
---  
  
Open the "[Trading Accounts](../Platform-Setup/Accounts.md)" section in MetaTrader 5 Administrator and click "Import from Server":

![Start import from the context menu of the Accounts section](images/migration_start.png)

Specify the server address and the details of the administrator/management account on it. The account must have the following permissions:

  * Manager (add/edit/delete accounts)
  * Supervise trades
  * Personal details



![Enter the server address, as well as the details of your administrator account on that server](images/migration_server.png)

On the receiving server, the account must have the following permissions:

  * Connection type: MetaTrader 5 Administrator
  * Accounts section: "Accountant", "Access accounts", "Access account personal details"
  * Dealing section: Access to trading orders (if import includes trading history)
  * Configuration settings section: group settings



<a id="request-accounts"></a>
## Request Accounts (#request-accounts)

The first step is to request the accounts you want to import from the source server. Enter your request in the "Choose groups" field. Here you can specify a comma separated list of logins or a more complex query using the "*" masks and the "!" negation symbol.

The "Choose groups" field contains the default request of "!demo*,!manager*,!coverage*,!contest*,*", which allows to select all accounts except those from the groups of demo and manager accounts, as well as coverage and contest groups.

To execute the request click "Request".

![The list of accounts received from the MetaTrader 4 server](images/migration_accounts.png)

Some of the accounts may have a red background, which means they cannot be imported. You can check the reason for that from the tooltip. The following reasons are possible:

  * The currency of the account deposit does not match the deposit currency of the group to which you want to import the account.
  * An account with the same number already exists on the current server or on one of other trade servers of the platform.
  * The account number is out of the range of accounts allowed for the current server.
  * The symbol, for which the account to import has orders or positions, does not exist on the server.
  * The symbol, for which the account to import has orders or positions, has different numbers of decimal places on the source and target servers.
  * The manager account group on the MetaTrader 4 server side does not have access to the financial instrument settings or the group of symbols.



Accounts from MetaTrader 4 can only be imported to groups with the [hedging system of position accounting](../Platform-Setup/Groups/Position-Accounting-Systems.md). Select a group with the hedging system in the "Move to group" field.

Double click on an account to view how it would look like after import. This will open a standard [account viewing](../Platform-Setup/Accounts/Editing-Account.md) window.

You can disable import of individual accounts from the list. To do this, click on the icon at the beginning of the account row, and then it will change to ![No import](images/access_block_icon.png). 

> If a client's name in MetaTrader 4 contains non-Latin characters, it may be imported incorrectly. During import, the current code page of MetaTrader 5 Administrator is used, which corresponds to the selected interface language. For example, a name with Chinese characters will be imported incorrectly if the Administrator terminal is used with English interface.

<a id="enable-import-of-trading-operations"></a>
## Enable Import of Trading Operations (#enable-import-of-trading-operations)

To import trading operations of selected clients, enable the "Import balance, trades and trade history" option.

In MetaTrader 4, all trading operations are represented as a single entity — an order, which can be open, closed and pending. Additional notions are used in the 5th generation platform for a more detailed and clear presentation: deal and position. During import, each operation can be divided into an order, deal and position depending on the type of a source operation.

Source operation | History in MetaTrader 4 | History in MetaTrader 5  
Open order | 1 operation | 2 operations: an order to open a position, an opening deal  
Closed order | 1 operation | 4 operations: an order to open a position, an order to close a position, an opening deal, a closing deal  
Pending order | 1 operation | 1 operation  
  
<a id="order-features"></a>
### Note when importing orders (#order-features)

  * "Migration" is specified in the "Reason" field of orders
  * Fill or Kill policy is set for all orders
  * If the expiry type is not specified in the source order, Good Till Canceled is set, otherwise the specified date is used.
  * Standard commission specified in the source open order in MetaTrader 4 is imported to the "Swap" field of the relevant position on the MetaTrader 5 side



<a id="note-when-importing-deals"></a>
### Note when importing deals (#note-when-importing-deals)

  * Balance operations are imported "as is"
  * Entry and exit trades are created based on the orders in accordance with the above table



<a id="ticket"></a>
### Importing Tickets (#ticket)

Up to four history records in MetaTrader 5 can correspond to one MetaTrader 4 history record. That is why MetaTrader 4 tickets of orders and positions (including history orders) are not written directly to the appropriate fields of MetaTrader 5 orders, deals and positions during import. New tickets are given to all imported trading records. Ticket numbers are assigned in the ascending order from the appropriate range of order, deal and position tickers set for the MetaTrader 5 trade server.

Tickets of orders from MetaTrader 4 are copied to the 'ID' field (ID in the external trading system) of orders, deals and positions created on their basis. For example, when you import an open order from MetaTrader 4, three trade records are created in MetaTrader 5: an opening order, an opening deal, and an open position. The ticket of the MetaTrader 4 order will be written to the ID field of each of these trading records. The # character is added before the ticket number.

![Writing the MetaTrader 4 ticket to the ID field of trade records on the MetaTrader 5 side](images/migration_ticket.png)

> If the comment of the source order contains non-Latin characters, it can be imported incorrectly. During import, the current code page of MetaTrader 5 Administrator is used, which corresponds to the selected interface language. For example, a comment written in Chinese will be imported incorrectly if the Administrator terminal is used with English interface.

<a id="result-of-import"></a>
## Result of Import (#result-of-import)

The total number and the number of imported accounts will be shown on the last step:

![Result of Import](images/migration_result.png)

Import details are also available in the trade server journal.

  * After import, the appropriate accounts on the MetaTrader 4 server must be disabled or set to the "read-only" mode to avoid trading state mismatch with MetaTrader 5.


  * After completing the import for accounts having open positions, you can see the differences in equity and free margin in the Manager terminal. This may happen if quotes in your MetaTrader 5 platform are significantly different from the ones in MetaTrader 4 or a data feed is not configured at all. The Manager terminal calculates these values in real time according to the current prices in the platform. In the Administrator terminal, there are no differences (the values coincide with MetaTrader 4) since the data is taken directly from the accounts and are not recalculated.

  
---  
  
<a id="client-connection-and-passwords"></a>
## Client connection and passwords (#client-connection-and-passwords)

Random passwords are generated for imported accounts. Hashes of passwords that were used on the MetaTrader 4 accounts are saved in the client record. They are used for verification during the first account connection in MetaTrader 5.

During the first connection to the imported account, the client will attempt to connect using the old password. Upon entering the incorrect password (since a new random password has been generated), a welcome dialog will be displayed:

![A welcome dialog for the client after migration to MetaTrader 5](images/migration_client_side.png)

The old password used in MetaTrader 4 should be specified here. The client will not be able to continue without this password. A new password should be set here, which will later be used to connect to the account.

If authenticated successfully, the dialog will not be displayed again. Once connected, the client will be able to continue using the account, just as if it has been opened in MetaTrader 5.

> You can set a new password for the imported account via the administrator or manager terminal and provide it to the client. The welcome dialog will not be displayed in this case. After password change, the hash of the MetaTrader 4 password is deleted from the client record.

<a id="import-features"></a>
## Import Features (#import-features)

Accounts are imported in packages each containing 100 account. If an account from the package could not be imported, you will need to repeat the import. If errors occur, the previous state will not be restored. The accounts and trade operations from the package successfully imported before the error will not be removed. Before re-import, remove them manually in the following order:

  * Orders
  * Deals
  * Positions
  * Accounts



Importing may take a long time: it depends on the database size and your Internet connection speed.

```

---

<a id='manager-accounts-md'></a>
### 6. `Manager-Accounts.md`

```markdown
[🏠 Document Start](../../README.md) / [MetaTrader 5 Trading Platform](../../MetaTrader-5-Trading-Platform.md) / [Migration from MetaTrader 4](../Migration-from-MetaTrader-4.md) / Manager Accounts

[Previous](Import-of-Accounts-and-Trades.md) | [Next](Data-Feeds.md)

# Manager Accounts

The essential difference between the MetaTrader 5 system from the MetaTrader 4 server is an ability to create multiple manager\* groups. This means that it is now possible to divide manager accounts so that different symbols (symbol groups) are available to them. Besides, they may receive different news, have different security settings and connect to different trade servers.

After installing the MetaTrader 4 server, the manager "1" with the highest server access level rights is created. In MetaTrader 5 platform, such an account is created by default as well but it has the login "1000".

Similarly to the fourth platform version, [open an account](../Platform-Setup/Accounts/Creating-Account.md) in the manager group and add a new entry in the [Managers](../Platform-Setup/Managers.md) section to create a manager account in MetaTrader 5. After that, configure the rights.

## Setting the Manager Rights

Most MetaTrader 4 access rights have retained their functions in MetaTrader 5. When you start working in MetaTrader 5, you are able to open manager accounts identical to MetaTrader 4 server ones in terms of access right settings.

  * Login, Groups and Email fields on the MetaTrader 4 server match the [Common (#common)](../Platform-Setup/Managers.md#common) tab settings of MetaTrader 5 manager account.
  * "Access Rights" block corresponds to the [Permissions (#permissions)](../Platform-Setup/Managers.md#permissions) tab in MetaTrader 5.
  * "IP filter" field matches the "IP Access List" tab.



![Manager settings in MetaTrader 4 and MetaTrader 5](images/migration_manager.png)

The table below shows the correlation between MetaTrader 4 and MetaTrader 5 access rights:

MetaTrader 4 | MetaTrader 5  
---|---  
Manager (add/edit/delete accounts) | Access accounts Access the account personal details Edit accounts  
Administrator (full access to server configuration) | It corresponds to enabling all permissions.  
Reports | Receive reports  
Internal mail system | Send emails  
Send news | Send news  
Connections (show online clients) | View currently connected clients  
Configure server plugins | Configure plugins  
Access to technical support page | Access technical support page  
Push notifications | Push notifications  
Supervise trades | Access orders and positions  
Accountant (deposit/credit/withdrawal money) | Accountant (deposit/withdraw)  
Risk manager | Risk manager  
Journals (direct access to server journals) | Access server logs  
Edit prices, spreads, execution types | Throw in quotes  
Personal details | Access the account personal details  
Automatic server reports | Receive automatic server reports  
Access to Applications Market | Access to Applications Market  
  
## Request Routing

The MetaTrader 5 manager settings have no parameters similar to symbol routing table of MetaTrader 4. However, the identical parameters can be configured in a separate [Routing](../Platform-Setup/Routing.md) section of the Administrator terminal. The new section allows configuring routing in MetaTrader 5 in a more flexible and efficient manner.

Below you can see how to reproduce the settings of the MetaTrader 4 routing table in the MetaTrader 5 Routing section. In our example, the manager "1" is responsible for processing all trade requests with the volumes from 0 to 10 lots at "Forex" group symbols on MetaTrader 4 server:

![MetaTrader 4 request routing table](images/migration_manager_routing.png)

First, create a custom rule and set conditions for processing trade operations. Then use the Dealers tab to specify the manager who will process trade requests that meet the rule conditions.

![Configuring trade requests routing to the manager](images/migration_manager_routing2.png)

Specify the following parameters:

  * Rule name.
  * Perform action — "Process to dealers". Enable "skip this rule if no dealers online" option to avoid missing trade requests if there are no managers online. In this case, if there is no appropriate manager online, all requests meeting the rule are processed according to the next rule in the list (with the lower priority).
  * Select All for "Where request is:" and "Where order is:" options.
  * Add the following rules for "Where conditions are:" section:


  * "Client group" — set "real\real" in order to limit the manager operation by processing client requests from the real account group.
  * "Request volume" — this condition corresponds to the level of maximum and minimum lots of the MetaTrader 4 routing table (from 0 to 10).
  * "Symbols" — select Forex symbols similar to the MetaTrader 4 settings.



Next, add the manager "1000" on the Dealers tab of the rule. Please note that you can assign more than one dealer for a single rule.

```

---

<a id='trade-groups-md'></a>
### 6. `Trade-Groups.md`

```markdown
[🏠 Document Start](../../README.md) / [MetaTrader 5 Trading Platform](../../MetaTrader-5-Trading-Platform.md) / [Migration from MetaTrader 4](../Migration-from-MetaTrader-4.md) / Trade Groups

[Previous](Financial-Instruments.md) | [Next](Import-of-Accounts-and-Trades.md)

# Importing and Setting Trade Groups

[Group](../Platform-Setup/Groups.md) parameters in MetaTrader 5 provide more flexibility as compared to MetaTrader 4. The total number of groups in MetaTrader 5 is not limited.

MetaTrader 5 supports the same functions as MetaTrader 4 except for a few functions related to hedging. MetaTrader 5 does not have the "Multiple Close by orders" and "Auto close-out" functions.

## Import of Groups

Use the [import of groups](../Platform-Setup/Groups/Import-of.md) to copy all groups and their settings from MetaTrader 4 server to the MetaTrader 5 platform. 

  * When you import groups, existing settings are converted and default values are assigned to missing settings.
  * Trade settings of symbols for the groups are not imported.
  * Groups from the MetaTrader 4 server are imported into the currently selected groups section.

  
---  
  
![Importing groups from MetaTrader 4 server](images/migration_group_import.png)

Select "MetaTrader 4" server type and specify connection data: IP address and server port, as well as account login and password. The account used for importing symbols should be opened in the manager group and have Administrator right.

![Importing groups from MetaTrader 4 server](images/migration_group_import2.png)

The next window shows the list of all groups that can be imported from MetaTrader 4 server. Selected groups are imported to MetaTrader 5 platform after pressing Import button.

  * After importing, check the settings of all groups.
  * All groups [are bound (#trade-server)](../Platform-Setup/Groups/Group-Settings.md#trade-server) to the main trade server. After importing the binding can be changed.
  * Only new groups are imported. Settings of existing groups of the same name are not overwritten.

  
---  
  
## Account Group Settings

MetaTrader 5 platform group settings have more tabs. This is due to the fact that MetaTrader 5 features additional group settings not present in MetaTrader 4. Most MetaTrader 4 settings have remained in MetaTrader 5.

![MetaTrader 5 client groups have more settings](images/migration_group.png)

## Individual Symbol Settings

MetaTrader 5 features considerably expanded [trading symbol settings redefining (#symbols)](../Platform-Setup/Groups/Group-Settings.md#symbols) options.

![MetaTrader 5 allows you to redefine plenty of trading symbol parameters](images/migration_group_symbol.png)

## Commission Settings

In MetaTrader 5, [commission (#commissions)](../Platform-Setup/Groups/Group-Settings.md#commissions) settings can be found on a separate tab. The number of settings has significantly increased: charging time, dependence on trade volume and turnover, etc.

![In MetaTrader 5, commission settings are located on a separate tab](images/migration_group_commission.png)

## Processing Trade Requests

Now, trade request execution settings are not limited to three types ("Manual only, no automation", "Automatic only" and "Manual, but automatic if no dealers online") like in MetaTrader 4. [Routing](../Platform-Setup/Routing.md) section introduced in MetaTrader 5 allows you to create custom rules and conditions with virtually any combination of settings and execution types.

![Configuring trade requests execution](images/migration_group_routing.png)

```

---
