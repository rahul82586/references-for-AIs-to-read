# 📁 19-takers

- **Generated:** 2026-09-10 12:07
- **Total Files:** 8
- **Source:** `C:\Users\DELL\Downloads\backend_code-main (1)\backend_code-main (2)\bridge_manual_md\19-takers`

---

## 📑 Table of Contents

1. [README.md](#readme-md)
2. [faq--taker-module.md](#faq-taker-module-md)
3. [taker-api-link.md](#taker-api-link-md)
4. [taker-execution-model.md](#taker-execution-model-md)
5. [taker-execution-rules.md](#taker-execution-rules-md)
6. [taker-feeds.md](#taker-feeds-md)
7. [takers/README.md](#takers-readme-md)
8. [takers/guidelines-for-configuring-and-sending-credentials-for-fix-centroid-taker.md](#takers-guidelines-for-configuring-and-sending-credentials-for-fix-centroid-taker-md)

---

## 🌲 Project Structure

```
19-takers/
├── faq--taker-module.md
├── README.md
├── taker-api-link.md
├── taker-execution-model.md
├── taker-execution-rules.md
├── taker-feeds.md
└── takers/
    ├── guidelines-for-configuring-and-sending-credentials-for-fix-centroid-taker.md
    └── README.md
```

---

## 📄 Files

<a id='readme-md'></a>
### 8. `README.md`

```markdown
[🏠 Document Start](..\README.md) / Takers

# Takers

The Takers Module allows the broker to create and configure Takers, Taker Feeds, Taker Execution Model, and Taker API Link. Upon
clicking the “Takers” button on the left-hand side menu, it expands to show the different components underneath which are explained in
greater detail hereunder.




```

---

<a id='faq-taker-module-md'></a>
### 8. `faq--taker-module.md`

```markdown
[🏠 Document Start](..\README.md) / [Taker Execution Rules](README.md) / FAQ - Taker Module

# FAQ - Taker Module

FAQ
Is it possible to add a new Taker Connection from our end?
Do we need to provide the Taker IPs to the Centroid Team?
What is the process for providing connection details to the FIX Taker?
What does specifying an IP during the creation of the taker entail? Does mentioning the IP mean it is automatically whitelisted for the taker?
Can multiple takers be assigned within a single Taker Feed?
Encountering challenges when saving a new taker feed? What could be the reasons for the error?
How can we ensure that the TEM (whether existing or newly added) is fully configured for B Book, and vice versa?
What does 'Min Volume' signify, and how can it be reconfigured?
Taker
Kindly note that users can add FIX as the taker connection type on their end. For MT5 and MT4 connections, we recommend
contacting our support team via email: support@centroidsol.com or Skype/Slack .
We kindly request the IPs of the newly added takers, Whitelisting these IPs ensures a smooth connection between Taker and the
Centroid Bridge.
To share connection details with your FIX Taker, you can access the "Export FIX Config" option on the extreme right to download the
FIX Details. Kindly note that this feature is exclusively for FIX Takers only.
Mentioning the IP during taker creation is for reference only and doesn't automatically whitelist it. To whitelist IPs, please share them
with Centroid via dedicated group chat or send an email to support@centroidsol.com
Taker Feed
Indeed, it is possible to assign multiple takers within a single Taker Feed.
Consider the following possibilities for the error:
If you're encountering issues with an existing suffix, ensure you're not attempting to save the same set of suffix taker feed with the
same taker.
If you're uploading a file, we recommend double-checking the Excel format for any potential discrepancies.
Taker Execution Model
To confirm whether the TEM is set up as B Book or A Book, just check the B Book percentage configured on the TEM level:
0 indicates the TEM is configured as complete A Book.
100 indicates the TEM is configured as complete B Book.
Min volume represents the minimum volume accepted at the bridge level; anything below this threshold will be declined.
To reconfigure, simply adjust the volume, considering the contract size and your desired minimum volume:
Volume = Contract Size × Lot Size.

Why was a particular order booked as B Book, even when the TEM is configured as A Book?

If an order is booked as B Book despite the TEM being configured as A Book, you might review your TEM settings. Specifically, check
AMin and AStep configurations. If these criteria's aren't met, the order may be booked as B Book, disregarding the TEM B Book%
configuration.


```

---

<a id='taker-api-link-md'></a>
### 8. `taker-api-link.md`

```markdown
[🏠 Document Start](..\README.md) / [Taker Execution Model](README.md) / Taker API link

# Taker API link

Overview
The Taker API link is a versatile functionality capable of serving multiple purposes. For every order that the bridge receives to broker can
control the flow and modify the order. It can redirect trades to another Taker Execution Model based on predetermined conditions, add
custom tags for the Maker API Link, identify scalpers and trade patterns, and redirect them accordingly. The Bridge performs Taker API
Link verification among its initial checks before trade execution.
In this component, you will be able to do the following:
1. Create a new Taker API Link
2. Filter the current configured Taker API Links by different criteria
3. Enable/Disable a particular rule
4. View and edit a current configured Taker API Link
5. Delete a Taker API Link rule
6. Click “Export” and select “Export to Excel” or “Export to CSV”
Creating a Taker API Link rule
To create a Taker API Link rule
1. Click “Add” button to create a new Taker API Link rule
2. Fill out the Wizard. You may refer to the field descriptions below
3. Click “Submit” to submit the changes


ID 1,2,3,10 A unique ID number for the configured rule
Takers Centroid_M
T5,
Centroid_M
T4
Select one or multiple Takers to be included in the configuration as source(s) You may select
the Takers from the available list of Takers or enter comma separated values manually by
ticking the “Pattern” tick box
Taker Execution
Models
TEM-1,
TEM-2,
Test_TEM
Select one or multiple Taker Execution Models to be included in the configuration as source(s)
You may select the Taker Execution Models from the available list of Taker Execution Models or
enter comma separated values manually by ticking the “Pattern” tick box
Securities FX, CFD Select one or multiple Securities from the available Securities in the Centroid Bridge to be
included in the configuration.
You may select the Securities from the available list of Securities or enter comma separated
values manually by ticking the “Pattern” tick box
Symbols EURUSD,
XAUUSD
Select one or multiple Securities from the available Symbols in the Centroid Bridge to be
included in the configuration.
You may select the Symbols from the available list of Symbols or enter comma separated
values manually by ticking the “Pattern” tick box
Makers Liquidity
Provider
Select one or multiple Makers to be included as a Target to which the Orders are routed.
You may select the Makers from the available list of Makers or enter comma separated values
manually by ticking the “Pattern” tick box
Sides Buy, Sell, All Select the side of the Order if you need to pass on values for a particular side, such as Buy or
Sell. Otherwise, just select “*” to include all Order sides
Ord Types Market,
Limit
Select the type of the Order if you need to pass on values for a particular execution type, such
as Market, Limit or Stop. Otherwise, just select “*” to include all Order types
Source ExtLogin MT4/MT5 Login number for Takers of type MT4/MT5
Default Value = 0 (all logins)
Field Possible
Values
Description

Note: Below are the available macros that can be used for Rule Macros.
Source ExtGroup Name of MT4/MT5 Group for Takers of type MT4/MT5
Rule Macro #tem# Select the predefined Macros from the dropdown by inputting #. In the subsequent table, we will
outline the definitions for the available macros.
Rule Value tem_b The value to be assigned to the Rule Macro.
For example: If the Rule Macro is #tem# then the Rule Value = tem_b.
Priority 1-10 The priority is essential in the event of having overlapping configurations and defines which
configuration should supersede. The configuration with the highest Priority always supersedes.
Min Size 0 Min size sets the lower limit in Volume for the Scalping threshold. Trades falling below Min Size
won't qualify for the scalping threshold.
Note: Minimum Size, Maximum Size, and Scalping Threshold are interrelated and function
together.
Default Value = 0
Max Size 1000 Max size sets the upper limit in Volume for the Scalping threshold. Trades falling above Max
Size won't qualify for the scalping threshold.
Note: Minimum Size, Maximum Size, and Scalping Threshold are interrelated and function
together.
Default Value = -1 (disabled)
Scalping Threshold
(ms)
300 Threshold in milliseconds to qualify for the Scalping threshold. It will be the time interval
between opening & closing a trade.
Note: Minimum Size, Maximum Size, and Scalping Threshold are interrelated and function
together.
Default Value = -1 (disabled)
Order Repetition
Interval (sec)
20 This component is used to detect the interval between two or more order with same volume,
same symbol, same side and same login.
Order Repetition
Counter
3 In this component you can input the number of time you will allow the repetition of same
volume, same symbol, same side and same login.
Description A short description for reference purposes
Enable Enabled,
Disabled
Indicates whether the configuration is enabled or disabled
If ticked, the Taker API Link is enabled upon creation
If unticked, the Taker API Link is disabled upon creation, hence no Tags or Values would be
passed on
#taker# The name of the Taker through which the Order was initiated
#tem# The name of the Taker Execution Model through which the Order was routed
#login# The MT4/MT5 Login number that placed the Order, in case it was initiated via an MT4/MT5 Taker
#order
#
This is relevant to Orders originated from a Taker of type MT4 or MT5.
MT4: Order will send the Ticket Number of the MT4 trade
MT5: Order will send the Order Number of the MT5 trade
Value Description

To configure a Maker API Link configuration
1. Double-click the desired column(s) in the Taker API Link Configuration.
2. For some columns, you are presented with a pop-up Window where you can edit and click submit as seen below. This process needs
to be done separately for each column or parameter
3. Click on “Save” to save the changes.
Delete a Taker API Link Rule
To delete a Maker API Link configuration
1. Click the “Delete” icon next to the desired Taker API Link configuration
2. To confirm deletion, type the ID of the Taker API Link in the field.
3. Click on the "Delete" button to confirm deletion.
Exporting a Taker API Link Rule
To export a Maker API Link configuration
1. Select the desired Taker API Link from the list
#pos# This is relevant to Orders originated from a Taker of type MT5. It sends the Position Number of the MT5 trade
#group
#
The name of the MT4/MT5 Group of the Account that placed the Order, in case it was initiated via an MT4/MT5 Taker
#deal# This is relevant to Orders originated from a Taker of type MT5. It sends the Deal Number of the MT5 trade
#____# This can be utilized to create any custom rule macro


2. Click “Export” and select “Export to Excel” or “Export to CSV”
Case Studies:
Case 1. Route Trades based on Filters.
In the below case study, we'll demonstrate how to route LIMIT orders to a different Taker Execution Model (TEM).
Set the filters as per the requirement and you must configure the Ord Types, Rule Macro and Rule Value.
Taker Execution Model → tem_a
Ord Types → LIMIT
Rule Macro → #tem#
Rule Value → tem_confirm
Explanation: If there are any LIMIT trades to be executed using tem_a, they will be rerouted to a different TEM - tem_confirm
Case 2. Modify Maker API link tags using Taker API link
In this case study, we will understand the process of modifying tag1 values before sending them to the Maker for a specific MT4/5 group.
For example, If you have a second account with your liquidity provider and desire to forward trades from a specific MT4/5 group to that
account, you can achieve this by utilizing both the Taker and Maker API links together.
Taker API Link:
Set the filters as per the requirement and you may configure the Source Ext Group, Rule Macro and Rule Value.
Source ExtGroup → real\VIP
Source ExtLogin
To redirect trades to another TEM, ensure that the Rule Macro is set to #tem#, and the Rule Value contains the name of the
specific Taker Execution Model (TEM) where the trades should be rerouted.

Rule Macro → #LPAccount#
Rule Value → 371294
Maker API Link:
Review the Maker API Link page on creating new rules.
Explanation: All trades executed from login “10001” will contain #LPAccount#=371294 where this value will be sent to the maker
“LIQUIDITY_PROVIDER” via FIX tag 526 as stated in the Maker API Links rule.
Case 3. Route trades using Scalping Threshold.
Set the filters as per the requirement and you may configure the Min Size, Max Size, Scalping Threshold, Rule Macro and Rule Value.
Symbols → XAUUSD
Min Size → 1000
Max Size → 10,000
Scalping Threshold → 2000ms
Rule Macro → #tem#
Rule Value → tem_scalpers
Explanation: If there are any XAUUSD trades executed within the specified Volume Range of 1000 to 10,000, both opened and closed
within 2000ms by the same login, they will be rerouted to a different TEM - tem_scalpers.
The Rule Macro can be any unused keyword within the bridge, enclosed by "#" at the beginning and end. The Rule Value will be
the tag value to be passed on to the Maker API link.


To redirect trades to another TEM, ensure that the Rule Macro is set to #tem#, and the Rule Value contains the name of the
specific Taker Execution Model (TEM) where the trades should be rerouted.


```

---

<a id='taker-execution-model-md'></a>
### 8. `taker-execution-model.md`

```markdown
[🏠 Document Start](..\README.md) / [Taker Feeds](README.md) / Taker Execution Model

# Taker Execution Model

Overview
A Taker Execution Model can be thought of as a Trading or Execution Account in the Centroid Bridge defined for one or multiple Takers
with execution settings configured on a per Symbol basis. Takers can target different Taker Execution Models defined in the Centroid
Bridge for the purpose of routing Orders based on different execution settings pertaining to different types of clients. The Taker Execution
Model can be configured down to the level of individual Symbols.
Within this module, you have the capability to:
Create a New Taker Execution Model: Initiate the setup for a new Taker Execution Model.
Enable/Disable Global Settings: Enable or disable a Taker Execution Model at a global level, applying changes across all available
models and Symbols.
Filter Taker Execution Models: Categorize Taker Execution Models based on various criteria for easier identification.
Configure Specific Model: Enable/Disable a particular Taker Execution Model and configure its parameters, affecting all associated
Symbols.
Delete Taker Execution Model: Remove an existing Taker Execution Model from the system.
Export Taker Execution Models: Save the list of Taker Execution Models to Excel or CSV for external reference.
Filter and Look up Symbol Settings: Streamline Symbol configuration by searching and filtering within a Taker Execution Model.
Configure Bulk Symbol Settings: Use the Edit icon to adjust settings for multiple Symbols at once, either for all or a filtered group.
Configure Model Symbol Settings: Fine-tune settings for a specific Symbol within a Taker Execution Model.
Export Symbol Settings: Save the configured settings of a particular Taker Execution Model's Symbol to Excel or CSV.
Upload Modified Settings: After making changes offline, re-upload the modified file to implement the necessary adjustments.
Creating a Taker Execution Model
To create a Taker Execution Model
1. Click the “Add” button to create a new Taker Execution Model


2. Fill out the Wizard. You may refer to the field descriptions hereafter
3. Click “Submit” to submit the changes
Taker Execution
Model
TEM-1, Test_TEM, A-
Book_TEM
A unique name of the Taker Execution Model
Taker Centroid_MT4,
Centroid_MT5
The Taker(s) to which the Taker Execution Model is assigned. You may select one or
multiple Takers.
Assigning the Taker means this Taker will be targeting this TEM.
Currency USD The Currency of the Taker Execution Model into which all calculations will be
converted.
USD is the default and only available option
Trade Limit 500, 700 The maximum number of Order requests the Centroid Bridge will process, within a
specified period of time, defined in Trade Span hereafter
Markup Model Markup_Model,
10PTS_MM
The Markup Model defines the markups to be added on top of the raw prices at the
Time of Execution.
Liquidity Model Liquidity_Model The Liquidity Model that will be assigned to the Taker Execution model indicates the
Maker(s) the Orders will be sent to.
Depending on the BBook% settings if the TEM is A Book or B Book. If A Book, please
check the below conditions
If the Liquidity Model comprises One Maker only, Orders will be routed to that one
Maker.
If the Liquidity Model comprises more than one Maker, Orders will be routed to
different Makers and executed with the Maker depending on the factor that which
Maker is advertising the best price during the time of execution.
Trade Span 1000ms, 1200ms,
1500ms
A time interval, in milliseconds, associated with Trade Limit which specifies the period
of time during which the Trade Limit will be applicable
Trade Reject
Delay
200ms, 400ms A time delay in milliseconds, by which the rejection replies occurring from Trade Limit
will be delayed, in the event of breaching the maximum number of allowed trade
Field Possible Values Description

modify and customize the settings of particular Symbols individually as explained hereafter.
Configuring Taker Execution Model
To Configure or modify a Taker Execution Model
1. Click on the checkbox next to the Taker Execution Model name to select it
2. Configure the settings on a symbol level
3. Click the “Save" button to apply the modifications.
4. Click the “Revert All” button to undo the changes that have been made
requests, specified in the Trade Limit
Enable Enabled, Disabled Indicates whether the Taker Execution Model is enabled or disabled
If ticked, the Taker Execution Model will be enabled for trading upon creation
If unticked, the Taker Execution Model will be fully switched off upon creation,
hence no Orders will be executed through this Taker Execution Model
Description A short description for reference purposes
Copy From It allows to copy all the settings from an existing Taker Execution Model
Symbol No EURUSD,
XAUUSD
The name of the Symbol to be configured, as defined in Symbols
Security No FX, Crypto The Security into which the Symbol is grouped, Default settings copied from the
Symbol from the Hub Module.
Taker Execution
Model
No TEM_A, TEM_B The name of the Taker Execution Model being configured
Liquidity Model Yes Aggregated_Mo
del
The Liquidity Model that will be assigned to the Taker Execution model indicates the
Maker(s) the Orders will be sent to.
Depending on the BBook% settings if the TEM is A Book or B Book. If A Book,
please check the below conditions
Field Editable Possible
Values
Description

If the Liquidity Model comprises One Maker only, Orders will be routed to that
one Maker.
If the Liquidity Model comprises more than one Maker, Orders will be routed to
different Makers and executed with the Maker depending on the factor that
which Maker is advertising the best price during the time of execution.
Markup Model Yes Plain_Markup
5Points_Markup
The Markup Model defines the Markups to be added on top of the Raw Prices when
Orders are executed on the Taker level.
Note: The Markup assigned here is not sent to the LP while execution which means
LP execution is on the Raw Price, but the Markup is only added on top of the Raw
Price when sending the confirmation from the Bridge to the Taker/Client.
Exec Mode Yes Sweep
Single_FOK
Single_IOC
The execution mode to be used when executing an Order.
Sweep: The Centroid Bridge sweeps the available liquidity book from top to
bottom (best to worse) until the Order is fully or partially filled
Single_IOC: The Centroid Bridge targets one quote (layer) of the liquidity book
that has enough volume and the best price to fill the Order entirely or partially. In
case no quote is available to fully fill the Order, it will be sent to the one that has
the largest volume from the available Book, also partial filling is allowed when
executing orders with Single_IOC.
Single_FOK: The Centroid Bridge targets one quote (layer) of the liquidity book
that can fill the entire size of the Order. If no quote with sufficient volume is
found, the Centroid Bridge reports a rejection after the TTL has expired which
means No Partial Filling is allowed when executing orders with Single_FOK.
Min Volume Yes 1000 The minimum order size, in notional volume, is to be processed by this Taker
Execution Model. Any volume below the specified amount will be rejected.
Example:
Taker: MT5/MT4/cTrader
Symbol: EURUSD
Contract Size: 100000
Min Lot on Application level: 0.01
Minimum Volume to be set on the bridge level: 0.01*100000 = 1000
Formula: Min Volume = Platform Min Lot x Contract Size
Max Volume Yes 100000000 The maximum Order size, in notional volume, to be processed by this Taker
Execution Model. Any volume beyond the specified amount will be rejected as
“above max vol”
Formula: Max Volume = Platform Max Lot x Contract Size
TTL Yes 300 ms This settings is in milliseconds, this component means, it will re-attempt to fill the
rejected orders if it is within the TTL time.
AMin Yes 1000 This component is same as the Min Volume, but as the name suggests this
component is strictly restricted for A book orders. Which means as a client you can
set a Minimum volume that you wish to send to your LP. If this condition is not
satisfied then the order will be booked as B Book irrespective of the BBook %
defined on the TEM level.
AStep Yes 1000
The value is in
Volume.
The step value in notional volume that represents the increment of the Order
Anything that does not comply, the remainder will be b booked
Example: If AStep is 3000, an Order of 5000 will be split as follows:

3000 sent to STP
2000 executed as B Book
Note: By default, this will also be used as Order Step validation unless configure
otherwise in description.
B Book Percent
(0-100)
Yes 0, 50, 100 The percentage of Order to be internalized (bbooked) in the Centroid Bridge. The
remainder is sent to the Maker as STP.
The percentage is a number between 0 and 100, where 0 represents a full A-Book
Order whereas 100 represents a full B-Book Order.
Example: If Book Percent is set to 80 then 80% of the Order will be b-booked while
the remaining 20% will be sent as STP.
BFix Yes 5000
10000
If you enter a value of 5000 under BFix, the centroid bridge will compare the TOB
from the Maker, if the advertised volume from the Maker is less than 5000, then the
BFix value will be New Available TOB for BBook.
BBoost Yes 1,2,3 This is only relevant to B-Book execution where the value defined in here is a
multiplier by which each layer of the liquidity book is multiplied. The BBoost value is
always equal or greater than 1.
Example: If liquidity book is made up of 3 layers:
Layer 1: 500K
Layer 2: 1M
Layer 3: 3M
Applying a BBoost factor of 3, the liquidity book would become as follows:
Layer 1: 1.5M
Layer 2: 3M
Layer 3: 9M
BDelay From Yes 100,200,300 This is only relevant to B-Book execution. It represents the first interval of a random
time delay applicable to execution in order to simulate the A-Book execution
BDelay To Yes 120,220,320 It represents the second interval of a random time delay applicable to execution in
order to simulate the A-Book execution.
The Order gets executed at the market price, after the delay has elapsed.
The below formula is used to calculate the final outcome of the delay that will be
enforced on the execution:
Delay = Random (BDelay From, BDelay To)
Example: If BDelay From is 100 ms and BDelay To is 120 ms, Delay would be
Random (100 and 120)
Gain Perc Yes 0,50,100 In the event of encountering a price improvement or positive slippage, the
percentage of improvement that will be reported to clients i.e. the difference
between Requested Price and Execution Price
100 means the Broker would keep all the improvement without passing on any
percentage to the client
0 means the Broker would pass all the improvement on to the Client
Multiplier Yes 0.5,2,10 A multiplier by which the order size will be multiplied prior to sending the order
request to the Maker.
Example: If Multiplier is set to 2 and client trades 100,000 EURUSD, an order
request of 200,000 EURUSD will be sent to the Maker.

LL Variation Yes 10, 20, 30 LL Variation is only relevant for B Book Execution and works along with the other
parameters such as BDelay From, BDelay To, Gain Perc and the action depends on
the parameters selected under LL Action.
This can be configured in points, where the Centroid Bridge will scan the book then
compare the previous price and new price. If the difference between the two price is
above or below the LL Variation then LL action will be triggered
1. If the difference between the new price after delay and the old price is within the
LL Variation: - If the new price is worse, the client gets the worse price
2. If the new price is better, the client gets a percentage of the price difference
depending on the percentage specified in the Gain Perc parameter
3. If the difference between the new price after delay and the old price is outside
the LL Variation, the Centroid Bridge would execute based on the selection in LL
Action as explained hereafter
Note: -1 means that this parameter is not enabled
LL Action Yes Indicates how to handle Orders if the difference between new price after delay and
old price is greater than the LL Variation on one side, or could be used to override
the normal execution in terms of request price.
Price Difference after delay:
Reject: The Centroid Bridge would reject the Order if the difference of the new
price after delay and old price is outside the LL Variation
Accept: Checks if the new price is in client’s favor or not
1- If new price is in broker’s favor (against client), client gets the new price
2- If new price is in client’s favor, the client gets a percentage of the price
difference depending on the percentage specified in Gain Perc parameter
Execution Parameters:
CONFIRM_BY_REQ_PRICE: Confirms order by request price as B Book
irrespective of the B Book Percentage Parameter, without even processing the
Order via the normal execution flow
PROC_CONFIRM_BY_REQ_PRICE: Processes the Order and returns the
requested price to the client irrespective of the actual execution price, for both A
and B Book Orders
PROC_CONFIRM_BY_REQ_PRICE_B: Processes the Order and returns the
requested price to client only for B Book execution whereas returning the actual
execution price to client for A Book execution
Note: For PROC_CONFIRM_BY_REQ_PRICE, clients may incur losses on A Book
trades in the event of order slippage
B Slip
Threshold
Yes 1, 2, 5 Configurable in points, it will absorb negative slippage according to the configured
value, provided it does not exceed the B Slip Max Accept value or if the B Slip Max
Accept is configured as 0
This feature is specifically intended for scenarios involving negative slippage. It is
applicable only to B Book trades, including of a 50% allocation for A Book and 50%
for B Book. The calculation of negative slippage will be based on the raw price,
excluding any markups.
You can use B Slip Threshold and B Slip Percentage independently or together.

To delete a Taker Execution Model
1. Click the “Delete” icon next to the desired Taker Execution Model
2. To confirm deletion, type the name of the Taker Execution Model in the field.
3. Click on the "Delete" button to confirm deletion.
The calculation of the threshold will take place prior to the percentage.
B Slip
Percentage
Yes 5%, 10%, 50% Configurable in percentage, this will additionally absorb any remaining negative
slippage after the B Slip Threshold, or it can function independently in determining
the extent of negative slippage absorption, as long as it does not surpass the B Slip
Max Accept
This feature is specifically intended for scenarios involving negative slippage. It is
applicable only to B Book trades, consisting of a 50% allocation for A Book and 50%
for B Book. The calculation of negative slippage will be based on the raw price,
excluding any markups.
You can use Threshold and Percentage independently or together.
When using Percentage Absorption, if it yields a value of 0.5, the absorbed slippage
will consistently be rounded in favor of the broker. For instance, if the negative
slippage is 7, the percentage is 50, resulting in 3.5 points, the absorption will be
3points.
B Slip Max
Accept
Yes 25, 50, 65 [in
points]
Configurable in points, it sets the maximum negative slippage that the broker can
absorb after applying the B Slip Threshold and B Slip Percentage settings.
This feature is specifically intended for scenarios involving negative slippage. It is
applicable only to B Book trades, consisting of a 50% allocation for A Book and 50%
for B Book. The calculation of negative slippage will be based on the raw price,
excluding any markups.
B Slip Max Accept will always prevail or take precedence over the total negative
slippage resulting from B Slip Threshold, B Slip Percentage, or a combination of B
Slip Threshold and B Slip Percentage.
Session Yes MON,00:00-
23:59
Defines the time of the day during which the Taker Execution Model will be
available for trading. All days of the week should be included and separated by
semicolon “;” along with the time interval during the day. 00:00-00:00 represents a
closure during a particular day
Description No A short description for reference purposes that is copied automatically from the
description defined in Symbols
Enable Yes Enabled,
Disabled
Indicates whether the Symbol is enabled or disabled for the selected Taker
Execution Model
If ticked, order requests of the particular Symbol will be processed via the Taker
Execution Model
If unticked, no order requests will go through

To Export the listed Taker Execution Model
1. Click on the “Taker Execution Models” Tab.
2. Click “Export” and select “Export to Excel” or “Export to CSV”
Exporting a Taker Execution Model Symbol Setting
To Export Takers Execution Model Symbol Settings
1. Select the desired Taker Execution Model from the list
2. Click Export → Export to Excel / Export to CSV
Uploading a Taker Execution Model
To Upload Takers Execution Model Symbol Settings
1. Click on “Upload”


2. Click on “Drop File” and select the File or drag the file to this section to upload.
3. To successfully upload the values, click on “Upload”.




```

---

<a id='taker-execution-rules-md'></a>
### 8. `taker-execution-rules.md`

```markdown
[🏠 Document Start](..\README.md) / [Taker API link](README.md) / Taker Execution Rules

# Taker Execution Rules

Overview
The Taker Execution Rules is an advanced feature that gives brokers enhanced control over the flow and execution of trades across
multiple platforms, including MT4, MT5, FIX, and REST API. This functionality enables brokers to define and implement various execution
strategies using key parameters such as tag 1, login, group, symbols, and other unique identifiers. Brokers can automate trade routing
based on specific criteria, giving them greater control over order flow from different platforms.
One of the standout features of Taker Execution Rules is the ability to modify rules in real-time without the need to restart the bridge or
platform plugins. This flexibility allows brokers to respond quickly to changing market conditions or trading behaviors, and seamlessly
onboard new execution strategies. The real-time adaptability helps optimize execution flow, ensuring brokers can react instantly,
maximizing efficiency and control in trade management.
With this feature, brokers can dynamically route orders to different execution models based on pre-set conditions—whether routing trades
to a maker via Straight Through Processing (STP) or internalizing them within the Centroid Bridge. Another key benefit is its ability to
enhance broker privacy. By eliminating the need to disclose tag 1 accounts to clients, it adds an extra layer of confidentiality, preventing
clients from identifying how their trades are being executed.
Taker Execution Rules enhances operational flexibility, enabling brokers to manage trades more effectively and privately, while
maintaining compliance with established trading conditions.

Within this module, you have the capability to:
Define Custom Execution Strategies: Set up tailored execution strategies across MT4, MT5, FIX, and REST API platforms.
Automate Trade Routing: Automatically route trades based on key parameters like tag 1, login, group, symbols, and other identifiers.
Modify Execution Rules in Real-Time: Update execution rules instantly without restarting the bridge or platform plugins.
Optimize Execution Flow: Respond to changing market conditions or trading behaviors efficiently by modifying execution strategies
on the fly.
Route Orders Dynamically: Direct orders to various execution models, such as STP or internalizing them within the Centroid Bridge.
Enhance Broker Privacy: Conceal tag 1 accounts from clients, adding an extra layer of confidentiality to the trade execution process.


Enabling Use Execution Rules
To enable the “Use Execution Rules” for a specific taker:
1. Navigate to the Taker Section
2. Enable the option "Use Execution Rules" for the desired taker
Creating Taker Execution Rules
To create a Taker Execution Rules
1. Click the “Add” button on the top right corner
2. Fill out the Wizard. You may refer to the field descriptions hereafter
3. Click “Submit” to submit the changes


For FIX Connections applying filters like Logins, Groups, Securities, or Directions, ensure that the required FIX tags are included
with each trade to ensure proper execution.
Rules won't be active unless 'Use Execution Rules' is enabled for the specific taker in the Taker section.
Enabled Yes Enabled,
Disabled
Indicates whether the Taker Execution Rule is enabled or disabled
If ticked, the Taker Execution Rule is enabled.
If unticked, the Taker Execution Rule is disabled.
Rule ID No 1,2,3 A unique ID number for the configured rule
Taker No Centroid_MT
5, Taker_FIX
When creating a rule, you must specify the Taker, as each rule is applied to one platform or
Taker.
Source
TEM
Yes TEM_A,
TEM_B
The Source TEM is the Tag 1 configured at the Taker level, where all trades are sent to the
bridge and then redirected to the Target TEM based on Taker Execution Rules. The Tag 1
account also acts as a filter available within the Source TEM for more precise trade routing.
Field Edita
ble
Possible
Values
Description

Bridge
Securities
Yes Bridge
Securities:
FX

Platform
Securities:
Forex\*

This option allows you to select or manage securities at the bridge level. When the 'Platform'
toggle is activated, the label changes to 'Platform Securities,' indicating that the configuration
will apply to platform-specific securities.
Explanation:
Bridge Securities: If you specify a Bridge Security here, only the symbols associated with that
security will be allowed for execution according to the defined rule.
Platform Securities: You can specify the securities available on your taker end or platform.
Once this is done, only symbols associated with those securities will be allowed for execution
according to the defined rules.
Note: For FIX connections, if a Platform Security filter is applied in the rule, FIX Tag 90013
must be included with each trade to ensure it follows the correct rule and execution flow.
Bridge
Symbols
Yes Bridge
Symbols:
EURUSD,XA
UUSD

Platform
Symbols:
EURUSD.x,E
URUSD.p
This field allows for symbol managing at the bridge level. If the 'Platform' toggle is enabled, it
updates to 'Platform Symbols,' reflecting that the symbol is now managed at the platform level.
Explanation:
Bridge Symbols: The 'Bridge Symbols' field allows you to configure symbols at the bridge level.
This option is applicable when the 'Platform' toggle is disabled, meaning symbol configuration
will follow the bridge-specific settings for routing and execution.
Platform Symbols: The 'Platform Symbols' field is displayed when the 'Platform' toggle is
enabled. This field allows you to manage the symbols that are available on the Taker side or
platform end. The mappings configured here will take precedence over bridge-level settings,
ensuring that the platform-specific symbols are used for routing and execution.
Side Yes Buy, Sell The trade side can be specified by selecting either "Buy" or "Sell." Additionally, the use of a
wildcard (*) allows for the inclusion of both sides, providing greater flexibility in trade execution.
Order Type Yes Market, Limit,
Stop
The type of order can be specified by selecting from options such as "Limit," "Market," or
"Stop." Additionally, the use of a wildcard (*) allows for the inclusion of all order types, providing
greater flexibility in trade execution.
ExtPartyId
1 (Login)
Yes 10012,10015 This parameter serves as the unique login identifier for the external party involved in trade
execution, enabling accurate order tracking and management.
MT5: Specify the MT5 logins in this field.
FIX: Specify the logins here, but ensure the corresponding FIX tag 90001 is included when
sending the order to follow the correct rule.
Note: Multiple accounts can be specified by separating them with a comma (",")
ExtPartyId
2 (Group)
Yes RetailGroup\*
,StandardGro
up\*
This parameter identifies the group associated with the external party, enabling trade execution
based on specific rules applicable to that group.
MT5: Specify the MT5 group here.
FIX: Specify the group here, but ensure the corresponding FIX tag 90002 is included when
sending the order to apply the correct grouping rule.
Note: Multiple groups can be specified by separating them with a comma (",")
Time in
Force (TIF)
Yes FOK, IOC,
GTC
You can choose from the available options i.e. Day, FOK, GTC, GTD and IOC and orders will
execute according to your selected settings.
Direction Yes IN, OUT You can select “IN”, “OUT” or “IN_OUT” to execute trades based on the directions.

To configure or modify an existing Taker Execution Rules
1. Track the desired Taker Execution Rules
2. Configure the desired fields
3. Click the “Save” button on top to deploy the changes
Adjusting Taker Execution Rules Order
How to adjust the order of Taker Execution Rules
Execution rules are read from top to bottom. Brokers can adjust the order using the drag-and-drop feature, allowing them to control which
rules take priority.
Delete Taker Execution Rules
To delete a Taker Execution Rules
Note: For FIX connections, if a Direction filter is applied in the rule, FIX Tag 90014 must be
included with each trade to ensure it follows the correct rule and execution flow.
Min Size Yes 1000 Min Size is the minimum trade volume for the rule to apply, ensuring trades below this are not
routed by the rule, but it doesn't limit the overall trade size.
Max Size Yes 50000 Max Size is the largest trade volume allowed for the rule to apply, ensuring trades above this
limit are excluded, but it doesn't restrict smaller trades.
Target TEMYes CentroidExec
ution_TEM
This is the TEM configured on the bridge where trades are directed. Trades coming from the
default account or TEM will be routed to the Target TEM based on the settings you’ve defined
above. This ensures that all trades are managed according to your specified rules, allowing for
precise execution and control.
Description Yes A short description for reference purposes
All changes made at the settings level take effect immediately and do not require restarting the bridge.


2. Enter the ID in the pop-up window & Click on “Delete” button to confirm the deletion
Exporting Taker Execution Rules
To Export Taker Execution Rules
1. Click “Export” and select “Export to Excel” or “Export to CSV”
Uploading Taker Execution Rules
To Upload Takers Execution Rules
1. Click on “Upload”
2. Click on “Drop File” and select the File or drag the file to this section to upload.


Replace All - Checked
Replace All - Unchecked
4. You also have the option to discard the bulk upload by clicking on the “Close” Button
When uploading Taker Execution Rules, the "Replace All" option allows you to control how new rules are applied:
Replace All - Checked If checked, this will overwrite all existing
rules with the new rules in the uploaded
file. The final set of rules will only include
those present in the uploaded file.
Replace All - Unchecked If unchecked, the system will append new
rules from the file to the existing ones. This
may result in duplicate entries if the file
contains rules already present in the
system.
Replace All Description Result


Sample Rules and Trade Processing with Execution Rules
Scenario 1: For MT5 Takers
As shown in the snapshot, the rule specifies that if a trade comes through Tag 1 "Centroid_TEM_A", from MT5 Login ID 10012, and is a
Market Order, it will be redirected to the Centroid_TEM_C account.
Additionally, there's a filter for Min Size and Max Size:
Min Size: 2000
Max Size: 5,000,000
(Both in volumes)
If the trade volume is below 2000, it won’t execute with Centroid_TEM_C. Instead, the system will move to the next rule to check its
conditions. But if the trade volume falls between 2000 and 5,000,000, it will be executed with Centroid_TEM_C.
Additionally, if no rules match the trade’s criteria and filters, the trade will be rejected by Centroid Bridge.

Scenario 2: For FIX Takers
As shown in the snapshot, the rule specifies that if a trade comes through Tag 1 "Centroid_TEM_1", with the symbol "XAUUSD" and is
an IOC Order, it will be redirected to the Centroid_TEM_2 account.
This rule applies only to XAUUSD trades as IOC orders. If a trade involves a different symbol, the bridge will move to the next rule and
check its conditions. If no rules match the trade's criteria and filters, the trade will be rejected by Centroid Bridge.




```

---

<a id='taker-feeds-md'></a>
### 8. `taker-feeds.md`

```markdown
[🏠 Document Start](..\README.md) / [Guidelines for Configuring and Sending Credentials for FIX Centroid Taker](README.md) / Taker Feeds

# Taker Feeds

Overview
The Taker Feeds component displays all the pricing feeds configured in the Centroid Bridge. The Taker Feed can be assigned to one or
multiple Takers into which quotes will be streamed.
An unlimited number of Taker Feeds can be defined with its dedicated settings and can be configured down to the level of individual
Symbol.
Within this module, you have the capability to:
Create a New Taker Feed: Initiate the setup for a new Taker Feed.
Filter Taker Feeds: Categorize Taker Feeds based on various criteria for easier identification.
Global Enable/Disable: Enable or disable all Taker Feeds globally, applying changes across associated Symbols.
Configure Taker Feed: Customize a specific Taker Feed, toggling its enable/disable status, and adding a description.
Delete Taker Feed: Remove an existing Taker Feed from the system.
Export Taker Feeds: Save the list of Taker Feeds to Excel or CSV for external reference.
Filter and Look up Symbols: Streamline Symbol configuration by searching and filtering within a Taker Feed.
Configure Bulk Symbol Settings: Use the Edit icon to adjust settings for multiple Symbols at once, either for all or a filtered group.
Configure Symbol Settings: Fine-tune settings for a specific Symbol within a Taker Feed.
Export Symbol Settings: Save the configured settings of a particular Taker Feed's Symbol to Excel or CSV.
Upload Modified Settings: After making changes offline, re-upload the modified file to implement the necessary adjustments.
Note: Enabling or disabling a Taker Feed at this level will impact all Symbols within that Taker Feed, meaning prices won’t be streamed for
this specific taker.
Creating a Taker Feed
To create a Taker Feed
1. Click the “Add” button on the top right corner


2. Fill out the Wizard. You may refer to the field descriptions hereafter
3. Click “Submit” to submit the changes
Taker
Feed
Plain_TF, Test_TF,
S_TF
A unique name of the Taker Feed
Taker Centroid_MT4,
Centroid_MT5
The Taker(s) to which the Taker Feed will be assigned. You may select one or multiple Takers
Markup
Model
Markup_Model,
10PTS_MM
The Markup Model which defines the markups to be added on top of the raw prices while
streaming the prices to the taker
Suffix .vip, .test, #, .pro This is mainly relevant to Taker type - MT4/MT5, because here you can have different set of
symbols.
Example: EURUSD, EURUSD.pro, EURUSD.vip
To ensure that the Taker receives prices for suffix symbols such as .pro and .vip, you need to
create a Taker Feed with the specified suffix. Simply input .pro or .vip
Upon adding this information, a Taker Feed will be generated with the designated suffix.
Liquidity
Model
Aggregated_Model When you assign a Liquidity Model to the Taker Feed, you are making sure that this particular feed
is receiving prices from the Maker(s) assigned in that Liquidity Model.
One Maker: If only 1 Maker is assigned to the Liquidity Model, then your Taker Feed is entitled to
receive prices from this Maker only.
Multiple Makers: If there is more then one Maker assigned to the Liquidity Model then your Taker
Feed is entitled to receive prices from both the makers as Aggregated Feed.
Enable Enabled, Disabled Indicates whether the Taker Feed is enabled or disabled
If ticked, the Taker Feed will be enabled for streaming prices upon creation
If unticked, the Taker Feed will be disabled upon creation, meaning no prices will be streamed
for this particular Taker Feed.
Descriptio
n
Plain_Feed,
Test_Feed,
VIP_Feed
A short description for reference purposes
Field Possible Values Description

Note: Settings configured during the creation of the Taker Feed will be applicable across all Symbols. You will be able to modify and
further customize the settings of a Taker Feed on a per Symbol basis as explained hereafter.
Configuring Taker Feed
To Configure/Modify a newly added/existing Taker Feed on a per Symbol basis
1. Select the checkbox adjacent to the taker feed name
2. Configure the settings on a symbol level
3. Click the “Save” button to apply the modifications.
Copy
From
Allows to copy the configuration settings of an existing Taker Feed
Symbol No EURUSD, XAUUSD The name of the Symbol to be configured, as defined under Symbols
Security No FX, CFD, Equity The Security into which the Symbol is grouped
Taker Feed No Retail_Feed,
Plain_Feed
The name of the Taker Feed being configured
Taker Symbol Yes EURUSD.pro,
EURUSD.vb
Taker symbol is the name of the instrument available at the Taker End where
connecting client is expected to subscribe
It is important that the correct Taker symbol is being sent to the bridge during
subscription. Taker symbol can be adjusted if really necessary and not
configurable on the connecting platform
Liquidity Model Yes Aggregated_pool,
ABC_LM
When you assign a Liquidity Model to the Taker Feed, you are making sure
that this particular feed is receiving prices from the Maker(s) assigned in that
Liquidity Model.
One Maker: If only 1 Maker is assigned to the Liquidity Model, then your Taker
Feed is entitled to receive prices from this Maker only.
Multiple Makers: If there is more then one Maker assigned to the Liquidity
Model then your Taker Feed is entitled to receive prices from both the makers
as Aggregated Feed.
Markup Model Yes Retail_markup,
Plain_markup,
By assigning the Markup Model here, all the settings from this Markup Model
will be applied on the Raw prices from the Maker i.e. the Liquidity Model and
Field Editable Possible Values Description

10Points_markup then streamed to your Taker.
Only one Markup Model can be selected for one Taker Feed while creating the
TF however, furthermore ,you can configure symbol wise manually.
Feed Mode Yes Aggregate, Layer The pricing mode to be used by the Feeder/TF.
Aggregate: The Centroid Bridge sends to the Taker the quotes in the
liquidity book, as received from the Maker(s)
Aggregate_IOC: The Centroid Bridge combines all similar quotes in the
liquidity book, sums up the respective liquidity, and streams into clients as
one quote
Layer: The Centroid Bridge constructs an artificial liquidity book based on
the Levels defined in Levels where it fills each Level with the best prices
with sufficient volume to match the volume defined at the respective Level
(layer). Only one quote per Level will be sent.
Layer_IOC: The Centroid Bridge constructs an artificial liquidity book
similar to Layer mode yet the only difference is that in each Level it would
show the VWAP price matching the volume specified at each Level
Volume: when multiple quotes in the liquidity have the same volume, the
Centroid Bridge streams only one quote with the best price
Min Volume Yes 1000 The minimum volume to appear at the TOB.
Note: A multiplier value of 100 should be accounted for in the minimum volume
Example: If Min Volume is set to 25M (250K x 100) and the liquidity book has
the following:
100K @ Level 1
500K @ Level 2
1M @ Level 3
Then the Centroid Bridge will stream the following:
250K @ Level 1
500K @ Level 2
1M @ Level 3
Depth Yes 1,3,5 The number of layers to be streamed to clients.
Example: If Depth is set to 1, only the TOB will be streamed If Depth is set to
5, the Centroid Bridge will stream the first five layers, provided that the liquidity
book has 5 or more layers
Feed Source Yes A_BOOK, B_BOOK The liquidity book that will be used to update clients about book consumption
and available liquidity in the price updates.
The Centroid Bridge maintains two separate books, A and B, and keeps track
of the available liquidity separately. When an A-Book Order is placed the A-
Book liquidity book will be affected and vice versa.
It’s advisable to use the A-Book mode with clients placed on the A-Book and
B-Book for clients placed on the B-Book
Feed TOB Volume Yes It defines a TOB value to be streamed into the Taker irrespective of the actual
Liquidity Book and its TOB value.
Example: If Feed TOB Volume is 10M, Taker would always see 10M at TOB
irrespective of the real Liquidity Book and its TOB

Deleting a Taker Feed
To delete a Taker Feed
1. Click the “Delete” icon next to the desired Taker Feed
2. To confirm deletion, type the name of the Taker Feed in the field.
3. Click on the “Delete” button to confirm the deletion
Feed Mult Yes 1,2,3 A multiplier by which the available liquidity in the book is multiplied, for the
purpose of showing more liquidity. The multiplier is a positive value greater or
equal to 1.
Example: If Feed Mult is set to 3 and available liquidity is as follows:
1M @ Level 1
2M @ Level 2
Then the Centroid Bridge will show:
3M @ Level 1
6M @ Level 2
Price Mode Yes Various, Midpoint Defines whether floating or fixed spreads are used for price streaming.
Various: The Centroid Bridge just adds the markups defined in Markup
Models to the bid and ask price respectively.
Midpoint: The Centroid Bridge streams prices with fixed spreads. The
Centroid Bridge first calculates the mid price (bid price + ask price/2) then
adds the bid and ask markups (defined in the Markup Model) to each side
of the price.
Interval Yes 100, 200, 300 The time interval, measured in milliseconds, specifies the frequency at which
the Taker Feed allows new price updates to the assigned taker. This interval
determines how often the taker receives the most recent prices.
Session Yes MON,00:00-23:59 Defines the time of the day during which the Taker Feed will be streaming All
days of the week should be included and separated by semicolon “;” along
with the time interval during the day. 00:00-00:00 represents a closure during
a particular day
Description No A short description for reference purposes that is copied automatically from
the description defined in Symbols
Enable Yes Enabled, Disabled Indicates whether the Trader Feed is enabled or disabled for the selected
Symbol.
If ticked, quotes will be streamed on that Symbol
If unticked, quotes will be switched off on that Symbol


Exporting a Taker Feed
To export a Taker Feed
1. Select the desired Taker Feed from the list
2. Tick the checkbox to select a Taker Feed
3. Click “Export” and select “Export to Excel” or “Export to CSV”
Uploading a Taker Feed
To upload a Taker Feed symbol settings
1. Click on the “Upload”
2. Click on “Drop File” and select the File or drag the file to this section to upload.


3. To successfully upload the Taker Feed values, click on “Upload”
4. You also have the option to discard the bulk upload by clicking on the “Close” Button



```

---

<a id='takers-readme-md'></a>
### 8. `takers/README.md`

```markdown
[🏠 Document Start](..\..\README.md) / [Takers](..\README.md) / Takers

# Takers

Overview
The Takers module handles the Liquidity Takers in the Centroid Bridge including a variety of popular front-end platforms as well as direct
FIX APIs connected to the Centroid Bridge in addition to Drop Copy. Platforms include MT4, MT5, Ctrader, or any other FIX-compliant
platforms as well as our own Centroid Trading UI.
From the Taker components, you can configure and manage all pricing and trading settings pertaining to the Takers connected to the
Centroid Bridge, through the different components, Taker Feeds, and Taker Execution Models, which are explained in more detail
hereafter.
This module displays all the liquidity Takers defined in the Centroid Bridge, which could be of type MT4, MT5, FIX, Centroid UI, and Drop
Copy.
In addition to viewing all Takers configured in the Centroid Bridge, additionally you have the capability to:
Create a New Taker (FIX or Drop Copy): Initiate the setup for a new FIX or Drop Copy Taker.
Filter and Look Up Takers: Categorize and search for specific Takers using various criteria.
Enable and Disable Taker: Manage the active status of a particular Taker.
Delete Taker: Remove a Taker of type FIX or Drop Copy by clicking the delete button.
View Taker Connection Settings: Access and review the connection settings for a Taker.
Export Taker FIX Config (Pricing and Trading) or Drop Copy: Save configuration details to Excel or CSV.
Export Taker List: Save the list of Takers to an Excel file or CSV file.
Note: Disabling Taker on this level means, you are disabling the taker to receive quotes/prices from the bridge and disabling the execution
i.e. no trade will be accepted by the bridge from this taker. While enabling a newly added taker will require a restart.
Note: Takers of type MT4 and MT5 cannot be added here, such configurations require assistance from Centroid Support Team.
Creating a Taker
To create a Taker of type FIX or Drop Copy
1. Click the “Add” button
2. Fill out the Wizard. You may refer to the field descriptions hereafter
3. Click “Submit” to submit the changes


Important Notes:
1. Only Takers of type FIX and Drop Copy can be created on the client end, for other types i.e. MT4/MT5, you need to send the request to
support@centroidsol.com and the Centroid Support team will add it for you.
2. Once you have created the Taker, you need to perform a Bridge Restart, after the restart, the Taker will be ready to accept
connectivity and the connecting party will be able to establish the connection to the bridge.
Export Takers List
To Export listed Takers
1. You will need to click on the “Takers” module
2. Click on the “Takers”
3. Click “Export” and select “Export to Excel” or “Export to CSV”
Taker A unique name of the Taker
Type The type of Taker:
FIX: FIX API Pricing and Trading to be given to clients who wish to connect via FIX
DROPCOPY: FIX Drop Copy allowing connection to post-trade information via FIX
Description A short description for reference purposes
IP List IP(s) of the Taker, comma separated in case of multiple IPs
Disclaimer: You need to share Sources IPs of the [Taker] with Centroid Support, so we can create the
whitelisting request, without the IP whitelisted no connection will be established.
Enable Indicates whether the Taker is enabled or disabled
If ticked, the Taker will be enabled upon creation
If unticked, the Taker will be fully disabled upon creation hence, no quotes and no execution of trades from
this Taker.
Field Description

Export FIX or Drop Copy Credentials
You can export the FIX credentials pertaining to Takers of type FIX or Drop Copy. The FIX Taker credentials allow clients to connect to the
Centroid Bridge via FIX to receive prices and send Order requests, whereas Drop Copy Taker settings allow you or any third party to
connect to post-trade information in real-time.
To Export the FIX credentials
1. Click the “Export Fix Config” button next to the desired Taker as seen below
2. Once exported, a text file will be downloaded automatically in which you can see the FIX API configuration
FIX Taker
It contains two sessions with a pricing connection for which the client will be able to connect to receive prices and a trading connection for
the client to be able to send trades and receive order confirmations and execution reports from the Centroid Bridge. FIX client should
target the Taker Execution Model when sending Order requests via FIX tag 1. In the event of having multiple accounts or Taker Execution
Models assigned to the same taker, the accounts or tag #1 will populate all the available values.


Drop Copy
It contains a single session similar to a Trading session through which the client can connect to receive a copy of post-trade information,
as seen below.




```

---

<a id='takers-guidelines-for-configuring-and-sending-credentials-for-fix-centroid-taker-md'></a>
### 8. `takers/guidelines-for-configuring-and-sending-credentials-for-fix-centroid-taker.md`

```markdown
[🏠 Document Start](..\..\README.md) / [Takers](..\README.md) / [Takers](README.md) / Guidelines for Configuring and Sending Credentials for FIX Centroid Taker

# Guidelines for Configuring and Sending Credentials for FIX Centroid Taker

Overview
This guide covers the setup of a Centroid Taker on the specified bridge, detailing the steps needed to configure and activate it as part of
the centroid-to-centroid connection process.
Provisioning Fix Taker and Related Components
For provisioning steps related to the Fix Taker, Taker Feed, and Execution Model, please refer to the documentation at [insert path or
link].
Instructions for Sending Maker Credentials to FIX Takers
After adding your FIX Taker, follow these steps to send the necessary credentials:
1. Locate the Mailbox Icon
Find the small mailbox icon in the interface. Clicking it will open a pop-up window requesting the following information:
Your Company: This field is auto-filled based on your Bridge configuration. You can edit it if necessary.
Client Name: Enter the name of the FIX Taker (typically your client's name).
Client Email: Provide the client's email address where the credentials will be sent. Ensure this email is correct and active.
Ensure that Tag1 is correctly configured, as the absence of Tag1 will prevent the email from being sent.
Once you click the Proceed button, your taker client will receive an email with the subject: Maker Credentials from "Your Company Name".


Upon completing these steps, your Taker client will receive an email containing the required credentials. The next phase will be managed
on their end, where they will proceed to add you as a Maker. For further assistance, they can refer to the relevant documentation or reach
out to support.
Note: A bridge restart is required to activate the Taker
Note: Whitelisting is not required for Centroid-to-Centroid connections


```

---
