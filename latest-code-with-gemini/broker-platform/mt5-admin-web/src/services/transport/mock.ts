/**
 * MockTransport — a fixture-driven, in-memory AdminApi implementation.
 *
 * Purpose:
 *  1. Develop and demo every screen with zero backend running (default mode).
 *  2. Act as the executable spec of the *ideal* admin API. Whatever the live
 *     transport throws BackendGapError for, but this transport serves, is the
 *     current gap list for the backend session.
 *
 * Shapes mirror what the ported pages consume (numbers for money, MT5-style
 * group names with backslashes, settings_json blobs for the group modal).
 */
import type { AdminApi, Ticks, PlaceOrderPayload } from '../api/contract';

const delay = (ms = 120) => new Promise((r) => setTimeout(r, ms));

/* ------------------------------------------------------------------ */
/* fixtures                                                            */
/* ------------------------------------------------------------------ */

const groupSettings = (over: Record<string, unknown> = {}) =>
    JSON.stringify({
        currency: 'USD',
        digits: 2,
        max_leverage: 100,
        default_leverage: 100,
        spread_override: 0,
        margin_call: 60,
        margin_stop_out: 30,
        trade_server: 'BrokerPlatform-Demo',
        company: 'Acme Brokerage Ltd',
        company_website: 'https://example.com',
        company_email: 'support@example.com',
        enable_connections: true,
        trade_allowed: true,
        allow_hedging: true,
        ...over,
    });

let groups = [
    { id: 1, name: 'demo\\demo', account_type: 'DEMO', currency: 'USD', settings_json: groupSettings({ currency: 'USD' }) },
    { id: 2, name: 'demo\\demo-pro', account_type: 'DEMO', currency: 'USD', settings_json: groupSettings({ max_leverage: 200 }) },
    { id: 3, name: 'real\\real', account_type: 'REAL', currency: 'USD', settings_json: groupSettings({ spread_override: 0 }) },
    { id: 4, name: 'real\\real-A', account_type: 'REAL', currency: 'USD', settings_json: groupSettings({ spread_override: 2 }) },
    { id: 5, name: 'real\\IB', account_type: 'REAL', currency: 'USD', settings_json: groupSettings({ spread_override: 5 }) },
    { id: 6, name: 'contest\\contest1', account_type: 'CONTEST', currency: 'USD', settings_json: groupSettings({ default_leverage: 500 }) },
    { id: 7, name: 'coverage\\coverage', account_type: 'COVERAGE', currency: 'USD', settings_json: groupSettings() },
    { id: 8, name: 'preliminary\\prelim', account_type: 'PRELIMINARY', currency: 'USD', settings_json: groupSettings() },
];

let accounts = [
    { login: 50001, name: 'Alice Sharma', group: 'demo\\demo', currency: 'USD', balance: 10000, credit: 0, equity: 10043.21, profit: 43.21, margin: 214.5, margin_free: 9828.71, margin_level: 4682, leverage: 100, is_enabled: true, account_type: 'DEMO', so_activation: 'PERCENT', email: 'alice@example.com', phone: '+91 98000 00001' },
    { login: 50002, name: 'Bob Verhoeven', group: 'real\\real', currency: 'USD', balance: 25000, credit: 0, equity: 24780.55, profit: -219.45, margin: 1893.2, margin_free: 22887.35, margin_level: 1309, leverage: 100, is_enabled: true, account_type: 'REAL', so_activation: 'PERCENT', email: 'bob@example.com', phone: '+31 600 000002' },
    { login: 50003, name: 'Chen Wei', group: 'real\\real-A', currency: 'USD', balance: 8200, credit: 0, equity: 8244.9, profit: 44.9, margin: 96.4, margin_free: 8148.5, margin_level: 8552, leverage: 200, is_enabled: true, account_type: 'REAL', so_activation: 'PERCENT', email: 'chen@example.com', phone: '+86 138 0000 0003' },
    { login: 50004, name: 'Dana Ivanova', group: 'real\\IB', currency: 'EUR', balance: 15300, credit: 0, equity: 15233.1, profit: -66.9, margin: 2210.0, margin_free: 13023.1, margin_level: 689, leverage: 50, is_enabled: true, account_type: 'REAL', so_activation: 'PERCENT', email: 'dana@example.com', phone: '+359 88 000 0004' },
    { login: 50005, name: 'Erik Lindqvist', group: 'demo\\demo-pro', currency: 'USD', balance: 1000, credit: 0, equity: 177.4, profit: -822.6, margin: 431.9, margin_free: -254.5, margin_level: 41, leverage: 100, is_enabled: false, account_type: 'DEMO', so_activation: 'PERCENT', email: 'erik@example.com', phone: '+46 70 000 0005' },
];

let symbols = [
    { name: 'EURUSD', path: 'Forex\\Major', description: 'Euro vs US Dollar', base_currency: 'EUR', quote_currency: 'USD', digits: 5, spread: 12, contract_size: 100000, volume_min: 0.01, volume_max: 200, volume_step: 0.01, trade_mode: 'FULL', exec_mode: 'MARKET', is_trade_allowed: true },
    { name: 'GBPUSD', path: 'Forex\\Major', description: 'Great Britain Pound vs US Dollar', base_currency: 'GBP', quote_currency: 'USD', digits: 5, spread: 15, contract_size: 100000, volume_min: 0.01, volume_max: 200, volume_step: 0.01, trade_mode: 'FULL', exec_mode: 'MARKET', is_trade_allowed: true },
    { name: 'USDJPY', path: 'Forex\\Major', description: 'US Dollar vs Japanese Yen', base_currency: 'USD', quote_currency: 'JPY', digits: 3, spread: 11, contract_size: 100000, volume_min: 0.01, volume_max: 200, volume_step: 0.01, trade_mode: 'FULL', exec_mode: 'MARKET', is_trade_allowed: true },
    { name: 'USDCHF', path: 'Forex\\Major', description: 'US Dollar vs Swiss Franc', base_currency: 'USD', quote_currency: 'CHF', digits: 5, spread: 16, contract_size: 100000, volume_min: 0.01, volume_max: 200, volume_step: 0.01, trade_mode: 'FULL', exec_mode: 'MARKET', is_trade_allowed: true },
    { name: 'AUDUSD', path: 'Forex\\Major', description: 'Australian Dollar vs US Dollar', base_currency: 'AUD', quote_currency: 'USD', digits: 5, spread: 14, contract_size: 100000, volume_min: 0.01, volume_max: 200, volume_step: 0.01, trade_mode: 'FULL', exec_mode: 'MARKET', is_trade_allowed: true },
    { name: 'XAUUSD', path: 'Metals', description: 'Gold vs US Dollar', base_currency: 'XAU', quote_currency: 'USD', digits: 2, spread: 25, contract_size: 100, volume_min: 0.01, volume_max: 50, volume_step: 0.01, trade_mode: 'FULL', exec_mode: 'MARKET', is_trade_allowed: true },
    { name: 'XAGUSD', path: 'Metals', description: 'Silver vs US Dollar', base_currency: 'XAG', quote_currency: 'USD', digits: 3, spread: 22, contract_size: 5000, volume_min: 0.01, volume_max: 100, volume_step: 0.01, trade_mode: 'FULL', exec_mode: 'MARKET', is_trade_allowed: true },
    { name: 'US500', path: 'Indices', description: 'S&P 500 Index', base_currency: 'USD', quote_currency: 'USD', digits: 2, spread: 40, contract_size: 1, volume_min: 0.1, volume_max: 500, volume_step: 0.1, trade_mode: 'FULL', exec_mode: 'MARKET', is_trade_allowed: true },
    { name: 'ESU5', path: 'Futures\\Exchange', description: 'E-mini S&P 500 Futures', base_currency: 'USD', quote_currency: 'USD', digits: 2, spread: 25, contract_size: 50, volume_min: 1, volume_max: 1000, volume_step: 1, trade_mode: 'FULL', exec_mode: 'EXCHANGE', is_trade_allowed: true },
];

let orders: any[] = [
    { ticket: 459000601, login: 50002, symbol: 'EURUSD', type: 3, volume: 0.5, volume_current: 0.5, price_order: 1.092, price_sl: 1.079, price_tp: 1.105, state: 0, reason: 'Client', time_setup: isoMinutesAgo(42) },
    { ticket: 459000602, login: 50003, symbol: 'XAUUSD', type: 4, volume: 0.1, volume_current: 0.1, price_order: 2466.100, price_sl: 0, price_tp: 2540, state: 0, reason: 'Client', time_setup: isoMinutesAgo(15) },
    { ticket: 459000603, login: 50004, symbol: 'USDJPY', type: 2, volume: 1.0, volume_current: 1.0, price_order: 155.016, price_sl: 156.2, price_tp: 0, state: 0, reason: 'Expert', time_setup: isoMinutesAgo(4) },
    { ticket: 459000604, login: 50001, symbol: 'GBPUSD', type: 5, volume: 0.2, volume_current: 0.2, price_order: 1.3005, price_sl: 0, price_tp: 0, state: 0, reason: 'Client', time_setup: isoMinutesAgo(120) },
    { ticket: 459000605, login: 50002, symbol: 'EURUSD', type: 0, volume: 25, volume_current: 25, price_order: 0, price_sl: 0, price_tp: 0, state: 6, reason: 'Client', time_setup: isoMinutesAgo(9) },
    { ticket: 459000606, login: 50004, symbol: 'XAUUSD', type: 1, volume: 5, volume_current: 5, price_order: 0, price_sl: 0, price_tp: 0, state: 6, reason: 'Expert', time_setup: isoMinutesAgo(4) },
];

