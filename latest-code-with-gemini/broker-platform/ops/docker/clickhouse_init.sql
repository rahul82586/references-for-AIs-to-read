-- ClickHouse Initialization Script
-- Creates tables for time-series analytics

-- Ticks table (high-frequency market data)
CREATE TABLE IF NOT EXISTS broker_analytics.ticks
(
    symbol String,
    bid Float64,
    ask Float64,
    last Float64,
    volume Float64,
    timestamp DateTime64(9)  -- Nanosecond precision
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (symbol, timestamp)
TTL timestamp + INTERVAL 365 DAY;

-- Bars/OHLCV table (aggregated)
CREATE TABLE IF NOT EXISTS broker_analytics.bars
(
    symbol String,
    timeframe String,  -- 1m, 5m, 15m, 1h, 4h, 1d
    open Float64,
    high Float64,
    low Float64,
    close Float64,
    volume Float64,
    bar_start DateTime,
    bar_end DateTime
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(bar_start)
ORDER BY (symbol, timeframe, bar_start)
TTL bar_start + INTERVAL 365 DAY;

-- Deals analytics (for reporting and analysis)
CREATE TABLE IF NOT EXISTS broker_analytics.deals_analytics
(
    deal_id UInt64,
    account_id String,
    symbol String,
    side String,
    volume Float64,
    price Float64,
    commission Float64,
    swap Float64,
    profit Float64,
    deal_type String,
    created_at DateTime
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(created_at)
ORDER BY (account_id, created_at);

-- Orders analytics
CREATE TABLE IF NOT EXISTS broker_analytics.orders_analytics
(
    ticket_id UInt64,
    account_id String,
    symbol String,
    order_type String,
    side String,
    volume Float64,
    price Float64,
    fill_price Float64,
    status String,
    created_at DateTime,
    filled_at Nullable(DateTime)
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(created_at)
ORDER BY (account_id, created_at);

-- Account balance history (for equity curves)
CREATE TABLE IF NOT EXISTS broker_analytics.balance_history
(
    account_id String,
    balance Float64,
    equity Float64,
    margin Float64,
    free_margin Float64,
    margin_level Float64,
    unrealized_pnl Float64,
    timestamp DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (account_id, timestamp);

-- Risk events (margin calls, stop outs, etc.)
CREATE TABLE IF NOT EXISTS broker_analytics.risk_events
(
    event_type String,
    account_id String,
    symbol Nullable(String),
    margin_level Nullable(Float64),
    threshold Nullable(Float64),
    equity Nullable(Float64),
    positions_closed Nullable(Array(String)),
    details String,
    created_at DateTime DEFAULT now()
)
ENGINE = MergeTree()
ORDER BY (account_id, created_at);

-- Trade modifications audit (analytics view)
CREATE TABLE IF NOT EXISTS broker_analytics.trade_modifications
(
    deal_id String,
    original_deal_id String,
    account_id String,
    dealer_id String,
    modification_type String,
    old_value String,
    new_value String,
    reason String,
    created_at DateTime
)
ENGINE = MergeTree()
ORDER BY (created_at);

-- News sentiment (from AI agents)
CREATE TABLE IF NOT EXISTS broker_analytics.news_sentiment
(
    news_id String,
    headline String,
    source String,
    sentiment_score Float64,  -- -1.0 to 1.0
    sentiment_label String,   -- positive, negative, neutral
    tickers Array(String),
    published_at DateTime,
    ingested_at DateTime DEFAULT now()
)
ENGINE = MergeTree()
ORDER BY (published_at);

-- Portfolio analytics snapshots
CREATE TABLE IF NOT EXISTS broker_analytics.portfolio_snapshots
(
    account_id String,
    total_equity Float64,
    total_balance Float64,
    total_unrealized_pnl Float64,
    total_realized_pnl Float64,
    var_95 Float64,  -- Value at Risk 95%
    sharpe_ratio Float64,
    max_drawdown Float64,
    exposure_by_symbol Map(String, Float64),
    snapshot_time DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(snapshot_time)
ORDER BY (account_id, snapshot_time);

-- Materialized view for 1-minute bars from ticks
CREATE MATERIALIZED VIEW IF NOT EXISTS broker_analytics.bars_1m
ENGINE = MergeTree()
PARTITION BY toYYYYMM(bar_start)
ORDER BY (symbol, bar_start)
AS SELECT
    symbol,
    '1m' as timeframe,
    argMin(open, timestamp) as open,
    max(high) as high,
    min(low) as low,
    argMax(close, timestamp) as close,
    sum(volume) as volume,
    toStartOfMinute(timestamp) as bar_start,
    toStartOfMinute(timestamp) + INTERVAL 1 MINUTE as bar_end
FROM broker_analytics.ticks
GROUP BY symbol, bar_start;
