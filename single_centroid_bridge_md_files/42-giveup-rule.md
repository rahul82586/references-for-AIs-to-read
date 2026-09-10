# 📁 42-giveup-rule

- **Generated:** 2026-09-10 12:08
- **Total Files:** 1
- **Source:** `C:\Users\DELL\Downloads\backend_code-main (1)\backend_code-main (2)\bridge_manual_md\42-giveup-rule`

---

## 📑 Table of Contents

1. [README.md](#readme-md)

---

## 🌲 Project Structure

```
42-giveup-rule/
└── README.md
```

---

## 📄 Files

<a id='readme-md'></a>
### 1. `README.md`

```markdown
[🏠 Document Start](..\README.md) / Giveup Rule

# Giveup Rule

Overview
Give-up is primarily employed for monitoring your market exposure, including your A Book and B Book exposure within a single MT4/MT5
account. It's important to note that these trades aren't executed in the market. Instead, a Give-up account functions as a presentation
account, aggregating all trades originating from the designated TEM. These accounts can also be referred to as Coverage Accounts.
Within this module, you have the capability to:
Add a new Give-up Rule: Incorporate a new Give-up Rule.
Filter Give-up Rules: Categorize Give-up Rules based on different criteria.
Enable/Disable a Give-up Rule: Manage the active status of a Give-up Rule.
Modify an Existing Give-up Rule: Adjust settings for an existing Give-up Rule.
Remove an Existing Give-up Rule: Delete a specific Give-up Rule.
Export Give-up Rules: Save the list of Give-up Rules to Excel or CSV files.
The Give-up Rule consists of the following components:
Source: Taker(s) and/or a Taker Execution Model(s) whose trades are covered or booked into an MT4/MT5 Account.
Target: MT4/MT5 Taker along with an MT4/MT5 Account within the Taker into which the trades are booked
Configuration Settings: Various parameters based on which the trades are covered.
You may also specify additional parameters to the configuration by adding some macros in the description as explained hereafter.
Create a Give-up Rule
To create a Give-up Rule
1. Click “Add” button to create a new Give-up Rule.
2. Fill out the Wizard. You may refer to the field descriptions below
3. Click “Submit” to submit the changes


ID A unique ID number for the configured rule
Taker The source Taker(s) You may select one or multiple Takers from the list or type a pattern manually by ticking the
Pattern tick-box
Note: You may use wildcards (*) for all and negations (!) for exclusion when typing a pattern
Taker
Execution
Model
This is source TEM, meaning all the trades executed with this TEM shall be executed to the target TEM/Account as
well.
Note: You may use wildcards (*) for all and negations (!) for exclusion when typing a pattern
Securities If you specify any Security here, then only those symbols under that security are entitled to be executed from the
Master account to the Slave/Target account.
Symbols The Symbol(s) whose trades will be booked into the Coverage Account. If a particular Symbol is chosen within a Give-
up Rule, only trades pertaining to the chosen Symbol will be covered, trades whose Symbols are not specified will be
overlooked (not covered) unless they belong to a chosen Security in the Securities parameter above.
You may select one or multiple Symbols from the list or type a pattern manually by ticking the Pattern tickbox.
Note: You may use wildcards (*) for all and negations (!) for exclusion when typing a pattern
Side Default Value: *(all) However, broker can further change the settings to either Buy or Sell trades to be executed from
the Master to Slave account.
Source Ext
Group
It is relevant to Takers of type MT4 or MT5 and allows to specify a Source MT4/MT5 Group where only trades
belonging to MT4/MT5 Accounts under those Groups will be covered.
Note: You may enter multiple Groups comma separated or use a pattern with wildcards (*) for all and negations (!) for
exclusion.
Source Ext
Login
It is relevant to Takers of type MT4 or MT5 and allows to specify a sole Source MT4/MT5 Account whose trades will be
covered.
Note: You may select One MT4/MT5 Account only at a time.
Target Taker Defines the MT4/MT5 Taker which contains the Coverage Account into which the trades will be copied.
Field Description

You can select one Taker from the list of MT4/MT5 Takers that are configured in the Centroid Bridge.
Target Login The MT4/MT5 Login Number of the Coverage Account into which the trades pertaining to the configured Give-up Rule
will be booked.
Note: You may select One Target Login only at a time.
Original
Centroid
Markup
Indicates whether the covered trade price will include the Markup defined on the Centroid Bridge. Basically the MM
assigned for the Master / Source TEM.
Ticked, the price of the covered trade will include the markup same as Master / Source.
Unticked, the price of the covered trade will not include any markup, hence it will be covered with the raw price just
in line with the way it’s booked on the Maker’s side.
Markup
Model
Allows to add additional markups to the booked price in case you wish to show a higher price. This can be done by
selecting an existing Markup Model or creating a new one for that purpose in which you can define the additional
Markups on a per Symbol basis.
This Additional Markup Model is totally independent and has no relation to the Source / Master TEM, just adding the
markup to the slave account when booking the trade.
Ratio A percentage Ratio at which the trade will be covered. You can select a percentage from the dropdown list which
contains predefined values or type in the value manually by ticking “Custom” which turns it into a free text.
Same Direction: For same direction trading we have options available from 10% to 100% volume ratio, 100 means
the exact same volume and same direction.
Reverse Direction: For reverse direction trading we have options available from 10% to 100% volume reverse
ration, 100 means exact same volume and reverse direction.
Custom: If the available option is not satisfying your business requirements, we have an option to create your own
percentage and decided same or reverse direction.
Example: For same direction but double the quantity, just check Custom and write 200%
For reverse direction and double the quantity, juts check Custom and write -200%, ( - ) means reverse.
Mode Specifies which flow to cover:
A Book: Only covers A Book trades that are routed to the Maker
B Book: Only covers B Book trades that are internalized in the Centroid Bridge
All: Copies all trades, A and B Book
Maker Maker option is useful to track down your A book positions sent to that specific Maker.
You can select one or multiple Makers from the drop down list, however the list is only available when your copying
mode is A book, as it defines you want to cover only A book position into the slave account and track your A book
exposure.
Stl Mode Defines how trades are covered
The configuration only works when using an MT4 platform.
FIFO: Covered trades are netted out on a First In First Out basis in the coverage account where a trade of opposite
direction would offset the first trade that came in. In the FIFO mode, the coverage account cannot have two trades
of opposite sides for the same Symbol simultaneously.
Hedge: The coverage account allows hedging where we can have trades of different directions. By using this
mode, there will be no offsetting or trade closing.
Priority This parameter applies in the event of having overlapping configurations where a Give-up Rule with a higher priority
supersedes other overlapping Rules with lower priorities.
You may refer to the examples below in the case studies to understand how priority works

To Configure/Modify a newly added/existing Giveup Rule
1. To edit a desired parameter, simply double-click on it. Parameters are modified based on the column, with options for entering values
manually or selecting from a dropdown list. For parameters involving multiple values or custom patterns, a pop-up window will appear,
allowing you to edit the value(s) and click "Submit," as illustrated below.
2. After editing the desired fields (which are highlighted), click the "Save" button to implement and deploy the changes.
Symbol
Format
Specifies in what Symbol format the trade will be covered in the coverage account. You may choose one of the two available formats below and even add a string or suffix that will
be added to the end of the Symbol.
#ts#: Taker Symbols are used when the Master and the Slave account both the accounts have access to the same set of symbols on the Trading platform i.e. MT4/MT5.
Example: Master is placing a trade with EURUSD@ the same EURUSD@ is available on the Slave account on the MT4/MT5.
#us#: Universal Symbols are used when the Master and the Slave account both the accounts have access to a different set of symbols on the Trading platform i.e. MT4/MT5.
Example: Master is placing a trade with EURUSD@ but this symbol is not available for the slave account on the Trading platform i.e. MT4/MT5 in this case you will proceed to
do the below configuration:
Note: It is important to ensure that the Target Login has access to the specified Taker Format in the MT4/MT5 Server. Otherwise, trade will not be booked
Description It can be used as a free text for reference or use the following macros for additional customizations:
#mm#: Adds MT4 Group Markups to the price
#vvs#: Used for % ratio and validates the AMin and AStep parameters on the source TEM prior to booking the
Give-up trade. If volume is less than Amin, the trade would not be booked. If Volume is not a multiple of AStep, only
the multiple AStep volume would be booked, the remaining would be discarded.
#vv#: Used for % ratio and validates the Min Volume parameter on the source TEM prior to booking the Give-up
trade. If volume is less than Min Volume, the trade would not be booked.
#vsym#: Books non confirmed trades that could result due to error in Symbol configuration
#extm#: Added source external markup (MT4/MT5 Group Markup) to target Give-up Order
Enable Indicates whether the Give-up Rule is enabled or disabled
If ticked, the Give-up Rule is enabled upon creation
If unticked, the Give-up Rule is disabled upon creation


3. The user also has the option to click on the "Revert All" button to return to the previous values of the selected parameters.
MetaTrader 5 (MT5) Giveup Rule Configuration
Note: While setting up the Give-up Rule, please read the MT5 Gateway Manual to configure the settings on the MT5 Level, if this
configuration is not done/completed on MT5, the trades won’t be copied from Master to the Slave Account.
Delete a Give-up Rule
To delete a Giveup Rule
1. Click the “Delete” icon next to the desired Give-up Rule
2. To confirm the Deletion, type in the specified text.
3. Click the “Delete” button in the pop-up window to confirm the deletion
Exporting a Giveup Rule
To Export a Giveup Rule
1. Filter the desired ID from the list to be able to export a specific Giveup Rule
2. Click “Export” and select “Export to Excel” or “Export to CSV”


Case Studies
In the below example, you can see four different Give-up Rules, some of which are overlapping rules with different configurations. For the
sake of clarity, we have categorized the four rules into two sets in which we have used the priority to differentiate, as explained hereafter.
Scenario 1:
The initial set consists of two rules that overlap, requiring us to assign distinct priorities. Both rules make use of the same Coverage
Account, which is 5002, but they implement different coverage rules.
In the first rule, our selection is limited to FX Security, and when it comes to covering trades in the Coverage Account 5002, we employ the
Symbol Format #ts# (Taker Symbol).
In contrast, the second rule encompasses the remaining securities, including Equities and CFDs. For covering trades in the Coverage
Account 5002, we use the Symbol Format #us# (Symbols).
The assignment of different priorities to each rule allows the Centroid Bridge to differentiate between them when booking trades.
The coverage process is illustrated in the diagram below.
Scenario 2:
The second set includes two rules that also overlap, necessitating the use of distinct priorities. However, in this case, the rules involve
different Coverage Accounts, specifically 8000 and 8001. Additionally, the second rule involves the application of additional markups on top
of the booking price for the Coverage Account.
In the first rule, our focus is on Centroid2_MT5, exclusively handling all trades associated with that Taker and booking them into Coverage
Account 8000.
In the second rule, we override the first rule by selecting a specific Taker Execution Model, tem_abook, within Centroid2_MT5. We direct
trades related to the Taker Execution Model tem_abook to a separate Coverage Account, which is 8001. Furthermore, we apply extra
markups to the final price, as defined in Markup Model 2pts_mm. To accomplish this, we assign a higher priority level, 2, to differentiate
orders originating from the Taker Execution tem_abook.
In summary, the Centroid Bridge scrutinizes all trades originating from Centroid2_MT5. If they are associated with the tem_abook Taker
Execution Model, these trades are booked into Coverage Account 8001, with the addition of the markups specified in Markup Model


2pts_mm. If the trades from Centroid2_MT5 are linked to a different Taker Execution Model (other than tem_abook), they are booked into
Coverage Account 8000 without any extra markups. The coverage process is visually represented in the diagram below.
FAQ
Why haven't the trades for the slave account been executed?
I cannot see trades on the MT5 account even though they are visible on the bridge for the slave account. What could be causing this discrepancy?
Can I use multiple MT5 accounts as the Source Ext Login for a specific rule?
What does a '0' value indicate under Source Ext Login?
Can I use multiple MT5 accounts as the Target Account for a specific rule?
To validate the accuracy of the rule, clients can review the filters applied during its creation. Any potential issues may arise from TEM
and External Filters or Master and Target Symbol (suffix), if any. For further assistance, feel free to contact Support via Skype or Slack.
The issue might be related to missing MT5 settings. Refer to the Gateway Manual for specific guidance on these settings.
You cannot use more than one MT5 account as the Source Ext Login for a specific rule.
Source Ext Login '0' signifies all accounts
You cannot use more than one MT5 account as the Target login for a specific rule.


```

---
