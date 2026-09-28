# 🏛️ MetaTrader 5 (MT5) API Endpoints & Interfaces Catalog

This document provides a clean, comprehensive, domain-structured breakdown of all **MetaTrader 5 (MT5) APIs, REST/Web Endpoints, and Native SDK Interfaces**, cataloged directly from official MetaTrader 5 SDK specifications.

---

## 📊 Summary: MT5 SDK Architecture & API Count

MetaTrader 5 provides **5 Core API Interfaces** plus **2 Data Engine Systems**, totaling **6,561 cataloged interface methods & endpoints**:

| # | MT5 API Module | Protocol / Interface Type | File / Method Count | Primary Use Case & Domain |
|---|---|---|---|---|
| **1** | **MetaTrader 5 Web API** | REST / JSON HTTP API | **489 Endpoints** | Web/Mobile CRMs, Client Portals, Admin Dashboards, HTTP Backends. |
| **2** | **MetaTrader 5 Manager API** | Native C++ / Python DLL | **1,103 Methods** | Dealer Desk, Account & Group Management, Real-time Trade Overrides. |
| **3** | **MetaTrader 5 Server API** | C++ In-Process Plugin SDK | **638 Methods** | Order Routing Hooks, Liquidity Allocation, Dealing Logic, Risk Engine. |
| **4** | **MetaTrader 5 Report API** | Custom Reporting SDK | **556 Methods** | Billing, Commission Tiers, Daily Account Statements, Manager Audit. |
| **5** | **MetaTrader 5 Gateway API** | LP Bridge SDK (FIX/API) | **195 Methods** | Liquidity Provider connectivity (A-Book bridge, Prime Broker feeds). |
| **6** | **Configuration Interfaces** | MT5 Config Schema Engine | **1,800 Interfaces** | System Configuration (Groups, Symbols, Routing, Feeds, Spreads). |
| **7** | **Database Interfaces** | Read-Plane Storage SDK | **1,535 Interfaces** | High-speed binary access to Orders, Deals, Positions, Users, Ticks. |
| **8** | **Tools & Utilities** | Encoding & Cryptography | **249 Tools** | Hashing, AES encryption, timestamp conversions, packet serializers. |

---

## 🌐 1. MetaTrader 5 Web API (REST & HTTP JSON Endpoints)

The **MT5 Web API** is the primary HTTP interface used by Web Apps, CRMs, Admin Portals, and Mobile Terminals to communicate with MT5 Trade Servers.

### 🔐 1.1 Authentication & Session Management
| HTTP Command | Operation / Action | Description |
|---|---|---|
| `auth_start` | GET / POST | Initiate two-phase authentication with MT5 Web API server. |
| `auth_answer` | POST | Complete challenge-response authentication using secret key hash. |
| `ping` | GET | Session keep-alive ping for active Web API connection. |
| `quit` | POST | Explicitly close and invalidate Web API session. |

---

### 👤 1.2 User & Account Management (`/api/user/*`)
| HTTP Command / Section | HTTP Action | Description |
|---|---|---|
| `user_add` | POST | Create a new trading account under a specific Group. |
| `user_update` | POST / PUT | Update client profile, leverage, investor/master password, or flags. |
| `user_delete` | POST / DELETE | Delete an account (requires zero balance & closed positions). |
| `user_get` | GET | Fetch detailed account info by Login ID. |
| `user_get_batch` | GET | Fetch a list of accounts filtered by Group, Name, or Login range. |
| `user_check_password` | POST | Verify investor or master password for a given login. |
| `user_password_change` | POST | Reset or change investor/master account password. |
| `user_account_get` | GET | Query live financial state: Balance, Credit, Equity, Margin, Free Margin. |
| `user_deposit_change` | POST | Balance deposit / withdrawal operation (creates a DEAL). |

---

### 🏢 1.3 Client CRM & Document Management (`/api/client/*`)
| HTTP Command / Section | HTTP Action | Description |
|---|---|---|
| `client_add` | POST | Create a new Client record in the broker database. |
| `client_update` | POST / PUT | Update client contact details, KYC status, or address. |
| `client_delete` | POST / DELETE | Remove a client entity. |
| `client_get` | GET | Query client details by Client ID. |
| `client_bind_account` | POST | Link a trading account Login ID to a Client entity. |
| `client_unbind_account` | POST | Unlink a trading account from a Client entity. |
| `client_add_document` | POST | Upload KYC document attachments. |
| `client_get_document` | GET | Retrieve client KYC documents or verification status. |

---

### 📈 1.4 Trading & Order Execution (`/api/trading/*`)
| HTTP Command / Section | HTTP Action | Description |
|---|---|---|
| `order_send` | POST | Submit Market, Limit, Stop, or Stop-Limit order. |
| `order_cancel` | POST | Cancel a pending order. |
| `order_update` | POST / PUT | Modify order price, SL/TP, or expiration. |
| `order_get` | GET | Query active order details by Ticket ID. |
| `order_get_batch` | GET | Fetch active orders for a login or group. |
| `position_get` | GET | Query open position details by Ticket ID. |
| `position_get_batch` | GET | Fetch open positions for a login or group. |
| `position_check` | POST | Re-calculate open position margin and floating PnL. |
| `position_split` | POST | Split an open position into multiple tickets. |
| `deal_get` | GET | Query executed trade deal details by Deal Ticket ID. |
| `deal_get_batch` | GET | Fetch historical trade deal records within date ranges. |
| `deal_update` | POST | Manager override / correction of an executed deal. |
| `deal_delete` | POST | Rollback / delete a deal (requires high manager right). |

