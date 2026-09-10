Here are all the links from our conversation, organized by category:

## 🔗 GitHub Repositories (Trading Infrastructure)

| Link | Description |
|------|-------------|
| [joaquinbejar/OptionStratLib](https://github.com/joaquinbejar/OptionStratLib) | Comprehensive Rust library for options trading and strategy development |
| [joaquinbejar/OrderBook-rs](https://github.com/joaquinbejar/OrderBook-rs) | High-performance, thread-safe limit order book implementation in Rust |
| [joaquinbejar/PriceLevel](https://github.com/joaquinbejar/PriceLevel) | Lock-free price level implementation for limit order books |
| [joaquinbejar/market-maker-rs](https://github.com/joaquinbejar/market-maker-rs) | Avellaneda-Stoikov market making strategies in Rust |
| [joaquinbejar/otc-rfq](https://github.com/joaquinbejar/otc-rfq) | OTC Request-for-Quote engine (0x, 1inch, Uniswap, Hashflow, FIX 4.4) |
| [joaquinbejar/tradier](https://github.com/joaquinbejar/tradier) | Rust library for Tradier broker API (REST + WebSocket) |
| [joaquinbejar/hft-clob-core](https://github.com/joaquinbejar/hft-clob-core) | Single-symbol HFT CLOB matching engine (integer-only hot path, no tokio) |
| [joaquinbejar/IronCondor](https://github.com/joaquinbejar/IronCondor) | High-performance options backtester with order-book-level fill simulation |
| [joaquinbejar/financial_types](https://github.com/joaquinbejar/financial_types) | Core financial enums (Side, Action, AssetType, OptionStyle) `#[repr(u8)]` |
| [joaquinbejar/quant-trading-system](https://github.com/joaquinbejar/quant-trading-system) | CLOB + AMM quantitative trading system with arbitrage detection |
| [joaquinbejar/Option-Chain-OrderBook](https://github.com/joaquinbejar/Option-Chain-OrderBook) | Options chain order book implementation |
| [joaquinbejar/OptionChain-Simulator](https://github.com/joaquinbejar/OptionChain-Simulator) | Synthetic option chain simulator |
| [joaquinbejar/ChainView](https://github.com/joaquinbejar/ChainView) | Options chain visualization and replay tool |

## 🔗 Institutional Trading Systems (Open Source)

| Link | Description |
|------|-------------|
| [nautechsystems/nautilus_trader](https://github.com/nautechsystems/nautilus_trader) | Gold standard for deterministic backtest/live parity (Rust/Python) |
| [llc-993/matching-core](https://github.com/llc-993/matching-core) | Sub-microsecond CLOB in Rust (LMAX Disruptor, ART price index, 7.2M TPS) |
| [tfrmma/oms-order-management-system](https://github.com/tfrmma/oms-order-management-system) | C++20 OMS + SOR with lock-free SPSC, zero-heap hot path, two-layer margin |
| [rabbittrix/ultra-low-latency-fx-etrading-platform](https://github.com/rabbittrix/ultra-low-latency-fx-etrading-platform) | Full Rust microservices FX platform (matching, risk, router, liquidity graph) |
| [stackconsult/traderx](https://github.com/stackconsult/traderx) | HFT system with LMAX Disruptor, 8 AI agents, eBPF/XDP kernel bypass |
| [FTHTrading/Broker-Dealer](https://github.com/FTHTrading/Broker-Dealer) | SEC/FINRA compliant broker-dealer (OMS, EMS, SOR, 15c3-1, 15c3-3, CAT/TRACE) |
| [pushkarkumarvats/OmniQuant](https://github.com/pushkarkumarvats/OmniQuant) | Rust OMS (BTreeMap LOB, ITCH 5.0, OUCH 4.2, FPGA risk gate stubs) + Python alpha |
| [mangit955/flux](https://github.com/mangit955/flux) | Perpetual futures exchange backend (TypeScript/Bun, matching, liquidation, ADL) |
| [lustigj-code/fx-option](https://github.com/lustigj-code/fx-option) | FX option platform with pricing orchestration and risk netting |
| [bmarshall511/forexflow](https://github.com/bmarshall511/forexflow) | Self-hosted forex trading platform with OANDA integration and AI analysis |

## 🔗 Chinese Market Resources

| Link | Description |
|------|-------------|
| [luoxz-ai/kungfu](https://github.com/luoxz-ai/kungfu) | 功夫量化 — Chinese quant framework (nanosecond timestamps, 翼春 execution engine, XTP对接) |
| [dromara/northstar](https://github.com/dromara/northstar) | 国内最优秀的基于JAVA的AI开源量化交易平台 (futures/stocks/forex/crypto) |
| [bambuo/TradeX](https://github.com/bambuo/TradeX) | Multi-exchange spot trading system (ASP.NET Core 10 + Vue 3) |
| [奥兴科技 MT5架构](https://aolgtech.com/build-mt5-liquidity-aggregation-routing/) | MT5 broker architecture: multi-LP aggregation, smart routing, dynamic margin |
| [Match-Trade Bridge+RMS](https://match-trade.com/zh-CN/products/bridge-mt4-mt5-with-rms/) | MT4/MT5 Bridge with A/B book routing and risk management |
| [龙穹价差对冲](https://lx.8fish.cn/) | Spread hedging system for MT4/MT5 (real-click/EA/API modes) |
| [trader2B 白标解决方案](https://trader2b.com/zh/pro-services-ch/prop-trading-technology-ch/) | White-label prop firm stack with integrated OMS + risk engine |
| [Northstar 文档](https://github.com/dromara/northstar) | Java quant platform with backtest/live parity and auto-risk |

## 🔗 Russian Market Resources

| Link | Description |
|------|-------------|
| [Track360 Risk Guide (RU)](https://track360.io/ru/blog/foreks-risk-menedzhment-brokera-rukovodstvo-2026) | Comprehensive Russian guide: NOP limits, dynamic hedge triggers, IB traffic profiling |
| [Track360 A/B Book (RU)](https://track360.io/ru/blog/foreks-a-book-b-book-model-brokera-2026) | Russian guide to hybrid execution models and client profiling |
| [B2Broker](https://b2broker.com/ru/products/b2connect/) | Turnkey broker/LP stack with A/B-book routing and real-time exposure dashboards |
| [Soft-FX](https://www.soft-fx.com/ru/solutions/forex-broker-turnkey/) | Internal ECN matching + external LP aggregation, hybrid via trade coefficients |
| [ARQA QUIK OMS](https://arqatech.com/ru/solutions/quik-oms/) | Russian sell-side OMS (pre-trade control, position limits, MiFID II) |
| [ЦБ РФ Standard](https://www.cbr.ru/press/event/?id=18427) | Central Bank of Russia risk management standard for forex dealers |
| [WikiFX B-Book Guide](https://www.wikifx.com/ru/learn/202201059274631863.html) | Russian explanation of B-book risk management |

## 🔗 MT5/Forex Broker Technical Resources

| Link | Description |
|------|-------------|
| [Softices MT5 Manager API Guide](https://softices.com/blogs/mt5-manager-api-prop-firm-backend) | Building prop firm backend on MT5 using Manager API |
| [Brokeret MT5 Margin Call Logic](https://brokeret.com/blog/mt5-margin-call-logic-12-configuration-mistakes-unfair-stop-out-complaints) | 12 MT5 configuration mistakes that cause unfair stop-outs |
| [Algoment MT5 Manager API](https://algoment.com/technology/mt5-manager-api) | MT5 Manager API integration for brokerages |
| [MT5 Manager RESTful API Docs](https://mng5doc.mtapi.io/) | Official MT5 Manager RESTful API documentation |
| [BrokerLauncher MT5 Integration Hub](https://brokerlauncher.com/en/mt5-integration-hub/) | REST API layer for MT5 Manager API |
| [Brokeret FIX vs API vs Plugins Guide](https://brokeret.com/blog/fix-api-vs-mt5-manager-api-vs-plugins-mt5-integration-guide) | Comprehensive MT5 integration methods comparison |
| [IT Corner MT5 Manager API](https://itcorneronline.com/mt5-manager-api) | Hosted MT5 Manager API service |
| [FxTrusts MT5 Manager API](https://fxtrusts.com/resources/blog/mt5-manager-api-explained-what-forex-brokers-can-do-with-full-api-access) | What forex brokers can do with full MT5 Manager API access |
| [FomoCapital MT5 Manager API](https://fomoscapital.com/mt5-manager-api/) | MT5 Manager API solutions for forex brokerages |

## 🔗 Academic/Industry Papers

| Link | Description |
|------|-------------|
| [arxiv.org/pdf/2112.02269](https://arxiv.org/pdf/2112.02269) | "To Hedge or Not to Hedge?" — Optimal control framework for FX market making (internalization vs externalization) |

## 🔗 Commercial/Industry Documentation

| Link | Description |
|------|-------------|
| [EBS FinTech A/B Book Guide](https://www.ebsfintech.com/a-book-b-book-and-hybrid-how-forex-brokers-manage-risk/) | How forex brokers manage risk with A/B book and hybrid models |
| [Babypips Internalization Guide](https://www.babypips.com/learn/forex/internalization-by-forex-brokers) | How forex brokers aggregate orders and hedge residual risk |
| [Track360 A/B Book Risk 2026](https://track360.io/blog/forex-broker-risk-management-a-book-b-book-exposure-2026) | A-book vs B-book exposure management for forex brokers |
| [ForexMechanics Execution Models](https://forexmechanics.com/choosing-broker/execution-models/) | A-book, B-book, and hybrid execution models explained |
| [LiquidityFinder A/B Book Risk](https://liquidityfinder.com/news/a-book-vs-b-book-risk-management-in-cfd-brokerages) | Risk management in CFD brokerages with A/B book |
| [Finance Magnates Hedging Guide](https://www.financemagnates.com/forex/hedging-is-crucial-for-cfd-brokers-but-when-should-one-avoid-it/) | When CFD brokers should avoid hedging |
| [Brokeree A-Book Guide (RU)](https://brokeree.com/zh/articles/a-book-how-forex-brokers-mitigate-risks/) | How A-book brokers mitigate risks |
| [QuantConnect LEAN (CN)](https://dev.to/henry_lin_3ac6363747f45b4/gong-ye-ji-liang-hua-kai-yuan-ruan-jian-quantconnectlean-gong-neng-jie-shao-an8) | Industrial-grade quant platform LEAN introduction (Chinese) |
| [奥兴科技 OMS/RMS](https://aolgtech.com/build-equities-oms-rms-routing/) | Stock trading platform construction: OMS/RMS, smart routing, clearing |
| [Interactive Brokers OMS (RU)](https://www.interactivebrokers.co.uk/ru/software/pdfhighlights/PDF-oms.php) | IBKR OMS for order management and execution control |

## 🔗 Crates/Docs (Recovered from Deleted Repo)

| Link | Description |
|------|-------------|
| [trading_core on crates.io](https://crates.io/crates/trading_core) | Deleted crate by joaquinbejar (v0.0.2-alpha) — Polars DataFrame utilities for trading |
| [trading_core docs.rs](https://docs.rs/trading_core/0.0.2-alpha/trading_core/) | Documentation for deleted trading_core crate |
| [trading_core source (candles.rs)](https://docs.rs/crate/trading_core/0.0.2-alpha/source/src/candles.rs) | Candle struct and AsDataFrame trait implementation |
| [trading_core source (utils.rs)](https://docs.rs/crate/trading_core/0.0.2-alpha/source/src/utils.rs) | extract_new_rows, extract_candles_from_df, extract_signals_from_df functions |
| [trading_core full source](https://docs.rs/crate/trading_core/0.0.2-alpha/source/) | Complete source code archive (535 lines) |

## 🔗 MT5 Risk Management EAs (GitHub)

| Link | Description |
|------|-------------|
| [dbgucci1017/MT5-Equity-Guardian](https://github.com/dbgucci1017/MT5-Equity-Guardian-Trailing-Pro) | Advanced risk manager EA with breakeven, trailing stop, partial close |
| [SHASHWATSAMARTH/nyao-mt5-advanced-toolkit](https://github.com/SHASHWATSAMARTH/nyao-mt5-advanced-toolkit) | Multi-broker arbitrage and risk management system |
| [Swift-Tech-Co/mt5-risk-engine-demo](https://github.com/Swift-Tech-Co/mt5-risk-engine-demo) | MetaTrader 5 risk engine demo (position sizing, drawdown limits) |
| [Syed-Imran88/MT5-Exposure-Mesh-Analyzer](https://github.com/Syed-Imran88/MT5-Exposure-Mesh-Analyzer) | Multi-asset correlation heatmap and portfolio risk matrix |
| [zrakd/MT5-Risk-Management-EA](https://github.com/zrakd/mt5-risk-management-ea) | MQL5 risk management EA (breakeven, trailing stop, equity protection) |
| [Valtorim/MT5-PropFirm-Drawdown-Guard](https://github.com/Valtorim/MT5-PropFirm-Drawdown-Guard) | Prop firm drawdown protection with kill-switch |
| [ro31337/RomanPushkin-RiskManager-RU](https://github.com/ro31337/RomanPushkin-RiskManager-RU) | Russian risk manager for MetaTrader 5 (auto stop-loss) |
| [Kaltorim/MT5-PropFirm-Drawdown-Guard](https://github.com/Kaltorim/MT5-PropFirm-Drawdown-Guard) | Equity guard and drawdown protector for prop firms |
| [Jotanune/PropGuardian](https://github.com/Jotanune/PropGuardian) | Automated forex trading bot for prop firm challenges (SMC, risk management) |
| [Quorvathz/Prop-Matrix-Engine](https://github.com/Quorvathz/Prop-Matrix-Engine) | Multi-account MT5 risk command center with global drawdown guard |

## 🔗 Other Trading Platforms

| Link | Description |
|------|-------------|
| [ShawFenng/OpenAlice](https://github.com/ShawFenng/OpenAlice) | Unified Trading Account (UTA) system with multi-broker support (IBKR, Alpaca, CCXT) |
| [ZagTrader OMS/EMS](https://www.zagtrader.com/platform/trading-execution) | Multi-asset OMS/EMS with A-book/B-book/RFQ execution |
| [TraderEvolution Risk Management](https://traderevolution.com/platform/risk-management/) | Server-side risk management with 16 margin calculation types |
| [Exness Trading Engine](https://mintlify.wiki/lakshay-goyal/Exness/services/engine) | Core trading engine with Redis Streams and parallel processing |
| [BULK Risk Engine](https://docs.bulk.trade/architecture/risk-engine) | Real-time risk engine with lambda surfaces and portfolio margin |
| [Hafzan Quant Labs Risk Toolkit](https://github.com/Hafzan-Quant-Labs/risk-toolkit) | Interactive quant toolkit for FX A/B-book risk modeling |

---

*All links extracted from conversation on September 8, 2026*