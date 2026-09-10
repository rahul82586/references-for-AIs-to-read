# 📁 101-mt4-repository

- **Generated:** 2026-09-10 12:10
- **Total Files:** 4
- **Source:** `C:\Users\DELL\Downloads\backend_code-main (1)\backend_code-main (2)\bridge_manual_md\101-mt4-repository`

---

## 📑 Table of Contents

1. [README.md](#readme-md)
2. [mt4-centroid-bridge-manual.md](#mt4-centroid-bridge-manual-md)
3. [mt4-centroid-feeder-manual.md](#mt4-centroid-feeder-manual-md)
4. [mt4-centroid-installers.md](#mt4-centroid-installers-md)

---

## 🌲 Project Structure

```
101-mt4-repository/
├── mt4-centroid-bridge-manual.md
├── mt4-centroid-feeder-manual.md
├── mt4-centroid-installers.md
└── README.md
```

---

## 📄 Files

<a id='readme-md'></a>
### 4. `README.md`

```markdown
[🏠 Document Start](..\README.md) / MT4 Repository

# MT4 Repository

Welcome to the section for setting up your Bridge and Feeder for MT4. Here, you'll find concise guides and the latest installer for a
seamless setup experience.





```

---

<a id='mt4-centroid-bridge-manual-md'></a>
### 4. `mt4-centroid-bridge-manual.md`

```markdown
[🏠 Document Start](..\README.md) / [MT4 Centroid Feeder Manual](README.md) / MT4 Centroid Bridge Manual

# MT4 Centroid Bridge Manual

Before initiating the setup for the Centroid MT4 Bridge plugin, you'll need to provide the following information to whitelist your IPs:
1. Provide the IP or DNS of all MT4 Live Servers where the MT4 Bridge Plugin will be installed
2. Provide the IP or DNS of all MT4 Live Backup Servers
To set up the Centroid MT4 Bridge Plugin, simply follow the below instructions:
1. Remote Server Access: Remotely access the server hosting the MT4 Server using tools such as RDP or any other remote access
method
2. Stop MT4 Services: Stop the MT4 Server through Windows Services by stopping the corresponding service named "MetaTrader 4
Server"
3. File and Configuration Transfer: Transfer the .dll file and the configuration folder for the bridge to the "plugins" directory within your
MT4 Server. The directory path is typically similar to D:\MetaTrader4Server\plugins
4. Restart MT4 Server: Initiate the MT4 Server once again through Windows Services by launching the relevant service named
"MetaTrader 4 Server"
5. Configuration on Backup Server: Repeat the aforementioned steps on your MT4 Backup Server
Important Note: Restart Required After Initial Installation and Configuration
Please be advised that a restart of the MT4 Server is essential after the initial installation and configuration of the Centroid MT4 Bridge
Plugin This step ensures proper activation and integration of the plugin into the MT4 Server environment Kindly follow the outlined
instructions in the documentation to seamlessly complete the setup process
Required Configuration Parameters for Establishing MT4 Server and Centroid Bridge Connection:
Essential Setup Information
Installation of the MT4 Bridge Plugin
Configuration

When upgrading the Centroid MT4 Bridge Plugin to a newer version, adhere to the following steps, ensuring the new folder supersedes
the old one:
The below process ensures a seamless transition, with the only exception being the temporary cessation of the MT4 Server during the .dll
file replacement The subsequent steps outline the update procedure for better clarity:
1. Remote Server Access: Remotely log in to the server hosting the MT4 Server using tools like RDP or any other suitable method
Updating the MT4 Bridge Plugin

2. Create a Backup: As a precautionary measure, copy the existing Centroid MT4 Bridge plugin and its folder to another directory This
backup ensures the ability to revert the update if necessary
3. Stop MT4 Server: Halt the MT4 Server through Windows Services by stopping the relevant service, "MetaTrader 4 Server"
4. Replace Plugin Files: Copy the new Centroid MT4 Bridge Plugin .dll and its folder into the "plugins" directory within your MT4 Server
installation This action effectively replaces the existing plugin files
5. Restart MT4 Server: Restart the MT4 Server through Windows Services by initiating the relevant service, "MetaTrader 4 Server"
6. Apply Update to Backup Server: Repeat the same update steps on your MT4 Backup Server for consistency across your
environment
By adhering to these instructions, the process of updating the Centroid MT4 Bridge Plugin is streamlined, ensuring a smooth transition to
the latest version while maintaining the integrity of your trading infrastructure
To Set-up the Centroid Bridge Plugin in your MT4, please follow the steps outlined below:
Let's categorize the parameters into two groups:
General Parameters
Required Configuration Parameters for Establishing MT4 Server and Centroid Bridge Connection:
Setting up the MT4 Bridge Plugin
User Taker_Name (Centroid_MT4) Description: Specifies the username associated with the FIX session
Configuration: Enter the designated username for authentication
Password b#4592A Description: Denotes the password corresponding to the FIX session
Configuration: Input the specific password required for authentication
Sender TD_Taker_Name
(TD_Centroid_MT4)
Description: Represents the Sender Comp ID of the FIX session
(TD_Username)
Name Value Explanation

Define the "Execution Rules / Routing Rules”
The routing rules determine how trades from various MT4 Groups, Logins, Groups of Symbols, or Symbols are directed to specific
accounts or Taker Execution Models (TEM) on the Centroid Bridge
Explanation:
sec = group of symbols (Example: Forex\Major)
sy = symbols
g = groups
ac= accounts / logins
tem = Taker Execution Model on the “Centroid Bridge”
1. No Filters
2. Group Filter
Configuration: Provide the Sender Comp ID associated with the FIX
session
Host Bridge IP/DNS Description: Specifies the IP address or DNS of the Centroid Bridge
Configuration: Input the accurate IP address or DNS information for the
Bridge
Port 1245, 1523, 100011 Description: Denotes the target port for the FIX session
Configuration: Specify the target port number required for connecting to
the FIX session
AccCfg.1 sec=*;g=*;tem=Test_TEM This rule defines all the securities and all the groups will target one Taker
Execution Model “TEM” ie Test_TEM
Parameter Value Description

3. Symbol and Group Filter
AccCfg.1 sec=*;g=ABC\USD;tem=TEM-1 This rule defines all the securities from a specific group ie “ABC/USD” will
target to TEM → TEM-1
AccCfg.2 sec=*;g=ABC\USD,Testonly\A-
1,Testonly\B-2;tem=TEM-1
This rule defines Multiple Groups Targeting one TEM → TEM-1
AccCfg.3 sec=*;g=Testonly\*;tem=5points_TEM This rule defines All the Groups under Testonly\ Targeting one TEM →
5points_TEM
Parameter Value Description
AccCfg.1 sy=EURUSDtest;g=NYZ\USD;tem=TEM-
2
This rule defines only symbol “EURUSDtest” from the group
“NYZ\USD” will target to TEM → TEM-2
AccCfg.2 sy=EURUSDtest,GBPUSDtest;g=NYZ\U
SD;tem=TEM-2
This rule defines Multiple Symbols from the group “NYZ\USD”
will target to TEM → TEM-2
Parameter Value Description

4. Account Filter
Note: It is recommended to place the Account Rules on top followed by the Group Rules. In the MT4 plugin, it is not feasible to rearrange
rules by moving them from the top to the bottom or vice versa using drag & drop. To accomplish this, one must update the configuration
number (AccCfg) and the plugin will automatically adjust the rule’s positioning.
An example is provided below:
AccCfg.3 sy=EUR*;g=NYZ\USD,Testonly\A1;tem=
TEM-2
This rule defines All EUR symbols from specific two groups will
target TEM → TEM-2
AccCfg.1 sy=*;ac=100012;tem=Plain_TEM This rule defines all the symbols available in the login 100012 will
target to TEM → Plain_TEM
AccCfg.2 sy=*;ac=100012,100015,102256;tem
=Plain_TEM
This rule defines Multiple Accounts/Logins Targeting one TEM →
Plain_TEM
Parameter Value Description


Rules in the Centroid MT4 Bridge Plugin are sorted by the numerical values following "AccCfg." The order matters, as the plugin
processes orders based on the first matching rule
Additional Parameters
Configure these parameters to utilize the add-on features provided by the "Centroid Bridge"
1. STP Configurations Guide
FullStpSecurities FX,Crypto This feature designates a set of securities for which trades will be sent to the
Bridge as 100% STP, regardless of the percentage defined in the Bridge under
TEM
Please note that routing to the Bridge adheres to established rules, but trades for
symbols within the specified securities will be executed as 100% STP
FullStpSymbols XAUUSD This setting identifies a list of symbols for which trades will be directed to the
Bridge as 100% STP, regardless of the percentage specified in the Bridge under
TEM
Please be aware that routing to the Bridge continues to adhere to defined rules,
but trades for the specified symbols will be executed as 100% STP
Name / Parameter
Value Explanation

Note: Adding Multiple Symbols, Securities, Groups, and Logins
You can include multiple symbols, securities, groups, and logins in the respective parameter by using commas (",")
2. BBook Configurations Guide
FullStpGroups NYZ\USD,Testonly\* This configuration designates a set of MT4 groups, ensuring that trades from
these groups are sent to the Bridge as 100% STP, regardless of the percentage
specified in the Bridge under TEM
It's important to note that while routing to the Bridge adheres to predefined rules,
trades associated with logins under the specified groups will be executed as
100% STP
FullStpLogins 1012,10156 This configuration defines a list of MT4 logins, ensuring that trades from these
logins are directed to the Bridge as 100% STP, regardless of the percentage
specified in the Bridge under TEM
It's important to note that while routing to the Bridge continues to adhere to
established rules, trades corresponding to the specified logins will be executed
as 100% STP
FullBBSecurities Forex/Major This configuration allows you to specify a list of securities for which trades will be
directed to the Bridge as 100% B-Book, irrespective of the percentage set in the
Bridge under TEM
While routing to the Bridge continues to follow predefined rules, trades
associated with the specified symbols will be executed exclusively as 100% B-
Book
FullBBSymbols EURUSD,GBPUSD This setting lets you choose certain symbols, ensuring that all their trades are
consistently processed as 100% B-Book in the Bridge
Even though regular routing rules to the Bridge remain in place, the specified
symbols will be handled exclusively as 100% B-Book
FullBBGroups Testonly\B-7 This configuration allows you to designate specific MT4 groups, ensuring that all
trades from these groups are consistently processed as 100% B-Book in the
Bridge
Name / Parameter Value Explanation

Note: Adding Multiple Symbols, Securities, Groups, and Logins
You can include multiple symbols, securities, groups, and logins in the respective parameter by using commas (",")
3. Exclusion Configurations in the Plugin
Note: Adding Multiple Groups and Logins
You can include multiple groups and logins in the respective parameter by using commas (",")
4. Trade Distinction through Configuration Comments
While the regular routing rules to the Bridge apply, trades associated with logins
under the specified groups will be executed exclusively as 100% B-Book
FullBBLogins 558941 This setting enables the selection of specific MT4 logins, ensuring that all trades
from these logins are consistently processed as 100% B-Book in the Bridge
While the regular routing rules to the Bridge apply, trades corresponding to the
specified logins will be executed exclusively as 100% B-Book
IgnoreGroups Testonly\A-10 Specify groups here, and the Centroid MT4 Bridge plugin will completely
disregard their trades
IgnoreLogins 559920,558974 Specify logins here, and the Centroid MT4 Bridge plugin will completely
disregard their trades
Name / Parameter Value Explanation

5. Managing Trade Frequency with ‘PendingOrderLockTimeout’
CommentOrder cenid;sl;tp;so;giveup; The Centroid order ID will be included to orders initiated by a manager or
pending limit orders.
CommentOrder cenid;sl;tp;so;giveup; A "[sl] comment" will be attached to orders with activated stop loss.
CommentOrder cenid;sl;tp;so;giveup; A "[tp] comment" will be appended to orders with activated take profit.
CommentOrder cenid;sl;tp;so;giveup; A "[so] comment" will be appended to the account when Stop Out is Triggered.
CommentOrder cenid;sl;tp;so;giveup; Centroid giveup order ID will be assigned to orders originating from Centroid
giveup.
Name /
Parameter
Value Explanation
PendingOrderLockTi
meout
5 This parameter enables you to regulate the initiation of limit/pending trades, aligning them with the
prevailing prices in MT4. This level of customization empowers you to finely adjust trade frequency
according to your preferences and market dynamics.
Name / Parameter Value Explanation

6. Filtering Trades: Utilizing 'IgnoreManagers' Configuration
7. Enhanced Order Configuration: Utilizing 'EnLimitClosePx'
Note: When working with the "PendingOrderLockTimeout" configuration, it's important to
understand the default, minimum, and maximum values:
Default Duration: The default duration is set at 15 seconds.
Minimum Duration: You can adjust the duration to a minimum of 3 seconds. If the configured
value falls below 3 seconds, it will automatically revert to the default value of 15 seconds.
Maximum Duration: The maximum duration can be set up to 60 seconds. If the configured
value exceeds 60 seconds, it will automatically reset to the default value of 15 seconds.
IgnoreManagers 10012 Implementing the configuration parameter "IgnoreManagers" allows you to specify that any
trades originating from a particular manager login, such as "10012," should be disregarded
by the bridge. This configuration provides a precise method for selectively excluding trades
from specific manager logins based on your requirements
Name / Parameter Value Explanation


8. Configuration to Force Price for Trading Accounts
EnLimitClosePx Y EnLimitClosePx (Enable Limit Close Price):
Y (Yes - Default): Activate pending orders with the default spread and a negative profit.
N (No): Activate pending orders with zero spread and zero profit.
In other words, when "Y" is chosen, pending orders will be triggered with the default spread and a
negative profit. On the other hand, selecting "N" will activate pending orders with no spread (zero
spread) and no profit.
Name /
Parameter
Value Explanation
ForceManagerPx Y: Yes (Manager can Force
Prices)
Not specified (Manager
cannot Force Prices)
Enabling the "ForceManagerPx" parameter by setting it to 'Y' grants authority to
Managers to force prices against the current market price on behalf of the
trading account.
Note: Enabling this config will impact all the Managers, i.e. All the Managers
within the MT4 Admin can force prices.
Parameter Value Explanation


```

---

<a id='mt4-centroid-feeder-manual-md'></a>
### 4. `mt4-centroid-feeder-manual.md`

```markdown
[🏠 Document Start](..\README.md) / [MT4 Centroid Installers](README.md) / MT4 Centroid Feeder Manual

# MT4 Centroid Feeder Manual

Before initiating the setup for the Centroid MT4 Feeder, you'll need to provide the following information to whitelist your IPs:
1. Provide the IP or DNS of all MT4 Live Servers where the MT4 Feeder will be installed
2. Provide the IP or DNS of all MT4 Live Backup Servers
Configuration Steps for Centroid MT4 Feeder
1. Remote Server Access: Remotely access the server hosting the MT4 Server using tools such as RDP or any other remote access
method
2. Stop MT4 Server: Stop the MT4 Server through Windows Services by stopping the corresponding service named "MetaTrader 4
Server"
3. File and Configuration Transfer: Place the Centroid MT4 Feeder .feed File in the 'datafeed' Directory of Your MT4 Server Installation.
The Path Typically Resides at D:\MetaTrader4Server\datafeed.
4. Restart MT4 Server: Initiate the MT4 Server once again through Windows Services by launching the relevant service named
"MetaTrader 4 Server"
5. Consistent Configuration on Backup Server: Repeat the aforementioned steps on your MT4 Backup Server for ensuring consistent
configuration
To set up the Centroid MT4 Feeder, follow these simple instructions:
1. Log in to MT4 Administrator and navigate to Data Feeds.
2. Add a new Data Feed.
3. Configure the newly added Data Feed with the following details:
Name: Enter the name of the configured feeder.
Type: Select "Quotes" from the dropdown list.
File: Locate the feeder file uploaded to the feeder folder on the MT4 Server, ensuring it matches the exact name.
Server: Provide the DNS and Port details given by Centroid.
Login: Enter the trading login ID provided by Centroid.
Password: Input the trading password provided by Centroid.
Keywords: This optional field allows you to specify certain Symbols to be quoted via the Data Feed or excluded. Use "*" for wildcard or
"!" for negation.
Essential Setup Information
Installation of MT4 Feeder
Configuration

When upgrading the Centroid MT4 Feeder to a newer version, adhere to the following steps, ensuring the new folder supersedes the old
one for simplicity:
1. Access the Server: Remotely access the server where the MT4 Server is installed, using RDP or any other tool.
2. Backup the Old Version: Create a backup by copying the existing Centroid feeder to another folder. This backup ensures you can
easily revert the update if needed.
3. Stop MT4 Server: Stop the MetaTrader 4 Server from Windows Services by stopping the relevant service, "MetaTrader 4 Server."
4. Replace the File: Override the existing feeder by copying the new Centroid Feeder .feed file into the "datafeed" folder of your MT4
Server installation.
5. Restart MT4 Server: Start the MetaTrader 4 Server from Windows Services by initiating the relevant service, "MetaTrader 4 Server."
6. Version Monitor: In the MT4 Administrator, monitor the disabled feeder's version under status. Once the correct version is loaded
successfully, enable the Feeder.
7. Enable the Centroid Feeder: Re-enable the Feeder from the MT4 Administrator.
Updating the Feeder


```

---

<a id='mt4-centroid-installers-md'></a>
### 4. `mt4-centroid-installers.md`

```markdown
[🏠 Document Start](..\README.md) / [MT4 Repository](README.md) / MT4 Centroid Installers

# MT4 Centroid Installers


Version Installer Status
238 Centroid_MT4_Bridge_v238.zip Latest Version
237 Centroid_MT4_Bridge_v237.zip Recent Version
236 Centroid_MT4_Bridge_v236.zip Old Version
MT4 Bridge Installer
Version Installer Status
101 Centroid_MT4_Feeder_v101.zip Latest Version
MT4 Feeder Installer
Version Installer Status
103 Centroid_MT4_Operations_v103.zip Latest Version
MT4 Bridge Operations


```

---
