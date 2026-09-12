import * as React from 'react';

export interface SymbolRule {
    symbol: string;
    trade_allowed: boolean;
    spread_diff: number;
    commission_rate: number;
    margin_rate: number;

    // Common Tab Extra Settings
    enable_dom?: boolean;
    dom_limit?: string;
    use_default_spreads?: boolean;
    diff_balance?: string;
    use_default_volumes?: boolean;
    vol_min?: number;
    vol_step?: number;
    vol_max?: number;
    use_default_limit?: boolean;
    vol_limit?: number;

    // Trade Tab Extra Settings
    use_default_trade?: boolean;
    trade_mode?: string;
    filling_fok?: boolean;
    filling_ioc?: boolean;
    filling_boc?: boolean;
    expiration_gtc?: boolean;
    expiration_day?: boolean;
    expiration_time?: boolean;
    expiration_date?: boolean;
    use_default_trade_levels?: boolean;
    limit_stop_level?: number;
    freeze_level?: number;

    // Execution Tab Extra Settings
    use_default_execution?: boolean;
    exec_mode?: string;
    instant_max_time_dev?: number;
    instant_max_profit_dev?: number;
    instant_max_loss_dev?: number;
    instant_max_volume?: number;
    request_timeout?: number;
    request_confirm?: boolean;

    // Margin Tab Extra Settings
    use_default_margin?: boolean;
    initial_margin?: number;
    maintenance_margin?: number;
    hedged_margin?: number;
    calc_hedged_larger_leg?: boolean;
    exclude_long_pnl?: boolean;
    recalc_margin_eod?: boolean;
    margin_check_exec?: boolean;
    margin_check_sltp?: boolean;

    // Margin Rates Tab Extra Settings
    use_default_margin_rates?: boolean;
    liquidity_rate?: number;
    currency_rate?: number;
    rate_market_buy?: number;
    rate_market_sell?: number;
    rate_limit_buy?: number;
    rate_limit_sell?: number;
    rate_stop_buy?: number;
    rate_stop_sell?: number;
    rate_stop_limit_buy?: number;
    rate_stop_limit_sell?: number;

    // Swaps Tab Extra Settings
    swap_type?: string;
    swap_long?: number;
    swap_short?: number;
    swap_days_in_year?: number;
    swap_multiplier_mon?: number;
    swap_multiplier_tue?: number;
    swap_multiplier_wed?: number;
    swap_multiplier_thu?: number;
    swap_multiplier_fri?: number;
    swap_multiplier_sat?: number;
    swap_multiplier_sun?: number;
    swap_consider_holidays?: boolean;
}

export interface CommissionRule {
    name: string;
    symbols: string;
    rate: number;
    type: 'points' | 'percent' | 'money';
}

export interface GroupDraft {
    name: string;
    max_leverage: number;
    spread_override: number;
    currency: string;
    digits: number;
    trade_server: string;
    authentication: string;
    min_password_len: number;
    enable_cert_confirm: boolean;
    change_pass_first_login: boolean;
    otp_mode: 'disabled' | 'all' | 'web';
    force_otp: boolean;
    push_placed_orders: boolean;
    push_performed_deals: boolean;
    push_balance_operations: boolean;
    enable_connections: boolean;
    show_risk_warning: boolean;
    regulatory_restrictions: boolean;

    // Company Tab
    company: string;
    company_website: string;
    company_email: string;
    deposit_url: string;
    withdrawal_url: string;
    support_site: string;
    support_email: string;
    templates_folder: string;

    // News & Mail Tab
    news_mode: 'none' | 'headers' | 'full';
    news_categories: string;
    news_languages: string[];
    enable_internal_mail: boolean;

