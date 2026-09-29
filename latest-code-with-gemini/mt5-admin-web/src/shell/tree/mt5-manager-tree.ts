/**
 * MT5 Manager navigator — structure per operator enumeration of the real
 * Manager terminal: Market Watch · Navigator (Server, Analytics, Server &
 * Reports, Clients and Orders [Online users, Clients, Trading accounts,
 * Positions, Orders], Subscriptions, Dealing, Groups, Plugins, Mailbox,
 * Support center) · Toolbox · Margin calls · Queue.
 *
 * `panel` names the registry definition; `api` documents the Manager API
 * family (MT5APIManager.h / MT5-Manager-REST-API.md) that backs the node.
 */
export interface ManagerTreeNode {
    id: string;
    label: string;
    icon?: string;
    panel?: string;
    api?: string;
    children?: ManagerTreeNode[];
}

export const MT5_MANAGER_TREE: ManagerTreeNode[] = [
    { id: 'manager.market-watch', label: 'Market Watch', icon: 'eye', panel: 'market-watch', api: 'OnQuote/OnTick/OnMarketWatch (WS)' },
    {
        id: 'manager.server', label: 'Server', icon: 'server', panel: 'manager-server',
        api: 'Ping/Version/MemoryUsage/StartTimeUtc/ServerTime · Connect/IsConnected',
    },
    { id: 'manager.analytics', label: 'Analytics', icon: 'graph-line', api: 'OnOrderProfit/OnOrderProfitInterval(Ex)/OnTickStat' },
    { id: 'manager.server-reports', label: 'Server & Reports', icon: 'graph', api: 'DailyRequest* family (13 report endpoints)' },
    {
        id: 'manager.clients-orders', label: 'Clients and Orders', icon: 'folder',
        children: [
            { id: 'manager.online', label: 'Online Users', icon: 'pulse', panel: 'manager-online', api: 'PUMP_MODE_ACTIVITY · OnConnectDisconnect' },
            { id: 'manager.clients', label: 'Clients', icon: 'organization', panel: 'clients', api: 'PUMP_MODE_CLIENTS' },
            { id: 'manager.accounts', label: 'Trading Accounts', icon: 'credit-card', panel: 'manager-accounts', api: 'UserGet/UserUpdate/UserPasswordCheck… (11-tab dialog)' },
            { id: 'manager.positions', label: 'Positions', icon: 'graph-scatter', panel: 'positions', api: 'PositionGet/PositionHistoryGet · OnPositionUpdate' },
            { id: 'manager.orders', label: 'Orders', icon: 'list-ordered', panel: 'orders', api: 'OrderGet/OrderHistoryGet · OnOrderUpdate' },
        ],
    },
    { id: 'manager.subscriptions', label: 'Subscriptions', icon: 'bell', api: 'Subscriptions section (11 endpoints) · ws/subscriptions' },
    { id: 'manager.dealing', label: 'Dealing', icon: 'briefcase', panel: 'manager-queue', api: 'dealer queue: PENDING_DEALER orders → confirm/reject/requote' },
    { id: 'manager.groups', label: 'Groups', icon: 'organization', panel: 'groups', api: 'GroupGet/GroupNext (manager-scoped)' },
    { id: 'manager.plugins', label: 'Plugins', icon: 'extensions', api: 'PUMP_MODE_PLUGINS' },
    { id: 'manager.mailbox', label: 'Mailbox', icon: 'mail', api: 'MailSend/MailGet (PUMP_MODE_MAIL)' },
    { id: 'manager.support', label: 'Support Center', icon: 'question', api: '—' },
    { id: 'manager.margin-calls', label: 'Margin Calls', icon: 'warning', panel: 'manager-margin-calls', api: 'margin call/stop-out monitoring window' },
    { id: 'manager.queue', label: 'Queue', icon: 'inbox', panel: 'manager-queue', api: 'OnRequesUpdate — dealer request queue' },
];

export function findManagerNode(nodes: ManagerTreeNode[], id: string): ManagerTreeNode | null {
    for (const n of nodes) {
        if (n.id === id) return n;
        if (n.children) {
            const hit = findManagerNode(n.children, id);
            if (hit) return hit;
        }
    }
    return null;
}
