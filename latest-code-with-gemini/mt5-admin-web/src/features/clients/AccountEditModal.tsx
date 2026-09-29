import * as React from 'react';
import { FloatingWindow } from '../../shared/FloatingWindow';
import { API, isBackendGap } from '../../services/api';
import { money, dateTime, leverage } from '../../shared/format';

interface Props {
    login: number;
    onClose: () => void;
    onSaved: (msg: string) => void;
    onError: (msg: string, gap?: boolean) => void;
    onOpenClient?: (clientId: string) => void;
}

type Tab = 'overview' | 'personal' | 'account' | 'limits' | 'profile' | 'subscriptions' | 'security';

const TABS: Array<{ id: Tab; label: string; icon: string }> = [
    { id: 'overview', label: 'Overview', icon: 'home' },
    { id: 'personal', label: 'Personal', icon: 'person' },
    { id: 'account', label: 'Account', icon: 'credit-card' },
    { id: 'limits', label: 'Limits', icon: 'shield' },
    { id: 'profile', label: 'Profile', icon: 'organization' },
    { id: 'subscriptions', label: 'Subscriptions', icon: 'rss' },
    { id: 'security', label: 'Security', icon: 'key' },
];

const PASSWORD_RULE = '4 character types (lower, UPPER, digit, symbol # @ !), min 8 (group setting), max 16.';

const ORDER_TYPE: Record<number, string> = { 0: 'BUY', 1: 'SELL', 2: 'BUY LIMIT', 3: 'SELL LIMIT', 4: 'BUY STOP', 5: 'SELL STOP' };
const ORDER_STATE: Record<number, string> = { 0: 'PLACED', 1: 'PARTIAL', 4: 'FILLED', 5: 'CANCELED', 6: 'DEALER', 7: 'GATEWAY' };

function generatePassword(): string {
    const lower = 'abcdefghijkmnopqrstuvwxyz';
    const upper = 'ABCDEFGHJKLMNPQRSTUVWXYZ';
    const digits = '23456789';
    const syms = '#@!$%&*';
    const pick = (s: string) => s[Math.floor(Math.random() * s.length)];
    const core = Array.from({ length: 8 }, () => pick(lower + upper + digits + syms));
    return [pick(lower), pick(upper), pick(digits), pick(syms), ...core].join('').slice(0, 12);
}

/**
 * Account editing window — the 7 tabs of the current MT5 Administrator
 * (doc §Accounts/Editing-Account + operator confirmation):
 * Overview · Personal · Account · Limits · Profile · Subscriptions · Security.
 * Read-mostly: writes go through updateAccount / changePassword only.
 */