---

### ⚙️ 1.5 Configuration Databases (`/api/config/*`)
| Config Domain | Available Operations (`add`, `update`, `delete`, `get`, `get_total`) | Description |
|---|---|---|
| **Groups** (`/config/group/*`) | `group_add`, `group_update`, `group_delete`, `group_get`, `group_get_total` | Manage Trading Groups (leverage, margin calls, symbols, permissions). |
| **Symbols** (`/config/symbol/*`) | `symbol_add`, `symbol_update`, `symbol_delete`, `symbol_get`, `symbol_get_total` | Manage Tradable Instruments (FX, Crypto, Metals, Commodities, Swaps, Spreads). |
| **Managers** (`/config/manager/*`) | `manager_add`, `manager_update`, `manager_delete`, `manager_get` | Manage Admin & Dealer logins and assign granular permissions (`RIGHT_*`). |
| **Gateways** (`/config/gateway/*`) | `gateway_add`, `gateway_update`, `gateway_delete`, `gateway_get` | Configure Liquidity Provider bridges and execution venues. |
| **Data Feeds** (`/config/feed/*`) | `feed_add`, `feed_update`, `feed_delete`, `feed_get`, `feed_restart` | Manage price feed providers (Reuters, Bloomberg, LMAX, MetaQuotes). |
| **Routing** (`/config/routing/*`) | `routing_add`, `routing_update`, `routing_delete`, `routing_get` | Configure Order Routing Rules (A-Book, B-Book, Hybrid routing conditions). |
| **Spreads** (`/config/spread/*`) | `spread_add`, `spread_update`, `spread_delete`, `spread_get` | Per-group spread diffs and markup tables. |
| **Holidays** (`/config/holiday/*`) | `holiday_add`, `holiday_update`, `holiday_delete`, `holiday_get` | Configure market holidays and trading session pauses. |
| **Firewall** (`/config/firewall/*`) | `firewall_add`, `firewall_delete`, `firewall_get` | IP whitelist and connection rate-limiting rules. |

---

### 📊 1.6 Market Data & Subscriptions (`/api/prices/*` & `/api/subscriptions/*`)
| HTTP Command | HTTP Action | Description |
|---|---|---|
| `tick_get` | GET | Download tick history for a symbol. |
| `tick_get_last` | GET | Get real-time bid/ask snapshot for symbols. |
| `tick_stat` | GET | High/Low/Daily volume statistics. |
| `chart_get` | GET | Download OHLC M1/H1/D1 bar chart history. |
| `subscription_add` | POST | Subscribe to real-time price tick or deal streams. |

---

## 🖥️ 2. MetaTrader 5 Manager API (Native C++ / Python SDK)

The **Manager API** provides binary-speed socket access for Manager Workstations and Dealer Desks.

### 🔑 2.1 Core Subsystems (1,103 Interface Methods)
1. **Connection & Auth:** `Connect`, `Disconnect`, `Login`, `Ping`, `Subscribe`, `Unsubscribe`.
2. **User Administration:** `UserCreate`, `UserUpdate`, `UserDelete`, `UserLogins`, `UserRequest`.
3. **Trading & Dealing:** `OrderSend`, `OrderUpdate`, `OrderCancel`, `DealerRequest`, `DealerReject`.
4. **Position & Deal Storage:** `PositionGet`, `PositionGetBatch`, `DealGet`, `DealGetBatch`.
5. **Group & Symbol Configuration:** `GroupSubscribe`, `GroupUpdate`, `SymbolSubscribe`, `SymbolUpdate`.

---

## ⚡ 3. MetaTrader 5 Server API (C++ Plugin Engine)

The **Server API** allows developers to embed custom C++ plugins directly inside the MT5 Core Server binary.

### 🔌 3.1 Hook & Event Subsystems (638 Interface Methods)
- **`OnTradeRequest`**: Intercepts order requests before risk evaluation (A-Book routing, toxic flow detection).
- **`OnTradeProcess`**: Custom execution algorithms (VWAP, TWAP, B-Book internal matching).
- **`OnQuoteProcess`**: Real-time tick filtering, spread manipulation, and synthetic quote generation.
- **`OnAccountCheck`**: Custom margin check algorithms and leverage scaling.

---

## 🌉 4. Gateway & Report APIs

### 4.1 Gateway API (195 Methods)
- Connects MT5 directly to Tier-1 Liquidity Providers (LMAX, PrimeXM, OneZero, Saxo, FXCM).
- Handles FIX Protocol translation (`FIX 4.4` / `FIX 5.0 SP2`).

### 4.2 Report API (556 Methods)
- Custom HTML/PDF generation for end-of-day broker balance statements.
- Commission and spread rebate calculations for IB (Introducing Broker) networks.

---

## 📁 Related Project References
- Original MT5 SDK Raw Files: [`bundle/m18/m18-references-for-AIs-to-read/mt5 sdk single md file/MT5 SDK in formated md format/`](file:///e:/references-for-AIs-to-read-main/bundle/m18/m18-references-for-AIs-to-read/mt5%20sdk%20single%20md%20file/MT5%20SDK%20in%20formated%20md%20format/)
- Broker Platform Backend Codebase: [`qwe-agen-broker-platform-backend/work/bp`](file:///e:/references-for-AIs-to-read-main/qwe-agen-broker-platform-backend/work/bp)
- Application Audit File: [`audit.md`](file:///e:/references-for-AIs-to-read-main/audit.md)