    // Permissions Tab
    max_symbols: number;
    max_positions: number;
    max_orders: number;
    available_history: string;
    interest_rate: number;
    default_deposit: number;
    default_leverage: number;
    trade_signals_mode: 'disabled' | 'all' | 'own_only';
    transfer_funds_mode: 'disabled' | 'same_details' | 'subgroup' | 'subgroup_name';
    enable_swaps: boolean;
    enable_trailing_stops: boolean;
    enable_ea_trading: boolean;
    fifo_rule: boolean;
    prohibit_hedge: boolean;
    deal_cost_calc: boolean;
    inactivity_days: number;

    // Margin Tab
    risk_management_model: 'netting' | 'hedging' | 'discount';
    margin_call: number;
    margin_stop_out: number;
    stop_out_mode: 'percent' | 'money';
    stop_out_hedged: boolean;
    compensate_negative_balance: boolean;
    withdraw_credit_after_comp: boolean;
    floating_leverage_profile: string;
    virtual_credit: number;
    unrealized_profit_mode: number;
    daily_fixed_profit_mode: number;
    release_fixed_profit: boolean;

    // Symbol & Commission Lists
    symbol_rules: SymbolRule[];
    commission_rules: CommissionRule[];

    // Reports Tab
    report_generation: 'off' | 'daily' | 'monthly' | 'both';
    generate_statements: boolean;
    send_statements_email: boolean;
    mail_server: string;
    send_copies_support: boolean;
    gateway_id?: number;
}

export const DEFAULT_DRAFT: GroupDraft = {
    name: '',
    max_leverage: 100,
    spread_override: 0,
    currency: 'USD',
    digits: 2,
    trade_server: 'MetaQuotes-Demo',
    authentication: 'Normal',
    min_password_len: 8,
    enable_cert_confirm: false,
    change_pass_first_login: false,
    otp_mode: 'disabled',
    force_otp: false,
    push_placed_orders: false,
    push_performed_deals: false,
    push_balance_operations: false,
    enable_connections: true,
    show_risk_warning: false,
    regulatory_restrictions: false,

    company: '',
    company_website: '',
    company_email: '',
    deposit_url: '',
    withdrawal_url: '',
    support_site: '',
    support_email: '',
    templates_folder: '',

    news_mode: 'full',
    news_categories: '',
    news_languages: ['Any language'],
    enable_internal_mail: true,

    max_symbols: 0,
    max_positions: 0,
    max_orders: 0,
    available_history: 'All',
    interest_rate: 0,
    default_deposit: 10000,
    default_leverage: 100,
    trade_signals_mode: 'all',
    transfer_funds_mode: 'same_details',
    enable_swaps: true,
    enable_trailing_stops: true,
    enable_ea_trading: true,
    fifo_rule: false,
    prohibit_hedge: false,
    deal_cost_calc: true,
    inactivity_days: 360,

    risk_management_model: 'hedging',
    margin_call: 50,
    margin_stop_out: 30,
    stop_out_mode: 'percent',
    stop_out_hedged: false,
    compensate_negative_balance: true,
    withdraw_credit_after_comp: true,
    floating_leverage_profile: 'Default',
    virtual_credit: 0,
    unrealized_profit_mode: 0,
    daily_fixed_profit_mode: 0,
    release_fixed_profit: false,

    symbol_rules: [{ symbol: '*', trade_allowed: true, spread_diff: 0, commission_rate: 0, margin_rate: 1.0 }],
    commission_rules: [],

    report_generation: 'off',
    generate_statements: false,
    send_statements_email: false,
    mail_server: 'Default',
    send_copies_support: false
};

interface GroupDraftContextProps {
    draft: GroupDraft;
    setDraft: React.Dispatch<React.SetStateAction<GroupDraft>>;
    errors: Record<string, string>;
    setErrors: React.Dispatch<React.SetStateAction<Record<string, string>>>;
    isEditing: boolean;
}

export const GroupDraftContext = React.createContext<GroupDraftContextProps | undefined>(undefined);

export function useGroupDraft() {
    const context = React.useContext(GroupDraftContext);
    if (!context) {
        throw new Error('useGroupDraft must be used within a GroupDraftProvider');
    }
    return context;
}
