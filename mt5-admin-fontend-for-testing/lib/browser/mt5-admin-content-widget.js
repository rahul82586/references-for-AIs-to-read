"use strict";
var Mt5AdminContentWidget_1;
Object.defineProperty(exports, "__esModule", { value: true });
exports.Mt5AdminContentWidget = void 0;
const tslib_1 = require("tslib");
// @ts-nocheck
const React = require("react");
const inversify_1 = require("@theia/core/shared/inversify");
const browser_1 = require("@theia/core/lib/browser");
// Network Cluster
const NetworkClusterPage_1 = require("./modules/network-cluster/NetworkClusterPage");
// Groups
const GroupsPage_1 = require("./modules/groups/GroupsPage");
// Clients
const ClientsPage_1 = require("./modules/clients/ClientsPage");
// Positions
const PositionsPage_1 = require("./modules/positions/PositionsPage");
const SummaryPage_1 = require("./modules/positions/SummaryPage");
const ExposurePage_1 = require("./modules/positions/ExposurePage");
const MarginCallPage_1 = require("./modules/positions/MarginCallPage");
// Orders
const OrdersPage_1 = require("./modules/orders/OrdersPage");
// Deals
const DealsPage_1 = require("./modules/deals/DealsPage");
// Gateways
const GatewaysPage_1 = require("./modules/gateways/GatewaysPage");
// Data Feeds
const DataFeedsPage_1 = require("./modules/data-feeds/DataFeedsPage");
// Routing
const RoutingPage_1 = require("./modules/routing/RoutingPage");
// Symbols
const SymbolsPage_1 = require("./modules/symbols/SymbolsPage");
// Market Watch (debug)
const MarketWatchPage_1 = require("./modules/market-watch/MarketWatchPage");
let Mt5AdminContentWidget = Mt5AdminContentWidget_1 = class Mt5AdminContentWidget extends browser_1.ReactWidget {
    constructor() {
        super(...arguments);
        this.nodeId = '';
        this.nodeLabel = '';
        this.filterPath = '';
    }
    static createId(nodeId) {
        return `mt5-admin-content:${nodeId}`;
    }
    setFilterPath(path) {
        this.filterPath = path;
        this.update();
    }
    initialize(nodeId, nodeLabel) {
        this.nodeId = nodeId;
        this.nodeLabel = nodeLabel;
        this.id = Mt5AdminContentWidget_1.createId(nodeId);
        this.title.label = nodeLabel;
        this.title.caption = nodeLabel;
        this.title.closable = true;
        this.title.iconClass = `codicon codicon-${this.getIconForNode(nodeId)}`;
        this.addClass('mt5-admin-content-widget');
        this.update();
    }
    getIconForNode(id) {
        const map = {
            'start-page': 'home',
            'network-cluster': 'server',
            'network-cluster.servers': 'server-environment',
            'network-cluster.data-centers': 'database',
            'network-cluster.backup': 'save',
            'groups': 'organization',
            'groups.settings': 'settings-gear',
            'groups.types': 'type-hierarchy',
            'groups.symbols': 'graph-line',
            'groups.permissions': 'lock',
            'allocations': 'list-selection',
            'clients-and-accounts': 'person',
            'clients-and-accounts.allocations': 'list-selection',
            'clients-and-accounts.clients': 'organization',
            'clients-and-accounts.managers': 'account',
            'clients-and-accounts.trading-accounts': 'credit-card',
            'positions': 'graph-scatter',
            'positions.open': 'graph-scatter',
            'positions.summary': 'list-flat',
            'positions.exposure': 'pie-chart',
            'positions.margin-call': 'warning',
            'positions.history': 'history',
            'orders': 'list-ordered',
            'orders.active': 'clock',
            'orders.history': 'history',
            'orders.create': 'add',
            'deals': 'pulse',
            'deals.list': 'list-unordered',
            'deals.search': 'search',
            'gateways': 'radio-tower',
            'gateways.list': 'radio-tower',
            'gateways.routing': 'git-merge',
            'data-feeds': 'broadcast',
            'data-feeds.sources': 'database',
            'data-feeds.news': 'rss',
            'routing': 'git-merge',
            'routing.rules': 'list-ordered',
            'routing.a-book': 'arrow-right',
            'routing.b-book': 'arrow-left',
            'routing.gateways': 'radio-tower',
            'symbols': 'symbol-namespace',
            'symbols.list': 'list-unordered',
            'symbols.create': 'add',
            'symbols.sessions': 'clock',
            'market-watch': 'eye',
        };
        return map[id] || 'server';
    }
    postInit() { }
    /**
     * Each node ID maps to a DISTINCT React component / view.
     * Sub-nodes must render different content from their parent.
     */
    renderPage(nodeId) {
        switch (nodeId) {
            // ── Network Cluster ──────────────────────────────────────
            case 'network-cluster': return React.createElement(NetworkClusterPage_1.NetworkClusterOverview, null);
            case 'network-cluster.servers': return React.createElement(NetworkClusterPage_1.NetworkServersPage, null);
            case 'network-cluster.data-centers': return React.createElement(NetworkClusterPage_1.NetworkDataCentersPage, null);
            case 'network-cluster.backup': return React.createElement(NetworkClusterPage_1.NetworkBackupPage, null);
            // ── Groups ───────────────────────────────────────────────
            case 'groups': return React.createElement(GroupsPage_1.GroupsOverviewPage, { selectedPath: this.filterPath });
            // ── Clients / Accounts ───────────────────────────────────
            case 'clients-and-accounts': return React.createElement(ClientsPage_1.ClientsPage, { initialTab: "accounts" });
            case 'clients-and-accounts.allocations': return React.createElement(ClientsPage_1.ClientsPage, { initialTab: "allocations" });
            case 'clients-and-accounts.clients': return React.createElement(ClientsPage_1.ClientsPage, { initialTab: "clients" });
            case 'clients-and-accounts.managers': return React.createElement(ClientsPage_1.ClientsPage, { initialTab: "managers" });
            case 'clients-and-accounts.trading-accounts': return React.createElement(ClientsPage_1.ClientsPage, { initialTab: "accounts" });
            // ── Positions ────────────────────────────────────────────
            case 'positions': return React.createElement(PositionsPage_1.PositionsPage, { view: "open" });
            case 'positions.open': return React.createElement(PositionsPage_1.PositionsPage, { view: "open" });
            case 'positions.summary': return React.createElement(SummaryPage_1.SummaryPage, null);
            case 'positions.exposure': return React.createElement(ExposurePage_1.ExposurePage, null);
            case 'positions.margin-call': return React.createElement(MarginCallPage_1.MarginCallPage, null);
            case 'positions.history': return React.createElement(PositionsPage_1.PositionsPage, { view: "history" });
            // ── Orders ───────────────────────────────────────────────
            case 'orders': return React.createElement(OrdersPage_1.OrdersPage, { view: "active" });
            case 'orders.active': return React.createElement(OrdersPage_1.OrdersPage, { view: "active" });
            case 'orders.history': return React.createElement(OrdersPage_1.OrdersPage, { view: "history" });
            case 'orders.create': return React.createElement(OrdersPage_1.OrdersPage, { view: "new" });
            // ── Deals ────────────────────────────────────────────────
            case 'deals': return React.createElement(DealsPage_1.DealsPage, { view: "log" });
            case 'deals.list': return React.createElement(DealsPage_1.DealsPage, { view: "log" });
            case 'deals.search': return React.createElement(DealsPage_1.DealsPage, { view: "search" });
            // ── Gateways ─────────────────────────────────────────────
            case 'gateways': return React.createElement(GatewaysPage_1.GatewaysPage, { view: "list" });
            case 'gateways.list': return React.createElement(GatewaysPage_1.GatewaysPage, { view: "list" });
            case 'gateways.routing': return React.createElement(GatewaysPage_1.GatewaysPage, { view: "routing" });
            // ── Data Feeds ───────────────────────────────────────────
            case 'data-feeds': return React.createElement(DataFeedsPage_1.DataFeedsPage, { view: "sources" });
            case 'data-feeds.sources': return React.createElement(DataFeedsPage_1.DataFeedsPage, { view: "sources" });
            case 'data-feeds.news': return React.createElement(DataFeedsPage_1.DataFeedsPage, { view: "news" });
            // ── Market Watch (debug) ─────────────────────────────────
            case 'market-watch': return React.createElement(MarketWatchPage_1.MarketWatchPage, null);
            // ── Routing ──────────────────────────────────────────────
            case 'routing': return React.createElement(RoutingPage_1.RoutingPage, { view: "all" });
            case 'routing.rules': return React.createElement(RoutingPage_1.RoutingPage, { view: "all" });
            case 'routing.a-book': return React.createElement(RoutingPage_1.RoutingPage, { view: "a-book" });
            case 'routing.b-book': return React.createElement(RoutingPage_1.RoutingPage, { view: "b-book" });
            case 'routing.gateways': return React.createElement(RoutingPage_1.RoutingPage, { view: "gateways" });
            // ── Symbols ──────────────────────────────────────────────
            case 'symbols': return React.createElement(SymbolsPage_1.SymbolsPage, { selectedPath: this.filterPath });
            default: return this.renderPlaceholder(nodeId);
        }
    }
    renderPlaceholder(nodeId) {
        return (React.createElement("div", { className: "mt5-admin-section-placeholder" },
            React.createElement("div", { className: "mt5-admin-section-desc" },
                React.createElement("strong", null, this.nodeLabel),
                " \u2014 This section is being implemented."),
            React.createElement("div", { className: "mt5-admin-section-wip" },
                React.createElement("i", { className: "codicon codicon-tools", style: { marginRight: '8px' } }),
                "Connect to ",
                React.createElement("code", null, "localhost:8000"),
                " API.")));
    }
    render() {
        return (React.createElement("div", { className: "mt5-admin-content-panel" },
            React.createElement("div", { className: "mt5-admin-content-header" },
                React.createElement("i", { className: `codicon codicon-${this.getIconForNode(this.nodeId)} mt5-admin-content-header-icon` }),
                React.createElement("h1", { className: "mt5-admin-content-title" }, this.nodeLabel)),
            React.createElement("div", { className: "mt5-admin-content-body", style: { padding: 0, display: 'flex', flexDirection: 'column', flex: 1, overflow: 'hidden' } }, this.renderPage(this.nodeId))));
    }
};
exports.Mt5AdminContentWidget = Mt5AdminContentWidget;
tslib_1.__decorate([
    (0, inversify_1.postConstruct)(),
    tslib_1.__metadata("design:type", Function),
    tslib_1.__metadata("design:paramtypes", []),
    tslib_1.__metadata("design:returntype", void 0)
], Mt5AdminContentWidget.prototype, "postInit", null);
exports.Mt5AdminContentWidget = Mt5AdminContentWidget = Mt5AdminContentWidget_1 = tslib_1.__decorate([
    (0, inversify_1.injectable)()
], Mt5AdminContentWidget);
//# sourceMappingURL=mt5-admin-content-widget.js.map