const orderHistory: any[] = [
    { ticket: 459000437, login: 50002, symbol: 'EURUSD', type: 1, volume: 0.01, volume_current: 0.01, price_order: 0, price_sl: 0, price_tp: 0, time_setup: isoMinutesAgo(3000), time_done: isoMinutesAgo(2999), price_done: 1.08459, reason: 'Client', state: 'filled' },
    { ticket: 459000438, login: 50002, symbol: 'EURUSD', type: 0, volume: 0.01, volume_current: 0.01, price_order: 0, price_sl: 0, price_tp: 0, time_setup: isoMinutesAgo(2900), time_done: isoMinutesAgo(2899), price_done: 1.08461, reason: 'Client', state: 'filled' },
    { ticket: 459000440, login: 50002, symbol: 'EURUSD', type: 1, volume: 0.01, volume_current: 0.01, price_order: 0, price_sl: 0, price_tp: 0, time_setup: isoMinutesAgo(2800), time_done: isoMinutesAgo(2799), price_done: 1.08463, reason: 'Client', state: 'filled' },
    { ticket: 459000443, login: 50002, symbol: 'EURUSD', type: 0, volume: 0.01, volume_current: 0.01, price_order: 0, price_sl: 0, price_tp: 0, time_setup: isoMinutesAgo(2700), time_done: isoMinutesAgo(2699), price_done: 1.08465, reason: 'Dealer', state: 'filled' },
    { ticket: 459000445, login: 50002, symbol: 'XAUUSD', type: 0, volume: 0.01, volume_current: 0.01, price_order: 2472.590, price_sl: 0, price_tp: 0, time_setup: isoMinutesAgo(2600), time_done: isoMinutesAgo(2599), price_done: 2472.590, reason: 'Dealer', state: 'filled' },
    { ticket: 459000446, login: 50002, symbol: 'XAUUSD', type: 1, volume: 0.01, volume_current: 0.01, price_order: 2466.100, price_sl: 0, price_tp: 0, time_setup: isoMinutesAgo(2500), time_done: isoMinutesAgo(2499), price_done: 2466.100, reason: 'Dealer', state: 'filled' },
    { ticket: 459000449, login: 50002, symbol: 'EURUSD', type: 1, volume: 0.01, volume_current: 0.01, price_order: 0, price_sl: 0, price_tp: 0, time_setup: isoMinutesAgo(2400), time_done: isoMinutesAgo(2399), price_done: 1.08468, reason: 'Client', state: 'filled' },
    { ticket: 459000450, login: 50002, symbol: 'EURUSD', type: 0, volume: 0.01, volume_current: 0.01, price_order: 0, price_sl: 0, price_tp: 0, time_setup: isoMinutesAgo(2300), time_done: isoMinutesAgo(2299), price_done: 1.08470, reason: 'Client', state: 'filled' },
    { ticket: 459000452, login: 50001, symbol: 'AUDUSD', type: 1, volume: 0.01, volume_current: 0.01, price_order: 0.62586, price_sl: 0, price_tp: 0, time_setup: isoMinutesAgo(2200), time_done: isoMinutesAgo(2199), price_done: 0.62586, reason: 'Dealer', state: 'filled' },
    { ticket: 459000453, login: 50002, symbol: 'EURUSD', type: 1, volume: 0.01, volume_current: 0.01, price_order: 2469.340, price_sl: 0, price_tp: 0, time_setup: isoMinutesAgo(2100), time_done: isoMinutesAgo(2099), price_done: 2469.340, reason: 'Dealer', state: 'filled' },
    { ticket: 459000454, login: 50002, symbol: 'EURUSD', type: 5, volume: 0.01, volume_current: 0.01, price_order: 2475.361, price_sl: 0, price_tp: 0, time_setup: isoMinutesAgo(2000), time_done: isoMinutesAgo(1999), price_done: 2475.361, reason: 'Dealer', state: 'canceled' },
    { ticket: 459000455, login: 50004, symbol: 'USDJPY', type: 0, volume: 2.0, volume_current: 2.0, price_order: 0, price_sl: 157.6, price_tp: 155.0, time_setup: isoMinutesAgo(90), time_done: isoMinutesAgo(89), price_done: 156.42, reason: 'Client', state: 'filled' },
    { ticket: 459000456, login: 50003, symbol: 'XAUUSD', type: 0, volume: 0.2, volume_current: 0.2, price_order: 0, price_sl: 0, price_tp: 0, time_setup: isoMinutesAgo(320), time_done: isoMinutesAgo(319), price_done: 2481.4, reason: 'Client', state: 'filled' },
    { ticket: 459000457, login: 50005, symbol: 'EURUSD', type: 2, volume: 0.1, volume_current: 0.1, price_order: 1.0780, price_sl: 0, price_tp: 0, time_setup: isoMinutesAgo(600), time_done: isoMinutesAgo(590), price_done: 0, reason: 'Client', state: 'rejected' },
];

let positions = [
    { position_id: 700001, login: 50002, symbol: 'EURUSD', type: 0, volume: 1.5, price_open: 1.0812, price_current: 1.0846, sl: 1.076, tp: 1.095, profit: 510.0, swap: -3.2, commission: -4.5, margin: 1626.3, open_time: isoMinutesAgo(1440), update_time: isoMinutesAgo(120), reason: 'Client', comment: '' },
    { position_id: 700002, login: 50001, symbol: 'XAUUSD', type: 0, volume: 0.2, price_open: 2481.4, price_current: 2496.1, sl: 0, tp: 0, profit: 294.0, swap: -1.1, commission: 0, margin: 497.2, open_time: isoMinutesAgo(320), update_time: isoMinutesAgo(320), reason: 'Client', comment: 'gold swing' },
    { position_id: 700003, login: 50004, symbol: 'USDJPY', type: 1, volume: 2.0, price_open: 156.8, price_current: 156.42, sl: 157.6, tp: 155.0, profit: 485.0, swap: 6.4, commission: -6.0, margin: 1250.0, open_time: isoMinutesAgo(90), update_time: isoMinutesAgo(89), reason: 'Client', comment: '' },
    { position_id: 700004, login: 50002, symbol: 'EURUSD', type: 1, volume: 0.5, price_open: 1.0866, price_current: 1.0846, sl: 0, tp: 0, profit: 100.0, swap: -0.8, commission: -1.75, margin: 542.3, open_time: isoMinutesAgo(2880), update_time: isoMinutesAgo(1440), reason: 'Rollover', comment: 'swap rollover' },
    { position_id: 700005, login: 50003, symbol: 'GBPUSD', type: 0, volume: 0.3, price_open: 1.3022, price_current: 1.3132, sl: 1.295, tp: 1.33, profit: 330.0, swap: 0, commission: -0.9, margin: 393.9, open_time: isoMinutesAgo(120), update_time: isoMinutesAgo(119), reason: 'Expert', comment: 'ea: breakout' },
    { position_id: 700006, login: 50005, symbol: 'AUDUSD', type: 1, volume: 0.1, price_open: 0.6660, price_current: 0.6642, sl: 0, tp: 0, profit: 18.0, swap: 0, commission: 0, margin: 66.6, open_time: isoMinutesAgo(45), update_time: isoMinutesAgo(45), reason: 'Client', comment: '' },
];

const deals: any[] = [
    { deal_id: 900001, login: 50002, order: 459000400, position: 700001, symbol: 'EURUSD', action: 'in', type: 'buy', volume: 1.5, price: 1.0812, profit: 0, swap: 0, commission: -4.5, time: isoMinutesAgo(1440), comment: '' },
    { deal_id: 900002, login: 50001, order: 459000410, position: 700002, symbol: 'XAUUSD', action: 'in', type: 'buy', volume: 0.2, price: 2481.4, profit: 0, swap: 0, commission: 0, time: isoMinutesAgo(320), comment: '' },
    { deal_id: 900003, login: 50003, order: 459000456, position: 700005, symbol: 'GBPUSD', action: 'in', type: 'buy', volume: 0.3, price: 1.3022, profit: 0, swap: 0, commission: -0.9, time: isoMinutesAgo(120), comment: 'ea: breakout' },
    { deal_id: 900004, login: 50004, order: 459000455, position: 700003, symbol: 'USDJPY', action: 'in', type: 'sell', volume: 2.0, price: 156.42, profit: 0, swap: 0, commission: -6.0, time: isoMinutesAgo(89), comment: '' },
    { deal_id: 900005, login: 50002, order: 0, position: 700001, symbol: 'EURUSD', action: 'in', type: 'daily commission', volume: 0, price: 0, profit: 0, swap: 0, commission: -1.75, time: isoMinutesAgo(1440 - 1), comment: 'daily commission' },
    { deal_id: 900006, login: 50002, order: 0, position: 700001, symbol: 'EURUSD', action: 'in', type: 'swap', volume: 0, price: 0, profit: 0, swap: -3.2, commission: 0, time: isoMinutesAgo(1439), comment: 'swap charge' },
    { deal_id: 900007, login: 50001, order: 0, position: 0, symbol: '', action: 'in', type: 'balance', volume: 0, price: 0, profit: 5000, swap: 0, commission: 0, time: isoMinutesAgo(40000), comment: 'deposit via wire' },
    { deal_id: 900008, login: 50005, order: 0, position: 0, symbol: '', action: 'in', type: 'credit', volume: 0, price: 0, profit: 500, swap: 0, commission: 0, time: isoMinutesAgo(3900), comment: 'credit facility' },
    { deal_id: 900009, login: 50003, order: 459000460, position: 700006, symbol: 'AUDUSD', action: 'in', type: 'sell', volume: 0.1, price: 0.6660, profit: 0, swap: 0, commission: 0, time: isoMinutesAgo(45), comment: '' },
    { deal_id: 900010, login: 50002, order: 459000461, position: 700004, symbol: 'EURUSD', action: 'in/out', type: 'sell', volume: 0.5, price: 1.0866, profit: -12.4, swap: 0, commission: -1.75, time: isoMinutesAgo(2880), comment: 'partial reverse' },
    { deal_id: 900011, login: 50004, order: 459000462, position: 700003, symbol: 'USDJPY', action: 'out', type: 'buy', volume: 0.5, price: 156.9, profit: -24.0, swap: 0, commission: -1.5, time: isoMinutesAgo(60), comment: 'tp hit' },
    { deal_id: 900012, login: 50001, order: 459000463, position: 700002, symbol: 'XAUUSD', action: 'out by', type: 'sell', volume: 0.05, price: 2494.0, profit: 6.3, swap: 0, commission: 0, time: isoMinutesAgo(30), comment: 'closed by opposite' },
];

