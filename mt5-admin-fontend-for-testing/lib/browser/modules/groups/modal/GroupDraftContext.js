"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.useGroupDraft = exports.GroupDraftContext = exports.DEFAULT_DRAFT = void 0;
const React = require("react");
exports.DEFAULT_DRAFT = {
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
exports.GroupDraftContext = React.createContext(undefined);
function useGroupDraft() {
    const context = React.useContext(exports.GroupDraftContext);
    if (!context) {
        throw new Error('useGroupDraft must be used within a GroupDraftProvider');
    }
    return context;
}
exports.useGroupDraft = useGroupDraft;
//# sourceMappingURL=GroupDraftContext.js.map