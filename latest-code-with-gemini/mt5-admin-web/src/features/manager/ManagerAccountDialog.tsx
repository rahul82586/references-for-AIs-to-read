import * as React from 'react';
import { API, isBackendGap } from '../../services/api';
import { money, dateTime, leverage } from '../../shared/format';
import { fmtTime, ORDER_TYPE, ORDER_STATE } from '../../shared/tradeTypes';
import { FloatingWindow } from '../../shared/FloatingWindow';

interface Props {
    login: number;
    onClose: () => void;
    onSaved: () => void;
    onError: (msg: string, gap?: boolean) => void;
}

/**
 * MT5 MANAGER trading-account dialog — the 11 tabs of the Manager terminal
 * (operator-confirmed list):
 * Overview · Exposure · Personal · Account · Limits · Profile · Subscriptions ·
 * Balance · Trade · History · Security
 * (differs from the Administrator's 7-tab window — Balance operations, the
 * Trade desk view and deal History live INSIDE the manager dialog).
 */
export const MANAGER_ACCOUNT_TABS = [
    'Overview', 'Exposure', 'Personal', 'Account', 'Limits', 'Profile',
    'Subscriptions', 'Balance', 'Trade', 'History', 'Security',
] as const;
type TabId = (typeof MANAGER_ACCOUNT_TABS)[number];

const BALANCE_TYPES = ['balance', 'deposit', 'withdrawal', 'credit', 'charge', 'correction', 'bonus', 'commission', 'daily commission', 'monthly commission', 'interest rate'];

function generatePassword(): string {
    const all = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789#@!$%';
    return Array.from({ length: 12 }, () => all[Math.floor(Math.random() * all.length)]).join('');
}

