import * as React from 'react';
import { API, isBackendGap, TradeRequest } from '../../services/api';
import { RequestBar } from './RequestBar';
import { OperationDialog } from './OperationDialog';
import type { OperationKind } from '../../services/api';
import { POSITION_ICON, fmtTime } from '../../shared/tradeTypes';
import { money } from '../../shared/format';

/**
 * Positions view — MT5 Administrator §Positions: all current positions of all
 * traders, request bar without period/open-only (current positions only).
 */
export function PositionsPanel(): React.ReactElement {
    const [rows, setRows] = React.useState<any[]>([]);
    const [symbols, setSymbols] = React.useState<string[]>([]);
    const [loading, setLoading] = React.useState(true);
    const [banner, setBanner] = React.useState<{ gap: boolean; text: string } | null>(null);

    const [op, setOp] = React.useState<{ kind: OperationKind; id: number | string } | null>(null);
    const [mask, setMask] = React.useState('*');
    const [symbol, setSymbol] = React.useState('');
    const [openOnly, setOpenOnly] = React.useState(true);
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
            openOnly,
            from: from ? new Date(from).toISOString() : undefined,
            to: to ? new Date(to).toISOString() : undefined,
        };
        try {
            setRows(await API.getPositions(req));
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
                                <th>Status</th><th>Login</th><th>Position</th><th>Open Time</th><th>Close Time</th>
                                <th>Type</th><th>Symbol</th><th className="num">Volume</th><th>Reason</th>
                                <th className="num">Price Open</th><th className="num">S/L</th><th className="num">T/P</th>
                                <th className="num">Price Current</th><th className="num">Swap</th><th className="num">Profit</th>
                                <th>Comment</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows.map((p) => {
                                const ic = POSITION_ICON[p.type] ?? { icon: 'circle-outline', cls: '' };
                                return (
                                    <tr onDoubleClick={(e) => { e.stopPropagation(); setOp({ kind: 'position', id: p.position_id }); }} key={p.position_id}>
                                        <td>
                                            <span className={`ca-pill ${p.is_closed ? 'off' : 'ok'}`}>
                                                {p.is_closed ? 'CLOSED' : 'OPEN'}
                                            </span>
                                        </td>
                                        <td><code className="adm-code">{p.login}</code></td>
                                        <td><code className="adm-code">{p.position_id}</code></td>
                                        <td className="ca-dim">{fmtTime(p.open_time)}</td>
                                        <td className="ca-dim">{p.close_time ? fmtTime(p.close_time) : '—'}</td>
                                        <td>
                                            <i className={`codicon codicon-${ic.icon} ${ic.cls}`} style={{ marginRight: 5 }} />
                                            {p.type === 0 ? 'buy' : 'sell'}
                                        </td>
                                        <td>{p.symbol}</td>
                                        <td className="num">{p.volume}</td>
                                        <td className="ca-dim">{p.reason}</td>
                                        <td className="num">{p.price_open}</td>
                                        <td className="num ca-dim">{p.sl || '0.000'}</td>
                                        <td className="num ca-dim">{p.tp || '0.000'}</td>
                                        <td className="num">{p.price_current}</td>
                                        <td className="num">{p.swap || ''}</td>
                                        <td className={`num ${p.profit >= 0 ? 'heat-green' : 'heat-red'}`}>{money(p.profit)}</td>
                                        <td className="ca-dim">{p.comment}</td>
                                    </tr>
                                );
                            })}
                            {!loading && rows.length === 0 && (
                                <tr><td colSpan={16} className="ca-empty"><i className="codicon codicon-graph-scatter" /> No positions for this request</td></tr>
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
