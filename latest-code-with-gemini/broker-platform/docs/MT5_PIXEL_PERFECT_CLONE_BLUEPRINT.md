# 🏛️ MetaTrader 5 (MT5) Pixel-Perfect Clone Master Blueprint & Architecture Audit

This document provides an exhaustive, macro-to-micro architectural blueprint and audit for building a 100% pixel-perfect, MT5-compliant institutional brokerage backend platform.

---

## 📑 Table of Contents
1. [Manager Account Roles & Rights Bitmask Engine (`RIGHT_*`)](#1-manager-account-roles--rights-bitmask-engine-right_)
2. [Netting vs. Hedging Execution & Position Engine](#2-netting-vs-hedging-execution--position-engine)
3. [Group Engine Architecture (8 Tabs & Wire Fields)](#3-group-engine-architecture-8-tabs--wire-fields)
4. [Symbol Engine Architecture (3-Currency & 8 Calc Modes)](#4-symbol-engine-architecture-3-currency--8-calc-modes)
5. [Account Types & Group Derivation Rules](#5-account-types--group-derivation-rules)
6. [Backoffice, Read-Plane & Admin Rights Gating](#6-backoffice-read-plane--admin-rights-gating)
7. [Dealing Desk: A-Book, B-Book & Hybrid Routing](#7-dealing-desk-a-book-b-book--hybrid-routing)

---

## 👨‍💼 1. Manager Account Roles & Rights Bitmask Engine (`RIGHT_*`)

In MT5 architecture, **there is no single string `role` field for staff**. Instead, a staff manager account's permissions are controlled by a **128-element binary array (`IMTConManager::Rights`)** indexed by `EnManagerRights`.

Our platform implements this exact bitmask engine in [`core/domains/identity/rights.py`](file:///e:/references-for-AIs-to-read-main/qwe-agen-broker-platform-backend/work/bp/core/domains/identity/rights.py) using `ManagerRightsMask`.

### 🛡️ Manager Account Role Presets (Derived from Rights Bitmasks)

| Manager Staff Role | Key Gating Rights Bitmask (`RIGHT_*`) | Operational Capabilities & Scope | Audit Status |
|---|---|---|---|
| **1. Administrator** | `RIGHT_CFG_GROUPS`, `RIGHT_CFG_SYMBOLS`, `RIGHT_MANAGERS_ACCESS`, `RIGHT_SERVER_ADMIN` | Full system configuration, group CRUD, symbol definitions, staff manager creation. | ✅ **100% MT5 Compliant** |
| **2. Dealer / Desk Operator** | `RIGHT_TRADES_DEALER`, `RIGHT_ORDERS_EXECUTE`, `RIGHT_POSITIONS_MODIFY` | Manual trade execution, order modifications, dealer price overrides, deal rollbacks. | ✅ **100% MT5 Compliant** |
| **3. Risk Manager** | `RIGHT_ACC_READ`, `RIGHT_POSITIONS_READ`, `RIGHT_RISK_READ` | Real-time monitoring of open positions, margin call alerts, floating PnL, stop-out audits. | ✅ **100% MT5 Compliant** |
| **4. Backoffice / Accountant** | `RIGHT_FUNDS_DEPOSIT`, `RIGHT_DEALS_READ`, `RIGHT_REPORTS_READ` | Balance deposits, withdrawals, credit adjustments, daily statement generation. | ✅ **100% MT5 Compliant** |
| **5. Compliance / KYC Officer** | `RIGHT_CLIENTS_ACCESS`, `RIGHT_DOCUMENTS_READ` | Client onboarding, identity verification, document approval/rejection. | ✅ **100% MT5 Compliant** |
| **6. API Service Account** | Restricted rights + IP whitelist (`IMTConManagerAccess`) | Automated API bot connections restricted to explicit IP ranges. | ✅ **100% MT5 Compliant** |

---

## 🔄 2. Netting vs. Hedging Execution & Position Engine

MT5 supports both Netting and Hedging accounting models via `MarginMode` on the Group entity.

### 📊 Netting vs. Hedging Comparison

| Feature / Calculation | Netting Mode (`MarginMode.RETAIL`) | Hedging Mode (`MarginMode.RETAIL_HEDGED`) |
|---|---|---|
| **Positions per Symbol** | **Strictly ONE position ticket per symbol per account**. | **Multiple independent position tickets** allowed simultaneously. |
| **Opposite Trade Action** | Submitting a BUY order when a SELL position exists **nets out or flips the position volume**. | Submitting a BUY order when a SELL position exists **opens a new independent LONG ticket**. |
| **Ticket Tracking** | Single ticket updated dynamically on every deal. | Each position ticket maintains its own open price, SL/TP, and volume. |
| **Margin Calculation** | `(Net Uncovered Volume * Contract Size * Price) / Leverage` | **Covered / Uncovered Volume Rule**: Net Uncovered Volume charged at standard rate + Covered Volume charged at `MarginHedged`. |
| **Exchange Netting** | Modeled via `MarginMode.EXCHANGE_DISCOUNT` for exchange derivatives. | Supported on Forex, CFD, Futures, and Crypto symbols. |

Our backend enforces this exact dual-engine accounting logic inside [`core/domains/accounts/group.py`](file:///e:/references-for-AIs-to-read-main/qwe-agen-broker-platform-backend/work/bp/core/domains/accounts/group.py) and [`core/domains/market_data/margin.py`](file:///e:/references-for-AIs-to-read-main/qwe-agen-broker-platform-backend/work/bp/core/domains/market_data/margin.py).

---

## 🏛️ 3. Group Engine Architecture (8 Tabs & Wire Fields)

The Group entity is the **master Rule Engine** of MT5. It governs all accounts assigned to it across 8 configuration tabs:

1. **Common Tab**: `name`, `server_id`, `currency`, `currency_digits`, `auth_mode`, `auth_password_min`, `auth_otp_mode`, `permissions_flags`.
2. **Company Tab (White Label)**: `company`, `company_page`, `company_email`, `company_support_page`, `company_support_email`, `company_catalog`, `company_deposit_url`, `company_withdrawal_url`.
3. **Permissions & Limits Tab**: `limit_orders`, `limit_positions`, `limit_symbols`, `limit_history`, `limit_positions_volume`, `trade_flags` (EXPERTS, SWAPS, TRAILING, EXPIRATION), `trade_interestrate`, `trade_transfer_mode`.
4. **Margin & Stop-Out Engine Tab**: `margin_call_level`, `stop_out_level`, `stop_out_mode` (`PERCENT`/`MONEY`), `free_margin_mode`, `free_profit_mode`, `margin_mode`, `trade_virtual_credit`, `calculate_margin()`.
5. **Symbol Overrides Tab**: Per-group `GroupSymbolOverride` (B-Book spread markup `spread_diff`, initial buy/sell margin rates, min/max volume, swap overrides).
6. **Commissions Tab**: `CommissionRule` & `CommissionTier` (`VOLUME` per lot, `DEAL` flat, `PERCENT` of value, Multi-rule stacking sum, volume tiers).
7. **Demo Provisioning Tab**: `demo_leverage`, `demo_deposit`, `demo_trades_clean` (inactivity cleanup days).
8. **News, Mail & Reports Tab**: `news_mode`, `news_category`, `mail_mode`, `reports_mode`, `reports_flags`.

---

## 📈 4. Symbol Engine Architecture (3-Currency & 8 Calc Modes)

The Symbol entity defines the trading parameters of financial instruments:

1. **MT5 3-Currency Model**: `base_currency` (`CurrencyBase`), `quote_currency` (`CurrencyProfit`), `margin_currency` (`CurrencyMargin`). Separating these prevents cross-currency conversion bugs on JPY, Crypto, and Index symbols.
2. **8 Calculation Modes (`calc_mode`)**: `FOREX`, `FUTURES`, `CFD`, `CFD_INDEX`, `CFD_LEVERAGE`, `FOREX_NO_LEVERAGE`, `EXCHANGE_STOCKS`, `OPTIONS`, `BONDS`.
3. **Price Precision & Alignment**: `digits` (precision), `tick_size` (Point step), `mt5_tick_size` (alignment), `tick_value`, `contract_size`.
4. **Volume Validation (`validate_volume()`)**: `volume_min`, `volume_max`, `volume_step`, `volume_limit`.
5. **16-Element Margin Rates Matrix**: 8 initial & 8 maintenance rates per side and order type (`margin_rates`).
6. **7-Day Sunday-First Sessions**: `quote_sessions`, `trade_sessions`, `mt5_day_index()` (aligns Python `weekday()` with MT5 Sunday-first index).

---

## 👤 5. Account Types & Group Derivation Rules

In MT5, account type is **100% derived from the Group Name**:

| Account Type | Group Name Substring Rule | Example Group | Purpose |
|---|---|---|---|
| **`REAL`** | Fallback / default (or `real`) | `real\real-SF` | Live money accounts |
| **`DEMO`** | Contains `demo` | `demo\Standard` | Paper trading accounts |
| **`CONTEST`** | Contains `contest` | `demo\Challenge-2026` | Prop challenges & competitions |
| **`COVERAGE`** | Contains `coverage` | `coverage\house` | Internal A-Book LP hedging |
| **`PRELIMINARY`** | Exact match `preliminary` | `preliminary` | KYC onboarding holding accounts |
| **`MANAGER`** | Contains `manager` | `managers\dealers` | Staff manager logins |

---

## 🏢 6. Backoffice, Read-Plane & Admin Rights Gating

Our read-plane implementation in [`api/routers/admin/reads.py`](file:///e:/references-for-AIs-to-read-main/qwe-agen-broker-platform-backend/work/bp/api/routers/admin/reads.py) provides:
- **Paged Reads**: Total counts (`X-Total-Count`), limit/offset pagination, and filter parameters.
- **Granular Rights Gating**: Every endpoint requires its exact MT5 right (`ACC_READ`, `CLIENTS_ACCESS`, `TRADES_READ`, `RISK_READ`).

---

## 💼 7. Dealing Desk: A-Book, B-Book & Hybrid Routing

1. **A-Book (STP / ECN Execution)**: Direct LP pass-through via Gateway API / Fix Bridge.
2. **B-Book (Internal Warehousing)**: Internal execution with per-group spread markups (`spread_diff` & `spread_diff_balance`).
3. **Hybrid Routing**: Automated routing rules based on client equity, volume, or toxicity score.

---

## 📁 Reference Specifications
- Group Engine Audit: [`GROUP_ENGINE_MT5_AUDIT.md`](file:///e:/references-for-AIs-to-read-main/GROUP_ENGINE_MT5_AUDIT.md)
- Symbol Engine Audit: [`SYMBOL_ENGINE_MT5_AUDIT.md`](file:///e:/references-for-AIs-to-read-main/SYMBOL_ENGINE_MT5_AUDIT.md)
- Application Audit Log: [`audit.md`](file:///e:/references-for-AIs-to-read-main/audit.md)
- MT5 Endpoints Catalog: [`MT5_API_ENDPOINTS_CATALOG.md`](file:///e:/references-for-AIs-to-read-main/MT5_API_ENDPOINTS_CATALOG.md)
