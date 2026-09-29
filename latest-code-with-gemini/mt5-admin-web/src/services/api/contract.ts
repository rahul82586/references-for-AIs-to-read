/**
 * AdminApi — the single contract every transport implements.
 *
 * Method names deliberately mirror the original Theia extension's `api.ts` so
 * ported pages call the exact same functions; only the import path changed.
 * F2 will split this into per-domain endpoint modules and generate DTO types
 * from the backend's OpenAPI schema; the contract boundary itself stays.
 *
 * Ground rules:
 *  - The frontend performs NO domain logic. These functions move data only.
 *  - Anything the real backend cannot serve yet throws BackendGapError —
 *    never a fabricated payload.
 */
import type { BackendGapError } from './errors';

export type Ticks = Record<string, { bid: number; ask: number; age: number; spread?: number }>;

/**
 * Trade-history request (doc §Orders/§Deals/§Positions "Requesting…"):
 * mask = logins / comma list / "#tickets" / "*" · symbols = list or folder
 * masks · openOnly (orders) · from/to (execution time) · db (current|backup).
 */
export interface TradeRequest {
    login?: number | string;
    mask?: string;
    symbols?: string;
    openOnly?: boolean;
    include_closed?: boolean;
    from?: string;
    to?: string;
    db?: string;
}

export interface PlaceOrderPayload {
    login: number;
    symbol: string;
    volume: number;
    price_request: number;
    type: number;
    price_sl?: number;
    price_tp?: number;
    type_filling?: string;
}

export interface RoutingRulePayload {
    name: string;
    priority: number;
    is_enabled: boolean;
    match_groups?: string[];
    match_symbols?: string[];
    match_accounts?: string[];
    match_order_types?: string[];
    match_volume_min?: number;
    match_volume_max?: number;
    action: string;
    gateway_id?: number;
    delay_seconds?: number;
}

export interface GatewayPayload {
    name: string;
    type: string;
    host?: string;
    port?: number;
    username?: string;
    api_key?: string;
    is_active?: boolean;
}

export interface GroupSymbolOverridePayload {
    symbol: string;
    spread_diff: number;
    commission_rate: number;
    margin_rate: number;
    trade_allowed: boolean;
}

export type OperationKind = 'position' | 'order' | 'deal';

export interface OperationChainRow {
    kind: OperationKind;
    ticket: number | string;
    time: string;
    ext_id: string;
    type: string;
    volume: string;
    volume_current?: string;
    price: string;
    reason: string;
    profit?: number;
    action?: string;
}

export interface TradeOperationView {
    kind: OperationKind;
    id: number | string;
    title: string;
    account: { login: number; name: string; group: string; leverage: number } | null;
    chain: OperationChainRow[];
    /** editable field set, keys per kind (see OperationDialog) */
    details: Record<string, any>;
    ticks: Array<{ time: string; bid: number; ask: number; last: number }>;
    journal: Array<{ time: string; server: string; message: string }>;
}

export interface AdminApi {
    // Server meta
    getStatus(): Promise<any>;

    // Accounts
    getAccounts(): Promise<any[]>;
    getAccountDetail(login: number): Promise<any>;
    createAccount(data: any): Promise<any>;
    updateAccount(login: number, data: any): Promise<any>;
    deleteAccount(login: number): Promise<any>;
    changePassword(login: number, newPassword: string): Promise<any>;

    // Clients / Managers / Allocations (MT5 entities, doc §Clients §Managers
    // §Account-Allocation-Settings)
    getClients(): Promise<any[]>;
    getManagers(): Promise<any[]>;
    getAllocations(): Promise<any[]>;

    // Positions
    getPositions(req?: TradeRequest): Promise<any[]>;

    // Deals
    getDeals(req?: TradeRequest): Promise<any[]>;