let routingRules = [
    { id: 1, name: 'dealer', priority: 1, is_enabled: true, match_groups: ['real\\real', 'real\\real-A'], match_symbols: ['*'], action: 'TO_DEALER' },
    { id: 2, name: 'Auto Execution', priority: 2, is_enabled: true, match_groups: ['demo\\*'], match_symbols: ['*'], action: 'CONFIRM_CLIENT' },
];

let gateways = [
    { id: 1, name: 'LP-Centroid-Primary', type: 'FIX', host: 'fix.lp.example.com', port: 8443, username: 'BROKER01', is_active: true, status: 'CONNECTED' },
    { id: 2, name: 'TradeServer-WS', type: 'WS', host: 'localhost', port: 8003, username: '', is_active: true, status: 'CONNECTED' },
    { id: 3, name: 'LP-Backup-REST', type: 'REST', host: 'api.lp2.example.com', port: 443, username: 'broker-backup', is_active: false, status: 'DISABLED' },
];

let clients = [
    {
        id: 'CL-00001', first_name: 'Alice', last_name: 'Sharma', middle_name: '', company: 'Sharma Traders Pvt',
        country: 'IN', state: 'Maharashtra', city: 'Mumbai', zip: '400001', address: '12 Marine Drive',
        email: 'alice@example.com', phone: '+91 98000 00001', registered: isoMinutesAgo(40000), status: 'verified',
        kyc: 'approved', regulation: 'Retail (SEBI jurisdiction)', language: 'en', id_number: 'PASSPORT M1234567',
        lead_source: 'website', lead_campaign: 'summer-2025', accounts: [50001],
        documents: [
            { id: 'D-11', type: 'Passport', number: 'M1234567', issued: '2019-04-02', expires: '2029-04-01', status: 'approved', versions: 2 },
            { id: 'D-12', type: 'Proof of address', number: 'EE-bill 08/2025', issued: '2025-08-11', expires: '2026-02-11', status: 'approved', versions: 1 },
        ],
        comments: [{ at: isoMinutesAgo(9000), by: '1001', text: 'KYC refresh completed via video call.' }],
        versions: [
            { at: isoMinutesAgo(40000), by: 'system', change: 'record created from demo account 50001' },
            { at: isoMinutesAgo(9000), by: '1001', change: 'KYC status → approved; PoA document added' },
        ],
    },
    {
        id: 'CL-00002', first_name: 'Bob', last_name: 'Verhoeven', middle_name: 'J.', company: 'BV Consulting B.V.',
        country: 'NL', state: '', city: 'Amsterdam', zip: '1011AB', address: 'Damrak 70',
        email: 'bob@example.com', phone: '+31 600 000002', registered: isoMinutesAgo(32000), status: 'verified',
        kyc: 'approved', regulation: 'Retail (ESMA)', language: 'en', id_number: 'BSN 123456789',
        lead_source: 'partner-mql5', lead_campaign: '', accounts: [50002],
        documents: [{ id: 'D-21', type: 'ID card', number: 'NL-8877', issued: '2021-01-15', expires: '2031-01-15', status: 'approved', versions: 1 }],
        comments: [], versions: [{ at: isoMinutesAgo(32000), by: 'system', change: 'record created from real account 50002' }],
    },
    {
        id: 'CL-00003', first_name: 'Chen', last_name: 'Wei', middle_name: '', company: '',
        country: 'CN', state: '', city: 'Shanghai', zip: '200000', address: 'Nanjing Rd 100',
        email: 'chen@example.com', phone: '+86 138 0000 0003', registered: isoMinutesAgo(21000), status: 'verified',
        kyc: 'pending', regulation: 'Retail', language: 'zh', id_number: '',
        lead_source: '', lead_campaign: '', accounts: [50003],
        documents: [{ id: 'D-31', type: 'Passport', number: 'E87654321', issued: '2022-06-01', expires: '2032-06-01', status: 'pending', versions: 1 }],
        comments: [{ at: isoMinutesAgo(500), by: '1002', text: 'Awaiting translated PoA.' }],
        versions: [{ at: isoMinutesAgo(21000), by: 'system', change: 'record created' }],
    },
    {
        id: 'CL-00004', first_name: 'Dana', last_name: 'Ivanova', middle_name: '', company: 'Ivanova EOOD',
        country: 'BG', state: '', city: 'Sofia', zip: '1000', address: 'Vitosha blvd 5',
        email: 'dana@example.com', phone: '+359 88 000 0004', registered: isoMinutesAgo(15000), status: 'verified',
        kyc: 'approved', regulation: 'Professional', language: 'bg', id_number: 'EGN 8801011234',
        lead_source: 'website', lead_campaign: 'pro-desk', accounts: [50004],
        documents: [], comments: [], versions: [{ at: isoMinutesAgo(15000), by: '1000', change: 'manual creation' }],
    },
    {
        id: 'CL-00005', first_name: 'Erik', last_name: 'Lindqvist', middle_name: '', company: '',
        country: 'SE', state: '', city: 'Stockholm', zip: '11120', address: 'Sveavägen 24',
        email: 'erik@example.com', phone: '+46 70 000 0005', registered: isoMinutesAgo(4000), status: 'demo',
        kyc: 'none', regulation: 'n/a (demo)', language: 'sv', id_number: '',
        lead_source: 'app-store', lead_campaign: '', accounts: [50005],
        documents: [], comments: [], versions: [{ at: isoMinutesAgo(4000), by: 'system', change: 'auto-created from demo registration' }],
    },
    {
        id: 'CL-00006', first_name: 'Fatima', last_name: 'Al-Sayed', middle_name: '', company: 'Sayed Capital',
        country: 'AE', state: '', city: 'Dubai', zip: '', address: 'DIFC Gate Village 4',
        email: 'fatima@example.com', phone: '+971 50 000 0006', registered: isoMinutesAgo(300), status: 'preliminary',
        kyc: 'pending', regulation: 'Retail (SCA)', language: 'en', id_number: 'EMU 784-1990-1234567-1',
        lead_source: 'expo-2026', lead_campaign: 'uae-launch', accounts: [],
        documents: [{ id: 'D-61', type: 'Emirates ID', number: '784-1990-1234567-1', issued: '2024-03-03', expires: '2027-03-03', status: 'pending', versions: 1 }],
        comments: [], versions: [{ at: isoMinutesAgo(300), by: 'system', change: 'preliminary registration' }],
    },
];

let managers = [
    { login: 1000, name: 'Platform Administrator', mailbox: 'admin', server_id: 1, role: 'ADMIN', rights_granted: 128, rights_total: 128, group_scope: ['*'], is_2fa_enabled: true, must_change_password: false, is_active: true, last_login: isoMinutesAgo(35), rights: ['*'], reports: { daily: true, monthly: true }, ip_access: ['0.0.0.0/0'] },
    { login: 1001, name: 'Senior Dealer', mailbox: 'dealing', server_id: 1, role: 'MANAGER', rights_granted: 96, rights_total: 128, group_scope: ['real\\*', 'demo\\*'], is_2fa_enabled: true, must_change_password: false, is_active: true, last_login: isoMinutesAgo(420), rights: ['accounts_view', 'accounts_edit', 'clients_view', 'clients_edit', 'trade_order_send', 'trade_order_close', 'trade_deal_modify', 'risk_manage', 'reports_run', 'manage_technical_accounts'], reports: { daily: true, monthly: false }, ip_access: ['10.0.0.0/8'] },
    { login: 1002, name: 'Support Desk', mailbox: 'support', server_id: 1, role: 'MANAGER', rights_granted: 24, rights_total: 128, group_scope: ['demo\\*'], is_2fa_enabled: false, must_change_password: true, is_active: true, last_login: isoMinutesAgo(2880), rights: ['accounts_view', 'clients_view', 'clients_edit'], reports: { daily: false, monthly: false }, ip_access: [] },
    { login: 1003, name: 'Auditor (read-only)', mailbox: '', server_id: 1, role: 'MANAGER', rights_granted: 8, rights_total: 128, group_scope: ['real\\real'], is_2fa_enabled: false, must_change_password: false, is_active: false, last_login: null, rights: ['accounts_view', 'reports_run'], reports: { daily: true, monthly: true }, ip_access: ['192.168.10.5/32'] },
];

