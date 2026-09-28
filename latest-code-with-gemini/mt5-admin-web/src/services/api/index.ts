/**
 * API facade — the single entry point features import.
 *
 * Keeps the exact method names the ported Theia pages already call, and
 * dispatches every call to the active transport (mock | live) chosen in the
 * Settings panel / VITE_API_MODE. Swapping transports is instant — no reload
 * needed — so any screen can be A/B'd against the real backend with one click.
 */
import type { AdminApi } from './contract';
import { mockApi } from '../transport/mock';
import { liveApi } from '../transport/http';
import { useSettingsStore } from '../../store/settingsStore';

export * from './contract';
export * from './errors';

function activeTransport(): AdminApi {
    const { apiMode } = useSettingsStore.getState();
    // env can force a default (e.g. CI demos), the persisted setting wins after
    // the user touches it; zustand persist rehydrates before first render.
    if (apiMode === 'live') return liveApi;
    return mockApi;
}

type ApiFacade = { [K in keyof AdminApi]: AdminApi[K] };

export const API: ApiFacade = {
    getStatus: (...a) => activeTransport().getStatus(...a),

    getAccounts: (...a) => activeTransport().getAccounts(...a),
    getAccountDetail: (...a) => activeTransport().getAccountDetail(...a),
    createAccount: (...a) => activeTransport().createAccount(...a),
    updateAccount: (...a) => activeTransport().updateAccount(...a),
    deleteAccount: (...a) => activeTransport().deleteAccount(...a),
    changePassword: (...a) => activeTransport().changePassword(...a),

    getClients: (...a) => activeTransport().getClients(...a),
    getManagers: (...a) => activeTransport().getManagers(...a),
    getAllocations: (...a) => activeTransport().getAllocations(...a),

    getPositions: (...a) => activeTransport().getPositions(...a),
    getDeals: (...a) => activeTransport().getDeals(...a),

    getOrders: (...a) => activeTransport().getOrders(...a),
    getOrderHistory: (...a) => activeTransport().getOrderHistory(...a),
    cancelOrder: (...a) => activeTransport().cancelOrder(...a),
    placeOrder: (...a) => activeTransport().placeOrder(...a),
    reopenOrder: (...a) => activeTransport().reopenOrder(...a),
    closePosition: (...a) => activeTransport().closePosition(...a),
    modifyPosition: (...a) => activeTransport().modifyPosition(...a),
    modifyOrder: (...a) => activeTransport().modifyOrder(...a),
    closeAllPositions: (...a) => activeTransport().closeAllPositions(...a),

    getTradeOperation: (...a) => activeTransport().getTradeOperation(...a),
    updateTradeOperation: (...a) => activeTransport().updateTradeOperation(...a),

    getSymbols: (...a) => activeTransport().getSymbols(...a),
    getSymbolDetail: (...a) => activeTransport().getSymbolDetail(...a),
    createSymbol: (...a) => activeTransport().createSymbol(...a),
    updateSymbol: (...a) => activeTransport().updateSymbol(...a),
    deleteSymbol: (...a) => activeTransport().deleteSymbol(...a),

    getGroups: (...a) => activeTransport().getGroups(...a),
    getGroupDetail: (...a) => activeTransport().getGroupDetail(...a),
    createGroup: (...a) => activeTransport().createGroup(...a),
    updateGroup: (...a) => activeTransport().updateGroup(...a),
    createGroupSymbolOverride: (...a) => activeTransport().createGroupSymbolOverride(...a),

    getRoutingRules: (...a) => activeTransport().getRoutingRules(...a),
    createRoutingRule: (...a) => activeTransport().createRoutingRule(...a),
    updateRoutingRule: (...a) => activeTransport().updateRoutingRule(...a),
    deleteRoutingRule: (...a) => activeTransport().deleteRoutingRule(...a),
    enableRoutingRule: (...a) => activeTransport().enableRoutingRule(...a),
    disableRoutingRule: (...a) => activeTransport().disableRoutingRule(...a),
    reorderRoutingRules: (...a) => activeTransport().reorderRoutingRules(...a),

    getGateways: (...a) => activeTransport().getGateways(...a),
    createGateway: (...a) => activeTransport().createGateway(...a),
    updateGateway: (...a) => activeTransport().updateGateway(...a),
    testGateway: (...a) => activeTransport().testGateway(...a),

    getTicks: (...a) => activeTransport().getTicks(...a),

    getRiskSummary: (...a) => activeTransport().getRiskSummary(...a),
    getRiskExposure: (...a) => activeTransport().getRiskExposure(...a),
    getRiskMarginCalls: (...a) => activeTransport().getRiskMarginCalls(...a),
};
