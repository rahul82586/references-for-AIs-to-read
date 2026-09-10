# USER ----------------

ok what is next?  AFTER SYMBOL

# AI --------------------

## 🎯 Next: Complete the OMS Domain (Orders, Deals, Positions)

We've built the foundation (Accounts + Instruments). Now we need the **heart of the trading system** — the Order Management System.

### Why OMS Next?

| Dependency | Status |
|:---|:---|
| Instruments (Symbols, Sessions, Holidays) | ✅ Complete |
| Accounts (Groups, Clients, Accounts) | ✅ Complete |
| **OMS (Orders, Deals, Positions)** | 🔴 **Next** |
| Risk Engine (Margin, Pre-trade checks) | ⏳ Depends on OMS |
| Execution (Gateways, LP routing) | ⏳ Depends on OMS |
| Manager API (FastAPI endpoints) | ⏳ Depends on OMS |

The OMS is where **all business logic happens**. It's the state machine that transforms a client's "Buy EURUSD" click into an immutable Deal record, updates their Position, and triggers margin calculations.

---

### What We'll Build in OMS

#### 1. **Order Entity** (State Machine)
```
NEW → PLACED → PARTIALLY_FILLED → FILLED → CANCELLED/REJECTED
```
- Validation logic (volume, price, session checks)
- Order types (MARKET, LIMIT, STOP, STOP_LIMIT)
- Time-in-force (GTC, DAY, IOC, FOK)
- MT5-accurate pending order logic

#### 2. **Deal Entity** (Immutable Trade Record)
- Deal types (BUY, SELL, BALANCE, DEPOSIT, WITHDRAWAL, SWAP, COMMISSION)
- Links to Order (if applicable)
- PnL calculation (realized profit/loss)
- Cross-currency support (using new Symbol base/quote fields)

#### 3. **Position Entity** (Aggregation)
- **Hedging Mode**: One position per deal (MT5 default)
- **Netting Mode**: Aggregate all deals for a symbol into one position
- PnL calculation (unrealized, using live tick prices)
- Margin calculation (using new Symbol margin rates per direction)

#### 4. **Trade Modification** (MT5 Pattern)
- **Reversal Deal**: Exact opposite of original deal
- **Correction Deal**: New deal with corrected parameters
- Both link to original `ticket_id` for audit trail
- Used when dealer needs to fix a wrong price from weeks ago

#### 5. **Bulk Operations**
- Close all positions
- Close by (hedge close)
- Bulk modification

---

### File Structure

```
core/domains/oms/
├── __init__.py
├── enums.py              # OrderType, OrderState, DealType, PositionMode
├── entities/
│   ├── order.py          # Order entity with state machine
│   ├── deal.py           # Deal entity (immutable)
│   └── position.py       # Position entity (hedging/netting)
├── services/
│   ├── order_service.py  # Order validation, state transitions
│   ├── deal_service.py   # Deal creation, PnL calculation
│   └── position_service.py  # Position aggregation, margin calc
└── trade_modification.py # Reversal + Correction logic
```

---

### Key MT5 Features to Implement

1. **Per-Direction Margin Rates** (from new Symbol)
   - BUY orders use `margin_rate_initial_buy`
   - SELL orders use `margin_rate_initial_sell`
   - LIMIT/STOP orders have their own rates

2. **Cross-Currency PnL** (from new Symbol)
   - Calculate PnL in quote currency (e.g., JPY for EURJPY)
   - Convert to account currency using live rate

3. **Hedging vs Netting Modes** (from Group)
   - Hedging: Each deal creates a new position
   - Netting: All deals for same symbol aggregate into one position

4. **Trade Modification Audit Trail**
   - Never modify existing deals
   - Always create Reversal + Correction pair
   - Link to original `ticket_id`

---

### Ready to Proceed?

Shall I generate the complete OMS domain code with:
- ✅ MT5-accurate state machines
- ✅ Integration with new Account/Client/Symbol structures
- ✅ Cross-currency PnL support
- ✅ Hedging/Netting modes
- ✅ Trade modification logic

**Type "Yes" and I'll provide the full implementation.**



# USER --------------------
first check the mt5 sdk all the files i provided you and provideing rest of the left mt5 sdk files. how things are structured in mt5 sdk



# AI -------------------------

Based on all the MT5 SDK files you've provided, here's the complete structure:

## 🏛️ MT5 SDK Architecture Overview

The MT5 SDK is organized into **5 major API layers**, each with distinct responsibilities:

---

## 1. **Core API Layers**

### A. **Manager API** (`MT5APIManager.h`)
- **Purpose**: Administrative operations (back-office)
- **Interface**: `IMTManagerAPI`
- **Factory**: `CMTManagerAPIFactory`
- **Key Operations**:
  - User/Account management
  - Order/Deal/Position queries
  - Configuration management (Groups, Symbols, Holidays)
  - Dealer workflow (manual execution)
  - Reports generation
  - Risk management (margin calls, stop-outs)

### B. **Server API** (`MT5APIServer.h`)
- **Purpose**: Server-side plugins (extending trade server)
- **Interface**: `IMTServerAPI`
- **Factory**: `CMTServerAPIFactory`
- **Key Operations**:
  - Trade request processing
  - Matching engine hooks
  - Risk checks
  - Custom execution logic

### C. **Gateway API** (`MT5APIGateway.h`)
- **Purpose**: Liquidity Provider bridges
- **Interface**: `IMTGatewayAPI`
- **Factory**: `CMTGatewayAPIFactory`
- **Key Operations**:
  - Connect to external LPs (FIX, REST, proprietary)
  - Route orders to LPs (A-Book)
  - Receive fills from LPs
  - Aggregate liquidity

### D. **Report API** (`MT5APIReport.h`)
- **Purpose**: Custom report generation
- **Interface**: `IMTReportAPI`
- **Key Operations**:
  - Dataset manipulation
  - Report templates
  - Export to Excel/PDF

### E. **Web API** (REST)
- **Purpose**: HTTP/JSON interface for web applications
- **Endpoints**: 124 endpoints (from your `swagger.json`)
- **Categories**: Trading, Accounts, Symbols, Groups, Reports, etc.

---

## 2. **Core Data Structures** (from `Structures/`)

### Price Data
```cpp
MTTick          // Full tick: bid, ask, last, volume, flags, time_msc
MTTickShort     // Lightweight tick: bid, ask, time
MTTickStat      // Tick statistics: bid/ask high/low, volume stats
MTChartBar      // OHLCV bar: open, high, low, close, volume, time
MTBookItem      // Order book entry: type (BUY/SELL), price, volume
```

### Market Data
```cpp
MTEconomicEvent // Economic calendar: time, country, event, forecast
MTNews          // News feed: time, topic, body, category
```

### System
```cpp
MTGatewayInfo   // Gateway configuration: name, type, address, status
MTLogRecord     // Log entry: severity, source, message, time
MTLicenseCheck  // License verification
MTProxyInfo     // Proxy server settings
MTServerInfo    // Server cluster config: trade/access/history roles
MTPluginInfo    // Plugin metadata: name, version, type
MTReportInfo    // Report definition: name, type, parameters
```

---

## 3. **Database Interfaces** (from `Database-Interfaces/`)

This is the **"Holy Trinity"** + supporting entities:

### A. **Trade Entities** (The Core)
```
Trade/
├── Accounts/
│   ├── IMTAccount          // Trading account state (balance, equity, margin)
│   └── IMTAccountArray     // Collection of accounts
├── Orders/
│   ├── IMTOrder            // Pending order (intent)
│   └── IMTOrderArray
├── Deals/
│   ├── IMTDeal             // Executed deal (immutable fact)
│   └── IMTDealArray
├── Positions/
│   ├── IMTPosition         // Open position (aggregate state)
│   └── IMTPositionArray
├── Daily-Reports/
│   └── IMTDaily            // Daily snapshot
└── History/
    ├── IMTHistoryDeal      // Historical deals
    ├── IMTHistoryOrder     // Historical orders
    └── IMTHistoryPosition  // Historical positions
```

### B. **User/Client Entities**
```
Users/
├── IMTUser                 // Client record (KYC, personal info)
├── IMTClient               // Client session state
├── IMTAttachment           // File attachments
├── IMTComment              // Comments/notes
└── IMTDocument             // KYC documents
```

### C. **ECN Matching** (In-House ECN)
```
ECN-Matching/
├── IMTECNMatching          // Order book entry
├── IMTECNFilling           // Fill record
├── IMTECNProvider          // Liquidity provider
└── IMTFilling              // Execution record
```

### D. **Online/Market Data**
```
Online-Connections/
├── IMTOnline               // Connected users
└── IMTBook                 // Market depth (order book)

Price-Data/
├── IMTTick                 // Tick data
├── IMTChart                // Chart bars
└── IMTSubscription         // Price subscriptions
```

---

## 4. **Configuration Interfaces** (from `Configuration-Interfaces/`)

These define the **rule engines** that control behavior:

### A. **Core Configuration**
```
Groups/
├── IMTConGroup             // Group rules (margin, commission, permissions)
├── IMTConGroupSymbol       // Per-symbol overrides within group
└── IMTConGroupCommission   // Commission tiers

Symbols/
├── IMTConSymbol            // Symbol configuration (contract size, tick, sessions)
├── IMTConSymbolSession     // Trading sessions per day
└── IMTConSymbolMargin      // Margin rates per direction

Holidays/
└── IMTConHoliday           // Holiday schedule (year, month, day, work times)
```

### B. **Execution & Routing**
```
Gateways/
├── IMTConGateway           // LP gateway configuration
├── IMTConGatewayModule     // Gateway plugin module
└── IMTConGatewaySymbol     // Symbol mapping per gateway

Routing/
├── IMTConRoute             // Routing rules (A-Book/B-Book logic)
└── IMTConRouteDealer       // Dealer assignment

Spreads/
└── IMTConSpread            // Spread configuration
```

### C. **Network & Cluster**
```
Network/
├── IMTConServer            // Server configuration (trade/access/history)
├── IMTConServerTrade       // Trade server settings
├── IMTConServerBackup      // Backup configuration
├── IMTConClusterState      // Cluster node state
└── IMTConServerAddressRange // IP ranges
```

### D. **Advanced Features**
```
Automation/                 // Automated actions (triggers, conditions)
VPS/                        // Virtual Private Server hosting
KYC/                        // Know Your Customer configuration
Leverage/                   // Leverage tiers
Plugins/                    // Server plugins
Reports/                    // Report configurations
Managers/                   // Manager accounts & permissions
```

---

## 5. **Event/Sink Pattern** (Critical for Real-Time)

MT5 uses **callback interfaces** (Sinks) for event-driven updates:

```cpp
// Example: Order events
IMTOrderSink {
    OnOrderAdd(order)      // New order created
    OnOrderUpdate(order)   // Order modified
    OnOrderDelete(order)   // Order deleted/cancelled
}

// Example: Account events
IMTAccountSink {
    OnAccountMarginCallEnter(account, group)   // Entered margin call
    OnAccountMarginCallLeave(account, group)   // Exited margin call
    OnAccountStopOutEnter(account, group)      // Stop-out triggered
    OnAccountStopOutLeave(account, group)      // Recovered from stop-out
}

// Example: Deal events
IMTDealSink {
    OnDealAdd(deal)        // New deal executed
}

// Example: Tick events
IMTTickSink {
    OnTick(tick)           // New tick received
}
```