let allocations = {
    demo_url: '',
    deposit_url: 'https://acme-broker.com/deposit',
    withdrawal_url: 'https://acme-broker.com/withdraw',
    rules: [
        { id: 1, kind: 'demo', group: 'demo\\demo', countries: '*', leverage: 100, extended_form: false },
        { id: 2, kind: 'real', group: 'real\\real', countries: 'EU, DE, NL, BG', leverage: 100, extended_form: true },
        { id: 3, kind: 'real', group: 'real\\IB', countries: 'AE, SA', leverage: 50, extended_form: true },
        { id: 4, kind: 'preliminary', group: 'preliminary\\prelim', countries: '*', leverage: 100, extended_form: true },
    ],
    agreements: [
        { id: 1, name: 'Client Agreement v4.2', required: true },
        { id: 2, name: 'Risk Disclosure Statement', required: true },
        { id: 3, name: 'Privacy & GDPR Consent', required: true },
        { id: 4, name: 'Professional Client Opt-in', required: false },
    ],
    verification: { phone: true, email: true, provider: 'SMTP+SMS gateway' },
};

/* per-account backoffice extras powering the 7-tab edit dialog (mock truth) */
const ACCOUNT_EXTRA: Record<number, any> = {
    50001: {
        middle_name: '', company: 'Sharma Traders Pvt', state: 'Maharashtra', zip: '400001', address: '12 Marine Drive',
        language: 'en', resident_status: 'NR', id_number: 'PASSPORT M1234567', lead_source: 'website', lead_campaign: 'summer-2025',
        registered: isoMinutesAgo(40000), last_login: isoMinutesAgo(60), last_login_ip: '103.21.58.14',
        color: '#4fc1ff', bank_account: '', agent_account: 0, allow_password_change: true, otp_enabled: false,
        limits: { show_to_managers: true, include_in_reports: true, daily_reports: true, api_connections: false, sponsored_vps: false },
        client_id: 'CL-00001',
        profile: { kyc: 'approved', risk_score: 'low', employment: 'employed', income_source: 'salary', annual_income: '50k–100k USD', education: 'university', experience_forex: '1–3 years', experience_stocks: 'none' },
        subscriptions: [{ service: 'VPS Hosting (sponsored)', state: 'active', since: isoMinutesAgo(20000), renewal: isoMinutesAgo(-20000), price: '0.00 USD/mo' }],
        passwords: { master: 'Mock#1234', investor: 'Mock#5678', webapi: '', phone: '' },
    },
    50002: {
        middle_name: 'J.', company: 'BV Consulting B.V.', state: '', zip: '1011AB', address: 'Damrak 70',
        language: 'en', resident_status: 'RE', id_number: 'BSN 123456789', lead_source: 'partner-mql5', lead_campaign: '',
        registered: isoMinutesAgo(32000), last_login: isoMinutesAgo(180), last_login_ip: '84.22.10.9',
        color: '#ff8a65', bank_account: 'NL91ABNA0417164300', agent_account: 0, allow_password_change: true, otp_enabled: true,
        limits: { show_to_managers: true, include_in_reports: true, daily_reports: true, api_connections: true, sponsored_vps: false },
        client_id: 'CL-00002',
        profile: { kyc: 'approved', risk_score: 'medium', employment: 'self-employed', income_source: 'business', annual_income: '100k+ EUR', education: 'university', experience_forex: '3–5 years', experience_stocks: '1–3 years' },
        subscriptions: [],
        passwords: { master: 'Mock#1234', investor: 'Mock#5678', webapi: 'Mock#9999', phone: '' },
    },
};

const defaultAccountExtra = (a: any) => ({
    middle_name: '', company: '', state: '', zip: '', address: '',
    language: 'en', resident_status: 'NR', id_number: '', lead_source: '', lead_campaign: '',
    registered: isoMinutesAgo(10000), last_login: isoMinutesAgo(1440), last_login_ip: '—',
    color: '#888888', bank_account: '', agent_account: 0, allow_password_change: true, otp_enabled: false,
    limits: { show_to_managers: true, include_in_reports: true, daily_reports: true, api_connections: false, sponsored_vps: false },
    client_id: clients.find((c) => c.accounts.includes(a.login))?.id ?? null,
    profile: { kyc: 'none', risk_score: '—', employment: '—', income_source: '—', annual_income: '—', education: '—', experience_forex: '—', experience_stocks: '—' },
    subscriptions: [],
    passwords: { master: 'Mock#1234', investor: '', webapi: '', phone: '' },
});


const ORDER_TYPE_LABEL: Record<number, string> = { 0: 'buy', 1: 'sell', 2: 'buy limit', 3: 'sell limit', 4: 'buy stop', 5: 'sell stop' };
const ORDER_STATE_LABEL: Record<number | string, string> = { 0: 'PLACED', 1: 'PARTIAL', 4: 'FILLED', 5: 'CANCELED', 6: 'DEALER', 7: 'GATEWAY', filled: 'FILLED', canceled: 'CANCELED', rejected: 'REJECTED', placed: 'PLACED' };

/** deterministic-ish tick series around an operation time (doc §Ticks) */
function genTicksAround(symbol: string, around: string): Array<{ time: string; bid: number; ask: number; last: number }> {
    const base = BASE_PRICES[symbol] ?? BASE_PRICES.EURUSD;
    const center = around ? new Date(around).getTime() : Date.now();
    const out: Array<{ time: string; bid: number; ask: number; last: number }> = [];
    let seed = symbol.length * 7919 + 13;
    const rnd = () => { seed = (seed * 9301 + 49297) % 233280; return seed / 233280; };
    const step = base.mid * 0.0002;
    for (let i = -20; i <= 20; i++) {
        const t = new Date(center + i * 450);
        const mid = base.mid + (rnd() - 0.5) * 2 * step * 6 + (i * step) / 4;
        const half = (base.spreadPts * Math.pow(10, -base.digits)) / 2;
        const bid = Number((mid - half).toFixed(base.digits));
        const ask = Number((mid + half).toFixed(base.digits));
        out.push({ time: t.toISOString(), bid, ask, last: bid });
    }
    return out;
}

/* ------------------------------------------------------------------ */
/* helpers                                                             */
/* ------------------------------------------------------------------ */

function isoMinutesAgo(min: number): string {
    return new Date(Date.now() - min * 60_000).toISOString().replace('T', ' ').slice(0, 19);
}

const BASE_PRICES: Record<string, { mid: number; spreadPts: number; digits: number }> = {
    EURUSD: { mid: 1.0846, spreadPts: 1.2, digits: 5 },
    GBPUSD: { mid: 1.3132, spreadPts: 1.5, digits: 5 },
    USDJPY: { mid: 156.42, spreadPts: 1.1, digits: 3 },
    USDCHF: { mid: 0.8871, spreadPts: 1.6, digits: 5 },
    AUDUSD: { mid: 0.6642, spreadPts: 1.4, digits: 5 },
    XAUUSD: { mid: 2496.1, spreadPts: 25, digits: 2 },
    XAGUSD: { mid: 28.42, spreadPts: 2.2, digits: 3 },
    US500: { mid: 5554.2, spreadPts: 40, digits: 2 },
};

const lastTick: Record<string, { bid: number; ask: number; at: number }> = {};

function nextTick(sym: string): { bid: number; ask: number; age: number } {
    const base = BASE_PRICES[sym];
    const prev = lastTick[sym];
    const step = base.mid * 0.00012; // ~1.2 pip jitter scale
    const drift = (Math.random() - 0.5) * 2 * step;
    const mid = prev ? Math.min(base.mid * 1.01, Math.max(base.mid * 0.99, prev.bid + drift)) : base.mid;
    const halfSpread = (base.spreadPts * Math.pow(10, -base.digits)) / 2;
    const bid = Number((mid - halfSpread).toFixed(base.digits));
    const ask = Number((mid + halfSpread).toFixed(base.digits));
    // occasionally leave a quote untouched so "age" visibly grows
    if (prev && Math.random() < 0.12) {
        return { bid: prev.bid, ask: prev.ask, age: Math.round((Date.now() - prev.at) / 1000) };
    }
    lastTick[sym] = { bid, ask, at: Date.now() };
    return { bid, ask, age: 0 };
}

/* ------------------------------------------------------------------ */
/* symbol settings blobs (SymbolDraft-shaped; the modal's source)      */
/* ------------------------------------------------------------------ */

