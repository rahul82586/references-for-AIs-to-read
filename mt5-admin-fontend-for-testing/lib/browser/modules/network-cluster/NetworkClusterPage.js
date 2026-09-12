"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.NetworkBackupPage = exports.NetworkDataCentersPage = exports.NetworkServersPage = exports.NetworkClusterOverview = void 0;
// @ts-nocheck
const React = require("react");
/** Network Cluster — Main overview: lists all servers with Type/Address/CPU/Connections */
function NetworkClusterOverview() {
    const [statuses, setStatuses] = React.useState({
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
        }
        catch {
            nextStatuses.trade = false;
        }
        // 2. History Server (port 8002)
        try {
            await fetch('http://localhost:8002/', { method: 'HEAD' });
            nextStatuses.history = true;
        }
        catch {
            nextStatuses.history = false;
        }
        // 3. Access Server (port 8001)
        try {
            await fetch('http://localhost:8001/', { method: 'HEAD' });
            nextStatuses.access = true;
        }
        catch {
            nextStatuses.access = false;
        }
        // 4. Backup Server (port 8004)
        try {
            await fetch('http://localhost:8004/', { method: 'HEAD' });
            nextStatuses.backup = true;
        }
        catch {
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
        { id: '2', type: 'History Server', name: 'History-01', address: '127.0.0.1:8002', pubAddr: '127.0.0.1', conns: statuses.history ? 1 : 0, basePri: 1, curPri: 1, cpu: statuses.history ? 4 : 0, online: statuses.history },
        { id: '3', type: 'Access Server', name: 'Access-01', address: '127.0.0.1:8001', pubAddr: '127.0.0.1', conns: statuses.access ? 3 : 0, basePri: 1, curPri: 1, cpu: statuses.access ? 2 : 0, online: statuses.access },
        { id: '4', type: 'Backup Server', name: 'Backup-01', address: '127.0.0.1:8004', pubAddr: '127.0.0.1', conns: 0, basePri: 2, curPri: 2, cpu: 0, online: statuses.backup },
    ];
    const [sel, setSel] = React.useState(null);
    return (React.createElement("div", { className: "adm-page" },
        React.createElement("div", { className: "adm-toolbar" },
            React.createElement("button", { className: "adm-btn", onClick: checkServerStatus, title: "Reload statuses" },
                React.createElement("i", { className: "codicon codicon-refresh" }),
                " Refresh")),
        React.createElement("div", { className: "adm-hint" },
            React.createElement("i", { className: "codicon codicon-info" }),
            "Red icon means the server is offline or unreachable on its configured local port."),
        React.createElement("div", { className: "adm-table-wrap" },
            React.createElement("table", { className: "adm-table" },
                React.createElement("thead", null,
                    React.createElement("tr", null,
                        React.createElement("th", null),
                        React.createElement("th", null, "Type"),
                        React.createElement("th", null, "Server Name"),
                        React.createElement("th", null, "Address"),
                        React.createElement("th", null, "Public Addresses"),
                        React.createElement("th", null, "ID"),
                        React.createElement("th", null, "Connections"),
                        React.createElement("th", null, "Base Priority"),
                        React.createElement("th", null, "Current Priority"),
                        React.createElement("th", null, "CPU %"))),
                React.createElement("tbody", null, servers.map(s => (React.createElement("tr", { key: s.id, className: sel === s.id ? 'selected' : '', onClick: () => setSel(s.id) },
                    React.createElement("td", null,
                        React.createElement("span", { className: `adm-status-dot ${s.online ? 'online' : 'offline'}` })),
                    React.createElement("td", null,
                        React.createElement("span", { className: "adm-tag" }, s.type)),
                    React.createElement("td", null,
                        React.createElement("strong", null, s.name)),
                    React.createElement("td", null,
                        React.createElement("code", { className: "adm-code" }, s.address)),
                    React.createElement("td", null,
                        React.createElement("code", { className: "adm-code" }, s.pubAddr)),
                    React.createElement("td", null, s.id),
                    React.createElement("td", { className: "adm-num" }, s.conns),
                    React.createElement("td", { className: "adm-num" }, s.basePri),
                    React.createElement("td", { className: "adm-num" }, s.curPri),
                    React.createElement("td", null,
                        React.createElement("div", { className: "adm-cpu-bar" },
                            React.createElement("div", { className: "adm-cpu-fill", style: { width: `${s.cpu}%`, background: s.cpu > 80 ? 'var(--theia-errorForeground)' : s.cpu > 50 ? '#f0ad4e' : '#27ae60' } }),
                            React.createElement("span", null,
                                s.cpu,
                                "%"))))))))),
        React.createElement("div", { className: "adm-statusbar" },
            React.createElement("span", null,
                "Servers: ",
                servers.length),
            React.createElement("span", { className: "adm-sep" }, "|"),
            React.createElement("span", { style: { color: '#27ae60' } },
                "Online: ",
                servers.filter(s => s.online).length),
            React.createElement("span", { className: "adm-sep" }, "|"),
            React.createElement("span", { style: { color: 'var(--theia-errorForeground)' } },
                "Offline: ",
                servers.filter(s => !s.online).length))));
}
exports.NetworkClusterOverview = NetworkClusterOverview;
/** Network Cluster — Servers: configure individual server settings (Common / Network / Service tabs) */
function NetworkServersPage() {
    const [tab, setTab] = React.useState('common');
    const serverTypes = ['Main Trade Server', 'Trade Server', 'History Server', 'Access Server', 'Backup Server'];
    return (React.createElement("div", { className: "adm-page" },
        React.createElement("div", { className: "adm-toolbar" },
            React.createElement("button", { className: "adm-btn adm-btn-primary", disabled: true },
                React.createElement("i", { className: "codicon codicon-add" }),
                " Add Server")),
        React.createElement("div", { className: "adm-tabs" }, ['common', 'network', 'service'].map(t => (React.createElement("button", { key: t, className: `adm-tab ${tab === t ? 'active' : ''}`, onClick: () => setTab(t) }, t.charAt(0).toUpperCase() + t.slice(1))))),
        tab === 'common' && (React.createElement("div", { className: "adm-form-body" },
            React.createElement("div", { className: "adm-form-section" }, "General"),
            React.createElement("div", { className: "adm-form-row" },
                React.createElement("label", null, "Type"),
                React.createElement("select", { className: "adm-select", disabled: true }, serverTypes.map(t => React.createElement("option", { key: t }, t)))),
            React.createElement("div", { className: "adm-form-row" },
                React.createElement("label", null, "Name"),
                React.createElement("input", { className: "adm-input", readOnly: true, defaultValue: "MetaQuotes-Demo" })),
            React.createElement("div", { className: "adm-form-row" },
                React.createElement("label", null, "ID"),
                React.createElement("input", { className: "adm-input", readOnly: true, defaultValue: "1", type: "number" })),
            React.createElement("div", { className: "adm-form-row" },
                React.createElement("label", null, "Password"),
                React.createElement("input", { className: "adm-input", readOnly: true, type: "password", value: "******" })),
            React.createElement("div", { className: "adm-form-section" }, "Geo Location"),
            React.createElement("div", { className: "adm-form-row" },
                React.createElement("label", null, "Latitude"),
                React.createElement("input", { className: "adm-input", readOnly: true, defaultValue: "0.0000" })),
            React.createElement("div", { className: "adm-form-row" },
                React.createElement("label", null, "Longitude"),
                React.createElement("input", { className: "adm-input", readOnly: true, defaultValue: "0.0000" })))),
        tab === 'network' && (React.createElement("div", { className: "adm-form-body" },
            React.createElement("div", { className: "adm-form-section" }, "IPv4 Settings"),
            React.createElement("div", { className: "adm-form-row" },
                React.createElement("label", null, "Listen Address (IPv4)"),
                React.createElement("input", { className: "adm-input", readOnly: true, defaultValue: "0.0.0.0:8000" })),
            React.createElement("div", { className: "adm-form-row" },
                React.createElement("label", null, "Outgoing Address (IPv4)"),
                React.createElement("input", { className: "adm-input", readOnly: true, defaultValue: "127.0.0.1:0" })),
            React.createElement("div", { className: "adm-form-section" }, "Public Addresses"),
            React.createElement("div", { className: "adm-form-row" },
                React.createElement("label", null, "Public Addresses"),
                React.createElement("textarea", { className: "adm-input", readOnly: true, style: { height: 40 }, defaultValue: "127.0.0.1" })))),
        tab === 'service' && (React.createElement("div", { className: "adm-form-body" },
            React.createElement("div", { className: "adm-form-section" }, "Service Management"),
            React.createElement("div", { className: "adm-form-row" },
                React.createElement("label", null, "Service Name"),
                React.createElement("input", { className: "adm-input", readOnly: true, defaultValue: "MT5TradeServer" })),
            React.createElement("div", { className: "adm-form-row" },
                React.createElement("label", null, "Startup Type"),
                React.createElement("select", { className: "adm-select", disabled: true },
                    React.createElement("option", null, "Automatic")))))));
}
exports.NetworkServersPage = NetworkServersPage;
/** Network Cluster — Data Centers */
function NetworkDataCentersPage() {
    const dcs = [
        { id: '1', name: 'DC-Main', region: 'US-East', ip: '127.0.0.1', servers: 3, latency: 1 },
    ];
    return (React.createElement("div", { className: "adm-page" },
        React.createElement("div", { className: "adm-table-wrap" },
            React.createElement("table", { className: "adm-table" },
                React.createElement("thead", null,
                    React.createElement("tr", null,
                        React.createElement("th", null, "Name"),
                        React.createElement("th", null, "Region"),
                        React.createElement("th", null, "IP Address"),
                        React.createElement("th", null, "Servers"),
                        React.createElement("th", null, "Latency (ms)"))),
                React.createElement("tbody", null, dcs.map(dc => (React.createElement("tr", { key: dc.id },
                    React.createElement("td", null,
                        React.createElement("strong", null, dc.name)),
                    React.createElement("td", null, dc.region),
                    React.createElement("td", null,
                        React.createElement("code", { className: "adm-code" }, dc.ip)),
                    React.createElement("td", null, dc.servers),
                    React.createElement("td", { className: "adm-num", style: { color: '#27ae60' } },
                        dc.latency,
                        " ms"))))))),
        React.createElement("div", { className: "adm-statusbar" },
            React.createElement("span", null,
                "Data Centers: ",
                dcs.length))));
}
exports.NetworkDataCentersPage = NetworkDataCentersPage;
/** Network Cluster — Backup Server configuration */
function NetworkBackupPage() {
    return (React.createElement("div", { className: "adm-page" },
        React.createElement("div", { className: "adm-form-body", style: { maxWidth: 520 } },
            React.createElement("div", { className: "adm-form-section" }, "Backup Server Settings"),
            React.createElement("div", { className: "adm-form-row" },
                React.createElement("label", null, "Backup Server"),
                React.createElement("select", { className: "adm-select", disabled: true },
                    React.createElement("option", null, "Backup-01 (127.0.0.1:8004)"))),
            React.createElement("div", { className: "adm-form-row" },
                React.createElement("label", null, "Backed Up Server"),
                React.createElement("select", { className: "adm-select", disabled: true },
                    React.createElement("option", null, "Main Trade Server"))),
            React.createElement("div", { className: "adm-form-row" },
                React.createElement("label", null, "Status"),
                React.createElement("span", { style: { color: 'var(--theia-errorForeground)', padding: '3px 0' } }, "\u25CF Offline")))));
}
exports.NetworkBackupPage = NetworkBackupPage;
//# sourceMappingURL=NetworkClusterPage.js.map