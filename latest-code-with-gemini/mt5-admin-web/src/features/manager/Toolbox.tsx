import * as React from 'react';
import { API } from '../../services/api';
import { money, dateTime } from '../../shared/format';

type Tab = 'summary' | 'exposure' | 'news' | 'calendar' | 'dealing' | 'alert' | 'search' | 'journal';

const TABS: Array<{ id: Tab; label: string; icon: string }> = [
    { id: 'summary', label: 'Summary', icon: 'list-flat' },
    { id: 'exposure', label: 'Exposure', icon: 'pie-chart' },
    { id: 'news', label: 'News', icon: 'rss' },
    { id: 'calendar', label: 'Calendar', icon: 'calendar' },
    { id: 'dealing', label: 'Dealing', icon: 'briefcase' },
    { id: 'alert', label: 'Alert', icon: 'bell' },
    { id: 'search', label: 'Search', icon: 'search' },
    { id: 'journal', label: 'Journal', icon: 'output' },
];

interface ToolboxProps {
    visible: boolean;
    onToggle: () => void;
    onOpenNode: (nodeId: string, label: string) => void;
}

/**
 * Manager Toolbox — the docked bottom window of the MT5 Manager terminal
 * (operator enumeration): Summary · Exposure · News · Calendar · Dealing ·
 * Alert · Search · Journal.
 *
 * Summary/Exposure implement the doc'd netting semantics display-side:
 * positions of `coverage\*` groups net against client positions per symbol;
 * Net volume = client − coverage; uncovered P/L = P/L of non-coverage legs.
 * All numbers arrive from getPositions/getSymbols — no domain math invented.
 */
