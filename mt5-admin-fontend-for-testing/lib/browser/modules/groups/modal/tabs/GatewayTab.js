"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.GatewayTab = void 0;
const React = require("react");
const GroupDraftContext_1 = require("../GroupDraftContext");
const api_1 = require("../../../api");
function GatewayTab() {
    const { draft, setDraft } = (0, GroupDraftContext_1.useGroupDraft)();
    const [gateways, setGateways] = React.useState([]);
    React.useEffect(() => {
        api_1.API.getGateways()
            .then((data) => {
            const filtered = data.filter((g) => !g.type.startsWith('Feeder_'));
            setGateways(filtered);
        })
            .catch(console.error);
    }, []);
    const updateField = (field, val) => {
        setDraft(prev => ({ ...prev, [field]: val }));
    };
    const selectedGateway = gateways.find(g => g.id === draft.gateway_id);
    return (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', height: '100%', gap: 10, fontSize: 11 } },
        React.createElement("div", { style: { display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', borderRadius: 4 } },
            React.createElement("div", { style: { width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#3498db', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' } }, "G"),
            React.createElement("div", { style: { flex: 1, opacity: 0.9, lineHeight: 1.3 } }, "Define loopback interface routing servers settings for secure history/trading component tunnels. Trading operations of this group will be routed to A-Book channels through the gateway selected below.")),
        React.createElement("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 24px', flex: 1, marginTop: 4 } },
            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 10 } },
                React.createElement("div", { style: { fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 } }, "ECN Route Assignment"),
                React.createElement("div", { className: "adm-form-row" },
                    React.createElement("label", null, "Default A-Book Gateway"),
                    React.createElement("select", { className: "adm-select", style: { width: '100%', height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.gateway_id || '', onChange: e => updateField('gateway_id', e.target.value ? parseInt(e.target.value) : undefined) },
                        React.createElement("option", { value: "" }, "None (B-Book Local Matching)"),
                        gateways.map(g => (React.createElement("option", { key: g.id, value: g.id },
                            g.name,
                            " (",
                            g.type,
                            ")"))))),
                React.createElement("div", { className: "adm-form-row" },
                    React.createElement("label", null, "Gateway Server (IP:Port)"),
                    React.createElement("input", { className: "adm-input", style: { width: '100%', height: 20 }, disabled: true, value: selectedGateway ? `${selectedGateway.host || 'localhost'}:${selectedGateway.port || '8003'}` : '—' }))),
            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 10 } },
                React.createElement("div", { style: { fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 } }, "Gateway Authentication Details"),
                React.createElement("div", { className: "adm-form-row" },
                    React.createElement("label", null, "Gateway Login"),
                    React.createElement("input", { className: "adm-input", style: { width: '100%', height: 20 }, disabled: true, value: selectedGateway ? (selectedGateway.username || 'Numeric Login') : '—' })),
                React.createElement("div", { className: "adm-form-row" },
                    React.createElement("label", null, "Gateway Password"),
                    React.createElement("input", { className: "adm-input", type: "password", style: { width: '100%', height: 20 }, disabled: true, value: selectedGateway ? '••••••••' : '', placeholder: selectedGateway ? 'Loopback key' : '—' }))))));
}
exports.GatewayTab = GatewayTab;
//# sourceMappingURL=GatewayTab.js.map