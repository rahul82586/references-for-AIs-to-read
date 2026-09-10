# 📁 41-trade-copier

- **Generated:** 2026-09-10 12:08
- **Total Files:** 1
- **Source:** `C:\Users\DELL\Downloads\backend_code-main (1)\backend_code-main (2)\bridge_manual_md\41-trade-copier`

---

## 📑 Table of Contents

1. [README.md](#readme-md)

---

## 🌲 Project Structure

```
41-trade-copier/
└── README.md
```

---

## 📄 Files

<a id='readme-md'></a>
### 1. `README.md`

```markdown
[🏠 Document Start](..\README.md) / Trade Copier

# Trade Copier

Overview
Trade Copier allows you to execute the Trade from the Master Account to the Target / Slave Account. Trade Copier has different ways to
execute the slave trade, including in the same direction or reverse. It also allows for the adjustment of slave trade volumes, allowing for
increasing or decreasing as required [depending on the Ratio Configuration].
The rules are divided into source and target where the source specifies the accounts to be executed and the target specifies where and
how to execute the trades.
Direct/Reverse Trade Copier
Within this component, you'll have the capability to perform the following actions
1. Add a New Trade Copier Rule: Create and implement a new rule for the Trade Copier functionality.
2. Filter Trade Copier Rules by Different Criteria: Utilize filters to sort and view Trade Copier rules based on specified criteria.
3. Enable/Disable a Particular Trade Copier Rule: Toggle the active status of a specific Trade Copier rule on or off.
4. Configure a Particular Trade Copier Rule: Modify and tailor the settings of a particular Trade Copier rule by editing configurable
parameters.
5. Delete a Trade Copier Rule: Remove a Trade Copier rule that is no longer needed.
6. Export the List of Trade Copier Rules to an Excel File / CSV File: Generate a downloadable file (Excel or CSV) containing the
comprehensive list of Trade Copier Rules for external reference or documentation purposes.
As stated above, you may configure a direct copy rule to copy exactly the same trade or a reverse copy that opens the opposite side of
the trade.
Create a Direct/Reverse Trade Copier
To create a new Trade Copier Rule
1. Click “Add” to create a new Trade Copier Rule.
2. Fill out the wizard with all the required fields, you may refer to the field descriptions hereafter
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
Field Description

To configure or modify an existing Trade Copier rule
1. Select the desired Trade Copier rule
2. Configure the desired fields
3. Click the “Save” button on top to deploy the changes
MetaTrader 5 (MT5) Trade Copier Configuration
Note: While setting up the Trade Copier Rule, please read the MT5 Gateway Manual to configure the settings on the MT5 Level, if this
configuration is not done/completed on MT5, the trades won’t be copied from Master to the Slave Account.
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
Enable Indicates whether the Trade Copier rule is enabled or disabled
If ticked, the Trade Copier rule is enabled upon creation
If unticked, the Trade Copier rule is disabled upon creation, hence no trades will be copied via this rule


To delete a Trade Copier rule
1. Click the “Delete” icon next to the desired Trade Copier rule
2. Enter the ID in the pop-up window & Click on “Delete” button to confirm the deletion
Exporting a Trade Copier Rule
To Export a Trade Copier Rule
1. Filter the desired Trade Copier Rule(s) using the available filters.
2. Click “Export” and select “Export to Excel” or “Export to CSV”
FAQ
Why haven't the trades for the slave account been executed?
I cannot see trades on the MT5 account even though they are visible on the bridge for the slave account. What could be causing this discrepancy?
Can I use multiple MT5 accounts as the Master Account for a specific rule?
What does a '0' value indicate under Master Login?
Can I use multiple MT5 accounts as the Target Account for a specific rule?

To validate the accuracy of the rule, clients can review the filters applied during its creation. Any potential issues may arise from TEM
and External Filters or Master and Target Symbol (suffix), if any. For further assistance, feel free to contact Support via Skype or Slack.
The issue might be related to missing MT5 settings. Refer to the Gateway Manual for specific guidance on these settings.
You cannot use more than one MT5 account as the Master login for a specific rule.
Master Login '0' signifies all accounts
You cannot use more than one MT5 account as the Target login for a specific rule.


```

---