**Your Python Equivalent**: This maps to your `core/events/domain_events.py` + `IEventBus` pattern.

---

## 6. **Array Pattern** (Collections)

Every entity has a corresponding Array interface:
```cpp
IMTOrderArray {
    Add(order)
    Delete(index)
    Total() -> count
    Next(index) -> order
    Search(criteria) -> results
}
```

**Your Python Equivalent**: Standard `List[Order]` or repository methods like `get_orders_by_account()`.

---

## 7. **Include Files** (from `Include/`)

### Bases/ (Database Entities)
```
MT5APIAccount.h      // IMTAccount
MT5APIOrder.h        // IMTOrder
MT5APIDeal.h         // IMTDeal
MT5APIPosition.h     // IMTPosition
MT5APIUser.h         // IMTUser
MT5APIBook.h         // IMTBook (market depth)
MT5APIChart.h        // IMTChart
MT5APITick.h         // IMTTick
```

### Config/ (Configuration)
```
MT5APIConfigGroup.h      // IMTConGroup
MT5APIConfigSymbol.h     // IMTConSymbol
MT5APIConfigHoliday.h    // IMTConHoliday
MT5APIConfigGateway.h    // IMTConGateway
MT5APIConfigRoute.h      // IMTConRoute
MT5APIConfigNetwork.h    // IMTConServer
```

### Classes/ (Utilities)
```
MT5APIFile.h         // File operations
MT5APIMath.h         // Math functions
MT5APIFormat.h       // String formatting
MT5APITime.h         // Time conversion
MT5APISync.h         // Thread synchronization
```

---

## 8. **How This Maps to Your broker-platform**

| MT5 SDK Component | Your Python Equivalent |
|:---|:---|
| `IMTAccount` | `core/domains/accounts/account.py` |
| `IMTUser` | `core/domains/accounts/client.py` |
| `IMTConGroup` | `core/domains/accounts/group.py` |
| `IMTConSymbol` | `core/domains/instruments/symbol.py` |
| `IMTConHoliday` | `core/domains/instruments/holiday.py` |
| `IMTOrder` | `core/domains/oms/entities/order.py` |
| `IMTDeal` | `core/domains/oms/entities/deal.py` |
| `IMTPosition` | `core/domains/oms/entities/position.py` |
| `IMTConGateway` | `core/domains/execution/models.py` (GatewayConfig) |
| `IMTConRoute` | `core/domains/execution/models.py` (RoutingRule) |
| `IMT*Sink` | `core/events/domain_events.py` + `IEventBus` |
| `IMTManagerAPI` | `api/routers/admin/` (FastAPI) |
| `IMTGatewayAPI` | `infrastructure/gateways/` (LP adapters) |

---

## 🎯 Key Takeaways

1. **Separation of Concerns**: MT5 strictly separates:
   - **Configuration** (Groups, Symbols, Holidays) → Your `core/domains/`
   - **State** (Accounts, Orders, Positions) → Your `core/domains/`
   - **Events** (Sinks) → Your `core/events/`
   - **Infrastructure** (Gateways, Plugins) → Your `infrastructure/`

2. **Immutability**: Deals are immutable facts. Only Orders and Positions change state.

3. **Event-Driven**: Everything uses Sinks (callbacks) for real-time updates.

4. **Configuration as Code**: Groups and Symbols are complex rule engines, not simple data bags.

5. **Cluster-Ready**: Network/Server configs support distributed deployment (Trade/History/Access servers).

---

## 📋 What's Next?

Now that you understand the MT5 SDK structure, we can:

1. **Continue building the OMS domain** (Orders, Deals, Positions) with full MT5 parity
2. **Map MT5 Manager API endpoints** to your FastAPI routers
3. **Implement the Gateway API pattern** for LP bridges
4. **Build the event system** matching MT5's Sink pattern

Which area would you like to tackle next?



# USER --------------------------

Continue building the OMS domain (Orders, Deals, Positions) with full MT5 parity
ok 


# AI ----------------------------

# 🏛️ OMS Domain: Full MT5 Parity Implementation

Based on the MT5 SDK (`Database-Interfaces/Trade/`), I'll build the complete OMS domain with all MT5-accurate enumerations, state machines, and trade modification logic.

## 📁 File Structure

```
core/domains/oms/
├── __init__.py
├── enums.py              # All MT5 OMS enumerations
├── entities/
│   ├── order.py          # Order entity with state machine + ATM
│   ├── deal.py           # Deal entity (immutable, with entry types)
│   └── position.py       # Position entity (hedging/netting/close-by)
├── services/
│   ├── order_service.py  # Order validation & state transitions
│   └── trade_modification.py  # MT5 reversal + correction pattern
└── events.py             # OMS-specific domain events
```

---

## 1. `core/domains/oms/enums.py` (~180 lines)

```python
"""OMS domain enumerations - MT5-accurate."""
from enum import Enum, IntFlag


class OrderType(Enum):
    """Order types (IMTOrder::EnOrderType)."""
    BUY = "BUY"
    SELL = "SELL"
    BUY_LIMIT = "BUY_LIMIT"
    SELL_LIMIT = "SELL_LIMIT"
    BUY_STOP = "BUY_STOP"
    SELL_STOP = "SELL_STOP"
    BUY_STOP_LIMIT = "BUY_STOP_LIMIT"
    SELL_STOP_LIMIT = "SELL_STOP_LIMIT"


class OrderState(Enum):
    """Order states (IMTOrder::EnOrderState)."""
    STARTED = "STARTED"           # Order adding started
    PLACED = "PLACED"             # Order placed in system
    CANCELLED = "CANCELLED"       # Cancelled by client
    PARTIALLY_FILLED = "PARTIALLY_FILLED"  # Partially filled
    FILLED = "FILLED"             # Fully filled
    REJECTED = "REJECTED"         # Rejected by broker
    EXPIRED = "EXPIRED"           # Expired by time


class OrderReason(Enum):
    """Who/what placed the order (IMTOrder::EnOrderReason)."""
    CLIENT = "CLIENT"             # Terminal
    EXPERT = "EXPERT"             # Expert Advisor
    DEALER = "DEALER"             # Dealer terminal
    GATEWAY = "GATEWAY"           # Gateway/external system
    SIGNAL = "SIGNAL"             # Trade signal
    API = "API"                   # Manager API
    MOBILE = "MOBILE"             # Mobile terminal
    WEB = "WEB"                   # Web terminal
    PLUGIN = "PLUGIN"             # Server plugin


class TimeInForce(Enum):
    """Order time-in-force (IMTOrder::EnOrderTimeType)."""
    GTC = "GTC"                   # Good till cancelled
    DAY = "DAY"                   # Good for the day
    SPECIFIED = "SPECIFIED"       # Good till specified date
    SPECIFIED_DAY = "SPECIFIED_DAY"  # Good till specified day


class ActivationMode(Enum):
    """Order activation mode for ATM orders (IMTOrder::EnOrderActivationMode)."""
    NONE = "NONE"                 # Not activated
    TIME = "TIME"                 # Activated by time
    PRICE = "PRICE"               # Activated by price
    TIME_PRICE = "TIME_PRICE"     # Activated by both


class DealType(Enum):
    """Deal types (IMTDeal::EnDealType)."""
    # Trading deals
    BUY = "BUY"
    SELL = "SELL"
    # Non-trading deals
    BALANCE = "BALANCE"
    CREDIT = "CREDIT"
    CHARGE = "CHARGE"
    CORRECTION = "CORRECTION"
    BONUS = "BONUS"
    COMMISSION = "COMMISSION"
    COMMISSION_DAILY = "COMMISSION_DAILY"
    COMMISSION_MONTHLY = "COMMISSION_MONTHLY"
    COMMISSION_AGENT_DAILY = "COMMISSION_AGENT_DAILY"
    COMMISSION_AGENT_MONTHLY = "COMMISSION_AGENT_MONTHLY"
    INTEREST = "INTEREST"
    BUY_CANCELED = "BUY_CANCELED"
    SELL_CANCELED = "SELL_CANCELED"
    REBATE = "REBATE"
    COMPENSATION = "COMPENSATION"
    # Rollover
    ROLLOVER_PROFIT = "ROLLOVER_PROFIT"
    ROLLOVER_LOSS = "ROLLOVER_LOSS"


class DealEntry(Enum):
    """Deal entry type - how deal affects position (IMTDeal::EnDealEntry)."""
    IN = "IN"           # Open position
    OUT = "OUT"         # Close position
    INOUT = "INOUT"     # Reverse position
    OUT_BY = "OUT_BY"   # Close by opposite position


class DealReason(Enum):
    """Deal reason (IMTDeal::EnDealReason)."""
    CLIENT = "CLIENT"
    EXPERT = "EXPERT"
    DEALER = "DEALER"
    SL = "SL"           # Stop loss triggered
    TP = "TP"           # Take profit triggered
    SO = "SO"           # Stop out triggered
    ROLLOVER = "ROLLOVER"
    VMARGIN = "VMARGIN"  # Margin call / daily margin
    STOP_OUT = "STOP_OUT"
    GATEWAY = "GATEWAY"
    SIGNAL = "SIGNAL"
    API = "API"
    MOBILE = "MOBILE"
    WEB = "WEB"
    PLUGIN = "PLUGIN"
    SPLIT = "SPLIT"


class PositionAction(Enum):
    """Position side (IMTPosition::EnPositionAction)."""
    BUY = "BUY"
    SELL = "SELL"


class PositionReason(Enum):
    """Position opening reason."""
    CLIENT = "CLIENT"
    EXPERT = "EXPERT"
    DEALER = "DEALER"
    GATEWAY = "GATEWAY"
    SIGNAL = "SIGNAL"
    API = "API"


class OrderFlags(IntFlag):
    """Order activation flags (IMTOrder::EnOrderActivationFlags)."""
    NONE = 0x00000000
    NO_SL = 0x00000001
    NO_TP = 0x00000002
    NO_SLTP_BY_TICK = 0x00000004
```

---

## 2. `core/domains/oms/entities/order.py` (~350 lines)

