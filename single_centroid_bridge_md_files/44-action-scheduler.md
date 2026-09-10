# 📁 44-action-scheduler

- **Generated:** 2026-09-10 12:09
- **Total Files:** 1
- **Source:** `C:\Users\DELL\Downloads\backend_code-main (1)\backend_code-main (2)\bridge_manual_md\44-action-scheduler`

---

## 📑 Table of Contents

1. [README.md](#readme-md)

---

## 🌲 Project Structure

```
44-action-scheduler/
└── README.md
```

---

## 📄 Files

<a id='readme-md'></a>
### 1. `README.md`

```markdown
[🏠 Document Start](..\README.md) / Action Scheduler

# Action Scheduler

Overview
This feature enables brokers to modify their default settings at the bridge level for a specific Time-Frame. It applies exclusively to the
following settings:
1. Markup Model
2. Liquidity Model
3. Taker Feeds
4. Taker Execution Model
The default filters for all these components include:
The option to select specific Symbols and Securities.
In-session values: These reflect the adjustments you wish to make to the default values for the specified time frame. These changes are
effective during the in-session period and revert to the default settings once the specified time frame has concluded.
Out-of-session values: These changes become effective after the specified in-session time frame has concluded. For instance:
If you start with the default setup, the in-session values will become active for the specified time frame.
When you mark a checkbox, you are indicating that you want to update your default values to new values. The out-of-session values will
then become the new default values for that particular component.
Sessions allow you to define the specific time frame during which the changes should take effect and transition the values from default to
in-session values.
Creating a new Action Scheduler Rule
To create a Action Scheduler Rule
1. Click on “Action Scheduler”
2. Click on the “Add” button to create a new Action Scheduler Rule.
3. Fill out the Wizard. You may refer to the field descriptions listed below
4. Click “Submit” to submit the changes.


ID A unique ID number for the configured rule
Type Available types are the following:
Markup Models
Liquidity Models
Taker Feeds
Taker Execution Model
Components This value depends on the selected Type
Securities The name of the Security to be filtered and used.
Symbols The name of the Symbol to be filtered and used.
In Session Values All configured values under the components will reflect in this field
Out of Session
Values
Configurable as new values in case the broker intended to not revert back to original values after the In Session
expires
Date Calendar Specific date in the calendar where Action Scheduler will be activated
Priority This parameter applies in the event of overlapping rules where an Action Scheduler Rule with a higher priority
supersedes other overlapping Rules with lower priorities.
Sessions Defines the time when the rule is Active and In Session
Description A short description for reference purposes
Field Description

In-Depth Explanation of the Components Listed Above:
Enabled Indicates whether the Action Scheduler Rule is enabled or disabled
If ticked, the Action Scheduler Rule is active and will be activated during the configured Sessions
If unticked, the Action Scheduler Rule is disabled, hence will not activate
Field Description
Markup Bid [Points] Adjust bid markup for a specified time frame.
Markup Ask [Points] Adjust ask markup for a specified time frame.
Markup Bid Var
[Points]
Adjust bid markup variation for a specified time frame.
Markup Ask Var
[Points]
Adjust ask markup variation for a specified time frame.
Spread Min [Points] Set the minimum spread for a specified time frame.
Spread Max [Points] Set the maximum spread for a specified time frame.
Spread Min Exec Set the minimum executable spread for a specified time frame.
Spread Max Exec Set the maximum executable spread for a specified time frame.
Markup Model
Field Description
Maker/Makers Configure liquidity maker settings.
Execution Mode
(Exec Mode)
Define the execution mode for liquidity.
Filter Factor Specify a filter factor for liquidity.
Liquidity Models
Field Description
Liquidity Model Configure the liquidity model for taker feeds.
Markup Model Configure the markup model for taker feeds.
Taker Feed
Field Description
Taker Execution Model

Notes: In-session values are applicable only for the specified time frame. Whether the settings return to default or switch to new
default values depends on the configuration of the Out-of-session values.
Configuring Action Scheduler
To Configure/Modify a newly added/existing Action Scheduler
1. Click the little arrow next to the Symbol column to have it sorted in alphabetical order.
2. Configure the Action Scheduler by editing the editable fields. All edited fields are represented by a pen icon
3. Click the “Save” button on top to apply the changes
4. Click on the “Revert All” button if you want to revert to the previous values
Delete an Action Scheduler
To delete an Action Scheduler rule
1. Click the “Delete” icon next to the desired Action Scheduler rule
2. Confirm the “Delete” button in the pop-up window to confirm the deletion
Liquidity Model Specify the liquidity model for taker execution.
Markup Model Specify the markup model for taker execution.
B Book Percentage
%
Set the percentage for B Book execution.
BFix Configure BFix settings.
BBoost Set BBoost parameters.
BDelay Range [From
ms to To ms]
Define a delay range for B Book execution.
Gain Percentage [0-
100]
Adjust gain percentage for execution.
LL Variation Set parameters for LL variation.
LL Action Define LL action parameters.


To export an Action Scheduler
1. Select the desired Action Scheduler from the list
2. Tick the checkbox to select an Action Scheduler
3. Click “Export” → Export to Excel / Export to CSV
FAQ
Why is the Action Scheduler not activating for the particular rule?
How can I set up an Action Scheduler Rule to apply daily? What about on a specific date?

The Action Scheduler takes about 60 seconds to activate after the In Session Time and an additional 60 seconds to revert to default
values (as per your rule) after the Out Session Time.
Yes, both scenarios are possible with the right session-level setup. Just choose your preferred option and make sure to set the
session in and out accordingly.


```

---
