-- PostgreSQL Initialization Script
-- Creates initial schema and extensions

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search

-- Create enum types
CREATE TYPE account_type_enum AS ENUM ('real', 'demo', 'preliminary', 'contest', 'coverage', 'manager', 'dealer');
CREATE TYPE order_type_enum AS ENUM ('market', 'limit', 'stop', 'stop_limit');
CREATE_TYPE order_side_enum AS ENUM ('buy', 'sell');
CREATE TYPE deal_type_enum AS ENUM ('buy', 'sell', 'balance_deposit', 'balance_withdrawal', 'commission', 'swap', 'correction');
CREATE TYPE position_side_enum AS ENUM ('buy', 'sell');

-- Groups table (The Rule Engine)
CREATE TABLE IF NOT EXISTS groups (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    type VARCHAR(50) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    leverage_default INTEGER NOT NULL DEFAULT 100,
    leverage_max INTEGER NOT NULL DEFAULT 500,
    margin_call_level DECIMAL(5,4) NOT NULL DEFAULT 0.8000,
    stop_out_level DECIMAL(5,4) NOT NULL DEFAULT 0.5000,
    permissions JSONB NOT NULL DEFAULT '{}',
    commissions JSONB NOT NULL DEFAULT '[]',
    swaps JSONB NOT NULL DEFAULT '{}',
    routing JSONB NOT NULL DEFAULT '{}',
    contest_duration_days INTEGER,
    virtual_balance DECIMAL(20,2),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Accounts table
CREATE TABLE IF NOT EXISTS accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    login INTEGER NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    investor_password_hash VARCHAR(255),
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    full_name VARCHAR(255),
    group_id UUID NOT NULL REFERENCES groups(id),
    account_type account_type_enum NOT NULL DEFAULT 'real',
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    balance DECIMAL(20,2) NOT NULL DEFAULT 0.00,
    equity DECIMAL(20,2) NOT NULL DEFAULT 0.00,
    margin DECIMAL(20,2) NOT NULL DEFAULT 0.00,
    free_margin DECIMAL(20,2) NOT NULL DEFAULT 0.00,
    margin_level DECIMAL(10,4) NOT NULL DEFAULT 0.0000,
    leverage INTEGER NOT NULL DEFAULT 100,
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    is_online BOOLEAN NOT NULL DEFAULT FALSE,
    last_login TIMESTAMP WITH TIME ZONE,
    registration_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    color_tag VARCHAR(50),
    dealer_notes TEXT,
    contest_start TIMESTAMP WITH TIME ZONE,
    contest_end TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_accounts_login ON accounts(login);
CREATE INDEX idx_accounts_group_id ON accounts(group_id);
CREATE INDEX idx_accounts_email ON accounts(email);
CREATE INDEX idx_accounts_type ON accounts(account_type);

-- Symbols table
CREATE TABLE IF NOT EXISTS symbols (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL,
    base_currency VARCHAR(3) NOT NULL,
    quote_currency VARCHAR(3) NOT NULL,
    precision INTEGER NOT NULL DEFAULT 5,
    tick_size DECIMAL(20,10) NOT NULL,
    tick_value DECIMAL(20,10) NOT NULL,
    contract_size DECIMAL(20,10) NOT NULL DEFAULT 100000,
    margin_currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    trading_hours JSONB NOT NULL DEFAULT '{}',
    spreads JSONB NOT NULL DEFAULT '{}',
    margins JSONB NOT NULL DEFAULT '{}',
    swaps JSONB NOT NULL DEFAULT '{}',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_symbols_category ON symbols(category);
CREATE INDEX idx_symbols_active ON symbols(is_active);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id BIGSERIAL NOT NULL UNIQUE,
    account_id UUID NOT NULL REFERENCES accounts(id),
    symbol VARCHAR(50) NOT NULL,
    order_type order_type_enum NOT NULL,
    side order_side_enum NOT NULL,
    volume DECIMAL(20,10) NOT NULL,
    price DECIMAL(20,10),
    stop_loss DECIMAL(20,10),
    take_profit DECIMAL(20,10),
    magic INTEGER,
    comment VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    fill_price DECIMAL(20,10),
    filled_volume DECIMAL(20,10) DEFAULT 0,
    commission DECIMAL(20,2) DEFAULT 0,
    swap DECIMAL(20,2) DEFAULT 0,
    profit DECIMAL(20,2) DEFAULT 0,
    external_order_id VARCHAR(255),
    rejection_reason VARCHAR(255),
    error_code INTEGER,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    filled_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_orders_account_id ON orders(account_id);
CREATE INDEX idx_orders_symbol ON orders(symbol);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_ticket_id ON orders(ticket_id);
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- Deals table
CREATE TABLE IF NOT EXISTS deals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    deal_id BIGSERIAL NOT NULL UNIQUE,
    order_id UUID REFERENCES orders(id),
    account_id UUID NOT NULL REFERENCES accounts(id),
    symbol VARCHAR(50) NOT NULL,
    side order_side_enum NOT NULL,
    volume DECIMAL(20,10) NOT NULL,
    price DECIMAL(20,10) NOT NULL,
    commission DECIMAL(20,2) NOT NULL DEFAULT 0,
    swap DECIMAL(20,2) NOT NULL DEFAULT 0,
    profit DECIMAL(20,2) NOT NULL DEFAULT 0,
    deal_type deal_type_enum NOT NULL,
    original_deal_id UUID,  -- For modifications
    modification_type VARCHAR(50),  -- PRICE, TIME, VOLUME, etc.
    dealer_id UUID,  -- Who made the modification
    modification_reason TEXT,
    audit_log JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_deals_account_id ON deals(account_id);
CREATE INDEX idx_deals_order_id ON deals(order_id);
CREATE INDEX idx_deals_symbol ON deals(symbol);
CREATE INDEX idx_deals_created_at ON deals(created_at);
CREATE INDEX idx_deals_original_deal_id ON deals(original_deal_id);

-- Positions table
CREATE TABLE IF NOT EXISTS positions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    position_id BIGSERIAL NOT NULL UNIQUE,
    account_id UUID NOT NULL REFERENCES accounts(id),
    symbol VARCHAR(50) NOT NULL,
    side position_side_enum NOT NULL,
    volume DECIMAL(20,10) NOT NULL,
    open_price DECIMAL(20,10) NOT NULL,
    current_price DECIMAL(20,10),
    stop_loss DECIMAL(20,10),
    take_profit DECIMAL(20,10),
    unrealized_pnl DECIMAL(20,2) DEFAULT 0,
    realized_pnl DECIMAL(20,2) DEFAULT 0,
    commission_total DECIMAL(20,2) DEFAULT 0,
    swap_total DECIMAL(20,2) DEFAULT 0,
    is_closed BOOLEAN NOT NULL DEFAULT FALSE,
    closed_at TIMESTAMP WITH TIME ZONE,
    close_price DECIMAL(20,10),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_positions_account_id ON positions(account_id);
CREATE INDEX idx_positions_symbol ON positions(symbol);
CREATE INDEX idx_positions_closed ON positions(is_closed);
CREATE INDEX idx_positions_position_id ON positions(position_id);

-- Audit log for trade modifications
CREATE TABLE IF NOT EXISTS trade_modifications_audit (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    deal_id UUID NOT NULL REFERENCES deals(id),
    original_deal_id UUID REFERENCES deals(id),
    reversal_deal_id UUID REFERENCES deals(id),
    correction_deal_id UUID REFERENCES deals(id),
    dealer_id UUID NOT NULL,
    modification_type VARCHAR(50) NOT NULL,
    old_value JSONB NOT NULL,
    new_value JSONB NOT NULL,
    reason TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_trade_modifications_deal_id ON trade_modifications_audit(deal_id);
CREATE INDEX idx_trade_modifications_created_at ON trade_modifications_audit(created_at);

-- Insert default group (will be overridden by seed script)
INSERT INTO groups (name, type, currency, leverage_default, leverage_max, margin_call_level, stop_out_level)
VALUES ('Real-Standard', 'real', 'USD', 100, 500, 0.8, 0.5)
ON CONFLICT (name) DO NOTHING;
