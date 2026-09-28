/**
 * Panel registry — replaces Theia's WidgetFactory + the old content-widget's
 * node→page switch. Every UI surface (sidebar tree, command palette, status
 * bar, layout restore) resolves panels through here and ONLY here.
 *
 * A tree node id resolves to:
 *   { panelId, title, icon, defId, props }
 * - panelId  → the dockview panel instance id (one tab per node, singleton)
 * - defId    → registry key of the component definition (JSON-safe, persisted
 *              in the layout; the component itself is resolved at render time)
 * - props    → JSON-safe component props (e.g. { view: 'history' })
 */
import type * as React from 'react';

export interface PanelDefinition {
    /** stable id used for serialization — must survive reloads */
    id: string;
    title: string;
    icon: string; // codicon name
    component: React.LazyExoticComponent<React.ComponentType<any>> | React.ComponentType<any>;
}

export interface ResolvedPanel {
    panelId: string;
    defId: string;
    title: string;
    icon: string;
    props: Record<string, unknown>;
}

const definitions = new Map<string, PanelDefinition>();

export function registerPanel(def: PanelDefinition): void {
    definitions.set(def.id, def);
}

export function getPanelDefinition(defId: string): PanelDefinition | undefined {
    return definitions.get(defId);
}

export function listPanelDefinitions(): PanelDefinition[] {
    return [...definitions.values()];
}

/* ------------------------------------------------------------------ */
/* tree-node → panel resolution (ported from mt5-admin-content-widget) */
/* ------------------------------------------------------------------ */

const ICONS: Record<string, string> = {
    'start-page': 'home',
    'network-cluster': 'server',
    'network-cluster.servers': 'server-environment',
    'network-cluster.data-centers': 'database',
    'network-cluster.backup': 'save',
    groups: 'organization',
    'clients-and-accounts': 'person',
    'clients-and-accounts.allocations': 'list-selection',
    'clients-and-accounts.clients': 'organization',
    'clients-and-accounts.managers': 'account',
    'clients-and-accounts.trading-accounts': 'credit-card',
    'orders-deals': 'list-ordered',
    'orders-deals.positions': 'graph-scatter',
    'orders-deals.orders': 'list-ordered',
    'orders-deals.deals': 'pulse',
    payments: 'credit-card',
    gateways: 'radio-tower',
    'gateways.list': 'radio-tower',
    'gateways.routing': 'git-merge',
    'data-feeds': 'broadcast',
    'data-feeds.sources': 'database',
    'data-feeds.news': 'rss',
    'market-watch': 'eye',
    plugins: 'extensions',
    reports: 'graph',
    ecn: 'git-network',
    routing: 'git-merge',
    'routing.rules': 'list-ordered',
    'routing.a-book': 'arrow-right',
    'routing.b-book': 'arrow-left',
    'routing.gateways': 'radio-tower',
    symbols: 'symbol-namespace',
    spreads: 'arrow-both',
    settings: 'settings-gear',
    'trade-panel': 'pulse',
};

let tradePanelCounter = 0;

function iconFor(nodeId: string): string {
    return ICONS[nodeId] ?? 'server';
}

/**
 * Resolve a sidebar tree node id to a panel to open.
 * `groups:<path>` / `symbols:<path>` deep links normalize to their master
 * panel with a filter prop (same behaviour as the Theia contribution).
 */
export function resolveTreeNode(rawNodeId: string, label?: string): ResolvedPanel {
    let nodeId = rawNodeId;
    let filterPath = '';
    if (nodeId.startsWith('groups:')) {
        nodeId = 'groups';
        filterPath = rawNodeId.substring('groups:'.length);
    } else if (nodeId.startsWith('symbols:')) {
        nodeId = 'symbols';
        filterPath = rawNodeId.substring('symbols:'.length);
    }

    const props: Record<string, unknown> = {};
    if (filterPath) props.selectedPath = filterPath;

    // Multi-instance support: every time Trade Terminal is opened, generate a unique panel instance
    if (nodeId === 'trade-panel' || nodeId.startsWith('trade-panel')) {
        tradePanelCounter++;
        const uniqueId = `trade-panel-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
        return {
            panelId: uniqueId,
            defId: 'trade-panel',
            title: label && label !== 'trade-panel' ? label : `Trade Terminal #${tradePanelCounter}`,
            icon: 'pulse',
            props: { instanceId: uniqueId },
        };
    }

    let defId = nodeId;
    let title = label ?? nodeId;

    switch (nodeId) {
        /* implemented in F0 */
        case 'market-watch':
            defId = 'market-watch';
            title = label ?? 'Market Watch';
            break;
        case 'groups':
            defId = 'groups';
            title = label ?? 'Groups';
            break;
        case 'settings':
            defId = 'settings';
            title = 'Settings';
            break;
        case 'start-page':
            defId = 'welcome';
            title = label ?? 'Start Page';
            break;

        /* ported in F1 — until then they render the placeholder */
        case 'clients-and-accounts':
        case 'clients-and-accounts.trading-accounts':
            defId = 'clients';
            props.initialTab = 'accounts';
            break;
        case 'clients-and-accounts.clients':
            defId = 'clients';
            props.initialTab = 'clients';
            break;
        case 'clients-and-accounts.managers':
            defId = 'clients';
            props.initialTab = 'managers';
            break;
        case 'clients-and-accounts.allocations':
            defId = 'clients';
            props.initialTab = 'allocations';
            break;
        case 'orders-deals.positions':
            defId = 'positions';
            break;
        case 'orders-deals.orders':
            defId = 'orders';
            break;
        case 'orders-deals.deals':
            defId = 'deals';
            break;
        case 'gateways':
        case 'gateways.list':
            defId = 'gateways';
            props.view = 'list';
            break;
        case 'gateways.routing':
            defId = 'gateways';
            props.view = 'routing';
            break;
        case 'data-feeds':
        case 'data-feeds.sources':
            defId = 'data-feeds';
            props.view = 'sources';
            break;
        case 'data-feeds.news':
            defId = 'data-feeds';
            props.view = 'news';
            break;
        case 'routing':
        case 'routing.rules':
            defId = 'routing';
            props.view = 'all';
            break;
        case 'routing.a-book':
            defId = 'routing';
            props.view = 'a-book';
            break;
        case 'routing.b-book':
            defId = 'routing';
            props.view = 'b-book';
            break;
        case 'routing.gateways':
            defId = 'routing';
            props.view = 'gateways';
            break;
        case 'symbols':
            defId = 'symbols';
            break;
        default:
            defId = 'placeholder';
            props.sectionLabel = label ?? nodeId;
            break;
    }

    if (!definitions.has(defId)) defId = 'placeholder';

    return {
        // one tab per normalized node id — groups:<path> deep links share the
        // single 'groups' tab (filter updates in place), exactly like Theia did
        panelId: normalizePanelId(rawNodeId),
        defId,
        title,
        icon: iconFor(nodeId),
        props,
    };
}

/** Deep-linked group/symbol nodes share the master panel id. */
export function normalizePanelId(rawNodeId: string): string {
    if (rawNodeId.startsWith('groups:')) return 'groups';
    if (rawNodeId.startsWith('symbols:')) return 'symbols';
    if (rawNodeId === 'trade-panel') {
        return `trade-panel-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
    }
    return rawNodeId;
}