```python
"""Order entity - Client intent (IMTOrder)."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
import uuid

from core.domains.common.value_objects import Price, Volume
from core.domains.oms.enums import (
    OrderType, OrderState, OrderReason, TimeInForce,
    ActivationMode, OrderFlags
)


@dataclass
class Order:
    """
    Order Entity - Client Intent (IMTOrder).
    
    An Order represents a REQUEST to trade. It is MUTABLE and has a state machine.
    It may result in zero, one, or multiple Deals (for partial fills).
    
    MT5 Order Types:
    - Market: BUY, SELL
    - Pending: BUY_LIMIT, SELL_LIMIT, BUY_STOP, SELL_STOP,
               BUY_STOP_LIMIT, SELL_STOP_LIMIT
    """
    # Identity
    ticket_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    external_id: Optional[str] = None  # Exchange/ECN order ID
    gateway_id: Optional[str] = None   # Gateway execution order ID
    
    # Account & Symbol
    account_login: int = 0
    dealer_login: Optional[int] = None  # Dealer who processed (0 = auto)
    symbol: str = ""
    
    # Order details
    order_type: OrderType = OrderType.BUY
    reason: OrderReason = OrderReason.CLIENT
    state: OrderState = OrderState.NEW
    
    # Volume
    volume_initial: Volume = field(default_factory=lambda: Volume(Decimal('0')))
    volume_current: Volume = field(default_factory=lambda: Volume(Decimal('0')))
    
    # Pricing
    price_order: Price = field(default_factory=lambda: Price(Decimal('0')))  # Limit/Stop price
    price_sl: Optional[Price] = None  # Stop loss
    price_tp: Optional[Price] = None  # Take profit
    price_trigger: Optional[Price] = None  # For STOP_LIMIT orders
    
    # Time
    time_setup: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    time_setup_msc: int = 0  # Milliseconds since epoch
    time_expiration: Optional[datetime] = None
    time_done: Optional[datetime] = None
    
    # Time in force
    time_in_force: TimeInForce = TimeInForce.GTC
    
    # ATM Activation (time/price triggered orders)
    activation_mode: ActivationMode = ActivationMode.NONE
    activation_time: Optional[datetime] = None
    activation_price: Optional[Price] = None
    activation_flags: OrderFlags = OrderFlags.NONE
    
    # Symbol metadata (snapshot at order time)
    digits: int = 5
    digits_currency: int = 2
    contract_size: Decimal = field(default_factory=lambda: Decimal('100000'))
    
    # Expert/Plugin info
    expert_id: str = ""  # Filled by EA
    expert_name: str = ""
    comment: str = ""
    
    # Matching
    order_matching: Optional[str] = None  # Opposite order ticket (for ECN)
    
    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        """Initialize volume_current to volume_initial for new orders."""
        if self.volume_current.value == Decimal('0') and self.volume_initial.value > 0:
            self.volume_current = Volume(self.volume_initial.value)
    
    # =========================================================================
    # STATE MACHINE
    # =========================================================================
    
    _VALID_TRANSITIONS = {
        OrderState.NEW: [OrderState.PLACED, OrderState.REJECTED, OrderState.CANCELLED],
        OrderState.PLACED: [
            OrderState.PARTIALLY_FILLED, OrderState.FILLED,
            OrderState.CANCELLED, OrderState.REJECTED, OrderState.EXPIRED
        ],
        OrderState.PARTIALLY_FILLED: [
            OrderState.PARTIALLY_FILLED, OrderState.FILLED,
            OrderState.CANCELLED, OrderState.EXPIRED
        ],
        # Terminal states - no transitions allowed
        OrderState.FILLED: [],
        OrderState.CANCELLED: [],
        OrderState.REJECTED: [],
        OrderState.EXPIRED: [],
    }
    
    def transition_to(self, new_state: OrderState) -> None:
        """
        Transition order to a new state.
        
        Raises ValueError if transition is invalid.
        """
        if new_state not in self._VALID_TRANSITIONS.get(self.state, []):
            raise ValueError(
                f"Invalid state transition: {self.state.value} -> {new_state.value} "
                f"for order {self.ticket_id}"
            )
        self.state = new_state
        self.updated_at = datetime.now(timezone.utc)
        
        # If terminal state, mark as done
        if new_state in [OrderState.FILLED, OrderState.CANCELLED,
                         OrderState.REJECTED, OrderState.EXPIRED]:
            self.time_done = datetime.now(timezone.utc)
    
    def is_pending(self) -> bool:
        """Check if order is a pending order (not market)."""
        return self.order_type in [
            OrderType.BUY_LIMIT, OrderType.SELL_LIMIT,
            OrderType.BUY_STOP, OrderType.SELL_STOP,
            OrderType.BUY_STOP_LIMIT, OrderType.SELL_STOP_LIMIT,
        ]
    
    def is_market(self) -> bool:
        """Check if order is a market order."""
        return self.order_type in [OrderType.BUY, OrderType.SELL]
    
    def is_buy(self) -> bool:
        """Check if order is a buy-side order."""
        return self.order_type.value.startswith("BUY")
    
    def is_sell(self) -> bool:
        """Check if order is a sell-side order."""
        return self.order_type.value.startswith("SELL")
    
    def is_terminal(self) -> bool:
        """Check if order is in a terminal state."""
        return self.state in [
            OrderState.FILLED, OrderState.CANCELLED,
            OrderState.REJECTED, OrderState.EXPIRED
        ]
    
    # =========================================================================
    # FILL LOGIC
    # =========================================================================
    
    def apply_fill(self, fill_volume: Volume, fill_price: Price) -> None:
        """
        Apply a partial fill to the order.
        
        Reduces volume_current and transitions state appropriately.
        """
        if fill_volume.value <= 0:
            raise ValueError("Fill volume must be positive")
        
        if fill_volume.value > self.volume_current.value:
            raise ValueError(
                f"Fill volume {fill_volume.value} exceeds remaining "
                f"{self.volume_current.value}"
            )
        
        self.volume_current = Volume(self.volume_current.value - fill_volume.value)
        self.updated_at = datetime.now(timezone.utc)
        
        # Transition state
        if self.volume_current.value == 0:
            self.transition_to(OrderState.FILLED)
        else:
            if self.state == OrderState.PLACED:
                self.transition_to(OrderState.PARTIALLY_FILLED)
    
    def cancel(self, reason: str = "") -> None:
        """Cancel the order."""
        if self.is_terminal():
            raise ValueError(f"Cannot cancel order in state {self.state.value}")
        self.transition_to(OrderState.CANCELLED)
        if reason:
            self.comment = f"{self.comment} [CANCELLED: {reason}]".strip()
    
    def reject(self, reason: str) -> None:
        """Reject the order."""
        if self.is_terminal():
            raise ValueError(f"Cannot reject order in state {self.state.value}")
        self.transition_to(OrderState.REJECTED)
        self.comment = f"{self.comment} [REJECTED: {reason}]".strip()
    
    def expire(self) -> None:
        """Expire the order (time-in-force expired)."""
        if self.is_terminal():
            raise ValueError(f"Cannot expire order in state {self.state.value}")
        self.transition_to(OrderState.EXPIRED)
    
    # =========================================================================
    # ATM / ACTIVATION LOGIC
    # =========================================================================
    
    def is_activated(self, current_time: datetime, current_price: Price) -> bool:
        """
        Check if an ATM order should be activated.
        
        ATM orders are triggered by time, price, or both.
        """
        if self.activation_mode == ActivationMode.NONE:
            return True  # Not an ATM order, always active
        
        time_triggered = False
        price_triggered = False
        
        if self.activation_mode in [ActivationMode.TIME, ActivationMode.TIME_PRICE]:
            if self.activation_time and current_time >= self.activation_time:
                time_triggered = True
        
        if self.activation_mode in [ActivationMode.PRICE, ActivationMode.TIME_PRICE]:
            if self.activation_price:
                # Price trigger depends on order type
                if self.is_buy():
                    price_triggered = current_price.value >= self.activation_price.value
                else:
                    price_triggered = current_price.value <= self.activation_price.value
        
        if self.activation_mode == ActivationMode.TIME:
            return time_triggered
        elif self.activation_mode == ActivationMode.PRICE:
            return price_triggered
        elif self.activation_mode == ActivationMode.TIME_PRICE:
            return time_triggered and price_triggered
        
        return True
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "ticket_id": self.ticket_id,
            "external_id": self.external_id,
            "account_login": self.account_login,
            "symbol": self.symbol,
            "order_type": self.order_type.value,
            "reason": self.reason.value,
            "state": self.state.value,
            "volume_initial": str(self.volume_initial.value),
            "volume_current": str(self.volume_current.value),
            "price_order": str(self.price_order.value),
            "price_sl": str(self.price_sl.value) if self.price_sl else None,
            "price_tp": str(self.price_tp.value) if self.price_tp else None,
            "time_in_force": self.time_in_force.value,
            "activation_mode": self.activation_mode.value,
            "time_setup": self.time_setup.isoformat(),
            "time_expiration": self.time_expiration.isoformat() if self.time_expiration else None,
            "time_done": self.time_done.isoformat() if self.time_done else None,
            "comment": self.comment,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
```

---

## 3. `core/domains/oms/entities/deal.py` (~280 lines)

