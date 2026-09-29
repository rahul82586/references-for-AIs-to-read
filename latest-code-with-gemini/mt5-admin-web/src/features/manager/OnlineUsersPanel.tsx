import * as React from 'react';
import { API } from '../../services/api';
import { dateTime } from '../../shared/format';

/** Manager → Clients and Orders → Online Users (PUMP_MODE_ACTIVITY). */
export function OnlineUsersPanel(): React.ReactElement {
    const [rows, setRows] = React.useState<any[]>([]);
    const [error, setError] = React.useState<string | null>(null);

    React.useEffect(() => {
        API.getOnlineUsers().then(setRows).catch((e) => setError(String(e?.message ?? e)));
    }, []);

    return (
        <div className="ca-page">
            {error && <div className="ca-banner gap"><i className="codicon codicon-warning" /><span>{error}</span></div>}
            <div className="ca-main">
                <div className="ca-table-wrap">
                    <table className="adm-table ca-table">
                        <thead>
                            <tr>
                                <th>Login</th><th>Name</th><th>Group</th><th>IP</th>
                                <th>Terminal</th><th>Connected</th><th className="num">Ping</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows.map((u) => (
                                <tr key={u.login}>
                                    <td><code className="adm-code">{u.login}</code></td>
                                    <td className="ca-name">{u.name}</td>
                                    <td><code className="adm-code ca-group">{u.group}</code></td>
                                    <td className="ca-dim">{u.ip}</td>
                                    <td className="ca-dim">{u.terminal}</td>
                                    <td className="ca-dim">{dateTime(u.connected_at)}</td>
                                    <td className="num">{u.ping_ms} ms</td>
                                </tr>
                            ))}
                            {!error && rows.length === 0 && (
                                <tr><td colSpan={7} className="ca-empty"><i className="codicon codicon-pulse" /> No online users</td></tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
