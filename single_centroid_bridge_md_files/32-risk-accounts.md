# 📁 32-risk-accounts

- **Generated:** 2026-09-10 12:08
- **Total Files:** 6
- **Source:** `C:\Users\DELL\Downloads\backend_code-main (1)\backend_code-main (2)\bridge_manual_md\32-risk-accounts`

---

## 📑 Table of Contents

1. [README.md](#readme-md)
2. [account-groups.md](#account-groups-md)
3. [balance-transaction.md](#balance-transaction-md)
4. [limit-symbol-groups.md](#limit-symbol-groups-md)
5. [master-risk-account.md](#master-risk-account-md)
6. [taker-risk-filter.md](#taker-risk-filter-md)

---

## 🌲 Project Structure

```
32-risk-accounts/
├── account-groups.md
├── balance-transaction.md
├── limit-symbol-groups.md
├── master-risk-account.md
├── README.md
└── taker-risk-filter.md
```

---

## 📄 Files

<a id='readme-md'></a>
### 6. `README.md`

```markdown
[🏠 Document Start](..\README.md) / Risk Accounts

# Risk Accounts

The Risk Accounts Module allows to create and configure Accounts Groups, Limit Symbol Groups, Balance Transaction, and Taker Risk
Filter. Upon clicking the “Risk Accounts” button on the left-hand side menu, it expands to show the different components underneath which
are explained in greater detail hereunder.




```

---

<a id='account-groups-md'></a>
### 6. `account-groups.md`

```markdown
[🏠 Document Start](..\README.md) / [Limit Symbol Groups](README.md) / Account Groups

# Account Groups

Overview
In this component, you can create Risk Accounts and account Groups (under which Risk Accounts are grouped) and configure Risk
Accounts on a Account Group and Risk Account basis.
Account Group Level Configuration
Configuration at the Account Group Level is applied across all Risk Accounts underneath. Limit Symbol Group is the parameter that is
being configured at the Group Level which is applied to all Risk Accounts underneath. The Limit Symbol Group parameter will be explained
in more detail in the respective section hereafter.
You can make the following configurations at the Account Group Level:
Filter Account Groups: Narrow down Account Groups based on desired fields to simplify configuration.
Select Account Groups: Choose one or multiple Account Groups to display the Risk Accounts underneath.
Enable/Disable all Account Groups: Manage the active status of all Account Groups.
Configure Limit Symbol Group: Set configurations across all available Account Groups, impacting all linked Risk Accounts.
Enable/Disable a particular Account Group: Affect all Risk Accounts within the selected Account Group.
Configure Limit Symbol Group of an Account Group: Apply settings across all Risk Accounts within the chosen Account Group.
Delete an Account Group: Remove an existing Account Group.
Export Account Groups: Save the list of Account Groups to an Excel file or CSV file.
Creating an Account Group
To create an Account Group
1. Click on the “Add” button
2. Fill out the Wizard, as explained below


3. Click on “Submit” to submit the changes
Deleting an Account Group
To delete an Account Group
1. Click the “Delete” icon next to the desired Account Group
2. To confirm the deletion, type the name of the Account Group in the field.
3. Click on the “Delete” button to confirm.

Exporting an Account Group
To Export an Account Group
Account Group The name of the Account Group to be created
Limit Symbol
Group
Assign the limit symbol group that you created for this particular Risk Account.
Enable Indicates whether the Account Group is enabled or disabled
* If ticked, the Account Group is enabled upon creation
* If unticked, the Account Group is disabled upon creation
Description A short description for reference purposes
Field Description


1. Select the desired Account Group from the list
2. Tick the checkbox to select an Account Group
3. Click “Export” and select “Export to Excel” or “Export to CSV”
Account Level Configuration
Other parameters can be configured at the level of Risk Account which applies solely to that particular Risk Account, unlike the ones
configured at the level of Account Group which are enforced across all Risk Accounts within.
You can configure the following parameters at the level of Risk Account under a selected Account Group:
Filter by Desired Fields: Narrow down options based on desired fields to simplify configuration.
Enable/Disable Risk Accounts: Manage the active status of Risk Accounts.
Configure Bulk Parameters: Adjust parameters across multiple Risk Accounts within the Account Group.
Configure Parameters of a Risk Account: Set desired parameters for a specific Risk Account.
Delete a Risk Account: Remove a specific Risk Account.
Export Risk Accounts: Save the list of Risk Accounts within an Account Group to an Excel File or CSV File.
Creating a Risk Account
To create a Risk Account
1. Click the “Add” to create a new Risk Account that is under the desired account group.
2. Fill out the Wizard as explained below.
3. Click on “Submit” to submit the changes.


Risk Account Preferred Risk Account Name
Group The Account Group the Risk Account belongs to
Currency USD The currency of the Risk Account into which all transactions are translated.
Note: Default value is always USD
Category Taker,
Maker
Defines whether the Risk Account is of type Taker or Maker.
Taker: If the Risk Account is linked to one or multiple Takers and/or Taker Execution Models
Maker: If the Risk Account is linked to one or multiple Makers
Note: If the Risk Account is linked to a Taker the name of the Taker will appear followed by @*. E.g:
FIX_CLIENT@*. IF the Risk Account is linked to a certain Taker Execution Model within the Taker, the
name of the Taker will appear followed by @ and the name of the Taker Execution Model. Example:
FIX_CLIENT@Account1
Taker/Maker Indicates whether the Risk Account is defined as a Taker or a Maker upon creating the Risk Account,
as explained hereafter in Create a Risk Account section
Taker: If the Risk Account is defined as a Taker, this parameter allows to link the Risk Account to
one or multiple Takers and/or Taker Execution Models
Maker: If the Risk Account is defined as a Maker, this parameter allows to link the Risk Account to
one or multiple Makers to check exposure as well as controlling what is being sent to the Maker
Type Margin,
NOP, Risk
The Type of the Risk Account which defines its purpose:
Margin: keeps track of all orders under a Risk Account and rejects any order that would increase
the exposure above the Margin Call Level threshold
Field Possible
Values
Description

Deleting a Risk Account
To delete a Risk Account
1. Click the “Delete” icon next to the desired Risk Account.
NOP: Similar to Margin with one additional feature that allows to define an exposure on a per
Symbol basis as explained in Limit Symbol Currency hereafter (Exposure Limit field)
Risk: This option is only available if the Risk Account is “Taker Type”, This applies to B Book
execution only and works in conjunction with the NOP Limits defined at the level of the Symbol.
When the threshold is breached, the Centroid Bridge would automatically start routing any position
that would further increase the exposure to the Maker. For orders of opposite side that would
decrease the exposure, the Centroid Bridge would send them to the Maker as well to offset
overflow until the exposure is flattened out.
Stop Out
Level
50 The margin percentage level at which point the Risk Account will get stopped out and positions will get
closed automatically
Stop Out
Mode

A_PERCEN
T
A_HIGH_L
OSS
A_HIGH_M
ARGIN
Dictates how the Risk Account gets liquidated when the Stop out level is reached:
AB_HIGH_LOSS: Closes the highest losing Position first irrespective of execution (A or B Book)
AB_HIGH_MARGIN: Closes the Position with the highest Blocked Margin first irrespective of
execution (A or B Book)
A_HIGH_LOSS: Closes the highest losing A Book Position
A_HIGH_MARGIN: Closes the A Book Position with the highest Blocked Margin first
B_HIGH_LOSS: Closes the highest losing B Book Position
B_HIGH_MARGIN: Closes the B Book Position with the highest Blocked Margin first
Disabled: Stop out is not active thus Account does not get liquidated
Note: When the Centroid Bridge closes the first Position it checks whether the Stop out level is still
above the defined one, if not it will close the next Position depending on the Square Off Mode utilized
Note: If the Position is made up of Orders accumulated from different Taker Execution Models, the
Centroid Bridge will close the Position by sending each Order separately through its respective Taker
Execution Model
Enable Enabled,
Disabled
Indicates whether the Risk Account is enabled or disabled
If ticked, the Risk Account is enabled
If unticked, the Risk Account is disabled which means that the Risk Account would still track the
positions but would not apply margin or risk settings
Exposure
Limit
1,000,000,0
00
This is only relevant to Risk Accounts of type NOP where a Limit in USD notional value can be set at
which point no Orders that would increase the exposure above that limit would be allowed.
Note: Default value is -1 which indicates that no Exposure Limit set
Warn Level 50,70,90 Margin percentage levels of the Risk Account at which point a notification alert will be sent by the
Centroid Bridge via email to the registered email address(es).
You can add as many values as you want provided that the total number of characters does not
exceed 40
Margin Call
Level
100 The Margin percentage level at which point no Orders that would further increase the exposure would
be allowed
Description A short description for reference purposes

2. To confirm the deletion, type the name of the Risk Account in the field.
3. Click on the “Delete” button to confirm.
Exporting a Risk Account
To Export a Risk Account
1. Select the desired Risk Account from the list
2. Tick the checkbox to select a Risk Account
3. Click “Export” and select “Export to Excel” or “Export to CSV”




```

---

<a id='balance-transaction-md'></a>
### 6. `balance-transaction.md`

```markdown
[🏠 Document Start](..\README.md) / [Account Groups](README.md) / Balance Transaction

# Balance Transaction

Overview
The Balance Transaction component allows one to make a variety of Balance Transactions into a Risk Account in addition to viewing the
list of all available Risk Accounts along with their information such as balance, P/L and margin details in real-time. Balance Transactions
can be manual if they come from Balance Operations (deposits, withdrawals, credits, etc) or automatic if they result from Trades (realized
P/L, Commissions, Swaps, etc).
Within this module, you have the capability to:
Balance Transaction on Risk Account: Adjust account balances for risk management.
View Real-Time Risk Accounts: See up-to-date information on Risk Accounts.
List Flat and Stopped Out Risk Accounts: Identify accounts in a flat state or stopped out.
Export Risk Accounts Data (Excel/CSV): Save Risk Accounts details for analysis.
Export Margin Call or Stopped Out Accounts (Excel/CSV): Specifically export accounts in Margin Call or stopped out status.
Balance Transaction Operations
In this component, you can make a variety of Balance Transaction operations into or out of Risk Accounts.
To make a balance transaction:
1. Fill out the wizard as explained below
2. Click the “Submit” buttons to submit the changes


Account Balance
The Account Balance table displays the list of all available Risk Accounts along with their account information in real-time.
Name The name of the Risk Account
Currency The currency of the Risk Account into which all transactions are translated.
Balance The available balance of the Risk Account
Balance = Deposit + Realized P/L
Available
Withdraw
The available amount for withdrawal which is equivalent to the Free Margin
Available Withdraw = Equity – Margin Blocked - Credit
Equity The real-time Equity of the Risk Account
Equity = Balance + running PL
PL The real-time floating PL of the Risk Account
Blocked Margin The amount of used Margin in Account Currency (USD)
Blocked Margin = Volume * (margin/100) * avg price
Margin Level The Margin Level Percentage of the Risk Account
Margin Level = Equity/Margin blocked x 100
Commission The Commission charged in USD on the Risk Account on a per Symbol basis, if any. Commissions remain
unrealized (only affect Equity) until the Position is partially or fully closed, which will affect the Balance based on
the closed Volume.
Swap The Swap charged in USD on the Risk Account on a per Symbol basis for keeping positions overnight, if any.
Swaps remain unrealized (only affect Equity) until the Position is partially or fully closed, which will affect the
Balance based on the closed Volume
Field Description

Notional The total USD exposure of the Risk Account in Notional Volume
Credit The available credit granted to the Risk Account in USD, if any
Trading State The Trading State of the Risk Account.
STOPPED OUT: Risk Account is flat or negative which could be due to stop out or Account out of balance
MARGIN CALL: Risk Account is on Margin Call when the Margin Level hits or drops below the percentage
defined in Warn Level set for the Account
NEUTRAL: Risk Account has enough balance


```

---

<a id='limit-symbol-groups-md'></a>
### 6. `limit-symbol-groups.md`

```markdown
[🏠 Document Start](..\README.md) / [Risk Accounts](README.md) / Limit Symbol Groups

# Limit Symbol Groups

Overview
In straightforward terms, the Limit Symbol Group allows you to set different parameters for various Risk Accounts, such as Margin,
Exposure Limit, Commission, Swaps, and more.
Here's how you assign the Limit Symbol Group to a Risk Account:
In this component, you can view all the Limit Symbol Groups defined in the portal in addition to doing the following:
Create a Limit Symbol Group: Establish a new Limit Symbol Group.
Filter and Look Up a Limit Symbol Group: Search for and identify a particular Limit Symbol Group.
Delete a Limit Symbol Group: Remove a specific Limit Symbol Group.
Export Limit Symbol Groups: Save the list of Limit Symbol Groups to an Excel file or CSV file.
Filter a Symbol within a Limit Symbol Group: Narrow down options for Symbols within a Limit Symbol Group to simplify
configuration.
Configure Bulk Symbol Settings: Adjust settings for multiple Symbols by clicking the edit button next to the desired column.
Configure a Limit Symbol Group: Fine-tune settings down to the level of each individual Symbol within a Limit Symbol Group.
Export Symbol Configuration of a Limit Symbol Group: Save the configured Symbol settings of a specific Limit Symbol Group to an
Excel file or CSV file.
Upload New Configuration: Implement new configurations for a specific Limit Symbol Group by uploading the changes.


Create a Limit Symbol Group
To create a Limit Symbol Group:
1. Click on “Add” to create a new Limit Symbol Group.
2. Fill out the Wizard as explained below
3. Click “Submit” to submit the changes
Once the new Limit Symbol Group has been created, you can assign it to the desired Account Group which in turn would deploy across all
Risk Account underneath.
Limit Symbol Group Test_LSG, Plain_LSG,
TakerName_LSG
A unique name of the Limit Symbol Group
Description A short description for reference purposes
Copy From Allows to copy the configuration settings of an existing Limit Symbol Group
Field Possible Values Description

Configure Limit Symbol Group
To configure a Limit Symbol Group on a per Symbol basis
1. Select the Limit Symbol Group you want to configure by ticking the box before the Limit Symbol Group Name.
2. Locate and make the changes to the desired Symbol(s). The changes are highlighted in orange
3. Click the “Save” button on top to deploy the changes
Symbol No EURUSD The Symbol to be configured
Limit Symbol
Group
No Test_LSG
ABC_LSG
The Limit Symbol Group being configured
Security No FX, CFD,
Equity
The Security into which the underlying Symbol is grouped
Limit Yes 10,000,000 Exposure Limit in notional value at which point no more Orders that would increase the
Symbol exposure above that limit would be permitted.
[Note: This will only work with Risk Account type NOP and Risk]
Margin
Percentage
Yes 0.5,1,2 The Margin % to be blocked when the client is opening a new position.
The resulting value will be added to the overall margin blocked of the Risk Account.
Example:
Symbol: EURUSD
Margin %: 0.5
Open Order: 100000
Price: 1.11550
The Margin Blocked will be calculated as = Open Order Value * Margin % * Price
= 100000 * 0.5% * 1.11550 = USD 557.75 [Margin will be blocked]
Margin Percentage is also related to Leverage and the formula is 1/Leverage * 100.
For example, if the symbol has a leverage of 5 then the Margin Percentage will be 20 (
1 / 5 * 100)
Field Editabl
e
Possible
Values
Description

Commission Yes 1.5, 10, 15 The commission column allows you to input the amount you wish to charge clients for
opening or closing positions in a trading platform.
Commission
Type
Yes Fixed, Fixed
Per Lot, Per
Mil
We have three type of Commission available for Risk Accounts, and they are as follows
Fixed
This will be calculated as Trade Entry i.e. One trade entry the commission will
applied as whole
Calculation: Trade Entry * Commission = Commission Value
This value will be deducted as soon as the trade is placed (in/out)
Fixed Per Lot
Calculation: Volume / Contract Size * Commission = Commission Value
This value will be deducted as soon as the trade is placed (in/out)
Per Mil
Calculation: Trade Volume / Per Million * Commission * Price = Commission Value.
This value will be deducted as soon as the trade is placed (in/out)
Swaps Type Yes Fixed Money
Per Lot,
Point, Price
Percentage
Swap calculation refers to the process of determining the interest or overnight financing
charges associated with holding a trading position overnight. It is commonly applied in
the context of forex trading. The swap amount is calculated as follows:
Fixed Money per Lot: This method involves dividing the trading volume by the
contract size and then multiplying by the swap value (in the Quote Currency) for
short or long positions.
For instance, if the swap long value for EURUSD is -7 and the contract size is
100,000, the overnight swap for a volume of 200,000 long EURUSD would be
calculated as (200,000/100,000) x -7 = USD -14.
Point: Similar to pip calculation, a point value in the Quote Currency considers the
number of decimals in the Symbol and Contract Size. The swap point is calculated
as (swap value) x (net volume) x (1/10^digits) x (conversion quote to deposit
currency).
For example, if the short value of EURGBP is 5 and the traded volume is 100,000,
the swap value would be 5 x 100,000 x 0.00001 x conv GBP to USD = GBP 5. This
value is then converted into the Risk Account currency by multiplying 5 x conv GBP
to USD.
Price Percentage: This method calculates swaps based on a percentage or
interest rate of the traded instrument. The formula is given by Price Percentage =
(current market price) x (net volume) x (swap value / 100.0) x (1 / 360) x (conversion
quote to deposit currency).
Note: Swap is subtracted from the Balance solely upon the partial or complete closure
of a position, contingent on the volume closed. While open positions persist, Swap
remains unrealized, akin to floating Profit/Loss (PL), and exclusively influences Equity.
Contract Size Yes 100,000 The Contract Size of the Symbol. This is mainly used for margin, commission and swap
calculations
Long Value Yes -2, 0.5, 3 The Swap value to be charged for long (buy) overnight positions.
If negative, the value will be deducted from the Risk Account Balance
If positive, the value will be added to the Risk Account Balance
Short Value Yes -2, 0.5, 3 The Swap value to be charged for short (sell) overnight positions.
If negative, the value will be deducted from the Risk Account Balance
If positive, the value will be added to the Risk Account Balance

Delete a Limit Symbol Group
To delete a Limit Symbol Group
1. Click on the “Delete” button next to the desired Limit Symbol Group.
2. To confirm the deletion, type the name of the Limit Symbol Group in the field.
2. Click on the “Delete” button to confirm.
Exporting a Limit Symbol Group
To Export a Limit Symbol Group
1. Select the Limit Symbol Group from the list you wish to export.
2. Click “Export” and select “Export to Excel” or “Export to CSV”
PL Multiplier Yes 0.5, 2 This parameter is only used to adjust the Profit and Loss (PL) in the event of different
PL calculations on the Maker’s side in terms of tick size and tick value.
For instance, if on our side the tick value for one tick size is equivalent to $1 whereas
on the Maker’s side it is equivalent to $2, we could simply put in 2 as PL Multiplier to
ensure that PLs are matching on both ends
Three Day
Swap
Yes WED, FRI The Day of the week on which a three day swap value will be charged for positions
held overnight on that day.
If the value is set to None, then no 3 day swap would be charged, instead the Bridge
would charge Swaps on Saturday and Sunday as well for any position held over the
weekend
Settlement
Time
Yes The Settlement Time of the contract, if any
Description No Symbol description for reference purposes


Uploading a Limit Symbol Group
To Upload a Limit Symbol Group
1. Click on “Upload”
2. Drop the file you want to upload. Alternatively, you can click on “Drop a File”, select the file and click “Open”
3. Click “Upload“ to upload the file or click “Close” to cancel.




```

---

<a id='master-risk-account-md'></a>
### 6. `master-risk-account.md`

```markdown
[🏠 Document Start](..\README.md) / [Taker Risk Filter](README.md) / Master Risk Account

# Master Risk Account

Overview
Master Risk Account can be thought of as a read-only Pool Account containing multiple Risk Accounts. You can link an unlimited number of
Risk Accounts upon creating a Master Risk Account whose trades and account information can be seen in an aggregated view.
Positions and Account information pertaining to different Risk Accounts within the Master Risk Account are shown as aggregated values.
As for history trades and balance transactions, the entries are displayed for all the Risk Accounts underneath.
The Master Risk Account, just like a regular Risk Account, can be linked to a Risk User with a dedicated interface through which you can
view all trading and balance activities pertaining to the Master Risk Account, hence all Risk Accounts underneath.
Note: Master Risk Account can have a read-only User Interface to monitor the Risk Accounts’ activities without having the ability to trade
on behalf of any Risk Account.
In this component, you can view all the Master Accounts defined in the portal in addition to doing the following:
Create a new Master Risk Account: Establish a new Market Risk Account.
Filter and look up a particular Master Risk Account: Search for and identify a particular Market Risk Account.
Configure an existing Master Risk Account: Modify and tailor the settings of a particular Market Risk Account by editing configurable
parameters.
Delete a Master Risk Account: Remove a Master Risk Account rule that is no longer needed.
Export the list of Master Risk Account to an Excel/CSV file: Generate a downloadable file (Excel or CSV) containing the
comprehensive list of Market Risk Account for external reference or documentation purposes.
Create a Master Risk Account
To create a Master Risk Account:
1. Go to Risk Accounts > Master Risk Account > Click on “
Add”
1. Fill out the Wizard as explained below
2. Click on
“Submit” to submit the changes


To modify a Master Risk Account existing configuration:
1. To configure, double-click on Risk Accounts or Description of your desired Master Risk Account.
2. Click the
“Save” button on top to deploy the changes
Note: You cannot edit the name of the existing Master Risk Account.
Delete a Master Risk Account
To delete a Master Risk Account:
1. Click on the
“Trash bin” icon next to desired Master Risk Account
1. To confirm deletion, type the name of the Master Risk Account
2. Click
“Delete” to confirm the deletion
Name The name of the Master Risk Account to be created
Risk Accounts Select the Risk Accounts that you wish to link to the Master
Account. You may select an unlimited number of Risk Accounts
Description A short description for reference purposes
Field Description


Exporting a Market Risk Account
To export a Market Risk Account configuration
1. Filter the desired Market Risk Account Filter rules using the available filters.
2. Click “Export” and select “Export to Excel” or “Export to CSV”




```

---

<a id='taker-risk-filter-md'></a>
### 6. `taker-risk-filter.md`

```markdown
[🏠 Document Start](..\README.md) / [Balance Transaction](README.md) / Taker Risk Filter

# Taker Risk Filter

Overview
Taker Risk Filter allows you to set up filters or rules to link existing risk account(s) using the available filters such as Taker Execution
Model, Liquidity Model, Group, Login, etc.
In this component, you will be able to do the following:
1. Add a New Taker Risk Filter rule: Create and implement a new rule for the Taker Risk Filter.
2. Filter Taker Risk Filter Rules by Different Criteria: Utilize filters to sort and view Taker Risk Filters based on specified criteria.
3. Enable/Disable a Particular Taker Risk Filter Rule: Toggle the active status of a specific Taker Risk Filter rule on or off.
4. Configure a Particular Taker Risk Filter Rule: Modify and tailor the settings of a particular Taker Risk Filter rule by editing
configurable parameters.
5. Delete a Taker Risk Filter Rule: Remove a Taker Risk Filter rule that is no longer needed.
6. Export the List of Taker Risk Filter Rules to an Excel File / CSV File: Generate a downloadable file (Excel or CSV) containing the
comprehensive list of Taker Risk Filter Rules for external reference or documentation purposes.
Creating a Taker Risk Filter
To create a Taker Risk Filter
1. Click the “Add” button on the top right corner

2. Fill out the Wizard. You may refer to the field descriptions hereafter
3. Click “Submit” to submit the changes


Risk Account FIX_RA Name of the risk account to which the filters need to be applied.
Takers Centroid_MT
5,
Centroid_MT
4
Select one or multiple Takers to be included in the filter as source(s) You may select the
Takers from the available list of Takers.
Taker Execution
Models
TEM-1, TEM-
2, Test_TEM
Select one or multiple Taker Execution Models to be included in the filter as source(s) You
may select the Taker Execution Models from the list, separating them with commas.
Liquidity Models LP1_LM Select one or multiple Liquidity Models to be included in the filter as source(s) You may select
the Liquidity Models from the list.
Securities FX, CFD Select one or multiple Securities to be included in the filter as source(s) You may select the
Securities from the list, separating them with commas.
Field Possible
Values
Description

Configuring a Taker Risk Filter
To configure/modify an existing Taker Risk Filter
1. Double-click the desired column(s) in the Taker Risk Filter.
2. You will be presented with a pop-up Window where you can edit and click submit as seen below.
3. Click on “Save” to save the changes.
Deleting a Taker Risk Filter
To delete a Taker Risk Filter
1. Click the “Delete” icon next to the desired Taker API Link configuration
2. Enter the ID in the pop-up window & Click on “Delete” button to confirm the deletion
Exporting a Taker Risk Filter
To export a Taker Risk Filter configuration
1. Filter the desired Taker Risk Filter rules using the available filters.
Symbols EURUSD,
XAUUSD
Select one or multiple Symbols to be included in the filter as source(s) You may select the
Symbols from the list, separating them with commas.
Groups real\vip Name of MT4/MT5 Group for Takers of type MT4/MT5
Logins 0, 100002,
500005
MT4/MT5 Login number for Takers of type MT4/MT5
Default Value = 0 (all logins)
Sides BUY, SELL,
ALL
Select the side of the Order to be included as a filter, such as Buy or Sell. Otherwise, just
select “*” to include all Order sides
Order Types LIMIT,
MARKET
Select the Type of the Order to be included as a filter, such as Market, Limit or Stop.
Otherwise, just select “*” to include all Order types.
Mode ALL, A, B Select the Mode to be included as a filter:
A Book: Only considers A Book trades that are routed to the Maker
B Book: Only considers B Book trades that are internalized in the Centroid Bridge
All: Considers all trades.
Priority 1,2,10 This parameter applies in the event of having overlapping configurations. You can proceed to
set the priority to adjust the rules, On a scale 1-10, rule with priority 10 will be considered first.
Description A short description for reference purposes


2. Click “Export” and select “Export to Excel” or “Export to CSV”




```

---
