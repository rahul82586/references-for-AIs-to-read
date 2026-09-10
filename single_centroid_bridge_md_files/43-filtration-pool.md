# 📁 43-filtration-pool

- **Generated:** 2026-09-10 12:09
- **Total Files:** 1
- **Source:** `C:\Users\DELL\Downloads\backend_code-main (1)\backend_code-main (2)\bridge_manual_md\43-filtration-pool`

---

## 📑 Table of Contents

1. [README.md](#readme-md)

---

## 🌲 Project Structure

```
43-filtration-pool/
└── README.md
```

---

## 📄 Files

<a id='readme-md'></a>
### 1. `README.md`

```markdown
[🏠 Document Start](..\README.md) / Filtration Pool

# Filtration Pool

Overview
The Filtration Pool module is designed to filter out incorrect or suspicious prices that could result from an error on the Maker’s side in order
to protect Brokers from spiked prices that could lead to a detrimental impact to the clients.
Pools can be constructed of different participants (Makers) whose average prices will be used as a benchmark against which each
incoming tick will be compared and filtered, through a filtering mechanism that utilizes different filtration parameters, before the bridge
decides whether to allow it in or not.
The mechanism used to filter prices uses a recursive methodology whereby each time a Maker’s tick price is excluded, the bridge would
run the filtration all over again on the remaining Makers for the next tick and keeps doing so if a suspicious price comes in until there are
only two Makers left in the Pool.
Different filtration rules can be created with different priorities for different Securities and/or Symbols.
Note: The Filtration Rule functionality runs in the background and can be enabled and disabled at the Level of Liquidity Model on a per
Symbol basis based on the value used in the Filter Factor column, which is explained in detail in the Liquidity Model section.
Within this module, you have the capability to:
Create a new Filtration Pool: Establish a new Filtration Pool.
Filter Filtration Pools: Categorize Filtration Pools based on different criteria.
Enable/Disable a Filtration Pool: Manage the active status of a Filtration Pool.
Edit an Existing Filtration Pool: Modify an existing Filtration Pool by changing configurable parameters.
Delete an Existing Filtration Pool: Remove a specific Filtration Pool.
Export Filtration Pools: Save the list of Filtration Pools to an Excel/CSV file.
Creating a Filtration Pool
To create a Filtration Pool
1. On the Filtration Pool and then click the “Add” button.
2. Fill out the Wizard. You may refer to the field descriptions below.
3. Click “Submit” to submit the changes.


ID A unique ID number for the configured rule
Makers One or multiple Maker(s) whose prices will be compared against any incoming tick prior to allowing the tick into the
bridge
Note: “*” implies that all Makers are selected
Securities One or multiple Security(ies) to which the filtering will apply
Note: “*” implies that all Securities are selected
Symbols One or multiple Symbol(s) to which the filtering will apply
Note: “*” implies that all Symbols are selected
Unit A Unit is equivalent to 10 points (1 pip for FX), the digit before the last digit of a Symbol. The Unit is used as a
measurement to be applied as an accepted tick price variance from the benchmark price of Makers making up the
Pool
Example: 1 Unit of a 5-digit EURUSD Symbol is equivalent to 10 points or 0.00010 1 Unit of a 2-digit DAX Symbol is
equivalent to 10 points
or
0.10 3 Units of a 3 digit Gold Symbol is equivalent to 30 points or 0.030
Factor A multiplier by which you can further increase or decrease the Unit and thus the accepted variance
Note: This value can be overridden at the level of Liquidity Model
Priority This parameter applies in the event of overlapping configurations whereby a Filtration Rule with a higher priority
supersedes other overlapping Rules with lower priorities.
Example: You may have a global filtration rule and you may want to apply the filtration differently to a particular
Symbol. In that case, you can have the global rule configured to include all Symbols and set its priority to 1 and then
configure another rule in which you select a particular Symbol and set its priority to 2. In that case, whenever a tick
for that Symbol comes in, filtration rule 2 will be applied since it has a higher priority
Accepted
Repeatance
This is relevant in case the Filtration Pool is made up of one Maker only. It defines how many times a price can be
filtered out and discarded in the event of having consecutive suspicious prices coming in. When the number of
Accepted Repeatance is exceeded, the bridge would let the suspicious price in. For instance, if the Accepted
Repeatance is set to 5, then the bridge would let a suspicious price in after the 5th consecutive tick.
Enable Indicates whether the Filtration Rule is enabled or disabled
If ticked, the Filtration Rule is enabled
If unticked, the Filtration Rule is disabled, hence no filtration is applied
Description A short description for reference purposes
Field Description

To configure a Filtration Pool
1. Select the desired Filtration Pool rule
2. Configure the desired fields
3. Click the “Save” button on top to deploy the changes
ID No 1,2,3 A unique ID number for the configured rule
Makers Yes LP1, PB1 One or multiple Maker(s) whose prices will be compared against any incoming tick prior to
allowing the tick into the bridge
Note: “*” implies that all Makers are selected
Securities Yes FX, CFDs One or multiple Security(ies) to which the filtering will apply
Note: “*” implies that all Securities are selected
Symbols No EURUSD,
XAUUSD
One or multiple Symbol(s) to which the filtering will apply
Note: “*” implies that all Symbols are selected
Unit Yes 1,2,3 A Unit is equivalent to 10 points (1 pip for FX), the digit before the last digit of a Symbol. The
Unit is used as a measurement to be applied as an accepted tick price variance from the
benchmark price of Makers making up the Pool
Example: 1 Unit of a 5-digit EURUSD Symbol is equivalent to 10 points or 0.00010 1 Unit of a
2-digit DAX Symbol is equivalent to 10 points
or
0.10 3 Units of a 3 digit Gold Symbol is equivalent to 30 points or 0.030
Factor Yes 1, 10, 25,
100
A multiplier by which you can further increase or decrease the Unit and thus the accepted
variance
Note: This value can be overridden at the level of Liquidity Model
Priority Yes 1,2,3 This parameter applies in the event of overlapping configurations whereby a Filtration Rule with
a higher priority supersedes other overlapping Rules with lower priorities.
Example: You may have a global filtration rule and you may want to apply the filtration
differently to a particular Symbol. In that case, you can have the global rule configured to
include all Symbols and set its priority to 1 and then configure another rule in which you select
a particular Symbol and set its priority to 2. In that case, whenever a tick for that Symbol comes
in, filtration rule 2 will be applied since it has a higher priority
Accepted
Repeatance
Yes 1,2,3 This is relevant in case the Filtration Pool is made up of one Maker only. It defines how many
times a price can be filtered out and discarded in the event of having consecutive suspicious
prices coming in. When the number of Accepted Repeatance is exceeded, the bridge would let
the suspicious price in. For instance, if the Accepted Repeatance is set to 5, then the bridge
would let a suspicious price in after the 5th consecutive tick.
Enable Yes Enabled,
Disabled
Indicates whether the Filtration Rule is enabled or disabled
Field Edita
ble
Possible
Values
Description

To delete a Filtration Pool
1. Click the “Delete” button next to the desired Filtration Pool rule.
2. To confirm the Deletion, type in the specified text.
3. Click the “Delete” button in the pop-up window to confirm the deletion.
Exporting a Filtration Pool
To Export a Filtration Pool
1. Select the desired Filtration Pool from the list.
2. Tick the checkbox to select a Filtration Pool.
3. Click “Export” and select “Export to Excel” or “Export to CSV”.
Filtration Logs
[2023-08-10 16:26:59.202337] [W] [17464] fp:[10], symbol[EURUSD], invalid mid_price:[1.10113], factor[1], unit[0.1], pools[1],
fdev[0.00001], var[0.00006], dg[5], bmp[1.10119]
[2023-08-10 16:26:59.202519] [I] [17464] fp:[10], symbol[EURUSD], invalid[ABC_DEMO][1.10113], count[5], unit[0.1], factor[1],
bmp[1.10119]
[2023-08-10 16:26:59.203107] [W] [17375] fp:[10], symbol[EURUSD], invalid mid_price:[1.10112], factor[1], unit[0.1], pools[1],
fdev[0.00001], var[0.00007], dg[5], bmp[1.10119]
[2023-08-10 16:26:59.206279] [W] [17375] agg_symbol[SUPPORT_LM@EURUSD], maker[ABC_DEMO], filtered-out[1.10109]/[1.10116]
[2023-08-10 16:26:59.250809] [W] [17464] fp:[10], symbol[EURUSD], invalid mid_price:[1.10114], factor[1], unit[0.1], pools[1],
fdev[0.00001], var[0.00005], dg[5], bmp[1.10119]
[2023-08-10 16:26:59.250856] [I] [17464] fp:[10], symbol[EURUSD], validated[ABC_DEMO][1.10114], after[5], unit[0.1], factor[1],
If ticked, the Filtration Rule is enabled
If unticked, the Filtration Rule is disabled, hence no filtration is applied
Description Yes A short description for reference purposes


bmp[1.10119]
[2023-08-10 16:26:59.315453] [W] [17464] fp:[10], symbol[EURUSD], invalid mid_price:[1.1011], factor[1], unit[0.1], pools[1],
fdev[0.00001], var[0.00001], dg[5], bmp[1.10112]
[2023-08-10 16:26:59.315714] [I] [17464] fp:[10], symbol[EURUSD], invalid[ABC_DEMO[1.1011], count[1], unit[0.1], factor[1],
bmp[1.10112]
fp Filtration Pool Rule ID
symbol Symbol
invalid
mid_price
New mid price that has been invalidated
factor Factor value in the Filtration Pool or Liquidity model filter factor
unit Unit value in the Filtration Pool
pools Number of active makers pricing in the Filtration Rule
fdev Allowed Factor Deviation which will be the allowed difference of the new mid price and the current midprice[bmp]
Formula: Unit x Factor (Rule or Liquidity Model)
var Variance or the difference between the new mid price and the current midprice[bmp]
Formula: BMP - Invalid mid_price
dg Digits of the symbol
bmp Benchmark price or the current midpoint
invalid Invalidated price from which maker
count Count of invalidated price
after After accepted repeatance
agg_symbol Name of the liquidity model and the symbol
filtered-out Filtered price
Field Explanation


```

---
