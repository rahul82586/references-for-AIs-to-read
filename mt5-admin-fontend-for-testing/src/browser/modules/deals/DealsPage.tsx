// @ts-nocheck
import * as React from 'react';

interface Deal {
    id: string;
    deal: number;
    order: number;
    login: number;
    symbol: string;
    action: 'BUY' | 'SELL';
    entry: 'IN' | 'OUT' | 'IN/OUT';
    volume: number;
    price: number;
    profit: number;
    swap: number;
    commission: number;
    time: string;
    comment: string;
    reason: string;
}

const MOCK_DEALS: Deal[] = [
    { id: '1', deal: 30001, order: 10001, login: 50080, symbol: 'EURUSD', action: 'BUY',  entry: 'IN',  volume: 0.10, price: 1.08250, profit: 0.00,   swap: 0.00,  commission: -0.50, time: '2026-08-19 10:22:11', comment: '',          reason: 'CLIENT' },
    { id: '2', deal: 30002, order: 10002, login: 50080, symbol: 'EURUSD', action: 'SELL', entry: 'OUT', volume: 0.10, price: 1.08340, profit: 9.00,   swap: -0.32, commission: -0.50, time: '2026-08-19 15:44:22', comment: '',          reason: 'CLIENT' },
    { id: '3', deal: 30003, order: 20003, login: 50082, symbol: 'GBPUSD', action: 'SELL', entry: 'IN',  volume: 0.50, price: 1.27100, profit: 0.00,   swap: 0.00,  commission: -2.50, time: '2026-08-19 14:22:10', comment: 'EA order',  reason: 'EXPERT' },
];

export function DealsPage(): React.ReactElement {
    const [deals] = React.useState<Deal[]>(MOCK_DEALS);
    const [selected, setSelected] = React.useState<string | null>(null);
    const [filter, setFilter] = React.useState('');
    const [dateFrom, setDateFrom] = React.useState('');
    const [dateTo, setDateTo] = React.useState('');

    const filtered = deals.filter(d =>
        String(d.login).includes(filter) ||
        d.symbol.toLowerCase().includes(filter.toLowerCase()) ||
        String(d.deal).includes(filter)
    );

    const totalProfit = filtered.reduce((s, d) => s + d.profit, 0);
    const totalComm   = filtered.reduce((s, d) => s + d.commission, 0);

    return (
        <div className="adm-page">
            <div className="adm-toolbar">
                <div className="adm-search-wrap">
                    <i className="codicon codicon-search" />
                    <input className="adm-search" placeholder="Filter by login, symbol, deal..." value={filter} onChange={e => setFilter(e.target.value)} />
                </div>
                <div className="adm-toolbar-sep" />
                <label style={{ fontSize: 11, opacity: 0.7 }}>From:</label>
                <input type="date" className="adm-input" style={{ width: 130 }} value={dateFrom} onChange={e => setDateFrom(e.target.value)} />
                <label style={{ fontSize: 11, opacity: 0.7 }}>To:</label>
                <input type="date" className="adm-input" style={{ width: 130 }} value={dateTo} onChange={e => setDateTo(e.target.value)} />
                <button className="adm-btn adm-btn-primary"><i className="codicon codicon-search" /> Request</button>
                <div className="adm-toolbar-sep" />
                <button className="adm-btn"><i className="codicon codicon-export" /> Export</button>
            </div>

            <div className="adm-table-wrap">
                <table className="adm-table">
                    <thead>
                        <tr>
                            <th>Deal #</th>
                            <th>Order #</th>
                            <th>Login</th>
                            <th>Symbol</th>
                            <th>Action</th>
                            <th>Entry</th>
                            <th>Volume</th>
                            <th>Price</th>
                            <th>Profit</th>
                            <th>Swap</th>
                            <th>Commission</th>
                            <th>Reason</th>
                            <th>Time</th>
                            <th>Comment</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filtered.map(d => (
                            <tr key={d.id} className={selected === d.id ? 'selected' : ''} onClick={() => setSelected(d.id)}>
                                <td><strong>{d.deal}</strong></td>
                                <td>{d.order}</td>
                                <td>{d.login}</td>
                                <td><strong>{d.symbol}</strong></td>
                                <td><span className={`adm-side-badge ${d.action.toLowerCase()}`}>{d.action}</span></td>
                                <td><span className="adm-tag">{d.entry}</span></td>
                                <td>{d.volume.toFixed(2)}</td>
                                <td className="adm-num">{d.price.toFixed(5)}</td>
                                <td className={`adm-num ${d.profit >= 0 ? 'adm-pos' : 'adm-neg'}`}>{d.profit >= 0 ? '+' : ''}{d.profit.toFixed(2)}</td>
                                <td className="adm-num">{d.swap.toFixed(2)}</td>
                                <td className="adm-num adm-neg">{d.commission.toFixed(2)}</td>
                                <td>{d.reason}</td>
                                <td>{d.time}</td>
                                <td>{d.comment}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <div className="adm-statusbar">
                <span>Deals: {filtered.length}</span>
                <span className="adm-sep">|</span>
                <span className={totalProfit >= 0 ? 'adm-pos' : 'adm-neg'}>Profit: {totalProfit >= 0 ? '+' : ''}{totalProfit.toFixed(2)}</span>
                <span className="adm-sep">|</span>
                <span className="adm-neg">Commission: {totalComm.toFixed(2)}</span>
            </div>
        </div>
    );
}