const defaultSymbolSettings = (over: Record<string, unknown> = {}) => ({
    description: '',
    isin: '',
    intl_name: '',
    exchange: '',
    category: '',
    cfi: '',
    sector: '',
    industry: '',
    country: '',
    basis: '',
    info_page: '',
    quote_source: '',
    bg_color: '',
    market_depth: 0,
    fixed_spread: 0,
    spread_balance_bid: 0,
    spread_balance_ask: 0,
    chart_mode: 'bid',
    base_currency: 'USD',
    profit_currency: 'USD',
    margin_currency: 'USD',
    allow_realtime_quotes: true,
    allow_negative_prices: false,
    save_raw_prices: false,
    receive_market_stats: false,
    soft_filter_level: 0,
    soft_filter_repeats: 0,
    hard_filter_level: 0,
    hard_filter_repeats: 0,
    discard_filter_level: 0,
    min_spread: 0,
    max_spread: 0,
    gap_mode_level: 0,
    gap_disable_ticks: 0,
    delay_subscriptions: 0,
    calculation: 'Forex',
    trade_mode: 'full',
    gtc_mode: 0,
    limit_stop_level: 0,
    freeze_level: 0,
    max_quote_delay: 0,
    expiration_flags: ['gtc', 'day'],
    orders_allowed: ['market', 'limit', 'stop', 'sltp'],
    min_volume: 0.01,
    max_volume: 200,
    step_volume: 0.01,
    limit_volume: 0,
    execution_mode: 'Instant',
    instant_max_time_dev: 5,
    instant_fast_requotes: false,
    request_timeout: 30,
    request_confirm: false,
    margin_initial: 0,
    margin_maintenance: 0,
    exclude_long_pnl: false,
    calc_hedged_larger_leg: false,
    recalc_margin_eod: false,
    check_before_execution: false,
    check_on_sltp: false,
    rate_market_buy_init: 100,
    rate_market_buy_maint: 100,
    rate_market_sell_init: 100,
    rate_market_sell_maint: 100,
    rate_limit_buy_init: 100,
    rate_limit_buy_maint: 100,
    rate_limit_sell_init: 100,
    rate_limit_sell_maint: 100,
    enable_swaps: true,
    swap_type: 'points',
    swap_long: -0.5,
    swap_short: -1.2,
    swap_days_in_year: 360,
    swap_multipliers: { MON: 1, TUE: 1, WED: 3, THU: 1, FRI: 1, SAT: 0, SUN: 0 },
    session_hours: 'MON,00:00-24:00;TUE,00:00-24:00;WED,00:00-24:00;THU,00:00-24:00;FRI,00:00-24:00',
    splice_type: 'none',
    splice_date_extension: '',
    splice_shift_days: 0,
    option_type: 'call',
    option_style: 'european',
    strike_price: 0,
    bond_face_value: 0,
    bond_accrued_interest: 0,
    ...over,
});

const SYMBOL_SETTINGS: Record<string, Record<string, unknown>> = {
    EURUSD: defaultSymbolSettings({
        description: 'Euro vs US Dollar', isin: 'EU0009652759', intl_name: 'Euro / US Dollar',
        category: 'Forex', sector: 'FX', country: 'EU', fixed_spread: 12,
        spread_balance_bid: 5, spread_balance_ask: 7, base_currency: 'EUR', profit_currency: 'USD',
        margin_currency: 'USD', calculation: 'Forex', execution_mode: 'Instant',
    }),
    GBPUSD: defaultSymbolSettings({
        description: 'Great Britain Pound vs US Dollar', base_currency: 'GBP', profit_currency: 'USD',
        fixed_spread: 15, spread_balance_bid: 7, spread_balance_ask: 8,
    }),
    USDJPY: defaultSymbolSettings({
        description: 'US Dollar vs Japanese Yen', base_currency: 'USD', profit_currency: 'JPY',
        margin_currency: 'JPY', fixed_spread: 11,
    }),
    XAUUSD: defaultSymbolSettings({
        description: 'Gold vs US Dollar', isin: 'XC0009655157', exchange: 'LBMA', category: 'Metals',
        sector: 'Precious Metals', base_currency: 'XAU', profit_currency: 'USD',
        calculation: 'CFD', execution_mode: 'Market', fixed_spread: 25,
        swap_long: -12.5, swap_short: -8.1, session_hours:
            'MON,01:05-23:55;TUE,01:05-23:55;WED,01:05-23:55;THU,01:05-23:55;FRI,01:05-23:55',
    }),
    US500: defaultSymbolSettings({
        description: 'S&P 500 Index', category: 'Indices', sector: 'Equity Index',
        calculation: 'CFD Index', execution_mode: 'Market', fixed_spread: 40,
        swap_long: -4.8, swap_short: -2.2,
    }),
    ESU5: defaultSymbolSettings({
        description: 'E-mini S&P 500 Futures (demo of exchange mode)', exchange: 'CME',
        category: 'Futures', calculation: 'Exchange Futures', execution_mode: 'Exchange',
        basis: 'US500', splice_type: 'unadjusted', splice_shift_days: 3,
        market_depth: 16, chart_mode: 'last', session_hours:
            'MON,00:00-23:00;TUE,00:00-23:00;WED,00:00-23:00;THU,00:00-23:00;FRI,00:00-23:00',
    }),
};

const settingsFor = (name: string) =>
    SYMBOL_SETTINGS[name] ?? defaultSymbolSettings({});

/* UI row projection: the Symbols/Orders UIs consume `symbol` as the FULL
   folder path ("Forex\Major\EURUSD") plus digits + settings_json — the wire
   shape of the original backend. The transport owns this mapping. */
const fullPathOf = (s: any): string => (s.path ? `${s.path}\\${s.name}` : s.name);

const uiSymbolRow = (s: any) => {
    const settings = s.settings_json ? JSON.parse(s.settings_json) : settingsFor(s.name);
    return {
        symbol: fullPathOf(s),
        name: s.name,
        path: s.path ?? '',
        digits: s.digits,
        spread: s.spread,
        contract_size: s.contract_size,
        currency: s.quote_currency,
        volume_min: s.volume_min,
        volume_max: s.volume_max,
        volume_step: s.volume_step,
        trade_mode: s.trade_mode,
        exec_mode: s.exec_mode,
        is_trade_allowed: s.is_trade_allowed,
        settings_json: JSON.stringify(settings),
    };
};

const findSymbolByAnyName = (nameOrPath: string) =>
    symbols.find((s) => s.name === nameOrPath || fullPathOf(s) === nameOrPath);


/* doc §Orders/§Deals/§Positions request semantics: mask = logins / comma list /
   "#tickets" / "*"; symbols = comma list with folder masks and ! negation;
   openOnly = pending only (orders); from/to filter on execution time, open
   orders/deals without execution time are always included for orders. */
function maskMatchesLoginOrTicket(mask: string | undefined, login: number, ticket: number): boolean {
    const q = (mask ?? '').trim();
    if (!q || q === '*') return true;
    const parts = q.split(',').map((x) => x.trim()).filter(Boolean);
    return parts.some((part) => {
        if (part.startsWith('#')) return String(ticket) === part.slice(1);
        if (/^\d+$/.test(part)) return login === Number(part);
        const rx = new RegExp(`^${part.toLowerCase().replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace(/\\\*/g, '.*')}$`);
        return rx.test(String(login));
    });
}

function symbolListMatches(spec: string | undefined, symbol: string): boolean {
    const q = (spec ?? '').trim();
    if (!q) return true;
    const parts = q.split(',').map((x) => x.trim()).filter(Boolean);
    let matched = false;
    for (const part of parts) {
        if (part.startsWith('!')) {
            const rx = new RegExp(`^${part.slice(1).toLowerCase().replace(/\\*/g, '.*')}$`);
            if (rx.test(symbol.toLowerCase())) return false;
            continue;
        }
        const rx = new RegExp(`^${part.toLowerCase().replace(/\\*/g, '.*')}$`);
        if (rx.test(symbol.toLowerCase())) matched = true;
    }
    return matched;
}

function inPeriod(from: string | undefined, to: string | undefined, time: string | undefined): boolean {
    if (!time) return true;
    const t = new Date(time).getTime();
    if (from && t < new Date(from).getTime()) return false;
    if (to && t > new Date(to).getTime()) return false;
    return true;
}

let managerSession: any = null;

/* ------------------------------------------------------------------ */
/* transport                                                           */
/* ------------------------------------------------------------------ */

