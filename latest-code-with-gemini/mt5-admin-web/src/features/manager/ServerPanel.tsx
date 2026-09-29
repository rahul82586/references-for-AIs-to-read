import * as React from 'react';
import { API } from '../../services/api';
import { dateTime } from '../../shared/format';

/** Manager → Server node: trade-server state via the Manager API service family. */
export function ServerPanel(): React.ReactElement {
    const [info, setInfo] = React.useState<any | null>(null);
    const [error, setError] = React.useState<string | null>(null);
    const [session, setSession] = React.useState<any>({ connected: false });
    const [form, setForm] = React.useState({ server: 'localhost:8000', login: '1000', password: '' });
    const [busy, setBusy] = React.useState(false);

    const refresh = React.useCallback(() => {
        API.getManagerServerInfo().then(setInfo).catch((e) => setError(String(e?.message ?? e)));
        API.managerSessionInfo().then(setSession).catch(() => setSession({ connected: false }));
    }, []);

    React.useEffect(refresh, [refresh]);

    const connect = async () => {
        setBusy(true); setError(null);
        try {
            const s = await API.managerConnect(form.server, Number(form.login), form.password);
            setSession({ connected: true, ...s });
        } catch (e: any) { setError(String(e?.message ?? e)); }
        finally { setBusy(false); }
    };

    const disconnect = async () => {
        setBusy(true);
        try { await API.managerDisconnect(); setSession({ connected: false }); }
        catch (e: any) { setError(String(e?.message ?? e)); }
        finally { setBusy(false); }
    };

    const kv = (l: string, v: React.ReactNode) => (
        <div className="ca-kv"><span className="ca-k">{l}</span><span className="ca-v">{v ?? '—'}</span></div>
    );

    return (
        <div className="ca-page">
            <div className="ca-toolbar">
                <div className="ca-request">
                    <i className="codicon codicon-server" />
                    <span style={{ fontSize: 12 }}>Trade server state — Manager API service family</span>
                </div>
            </div>
            {error && (
                <div className="ca-banner gap"><i className="codicon codicon-warning" /><span>{error}</span></div>
            )}
            <div className="ca-main" style={{ padding: 16, overflow: 'auto' }}>
                <div className="ca-box">
                    <div className="ca-box-title"><i className="codicon codicon-plug" /> Manager session</div>
                    <div className="ca-connect-row">
                        <label>Server<input className="adm-input" value={form.server} onChange={(e) => setForm({ ...form, server: e.target.value })} /></label>
                        <label>Login<input className="adm-input" value={form.login} onChange={(e) => setForm({ ...form, login: e.target.value })} /></label>
                        <label>Password<input className="adm-input" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></label>
                        {session.connected
                            ? <button className="wb-btn secondary ca-danger" disabled={busy} onClick={() => void disconnect()}>Disconnect</button>
                            : <button className="wb-btn" disabled={busy || !form.password} onClick={() => void connect()}>{busy ? 'Connecting…' : 'Connect'}</button>}
                    </div>
                    <div className="wb-settings-hint">
                        {session.connected
                            ? <>Connected as <b>{session.user_login}</b> · access <b>{session.access_level}</b> · session <code className="adm-code">{session.session_id}</code></>
                            : 'Manager login required before OrderSend/OrderClose/dealing actions (Manager API Connect family).'}
                    </div>
                </div>
                {info && (
                    <div className="ca-kv-grid">
                        {kv('Connected', info.connected ? <span className="ca-pill ok">yes</span> : <span className="ca-pill off">no</span>)}
                        {kv('Ping', `${info.ping_ms ?? info.ping ?? '—'} ms`)}
                        {kv('Version', info.version)}
                        {kv('Memory', `${info.memory_mb ?? info.memory ?? '—'} MB`)}
                        {kv('Started', dateTime(info.start_time))}
                        {kv('Server time', dateTime(info.server_time))}
                        {kv('Accounts online', info.accounts_online)}
                        {kv('Pump modes', <span className="ca-dim">{info.pump_modes}</span>)}
                    </div>
                )}
            </div>
        </div>
    );
}
