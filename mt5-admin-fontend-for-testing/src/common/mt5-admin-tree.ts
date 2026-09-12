// @ts-nocheck

/**
 * MT5 Admin tree node types — mirrors the full MT5 Administrator sidebar.
 */

export interface AdminTreeNode {
    id: string;
    label: string;
    icon?: string;            // codicon name
    children?: AdminTreeNode[];
}

/**
 * Full MT5 Administrator sidebar tree, taken from the official documentation.
 * Each leaf node opens a dedicated tab in the main area.
 */
export const MT5_ADMIN_TREE: AdminTreeNode[] = [
    {
        id: 'start-page',
        label: 'Start Page',
        icon: 'home'
    },
    {
        id: 'network-cluster',
        label: 'Network Cluster',
        icon: 'server',
        children: [
            { id: 'network-cluster.servers',       label: 'Servers',         icon: 'server-environment' },
            { id: 'network-cluster.data-centers',  label: 'Data Centers',    icon: 'database' },
            { id: 'network-cluster.backup',        label: 'Backup Server',   icon: 'save' }
        ]
    },
    {
        id: 'integrations',
        label: 'Integrations',
        icon: 'plug',
        children: [
            { id: 'integrations.mail',      label: 'Mail Servers',  icon: 'mail' },
            { id: 'integrations.messenger', label: 'Messengers',    icon: 'comment-discussion' },
            { id: 'integrations.finteza',   label: 'Finteza',       icon: 'graph' }
        ]
    },
    {
        id: 'automations',
        label: 'Automations',
        icon: 'zap',
        children: [
            { id: 'automations.scenarios', label: 'Scenarios', icon: 'play' }
        ]
    },
    {
        id: 'security',
        label: 'Security',
        icon: 'shield',
        children: [
            { id: 'security.certificates',     label: 'Certificates',       icon: 'verified-filled' },
            { id: 'security.firewall',          label: 'Firewall',           icon: 'shield' },
            { id: 'security.antiddos',          label: 'Anti DDoS',          icon: 'shield-x' }
        ]
    },
    {
        id: 'time',
        label: 'Time',
        icon: 'clock'
    },
    {
        id: 'holidays',
        label: 'Holidays',
        icon: 'calendar'
    },
    {
        id: 'leverage',
        label: 'Leverage',
        icon: 'arrow-both'
    },
    {
        id: 'groups',
        label: 'Groups',
        icon: 'organization'
    },
    {
        id: 'clients-and-accounts',
        label: 'Clients & Accounts',
        icon: 'person',
        children: [
            { id: 'clients-and-accounts.allocations',      label: 'Allocations',      icon: 'list-selection' },
            { id: 'clients-and-accounts.clients',          label: 'Clients',          icon: 'organization' },
            { id: 'clients-and-accounts.managers',         label: 'Managers',         icon: 'account' },
            { id: 'clients-and-accounts.trading-accounts',  label: 'Trading Accounts',  icon: 'credit-card' }
        ]
    },
    {
        id: 'positions',
        label: 'Positions',
        icon: 'graph-scatter',
        children: [
            { id: 'positions.open',        label: 'Open Positions',          icon: 'graph-scatter' },
            { id: 'positions.summary',     label: 'Summary (Positions)',     icon: 'list-flat' },
            { id: 'positions.exposure',    label: 'Exposure (Assets)',       icon: 'pie-chart' },
            { id: 'positions.margin-call', label: 'Margin Call / Stop Out',  icon: 'warning' },
            { id: 'positions.history',     label: 'Position History',        icon: 'history' }
        ]
    },
    {
        id: 'orders',
        label: 'Orders',
        icon: 'list-ordered',
        children: [
            { id: 'orders.active',   label: 'Active Orders',   icon: 'clock' },
            { id: 'orders.history',  label: 'Order History',   icon: 'history' },
            { id: 'orders.create',   label: 'New Order',       icon: 'add' }
        ]
    },
    {
        id: 'deals',
        label: 'Deals',
        icon: 'pulse',
        children: [
            { id: 'deals.list',    label: 'Deal Log',     icon: 'list-unordered' },
            { id: 'deals.search',  label: 'Search',       icon: 'search' }
        ]
    },
    {
        id: 'payments',
        label: 'Payments',
        icon: 'credit-card',
        children: [
            { id: 'payments.list',       label: 'Payment Log',  icon: 'list-unordered' },
            { id: 'payments.systems',    label: 'Systems',      icon: 'plug' }
        ]
    },
    {
        id: 'gateways',
        label: 'Gateways',
        icon: 'radio-tower',
        children: [
            { id: 'gateways.list',    label: 'Gateway List', icon: 'list-unordered' },
            { id: 'gateways.routing', label: 'Routing',      icon: 'git-merge' }
        ]
    },
    {
        id: 'data-feeds',
        label: 'Data Feeds',
        icon: 'broadcast',
        children: [
            { id: 'data-feeds.sources',  label: 'Feed Sources', icon: 'database' },
            { id: 'data-feeds.news',     label: 'News',         icon: 'rss' }
        ]
    },
    {
        id: 'market-watch',
        label: 'Market Watch',
        icon: 'eye'
    },
    {
        id: 'plugins',
        label: 'Plugins',
        icon: 'extensions',
        children: [
            { id: 'plugins.installed', label: 'Installed',  icon: 'check' },
            { id: 'plugins.store',     label: 'App Store',  icon: 'package' }
        ]
    },
    {
        id: 'reports',
        label: 'Reports',
        icon: 'graph',
        children: [
            { id: 'reports.standard', label: 'Standard',  icon: 'list-flat' },
            { id: 'reports.custom',   label: 'Custom',    icon: 'edit' }
        ]
    },
    {
        id: 'ecn',
        label: 'ECN',
        icon: 'git-network'
    },
    {
        id: 'routing',
        label: 'Routing',
        icon: 'git-merge',
        children: [
            { id: 'routing.rules',      label: 'Routing Rules',     icon: 'list-ordered' },
            { id: 'routing.a-book',     label: 'A-Book',            icon: 'arrow-right' },
            { id: 'routing.b-book',     label: 'B-Book',            icon: 'arrow-left' },
            { id: 'routing.gateways',   label: 'LP Gateways',       icon: 'radio-tower' }
        ]
    },
    {
        id: 'funds-etf',
        label: 'Funds & ETF',
        icon: 'pie-chart',
        children: [
            { id: 'funds-etf.funds',    label: 'Funds',     icon: 'pie-chart' },
            { id: 'funds-etf.etf',      label: 'ETF',       icon: 'graph-line' }
        ]
    },
    {
        id: 'symbols',
        label: 'Symbols',
        icon: 'symbol-namespace'
    },
    {
        id: 'spreads',
        label: 'Spreads',
        icon: 'arrow-both'
    },
    {
        id: 'history-charts',
        label: '1-Min History Charts',
        icon: 'graph-line'
    },
    {
        id: 'tick-data',
        label: 'Bid/Ask/Last Ticks',
        icon: 'pulse'
    },
    {
        id: 'synchronization',
        label: 'Synchronization',
        icon: 'sync'
    },
    {
        id: 'subscriptions',
        label: 'Subscriptions',
        icon: 'rss'
    },
    {
        id: 'mailbox',
        label: 'Mailbox',
        icon: 'mail'
    },
    {
        id: 'live-update',
        label: 'Live Update',
        icon: 'cloud-download'
    },
    {
        id: 'support-center',
        label: 'Support Center',
        icon: 'question'
    },
    {
        id: 'app-store',
        label: 'App Store',
        icon: 'package'
    }
];
