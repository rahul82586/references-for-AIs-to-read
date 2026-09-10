# 📁 45-stale-prices

- **Generated:** 2026-09-10 12:09
- **Total Files:** 3
- **Source:** `C:\Users\DELL\Downloads\backend_code-main (1)\backend_code-main (2)\bridge_manual_md\45-stale-prices`

---

## 📑 Table of Contents

1. [README.md](#readme-md)
2. [stale-rules.md](#stale-rules-md)
3. [symbols-profile.md](#symbols-profile-md)

---

## 🌲 Project Structure

```
45-stale-prices/
├── README.md
├── stale-rules.md
└── symbols-profile.md
```

---

## 📄 Files

<a id='readme-md'></a>
### 3. `README.md`

```markdown
[🏠 Document Start](..\README.md) / Stale Prices

# Stale Prices

Overview
Failover Makers is used to seamlessly and automatically switch to another stream of prices when the primary stream of prices fails due to
various reasons. This can also help to redirect trades in case of primary makers unavailability. This can be achieved through the use of the
“Stale Prices” module.
In its operations, the system captures the time of a symbol’s latest tick from a Maker and starts counting based on Warning and Error
Timeout, the following logic will be followed:
If no new quote has been received and the time exceeds the Warning Timeout, A Warning Alert will be triggered and sent by the
bridge.
If no new quote has been received and the time exceeds the Error Timeout, one of the following will happen:
If Switch to Failover is disabled, An Error Alert will be triggered.
If Switch to Failover is enabled, An Error Alert will be triggered, and one of the following can happen:
If Check LM is disabled, the system will immediately switch to Failover Maker and it will ignore the other makers available in the
Liquidity model.
If Check LM is enabled, the system will check first the other Makers in the Liquidity Model and one of the following can happen:
If the other Makers in the Liquidity Model are not streaming, the system will switch to Failover Maker.
If the other Makers in the Liquidity Model are streaming, the system will not switch to Failover Maker.
Setting up an Auto-failover
To setup an Auto-Failover we need to


1. Create a Symbol Profile → Refer to the Symbol Profile component for comprehensive documentation.
2. Create a Stale Rule → Refer to the Stale Rule component for comprehensive documentation.
3. Add a Failover Maker to the Liquidity Model → Refer to the Liquidity Model for comprehensive documentation.


```

---

<a id='stale-rules-md'></a>
### 3. `stale-rules.md`

```markdown
[🏠 Document Start](..\README.md) / [Symbols Profile](README.md) / Stale Rules

# Stale Rules

Overview
Stale rules are a crucial aspect of the Maker Failover Mechanism. They aid in determining the maker to monitor based on symbol profile
settings and specify the Liquidity Models for which the "Switch To Failover" is applicable when activated. Additionally, they allow users to
apply rules during specific sessions, enabling them to skip checks or failovers during anticipated periods when no prices are expected.
Creating a Stale Rule
To create a Stale Rule
1. Click the “Stale Rules” component.
2. Click the “Add” button to create a new Liquidity Model.
3. Fill out the wizard with all relevant information. You may refer to the field descriptions hereafter.
4. Click the “Submit” button to submit the changes.
Enable Enabled,
Disabled
Indicates whether the stale rule is enabled or disabled
Field Possible
Values
Description

Deleting Stale Rule
To delete a Stale Rule
1. Click the “Delete” button next to the desired Stale Rule.
2. To confirm the Deletion, type in the specified text.
3. Click the “Delete” button in the pop-up window to confirm the deletion.
Exporting a Stale Rule
To Export a Stale Rule
1. Select the desired Stale Rule from the list.
2. Click “Export” and select “Export to Excel” or “Export to CSV”.
Maker Maker_1 The Maker into which the Stale Prices checkers will be applied on.
Symbol
Profile
StaleProfile1 The Symbol Profile into which the Stale Prices will base its settings on.
Liquidity
Models
LM_1,
AGG_Makers
The Liquidity Model to be monitored by the Stale Rule.
Session MON,00:00-
23:59
Defines the time of the day during which the Stale Prices will be checked on.
All days of the week should be included and separated by a semicolon “;” along with the time interval
during the day. 00:00-00:00 represents a closure during a particular day.
Priority 1-10 This parameter applies in the event of overlapping configurations where a Stale Rule with a higher
priority supersedes other overlapping Rules with lower priorities.
Description A short description for reference purposes





```

---

<a id='symbols-profile-md'></a>
### 3. `symbols-profile.md`

```markdown
[🏠 Document Start](..\README.md) / [Stale Prices](README.md) / Symbols Profile

# Symbols Profile

Overview
The Symbols Profile plays a crucial role in the Maker Failover Mechanism. Here, you can set up the symbol's preferences, guiding the
system in recognizing when a symbol’s price becomes outdated or stale. These preferences are unique for each symbol. There are two
timeout levels: a warning threshold and an error threshold. If either is reached, an alert is generated and recorded in the logs. Beyond
timeouts and alerts, you can also configure the system to automatically switch if a particular symbol is identified as not pricing.
Creating a Symbol Profile
To create a Symbol Profile
1. Click the “Symbol Profile” component.
2. Click the “Add” button to create a new Symbol Profile.
3. Fill out the wizard with all relevant information. You may refer to the field descriptions hereafter.
4. Click the “Submit” button to submit the changes.
Configuring Symbol Profile
To configure or modify a newly added Symbol Profile on a per symbol basis
Name StaleProfile1 This is intended to recognize the Symbol Profile and determine the particular Maker being
utilized in this Symbol Profile.
Description A short description for reference purposes only.
Field Possible Values Description

1. Configure the Symbol Profile by modifying the editable fields. All editable fields are represented by a “Pen” icon.
2. Click the “Save” button on the top left to apply the changes.
3. Click the “Revert All” button if you want to revert to the previous values.
Deleting Symbol Profile
To delete a Symbol Profile
1. Click the “Delete” button next to the desired Symbol Profile.
2. To confirm the Deletion, type in the specified text.
3. Click the “Delete” button in the pop-up window to confirm the deletion.
Symbol EURUSD,
XAUUSD
The Symbol to be tracked and to be applied with succeeding settings.
Symbols Profile StaleProfile1 Different Symbols Profiles can have distinct timeout setups, linked within the Stale Rules.
Warning Timeout
(sec)
5,10 Initial threshold tracking the time elapsed in seconds since the last update before issuing
warning alerts.
Error Timeout (sec) 10,15 Final threshold tracking the time elapsed in seconds since the last update before issuing
alerts and initiating failover mechanism.
Check LM other
makers
Enabled,
Disabled
During aggregation, this verifies other available makers in the Liquidity model before initiating
failover. If other makers in the same liquidity model are pricing, Switch To Failover is ignored.
Switch To Failover Enabled,
Disabled
Determines if the liquidity model(s) will shift from Primary to Failover. This collaborates with
Check LM other makers, enabled symbol profile, and an active stale rule.
Enable Enabled,
Disabled
Indicates whether the symbol profile is enabled or disabled.
Field Possible
Values
Description


Exporting a Symbol Profile
To Export a Symbol Profile
1. Select the desired Symbol Profile from the list.
2. Click “Export” and select “Export to Excel” or “Export to CSV”.




```

---
