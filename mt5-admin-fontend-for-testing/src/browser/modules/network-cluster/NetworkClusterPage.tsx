// @ts-nocheck
import * as React from 'react';

/** Network Cluster — Main overview: lists all servers with Type/Address/CPU/Connections */
export function NetworkClusterOverview(): React.ReactElement {
    const [statuses, setStatuses] = React.useState<Record<string, boolean>>({
        trade: false,
        history: false,
        access: false,
        backup: false
    });

    const checkServerStatus = async () => {
        const nextStatuses = { ...statuses };
        
        // 1. Trade Server (port 8000)
        try {
            const resp = await fetch('http://localhost:8000/accounts/10001', { method: 'HEAD' });
            nextStatuses.trade = true;
        } catch {
            nextStatuses.trade = false;
        }

        // 2. History Server (port 8002)
        try {
            await fetch('http://localhost:8002/', { method: 'HEAD' });
            nextStatuses.history = true;
        } catch {
            nextStatuses.history = false;
        }

        // 3. Access Server (port 8001)
        try {
            await fetch('http://localhost:8001/', { method: 'HEAD' });
            nextStatuses.access = true;
        } catch {
            nextStatuses.access = false;
        }

        // 4. Backup Server (port 8004)
        try {
            await fetch('http://localhost:8004/', { method: 'HEAD' });
            nextStatuses.backup = true;
        } catch {
            nextStatuses.backup = false;
        }

        setStatuses(nextStatuses);
    };

    React.useEffect(() => {
        checkServerStatus();
        const interval = setInterval(checkServerStatus, 5000);
        return () => clearInterval(interval);
    }, []);

    const servers = [
        { id: '1', type: 'Main Trade Server', name: 'MetaQuotes-Demo', address: '127.0.0.1:8000', pubAddr: '127.0.0.1', conns: statuses.trade ? 142 : 0, basePri: 1, curPri: 1, cpu: statuses.trade ? 8 : 0, online: statuses.trade },
        { id: '2', type: 'History Server',     name: 'History-01',     address: '127.0.0.1:8002',      pubAddr: '127.0.0.1',      conns: statuses.history ? 1 : 0,   basePri: 1, curPri: 1, cpu: statuses.history ? 4 : 0,  online: statuses.history },
        { id: '3', type: 'Access Server',      name: 'Access-01',      address: '127.0.0.1:8001',      pubAddr: '127.0.0.1',      conns: statuses.access ? 3 : 0,   basePri: 1, curPri: 1, cpu: statuses.access ? 2 : 0,  online: statuses.access },
        { id: '4', type: 'Backup Server',      name: 'Backup-01',      address: '127.0.0.1:8004',      pubAddr: '127.0.0.1',      conns: 0,   basePri: 2, curPri: 2, cpu: 0,  online: statuses.backup },
    ];

    const [sel, setSel] = React.useState<string | null>(null);

    return (
        <div className="adm-page">
            <div className="adm-toolbar">
                <button className="adm-btn" onClick={checkServerStatus} title="Reload statuses"><i className="codicon codicon-refresh" /> Refresh</button>
            </div>
            <div className="adm-hint"><i className="codicon codicon-info" />Red icon means the server is offline or unreachable on its configured local port.</div>
            <div className="adm-table-wrap">
                <table className="adm-table">
                    <thead><tr><th></th><th>Type</th><th>Server Name</th><th>Address</th><th>Public Addresses</th><th>ID</th><th>Connections</th><th>Base Priority</th><th>Current Priority</th><th>CPU %</th></tr></thead>
                    <tbody>
                        {servers.map(s => (
                            <tr key={s.id} className={sel === s.id ? 'selected' : ''} onClick={() => setSel(s.id)}>
                                <td><span className={`adm-status-dot ${s.online ? 'online' : 'offline'}`} /></td>
                                <td><span className="adm-tag">{s.type}</span></td>
                                <td><strong>{s.name}</strong></td>
                                <td><code className="adm-code">{s.address}</code></td>
                                <td><code className="adm-code">{s.pubAddr}</code></td>
                                <td>{s.id}</td>
                                <td className="adm-num">{s.conns}</td>
                                <td className="adm-num">{s.basePri}</td>
                                <td className="adm-num">{s.curPri}</td>
                                <td>
                                    <div className="adm-cpu-bar">
                                        <div className="adm-cpu-fill" style={{ width: `${s.cpu}%`, background: s.cpu > 80 ? 'var(--theia-errorForeground)' : s.cpu > 50 ? '#f0ad4e' : '#27ae60' }} />
                                        <span>{s.cpu}%</span>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            <div className="adm-statusbar">
                <span>Servers: {servers.length}</span>
                <span className="adm-sep">|</span>
                <span style={{ color: '#27ae60' }}>Online: {servers.filter(s => s.online).length}</span>
                <span className="adm-sep">|</span>
                <span style={{ color: 'var(--theia-errorForeground)' }}>Offline: {servers.filter(s => !s.online).length}</span>
            </div>
        </div>
    );
}

/** Network Cluster — Servers: configure individual server settings (Common / Network / Service tabs) */
export function NetworkServersPage(): React.ReactElement {
    const [tab, setTab] = React.useState<'common' | 'network' | 'service'>('common');
    const serverTypes = ['Main Trade Server', 'Trade Server', 'History Server', 'Access Server', 'Backup Server'];
    return (
        <div className="adm-page">
            <div className="adm-toolbar">
                <button className="adm-btn adm-btn-primary" disabled><i className="codicon codicon-add" /> Add Server</button>
            </div>
            <div className="adm-tabs">
                {(['common', 'network', 'service'] as const).map(t => (
                    <button key={t} className={`adm-tab ${tab === t ? 'active' : ''}`} onClick={() => setTab(t)}>{t.charAt(0).toUpperCase() + t.slice(1)}</button>
                ))}
            </div>
            {tab === 'common' && (
                <div className="adm-form-body">
                    <div className="adm-form-section">General</div>
                    <div className="adm-form-row"><label>Type</label><select className="adm-select" disabled>{serverTypes.map(t => <option key={t}>{t}</option>)}</select></div>
                    <div className="adm-form-row"><label>Name</label><input className="adm-input" readOnly defaultValue="MetaQuotes-Demo" /></div>
                    <div className="adm-form-row"><label>ID</label><input className="adm-input" readOnly defaultValue="1" type="number" /></div>
                    <div className="adm-form-row"><label>Password</label><input className="adm-input" readOnly type="password" value="******" /></div>
                    <div className="adm-form-section">Geo Location</div>
                    <div className="adm-form-row"><label>Latitude</label><input className="adm-input" readOnly defaultValue="0.0000" /></div>
                    <div className="adm-form-row"><label>Longitude</label><input className="adm-input" readOnly defaultValue="0.0000" /></div>
                </div>
            )}
            {tab === 'network' && (
                <div className="adm-form-body">
                    <div className="adm-form-section">IPv4 Settings</div>
                    <div className="adm-form-row"><label>Listen Address (IPv4)</label><input className="adm-input" readOnly defaultValue="0.0.0.0:8000" /></div>
                    <div className="adm-form-row"><label>Outgoing Address (IPv4)</label><input className="adm-input" readOnly defaultValue="127.0.0.1:0" /></div>
                    <div className="adm-form-section">Public Addresses</div>
                    <div className="adm-form-row"><label>Public Addresses</label><textarea className="adm-input" readOnly style={{ height: 40 }} defaultValue="127.0.0.1" /></div>
                </div>
            )}
            {tab === 'service' && (
                <div className="adm-form-body">
                    <div className="adm-form-section">Service Management</div>
                    <div className="adm-form-row"><label>Service Name</label><input className="adm-input" readOnly defaultValue="MT5TradeServer" /></div>
                    <div className="adm-form-row"><label>Startup Type</label><select className="adm-select" disabled><option>Automatic</option></select></div>
                </div>
            )}
        </div>
    );
}

/** Network Cluster — Data Centers */
export function NetworkDataCentersPage(): React.ReactElement {
    const dcs = [
        { id: '1', name: 'DC-Main', region: 'US-East',   ip: '127.0.0.1', servers: 3, latency: 1  },
    ];
    return (
        <div className="adm-page">
            <div className="adm-table-wrap">
                <table className="adm-table">
                    <thead><tr><th>Name</th><th>Region</th><th>IP Address</th><th>Servers</th><th>Latency (ms)</th></tr></thead>
                    <tbody>
                        {dcs.map(dc => (
                            <tr key={dc.id}>
                                <td><strong>{dc.name}</strong></td>
                                <td>{dc.region}</td>
                                <td><code className="adm-code">{dc.ip}</code></td>
                                <td>{dc.servers}</td>
                                <td className="adm-num" style={{ color: '#27ae60' }}>{dc.latency} ms</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            <div className="adm-statusbar"><span>Data Centers: {dcs.length}</span></div>
        </div>
    );
}

/** Network Cluster — Backup Server configuration */
export function NetworkBackupPage(): React.ReactElement {
    return (
        <div className="adm-page">
            <div className="adm-form-body" style={{ maxWidth: 520 }}>
                <div className="adm-form-section">Backup Server Settings</div>
                <div className="adm-form-row"><label>Backup Server</label><select className="adm-select" disabled><option>Backup-01 (127.0.0.1:8004)</option></select></div>
                <div className="adm-form-row"><label>Backed Up Server</label><select className="adm-select" disabled><option>Main Trade Server</option></select></div>
                <div className="adm-form-row"><label>Status</label><span style={{ color: 'var(--theia-errorForeground)', padding: '3px 0' }}>● Offline</span></div>
            </div>
        </div>
    );
}
