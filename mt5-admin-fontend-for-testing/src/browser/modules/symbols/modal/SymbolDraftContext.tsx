import * as React from 'react';

export interface SymbolDraft {
    symbol: string;
    digits: number;
    contract_size: number;
    currency: string;
    margin_initial: number;
    margin_maintenance: number;
    spread_base: number;
    session_hours: string;
    
    // Common tab
    description: string;
    isin: string;
    intl_name: string;
    exchange: string;
    category: string;
    cfi: string;
    sector: string;
    industry: string;
    country: string;
    basis: string;
    info_page: string;
    quote_source: string;
    bg_color: string;
    market_depth: number;
    fixed_spread: number;
    spread_balance_bid: number;
    spread_balance_ask: number;
    chart_mode: 'bid' | 'last';
    
    // Currency tab
    base_currency: string;
    profit_currency: string;
    margin_currency: string;

    // Quotes tab
    allow_realtime_quotes: boolean;
    allow_negative_prices: boolean;
    save_raw_prices: boolean;
    receive_market_stats: boolean;
    soft_filter_level: number;
    soft_filter_repeats: number;
    hard_filter_level: number;
    hard_filter_repeats: number;
    discard_filter_level: number;
    min_spread: number;
    max_spread: number;
    gap_mode_level: number;
    gap_disable_ticks: number;
    delay_subscriptions: number;

    // Trade tab
    calculation: string; 
    trade_mode: 'disabled' | 'long_only' | 'short_only' | 'close_only' | 'full';
    gtc_mode: number;
    limit_stop_level: number;
    freeze_level: number;
    max_quote_delay: number;
    expiration_flags: string[]; 
    orders_allowed: string[]; 
    min_volume: number;
    max_volume: number;
    step_volume: number;
    limit_volume: number;

    // Execution tab
    execution_mode: 'Instant' | 'Request' | 'Market' | 'Exchange';
    instant_max_time_dev: number;
    instant_fast_requotes: boolean;
    request_timeout: number;
    request_confirm: boolean;

    // Margin tab
    exclude_long_pnl: boolean;
    calc_hedged_larger_leg: boolean;
    recalc_margin_eod: boolean;
    check_before_execution: boolean;
    check_on_sltp: boolean;

    // Margin Rates tab
    rate_market_buy_init: number;
    rate_market_buy_maint: number;
    rate_market_sell_init: number;
    rate_market_sell_maint: number;
    rate_limit_buy_init: number;
    rate_limit_buy_maint: number;
    rate_limit_sell_init: number;
    rate_limit_sell_maint: number;

    // Swaps tab
    enable_swaps: boolean;
    swap_type: 'points' | 'money' | 'percent' | 'reopen_close' | 'reopen_bid';
    swap_long: number;
    swap_short: number;
    swap_days_in_year: number;
    swap_multipliers: Record<string, number>; 

    // Futures tab
    splice_type: 'none' | 'unadjusted' | 'adjusted';
    splice_date_extension: string;
    splice_shift_days: number;

    // Options tab
    option_type: 'call' | 'put';
    option_style: 'american' | 'european';
    strike_price: number;

    // Bonds tab
    bond_face_value: number;
    bond_accrued_interest: number;
}

export const DEFAULT_SYMBOL_DRAFT: SymbolDraft = {
    symbol: '',
    digits: 5,
    contract_size: 100000.0,
    currency: 'USD',
    margin_initial: 1.0,
    margin_maintenance: 1.0,
    spread_base: 10,
    session_hours: 'MON,00:00-24:00;TUE,00:00-24:00;WED,00:00-24:00;THU,00:00-24:00;FRI,00:00-24:00',

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
    bg_color: '#ffffff',
    market_depth: 0,
    fixed_spread: 0,
    spread_balance_bid: 0,
    spread_balance_ask: 0,
    chart_mode: 'bid',

    base_currency: 'EUR',
    profit_currency: 'USD',
    margin_currency: 'EUR',

    allow_realtime_quotes: true,
    allow_negative_prices: false,
    save_raw_prices: false,
    receive_market_stats: true,
    soft_filter_level: 5,
    soft_filter_repeats: 3,
    hard_filter_level: 15,
    hard_filter_repeats: 3,
    discard_filter_level: 50,
    min_spread: 0,
    max_spread: 0,
    gap_mode_level: 5,
    gap_disable_ticks: 3,
    delay_subscriptions: 0,

    calculation: 'Forex',
    trade_mode: 'full',
    gtc_mode: 0,
    limit_stop_level: 0,
    freeze_level: 0,
    max_quote_delay: 15,
    expiration_flags: ['gtc', 'day'],
    orders_allowed: ['market', 'limit', 'stop', 'sltp'],
    min_volume: 0.01,
    max_volume: 100.0,
    step_volume: 0.01,
    limit_volume: 0.0,

    execution_mode: 'Instant',
    instant_max_time_dev: 5,
    instant_fast_requotes: true,
    request_timeout: 10,
    request_confirm: false,

    exclude_long_pnl: false,
    calc_hedged_larger_leg: false,
    recalc_margin_eod: true,
    check_before_execution: true,
    check_on_sltp: true,

    rate_market_buy_init: 1.0,
    rate_market_buy_maint: 1.0,
    rate_market_sell_init: 1.0,
    rate_market_sell_maint: 1.0,
    rate_limit_buy_init: 1.0,
    rate_limit_buy_maint: 1.0,
    rate_limit_sell_init: 1.0,
    rate_limit_sell_maint: 1.0,

    enable_swaps: true,
    swap_type: 'points',
    swap_long: -0.5,
    swap_short: -0.2,
    swap_days_in_year: 360,
    swap_multipliers: {
        'Mon': 1,
        'Tue': 1,
        'Wed': 3,
        'Thu': 1,
        'Fri': 1,
        'Sat': 0,
        'Sun': 0
    },

    splice_type: 'none',
    splice_date_extension: '',
    splice_shift_days: 0,

    option_type: 'call',
    option_style: 'american',
    strike_price: 0.0,

    bond_face_value: 100.0,
    bond_accrued_interest: 0.0
};

export interface SymbolDraftContextType {
    draft: SymbolDraft;
    setDraft: React.Dispatch<React.SetStateAction<SymbolDraft>>;
    errors: Record<string, string>;
    setErrors: React.Dispatch<React.SetStateAction<Record<string, string>>>;
    isEditing: boolean;
}

export const SymbolDraftContext = React.createContext<SymbolDraftContextType | undefined>(undefined);

export function useSymbolDraft() {
    const context = React.useContext(SymbolDraftContext);
    if (!context) {
        throw new Error('useSymbolDraft must be used within SymbolDraftProvider');
    }
    return context;
}
