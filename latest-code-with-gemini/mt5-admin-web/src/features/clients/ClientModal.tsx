import * as React from 'react';
import { dateTime, money } from './format';

interface Props {
    client: any;
    onClose: () => void;
    onOpenAccount: (login: number) => void;
    onError: (msg: string, gap?: boolean) => void;
}

type Tab = 'general' | 'personal' | 'address' | 'regulation' | 'documents' | 'comments' | 'history' | 'accounts';

const TABS: Array<{ id: Tab; label: string; icon: string }> = [
    { id: 'general', label: 'General', icon: 'info' },
    { id: 'personal', label: 'Personal Data', icon: 'person' },
    { id: 'address', label: 'Address', icon: 'location' },
    { id: 'regulation', label: 'Regulation', icon: 'law' },
    { id: 'documents', label: 'Documents', icon: 'file' },
    { id: 'comments', label: 'Comments', icon: 'comment' },
    { id: 'history', label: 'History', icon: 'history' },
    { id: 'accounts', label: 'Trading Accounts', icon: 'credit-card' },
];

const KYC_PILL: Record<string, string> = { approved: 'ok', pending: 'warn', none: 'off' };

/**
 * Client record — the BACKOFFICE entity (doc §Clients): aggregate person over
 * all their accounts, with KYC, documents, comments and version history.
 * Writes are backend gaps today; the dialog is complete and read-mostly.
 */
export function ClientModal({ client, onClose, onOpenAccount, onError }: Props): React.ReactElement {
    const [tab, setTab] = React.useState<Tab>('general');
    const kv = (label: string, value: React.ReactNode) => (
        <div className="ca-kv"><span className="ca-k">{label}</span><span className="ca-v">{value ?? '—'}</span></div>
    );

    return (
        <div className="adm-modal-overlay" onMouseDown={onClose}>
            <div className="adm-modal ca-modal ca-modal-xl" onMouseDown={(e) => e.stopPropagation()}>
                <div className="adm-modal-header">
                    <i className="codicon codicon-organization" />
                    <span>Client {client.id} — {client.first_name} {client.last_name}</span>
                    <span className={`ca-pill ${KYC_PILL[client.kyc] ?? 'off'}`} style={{ marginLeft: 8 }}>kyc {client.kyc}</span>
                    <button type="button" className="adm-icon-btn" onClick={onClose}><i className="codicon codicon-close" /></button>
                </div>
                <div className="adm-tabs ca-modal-tabs">
                    {TABS.map((t) => (
                        <button key={t.id} className={`adm-tab ${tab === t.id ? 'active' : ''}`} onClick={() => setTab(t.id)}>
                            <i className={`codicon codicon-${t.icon}`} /> {t.label}
                        </button>
                    ))}
                </div>
                <div className="adm-modal-body ca-modal-body">
                    {tab === 'general' && (
                        <div className="ca-kv-grid">
                            {kv('Client ID', <code className="adm-code">{client.id}</code>)}
                            {kv('Status', client.status)}
                            {kv('KYC check', client.kyc)}
                            {kv('Registered', dateTime(client.registered))}
                            {kv('Accounts', (client.accounts ?? []).join(', ') || 'none')}
                            {kv('Total equity', money(client.equity))}
                            {kv('Lead source', client.lead_source)}
                            {kv('Lead campaign', client.lead_campaign)}
                        </div>
                    )}
                    {tab === 'personal' && (
                        <div className="ca-kv-grid">
                            {kv('First name', client.first_name)}
                            {kv('Last name', client.last_name)}
                            {kv('Middle name', client.middle_name)}
                            {kv('Company', client.company)}
                            {kv('ID number', client.id_number)}
                            {kv('Language', client.language)}
                            {kv('E-Mail', client.email)}
                            {kv('Phone', client.phone)}
                        </div>
                    )}
                    {tab === 'address' && (
                        <div className="ca-kv-grid">
                            {kv('Country', client.country)}
                            {kv('State', client.state)}
                            {kv('City', client.city)}
                            {kv('Zip', client.zip)}
                            {kv('Address', client.address)}
                        </div>
                    )}
                    {tab === 'regulation' && (
                        <div className="ca-kv-grid">
                            {kv('Regulation category', client.regulation)}
                            {kv('KYC status', client.kyc)}
                            {kv('Tax residency', client.country)}
                        </div>
                    )}
                    {tab === 'documents' && (
                        <table className="adm-table ca-table ca-mini">
                            <thead>
                                <tr><th>Type</th><th>Number</th><th>Issued</th><th>Expires</th><th>Status</th><th className="num">Versions</th></tr>
                            </thead>
                            <tbody>
                                {(client.documents ?? []).map((d: any) => (
                                    <tr key={d.id}>
                                        <td>{d.type}</td>
                                        <td><code className="adm-code">{d.number}</code></td>
                                        <td className="ca-dim">{d.issued}</td>
                                        <td className="ca-dim">{d.expires}</td>
                                        <td><span className={`ca-pill ${d.status === 'approved' ? 'ok' : 'warn'}`}>{d.status}</span></td>
                                        <td className="num">{d.versions}</td>
                                    </tr>
                                ))}
                                {(client.documents ?? []).length === 0 && (
                                    <tr><td colSpan={6} className="ca-empty">No documents on file</td></tr>
                                )}
                            </tbody>
                        </table>
                    )}
                    {tab === 'comments' && (
                        (client.comments ?? []).length === 0
                            ? <div className="ca-dim" style={{ fontSize: 12, padding: 8 }}>No comments.</div>
                            : (client.comments ?? []).map((c: any, i: number) => (
                                <div className="ca-comment" key={i}>
                                    <span className="ca-dim">{dateTime(c.at)} · manager {c.by}</span>
                                    <div>{c.text}</div>
                                </div>
                            ))
                    )}
                    {tab === 'history' && (
                        <table className="adm-table ca-table ca-mini">
                            <thead><tr><th>When</th><th>By</th><th>Change</th></tr></thead>
                            <tbody>
                                {(client.versions ?? []).map((v: any, i: number) => (
                                    <tr key={i}>
                                        <td className="ca-dim">{dateTime(v.at)}</td>
                                        <td>{v.by}</td>
                                        <td>{v.change}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                    {tab === 'accounts' && (
                        (client.accounts ?? []).length === 0
                            ? <div className="ca-dim" style={{ fontSize: 12, padding: 8 }}>No trading accounts bound to this client.</div>
                            : (
                                <table className="adm-table ca-table ca-mini">
                                    <thead><tr><th>Login</th><th>Group</th><th className="num">Equity</th><th></th></tr></thead>
                                    <tbody>
                                        {(client.accounts ?? []).map((l: number) => (
                                            <tr key={l}>
                                                <td><code className="adm-code">{l}</code></td>
                                                <td className="ca-dim">—</td>
                                                <td className="num">—</td>
                                                <td>
                                                    <button className="ca-linkbtn" onClick={() => onOpenAccount(l)}>open account</button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            )
                    )}
                </div>
                <div className="adm-modal-footer">
                    <span className="ca-dim" style={{ fontSize: 11, marginRight: 'auto' }}>backoffice record — writes are a backend gap today</span>
                    <button type="button" className="wb-btn secondary" onClick={() => onError('Backend gap: client record writes are not exposed by the API yet.', true)}>
                        <i className="codicon codicon-edit" /> Edit Record
                    </button>
                    <button type="button" className="wb-btn secondary" onClick={onClose}>Close</button>
                </div>
            </div>
        </div>
    );
}
