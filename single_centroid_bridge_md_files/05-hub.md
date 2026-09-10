# 📁 05-hub

- **Generated:** 2026-09-10 12:07
- **Total Files:** 8
- **Source:** `C:\Users\DELL\Downloads\backend_code-main (1)\backend_code-main (2)\bridge_manual_md\05-hub`

---

## 📑 Table of Contents

1. [README.md](#readme-md)
2. [faq--hub-module.md](#faq-hub-module-md)
3. [markup-models.md](#markup-models-md)
4. [securities.md](#securities-md)
5. [liquidity-models/README.md](#liquidity-models-readme-md)
6. [liquidity-models/book-construction.md](#liquidity-models-book-construction-md)
7. [symbols/README.md](#symbols-readme-md)
8. [symbols/synthetic-symbols.md](#symbols-synthetic-symbols-md)

---

## 🌲 Project Structure

```
05-hub/
├── faq--hub-module.md
├── liquidity-models/
│   ├── book-construction.md
│   └── README.md
├── markup-models.md
├── README.md
├── securities.md
└── symbols/
    ├── README.md
    └── synthetic-symbols.md
```

---

## 📄 Files

<a id='readme-md'></a>
### 8. `README.md`

```markdown
[🏠 Document Start](..\README.md) / Hub

# Hub

The Hub Module allows to create and configure Security groups, core Symbols, Aggregation Modes, and Markup Profiles. Upon clicking
the “Hub” button on the left-hand side menu, it expands to show the different components underneath which are explained in greater detail
hereunder.




```

---

<a id='faq-hub-module-md'></a>
### 8. `faq--hub-module.md`

```markdown
[🏠 Document Start](..\README.md) / [Markup Models](README.md) / FAQ - Hub Module

# FAQ - Hub Module

FAQ
Can we introduce more Security Types?
Do I need to perform a system restart after adding a new symbol to the centroid bridge?
What is the recommended way to update the Vol Digits?
Should I consider updating the Session time over the Centroid Bridge, and is it recommended?
Can multiple makers be assigned in a single LM?
What effects should be expected when disabling a LM or a symbol within it?

Securities
At the moment, we cannot add more security types, However all the security types would be available in your Centroid Bridge.
Symbols
A system restart is not necessary when adding a new symbol.
For updating the Vol digits, we kindly suggest contacting our support team through email support@centroidsol.com, as this process
also requires restarting your Centroid Bridge.
We generally advise maintaining the Centroid Bridge session 24/7 and suggest making any required session changes on the Trading
Platform.
Liquidity Models
Certainly, it is possible to assign multiple makers within a single LM.
When a Liquidity Model or a specific symbol within it is disabled, price updates will cease, and trades won't be forwarded to the
designated maker.


```

---

<a id='markup-models-md'></a>
### 8. `markup-models.md`

```markdown
[🏠 Document Start](..\README.md) / [Book Construction](README.md) / Markup Models

# Markup Models

Overview
A Markup Model goes together with the Liquidity Model and consists of additional Markups to be added on top of the quotes coming
through the Liquidity Model i.e. the Maker.
In this component, you can define a variety of Markup Models for the purpose of adding additional Markups on top of the prices coming
from your Liquidity Providers (Makers) for both streaming and execution. The additional Markups defined in this component represents the
profit the Broker will be earning on all the flow sent to the Liquidity Providers (Makers).
Within this module, you have the capability to:
Add a Markup Model: Introduce a new Markup Model.
Filter Markup Models: Categorize Markup Models based on different criteria to simplify configuration.
Configure Global Markup Model: Adjust bid and ask markups, configure markup multipliers, manage enabling/disabling setting, and
adding a description for a specific Markup Model at a global level.
Delete a Markup Model: Remove an existing Markup Model.
Export a Markup Model: Save the list of Markup Models to an Excel or CSV file.
Filter and Lookup Configuration Settings: Search for configuration settings by different lookup criteria to ease configuration.
Configure Bulk Symbols: Click the “Edit” icon to modify bulk Symbols may it be all Symbols or a group of filtered Symbols.
Configure Markup Model Symbol: Fine-tune the settings of a Symbol within a Markup Model at the level of each Symbol.
Export Symbol Settings of a Particular Markup Model: Save the configured Symbol settings of a specific Markup Model to an Excel
or CSV file.
Upload Excel or CSV File: Update or change bulk configurations of an existing Markup Model by uploading an Excel or CSV file.
Note: Multipliers are coefficients by which the entire Markup Model will be multiplied. You may set up three different Multipliers and
alternate between them at any point in time. Multipliers are useful when it comes to increasing markups during news or market volatility in
one click without going through each Symbol individually.
Creating a Markup Model
To create a Markup Model
1. Click on Hub > Markup Models > Add


2. Fill out the Wizard with all relevant information. You may refer to the field descriptions hereafter.
3. Click the “Submit” button to apply the changes.
Enabled Indicates whether the Markup Model is enabled or disabled.
If ticked, the Markup Model is enabled upon creation.
If unticked, the Markup Model is disabled upon creation.
Note: Disabling a Markup Model at this level means that Markup and other relevant settings defined
here will not be taken into account for all Takers to which this Markup Model is assigned.
Note: Enabling/Disabling State at this level will apply across all Symbols and can be later changed
separately for each Symbol
Name Markup_Mo
del
A unique name of the Markup Model.
Description A short description for reference purposes only.
Bid Points 1, 2, 5 Bid Markup to be added on top of the bid price. Markups are specified in points which are added to
the last digit of the symbol. The Markups defined here are applicable across all Symbols within this
Markup Model. However, you may have to change the Markups separately on a per symbol basis for
securities other than FX at a later stage.
Field Possible
Values
Description

Configuring a Markup Model
To configure or modify a newly added or existing Markup Model on a per symbol basis
1. Click the little arrow on the Symbol column to have it sorted in an alphabetical order.
2. Configure the Markup Model by modifying the editable fields.
a. Select “Points” if you want to put a Markup as points. Example: BTCUSD is a 2-digit symbol. If you put a 5 points Markup Bid and
Ask, it will correspond to 0.05 on Bid/Ask respectively.
b. Select “Price” if you want to put a Markup as a whole number. Example: EURUSD is a 5-digit symbol. If you put a 5 number
Markup Bid and Ask, it will correspond to 5.00000 on Bid/Ask respectively.
3. All editable fields are represented by a “Pen” icon. You may utilize it to bulk edit.
4. Click the “Save” button on the top left to apply the changes.
5. Click the “Revert All” button if you want to revert to the previous values.
Note: A negative value would represent a markdown whereby Broker would be giving a price better
than the raw price for the client.
Example: 1 point Markup for the symbol having digits of 5 would correspond to 0.00001.
Ask Points 1, 2, 5 Ask Markup to be added on top of the ask price. Markups are specified in points which are added to
the last digit of the symbol. The Markups defined here are applicable across all Symbols within this
Markup Model. However, you may have to change the markups separately on a per symbol basis for
securities other than FX at a later stage.
Note: A negative value would represent a markdown whereby Broker would be giving a price better
than the raw price for the client.
Example: 1 point Markup for the symbol having digits of 5 would correspond to 0.00001.
Multiplier Mode Select one of the three available Multipliers. If no Multiplier is selected, the default value will be the
First Multiplier.
Multipliers
(1,2,3)
0.5, 1, 2 A coefficient by which the entire Markup Model will be multiplied across all Symbols. Bid and Ask
Markups for each Symbol will be multiplied by the value defined in the selected Multiplier.
Copy From Allows to copy all settings from an existing Markup Model.
Symbol EURUSD,
XAUUSD
The name of the Symbol to be configured as defined in Symbols.
Security FX, CFD,
EQUITIES
The Security into which the Symbol is grouped.
Field Possible
Values
Description

Model
plain_markup The current Markup Model being configured.
Digits 2 The number of digits defined for the Symbol upon creation.
Sessions MON,00:00-
23:59
Defines the time of the day during which the Markup Model will be functional.
All days of the week should be included and separated by a semicolon “;” along with the time interval
during the day. 00:00-00:00 represents a closure during a particular day.
Markup Bid 0.00002, 0.02,
0.003
The Markup or additional spread to be added on top of the bid price. Markups are defined in decimal
points.
Note: A negative value would be highlighted in red and represent a markdown whereby Broker would
be giving a price better than the raw price for the client.
Example: 2 points Markup for the symbol having digit of 5 would correspond to 0.00002.
Markup Ask 0.02, 0.00002,
0.003
The Markup or additional spread to be added on top of the ask price. Markups are defined in decimal
points.
Note: A negative value would be highlighted in red and represent a markdown whereby Broker would
be giving a price better than the raw price for the client.
Example: 5 points Markup for the symbol having digits of 5 would correspond to 0.00005.
Example: 10 points Markup for the symbol having digit of 5 would correspond to 0.00010.
Markup Bid
Var
0.00003 Defines a random additional bid Markup to be added on top of the Markup Bid to randomize the
behavior. The client in this case will see the spread as “Any value between Markup Bid + Markup Bid
Var”.
Example: Let’s say Markup Bid is 0.00010 (10 points) and the Markup Bid Var is 0.00003 (3 points).
So, the Markup Bid will be any value between 10-13 points.
10 points [Fixed] + 3 points [Var] = 10-13 points
Markup Ask
Var
0.00005 Defines a random additional ask Markup to be added on top of the Markup Ask to randomize the
behavior. The client in this case will see the spread as “Any value between Markup Ask + Markup
Ask Var”.
Example: Let’s say Markup Ask is 0.00010 (10 points) and the Markup Ask Var is 0.00005 (5 points).
So, the Markup Ask will be any value between 10-15 points.
10 points [Fixed] + 5 points [Var] = 10-15 points
Spread Min 0.00003 Defines a minimum spread of the final price shown to client after the bid and ask Markups have been
applied.
If the price is lower than the defined Spread Min, the Centroid Bridge will enforce the Spread Min by
adjusting the Bid and Ask Prices accordingly.
If Spread Min = -1, this indicates that Spread Min is disabled, meaning no spread min to be
enforced. (Note: In case of inverted spread from the Maker, the bridge will accept and advertise
the prices to the Takers.)
If Spread Min = Spread Max, this results in a FIXED SPREAD.
If Spread Min = 0, the bridge will adjust the inverted spread to become 0.
Midpoint Price – (Spread Min/2) and Midpoint Price + (Spread Min/2)
Spread Max 0.00008 Defines a maximum spread of the final price shown to client after the bid and ask Markups have
been applied in the event of price widening.

If the price is greater than the defined Spread Max, the Centroid Bridge will enforce the Spread Max
by adjusting the Bid and Ask Prices accordingly.
If Spread Max = -1, this indicates that Spread Max is disabled.
If Spread Min = Spread Max, this results in a FIXED SPREAD.
If Spread Max = 0, the spread would become 0 using the midpoint price which would be shown
on both ends, bid and ask respectively.
Midpoint Price – (Spread Max/2) and Midpoint Price + (Spread Max/2)
Spread Min
Exec
ABSORB,
PASS,
INVALIDATE,
REJECT,
INVALIDATE_A
ND_REJECT,
PASS_A_ABS
ORB_B
This works with coordination of Spread Min if defined. It dictates the execution behavior in case the
Price exceeds the Spread Min. The execution will be subject to the following options:
ABSORB: The difference between the Actual Price and the Spread Min will be absorbed by the
Broker. So, the client will get executed at the adjusted price that was advertised upon placing the
order.
PASS: The difference between the Actual Price and Spread Min will be passed on to the client
which will theoretically execute the client against the real market price.
INVALIDATE: If the Price is higher than the Spread Min defined, the tick will not be advertised
to client but order may still come through if same Markup Model is used for TF and TEM.
REJECT: If the Price is higher than the Spread Min defined, then the Centroid Bridge will reject
all the trades, hence no execution will take place. However, the price is still advertised to the
Taker.
INVALIDATE_AND_REJECT: If the Price is higher than the Spread Min defined, Prices will be
invalidated (not updating) and trades will be rejected.
PASS_A_ABSORB_B: If the Price is higher than the Spread Min defined, the slippage or the
difference between the Actual Price and Spread Min for A Book orders will be passed on the to
the client, while for B Book Orders, the Broker will absorb the slippage.
Spread Max
Exec
ABSORB,
PASS,
INVALIDATE,
REJECT,
INVALIDATE_A
ND_REJECT,
PASS_A_ABS
ORB_B
This works with coordination of Spread Max if defined. It dictates the execution behavior in case the
Price exceeds the Spread Max. The execution will be subject to the following options:
PASS: The difference between the Actual Price and Spread Max will be passed on to the client
which will theoretically execute the client against the real market price.
ABSORB: The difference between the Actual Price and the Spread Max will be absorbed by the
Broker. So, the client will get executed at the adjusted price that was advertised upon placing the
order.
REJECT: If the Price is higher than the Spread Max defined, then the Centroid Bridge will reject
all the trades, hence no execution will take place. However, the price is still advertised to the
Taker.
INVALIDATE: If the Price is higher than the Spread Max defined, the tick will not be advertised
to client but order may still come through if same Markup Model is used for TF and TEM.
INVALIDATE_AND_REJECT: If the Price is higher than the Spread Max defined, Prices will be
invalidated (not updating) and trades will be rejected.
PASS_A_ABSORB_B: If the Price is higher than the Spread Max defined, this is how it will work
for A Book and B Book clients:
For A Book Clients: Execution Price will be sent as the confirmation i.e. the difference will be
passed to the client resulting to Slippage.
For B Book Clients: Requested Price will be sent as the confirmation i.e. the difference will be
absorbed by the Broker.
Extra Digits 1, 2, 3 This adds a decimal digit to the price for all clients to where this Markup Model will be assigned.

Deleting a Markup Model
To delete a Markup Model
1. Click the “Delete” icon next to the desired Markup Model
2. To confirm the deletion, type the name of the Markup Model in the field.
3. Confirm the “Delete” button in the pop-up window to confirm the deletion
Exporting a Markup Model
To export a Markup Model
Example: EURUSD 5-digit symbol. Let’s say you are adding 1 decimal, then EURUSD will start
pricing with 6 digits and you can confirm this by checking from the Market Watch.
Level 0, 2, 5 If the Maker is pricing with 5 layers and the Markup Model is having a Level of 1, then only 1 layer
(that is first layers only) will have the effect of Markup Model while the rest of the 4 layers from the
Maker will be streamed as raw to your clients.
0 = It covers all layers.
1, 2, 3 = Any other number configured here means it would be restricted to these many layers
only.
WL Bid
Points
(White-
Label)
0, 10, 50 Here you can define a value in points as a share of the markup you are giving to your White-Label
Client that will be available in the markup report.
Example: If the digit for a particular symbol is 5 and you have configured 5 (points) then the WL
client will get 5 points out of the Bid Markup configured here.
WL Ask
Points
(White-
Label)
0, 10, 50 Here you can define a value in points as a share of the markup you are giving to your White-Label
Client that will be available in the markup report
Example: If the digit for a particular symbol is 5 and you have configured 5 (points) then the WL
client will get 5 points out of the Ask Markup configured here.
Description A short description for reference purposes that is copied automatically from the description defined in
Symbols.
Enable Enabled,
Disabled
Defines whether the Markup settings are enabled or disabled for that particular symbol.
If ticked, the Markup settings are Enabled.
If unticked, the Markup settings are Disabled.


1. Select the markup model from the list you wish to export.
2. Click “Export” and select “Export to Excel” or “Export to CSV”
Uploading a Markup Model
To upload a Markup Model symbol settings
1. Click on “Upload”
2. Drop the file you want to upload. Alternatively, you can click on “Drop a File”, select the file and click “Open”
3. Click “Upload“ to upload the file or click “Close” to cancel.


Note: The best way to avoid any errors would be creating a plain markup model or exporting the existing one, and updating all the details
along with the Markup Model Name, so a new one is created and nothing is changed for the old one.


```

---

<a id='securities-md'></a>
### 8. `securities.md`

```markdown
[🏠 Document Start](..\README.md) / [Hub](README.md) / Securities

# Securities

Overview
Security is a grouping of symbols that can be categorized into different types such as FX, CFD, Futures, Equities, and Crypto.
As seen above, the Securities component displays all configured Securities in the Centroid Bridge.
Within this module, you have the capability to:
Update Descriptions: Modify the description of a specific security or multi-update descriptions for multiple securities.
Sort Columns: Arrange certain columns in ascending or descending order by clicking the field name.
Export Securities: Save the list of securities to an Excel file or CSV file.

test caption for metadata purposes
Security No FX, CFD, CRYPTO, EQUITIES, FUTURES The name of the Security as defined in the Centroid
Bridge
Description Yes Foreign Exchange Market, Contract For
Differences, Cryptocurrencies, Stocks,
Futures Markets
A short description for reference purposes
Field Editable Possible Values Description


```

---

<a id='liquidity-models-readme-md'></a>
### 8. `liquidity-models/README.md`

```markdown
[🏠 Document Start](..\..\README.md) / [Synthetic Symbols](..\README.md) / Liquidity Models

# Liquidity Models

Overview
We can picture the Liquidity Model as pools where one or more Liquidity Providers (Makers) come together. The Makers are the
participants in this liquidity pool which we call the Liquidity Model and are responsible for sending prices and executing the orders.
The Liquidity Model can be a standalone model if it only contains one Maker (LP) or can be aggregated in case it contains more than one
Maker (LP). In the case of aggregation, Centroid Bridge will advertise the top of the book or the best price and target the Maker that offers
it during the execution. The selection of Liquidity Provider(s) or Maker(s) within the model can be configured on a per symbol basis offering
a great degree of flexibility.
Within this module, you have the capability to:
Add a Liquidity Model: Incorporate a new Liquidity Model.
Filter Liquidity Models: Categorize Liquidity Models based on different criteria.
Enable/Disable Liquidity Models: Manage the active status of the Liquidity Models in the Centroid Bridge.
Configure Global Liquidity Model: Adjust the settings at a global level by enabling/disabling or adding a description.
Delete a Liquidity Model: Remove an existing Liquidity Model.
Export a Liquidity Model: Save the list of Liquidity Models to an Excel or CSV file.
Filter and Lookup Symbol Settings: Search for Symbol settings by different lookup criteria to ease configuration.
Configure Bulk Symbols: Click the “Edit” icon to modify bulk Symbols may it be all Symbols or a group of filtered Symbols.
Configure Symbol Settings (Pricing and Trading): Fine-tune the settings of a Symbol within a Liquidity Model at the level of each
Symbol.
Export Symbol Settings of a Particular Liquidity Model: Save the configured Symbol settings of a specific Liquidity Model to an
Excel or CSV file.
Upload Excel or CSV File: Update or change bulk configurations of an existing Liquidity Model by uploading an Excel or CSV file.
Creating a Liquidity Model
To create a Liquidity Model
1. Click the “Hub” module.
2. Click the “Liquidity Models” component.
3. Click the “Add” button to create a new Liquidity Model.
4. Fill out the wizard with all relevant information. You may refer to the field descriptions hereafter.
5. Click the “Submit” button to submit the changes.


Configuring a Liquidity Model
To configure or modify a newly added or existing Liquidity Model on a per symbol basis
1. Click the little arrow on the Symbol column to have it sorted in an alphabetical order.
2. Configure the Liquidity Model by modifying the editable fields. All editable fields are represented by a “Pen” icon.
3. Click the “Save” button on the top left to apply the changes.
4. Click the “Revert All” button if you want to revert to the previous values.
Enabled This will determine whether the newly created Liquidity Model should be activated or
deactivated upon creation.
Name MakerName_LM This is intended to recognize the Liquidity Model and determine the particular Maker being
utilized in this Liquidity Model.
Description A short description for reference purposes only.
Makers Liquidity_Provider
-1
In this process, you will designate a specific Maker for the newly created Liquidity Model.
Essentially, this Liquidity Model will be responsible for interacting with the assigned Maker.
Field Possible Values Description

Symbol No EURUSD,
XAUUSD
The name of the Symbol to be configured as defined in Symbols.
Security No FX, CFD,
EQUITIES
The Security into which the Symbol is grouped.
Liquidity Model No Aggregated_LM The current Liquidity Model being configured.
Primary Maker Yes PB1, Maker_1 The Primary Maker or Liquidity Provider to source liquidity from by streaming
quotes into the Liquidity Model and executing any flow routed through that Liquidity
Model.
You can select multiple Makers in case you wish to aggregate prices from different
Makers to construct an aggregated liquidity book. The book is ordered by best
prices on top. As for Orders, it will be routed to the Maker providing the best price
at the time of execution.
Failover Makers Yes Maker_2 The Failover Makers to source liquidity in case of the Primary Maker stopped
pricing. This column will only work if stated in Symbols Profile and Stale Rules.
Sessions Yes MON,00:00-23:59 Defines the time of the day during which the Liquidity Model will be available for
trading.
All days of the week should be included and separated by a semicolon “;” along
with the time interval during the day. 00:00-00:00 represents a closure during a
particular day.
Exec Mode Yes SWEEP,
SINGLE_IOC,
SINGLE_FOK
Defines the execution modes of the Symbol for all Orders routed via Liquidity
Model.
SWEEP: the Orders will be executed by sweeping the book of quotes
constructed by the Maker(s) making up that Liquidity Model (unless indicated
otherwise in the Exec Boost parameter).
SINGLE_IOC: only one quote of the book will be targeted for execution even if
it does not satisfy the full amount, hence may result in a partial fill.
SINGLE_FOK only one quote of the book will be targeted for execution
provided that this quote can fill the requested volume entirely, hence no partial
fills.
Field Editab
le
Possible Values Description

Adding a Failover Maker
To add a Failover Maker
1. Click the “Hub” module.
2. Click the “Liquidity Models” component.
3. Select the desired “Liquidity Model” you wish to add a Failover Maker to it.
4. Add one or more Makers on the “Failover Makers“ column
Exec Boost Yes Enabled, Disabled Allows to boost the Order by sending the full requested amount at the TOB, rather
than splitting it into Legs based on the available Liquidity Book.
If Enabled, the Order will be sent in full to the Maker at the TOB, irrespective of
the available volume.
If Disabled, the Order will be executed by splitting it into different Legs if
needed based on the available Liquidity Book.
Note: For B Book Orders, the Order will be fully filled at TOB price if Exec Boost is
enabled.
Filter Factor Yes -2, -1, 10 Indicates whether a filtration is applied to prices coming into the Liquidity Model or
not.
If filtration is enabled, it dictates how the filtration is applied as explained below:
(-2) means that no price filtration is applied to the Liquidity Model, hence all
prices are allowed in.
(-1) means that filtration is being applied using the default parameters applied
in the relevant Filtration Pool.
(Other positive value) means that this value is used as a Factor which would
override the one defined in the Filtration Pool.
Book
Construction
Yes Allows to construct multi-layer books at the level of each Symbol and set markups
at each layer.
Note: Refer to the sub-section hereafter wherein construction of books at the level
of each Symbol are discussed in-depth.
Description Yes A short description for reference purposes that is copied automatically from the
description defined in Symbols.
Enable Yes Enabled, Disabled Indicates whether the Liquidity Model is enabled or disabled.

Deleting a Liquidity Model
To delete a Liquidity Model
1. Click the “Delete” icon next to the desired Liquidity Model.
2. Enter the Liquidity Model name in the text field on the confirmation pop-up window and click the “Delete” button to confirm the deletion.
Exporting a Liquidity Model
To export a Liquidity Model
1. Select the desired liquidity model from the list.
2. Tick the checkbox to select a Liquidity Model.
3. Click the “Export” button and select “Export to Excel” or “Export to CSV”.


Uploading a Liquidity Model
To upload a Liquidity Model symbol settings
1. To get the correct format, you need to use and follow the Exporting a Liquidity Model
2. Click the “Upload” button.
3. Click the “Drop A File” to browse and select the file or you can just easily drop the Excel or CSV file into the designated area.
4. To successfully upload the Liquidity Model values, click the “Upload” button.
5. You also have the option to discard the bulk upload by clicking the “Close” button.
Book Construction
The Book Construction is a feature within the Liquidity Model module that is configured at the level of individual Symbol through the Book
Construction field. It allows the construction of a virtual liquidity book and customizes a multi-layered Liquidity Book based on own


preferences in addition to adding markups at the different levels of the constructed Liquidity Book.
Note: If you are creating a virtual book of 3 layers without any markup then it will be merged and streamed as one layer only. So
to achieve a multi-layered virtual book, you need to add markups on each layer along with the volume.
When constructing a Book, the Centroid Bridge always takes the Top of the Book that is available to the Centroid Bridge whenever a new
price update comes in. The Book is constructed using the artificial Volumes specified at each level in addition to the Top of the Book price
to which the markup specified at each level is added. Volume can be randomized (using a range), fixed, or derived from the real Volume at
the Top of the Book.
When it comes to execution, we have to differentiate A Book from B Book as follows:
A Book: For A Book execution, the entire Order will be sent to the Makers at the Top of the Book irrespective of the Volumes at the
constructed Book.
B Book: For B Book execution, Orders will be filled based on the constructed Book by sweeping the Book from top to bottom until the
Order is fully or partially filled. It’s the same way the Centroid Bridge would execute any Order based on a real Liquidity Book.

Adding a Book Construction
1. Double-click the Book Construction field next to your desired Symbol.
2. Select whether you like to create the Book through a List or Text.
3. Select your preferred book construction mode as follows:
“Normal”: If you want to construct the Book based on the Bid and Ask.
“Midpoint”: if you want to construct the Book based on the midpoint price.
4. Click the “Add” button to start creating the Book Construction.


5. Fill out the wizard. Please note that the Markup shall be defined in points.


6. Click the “Submit” button once you have finalized the Book.
Note: The above steps will be repeated depending on the number of levels the Book will be made of.
7. Click the “Save” button to save the changes and finalize the Book Construction.
8. Click the “Revert All” button if you want to discard the changes made.



```

---

<a id='liquidity-models-book-construction-md'></a>
### 8. `liquidity-models/book-construction.md`

```markdown
[🏠 Document Start](..\..\README.md) / [Synthetic Symbols](..\README.md) / [Liquidity Models](README.md) / Book Construction

# Book Construction

Overview
The Book Construction feature is an essential component of the Liquidity Model module, and its configuration takes place at the individual
Symbol level through the dedicated Book Construction field. This feature facilitates the creation of a virtual liquidity book, enabling users to
tailor a multi-layered Liquidity Book according to their specific preferences. Additionally, it provides the capability to incorporate markups at
various levels within the constructed Liquidity Book. This means users have the flexibility to customize and enhance the liquidity
representation based on their unique requirements, introducing personalized adjustments and markups at different tiers of the constructed
Liquidity Book. When constructing a Book, the Centroid Bridge always takes the Top of the Book that is available to the Centroid Bridge
Constructing an Artificial Book
To construct an artificial book
1. Click on Hub > Liquidity Model > Desired Liquidity Model > Symbol > Book Construction > Add.
2. . Select your preferred book construction mode as follows:
Normal: The book is constructed using TOB Bid and TOB Ask Price from the maker.
Midpoint: The book is constructed using the Midpoint price of the TOB Bid and Ask Price from the maker.
3. Configure the required values, You may refer to the field descriptions hereafter.


4. Click the “Save” button to save your configured values.
How pricing works when using the Book Construction
When constructing a Book, the Centroid Bridge always takes the Top of the Book that is available on the Centroid Bridge whenever a new
price update comes in. The Book is constructed using the artificial Volumes specified at each level in addition to the Top of the Book price
to which the markup specified at each level is added. Volume can be randomized (using a range), fixed, or derived from the real Volume at
the Top of the Book.
Mode Normal, Midpoint Normal: The book is constructed using TOB Bid and TOB Ask Price from the maker.
Midpoint: The book is constructed using the Midpoint price of the TOB Bid and Ask Price from
the maker.
Bid Vol From 1000,15000 Clients can specify starting volume in the "Vol From" for Bid side
Bid Vol To 1000,1500 Clients can input the same volume in "Vol From" for a fixed range, or a different volume to
establish a variable volume range for the Bid layer.
Markup 0,10,15 Markups can be added on each layer in points for Bid Volume
Ask Vol From 1000,15000 Clients can specify starting volume in the "Vol From" for Ask side
Ask Vol To 1000,1500 Clients can input the same volume in "Vol From" for a fixed range, or a different volume to
establish a variable volume range for the Ask layer.
Field Possible Values Description

Note: If you are creating a virtual book of 3 layers without any markup then it will be merged and streamed as one layer only. So to
achieve a multi-layered virtual book, you need to add markups on each layer along with the volume.
How execution works when using the Book Construction
When it comes to execution, we differentiate A Book from B Book as follows
Modes Of Book Construction

Normal Mode:
When creating a book using the Normal mode for Book Construction, the system utilizes the TOB Bid Price and TOB Ask Price provided
by the maker(s) in the liquidity model or pool, in conjunction with the volumes you specified in the book construction process. This
approach ensures that the book is constructed based on the most recent bid and ask prices available.
Example:
Raw Book from the Maker ( 1.1 )
Markup 0,10,15 Markups can be added on each layer in points for Ask Volume
A Book The entire Order will be sent to the Makers at the Top of the Book irrespective of the Volumes at the
constructed Book.
B Book Orders will be filled based on the constructed Book by sweeping the Book from top to bottom until the Order
is fully or partially filled. It’s the same way the Centroid Bridge would execute any Order based on a real
Liquidity Book.
Book Execution Type Execution Mode


Summary:
In the process of constructing the book using normal mode, we initially referenced the raw TOB Bid and Ask Prices (see Image 1.1).
We then performed the requisite markup adjustments and incorporated the volume data, as outlined in Image 1.2.
The resultant prices and volumes, as shown in Image 1.3, confirm that the final output meets our anticipated criteria.
Midpoint Mode:
When using the Midpoint mode for Book Construction, the system calculates the book values based on the midpoint between the TOB Bid
Price and TOB Ask Price provided by the maker(s) in the liquidity model or pool. Additionally, any markups you apply are incorporated
along with the volumes you specify during the construction process. This approach ensures that the book accurately reflects the adjusted
pricing and the volumes you have entered.
Example:
Raw Book from the Maker ( 2.1 )
1 1.05567 2000 1.05571 1500
2 1.05566 3000 1.05572 2500
3 1.05565 4000 1.05573 4500
Number of Layers Bid Prices Bid Volumes Ask Prices Ask Volumes
Market Watch Raw Book from the
Maker ( 1.1 )
Constructed Artificial Book ( 1.2 )
Market Watch Utilizing the Book
Construction ( 1.3 )
1 1.05567 1000 1.05571 1500
2 1.05566 2000 1.05572 2500
3 1.05565 4000 1.05573 4500
Number of Layers Bid Prices Bid Volumes Ask Prices Ask Volumes
Market Watch Raw Book from the
Maker ( 2.1 )
Constructed Artificial Book ( 2.2 )Market Watch Utilizing the Book
Construction ( 2.3 )

Summary:
During the book construction using midpoint mode, we first used the raw TOB Bid and Ask Prices to determine the Midpoint (Average)
(refer to Image 2.1).
After calculating the average from the TOB Bid and Ask Prices, we applied the necessary markup adjustments and incorporated the
volume data, as detailed in Image 2.2.
The resulting prices and volumes, illustrated in Image 2.3, verify that the final output aligns with our expected criteria.
VWAP Mode:
In VWAP Mode for Book Construction, the system considers the pricing from all layers provided by the maker(s) in the liquidity model or
pool, as well as the volumes the maker(s) is streaming. The book is constructed based on the volumes you specify. If necessary, the
system will use pricing and volumes from two layers provided by the maker to build one layer of your artificial book. The construction of the
second layer will begin where the first layer concluded. Further details will be provided with an example. The price displayed for the book
will be the Volume-Weighted Average Price (VWAP).
Example:
Raw Book from the Maker ( 3.1 )
Summary:
In constructing the book using VWAP mode, we utilized the Raw Bid Prices and Volumes and Raw Ask Prices and Volumes from all
layers (see Image 3.1) to create the artificial book.
1 1.05567 1000 1.05571 1000
2 1.05566 1500 1.05572 1500
3 1.05565 1500 1.05573 1500
Number of Layers Bid Prices Bid Volumes Ask Prices Ask Volumes
Market Watch Raw Book from the
Maker ( 3.1 )
Constructed Artificial Book ( 3.2 )
Market Watch Utilizing the Book
Construction ( 3.3 )


We then applied any necessary markup adjustments and integrated the volume data, as described in Image 3.2. This process involved
sweeping the Raw Book from top to bottom.
The final prices and volumes, shown in Image 3.3, confirm that the output meets our anticipated criteria. Price for Artificial Book is
calculated as
VWAP is calculated using the formula: VWAP=∑(Price×Quantity)/∑Quantity, where each raw price and quantity pair is considered
until the final value meets the expected criteria.
VWAP Cumulative Mode:
In VWAP Cumulative Mode for Book Construction, the system incorporates the pricing from all layers provided by the maker(s) in the
liquidity model or pool, as well as the volumes the maker(s) is streaming. The book is constructed based on the volumes you specify. If
necessary, the system will use pricing and volumes from two layers provided by the maker to build one layer of your artificial book. The
construction of the second layer will start from the very top again. Further details will be provided with an example. The displayed price for
the book will be the Volume-Weighted Average Price (VWAP).
Example:
Raw Book from the Maker ( 4.1 )
Summary:
In constructing the book using VWAP Cumulative Mode, we utilized the Raw Bid Prices and Volumes and Raw Ask Prices and Volumes
from all layers (see Image 4.1) to create the artificial book.
We then applied any necessary markup adjustments and integrated the volume data, as described in Image 4.2. This process involved
sweeping the Raw Book from top to bottom, restarting from the top for each subsequent layer.
The final prices and volumes, shown in Image 4.3, confirm that the output meets our anticipated criteria. Price for the Artificial Book is
calculated as
VWAP is calculated using the formula: VWAP = ∑(Price × Quantity) / ∑Quantity, where each raw price and quantity pair is considered
until the final value meets the specified volume requirements.
1 1.05567 500 1.05571 500
2 1.05566 1500 1.05572 1500
3 1.05565 5000 1.05573 5000
Number of Layers Bid Prices Bid Volumes Ask Prices Ask Volumes
Market Watch Raw Book from the
Maker ( 4.1 )
Constructed Artificial Book ( 4.2 )
Market Watch Utilizing the Book
Construction ( 4.3 )


Cumulative Mode:
In Cumulative Mode for Book Construction, the system takes into account the pricing from all layers provided by the maker(s) in the
liquidity model or pool, as well as the volumes the maker(s) is streaming. The book is constructed based on the volumes you specify. If
necessary, the system will use pricing and volumes from two layers provided by the maker to build one layer of your artificial book. The
construction of the second layer will start from the very top again. In Cumulative Mode, the displayed price will always reflect the price of
the last consumed layer. Further details will be provided with an example.
Example:
Raw Book from the Maker ( 5.1 )
Summary:
In constructing the book using Cumulative Mode, we utilized the Raw Bid Prices and Volumes and Raw Ask Prices and Volumes from
all layers (see Image 5.1) to create the artificial book.
We applied the necessary markup adjustments and integrated the volume data, as detailed in Image 5.2. In Cumulative Mode, the
process involved sweeping the Raw Book from top to bottom and restarting from the top for each new layer. Notably, if a layer was
touched, its full volume was utilized rather than the Book Construction Volume.
The final prices and volumes, shown in Image 5.3, confirm that the output meets our anticipated criteria. Price for the Artificial Book is
derived from the last consumed layer.


1 1.05567 1500 1.05571 1500
2 1.05566 2250 1.05572 2250
3 1.05565 7250 1.05573 7250
Number of Layers Bid Prices Bid Volumes Ask Prices Ask Volumes
Market Watch Raw Book from the
Maker ( 5.1 )
Constructed Artificial Book ( 5.2 )
Market Watch Utilizing the Book
Construction ( 5.3 )




```

---

<a id='symbols-readme-md'></a>
### 8. `symbols/README.md`

```markdown
[🏠 Document Start](..\..\README.md) / [Securities](..\README.md) / Symbols

# Symbols

Overview
In this component, you can include symbols for trading on the Centroid Bridge which is explained as the top level here. Any modification
made to the symbol at this main level will impact the symbol at all the other levels or components.
All Symbols defined in the Centroid Bridge and their respective configuration settings are displayed in this component.
Within this module, you have the capability to:
Add a New Symbol: Use the new Symbol wizard to add a new Symbol.
Add or Update Symbols: Upload a bulk of Symbols from an Excel file or CSV file.
Filter and Look Up Symbols: Search for specific Symbols by different lookup criteria to ease configuration.
Configure Bulk Symbols: Edit a bulk of Symbols by clicking the Edit icon for all or a group of filtered Symbols.
Sort Columns: Arrange certain columns in ascending or descending order by clicking the field name.
Enable/Disable Symbols: Manage the active status of particular Symbol(s) in the Centroid Bridge.
Configure Per Symbol: Edit and configure specific fields on a per Symbol basis.
Delete a Symbol: Remove a Symbol from the system.
Multi-delete Symbols: Select multiple symbols and delete them simultaneously.
Export Symbols: Save the list of Symbols to an Excel file or CSV file.
Symbol No EURUSD,
XAUUSD,
AAPL,
BTCUSD
The name of the Symbol to be added and used.
Note: You may have multiple suffixes on your Taker/MT4/MT5. However, while creating a
symbol, the only focus is to create the base symbols. So you will only be adding Plain
Symbols in this window. Suffix can be added later with the help of Taker Feed component.
Security No FX, CFD,
EQUITIES
The Security into which the underlying Symbol is grouped.
Base Yes EUR, GBP,
DAX
The base currency of the Symbol.
For FX, it’s the first currency of the pair.
For non-FX such as CFDs, it’s the full name of the Symbol.
Field Editable Possible
Values
Description

Adding a Symbol
To add a New Symbol from the UI
You can add a new Symbol any time you wish to introduce a new product to be traded via the Centroid Bridge. There are two ways of
creating a Symbol, either by creating one Symbol at a time from the UI or by bulk creation i.e. uploading a list of Symbols from an Excel file
or CSV format.
1. Click the “Add” button to create a symbol.
Quote Yes USD, EUR,
GBP
The quote currency by which the Symbol is denominated.
For FX, it’s the second currency of the pair.
For CFDs, it’s the currency in which the Symbol is quoted. (e.g., FTSE is quoted in
GBP)
Category Yes Spot, Futures Represents another level of categorization to further categorize a Symbol.
ISIN Yes US0378331005 The ISIN code of the underlying instrument. For reference purposes only and is not
mandatory.
(e.g., Symbol: AAPL, ISIN: US0378331005)
Digits Yes 5 The number of decimals in the quoted price of the underlying Symbol.
Vol Digits Yes 2 The number of decimals allowed to be traded of the underlying Symbol.
Default value is 2. This allows up to 0.01 volume of trade. To allow 0.00000001 volume of
trades for Crypto symbols, Vol Digits must be updated to 8 and all the min size and step
settings must also be adjusted on Taker Execution Model and Maker Symbol settings with
consideration to allowed ABook and BBook minimum volume.
Note: Vol Digits setting can only be changed by Centroid Support Team.
Sessions Yes MON,00:00-
23:59
Defines the time when the symbol is Active i.e. sending prices to the Taker and receiving
the trades from the Taker.

All days of the week should be included and separated by a semicolon “;” along with the
time interval during the day. 00:00-00:00 represents a closure during a particular day.
Descripti
on
Yes A short description for reference. This will also be used as the default description values
for all the other components such as Liquidity Models, Markup Models, Makers, Taker
Feeds, and Taker Execution Models.
The description column can also be utilized to write rules whenever creating Synthetic
Symbols.
Enable Yes Enabled,
Disabled
Indicates whether the Symbol is enabled or disabled.
Note: Disabling a Symbol at this level implies that the Symbol will be disabled at all levels
throughout the Centroid Bridge, hence no quoting or trading on that Symbol.

2. Fill out the Wizard with all relevant information and click the “Submit” button.
Uploading Symbols
To upload Symbols from an Excel Sheet or CSV
An alternative method of creating Symbols from the UI is available which allows creating a bulk of Symbols all at once by uploading
multiple Symbols from an Excel or CSV file format.
Note: Please make sure to export the file first. Once you have the format, you will work on the same file and upload it with the same format
to avoid errors. Kindly also avoid utilizing special characters.
1. To get the correct format of the file or export your symbol settings list (via Excel or CSV), click the “Export” button and proceed to make
the changes.
2. Click the “Upload” button if you want to upload multiple new symbols or to update existing symbols.
3. Click the “Drop A File” to browse and select the file or you can just easily drop the Excel or CSV file into the designated area.


4. Click the “Upload” button to submit and upload the file.
5. You also have the option to discard the bulk upload by clicking the “Close” Button.
Note: When using the bulk operation to upload all the symbols, you can perform the following or possible scenarios:
Case 1: Uploading a file to only add new symbols
* Export the Symbol file
* Remove all the existing symbols
* Add new symbols then upload the file
Case 2: Uploading a file to add new symbols and not modifying any existing symbols
* Export the Symbol file
* Do not remove the existing symbols
* Add the new symbols then upload the file
Case 3: Uploading a file to only modify existing symbols
* Export the file
* Modify the values then upload the file
Case 4: Uploading a file to add new symbols and modify existing symbols
* Export the Symbol file
* Modify the existing symbols
* Add new symbols then upload the file


Modifying a Symbol
To configure or modify an existing Symbol’s configuration
1. Double-click the editable field next to the desired Symbol. The rows configured are flagged by a brown-highlighted check box on the left
and the edited field(s) are also highlighted in brown.
2. Click the “Save” button on the top left to deploy the changes or “Revert All” to discard the changes.
3. Another option to modify the Symbol(s) is mentioned on Uploading Symbols.
Deleting a Symbol
To delete an existing Symbol
1. Click the “Delete” icon next to the desired Symbol or you may also tick the check box beside the symbol and click the “Delete” button
on the top left.
To delete an existing Symbol in bulk
1. Tick the check box next to the specific symbol(s) you wish to delete and it will be highlighted. Multi-selecting symbols can also be done
by ticking the check box on the top left of the Symbol column.
2. Click the “Delete” button to bulk delete.
3. Enter “delete” in the text field on the confirmation pop-up message and click the “Delete” button to confirm the deletion.





```

---

<a id='symbols-synthetic-symbols-md'></a>
### 8. `symbols/synthetic-symbols.md`

```markdown
[🏠 Document Start](..\..\README.md) / [Securities](..\README.md) / [Symbols](README.md) / Synthetic Symbols

# Synthetic Symbols

Overview
The Synthetic Symbols offer the ability to create and price new products by combining one or multiple Symbols as well as using complex
formulas to price the new Symbols. For instance, you can derive the price of Gold in KG out of the price of XAUUSD by setting a multiplier
of 32.15. Similarly, you can make an Exotic FX Symbol by combining two currency pairs. The Exotic Symbol starts at the level of the
Liquidity Model and follows the same flow other Symbols follow in terms of Markup Models which are applicable at the level of the Taker
(Feed and Execution).
Format and Usage
The two main used operators are division and multiplication involving source symbols and numbers and should be written as follows:
Division: @
Multiplication: *
Additionally, you may use a variety of formulas as follows:
SQRT– Square Root (1 parameter)
POW – Power (2 parameters) - POW(x^y)
AVG – Average (n parameters) - AVG(a,b,c,…)
SUM – Sum (n parameters) - SUM(a,b,c,…)
ABS – Absolute Value (1 parameter) – ABS(x)

All formulas need to be written between # # where b refers to the BID price and a to the ASK price, and can be applied differently as
follows:
1. One-sided formula: #b=x@y# This obtains the BID price by dividing x BID price by y BID price and does the same to the ASK price.
2. Two sided formula: #b=x*y#a=(x*y)+0.0001# This obtains the BID price by dividing x BID price by y BID price. As for the ASK price, it
divides x BID price by y BID price and adds 0.0001 to it.
3. In terms of formula: #b=x*y*z#a=_b_+0.05# This obtains the BID price by multiplying x and y and z. As for the ASK price, the _ _
indicates that the BID price of the calculated Synthetic Symbol is taken and 0.05 is getting added to it, hence we increase the ASK price by
0.05 ensuring that spread constantly stands at 0.05
Note: x, y, and z in the above example are the source symbols.
Examples
1. Create XAGGBP Synthetic Symbol: This is done by simply creating the Synthetic Symbol XAGGBP as a Universal Symbol and then
combining Symbols XAGUSD and GBPUSD where XAGUSD is divided by GBPUSD, by writing the formula in the description as follows:
In the above example, we only applied the formula on the BID price which automatically simulates the same behavior on the ASK price.
Once the formula has been written in the correct format and saved, the newly added symbol will start pricing instantly.


2. Create GOLD_KG Synthetic Symbol:
This is done by simply creating the Synthetic Symbol GOLD_KG as a Universal Symbol and then multiplying the source symbol XAUUSD
by 32.15.
In the above example, we obtained the BID price by multiplying the BID price of the source symbol XAUUSD by 32.15 to convert from troy
ounce to Kilo. As for the ASK price, we just used the same BID price we got and added 0.3 which fixed the spread at 0.3.
Notes:
Synthetic Symbols can be used only for pricing and B Book execution at this stage
You may increase the default volume of the Synthetic Symbols by using the Book Construction feature at the level of the Liquidity
Model



```

---