export function ManagerAccountDialog({ login, onClose, onSaved, onError }: Props): React.ReactElement {
    const [tab, setTab] = React.useState<TabId>('Overview');
    const [data, setData] = React.useState<any | null>(null);
    const [deals, setDeals] = React.useState<any[]>([]);
    const [draft, setDraft] = React.useState<any>(null);
    const [balForm, setBalForm] = React.useState({ type: 'balance', amount: '', comment: '' });
    const [pwd, setPwd] = React.useState<Record<string, string>>({ master: '', investor: '', webapi: '', phone: '' });
    const [pwdMsg, setPwdMsg] = React.useState<Record<string, string>>({});

    const isInitial = React.useRef(true);
    const load = React.useCallback(() => {
        API.getAccountDetail(login).then((d) => {
            setData(d);
            if (isInitial.current) {
                isInitial.current = false;
                setDraft({
                    group: d.group, leverage: d.leverage, color: d.color ?? '#888888',
                    bank_account: d.bank_account ?? '', agent_account: d.agent_account ?? 0,
                    is_enabled: Boolean(d.is_enabled), allow_password_change: d.allow_password_change ?? true,
                    otp_enabled: Boolean(d.otp_enabled), limits: { ...(d.limits ?? {}) },
                    name: d.name ?? '', last_name: d.last_name ?? '', middle_name: d.middle_name ?? '',
                    company: d.company ?? '', language: d.language ?? 'en', resident_status: d.resident_status ?? 'NR',
                    id_number: d.id_number ?? '', lead_source: d.lead_source ?? '', lead_campaign: d.lead_campaign ?? '',
                    email: d.email ?? '', phone: d.phone ?? '', country: d.country ?? '', state: d.state ?? '',
                    city: d.city ?? '', zip: d.zip ?? '', address: d.address ?? '',
                });
            }
        }).catch((e) => onError(String(e?.message ?? e)));
        API.getDeals().then((rows) => setDeals(rows.filter((x: any) => x.login === login))).catch(() => setDeals([]));
    }, [login, onError]);

    React.useEffect(() => {
        load();
        const iv = setInterval(load, 2500);
        return () => clearInterval(iv);
    }, [load]);

    const kv = (l: string, v: React.ReactNode) => (
        <div className="ca-kv"><span className="ca-k">{l}</span><span className="ca-v">{v ?? '—'}</span></div>
    );
    const field = (label: string, key: string, extra: any = {}) => (
        <div className="wb-settings-row" key={key}>
            <label>{label}</label>
            <input className="adm-input" value={String(draft?.[key] ?? '')} onChange={(e) => setDraft((d: any) => ({ ...d, [key]: e.target.value }))} {...extra} />
        </div>
    );

    const save = async () => {
        try {
            await API.updateAccount(login, draft);
            onSaved();
            onClose();
        } catch (e: any) {
            onError(String(e?.message ?? e), isBackendGap(e));
        }
    };

    const exposure = React.useMemo(() => {
        const by = new Map<string, { symbol: string; volume: number; pl: number; swap: number }>();
        for (const p of data?.positions ?? []) {
            const e = by.get(p.symbol) ?? { symbol: p.symbol, volume: 0, pl: 0, swap: 0 };
            e.volume += p.type === 0 ? p.volume : -p.volume;
            e.pl += p.profit ?? 0;
            e.swap += p.swap ?? 0;
            by.set(p.symbol, e);
        }
        return [...by.values()];
    }, [data]);

    const totalSwap = React.useMemo(() => {
        return (data?.positions ?? []).reduce((acc: number, p: any) => acc + (Number(p.swap) || 0), 0);
    }, [data?.positions]);

    const totalProfit = React.useMemo(() => {
        if ((data?.positions ?? []).length > 0) {
            return (data.positions ?? []).reduce((acc: number, p: any) => acc + (Number(p.profit) || 0), 0);
        }
        return Number(data?.profit ?? data?.state?.profit ?? 0);
    }, [data?.positions, data?.profit, data?.state?.profit]);

    const balanceOps = deals.filter((d) => BALANCE_TYPES.includes(String(d.type)));

    const pwdBox = (kind: 'master' | 'investor' | 'webapi' | 'phone', title: string) => (
        <div className="ca-secbox" key={kind}>
            <div className="ca-secbox-title">{title}</div>
            <div className="ca-secbox-row">
                <input className="adm-input" type="password" value={pwd[kind]} onChange={(e) => setPwd((p) => ({ ...p, [kind]: e.target.value }))} />
                <button type="button" className="wb-btn secondary" onClick={() => {
                    const stored = data?.passwords?.[kind];
                    if (stored === undefined) { setPwdMsg((m) => ({ ...m, [kind]: 'Backend gap: password check not exposed.' })); return; }
                    setPwdMsg((m) => ({ ...m, [kind]: pwd[kind] === stored ? 'matches ✔' : 'does NOT match ✘' }));
                }}>Check</button>
                <button type="button" className="wb-btn secondary" onClick={async () => {
                    try { await API.changePassword(login, pwd[kind]); setPwdMsg((m) => ({ ...m, [kind]: 'changed ✔' })); }
                    catch (e: any) { setPwdMsg((m) => ({ ...m, [kind]: String(e?.message ?? e) })); }
                }}>Change</button>
                <button type="button" className="wb-btn secondary" onClick={() => setPwd((p) => ({ ...p, [kind]: generatePassword() }))}>Generate</button>
            </div>
            {pwdMsg[kind] && <div className={`ca-secbox-msg ${pwdMsg[kind].includes('✘') || pwdMsg[kind].includes('gap') ? 'err' : 'ok'}`}>{pwdMsg[kind]}</div>}
        </div>
    );

    const miniTable = (cols: string[], body: React.ReactNode) => (
        <table className="adm-table ca-table ca-mini">
            <thead><tr>{cols.map((c, i) => <th key={c + i} className={['Volume', 'Price', 'Swap', 'Profit', 'S/L', 'T/P', 'Current', 'Amount'].includes(c) ? 'num' : ''}>{c}</th>)}</tr></thead>
            <tbody>{body}</tbody>
        </table>
    );

    return (
        <FloatingWindow width={1080} height={680} onClose={onClose}>
            <div className="adm-modal ca-modal" style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
                <div className="adm-modal-header">
                    <i className="codicon codicon-credit-card" />
                    <span>Manager — Account {login}</span>
                    {data && <span className="ca-pill info" style={{ marginLeft: 8 }}>{data.account_type ?? ''} · {data.group}</span>}
                </div>
                <div className="adm-tabs ca-modal-tabs">
                    {MANAGER_ACCOUNT_TABS.map((t) => (
                        <button key={t} className={`adm-tab ${tab === t ? 'active' : ''}`} onClick={() => setTab(t)}>{t}</button>
                    ))}
                </div>
                <div className="adm-modal-body ca-modal-body">
                    {tab === 'Overview' && data && (
                        <>
                            <div className="ca-mt5-overview-header" style={{
                                padding: '10px 14px',
                                background: 'rgba(255, 255, 255, 0.03)',
                                border: '1px solid var(--theia-border, #333)',
                                borderRadius: 4,
                                marginBottom: 12,
                            }}>
                                <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--theia-foreground, #eee)' }}>
                                    {[data.name, data.last_name].filter(Boolean).join(' ') || `Account ${data.login}`}, {data.login}, <code className="adm-code" style={{ fontSize: 13, color: '#3794ff' }}>{data.group}</code>, 1 : {data.leverage ?? 100}
                                </div>
                                <div style={{ fontSize: 12, color: 'var(--theia-descriptionForeground, #aaa)', marginTop: 3 }}>
                                    {data.country || 'United States'}
                                </div>
                                <div style={{ fontSize: 11, color: 'var(--theia-descriptionForeground, #888)', marginTop: 6, display: 'flex', gap: 20, flexWrap: 'wrap' }}>
                                    <span>Registered: <b style={{ color: 'var(--theia-foreground, #ddd)' }}>{data.registered ? dateTime(data.registered) : '—'}</b></span>
                                    <span>Last access: <b style={{ color: 'var(--theia-foreground, #ddd)' }}>{data.last_login ? dateTime(data.last_login) : '—'}</b></span>
                                    <span>Last Address: <b style={{ color: 'var(--theia-foreground, #ddd)' }}>{data.last_ip || '—'}</b></span>
                                    {data.client_id && <span>Client: <b style={{ color: 'var(--theia-foreground, #ddd)' }}>{data.client_id}</b></span>}
                                </div>
                            </div>

                            <div className="ca-subtitle" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
                                <span>Open positions ({(data.positions ?? []).length})</span>
                            </div>
                            <div style={{ maxHeight: 250, overflowY: 'auto', border: '1px solid var(--theia-border, #333)', borderRadius: '4px 4px 0 0' }}>
                                <table className="adm-table ca-table ca-mini" style={{ width: '100%', margin: 0 }}>
                                    <thead>
                                        <tr>
                                            <th>Symbol</th>
                                            <th>Ticket</th>
                                            <th>Type</th>
                                            <th className="num">Volume</th>
                                            <th className="num">Price</th>
                                            <th className="num">S / L</th>
                                            <th className="num">T / P</th>
                                            <th className="num">Price</th>
                                            <th className="num">Swap</th>
                                            <th className="num">Profit</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {(data.positions ?? []).length === 0 ? (
                                            <tr>
                                                <td colSpan={10} style={{ textAlign: 'center', padding: '16px', color: 'var(--theia-descriptionForeground)' }}>
                                                    No open positions
                                                </td>
                                            </tr>
                                        ) : (
                                            (data.positions ?? []).map((p: any) => (
                                                <tr key={p.position_id || p.ticket}>
                                                    <td>
                                                        <i className="codicon codicon-graph" style={{ marginRight: 6, color: '#0078d4', fontSize: 12 }} />
                                                        <b>{p.symbol}</b>
                                                    </td>
                                                    <td><code className="adm-code">{p.position_id || p.ticket}</code></td>
                                                    <td>
                                                        <span className={p.type === 0 || String(p.action).toLowerCase() === 'buy' ? 'ca-pill ok' : 'ca-pill danger'} style={{ textTransform: 'uppercase', fontSize: 10, padding: '1px 6px' }}>
                                                            {p.type === 0 || String(p.action).toLowerCase() === 'buy' ? 'buy' : 'sell'}
                                                        </span>
                                                    </td>
                                                    <td className="num font-mono">{Number(p.volume).toFixed(2)}</td>
                                                    <td className="num font-mono">{Number(p.price_open).toFixed(data.currency_digits ?? 2)}</td>
                                                    <td className="num ca-dim font-mono">{p.sl ? Number(p.sl).toFixed(data.currency_digits ?? 2) : '0.000'}</td>
                                                    <td className="num ca-dim font-mono">{p.tp ? Number(p.tp).toFixed(data.currency_digits ?? 2) : '0.000'}</td>
                                                    <td className="num font-mono">{Number(p.price_current || p.price_open).toFixed(data.currency_digits ?? 2)}</td>
                                                    <td className="num font-mono">{Number(p.swap || 0).toFixed(2)}</td>
                                                    <td className={`num font-mono ${(p.profit ?? 0) >= 0 ? 'heat-green' : 'heat-red'}`} style={{ fontWeight: 600 }}>
                                                        {money(p.profit, data.currency)}
                                                    </td>
                                                </tr>
                                            ))
                                        )}
                                    </tbody>
                                </table>
                            </div>

                            {/* MT5 Blue Highlight Summary Bar */}
                            <div className="ca-mt5-summary-row" style={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'space-between',
                                background: '#0078d4',
                                color: '#ffffff',
                                padding: '8px 14px',
                                borderRadius: '0 0 4px 4px',
                                fontSize: 12,
                                fontWeight: 500,
                                boxShadow: '0 2px 4px rgba(0,0,0,0.25)',
                            }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 14, flexWrap: 'wrap' }}>
                                    <span style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: 14, height: 14, borderRadius: '50%', border: '1.5px solid #fff', fontSize: 11, lineHeight: 1, fontWeight: 'bold' }}>−</span>
                                    <span>Balance: <b>{money(data.balance ?? data.state?.balance, data.currency)}</b></span>
                                    <span>Equity: <b>{money(data.equity ?? data.state?.equity, data.currency)}</b></span>
                                    <span>Margin: <b>{money(data.margin ?? data.state?.margin, data.currency)}</b></span>
                                    <span>Free Margin: <b>{money(data.margin_free ?? data.state?.margin_free, data.currency)}</b></span>
                                    <span>Margin Level: <b>{data.margin_level ? `${Number(data.margin_level).toFixed(2)} %` : (data.state?.margin_level ? `${Number(data.state.margin_level).toFixed(2)} %` : '—')}</b></span>
                                </div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
                                    <span>Swap: <b>{money(totalSwap, data.currency)}</b></span>
                                    <span>Profit: <b style={{ color: totalProfit >= 0 ? '#b8ffd0' : '#ffb8b8' }}>{money(totalProfit, data.currency)}</b></span>
                                </div>
                            </div>
                        </>
                    )}

                    {tab === 'Exposure' && miniTable(['Symbol', 'Volume', 'Swap', 'Profit'],
                        exposure.map((r) => (
                            <tr key={r.symbol}>
                                <td>{r.symbol}</td>
                                <td className={`num ${r.volume === 0 ? 'heat-green' : 'heat-amber'}`}>{r.volume.toFixed(2)}</td>
                                <td className="num">{r.swap}</td>
                                <td className={`num ${r.pl >= 0 ? 'heat-green' : 'heat-red'}`}>{money(r.pl)}</td>
                            </tr>
                        )))}

                    {tab === 'Personal' && draft && (
                        <div className="ca-modal-grid">
                            {field('Name', 'name')}{field('Last Name', 'last_name')}{field('Middle Name', 'middle_name')}
                            {field('Company', 'company')}
                            <div className="wb-settings-row"><label>Registered</label><input className="adm-input" value={dateTime(data?.registered)} readOnly /></div>
                            {field('Language', 'language')}
                            <div className="wb-settings-row"><label>Status</label>
                                <select className="adm-select" value={draft.resident_status} onChange={(e) => setDraft((d: any) => ({ ...d, resident_status: e.target.value }))}>
                                    <option value="RE">RE — resident</option><option value="NR">NR — non-resident</option>
                                </select>
                            </div>
                            {field('ID number', 'id_number')}{field('Lead Source', 'lead_source')}{field('Lead Campaign', 'lead_campaign')}
                            {field('E-Mail', 'email')}{field('Phone', 'phone')}{field('Country', 'country')}
                            {field('State', 'state')}{field('City', 'city')}{field('Zip code', 'zip')}
                            <div className="wb-settings-row" style={{ gridColumn: '1 / -1' }}>{field('Address', 'address')}</div>
                        </div>
                    )}

                    {tab === 'Account' && draft && (
                        <div className="ca-modal-grid">
                            {field('Group', 'group', { readOnly: true })}
                            <div className="wb-settings-row"><label>Color</label><input type="color" value={draft.color} onChange={(e) => setDraft((d: any) => ({ ...d, color: e.target.value }))} /></div>
                            {field('Leverage', 'leverage', { type: 'number' })}
                            {field('Bank account', 'bank_account')}
                            {field('Agent account', 'agent_account', { type: 'number' })}
                            <div className="ca-checks" style={{ gridColumn: '1 / -1' }}>
                                <label className="ca-check"><input type="checkbox" checked={draft.is_enabled} onChange={(e) => setDraft((d: any) => ({ ...d, is_enabled: e.target.checked }))} /> Enable this account</label>
                                <label className="ca-check"><input type="checkbox" checked={draft.allow_password_change} onChange={(e) => setDraft((d: any) => ({ ...d, allow_password_change: e.target.checked }))} /> Allow to change password</label>
                                <label className="ca-check"><input type="checkbox" checked={draft.otp_enabled} onChange={(e) => setDraft((d: any) => ({ ...d, otp_enabled: e.target.checked }))} /> Enable one-time passwords</label>
                            </div>
                        </div>
                    )}

                    {tab === 'Limits' && draft && (
                        <div className="ca-checks ca-checks-col">
                            {['show_to_managers|Show to regular managers', 'include_in_reports|Include in server reports', 'daily_reports|Enable daily reports', 'api_connections|Enable API connections (obsolete)', 'sponsored_vps|Enable sponsored VPS hosting'].map((s) => {
                                const [k, l] = s.split('|');
                                return (
                                    <label className="ca-check" key={k}>
                                        <input type="checkbox" checked={Boolean(draft.limits?.[k])} onChange={(e) => setDraft((d: any) => ({ ...d, limits: { ...d.limits, [k]: e.target.checked } }))} /> {l}
                                    </label>
                                );
                            })}
                        </div>
                    )}

                    {tab === 'Profile' && data && (
                        <div className="ca-kv-grid">
                            {kv('KYC status', data.profile?.kyc)}{kv('Risk score', data.profile?.risk_score)}
                            {kv('Employment', data.profile?.employment)}{kv('Income source', data.profile?.income_source)}
                            {kv('Annual income', data.profile?.annual_income)}{kv('Education', data.profile?.education)}
                            {kv('Experience (FX)', data.profile?.experience_forex)}{kv('Experience (stocks)', data.profile?.experience_stocks)}
                        </div>
                    )}

                    {tab === 'Subscriptions' && data && (
                        (data.subscriptions ?? []).length === 0
                            ? <div className="ca-dim" style={{ fontSize: 12, padding: 8 }}>No active additional-service subscriptions.</div>
                            : miniTable(['Service', 'State', 'Since', 'Renewal', 'Price'],
                                data.subscriptions.map((s: any, i: number) => (
                                    <tr key={i}><td>{s.service}</td><td><span className="ca-pill ok">{s.state}</span></td>
                                        <td className="ca-dim">{dateTime(s.since)}</td><td className="ca-dim">{dateTime(s.renewal)}</td><td>{s.price}</td></tr>
                                )))
                    )}

                    {tab === 'Balance' && (
                        <>
                            <div className="ca-toolbar" style={{ borderBottom: 'none', padding: '8px 0', display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
                                <select className="adm-select" style={{ height: 28, minWidth: 140 }} value={balForm.type} onChange={(e) => setBalForm({ ...balForm, type: e.target.value })}>
                                    <option value="balance">Deposit (Balance)</option>
                                    <option value="withdrawal">Withdrawal</option>
                                    <option value="credit">Credit</option>
                                    <option value="charge">Charge</option>
                                    <option value="bonus">Bonus</option>
                                    <option value="correction">Correction</option>
                                </select>
                                <input className="adm-input" style={{ width: 130, height: 28 }} type="number" placeholder="Amount" value={balForm.amount} onChange={(e) => setBalForm({ ...balForm, amount: e.target.value })} />
                                <input className="adm-input" style={{ width: 220, height: 28 }} placeholder="Comment (optional)" value={balForm.comment} onChange={(e) => setBalForm({ ...balForm, comment: e.target.value })} />
                                
                                <button
                                    className="wb-btn"
                                    style={{ background: '#0078d4', color: '#fff', display: 'flex', alignItems: 'center', gap: 4 }}
                                    onClick={async () => {
                                        const amt = Number(balForm.amount);
                                        if (!amt) { onError('Amount is required.'); return; }
                                        try {
                                            const op = balForm.type === 'withdrawal' ? 'balance' : (balForm.type || 'balance');
                                            await API.balanceOperation(login, op, Math.abs(amt), balForm.comment || 'Manager deposit');
                                            setBalForm({ type: 'balance', amount: '', comment: '' });
                                            load(); onSaved();
                                        } catch (e: any) { onError(String(e?.message ?? e), isBackendGap(e)); }
                                    }}
                                >
                                    <i className="codicon codicon-arrow-down" /> Deposit
                                </button>

                                <button
                                    className="wb-btn secondary"
                                    style={{ color: '#ff6b6b', borderColor: 'rgba(255, 107, 107, 0.4)', display: 'flex', alignItems: 'center', gap: 4 }}
                                    onClick={async () => {
                                        const amt = Number(balForm.amount);
                                        if (!amt) { onError('Amount is required.'); return; }
                                        try {
                                            await API.balanceOperation(login, 'withdrawal', Math.abs(amt), balForm.comment || 'Manager withdrawal');
                                            setBalForm({ type: 'balance', amount: '', comment: '' });
                                            load(); onSaved();
                                        } catch (e: any) { onError(String(e?.message ?? e), isBackendGap(e)); }
                                    }}
                                >
                                    <i className="codicon codicon-arrow-up" /> Withdraw
                                </button>

                                {['credit', 'charge', 'bonus', 'correction'].includes(balForm.type) && (
                                    <button
                                        className="wb-btn secondary"
                                        onClick={async () => {
                                            const amt = Number(balForm.amount);
                                            if (!amt) { onError('Amount is required.'); return; }
                                            try {
                                                await API.balanceOperation(login, balForm.type, Math.abs(amt), balForm.comment || `Manager ${balForm.type}`);
                                                setBalForm({ type: 'balance', amount: '', comment: '' });
                                                load(); onSaved();
                                            } catch (e: any) { onError(String(e?.message ?? e), isBackendGap(e)); }
                                        }}
                                    >
                                        Apply {balForm.type.toUpperCase()}
                                    </button>
                                )}
                            </div>
                            {miniTable(['Time', 'Deal', 'Type', 'Amount', 'Comment'],
                                balanceOps.map((d) => (
                                    <tr key={d.deal_id}>
                                        <td className="ca-dim">{fmtTime(d.time)}</td>
                                        <td><code className="adm-code">{d.deal_id}</code></td>
                                        <td>{d.type}</td>
                                        <td className={`num ${d.profit >= 0 ? 'heat-green' : 'heat-red'}`}>{money(d.profit)}</td>
                                        <td className="ca-dim">{d.comment}</td>
                                    </tr>
                                )))}
                        </>
                    )}

                    {tab === 'Trade' && (
                        <>
                            <div className="wb-settings-hint" style={{ padding: '4px 0 8px' }}>
                                Dealer actions on this account (OrderSend / OrderClose / PositionModify) run through the
                                Manager session — connect on <b>Navigator → Server</b> first.
                            </div>
                            <div className="ca-subtitle">Positions</div>
                            {miniTable(['Symbol', 'Ticket', 'Type', 'Volume', 'Price', 'Current', 'Swap', 'Profit'],
                                (data?.positions ?? []).map((p: any) => (
                                    <tr key={p.position_id}>
                                        <td>{p.symbol}</td><td><code className="adm-code">{p.position_id}</code></td>
                                        <td>{p.type === 0 ? 'buy' : 'sell'}</td><td className="num">{p.volume}</td>
                                        <td className="num">{p.price_open}</td><td className="num">{p.price_current}</td>
                                        <td className="num">{p.swap}</td>
                                        <td className={`num ${p.profit >= 0 ? 'heat-green' : 'heat-red'}`}>{money(p.profit)}</td>
                                    </tr>
                                )))}
                            <div className="ca-subtitle">Pending orders</div>
                            {miniTable(['Ticket', 'Symbol', 'Type', 'Volume', 'Price', 'State', 'Setup'],
                                (data?.orders ?? []).map((o: any) => (
                                    <tr key={o.ticket}>
                                        <td><code className="adm-code">{o.ticket}</code></td><td>{o.symbol}</td>
                                        <td>{ORDER_TYPE[o.type] ?? o.type}</td><td className="num">{o.volume}</td>
                                        <td className="num">{o.price_order || 'market'}</td>
                                        <td>{ORDER_STATE[o.state] ?? o.state}</td><td className="ca-dim">{fmtTime(o.time_setup)}</td>
                                    </tr>
                                )))}
                        </>
                    )}

                    {tab === 'History' && miniTable(['Time', 'Deal', 'Order', 'Symbol', 'Action', 'Type', 'Volume', 'Price', 'Profit', 'Swap', 'Commission', 'Comment'],
                        deals.map((d) => (
                            <tr key={d.deal_id}>
                                <td className="ca-dim">{fmtTime(d.time)}</td>
                                <td><code className="adm-code">{d.deal_id}</code></td>
                                <td className="ca-dim">{d.order || '—'}</td>
                                <td>{d.symbol || '—'}</td>
                                <td><span className="ca-pill">{d.action}</span></td>
                                <td>{d.type}</td>
                                <td className="num">{d.volume || ''}</td>
                                <td className="num">{d.price || ''}</td>
                                <td className={`num ${d.profit > 0 ? 'heat-green' : d.profit < 0 ? 'heat-red' : ''}`}>{d.profit ? money(d.profit) : ''}</td>
                                <td className="num">{d.swap || ''}</td>
                                <td className="num">{d.commission ? money(d.commission) : ''}</td>
                                <td className="ca-dim">{d.comment}</td>
                            </tr>
                        )))}

                    {tab === 'Security' && (
                        <div className="ca-secgrid">
                            {pwdBox('master', 'Master Password')}
                            {pwdBox('investor', 'Investor Password')}
                            {pwdBox('webapi', 'Web API Password')}
                            {pwdBox('phone', 'Phone Password')}
                            <div className="ca-secbox">
                                <div className="ca-secbox-title">OTP Secret Key</div>
                                <div className="ca-secbox-row">
                                    <code className="adm-code">{data?.otp_enabled ? 'provisioned' : 'not provisioned'}</code>
                                    <button type="button" className="wb-btn secondary" onClick={() => onError('Backend gap: OTP secret reset is not exposed by the API yet.', true)}>Reset</button>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
                <div className="adm-modal-footer" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <button type="button" className="wb-btn secondary" onClick={() => onSaved()}>
                            New Client...
                        </button>
                        {['Personal', 'Account', 'Limits'].includes(tab) && (
                            <span className="ca-dim" style={{ fontSize: 11 }}>changes apply on Update</span>
                        )}
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <button type="button" className="wb-btn" onClick={() => void save()}>Update</button>
                        <button type="button" className="wb-btn secondary" onClick={onClose}>Cancel</button>
                        <button type="button" className="wb-btn secondary" onClick={() => alert('MetaTrader 5 Manager Account Details.\nChanges on Personal, Account and Limits tabs take effect on Update.')}>Help</button>
                    </div>
                </div>
            </div>
        </FloatingWindow>
    );
}