    // Orders
    getOrders(req?: TradeRequest): Promise<any[]>;
    getOrderHistory(req?: TradeRequest): Promise<any[]>;
    cancelOrder(ticket: number | string, force?: boolean): Promise<any>;
    placeOrder(data: any): Promise<any>;
    reopenOrder(ticket: number | string): Promise<any>;
    closePosition(ticket: number | string, lots?: number, price?: number, type_filling?: string): Promise<any>;
    modifyPosition(ticket: number | string, sl?: number, tp?: number, price?: number): Promise<any>;
    modifyOrder(ticket: number | string, price?: number, sl?: number, tp?: number): Promise<any>;
    closeAllPositions(logins?: string, type_filling?: string): Promise<any>;

    // Trading operation dialog (doc §Viewing an Order/Deal/Position)
    getTradeOperation(kind: OperationKind, id: number | string): Promise<TradeOperationView>;
    updateTradeOperation(kind: OperationKind, id: number | string, patch: Record<string, any>): Promise<any>;

    // Trade Calculators (MT5 trade/calc-* family)
    calcMargin(params: { group_name: string; symbol: string; side: 'BUY' | 'SELL' | string; volume: number; currency?: string }): Promise<any>;
    calcProfit(params: { symbol: string; side: 'BUY' | 'SELL' | string; volume: number; open_price: number; currency?: string }): Promise<any>;
    calcRate(params: { from_currency: string; to_currency: string; side?: string }): Promise<any>;
    checkMargin(params: { login: number; symbol: string; side: 'BUY' | 'SELL' | string; volume: number }): Promise<any>;

    // Symbols
    getSymbols(): Promise<any[]>;
    getSymbolDetail(symbol: string): Promise<any>;
    createSymbol(data: any): Promise<any>;
    updateSymbol(symbol: string, data: any): Promise<any>;
    deleteSymbol(symbol: string): Promise<any>;

    // Groups
    getGroups(): Promise<any[]>;
    getGroupDetail(name: string): Promise<any>;
    createGroup(data: any): Promise<any>;
    updateGroup(name: string, data: any): Promise<any>;
    createGroupSymbolOverride(groupName: string, data: GroupSymbolOverridePayload): Promise<any>;

    // Routing
    getRoutingRules(): Promise<any[]>;
    createRoutingRule(data: RoutingRulePayload): Promise<any>;
    updateRoutingRule(id: number, data: any): Promise<any>;
    deleteRoutingRule(id: number): Promise<any>;
    enableRoutingRule(id: number): Promise<any>;
    disableRoutingRule(id: number): Promise<any>;
    reorderRoutingRules(ids: number[]): Promise<any>;

    // Gateways
    getGateways(): Promise<any[]>;
    createGateway(data: GatewayPayload): Promise<any>;
    updateGateway(id: number, data: any): Promise<any>;
    testGateway(id: number): Promise<any>;

    // Market data
    getTicks(): Promise<Ticks>;

    // Manager session (MT5 Manager API Connect family — bp M18)
    managerConnect(server: string, login: number, password: string): Promise<any>;
    managerDisconnect(): Promise<any>;
    managerSessionInfo(): Promise<any>;
    /** balance operation on an account (Manager → Balance tab) */
    balanceOperation(login: number, type: 'balance' | 'credit' | 'correction' | 'bonus' | 'charge' | 'deposit' | 'withdrawal' | string, amount: number, comment?: string): Promise<any>;

    // Manager terminal modules (MT5APIManager.h / MT5-Manager-REST-API.md)
    getManagerServerInfo(): Promise<any>;
    getOnlineUsers(): Promise<any[]>;
    getDealerQueue(): Promise<any[]>;
    answerDealer(ticket: number, action: 'confirm' | 'reject' | 'requote', price?: number): Promise<any>;
    getManagerNews(): Promise<any[]>;
    getManagerJournal(): Promise<any[]>;

    // Risk
    getRiskSummary(): Promise<any>;
    getRiskExposure(): Promise<any[]>;
    getRiskMarginCalls(): Promise<any[]>;
}

export type { BackendGapError };
