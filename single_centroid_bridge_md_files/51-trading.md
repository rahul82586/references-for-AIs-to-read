# 📁 51-trading

- **Generated:** 2026-09-10 12:09
- **Total Files:** 4
- **Source:** `C:\Users\DELL\Downloads\backend_code-main (1)\backend_code-main (2)\bridge_manual_md\51-trading`

---

## 📑 Table of Contents

1. [README.md](#readme-md)
2. [market-watch.md](#market-watch-md)
3. [push-ticks.md](#push-ticks-md)
4. [trading-platform.md](#trading-platform-md)

---

## 🌲 Project Structure

```
51-trading/
├── market-watch.md
├── push-ticks.md
├── README.md
└── trading-platform.md
```

---

## 📄 Files

<a id='readme-md'></a>
### 4. `README.md`

```markdown
[🏠 Document Start](..\README.md) / Trading

# Trading

The Trading Module allows configuration, usage, and viewing of Market Watch, Trading Platform, and Push Ticks. Upon clicking the
“Trading” button on the left-hand side menu, it expands to show the different components underneath which are explained in greater detail
hereunder.




```

---

<a id='market-watch-md'></a>
### 4. `market-watch.md`

```markdown
[🏠 Document Start](..\README.md) / [Trading](README.md) / Market Watch

# Market Watch

Overview
The Market Watch allows Brokers to view prices coming through the different Taker Feeds defined in the Centroid Bridge including the full
depth of the market. This also allows Brokers to test price connectivity with Makers and the Taker Feed when a new Maker is added or
upon adding a new instrument with a Maker.
Within this module, you have the capability to:
Add or Remove Symbol from List: Include or exclude symbols from the list.
View Prices with Full Market Depth: Observe prices in panels with extensive market depth and adjustable based on Taker Feed and
Maker level.
View Prices as List with TOB: Explore prices presented as a list with the Top of Book (TOB) highlighted.
Adding a Symbol to the List
To add a Symbol to the Market Watch list
1. Click the dropdown button “Toggle here to add/remove Symbol”.
2. Fill it in with the relevant information. You may refer to the field descriptions hereafter.
3. Click the “Add / Remove Symbol” button to submit the changes.
Deleting a Symbol from the List
To delete a Symbol from the list
1. Click the dropdown button “Toggle here to add/remove Symbol”.
Taker
Feed
Select a Taker Feed from the list of available Taker Feeds. You can also add multiple Taker Feeds.
Symbol Select one or multiple Symbols pertaining to the selected Taker Feed for which you want to see the price.
Field Description

2. In the Symbol textfield, search and choose your desired Symbol. Once you hover your mouse to the selected symbol, you may click the
“x” button next to it if you wish to remove it from the list. Alternatively, you can simplify the deletion by clicking the “x” button on the top
right side of the panel.
3. Click the “Add / Remove Symbol” button to submit the changes.
Panel View
In the panel, you can view the price of each Symbol separately. Selected Symbols will appear in a separate panel on which all the pricing-
related information is shown.
Symbol name with configured suffix from Taker Feed
Bid and Ask indicator with green upward arrow for an increase and red downward arrow for a decrease
TOB quantity or available liquidity on the Bid and Ask side
TOB Bid price and TOB Ask price
Spread at TOB in decimals (e.g., 000002 for a 2 pip spread)
Time of the last received price
Full depth of available liquidity sizes on the Bid and Ask side (below TOB)
Full depth of available liquidity prices on the Bid and Ask side (below TOB)


List View
In the panel, you can view the TOB price of each Symbol along with other relevant information.
FAQ
What could be the reason why a particular symbol is not pricing on the Taker Feed level?
Symbol The selected Taker Feed Symbol(s).
Bid Price The Bid Price at the top of the book (TOB).
Ask Price The Ask Price at the top of the book (TOB).
Spread The Spread at the top of the book (TOB) expressed in decimal form. For instance, a spread of 0.00005 on a 5-digit
EURUSD symbol corresponds to 0.5 pips and 5 points.
Spread
Points
The spread at the top of the book (TOB) expressed in points. For instance, a spread points of 2 corresponds to
0.00002 on a 5-digit EURUSD symbol.
Bid Volume The Bid liquidity currently available at the top of the book (TOB).
Ask Volume The Ask liquidity currently available at the top of the book (TOB).
Bid Maker The Maker streaming the Bid liquidity.
Ask Maker The Maker streaming the Ask liquidity.
Last
Updated
The timestamp indicating when the price was last updated.
LTP Price The Last Traded Price.
LTP Volume The Last Traded Price Volume.
Field Description
To troubleshoot, follow these steps:
1. Ensure the Taker Feed is enabled.
2. Check if you have assigned a working Liquidity Model.
3. Check if the assigned Maker is sending prices for that particular Symbol to the Centroid Bridge. You can check this by navigating to
Monitoring -> Maker Status, as detailed in the manual.


```

---

<a id='push-ticks-md'></a>
### 4. `push-ticks.md`

```markdown
[🏠 Document Start](..\README.md) / [Trading Platform](README.md) / Push Ticks

# Push Ticks

Overview
The Push Ticks component allows pushing prices manually as a Maker into Taker Feeds in the event of stale prices.
This functionality has several uses and is mainly used for B Book execution, allowing to settle B Book Positions at a certain close price
such as Risk Account Adjustment, Position Adjustments, and Expired Future Symbol.
Symbol Selection
To select the Symbol into which the ticks will be pushed
1. Click the dropdown button “Toggle here to add/remove Symbol”.
2. Fill it in with the relevant information. You may refer to the field descriptions hereafter.
3. Click the “Add / Remove Symbol” button to submit the changes.
Push Ticks Manually
To push the ticks manually
Once you have selected the desired parameter, you will be presented will a panel pertaining to the selected Symbol through which you can
push the ticks manually.
1. Fill in the Bid and Ask volumes and prices as highlighted below. You may refer to the field descriptions hereafter.
2. Click the “Submit” button to push the tick.
Makers Select a Maker into which the Orders will be executed.
Taker Feed Select a Taker Feed into which the ticks will be pushed.
Symbol Select a Symbol into which the ticks will be pushed. By doing this, you are pushing ticks to that specific symbol only.
Field Description

Symbol The selected Symbol.
Makers The selected Maker.
Bid The Bid Price to be pushed.
Ask The Ask Price to be pushed.
LTP Price The Last Traded Price to be pushed.
Bid Volume The Bid Volume to be pushed along with the Bid Price which defines the available liquidity for order execution.
Ask
Volume
The Ask Volume to be pushed along with the Ask Price which defines the available liquidity for order execution.
LTP
Volume
The Last Traded Price Volume to be pushed along with the LTP Price which defines the available liquidity for order
execution.
Field Description


```

---

<a id='trading-platform-md'></a>
### 4. `trading-platform.md`

```markdown
[🏠 Document Start](..\README.md) / [Market Watch](README.md) / Trading Platform

# Trading Platform

Overview
The Trading Platform provides Brokers with direct access to the market to trade directly with their Liquidity Providers (Makers). Through
the Trading Panel, Brokers have access to the liquidity book allowing them to see the full depth of the market across all Symbols. Brokers
can trade using different order types as well as execution modes such as Market, Limit, Stop, IOC, FOK, and so on.
The Trading Platform component consists of a Trading Panel, Order Logs, Positions, and Account Balance.
Trading Panel
Similar to Market Watch, the Trading Panel displays full pricing information about the Symbol. Additionally, through this panel, Brokers can
place different types of orders using different execution methods. One symbol panel can be used at a time.
Adding a Symbol
To add a Symbol to trade on
1. Click the dropdown button “Toggle here to add/remove Symbol”.
2. Fill it in with the relevant information. You may refer to the field descriptions hereafter.
3. Click the “Add / Remove Symbol” button to submit the changes.
Risk Account / Taker
Execution Model
You may choose a Risk Account with its dedicated Taker Feed and Taker Execution Model to trade on or an
individual Taker Execution Model.
Note: If a Risk Account is chosen, then any order will be subject to all configurations within the Risk Account
and will affect the Risk Account balance and positions.
Risk Account Choose a particular Risk Account from the dropdown list.
Note: If Taker Execution Model is initially selected above, this field will be greyed out.
Taker The Taker to trade on.
Taker Execution
Model
The Taker Execution Model within the chosen Taker to trade on.
Field Description

Note: To add another Symbol to trade on, you just need to repeat the same process above and replace the current Symbol with the new
one in the Symbol field.
Once a Symbol has been added, Brokers can click on the “Sell” or “Buy” buttons from the Symbol panel to send “Sell” or “Buy” orders.

Taker Feed The Taker Feed within the chosen Taker to show prices on the Trading Panel.
Symbol The Symbol to trade on.
Note: Only one Symbol can be chosen at a time.
One Click Trading Defines whether the One Click Trading setting is enabled or disabled.
Enable: Order is placed once the trade button is clicked.
Disable: Order requires an additional confirmation prior to sending it through.
TOB Price

Sends the Top of the Book Price as target price for Orders of types Limit or Stop which require Request Price.
Enable: Sends the TOB Price as a Request Price for Orders of types Limit or Stop.
Disable: User needs to manually input the Request Price for Orders of types Limit or Stop.
Symbol Symbol to trade on as configured in Taker Feeds.
Maker Liquidity Price information of the Symbol as explained in Market Watch component.
Ord Type Order Type which specifies the type of order being sent:
Market: Order is executed at the current Market Price.
Limit: Order is executed at the requested or better price. If price is worse than the requested price, then
order will get rejected.
Stop: Order is executed at requested or worse price.
Volume Quantity the order size in notional volume.
Field Description

Note: It is important to ensure that the Taker Feed is showing prices and the Trading Account (Taker Execution Model) are assigned to the
same Liquidity Models and Markup Models to ensure that you are trading with the correct prices being displayed, hence getting price
updates from the same Makers (LP).
Order Logs
The Order Logs panel is an Order blotter that shows each Order executed through the Trading Platform at different stages of the
execution.
Within this module, you have the capability to:
Filter and Look Up Orders: Search orders by different criteria.
Navigate to Previous Page: Move to the previous page by clicking the "Previous" button.
Navigate to Next Page: Move to the next page by clicking the "Next" button.
Navigate to Desired Page: Go to a specific page by entering the page number into the textbox.
Price Defines the desired price. For Market orders, no price is sent along with the order request. Order always gets
executed at the market price. As for Limit and Stop orders, you can specify the desired price.
Validity Specifies the execution mode:
IOC: Allows partial filling of an order in case the requested quantity cannot be fully filled.
FOK: Does not allow partial filling. If the order cannot be entirely filled, it will get rejected.
Deviation Defines the deviation away from the price. This is only applicable for Orders of types Limit and Stop and
specifies the deviation in pips that is acceptable if the price improves or worsens for Orders of types Limit and
Stop respectively.
Example: If a buy Order of Limit type is sent at 1.13850 with a deviation of 1.0, the Order can still be filled if
the price worsens by up to 1 pip (10 points) so it can be executed at a worse price up to 1.13840. Any price
above 1.13840 is acceptable whereas if price drops below 1.13840, the order will be rejected.
Ext Order ID An MT4/MT5 order number linked to the order.
Ext Client Login An MT4/MT5 login number linked to the order.
Ext Client Group An MT4/MT5 Group linked to the order.
Sell Button sends a SELL order.
Buy Button sends a BUY order.

Time The time at which the order was received / created / executed.
Client Ord Id The Client Order ID received in the Centroid Bridge.
Cen Order Id The Centroid Order ID generated.
Fill State The status of the Order being sent. For each order, it goes at least through 3 stages. New, Created, and a Final post-
order stage depending on the result which usually comes from the Maker:
New: Indicates that the Order was received in the Centroid Bridge.
Created: Indicates that the Centroid Bridge is ready to dispatch the Order.
Filled: Indicates that the order has been filled.
Rejected: Indicates that Order has been rejected.
Partially Filled: Indicates that Order has been filled in partial with the quantity filled. The Centroid Bridge will
attempt to fill the remaining quantity and there is another order associated whose status could be filled, in case it
fully fills the remaining quantity or partially filled in case the remaining quantity is partially filled or cancelled in case
there’s no availability to fully fill the remaining quantity.
Canceled: Indicates that the remaining quantity of a partially filled order was cancelled due to no available liquidity.
Symbol The Symbol that has been traded.
Maker The Maker responsible for processing the order:
If an order is STP, the displayed name of the Maker will be the name as configured in the Maker.
If an order is B Book, "B_BOOK" will be displayed.
Side The Side of the Order: BUY or SELL.
Taker The Taker that initiated the Order.
TEM The Taker Execution Model through which the Order was executed.
Ord Type Type of the executed Order (Market, Limit or Stop).
Volume Defines the Requested Volume.
Fill Volume The actual filled Volume of the Order:
Fully Filled Orders: Fill Volume equal to Volume.
Field Description

Positions
The Positions tab displays the current net open positions in real-time for the selected Risk Account or Taker Execution Model. Brokers can
have overview into all Risk Accounts or Taker Execution Models which allows to track the current exposure and net open positions on a
per Symbol basis.
One Risk Account/Taker Execution Model only can be selected at a time.
Partially Filled Orders: Fill Volume less than Volume.
Rejected Orders: 0 Volume as no Volume was executed.
The actual filled Volume could be equal or less than the requested Volume above.
Price The Requested Price specified in the Order request, if any.
This is only relevant to Limit and Stop Orders.
Avg Price The Weighted Average Price in case the Order was split into multiple legs.
Time in
Force
The execution mode: IOC or FOK.
Deviation Defines the deviation between the Requested Price and the Filled Price if any.
This is only relevant to Limit and Stop Orders.
Text A message pertaining to the executed order in the event of execution or rejection. In cases of rejection, this message
may provide insights into the reasons behind the rejection.
Symbol The Symbol with open positions
Taker
Execution
Model
The name of the Taker Execution Model where the Order is originated from
Note: This is only relevant if a Taker Execution Model is selected. Otherwise, if a Risk Account is selected, the field will
show an empty value
Taker The name of the Taker where the Order is originated from
Note: This is only relevant if a Taker Execution Model is selected. Otherwise, if a Risk Account is selected, the field will
show an empty value
Field Description

Account Balance
Account Balance is only relevant if Risk Account is selected and shows all balance, P/L and margin information pertaining to the Risk
Account.
If Taker Execution Model is selected, this tab will display empty values.
Liquidity
Model
The Liquidity Model assigned to the Risk Account/Taker Execution Model which specifies the Maker(s) Orders are
executed with
Net Volume The Net Open Positions in notional value.
If the Account is Short on the Symbol, the Net Volume will show a negative value and will be highlighted in Red
If the Account is Long on the Symbol, the Net Volume will show a positive value and will be highlighted in Blue
ANet Volume The Net Open Positions of the STP Orders
BNet Volume The Net Open Positions of the internalized (B-Book) Orders
Avg Price The Weighted Average Price of all Orders that form the Position
AAvg Price The Weighted Average Price of all Orders that make up the STP Positions
BAvg Price The Weighted Average Price of all Orders that make up the B Book Positions
Last Time The Last Time the price hence the Position were updated
Close Price The current Market Price of the Symbol
PL The floating (unrealized) P/L of the Symbol based on the Open Positions
Margin The current Utilized or Blocked Margin of the Symbol’s Open Positions
Swaps The accumulated Swap charges that have been charged on Open Positions.
Note: These charges represent the unrealized charges that have not been deducted from the Account Balance yet.
When an Order offsets (partially or totally) the Open Position, the corresponding value will be deducted (proportionally
or fully) from the Account Balance and will appear in the Account Statement
Commission The accumulated Commission charges that have been charged upon opening the Position.
Note: These charges represent the unrealized charges that have not been deducted from the Account Balance yet.
When an Order offsets (partially or totally) the Open Position, the corresponding value will be deducted (proportionally
or fully) from the Account Balance and will appear in the Account Statement
Name The Name of the Risk Account
Margin
Blocked
The blocked or utilized margin of the Risk Account based on the open positions
Balance The current Balance in USD of the Risk Account
Available
Withdraw
The amount in USD available for withdrawal. It is equivalent to the Free Margin of the Risk Account and is calculated as
follows:
Available Withdraw = Equity – Margin Blocked - Credit
Equity The current Equity in USD of the Risk Account
Equity = Balance + PL
Field Description

PL The PL of the floating positions which is equal to the sum of floating PL of all Symbols
Margin
Level
The Margin Percentage Level of the Risk Account which specifies the level at which no more Orders are allowed or
Account gets liquidated.
Margin Level = Equity/Margin Blocked x 100
Commission The accumulated Commission charges that have been charged on the Risk Account.
Note: These charges represent the unrealized charges that have not been deducted from the Account Balance yet.
When an Order offsets (partially or totally) the Open Position, the corresponding value will be deducted (proportionally
or fully) from the Account Balance and will appear in the Account Statement
Swaps The accumulated Commission charges that have been charged on the Risk Account.
Note: These charges represent the unrealized charges that have not been deducted from the Account Balance yet.
When an Order offsets (partially or totally) the Open Position, the corresponding value will be deducted (proportionally
or fully) from the Account Balance and will appear in the Account Statement
Notional The Notional Volume of all Open Positions translated into USD (Risk Account Currency)
Credit The amount of Credit given to the Risk Account, if any
Trading
State
The Trading State of the Risk Account.
STOPPED OUT: Risk Account is flat or negative which could be due to stop out or Account is out of balance
* MARGIN CALL: Risk Account is on Margin Call when the Margin Level hits or drops below the percentage
defined in Warn Level set for the Account
* NEUTRAL: Risk Account is funded


```

---
