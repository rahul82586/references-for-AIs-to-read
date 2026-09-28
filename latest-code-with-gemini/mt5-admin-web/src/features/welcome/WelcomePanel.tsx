import * as React from 'react';
import { useSettingsStore } from '../../store/settingsStore';

interface Props {
    close(): void;
}

const QUICK_LINKS: Array<{ id: string; label: string; icon: string }> = [
    { id: 'market-watch', label: 'Market Watch', icon: 'eye' },
    { id: 'groups', label: 'Groups', icon: 'organization' },
    { id: 'orders-deals.orders', label: 'Orders', icon: 'list-ordered' },
    { id: 'symbols', label: 'Symbols', icon: 'symbol-namespace' },
    { id: 'orders-deals.positions', label: 'Positions', icon: 'graph-scatter' },
    { id: 'routing.rules', label: 'Routing', icon: 'git-merge' },
    { id: 'settings', label: 'Connection Settings', icon: 'settings-gear' },
];

/** Start page — VS Code "Welcome" adapted to the admin panel. */
export function WelcomePanel(_props: Props): React.ReactElement {
    const { apiMode } = useSettingsStore();
    const open = (id: string, label: string) => {
        // dispatched through the same command the tree uses
        window.dispatchEvent(new CustomEvent('mt5-admin:open-node', { detail: { id, label } }));
    };

    return (
        <div className="wb-welcome">
            <h1>
                <i className="codicon codicon-symbol-namespace" />
                MT5 Administrator
            </h1>
            <p className="wb-welcome-sub">
                Broker platform admin workbench — standalone, API-driven, zero client-side trading logic.
            </p>
            <span className={`wb-welcome-mode ${apiMode}`}>
                {apiMode === 'live' ? 'LIVE backend' : 'MOCK backend — switch in Settings'}
            </span>
            <div className="wb-welcome-grid">
                {QUICK_LINKS.map((l) => (
                    <button key={l.id} className="wb-welcome-card" onClick={() => open(l.id, l.label)}>
                        <i className={`codicon codicon-${l.icon}`} />
                        {l.label}
                    </button>
                ))}
            </div>
            <p className="wb-welcome-sub" style={{ fontSize: 11 }}>
                Tip: press Ctrl+Shift+P for the command palette · drag tabs to split the workbench
            </p>
        </div>
    );
}
