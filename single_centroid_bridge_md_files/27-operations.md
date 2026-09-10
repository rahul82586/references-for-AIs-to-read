# 📁 27-operations

- **Generated:** 2026-09-10 12:08
- **Total Files:** 5
- **Source:** `C:\Users\DELL\Downloads\backend_code-main (1)\backend_code-main (2)\bridge_manual_md\27-operations`

---

## 📑 Table of Contents

1. [README.md](#readme-md)
2. [dividends-adjustments.md](#dividends-adjustments-md)
3. [swapdividend-requirement.md](#swapdividend-requirement-md)
4. [swaps-groups.md](#swaps-groups-md)
5. [swaps-symbols.md](#swaps-symbols-md)

---

## 🌲 Project Structure

```
27-operations/
├── dividends-adjustments.md
├── README.md
├── swapdividend-requirement.md
├── swaps-groups.md
└── swaps-symbols.md
```

---

## 📄 Files

<a id='readme-md'></a>
### 5. `README.md`

```markdown
[🏠 Document Start](..\README.md) / Operations

# Operations

The Operations Module allows to create and configure Dividends Adjustments, Swaps Symbols, and Swaps Groups groups. Upon clicking
the “Operations” button on the left-hand side menu, it expands to show the different components underneath which are explained in
greater detail hereunder.




```

---

<a id='dividends-adjustments-md'></a>
### 5. `dividends-adjustments.md`

```markdown
[🏠 Document Start](..\README.md) / [Operations](README.md) / Dividends Adjustments

# Dividends Adjustments

Overview
The Dividend Adjustment under Operation allows a broker to apply dividends to any MT4/5 login based on their open positions. It offers an
option to fully apply automated dividends according to broker's requirements. With the dividend component, we can select the
corresponding MT4/5 server. The required symbol can be selected together with the base currency which will be used for the conversion
rate. Long/Short dividend value will be used to calculate the final dividend amount and it can be set to apply immediately or scheduled to
be performed at a later time.
Create a Dividend Operation
To create a new dividend task
1. Click “Schedule Dividends Adjustment” to create a new dividend operation.
2. Fill out the wizard with all the required fields, you may refer to the field descriptions hereafter.
3. Click “Preview and Schedule” to submit the changes.


Server The specific MT4/5 server you can choose to apply the dividends adjustment
Symbol The symbol for which the dividends need to be applied
Currency The currency will be treated as the base currency for calculating the conversion rate. Custom button can be
ticked to manually type any desired currency for conversion rate
Collect Symbol Suffixes Dividend will be applied to all the symbol suffixes of the selected symbol
Long Dividends The amount to be (added/deducted) to an account for a long position
Short Dividends The amount to be (added/deducted) from an account for a short position
Conversion Rates The current conversion rate will be used for converting the dividend amount from the selected currency to
the account's group currency. It will apply the conversion rate only if it is enabled
Delayed Allows the dividend task to be scheduled at any date/time
Field Description

Scheduled/Completed Dividend
Scheduled Dividend
1. Scheduled dividend will be shown as blue circle.
2. Clicking on the “pen” icon allows us to edit the dividend fields.
3. Preview of the dividend will be shown after we click “Preview and Schedule”.
Completed Dividend:
1. Completed dividend will be shown as green circle.
2. Clicking on the “eye” icon will display the details of the operation.
3. All the completed tasks can be displayed based on date/time on Monitoring >> “Dividend Completed Jobs” Component.
Applied Date UTC The UTC date and time when the dividends adjustment will be applied
Dividends Deal
Comment
A comment related to the dividend adjustment balance operation. It will be displayed in the MT4/5
Check Margin if enabled, it will check the account margin before applying dividend. Set to disable, the dividend task will
not consider account margin


Dividend Calculation Formula
→ For Long Position:
Amount=Position Volume × Contract Size × Conversion Rate × Long Dividends Value
→ For Short Position:
Amount=Position Volume × Contract Size × Conversion Rate × Short Dividends Value
Important Notes
1. Position Volume Unit: The Position Volume is in lots.
2. Conversion Rate: The conversion rate goes from the chosen base currency to the MT4/MT5 login currency.
3. Conversion Rate of 0: The conversion rate will be zero if the base currency to login currency is not priced in MT4/MT5.
Example:
Base currency (CCY) = GBP
MT4/MT5 login currency (CCY) = USD
To obtain a conversion rate for a dividend, GBPUSD must be priced on MT4/MT5.



```

---

<a id='swapdividend-requirement-md'></a>
### 5. `swapdividend-requirement.md`

```markdown
[🏠 Document Start](..\README.md) / [Swaps Groups](README.md) / Swap/Dividend Requirement

# Swap/Dividend Requirement

MT4 Required Configurations & Actions
For the installation of the MT4 Centroid plugin, follow these steps:
a. Open port 11000 on the MT4 server or allow the bridge IP on port 11000.
b. Send the following details to support@centroidsol.com:
Confirmation that the plugin is successfully installed.
Target Server IP: 11000
Installation
1. Stop the MT4 service via Windows Services
2. Add the centroid_mt4_operations.dll file to the plugin folder (download here).
3. Start the MT4 service via Windows Services.
Note: Config file will be automatically created during the installation with a default port of 11000.
MT5 Required Configurations & Actions
Provisioning MT5 Manager
1. Create a dedicated MT5 Manager for Swap Uploader
2. Manager Group Permission must be configured
3. Manager Permission must be configured with the below rights:


4. Send the following details to support@centroidsol.com
* Desired Swap Uploader name (e.g., “Main MT5 Server”)
* Manager Login
* Manager Master Password
* Public Access Server



```

---

<a id='swaps-groups-md'></a>
### 5. `swaps-groups.md`

```markdown
[🏠 Document Start](..\README.md) / [Swaps Symbols](README.md) / Swaps Groups

# Swaps Groups

Overview
The MT4/MT5 Swaps Group Update functionality, can be found within the Bridge Engine UI, under the Operations section. The Swaps
Update functionality is part of a set of operational tools for trading platforms (i.e. MT4, MT5, etc.) that is intended to optimize and minimize
the time needed to manage specific configurations on the trading platforms that need to be performed periodically. Therefore, by having an
optimized way and single system where to manage such tasks (for one or multiple platforms), it can save a lot of time and avoid overhead.
At the Swaps Group screen, the swap values of all or specific symbols, for any specific group within the trading platform, can be updated.
This can be done either via the UI, by adding new config lines for specific group and symbol, or editing existing settings; alternatively, the
Export and Upload can be used to bulk add or update the swap settings across a large number of groups and symbols at the same time.
Swap Group Change
To change the swap for groups:
1. Select the required MT4/5 server.
2. Enter the “New Swap Long/New Swap Short” value on the UI or via upload function.
3. Click “Save” to deploy the changes.
Important Notes
Swap changes will be applied immediately
New value is highlighted in red if it is more or less than 10% of the current swap value.
Swap changes from default to any value or vice versa will always be highlighted red.
Server The specific MT4/5 server to apply the swap operation
Group The group on MT4/5 server
Symbol The symbol for which the swap will be changed
Description Group name - Symbol
Swap Long Current Swap Long value of that group symbol
New Swap Long The new swap long value which will replace the current group symbol swap value
Swap Short Current Swap Short value of that group symbol
New Swap Short The new swap short value which will replace the current group symbol swap value
Field Description

Swap changes can be performed using UI Wizard or upload an excel/csv file.
Deleting a Swap Group
To delete a Swap Group
1. Click the “Delete” icon next to the desired Swap Group.
2. Confirm the “Delete” button in the pop-up window to confirm the deletion.
Exporting a Swap Group
Click “Export” and select “Export to Excel” or “Export to CSV”
Uploading a Swap Group
1. Click on “Upload”
2. Drop the file you want to upload. Alternatively, you can click on “Drop a File”, select the file and click “Open”


3. Click “Upload“ to upload the file or click “Close” to cancel.




```

---

<a id='swaps-symbols-md'></a>
### 5. `swaps-symbols.md`

```markdown
[🏠 Document Start](..\README.md) / [Dividends Adjustments](README.md) / Swaps Symbols

# Swaps Symbols

Overview
The MT4/MT5 Swap Symbol Update functionality, can be found within the Bridge Engine UI, under the Operations section. The Swaps
Update functionality is part of a set of operational tools for trading platforms (i.e. MT4, MT5, etc.) that is intended to optimize and minimize
the time needed to manage specific configurations on the trading platforms that need to be performed periodically. Therefore, by having an
optimized way and single system where to manage such tasks (for one or multiple platforms), it can save a lot of time and avoid overhead.
At the Swaps Symbols screen, the swap values of all the symbols within the trading platform can be updated. This can be done either via
the UI, by setting the new values for the Short and Long swaps, respectively; alternatively, the Export and Upload can be used to bulk
update the swap settings across a large number of symbols at the same time.
Swap Symbol Change
To change the swap for symbol
1. Select the required MT4/5 server.
2. Enter the required “New Swap Long/New Swap Short” on the UI or via the upload function.
3. Click “Save” to deploy the changes.
Important Notes
Swap changes will be applied immediately
New value is highlighted in red if it is more or less than 10% of the current swap value
Swap changes can be performed using UI Wizard or upload an excel/csv file
Server The specific MT4/5 server to apply the swap operation
Symbol The symbol for which the swap will be changed
Description The description of symbol as per MT4/5 server
Swap Long Current Swap Long value of that symbol
New Swap Long The new swap long value which will replace the current swap value
Swap Short Current Swap Short value of that symbol
New Swap Short The new swap short value which will replace the current swap value
Field Description

Exporting the Swap Symbols
To export the Swap Symbols
Click “Export” and select “Export to Excel” or “Export to CSV”
Uploading the Swap Symbols
To upload the Swap Symbols Settings
1. Click on the “Upload”
2. Drop the file you want to upload. Alternatively, you can click on “Drop a File”, select the file and click “Open”


3. Click “Upload“ to upload the file or click “Close” to cancel.




```

---
