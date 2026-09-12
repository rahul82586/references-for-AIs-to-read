// @ts-nocheck
import * as React from 'react';
import { injectable, postConstruct } from '@theia/core/shared/inversify';
import { ReactWidget } from '@theia/core/lib/browser';

// Network Cluster
import { NetworkClusterOverview, NetworkServersPage, NetworkDataCentersPage, NetworkBackupPage } from './modules/network-cluster/NetworkClusterPage';
// Groups
import { GroupsOverviewPage } from './modules/groups/GroupsPage';
// Clients
import { ClientsPage } from './modules/clients/ClientsPage';
// Positions
import { PositionsPage } from './modules/positions/PositionsPage';
import { SummaryPage } from './modules/positions/SummaryPage';
import { ExposurePage } from './modules/positions/ExposurePage';
import { MarginCallPage } from './modules/positions/MarginCallPage';
// Orders
import { OrdersPage } from './modules/orders/OrdersPage';
// Deals
import { DealsPage } from './modules/deals/DealsPage';
// Gateways
import { GatewaysPage } from './modules/gateways/GatewaysPage';
// Data Feeds
import { DataFeedsPage } from './modules/data-feeds/DataFeedsPage';
// Routing
import { RoutingPage } from './modules/routing/RoutingPage';
// Symbols
import { SymbolsPage } from './modules/symbols/SymbolsPage';
// Market Watch (debug)
import { MarketWatchPage } from './modules/market-watch/MarketWatchPage';

@injectable()
export class Mt5AdminContentWidget extends ReactWidget {

    static createId(nodeId: string): string {
        return `mt5-admin-content:${nodeId}`;
    }

    protected nodeId: string = '';
    protected nodeLabel: string = '';
    protected filterPath: string = '';

    setFilterPath(path: string): void {
        this.filterPath = path;
        this.update();
    }

    initialize(nodeId: string, nodeLabel: string): void {
        this.nodeId = nodeId;
        this.nodeLabel = nodeLabel;
        this.id = Mt5AdminContentWidget.createId(nodeId);
        this.title.label = nodeLabel;
        this.title.caption = nodeLabel;
        this.title.closable = true;
        this.title.iconClass = `codicon codicon-${this.getIconForNode(nodeId)}`;
        this.addClass('mt5-admin-content-widget');
        this.update();
    }

    protected getIconForNode(id: string): string {
        const map: Record<string, string> = {
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

    @postConstruct()
    protected postInit(): void { }

    /**
     * Each node ID maps to a DISTINCT React component / view.
     * Sub-nodes must render different content from their parent.
     */
    protected renderPage(nodeId: string): React.ReactNode {
        switch (nodeId) {
            // ── Network Cluster ──────────────────────────────────────
            case 'network-cluster':           return <NetworkClusterOverview />;
            case 'network-cluster.servers':   return <NetworkServersPage />;
            case 'network-cluster.data-centers': return <NetworkDataCentersPage />;
            case 'network-cluster.backup':    return <NetworkBackupPage />;

            // ── Groups ───────────────────────────────────────────────
            case 'groups':                    return <GroupsOverviewPage selectedPath={this.filterPath} />;

            // ── Clients / Accounts ───────────────────────────────────
            case 'clients-and-accounts':                       return <ClientsPage initialTab="accounts" />;
            case 'clients-and-accounts.allocations':          return <ClientsPage initialTab="allocations" />;
            case 'clients-and-accounts.clients':              return <ClientsPage initialTab="clients" />;
            case 'clients-and-accounts.managers':             return <ClientsPage initialTab="managers" />;
            case 'clients-and-accounts.trading-accounts':      return <ClientsPage initialTab="accounts" />;

            // ── Positions ────────────────────────────────────────────
            case 'positions':                 return <PositionsPage view="open" />;
            case 'positions.open':            return <PositionsPage view="open" />;
            case 'positions.summary':         return <SummaryPage />;
            case 'positions.exposure':        return <ExposurePage />;
            case 'positions.margin-call':     return <MarginCallPage />;
            case 'positions.history':         return <PositionsPage view="history" />;

            // ── Orders ───────────────────────────────────────────────
            case 'orders':                    return <OrdersPage view="active" />;
            case 'orders.active':             return <OrdersPage view="active" />;
            case 'orders.history':            return <OrdersPage view="history" />;
            case 'orders.create':             return <OrdersPage view="new" />;

            // ── Deals ────────────────────────────────────────────────
            case 'deals':                     return <DealsPage view="log" />;
            case 'deals.list':                return <DealsPage view="log" />;
            case 'deals.search':              return <DealsPage view="search" />;

            // ── Gateways ─────────────────────────────────────────────
            case 'gateways':                  return <GatewaysPage view="list" />;
            case 'gateways.list':             return <GatewaysPage view="list" />;
            case 'gateways.routing':          return <GatewaysPage view="routing" />;

            // ── Data Feeds ───────────────────────────────────────────
            case 'data-feeds':                return <DataFeedsPage view="sources" />;
            case 'data-feeds.sources':        return <DataFeedsPage view="sources" />;
            case 'data-feeds.news':           return <DataFeedsPage view="news" />;

            // ── Market Watch (debug) ─────────────────────────────────
            case 'market-watch':              return <MarketWatchPage />;

            // ── Routing ──────────────────────────────────────────────
            case 'routing':                   return <RoutingPage view="all" />;
            case 'routing.rules':             return <RoutingPage view="all" />;
            case 'routing.a-book':            return <RoutingPage view="a-book" />;
            case 'routing.b-book':            return <RoutingPage view="b-book" />;
            case 'routing.gateways':          return <RoutingPage view="gateways" />;

            // ── Symbols ──────────────────────────────────────────────
            case 'symbols':                   return <SymbolsPage selectedPath={this.filterPath} />;

            default: return this.renderPlaceholder(nodeId);
        }
    }

    protected renderPlaceholder(nodeId: string): React.ReactNode {
        return (
            <div className="mt5-admin-section-placeholder">
                <div className="mt5-admin-section-desc">
                    <strong>{this.nodeLabel}</strong> — This section is being implemented.
                </div>
                <div className="mt5-admin-section-wip">
                    <i className="codicon codicon-tools" style={{ marginRight: '8px' }} />
                    Connect to <code>localhost:8000</code> API.
                </div>
            </div>
        );
    }

    protected render(): React.ReactNode {
        return (
            <div className="mt5-admin-content-panel">
                <div className="mt5-admin-content-header">
                    <i className={`codicon codicon-${this.getIconForNode(this.nodeId)} mt5-admin-content-header-icon`} />
                    <h1 className="mt5-admin-content-title">{this.nodeLabel}</h1>
                </div>
                <div className="mt5-admin-content-body" style={{ padding: 0, display: 'flex', flexDirection: 'column', flex: 1, overflow: 'hidden' }}>
                    {this.renderPage(this.nodeId)}
                </div>
            </div>
        );
    }
}
