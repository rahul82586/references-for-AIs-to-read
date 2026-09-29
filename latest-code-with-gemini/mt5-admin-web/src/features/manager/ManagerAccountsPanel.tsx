import * as React from 'react';
import { API } from '../../services/api';
import { AccountsTable } from '../../shared/AccountsTable';
import { ManagerAccountDialog } from './ManagerAccountDialog';

/**
 * Manager → Clients and Orders → Trading Accounts.
 * Same table component as the Administrator section (one app, shared UI kit);
 * double-click opens the MANAGER account dialog — 11 tabs, per operator:
 * the Manager terminal's dialog differs from the Administrator's 7-tab one.
 */
export function ManagerAccountsPanel(): React.ReactElement {
    const [rows, setRows] = React.useState<any[]>([]);
    const [selected, setSelected] = React.useState<number[]>([]);
    const [editLogin, setEditLogin] = React.useState<number | null>(null);
    const [error, setError] = React.useState<string | null>(null);

    const load = React.useCallback(() => {
        API.getAccounts().then(setRows).catch((e) => setError(String(e?.message ?? e)));
    }, []);
    React.useEffect(load, [load]);

    return (
        <div className="ca-page">
            <div className="ca-toolbar">
                <div className="ca-request">
                    <i className="codicon codicon-credit-card" />
                    <span style={{ fontSize: 12 }}>Trading accounts — manager-scoped view (type follows the group)</span>
                </div>
                <button className="wb-btn secondary" onClick={load}><i className="codicon codicon-refresh" /> Request</button>
            </div>
            {error && <div className="ca-banner gap"><i className="codicon codicon-warning" /><span>{error}</span></div>}
            <div className="ca-main">
                <AccountsTable
                    rows={rows}
                    selected={selected}
                    onSelect={(ls, e) => setSelected(e.ctrlKey || e.metaKey ? (selected.includes(ls[0]) ? selected.filter((x) => x !== ls[0]) : [...selected, ...ls]) : ls)}
                    onOpen={(l) => setEditLogin(l)}
                    onContext={() => undefined}
                />
            </div>
            {editLogin !== null && (
                <ManagerAccountDialog
                    login={editLogin}
                    onClose={() => setEditLogin(null)}
                    onSaved={load}
                    onError={(m, gap) => setError(gap ? `Backend gap: ${m}` : m)}
                />
            )}
        </div>
    );
}
