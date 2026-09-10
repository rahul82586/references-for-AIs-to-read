# 📁 48-risk-management

- **Generated:** 2026-09-10 12:09
- **Total Files:** 3
- **Source:** `C:\Users\DELL\Downloads\backend_code-main (1)\backend_code-main (2)\bridge_manual_md\48-risk-management`

---

## 📑 Table of Contents

1. [README.md](#readme-md)
2. [concentration-per-login.md](#concentration-per-login-md)
3. [hedge-trade-rule.md](#hedge-trade-rule-md)

---

## 🌲 Project Structure

```
48-risk-management/
├── concentration-per-login.md
├── hedge-trade-rule.md
└── README.md
```

---

## 📄 Files

<a id='readme-md'></a>
### 3. `README.md`

```markdown
[🏠 Document Start](..\README.md) / Risk Management

# Risk Management

The Risk Management Module allows to create and configure Market Impact and Concentration Per Login. Upon clicking the “Risk
Management” button on the left-hand side menu, it expands to show the different components underneath which are explained in greater
detail hereunder.




```

---

<a id='concentration-per-login-md'></a>
### 3. `concentration-per-login.md`

```markdown
[🏠 Document Start](..\README.md) / [Risk Management](README.md) / Concentration Per Login

# Concentration Per Login

Overview
Concentration Per Login facilitates exposure management, this feature allows the brokers to customize exposure settings for every
MT4/MT5 login at the symbol level. It also assists in crucial decision-making, by offering the option to Manage or Limit the allowed
exposure in terms of traded volume.
Note: Concentration per login works only with BBook Trades.
Manage (By Default): When referring to ‘Manage,' it entails that if the MT4/MT5 Login surpasses the exposure set at the symbol level, all
incoming trades for that symbol should be redirected to the Maker.
Limit (Macro Rule): When referring to 'Limit,' it means that if the MT4/MT5 Login surpasses the exposure set at the symbol level, all
incoming trades for that symbol should be automatically 'Rejected’.
* Macro Rule → #reject#
Within this module, you have the capability to:
Add a New Concentration Per Login Rule: Create and implement a new rule for the Concentration Per Login functionality.
Filter Concentration Per Login Rules by Different Criteria: Utilize filters to sort and view Concentration Per Login rules based on
specified criteria.
Enable/Disable a Particular Concentration Per Login Rule: Toggle the active status of a specific Concentration Per Login rule on or
off.
Configure a Particular Concentration Per Login Rule: Modify and tailor the settings of a particular Concentration Per Login rule by
editing configurable parameters.
Delete a Concentration Per Login Rule: Remove a Concentration Per Login rule that is no longer needed.
Export the List of Concentration Per Login Rules to an Excel File / CSV File: Generate a downloadable file (Excel or CSV)
containing the comprehensive list of Concentration Per Login Rules for external reference or documentation purposes.
Creating a Concentration Per Login
To create a Concentration Per Login
1. Locate Concentration Per Login and then click the “Add” button


2. Fill out the Wizard. You may refer to the field descriptions below
3. Click “Submit” to submit the changes
ID A unique ID number for the configured rule
Taker The source Taker(s) You may select one or multiple Takers from the list or type a pattern manually by ticking the
Pattern tick-box
Note: You may use wildcards (*) for all and negations (!) for exclusion when typing a pattern
TEM Trades executed with this source TEM will adhere to the exposure rule, additionally following Source Login and
Group Filter criteria.
Securities Specifying a security here indicates that only the symbols falling under this security are eligible to adhere to the
concentration per login rule, either by managing or limiting the exposure.
Symbols The exposure limit will be exclusively applied to the symbols specified here. If no symbols are selected, it implies
that all symbols within the chosen security will adhere to the exposure rule.
Sides Default Value: * [meaning all] However, broker can further change the settings to either Buy or Sell trades.
Ord Types The additional filter for order types enables you to specify whether you want the exposure rule applied to market
orders, limit orders, stop orders, or all (*).
Source
ExtLogin
This parameter allows you to enter a specific MT4/MT5 Login number.
Note: You can add only one account at a time.
Note: Entering '0' means that all accounts will adhere to this exposure rule.
Source
ExtGroup
This parameter enables you to enter a specific MT4/MT5 Group to adhere to the exposure rule. Note: You can add
multiple groups by using a comma (',').
Limit This parameter empowers you to establish the exposure for the selected filters (Account, Symbol, Group, TEM). The
limit is specified in volumes.
Example:
Symbol: XAUUSD
MT5 Login: 12012
Limit: 100,000 volumes
In the given example, if the account 12012 surpasses the set exposure limit, subsequent incoming trades will be
either redirected to the Maker or rejected, depending on the specified rule.
Adjustment
Value
When set to 1, the purpose is to trigger a flag, allowing fractional volume to be counted towards 'B,' even if it
exceeds the limit for A-book routing.
Field Description

To configure a Concentration Per Login
1. Select the desired Concentration Per the Login rule.
2. Configure the desired fields.
3. Click the “Save” button on top to deploy the changes.
Priority This parameter applies in the event of having overlapping configurations. You can proceed to set the priority to
adjust the rules, On a scale 1-10, rule with priority 10 will be considered first.
Description This is the section where you can determine whether you want to manage the exposure or limit the exposure.
If you choose option 1, which is 'Manage,' you can add any value or text in the description box for reference purposes only.
On the other hand, if you choose option 2, which is 'Limit,' you must add a macro rule in the description box, and the value should be '#reject#.
By adding the macro rule, you have specified that if any filtered account/group/symbol/TEM exceeds the set exposure, subsequent incoming trades will be rejected.
Enable Indicates whether the Rule is enabled or disabled
If ticked, the Rule is enabled
If unticked, the Rule is disabled, hence no is applied
ID No 100, 1, 12 A unique ID number for the configured rule
Taker Yes Centroid_MT
5
The source Taker(s) You may select one or multiple Takers from the list or type a pattern
manually by ticking the Pattern tick-box
Note: You may use wildcards (*) for all and negations (!) for exclusion when typing a pattern
TEM Yes TEM-1 Trades executed with this source TEM will adhere to the exposure rule, additionally following
Source Login and Group Filter criteria.
Securities Yes CFD Specifying a security here indicates that only the symbols falling under this security are
eligible to adhere to the concentration per login rule, either by managing or limiting the
exposure.
Symbols Yes XAUUSD The exposure limit will be exclusively applied to the symbols specified here. If no symbols
are selected, it implies that all symbols within the chosen security will adhere to the exposure
rule.
Sides Yes *, Buy, Sell Default Value: * [meaning all] However, broker can further change the settings to either Buy
or Sell trades.
Ord Types Yes Market, Limit The additional filter for order types enables you to specify whether you want the exposure
rule applied to market orders, limit orders, stop orders, or all (*).
Field Editab
le
Possible
Values
Description

To delete a Concentration Per Login
1. Click the “Delete” icon next to the desired Concentration Per Login.
2. To confirm the Deletion, type in the specified text.
3. Click the “Delete” button in the pop-up window to confirm the deletion.
Source
ExtLogin
Yes 10012,
10013
This parameter allows you to enter a specific MT4/MT5 Login number.
Note: You can add only one account at a time.
Note: Entering '0' means that all accounts will adhere to this exposure rule.
Source
ExtGroup
Yes Testonly\A-
10
This parameter enables you to enter a specific MT4/MT5 Group to adhere to the exposure
rule. Note: You can add multiple groups by using a comma (',').
Limit Yes 100000,
350000
This parameter empowers you to establish the exposure for the selected filters (Account,
Symbol, Group, TEM). The limit is specified in volumes.
Example:
Symbol: XAUUSD
MT5 Login: 12012
Limit: 100,000 volumes
In the given example, if the account 12012 surpasses the set exposure limit, subsequent
incoming trades will be either redirected to the Maker or rejected, depending on the
specified rule.
Adjustment
Value
Yes 1 When set to 1, the purpose is to trigger a flag, allowing fractional volume to be counted
towards 'B,' even if it exceeds the limit for A-book routing.
Priority Yes 1, 2, 5, 10 This parameter applies in the event of having overlapping configurations. You can proceed to
set the priority to adjust the rules, On a scale 1-10, rule with priority 10 will be considered
first.
Description Yes This is the section where you can determine whether you want to manage the exposure or limit the exposure.
If you choose option 1, which is 'Manage,' you can add any value or text in the description box for reference purposes only.
On the other hand, if you choose option 2, which is 'Limit,' you must add a macro rule in the description box, and the value should be
'#reject#.
By adding the macro rule, you have specified that if any filtered account/group/symbol/TEM exceeds the set exposure, subsequent incoming
trades will be rejected.
Enable Yes Enabled,
Disabled
Indicates whether the Rule is enabled or disabled
If ticked, the Rule is enabled
If unticked, the Rule is disabled, hence no is applied


To Export a Concentration Per Login
1. Click “Export” and select “Export to Excel” or “Export to CSV”.




```

---

<a id='hedge-trade-rule-md'></a>
### 3. `hedge-trade-rule.md`

```markdown
[🏠 Document Start](..\README.md) / [Concentration Per Login](README.md) / Hedge Trade Rule

# Hedge Trade Rule

Overview
The Hedge Trade Rule allows you to create rules that automatically copy or hedge a trade with a customizable delay specified in
milliseconds to optimize timing and potentially minimize slippage. It has a refined mechanism for securing a better price while maintaining
control over the acceptable deviation from the ideal price point, thereby managing risk more effectively. It will open new positions primarily
for hedging risks, based on predefined conditions such as Better Points, Worse Points, and Delay.
In this component, you will be able to do the following:
1. Create a new Hedge Trade Rule
2. Filter the currently configured Hedge Trade Rule by different criteria
3. Enable/Disable a particular Rule
4. View and edit a currently configured Hedge Trade Rule
5. Delete a Hedge Trade Rule
6. Click “Export” and select “Export to Excel” or “Export to CSV”
Creating a Hedge Trade Rule
To create a Hedge Trade Rule
1. Click “Add” button to create a new Hedge Trade Rule
2. Fill out the Wizard. You may refer to the field descriptions below
3. Click “Submit” to submit the changes



ID A unique ID number for the configured rule
Takers The source Taker(s) You may select one or multiple Takers from the list or type a pattern manually by ticking
the Pattern tick-box
Note: You may use wildcards (*) for all and negations (!) for exclusion when typing a pattern
Taker Execution
Models
This is source TEM, meaning all the trades executed with this TEM shall be executed to the Slave/Target
account.
Note: You may use wildcards (*) for all and negations (!) for exclusion when typing a pattern
Liquidity Models Specific Liquidity Model(s) assigned to the TEM. You may select one or multiple LM(s) from the list or type a
pattern manually by ticking the Pattern tick-box.
Note: You may use wildcards (*) for all and negations (!) for exclusion when typing a pattern
Securities If you specify any Security here, then only those symbols [under this security] are entitled to be executed
from the Master account to the Slave/Target account.
Groups You may select one or multiple MT4/MT5 Groups by typing in the name of the Group(s). If particular Groups
are selected, only Logins belonging to these Groups will have their trades executed to the target account.
Note: You may use wildcards (*) for all and negations (!) for exclusion when typing a pattern
Symbols If you specify any Symbol here, then only those symbols are entitled to be executed from the Master account
to the Slave/Target account.
Note: By default, all Symbols are selected. You may select particular ones if you wish to restrict the rule to
particular Symbols
Side Default Value: * [meaning all] However, broker can further change the settings to either Buy or Sell trades to
be executed from the Master to Slave account.
Master Login Select a particular MT4/MT5 Login whose trades will be used for execution.
Note: This is a very specific rule whereby the copy will be applicable to the selected Login only.
Note: It is important to ensure that the Login already satisfies the other criteria [meaning it is targeting the
source TEM]. Otherwise, the copy rule would not work
Target Taker Select one Target Taker of type MT4 or MT5. This could be the same Taker or even a different Taker within
the same Centroid Bridge.
Note: If no Target Taker is selected, the Centroid Bridge will use the same Taker source for target as well
Target Taker
Execution Model
Select the Target Taker Execution Model, this will define where the target or slave trades will be executed.
Note: If no Target TEM is selected please note it will use the Source TEM as Target TEM, and all the trades
will follow the master TEM for execution.
Target Login Specify an MT4/MT5 Login into which the copied trades will be booked. This is an optional field that helps
keep track of all copied trades pertaining to a particular rule in one single coverage account
Ratio A component to decide the direction and trade volume to be executed from the master to the slave account.
Positive: executes trades in the same direction [If 1, then same volume, if 2 it will start multiplying but in
same direction]
Negative: copies trades in the opposite direction (reverse copy) [If 1, then same volume, if 2 it will start
multiplying but in reverse direction]
Copy Mode Specifies which flow to copy:
All: copies all trades, A and B Book
Field Description

Notes:
Delay, Better Points, and Worse Points can be combined in a single rule. The trigger point will be whichever condition is met first.
Better and Worse Points cannot be configured with a Negative Ratio
The triggered Slave or Hedge trade awaiting execution will be displayed under Monitoring > Hedge Trade Order.
Configure Hedge Trade Rule
To configure or modify an existing Hedge Trade Rule
1. Select the desired Hedge Trade Rule
2. Configure the desired fields
3. Click the “Save” button on top to deploy the changes
A: copies A Book trades only
B: copies B Book trades only
Priority This parameter applies in the event of having overlapping configurations. You can proceed to set the priority
to adjust the rules, On a scale 1-10, rule with priority 10 will be considered first.
Symbol Format Specifies in what Symbol format the trade will be booked in the Target Login, if Target Login is selected. You may choose one of the two available formats below and
even add a string or suffix that will be added to the end of the Symbol.
#ts#: Taker Symbols are used when the Master and the Slave account both the accounts have access to the same set of symbols on the Trading platform i.e.
MT4/MT5.
Example: Master is placing a trade with EURUSD@ the same EURUSD@ is available on the Slave account on the MT4/MT5.
#us#: Universal Symbols are used when the Master and the Slave account both the accounts have access to a different set of symbols on the Trading platform
i.e. MT4/MT5.
Example: Master is placing a trade with EURUSD@ but this symbol is not available for the slave account on the Trading platform i.e. MT4/MT5 in this case you
will proceed to do the below configuration:
Note: It is important to ensure that the Target Login has access to the specified Taker Format in the MT4/MT5 Server. Otherwise, trade will not be booked
Delay(ms) / Max
Waiting
The delay in ms after which the slave or hedge trade will be triggered after the execution of the Master trade.
Send Execution The Slave or Hedge Trade will be copied or covered to the Target Login after execution.
Always STP The Slave or Hedge Trade will be sent to the Maker regardless of the TEM B-Book percentage.
Better Points The extra points added or deducted on the Master trade's executed price for the Slave or Hedge trade to
execute at a better price.
In other words, the take-profit points at which the slave trade must be triggered for execution.
Worse Points The extra points added or deducted to the Master trade's price to prevent it from executing at a worse price.
In other words, the stop-loss points at which the slave trade must be triggered to avoid further losses.
Description A short description for reference purposes
Enable Indicates whether the Trade Copier rule is enabled or disabled
If ticked, the Trade Copier rule is enabled upon creation
If unticked, the Trade Copier rule is disabled upon creation, hence no trades will be copied via this rule


To delete a Hedge Trade Rule
1. Click the “Delete” icon next to the desired Hedge Trade Rule
2. To confirm deletion, type the ID of the Hedge Trade Rule in the field.
3. Click on the "Delete" button to confirm deletion.

Exporting a Hedge Trade Rule
1. Filter the desired Hedge Trade Rule(s) using the available filters.
2. Click “Export” and select “Export to Excel” or “Export to CSV”
Case Studies:
Case 1. Configuring the Better Points Only
In this case, only the better points are configured with a value of 5.
Outcome: The Slave/Hedge trade of BUY side will be triggered for execution once the Market Price reaches 1.00005 following the
execution of the Master trade at 1.00010.
Case 2. Configuring the Worse Points Only
In this case, only the Worse Points are configured with a value of 5.


Outcome: The Slave/Hedge trade of BUY side will be triggered for execution once the Market Price reaches 1.00020 following the
execution of the Master trade at 1.00015.
Case 3. Configuring the Delay/Max Waiting Only
In this case, only the Delay(ms) / Max Waiting is configured with a value of 5000 ms.
Outcome: The Slave/Hedge trade will be triggered for execution after a delay of 5000ms following the execution of the Master trade.
Case 4. Configuring the Better Points and Delay
In this case, Better Points and Delay are configured.
Outcome: There are two possible outcomes in this situation, the slave trade will be triggered for execution if the better points are reached
first; otherwise, it will be triggered after the delay.
Case 5. Configuring the Worse Points and Delay
In this case, Worse Points and Delay are configured.
Outcome: There are two possible outcomes in this situation, the slave trade will be triggered for execution if the worse points are reached
first; otherwise, it will be triggered after the delay.
Case 6. Configuring the Worse Points and Better Points
In this case, Worse Points and Better Points are configured.
Outcome: There are two possible outcomes in this situation, the slave trade will be triggered for execution if the worse points are reached
first; otherwise, it will be triggered once the better points are met.
Case 7. Configuring the Worse Points, Better Points and Delay
In this case, Worse Points, Better Points and Delay are configured,
Outcome: There are three possible outcomes:


1. If the worse points are reached first, the slave trade will trigger for execution.
2. Else if the better points are reached first, the slave trade will trigger for execution.
3. Else, if neither of the above conditions are met, the slave trade will trigger for execution after the Delay.
The trigger point will be whichever condition is met first.



```

---
