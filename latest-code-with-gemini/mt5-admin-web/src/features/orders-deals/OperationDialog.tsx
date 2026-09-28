import * as React from 'react';
import { API, isBackendGap, OperationKind, TradeOperationView } from '../../services/api';
import { fmtTime } from './tradeTypes';
import { money } from '../clients/format';

interface Props {
    kind: OperationKind;
    id: number | string;
    onClose: () => void;
    onOpenAccount: (login: number) => void;
    onInfo: (msg: string) => void;
    onError: (msg: string, gap?: boolean) => void;
}

type Tab = 'details' | 'visualization' | 'ticks' | 'journal';

interface Field { key: string; label: string; type?: 'text' | 'num' | 'dt' | 'select'; options?: string[]; ro?: boolean }

const FIELDSETS: Record<OperationKind, { left: Field[]; mid?: Field[]; right: Field[] }> = {
    position: {
        left: [
            { key: 'opened', label: 'Opened', type: 'dt', ro: true },
            { key: 'updated', label: 'Updated', type: 'dt', ro: true },
            { key: 'reason', label: 'Reason', type: 'select', options: ['Client', 'Dealer', 'Expert', 'Rollover', 'Split', 'Synchronization', 'Transfer'] },
            { key: 'dealer_id', label: 'Dealer ID' },
            { key: 'expert_id', label: 'Expert ID' },
            { key: 'external_id', label: 'External ID' },
            { key: 'comment', label: 'Comment' },
        ],
        right: [
            { key: 'open_price', label: 'Open price', type: 'num', ro: true },
            { key: 'current_price', label: 'Current price', type: 'num', ro: true },
            { key: 'sl', label: 'Stop loss', type: 'num' },
            { key: 'tp', label: 'Take profit', type: 'num' },
            { key: 'swap', label: 'Swap', type: 'num', ro: true },
            { key: 'profit', label: 'Profit', type: 'num', ro: true },
            { key: 'margin_rate', label: 'Margin rate', type: 'num', ro: true },
        ],
    },
    order: {
        left: [
            { key: 'reason', label: 'Reason', type: 'select', options: ['Client', 'Dealer', 'Expert', 'SL/TP', 'SO', 'Gateway'] },
            { key: 'state', label: 'State', type: 'select', options: ['PLACED', 'PARTIAL', 'FILLED', 'CANCELED', 'REJECTED'] },
            { key: 'expiration', label: 'Expiration', type: 'select', options: ['GTC', 'DAY', 'SPECIFIED'] },
            { key: 'filling', label: 'Filling', type: 'select', options: ['IMMEDIATE OR CANCEL', 'FILL OR KILL', 'RETURN'] },
            { key: 'dealer_id', label: 'Dealer ID' },
            { key: 'expert_id', label: 'Expert ID' },
            { key: 'external_id', label: 'External ID' },
            { key: 'comment', label: 'Comment' },
        ],
        mid: [
            { key: 'setup_time', label: 'Setup time', type: 'dt', ro: true },
            { key: 'done_time', label: 'Done time', type: 'dt', ro: true },
            { key: 'expiration_time', label: 'Expiration time', type: 'dt' },
        ],
        right: [
            { key: 'order_price', label: 'Order price', type: 'num', ro: true },
            { key: 'current_price', label: 'Current price', type: 'num', ro: true },
            { key: 'trigger_price', label: 'Trigger price', type: 'num' },
            { key: 'sl', label: 'Stop loss', type: 'num' },
            { key: 'tp', label: 'Take profit', type: 'num' },
            { key: 'margin_rate', label: 'Margin rate', type: 'num', ro: true },
        ],
    },
    deal: {
        left: [
            { key: 'create_time', label: 'Create time', type: 'dt', ro: true },
            { key: 'reason', label: 'Reason', type: 'select', options: ['Client', 'Dealer', 'Expert', 'SL/TP', 'SO', 'Gateway'] },
            { key: 'dealer_id', label: 'Dealer ID' },
            { key: 'expert_id', label: 'Expert ID' },
            { key: 'external_id', label: 'External ID' },
            { key: 'comment', label: 'Comment' },
            { key: 'market_bid', label: 'Market Bid', type: 'num', ro: true },
            { key: 'market_ask', label: 'Market Ask', type: 'num', ro: true },
            { key: 'market_last', label: 'Market Last', type: 'num', ro: true },
        ],
        right: [
            { key: 'price', label: 'Price', type: 'num', ro: true },
            { key: 'position_price', label: 'Position price', type: 'num', ro: true },
            { key: 'sl', label: 'Stop loss', type: 'num' },
            { key: 'tp', label: 'Take profit', type: 'num' },
            { key: 'commission', label: 'Commission', type: 'num', ro: true },
            { key: 'fee', label: 'Fee', type: 'num', ro: true },
            { key: 'swap', label: 'Swap', type: 'num', ro: true },
            { key: 'profit', label: 'Profit', type: 'num', ro: true },
            { key: 'raw_profit', label: 'Raw profit', type: 'num', ro: true },
            { key: 'profit_rate', label: 'Profit rate', type: 'num', ro: true },
            { key: 'margin_rate', label: 'Margin rate', type: 'num', ro: true },
            { key: 'gateway_price', label: 'Gateway price', type: 'num', ro: true },
        ],
    },
};

