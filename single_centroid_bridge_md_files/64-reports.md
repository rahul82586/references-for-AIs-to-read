# 📁 64-reports

- **Generated:** 2026-09-10 12:10
- **Total Files:** 32
- **Source:** `C:\Users\DELL\Downloads\backend_code-main (1)\backend_code-main (2)\bridge_manual_md\64-reports`

---

## 📑 Table of Contents

1. [README.md](#readme-md)
2. [bbook-profitability-report.md](#bbook-profitability-report-md)
3. [detailed-leg-report.md](#detailed-leg-report-md)
4. [fills.md](#fills-md)
5. [giveup-orders.md](#giveup-orders-md)
6. [legs.md](#legs-md)
7. [login-spread-(client).md](#login-spread-client-md)
8. [login-spread-(cover).md](#login-spread-cover-md)
9. [maker-notional-chart.md](#maker-notional-chart-md)
10. [maker-notional-report.md](#maker-notional-report-md)
11. [maker-orders.md](#maker-orders-md)
12. [maker-rejection.md](#maker-rejection-md)
13. [maker-symbol-chart.md](#maker-symbol-chart-md)
14. [maker-symbol-spread-history-chart.md](#maker-symbol-spread-history-chart-md)
15. [maker-symbol-status.md](#maker-symbol-status-md)
16. [markup-leg-report.md](#markup-leg-report-md)
17. [markup-report.md](#markup-report-md)
18. [mt4-reports.md](#mt4-reports-md)
19. [mt5-reports.md](#mt5-reports-md)
20. [net-per-login.md](#net-per-login-md)
21. [orders.md](#orders-md)
22. [risk-account-statement.md](#risk-account-statement-md)
23. [slippage-leg-report.md](#slippage-leg-report-md)
24. [slippage-report.md](#slippage-report-md)
25. [symbol-detail-chart.md](#symbol-detail-chart-md)
26. [symbol-notional-chart.md](#symbol-notional-chart-md)
27. [symbol-notional.md](#symbol-notional-md)
28. [taker-notional.md](#taker-notional-md)
29. [trade-transactions.md](#trade-transactions-md)
30. [positions/README.md](#positions-readme-md)
31. [positions/risk-account-position-upload.md](#positions-risk-account-position-upload-md)
32. [positions/tem-position-upload.md](#positions-tem-position-upload-md)

---

## 🌲 Project Structure

```
64-reports/
├── bbook-profitability-report.md
├── detailed-leg-report.md
├── fills.md
├── giveup-orders.md
├── legs.md
├── login-spread-(client).md
├── login-spread-(cover).md
├── maker-notional-chart.md
├── maker-notional-report.md
├── maker-orders.md
├── maker-rejection.md
├── maker-symbol-chart.md
├── maker-symbol-spread-history-chart.md
├── maker-symbol-status.md
├── markup-leg-report.md
├── markup-report.md
├── mt4-reports.md
├── mt5-reports.md
├── net-per-login.md
├── orders.md
├── positions/
│   ├── README.md
│   ├── risk-account-position-upload.md
│   └── tem-position-upload.md
├── README.md
├── risk-account-statement.md
├── slippage-leg-report.md
├── slippage-report.md
├── symbol-detail-chart.md
├── symbol-notional-chart.md
├── symbol-notional.md
├── taker-notional.md
└── trade-transactions.md
```

---

## 📄 Files

<a id='readme-md'></a>
### 32. `README.md`

```markdown
[🏠 Document Start](..\README.md) / Reports

# Reports

Centroid provides over 25 detailed reports, empowering clients to efficiently track their market exposure. Stay informed and make informed
decisions with our comprehensive reporting tools.


```

---

<a id='bbook-profitability-report-md'></a>
### 32. `bbook-profitability-report.md`

```markdown
[🏠 Document Start](..\README.md) / [Trade Transactions](README.md) / BBook Profitability Report

# BBook Profitability Report

Overview
The BBook Profitability Report offers a comprehensive examination of orders within the Aggregator, whether partially or fully directed to the
B Book. It provides a detailed breakdown of how B Book legs are executed, simulating an authentic STP setup. Moreover, the report
enables brokers to contrast the execution on MT4/MT5 platforms with that on the Centroid Aggregator.
Beyond mere numerical data, this report serves as a valuable tool for brokers to assess the financial impact of price improvement. By
comparing Centroid Aggregator execution to retaining orders in MT4/MT5, brokers can gauge whether they would achieve better or lesser
returns. This analytical approach helps brokers identify scenarios where price improvement proves advantageous for them or their clients,
facilitating more informed decision-making.
Note: Brokers have the capability to fine-tune the allocation of price improvement in favor of the client through the Gain Percentage field
within the Taker Execution Model, specified on a per Symbol basis. For instance, configuring the Gain Percentage to 100 allows the broker
to retain the entire price improvement when it favors the client, without passing on any percentage. Conversely, a Gain Percentage setting
of 0 ensures that the client receives the complete benefit of the price improvement.
Request BBook Profitability Report
To request a BBook Profitability Report
1. Click on the "Toggle here to search" button.
2. Complete the Wizard as detailed below.
3. Pre-set the columns necessary for the report in the Grid Columns.
4. Click "View Results" to execute the report or directly "Export to CSV or Excel" file.
Note: Use the Reset button to clear the pre-defined filters
Note: In the above fields, any field that is left empty, apart from dates, implies that all values are included in the search
Start Date The Start Date of your desired search interval
End Date The End Date of your desired search interval
Ext Client
Group
MT4/MT5 Group number for Takers of type MT4/MT5
Ext Client
Login
MT4/MT5 Login number for Takers of type MT4/MT5
Field Description

After generating the BBook Profitability Report, you can perform the following actions
1. Arrange columns in ascending or descending order.
2. Apply filters to columns using various arithmetic and logical conditions.
3. Navigate through pages using options for first, last, previous, and next pages.
4. Optimize the report layout to fit the entire content on the page.
5. Automatically adjust column sizes based on the data within each column.
BBook Profitability Details
Ext Order
ID
MT4/MT5 Ticket Number for Takers of type MT4/MT5
Cen Ord Id Centroid Order ID
Symbol Select one or multiple Symbols from the list of Symbols
Taker The Taker(s) configured in the Centroid Bridge such as FIX, MT4, MT5 and Centroid’s Trading Platform
TEM Taker Execution Model(s) through which the Order was executed
Risk
Account
Risk Account through which the Order was executed, if any
Ext Bid/Ask Indicates whether we are comparing the Filled Price to the Price that was initiated from the Taker (MT4 or MT5) or not.
If ticked, Aggregator calculates the Slippage based on the difference between Fill Price and Price initiated by Taker
If unticked, Aggregator calculates the Slippage based on the difference between Fill Price and the Price initiated by
the Aggregator based on the first scan of the Liquidity Book when the Order was received
Grid
Columns
Columns or data fields that will be available in the report
Cen Ord ID Centroid unique Order ID recorded in the Aggregator
Ext Client Login Login number of the MT4/MT5 Taker if the order is originated from a Taker of type MT4 or MT5. Otherwise,
value will be 0
Ext Order ID Order ID number of the MT4/MT5 Taker if the order is originated from a Taker of type MT4 or MT5. Otherwise,
value will be 0
Field Description

To Export the BBook Profitability Report
Click on “Export to CSV” or “Export to Excel” to export the report
Recv Time The Time at which the Oder was received in the Aggregator
Taker Execution
Model
The Taker Execution Model through which the Order was processed
Symbol The traded Symbol
Party Symbol The Party Symbol as defined in the corresponding Maker Session
Side The side of the Order; Buy or Sell
Ord Type The category of the executed Order, whether it is Market or Limit.
Volume The requested Volume of the Order
Fill Volume The total Filled Volume in Base Currency
BFill Volume The B Book Filled Volume of the Order is determined as follows:
If the Order is 100% B Book, BFill Volume is equivalent to the Fill Volume.
If the Order is partially B Booked, this value represents the percentage of the Order that has been directed
to the B Book.
BFill Price The Aggregator's execution price for the B Book Order.
Exit Price The price at which the client's Order would have been executed in the front-end platform (MT4/MT5) without
utilizing the Centroid B Book (Depth of Market).
Notional B The notional value of the B Book-filled Order in USD.
Price Improvement
(USD)
The Price Improvement in USD is calculated as the difference between the Exit Price and BFill Price, multiplied
by the Volume.
If the result is positive, it indicates a profit for the Broker.
If the result is negative, it signifies a loss for the Broker and a profit for the Client.
CS Cost (USD) The cost of executing the Order through Centroid Aggregator in USD.
Price Improvement
Net of CS Cost
(USD)
The net Profit/Loss attributable to Price Improvement, considering the CS Cost resulting from executing the
trade via the Centroid Aggregator, is calculated as follows:
Price Improvement Net=Price Improvement USD−CS Cost USD
This metric reflects the overall financial impact of price improvement, accounting for the associated cost
incurred through the Centroid Aggregator.




```

---

<a id='detailed-leg-report-md'></a>
### 32. `detailed-leg-report.md`

```markdown
[🏠 Document Start](..\README.md) / [Legs](README.md) / Detailed Leg Report

# Detailed Leg Report

Overview
A Detailed Leg Report provides a brief analysis of slippage at the Maker, Broker, and Client levels, along with profitability (resulting from
markups) on a per-leg basis.
Request Detailed Leg Report
To request a Detailed Leg Report
1. Click on the "Toggle here to search" button.
2. Complete the Wizard as detailed below.
3. Pre-set the columns necessary for the report in the Grid Columns.
4. Click "View Results" to execute the report or directly "Export to CSV or Excel" file.
Note: Use the Reset button to clear the pre-defined filters
Note: In the above fields, any field that is left empty, apart from dates, implies that all values are included in the search
Start Date The Start Date of your desired search interval
End Date The End Date of your desired search interval
Ext Client
Group
MT4 Group number for Takers of type MT4/MT5
Ext Client
Login
MT4 Login number for Takers of type MT4/MT5
Ext Order
ID
MT4 Ticket Number for Takers of type MT4/MT5
Cen Ord Id Centroid Order ID
Symbol Select one or multiple Symbols from the list of Symbols
Taker The Taker(s) configured in the Centroid Bridge such as FIX, MT4, MT5 and Centroid’s Trading Platform
TEM Taker Execution Model(s) through which the Order was executed
Risk
Account
Risk Account through which the Order was executed, if any
Field Description

The Detailed Leg Report is divided into two sections, Leg Details and Order Details. When Order is split into multiple Legs, different Legs
will be shown on one side whereas on the other side the same Order will be shown multiple times depending on the number of Legs it was
split into.
Once the Detailed Leg Report has been generated, you can do the following:
1. Sort columns by ascending or descending order
2. Filter columns using a variety of arithmetic and logical conditions
3. Navigate through pages by accessing first, last, previous and next pages
4. Fit the entire report into the page
5. Auto size columns based on the column data
Leg Details
Order Details
Maker Select one or multiple Makers from the list.
For B Book Orders, they will be under B_BOOK Maker
Grid
Columns
Columns or data fields that will be available in the report
Cen Client
OrdId
The ID of the Leg. For instance, an Order split into three legs will have Leg IDs of 0, 1 and 2
Maker The Maker Leg got executed with or that provided the quote for B Book Orders
Send Time The Time at which the Leg was sent to the Maker
Fill Volume The filled Volume of the Leg
Notional The Notional Volume of the Leg in USD
Maker
Symbol
The Symbol name on Maker’s side
Maker
OrderID
The assigned ID of the Order returned by the Maker
Field Description
Client Ord
Id
Client Order ID received in the Centroid Bridge
Cen Ord Id Centroid unique Order ID recorded in the Centroid Bridge
Recv Time The Time at which the Oder was received and processed in the Centroid Bridge
Taker The Taker that initiated the Order
TEM The Trading Execution Model within the Taker from where the Order was placed
Symbol The traded Symbol
Field Description

Ord Type The type of the Order; Market, Limit or Stop
Side The side of the Order; Buy or Sell
Fill Volume The filled Volume of the Order
Avg Price The VWAP Fill Price reported back to Client after the Order has been filled


```

---

<a id='fills-md'></a>
### 32. `fills.md`

```markdown
[🏠 Document Start](..\README.md) / [Detailed Leg Report](README.md) / Fills

# Fills

Overview
The Fills Report presents a detailed overview into each Legs in terms of how the Order got executed along with the relevant execution
details. The relationship between Order and Leg is one to many as a single Order can be split into multiple Legs in the event in filling the
Order in more than one attempt. The report is split into Leg Details and Order Details which relevant fields for each.
Request Fill Report
To request a Fill Report
1. Click on the "Toggle here to search" button.
2. Complete the Wizard as detailed below.
3. Pre-set the columns necessary for the report in the Grid Columns.
4. Click "View Results" to execute the report or directly "Export to CSV or Excel" file.
Note: Use the Reset button to clear the pre-defined filters
Note: In the above fields, any field that is left empty, apart from dates, implies that all values are included in the search
Start Date The Start Date of your desired search interval
End Date The End Date of your desired search interval
Ext Client
Group
MT4/MT5 Group number for Takers of type MT4/MT5
Ext Client
Login
MT4/MT5 Login number for Takers of type MT4/MT5
Ext Order
ID
MT4/MT5 Ticket Number for Takers of type MT4/MT5
Cen Ord Id Centroid Order ID
Symbol Select one or multiple Symbols from the list of Symbols
TEM Taker Execution Model(s) through which the Order was executed
Taker The Taker(s) configured in the Centroid Bridge such as FIX, MT4, MT5 and Centroid’s Trading Platform
Field Description

Display Fill Report
After generating the Fills Report, you can perform the following actions
1. Arrange columns in ascending or descending order.
2. Apply filters to columns using various arithmetic and logical conditions.
3. Navigate through pages using options for first, last, previous, and next pages.
4. Optimize the report layout to fit the entire content on the page.
5. Automatically adjust column sizes based on the data within each column.
Leg Details
Risk
Account
Risk Account through which the Order was executed, if any
Maker Select one or multiple Makers you wish to check Orders with
Maker B This is relevant to B Book Orders only where you can check the Makers who provided the quote at the time the B Book
Order was executed
Grid
Columns
Columns or data fields that will be available in the report
Cen Client
OrdId
The ID of the Leg. For instance, an Order split into three legs will have Leg IDs of 0, 1 and 2
Maker The name of the Maker the Leg got it executed with
If A Book: The name of the LP that processed the Order will be displayed as configured in the bridge
If B Book: B_BOOK will be displayed
Maker B This is relevant to B Book Orders only and discloses the Maker that provided the quote at the time the B Book Order
was executed
Time The Date and Time at which the Leg was executed
Side The side of the Order; Buy or Sell
Volume The requested Leg Volume
Fill Volume The actual filled Leg Volume which could be equal or less than the requested Volume above
Notional The Notional Volume of the filled Leg in USD
Field Description

Order Details
Maker Symbol The name of the Symbol on the Maker’s side
Maker
OrderID
The assigned ID of the Order returned by the Maker
Maker Cat The Maker Category or Type
Maker ExecID The Execution ID of the Leg assigned by the Maker
Fill Price The fill Price the Leg got executed at including Markup
Markup Defined Markup in decimal on top of the Price, if any
Raw Fill Price The fill Price the Leg got executed at excluding Markup
Exec Time
(ms.mic)
Order Execution Time in milliseconds and microseconds
Client Ord ID Client Order ID received in the bridge
Cen Ord ID Centroid unique Order ID recorded in the bridge
Ext Client
Login
Login number of the MT4/MT5 Taker if the order is originated from a Taker of type MT4 or MT5. Otherwise, value will
be 0
Ext Client
Group
Group name of the MT4/MT5 Login from which the order was generated, if the order is originated from a Taker of
type MT4 or MT5. Otherwise, the field will display an empty value
Ext Order ID Ticket Number of the MT4/MT5 Taker if the order is originated from a Taker of type MT4 or MT5. Otherwise, value will
be 0
TEM The Taker Execution Model through which the Order was processed
Symbol The traded Symbol
Liquidity
Model
The Liquidity Model used for execution
Side The side of the Order; Buy or Sell
Ord Type The type of the Order; Market, Limit or Stop
Volume The requested Volume of the Order
Fill Volume

The effective filled Volume of the Order.
Fully Filled: Orders exhibit a Full Volume equivalent to the specified Volume.
Partially Filled: Orders have a Fill Volume that is less than the specified Volume.
Rejected: Orders show 0 Volume since no Volume was executed.
Notional The Notional Volume of the filled order in USD
Avg Price The Weighted Average Price in case the Order was split into multiple legs
Field Description

To Export the Fills Report
Click on “Export to CSV” or “Export to Excel” to export the report

Slippage The Slippage in decimal value which results due to price difference between request price and filled price. Slippage is
the difference between the fill price and the requested price
State

The status of the Order:
Filled: Denotes complete fulfillment of the Order
Partial: Denotes a partial fulfillment of the Order
Rejected: Denotes rejection of the Order



```

---

<a id='giveup-orders-md'></a>
### 32. `giveup-orders.md`

```markdown
[🏠 Document Start](..\README.md) / [Maker Orders](README.md) / Giveup Orders

# Giveup Orders

Overview
The Giveup Orders Report offers a summary of all giveup orders recorded on MT4 or MT5 giveup accounts specified in the Giveup Rule
module.
Request Giveup Orders Report
To request a Giveup Orders Report
1. Click on the "Toggle here to search" button.
2. Complete the Wizard as detailed below.
3. Pre-set the columns necessary for the report in the Grid Columns.
4. Click "View Results" to execute the report or directly "Export to CSV or Excel" file.
Note: Use the Reset button to clear the pre-defined filters
Note: In the above fields, any field that is left empty, apart from dates, implies that all values are included in the search
Start Date The Start Date of your desired search interval
End Date The End Date of your desired search interval
Ext Client
Group
MT4/MT5 Group number for Takers of type MT4/MT5
Ext Client
Login
MT4/MT5 Login number for Takers of type MT4/MT5
Ext Order ID MT4/MT5 Ticket Number for Takers of type MT4/MT5
Cen Ord Id Centroid Order ID
Symbol Select one or multiple Symbols from the list of Symbols
Taker The Taker(s) configured in the Centroid Bridge such as FIX, MT4, MT5 and Centroid’s Trading Platform
TEM Taker Execution Model(s) through which the Order was executed
Grid
Columns
Columns or data fields that will be available in the report
Field Description

After generating the Giveup Orders Report, you can perform the following actions
1. Arrange columns in ascending or descending order.
2. Apply filters to columns using various arithmetic and logical conditions.
3. Navigate through pages using options for first, last, previous, and next pages.
4. Optimize the report layout to fit the entire content on the page.
5. Automatically adjust column sizes based on the data within each column.
Risk Account Risk Account through which the Order was executed, if any
Client Ord ID Client Order ID received in the Centroid Bridge of the Giveup Order
Cen Ord ID Centroid unique Order ID recorded in the Centroid Bridge of the Giveup Order
Ext Client
Login
Login number of the MT4/MT5 Taker if the order is originated from a Taker of type MT4 or MT5. Otherwise, value will
be 0
Ext Client
Group
Group name of the MT4/MT5 Login from which the order was generated, if the order is originated from a Taker of type
MT4 or MT5. Otherwise, the field will display an empty value
Ext Order ID Ticket Number of the MT4/MT5 Taker if the order is originated from a Taker of type MT4 or MT5. Otherwise, value will
be 0
Send Time The Time at which the Oder was sent to the Maker
Maker The Maker that processed the Order
If Order is STP, the name of the Maker would be displayed as configured in Maker Sessions
If Order is B Book, B_BOOK will be displayed
TEM The Taker Execution Model through which the Order was processed
Symbol The traded Symbol
Liquidity
Model
The Liquidity Model used for execution
Side The side of the Order; Buy or Sell
Ord Type The type of the Order; Market, Limit or Stop
Volume The requested Volume of the Order
Fill Volume

The actual filled Volume of the Order.
Fully Filled Orders have Full Volume equal to Volume
Partially Filled Order have Fill Volume less than Volume
Rejected Orders have 0 Volume as no Volume was executed
Notional The Notional Volume of the filled order in USD
Avg Price The Weighted Average Price in case the Order was split into multiple legs
Field Description

Exporting the Giveup Order Report
To Export the Giveup Order Report
Click on “Export to CSV” or “Export to Excel” to export the report

Slippage The Slippage in decimal value which results due to price difference between request price and filled price. Slippage is
the difference between the fill price and the requested price
State The State of the Order:
Filled: Indicates a full fill of the Order
Partial: Indicates a partial fill of the Order
Rejected: Indicates an Order rejection



```

---

<a id='legs-md'></a>
### 32. `legs.md`

```markdown
[🏠 Document Start](..\README.md) / [Giveup Orders](README.md) / Legs

# Legs

Overview
The Leg Report offers a detailed overview of each order, outlining the execution process and providing relevant execution details. The
relationship between an order and its legs is one-to-many, as a single order may be divided into multiple legs when the order is filled in
more than one attempt.
The report is divided into Leg Details and Order Details, each containing relevant fields.
Request Leg Report
To request a Leg Report
1. Click on the "Toggle here to search" button.
2. Complete the Wizard as detailed below.
3. Pre-set the columns necessary for the report in the Grid Columns.
4. Click "View Results" to execute the report or directly "Export to CSV or Excel" file.
Note: Use the Reset button to clear the pre-defined filters
Note: In the above fields, any field that is left empty, apart from dates, implies that all values are included in the search
Start Date The Start Date of your desired search interval
End Date The End Date of your desired search interval
Ext Client
Group
MT4/MT5 Group number for Takers of type MT4/MT5
Ext Client
Login
MT4/MT5 Login number for Takers of type MT4/MT5
Ext Order
ID
MT4/MT5 Ticket Number for Takers of type MT4/MT5
Cen Ord Id Centroid Order ID
Symbol Select one or multiple Symbols from the list of Symbols
TEM Taker Execution Model(s) through which the Order was executed
Taker The Taker(s) configured in the Centroid Bridge such as FIX, MT4, MT5 and Centroid’s Trading Platform
Field Description

Display Leg Report
After generating the Leg Report, you can perform the following actions
1. Arrange columns in ascending or descending order.
2. Apply filters to columns using various arithmetic and logical conditions.
3. Navigate through pages using options for first, last, previous, and next pages.
4. Optimize the report layout to fit the entire content on the page.
5. Automatically adjust column sizes based on the data within each column.
Leg Details
Risk
Account
Risk Account through which the Order was executed, if any
Maker Select one or multiple Makers you wish to check Orders with
Grid
Columns
Columns or data fields that will be available in the report
Cen Client
OrdId
The ID of the Leg. For instance, an Order split into three legs will have Leg IDs of 0, 1 and 2
Maker The name of the Maker the Leg got it executed with
If A Book: The name of the LP that processed the Order will be displayed as configured in the Centroid Bridge
If B Book: B_BOOK will be displayed
Maker B This is relevant to B Book Orders only and discloses the Maker that provided the quote at the time the B Book Order
was executed
Time The Date and Time at which the Leg was executed
Side The side of the Order; Buy or Sell
Volume The requested Leg Volume
Fill Volume The actual filled Leg Volume which could be equal or less than the requested Volume above
Notional The Notional Volume of the filled Leg in USD
Maker
Symbol
The name of the Symbol on the Maker’s side
Field Description

Order Details
Maker
OrderID
The assigned ID of the Order returned by the Maker
Maker Cat The Maker Category or Type
Maker ExecID The Execution ID of the Leg assigned by the Maker
Fill Price The fill Price the Leg got executed at including Markup
Markup Defined Markup in decimal on top of the Price, if any
Raw Fill Price The fill Price the Leg got executed at excluding Markup
Exec Time
(ms.mic)
Order Execution Time in milliseconds and microseconds
Client Ord ID Client Order ID received in the Centroid Bridge
Cen Ord ID Centroid unique Order ID recorded in the Centroid Bridge
Ext Client
Login
Login number of the MT4/MT5 Taker if the order is originated from a Taker of type MT4 or MT5. Otherwise, value will
be 0
Ext Client
Group
Group name of the MT4/MT5 Login from which the order was generated, if the order is originated from a Taker of type
MT4 or MT5. Otherwise, the field will display an empty value
Ext Order ID Ticket Number of the MT4/MT5 Taker if the order is originated from a Taker of type MT4 or MT5. Otherwise, value will
be 0
TEM The Taker Execution Model through which the Order was processed
Symbol The traded Symbol
Liquidity
Model
The Liquidity Model used for execution
Side The side of the Order; Buy or Sell
Ord Type The type of the Order; Market, Limit or Stop
Volume The requested Volume of the Order
Fill Volume

The actual filled Volume of the Order.
Fully Filled Orders have Full Volume equal to Volume
Partially Filled Orders have Fill Volume less than Volume
Rejected Orders have 0 Volume as no Volume was executed
Notional The Notional Volume of the filled order in USD
Avg Price The Weighted Average Price in case the Order was split into multiple legs
Slippage The Slippage in decimal value which results due to price difference between request price and filled price. Slippage is
the difference between the fill price and the requested price
State The State of the Order:
Field Description

To Export the Legs Report
Click on “Export to CSV” or “Export to Excel” to export the report

Filled: Indicates a full fill of the Order
Partial: Indicates a partial fill of the Order
Rejected: Indicates an Order rejection



```

---

<a id='login-spread-client-md'></a>
### 32. `login-spread-(client).md`

```markdown
[🏠 Document Start](..\README.md) / [Markup Leg Report](README.md) / Login Spread (Client)

# Login Spread (Client)




```

---

<a id='login-spread-cover-md'></a>
### 32. `login-spread-(cover).md`

```markdown
[🏠 Document Start](..\README.md) / [Login Spread (Client)](README.md) / Login Spread (Cover)

# Login Spread (Cover)




```

---

<a id='maker-notional-chart-md'></a>
### 32. `maker-notional-chart.md`

```markdown
[🏠 Document Start](..\README.md) / [Maker Notional Report](README.md) / Maker Notional Chart

# Maker Notional Chart

Overview
The Maker Notional Chart features a visual Pie Chart illustrating the distribution of Notional Volume in USD among various Makers and the
B Book. The Total Volume is presented individually for each Maker. This visual representation provides an insightful overview of trading
volumes associated with different Makers.
Request Maker Notional Chart
To request a Maker Notional Chart Report
1. Click on the "Toggle here to search" button.
2. Complete the Wizard as detailed below.
3. Click the “Search” button
Note: Use the Reset button to clear the pre-defined filters
Note: If Symbol and Maker are left empty, the report assumes that all Symbols and Makers are selected
Start Date The Start Date of your desired search interval
End Date The End Date of your desired search interval
Symbol Select one or multiple Symbols from the list of Symbols
Note: If multiple Symbols are selected, the value shown will be the aggregated total value, not on a per Symbol basis
Maker Select one or multiple Makers to check the exposure with.
Note: Maker B Book represents the B Book exposure of the flow that has been internalized and not routed to any
Maker
Note: If multiple Makers are selected, it will show the segregated values for each Maker
Field Description

After generating the Maker Notional Chart, you can perform the following actions
Upon generating the Maker Notional Chart, you can examine the total USD Volume associated with each Maker and the B Book (if the B
Book Maker is selected).
Exporting the Maker Notional Chart
To Export the Maker Notional Chart
You can download the charts in various formats by clicking the button in the “Top Right Corner and choosing the “Preferred Format”


Note: The M next to the value represents million whereas the B represents billion (equivalent to 1 yard = 1000 M)




```

---

<a id='maker-notional-report-md'></a>
### 32. `maker-notional-report.md`

```markdown
[🏠 Document Start](..\README.md) / [Taker Notional](README.md) / Maker Notional Report

# Maker Notional Report

Overview
The Maker Notional Report provides a consolidated view of traded USD Volume categorized by individual Makers. This report is designed
to assess the total Volume directed to each Maker over a specified time interval.
Request Maker Notional Report
To request a Maker Notional Report
1. Click on the "Toggle here to search" button.
2. Complete the Wizard as detailed below.
3. Pre-set the columns necessary for the report in the Grid Columns.
4. Click "Search" to execute the report or directly "Export to CSV or Excel" file.
Note: Use the Reset button to clear the pre-defined filters
Note: If Symbol and Maker are left empty, the report assumes that all Symbols and Maker are included in the selection
Display Maker Notional Report
After generating the Maker Notional Report, you can perform the following actions
1. Arrange columns in ascending or descending order.
2. Apply filters to columns using various arithmetic and logical conditions.
3. Navigate through pages using options for first, last, previous, and next pages.
4. Optimize the report layout to fit the entire content on the page.
5. Automatically adjust column sizes based on the data within each column.
Start Date The Start Date of your desired search interval
End Date The End Date of your desired search interval
Symbol Select one or multiple Symbols from the list of Symbols
Note: If multiple Symbols are selected, the value shown will be the aggregated total value, not on a per Symbol
basis
Maker Select one or multiple Makers to check the routed Volume
Field Description

Note: To check the report corresponding to particular Symbols, you should run multiple reports corresponding to each Symbol, in which
the desired Symbol is selected solely in the Symbol field.
Exporting the Maker Notional Report
To Export the Maker Notional Report
Click on “Export to CSV” or “Export to Excel” to export the report

Maker The Maker to which the Volume corresponds
Taker
Execution
Model
The Taker Execution Model to which the Volume corresponds
Note: If one Taker Execution Model is assigned to two different Takers, the same Taker Execution Model will be
displayed twice, one time under each Taker
Total Fill
Volume
The cumulative total of all filled orders.
Total Notional
(USD)
The aggregate notional volume in USD.
Total Notional
(USD)
Readable
Format
The total notional volume in USD is displayed in a condensed format:
"K" represents 1000.
"M" represents 1 Million (1,000,000).
"B" represents 1 Billion (1,000,000,000).
Field Description



```

---

<a id='maker-orders-md'></a>
### 32. `maker-orders.md`

```markdown
[🏠 Document Start](..\README.md) / [Orders](README.md) / Maker Orders

# Maker Orders

Overview
The Maker Orders Report offers a comprehensive view of all STP Orders sent to the Maker(s), encompassing relevant execution details.
Additionally, it includes orders that have been internalized within the Centroid Bridge as “B Book”
Request Maker Report
To request a Maker Order Report
1. Click on the "Toggle here to search" button.
2. Complete the Wizard as detailed below.
3. Pre-set the columns necessary for the report in the Grid Columns.
4. Click "View Results" to execute the report or directly "Export to CSV or Excel" file.
Note: Use the Reset button to clear the pre-defined filters
Note: In the above fields, any field that is left empty, apart from dates, implies that all values are included in the search
Start Date The Start Date of your desired search interval
End Date The End Date of your desired search interval
Ext Client
Group
MT4/MT5 Group number for Takers of type MT4/MT5
Ext Client
Login
MT4/MT5 Login number for Takers of type MT4/MT5
Ext Order
ID
MT4/MT5 Ticket Number for Takers of type MT4/MT5
Cen Ord Id Centroid Order ID
Symbol Select one or multiple Symbols from the list of Symbols
TEM Taker Execution Model(s) through which the Order was executed
Taker The Taker(s) configured in the Centroid Bridge such as FIX, MT4, MT5 and Centroid’s Trading Platform
Risk
Account
Risk Account through which the Order was executed, if any
Field Description

Display Maker Report
After generating the Maker Orders Report, you can perform the following actions
1. Arrange columns in ascending or descending order.
2. Apply filters to columns using various arithmetic and logical conditions.
3. Navigate through pages using options for first, last, previous, and next pages.
4. Optimize the report layout to fit the entire content on the page.
5. Automatically adjust column sizes based on the data within each column.
Maker Order Details
Maker Select one or multiple Makers you wish to check Orders with
Grid
Columns
Columns or data fields that will be available in the report
Cen Client
Ord ID
The Leg ID of the Order which shows the Order and Leg number in the format OrderID_LegID
Maker The Maker responsible for processing the order:
If the order is STP, the displayed name of the Maker will be as configured in the Maker
If the order is B Book, "B_BOOK" will be displayed
Price The raw price advertised by the maker during the time of execution.
Avg Price The price after including the markup on top of the raw price.
Raw Avg
Price
The raw price at which the Maker filled the Order.
Volume The requested Volume of the Order
Fill Volume The actual filled Volume which could be equal or less than the requested Volume above
Notional The Notional Volume of the filled order in USD
Filled State The State of the Order:
Filled: Indicates a full fill of the Order
Partial: Indicates a partial fill of the Order
Rejected: Indicates an Order rejection
Field Description

Order Details
Exporting the Maker Order Report
To Export the Maker Order Report
Click on “Export to CSV” or “Export to Excel” to export the report


Client
Ord ID
Client Order ID received in the Bridge
Cen Ord
ID
Centroid unique Order ID recorded in the Bridge
Recv
Time
The time at which the Order was received in the Bridge
Taker The taker that initiated the Order
Symbol The traded Symbol
Side The side of the Order; Buy or Sell
Volume The requested Volume of the Order
Price Requested or Desired Price, in case of Limit or Stop Orders.
For Market Orders, it will be 0 as the Order is executed at the Market Price
Fill
Volume
The actual filled Volume of the Order.
Fully Filled Orders have Full Volume equal to Volume
Partially Filled Orders have Fill Volume less than Volume
Rejected Orders have 0 Volume as no Volume was executed
Avg Price The Weighted Average Price in case the Order was split into multiple legs
Filled
State
The State of the Order:
Filled: Indicates a full fill of the Order
Partial: Indicates a partial fill of the Order
Rejected: Indicates an Order rejection
Field Description



```

---

<a id='maker-rejection-md'></a>
### 32. `maker-rejection.md`

```markdown
[🏠 Document Start](..\README.md) / [Maker Symbol Spread History Chart](README.md) / Maker Rejection

# Maker Rejection

Overview
The Maker Rejection Report enables the examination of all orders that have been rejected by Makers on a per Leg basis. In instances of
Immediate or Cancel (IOC) execution, it is possible to have both accepted and rejected Legs within the same Order.
Request Maker Rejection Report
To request a Maker Rejection Report
1. Click on the "Toggle here to search" button.
2. Complete the Wizard as detailed below.
3. Pre-set the columns necessary for the report in the Grid Columns.
4. Click "View Results" to execute the report or directly "Export to CSV or Excel" file.
Note: Use the Reset button to clear the pre-defined filters
Note: In the above fields, any field that is left empty, apart from dates, implies that all values are included in the search
Display Maker Rejection Report
Once the Maker Rejection Report has been generated, you can do the following:
1. Arrange columns in ascending or descending order.
2. Apply filters to columns using various arithmetic and logical conditions.
3. Navigate through pages using options for first, last, previous, and next pages.
4. Optimize the report layout to fit the entire content on the page.
5. Automatically adjust column sizes based on the data within each column.
Start Date The Start Date of your desired search interval
End Date The End Date of your desired search interval
Symbol Select one or multiple Symbols from the list of Symbols
Maker The Maker that rejected/declined the Leg.
Field Description

To Export the Maker Rejection Report
Click on “Export to CSV” or “Export to Excel” to export the report
Cen Client
OrdId
The Leg ID of the Order which shows the Order and Leg number in the format OrderID_LegID
Note: An Order can be split into N Legs. The ID would look like Order_Leg1, Order_Leg2…LegN
Client Ord
Id
Client Order ID received in the Centroid Bridge
Cen Ord Id Centroid unique Order ID recorded in the Centroid Bridge which could be split into multiple Legs shown as different Cen
Client OrdId
Maker The Maker that rejected/declined the Leg
Symbol The Symbol that was traded in the rejected Order
Send Time The timestamp indicating when the rejected Order was transmitted to the Maker.
Maker
Recv Time
Sec
The timestamp indicating when the Order was received by the Maker.
Price The requested price of the Order.
Volume The requested volume of the Order.
Side The direction of the Order: Buy or Sell.
Ord Type The classification of the Order: Market, Limit, or Stop.
Time in
Force
The Fill Policy of the Order is defined as follows:
FOK: Fill or Kill, indicating that the Order can be fully filled in the requested volume.
IOC: Immediate or Cancel, indicating that the Order can be partially filled with the maximum available liquidity in the
market, and any remaining volume will be canceled.
Scale Size The Scale Size of the Order, as specified in the Maker Session Symbol Settings.
Field Description




```

---

<a id='maker-symbol-chart-md'></a>
### 32. `maker-symbol-chart.md`

```markdown
[🏠 Document Start](..\README.md) / [Maker Notional Chart](README.md) / Maker Symbol Chart

# Maker Symbol Chart

Overview
The Maker Symbol Chart is a graphical representation in the form of a Bar Chart. It illustrates the Notional Volume in USD for various
Makers and the B Book, organized on a per-Symbol basis.
Request Maker Symbol Chart
To request a Maker Symbol Chart Report
1. Click on the "Toggle here to search" button.
2. Complete the Wizard as detailed below.
3. Click the “Search” button
Note: Use the Reset button to clear the pre-defined filters
Note: If Symbol and Maker are left empty, the report assumes that all Symbols and Makers are selected
Display Maker Symbol Chart
After generating the Maker Symbol Chart, you can perform the following actions
Upon generating the Maker Symbol Chart, you can examine the total USD Volume associated with each Maker and the B Book (if the B
Book Maker is selected).
Start
Date
The Start Date of your desired search interval
End
Date
The End Date of your desired search interval
Symbol Select one or multiple Symbols from the list of Symbols
Maker Choose one or multiple Makers to assess the exposure.
Note: Maker B_Book signifies the B Book exposure of the flow that has been internalized and not routed to any specific
Maker.
Note: If multiple Makers are selected, the chart will present segregated values for each Maker.
Field Description


To Export the Maker Symbol Chart
You can download the charts in various formats by clicking the button in the “Top Right Corner and choosing the “Preferred Format”




```

---

<a id='maker-symbol-spread-history-chart-md'></a>
### 32. `maker-symbol-spread-history-chart.md`

```markdown
[🏠 Document Start](..\README.md) / [Maker Symbol Status](README.md) / Maker Symbol Spread History Chart

# Maker Symbol Spread History Chart

Overview
The Maker Symbol Spread History Chart enables the examination of historical spreads received from all Makers. The Centroid Bridge
records data at 5-minute intervals, calculating the average spread based on all ticks received during each interval. This chart provides
insights into the historical spread patterns contributed by different Makers.
Request Maker Symbol Spread History Chart
To request a Symbol Notional Chart Report
1. Click on the "Toggle here to search" button.
2. Complete the Wizard as detailed below.
3. Click the “Search” button
Note: Use the Reset button to clear the pre-defined filters
Display Maker Symbol Spread History Chart
After generating the Maker Symbol Spread History Chart, you can perform the following actions
After generating the Maker Symbol Spread History Chart, you can observe the average spreads in points for the selected Symbol provided
by the chosen Makers. The spreads are presented in various chart types within 5-minute intervals.
Start
Date
The Start Date of your desired search interval
End
Date
The End Date of your desired search interval
Maker Select one or multiple Makers from the list of Makers configured in the Centroid Bridge
Symbol Select one Symbol at a time from the available list of Symbols
Note: Only one Symbol can be selected at a time
Field Description

Exporting the Maker Notional Chart
To Export the Maker Notional Chart
You can download the charts in various formats by clicking the button in the “Top Right Corner and choosing the “Preferred Format”






```

---

<a id='maker-symbol-status-md'></a>
### 32. `maker-symbol-status.md`

```markdown
[🏠 Document Start](..\README.md) / [Maker Symbol Chart](README.md) / Maker Symbol Status

# Maker Symbol Status

Overview
The Maker Symbol Status report offers a comprehensive look into various statistical data associated with pricing and trading with the
Maker, organized on a per-Symbol basis. The Centroid Bridge captures a snapshot every 5 minutes, consolidating the information into
records with all relevant statistics for each Symbol during the specified interval.
This report serves as a valuable tool for assessing the performance of each Maker in terms of pricing and execution. It plays a crucial role
in aiding Brokers in the decision-making process regarding Maker selection.
Request Maker Symbol Status Report
To request a Maker Symbol Status Report
1. Click on the "Toggle here to search" button.
2. Complete the Wizard as detailed below.
3. Pre-set the columns necessary for the report in the Grid Columns.
4. Click "View Results" to execute the report or directly "Export to CSV or Excel" file.
Note: Use the Reset button to clear the pre-defined filters
Note: In the above fields, if Maker and Symbol are left empty, this implies that all values are included in the selection
Display Maker Symbol Status Report
After generating the Maker Symbol Status, you can perform the following actions
1. Arrange columns in ascending or descending order.
2. Apply filters to columns using various arithmetic and logical conditions.
3. Navigate through pages using options for first, last, previous, and next pages.
4. Optimize the report layout to fit the entire content on the page.
5. Automatically adjust column sizes based on the data within each column.
Start Date The Start Date of your desired search interval
End Date The End Date of your desired search interval
Maker Select one or multiple Makers from the list of Makers configured in the Centroid Bridge
Symbol Select one or multiple Symbols from the list of Symbols available in the Centroid Bridge
Field Description

Maker The name of the Maker
Symbol The name of the Symbol
Sub ID The Symbol’s market data subscription ID that is sent to the Maker upon subscription
Time The timestamp indicating when the snapshot was captured and the record was generated.
Subscribed Specifies whether we are currently subscribed to the Symbol with the Maker.
If YES, it signifies that we are subscribed to the Symbol.
If NO, it indicates that we are not subscribed to the Symbol.
Ticks Count The count of ticks or price updates received for the Symbol within the 5-minute time interval.
Avg Spread The average spread of the Symbol, represented in decimal format.
Avg Spread in
Points
The average spread of the Symbol, expressed in points.
Spread Ticks
Count
The count of ticks or price updates received for the Symbol, which served as the basis for calculating the average
spread during the current time interval.
Delayed Ticks
Count
The count of ticks or price updates that experienced delays.
Orders Count The total count of orders executed with the Maker during the specified time interval, regardless of the order size.
Each executed order is treated as a single occurrence, irrespective of the volume involved.
Long Orders The overall count of Long Orders executed with the Maker during the specified time interval, regardless of the
order size. Each executed Long Order is considered as one occurrence, irrespective of the volume involved.
Short Orders The total count of Short Orders executed with the Maker during the specified time interval, regardless of the order
size. Each executed Short Order is considered as one occurrence, regardless of the volume involved.
Avg Fill Time The average fill time, measured in microseconds, for all orders executed during the current time interval.
Avg Travel Time The average travel time, measured in microseconds, for an order to journey from the Centroid Bridge to the Maker.
Rejected Count The count of rejected orders.
Partial Fills
Count
The count of orders that experienced partial fills.
Fully Fills Count The count of orders that were completely filled.
Total Till Volume The aggregate notional volume executed with the Maker within the 5-minute time interval.
Field Description

To Export the Maker Symbol Status Report
Click on “Export to CSV” or “Export to Excel” to export the report

Average
Slippage
The average slippage, expressed in decimals, for all executed orders.
Average
Slippage Points
The average slippage, measured in points, for all executed orders.



```

---

<a id='markup-leg-report-md'></a>
### 32. `markup-leg-report.md`

```markdown
[🏠 Document Start](..\README.md) / [Markup Report](README.md) / Markup Leg Report

# Markup Leg Report

Overview
The Markup Leg Report is a profitability analysis tool designed for brokers to assess the profitability attributed to markups on a Per-Leg
basis. In the context of orders sent to the Maker, execution occurs on a per Leg basis, with an order comprising multiple Legs. This report
provides detailed insights into how markups impact profitability at the individual Leg level within multipart orders.
Request Markup Leg Report
To request a Markup Leg Report
1. Click on the "Toggle here to search" button.
2. Complete the Wizard as detailed below.
3. Pre-set the columns necessary for the report in the Grid Columns.
4. Click "View Results" to execute the report or directly "Export to CSV or Excel" file.
Note: Use the Reset button to clear the pre-defined filters
Note: In the above fields, any field that is left empty, apart from dates, implies that all values are included in the search
Start Date The Start Date of your desired search interval
End Date The End Date of your desired search interval.
Ext Client
Group
Name of MT4/MT5 Group for Takers of type MT4/MT5
Ext Client
Login
MT4/MT5 Login number for Takers of type MT4/MT5
Ext Order
ID
MT4/MT5 Ticket Number for Takers of type MT4/MT5
Cen Ord Id Centroid Order ID
Symbol Select one or multiple Symbols from the list of Symbols available in the Centroid Bridge
Field Description

After generating the Markup Leg Report, you can perform the following actions
1. Arrange columns in ascending or descending order.
2. Apply filters to columns using various arithmetic and logical conditions.
3. Navigate through pages using options for first, last, previous, and next pages.
4. Optimize the report layout to fit the entire content on the page.
5. Automatically adjust column sizes based on the data within each column.
The Markup Leg Report is divided into two sections, Leg Details and Order Details. When Order is split into multiple Legs, different Legs
will be shown on one side whereas on the other side the same Order will be shown multiple times depending on the number of Legs it was
split into.
Order Details
TEM Taker Execution Model(s) through which the Order was executed
Taker The Taker(s) configured in the Centroid Bridge such as FIX, MT4, MT5 and Centroid’s Trading Platform
Risk
Account
Risk Account through which the Order was executed, if any
Grid
Columns
Columns or data fields that will be available in the report
Note: To determine the reason and comments for rejections, ensure you include both filters when running the report.
Client Ord ID Client Order ID received in the Centroid Bridge
Cen Ord ID Centroid unique Order ID recorded in the Centroid Bridge
Ext Client
Login
Login number of the MT4/MT5 Taker if the order is originated from a Taker of type MT4 or MT5. Otherwise, value will
be 0
Ext Client
Group
Name of the MT4/MT5 Group from which the order was generated, if the order is originated from a Taker of type MT4
or MT5. Otherwise, the field will show an empty value
Ext Order
ID
Ticket number of the MT4/MT5 Taker if the order is originated from a Taker of type MT4 or MT5. Otherwise, value will
be 0
Recv Time The Time at which the Order was received and processed in the Centroid Bridge
Taker The Taker that initiated the Order
TEM The Trading Execution Model used for executing the order
Symbol The universal symbol in the bridge
Field Description

Leg Details
Taker
Symbol
The traded Symbol on Taker’s end
Side The side of the Order; Buy or Sell
Fill Volume The actual filled Volume of the Order.
Fully Filled Orders have Full Volume equal to Volume
Partially Filled Orders have Fill Volume less than Volume
Rejected Orders have 0 Volume as no Volume was executed
Notional The Notional Volume of the filled order in USD
Fill Price
Broker
The raw Fill Price of the Broker with the Maker (or B Book) excluding any markup
Fill Price
Client
The Fill Price reported back to Client which includes the markup, if any, defined in Markup Model
Total Markup The total Markup of the Order in decimal which is the difference between Broker Fill Price and Client Fill Price
Markup
USD
The total Markup of the Order converted into USD representing the Broker’s profitability on the Order
Markup WL
(%)
WL Markup in USD as per the defined WL Bid % and WL Ask %, if any, in Markup Model
Cen Client
OrdId
The ID of the Leg. For instance, an Order split into three legs will have Leg IDs of 0, 1 and 2
Maker The Maker Leg got executed with.
For A Book: The name of the Maker will be displayed
For B Book: B_BOOK will be displayed
Fill Volume The filled Volume of the Leg
Notional The Notional Volume of the Leg in USD
Fill Price
Broker
The raw Fill Price of the Broker with the Maker (or B Book) excluding any markup
Fill Price
Client
The Fill Price reported back to Client which includes the markup, if any, defined in Markup Model
Markup The Markup of the Leg in decimal which is the difference between Broker Fill Price and Client Fill Price. For Orders
split into multiple Legs, it represents the proportion of the Order executed in the Leg
Markup
USD
The Markup converted into USD representing the Broker’s profitability on the Leg. For Orders split into multiple Legs, it
represents the proportion of the Order executed in the Leg
Markup WL
(%)
WL Markup in USD as per the defined WL Bid % and WL Ask %, if any, in Markup Model. For Orders split into multiple
Legs, it represents the proportion of the Order executed in the Leg
Field Description

To Export the Markup Leg Report
Click on “Export to CSV” or “Export to Excel” to export the report




```

---

<a id='markup-report-md'></a>
### 32. `markup-report.md`

```markdown
[🏠 Document Start](..\README.md) / [Symbol Notional](README.md) / Markup Report

# Markup Report

Overview
The Markup Report functions as a pivotal tool for profitability analysis, granting brokers the ability to discern the financial impact of
markups on a per-order basis. By offering detailed insights into the relationship between markups and financial performance, this report
enables brokers to precisely evaluate how markups influence the profitability of each individual order.
Request Markup Report
To request a Markup Report
1. Click on the "Toggle here to search" button.
2. Complete the Wizard as detailed below.
3. Pre-set the columns necessary for the report in the Grid Columns.
4. Click "View Results" to execute the report or directly "Export to CSV or Excel" file.
Note: Use the Reset button to clear the pre-defined filters
Note: In the above fields, any field that is left empty, apart from dates, implies that all values are included in the search
Start Date The Start Date of your desired search interval
End Date The End Date of your desired search interval.
Ext Client
Group
Name of MT4/MT5 Group for Takers of type MT4/MT5
Ext Client
Login
MT4/MT5 Login number for Takers of type MT4/MT5
Ext Order
ID
MT4/MT5 Ticket Number for Takers of type MT4/MT5
Cen Ord Id Centroid Order ID
Symbol Select one or multiple Symbols from the list of Symbols available in the Centroid Bridge
Field Description

After generating the Markup Report, you can perform the following actions
1. Arrange columns in ascending or descending order.
2. Apply filters to columns using various arithmetic and logical conditions.
3. Navigate through pages using options for first, last, previous, and next pages.
4. Optimize the report layout to fit the entire content on the page.
5. Automatically adjust column sizes based on the data within each column.
TEM Taker Execution Model(s) through which the Order was executed
Taker The Taker(s) configured in the Centroid Bridge such as FIX, MT4, MT5 and Centroid’s Trading Platform
Risk
Account
Risk Account through which the Order was executed, if any
Grid
Columns
Columns or data fields that will be available in the report
Note: To determine the reason and comments for rejections, ensure you include both filters when running the report.
Client Ord
ID
Client Order ID received in the Centroid Bridge
Cen Ord ID Centroid unique Order ID recorded in the Centroid Bridge
Ext Client
Login
Login number of the MT4/MT5 Taker if the order is originated from a Taker of type MT4 or MT5. Otherwise, value will be
0
Ext Client
Group
Name of the MT4/MT5 Group from which the order was generated, if the order is originated from a Taker of type MT4 or
MT5. Otherwise, the field will show an empty value
Ext Order
ID
Ticket number of the MT4/MT5 Taker if the order is originated from a Taker of type MT4 or MT5. Otherwise, value will be
0
Recv Time The Time at which the Oder was received and processed in the Centroid Bridge
Taker The Taker that initiated the Order
TEM The Trading Execution Model within the Taker from where the Order was placed
Symbol The traded Symbol
Field Description

To Export the Markup Report
Click on “Export to CSV” or “Export to Excel” to export the report

Side The side of the Order; Buy or Sell
Fill Volume The filled Volume of the Order
Notional The Notional Volume in USD
Fill Price
Broker
The raw Fill Price of the Broker with the Maker (or B Book) excluding any markup
Fill Price
Client
The Fill Price reported back to Client which includes the markup, if any, defined in Markup Model
Markup The Markup in decimal which is the difference between Broker Fill Price and Client Fill Price
Markup
USD
The Markup converted into USD representing the Broker’s profitability on the Order
Markup WL
(%)
WL Markup in USD as per the defined WL Bid % and WL Ask %, if any, in Markup Model



```

---

<a id='mt4-reports-md'></a>
### 32. `mt4-reports.md`

```markdown
[🏠 Document Start](..\README.md) / [Fills](README.md) / MT4 Reports

# MT4 Reports

Overview
The MT4 Report enables users to review all MT4 Orders generated by any MT4 Taker within the Centroid Bridge. It provides a
comprehensive display of these orders as they appear in MT4, along with pertinent execution details.
Request MT4 Report
To request an MT4 Report:
1. Click on the "Toggle here to search" button.
2. Complete the Wizard as detailed below.
3. Pre-set the columns necessary for the report in the Grid Columns.
4. Click "View Results" to execute the report or directly "Export to CSV or Excel" file.
Note: Use the Reset button to clear the pre-defined filters
Note: In the above fields, any field that is left empty, apart from dates, implies that all values are included in the search
Start Date The Start Date of your desired search interval
End Date The End Date of your desired search interval.
Ext Client
Group
Name of MT4/MT5 Group for Takers of type MT4/MT5
Ext Client
Login
MT4/MT5 Login number for Takers of type MT4/MT5
Ext Order
ID
MT4/MT5 Ticket Number for Takers of type MT4/MT5
Cen Ord Id Centroid Order ID
Symbol Select one or multiple Symbols from the list of Symbols available in the Centroid Bridge
TEM Taker Execution Model(s) through which the Order was executed
Taker The Taker(s) configured in the Centroid Bridge such as FIX, MT4, MT5 and Centroid’s Trading Platform
Risk
Account
Risk Account through which the Order was executed, if any
Field Description

Display MT4 Report
After generating the MT4 Report, you can perform the following actions
1. Arrange columns in ascending or descending order.
2. Apply filters to columns using various arithmetic and logical conditions.
3. Navigate through pages using options for first, last, previous, and next pages.
4. Optimize the report layout to fit the entire content on the page.
5. Automatically adjust column sizes based on the data within each column.
Grid
Columns
Columns or data fields that will be available in the report
Note: To determine the reason and comments for rejections, ensure you include both filters when running the report.
Client Ord ID The Client (Taker) Order ID
Cen Ord ID Centroid unique Order ID recorded in the Centroid Bridge
Ext Client Login The Login number of the MT4 Account
Ext Client
Group
The name of the MT4 Group
Ext Order ID MT4 ticket number
Open Time The Time at which the MT4 Order was opened
Taker The name of the MT4 Taker that initiated the Order
Taker Execution
Model
The name of the TEM through which the Order was routed
Symbol The traded Symbol
Taker Symbol The Symbol name on the Taker’s side
Side The side of the Order; Buy or Sell
Ord Type The category of the executed Order, whether it is Market or Limit.
Time in Force

The Fill Policy of the Order:
FOK (Fill or Kill): This signifies that the Order can be entirely filled at the specified volume or canceled if full
execution is not immediately possible.
Field Description

To Export the MT4 Report
Click on “Export to CSV” or “Export to Excel” to export the report

IOC (Immediate or Cancel): In this case, the Order can be partially filled with the maximum available liquidity in the
market, and any remaining volume will be canceled.
Volume The specified MT4 Volume is calculated based on the notional value, where Volume equals the product of MT4 lots
and the Symbol Contract Size.
Volume = MT4 Lots x Symbol Contract Size
Fill Volume The volume that has been successfully executed and remains open for the MT4 Order.
Open Price The Open Price of the MT4 Order
Close Volume The Close Volume of the MT4 Order
Close Price The Close Price of the MT4 Order
Close Time The Time at which the MT4 Order was closed
Slippage The Slippage in decimal which is the difference between the fill price and the requested price
State The effective filled Volume of the Order.
Fully Filled: Orders exhibit a Full Volume equivalent to the specified Volume.
Partially Filled: Orders have a Fill Volume that is less than the specified Volume.
Rejected: Orders show 0 Volume since no Volume was executed.
Exec Time
(ms.mic)
Order Execution Time in milliseconds and microseconds



```

---

<a id='mt5-reports-md'></a>
### 32. `mt5-reports.md`

```markdown
[🏠 Document Start](..\README.md) / [MT4 Reports](README.md) / MT5 Reports

# MT5 Reports

Overview
The MT5 Report enables users to review all MT5 Orders generated by any MT5 Taker within the Centroid Bridge. It provides a
comprehensive display of these orders as they appear in MT5, along with all pertinent execution details.
Request MT5 Report
To request an MT5 Report:
1. Click on the "Toggle here to search" button.
2. Complete the Wizard as detailed below.
3. Pre-set the columns necessary for the report in the Grid Columns.
4. Click "View Results" to execute the report or directly "Export to CSV or Excel" file.
Note: Use the Reset button to clear the pre-defined filters
Note: In the above fields, any field that is left empty, apart from dates, implies that all values are included in the search
Start Date The Start Date of your desired search interval
End Date The End Date of your desired search interval.
Ext Client
Group
Name of MT4/MT5 Group for Takers of type MT4/MT5
Ext Client
Login
MT4/MT5 Login number for Takers of type MT4/MT5
Ext Order
ID
MT4/MT5 Ticket Number for Takers of type MT4/MT5
Cen Ord Id Centroid Order ID
Symbol Select one or multiple Symbols from the list of Symbols available in the Centroid Bridge
TEM Taker Execution Model(s) through which the Order was executed
Taker The Taker(s) configured in the Centroid Bridge such as FIX, MT4, MT5 and Centroid’s Trading Platform
Risk
Account
Risk Account through which the Order was executed, if any
Grid
Columns
Columns or data fields that will be available in the report
Note: To determine the reason and comments for rejections, ensure you include both filters when running the report.
Field Description

Display MT5 Report
After generating the MT5 Report, you can perform the following actions
1. Arrange columns in ascending or descending order.
2. Apply filters to columns using various arithmetic and logical conditions.
3. Navigate through pages using options for first, last, previous, and next pages.
4. Optimize the report layout to fit the entire content on the page.
5. Automatically adjust column sizes based on the data within each column.
Client Ord
ID
The Client (Taker) Order ID
Cen Ord ID Centroid unique Order ID recorded in the Centroid Bridge
Ext Client
Login
The Login number of the MT5 Account
Ext Client
Group
The name of the MT5 Group
Ext Order
ID
MT5 Order ID Number
Open Time The Time at which the MT5 Order was opened
Taker The name of the MT5 Taker that initiated the Order
Taker
Execution
Model
The name of the TEM through which the Order was routed
Symbol The traded Symbol
Taker
Symbol
The name of the Symbol on the Taker's side.
Side The side of the Order; Buy or Sell
Ord Type The category of the executed Order, whether it is Market or Limit.
Time in
Force

The Fill Policy of the Order:
FOK (Fill or Kill): This signifies that the Order can be entirely filled at the specified volume or canceled if full execution
is not immediately possible.
Field Description

To Export the MT5 Report
Click on “Export to CSV” or “Export to Excel” to export the report

IOC (Immediate or Cancel): In this case, the Order can be partially filled with the maximum available liquidity in the
market, and any remaining volume will be canceled.
Volume The specified MT5 Volume is calculated based on the notional value, where Volume equals the product of MT4 lots and
the Symbol Contract Size.
Volume = MT5 Lots x Symbol Contract Size
Fill Volume The Filled Open Volume of the MT5 Order
Open Price The Open Price of the MT5 Order
Close
Volume
The Close Volume of the MT5 Order
Close Price The Close Price of the MT5 Order
Close Time The Time at which the MT5 Order was closed
Slippage The slippage, represented in decimal form, indicates the variance between the fill price and the requested price.
State The effective filled Volume of the Order.
Fully Filled: Orders exhibit a Full Volume equivalent to the specified Volume.
Partially Filled: Orders have a Fill Volume that is less than the specified Volume.
Rejected: Orders show 0 Volume since no Volume was executed.
Exec Time
(ms.mic)
Order Execution Time in milliseconds and microseconds



```

---

<a id='net-per-login-md'></a>
### 32. `net-per-login.md`

```markdown
[🏠 Document Start](..\README.md) / [Slippage Leg Report](README.md) / Net Per Login

# Net Per Login

Overview
The Per Net Login Report provides a detailed summary of the overall Net Open Positions, encompassing both A-Book and B-Book Net
Open Positions. This report aggregates the Net Open Positions on a per Symbol basis, delivering valuable insights into trading activities
for enhanced analysis and understanding.
When searching for Takers like MT4 and MT5, the report also furnishes external information in the form of Client Login details. This
additional feature enhances the comprehensiveness of the report by including pertinent data related to client logins associated with
platforms such as MT4 and MT5.
Request Net Per Login Report
To request a Net Per Login Report
1. Click on the "Toggle here to search" button.
2. Complete the Wizard as detailed below.
3. Pre-set the columns necessary for the report in the Grid Columns.
4. Click "View Results" to execute the report or directly "Export to CSV or Excel" file.
Note: Use the Reset button to clear the pre-defined filters
Note: In the above fields, any field that is left empty implies that all values are included in the selection
Display Net Per Login Report
After generating the Net Per Login Report, you can perform the following actions
Ext Client
Login
The Login number of the MT4/MT5 Account. You may enter multiple comma separated Logins
Party
Symbol
Party Symbol is the Symbol name on the Taker’s side, as set up in the Taker Feeds.
You may select one or multiple Party Symbols from the list
Symbol Select one or multiple Symbols from the list of Symbols available in the Centroid Bridge
Hide Zero
Net
Choose whether to display the Logins with no Open Positions or not.
If ticked, the generated report will hide all rows with zero net open positions
If un-ticked, the generated report will still display the rows showing logins with zero net open positions
Field Description

1. Arrange columns in ascending or descending order.
2. Apply filters to columns using various arithmetic and logical conditions.
3. Navigate through pages using options for first, last, previous, and next pages.
4. Optimize the report layout to fit the entire content on the page.
5. Automatically adjust column sizes based on the data within each column.
Ext Client
Login
Login number of the MT4/MT5 Taker
Party
Symbol
The Symbol name on the Taker’s side
Ext Client
Login
The Symbol name as configured in Symbols
Net The Total Net Open Position in Notional Volume denominated in the Base Currency consolidates both buy and sell
positions, effectively offsetting each other. It's important to note that a negative value signifies a short net open position
(sell), whereas a positive value indicates a long net open position (buy).
Net Buy The Buy Net Open Position signifies the combined Notional Volume in the Base Currency for all buy positions. This
metric is specifically designed to highlight the volume of open positions where clients have adopted a long (buy)
position in the market. It provides a targeted insight into the overall volume associated with clients taking a bullish
stance.
Net Sell The Sell Net Open Position relates to the total Notional Volume in the Base Currency attributed to all sell positions. This
metric exclusively portrays the volume of open positions wherein clients have assumed a short (sell) position in the
market. It offers a focused perspective on the overall volume associated with clients adopting a bearish stance.
ANet The Comprehensive Net Open Position of A-Book Orders, denominated in Notional Volume in the Base Currency,
amalgamates both buy and sell A-Book positions, efficiently balancing each other out. It's crucial to recognize that a
negative value indicates a short net open position (sell), while a positive value signifies a long net open position (buy).
This metric offers an all-encompassing perspective on the overall A-Book exposure, presenting insights into volume
and directional bias.
ANet Buy The Buy Net Open Position for A-Book Orders, measured in Notional Volume in the Base Currency, represents the
aggregated volume of all buy positions within the A-Book. This metric specifically focuses on the cumulative volume
associated with clients taking a long (buy) position in the market within the A-Book segment.
ANet Sell The Sell Net Open Position for A-Book Orders, quantified in Notional Volume in the Base Currency, signifies the
combined volume of all sell positions within the A-Book. This metric exclusively reflects the aggregated volume of open
positions where clients have opted for a short (sell) stance in the market within the A-Book segment.
BNet The Total Net Open Position of B-Book Orders, expressed in Notional Volume in the Base Currency, consolidates both
buy and sell B-Book positions, effectively offsetting each other. It's important to note that a negative value signifies a
Field Description

To Export the Net Per Login Report
Click on “Export to CSV” or “Export to Excel” to export the report


short net open position (sell), while a positive value indicates a long net open position (buy). This metric provides a
comprehensive overview of the overall B-Book exposure in terms of volume and directional bias.
BNet Buy The Buy Net Open Position for A-Book Orders, measured in Notional Volume in the Base Currency, represents the
cumulative volume of all buy positions within the A-Book. This metric specifically focuses on the combined volume
associated with clients taking a long (buy) position in the market within the A-Book segment.
BNet Sell The Sell Net Open Position for B-Book Orders, quantified in Notional Volume in the Base Currency, signifies the
aggregated volume of all sell positions within the B-Book. This metric exclusively reflects the combined volume of open
positions where clients have chosen a short (sell) stance in the market within the B-Book segment.



```

---

<a id='orders-md'></a>
### 32. `orders.md`

```markdown
[🏠 Document Start](..\README.md) / [TEM Position Upload](README.md) / Orders

# Orders

Overview
The Orders Report offers a summary of an order blotter, presenting a comprehensive view of all individual orders placed through the
Centroid Bridge, originating from various Takers like: MT4, MT5, FIX, and others.
Much like the Trading section, the Orders Report features two distinct views: Broker and Trader.
You have visibility over all Orders originating from different Takers connected to the Centroid Bridge. Brokers can search and retrieve
Orders using different search and filtration criteria.
Request Order Report
To request an Order Report
1. Click on the "Toggle here to search" button.
2. Complete the Wizard as detailed below.
3. Pre-set the columns necessary for the report in the Grid Columns.
4. Click "View Results" to execute the report or directly "Export to CSV or Excel" file.
Note: Use the Reset button to clear the pre-defined filters
Note: In the above fields, any field that is left empty implies that all values are included in the search
Start Date The Start Date of your desired search interval
End Date The End Date of your desired search interval.
Ext Client
Group
Name of MT4/MT5 Group for Takers of type MT4/MT5
Ext Client
Login
MT4/MT5 Login number for Takers of type MT4/MT5
Ext Order
ID
MT4/MT5 Ticket Number for Takers of type MT4/MT5
Cen Ord Id Centroid Order ID
Symbol Select one or multiple Symbols from the list of Symbols available in the Centroid Bridge
TEM Taker Execution Model(s) through which the Order was executed
Field Description

Display Order Report
After generating the Orders Report, you can perform the following actions
1. Arrange columns in ascending or descending order.
2. Apply filters to columns using various arithmetic and logical conditions.
3. Navigate through pages using options for first, last, previous, and next pages.
4. Optimize the report layout to fit the entire content on the page.
5. Automatically adjust column sizes based on the data within each column.
Taker The Taker(s) configured in the Centroid Bridge such as FIX, MT4, MT5 and Centroid’s Trading Platform
Risk
Account
Risk Account through which the Order was executed, if any
Grid
Columns
Columns or data fields that will be available in the report
Note: To determine the reason and comments for rejections, ensure you include both filters when running the report.
Client Ord
ID
Client Order ID received in the Centroid Bridge
Cen Ord ID Centroid unique Order ID recorded in the Centroid Bridge
Ext Client
Login
Login number of the MT4/MT5 Taker if the order is originated from a Taker of type MT4 or MT5. Otherwise, value will be
0
Ext Client
Group
Name of the MT4/MT5 Group from which the order was generated, if the order is originated from a Taker of type MT4 or
MT5. Otherwise, the field will show an empty value
Ext Order
ID
Ticket number of the MT4/MT5 Taker if the order is originated from a Taker of type MT4 or MT5. Otherwise, value will be
0
Recv Time The Time at which the Order was received and processed in the Centroid Bridge
Taker The Taker that initiated the Order
Taker
Execution
Model
The Trading Execution Model used for executing the order
Symbol The universal symbol in the bridge
Field Description

Exporting the Order Report
To Export the Order Report
Click on “Export to CSV” or “Export to Excel” to export the report
Taker
Symbol
The traded Symbol on Taker’s end
Liquidity
Model
The Liquidity Model used for execution
Side The side of the Order; Buy or Sell
Ord Type The type of the Order; Market, Limit or Stop
Volume The requested Volume of the Order
Price Requested or Desired Price, in case of Limit or Stop Orders.
For Market Orders, it will be 0 as the Order is executed at the Market Price
Fill Volume The actual filled Volume of the Order.
Fully Filled Orders have Full Volume equal to Volume
Partially Filled Orders have Fill Volume less than Volume
Rejected Orders have 0 Volume as no Volume was executed
Notional
Volume
The Notional Volume of the filled order in USD
Avg Price The Weighted Average Price in case the Order was split into multiple legs
Fill State

The State of the Order:
Filled: Indicates a full fill of the Order
Partial: Indicates a partial fill of the Order
Rejected: Indicates an Order rejection
Slippage The Slippage in decimal value which results due to price difference between request price and filled price. Slippage is
the difference between the fill price and the requested price
Ext
Markup
This is relevant to MT4/MT5 Takers and consists of the Markup at the level of MT4/MT5 group in decimal points
B% The B Book percentage of the Order
A Vol The requested A Book volume
B Vol The requested B Book volume
A Fill The filled A Book Volume
B Fill The filled B Book Volume
Sender The Taker through which the Order was initiated
Exec Time
(ms.mic)
Order Execution Time in milliseconds and microseconds





```

---

<a id='risk-account-statement-md'></a>
### 32. `risk-account-statement.md`

```markdown
[🏠 Document Start](..\README.md) / [MT5 Reports](README.md) / Risk Account Statement

# Risk Account Statement

Overview
The Risk Account Statement offers Brokers and Traders (Risk Users) a comprehensive view of Risk Accounts, allowing them to review
both Trade and Account information. Moreover, the Risk Account Statement is categorized into three tabs, providing access to historical
reports, statements, as well as real-time trade and account details.
Request Risk Account Statement
To request a Risk Account Statement
1. Click on the "Toggle here to search" button.
2. Complete the Wizard as detailed below.
3. Click the “Search” button
4. Export the statement to HTML
Note: Use the Reset button to clear the pre-defined filters
Display Risk Account Statement
After generating the Risk Account Statement, you can perform the following actions
The Risk Account Statement is divided into three components: Closed Transactions, Positions and Account Balance
Start Date The Start Date of your desired search interval
End Date The End Date of your desired search interval
Risk
Account
Choose a specific Risk Account from the array of Risk Accounts configured in the Centroid Bridge.
Field Description


Closed Transactions
The Closed Transactions Report, positioned at the top, displays all balance transactions impacting the Risk Account Balance.
This includes transactions like Deposits, Withdrawals, Realized Profit/Loss, Swaps, Commissions, and more.
Ticket The unique ID of the balance transactions
Open Time The Date and Time at which the balance transaction request was sent to the Centroid Bridge
Volume This is relevant only if the balance transaction is a PL in FIFO mode where the closed Volume is shown. In case it
corresponds to another type of balance transaction not related to trading such as Deposit or Withdrawal the value
would be 0
Amt The amount in USD deposited into or deducted from the Risk Account.
Type The category of the balance transaction is identified by the following types:
PL [Profit & Loss]: Represents a closed order in FIFO mode.
Commission: Signifies the commission deducted from the Risk Account.
Swaps: Denotes swaps applied to the Risk Account.
Deposit: Indicates a transaction involving a deposit into the Risk Account.
Withdraw: Represents a withdrawal from the Risk Account.
Credit: Refers to a credit transaction, either in or out.
Other: Encompasses other types of in/out balance operations that may be conducted for balance adjustment
purposes.
Symbol The Symbol involved in the event of a balance transaction representing a closed trade. Otherwise, the field will display
an empty value.
Cur Currency of the Risk Account, USD
Open Price The Open Price of the Order being closed, if Balance Transaction is a PL. For other Balance Transactions, this column
will show 0
Open Cen
Order
The Order ID of the Open Position if Balance Transaction is a PL resulting from a partial or full closing of a Position.
For other Balance Transactions, this column will show an empty value
Close Time The Close Time of the Position if Balance Transaction is a PL resulting from partial or full Position closure. For other
Balance Transactions, this column will show an empty value
Close Price The Close Price of the Order being closed, if the balance transaction is a PL. Otherwise, this column will show 0
Field Description

Open Positions
The Open Positions tab displays the comprehensive view of all net open positions within the Risk Account, consolidated on a per-Symbol
basis.
Closed Cen
Order
The Order ID for closing a Position is indicated in the case of a PL, Commission, or Swaps balance transaction. For
other balance transactions, this column will display 0.
Transaction
Time
The Time at which the amount resulting from Balance Transaction was added or deducted from the Account
Comment The Comment field is either automatically generated or manually entered:
Manual: For non-trade-related transactions like Deposits, Withdrawals, Credits, and Adjustments, it will exhibit the
value manually input by the user into the Comment field during the execution of account balance operations.
Automatic: For trade-related transactions such as realized PL, commissions, and Swaps, the comment is
automatically populated, revealing the open and closed price of the Order. This is particularly applicable when
closing two Orders against each other.
Total
Commission
s
The aggregate of all incurred Commissions within the specified time frame.
Total Swaps The cumulative total of all accrued/paid Swaps within the designated time period.
Total
Realized PL
The cumulative total of all Realized Profit and Loss (PL) arising from Trades throughout the chosen time period.
Total
Deposits
The total accumulation of all Deposits executed in the Account within the specified time frame.
Total
Withdrawal
The aggregate of all Withdrawals subtracted from the Account within the specified time frame.
Total Credit The cumulative amount of Net Credits (in or out) within the specified time interval.
Pos ID The ID number of the Position
Symbol The Open Position Symbol
Risk
Account
The name of the selected Risk Account
Field Description

Account Balance
The Account Balance tab provides live updates on key Account Balance details for the Risk Account, including information on Balance,
Equity, Margin, floating Profit/Loss (PL), and more.
Liquidity
Model
The Liquidity Model assigned to the Risk Account which defines the pool of Makers
Net Volume The Notional Volume of the Position in USD
ANet
Volume
The Notional Volume of the STP Position in USD
BNet
Volume
The Notional Volume of the B Book Position in USD
Avg Price The Weighted Average Price of the orders comprising the position.
AAvg Price The Weighted Average Price of the STP orders forming the position.
BAvg Price The Weighted Average Price of the B-Book orders forming the position.
Last Time The Last Time the real-time data of the Position were updated
Close Price The current market price of the symbol.
PL The floating Profit/Loss of the symbol determined by the open positions.
Margin The existing Utilized or Blocked Margin associated with the open positions of the symbol. This reflects the margin
amount currently allocated or reserved for the symbol's open positions.
Swaps The cumulative unrealized Swap charges applied to the open positions. This represents the total accrued swap fees on
the currently active positions.
Commission
s
The commissions incurred upon the initiation of the positions. This refers to the total commission charges associated
with the opening of the positions.
Total
Unrealized
Swaps
The total of all unrealized swaps associated with open positions across all symbols. This includes the collective amount
of swap charges that have accrued but not yet been realized for open positions.
Total
Unrealized
PL
The overall unrealized Profit/Loss (PL) of the Risk Account. This encompasses the total unrealized financial gain or
loss across all open positions within the account.


To Export the Risk Account Statement
Click on “Export to HTML” to export the statement
Name The Name of the selected Risk Account
Margin
Blocked
The utilized Margin amount in the Account Currency (USD). This represents the extent of Margin that has been
employed in USD within the account.
Balance The accessible balance within the Risk Account. This denotes the remaining funds that are available for trading or
withdrawal after considering existing positions and any reserved margin.
Available to
Withdraw
The available withdrawal amount, equivalent to the Free Margin, is calculated as follows:
Available Withdraw=Equity−Margin Blocked−Credit
This represents the amount that can be withdrawn, factoring in the current Equity, blocked margin, and credit in the
Risk Account.
Equity The Equity of the Risk Account signifies the total current value of the account, encompassing both the open positions
and available balance
PL The floating Profit/Loss (PL) of the Risk Account represents the unrealized gains or losses associated with open
positions.
Margin Level The Margin Level Percentage for the Risk Account is calculated as follows:
Margin Level=Equity/Margin Blocked × 100
This percentage indicates the relationship between the account's Equity and the blocked Margin, serving as a crucial
measure of risk exposure and available margin for trading.
Commission The total unrealized Commission charged in USD on all Open Positions
Note: These Commissions remain unrealized (only affect Equity) until the Position or part of the Position is closed, and
then it will affect the Balance based on the closed Volume
Swaps The total unrealized Swaps charged in USD on the Risk Account on a per Symbol basis for keeping positions
overnight, if any.
Note: These Swaps remain unrealized (only affect Equity) until the Position or part of the Position is closed, and then it
will affect the Balance based on the closed Volume
Notional The aggregated USD exposure of the Risk Account in Notional Volume represents the total financial commitment of
the account across all positions.
Credit The available credit extended to the Risk Account in USD, if applicable. This signifies the amount of credit that the
account is currently eligible to utilize.
Trading
State
The Trading State of the Risk Account is as follows:
STOPPED OUT: The Risk Account is either flat or negative, possibly resulting from a stop-out or an imbalance in
the account.
MARGIN CALL: The Risk Account is under a Margin Call when the Margin Level reaches or falls below the
percentage specified in the Warn Level set for the Account.
NEUTRAL: The Risk Account is adequately funded and in a neutral state.
Field Description




```

---

<a id='slippage-leg-report-md'></a>
### 32. `slippage-leg-report.md`

```markdown
[🏠 Document Start](..\README.md) / [Slippage Report](README.md) / Slippage Leg Report

# Slippage Leg Report

Overview
The Slippage Report enables the assessment of slippage on orders, considering the variance between the requested price and the actual
filled price on a per Leg basis. Slippage can be advantageous for the client if positive, indicating a better fill, or disadvantageous if
negative, favoring the broker. Additionally, the Slippage Leg feature allows tracking of slippages the client experiences from the Maker on a
per Leg basis, particularly relevant when an order is executed in multiple Legs.
Request Slippage Leg Report
To request a Slippage Leg Report
1. Click on the "Toggle here to search" button.
2. Complete the Wizard as detailed below.
3. Pre-set the columns necessary for the report in the Grid Columns.
4. Click "View Results" to execute the report or directly "Export to CSV or Excel" file.
Note: Use the Reset button to clear the pre-defined filters
Note: In the above fields, any field that is left empty, except for Start and End Dates, implies that all values are included in the selection
Start Date The Start Date of your desired search interval
End Date The End Date of your desired search interval
Ext Client
Group
MT4 / MT5 Group number for Takers of type MT4/MT5
Ext Client
Login
MT4 / MT5 Login number for Takers of type MT4/MT5
Ext Order ID MT4 / MT5 Order ID Number for Takers of type MT4/MT5
Cen Ord Id Centroid Order ID
Symbol Select one or multiple Symbols from the list of Symbols
Taker The Taker(s) configured in the Centroid Bridge such as FIX, MT4, MT5 and Centroid’s Trading Platform
TEM Taker Execution Model through which the Order was executed
Risk Account Risk Account through which the Order was executed, if any
Field Description

After generating the Slippage Leg Report, you can perform the following actions
1. Arrange columns in ascending or descending order.
2. Apply filters to columns using various arithmetic and logical conditions.
3. Navigate through pages using options for first, last, previous, and next pages.
4. Optimize the report layout to fit the entire content on the page.
5. Automatically adjust column sizes based on the data within each column.
Leg Details
Maker Slippage Leg
Maker Select one or multiple Makers from the list.
For B Book Orders, they will be under B_BOOK Maker
Grid Columns Columns or data fields that will be available in the report
Cen Client
OrdId
The ID of the Leg. For instance, an Order split into three legs will have Leg IDs of 0, 1 and 2
Maker The Maker Leg that was either executed or provided the quote for B Book Orders.
Send Time The timestamp indicating when the Leg was transmitted to the Maker.
Fill Volume The volume that has been filled for the Leg.
Notional The notional volume of the Leg, expressed in USD.
Raw Fill Price The raw price at which the Leg was filled with the Maker, excluding all markups.
Fill Price The fill price of the Leg, which includes the Centroid Bridge markup.
Price The request price of the Leg, originating from the Centroid Bridge to the Maker.
Maker
Symbol
The symbol name on the Maker's side.
Field Description
Field Description

Order Details
Exporting the Slippage Leg Report
To Export the Slippage Leg Report
Click on “Export to CSV” or “Export to Excel” to export the report
Expected
Price
The requested price of the Leg.
Fill Price The actual fill price of the Leg.
Slippage The slippage, expressed in decimal form, is the difference between the requested price and the actual fill price for the
Leg.
Slippage
USD
The slippage, when converted into USD, reflects the monetary difference between the requested price and the actual
fill price for the Leg.
The slippage, when converted into USD
Positive slippage indicates the Order was filled at a better price.
Negative slippage indicates the Order was filled at a worse price.
A slippage of 0 means the Order was filled without any slippage.
Client Ord ID Client Order ID received in the Centroid Bridge
Cen Ord ID Centroid unique Order ID recorded in the Centroid Bridge
Recv Time The timestamp indicating when the Order was received and processed in the Centroid Bridge.
Taker The Taker responsible for initiating the Order.
TEM The trading execution model within the Taker from which the Order was placed.
Symbol The Symbol that was traded.
Taker Symbol The Symbol that was traded on the Taker's end.
Side The direction of the Order: Buy or Sell.
Fill Volume The volume that has been filled for the Order.
Notional The notional volume of the Order, expressed in USD.
Avg Price The VWAP (Volume Weighted Average Price) fill price reported back to the client after the Order has been filled.
Field Description





```

---

<a id='slippage-report-md'></a>
### 32. `slippage-report.md`

```markdown
[🏠 Document Start](..\README.md) / [Maker Rejection](README.md) / Slippage Report

# Slippage Report

Overview
The Slippage Report facilitates the identification of slippage on orders, arising from the variance between the requested price and the
actual filled price on an individual order basis. Slippage may favor the client when positive (indicating a better fill) or favor the broker when
negative (indicating a worse fill).
Request Slippage Report
Request Slippage Report
1. Click on the "Toggle here to search" button.
2. Complete the Wizard as detailed below.
3. Pre-set the columns necessary for the report in the Grid Columns.
4. Click "View Results" to execute the report or directly "Export to CSV or Excel" file.
Note: Use the Reset button to clear the pre-defined filters
Note: In the above fields, any field that is left empty, except for Start and End Dates, implies that all values are included in the selection
Start Date The Start Date of your desired search interval
End Date The End Date of your desired search interval.
Ext Client
Group
Name of MT4/MT5 Group for Takers of type MT4/MT5
Ext Client
Login
MT4/MT5 Login number for Takers of type MT4/MT5
Ext Order
ID
MT4/MT5 Ticket Number for Takers of type MT4/MT5
Cen Ord Id Centroid Order ID
Symbol Select one or multiple Symbols from the list of Symbols available in the Centroid Bridge
TEM Taker Execution Model(s) through which the Order was executed
Taker The Taker(s) configured in the Centroid Bridge such as FIX, MT4, MT5 and Centroid’s Trading Platform
Risk
Account
Risk Account through which the Order was executed, if any
Field Description

After generating the Slippage Report, you can perform the following actions
1. Arrange columns in ascending or descending order.
2. Apply filters to columns using various arithmetic and logical conditions.
3. Navigate through pages using options for first, last, previous, and next pages.
4. Optimize the report layout to fit the entire content on the page.
5. Automatically adjust column sizes based on the data within each column.
Primary Details
Limit Order Slippage
Grid
Columns
Columns or data fields that will be available in the report
Note: To determine the reason and comments for rejections, ensure you include both filters when running the report.
Client Ord ID Client Order ID received in the Centroid Bridge
Cen Ord ID Centroid unique Order ID recorded in the Centroid Bridge
Recv Time The timestamp indicating when the Order was received and processed in the Centroid Bridge.
Taker The Taker that initiated the Order
TEM The trading execution model within the Taker from which the Order originated.
Symbol The Symbol that was traded.
Taker Symbol The Symbol that was traded on the Taker's end.
Side The direction of the Order: Buy or Sell.
Ord Type The classification of the Order: Market, Limit, Stop, etc.
Fill Volume The volume that has been filled for the Order.
Notional The notional volume of the Order, expressed in USD.
Avg Price The VWAP (Volume Weighted Average Price) fill price communicated to the client after the Order has been
successfully filled.
Field Description

Order Slippage Broker
Client Order Slippage Ext
Exporting the Slippage Report
To Export the Slippage Report
Click on “Export to CSV” or “Export to Excel” to export the report
Expected
Price
The specified price sent with the Limit Order.
Fill Price The actual fill price achieved by the broker, which is either equal to or better than the expected price.
Slippage The slippage, expressed in decimal format, is the difference between the requested price and the actual fill price. It is
either 0 or a positive number.
Slippage
USD
The slippage, converted into USD, is either 0 or a positive value since there is no worse fill in the case of a Limit Order.
Field Description
Expected
Price
The price at which the Centroid Bridge processed the Order request.
Fill Price The actual price at which the broker's Order is filled.
Slippage The slippage, in decimal form, represents the difference between the requested price and the actual fill price.
Slippage
USD
The slippage, when converted into USD
Positive slippage indicates the Order was filled at a better price.
Negative slippage indicates the Order was filled at a worse price.
A slippage of 0 means the Order was filled without any slippage.
Field Description
Expected
Price
The request price from a client's perspective is equivalent to the available price on the client's platforms at the time the
Order was placed. This encompasses all markups, including those from Centroid and MT4/MT5.
Fill Price The actual fill price reported back to the client includes all markups, such as those from Centroid and MT4/MT5.
Slippage The slippage, expressed in decimal form for the client, is the difference between the client's requested price and the
actual fill price.
Slippage
USD
The slippage, when converted into USD, is interpreted as follows:
Positive slippage indicates the Order was filled at a better price.
Negative slippage indicates the Order was filled at a worse price.
A slippage of 0 means the Order was filled without any slippage.
Field Description





```

---

<a id='symbol-detail-chart-md'></a>
### 32. `symbol-detail-chart.md`

```markdown
[🏠 Document Start](..\README.md) / [Symbol Notional Chart](README.md) / Symbol Detail Chart

# Symbol Detail Chart

Overview
The Symbol Detail Chart offers a visual representation of the Daily Notional Volume in USD traded for a specific Symbol within a user-
selected time interval. This chart provides a granular view, allowing users to explore in-depth details and observe the evolution of Volume
throughout a chosen day.
Request Symbol Detail Chart
To request a Symbol Detail Chart
1. Click on the "Toggle here to search" button.
2. Complete the Wizard as detailed below.
3. Click the “Search” button
Note: Use the Reset button to clear the pre-defined filters
Display Symbol Detail Chart
After generating the Symbol Detail Chart, you can perform the following actions
Upon generating the Symbol Detail Chart, users can access the total traded USD Volume for the selected Symbol. Furthermore, users
have the capability to delve deeper into specific days and times, gaining insights into how the Volume has changed over the designated
period.
Start Date The Start Date of your desired search interval
End Date The End Date of your desired search interval
Symbol Select one or multiple Symbols from the list of Symbols
Note: If multiple Symbols are selected, the report will shows the Total Volume for each of the selected Symbols
Field Description

To Export the Symbol Detail Chart
You can download the charts in various formats by clicking the button in the “Top Right Corner and choosing the “Preferred Format”



```

---

<a id='symbol-notional-chart-md'></a>
### 32. `symbol-notional-chart.md`

```markdown
[🏠 Document Start](..\README.md) / [Net Per Login](README.md) / Symbol Notional Chart

# Symbol Notional Chart

Overview
The Symbol Notional Chart is a graphical representation in the form of a bar chart, visually illustrating the Notional Volume in USD traded
throughout the entirety of the Centroid Bridge.
Request Symbol Notional Chart
To request a Symbol Notional Chart Report
1. Click on the "Toggle here to search" button.
2. Complete the Wizard as detailed below.
3. Click the “Search” button
Note: Use the Reset button to clear the pre-defined filters
Note: If Symbol is left empty, the report assumes that all Symbols are selected
Display Symbol Notional Chart
After generating the Symbol Notional Chart, you can perform the following actions
1. The Symbol Notional Chart visually represents Notional Volume in USD traded across the entire Centroid Bridge.
2. Once generated, this chart enables you to analyze the total USD Volume for each selected Symbol using Bar Charts.
3. The displayed dates vary depending on the chosen time interval, with shorter intervals presenting more days on the chart.
4. For instance, a 2-month time interval displays weekly results instead of daily, whereas a 2-week interval includes figures for all days
within that timeframe.
Start Date The Start Date of your desired search interval
End Date The End Date of your desired search interval
Symbol Select one or multiple Symbols from the list of Symbols
Note: If multiple Symbols are selected, the report will shows the Total Volume for each of the selected Symbols
Field Description

To Export the Symbol Notional Chart
You can download the charts in various formats by clicking the button in the “Top Right Corner and choosing the “Preferred Format”
Symbol The traded Symbol to check the Volume for
Total Fill Volume The cumulative total of all filled orders.
Total Notional
(USD)
The aggregate notional volume in USD.
Total Notional
(USD) Readable
Format
The total notional volume in USD is displayed in a condensed format:
"K" represents 1000.
"M" represents 1 Million (1,000,000).
"B" represents 1 Billion (1,000,000,000).
Field Description




```

---

<a id='symbol-notional-md'></a>
### 32. `symbol-notional.md`

```markdown
[🏠 Document Start](..\README.md) / [Symbol Detail Chart](README.md) / Symbol Notional

# Symbol Notional

Overview
The Symbol Notional Report is a visual representation that displays the Total Volume traded across the entire Centroid Bridge. This report
aggregates the data on a per Symbol basis, offering a comprehensive overview of trading activity for individual symbols within the given
time frame.
Request Symbol Notional Report
To request a Symbol Notional Report
1. Click on the "Toggle here to search" button.
2. Complete the Wizard as detailed below.
3. Click the “Search” button
Note: Use the Reset button to clear the pre-defined filters
Note: If Symbol is left empty, the report assumes that all Symbols are included in the selection
Display Symbol Notional Report
After generating the Symbol Notional Report, you can perform the following actions
Upon generating the Symbol Notional Report, users have the capability to view the aggregated Volume, providing a detailed breakdown
for each Symbol individually. This feature allows for a granular examination of trading activity at the level of each specific symbol within the
report.
Start Date The Start Date of your desired search interval
End Date The End Date of your desired search interval
Symbol Select one or multiple Symbols from the list of Symbols
Note: If multiple Symbols are selected, the report will shows the Total Volume for each of the selected
Symbols
Field Description

To Export the Slippage Report
Click on “Export to CSV” or “Export to Excel” to export the report

Symbol The traded Symbol to check the Volume for
Total Fill Volume The cumulative total of all filled orders.
Total Notional (USD) The aggregate notional volume in USD.
Total Notional (USD)
Readable Format
The total notional volume in USD is displayed in a condensed format:
"K" represents 1000.
"M" represents 1 Million (1,000,000).
"B" represents 1 Billion (1,000,000,000).
Field Description



```

---

<a id='taker-notional-md'></a>
### 32. `taker-notional.md`

```markdown
[🏠 Document Start](..\README.md) / [BBook Profitability Report](README.md) / Taker Notional

# Taker Notional

Overview
The Taker Notional Report presents a consolidated view of traded USD Volume, organized by individual Takers and Taker Execution
Models. This report facilitates an examination of the total Volume generated by each Taker, along with insights into Taker Execution Models
representing specific Accounts within a Taker.
Request Taker Notional Report
To request a Taker Notional Report
1. Click on the "Toggle here to search" button.
2. Complete the Wizard as detailed below.
3. Pre-set the columns necessary for the report in the Grid Columns.
4. Click "Search" to execute the report or directly "Export to CSV or Excel" file.
Note: Use the Reset button to clear the pre-defined filters
Note: If Symbol, Taker and/or Taker Execution Model are left empty, the report assumes that all Symbols, Takers and Taker Execution
Models are included in the selection
Display Taker Notional Report
After generating the Taker Notional Report, you can perform the following actions
1. Arrange columns in ascending or descending order.
2. Apply filters to columns using various arithmetic and logical conditions.
3. Navigate through pages using options for first, last, previous, and next pages.
4. Optimize the report layout to fit the entire content on the page.
Start Date The Start Date of your desired search interval
End Date The End Date of your desired search interval
Symbol Select one or multiple Symbols from the list of Symbols.
Note: If multiple Symbols are selected, the value shown will be the aggregated total value, not on a per Symbol basis
Taker Select one or multiple Takers
Taker
Execution
Model
Select one or multiple Taker Execution Models
Note: If multiple Taker Execution Models are selected, the total values shown will be the aggregated values for Each
Taker Execution Model within a Taker
Field Description

5. Automatically adjust column sizes based on the data within each column.
Note: To check the report corresponding to particular Symbols, you should run multiple reports corresponding to each Symbol, in which
the desired Symbol is selected solely in the Symbol field.
Exporting the Taker Notional Report
To Export the Taker Notional Report
Click on “Export to CSV” or “Export to Excel” to export the report

Taker The Taker to which the Volume corresponds
Taker
Execution
Model
The Taker Execution Model to which the Volume corresponds
Note: If one Taker Execution Model is assigned to two different Takers, the same Taker Execution Model will be
displayed twice, one time under each Taker
Total Fill
Volume
The cumulative total of all filled orders.
Total Notional
(USD)
The aggregate notional volume in USD.
Total Notional
(USD)
Readable
Format
The total notional volume in USD is displayed in a condensed format:
"K" represents 1000.
"M" represents 1 Million (1,000,000).
"B" represents 1 Billion (1,000,000,000).
Field Description



```

---

<a id='trade-transactions-md'></a>
### 32. `trade-transactions.md`

```markdown
[🏠 Document Start](..\README.md) / [Risk Account Statement](README.md) / Trade Transactions

# Trade Transactions

Overview
The Trade Transaction Report serves as a comprehensive account statement, enabling Brokers to review a detailed history of all balance
transactions impacting the Risk Account Balance.
This report provides valuable insights into the various financial activities that have influenced the overall balance of the account.
Request Trade Transaction
To request a Trade Transaction Report:
1. Complete the Wizard as detailed below.
2. Click the “Search” button
Display Trade Transaction
After generating the Trade Transaction, you can perform the following actions
Upon requesting the Trade Transaction, you gain visibility into a range of Balance Transactions that occurred, influencing the Risk Account
throughout the chosen time interval. This feature allows you to examine and understand the diverse financial activities impacting the
account during the specified duration.
Start Date The Start Date of your desired search interval
End Date The End Date of your desired search interval
Risk Account Choose a specific Risk Account from the array of Risk Accounts configured in the Centroid Bridge.
Field Description
Ticket The unique ID of the balance transactions
Open Time The Date and Time at which the balance transaction request was sent to the Centroid Bridge
Volume This information is applicable specifically to balance transactions involving PL in FIFO mode, where the closed
Volume is displayed. If the transaction corresponds to another type, unrelated to trading, such as Deposit or
Field Description

Withdrawal, the value will be 0.
Amt The USD amount either deposited into or deducted from the Risk Account. This value reflects the financial impact of
transactions involving deposits or withdrawals in USD.
Type The category of the balance transaction is identified by the following types:
PL [Profit & Loss]: Represents a closed order in FIFO mode.
Commission: Signifies the commission deducted from the Risk Account.
Swaps: Denotes swaps applied to the Risk Account.
Deposit: Indicates a transaction involving a deposit into the Risk Account.
Withdraw: Represents a withdrawal from the Risk Account.
Credit: Refers to a credit transaction, either in or out.
Other: Encompasses other types of in/out balance operations that may be conducted for balance adjustment
purposes.
Symbol The Symbol involved in the event of a balance transaction representing a closed trade. Otherwise, the field will
display an empty value.
Cur Currency of the Risk Account, USD
Open Price The Open Price of the Order being closed, if Balance Transaction is a PL. For other Balance Transactions, this
column will show 0
Open Cen
Order
The Order ID of the Open Position if Balance Transaction is a PL resulting from a partial or full closing of a Position.
For other Balance Transactions, this column will show an empty value
Close Time The Close Time column indicates the closing time of the position if the balance transaction is a Profit/Loss (PL)
resulting from partial or full position closure. For other balance transactions, this column will display an empty value.
Close Price The Close Price column indicates the closing price of the order if the balance transaction is a Profit/Loss (PL).
Otherwise, this column will display a value of 0.
Closed Cen
Order
The Order ID for closing a position is displayed if the balance transaction corresponds to a Profit/Loss (PL),
Commission, or Swaps. For other balance transactions, this column will indicate 0. This differentiation helps identify
the specific order involved in the closure process for relevant transactions and highlights instances where the column
remains inactive for other types of balance transactions.
Transaction
Time
The timestamp indicating when the amount resulting from the balance transaction was added or deducted from the
account.
Comment The Comment field is either automatically generated or manually entered:
Manual: For non-trade-related transactions like Deposits, Withdrawals, Credits, and Adjustments, it will exhibit
the value manually input by the user into the Comment field during the execution of account balance operations.
Automatic: For trade-related transactions such as realized PL, commissions, and Swaps, the comment is
automatically populated, revealing the open and closed price of the Order. This is particularly applicable when
closing two Orders against each other.
Total
Commissions
The aggregate of all incurred Commissions within the specified time frame.
Total Swaps The cumulative total of all accrued/paid Swaps within the designated time period.
Total Realized
PL
The cumulative total of all Realized Profit and Loss (PL) arising from Trades throughout the chosen time period.

To Export the Trade Transaction Report
Click “Export” and select “Export to Excel” or “Export to CSV”

Total
Deposits
The total accumulation of all Deposits executed in the Account within the specified time frame.
Total
Withdrawal
The aggregate of all Withdrawals subtracted from the Account within the specified time frame.
Total Credit The cumulative amount of Net Credits (in or out) within the specified time interval.



```

---

<a id='positions-readme-md'></a>
### 32. `positions/README.md`

```markdown
[🏠 Document Start](..\..\README.md) / [Reports](..\README.md) / Positions

# Positions

Overview
The Positions report offers an up-to-the-minute summary of the aggregate open positions within one or more Risk Accounts, Taker
Execution Models, or a combination thereof. The report presents positions on a per-Account and per-Symbol basis.
This report allows Brokers to effortlessly monitor all net open positions and employ filtering options to examine those associated with a
specific Risk Account or Taker Execution Model.
Request a Position Report
To request a Position Report:
1. Click on the "Toggle here to search" button.
2. Complete the Wizard as detailed below.
3. Click on the "Search" button to execute the report.
Note: Use the Reset button to clear the pre-defined filters
Note: If the above fields are left empty, all values pertaining to the above fields will be included in the search
Display Position Report
After generating the Position Report, you can perform the following actions
The Positions Report is displayed on a per Risk Account/Taker Execution Model and Symbol basis.
Symbol Select one or multiple Symbols
Taker Select one of multiple Takers
Type The Type of Account
Taker Execution Model: To check the Open Positions of one or multiple Taker Execution Models and/or Makers
Risk Account: To Check the Open Positions of a Risk Account which may contain one or multiple Taker/Taker
Execution Models
All Models: A combination of both Risk Accounts and Taker Execution Models and/or Makers
Taker
Execution
Model
Select one or multiple Risk Accounts, Taker Execution Models, Makers or a combination of all, depending on the Type
selected in the previous field
Field Description

Within the Position Report, you have the capability to:
1. Click the "Columns" button to add and display additional columns related to Positions, which are initially hidden.
2. Apply various arithmetic and logical conditions to filter columns.
3. Export the Maker Positions Report to identify any disparities between actual Trades and Net Positions on the Maker's side, potentially
resulting from a Centroid Bridge crash or unplanned restart.
4. Verify discrepancies between Trades and Net Open Positions on the Maker's side.
5. Export the Taker Positions Report to examine any inconsistencies between actual Trades and Net Positions on the Taker's side,
possibly stemming from a Centroid Bridge crash or unplanned restart.
6. Verify discrepancies between Trades and Net Open Positions on the Taker's side.
7. Export the list of Open Positions to an Excel or CSV file.
8. Click the arrow button to view the list of Orders comprising the Positions. This feature is relevant to Risk Accounts only.
9. Click the "Refresh" or the right arrow button to update the Positions and access real-time information.
Pos ID The ID number of the Position
Symbol The Symbol that has the open position
Taker
Execution
Model
The Taker Execution Model that has the open position.
Note: All B Book orders that were not processed by any Makers will display B_BOOK in this column
Taker The Taker under which the Taker Execution Model is set up.
Field Description

Risk
Account
The name of the Risk Account that holds the open position
Note: This column would appear only if requested Type is Risk Account. If Type is Taker Execution Model or All Models,
this column would display an empty value
Account
Type
The type of Account that holds the open position
Client: If position belongs to a client, Taker/Risk Account
Provider: If the position belongs to a Maker or B Book
Liquidity
Model
The Liquidity Model assigned to the Trading Account which specifies the Maker(s) the open position is held with
Net Volume The Net Open Positions in notional value.
Short Symbols show a negative value and are highlighted in Red
Long Symbols show a positive value and are highlighted in Blue
ANet
Volume
The Net Open Positions of all STP trades in notional value
BNet
Volume
The Net Open Positions of all B Book trades in notional value
Avg Price The Weighted Average Price of all deals that form the position
AAvg Price The Weighted Average Price of STP Position
BAvg Price The Weighted Average Price of B Book Position
Last Time The Last Time the real-time data of the Position were updated
Close Price The current Market Price
PL The current floating (unrealized) P/L which is the difference between Close Price and Avg Price multiplied by Net
Volume
Margin The current Blocked Margin of the Position
Swaps This is relevant to Position pertaining to a Risk Account and shows accumulated Swap charges that have been charged
on Open Positions
Commission

This is relevant to Position pertaining to a Risk Account and shows commission charges that have been charged on
Open Positions
Base
Exposure
The Notional Volume in Base Currency
Quote
Exposure
The Notional Volume in Quote Currency
Base Cur
Exposure
This Base Volume converted into Risk Account Currency
Note: For Positions that do not correspond to a Risk Account, it will show exactly the same value as Base Exposure
Quote Cur
Exposure
The Quote Volume converted into Risk Account Currency
Note: For Positions that do not correspond to a Risk Account, it will show exactly the same value as Quote Exposure
BBase
Exposure
The Notional Volume in Base Currency of the B Book Positions

As indicated in the preceding step, you have the option to expand the Position further to inspect the various Orders beneath that constitute
the Position.
BQuote
Exposure
The Notional Volume in Quote Currency of the B Book Positions
BBase Cur
Exposure
This Base Volume of the B Book Positions converted into Risk Account Currency
Note: For Positions that do not correspond to a Risk Account, it will show exactly the same value as BBase Exposure
BQuote Cur
Exposure
The Quote Volume of the B Book Positions converted into Risk Account Currency
Note: For Positions that do not correspond to a Risk Account, it will show exactly the same value as BQuote Exposure
Markup The Markup in decimal, if any, that was applied to the Open Positions
Margin
Conv Rate
The Margin Conversion rate from Base Currency into USD
PL Conv
Rate
The Profit Conversion rate from Quote currency into USD
Actions Allows to check the Orders that make up the Position, in the event of having an aggregated position, and perform
closing actions and adjustments for accounting purposes
Note: This is only relevant to Positions pertaining to Risk Accounts
Seq ID A sequential ID number of the Order
Cen Ord ID The Centroid Bridge Order ID of the Order
Price The Price at which the Order was opened
Volume The Notional Volume in Base Currency of the Order. The Volume decreases when another Order of opposite side is
placed using the FIFO mode
Time The Date and Time at which the Order was opened
Actions Allows to close an Order to decrease the overall Position. This does not send the Order to processing. It merely closes
it on the Centroid Bridge for Accounting purposes
Field Description

Position Upload
The functionality to upload positions is provided for Risk Account and the Taker Execution Model (TEM).
Risk Account:
The Risk Account Position Upload feature can be utilized when you want to increase or decrease the exposure or volume.
TEM:
The TEM Position Upload feature can be utilized to replace the existing values with new ones.
For more detailed information, please refer to the following pages within the Positions section:
Exporting the Positions Report
To Export the Position Report
Click on “Export to CSV” or “Export to Excel” to export the report






```

---

<a id='positions-risk-account-position-upload-md'></a>
### 32. `positions/risk-account-position-upload.md`

```markdown
[🏠 Document Start](..\..\README.md) / [Reports](..\README.md) / [Positions](README.md) / Risk Account Position Upload

# Risk Account Position Upload

Overview
In this module, you will learn how to upload positions using the Upload Feature for Risk Accounts. Also when uploading positions, it is
strongly recommended to use the correct template to prevent errors.
Guide to Uploading Positions in Risk Accounts
1. Select the Risk Account Template from the drop-down list.
2. Click the Download icon to obtain the template.
3. Complete the Excel file using the field descriptions below.
4. Upload the completed file to the Bridge.
Symbol EURUSD The name of the Symbol as defined under Symbols
Taker Symbol EURUSD.a
ma
The name of Taker Symbol which is allocated for the particular Taker
Taker Execution
Model
TEM-1 The name of the Taker Execution Model where the exposure needs to be adjusted & is linked to
the specific Risk Account
Taker Centroid_M
T5
The name of the Taker for which the exposure needs to be adjusted & is linked to the specific Risk
Account
Taker Feed Test_Feed The name of the Taker Feed linked to this Risk Account
Risk Account The name of the Risk Account for which the exposure needs to be adjusted
Liquidity Model Liquidity_M
odel
The Liquidity Model linked to the Execution Model
Net Volume 10,000 The Net Open Positions must be the sum of ANet and BNet Volumes
ANet Volume 5,000 The volumes to be adjusted (added/deducted) for the A Book Positions.
BNet Volume 5,000 The volumes to be adjusted (added/deducted) for the B Book Positions.
Field Possible
Values
Description

Notes:
To increase exposure or volume: Enter the amount to be Added in the Excel sheet.
To decrease exposure or volume: Enter the amount to be Deducted using a negative value.
Avg Price 1.08644 The Weighted Average Price of all deals that form the position
AAvg Price 1.08114 The Weighted Average Price of A Book Position
BAvg Price 1.08644 The Weighted Average Price of B Book Position
Close Price 1.07094 The expected close price for this position.
Note: The close price will be overridden by the current market price. This field will be useful during
market close hours to provide an estimated P&L.
Please exercise caution, as changes made after the upload cannot be undone.


```

---

<a id='positions-tem-position-upload-md'></a>
### 32. `positions/tem-position-upload.md`

```markdown
[🏠 Document Start](..\..\README.md) / [Positions](..\README.md) / [Positions](README.md) / TEM Position Upload

# TEM Position Upload

Overview
In this module, you will learn how to upload positions using the Upload Feature for Taker Execution Model. Also when uploading positions,
it is strongly recommended to use the correct template to prevent errors.
Guide to Uploading Positions in TEM
1. Select the Taker Execution Model Template from the drop-down list.
2. Click the Download icon to obtain the template.
3. Complete the Excel file using the field descriptions below.
Upload the completed file to the Bridge.
Symbol EURUSD The name of the Symbol as defined under Symbols
Taker Execution
Model
TEM-1 The name of the Taker Execution Model where the exposure needs to be adjusted
Taker Centroid_M
T5
The name of the Taker for which the exposure needs to be adjusted
Liquidity Model Liquidity_M
odel
The Liquidity Model linked to the Execution Model
Net Volume 10,000 The Net Open Positions must be the sum of ANet and BNet Volumes
ANet Volume 5000 The volumes to be adjusted (added/deducted) for the A Book Positions.
BNet Volume 5000 The volumes to be adjusted (added/deducted) for the B Book Positions.
Avg Price 1.08644 The Weighted Average Price of all deals that form the position
AAvg Price 1.08114 The Weighted Average Price of A Book Position
BAvg Price 1.08644 The Weighted Average Price of B Book Position
Field Possible
Values
Description

Notes:
The uploaded file will overwrite all existing values for the TEM

Close Price 1.07094 The expected close price for this position.
Note: The close price will be overridden by the current market price. This field will be useful during
market close hours to provide an estimated P&L.
Please exercise caution, as changes made after the upload cannot be undone.


```

---