export function ManagerToolbox({ visible, onToggle, onOpenNode }: ToolboxProps): React.ReactElement {
    const [tab, setTab] = React.useState<Tab>('summary');
    const [positions, setPositions] = React.useState<any[]>([]);
    const [symbols, setSymbols] = React.useState<any[]>([]);
    const [queue, setQueue] = React.useState<any[]>([]);
    const [news, setNews] = React.useState<any[]>([]);
    const [journal, setJournal] = React.useState<any[]>([]);
    const [accounts, setAccounts] = React.useState<any[]>([]);
    const [q, setQ] = React.useState('');

    React.useEffect(() => {
        if (!visible) return;
        API.getPositions().then(setPositions).catch(() => setPositions([]));
        API.getSymbols().then(setSymbols).catch(() => setSymbols([]));
        API.getDealerQueue().then(setQueue).catch(() => setQueue([]));
        API.getManagerNews().then(setNews).catch(() => setNews([]));
        API.getManagerJournal().then(setJournal).catch(() => setJournal([]));
        API.getAccounts().then(setAccounts).catch(() => setAccounts([]));
    }, [visible, tab]);

    const summary = React.useMemo(() => {
        const bySym = new Map<string, { symbol: string; client: number; coverage: number; pl: number; uncovered: number }>();
        for (const p of positions) {
            const e = bySym.get(p.symbol) ?? { symbol: p.symbol, client: 0, coverage: 0, pl: 0, uncovered: 0 };
            const vol = p.type === 0 ? p.volume : -p.volume;
            const isCov = String(p.group ?? '').toLowerCase().startsWith('coverage');
            if (isCov) e.coverage += vol;
            else { e.client += vol; e.uncovered += p.profit ?? 0; }
            e.pl += p.profit ?? 0;
            bySym.set(p.symbol, e);
        }
        return [...bySym.values()].map((e) => ({ ...e, net: e.client + e.coverage }));
    }, [positions]);

    const exposure = React.useMemo(() => {
        const quote = new Map<string, string>(symbols.map((s: any) => [s.symbol ?? s.name, s.quote_currency ?? s.currency ?? 'USD']));
        const byCur = new Map<string, { currency: string; net: number; pl: number }>();
        for (const row of summary) {
            const cur = quote.get(row.symbol) ?? 'USD';
            const e = byCur.get(cur) ?? { currency: cur, net: 0, pl: 0 };
            e.net += row.net;
            e.pl += row.uncovered;
            byCur.set(cur, e);
        }
        return [...byCur.values()];
    }, [summary, symbols]);

    const alerts = React.useMemo(() => {
        const out: Array<{ icon: string; cls: string; text: string }> = [];
        for (const a of accounts) {
            const lvl = Number(a.margin_level ?? 0);
            if (lvl > 0 && lvl < 300) out.push({ icon: 'warning', cls: 'heat-amber', text: `account ${a.login} margin level ${lvl}%` });
            if (lvl > 0 && lvl < 100) out.push({ icon: 'error', cls: 'heat-red', text: `account ${a.login} below stop-out level` });
        }
        if (queue.length) out.push({ icon: 'inbox', cls: '', text: `${queue.length} request(s) awaiting dealing` });
        return out;
    }, [accounts, queue]);

    const searchHits = React.useMemo(() => {
        const term = q.trim().toLowerCase();
        if (!term) return [];
        const hits: Array<{ kind: string; label: string; node?: string }> = [];
        for (const a of accounts) if (`${a.login} ${a.name} ${a.group}`.toLowerCase().includes(term)) hits.push({ kind: 'account', label: `${a.login} · ${a.name} · ${a.group}`, node: 'manager.accounts' });
        for (const p of positions) if (`${p.position_id} ${p.symbol} ${p.login}`.toLowerCase().includes(term)) hits.push({ kind: 'position', label: `#${p.position_id} · ${p.symbol} · ${p.login}`, node: 'manager.positions' });
        for (const s of symbols) if (String(s.symbol ?? s.name).toLowerCase().includes(term)) hits.push({ kind: 'symbol', label: String(s.symbol ?? s.name), node: 'manager.symbols' });
        return hits.slice(0, 30);
    }, [q, accounts, positions, symbols]);

    if (!visible) {
        return (
            <button className="mg-toolbox-toggle" onClick={onToggle}>
                <i className="codicon codicon-chevron-up" /> Toolbox
            </button>
        );
    }

    return (
        <div className="mg-toolbox">
            <div className="mg-toolbox-head">
                {TABS.map((t) => (
                    <button key={t.id} className={`mg-toolbox-tab ${tab === t.id ? 'active' : ''}`} onClick={() => setTab(t.id)}>
                        <i className={`codicon codicon-${t.icon}`} /> {t.label}
                        {t.id === 'dealing' && queue.length > 0 && <span className="ca-pill warn" style={{ marginLeft: 6 }}>{queue.length}</span>}
                        {t.id === 'alert' && alerts.length > 0 && <span className="ca-pill off" style={{ marginLeft: 6 }}>{alerts.length}</span>}
                    </button>
                ))}
                <button className="adm-icon-btn" style={{ marginLeft: 'auto' }} onClick={onToggle} title="Hide toolbox">
                    <i className="codicon codicon-chevron-down" />
                </button>
            </div>
            <div className="mg-toolbox-body">
                {tab === 'summary' && (
                    <table className="adm-table ca-table ca-mini">
                        <thead><tr><th>Symbol</th><th className="num">Client volume</th><th className="num">Coverage volume</th><th className="num">Net volume</th><th className="num">Uncovered P/L</th><th className="num">Total P/L</th></tr></thead>
                        <tbody>
                            {summary.map((r) => (
                                <tr key={r.symbol}>
                                    <td>{r.symbol}</td>
                                    <td className="num">{r.client.toFixed(2)}</td>
                                    <td className="num">{r.coverage.toFixed(2)}</td>
                                    <td className={`num ${r.net === 0 ? 'heat-green' : 'heat-amber'}`}>{r.net.toFixed(2)}</td>
                                    <td className={`num ${r.uncovered >= 0 ? 'heat-green' : 'heat-red'}`}>{money(r.uncovered)}</td>
                                    <td className="num">{money(r.pl)}</td>
                                </tr>
                            ))}
                            {summary.length === 0 && <tr><td colSpan={6} className="ca-empty">No open positions</td></tr>}
                        </tbody>
                    </table>
                )}
                {tab === 'exposure' && (
                    <table className="adm-table ca-table ca-mini">
                        <thead><tr><th>Currency</th><th className="num">Net volume (lots)</th><th className="num">Uncovered P/L</th></tr></thead>
                        <tbody>
                            {exposure.map((r) => (
                                <tr key={r.currency}>
                                    <td>{r.currency}</td>
                                    <td className={`num ${r.net === 0 ? 'heat-green' : 'heat-amber'}`}>{r.net.toFixed(2)}</td>
                                    <td className={`num ${r.pl >= 0 ? 'heat-green' : 'heat-red'}`}>{money(r.pl)}</td>
                                </tr>
                            ))}
                            {exposure.length === 0 && <tr><td colSpan={3} className="ca-empty">Flat — no net exposure</td></tr>}
                        </tbody>
                    </table>
                )}
                {tab === 'news' && (
                    <div className="mg-list">
                        {news.map((n) => (
                            <div className="mg-list-row" key={n.id}>
                                <span className="ca-dim">{dateTime(n.time)}</span>
                                <b>{n.title}</b>
                                <span className="ca-dim">{n.body}</span>
                            </div>
                        ))}
                        {news.length === 0 && <div className="ca-empty">No news (backend gap in live mode)</div>}
                    </div>
                )}
                {tab === 'calendar' && (
                    <div className="mg-list">
                        <div className="mg-list-row"><span className="ca-dim">session calendar</span> — symbol trade/quote sessions live in Symbols → Sessions tab; holiday calendar is a server configuration (doc §Holidays).</div>
                    </div>
                )}
                {tab === 'dealing' && (
                    <table className="adm-table ca-table ca-mini">
                        <thead><tr><th>Order</th><th>Login</th><th>Symbol</th><th className="num">Volume</th><th>Queued</th><th></th></tr></thead>
                        <tbody>
                            {queue.map((o) => (
                                <tr key={o.ticket}>
                                    <td><code className="adm-code">{o.ticket}</code></td>
                                    <td>{o.login}</td><td>{o.symbol}</td><td className="num">{o.volume}</td>
                                    <td className="ca-dim">{dateTime(o.time_setup)}</td>
                                    <td><button className="ca-linkbtn" onClick={() => onOpenNode('manager.dealing', 'Dealing')}>open dealing desk</button></td>
                                </tr>
                            ))}
                            {queue.length === 0 && <tr><td colSpan={6} className="ca-empty">Queue empty</td></tr>}
                        </tbody>
                    </table>
                )}
                {tab === 'alert' && (
                    <div className="mg-list">
                        {alerts.map((a, i) => (
                            <div className="mg-list-row" key={i}>
                                <i className={`codicon codicon-${a.icon} ${a.cls}`} /> {a.text}
                            </div>
                        ))}
                        {alerts.length === 0 && <div className="ca-empty">No active alerts</div>}
                    </div>
                )}
                {tab === 'search' && (
                    <div className="mg-search">
                        <input className="adm-input" placeholder="search accounts, positions, symbols…" value={q} onChange={(e) => setQ(e.target.value)} autoFocus />
                        <div className="mg-list">
                            {searchHits.map((h, i) => (
                                <div className="mg-list-row" key={i}>
                                    <span className="ca-pill">{h.kind}</span>
                                    {h.node ? (
                                        <button className="ca-linkbtn" onClick={() => onOpenNode(h.node!, h.label)}>{h.label}</button>
                                    ) : (
                                        <span>{h.label}</span>
                                    )}
                                </div>
                            ))}
                            {q && searchHits.length === 0 && <div className="ca-empty">No matches</div>}
                        </div>
                    </div>
                )}
                {tab === 'journal' && (
                    <div className="op-journal">
                        {journal.map((j, i) => (
                            <div className="op-journal-row" key={i}>
                                <span className="ca-dim">{dateTime(j.time)}</span>
                                <span className="op-journal-server">{j.server}</span>
                                <span>{j.message}</span>
                            </div>
                        ))}
                        {journal.length === 0 && <div className="ca-empty">No journal entries (backend gap in live mode)</div>}
                    </div>
                )}
            </div>
        </div>
    );
}
