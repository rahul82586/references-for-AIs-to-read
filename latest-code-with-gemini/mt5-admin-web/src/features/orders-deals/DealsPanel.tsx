import * as React from 'react';
import { API, isBackendGap, TradeRequest } from '../../services/api';
import { RequestBar } from './RequestBar';
import { OperationDialog } from './OperationDialog';
import type { OperationKind } from '../../services/api';
import { DEAL_ICON, fmtTime } from './tradeTypes';
import { money } from '../clients/format';

/**
 * Deals view — MT5 Administrator §Deals: full deal history incl. balance
 * operations, with the bottom request bar.
 */
export function DealsPanel(): React.ReactElement {
    const [rows, setRows] = React.useState<any[]>([]);
    const [symbols, setSymbols] = React.useState<string[]>([]);
    const [loading, setLoading] = React.useState(true);
    const [banner, setBanner] = React.useState<{ gap: boolean; text: string } | null>(null);

    const [op, setOp] = React.useState<{ kind: OperationKind; id: number | string } | null>(null);
    const [mask, setMask] = React.useState('*');
    const [symbol, setSymbol] = React.useState('');
    const [from, setFrom] = React.useState('');
    const [to, setTo] = React.useState('');

    React.useEffect(() => {
        API.getSymbols().then((s) => setSymbols(s.map((x: any) => x.symbol ?? x.name))).catch(() => setSymbols([]));
    }, []);

    const request = React.useCallback(async () => {
        setLoading(true);
        setBanner(null);
        const req: TradeRequest = {
            mask,
            symbols: symbol,
            from: from ? new Date(from).toISOString() : undefined,
            to: to ? new Date(to).toISOString() : undefined,
        };
        try {
            setRows(await API.getDeals(req));
        } catch (e: any) {
            setBanner({ gap: isBackendGap(e), text: String(e?.message ?? e) });
            setRows([]);
        } finally {
            setLoading(false);
        }
    }, [mask, symbol, from, to]);

    React.useEffect(() => {
        void request();
    }, [request]);

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
                                <th>Time</th><th>Login</th><th>Deal</th><th>Order</th><th>Position</th>
                                <th>Symbol</th><th>Action</th><th>Type</th>
                                <th className="num">Volume</th><th className="num">Price</th>
                                <th className="num">Profit</th><th className="num">Swap</th><th className="num">Commission</th>
                                <th>Comment</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows.map((d) => {
                                const ic = DEAL_ICON[d.type] ?? { icon: 'circle-outline', cls: '' };
                                return (
                                    <tr onDoubleClick={(e) => { e.stopPropagation(); setOp({ kind: 'deal', id: d.deal_id }); }} key={d.deal_id}>
                                        <td className="ca-dim">{fmtTime(d.time)}</td>
                                        <td><code className="adm-code">{d.login}</code></td>
                                        <td><code className="adm-code">{d.deal_id}</code></td>
                                        <td className="ca-dim">{d.order || '—'}</td>
                                        <td className="ca-dim">{d.position || '—'}</td>
                                        <td>{d.symbol || <span className="ca-dim">—</span>}</td>
                                        <td><span className="ca-pill">{d.action}</span></td>
                                        <td>
                                            <i className={`codicon codicon-${ic.icon} ${ic.cls}`} style={{ marginRight: 5 }} />
                                            {d.type}
                                        </td>
                                        <td className="num">{d.volume || ''}</td>
                                        <td className="num">{d.price || ''}</td>
                                        <td className={`num ${d.profit > 0 ? 'heat-green' : d.profit < 0 ? 'heat-red' : ''}`}>{d.profit ? money(d.profit) : ''}</td>
                                        <td className="num">{d.swap || ''}</td>
                                        <td className="num">{d.commission ? money(d.commission) : ''}</td>
                                        <td className="ca-dim">{d.comment}</td>
                                    </tr>
                                );
                            })}
                            {!loading && rows.length === 0 && (
                                <tr><td colSpan={14} className="ca-empty"><i className="codicon codicon-pulse" /> No deals for this request</td></tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
            <RequestBar
                mask={mask} onMask={setMask}
                symbols={symbols} symbol={symbol} onSymbol={setSymbol}
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