/**
 * Trading operation dialog — double-click on a position/order/deal
 * (doc §Viewing an Order/Deal/Position + operator screenshots):
 *  · title line per operation
 *  · account link line (click → account editing window)
 *  · related-operations chain; selecting a row swaps the details below
 *  · tabs Details / Visualization / Ticks / Journal
 *  · footer Report… · Reopen (orders) · Update · Cancel · Help
 */
export function OperationDialog({ kind, id, onClose, onOpenAccount, onInfo, onError }: Props): React.ReactElement {
    const [view, setView] = React.useState<TradeOperationView | null>(null);
    const [loadError, setLoadError] = React.useState<string | null>(null);
    const [tab, setTab] = React.useState<Tab>('details');
    const [selectedChain, setSelectedChain] = React.useState<number | string | null>(null);
    const [draft, setDraft] = React.useState<Record<string, any>>({});

    const onErrorRef = React.useRef(onError);
    onErrorRef.current = onError;
    const onInfoRef = React.useRef(onInfo);
    onInfoRef.current = onInfo;

    const load = React.useCallback(async (k: OperationKind, i: number | string) => {
        try {
            const v = await API.getTradeOperation(k, i);
            setView(v);
            setDraft(JSON.parse(JSON.stringify(v.details)));
            setSelectedChain(v.id);
            setLoadError(null);
        } catch (e: any) {
            setLoadError(String(e?.message ?? e));
            if (isBackendGap(e)) onErrorRef.current(e.message, true);
        }
    }, []);

    React.useEffect(() => {
        setTab('details');
        void load(kind, id);
    }, [kind, id, load]);

    const selectChain = (row: any) => {
        if (row.kind === view?.kind && String(row.ticket) === String(view?.id)) return;
        void load(row.kind, row.ticket);
    };

    const update = async () => {
        if (!view) return;
        try {
            await API.updateTradeOperation(view.kind, view.id, draft);
            onInfoRef.current(`${view.kind} #${view.id} updated.`);
            void load(view.kind, view.id);
        } catch (e: any) {
            onErrorRef.current(String(e?.message ?? e), isBackendGap(e));
        }
    };

    const reopen = async () => {
        if (!view) return;
        try {
            await API.reopenOrder(view.id);
            onInfoRef.current(`Order ${view.id} reopened (pending again).`);
            onClose();
        } catch (e: any) {
            onErrorRef.current(String(e?.message ?? e), isBackendGap(e));
        }
    };

    const report = () => {
        if (!view) return;
        // doc §Trading operation report: chain + details + journal saved to a file
        const html = `<html><head><title>Trade operation report ${view.kind} #${view.id}</title></head><body>
<h2>${view.title}</h2>
<p>Account: ${view.account ? `${view.account.name}, ${view.account.login}, ${view.account.group}, 1:${view.account.leverage}` : '—'}</p>
<h3>Related operations</h3>
<table border="1"><tr><th>Kind</th><th>Ticket</th><th>Time</th><th>Type</th><th>Volume</th><th>Price</th><th>Reason</th><th>Profit</th></tr>
${view.chain.map((c) => `<tr><td>${c.kind}</td><td>${c.ticket}</td><td>${c.time}</td><td>${c.type}</td><td>${c.volume}</td><td>${c.price}</td><td>${c.reason}</td><td>${c.profit ?? ''}</td></tr>`).join('')}
</table>
<h3>Details</h3><pre>${JSON.stringify(view.details, null, 2)}</pre>
<h3>Journal</h3><pre>${view.journal.map((j) => `${j.time} ${j.server}: ${j.message}`).join('\n')}</pre>
</body></html>`;
        const blob = new Blob([html], { type: 'text/html' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `${view.kind}_${view.id}_report.html`;
        a.click();
        URL.revokeObjectURL(a.href);
        onInfo('Operation report saved.');
    };

    if (loadError) {
        return (
            <div className="adm-modal-overlay" onMouseDown={onClose}>
                <div className="adm-modal op-dialog" onMouseDown={(e) => e.stopPropagation()}>
                    <div className="adm-modal-body ca-gap-note"><i className="codicon codicon-warning" /> {loadError}</div>
                    <div className="adm-modal-footer"><button className="wb-btn secondary" onClick={onClose}>Close</button></div>
                </div>
            </div>
        );
    }
    if (!view) {
        return (
            <div className="adm-modal-overlay" onMouseDown={onClose}>
                <div className="adm-modal op-dialog" onMouseDown={(e) => e.stopPropagation()}>
                    <div className="adm-modal-body ca-empty"><i className="codicon codicon-loading codicon-modifier-spin" /> loading operation…</div>
                </div>
            </div>
        );
    }

    const fs = FIELDSETS[view.kind];
    const opTime = new Date(
        (view.details.opened ?? view.details.setup_time ?? view.details.create_time ?? '') as string
    ).getTime();
    const nearestTickIdx = view.ticks.reduce(
        (best, t, i) => (Math.abs(new Date(t.time).getTime() - opTime) < Math.abs(new Date(view.ticks[best].time).getTime() - opTime) ? i : best),
        0
    );

    const renderField = (f: Field) => (
        <div className="op-field" key={f.key}>
            <label>{f.label}:</label>
            {f.type === 'select' ? (
                <select
                    className="adm-select"
                    value={String(draft[f.key] ?? '')}
                    disabled={f.ro}
                    onChange={(e) => setDraft((d) => ({ ...d, [f.key]: e.target.value }))}
                >
                    {(f.options ?? []).map((o) => <option key={o} value={o}>{o}</option>)}
                    {!f.options?.includes(String(draft[f.key] ?? '')) && String(draft[f.key] ?? '') !== '' && (
                        <option value={String(draft[f.key])}>{String(draft[f.key])}</option>
                    )}
                </select>
            ) : (
                <input
                    className="adm-input"
                    type={f.type === 'dt' ? 'text' : f.type === 'num' ? 'number' : 'text'}
                    value={f.type === 'dt' ? fmtTime(draft[f.key]) : String(draft[f.key] ?? '')}
                    readOnly={f.ro}
                    onChange={(e) => setDraft((d) => ({ ...d, [f.key]: f.type === 'num' ? Number(e.target.value) : e.target.value }))}
                />
            )}
        </div>
    );

    /* Visualization: tick chart with the operation marked */
    const W = 860, H = 240, PAD = 30;
    const bids = view.ticks.map((t) => t.bid);
    const min = Math.min(...bids, ...view.ticks.map((t) => t.ask));
    const max = Math.max(...bids, ...view.ticks.map((t) => t.ask));
    const px = (i: number) => PAD + (i / Math.max(1, view.ticks.length - 1)) * (W - PAD * 2);
    const py = (v: number) => H - PAD - ((v - min) / Math.max(1e-9, max - min)) * (H - PAD * 2);
    const bidPath = view.ticks.map((t, i) => `${i === 0 ? 'M' : 'L'}${px(i).toFixed(1)},${py(t.bid).toFixed(1)}`).join(' ');
    const askPath = view.ticks.map((t, i) => `${i === 0 ? 'M' : 'L'}${px(i).toFixed(1)},${py(t.ask).toFixed(1)}`).join(' ');

    return (
        <div className="adm-modal-overlay" onMouseDown={onClose}>
            <div className="adm-modal op-dialog" onMouseDown={(e) => e.stopPropagation()}>
                <div className="adm-modal-header">
                    <span className="op-title">{view.title}</span>
                    <button type="button" className="adm-icon-btn" onClick={onClose}><i className="codicon codicon-close" /></button>
                </div>

                {view.account && (
                    <button className="op-account" onClick={() => onOpenAccount(view.account!.login)}>
                        <i className="codicon codicon-person" />
                        {view.account.name}, {view.account.login}, {view.account.group}, 1 : {view.account.leverage}
                    </button>
                )}

                {/* related operations chain */}
                <div className="op-chain">
                    <table className="adm-table ca-table ca-mini">
                        <thead>
                            <tr>
                                <th>Ticket</th><th>Time</th><th>ID</th><th>Type</th><th className="num">Volume</th>
                                <th className="num">Volume Cl.</th><th className="num">Price</th><th>Reason</th><th className="num">Profit</th>
                            </tr>
                        </thead>
                        <tbody>
                            {view.chain.map((c, i) => {
                                const isSelected = String(selectedChain) === String(c.ticket) && c.kind === view.kind;
                                const isSell = String(c.type || '').toLowerCase().includes('sell');
                                const isOut = String(c.action || '').toLowerCase() === 'out' || (c.volume_current && c.volume_current !== '0' && c.volume_current !== '');
                                return (
                                    <tr
                                        key={`${c.kind}-${c.ticket}-${i}`}
                                        className={isSelected ? 'selected' : ''}
                                        onClick={() => selectChain(c)}
                                        title={`view ${c.kind} #${c.ticket}`}
                                    >
                                        <td>
                                            {c.kind === 'position' ? (
                                                <i className="codicon codicon-credit-card ca-chain-ic ca-chain-pos" title="Position" />
                                            ) : c.kind === 'order' ? (
                                                <i className={`codicon codicon-file-text ca-chain-ic ${isSell ? 'ca-chain-sell' : 'ca-chain-buy'}`} title="Order" />
                                            ) : isOut ? (
                                                <i className="codicon codicon-arrow-left ca-chain-ic ca-chain-sell" title="Deal OUT" />
                                            ) : (
                                                <i className="codicon codicon-arrow-right ca-chain-ic ca-chain-buy" title="Deal IN" />
                                            )}
                                            <code className="adm-code">{c.ticket}</code>
                                        </td>
                                        <td className="ca-dim">{fmtTime(c.time)}</td>
                                        <td className="ca-dim">{c.ext_id}</td>
                                        <td>{c.type}</td>
                                        <td className="num">{c.volume}</td>
                                        <td className="num ca-dim">{c.volume_current ?? ''}</td>
                                        <td className="num">{c.price}</td>
                                        <td className="ca-dim">{c.reason}</td>
                                        <td className={`num ${c.profit !== undefined && c.profit < 0 ? 'heat-red' : c.profit && c.profit > 0 ? 'heat-green' : 'ca-dim'}`}>
                                            {c.profit !== undefined ? (c.profit === 0 ? '0.00' : money(c.profit)) : ''}
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>

                <div className="adm-tabs ca-modal-tabs op-tabs">
                    {(['details', 'visualization', 'ticks', 'journal'] as Tab[]).map((t) => (
                        <button key={t} className={`adm-tab ${tab === t ? 'active' : ''}`} onClick={() => setTab(t)}>
                            {t[0].toUpperCase() + t.slice(1)}
                        </button>
                    ))}
                </div>

                <div className="adm-modal-body op-body">
                    {tab === 'details' && (
                        <div className="op-details">
                            <div className="op-links-row">
                                <span className="op-link-label">{view.kind[0].toUpperCase() + view.kind.slice(1)}:</span>
                                <code className="adm-code op-link">{view.id}</code>
                                {view.kind !== 'position' && draft.position ? (
                                    <>
                                        <span className="op-link-label">Position:</span>
                                        <button className="ca-linkbtn" onClick={() => void load('position', draft.position)}>{draft.position}</button>
                                    </>
                                ) : null}
                                {view.kind === 'deal' && draft.order ? (
                                    <>
                                        <span className="op-link-label">Order:</span>
                                        <button className="ca-linkbtn" onClick={() => void load('order', draft.order)}>{draft.order}</button>
                                    </>
                                ) : null}
                            </div>
                            <div className="op-head-row">
                                <select
                                    className="adm-select"
                                    value={String(draft.type ?? '')}
                                    onChange={(e) => setDraft((d) => ({ ...d, type: e.target.value }))}
                                >
                                    {(view.kind === 'deal'
                                        ? ['buy', 'sell', 'balance', 'credit', 'charge', 'commission', 'daily commission', 'swap', 'bonus']
                                        : ['buy', 'sell', 'buy limit', 'sell limit', 'buy stop', 'sell stop']
                                    ).map((o) => <option key={o} value={o}>{o.toUpperCase()}</option>)}
                                </select>
                                {view.kind === 'deal' && (
                                    <select className="adm-select" value={String(draft.action ?? '')} onChange={(e) => setDraft((d) => ({ ...d, action: e.target.value }))}>
                                        {['in', 'out', 'in/out', 'out by'].map((o) => <option key={o} value={o}>{o.toUpperCase()}</option>)}
                                    </select>
                                )}
                                <input className="adm-input op-vol" type="number" step="0.01" value={draft.volume ?? 0} onChange={(e) => setDraft((d) => ({ ...d, volume: Number(e.target.value) }))} />
                                {view.kind === 'order' && (
                                    <span className="op-remained">Remained volume: <b>{draft.remained_volume ?? 0}</b></span>
                                )}
                                {view.kind === 'deal' && (
                                    <span className="op-remained">Closed volume: <b>{draft.closed_volume ?? 0}</b></span>
                                )}
                                <select className="adm-select op-symbol" value={String(draft.symbol ?? '')} disabled>
                                    <option value={String(draft.symbol ?? '')}>{String(draft.symbol ?? '—')}</option>
                                </select>
                            </div>
                            <div className="op-cols">
                                <div className="op-col">{fs.left.map(renderField)}</div>
                                {fs.mid && <div className="op-col op-col-mid">{fs.mid.map(renderField)}</div>}
                                <div className="op-col">{fs.right.map(renderField)}</div>
                            </div>
                            <div className="op-note">Disabled activations: <span className="ca-dim">{(draft.disabled_activations ?? []).join(', ') || 'none'}</span></div>
                            <div className="op-note">Modifications: <span className="ca-dim">{(draft.modifications ?? []).length ? JSON.stringify(draft.modifications) : 'none'}</span></div>
                        </div>
                    )}

                    {tab === 'visualization' && (
                        <div className="op-viz">
                            <svg viewBox={`0 0 ${W} ${H}`} className="op-svg">
                                <path d={askPath} fill="none" stroke="#f48771" strokeWidth="1" />
                                <path d={bidPath} fill="none" stroke="#4fc1ff" strokeWidth="1" />
                                <line x1={px(nearestTickIdx)} y1={8} x2={px(nearestTickIdx)} y2={H - 8} stroke="#cca700" strokeDasharray="4 3" />
                                <circle cx={px(nearestTickIdx)} cy={py(view.ticks[nearestTickIdx]?.bid ?? 0)} r="4" fill="#cca700" />
                                <text x={PAD} y={16} className="op-svg-label">bid</text>
                                <text x={PAD + 30} y={16} className="op-svg-label" fill="#f48771">ask</text>
                                <text x={px(nearestTickIdx) + 6} y={20} className="op-svg-label" fill="#cca700">operation</text>
                            </svg>
                            <div className="wb-settings-hint">Tick chart of {draft.symbol || '—'} around the operation time (doc §Visualization).</div>
                        </div>
                    )}

                    {tab === 'ticks' && (
                        <div className="ca-table-wrap">
                            <table className="adm-table ca-table ca-mini">
                                <thead><tr><th>Time</th><th className="num">Bid</th><th className="num">Ask</th><th className="num">Last</th></tr></thead>
                                <tbody>
                                    {view.ticks.map((t, i) => (
                                        <tr key={i} className={i === nearestTickIdx ? 'selected' : ''}>
                                            <td className="ca-dim">{fmtTime(t.time)}</td>
                                            <td className="num">{t.bid}</td>
                                            <td className="num">{t.ask}</td>
                                            <td className="num">{t.last}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                            <div className="wb-settings-hint" style={{ padding: '6px 10px' }}>
                                Quote history for the operation day; the tick nearest to the operation time is selected (doc §Ticks).
                            </div>
                        </div>
                    )}

                    {tab === 'journal' && (
                        <div className="op-journal">
                            {view.journal.map((j, i) => (
                                <div className="op-journal-row" key={i}>
                                    <span className="ca-dim">{fmtTime(j.time)}</span>
                                    <span className="op-journal-server">{j.server}</span>
                                    <span>{j.message}</span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                <div className="adm-modal-footer">
                    <button type="button" className="wb-btn secondary" onClick={report}>Report…</button>
                    <span style={{ flex: 1 }} />
                    {view.kind === 'order' && (
                        <button type="button" className="wb-btn secondary" onClick={() => void reopen()}>Reopen</button>
                    )}
                    <button type="button" className="wb-btn" onClick={() => void update()}>Update</button>
                    <button type="button" className="wb-btn secondary" onClick={onClose}>Cancel</button>
                    <button type="button" className="wb-btn secondary" title="MetaTrader 5 Administrator guide — Orders/Deals/Positions sections" onClick={() => onInfo('See MT5 Administrator guide: Viewing an Order/Deal/Position.')}>Help</button>
                </div>
            </div>
        </div>
    );
}
