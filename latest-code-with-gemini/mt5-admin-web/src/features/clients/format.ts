/** Display-only formatters. No domain math lives here — values arrive
 *  pre-computed from the API; these only shape them for humans. */

export const money = (v: number | undefined | null, currency = ''): string => {
    if (v === undefined || v === null || !Number.isFinite(v)) return '—';
    const s = v.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    return currency ? `${s} ${currency}` : s;
};

export const percent = (v: number | undefined | null): string =>
    v === undefined || v === null || !Number.isFinite(v) ? '—' : `${v.toLocaleString('en-US', { maximumFractionDigits: 1 })}%`;

export const leverage = (v: number | undefined | null): string =>
    v === undefined || v === null || !Number.isFinite(v) || v <= 0 ? '—' : `1:${v}`;

export const dateTime = (iso: string | null | undefined): string => {
    if (!iso) return '—';
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return String(iso);
    return d.toLocaleString('en-GB', {
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit',
    });
};

/** Margin-level heat: red below 100%, amber below 300%, green above. */
export const marginLevelClass = (v: number | undefined | null): string => {
    if (v === undefined || v === null || !Number.isFinite(v) || v <= 0) return '';
    if (v < 100) return 'heat-red';
    if (v < 300) return 'heat-amber';
    return 'heat-green';
};

export function toCsv(rows: Record<string, unknown>[], columns: { key: string; label: string }[]): string {
    const esc = (x: unknown) => {
        const s = x === null || x === undefined ? '' : String(x);
        return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
    };
    const head = columns.map((c) => esc(c.label)).join(',');
    const body = rows.map((r) => columns.map((c) => esc(r[c.key])).join(','));
    return [head, ...body].join('\n');
}

export function downloadCsv(filename: string, csv: string): void {
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}
