import * as React from 'react';
import { FloatingWindow } from '../../shared/FloatingWindow';
import { dateTime } from '../../shared/format';

interface Props {
    manager: any;
    onClose: () => void;
    onError: (msg: string, gap?: boolean) => void;
}

type Tab = 'common' | 'permissions' | 'reports' | 'ip';

/** Curated subset of MT5's 128 manager rights, grouped for the checklist. */
const RIGHT_GROUPS: Array<{ group: string; rights: string[] }> = [
    { group: 'Accounts', rights: ['accounts_view', 'accounts_edit', 'accounts_delete', 'manage_technical_accounts'] },
    { group: 'Clients (backoffice)', rights: ['clients_view', 'clients_edit', 'clients_kyc'] },
    { group: 'Trading', rights: ['trade_order_send', 'trade_order_close', 'trade_order_modify', 'trade_deal_modify'] },
    { group: 'Risk & Dealing', rights: ['risk_manage', 'dealing_requote', 'dealing_confirm'] },
    { group: 'Configuration', rights: ['groups_edit', 'symbols_edit', 'routing_edit', 'gateways_edit'] },
    { group: 'Reports & Journal', rights: ['reports_run', 'reports_export', 'journal_view'] },
];

/**
 * Manager dialog — permissions & access (doc §Managers: Common, Permissions,
 * Reports, IP Access List). Writes are backend gaps; the rights model is
 * displayed from the manager record.
 */
export function ManagerModal({ manager, onClose, onError }: Props): React.ReactElement {
    const [tab, setTab] = React.useState<Tab>('common');
    const granted = new Set<string>(manager.rights ?? []);

    const kv = (label: string, value: React.ReactNode) => (
        <div className="ca-kv"><span className="ca-k">{label}</span><span className="ca-v">{value ?? '—'}</span></div>
    );

    return (
        <FloatingWindow width={980} height={600} onClose={onClose}>
            <div className="adm-modal ca-modal ca-modal-xl">
                <div className="adm-modal-header">
                    <i className={`codicon codicon-${manager.role === 'ADMIN' ? 'shield' : 'account'}`} />
                    <span>Manager {manager.login} — {manager.name}</span>
                    <span className="ca-pill info" style={{ marginLeft: 8 }}>{manager.role}</span>
                    <button type="button" className="adm-icon-btn" onClick={onClose}><i className="codicon codicon-close" /></button>
                </div>
                <div className="adm-tabs ca-modal-tabs">
                    {([
                        { id: 'common', label: 'Common', icon: 'settings-gear' },
                        { id: 'permissions', label: 'Permissions', icon: 'lock' },
                        { id: 'reports', label: 'Reports', icon: 'graph' },
                        { id: 'ip', label: 'IP Access List', icon: 'globe' },
                    ] as Array<{ id: Tab; label: string; icon: string }>).map((t) => (
                        <button key={t.id} className={`adm-tab ${tab === t.id ? 'active' : ''}`} onClick={() => setTab(t.id)}>
                            <i className={`codicon codicon-${t.icon}`} /> {t.label}
                        </button>
                    ))}
                </div>
                <div className="adm-modal-body ca-modal-body">
                    {tab === 'common' && (
                        <div className="ca-kv-grid">
                            {kv('Login', <code className="adm-code">{manager.login}</code>)}
                            {kv('Name', manager.name)}
                            {kv('Mailbox name', manager.mailbox || '— (no internal mail)')}
                            {kv('Serviced groups', (manager.group_scope ?? []).join(', '))}
                            {kv('Server', `#${manager.server_id}`)}
                            {kv('2FA', manager.is_2fa_enabled ? 'enabled' : 'disabled')}
                            {kv('Active', manager.is_active ? 'yes' : 'no')}
                            {kv('Last login', dateTime(manager.last_login))}
                        </div>
                    )}
                    {tab === 'permissions' && (
                        <div className="ca-rights-grid">
                            {RIGHT_GROUPS.map((g) => (
                                <div className="ca-rights-group" key={g.group}>
                                    <div className="ca-subtitle">{g.group}</div>
                                    {g.rights.map((r) => (
                                        <label className={`ca-check ca-check-right ${granted.has(r) || granted.has('*') ? 'on' : ''}`} key={r}>
                                            <input type="checkbox" disabled readOnly checked={granted.has(r) || granted.has('*')} />
                                            <code className="adm-code">{r}</code>
                                        </label>
                                    ))}
                                </div>
                            ))}
                            <div className="wb-settings-hint" style={{ gridColumn: '1 / -1' }}>
                                {manager.rights_granted}/{manager.rights_total} rights granted — editing requires the backend manager-write endpoints (gap).
                            </div>
                        </div>
                    )}
                    {tab === 'reports' && (
                        <div className="ca-checks ca-checks-col">
                            <label className="ca-check"><input type="checkbox" readOnly disabled checked={Boolean(manager.reports?.daily)} /> Receive daily reports</label>
                            <label className="ca-check"><input type="checkbox" readOnly disabled checked={Boolean(manager.reports?.monthly)} /> Receive monthly reports</label>
                        </div>
                    )}
                    {tab === 'ip' && (
                        (manager.ip_access ?? []).length === 0
                            ? <div className="ca-dim" style={{ fontSize: 12, padding: 8 }}>No IP restrictions — connections accepted from anywhere.</div>
                            : (
                                <ul className="ca-iplist">
                                    {(manager.ip_access ?? []).map((ip: string) => <li key={ip}><code className="adm-code">{ip}</code></li>)}
                                </ul>
                            )
                    )}
                </div>
                <div className="adm-modal-footer">
                    <span className="ca-dim" style={{ fontSize: 11, marginRight: 'auto' }}>permissions & access are read-only until backend manager-write endpoints exist</span>
                    <button type="button" className="wb-btn secondary" onClick={() => onError('Backend gap: manager write endpoints are not exposed by the API yet.', true)}>
                        <i className="codicon codicon-edit" /> Edit
                    </button>
                    <button type="button" className="wb-btn secondary" onClick={onClose}>Close</button>
                </div>
            </div>
        </FloatingWindow>
    );
}