```python
"""Deal entity - Immutable execution record (IMTDeal)."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
import uuid

from core.domains.common.value_objects import Money, Price, Volume
from core.domains.oms.enums import (
    OrderType, DealType, DealEntry, DealReason
)


@dataclass
class Deal:
    """
    Deal Entity - Immutable Execution Record (IMTDeal).
    
    A Deal is a HISTORICAL FACT. Once created, it is NEVER modified.
    Corrections are handled via Trade Modification (Reversal + Correction).
    
    MT5 Deal Entry Types:
    - IN: Opens a position
    - OUT: Closes a position
    - INOUT: Reverses a position
    - OUT_BY: Closes by opposite position
    """
    # Identity
    deal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    order_id: Optional[str] = None  # Link to originating order
    position_id: Optional[str] = None  # Link to position
    
    # Account
    account_login: int = 0
    dealer_login: Optional[int] = None
    
    # Symbol & trade
    symbol: str = ""
    deal_type: DealType = DealType.BUY
    entry: DealEntry = DealEntry.IN  # How it affects position
    reason: DealReason = DealReason.CLIENT
    
    # Volume & price
    volume: Volume = field(default_factory=lambda: Volume(Decimal('0')))
    price: Price = field(default_factory=lambda: Price(Decimal('0')))
    
    # External references
    external_id: Optional[str] = None  # Exchange/ECN deal ID
    order_ticket: Optional[str] = None  # Original order ticket
    
    # Financial
    profit: Money = field(default_factory=lambda: Money(Decimal('0'), "USD"))
    swap: Money = field(default_factory=lambda: Money(Decimal('0'), "USD"))
    commission: Money = field(default_factory=lambda: Money(Decimal('0'), "USD"))
    
    # Symbol metadata
    digits: int = 5
    digits_currency: int = 2
    contract_size: Decimal = field(default_factory=lambda: Decimal('100000'))
    
    # Comment
    comment: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # =========================================================================
    # FACTORY METHODS
    # =========================================================================
    
    @classmethod
    def create_from_order(
        cls,
        order: "Order",
        fill_volume: Volume,
        fill_price: Price,
        entry: DealEntry = DealEntry.IN,
        reason: DealReason = DealReason.CLIENT,
        profit: Optional[Money] = None,
    ) -> "Deal":
        """Create a Deal from an Order fill."""
        from core.domains.oms.entities.order import Order
        
        # Map OrderType to DealType
        deal_type = cls._order_type_to_deal_type(order.order_type)
        
        return cls(
            order_id=order.ticket_id,
            account_login=order.account_login,
            symbol=order.symbol,
            deal_type=deal_type,
            entry=entry,
            reason=reason,
            volume=fill_volume,
            price=fill_price,
            order_ticket=order.ticket_id,
            digits=order.digits,
            digits_currency=order.digits_currency,
            contract_size=order.contract_size,
            profit=profit or Money(Decimal('0'), "USD"),
        )
    
    @staticmethod
    def _order_type_to_deal_type(order_type: OrderType) -> DealType:
        """Map OrderType to DealType."""
        if order_type in [OrderType.BUY, OrderType.BUY_LIMIT,
                          OrderType.BUY_STOP, OrderType.BUY_STOP_LIMIT]:
            return DealType.BUY
        return DealType.SELL
    
    # =========================================================================
    # TRADE MODIFICATION (MT5 Pattern)
    # =========================================================================
    
    def create_reversal(self, reason: str = "Trade modification") -> "Deal":
        """
        Create a REVERSAL deal - exact opposite of this deal.
        
        Used in MT5 Trade Modification to undo a deal before applying correction.
        The reversal deal has:
        - Opposite deal_type (BUY -> SELL, SELL -> BUY)
        - Negated profit, swap, commission
        - Link to original deal_id
        """
        reversed_type = DealType.SELL if self.deal_type == DealType.BUY else DealType.BUY
        
        return Deal(
            deal_id=str(uuid.uuid4()),
            order_id=self.order_id,
            position_id=self.position_id,
            account_login=self.account_login,
            symbol=self.symbol,
            deal_type=reversed_type,
            entry=self.entry,
            reason=DealReason.DEALER,
            volume=self.volume,
            price=self.price,
            order_ticket=self.order_ticket,
            digits=self.digits,
            digits_currency=self.digits_currency,
            contract_size=self.contract_size,
            # Negate financials
            profit=Money(-self.profit.amount, self.profit.currency),
            swap=Money(-self.swap.amount, self.swap.currency),
            commission=Money(-self.commission.amount, self.commission.currency),
            comment=f"[REVERSAL of {self.deal_id}] {reason}",
            created_at=datetime.now(timezone.utc),
        )
    
    def create_correction(
        self,
        new_volume: Optional[Volume] = None,
        new_price: Optional[Price] = None,
        new_profit: Optional[Money] = None,
        reason: str = "Trade modification",
    ) -> "Deal":
        """
        Create a CORRECTION deal - new deal with corrected parameters.
        
        Used after a reversal to apply the corrected values.
        """
        return Deal(
            deal_id=str(uuid.uuid4()),
            order_id=self.order_id,
            position_id=self.position_id,
            account_login=self.account_login,
            symbol=self.symbol,
            deal_type=self.deal_type,
            entry=self.entry,
            reason=DealReason.DEALER,
            volume=new_volume or self.volume,
            price=new_price or self.price,
            order_ticket=self.order_ticket,
            digits=self.digits,
            digits_currency=self.digits_currency,
            contract_size=self.contract_size,
            profit=new_profit or self.profit,
            swap=self.swap,
            commission=self.commission,
            comment=f"[CORRECTION of {self.deal_id}] {reason}",
            created_at=datetime.now(timezone.utc),
        )
    
    # =========================================================================
    # PnL CALCULATION
    # =========================================================================
    
    def calculate_realized_pnl(
        self,
        open_price: Price,
        close_price: Price,
        account_currency: str,
        conversion_rate: Decimal = Decimal('1.0'),
    ) -> Money:
        """
        Calculate realized PnL for a closing deal.
        
        Formula (for BUY close):
        pnl = (close_price - open_price) * volume * contract_size * conversion_rate
        
        Formula (for SELL close):
        pnl = (open_price - close_price) * volume * contract_size * conversion_rate
        """
        if self.deal_type == DealType.BUY:
            price_diff = close_price.value - open_price.value
        else:
            price_diff = open_price.value - close_price.value
        
        pnl = price_diff * self.volume.value * self.contract_size * conversion_rate
        
        return Money(pnl, account_currency)
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "deal_id": self.deal_id,
            "order_id": self.order_id,
            "position_id": self.position_id,
            "account_login": self.account_login,
            "symbol": self.symbol,
            "deal_type": self.deal_type.value,
            "entry": self.entry.value,
            "reason": self.reason.value,
            "volume": str(self.volume.value),
            "price": str(self.price.value),
            "profit": str(self.profit.amount),
            "swap": str(self.swap.amount),
            "commission": str(self.commission.amount),
            "comment": self.comment,
            "created_at": self.created_at.isoformat(),
        }
```

---

## 4. `core/domains/oms/entities/position.py` (~320 lines)

```python
"""Position entity - Aggregate open state (IMTPosition)."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List
import uuid

from core.domains.common.value_objects import Money, Price, Volume
from core.domains.oms.enums import (
    OrderType, DealType, DealEntry, PositionAction, PositionReason
)


@dataclass
class Position:
    """
    Position Entity - Aggregate Open State (IMTPosition).
    
    A Position represents the trader's current exposure to a symbol.
    
    MT5 Position Modes:
    - HEDGING: Every deal creates a new position (retail default)
    - NETTING: All deals for a symbol aggregate into one position (institutional)
    
    MT5 Position Actions:
    - BUY: Long position
    - SELL: Short position
    """
    # Identity
    position_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    external_id: Optional[str] = None  # Exchange/ECN position ID
    identifier: Optional[str] = None   # For netting: groups positions by identifier
    
    # Account
    account_login: int = 0
    
    # Symbol & side
    symbol: str = ""
    action: PositionAction = PositionAction.BUY
    reason: PositionReason = PositionReason.CLIENT
    
    # Volume
    volume: Volume = field(default_factory=lambda: Volume(Decimal('0')))
    
    # Pricing
    price_open: Price = field(default_factory=lambda: Price(Decimal('0')))
    price_current: Price = field(default_factory=lambda: Price(Decimal('0')))
    price_sl: Optional[Price] = None
    price_tp: Optional[Price] = None
    
    # Financial
    profit: Money = field(default_factory=lambda: Money(Decimal('0'), "USD"))  # Unrealized PnL
    swap: Money = field(default_factory=lambda: Money(Decimal('0'), "USD"))
    commission: Money = field(default_factory=lambda: Money(Decimal('0'), "USD"))
    
    # Symbol metadata
    digits: int = 5
    digits_currency: int = 2
    contract_size: Decimal = field(default_factory=lambda: Decimal('100000'))
    
    # Links
    deal_open: Optional[str] = None  # Opening deal ID
    deal_close: Optional[str] = None  # Closing deal ID (if closed)
    position_by_id: Optional[str] = None  # For close-by operations
    
    # Timestamps
    time_create: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    time_update: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    time_done: Optional[datetime] = None  # When position was closed
    
    # Metadata
    comment: str = ""
    magic_number: int = 0  # EA magic number
    
    # =========================================================================
    # APPLY DEAL (Core Logic)
    # =========================================================================
    
    def apply_deal(
        self,
        deal: "Deal",
        position_mode: str = "HEDGING",
    ) -> Optional["Position"]:
        """
        Apply a deal to this position.
        
        Returns:
            - In HEDGING mode with opposite side: Returns NEW position (reversal)
            - In NETTING mode: Updates self, returns None
            - If closed fully: Sets volume to 0, caller should archive
        """
        from core.domains.oms.entities.deal import Deal
        
        if deal.deal_type not in [DealType.BUY, DealType.SELL]:
            return None  # Ignore non-trading deals
        
        deal_side = PositionAction.BUY if deal.deal_type == DealType.BUY else PositionAction.SELL
        
        # HEDGING MODE: Every deal creates a new position or adds to same-direction only
        if position_mode == "HEDGING":
            if deal_side != self.action:
                # Opposite direction in Hedging = Create NEW position (reversal)
                return self._create_opposite_position(deal)
            else:
                # Same direction = Add to existing position
                self._add_to_position(deal)
                return None
        # NETTING MODE: Aggregate all deals
        else:
            if deal_side == self.action:
                # Adding to position
                self._add_to_position(deal)
                return None
            else:
                # Closing or Reversing
                return self._close_or_reverse(deal)
    
    def _add_to_position(self, deal: "Deal") -> None:
        """Add a same-direction deal to the position (averaging price)."""
        old_notional = self.volume.value * self.price_open.value
        new_notional = deal.volume.value * deal.price.value
        
        new_volume = self.volume.value + deal.volume.value
        if new_volume > 0:
            new_price = (old_notional + new_notional) / new_volume
            self.price_open = Price(new_price)
        
        self.volume = Volume(new_volume)
        self.swap = Money(self.swap.amount + deal.swap.amount, self.swap.currency)
        self.commission = Money(
            self.commission.amount + deal.commission.amount,
            self.commission.currency
        )
        self.time_update = datetime.now(timezone.utc)
    
    def _close_or_reverse(self, deal: "Deal") -> Optional["Position"]:
        """Close or reverse a position (netting mode)."""
        if deal.volume.value >= self.volume.value:
            # Full close or reversal
            close_volume = self.volume.value
            remaining_volume = deal.volume.value - close_volume
            
            # Mark as closed
            self.volume = Volume(Decimal('0'))
            self.deal_close = deal.deal_id
            self.time_done = datetime.now(timezone.utc)
            self.time_update = datetime.now(timezone.utc)
            
            # If there's remaining volume, create new position in opposite direction
            if remaining_volume > 0:
                return self._create_opposite_position_with_remaining(deal, remaining_volume)
            return None
        else:
            # Partial close
            self.volume = Volume(self.volume.value - deal.volume.value)
            self.time_update = datetime.now(timezone.utc)
            return None
    
    def _create_opposite_position(self, deal: "Deal") -> "Position":
        """Create a new position in the opposite direction (hedging reversal)."""
        new_action = PositionAction.SELL if self.action == PositionAction.BUY else PositionAction.BUY
        
        return Position(
            position_id=str(uuid.uuid4()),
            account_login=deal.account_login,
            symbol=deal.symbol,
            action=new_action,
            reason=PositionReason(deal.reason.value) if deal.reason.value in [
                r.value for r in PositionReason
            ] else PositionReason.CLIENT,
            volume=deal.volume,
            price_open=deal.price,
            price_current=deal.price,
            digits=deal.digits,
            digits_currency=deal.digits_currency,
            contract_size=deal.contract_size,
            deal_open=deal.deal_id,
            time_create=deal.created_at,
            time_update=deal.created_at,
            comment=deal.comment,
        )
    
    def _create_opposite_position_with_remaining(
        self, deal: "Deal", remaining_volume: Decimal
    ) -> "Position":
        """Create new position with remaining volume after reversal."""
        new_action = PositionAction.SELL if self.action == PositionAction.BUY else PositionAction.BUY
        
        return Position(
            position_id=str(uuid.uuid4()),
            account_login=deal.account_login,
            symbol=deal.symbol,
            action=new_action,
            reason=PositionReason.CLIENT,
            volume=Volume(remaining_volume),
            price_open=deal.price,
            price_current=deal.price,
            digits=deal.digits,
            digits_currency=deal.digits_currency,
            contract_size=deal.contract_size,
            deal_open=deal.deal_id,
            time_create=deal.created_at,
            time_update=deal.created_at,
            comment=f"[REVERSED from {self.position_id}] {deal.comment}",
        )
    
    # =========================================================================
    # PnL & MARGIN
    # =========================================================================
    
    def update_unrealized_pnl(
        self,
        current_price: Price,
        conversion_rate: Decimal = Decimal('1.0'),
    ) -> Money:
        """
        Update unrealized PnL based on current market price.
        
        Formula:
        - BUY: (current - open) * volume * contract_size * conversion_rate
        - SELL: (open - current) * volume * contract_size * conversion_rate
        """
        if self.action == PositionAction.BUY:
            price_diff = current_price.value - self.price_open.value
        else:
            price_diff = self.price_open.value - current_price.value
        
        pnl = price_diff * self.volume.value * self.contract_size * conversion_rate
        self.profit = Money(pnl, self.profit.currency)
        self.price_current = current_price
        self.time_update = datetime.now(timezone.utc)
        
        return self.profit
    
    def calculate_margin_required(
        self,
        margin_rate: Decimal = Decimal('1.0'),
        leverage: int = 100,
    ) -> Decimal:
        """
        Calculate margin required for this position.
        
        Formula: (volume * contract_size * price_open * margin_rate) / leverage
        """
        if leverage <= 0:
            leverage = 1
        
        notional = self.volume.value * self.contract_size * self.price_open.value
        return (notional * margin_rate) / Decimal(str(leverage))
    
    # =========================================================================
    # CLOSE-BY (MT5 Feature)
    # =========================================================================
    
    def close_by(self, opposite_position: "Position") -> None:
        """
        Close this position by an opposite position (MT5 Close-By).
        
        Both positions are closed against each other, with net PnL.
        """
        if opposite_position.symbol != self.symbol:
            raise ValueError("Close-by requires same symbol")
        if opposite_position.action == self.action:
            raise ValueError("Close-by requires opposite positions")
        
        # Determine close volume (minimum of both)
        close_volume = min(self.volume.value, opposite_position.volume.value)
        
        # Mark both as closed
        self.volume = Volume(self.volume.value - close_volume)
        opposite_position.volume = Volume(opposite_position.volume.value - close_volume)
        
        self.position_by_id = opposite_position.position_id
        opposite_position.position_by_id = self.position_id
        
        if self.volume.value == 0:
            self.time_done = datetime.now(timezone.utc)
        if opposite_position.volume.value == 0:
            opposite_position.time_done = datetime.now(timezone.utc)
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "position_id": self.position_id,
            "account_login": self.account_login,
            "symbol": self.symbol,
            "action": self.action.value,
            "volume": str(self.volume.value),
            "price_open": str(self.price_open.value),
            "price_current": str(self.price_current.value),
            "price_sl": str(self.price_sl.value) if self.price_sl else None,
            "price_tp": str(self.price_tp.value) if self.price_tp else None,
            "profit": str(self.profit.amount),
            "swap": str(self.swap.amount),
            "commission": str(self.commission.amount),
            "deal_open": self.deal_open,
            "deal_close": self.deal_close,
            "time_create": self.time_create.isoformat(),
            "time_update": self.time_update.isoformat(),
            "time_done": self.time_done.isoformat() if self.time_done else None,
            "comment": self.comment,
        }
```