export const mockApi: AdminApi = {
    async getStatus() {
        await delay(40);
        return { status: 'ok', mode: 'mock', version: '0.1.0-mock', time: new Date().toISOString() };
    },

    /* accounts */
    async getAccounts() {
        await delay();
        return accounts.map((a) => ({ ...a }));
    },
    async getAccountDetail(login: number) {
        await delay();
        const a = accounts.find((x) => x.login === login);
        if (!a) throw new Error(`account ${login} not found`);
        const extra = ACCOUNT_EXTRA[login] ?? defaultAccountExtra(a);
        const pos = positions.filter((p) => p.login === login);
        const ords = orders.filter((o) => o.login === login);
        return {
            ...a,
            ...extra,
            positions: pos,
            orders: ords,
            state: {
                balance: a.balance,
                credit: a.credit,
                commission: -Math.round(pos.length * 1.75 * 100) / 100,
                swap: -Math.round(pos.length * 0.9 * 100) / 100,
                profit: a.profit,
            },
        };
    },
    async createAccount(data: any) {
        await delay();
        const login = data.login ? Number(data.login) : Math.max(...accounts.map((a) => a.login)) + 1;
        if (accounts.some((a) => a.login === login)) throw new Error(`login ${login} already exists`);
        const acc = {
            login,
            name: [data.name, data.last_name].filter(Boolean).join(' ') || `Account ${login}`,
            group: data.group_name || 'demo\\demo',
            currency: 'USD',
            balance: Number(data.initial_balance || 0),
            credit: 0,
            equity: Number(data.initial_balance || 0),
            profit: 0,
            margin: 0,
            margin_free: Number(data.initial_balance || 0),
            margin_level: 0,
            leverage: Number(data.leverage || 100),
            is_enabled: true,
            account_type: 'REAL',
            so_activation: 'PERCENT',
            email: data.email || '',
            phone: data.phone || '',
        };
        accounts = [...accounts, acc];
        return { status: 'success', login };
    },
    async updateAccount(login: number, data: any) {
        await delay();
        accounts = accounts.map((a) => (a.login === login ? { ...a, ...data, login } : a));
        return { status: 'success' };
    },
    async deleteAccount(login: number) {
        await delay();
        accounts = accounts.filter((a) => a.login !== login);
        return { status: 'success' };
    },
    async changePassword(login: number, newPassword: string) {
        await delay();
        if (!accounts.some((a) => a.login === login)) throw new Error(`account ${login} not found`);
        if (!newPassword || newPassword.length < 8) throw new Error('password must be at least 8 characters');
        return { status: 'success' };
    },

    /* clients / managers / allocations */
    async getClients() {
        await delay();
        return clients.map((c) => {
            const accs = accounts.filter((a) => c.accounts.includes(a.login));
            return {
                ...c,
                accounts: accs.map((a) => a.login),
                equity: accs.reduce((s, a) => s + a.equity, 0),
            };
        });
    },
    async getManagers() {
        await delay();
        return managers.map((m) => ({ ...m }));
    },
    async getAllocations() {
        await delay();
        return JSON.parse(JSON.stringify(allocations));
    },

    /* positions / deals */
    async getPositions(req) {
        await delay();
        return positions
            .filter((p) => maskMatchesLoginOrTicket(req?.mask, p.login, p.position_id))
            .filter((p) => symbolListMatches(req?.symbols, p.symbol))
            .map((p) => ({ ...p }));
    },
    async getDeals(req) {
        await delay();
        return deals
            .filter((d) => maskMatchesLoginOrTicket(req?.mask, d.login, d.deal_id))
            .filter((d) => symbolListMatches(req?.symbols, d.symbol))
            .filter((d) => inPeriod(req?.from, req?.to, d.time))
            .map((d) => ({ ...d }));
    },

    /* orders */
    async getOrders(req) {
        await delay();
        const active = orders
            .filter((o) => maskMatchesLoginOrTicket(req?.mask, o.login, o.ticket))
            .filter((o) => symbolListMatches(req?.symbols, o.symbol));
        const hist = orderHistory
            .filter((o) => (req?.openOnly ? false : true))
            .filter((o) => maskMatchesLoginOrTicket(req?.mask, o.login, o.ticket))
            .filter((o) => symbolListMatches(req?.symbols, o.symbol))
            .filter((o) => inPeriod(req?.from, req?.to, o.time_done));
        return [...active, ...hist].map((o) => ({ ...o }));
    },
    async getOrderHistory(req) {
        await delay();
        return orderHistory
            .filter((o) => maskMatchesLoginOrTicket(req?.mask, o.login, o.ticket))
            .filter((o) => symbolListMatches(req?.symbols, o.symbol))
            .filter((o) => inPeriod(req?.from, req?.to, o.time_done))
            .map((o) => ({ ...o }));
    },
    async cancelOrder(ticket: number | string, _force = false) {
        await delay();
        const o = orders.find((x) => String(x.ticket) === String(ticket));
        if (!o) throw new Error(`order ${ticket} not found`);
        orders = orders.filter((x) => String(x.ticket) !== String(ticket));
        orderHistory.unshift({ ...o, state: 'canceled', reason: 'Dealer', time_done: isoMinutesAgo(0), price_done: 0 });
        return { status: 'success' };
    },
    async placeOrder(data: PlaceOrderPayload) {
        await delay(220);
        const t = nextTick(data.symbol);
        const ticket = Math.max(459000000, ...orders.map((o) => o.ticket), ...orderHistory.map((o) => o.ticket)) + 1;
        const isMarket = data.type === 0 || data.type === 1;
        const fillPrice = data.type === 0 ? t.ask : t.bid;
        const order: any = {
            ticket,
            login: data.login,
            symbol: data.symbol,
            volume: data.volume,
            volume_current: data.volume,
            price_order: isMarket ? 0 : data.price_request,
            price_done: isMarket ? fillPrice : 0,
            price_sl: data.price_sl || 0,
            price_tp: data.price_tp || 0,
            type: data.type,
            state: isMarket ? 'filled' : 0,
            reason: 'Client',
            time_setup: isoMinutesAgo(0),
            time_done: isMarket ? isoMinutesAgo(0) : undefined,
        };
        if (isMarket) {
            orderHistory.unshift(order);
            positions.unshift({
                position_id: 700100 + (ticket % 900),
                login: data.login,
                symbol: data.symbol,
                type: data.type,
                volume: data.volume,
                price_open: fillPrice,
                price_current: fillPrice,
                sl: data.price_sl || 0,
                tp: data.price_tp || 0,
                profit: 0,
                swap: 0,
                commission: -Math.round(data.volume * 3.5 * 100) / 100,
                margin: Math.round(((fillPrice * data.volume * 100000) / 100) * 100) / 100,
                open_time: order.time_setup,
                update_time: order.time_setup,
                reason: 'Client',
                comment: '',
            });
        } else {
            orders.unshift(order);
        }
        return { status: 'success', retcode: 10009, order: ticket, price: fillPrice, volume: data.volume };
    },

    async closePosition(ticket: number | string, lots?: number, _price?: number, _type_filling?: string) {
        await delay();
        const id = Number(ticket);
        const p = positions.find((x) => x.position_id === id);
        if (!p) throw new Error(`position ${ticket} not found`);
        if (lots && lots < p.volume) {
            p.volume -= lots;
        } else {
            positions = positions.filter((x) => x.position_id !== id);
        }
        return { status: 'success' };
    },
    async modifyPosition(ticket: number | string, sl?: number, tp?: number) {
        await delay();
        const id = Number(ticket);
        const p = positions.find((x) => x.position_id === id);
        if (!p) throw new Error(`position ${ticket} not found`);
        if (sl !== undefined) p.sl = sl;
        if (tp !== undefined) p.tp = tp;
        return { status: 'success' };
    },
    async modifyOrder(ticket: number | string, price?: number, sl?: number, tp?: number) {
        await delay();
        const id = Number(ticket);
        const o = orders.find((x) => x.ticket === id);
        if (!o) throw new Error(`order ${ticket} not found`);
        if (price !== undefined) o.price_order = price;
        if (sl !== undefined) o.price_sl = sl;
        if (tp !== undefined) o.price_tp = tp;
        return { status: 'success' };
    },
    async closeAllPositions(_logins?: string, _type_filling?: string) {
        await delay();
        positions = [];
        return { status: 'success' };
    },

    async reopenOrder(ticket: number) {
        await delay();
        const idx = orderHistory.findIndex((o) => o.ticket === ticket);
        if (idx < 0) throw new Error(`order ${ticket} not found in history`);
        const o = orderHistory[idx];
        if (o.state !== 'canceled' && o.state !== 'filled') throw new Error(`order ${ticket} cannot be reopened`);
        orderHistory.splice(idx, 1);
        orders.unshift({ ...o, state: 0, time_setup: isoMinutesAgo(0) });
        return { status: 'success' };
    },

    async getTradeOperation(kind, id) {
        await delay(150);
        const chain: any[] = [];
        let title = '';
        let details: Record<string, any> = {};
        let login = 0;
        let opTime = '';
        let opPrice = 0;
        let sym = '';

        const dealRow = (d: any): any => ({ kind: 'deal', ticket: d.deal_id, time: d.time, ext_id: '', type: d.type, volume: d.volume ? String(d.volume) : '', price: d.price ? String(d.price) : '', reason: d.comment || 'Client', profit: d.profit });
        const orderRow = (o: any): any => ({ kind: 'order', ticket: o.ticket, time: o.time_setup, ext_id: '', type: ORDER_TYPE_LABEL[o.type] ?? String(o.type), volume: o.volume_current && o.volume_current !== o.volume ? `${o.volume_current} / ${o.volume}` : String(o.volume), price: o.type === 0 || o.type === 1 ? 'market' : String(o.price_order), reason: o.reason, profit: undefined });
        const posRow = (p: any): any => ({ kind: 'position', ticket: p.position_id, time: p.open_time, ext_id: '', type: p.type === 0 ? 'buy' : 'sell', volume: String(p.volume), price: String(p.price_open), reason: p.reason, profit: p.profit });

        if (kind === 'position') {
            const p = positions.find((x) => String(x.position_id) === String(id) || x.position_id === id);
            if (!p) throw new Error(`position ${id} not found`);
            login = p.login; sym = p.symbol; opTime = p.open_time; opPrice = p.price_open;
            title = `Position #${p.position_id} ${p.type === 0 ? 'buy' : 'sell'} ${p.volume} ${p.symbol} ${p.price_open}`;
            const relDeals = deals.filter((d) => String(d.position) === String(id));
            const relOrders = orders.concat(orderHistory).filter((o) => relDeals.some((d) => d.order === o.ticket));
            chain.push(...relDeals.map(dealRow), ...relOrders.map(orderRow), posRow(p));
            details = {
                position: p.position_id, type: p.type === 0 ? 'buy' : 'sell', volume: p.volume, symbol: p.symbol,
                opened: p.open_time, updated: p.update_time, reason: p.reason,
                dealer_id: '', expert_id: '', external_id: '', comment: p.comment ?? '',
                open_price: p.price_open, current_price: p.price_current, sl: p.sl, tp: p.tp,
                swap: p.swap, profit: p.profit, margin_rate: p.price_open,
                disabled_activations: [], modifications: [],
            };
        } else if (kind === 'order') {
            const o = orders.concat(orderHistory).find((x) => String(x.ticket) === String(id) || x.ticket === id);
            if (!o) throw new Error(`order ${id} not found`);
            login = o.login; sym = o.symbol; opTime = o.time_done || o.time_setup; opPrice = o.price_done || o.price_order;
            title = `Order #${o.ticket} ${ORDER_TYPE_LABEL[o.type]} ${o.volume_current} / ${o.volume} ${o.symbol} ${o.type === 0 || o.type === 1 ? 'at market' : `at ${o.price_order}`}`;
            const relDeals = deals.filter((d) => String(d.order) === String(id));
            const relPos = positions.filter((pp) => relDeals.some((d) => d.position === pp.position_id));
            chain.push(orderRow(o), ...relDeals.map(dealRow), ...relPos.map(posRow));
            details = {
                order: o.ticket, position: relPos[0]?.position_id ?? null, type: ORDER_TYPE_LABEL[o.type],
                volume: o.volume, remained_volume: Math.max(0, o.volume - (o.volume_current ?? 0)), symbol: o.symbol,
                reason: o.reason, state: ORDER_STATE_LABEL[o.state] ?? o.state, expiration: 'GTC', filling: 'IMMEDIATE OR CANCEL',
                dealer_id: '', expert_id: '', external_id: '', comment: '',
                setup_time: o.time_setup, done_time: o.time_done ?? '', expiration_time: '',
                order_price: o.price_order, current_price: o.price_done, trigger_price: 0, sl: o.price_sl, tp: o.price_tp,
                margin_rate: o.price_done || o.price_order, disabled_activations: [], modifications: [],
            };
        } else {
            const d = deals.find((x) => String(x.deal_id) === String(id) || x.deal_id === id);
            if (!d) throw new Error(`deal ${id} not found`);
            login = d.login; sym = d.symbol; opTime = d.time; opPrice = d.price;
            title = `Deal #${d.deal_id} ${d.type} ${d.volume} ${d.symbol || '—'} at ${d.price}`;
            const o = orders.concat(orderHistory).find((x) => x.ticket === d.order);
            const p = positions.find((x) => x.position_id === d.position);
            const siblings = deals.filter((x) => x.position === d.position && x.deal_id !== id);
            chain.push(dealRow(d), ...(o ? [orderRow(o)] : []), ...(p ? [posRow(p)] : []), ...siblings.map(dealRow));
            details = {
                deal: d.deal_id, position: d.position || null, order: d.order || null,
                type: d.type, action: d.action, volume: d.volume, closed_volume: d.action === 'out' || d.action === 'in/out' ? d.volume : 0, symbol: d.symbol,
                create_time: d.time, reason: d.reason ?? 'Dealer', dealer_id: '', expert_id: '', external_id: '', comment: d.comment ?? '',
                market_bid: d.price, market_ask: d.price, market_last: 0,
                price: d.price, position_price: p?.price_open ?? d.price, sl: 0, tp: 0,
                commission: d.commission, fee: 0, swap: d.swap, profit: d.profit, raw_profit: d.profit,
                profit_rate: 1, margin_rate: d.price, gateway_price: 0, modifications: [],
            };
        }

        chain.sort((a, b) => String(a.time).localeCompare(String(b.time)));
        const acc = accounts.find((a) => a.login === login);
        return {
            kind, id, title,
            account: acc ? { login: acc.login, name: acc.name, group: acc.group, leverage: acc.leverage } : null,
            chain,
            details,
            ticks: genTicksAround(sym || 'EURUSD', opTime),
            journal: [
                { time: opTime, server: 'TradeServer-Demo', message: `'${login}': ${kind} #${id} ${title.split(' ').slice(1).join(' ')} requested` },
                { time: opTime, server: 'TradeServer-Demo', message: `'${login}': ${kind} #${id} executed by ${details.reason ?? 'Client'} at ${opPrice}` },
                { time: opTime, server: 'HistoryServer', message: `tick stream archived for ${sym || 'n/a'} at ${opTime}` },
            ],
        };
    },

    async updateTradeOperation(kind, id, patch) {
        await delay();
        if (kind === 'position') {
            const p = positions.find((x) => String(x.position_id) === String(id) || x.position_id === id);
            if (!p) throw new Error(`position ${id} not found`);
            Object.assign(p, {
                sl: patch.sl ?? p.sl, tp: patch.tp ?? p.tp, comment: patch.comment ?? p.comment,
                reason: patch.reason ?? p.reason, type: patch.type === 'sell' ? 1 : patch.type === 'buy' ? 0 : p.type,
                volume: patch.volume ?? p.volume,
            });
        } else if (kind === 'order') {
            const o = orders.concat(orderHistory).find((x) => String(x.ticket) === String(id) || x.ticket === id);
            if (!o) throw new Error(`order ${id} not found`);
            Object.assign(o, {
                price_sl: patch.sl ?? o.price_sl, price_tp: patch.tp ?? o.tp ?? o.price_tp,
                comment: patch.comment ?? o.comment, reason: patch.reason ?? o.reason,
            });
        } else {
            const d = deals.find((x) => String(x.deal_id) === String(id) || x.deal_id === id);
            if (!d) throw new Error(`deal ${id} not found`);
            Object.assign(d, { comment: patch.comment ?? d.comment, reason: patch.reason ?? d.reason });
        }
        return { status: 'success' };
    },

    // Trade Calculators (MT5 trade/calc-* family)
    async calcMargin(params) {
        await delay(30);
        const lots = params.volume || 1.0;
        return {
            margin_required: String(lots * 1000),
            symbol: params.symbol,
            side: params.side,
            volume: String(lots),
            price_used: '1.08500',
            currency: params.currency || 'USD',
        };
    },
    async calcProfit(params) {
        await delay(30);
        const lots = params.volume || 1.0;
        return {
            profit: '0.00',
            symbol: params.symbol,
            side: params.side,
            volume: String(lots),
            open_price: String(params.open_price),
            close_price_used: '1.08500',
            currency: params.currency || 'USD',
        };
    },
    async calcRate(params) {
        await delay(20);
        return { rate: '1.00000', from: params.from_currency, to: params.to_currency };
    },
    async checkMargin(params) {
        await delay(30);
        return {
            margin_required: '11.37',
            margin_free: '1000.00',
            margin_level: '8800.0',
            status: 'NORMAL',
        };
    },

    /* symbols */
    async getSymbols() {
        await delay();
        return symbols.map(uiSymbolRow);
    },
    async getSymbolDetail(symbol: string) {
        await delay();
        const s = findSymbolByAnyName(symbol);
        if (!s) throw new Error(`symbol ${symbol} not found`);
        const row = uiSymbolRow(s);
        const settings = JSON.parse(row.settings_json);
        return {
            ...row,
            // base keys the modal reads before merging settings_json
            margin_initial: settings.margin_initial ?? 0,
            margin_maintenance: settings.margin_maintenance ?? 0,
            spread_base: row.spread,
            session_hours: settings.session_hours,
        };
    },
    async createSymbol(data: any) {
        await delay();
        const full: string = data.symbol ?? data.name ?? '';
        if (!full) throw new Error('symbol name required');
        if (findSymbolByAnyName(full)) throw new Error(`symbol ${full} already exists`);
        const idx = full.lastIndexOf('\\');
        const path = idx >= 0 ? full.slice(0, idx) : '';
        const name = idx >= 0 ? full.slice(idx + 1) : full;
        const { symbol: _s, settings_json, ...rest } = data;
        symbols.push({
            name,
            path,
            digits: 5,
            spread: 20,
            contract_size: 100000,
            quote_currency: 'USD',
            volume_min: 0.01,
            volume_max: 200,
            volume_step: 0.01,
            trade_mode: 'FULL',
            exec_mode: 'MARKET',
            is_trade_allowed: true,
            ...rest,
            ...(settings_json ? { settings_json } : {}),
        } as any);
        return { status: 'success' };
    },
    async updateSymbol(symbol: string, data: any) {
        await delay();
        const existing = findSymbolByAnyName(symbol);
        if (!existing) throw new Error(`symbol ${symbol} not found`);
        const { symbol: newFull, ...rest } = data;
        // postfix-copy / rename support: recompute name+path from the new full path
        let name = existing.name;
        let path = existing.path;
        if (typeof newFull === 'string' && newFull && newFull !== fullPathOf(existing)) {
            const idx = newFull.lastIndexOf('\\');
            path = idx >= 0 ? newFull.slice(0, idx) : '';
            name = idx >= 0 ? newFull.slice(idx + 1) : newFull;
        }
        symbols = symbols.map((s) =>
            s === existing ? ({ ...s, ...rest, name, path } as any) : s
        );
        return { status: 'success' };
    },
    async deleteSymbol(symbol: string) {
        await delay();
        const existing = findSymbolByAnyName(symbol);
        if (!existing) throw new Error(`symbol ${symbol} not found`);
        symbols = symbols.filter((s) => s !== existing);
        return { status: 'success' };
    },

    /* groups */
    async getGroups() {
        await delay();
        return groups.map((g) => ({ ...g }));
    },
    async getGroupDetail(name: string) {
        await delay();
        const g = groups.find((x) => x.name === name || x.name.replace(/\\/g, '/') === name.replace(/\\/g, '/'));
        if (!g) throw new Error(`group ${name} not found`);
        return { ...g };
    },
    async createGroup(data: any) {
        await delay();
        const id = Math.max(...groups.map((g) => g.id)) + 1;
        groups = [...groups, { id, name: data.name, account_type: 'REAL', currency: 'USD', settings_json: data.settings_json || groupSettings() }];
        return { status: 'success', group_id: id, name: data.name };
    },
    async updateGroup(name: string, data: any) {
        await delay();
        groups = groups.map((g) => (g.name === name ? { ...g, ...data, name: g.name } : g));
        return { status: 'success' };
    },
    async createGroupSymbolOverride(groupName: string, data: any) {
        await delay();
        return { status: 'success', group: groupName, ...data };
    },

    /* routing */
    async getRoutingRules() {
        await delay();
        return routingRules.map((r) => ({ ...r }));
    },
    async createRoutingRule(data: any) {
        await delay();
        const id = Math.max(0, ...routingRules.map((r) => r.id)) + 1;
        routingRules = [...routingRules, { ...data, id }];
        return { status: 'success', id };
    },
    async updateRoutingRule(id: number, data: any) {
        await delay();
        routingRules = routingRules.map((r) => (r.id === id ? { ...r, ...data } : r));
        return { status: 'success' };
    },
    async deleteRoutingRule(id: number) {
        await delay();
        routingRules = routingRules.filter((r) => r.id !== id);
        return { status: 'success' };
    },
    async enableRoutingRule(id: number) {
        await delay(60);
        routingRules = routingRules.map((r) => (r.id === id ? { ...r, is_enabled: true } : r));
        return { status: 'success' };
    },
    async disableRoutingRule(id: number) {
        await delay(60);
        routingRules = routingRules.map((r) => (r.id === id ? { ...r, is_enabled: false } : r));
        return { status: 'success' };
    },
    async reorderRoutingRules(ids: number[]) {
        await delay(60);
        const byId = new Map(routingRules.map((r) => [r.id, r]));
        routingRules = ids.map((id, i) => ({ ...(byId.get(id) as any), priority: i + 1 })).filter(Boolean);
        return { status: 'success' };
    },

    /* gateways */
    async getGateways() {
        await delay();
        return gateways.map((g) => ({ ...g }));
    },
    async createGateway(data: any) {
        await delay();
        const id = Math.max(0, ...gateways.map((g) => g.id)) + 1;
        gateways = [...gateways, { ...data, id, status: data.is_active === false ? 'DISABLED' : 'NEW' }];
        return { status: 'success', id };
    },
    async updateGateway(id: number, data: any) {
        await delay();
        gateways = gateways.map((g) => (g.id === id ? { ...g, ...data } : g));
        return { status: 'success' };
    },
    async testGateway(id: number) {
        await delay(600);
        const g = gateways.find((x) => x.id === id);
        if (!g) throw new Error(`gateway ${id} not found`);
        return { status: 'ok', gateway: g.name, latency_ms: Math.round(18 + Math.random() * 40), message: 'handshake ok (mock)' };
    },

    /* market data */
    async getTicks(): Promise<Ticks> {
        await delay(30);
        const out: Ticks = {};
        for (const sym of Object.keys(BASE_PRICES)) out[sym] = nextTick(sym);
        return out;
    },

    /* manager session */
    async managerConnect(server: string, login: number, password: string) {
        await delay(400);
        if (!password || password.length < 4) throw new Error('invalid manager password');
        managerSession = {
            connected: true, server, session_id: `session_${login}_${Date.now()}`,
            access_level: 'FULL', user_login: login, connected_at: new Date().toISOString(),
            permissions: ['accounts_view', 'accounts_edit', 'trade_order_send', 'clients_view'],
        };
        return managerSession;
    },
    async managerDisconnect() {
        await delay(80);
        managerSession = null;
        return { status: 'success' };
    },
    async managerSessionInfo() {
        await delay(30);
        return managerSession ?? { connected: false };
    },
    async balanceOperation(login: number, type: string, amount: number, comment?: string) {
        await delay(150);
        const a = accounts.find((x) => x.login === login);
        if (!a) throw new Error(`account ${login} not found`);
        const delta = (type === 'charge' || type === 'withdrawal') ? -Math.abs(amount) : Math.abs(amount);
        a.balance = Math.round((a.balance + delta) * 100) / 100;
        a.equity = Math.round((a.equity + delta) * 100) / 100;
        deals.unshift({
            deal_id: Math.max(...deals.map((d) => d.deal_id)) + 1,
            login, order: 0, position: 0, symbol: '', action: 'in', type,
            volume: 0, price: 0, profit: delta, swap: 0, commission: 0,
            time: isoMinutesAgo(0), comment: comment ?? 'balance operation',
        } as any);
        return { status: 'success', balance: a.balance };
    },

    /* manager terminal modules */
    async getManagerServerInfo() {
        await delay(60);
        return {
            connected: true, ping_ms: 41.7, version: '5.0.4323 (M18-mock)',
            memory_mb: 412.6, start_time: isoMinutesAgo(43200), server_time: new Date().toISOString(),
            accounts_online: 3, pump_modes: 'users|orders|positions|groups|symbols|mail|news|clients|subscriptions',
        };
    },
    async getOnlineUsers() {
        await delay();
        return [
            { login: 50001, name: 'Alice Sharma', group: 'demo\\demo', ip: '103.21.58.14', terminal: 'MetaTrader 5 x64 build 4320', connected_at: isoMinutesAgo(64), ping_ms: 82 },
            { login: 50002, name: 'Bob Verhoeven', group: 'real\\real', ip: '84.22.10.9', terminal: 'MetaTrader 5 x64 build 4320', connected_at: isoMinutesAgo(12), ping_ms: 41 },
            { login: 50003, name: 'Chen Wei', group: 'real\\real-A', ip: '112.65.4.1', terminal: 'MetaTrader 5 iOS build 1420', connected_at: isoMinutesAgo(3), ping_ms: 133 },
        ];
    },
    async getDealerQueue() {
        await delay();
        return orders.filter((o) => o.state === 6).map((o) => ({ ...o }));
    },
    async answerDealer(ticket, action, price) {
        await delay(200);
        const o = orders.find((x) => x.ticket === ticket);
        if (!o) throw new Error(`order ${ticket} not in queue`);
        if (action === 'confirm') {
            o.state = 'filled';
            o.price_done = price || o.price_order;
            o.time_done = isoMinutesAgo(0);
            orderHistory.unshift(o);
            orders = orders.filter((x) => x.ticket !== ticket);
        } else if (action === 'reject') {
            o.state = 'rejected';
            o.time_done = isoMinutesAgo(0);
            orderHistory.unshift(o);
            orders = orders.filter((x) => x.ticket !== ticket);
        } else {
            o.price_order = price ?? o.price_order; // requote: new price offered
        }
        return { status: 'success', action };
    },
    async getManagerNews() {
        await delay();
        return [
            { id: 1, time: isoMinutesAgo(55), title: 'Scheduled maintenance window', body: 'Trade server restart Sunday 02:00–02:15 UTC.', lang: 'en' },
            { id: 2, time: isoMinutesAgo(300), title: 'New symbol list: indices Q4', body: 'US500, DE40 roll dates updated.', lang: 'en' },
            { id: 3, time: isoMinutesAgo(1500), title: 'Swap triple day reminder', body: 'Wednesday multiplier applies per symbol swaps tab.', lang: 'en' },
        ];
    },
    async getManagerJournal() {
        await delay();
        return [
            { time: isoMinutesAgo(2), server: 'TradeServer', message: "'50002': order #459000601 placed (sell limit 0.5 EURUSD at 1.092)" },
            { time: isoMinutesAgo(6), server: 'TradeServer', message: "'50004': position #700003 modified by dealer (SL 157.6)" },
            { time: isoMinutesAgo(11), server: 'DealerDesk', message: 'request #459000603 queued for dealing (volume above auto-execution limit)' },
            { time: isoMinutesAgo(19), server: 'RiskEngine', message: "account 50005 margin level 226% — margin call threshold breached" },
            { time: isoMinutesAgo(27), server: 'HistoryServer', message: 'tick archive rolled for 2026.09.27' },
        ];
    },

    /* risk */
    async getRiskSummary() {
        await delay();
        const totalMargin = positions.reduce((s, p) => s + p.margin, 0);
        const totalProfit = positions.reduce((s, p) => s + p.profit, 0);
        return { total_accounts: accounts.length, open_positions: positions.length, total_margin: totalMargin, total_profit: totalProfit, margin_level_avg: totalMargin > 0 ? Math.round(((accounts.reduce((s, a) => s + a.equity, 0)) / totalMargin) * 100) / 100 : 0, at_risk_accounts: accounts.filter((a) => a.margin_level > 0 && a.margin_level < 300).length };
    },
    async getRiskExposure() {
        await delay();
        const bySym: Record<string, { symbol: string; net_volume: number; count: number }> = {};
        for (const p of positions) {
            const e = (bySym[p.symbol] ||= { symbol: p.symbol, net_volume: 0, count: 0 });
            e.net_volume += p.type === 0 ? p.volume : -p.volume;
            e.count += 1;
        }
        return Object.values(bySym);
    },
    async getRiskMarginCalls() {
        await delay();
        return accounts
            .filter((a) => a.margin_level > 0 && a.margin_level < 300)
            .map((a) => ({ login: a.login, group: a.group, margin_level: a.margin_level, state: a.margin_level < 150 ? 'STOP_OUT_PENDING' : 'MARGIN_CALL' }));
    },
};
