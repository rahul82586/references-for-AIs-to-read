"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ConnectStep = void 0;
const React = require("react");
function ConnectStep({ data, onChange }) {
    return (React.createElement("div", { className: "adm-modal-body", style: { display: 'flex', flexDirection: 'column', gap: 12 } },
        React.createElement("div", { className: "adm-hint", style: { background: 'var(--theia-sideBarSectionHeader-background)', color: 'var(--theia-foreground)', margin: '0 0 12px 0' } },
            React.createElement("i", { className: "codicon codicon-info" }),
            " Connect to a remote MetaTrader 4/5 server to download symbols configurations directly."),
        React.createElement("div", { className: "adm-form-row" },
            React.createElement("label", { className: "required" }, "Server Type"),
            React.createElement("select", { className: "adm-select", value: data.serverType, onChange: e => onChange({ serverType: e.target.value }) },
                React.createElement("option", { value: "MT5" }, "MetaTrader 5 Server"),
                React.createElement("option", { value: "MT4" }, "MetaTrader 4 Server"))),
        React.createElement("div", { className: "adm-form-row" },
            React.createElement("label", { className: "required" }, "Server IP / Address"),
            React.createElement("input", { className: "adm-input", required: true, placeholder: "e.g. 192.168.1.100:443", value: data.address, onChange: e => onChange({ address: e.target.value }) })),
        React.createElement("div", { className: "adm-form-row" },
            React.createElement("label", { className: "required" }, "Login / Manager ID"),
            React.createElement("input", { className: "adm-input", type: "number", required: true, placeholder: "1000", value: data.login, onChange: e => onChange({ login: e.target.value }) })),
        React.createElement("div", { className: "adm-form-row" },
            React.createElement("label", { className: "required" }, "Password"),
            React.createElement("input", { className: "adm-input", type: "password", required: true, placeholder: "\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022", value: data.password, onChange: e => onChange({ password: e.target.value }) })),
        data.serverType === 'MT5' && (React.createElement(React.Fragment, null,
            React.createElement("div", { className: "adm-form-row", style: { flexDirection: 'row', alignItems: 'center', gap: 8, marginTop: 8 } },
                React.createElement("input", { type: "checkbox", id: "use-cert", checked: data.useCert, onChange: e => onChange({ useCert: e.target.checked }) }),
                React.createElement("label", { htmlFor: "use-cert", style: { cursor: 'pointer', margin: 0 } }, "Use certificate file (.pfx) for extended login authorization")),
            data.useCert && (React.createElement("div", { style: { paddingLeft: 20, display: 'flex', flexDirection: 'column', gap: 10 } },
                React.createElement("div", { className: "adm-form-row" },
                    React.createElement("label", { className: "required" }, "Certificate File"),
                    React.createElement("input", { className: "adm-input", type: "text", placeholder: "Click to choose certificate metadata...", value: data.certFile, onChange: e => onChange({ certFile: e.target.value }) })),
                React.createElement("div", { className: "adm-form-row" },
                    React.createElement("label", { className: "required" }, "Certificate Password"),
                    React.createElement("input", { className: "adm-input", type: "password", placeholder: "Cert key password", value: data.certPassword, onChange: e => onChange({ certPassword: e.target.value }) }))))))));
}
exports.ConnectStep = ConnectStep;
//# sourceMappingURL=ConnectStep.js.map