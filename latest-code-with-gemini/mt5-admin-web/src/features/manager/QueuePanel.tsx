import * as React from 'react';
import { API, isBackendGap } from '../../services/api';
import { fmtTime, ORDER_TYPE } from '../../shared/tradeTypes';

/**
 * Dealing / Queue — the dealer request queue (orders in PENDING_DEALER).
 * Confirm / Reject / Requote per MT5 dealing semantics; mock executes,
 * live raises the honest gap until the backend dealer endpoints exist.
 */
export function QueuePanel(): React.ReactElement {
    const [rows, setRows] = React.useState<any[]>([]);
    const [error, setError] = React.useState<{ gap: boolean; text: string } | null>(null);
    const [busy, setBusy] = React.useState<number | null>(null);
    const [requote, setRequote] = React.useState<Record<number, string>>({});

    const load = React.useCallback(() => {
        API.getDealerQueue()
            .then((r) => { setRows(r); setError(null); })
            .catch((e) => { setRows([]); setError({ gap: isBackendGap(e), text: String(e?.message ?? e) }); });
    }, []);

    React.useEffect(load, [load]);

    const answer = async (ticket: number, action: 'confirm' | 'reject' | 'requote') => {
        setBusy(ticket);
        try {
            await API.answerDealer(ticket, action, action === 'requote' ? Number(requote[ticket] ?? 0) || undefined : undefined);
            load();
        } catch (e: any) {
            setError({ gap: isBackendGap(e), text: String(e?.message ?? e) });
        } finally {
            setBusy(null);
        }
    };

    return (
        <div className="ca-page">
            <div className="ca-toolbar">
                <div className="ca-request">
                    <i className="codicon codicon-briefcase" />
                    <span style={{ fontSize: 12 }}>Dealer request queue — confirm, reject or requote client requests</span>
                </div>
                <button className="wb-btn secondary" onClick={load}><i className="codicon codicon-refresh" /> Refresh</button>
            </div>
            {error && (
                <div className={`ca-banner ${error.gap ? 'gap' : 'error'}`}>
                    <i className="codicon codicon-warning" /><span>{error.text}</span>
                    <button className="adm-icon-btn" onClick={() => setError(null)}><i className="codicon codicon-close" /></button>
                </div>
            )}
            <div className="ca-main">
                <div className="ca-table-wrap">
                    <table className="adm-table ca-table">
                        <thead>
                            <tr>
                                <th>Queued</th><th>Login</th><th>Order</th><th>Symbol</th><th>Type</th>
                                <th className="num">Volume</th><th className="num">Price</th><th>Reason</th>
                                <th className="num">Requote price</th><th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows.map((o) => (
                                <tr key={o.ticket}>
                                    <td className="ca-dim">{fmtTime(o.time_setup)}</td>
                                    <td><code className="adm-code">{o.login}</code></td>
                                    <td><code className="adm-code">{o.ticket}</code></td>
                                    <td>{o.symbol}</td>
                                    <td>{ORDER_TYPE[o.type] ?? o.type}</td>
                                    <td className="num">{o.volume_current} / {o.volume}</td>
                                    <td className="num">{o.price_order || 'market'}</td>
                                    <td className="ca-dim">{o.reason}</td>
                                    <td className="num">
                                        <input
                                            className="adm-input"
                                            style={{ width: 100, height: 22 }}
                                            type="number"
                                            step="0.00001"
                                            placeholder="new price"
                                            value={requote[o.ticket] ?? ''}
                                            onChange={(e) => setRequote((r) => ({ ...r, [o.ticket]: e.target.value }))}
                                        />
                                    </td>
                                    <td>
                                        <span className="ca-queue-actions">
                                            <button className="wb-btn" disabled={busy === o.ticket} onClick={() => void answer(o.ticket, 'confirm')}>Confirm</button>
                                            <button className="wb-btn secondary" disabled={busy === o.ticket} onClick={() => void answer(o.ticket, 'requote')}>Requote</button>
                                            <button className="wb-btn secondary ca-danger" disabled={busy === o.ticket} onClick={() => void answer(o.ticket, 'reject')}>Reject</button>
                                        </span>
                                    </td>
                                </tr>
                            ))}
                            {!error && rows.length === 0 && (
                                <tr><td colSpan={10} className="ca-empty"><i className="codicon codicon-inbox" /> Queue is empty — no requests awaiting dealing</td></tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