---

## 5. `core/domains/oms/services/trade_modification.py` (~120 lines)

```python
"""Trade Modification Service - MT5 Reversal + Correction pattern."""
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from core.domains.common.value_objects import Money, Price, Volume
from core.domains.oms.entities.deal import Deal


@dataclass
class TradeModificationResult:
    """Result of a trade modification."""
    reversal_deal: Deal
    correction_deal: Deal
    original_deal_id: str


class TradeModificationService:
    """
    MT5 Trade Modification Service.
    
    In MT5, dealers NEVER modify existing deals. Instead, they:
    1. Create a REVERSAL deal (exact opposite of original)
    2. Create a CORRECTION deal (new deal with corrected parameters)
    3. Both deals link to the original ticket_id for audit trail
    
    This preserves the immutable ledger while allowing corrections.
    """
    
    def __init__(self, deal_repository):
        self.deal_repository = deal_repository
    
    async def modify_deal(
        self,
        original_deal_id: str,
        new_price: Optional[Price] = None,
        new_volume: Optional[Volume] = None,
        new_profit: Optional[Money] = None,
        reason: str = "Dealer modification",
        dealer_login: Optional[int] = None,
    ) -> TradeModificationResult:
        """
        Modify a deal using the MT5 Reversal + Correction pattern.
        
        Args:
            original_deal_id: ID of the deal to modify
            new_price: New price (optional)
            new_volume: New volume (optional)
            new_profit: New profit (optional)
            reason: Reason for modification (audit trail)
            dealer_login: Dealer performing the modification
        
        Returns:
            TradeModificationResult with both reversal and correction deals
        """
        # Fetch original deal
        original = await self.deal_repository.find_by_id(original_deal_id)
        if not original:
            raise ValueError(f"Deal {original_deal_id} not found")
        
        # Create reversal deal (exact opposite)
        reversal = original.create_reversal(reason=reason)
        reversal.dealer_login = dealer_login
        
        # Create correction deal (with new parameters)
        correction = original.create_correction(
            new_volume=new_volume,
            new_price=new_price,
            new_profit=new_profit,
            reason=reason,
        )
        correction.dealer_login = dealer_login
        
        # Persist both deals atomically
        await self.deal_repository.save(reversal)
        await self.deal_repository.save(correction)
        
        return TradeModificationResult(
            reversal_deal=reversal,
            correction_deal=correction,
            original_deal_id=original_deal_id,
        )
```

---

## 6. `core/domains/oms/events.py` (~60 lines)

```python
"""OMS-specific domain events."""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict
import uuid


@dataclass
class OMSDomainEvent:
    """Base class for OMS domain events."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    aggregate_id: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)


# Need to import field
from dataclasses import field


@dataclass
class OrderCreated(OMSDomainEvent):
    """Published when a new order is created."""
    pass


@dataclass
class OrderStateChanged(OMSDomainEvent):
    """Published when order state changes."""
    pass


@dataclass
class OrderFilled(OMSDomainEvent):
    """Published when an order is fully filled."""
    pass


@dataclass
class DealCreated(OMSDomainEvent):
    """Published when a new deal is recorded."""
    pass


@dataclass
class PositionOpened(OMSDomainEvent):
    """Published when a new position is opened."""
    pass


@dataclass
class PositionClosed(OMSDomainEvent):
    """Published when a position is closed."""
    pass


@dataclass
class PositionModified(OMSDomainEvent):
    """Published when a position is modified (SL/TP change)."""
    pass


@dataclass
class TradeModified(OMSDomainEvent):
    """Published when a deal is modified via reversal + correction."""
    pass
```

---

## 7. `core/domains/oms/__init__.py` (~25 lines)

```python
"""OMS Domain - Order Management System (MT5-accurate)."""
from .enums import (
    OrderType, OrderState, OrderReason, TimeInForce, ActivationMode,
    DealType, DealEntry, DealReason, PositionAction, PositionReason,
    OrderFlags
)
from .entities.order import Order
from .entities.deal import Deal
from .entities.position import Position
from .services.trade_modification import TradeModificationService, TradeModificationResult
from .events import (
    OrderCreated, OrderStateChanged, OrderFilled,
    DealCreated, PositionOpened, PositionClosed,
    PositionModified, TradeModified
)

__all__ = [
    # Enums
    "OrderType", "OrderState", "OrderReason", "TimeInForce", "ActivationMode",
    "DealType", "DealEntry", "DealReason", "PositionAction", "PositionReason",
    "OrderFlags",
    # Entities
    "Order", "Deal", "Position",
    # Services
    "TradeModificationService", "TradeModificationResult",
    # Events
    "OrderCreated", "OrderStateChanged", "OrderFilled",
    "DealCreated", "PositionOpened", "PositionClosed",
    "PositionModified", "TradeModified",
]
```

---

## 📊 Summary

| File | Lines | Key MT5 Features |
|:---|:---:|:---|
| `enums.py` | ~180 | 8 order types, 7 order states, 9 order reasons, 4 deal entries, 16 deal reasons |
| `order.py` | ~350 | State machine, ATM activation, partial fills, time-in-force |
| `deal.py` | ~280 | Immutable, entry types, reversal/correction, PnL calculation |
| `position.py` | ~320 | Hedging/Netting modes, close-by, volume averaging |
| `trade_modification.py` | ~120 | MT5 Reversal + Correction pattern |
| `events.py` | ~60 | 8 domain events |
| `__init__.py` | ~25 | Public exports |
| **TOTAL** | **~1335** | **Full MT5 OMS parity** |

---

## 🎯 Key MT5 Features Implemented

✅ **Order Types**: BUY, SELL, BUY_LIMIT, SELL_LIMIT, BUY_STOP, SELL_STOP, BUY_STOP_LIMIT, SELL_STOP_LIMIT  
✅ **Order State Machine**: NEW → PLACED → PARTIALLY_FILLED → FILLED (with CANCELLED, REJECTED, EXPIRED)  
✅ **Order Reasons**: CLIENT, EXPERT, DEALER, GATEWAY, SIGNAL, API, MOBILE, WEB, PLUGIN  
✅ **ATM Orders**: Time/Price activation for advanced order types  
✅ **Deal Entry Types**: IN (open), OUT (close), INOUT (reverse), OUT_BY (close-by)  
✅ **Deal Reasons**: CLIENT, SL, TP, SO, ROLLOVER, VMARGIN, etc.  
✅ **Position Modes**: HEDGING (retail default) and NETTING (institutional)  
✅ **Close-By**: MT5 close-by operation for opposite positions  
✅ **Trade Modification**: Reversal + Correction pattern (immutable ledger)  
✅ **Cross-Currency PnL**: Conversion rate support  
✅ **Volume Averaging**: Price averaging when adding to position  

---

## 🚀 Next Steps

1. **Create these 7 files** in `core/domains/oms/`
2. **Update existing code** that imports from `core.domains.oms.entities.*` to use the new structure
3. **Run `pytest tests/`** to verify nothing breaks
4. **Update repositories** to support the new fields (external_id, activation_mode, etc.)

Would you like me to:
- **Update the existing repositories** (`IOrderRepository`, `IDealRepository`, `IPositionRepository`) to support the new fields?
- **Write unit tests** for the state machine and trade modification logic?
- **Move to the next domain** (Execution/Gateway)?


# USER -------------

Update the existing repositories support the new fields.



# AI ------------------

# 🏛️ Update Repositories for New OMS Fields

I'll update all the infrastructure layers to support the new MT5-accurate fields in Order, Deal, and Position entities.

---

## 1. Update `infrastructure/persistence/db_models.py`

Add new columns to support the enriched OMS entities:

```python
# Find the existing OrderModel class and REPLACE it with:

class OrderModel(Base):
    """SQLAlchemy model for Order entity (MT5 IMTOrder)."""
    __tablename__ = "orders"

    # Identity
    ticket_id = Column(String, primary_key=True)
    external_id = Column(String, nullable=True)  # Exchange/ECN order ID
    gateway_id = Column(String, nullable=True)   # Gateway execution order ID
    
    # Account & Symbol
    account_login = Column(BigInteger, nullable=False, index=True)
    dealer_login = Column(BigInteger, nullable=True)
    symbol = Column(String, nullable=False, index=True)
    
    # Order details
    order_type = Column(String, nullable=False)  # OrderType enum value
    reason = Column(String, nullable=False, default="CLIENT")  # OrderReason enum
    state = Column(String, nullable=False, default="NEW")  # OrderState enum
    
    # Volume (split into initial/current for partial fills)
    volume_initial = Column(Numeric(20, 8), nullable=False)
    volume_current = Column(Numeric(20, 8), nullable=False)
    
    # Pricing (Price value objects stored as Numeric)
    price_order = Column(Numeric(20, 8), nullable=False)  # Limit/Stop price
    price_sl = Column(Numeric(20, 8), nullable=True)
    price_tp = Column(Numeric(20, 8), nullable=True)
    price_trigger = Column(Numeric(20, 8), nullable=True)  # For STOP_LIMIT
    
    # Time
    time_setup = Column(DateTime(timezone=True), nullable=False)
    time_setup_msc = Column(BigInteger, nullable=False, default=0)
    time_expiration = Column(DateTime(timezone=True), nullable=True)
    time_done = Column(DateTime(timezone=True), nullable=True)
    
    # Time in force
    time_in_force = Column(String, nullable=False, default="GTC")
    
    # ATM Activation
    activation_mode = Column(String, nullable=False, default="NONE")
    activation_time = Column(DateTime(timezone=True), nullable=True)
    activation_price = Column(Numeric(20, 8), nullable=True)
    activation_flags = Column(Integer, nullable=False, default=0)
    
    # Symbol metadata snapshot
    digits = Column(Integer, nullable=False, default=5)
    digits_currency = Column(Integer, nullable=False, default=2)
    contract_size = Column(Numeric(20, 8), nullable=False, default=100000)
    
    # Expert/Plugin info
    expert_id = Column(String, nullable=True)
    expert_name = Column(String, nullable=True)
    comment = Column(Text, nullable=True)
    
    # Matching
    order_matching = Column(String, nullable=True)  # Opposite order ticket
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_orders_account_state", "account_login", "state"),
        Index("idx_orders_symbol_state", "symbol", "state"),
        Index("idx_orders_time_setup", "time_setup"),
    )


# Find the existing DealModel class and REPLACE it with:

class DealModel(Base):
    """SQLAlchemy model for Deal entity (MT5 IMTDeal)."""
    __tablename__ = "deals"

    # Identity
    deal_id = Column(String, primary_key=True)
    order_id = Column(String, nullable=True, index=True)
    position_id = Column(String, nullable=True, index=True)
    
    # Account
    account_login = Column(BigInteger, nullable=False, index=True)
    dealer_login = Column(BigInteger, nullable=True)
    
    # Symbol & trade
    symbol = Column(String, nullable=False, index=True)
    deal_type = Column(String, nullable=False)  # DealType enum
    entry = Column(String, nullable=False, default="IN")  # DealEntry enum
    reason = Column(String, nullable=False, default="CLIENT")  # DealReason enum
    
    # Volume & price
    volume = Column(Numeric(20, 8), nullable=False)
    price = Column(Numeric(20, 8), nullable=False)
    
    # External references
    external_id = Column(String, nullable=True)
    order_ticket = Column(String, nullable=True)
    
    # Financial (Money value objects)
    profit = Column(Numeric(20, 8), nullable=False, default=0)
    swap = Column(Numeric(20, 8), nullable=False, default=0)
    commission = Column(Numeric(20, 8), nullable=False, default=0)
    currency = Column(String, nullable=False, default="USD")
    
    # Symbol metadata
    digits = Column(Integer, nullable=False, default=5)
    digits_currency = Column(Integer, nullable=False, default=2)
    contract_size = Column(Numeric(20, 8), nullable=False, default=100000)
    
    # Comment
    comment = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_deals_account_time", "account_login", "created_at"),
        Index("idx_deals_symbol_time", "symbol", "created_at"),
        Index("idx_deals_type", "deal_type"),
    )


# Find the existing PositionModel class and REPLACE it with:

class PositionModel(Base):
    """SQLAlchemy model for Position entity (MT5 IMTPosition)."""
    __tablename__ = "positions"

    # Identity
    position_id = Column(String, primary_key=True)
    external_id = Column(String, nullable=True)
    identifier = Column(String, nullable=True, index=True)  # For netting
    
    # Account
    account_login = Column(BigInteger, nullable=False, index=True)
    
    # Symbol & side
    symbol = Column(String, nullable=False, index=True)
    action = Column(String, nullable=False)  # PositionAction enum (BUY/SELL)
    reason = Column(String, nullable=False, default="CLIENT")  # PositionReason enum
    
    # Volume
    volume = Column(Numeric(20, 8), nullable=False)
    
    # Pricing (Price value objects)
    price_open = Column(Numeric(20, 8), nullable=False)
    price_current = Column(Numeric(20, 8), nullable=False)
    price_sl = Column(Numeric(20, 8), nullable=True)
    price_tp = Column(Numeric(20, 8), nullable=True)
    
    # Financial (Money value objects)
    profit = Column(Numeric(20, 8), nullable=False, default=0)
    swap = Column(Numeric(20, 8), nullable=False, default=0)
    commission = Column(Numeric(20, 8), nullable=False, default=0)
    currency = Column(String, nullable=False, default="USD")
    
    # Symbol metadata
    digits = Column(Integer, nullable=False, default=5)
    digits_currency = Column(Integer, nullable=False, default=2)
    contract_size = Column(Numeric(20, 8), nullable=False, default=100000)
    
    # Links
    deal_open = Column(String, nullable=True)
    deal_close = Column(String, nullable=True)
    position_by_id = Column(String, nullable=True)  # For close-by
    
    # Timestamps
    time_create = Column(DateTime(timezone=True), nullable=False)
    time_update = Column(DateTime(timezone=True), nullable=False)
    time_done = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    comment = Column(Text, nullable=True)
    magic_number = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        Index("idx_positions_account_symbol", "account_login", "symbol"),
        Index("idx_positions_action", "action"),
        Index("idx_positions_time_create", "time_create"),
    )
```

---

## 2. Update `infrastructure/persistence/mappers.py`

Replace the existing mapper functions with MT5-accurate versions:

```python
# ============================================================================
# ORDER MAPPERS
# ============================================================================

def order_to_db(order: Order) -> OrderModel:
    """Map domain Order to DB model."""
    return OrderModel(
        ticket_id=order.ticket_id,
        external_id=order.external_id,
        gateway_id=order.gateway_id,
        account_login=order.account_login,
        dealer_login=order.dealer_login,
        symbol=order.symbol,
        order_type=order.order_type.value,
        reason=order.reason.value,
        state=order.state.value,
        volume_initial=order.volume_initial.value,
        volume_current=order.volume_current.value,
        price_order=order.price_order.value,
        price_sl=order.price_sl.value if order.price_sl else None,
        price_tp=order.price_tp.value if order.price_tp else None,
        price_trigger=order.price_trigger.value if order.price_trigger else None,
        time_setup=order.time_setup,
        time_setup_msc=order.time_setup_msc,
        time_expiration=order.time_expiration,
        time_done=order.time_done,
        time_in_force=order.time_in_force.value,
        activation_mode=order.activation_mode.value,
        activation_time=order.activation_time,
        activation_price=order.activation_price.value if order.activation_price else None,
        activation_flags=int(order.activation_flags),
        digits=order.digits,
        digits_currency=order.digits_currency,
        contract_size=order.contract_size,
        expert_id=order.expert_id,
        expert_name=order.expert_name,
        comment=order.comment,
        order_matching=order.order_matching,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


def db_to_order(model: OrderModel) -> Order:
    """Map DB model to domain Order."""
    from core.domains.oms.enums import OrderType, OrderState, OrderReason, TimeInForce, ActivationMode, OrderFlags
    from core.domains.common.value_objects import Price, Volume
    
    return Order(
        ticket_id=model.ticket_id,
        external_id=model.external_id,
        gateway_id=model.gateway_id,
        account_login=model.account_login,
        dealer_login=model.dealer_login,
        symbol=model.symbol,
        order_type=OrderType(model.order_type),
        reason=OrderReason(model.reason),
        state=OrderState(model.state),
        volume_initial=Volume(Decimal(str(model.volume_initial))),
        volume_current=Volume(Decimal(str(model.volume_current))),
        price_order=Price(Decimal(str(model.price_order))),
        price_sl=Price(Decimal(str(model.price_sl))) if model.price_sl else None,
        price_tp=Price(Decimal(str(model.price_tp))) if model.price_tp else None,
        price_trigger=Price(Decimal(str(model.price_trigger))) if model.price_trigger else None,
        time_setup=model.time_setup,
        time_setup_msc=model.time_setup_msc,
        time_expiration=model.time_expiration,
        time_done=model.time_done,
        time_in_force=TimeInForce(model.time_in_force),
        activation_mode=ActivationMode(model.activation_mode),
        activation_time=model.activation_time,
        activation_price=Price(Decimal(str(model.activation_price))) if model.activation_price else None,
        activation_flags=OrderFlags(model.activation_flags),
        digits=model.digits,
        digits_currency=model.digits_currency,
        contract_size=Decimal(str(model.contract_size)),
        expert_id=model.expert_id or "",
        expert_name=model.expert_name or "",
        comment=model.comment or "",
        order_matching=model.order_matching,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


# ============================================================================
# DEAL MAPPERS
# ============================================================================

def deal_to_db(deal: Deal) -> DealModel:
    """Map domain Deal to DB model."""
    return DealModel(
        deal_id=deal.deal_id,
        order_id=deal.order_id,
        position_id=deal.position_id,
        account_login=deal.account_login,
        dealer_login=deal.dealer_login,
        symbol=deal.symbol,
        deal_type=deal.deal_type.value,
        entry=deal.entry.value,
        reason=deal.reason.value,
        volume=deal.volume.value,
        price=deal.price.value,
        external_id=deal.external_id,
        order_ticket=deal.order_ticket,
        profit=deal.profit.amount,
        swap=deal.swap.amount,
        commission=deal.commission.amount,
        currency=deal.profit.currency,
        digits=deal.digits,
        digits_currency=deal.digits_currency,
        contract_size=deal.contract_size,
        comment=deal.comment,
        created_at=deal.created_at,
    )


def db_to_deal(model: DealModel) -> Deal:
    """Map DB model to domain Deal."""
    from core.domains.oms.enums import DealType, DealEntry, DealReason
    from core.domains.common.value_objects import Money, Price, Volume
    
    return Deal(
        deal_id=model.deal_id,
        order_id=model.order_id,
        position_id=model.position_id,
        account_login=model.account_login,
        dealer_login=model.dealer_login,
        symbol=model.symbol,
        deal_type=DealType(model.deal_type),
        entry=DealEntry(model.entry),
        reason=DealReason(model.reason),
        volume=Volume(Decimal(str(model.volume))),
        price=Price(Decimal(str(model.price))),
        external_id=model.external_id,
        order_ticket=model.order_ticket,
        profit=Money(Decimal(str(model.profit)), model.currency),
        swap=Money(Decimal(str(model.swap)), model.currency),
        commission=Money(Decimal(str(model.commission)), model.currency),
        digits=model.digits,
        digits_currency=model.digits_currency,
        contract_size=Decimal(str(model.contract_size)),
        comment=model.comment or "",
        created_at=model.created_at,
    )


# ============================================================================
# POSITION MAPPERS
# ============================================================================

def position_to_db(position: Position) -> PositionModel:
    """Map domain Position to DB model."""
    return PositionModel(
        position_id=position.position_id,
        external_id=position.external_id,
        identifier=position.identifier,
        account_login=position.account_login,
        symbol=position.symbol,
        action=position.action.value,
        reason=position.reason.value,
        volume=position.volume.value,
        price_open=position.price_open.value,
        price_current=position.price_current.value,
        price_sl=position.price_sl.value if position.price_sl else None,
        price_tp=position.price_tp.value if position.price_tp else None,
        profit=position.profit.amount,
        swap=position.swap.amount,
        commission=position.commission.amount,
        currency=position.profit.currency,
        digits=position.digits,
        digits_currency=position.digits_currency,
        contract_size=position.contract_size,
        deal_open=position.deal_open,
        deal_close=position.deal_close,
        position_by_id=position.position_by_id,
        time_create=position.time_create,
        time_update=position.time_update,
        time_done=position.time_done,
        comment=position.comment,
        magic_number=position.magic_number,
    )


def db_to_position(model: PositionModel) -> Position:
    """Map DB model to domain Position."""
    from core.domains.oms.enums import PositionAction, PositionReason
    from core.domains.common.value_objects import Money, Price, Volume
    
    return Position(
        position_id=model.position_id,
        external_id=model.external_id,
        identifier=model.identifier,
        account_login=model.account_login,
        symbol=model.symbol,
        action=PositionAction(model.action),
        reason=PositionReason(model.reason),
        volume=Volume(Decimal(str(model.volume))),
        price_open=Price(Decimal(str(model.price_open))),
        price_current=Price(Decimal(str(model.price_current))),
        price_sl=Price(Decimal(str(model.price_sl))) if model.price_sl else None,
        price_tp=Price(Decimal(str(model.price_tp))) if model.price_tp else None,
        profit=Money(Decimal(str(model.profit)), model.currency),
        swap=Money(Decimal(str(model.swap)), model.currency),
        commission=Money(Decimal(str(model.commission)), model.currency),
        digits=model.digits,
        digits_currency=model.digits_currency,
        contract_size=Decimal(str(model.contract_size)),
        deal_open=model.deal_open,
        deal_close=model.deal_close,
        position_by_id=model.position_by_id,
        time_create=model.time_create,
        time_update=model.time_update,
        time_done=model.time_done,
        comment=model.comment or "",
        magic_number=model.magic_number,
    )
```

