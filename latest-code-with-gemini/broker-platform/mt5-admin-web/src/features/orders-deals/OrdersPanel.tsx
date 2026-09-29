import * as React from 'react';
import { API, isBackendGap, TradeRequest } from '../../services/api';
import { RequestBar } from './RequestBar';
import { OperationDialog } from './OperationDialog';
import type { OperationKind } from '../../services/api';
import { ORDER_TYPE, ORDER_STATE, ORDER_ICON, fmtTime } from '../../shared/tradeTypes';

/**
 * Orders view — MT5 Administrator §Orders: pending + executed orders with the
 * admin terminal's column set and bottom request bar.
 */
export function OrdersPanel(): React.ReactElement {
    const [rows, setRows] = React.useState<any[]>([]);
    const [symbols, setSymbols] = React.useState<string[]>([]);
    const [loading, setLoading] = React.useState(true);
    const [banner, setBanner] = React.useState<{ gap: boolean; text: string } | null>(null);

    const [mask, setMask] = React.useState('*');
    const [symbol, setSymbol] = React.useState('');
    const [openOnly, setOpenOnly] = React.useState(false);
    const [from, setFrom] = React.useState('');
    const [to, setTo] = React.useState('');
    const [op, setOp] = React.useState<{ kind: OperationKind; id: number | string } | null>(null);
    const [sort, setSort] = React.useState<{ key: string; dir: 1 | -1 }>({ key: 'time_setup', dir: -1 });

    React.useEffect(() => {
        API.getSymbols().then((s) => setSymbols(s.map((x: any) => x.symbol ?? x.name))).catch(() => setSymbols([]));
    }, []);

    const request = React.useCallback(async () => {
        setLoading(true);
        setBanner(null);
        const req: TradeRequest = {
            mask,
            symbols: symbol,
            openOnly,
            from: from ? new Date(from).toISOString() : undefined,
            to: to ? new Date(to).toISOString() : undefined,
        };
        try {
            setRows(await API.getOrders(req));
        } catch (e: any) {
            setBanner({ gap: isBackendGap(e), text: String(e?.message ?? e) });
            setRows([]);
        } finally {
            setLoading(false);
        }
    }, [mask, symbol, openOnly, from, to]);

    React.useEffect(() => {
        void request();
    }, [request]);

    const sorted = React.useMemo(() => {
        const val = (r: any) => (sort.key === 'symbol' ? r.symbol : sort.key === 'login' ? r.login : sort.key === 'ticket' ? r.ticket : r.time_setup ?? '');
        return [...rows].sort((a, b) => {
            const x = val(a), y = val(b);
            return (x < y ? -1 : x > y ? 1 : 0) * sort.dir;
        });
    }, [rows, sort]);

    const th = (key: string | null, label: string, num = false) => (
        <th
            className={num ? 'num' : ''}
            style={key ? { cursor: 'pointer' } : undefined}
            onClick={() => key && setSort((s) => ({ key, dir: s.key === key && s.dir === 1 ? -1 : 1 }))}
        >
            {label}
            {key && sort.key === key && <i className={`codicon codicon-chevron-${sort.dir === 1 ? 'up' : 'down'} ca-sort`} />}
        </th>
    );

    return (
        <div className="ca-page">
            {banner && (
                <div className={`ca-banner ${banner.gap ? 'gap' : 'error'}`}>
                    <i className="codicon codicon-warning" />
                    <span>{banner.text}</span>
                    <button className="adm-icon-btn" onClick={() => setBanner(null)}><i className="codicon codicon-close" /></button>
                </div>
            )}
            <div className="ca-main">
                <div className="ca-table-wrap">
                    <table className="adm-table ca-table">
                        <thead>
                            <tr>
                                {th('time_setup', 'Time')}
                                {th('login', 'Login')}
                                {th('ticket', 'Order')}
                                {th('symbol', 'Symbol')}
                                {th(null, 'Type')}
                                {th(null, 'Volume', true)}
                                {th(null, 'Price', true)}
                                {th(null, 'S/L', true)}
                                {th(null, 'T/P', true)}
                                {th(null, 'Time', true)}
                                {th(null, 'Price', true)}
                                {th(null, 'Reason')}
                                {th(null, 'State')}
                            </tr>
                        </thead>
                        <tbody>
                            {sorted.map((o) => {
                                const ic = ORDER_ICON[o.type] ?? { icon: 'circle-outline', cls: '' };
                                const pending = o.state === 0 || o.state === 'placed';
                                return (
                                    <tr onDoubleClick={(e) => { e.stopPropagation(); setOp({ kind: 'order', id: o.ticket }); }} key={o.order_id || o.ticket}>
                                        <td className="ca-dim">{fmtTime(o.time_setup)}</td>
                                        <td><code className="adm-code">{o.login}</code></td>
                                        <td><code className="adm-code">{o.ticket || o.order_id}</code></td>
                                        <td>{o.symbol}</td>
                                        <td>
                                            <i className={`codicon codicon-${ic.icon} ${ic.cls}`} style={{ marginRight: 5 }} />
                                            {ORDER_TYPE[o.type] ?? o.type}
                                        </td>
                                        <td className="num">{o.volume_current} / {o.volume}</td>
                                        <td className="num">{o.type === 0 || o.type === 1 ? 'market' : o.price_order || '—'}</td>
                                        <td className="num ca-dim">{o.price_sl || '0.000'}</td>
                                        <td className="num ca-dim">{o.price_tp || '0.000'}</td>
                                        <td className="ca-dim">{fmtTime(o.time_done)}</td>
                                        <td className="num">{o.price_done || ''}</td>
                                        <td className="ca-dim">{o.reason}</td>
                                        <td>
                                            <span className={`ca-pill ${o.state === 'filled' ? 'ok' : o.state === 'canceled' || o.state === 'rejected' ? 'off' : 'warn'}`}>
                                                {ORDER_STATE[o.state] ?? o.state}
                                            </span>
                                        </td>
                                    </tr>
                                );
                            })}
                            {!loading && sorted.length === 0 && (
                                <tr><td colSpan={13} className="ca-empty"><i className="codicon codicon-list-ordered" /> No orders for this request</td></tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
            <RequestBar
                mask={mask} onMask={setMask}
                symbols={symbols} symbol={symbol} onSymbol={setSymbol}
                showOpenOnly openOnly={openOnly} onOpenOnly={setOpenOnly}
                showPeriod from={from} to={to} onFrom={setFrom} onTo={setTo}
                requesting={loading} onRequest={() => void request()}
            />
            {op && (
                <OperationDialog
                    kind={op.kind}
                    id={op.id}
                    onClose={() => setOp(null)}
                    onOpenAccount={(login) => {
                        setOp(null);
                        window.dispatchEvent(new CustomEvent('mt5-admin:open-node', {
                            detail: {
                                id: 'clients-and-accounts.trading-accounts',
                                label: 'Trading Accounts',
                                props: { initialTab: 'accounts', initialRequest: String(login) },
                            },
                        }));
                    }}
                    onInfo={(m) => setBanner({ gap: false, text: m })}
                    onError={(m, g) => setBanner({ gap: Boolean(g), text: m })}
                />
            )}
        </div>
    );
}
