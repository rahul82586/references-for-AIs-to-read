import * as React from 'react';

export interface RequestBarProps {
    mask: string;
    onMask: (v: string) => void;
    symbols: string[];
    symbol: string;
    onSymbol: (v: string) => void;
    showOpenOnly?: boolean;
    openOnly?: boolean;
    onOpenOnly?: (v: boolean) => void;
    showPeriod?: boolean;
    from: string;
    to: string;
    onFrom: (v: string) => void;
    onTo: (v: string) => void;
    requesting: boolean;
    onRequest: () => void;
}

const PRESETS = ['Today', 'Last 3 days', 'Last week', 'Last 3 months', 'Last 6 months', 'All history'];

/**
 * The admin terminal's bottom request line (doc §Orders/§Deals/§Positions
 * "Requesting…"): mask (* / logins / #tickets), symbol list, Open only,
 * period presets + exact From/To, database selector, Request.
 */
export function RequestBar(p: RequestBarProps): React.ReactElement {
    const applyPreset = (preset: string) => {
        const now = new Date();
        const from = new Date(now);
        if (preset === 'Today') from.setHours(0, 0, 0, 0);
        if (preset === 'Last 3 days') from.setDate(from.getDate() - 3);
        if (preset === 'Last week') from.setDate(from.getDate() - 7);
        if (preset === 'Last 3 months') from.setMonth(from.getMonth() - 3);
        if (preset === 'Last 6 months') from.setMonth(from.getMonth() - 6);
        if (preset === 'All history') {
            p.onFrom('');
            p.onTo('');
            return;
        }
        p.onFrom(toLocalInput(from));
        p.onTo(toLocalInput(now));
    };

    return (
        <div className="ca-reqbar">
            <i className="codicon codicon-search" />
            <input
                className="adm-input"
                title="logins comma-separated, #tickets, or * for all"
                placeholder="*"
                value={p.mask}
                onChange={(e) => p.onMask(e.target.value)}
            />
            <select className="adm-select" value={p.symbol} onChange={(e) => p.onSymbol(e.target.value)} title="symbols: one, comma list, or folder masks">
                <option value="">All Symbols</option>
                {p.symbols.map((s) => (
                    <option key={s} value={s}>{s}</option>
                ))}
            </select>
            {p.showOpenOnly && (
                <label className="ca-check">
                    <input type="checkbox" checked={Boolean(p.openOnly)} onChange={(e) => p.onOpenOnly?.(e.target.checked)} />
                    Open only
                </label>
            )}
            {p.showPeriod && (
                <>
                    <select className="adm-select" value="" onChange={(e) => e.target.value && applyPreset(e.target.value)}>
                        <option value="">period…</option>
                        {PRESETS.map((x) => (
                            <option key={x} value={x}>{x}</option>
                        ))}
                    </select>
                    <input type="datetime-local" className="adm-input ca-dt" value={p.from} onChange={(e) => p.onFrom(e.target.value)} />
                    <span className="ca-dim">—</span>
                    <input type="datetime-local" className="adm-input ca-dt" value={p.to} onChange={(e) => p.onTo(e.target.value)} />
                </>
            )}
            <select className="adm-select" defaultValue="current" title="database">
                <option value="current">Current database</option>
                <option value="archive" disabled>Archive (gap)</option>
            </select>
            <button className="wb-btn" onClick={p.onRequest} disabled={p.requesting}>
                <i className="codicon codicon-refresh" /> {p.requesting ? 'Requesting…' : 'Request'}
            </button>
        </div>
    );
}

export function toLocalInput(d: Date): string {
    const p = (n: number) => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}`;
}
