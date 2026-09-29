import * as React from 'react';
import { money, dateTime } from '../../shared/format';

interface Props {
    rows: any[];
    selected: string[];
    onSelect: (ids: string[], e: React.MouseEvent) => void;
    onContext: (id: string | null, e: React.MouseEvent) => void;
    onViewAccounts: (id: string) => void;
    onOpen: (id: string) => void;
}

const STATUS_STYLE: Record<string, string> = {
    verified: 'ok',
    demo: 'info',
    preliminary: 'warn',
};

/** Clients table — MT5 §Clients: aggregate trader entity over all accounts. */
export function ClientsTable({ rows, selected, onSelect, onContext, onViewAccounts, onOpen }: Props): React.ReactElement {
    return (
        <div className="ca-table-wrap">
            <table className="adm-table ca-table">
                <thead>
                    <tr>
                        <th>Client ID</th>
                        <th>Name</th>
                        <th>Company</th>
                        <th>Country</th>
                        <th>City</th>
                        <th>Email</th>
                        <th>Phone</th>
                        <th className="num">Accounts</th>
                        <th className="num">Total Equity</th>
                        <th>Status</th>
                        <th>Registered</th>
                    </tr>
                </thead>
                <tbody onContextMenu={(e) => onContext(null, e)}>
                    {rows.map((c) => (
                        <tr
                            key={c.id}
                            className={selected.includes(c.id) ? 'selected' : ''}
                            onClick={(e) => onSelect([c.id], e)}
                            onDoubleClick={() => onOpen(c.id)}
                            onContextMenu={(e) => { e.stopPropagation(); onContext(c.id, e); }}
                        >
                            <td><code className="adm-code">{c.id}</code></td>
                            <td className="ca-name">{c.first_name} {c.last_name}</td>
                            <td>{c.company || <span className="ca-dim">—</span>}</td>
                            <td>{c.country}</td>
                            <td>{c.city}</td>
                            <td className="ca-dim">{c.email}</td>
                            <td className="ca-dim">{c.phone}</td>
                            <td className="num">
                                <button className="ca-linkbtn" onClick={(e) => { e.stopPropagation(); onViewAccounts(c.id); }}>
                                    {c.accounts?.length ?? 0}
                                </button>
                            </td>
                            <td className="num">{money(c.equity)}</td>
                            <td>
                                <span className={`ca-pill ${STATUS_STYLE[c.status] ?? 'off'}`}>{c.status}</span>
                            </td>
                            <td className="ca-dim">{dateTime(c.registered)}</td>
                        </tr>
                    ))}
                    {rows.length === 0 && (
                        <tr>
                            <td colSpan={11} className="ca-empty">
                                <i className="codicon codicon-organization" /> No clients match the request
                            </td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );
}