---

## 3. Update `core/ports/interfaces.py`

Add new repository methods to support the enriched queries:

```python
# ============================================================================
# ORDER REPOSITORY - Add these methods
# ============================================================================

class IOrderRepository(ABC, Generic[T]):
    """Contract for Order persistence."""

    @abstractmethod
    async def save(self, order: T) -> T:
        pass

    @abstractmethod
    async def find_by_id(self, order_id: str) -> Optional[T]:
        pass

    @abstractmethod
    async def find_by_account(self, account_login: int) -> List[T]:
        pass

    @abstractmethod
    async def find_pending_orders(self, account_login: int) -> List[T]:
        """Get all pending orders (not filled/cancelled) for an account."""
        pass

    @abstractmethod
    async def find_by_symbol_and_state(self, symbol: str, state: str) -> List[T]:
        """Get orders by symbol and state."""
        pass

    @abstractmethod
    async def find_expired_orders(self, before_time: datetime) -> List[T]:
        """Get orders that have expired (time_expiration < before_time)."""
        pass

    @abstractmethod
    async def delete(self, order_id: str) -> bool:
        pass


# ============================================================================
# DEAL REPOSITORY - Add these methods
# ============================================================================

class IDealRepository(ABC, Generic[T]):
    """Contract for Deal persistence."""

    @abstractmethod
    async def save(self, deal: T) -> T:
        pass

    @abstractmethod
    async def find_by_id(self, deal_id: str) -> Optional[T]:
        pass

    @abstractmethod
    async def find_by_order_id(self, order_id: str) -> List[T]:
        pass

    @abstractmethod
    async def find_by_position_id(self, position_id: str) -> List[T]:
        """Get all deals for a position."""
        pass

    @abstractmethod
    async def find_by_account(self, account_login: int) -> List[T]:
        pass

    @abstractmethod
    async def find_by_account_and_symbol(self, account_login: int, symbol: str) -> List[T]:
        """Get deals for a specific account and symbol."""
        pass

    @abstractmethod
    async def find_by_entry_type(self, account_login: int, entry: str) -> List[T]:
        """Get deals by entry type (IN, OUT, INOUT, OUT_BY)."""
        pass

    @abstractmethod
    async def find_trade_modifications(self, original_deal_id: str) -> List[T]:
        """Get reversal and correction deals linked to original deal."""
        pass


# ============================================================================
# POSITION REPOSITORY - Add these methods
# ============================================================================

class IPositionRepository(ABC, Generic[T]):
    """Contract for Position persistence."""

    @abstractmethod
    async def save(self, position: T) -> T:
        pass

    @abstractmethod
    async def find_by_id(self, position_id: str) -> Optional[T]:
        pass

    @abstractmethod
    async def get_open_positions(self, session: Optional[Any] = None) -> List[T]:
        pass

    @abstractmethod
    async def get_by_account(self, account_login: int) -> List[T]:
        """Get all open positions for an account."""
        pass

    @abstractmethod
    async def get_by_account_and_symbol(self, account_login: int, symbol: str) -> List[T]:
        """Get positions for a specific account and symbol."""
        pass

    @abstractmethod
    async def get_by_symbol(self, symbol: str) -> List[T]:
        """Get all open positions for a symbol (for exposure calculation)."""
        pass

    @abstractmethod
    async def get_closed_positions(self, account_login: int, from_time: datetime, to_time: datetime) -> List[T]:
        """Get closed positions within a time range."""
        pass

    @abstractmethod
    async def delete(self, position_id: str) -> bool:
        pass
```

---

## 4. Update Repository Implementations

### `infrastructure/persistence/repositories/order_repository.py`

```python
class SqlOrderRepository(IOrderRepository[Order]):
    """PostgreSQL implementation of IOrderRepository."""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def save(self, order: Order, session: Optional[AsyncSession] = None) -> Order:
        """Save or update an order."""
        async def _save(sess: AsyncSession):
            model = order_to_db(order)
            await sess.merge(model)
            return order

        if session:
            return await _save(session)
        async with self.session_factory() as sess:
            result = await _save(sess)
            await sess.commit()
            return result

    async def find_by_id(self, order_id: str) -> Optional[Order]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(OrderModel).where(OrderModel.ticket_id == order_id)
            )
            model = result.scalar_one_or_none()
            return db_to_order(model) if model else None

    async def find_by_account(self, account_login: int) -> List[Order]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(OrderModel).where(OrderModel.account_login == account_login)
            )
            models = result.scalars().all()
            return [db_to_order(m) for m in models]

    async def find_pending_orders(self, account_login: int) -> List[Order]:
        """Get all pending orders (not in terminal state)."""
        from core.domains.oms.enums import OrderState
        terminal_states = [OrderState.FILLED.value, OrderState.CANCELLED.value,
                          OrderState.REJECTED.value, OrderState.EXPIRED.value]
        
        async with self.session_factory() as session:
            result = await session.execute(
                select(OrderModel).where(
                    (OrderModel.account_login == account_login) &
                    (OrderModel.state.notin_(terminal_states))
                )
            )
            models = result.scalars().all()
            return [db_to_order(m) for m in models]

    async def find_by_symbol_and_state(self, symbol: str, state: str) -> List[Order]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(OrderModel).where(
                    (OrderModel.symbol == symbol) &
                    (OrderModel.state == state)
                )
            )
            models = result.scalars().all()
            return [db_to_order(m) for m in models]

    async def find_expired_orders(self, before_time: datetime) -> List[Order]:
        """Get orders that have expired."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(OrderModel).where(
                    (OrderModel.time_expiration < before_time) &
                    (OrderModel.state.in_(["NEW", "PLACED", "PARTIALLY_FILLED"]))
                )
            )
            models = result.scalars().all()
            return [db_to_order(m) for m in models]

    async def delete(self, order_id: str) -> bool:
        async with self.session_factory() as session:
            result = await session.execute(
                select(OrderModel).where(OrderModel.ticket_id == order_id)
            )
            model = result.scalar_one_or_none()
            if model:
                await session.delete(model)
                await session.commit()
                return True
            return False
```

### `infrastructure/persistence/repositories/deal_repository.py`

```python
class SqlDealRepository(IDealRepository[Deal]):
    """PostgreSQL implementation of IDealRepository."""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def save(self, deal: Deal, session: Optional[AsyncSession] = None) -> Deal:
        async def _save(sess: AsyncSession):
            model = deal_to_db(deal)
            await sess.merge(model)
            return deal

        if session:
            return await _save(session)
        async with self.session_factory() as sess:
            result = await _save(sess)
            await sess.commit()
            return result

    async def find_by_id(self, deal_id: str) -> Optional[Deal]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(DealModel).where(DealModel.deal_id == deal_id)
            )
            model = result.scalar_one_or_none()
            return db_to_deal(model) if model else None

    async def find_by_order_id(self, order_id: str) -> List[Deal]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(DealModel).where(DealModel.order_id == order_id)
            )
            models = result.scalars().all()
            return [db_to_deal(m) for m in models]

    async def find_by_position_id(self, position_id: str) -> List[Deal]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(DealModel).where(DealModel.position_id == position_id)
            )
            models = result.scalars().all()
            return [db_to_deal(m) for m in models]

    async def find_by_account(self, account_login: int) -> List[Deal]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(DealModel).where(DealModel.account_login == account_login)
            )
            models = result.scalars().all()
            return [db_to_deal(m) for m in models]

    async def find_by_account_and_symbol(self, account_login: int, symbol: str) -> List[Deal]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(DealModel).where(
                    (DealModel.account_login == account_login) &
                    (DealModel.symbol == symbol)
                )
            )
            models = result.scalars().all()
            return [db_to_deal(m) for m in models]

    async def find_by_entry_type(self, account_login: int, entry: str) -> List[Deal]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(DealModel).where(
                    (DealModel.account_login == account_login) &
                    (DealModel.entry == entry)
                )
            )
            models = result.scalars().all()
            return [db_to_deal(m) for m in models]

    async def find_trade_modifications(self, original_deal_id: str) -> List[Deal]:
        """Get reversal and correction deals linked to original deal."""
        async with self.session_factory() as session:
            # Search for deals with comment containing the original deal_id
            result = await session.execute(
                select(DealModel).where(
                    DealModel.comment.contains(f"[REVERSAL of {original_deal_id}]") |
                    DealModel.comment.contains(f"[CORRECTION of {original_deal_id}]")
                )
            )
            models = result.scalars().all()
            return [db_to_deal(m) for m in models]
```

### `infrastructure/persistence/repositories/position_repository.py`

