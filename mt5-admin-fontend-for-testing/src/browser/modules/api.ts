const BASE_URL = 'http://localhost:8000';
const ADMIN_API_KEY = 'default_admin_api_key_token_change_in_production';

interface RequestOptions {
    method?: string;
    body?: any;
    headers?: Record<string, string>;
}

async function apiRequest<T = any>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    const url = `${BASE_URL}${endpoint}`;
    const headers = {
        'Content-Type': 'application/json',
        'X-Admin-API-Key': ADMIN_API_KEY,
        ...options.headers,
    };
    
    const response = await fetch(url, {
        method: options.method || 'GET',
        headers,
        body: options.body ? JSON.stringify(options.body) : undefined,
    });

    if (!response.ok) {
        const errorText = await response.text();
        let errMsg: any = errorText;
        try {
            const errJson = JSON.parse(errorText);
            errMsg = errJson.detail || errMsg;
            if (typeof errMsg === 'object') {
                if (Array.isArray(errMsg)) {
                    errMsg = errMsg.map(e => `${e.loc ? e.loc.join('.') : 'field'}: ${e.msg || JSON.stringify(e)}`).join(', ');
                } else {
                    errMsg = JSON.stringify(errMsg);
                }
            }
        } catch {
            // keep text
        }
        throw new Error(errMsg || `API error ${response.status}`);
    }

    return response.json();
}

export const API = {
    // Accounts
    async getAccounts() {
        return apiRequest('/admin/accounts');
    },
    async getAccountDetail(login: number) {
        return apiRequest(`/admin/accounts/${login}`);
    },
    async createAccount(data: any) {
        return apiRequest('/admin/accounts', { method: 'POST', body: data });
    },
    async updateAccount(login: number, data: any) {
        return apiRequest(`/admin/accounts/${login}`, { method: 'PUT', body: data });
    },
    async deleteAccount(login: number) {
        return apiRequest(`/admin/accounts/${login}`, { method: 'DELETE' });
    },

    // Positions
    async getPositions() {
        return apiRequest('/admin/positions');
    },

    // Deals
    async getDeals() {
        return apiRequest('/admin/deals');
    },

    // Orders
    async getOrders() {
        return apiRequest('/admin/orders');
    },
    async getOrderHistory() {
        return apiRequest('/admin/orders/history');
    },
    async cancelOrder(ticket: number) {
        return apiRequest(`/admin/orders/${ticket}/cancel`, { method: 'POST' });
    },
    async placeOrder(data: { login: number; symbol: string; volume: number; price_request: number; type: number; price_sl?: number; price_tp?: number; type_filling?: string }) {
        return apiRequest('/admin/trade/order', { method: 'POST', body: data });
    },

    // Symbols
    async getSymbols() {
        return apiRequest('/admin/symbols');
    },
    async getSymbolDetail(symbol: string) {
        return apiRequest(`/admin/symbols/${encodeURIComponent(symbol)}`);
    },
    async createSymbol(data: any) {
        return apiRequest('/admin/symbols', { method: 'POST', body: data });
    },
    async deleteSymbol(symbol: string) {
        return apiRequest(`/admin/symbols/${encodeURIComponent(symbol)}`, { method: 'DELETE' });
    },
    async updateSymbol(symbol: string, data: any) {
        return apiRequest(`/admin/symbols/${encodeURIComponent(symbol)}`, { method: 'PUT', body: data });
    },

    // Groups
    async getGroups() {
        return apiRequest('/admin/groups');
    },
    async getGroupDetail(name: string) {
        return apiRequest(`/admin/groups/${encodeURIComponent(name)}`);
    },
    async createGroup(data: { name: string; max_leverage: number; margin_call: number; margin_stop_out: number; spread_override: number }) {
        return apiRequest('/admin/groups', { method: 'POST', body: data });
    },
    async updateGroup(name: string, data: any) {
        return apiRequest(`/admin/groups/${encodeURIComponent(name)}`, { method: 'PUT', body: data });
    },
    async createGroupSymbolOverride(groupName: string, data: { symbol: string; spread_diff: number; commission_rate: number; margin_rate: number; trade_allowed: boolean }) {
        return apiRequest(`/admin/groups/${encodeURIComponent(groupName)}/symbols`, { method: 'POST', body: data });
    },

    // Routing
    async getRoutingRules() {
        return apiRequest('/admin/routing');
    },
    async createRoutingRule(data: { name: string; priority: number; is_enabled: boolean; match_groups?: string[]; match_symbols?: string[]; match_accounts?: string[]; match_order_types?: string[]; match_volume_min?: number; match_volume_max?: number; action: string; gateway_id?: number; delay_seconds?: number }) {
        return apiRequest('/admin/routing', { method: 'POST', body: data });
    },
    async updateRoutingRule(id: number, data: any) {
        return apiRequest(`/admin/routing/${id}`, { method: 'PUT', body: data });
    },
    async deleteRoutingRule(id: number) {
        return apiRequest(`/admin/routing/${id}`, { method: 'DELETE' });
    },
    async enableRoutingRule(id: number) {
        return apiRequest(`/admin/routing/${id}/enable`, { method: 'POST' });
    },
    async disableRoutingRule(id: number) {
        return apiRequest(`/admin/routing/${id}/disable`, { method: 'POST' });
    },
    async reorderRoutingRules(ids: number[]) {
        return apiRequest('/admin/routing/reorder', { method: 'POST', body: ids });
    },

    // Gateways
    async getGateways() {
        return apiRequest('/admin/gateways');
    },
    async createGateway(data: { name: string; type: string; host?: string; port?: number; username?: string; api_key?: string; is_active?: boolean }) {
        return apiRequest('/admin/gateways', { method: 'POST', body: data });
    },
    async updateGateway(id: number, data: any) {
        return apiRequest(`/admin/gateways/${id}`, { method: 'PUT', body: data });
    },
    async testGateway(id: number) {
        return apiRequest(`/admin/gateways/${id}/test`, { method: 'POST' });
    },

    // Live market quotes (for Market Watch debug panel)
    async getTicks(): Promise<Record<string, { bid: number; ask: number; age: number }>> {
        return apiRequest('/admin/ticks');
    },

    // Risk Management (RMS)
    async getRiskSummary() {
        return apiRequest('/admin/risk/summary');
    },
    async getRiskExposure() {
        return apiRequest('/admin/risk/exposure');
    },
    async getRiskMarginCalls() {
        return apiRequest('/admin/risk/margin-calls');
    }
};
