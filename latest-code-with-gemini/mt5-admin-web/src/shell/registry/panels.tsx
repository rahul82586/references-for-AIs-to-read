/**
 * Panel definitions — the composition root of the feature layer.
 * Every feature is lazy-loaded: opening a section for the first time pulls
 * its chunk. F1 adds the remaining ~20 features here, one line each.
 */
import * as React from 'react';
import { registerPanel } from './panel-registry';

registerPanel({
    id: 'market-watch',
    title: 'Market Watch',
    icon: 'eye',
    component: React.lazy(() =>
        import('../../features/market-watch/MarketWatchPage').then((m) => ({ default: m.MarketWatchPage }))
    ),
});

registerPanel({
    id: 'groups',
    title: 'Groups',
    icon: 'organization',
    component: React.lazy(() =>
        import('../../features/groups/GroupsPage').then((m) => ({ default: m.GroupsOverviewPage }))
    ),
});

registerPanel({
    id: 'orders',
    title: 'Orders',
    icon: 'list-ordered',
    component: React.lazy(() =>
        import('../../features/orders-deals/OrdersPanel').then((m) => ({ default: m.OrdersPanel }))
    ),
});

registerPanel({
    id: 'positions',
    title: 'Positions',
    icon: 'graph-scatter',
    component: React.lazy(() =>
        import('../../features/orders-deals/PositionsPanel').then((m) => ({ default: m.PositionsPanel }))
    ),
});

registerPanel({
    id: 'deals',
    title: 'Deals',
    icon: 'pulse',
    component: React.lazy(() =>
        import('../../features/orders-deals/DealsPanel').then((m) => ({ default: m.DealsPanel }))
    ),
});

registerPanel({
    id: 'symbols',
    title: 'Symbols',
    icon: 'symbol-namespace',
    component: React.lazy(() =>
        import('../../features/symbols/SymbolsPage').then((m) => ({ default: m.SymbolsPage }))
    ),
});

registerPanel({
    id: 'clients',
    title: 'Clients & Accounts',
    icon: 'person',
    component: React.lazy(() =>
        import('../../features/clients/ClientsPage').then((m) => ({ default: m.ClientsPage }))
    ),
});

registerPanel({
    id: 'settings',
    title: 'Settings',
    icon: 'settings-gear',
    component: React.lazy(() =>
        import('../../features/settings/SettingsPanel').then((m) => ({ default: m.SettingsPanel }))
    ),
});

registerPanel({
    id: 'welcome',
    title: 'Start Page',
    icon: 'home',
    component: React.lazy(() =>
        import('../../features/welcome/WelcomePanel').then((m) => ({ default: m.WelcomePanel }))
    ),
});

registerPanel({
    id: 'placeholder',
    title: 'Section',
    icon: 'tools',
    component: React.lazy(() =>
        import('../../features/placeholder/PlaceholderPanel').then((m) => ({ default: m.PlaceholderPanel }))
    ),
});

registerPanel({
    id: 'trade-panel',
    title: 'Trade Terminal',
    icon: 'pulse',
    component: React.lazy(() =>
        import('../../features/trade-panel/TradePanel').then((m) => ({ default: m.TradePanel }))
    ),
});
