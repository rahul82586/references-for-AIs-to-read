// @ts-nocheck
import * as React from 'react';
import { API } from '../api';

interface Position {
    ticket: number;
    login: number;
    symbol: string;
    action: number; // 0 = Buy, 1 = Sell
    volume: number;
    price_open: number;
    price_current?: number;
    price?: number; // for deals
    price_sl: number;
    price_tp: number;
    profit: number;
    storage: number; // swap
    time_create?: string;
    timestamp?: string; // for deals
    entry?: number; // for deals (0 = In, 1 = Out, 2 = In/Out)
}

interface Props { view: 'open' | 'history'; }

export function PositionsPage({ view }: Props): React.ReactElement {
    const [positions, setPositions] = React.useState<Position[]>([]);
    const [sel, setSel] = React.useState<number | null>(null);
    const [filter, setFilter] = React.useState('');
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState<string | null>(null);

    const loadData = async () => {
        setLoading(true);
        setError(null);
        try {
            if (view === 'open') {
                const data = await API.getPositions();
                setPositions(data);
            } else {
                // For history, list deals
                const data = await API.getDeals();
                setPositions(data);
            }
        } catch (err: any) {
            setError(err.message || 'Failed to fetch positions/deals.');
        } finally {
            setLoading(false);
        }
    };

    React.useEffect(() => {
        loadData();
    }, [view]);

    const filtered = positions.filter(p =>
        String(p.login).includes(filter) ||
        p.symbol.toLowerCase().includes(filter.toLowerCase()) ||
        String(p.ticket).includes(filter)
    );
    const totalProfit = filtered.reduce((s, p) => s + (p.profit || 0), 0);

    return (
        <div className="adm-page">
            <div className="adm-toolbar">
                <button className="adm-btn" onClick={loadData} title="Reload data">
                    <i className="codicon codicon-refresh" /> Refresh
                </button>
                <div className="adm-toolbar-sep" />
                <div className="adm-search-wrap">
                    <i className="codicon codicon-search" />
                    <input className="adm-search" placeholder="Filter by login, symbol, ticket..." value={filter} onChange={e => setFilter(e.target.value)} />
                </div>
            </div>

            {error && (
                <div className="adm-hint" style={{ background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)' }}>
                    <i className="codicon codicon-error" /> {error}
                </div>
            )}

            <div className="adm-table-wrap">
                {loading ? (
                    <div style={{ padding: 20, textAlign: 'center', opacity: 0.7 }}>Loading data...</div>
                ) : filtered.length === 0 ? (
                    <div style={{ padding: 20, textAlign: 'center', opacity: 0.7 }}>No records found.</div>
                ) : (
                    <table className="adm-table">
                        <thead>
                            {view === 'open' ? (
                                <tr>
                                    <th>Ticket</th><th>Login</th><th>Symbol</th><th>Type</th>
                                    <th>Volume</th><th>Open Price</th><th>Current Price</th>
                                    <th>S/L</th><th>T/P</th><th>Float Profit</th><th>Swap</th>
                                    <th>Open Time</th>
                                </tr>
                            ) : (
                                <tr>
                                    <th>Ticket</th><th>Order Ticket</th><th>Login</th><th>Symbol</th><th>Action</th><th>Entry</th>
                                    <th>Volume</th><th>Execution Price</th><th>Realized Profit</th><th>Swap</th><th>Commission</th>
                                    <th>Timestamp</th>
                                </tr>
                            )}
                        </thead>
                        <tbody>
                            {filtered.map(p => {
                                const isBuy = p.action === 0;
                                const typeStr = isBuy ? 'BUY' : 'SELL';
                                const ticketId = p.ticket;

                                if (view === 'open') {
                                    return (
                                        <tr key={ticketId} className={sel === ticketId ? 'selected' : ''} onClick={() => setSel(ticketId)}>
                                            <td><strong>{p.ticket}</strong></td>
                                            <td>{p.login}</td>
                                            <td><strong>{p.symbol}</strong></td>
                                            <td><span className={`adm-side-badge ${typeStr.toLowerCase()}`}>{typeStr}</span></td>
                                            <td>{(p.volume || 0).toFixed(2)}</td>
                                            <td className="adm-num">{(p.price_open || 0).toFixed(5)}</td>
                                            <td className="adm-num">{(p.price_current || 0).toFixed(5)}</td>
                                            <td className="adm-num">{p.price_sl || '—'}</td>
                                            <td className="adm-num">{p.price_tp || '—'}</td>
                                            <td className={`adm-num ${(p.profit || 0) >= 0 ? 'adm-pos' : 'adm-neg'}`}>{(p.profit || 0) >= 0 ? '+' : ''}{(p.profit || 0).toFixed(2)}</td>
                                            <td className="adm-num">{(p.storage || 0).toFixed(2)}</td>
                                            <td>{p.time_create || '—'}</td>
                                        </tr>
                                    );
                                } else {
                                    // Deal history format
                                    const entryStr = p.entry === 0 ? 'IN' : p.entry === 1 ? 'OUT' : 'IN/OUT';
                                    return (
                                        <tr key={ticketId} className={sel === ticketId ? 'selected' : ''} onClick={() => setSel(ticketId)}>
                                            <td><strong>{p.ticket}</strong></td>
                                            <td>{p.order_ticket || '—'}</td>
                                            <td>{p.login}</td>
                                            <td><strong>{p.symbol}</strong></td>
                                            <td><span className={`adm-side-badge ${typeStr.toLowerCase()}`}>{typeStr}</span></td>
                                            <td><span className="adm-tag">{entryStr}</span></td>
                                            <td>{(p.volume || 0).toFixed(2)}</td>
                                            <td className="adm-num">{(p.price || 0).toFixed(5)}</td>
                                            <td className={`adm-num ${(p.profit || 0) >= 0 ? 'adm-pos' : 'adm-neg'}`}>{(p.profit || 0) >= 0 ? '+' : ''}{(p.profit || 0).toFixed(2)}</td>
                                            <td className="adm-num">{(p.storage || 0).toFixed(2)}</td>
                                            <td className="adm-num adm-neg">{(p.commission || 0).toFixed(2)}</td>
                                            <td>{p.timestamp || '—'}</td>
                                        </tr>
                                    );
                                }
                            })}
                        </tbody>
                    </table>
                )}
            </div>

            <div className="adm-statusbar">
                <span>{view === 'open' ? 'Open Positions' : 'Closed Deals'}: {filtered.length}</span>
                <span className="adm-sep">|</span>
                <span className={totalProfit >= 0 ? 'adm-pos' : 'adm-neg'}>
                    Total {view === 'open' ? 'Float P&L' : 'Realized P&L'}: {totalProfit >= 0 ? '+' : ''}{totalProfit.toFixed(2)} USD
                </span>
            </div>
        </div>
    );
}
