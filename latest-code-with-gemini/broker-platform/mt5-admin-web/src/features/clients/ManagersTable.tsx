import * as React from 'react';
import { dateTime } from '../../shared/format';

interface Props {
    rows: any[];
    selected: number[];
    onSelect: (logins: number[], e: React.MouseEvent) => void;
    onContext: (login: number | null, e: React.MouseEvent) => void;
    onOpen: (login: number) => void;
}

/**
 * Managers table — columns exactly per MT5 §Managers:
 * Login · Name · Mailbox · Groups, plus the administrator/manager marker icon
 * and (superset, from our backend) rights count, 2FA, status, last login.
 */
export function ManagersTable({ rows, selected, onSelect, onContext, onOpen }: Props): React.ReactElement {
    return (
        <div className="ca-table-wrap">
            <table className="adm-table ca-table">
                <thead>
                    <tr>
                        <th style={{ width: 34 }}></th>
                        <th>Login</th>
                        <th>Name</th>
                        <th>Mailbox</th>
                        <th>Groups</th>
                        <th className="num">Rights</th>
                        <th>2FA</th>
                        <th>Status</th>
                        <th>Last Login</th>
                    </tr>
                </thead>
                <tbody onContextMenu={(e) => onContext(null, e)}>
                    {rows.map((m) => {
                        const isAdmin = m.role === 'ADMIN';
                        const pct = m.rights_total ? Math.round((m.rights_granted / m.rights_total) * 100) : 0;
                        return (
                            <tr
                                key={m.login}
                                className={selected.includes(m.login) ? 'selected' : ''}
                                onClick={(e) => onSelect([m.login], e)}
                                onDoubleClick={() => onOpen(m.login)}
                                onContextMenu={(e) => { e.stopPropagation(); onContext(m.login, e); }}
                            >
                                <td className="ca-center">
                                    <i
                                        className={`codicon codicon-${isAdmin ? 'shield' : 'person'}`}
                                        title={isAdmin ? 'Administrator terminal access' : 'Manager'}
                                        style={{ color: isAdmin ? '#4fc1ff' : 'var(--theia-descriptionForeground)' }}
                                    />
                                </td>
                                <td><code className="adm-code">{m.login}</code></td>
                                <td className="ca-name">{m.name}</td>
                                <td>{m.mailbox || <span className="ca-dim">—</span>}</td>
                                <td className="ca-dim">{(m.group_scope ?? []).join(', ') || '—'}</td>
                                <td className="num">
                                    <span className="ca-rights">
                                        <span className="ca-rights-bar">
                                            <span style={{ width: `${pct}%` }} />
                                        </span>
                                        {m.rights_granted}/{m.rights_total}
                                    </span>
                                </td>
                                <td>
                                    {m.is_2fa_enabled ? (
                                        <i className="codicon codicon-key" title="2FA enabled" style={{ color: 'var(--theia-successForeground)' }} />
                                    ) : (
                                        <span className="ca-dim">—</span>
                                    )}
                                </td>
                                <td>
                                    <span className={`ca-pill ${m.is_active ? 'ok' : 'off'}`}>
                                        {m.is_active ? 'active' : 'disabled'}
                                    </span>
                                    {m.must_change_password && (
                                        <span className="ca-pill warn" title="must rotate password at next login">pwd!</span>
                                    )}
                                </td>
                                <td className="ca-dim">{dateTime(m.last_login)}</td>
                            </tr>
                        );
                    })}
                    {rows.length === 0 && (
                        <tr>
                            <td colSpan={9} className="ca-empty">
                                <i className="codicon codicon-account" /> No managers
                            </td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );
}