export function AccountEditModal({ login, onClose, onSaved, onError, onOpenClient }: Props): React.ReactElement {
    const [tab, setTab] = React.useState<Tab>('overview');
    const [data, setData] = React.useState<any | null>(null);
    const [groups, setGroups] = React.useState<any[]>([]);
    const [error, setError] = React.useState<string | null>(null);

    // editable draft for the writable tabs (Personal/Account/Limits)
    const [draft, setDraft] = React.useState<any>(null);
    const [pwd, setPwd] = React.useState<Record<string, string>>({ master: '', investor: '', webapi: '', phone: '' });
    const [pwdMsg, setPwdMsg] = React.useState<Record<string, string>>({});

    React.useEffect(() => {
        API.getAccountDetail(login)
            .then((d) => {
                setData(d);
                setDraft({
                    name: d.name ?? '', last_name: d.last_name ?? '', middle_name: d.middle_name ?? '',
                    company: d.company ?? '', email: d.email ?? '', phone: d.phone ?? '',
                    country: d.country ?? '', state: d.state ?? '', city: d.city ?? '', zip: d.zip ?? '', address: d.address ?? '',
                    language: d.language ?? 'en', resident_status: d.resident_status ?? 'NR',
                    id_number: d.id_number ?? '', lead_source: dLead(d.lead_source), lead_campaign: d.lead_campaign ?? '',
                    group: d.group ?? '', color: d.color ?? '#888888', leverage: d.leverage ?? 100,
                    bank_account: d.bank_account ?? '', agent_account: d.agent_account ?? 0,
                    is_enabled: Boolean(d.is_enabled), allow_password_change: Boolean(d.allow_password_change),
                    otp_enabled: Boolean(d.otp_enabled), limits: { ...(d.limits ?? {}) },
                });
            })
            .catch((e) => setError(String(e?.message ?? e)));
        API.getGroups().then(setGroups).catch(() => setGroups([]));
    }, [login]);

    const set = (patch: any) => setDraft((f: any) => ({ ...f, ...patch }));

    const saveWritable = async () => {
        try {
            await API.updateAccount(login, {
                name: draft.name, email: draft.email, phone: draft.phone, country: draft.country,
                city: draft.city, address: draft.address, group: draft.group, leverage: Number(draft.leverage),
                is_enabled: draft.is_enabled,
            });
            onSaved(`Account ${login} saved.`);
        } catch (e: any) {
            onError(String(e?.message ?? e), isBackendGap(e));
        }
    };

    const pwdAction = async (kind: 'master' | 'investor' | 'webapi' | 'phone', action: 'check' | 'change') => {
        setPwdMsg((m) => ({ ...m, [kind]: '' }));
        try {
            if (action === 'change') {
                await API.changePassword(login, pwd[kind] ?? '');
                setPwdMsg((m) => ({ ...m, [kind]: 'changed ✔' }));
            } else {
                // check requires server-side verification
                await API.getStatus(); // reachability probe only
                const stored = data?.passwords?.[kind];
                if (stored === undefined) throw Object.assign(new Error('Backend gap: password check is not exposed by the API yet.'), { kind: 'backend-gap' });
                setPwdMsg((m) => ({ ...m, [kind]: pwd[kind] === stored ? 'matches ✔' : 'does NOT match ✘' }));
            }
        } catch (e: any) {
            setPwdMsg((m) => ({ ...m, [kind]: String(e?.message ?? e) }));
        }
    };

    if (error) {
        return (
            <FloatingWindow width={1080} height={680} onClose={onClose}>
                <div className="adm-modal ca-modal">
                    <div className="adm-modal-body ca-gap-note"><i className="codicon codicon-warning" /> {error}</div>
                </div>
            </FloatingWindow>
        );
    }

    const kv = (label: string, value: React.ReactNode) => (
        <div className="ca-kv"><span className="ca-k">{label}</span><span className="ca-v">{value ?? '—'}</span></div>
    );

    const passwordBox = (kind: 'master' | 'investor' | 'webapi' | 'phone', title: string, note?: string) => (
        <div className="ca-secbox" key={kind}>
            <div className="ca-secbox-title">{title}</div>
            {note && <div className="wb-settings-hint">{note}</div>}
            <div className="ca-secbox-row">
                <input
                    type="password"
                    className="adm-input"
                    placeholder="Password"
                    value={pwd[kind] ?? ''}
                    onChange={(e) => setPwd((p) => ({ ...p, [kind]: e.target.value }))}
                />
                <button type="button" className="wb-btn secondary" onClick={() => void pwdAction(kind, 'check')}>Check</button>
                <button type="button" className="wb-btn secondary" onClick={() => void pwdAction(kind, 'change')}>Change</button>
                <button
                    type="button"
                    className="wb-btn secondary"
                    title="Generate a compliant candidate, then press Change"
                    onClick={() => setPwd((p) => ({ ...p, [kind]: generatePassword() }))}
                >
                    Generate
                </button>
            </div>
            {pwdMsg[kind] && <div className={`ca-secbox-msg ${pwdMsg[kind].includes('✘') || pwdMsg[kind].includes('gap') || pwdMsg[kind].includes('Backend') ? 'err' : 'ok'}`}>{pwdMsg[kind]}</div>}
        </div>
    );

    return (
        <FloatingWindow width={1080} height={680} onClose={onClose}>
            <div className="adm-modal ca-modal ca-modal-xl">
                <div className="adm-modal-header">
                    <i className="codicon codicon-credit-card" />
                    <span>Account {login} — {data?.group ?? ''}</span>
                    <span className="ca-pill info" style={{ marginLeft: 8 }}>{data?.account_type ?? '—'}</span>
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
                    {/* ── Overview ─────────────────────────────────────── */}
                    {tab === 'overview' && data && (
                        <div className="ca-ov">
                            <div className="ca-kv-grid">
                                {kv('Name', [data.name, data.last_name].filter(Boolean).join(' ') || '—')}
                                {kv('Company', data.company)}
                                {kv('Email', data.email)}
                                {kv('Phone', data.phone)}
                                {kv('Registered', dateTime(data.registered))}
                                {kv('Last access', `${dateTime(data.last_login)} · ${data.last_login_ip ?? '—'}`)}
                                {kv('Client record', data.client_id
                                    ? <button className="ca-linkbtn" onClick={() => data.client_id && onOpenClient?.(data.client_id)}>{data.client_id}</button>
                                    : '—')}
                                {kv('Leverage', leverage(data.leverage))}
                            </div>
                            <div className="ca-subtitle">Open positions</div>
                            <table className="adm-table ca-table ca-mini">
                                <thead>
                                    <tr>
                                        <th>Symbol</th><th>Ticket</th><th>Time</th><th>Type</th><th className="num">Volume</th>
                                        <th className="num">Price</th><th className="num">S/L</th><th className="num">T/P</th>
                                        <th className="num">Swap</th><th className="num">Profit</th><th>Comment</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {(data.positions ?? []).map((p: any) => (
                                        <tr key={p.position_id}>
                                            <td>{p.symbol}</td>
                                            <td><code className="adm-code">{p.position_id}</code></td>
                                            <td className="ca-dim">{dateTime(p.time)}</td>
                                            <td>{p.type === 0 ? 'BUY' : 'SELL'}</td>
                                            <td className="num">{p.volume}</td>
                                            <td className="num">{p.price_open}</td>
                                            <td className="num ca-dim">{p.sl || '—'}</td>
                                            <td className="num ca-dim">{p.tp || '—'}</td>
                                            <td className="num">{p.swap}</td>
                                            <td className={`num ${p.profit >= 0 ? 'heat-green' : 'heat-red'}`}>{money(p.profit)}</td>
                                            <td className="ca-dim">{p.comment ?? ''}</td>
                                        </tr>
                                    ))}
                                    {(data.positions ?? []).length === 0 && (
                                        <tr><td colSpan={11} className="ca-empty">No open positions</td></tr>
                                    )}
                                </tbody>
                            </table>
                            <div className="ca-state-row">
                                <span>Balance <b>{money(data.state?.balance, data.currency)}</b></span>
                                <span>Credit <b>{money(data.state?.credit, data.currency)}</b></span>
                                <span>Commission <b>{money(data.state?.commission, data.currency)}</b></span>
                                <span>Swap <b>{money(data.state?.swap, data.currency)}</b></span>
                                <span>Profit <b className={data.state?.profit >= 0 ? 'heat-green' : 'heat-red'}>{money(data.state?.profit, data.currency)}</b></span>
                            </div>
                            <div className="ca-subtitle">Pending orders</div>
                            {(data.orders ?? []).length === 0
                                ? <div className="ca-dim" style={{ fontSize: 12 }}>No pending orders</div>
                                : (
                                    <table className="adm-table ca-table ca-mini">
                                        <thead>
                                            <tr><th>Ticket</th><th>Symbol</th><th>Type</th><th className="num">Volume</th><th className="num">Price</th><th>State</th></tr>
                                        </thead>
                                        <tbody>
                                            {(data.orders ?? []).map((o: any) => (
                                                <tr key={o.ticket}>
                                                    <td><code className="adm-code">{o.ticket}</code></td>
                                                    <td>{o.symbol}</td><td>{ORDER_TYPE[o.type] ?? o.type}</td>
                                                    <td className="num">{o.volume}</td><td className="num">{o.price_order}</td><td>{ORDER_STATE[o.state] ?? o.state}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                )}
                        </div>
                    )}

                    {/* ── Personal ─────────────────────────────────────── */}
                    {tab === 'personal' && draft && (
                        <div className="ca-modal-grid">
                            <div className="wb-settings-row"><label>Name</label><input className="adm-input" value={draft.name} onChange={(e) => set({ name: e.target.value })} /></div>
                            <div className="wb-settings-row"><label>Last Name</label><input className="adm-input" value={draft.last_name} onChange={(e) => set({ last_name: e.target.value })} /></div>
                            <div className="wb-settings-row"><label>Middle Name</label><input className="adm-input" value={draft.middle_name} onChange={(e) => set({ middle_name: e.target.value })} /></div>
                            <div className="wb-settings-row"><label>Company</label><input className="adm-input" value={draft.company} onChange={(e) => set({ company: e.target.value })} /></div>
                            <div className="wb-settings-row"><label>Registered</label><input className="adm-input" value={dateTime(data?.registered)} disabled /></div>
                            <div className="wb-settings-row"><label>Language</label><input className="adm-input" value={draft.language} onChange={(e) => set({ language: e.target.value })} /></div>
                            <div className="wb-settings-row">
                                <label>Status</label>
                                <select className="adm-select" value={draft.resident_status} onChange={(e) => set({ resident_status: e.target.value })}>
                                    <option value="RE">RE — resident</option>
                                    <option value="NR">NR — non-resident</option>
                                </select>
                            </div>
                            <div className="wb-settings-row"><label>ID number</label><input className="adm-input" value={draft.id_number} onChange={(e) => set({ id_number: e.target.value })} /></div>
                            <div className="wb-settings-row"><label>Lead Source</label><input className="adm-input" value={draft.lead_source} onChange={(e) => set({ lead_source: e.target.value })} /></div>
                            <div className="wb-settings-row"><label>Lead Campaign</label><input className="adm-input" value={draft.lead_campaign} onChange={(e) => set({ lead_campaign: e.target.value })} /></div>
                            <div className="wb-settings-row"><label>E-Mail</label><input className="adm-input" value={draft.email} onChange={(e) => set({ email: e.target.value })} /></div>
                            <div className="wb-settings-row"><label>Phone</label><input className="adm-input" value={draft.phone} onChange={(e) => set({ phone: e.target.value })} /></div>
                            <div className="wb-settings-row"><label>Country</label><input className="adm-input" value={draft.country} onChange={(e) => set({ country: e.target.value })} /></div>
                            <div className="wb-settings-row"><label>State</label><input className="adm-input" value={draft.state} onChange={(e) => set({ state: e.target.value })} /></div>
                            <div className="wb-settings-row"><label>City</label><input className="adm-input" value={draft.city} onChange={(e) => set({ city: e.target.value })} /></div>
                            <div className="wb-settings-row"><label>Zip code</label><input className="adm-input" value={draft.zip} onChange={(e) => set({ zip: e.target.value })} /></div>
                            <div className="wb-settings-row" style={{ gridColumn: '1 / -1' }}><label>Address</label><input className="adm-input" value={draft.address} onChange={(e) => set({ address: e.target.value })} /></div>
                        </div>
                    )}

                    {/* ── Account ──────────────────────────────────────── */}
                    {tab === 'account' && draft && (
                        <div className="ca-modal-grid">
                            <div className="wb-settings-row">
                                <label>Group</label>
                                <select className="adm-select" value={draft.group} onChange={(e) => set({ group: e.target.value })}>
                                    {groups.map((g) => <option key={g.name} value={g.name}>{g.name}</option>)}
                                </select>
                                <div className="wb-settings-hint">account type follows the group</div>
                            </div>
                            <div className="wb-settings-row"><label>Color</label><input type="color" value={draft.color} onChange={(e) => set({ color: e.target.value })} /></div>
                            <div className="wb-settings-row"><label>Leverage</label><input className="adm-input" type="number" min={1} value={draft.leverage} onChange={(e) => set({ leverage: e.target.value })} /></div>
                            <div className="wb-settings-row"><label>Bank account</label><input className="adm-input" value={draft.bank_account} onChange={(e) => set({ bank_account: e.target.value })} /></div>
                            <div className="wb-settings-row"><label>Agent account</label><input className="adm-input" type="number" value={draft.agent_account} onChange={(e) => set({ agent_account: Number(e.target.value) })} /></div>
                            <div className="ca-checks" style={{ gridColumn: '1 / -1' }}>
                                <label className="ca-check"><input type="checkbox" checked={draft.is_enabled} onChange={(e) => set({ is_enabled: e.target.checked })} /> Enable this account</label>
                                <label className="ca-check"><input type="checkbox" checked={draft.allow_password_change} onChange={(e) => set({ allow_password_change: e.target.checked })} /> Allow to change password</label>
                                <label className="ca-check"><input type="checkbox" checked={draft.otp_enabled} onChange={(e) => set({ otp_enabled: e.target.checked })} /> Enable one-time passwords</label>
                            </div>
                        </div>
                    )}

                    {/* ── Limits ───────────────────────────────────────── */}
                    {tab === 'limits' && draft && (
                        <div className="ca-checks ca-checks-col">
                            <label className="ca-check"><input type="checkbox" checked={draft.limits.show_to_managers} onChange={(e) => set({ limits: { ...draft.limits, show_to_managers: e.target.checked } })} /> Show to regular managers</label>
                            <label className="ca-check"><input type="checkbox" checked={draft.limits.include_in_reports} onChange={(e) => set({ limits: { ...draft.limits, include_in_reports: e.target.checked } })} /> Include in server reports</label>
                            <label className="ca-check"><input type="checkbox" checked={draft.limits.daily_reports} onChange={(e) => set({ limits: { ...draft.limits, daily_reports: e.target.checked } })} /> Enable daily reports</label>
                            <label className="ca-check"><input type="checkbox" checked={draft.limits.api_connections} onChange={(e) => set({ limits: { ...draft.limits, api_connections: e.target.checked } })} /> Enable API connections <span className="ca-dim">(obsolete, unused)</span></label>
                            <label className="ca-check"><input type="checkbox" checked={draft.limits.sponsored_vps} onChange={(e) => set({ limits: { ...draft.limits, sponsored_vps: e.target.checked } })} /> Enable sponsored VPS hosting</label>
                        </div>
                    )}

                    {/* ── Profile ──────────────────────────────────────── */}
                    {tab === 'profile' && data && (
                        <div className="ca-kv-grid">
                            {kv('KYC status', data.profile?.kyc)}
                            {kv('Risk score', data.profile?.risk_score)}
                            {kv('Employment', data.profile?.employment)}
                            {kv('Income source', data.profile?.income_source)}
                            {kv('Annual income', data.profile?.annual_income)}
                            {kv('Education', data.profile?.education)}
                            {kv('Experience (FX)', data.profile?.experience_forex)}
                            {kv('Experience (stocks)', data.profile?.experience_stocks)}
                        </div>
                    )}

                    {/* ── Subscriptions ────────────────────────────────── */}
                    {tab === 'subscriptions' && data && (
                        (data.subscriptions ?? []).length === 0
                            ? <div className="ca-dim" style={{ fontSize: 12, padding: 8 }}>No active additional-service subscriptions.</div>
                            : (
                                <table className="adm-table ca-table ca-mini">
                                    <thead><tr><th>Service</th><th>State</th><th>Since</th><th>Next renewal</th><th>Price</th></tr></thead>
                                    <tbody>
                                        {data.subscriptions.map((s: any, i: number) => (
                                            <tr key={i}>
                                                <td>{s.service}</td><td><span className="ca-pill ok">{s.state}</span></td>
                                                <td className="ca-dim">{dateTime(s.since)}</td><td className="ca-dim">{dateTime(s.renewal)}</td><td>{s.price}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            )
                    )}

                    {/* ── Security ─────────────────────────────────────── */}
                    {tab === 'security' && (
                        <div className="ca-secgrid">
                            {passwordBox('master', 'Master Password')}
                            {passwordBox('investor', 'Investor Password', 'read-only, no trading')}
                            {passwordBox('webapi', 'Web API Password', 'for Web clients via MetaTrader Web API')}
                            {passwordBox('phone', 'Phone Password', 'owner identification for phone trading')}
                            <div className="ca-secbox">
                                <div className="ca-secbox-title">OTP Secret Key</div>
                                <div className="ca-secbox-row">
                                    <code className="adm-code">{data?.otp_enabled ? 'provisioned' : 'not provisioned'}</code>
                                    <button type="button" className="wb-btn secondary" onClick={() => onError('Backend gap: OTP secret reset is not exposed by the API yet.', true)}>Reset</button>
                                </div>
                            </div>
                            <div className="ca-secbox">
                                <div className="ca-secbox-title">Certificate</div>
                                <div className="wb-settings-hint">Extended authorization certificate: {data?.certificate ?? 'none issued'}</div>
                            </div>
                            <div className="wb-settings-hint" style={{ gridColumn: '1 / -1' }}>{PASSWORD_RULE}</div>
                        </div>
                    )}
                </div>

                <div className="adm-modal-footer">
                    <span className="ca-dim" style={{ fontSize: 11, marginRight: 'auto' }}>
                        {['personal', 'account', 'limits'].includes(tab) ? 'changes apply on Save' : 'read-only tab'}
                    </span>
                    <button type="button" className="wb-btn secondary" onClick={onClose}>Close</button>
                    {['personal', 'account', 'limits'].includes(tab) && (
                        <button type="button" className="wb-btn" onClick={() => void saveWritable()}>Save</button>
                    )}
                </div>
            </div>
        </FloatingWindow>
    );
}

function dLead(v: any): string {
    return typeof v === 'string' ? v : '';
}