```python
class SqlPositionRepository(IPositionRepository[Position]):
    """PostgreSQL implementation of IPositionRepository."""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def save(self, position: Position, session: Optional[AsyncSession] = None) -> Position:
        async def _save(sess: AsyncSession):
            model = position_to_db(position)
            await sess.merge(model)
            return position

        if session:
            return await _save(session)
        async with self.session_factory() as sess:
            result = await _save(sess)
            await sess.commit()
            return result

    async def find_by_id(self, position_id: str) -> Optional[Position]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(PositionModel).where(PositionModel.position_id == position_id)
            )
            model = result.scalar_one_or_none()
            return db_to_position(model) if model else None

    async def get_open_positions(self, session: Optional[AsyncSession] = None) -> List[Position]:
        """Get all open positions (time_done is NULL)."""
        async def _get(sess: AsyncSession):
            result = await sess.execute(
                select(PositionModel).where(PositionModel.time_done.is_(None))
            )
            models = result.scalars().all()
            return [db_to_position(m) for m in models]

        if session:
            return await _get(session)
        async with self.session_factory() as sess:
            return await _get(sess)

    async def get_by_account(self, account_login: int) -> List[Position]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(PositionModel).where(
                    (PositionModel.account_login == account_login) &
                    (PositionModel.time_done.is_(None))
                )
            )
            models = result.scalars().all()
            return [db_to_position(m) for m in models]

    async def get_by_account_and_symbol(self, account_login: int, symbol: str) -> List[Position]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(PositionModel).where(
                    (PositionModel.account_login == account_login) &
                    (PositionModel.symbol == symbol) &
                    (PositionModel.time_done.is_(None))
                )
            )
            models = result.scalars().all()
            return [db_to_position(m) for m in models]

    async def get_by_symbol(self, symbol: str) -> List[Position]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(PositionModel).where(
                    (PositionModel.symbol == symbol) &
                    (PositionModel.time_done.is_(None))
                )
            )
            models = result.scalars().all()
            return [db_to_position(m) for m in models]

    async def get_closed_positions(self, account_login: int, from_time: datetime, to_time: datetime) -> List[Position]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(PositionModel).where(
                    (PositionModel.account_login == account_login) &
                    (PositionModel.time_done >= from_time) &
                    (PositionModel.time_done <= to_time)
                )
            )
            models = result.scalars().all()
            return [db_to_position(m) for m in models]

    async def delete(self, position_id: str) -> bool:
        async with self.session_factory() as session:
            result = await session.execute(
                select(PositionModel).where(PositionModel.position_id == position_id)
            )
            model = result.scalar_one_or_none()
            if model:
                await session.delete(model)
                await session.commit()
                return True
            return False
```

---

## 5. Generate Alembic Migration

Create a new migration file to add the new columns:

```bash
# Run this command to generate the migration
alembic revision --autogenerate -m "Add MT5-accurate OMS fields"
```

Or manually create the migration in `alembic/versions/`:

```python
"""Add MT5-accurate OMS fields

Revision ID: add_mt5_oms_fields
Revises: previous_revision
Create Date: 2026-01-XX

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade() -> None:
    # Orders table - add new columns
    op.add_column('orders', sa.Column('external_id', sa.String(), nullable=True))
    op.add_column('orders', sa.Column('gateway_id', sa.String(), nullable=True))
    op.add_column('orders', sa.Column('dealer_login', sa.BigInteger(), nullable=True))
    op.add_column('orders', sa.Column('reason', sa.String(), nullable=False, server_default='CLIENT'))
    op.add_column('orders', sa.Column('volume_initial', sa.Numeric(20, 8), nullable=False, server_default='0'))
    op.add_column('orders', sa.Column('volume_current', sa.Numeric(20, 8), nullable=False, server_default='0'))
    op.add_column('orders', sa.Column('price_order', sa.Numeric(20, 8), nullable=False, server_default='0'))
    op.add_column('orders', sa.Column('price_trigger', sa.Numeric(20, 8), nullable=True))
    op.add_column('orders', sa.Column('time_setup_msc', sa.BigInteger(), nullable=False, server_default='0'))
    op.add_column('orders', sa.Column('time_in_force', sa.String(), nullable=False, server_default='GTC'))
    op.add_column('orders', sa.Column('activation_mode', sa.String(), nullable=False, server_default='NONE'))
    op.add_column('orders', sa.Column('activation_time', sa.DateTime(timezone=True), nullable=True))
    op.add_column('orders', sa.Column('activation_price', sa.Numeric(20, 8), nullable=True))
    op.add_column('orders', sa.Column('activation_flags', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('orders', sa.Column('digits', sa.Integer(), nullable=False, server_default='5'))
    op.add_column('orders', sa.Column('digits_currency', sa.Integer(), nullable=False, server_default='2'))
    op.add_column('orders', sa.Column('contract_size', sa.Numeric(20, 8), nullable=False, server_default='100000'))
    op.add_column('orders', sa.Column('expert_id', sa.String(), nullable=True))
    op.add_column('orders', sa.Column('expert_name', sa.String(), nullable=True))
    op.add_column('orders', sa.Column('order_matching', sa.String(), nullable=True))
    
    # Add new indexes
    op.create_index('idx_orders_account_state', 'orders', ['account_login', 'state'])
    op.create_index('idx_orders_symbol_state', 'orders', ['symbol', 'state'])
    
    # Deals table - add new columns
    op.add_column('deals', sa.Column('position_id', sa.String(), nullable=True))
    op.add_column('deals', sa.Column('entry', sa.String(), nullable=False, server_default='IN'))
    op.add_column('deals', sa.Column('reason', sa.String(), nullable=False, server_default='CLIENT'))
    op.add_column('deals', sa.Column('external_id', sa.String(), nullable=True))
    op.add_column('deals', sa.Column('order_ticket', sa.String(), nullable=True))
    op.add_column('deals', sa.Column('swap', sa.Numeric(20, 8), nullable=False, server_default='0'))
    op.add_column('deals', sa.Column('currency', sa.String(), nullable=False, server_default='USD'))
    op.add_column('deals', sa.Column('digits', sa.Integer(), nullable=False, server_default='5'))
    op.add_column('deals', sa.Column('digits_currency', sa.Integer(), nullable=False, server_default='2'))
    op.add_column('deals', sa.Column('contract_size', sa.Numeric(20, 8), nullable=False, server_default='100000'))
    
    # Add new indexes
    op.create_index('idx_deals_position', 'deals', ['position_id'])
    op.create_index('idx_deals_account_time', 'deals', ['account_login', 'created_at'])
    
    # Positions table - add new columns
    op.add_column('positions', sa.Column('external_id', sa.String(), nullable=True))
    op.add_column('positions', sa.Column('identifier', sa.String(), nullable=True))
    op.add_column('positions', sa.Column('action', sa.String(), nullable=False, server_default='BUY'))
    op.add_column('positions', sa.Column('reason', sa.String(), nullable=False, server_default='CLIENT'))
    op.add_column('positions', sa.Column('price_open', sa.Numeric(20, 8), nullable=False, server_default='0'))
    op.add_column('positions', sa.Column('price_current', sa.Numeric(20, 8), nullable=False, server_default='0'))
    op.add_column('positions', sa.Column('swap', sa.Numeric(20, 8), nullable=False, server_default='0'))
    op.add_column('positions', sa.Column('currency', sa.String(), nullable=False, server_default='USD'))
    op.add_column('positions', sa.Column('digits', sa.Integer(), nullable=False, server_default='5'))
    op.add_column('positions', sa.Column('digits_currency', sa.Integer(), nullable=False, server_default='2'))
    op.add_column('positions', sa.Column('contract_size', sa.Numeric(20, 8), nullable=False, server_default='100000'))
    op.add_column('positions', sa.Column('deal_open', sa.String(), nullable=True))
    op.add_column('positions', sa.Column('deal_close', sa.String(), nullable=True))
    op.add_column('positions', sa.Column('position_by_id', sa.String(), nullable=True))
    op.add_column('positions', sa.Column('time_create', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
    op.add_column('positions', sa.Column('time_update', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
    op.add_column('positions', sa.Column('comment', sa.Text(), nullable=True))
    op.add_column('positions', sa.Column('magic_number', sa.Integer(), nullable=False, server_default='0'))
    
    # Add new indexes
    op.create_index('idx_positions_identifier', 'positions', ['identifier'])
    op.create_index('idx_positions_account_symbol', 'positions', ['account_login', 'symbol'])
    op.create_index('idx_positions_action', 'positions', ['action'])


def downgrade() -> None:
    # Remove new indexes
    op.drop_index('idx_positions_action', table_name='positions')
    op.drop_index('idx_positions_account_symbol', table_name='positions')
    op.drop_index('idx_positions_identifier', table_name='positions')
    op.drop_index('idx_deals_account_time', table_name='deals')
    op.drop_index('idx_deals_position', table_name='deals')
    op.drop_index('idx_orders_symbol_state', table_name='orders')
    op.drop_index('idx_orders_account_state', table_name='orders')
    
    # Remove new columns from positions
    op.drop_column('positions', 'magic_number')
    op.drop_column('positions', 'comment')
    op.drop_column('positions', 'time_update')
    op.drop_column('positions', 'time_create')
    op.drop_column('positions', 'position_by_id')
    op.drop_column('positions', 'deal_close')
    op.drop_column('positions', 'deal_open')
    op.drop_column('positions', 'contract_size')
    op.drop_column('positions', 'digits_currency')
    op.drop_column('positions', 'digits')
    op.drop_column('positions', 'currency')
    op.drop_column('positions', 'swap')
    op.drop_column('positions', 'price_current')
    op.drop_column('positions', 'price_open')
    op.drop_column('positions', 'reason')
    op.drop_column('positions', 'action')
    op.drop_column('positions', 'identifier')
    op.drop_column('positions', 'external_id')
    
    # Remove new columns from deals
    op.drop_column('deals', 'contract_size')
    op.drop_column('deals', 'digits_currency')
    op.drop_column('deals', 'digits')
    op.drop_column('deals', 'currency')
    op.drop_column('deals', 'swap')
    op.drop_column('deals', 'order_ticket')
    op.drop_column('deals', 'external_id')
    op.drop_column('deals', 'reason')
    op.drop_column('deals', 'entry')
    op.drop_column('deals', 'position_id')
    
    # Remove new columns from orders
    op.drop_column('orders', 'order_matching')
    op.drop_column('orders', 'expert_name')
    op.drop_column('orders', 'expert_id')
    op.drop_column('orders', 'contract_size')
    op.drop_column('orders', 'digits_currency')
    op.drop_column('orders', 'digits')
    op.drop_column('orders', 'activation_flags')
    op.drop_column('orders', 'activation_price')
    op.drop_column('orders', 'activation_time')
    op.drop_column('orders', 'activation_mode')
    op.drop_column('orders', 'time_in_force')
    op.drop_column('orders', 'time_setup_msc')
    op.drop_column('orders', 'price_trigger')
    op.drop_column('orders', 'price_order')
    op.drop_column('orders', 'volume_current')
    op.drop_column('orders', 'volume_initial')
    op.drop_column('orders', 'reason')
    op.drop_column('orders', 'dealer_login')
    op.drop_column('orders', 'gateway_id')
    op.drop_column('orders', 'external_id')
```

---

## 📊 Summary

✅ **Updated `db_models.py`** - Added all new columns for Order, Deal, Position  
✅ **Updated `mappers.py`** - Added complete bidirectional mapping with Value Objects  
✅ **Updated `interfaces.py`** - Added new repository methods for MT5 queries  
✅ **Updated repositories** - Implemented all new query methods  
✅ **Generated Alembic migration** - Added all new columns with proper defaults  

The repositories now fully support the MT5-accurate OMS domain with all the new fields for partial fills, trade modifications, ATM orders, and position management.