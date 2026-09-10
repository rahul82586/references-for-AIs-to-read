# 📁 105-mt5-repository

- **Generated:** 2026-09-10 12:10
- **Total Files:** 5
- **Source:** `C:\Users\DELL\Downloads\backend_code-main (1)\backend_code-main (2)\bridge_manual_md\105-mt5-repository`

---

## 📑 Table of Contents

1. [README.md](#readme-md)
2. [mt5-centroid-dom-feeder-manual.md](#mt5-centroid-dom-feeder-manual-md)
3. [mt5-centroid-gateway-manual.md](#mt5-centroid-gateway-manual-md)
4. [mt5-centroid-installers.md](#mt5-centroid-installers-md)
5. [mt5-centroid-tob-feeder-manual.md](#mt5-centroid-tob-feeder-manual-md)

---

## 🌲 Project Structure

```
105-mt5-repository/
├── mt5-centroid-dom-feeder-manual.md
├── mt5-centroid-gateway-manual.md
├── mt5-centroid-installers.md
├── mt5-centroid-tob-feeder-manual.md
└── README.md
```

---

## 📄 Files

<a id='readme-md'></a>
### 5. `README.md`

```markdown
[🏠 Document Start](..\README.md) / MT5 Repository

# MT5 Repository

Welcome to the section for setting up your Gateway and Feeder for MT5. Here, you'll find concise guides and the latest installer for a
seamless setup experience.




```

---

<a id='mt5-centroid-dom-feeder-manual-md'></a>
### 5. `mt5-centroid-dom-feeder-manual.md`

```markdown
[🏠 Document Start](..\README.md) / [MT5 Centroid TOB Feeder Manual](README.md) / MT5 Centroid DOM Feeder Manual

# MT5 Centroid DOM Feeder Manual

Before initiating the setup for the Centroid MT5 DOM Feeder, you'll need to provide the following information to whitelist your IPs:
1. Provide the IP of all MT5 Live Servers where the MT5 Feeder will be installed.
2. Supply the IP of all MT5 Live Backup Servers.
To configure the Centroid MT5 DOM Feeder, follow the instructions below:
1. Remotely log in to the server where the MT5 Server is installed using RDP or another tool.
2. Copy the Centroid MT5 Datafeed folder into the "Feeder" directory of your MT5 History Server installation. “The path will resemble D
or C:\MetaTrader 5 Platform\History\Datafeed.”
Note:
1. The installation process does not necessitate stopping the MT5 Service.
2. The Centroid MT5 Feeder will be automatically duplicated to the MT5 Backup Server.
To set up the Centroid MT5 DOM Feeder:
1. Log into MT5 Administrator and navigate to Datafeed.
2. Add a new Datafeed.
3. Customize the newly added Feeder as follows:
Name: Specify the configured Feeder's name.
Module: Locate the Feeder file within the uploaded folder.
Select: Choose "Quotes" from the dropdown.
Trading Server: Provide the DNS and Port details given by Centroid.
Trading Login: Enter the trading login ID provided by Centroid.
Password: Input the trading password provided by Centroid.
Parameters: Sender and Input the TargetCompID provided by Centroid.
Essential Setup Information
Installation
The new plugin can be installed as either a Data Feed or a Gateway. It is recommended that this feeder be installed under
datafeed. If there’s a requirement to install it as a Gateway, please contact our support team via Skype/Slack or email.
Configuration

Note: Make certain that all the Symbols intended for pricing by the Centroid Feeder are appropriately listed in the Symbols tabs,
respectively.
If the Sender is not added in the parameters, the DOM Feeder will not be able to establish a connection with the bridge.

When upgrading the Centroid MT5 DOM Feeder to a newer version, adhere to the following steps, ensuring the new folder supersedes the
old one for simplicity:
To enhance the Centroid DOM MT5 Feeder, proceed with the following instructions:
1. Access the Server: Remotely access the server where the MT5 History Server is installed, using RDP or any other tool.
2. Backup the Old Version: Create a backup by copying the existing Centroid DOM Feeder to another folder, ensuring the ability to
revert the update if needed.
3. Disable the Centroid Feeder: Before replacing the file, it is recommended to disable the “Centroid DOM Feeder” from the MT5
Administrator.
4. Replace the File: Replace the existing Centroid DOM Feeder .exe file in the "Datafeed" folder of your MT5 History Server installation
with the new one, maintaining the exact name.
5. Version Monitor: In the MT5 Administrator, monitor the disabled feeder's version under status. Once the correct version is loaded
successfully, enable the Feeder.
6. Enable the Centroid Feeder: Re-enable the Feeder using the MT5 Administrator.
Enhancing the Feeder
How to Backup:
Please ensure that the existing Centroid DOM Feeder is copied to a location outside the DataFeed folder (e.g., Desktop or any
other preferred directory). This will prevent the backup file from appearing in the drop-down menu in MT5.
The DOM Feeder will remain connected, as the continuous heartbeat exchange ensures an active connection, even if the prices
are not streamed from your bridge to MT5.


```

---

<a id='mt5-centroid-gateway-manual-md'></a>
### 5. `mt5-centroid-gateway-manual.md`

```markdown
[🏠 Document Start](..\README.md) / [MT5 Centroid DOM Feeder Manual](README.md) / MT5 Centroid Gateway Manual

# MT5 Centroid Gateway Manual

Before initiating the setup for the Centroid MT5 Gateway, you'll need to provide the following information to whitelist your IPs:
1. Provide the IP or DNS of all MT5 Live Servers where the MT5 Gateway will be installed.
2. Supply the IP or DNS of all MT5 Live Backup Servers.
To configure the Centroid MT5 Gateway, follow the instructions below:
1. Remotely log in to the server where the MT5 Server is installed using RDP or another tool.
2. Copy the Centroid MT5 Gateway folder into the "Gateway" directory of your MT5 History Server installation. “The path will resemble
D or C:\MetaTrader 5 Platform\History\Gateway.”
Note:
1. The installation process does not necessitate stopping the MT5 Service.
2. The Centroid MT5 Gateway will be automatically duplicated to the MT5 Backup Server.
To set up the Centroid MT5 Gateway:
1. Log into MT5 Administrator and navigate to Gateways.
2. Add a new Gateway.
3. Customize the newly added Gateway as follows:
Name: Specify the configured Gateway's name.
Module: Locate the Gateway file within the uploaded folder.
Select: Choose "Trade Only" from the dropdown.
Trading Server: Provide the DNS and Port details given by Centroid.
Trading Login: Enter the trading login ID provided by Centroid.
Password: Input the trading password provided by Centroid.
Essential Setup Information
Installation
Configuration

Note: Make certain that all the Groups and Symbols intended for processing by the Gateway are appropriately listed in the Groups and
Symbols tabs, respectively.


When upgrading the Centroid MT5 Gateway to a newer version, adhere to the following steps, ensuring the new folder supersedes the old
one for simplicity:
To enhance the Centroid MT5 Gateway, proceed with the following instructions:
1. Access the Server: Remotely access the server where the MT5 Server is installed, using RDP or any other tool.
2. Backup the Old Version: Safeguard your current Centroid MT5 Gateway folder by copying it into a separate folder. This backup
facilitates a seamless reversion to the previous version if necessary.
3. Disable the Centroid Gateway: Before replacing the file, it is recommended to disable the “Centroid Gateway” from the MT5
Administrator.
4. Replace the File: Overwrite the existing Centroid MT5 Gateway folder in the MT5 History Installation with the new one.
5. Enable the Centroid Gateway: Re-enable the Gateway using the MT5 Administrator.
To Set-Up the Centroid Gateway in your MT5, please follow the steps outlined below:
Updating the Gateway
Setting up the “Centroid Gateway”


Let's categorize the parameters into two groups:
General Parameters
Facilitating the connection of your "Centroid Gateway" (MT5) to the "Centroid Bridge” (Bridge).
Define the "Execution Rules."
The routing rules determine how trades from various MT5 Groups, Logins, Groups of Symbols, or Symbols are directed to specific
accounts or Taker Execution Models (TEM) on the Centroid Bridge.
Explanation:
sec = group of symbols (Example: Forex\Major)
sy = symbols
g = groups
ac= accounts / logins
tem = Taker Execution Model on the “Centroid Bridge”
dir = direction of the order (close/open)
1. No Filters
2. Group Filter
Sender Example: TD_Username This is available in the 'Centroid Bridge' Taker -> Config -> SenderCompID. Please
note: The format is supposed to be TD_Username.
Account Example: TEM-1, Test_TEM,
Plain_TEM
This Account will represent that, you wish to target this Account while executing your
trades, this is available in the "Centroid Bridge" under Taker -> Taker Execution
Model (TEM) and this will be further used while establishing the "Execution Rules".
Parameter Value Description
AccCfg.1 sec=*;g=*;tem=Test_TEM This rule defines all the securities and all the groups will target one Taker
Execution Model “TEM” i.e. Test_TEM
Parameter Value Description


3. Symbol and Group Filter
4. Account Filter
AccCfg.1 sec=*;g=ABC\USD;tem=TEM-1 This rule defines all the securities from a specific group i.e. “ABC/USD” will
target to TEM → TEM-1
AccCfg.2 sec=*;g=ABC\USD,Testonly\A-
1,Testonly\B-2;tem=TEM-1
This rule defines Multiple Groups Targeting one TEM
AccCfg.3 sec=*;g=Testonly\*;tem=5points_TEM This rule defines All the Groups under Testonly\ Targeting one TEM
Parameter Value Description
AccCfg.1 sy=EURUSD.test;g=NYZ\USD;tem=TEM-
2
This rule defines only symbol “EURUSD.test” from the group
“NYZ\USD” will target to TEM → TEM-2
AccCfg.2 sy=EURUSD.test,GBPUSD.test;g=NYZ\
USD;tem=TEM-2
This rule defines Multiple Symbols from the group “NYZ\USD”
will target to TEM → TEM-2
AccCfg.3 sy=EUR*;g=NYZ\USD,Testonly\A1;tem=
TEM-2
This rule defines All EUR symbols from specific two groups will
target TEM → TEM-2
Parameter Value Description
AccCfg.1 sy=*;ac=100012;tem=Plain_TEM This rule defines all the symbols available in the account 100012 will
target to TEM → Plain_TEM
Note: Account rules should always be placed at the Top of all the
Group rules, as the “Gateway” follows Top-Down Approach.
Parameter Value Description

5. Entry Direction Filter
Additional Parameters
Configure these parameters to utilize the add-on features provided by the "Centroid Bridge."
1. EnGiveUp
Configuration Guide →
Assign the configured "Centroid Gateway" to the "Slave Account" to establish a seamless connection.
AccCfg.2 sy=*;ac=100012,100015,102256;tem
=Plain_TEM
This rule defines Multiple Accounts/Logins Targeting one TEM
AccCfg.3 ac=501265,511456;tem=TEM-2 This rule defines Multiple Accounts/Logins Targeting one TEM
AccCfg.1 sec=*;g=real/fx-
1;tem=Plain_TEM;dir=in
This rule defines all the symbols available in the group real/fx-1 from
any account with deal entry as IN or opening orders will be directed to
Plain_TEM
AccCfg.2 sec=*;g=real/fx-
1;tem=Slip_TEM;dir=out
This rule defines all the symbols available in the group real/fx-1 from
any account with deal entry as OUT or closing orders will be directed
to Slip_TEM
Parameter Value Description

2. EnTradeCopy
Configuration Guide →
1. Add a parameter in the "Centroid Gateway" for optimal settings.
2. Assign the configured "Centroid Gateway" to the "Slave Account" to establish a seamless connection.
EnTradeCopy Y The Parameter is enabled and it allows to send copy trades to the
“Slave Account”
EnTradeCopy N The Parameter is disabled
Parameter Value Explanation

3. EnReturnFillPolicy
4. Configuration of Limit Orders
EnReturnFillPolicy Y This parameter is pertinent to pending orders in MT5. When enabled, it
permits MT5 to resend the remaining volume in case of full or partial
order cancellation.
EnReturnFillPolicy N The Parameter is disabled, and the pending order will be cancelled.
Parameter Value Explanation

5. Limit Order Deviation Configuration
lmt Y: Yes (Send as a Limit Order)
Not specified (Send as a
Market Order)
Enabling the "lmt" parameter by setting it to "Y" facilitates the transmission of pending
orders, specifically Sell Limit and Buy Limit types, to the Bridge as Limit orders upon
activation.
Ordinarily, these order types are sent as Market orders by default.
Sample Rule: sec=*;g=Testonly\A-1;tem=TEM-1;lmt=Y
stp Y: Yes (Send as a Limit Order)
Not specified (Send as a
Market Order)
Enabling the "stp" parameter by setting it to "Y" enables the transmission of pending
orders, specifically Sell Stop and Buy Stop types, to the Aggregator as Limit orders upon
activation.
Ordinarily, these order types are sent as Market orders by default.
Sample Rule: sec=*;g=Testonly\A-1;tem=TEM-1;stp=Y
sl Y: Yes (Send as a Limit Order)
Not specified (Send as a
Market Order)
Enabling the "sl" parameter by setting it to "Y" enables the transmission of Stop Loss
triggered orders to the Aggregator as Limit orders upon activation.
Ordinarily, these order types are sent as Market orders by default.
Sample Rule: sec=*;g=Testonly\B-1;tem=TEM-1;sl=Y
tp Y: Yes (Send as a Limit Order)
Not specified (Send as a
Market Order)
Enabling the "tp" parameter by setting it to "Y" enables the transmission of Take Profit
triggered orders to the Aggregator as Limit orders upon activation.
Ordinarily, these order types are sent as Market orders by default.
Sample Rule: sec=*;g=Testonly\B-2;tem=TEM-1;tp=Y
Paramet
er
Value Explanation


6. Configuration to Force Price for Trading Accounts when a trade placed by a Manager

dev 10, 5, 7, 3 (In Points) Enabling the "dev" parameter by setting it to the desired value (in points), hence allowing
for the acceptance of deviation concerning Limit Orders. Deviation is consistently
measured in points. It's essential to note that for deviation to function, your limit
configurations must be in place; deviation operates in conjunction with Limit orders and
cannot function independently.
Parameter Value Explanation
ForceManagerPx Y: Yes (Manager can Force
Prices)
Not specified (Manager
cannot Force Prices)
Enabling the "ForceManagerPx" parameter by setting it to 'Y' grants authority to
managers listed in "ListForceManagerPx" to force prices against the current
market price for the trading accounts.
ListForceManagerPx 1012, 1013, 1015 The authority to force prices is exclusive to the manager number specified in
the "ListForceManagerPx" parameter.
Parameter Value Explanation


```

---

<a id='mt5-centroid-installers-md'></a>
### 5. `mt5-centroid-installers.md`

```markdown
[🏠 Document Start](..\README.md) / [MT5 Repository](README.md) / MT5 Centroid Installers

# MT5 Centroid Installers

Version Installer Status
137 Centroid_MT5_Gateway_v137.zip Old Version
134 Centroid_MT5_Gateway_v134 No longer available
133 Centroid_MT5_Gateway_v133 No longer available
MT5 Gateway Installer
Version Installer Status
110 Centroid_MT5_TOB_Feeder_v110.zip Latest Version
109 Centroid_MT5_TOB_Feeder_v109.zip Old Version
108 Centroid_MT5_Feeder_v108 No longer available
107 Centroid_MT5_Feeder_v107 No longer available
MT5 Top Of Book (TOB) Feeder Installer
Version Installer Status
115 Centroid_MT5_DOM_Feeder_v115.zip Latest Version
MT5 Depth Of Market (DOM) Feeder Installer


```

---

<a id='mt5-centroid-tob-feeder-manual-md'></a>
### 5. `mt5-centroid-tob-feeder-manual.md`

```markdown
[🏠 Document Start](..\README.md) / [MT5 Centroid Installers](README.md) / MT5 Centroid TOB Feeder Manual

# MT5 Centroid TOB Feeder Manual

Before initiating the setup for the Centroid MT5 Feeder, you'll need to provide the following information to whitelist your IPs:
1. Provide the IP of all MT5 Live Servers where the MT5 Feeder will be installed.
2. Supply the IP of all MT5 Live Backup Servers.
To configure the Centroid MT5 Feeder, follow the instructions below:
1. Remotely log in to the server where the MT5 Server is installed using RDP or another tool.
2. Copy the Centroid MT5 Datafeed folder into the "Feeder" directory of your MT5 History Server installation. “The path will resemble D
or C:\MetaTrader 5 Platform\History\Datafeed.”
Note:
1. The installation process does not necessitate stopping the MT5 Service.
2. The Centroid MT5 Feeder will be automatically duplicated to the MT5 Backup Server.
To set up the Centroid MT5 Feeder:
1. Log into MT5 Administrator and navigate to Datafeed.
2. Add a new Datafeed.
3. Customize the newly added Feeder as follows:
Name: Specify the configured Feeder's name.
Module: Locate the Feeder file within the uploaded folder.
Select: Choose "Quotes" from the dropdown.
Trading Server: Provide the DNS and Port details given by Centroid.
Trading Login: Enter the trading login ID provided by Centroid.
Password: Input the trading password provided by Centroid.
Essential Setup Information
Installation
Configuration

Note: Make certain that all the Symbols intended for pricing by the Centroid Feeder are appropriately listed in the Symbols tabs,
respectively.
When upgrading the Centroid MT5 TOB Feeder to a newer version, adhere to the following steps, ensuring the new folder supersedes the
old one for simplicity:
To enhance the Centroid TOB MT5 Feeder, proceed with the following instructions:
1. Access the Server: Remotely access the server where the MT5 History Server is installed, using RDP or any other tool.
2. Backup the Old Version: Create a backup by copying the existing Centroid TOB Feeder to another folder, ensuring the ability to revert
the update if needed.
3. Disable the Centroid Feeder: Before replacing the file, it is recommended to disable the “Centroid TOB Feeder” from the MT5
Administrator.
4. Replace the File: Replace the existing Centroid TOB Feeder .exe file in the "Datafeed" folder of your MT5 History Server installation
with the new one, maintaining the exact name.
5. Version Monitor: In the MT5 Administrator, monitor the disabled feeder's version under status. Once the correct version is loaded
successfully, enable the Feeder.
Enhancing the Feeder
How to Backup:
Please ensure that the existing Centroid TOB Feeder is copied to a location outside the DataFeed folder (e.g., Desktop or any
other preferred directory). This will prevent the backup file from appearing in the drop-down menu in MT5.

6. Enable the Centroid Feeder: Re-enable the Feeder using the MT5 Administrator.
Pricing during the Weekend
Do you offer CRYPTO? Are you expecting Prices during the Weekend?
If you offer Crypto prices during the weekend, ensure the weekend pricing session is enabled on both SYMBOL and PLATFORM Levels on the MT4/MT5 side.
Do this only if you are expecting Prices for Crypto During the WEEKEND.
Scenario 1: If you Don’t offer Crypto prices during the weekend, from any plugin apart from Centroid, then ensure the weekend pricing session is disabled on the SYMBOL


and PLATFORM Level at the MT4/MT5 side.
Scenario 2: If any other bridge/plugin is pricing for Crypto and Centroid Feeder is trying to connect, it is better to remove those symbols from the Centroid Feeder.
Do this only in the case of Scenario 1:



```

---
