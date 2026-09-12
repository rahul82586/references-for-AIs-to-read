"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.API = void 0;
const BASE_URL = 'http://localhost:8000';
const ADMIN_API_KEY = 'default_admin_api_key_token_change_in_production';
async function apiRequest(endpoint, options = {}) {
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
        let errMsg = errorText;
        try {
            const errJson = JSON.parse(errorText);
            errMsg = errJson.detail || errMsg;
            if (typeof errMsg === 'object') {
                if (Array.isArray(errMsg)) {
                    errMsg = errMsg.map(e => `${e.loc ? e.loc.join('.') : 'field'}: ${e.msg || JSON.stringify(e)}`).join(', ');
                }
                else {
                    errMsg = JSON.stringify(errMsg);
                }
            }
        }
        catch {
            // keep text
        }
        throw new Error(errMsg || `API error ${response.status}`);
    }
    return response.json();
}
exports.API = {
    // Accounts
    async getAccounts() {
        return apiRequest('/admin/accounts');
    },
    async getAccountDetail(login) {
        return apiRequest(`/admin/accounts/${login}`);
    },
    async createAccount(data) {
        return apiRequest('/admin/accounts', { method: 'POST', body: data });
    },
    async updateAccount(login, data) {
        return apiRequest(`/admin/accounts/${login}`, { method: 'PUT', body: data });
    },
    async deleteAccount(login) {
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
    async cancelOrder(ticket) {
        return apiRequest(`/admin/orders/${ticket}/cancel`, { method: 'POST' });
    },
    async placeOrder(data) {
        return apiRequest('/admin/trade/order', { method: 'POST', body: data });
    },
    // Symbols
    async getSymbols() {
        return apiRequest('/admin/symbols');
    },
    async getSymbolDetail(symbol) {
        return apiRequest(`/admin/symbols/${encodeURIComponent(symbol)}`);
    },
    async createSymbol(data) {
        return apiRequest('/admin/symbols', { method: 'POST', body: data });
    },
    async deleteSymbol(symbol) {
        return apiRequest(`/admin/symbols/${encodeURIComponent(symbol)}`, { method: 'DELETE' });
    },
    async updateSymbol(symbol, data) {
        return apiRequest(`/admin/symbols/${encodeURIComponent(symbol)}`, { method: 'PUT', body: data });
    },
    // Groups
    async getGroups() {
        return apiRequest('/admin/groups');
    },
    async getGroupDetail(name) {
        return apiRequest(`/admin/groups/${encodeURIComponent(name)}`);
    },
    async createGroup(data) {
        return apiRequest('/admin/groups', { method: 'POST', body: data });
    },
    async updateGroup(name, data) {
        return apiRequest(`/admin/groups/${encodeURIComponent(name)}`, { method: 'PUT', body: data });
    },
    async createGroupSymbolOverride(groupName, data) {
        return apiRequest(`/admin/groups/${encodeURIComponent(groupName)}/symbols`, { method: 'POST', body: data });
    },
    // Routing
    async getRoutingRules() {
        return apiRequest('/admin/routing');
    },
    async createRoutingRule(data) {
        return apiRequest('/admin/routing', { method: 'POST', body: data });
    },
    async updateRoutingRule(id, data) {
        return apiRequest(`/admin/routing/${id}`, { method: 'PUT', body: data });
    },
    async deleteRoutingRule(id) {
        return apiRequest(`/admin/routing/${id}`, { method: 'DELETE' });
    },
    async enableRoutingRule(id) {
        return apiRequest(`/admin/routing/${id}/enable`, { method: 'POST' });
    },
    async disableRoutingRule(id) {
        return apiRequest(`/admin/routing/${id}/disable`, { method: 'POST' });
    },
    async reorderRoutingRules(ids) {
        return apiRequest('/admin/routing/reorder', { method: 'POST', body: ids });
    },
    // Gateways
    async getGateways() {
        return apiRequest('/admin/gateways');
    },
    async createGateway(data) {
        return apiRequest('/admin/gateways', { method: 'POST', body: data });
    },
    async updateGateway(id, data) {
        return apiRequest(`/admin/gateways/${id}`, { method: 'PUT', body: data });
    },
    async testGateway(id) {
        return apiRequest(`/admin/gateways/${id}/test`, { method: 'POST' });
    },
    // Live market quotes (for Market Watch debug panel)
    async getTicks() {
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
//# sourceMappingURL=api.js.map