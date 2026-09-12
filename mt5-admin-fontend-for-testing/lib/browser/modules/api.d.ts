export declare const API: {
    getAccounts(): Promise<any>;
    getAccountDetail(login: number): Promise<any>;
    createAccount(data: any): Promise<any>;
    updateAccount(login: number, data: any): Promise<any>;
    deleteAccount(login: number): Promise<any>;
    getPositions(): Promise<any>;
    getDeals(): Promise<any>;
    getOrders(): Promise<any>;
    getOrderHistory(): Promise<any>;
    cancelOrder(ticket: number): Promise<any>;
    placeOrder(data: {
        login: number;
        symbol: string;
        volume: number;
        price_request: number;
        type: number;
        price_sl?: number;
        price_tp?: number;
        type_filling?: string;
    }): Promise<any>;
    getSymbols(): Promise<any>;
    getSymbolDetail(symbol: string): Promise<any>;
    createSymbol(data: any): Promise<any>;
    deleteSymbol(symbol: string): Promise<any>;
    updateSymbol(symbol: string, data: any): Promise<any>;
    getGroups(): Promise<any>;
    getGroupDetail(name: string): Promise<any>;
    createGroup(data: {
        name: string;
        max_leverage: number;
        margin_call: number;
        margin_stop_out: number;
        spread_override: number;
    }): Promise<any>;
    updateGroup(name: string, data: any): Promise<any>;
    createGroupSymbolOverride(groupName: string, data: {
        symbol: string;
        spread_diff: number;
        commission_rate: number;
        margin_rate: number;
        trade_allowed: boolean;
    }): Promise<any>;
    getRoutingRules(): Promise<any>;
    createRoutingRule(data: {
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
    }): Promise<any>;
    updateRoutingRule(id: number, data: any): Promise<any>;
    deleteRoutingRule(id: number): Promise<any>;
    enableRoutingRule(id: number): Promise<any>;
    disableRoutingRule(id: number): Promise<any>;
    reorderRoutingRules(ids: number[]): Promise<any>;
    getGateways(): Promise<any>;
    createGateway(data: {
        name: string;
        type: string;
        host?: string;
        port?: number;
        username?: string;
        api_key?: string;
        is_active?: boolean;
    }): Promise<any>;
    updateGateway(id: number, data: any): Promise<any>;
    testGateway(id: number): Promise<any>;
    getTicks(): Promise<Record<string, {
        bid: number;
        ask: number;
        age: number;
    }>>;
    getRiskSummary(): Promise<any>;
    getRiskExposure(): Promise<any>;
    getRiskMarginCalls(): Promise<any>;
};
//# sourceMappingURL=api.d.ts.map