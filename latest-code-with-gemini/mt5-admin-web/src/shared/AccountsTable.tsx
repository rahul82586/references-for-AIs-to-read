import * as React from 'react';
import { money, percent, leverage, marginLevelClass } from './format';

interface Props {
    rows: any[];
    selected: number[];
    onSelect: (logins: number[], e: React.MouseEvent) => void;
    onOpen: (login: number) => void;
    onContext: (login: number | null, e: React.MouseEvent) => void;
}

type SortKey = 'login' | 'name' | 'group' | 'account_type' | 'balance' | 'equity' | 'margin_level' | 'leverage';

const COLUMNS: Array<{ key: SortKey | null; label: string; num?: boolean }> = [
    { key: 'login', label: 'Login' },
    { key: 'name', label: 'Name' },
    { key: 'group', label: 'Group' },
    { key: 'account_type', label: 'Type' },
    { key: null, label: 'Currency' },
    { key: 'balance', label: 'Balance', num: true },
    { key: null, label: 'Credit', num: true },
    { key: 'equity', label: 'Equity', num: true },
    { key: null, label: 'Margin', num: true },
    { key: null, label: 'Free Margin', num: true },
    { key: 'margin_level', label: 'Margin Level', num: true },
    { key: 'leverage', label: 'Leverage', num: true },
    { key: null, label: 'Status' },
];

/**
 * Trading Accounts table — columns per MT5 Administrator §Accounts
 * (financial status view). Sortable by any column (doc: "Accounts can be
 * sorted out by any of the fields. Click on a column name to sort.").
 */
export function AccountsTable({ rows, selected, onSelect, onOpen, onContext }: Props): React.ReactElement {
    const [sort, setSort] = React.useState<{ key: SortKey; dir: 1 | -1 }>({ key: 'login', dir: 1 });

    const sorted = React.useMemo(() => {
        const val = (r: any): any => {
            switch (sort.key) {
                case 'name': return r.name ?? '';
                case 'group': return r.group ?? '';
                case 'account_type': return r.account_type ?? '';
                case 'balance': return r.balance ?? 0;
                case 'equity': return r.equity ?? 0;
                case 'margin_level': return r.margin_level ?? 0;
                case 'leverage': return r.leverage ?? 0;
                default: return r.login ?? 0;
            }
        };
        return [...rows].sort((a, b) => {
            const x = val(a), y = val(b);
            return (x < y ? -1 : x > y ? 1 : 0) * sort.dir;
        });
    }, [rows, sort]);

    const th = (c: (typeof COLUMNS)[number]) => (
        <th
            key={c.label}
            className={c.num ? 'num' : ''}
            onClick={() => c.key && setSort((s) => ({ key: c.key!, dir: s.key === c.key && s.dir === 1 ? -1 : 1 }))}
            style={c.key ? { cursor: 'pointer' } : undefined}
        >
            {c.label}
            {c.key && sort.key === c.key && (
                <i className={`codicon codicon-chevron-${sort.dir === 1 ? 'up' : 'down'} ca-sort`} />
            )}
        </th>
    );

    return (
        <div className="ca-table-wrap">
            <table className="adm-table ca-table">
                <thead>
                    <tr>{COLUMNS.map(th)}</tr>
                </thead>
                <tbody onContextMenu={(e) => onContext(null, e)}>
                    {sorted.map((r) => {
                        const isSel = selected.includes(r.login);
                        return (
                            <tr
                                key={r.login}
                                className={isSel ? 'selected' : ''}
                                onClick={(e) => onSelect([r.login], e)}
                                onDoubleClick={() => onOpen(r.login)}
                                onContextMenu={(e) => { e.stopPropagation(); onContext(r.login, e); }}
                            >
                                <td><code className="adm-code">{r.login}</code></td>
                                <td className="ca-name">{r.name || <span className="ca-dim">—</span>}</td>
                                <td><code className="adm-code ca-group">{r.group}</code></td>
                                <td><span className={`ca-pill ${String(r.account_type).toLowerCase() === 'real' ? 'ok' : String(r.account_type).toLowerCase() === 'demo' ? 'info' : 'warn'}`}>{r.account_type ?? '—'}</span></td>
                                <td>{r.currency}</td>
                                <td className="num">{money(r.balance)}</td>
                                <td className="num ca-dim">{r.credit ? money(r.credit) : '—'}</td>
                                <td className="num">{money(r.equity)}</td>
                                <td className="num">{money(r.margin)}</td>
                                <td className="num">{money(r.margin_free)}</td>
                                <td className={`num ${marginLevelClass(r.margin_level)}`}>{percent(r.margin_level)}</td>
                                <td className="num">{leverage(r.leverage)}</td>
                                <td>
                                    <span className={`ca-pill ${r.is_enabled ? 'ok' : 'off'}`}>
                                        <i className={`codicon codicon-${r.is_enabled ? 'unlock' : 'lock'}`} />
                                        {r.is_enabled ? 'enabled' : 'disabled'}
                                    </span>
                                </td>
                            </tr>
                        );
                    })}
                    {sorted.length === 0 && (
                        <tr>
                            <td colSpan={COLUMNS.length} className="ca-empty">
                                <i className="codicon codicon-person" /> No accounts match the request
                            </td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );
}
