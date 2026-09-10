# 📁 55-monitoring

- **Generated:** 2026-09-10 12:10
- **Total Files:** 9
- **Source:** `C:\Users\DELL\Downloads\backend_code-main (1)\backend_code-main (2)\bridge_manual_md\55-monitoring`

---

## 📑 Table of Contents

1. [README.md](#readme-md)
2. [dividends-completed-jobs.md](#dividends-completed-jobs-md)
3. [logs.md](#logs-md)
4. [maker-status.md](#maker-status-md)
5. [margin-level-alerts.md](#margin-level-alerts-md)
6. [taker-status.md](#taker-status-md)
7. [alerts/README.md](#alerts-readme-md)
8. [alerts/slack-how-to-configure-alerts.md](#alerts-slack-how-to-configure-alerts-md)
9. [alerts/telegram-how-to-configure-alerts.md](#alerts-telegram-how-to-configure-alerts-md)

---

## 🌲 Project Structure

```
55-monitoring/
├── alerts/
│   ├── README.md
│   ├── slack-how-to-configure-alerts.md
│   └── telegram-how-to-configure-alerts.md
├── dividends-completed-jobs.md
├── logs.md
├── maker-status.md
├── margin-level-alerts.md
├── README.md
└── taker-status.md
```

---

## 📄 Files

<a id='readme-md'></a>
### 9. `README.md`

```markdown
[🏠 Document Start](..\README.md) / Monitoring

# Monitoring

The Monitoring module of the Centroid Bridge provides a real-time monitoring tool for Takers and Makers connectivity allowing users to
check connections at all times and troubleshoot any Taker/Maker connectivity issue. Real-time and Historical logs and alerts are also
available in this module. Upon clicking the “Monitoring” button on the left-hand side menu, it expands to show the different components
underneath which are explained in greater detail hereunder.



```

---

<a id='dividends-completed-jobs-md'></a>
### 9. `dividends-completed-jobs.md`

```markdown
[🏠 Document Start](..\README.md) / [Margin Level Alerts](README.md) / Dividends Completed Jobs

# Dividends Completed Jobs




```

---

<a id='logs-md'></a>
### 9. `logs.md`

```markdown
[🏠 Document Start](..\README.md) / [Monitoring](README.md) / Logs

# Logs

Overview
The Logs feature lets you check detailed records of the Centroid Bridge. These logs hold important information for investigating
connectivity, pricing, and trading problems, as well as updates to configurations and other relevant details. You can see current logs in real
time, while past logs are compressed and saved in the Centroid Bridge at regular intervals.
Log Types
In-Depth Explanation of All Log Types
1. Makers
Where to Find the Makers Log: Path → Monitoring → Logs → Makers → Two folders available “marketdata” for pricing “trading” for
trading logs respectively.
Makers Maker logs encompass all the trading and pricing details between your Centroid Bridge and the
corresponding Maker.
Takers Taker logs encompass all the trading and pricing details between your Centroid Bridge and the corresponding
Taker.
Feeder The Feeder contains all the ticks forwarded to your taker, providing real-time ticks specifically tailored for
MT4/MT5 takers only.
Trade Statement If you have Risk Accounts set up in your Centroid Bridge, a statement is generated and stored here at the
end of each day. This statement includes all the transactions conducted throughout the day along with
additional details.
Downloads In addition to the Online Manual, you can conveniently find the most recent versions for both GW and Feeder
in the download section.
System The system log compiles all the details of activities carried out at the bridge level. This includes recording any
changes made to any component on the bridge.
Log type Description

formatted as YY/MM/DD Hours/Minutes/Seconds. For reading the downloaded logs, you can utilize FIX Parser. Follow these steps:
Download the log file, locate the specific order or logline, and copy-paste it into the provided link.
What Are the Logs About: The Maker logs provide valuable insights into whether you are receiving prices from a specific maker. They
also offer information on the reasons for rejection, providing clarity on whether your trade was successful, partially filled, or rejected. In the
case of rejection, the logs specify the reasons behind the rejection, enhancing your understanding of the trading process.
Note: Centroid Bridge stores “Pricing or Market Data” internally for a maximum period of 7 days.


2. Takers
Where to Find the Takers Log: Path → Monitoring → Logs → Takers → Two separate folders available “MD_Taker_Name” for pricing
and “TD_Taker_Name” for trading logs respectively.
Note: For Taker type MT4/MT5 Centroid bridge does not store the ticks in the “marketdata” folder.
How to Download/Read the Logs: To ensure you download the accurate log file, review the timestamp for each file, where the time is
formatted as YY/MM/DD Hours/Minutes/Seconds. For reading the downloaded logs, you can utilize FIX Parser. Follow these steps:
Download the log file, locate the specific order or logline, and copy-paste it into the provided link.
What Are the Logs About: As mentioned earlier, pricing data is not stored for MT4/MT5 taker types. However, through FIX connections,
both Pricing and Trading logs are available. The Trading log is particularly useful for verifying the orders received by the bridge from your
Taker. It provides details on whether the order was filled, rejected, or partially filled at the bridge level, and any corresponding out
messages sent back to your Taker.
Note: For taker connection type “DropCopy” there will be only one folder available as “Trading” Given that it exclusively encompasses a
trading session, the naming convention follows the format DC_TakerName.
3. Feeder
Where to Find the Feeder Log: Path → Monitoring → Logs → Feeder, This log file is specifically designated for your Taker types MT4
and MT5. If enabled on the backend, it will commence storing pricing data for MT4/5 takers. In the presence of both taker types (MT4 and
MT5), the log file consolidates pricing data, and you can distinguish them by entering your Taker Name after downloading the file.
Note: To enable this functionality, it must be activated at the configuration level of your Centroid Bridge. This process can be facilitated
from the support side.


4. Trade Statements
Where to Find the Statement: Path → Monitoring → Logs → Trade Statements
What Is the Statement About: Trade Statements are automatically generated daily and saved as HTML files at the close of each trading
day, provided you have Risk Accounts within your Centroid Bridge. To view a statement, you need to download it to your local machine and
then open it as an HTML file. The Trade Statement adheres to the naming convention: YY/MM/DD_RiskAccountName.html.


5. System
Where to Find the System Logs: Path → Monitoring → Logs → System
What Are the Logs About: The System Log encompasses all changes made at the bridge level, recording any addition or modification to
its components. In addition to these changes, it also keeps a record of all trades, regardless of whether they belong to the A book or B
book. You have the option to download the system logs, and you can read them using a simple text editor like Notepad.
System logs can be categorized into different types, classified as follows:
[I] → Info
[W] → Warning
[E] → Error
[D] → Debug
[T] → Trace
Note: The System Log is typically stored as one log file for an entire day.





```

---

<a id='maker-status-md'></a>
### 9. `maker-status.md`

```markdown
[🏠 Document Start](..\README.md) / [Logs](README.md) / Maker Status

# Maker Status

Overview
The Maker Status component provides real-time health into the connectivity with Makers to ensure that Maker Sessions are connected at
all times in addition to providing statistical data about the connection in addition to prices and execution for each Maker on a per Symbols
basis.
Maker Status
The Maker Status monitoring tool provides real-time visibility over the different sessions i.e. Feeding and Trading of different Makers to
determine whether the session is connected or not. It also provides statistical data in terms of exchange from and into the Centroid Bridge.
Maker The Maker's name can be configured either as a single session encompassing both Feeding and Trading, or as two
separate sessions—Feeding and Trading—depending on the specifications of the Maker.
Status Indicates the status of the connection:
Enabled: If the Maker is enabled from the Maker section.
Disabled: If the Maker is disabled from the Maker section.
STime Indicates whether the connection is within the defined time session:
Within Time: If the connection falls within the specified time session.
Outside Time: If the connection extends beyond the defined time session. For instance, if the Time Session is set from
Monday to Friday, Saturday would be categorized as Outside Time.
Logged
in
Specifies the session's connection status:
Connected: If there is an established connection between the Maker and the Centroid Bridge.
Disconnected: If there is no established connection between the Maker and the Centroid Bridge.
Receive
d
Count
The count of messages received by the Centroid Bridge from the Maker.
Sent
Count
The count of messages sent by the Centroid Bridge to the Maker.
Field Description

Maker Symbol Status
The Maker Symbol status is a very useful real-time tool that allows checking of statistical data with each Maker on a per Symbol basis.
Data are related to prices obtained from the Makers in addition to Orders that are routed to the Makers.
You need to select a combination of at least one Maker and Symbol for the report to be generated.
The report is reset every five minutes where the Centroid Bridge starts counting all over again until the next reset.
Within this module, you have the capability to:
Filter: Click on the four lines next to the Maker and select the desired Maker.
Select/Tick Security or Symbol: Choose a Security or Symbol by selecting or ticking the desired ones.
Export Report (Excel/CSV): Save the report by exporting it to an Excel or CSV file.
Maker The name of the Maker.
Symbol The name of the Symbol under a specific security.
Sub ID The Symbol’s market data subscription ID that is sent to the Maker upon subscription.
Subscribed Indicates whether we are subscribed to the Symbol with the Maker or not.
If ticked, it means we are subscribed to the Symbol.
If un-ticked, it means we are not subscribed to the Symbol.
Ticks Count The number of Ticks or prices updates received for that Symbol during the 5-minute time interval.
Note: If Ticks says “0” that means the respective Maker is not pricing.
Avg Spread The Average Spread of the Symbol in decimal.
Avg Spread
in Points
The Average Spread of the Symbol in points.
Spread Ticks
Count
The number of Ticks or prices updates received for that Symbol based on which the average spread was calculated
during the current time interval.
Delayed
Ticks Count
The number of Ticks or prices updated that were delayed.
Orders Count The total number of Orders executed with the Maker during the time interval irrespective of the Order Size. In other
words, if executed Order is counted as 1 no matter what the Volume is.
Long Orders The total number of Long Orders executed with the Maker during the time interval irrespective of the Order Size.
Short Orders The total number of Short Orders executed with the Maker during the time interval irrespective of the Order Size.
Avg Fill Time The Average Fill Time in microseconds of all Orders that were executed during the current time interval.
Field Description

Avg Travel
Time
The Average Time in microseconds it takes the Order to travel from the Centroid Bridge to the Maker.
Rejected
Count
The number of rejected Orders.
Partial Fills
Count
The number of Orders that resulted in partial fills.
Fully Fills
Count
The number of Orders that were fully filled.
Total Till
Volume
The total notional Volume executed with the Maker during the 5 minute time interval.
Average
Slippage
The Average Slippage in decimals of all executed Orders.
Average
Slippage
Points
The Average Slippage in points of all executed Orders.


```

---

<a id='margin-level-alerts-md'></a>
### 9. `margin-level-alerts.md`

```markdown
[🏠 Document Start](..\README.md) / [Slack: How to configure Alerts](README.md) / Margin Level Alerts

# Margin Level Alerts

Overview
The Margin Level Alerts module facilitates users in examining margin level movements or incidents that transpired on the designated Risk
Account within the Centroid Bridge during a specified time interval. These alerts activate when the margin of the designated risk account
falls below the predefined Warn Level in the Account Group > Risk Account settings.
Request Margin Level Alerts Report
To request a Margin Level Alerts Report
1. Click on the "Toggle here to search" button.
2. Complete the Wizard as detailed below.
3. Click "View Results" to execute the report or "Export to CSV or Excel" file.
Display Margin Level Alerts Report
Once the Margin Level Alerts Report has been generated, you can see the following
Start
Date
The Start Date of your desired time interval.
End Date The End Date of your desired time interval.
Risk
Account
Select the specific Risk Account
Field Description

Click on “Export to CSV” or “Export to Excel” to export the report

Risk Account This column identifies the particular Risk Account referenced.
Margin Level Within this column, you will find the margin level corresponding to the specific risk account at the time of the
incident.
Warn Level This column serves to specify the Warn level at which the Alert was triggered for the particular risk account.
Warn Level
Config
Imprinted within this column is the configured Warn Level at the Risk Account level.
Time This column precisely notes the occurrence time of the incident.
Field Description



```

---

<a id='taker-status-md'></a>
### 9. `taker-status.md`

```markdown
[🏠 Document Start](..\README.md) / [Maker Status](README.md) / Taker Status

# Taker Status

Overview
The Taker Status component offers a live health assessment of all Pricing and Trading connections across all Takers. It serves as a
valuable tool for diagnosing and resolving connectivity issues between Takers and the Centroid Bridge.
The Taker Status is categorized into three sections:
Trading Status
Depth Feeding Status
Feeder Status
Trading Status FIX & MT5, MT4 Trading Connection Status
Depth Feeding Status FIX Clients only Pricing Connection Status
Feeder Status MT5 and MT4 Clients only Pricing Connection Status
Session Type Taker Type Connection Status
Taker The name of the Taker which could be set up as one session combining both Feeding and Trading or two separate
sessions for each, Feeding and Trading.
Status

Shows the Status of the connection.
* Enabled: If Taker is enabled from Taker section.
* Disabled: If Taker is disabled from Taker section.
STime Indicates whether the connection is within the defined time session.
* Within Time: If the connection is within the defined time session.
* Outside Time: If the connection is outside the defined time session.
Example: If Time Session is from Monday to Friday, then Saturday would show Outside Time.
Logged in Indicates whether the session is connected or not.
* Connected: If there is an established connection between the Taker and the Centroid Bridge.
Field Description

Feeder Status
The Feeder Status component oversees the status and health of feeders associated with Takers of MT4, MT5, or Centroid types,
presenting relevant statistics in real time. Moreover, it enables users to inspect all the symbols to which Takers are subscribed on a per
Taker basis.
Subscription List Check
To review the list of symbols to which Takers are subscribed:
1. Click on the "Subscription List" next to the desired Taker.
2. In the pop-up window displaying the list of all subscriptions, enter one or multiple values (comma-separated) into the search box. You
can input either the full symbol name or a part of it. The symbols matching the criteria will be highlighted in yellow.
* Disconnected: If there is no established connection between the Taker and the Centroid Bridge.
Received
Count
The number of messages received by the Centroid Bridge from the Taker.
Sent Count The number of messages sent by the Centroid Bridge to the Taker.
Taker The name of the Taker
IP The IP of the Server on which the feeder/ platform (MT4 or MT4) is installed
Last Ping The last Date and Time the Feeder was pinged successfully
Received
Count
The number of messages received in the Centroid Bridge from the Taker which mainly consist of subscription to
Symbols
Sent
Count
The number of messages sent by the Centroid Bridge to the Taker mainly the ticks pertaining to the quotes streamed into
the Taker via Taker Feeds
Subscripti
on List
Allows to check all the Symbols the Taker is subscribed to, by clicking the button next to the desired Taker
Field Description






```

---

<a id='alerts-readme-md'></a>
### 9. `alerts/README.md`

```markdown
[🏠 Document Start](..\..\README.md) / [Taker Status](..\README.md) / Alerts

# Alerts

Overview
The Alerts feature enables users to review issues or incidents that occurred on the Centroid Bridge within a specified time frame. These
issues are categorized into three levels, indicating the severity of the incidents.
To access Alerts, click on the alert icon located at the top of the page, as illustrated below:
Request Alert Report
To request an Alert Report
1. Click on the "Toggle here to search" button.
2. Complete the Wizard as detailed below.
3. Click "View Results" to execute the report or "Export to CSV or Excel" file.
Display Alert Report
Once the Alert Report has been generated, you can do the following
1. Filter by different columns to look up a particular “Alert”
2. Click the “Export” button to export the list of Alerts to an “Excel file” or a “CSV file”
Start
Date
The Start Date of your desired time interval.
End Date The End Date of your desired time interval.
Urgency This indicates the severity of the Alert as explained below:
Critical: Critical Alert such as a major error that occurred in the Centroid Bridge.
Event: Warning about a misconfiguration that could lead to errors.
Information: General information in the Centroid Bridge such as session Login.
Field Description

Click “Export” and select “Export to Excel” or “Export to CSV”

Urgency This indicates the severity of the Alert as explained below:
Critical: Critical Alert such as a major error that occurred in the Centroid Bridge.
Event: Warning about a misconfiguration that could lead to errors.
Information: General information in the Centroid Bridge such as session login.
Cen Ord
ID
Centroid unique Order ID recorded in the Centroid Bridge.
Headline An informative log message explaining the nature of the Alert.
Time The Date and Time at which the Alert occurred.
Field Description



```

---

<a id='alerts-slack-how-to-configure-alerts-md'></a>
### 9. `alerts/slack-how-to-configure-alerts.md`

```markdown
[🏠 Document Start](..\..\README.md) / [Alerts](..\README.md) / [Alerts](README.md) / Slack: How to configure Alerts

# Slack: How to configure Alerts

Overview
Slack is a cloud-based communication and collaboration platform designed for teams to streamline messaging, share files, and integrate
with various productivity tools including custom applications for automation. Within the Slack application, a bot app can be created to
enable automated interactions with users via text commands. The Slack Bot API facilitates bot delivering messages which Centroid
Solutions integrated into our Centroid Bridge. This integration empowers real-time alerting for critical events, enhancing responsiveness
and communication for bridge broker administrators.
Main Requirements
1. Dedicated Slack App for Bot
2. Bot OAuth Token
3. Channel ID
Important notes:
1. Only 1 Slack app bot is needed per company
2. For the public channel, any users within the company can join the channel
3. For the private channel, the administrator must add their employees to the channel
Creating a Dedicated Slack App (bot) and retrieving Bot OAuth Token
1. Download and install Slack then register for an account
2. Go to https://api.slack.com/apps
3. Click on “Create an App”
4. Select “From an app manifest”
5. Select your workspace
6. Select “YAML” then clear the script
7. Add the below Script
8. Click “Next” then “Create”
9. Click “OAuth & Permissions”
YAML
display_information:
name: Centroid Bridge
features:
bot_user:
display_name: Centroid Bridge
always_online: false
oauth_config:
scopes:
bot:
* chat:write
* chat:write.public
settings:
org_deploy_enabled: false
socket_mode_enabled: false
token_rotation_enabled: false

10. Click on “Install to Workspace” then “Allow”
11. Click on “Copy” to copy the Bot User OAuth Token
12. Save the “Bot User OAuth Token” for later configuration
A quick guide on how to create a Slack App (bot)
Creating a Channel and Retrieving Channel ID
1. Go to Slack Application
2. On the lower left pane, click on the plus + icon
3. Select Channel
4. Name the channel
5. You can select the visibility and privacy of the channel
Public - anyone in your workspace can join the channel
Private - Only specific of invited people can join the channel (please refer below for additional steps)
6. Click on the channel name to access its information
7. Scroll down and copy the “Channel ID”
8. Save the “Channel ID” for later Configuration


A quick guide on how to create a public channel
Channels with “Private” visibility settings
1. Bot App is required to join or be added to the channel
2. Click on the channel name
3. Click on “Integrations” then “Add an App”
4. Search for the “Centroid Bridge” app then “Install”
A quick guide on how to create and configure a private channel


Configuring Slack Bridge Alerts
1. Login to bridge
2. On the left lower pane, click on Account
3. Within the account, click on “Update your profile”
4. Go to “Slack Notification”
5. Add the Bot User OAuth Token & Channel ID following the below format
Example only:
xoxb-6676000001859-6600000004022-bd7Gx0000000Y0NYj7w8uV7r;C06L000007B




```

---

<a id='alerts-telegram-how-to-configure-alerts-md'></a>
### 9. `alerts/telegram-how-to-configure-alerts.md`

```markdown
[🏠 Document Start](..\..\README.md) / [Taker Status](..\README.md) / [Alerts](README.md) / Telegram: How to configure alerts

# Telegram: How to configure alerts

Overview
A lot of companies started utilizing telegram as one of their main channels to monitor systems and receive notifications or alerts. Within the
telegram messaging platform, a bot tool can be created to enable automated interactions with users via text commands. The Telegram Bot
API facilitates bot delivering messages which Centroid Solutions integrated into our Centroid Bridge. This integration empowers real-time
alerting for critical events, enhancing responsiveness and communication for bridge broker administrators.
Main Requirements
1. Dedicated Telegram Bot
2. Bot Token ID
3. User ID

Important notes:
1. Only 1 telegram bot is required per company
2. Company users must subscribe to the telegram bot that you created
3. Company users are required to retrieve their personal User ID number
4. Company users are required to configure their profile with the token and their User ID
Creating a Telegram bot and retrieving Token ID
1. Download and install Telegram then register for an account
2. To create a bot, search for @BotFather
3. Click on Start then type /newbot
4. Give your bot a unique company name and create a unique username (e.g., Centroid Bridge FXBroker with username
CBFXBroker_Bot)
5. Upon confirmation that the bot has been created, retrieve the token ID
6. Save the “token ID” for later configuration
Warning: The above bot name is only an example. Please do not copy it to avoid having the same bot name with other Brokers or
Centroid Clients.


A quick guide on how to create a bot
Retrieving your User ID
1. Download and Install Telegram then register for an account
2. Search for @userinfobot
3. Click Start then retrieve your UserID number
4. Save the “User ID” for later configuration


Subscribing to your Company's Telegram Bot
1. Download and Install Telegram then register for an account
2. Search for the name or username of the bot that your company created for the Bridge alerts
3. Click Start to subscribe and receive alerts
Configuring Telegram Bridge Alerts
1. Login to bridge
2. On the left lower pane, click on Account
3. Within the account, click on “Update your profile”
4. Go to “Telegram Notification”
5.Add the Bot Token ID & User ID following the below format
Example only:
7110000034:AAGg4No0000Q2sJKnx9s5_ifRc00000Nfk;920000052




```

---
