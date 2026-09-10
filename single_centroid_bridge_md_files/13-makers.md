# 📁 13-makers

- **Generated:** 2026-09-10 12:07
- **Total Files:** 6
- **Source:** `C:\Users\DELL\Downloads\backend_code-main (1)\backend_code-main (2)\bridge_manual_md\13-makers`

---

## 📑 Table of Contents

1. [README.md](#readme-md)
2. [faq--maker-module.md](#faq-maker-module-md)
3. [maker-api-link.md](#maker-api-link-md)
4. [maker-scaling.md](#maker-scaling-md)
5. [makers/README.md](#makers-readme-md)
6. [makers/guidelines-for-receiving-and-incorporating-the-centroid-maker-into-your-centroid-bridge.md](#makers-guidelines-for-receiving-and-incorporating-the-centroid-maker-into-your-centroid-bridge-md)

---

## 🌲 Project Structure

```
13-makers/
├── faq--maker-module.md
├── maker-api-link.md
├── maker-scaling.md
├── makers/
│   ├── guidelines-for-receiving-and-incorporating-the-centroid-maker-into-your-centroid-bridge.md
│   └── README.md
└── README.md
```

---

## 📄 Files

<a id='readme-md'></a>
### 6. `README.md`

```markdown
[🏠 Document Start](..\README.md) / Makers

# Makers

The Makers Module allows the broker to create and configure Makers, Maker API Link, and Maker Scaling. Upon clicking the “Makers”
button on the left-hand side menu, it expands to show the different components underneath which are explained in greater detail
hereunder.




```

---

<a id='faq-maker-module-md'></a>
### 6. `faq--maker-module.md`

```markdown
[🏠 Document Start](..\README.md) / [Maker Scaling](README.md) / FAQ - Maker Module

# FAQ - Maker Module

FAQ
What is the process for adding a Maker connection into our system?
Does establishing connectivity with a new maker connection necessitate a restart?
Is sharing IPs required for a successful connection with the maker? If yes, which IPs are needed?
In the event that a Maker symbol is not pricing, what is the procedure for resubscribing to the Symbol?
How can I subscribe to additional layers from the Maker?
Makers
To add a new Maker connection to the Centroid Bridge, we recommend reaching out to our support team via email at
support@centroidsol.com
A restart is necessary to establish connectivity with the Centroid Bridge after adding a new maker connection.
It is important to share the IPs provided by the Centroid Team via the Onboarding Email. Alternatively, you can contact us through
Skype/Slack for the IPs. Whitelisting these IPs on the Maker end ensures a smooth connection.
To re-subscribe to a Maker symbol, disable and then enable the symbol on Maker level. This triggers a subscription request from the
Centroid Bridge to the Maker. Refer to the Gateway Manual for specific insight on this matter.
To subscribe to additional Price layers from your specific Maker, configure the Depth setting. Please note that setting the depth to 5
doesn't guarantee receiving 5 layers; the actual number depends on your Maker. This configuration ensures you are sending
subscription for 5 layers from the Centroid Bridge to your Maker.


```

---

<a id='maker-api-link-md'></a>
### 6. `maker-api-link.md`

```markdown
[🏠 Document Start](..\README.md) / [Guidelines for Receiving and Incorporating the Centroid Maker into Your Centroid Bridge](README.md) / Maker API link

# Maker API link

Overview
The Maker API Link component is an added feature for sending lists of values over FIX tags with order requests to the Maker. These lists
can be necessary for Makers or used to distinguish specific orders.
One of its useful cases is when targeting different Accounts in a Maker Session, the Account name is sent in tag 1 to ensure the Order is
booked into the correct Account on the Maker side.
The diagram below illustrates how the Maker API Link functions.
Rules to be applied/created under Maker API Link
Rule 1 → This rule will consist of filtered trades from Centroid_MT4 from any “Taker Execution Model” to be sent to the maker with Tag
1 (account) with value “Account-1” as a low priority of 1 which can be superseded by higher priority.
Rule 2 → This rule will consist of filtered trades from Centroid_MT4 from the Taker Execution Model of “TEM 2” to be sent to the maker
with Tag 1 (account) with value “Account-2” as a high priority of 2 which can supersede low priority such as 1.
To summarize, any trades incoming from TEM-2 will be re-directed to Account-2 as the rule priority is set to 2, which means Rule 2 will
take effect first followed by Rule 1.
As mentioned above, the Maker API Link can be configured down to the level of the Taker Execution Model and can be done for specific
Securities or Symbols as well.

In this component, you will be able to do the following:
1. Create a new Maker API Link.
2. Filter the currently configured Maker API Links by different criteria.
3. Enable/Disable a particular configuration.
4. View and edit a currently configured Maker API Link.


6. Click “Export” and select “Export to Excel” or “Export to CSV”.
Creating a Maker API Link Rule
To create a new Maker API Link:
1. Click the “Add” button to create a new Maker API Link.
2. Fill out the Wizard. You may refer to the field descriptions hereunder.
3. Click “Submit” to submit the changes.
Note: In the Values parameter, you can add multiple values depending on your requirements by clicking the “Add Values” button.
ID 1,2,3,10 A unique configuration ID number for reference purposes. When creating a new configuration,
make sure the ID does not exist already.
Takers Centroid_MT5
,
Centroid_MT4
Select one or multiple Takers to be included in the configuration as source(s). You may select the
Takers from the available list of Takers or enter comma-separated values manually by ticking the
“Pattern” tick box.
Taker Execution
Models
TEM-1, TEM-
2, Test_TEM
Select one or multiple Taker Execution Models to be included in the configuration as source(s).
You may select the Taker Execution Models from the available list of Taker Execution Models or
Field Possible
Values
Description

Note: For patterns, you may use wildcards “*” and negations “!” to include all or exclude certain values.
enter comma-separated values manually by ticking the “Pattern” tick box.
Liquidity Models Liquidity_Mod
el
Select one or multiple Liquidity Models to be included in the configuration as source(s). You may
select the Liquidity Model from the available list of Liquidity Models or enter comma-separated
values manually by ticking the “Pattern” tick box.
Securities FX, CFD Select one or multiple Securities from the available Securities in the Centroid Bridge to be
included in the configuration.
You may select the Securities from the available list of Securities or enter comma-separated
values manually by ticking the “Pattern” tick box.
Symbols EURUSD,
XAUUSD
Select one or multiple Securities from the available Symbols in the Centroid Bridge to be included
in the configuration.
You may select the Symbols from the available list of Symbols or enter comma separated values
manually by ticking the “Pattern” tick box.
Makers Liquidity
Provider
Select one or multiple Makers to be included as a Target to which the Orders are routed.
You may select the Makers from the available list of Makers or enter comma-separated values
manually by ticking the “Pattern” tick box.
Sides Buy, Sell, All Select the side of the Order if you need to pass on values for a particular side, such as Buy or
Sell. Otherwise, just select “*” to include all Order sides.
Ord Types Market, Limit Select the type of the Order if you need to pass on values for a particular execution type, such as
Market, Limit or Stop. Otherwise, just select “*” to include all Order types.
Priority 1-10 The priority is essential in the event of overlapping configurations and defines which configuration
should supersede. The configuration with the highest Priority always supersedes.
You may refer to the above diagram example to understand how the Priority works.
Enable Enabled,
Disabled
Indicates whether the configuration is enabled or disabled.
If ticked, the Maker API Link is enabled upon creation.
If unticked, the Maker API Link is disabled upon creation, hence no Tags or Values would be
passed on.
Description A short description for reference purposes.
Values Tag: 1, Value:
LP Account
Number
The Tags and Values to be passed on in the execution message. It is divided into two
parameters:
Tag: Enter the tag number you wish to send across. For example, if you select and put in the
value 1 under Tag, this means you are targeting a particular account.
Value: You can select any Value to be passed on for the selected Tag. It can be either entered
manually by typing in the value or passed on as a predefined value using the # key as
explained hereafter.
You may add as many Values (Tag and Value) as you want by clicking the “Add Value” button.
A common example is Tag 1 in case you are targeting different Accounts within a Maker Session.
Account is equivalent to Taker Execution Model in the Maker Class is Centroid. For instance, to
target an Account called “Acc001”, you simply add the Values: 1 in the Tag textbox and Acc001 in
the Value textbox.
Note: You can pass on some values using macros by putting the parameter name in between two
# keys. You may refer to the list of predefined values below.

Note: Below are some of the macros that can be passed across to the Maker while executing the Order using the hash “#” keys.
Available macros for sending prices based on the order type.
Configuring Maker API Link
To configure a Maker API Link configuration:
1. Double-click the desired column(s) in the Maker API Link Configuration.
2. For some columns, you are presented with a pop-up Window where you can edit and click submit as seen below. This process needs
to be done separately for each column or parameter.
3. Click the “Submit” button to apply the changes.
4. Click on “Save” to finally save the changes.
5. Click the “Revert All” button to undo the changes that have been made
#taker# The name of the Taker through which the Order was initiated.
#tem# The name of the Taker Execution Model through which the Order was routed.
#login# The MT4/MT5 Login number that placed the Order, in case it was initiated via an MT4/MT5 Taker.
#order# This is relevant to Orders originating from a Taker of type MT4 or MT5.
MT4: Order will send the Ticket Number of the MT4 trade.
MT5: Order will send the Order Number of the MT5 trade.
#pos# This is relevant to Orders originating from a Taker of type MT5. It sends the Position Number of the MT5 trade.
#group
#
The name of the MT4/MT5 Group of the Account that placed the Order, in case it was initiated via an MT4/MT5 Taker.
#deal# This is relevant to Orders originating from a Taker of type MT5. It sends the Deal Number of the MT5 trade.
Value Description
#ordpx# To include order price “limit/stop price”
#ordtobpxb# To include Agg Book raw ToB bid price to any defined FIX tag, while setting up the rule you might want to filter is as
Sell rule.
#ordtobpxa# To include Agg Book raw ToB ask price to any defined FIX tag, while setting up the rule you might want to filter is as
Buy rule.
#ordextpxb# To include Ext ToB bid price to any defined FIX tag, while setting up the rule you might want to filter is as Sell rule.
#ordextpxa# To include Ext ToB ask price to any defined FIX tag, while setting up the rule you might want to filter is as Buy rule.
#reqpx# To include request price “ToB or level book price” to any defined FIX tag
Macro Value Definition


To delete a Maker API Link configuration:
1. Click the “Delete” icon next to the desired Maker API Link configuration.
2. To confirm the Deletion, type in the specified text.
3. Click the “Delete” button in the pop-up window to confirm the deletion.
Exporting a Maker API Link
To export a Maker API Link configuration:
1. Filter the desired ID from the list to be able to export a specific Maker API Link rule.
2. Click “Export” and select “Export to Excel” or “Export to CSV”.



```

---

<a id='maker-scaling-md'></a>
### 6. `maker-scaling.md`

```markdown
[🏠 Document Start](..\README.md) / [Maker API link](README.md) / Maker Scaling

# Maker Scaling

Overview
The Maker scaling acts as a multiplier for the Prices and Volumes provided by the Maker. This can be applied to both incoming (IN) and
outgoing (OUT) Prices, as well as Volumes.
It's crucial to emphasize that this scaling operates on a symbol basis at the Maker Level.
Within this module, you have the capability to:
Create a New Maker Scaling Rule: Initiate the setup for a new Maker Scaling Rule.
Filter Rules: Categorize Maker Scaling Rules based on various criteria for easier identification.
Enable/Disable Rule: Manage the active status of a Maker Scaling Rule.
Edit Rule: Modify an existing Maker Scaling Rule by adjusting configurable parameters.
Delete Rule: Remove an existing Maker Scaling Rule.
Export Rules: Save the list of Maker Scaling Rules to an Excel/CSV file.
Creating a Maker Scaling Rule
To create a Maker Scaling Rule:
1. Click on Maker Scaling and then click the “Add” button.
2. Fill out the Wizard. You may refer to the field descriptions below.
3. Click “Submit” to submit the changes.
Symbol No EURUSD Select the Symbol to be scaled up or down
Field Editabl
e
Possible
Values
Description

To configure or modify an existing Maker Scaling Rule
1. Select the desired Maker Scaling Rule.
2. Configure the desired fields.
3. Click the “Save” button on the top left to deploy the changes.
Deleting a Maker Scaling Rule
To delete a Maker Scaling rule
1. Click the “Delete” icon next to the desired Rule.
2. To confirm the Deletion, type in the confirmation text.
3. Click the “Delete” button in the pop-up window.
Note: Only one symbol can be selected per rule.
Maker No LP1 Select the Maker from the drop-down.
Note: Only one Maker can be selected per rule.
Price In Yes 0.1, 1, 10,
100
The Multiplier value to be applied on the incoming prices.
Example: An incoming price of 101.555 with scaling of 0.1, then the received price on bridge
will be 10.1555.
Price Out Yes 0.1, 1, 10,
100
The Multiplier value to be applied on the outgoing prices. This will only work for LIMIT orders
as for MARKET orders the price request is not being sent.
Example: A limit price of 101.555 with a price scale of 0.1 will be sent to the Maker as
10.1555.
Volume In Yes 1, 10,
100000
The Multiplier value to be applied on the incoming volumes.
Example: A volume of 10 with a scaled volume of 100000 will be processed by the bridge as
1000000.
Volume
Out
Yes 0.00001, 1,
10, 100
The Multiplier value to be applied on the outgoing volumes.
Example: A traded volume of 1000000 with a scaled volume of 0.00001 will be sent to the
Maker as 10.
Description Yes A short description for reference purposes.
Enable Yes Enabled,
Disabled
Indicates whether the Maker Scaling Rule is enabled or disabled.
If ticked, the Maker Scaling Rule is enabled.
If unticked, the Maker Scaling Rule is disabled.


To export a Maker Scaling rule
1. Filter the desired Maker Scaling from the list; otherwise, leave it unfiltered to select all
2. Click “Export” and select “Export to Excel” or “Export to CSV”
Uploading a Maker Scaling Rule
To upload multiple maker scaling rules via the exported file “Excel” or “CSV”
1. Click on the “Upload”.
2. Click on “Drop File”.
3. To upload the Liquidity Model values, click on “Upload”.


4. You also have the option to discard the bulk upload by clicking on the “Close” Button.




```

---

<a id='makers-readme-md'></a>
### 6. `makers/README.md`

```markdown
[🏠 Document Start](..\..\README.md) / [Makers](..\README.md) / Makers

# Makers

Overview
A Maker represents the Liquidity Provider in the Bridge. It consists of a 2-way connection between the Centroid Bridge and the Maker
whereby the Bridge receives price updates from the Maker and sends Order requests for execution to the Maker based on a variety of
routing rules.
In this Component, you can view the list of Makers that are defined in the Centroid Bridge and its symbol settings. The makers can be
configured down to the level of individual Symbols as explained below.
In this component, you will be able to do the following:
Create a New Maker Session: Add a new Maker Session to the Centroid Bridge.
Filter Maker Sessions: Filter by different search criteria.
Edit Maker Configurations: View and edit Maker configuration settings for both trading and pricing sessions.
Export List: Export the list of Makers to an Excel File or CSV file.
Configure Bulk Symbol Settings: Configure a bulk of Symbol settings by clicking the Edit icon, for all Symbols at once or a group of
filtered Symbols.
Export Symbol Settings: Export the list of Symbol Settings of a particular Maker to an Excel file or CSV file.
Upload Modified Settings: Upload an Excel or CSV file to update or change a bulk of configurations on existing Makers.
Viewing / Editing Maker Connection Settings
To view the Maker Connection Settings, click on the button right next to the desired Maker and a pop-up window that contains the Maker
Settings will appear as shown below:
The settings are divided into the following three tabs:
Feeding: The Maker Connection Settings of the pricing session.
Trading: The Maker Connection Settings of the trading session.


Both: The Maker Connection Settings of the Maker in case the connection to the Maker is made via one session that combines both
feeding and trading.
Note: If the connection to the Maker is made through separate sessions, Feeding and Trading, both tabs will have values, whereas if the
connection is made through one session, both Feeding and Trading tabs will show empty values.
Note: For some Makers, you may find the Account number of the Trading Account with the Maker within the configuration settings.
In some cases, editing the session is required from the Broker’s end if the LP, for instance, changed some settings such as the account
(tag 1) credentials of the Trading Session.
To edit the Maker Connection Settings
1. Click on the desired tab, Trading in the below example.
2. Edit the desired values to the right, Username, and Password in the below example.
3. Click the Save button.


Configuring the Maker and its Symbols
To configure or modify a Maker on a per Symbol basis:
1. Click the check box at the start of the row next to the desired Maker.
2. Configure the desired field for the desired Symbol, which is highlighted.
3. Click the “Save” button on the top left to deploy the changes.
Symbol No EURUSD,
XAUUSD
The Symbol to be configured
Maker Symbol Yes EUR/USD,
XAUUSD.c
The name of the instrument you are subscribing to on the Maker’s end. This
allows to map Symbols in your Centroid Bridge to Maker’s Symbols. Here we can
configure the Maker Symbol, which will be provided by the Maker itself
Example:
Symbol: EURUSD
Maker Symbol: EUR/USD
Security No FX, CFD,
EQUITIES
The Security into which the Symbol is grouped.
Base Yes EUR, USD,
GER30
The base currency of the Symbol. For FX, it is by default the first currency of the
pair whereas for CFDs, it is the full name of the Symbol.
Example:
EURUSD, Base is EUR
UK100, Base is UK100
Quote Yes EUR, USD, GBP The quote currency of the Symbol. For FX, it is by default the second currency of
the pair whereas for CFDs, it is the currency by which the Symbol is
denominated.
Example:
GBPUSD, Quote is USD
Digits Yes 5 Defines the decimal points in the price of the underlying Symbol to be received
from the Maker.
Session Yes MON,00:00-23:59 Defines the time of the day during which the Maker Symbol will be available for
trading.
Field Editable Possible Values Description

All days of the week should be included and separated by semicolon “;” along
with the time interval during the day. 00:00-00:00 represents a closure during a
particular day.
Markup Bid Yes 0.00005, 0.1, 1 Pre-Aggregation Markup, i.e. This will have the Markup on the Raw Price from
the Maker, and if you have any Additional Markup Model then, Raw Price +
Markup [Maker] + Markup Model = Client’s Final Price / Spread.
Example: Same as Markup Model, In Points, 1 point markup for the symbol
having digit as 5 would be 0.00001.
Note: A negative value would represent a markdown whereby the broker would
be giving a price better than the raw price for the client.
Markup Ask Yes 0.003, 0.5 Pre-Aggregation Markup, i.e. This will have the Markup on the Raw Price from
the Maker, and if you have any Additional Markup Model then, Raw Price +
Markup [Maker] + Markup Model = Client’s Final Price / Spread.
Example: Same as Markup Model, In Points, 5 point markup for the symbol
having digit as 5 would be 0.00005.
Note: A negative value would represent a markdown whereby the broker would
be giving a price better than the raw price for the client.
Depth Yes 0,1,3,5,10 Depth, the number of layers you are subscribing to from a specific Maker.
Example: Depth configured as 5, then the bridge is expecting to receive and
process up to a maximum of 5 layers from the Maker, now it depends on the
maker if it will send 5 layers.
Min Size Yes 1000
[In Volume]
The Minimum size of order allowed, executed, and to be sent to the Maker, any
order below this value will be rejected by the Bridge.
Example: EURUSD Min Size configured as 10000, client is placing an order for
1000, this order will be rejected as “below min volume”
A Step Yes 5000 The increment in the size from the minimum.
Orders sent to the Maker should be a multiple of A Step.
Example: If A Step is 2,000 and an order of 9,000 is received, then the
Aggregator will execute 8,000 and the remaining 1,000 will expire.
Note: It is advisable to keep the A Step similar to Min Size.
Consume A Vol Yes Enabled, Disabled Order requests will lead to a reduction in the total/available liquidity from the
maker.
Enabled: The available liquidity book will be 800k from that Maker for
EURUSD.
Disabled: It won’t have any effect of the order request it will still stream with
1M as available liquidity from the Maker for EURUSD.
Example: If Maker is advertising 1M on a certain symbol, if consume is enabled,
an Order request of 100K will reduce the available liquidity advertised by the
Maker to 900k.
Allow Sweep Yes Enabled, Disabled Indicates whether the price updates received from the Maker are sweepable or
not.
Enabled: The Aggregator targets more than one quote by sweeping the book
until the order is filled (fully or partially).

Disabled: The Aggregator targets one quote of the book per Maker only, that
can best fill the order.
Multi Req Trade Yes 0, 1 This defines how orders pertaining to different levels of the liquidity book are sent
to the Maker.
If set to 1, the Aggregator breaks the order into multiple legs based on the
number of levels swept in the book and sends multiple order requests to the
Maker(s).
If set to 0, the Aggregator sends one Order in full to the Maker at TOB Price
Example: If you have the following liquidity book.
Level 1: 100K – Maker 1
Level 2: 100K – Maker 2
Level 3: 200k – Maker 1
Level 4: 500K – Maker 2
If an Order of 500K comes in:
If Multi Req Trade is 1, 2 order requests will be sent to each LP as follows:
100K and 200K to Maker 1
100K and 100K to Maker 2
If Multi Req Trade is 0, 1 order request will be sent to each LP as follows:
300K to Maker 1
200K to Maker 2
Expiry Date Yes 20220131 This is only relevant to Symbols of type Futures which could be mandated by
some Makers and defines the Expiry Date of the Symbol.
Note: Each Maker may have a different format of Expiry Date to be sent
alongside the Order request.
Sub Volumes Yes 100, 500, 1000 This is only relevant to certain Makers which allow to subscribe to different
volumes of the liquidity book.
Timeout Warn Yes 30,000 ms Default Value is 30000 millisecond, at which, if no reply is received from the
maker for a specific order request then the Centroid Bridge will start generating
Warning Messages.
Timeout Error Yes 180,000 ms Default Value is 180000 millisecond, at which, if no reply is received from the
maker for a specific order request the Centroid Bridge will consider the Order
Expired and Rejects It.
Disclaimer: It is ideal that Timeout Error value is higher than the Timeout Warn
value.
Timeout Kill Yes 10, 20, 30 Default value is 10, meaning after 10 Timeout Errors the Centroid Bridge will
Disable that specific symbol.
Prices Timeout Yes 35000 ms Default value is 35000, meaning if there is no price updates within this time frame
from the maker, trades on Bbook will be rejected.
Feed Side Yes BID,ASK,BID_AS
K
You can define which side of prices you would like to receive from the specific
Maker.
ASK: Only Ask price will be processed after receiving it from the Maker.
ASK_TRADE: Both Ask and Trade prices will be processed after receiving
from the Maker.
BID: Only the Bid price will be processed after receiving it from the Maker.

Re-subscribing Maker Session / Symbol
To re-subscribe or refresh a session at the maker level, you will need to do the following:
1. Click on the configuration option located at the right end of the respective maker session.
2. Access the relevant session, such as Feeding or Trading.
3. Modify the value of the "Enabled" key to 'N' and save the changes.
4. Subsequently, update the value back to 'Y' and save the changes.
This action initiates the resubscription process at the maker session-level.
To re-subscribe or refresh a maker symbol(s), you will need to do the following:
1. Select the relevant maker session.
2. Find the symbol you want to re-subscribe to and deactivate it.
3. Apply the modifications on the Maker Symbol (not just the symbol) and save.
BID_ASK: Both Bid and Ask prices will be processed after receiving them
from the Maker.
BID_ASK_TRADE: Bid, Ask, and Trade prices will be processed after
receiving them from the Maker.
BID_TRADE: Both Bid and Trade prices will be processed after receiving from
the Maker.
TRADE: Only the Trade price will be processed after receiving it from the
Maker.
Accepted Price
Delay
Yes 400 ms Delay in milliseconds after which the price coming from the Maker into the Bridge
will be rejected. In other words, if the travel time it takes for the price to be
streamed from the Maker into the Bridge is greater than the defined Accepted
Price Delay, the price will be discarded hence won’t be allowed into the Bridge.
Ignore Prices for
B exec
Yes Enabled, Disabled This works with the Prices Timeout Component.
Enabled: If there are no price updates from the maker for the defined value [ms]
in Prices Timeout, no execution will take place for the B Book orders.
Disabled: Here the Centroid Bridge will ignore the Prices Timeout settings and
will process/execute the B Book orders based on the last received price.
Description No Euro Vs. US
Dollar
Default values from the Symbol.
MS Description Yes SPOT Symbols An additional description field which could be used for the Maker itself. The most
common approach is to copy tick prices from one Maker to another which does
not have a working Pricing Session. To do so, it suffices to list the name of the
Maker which you wish to price on a per Symbol basis. The Maker Name should
be exactly as appears in Maker Session in the format #mask=Maker_Name#.
Enable Yes Enabled, Disabled Indicates whether the Symbol is enabled or disabled on the Maker Session .
If ticked, the Symbol is enabled.
If unticked, the Symbol is disabled.
Disclaimer: Disabling a Symbol at this level means that the Symbol will be
disabled for a particular Maker, hence the symbol is not subscribed and no
quoting or trading on that Symbol will be allowed.

4. Reactivate the symbol after the changes have been made.
This action initiates the resubscription process at the maker symbol level.
To apply the same action to multiple symbols, you can utilize the Bulk Edit function.
Exporting Maker Symbol Settings
To Export Maker Symbol Settings
1. You will need to click on the “Makers” module.
2. Click on the required “Maker”.
3. Click “Export” and select “Export to Excel” or “Export to CSV”.
Importing Maker Symbol Settings
To Import Maker Symbol Settings:
1. Click on “Upload”
2. Click on “Drop File”


3. To successfully upload the Maker Symbols values, click on “Upload”
4. You also have the option to discard the bulk upload by clicking on the “Close” Button.




```

---

<a id='makers-guidelines-for-receiving-and-incorporating-the-centroid-maker-into-your-centroid-bridge-md'></a>
### 6. `makers/guidelines-for-receiving-and-incorporating-the-centroid-maker-into-your-centroid-bridge.md`

```markdown
[🏠 Document Start](..\..\README.md) / [Makers](..\README.md) / [Makers](README.md) / Guidelines for Receiving and Incorporating the Centroid Maker into Your Centroid Bridge

# Guidelines for Receiving and Incorporating the Centroid Maker into Your Centroid Bridge

Overview
This guide walks you through the steps to add the Centroid Maker on your bridge. Before starting, ensure you have received the email with
the subject: "Maker Credentials from [Your Company Name]." Once confirmed, follow the step-by-step instructions to complete the setup.
The Maker credentials email you receive should look similar to the sample provided below. Please review it to ensure you have all the
necessary details.
Steps to Complete Maker Addition in the Bridge
Click on the Add Maker button in the Maker Credentials email.
You will be redirected to the Centroid Bridge, where the following interface will appear.


In the interface, enter the Maker's name as desired.
If there are more than two TEMs (Tag1) associated with the Maker, select the default account from the dropdown menu.
Once all fields are completed, click the Proceed button to finalize the Maker addition.
Note: A bridge restart is required to activate the Maker
Note: Whitelisting is not required for Centroid-to-Centroid connections


```

---
