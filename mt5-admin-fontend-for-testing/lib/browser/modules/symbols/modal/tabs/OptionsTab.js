"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.OptionsTab = void 0;
const React = require("react");
const SymbolDraftContext_1 = require("../SymbolDraftContext");
function OptionsTab() {
    const { draft, setDraft } = (0, SymbolDraftContext_1.useSymbolDraft)();
    const updateField = (field, val) => {
        setDraft(prev => ({ ...prev, [field]: val }));
    };
    return (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', height: '100%', gap: 10, fontSize: 11 } },
        React.createElement("div", { style: { display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', borderRadius: 4 } },
            React.createElement("div", { style: { width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#e67e22', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' } }, "O"),
            React.createElement("div", { style: { flex: 1, opacity: 0.9, lineHeight: 1.3 } }, "Configure options derivative settings. Options can be Call or Put, and structured as American or European exercise styles.")),
        React.createElement("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 24px', flex: 1, marginTop: 8 } },
            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 8 } },
                React.createElement("div", { style: { fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 } }, "Option Classification"),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 90, textAlign: 'right', opacity: 0.8 } }, "Option Type:"),
                    React.createElement("div", { style: { flex: 1, display: 'flex', gap: 12 } },
                        React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 4, cursor: 'pointer' } },
                            React.createElement("input", { type: "radio", name: "opt-type", checked: draft.option_type === 'call', onChange: () => updateField('option_type', 'call') }),
                            "Call"),
                        React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 4, cursor: 'pointer' } },
                            React.createElement("input", { type: "radio", name: "opt-type", checked: draft.option_type === 'put', onChange: () => updateField('option_type', 'put') }),
                            "Put"))),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 90, textAlign: 'right', opacity: 0.8 } }, "Option Style:"),
                    React.createElement("div", { style: { flex: 1, display: 'flex', gap: 12 } },
                        React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 4, cursor: 'pointer' } },
                            React.createElement("input", { type: "radio", name: "opt-style", checked: draft.option_style === 'american', onChange: () => updateField('option_style', 'american') }),
                            "American"),
                        React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 4, cursor: 'pointer' } },
                            React.createElement("input", { type: "radio", name: "opt-style", checked: draft.option_style === 'european', onChange: () => updateField('option_style', 'european') }),
                            "European")))),
            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 8 } },
                React.createElement("div", { style: { fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 } }, "Pricing Limits"),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 90, textAlign: 'right', opacity: 0.8 } }, "Strike Price:"),
                    React.createElement("input", { className: "adm-input", type: "number", step: "0.0001", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, placeholder: "Strike boundary price", value: draft.strike_price, onChange: e => updateField('strike_price', parseFloat(e.target.value) || 0.0) }))))));
}
exports.OptionsTab = OptionsTab;
//# sourceMappingURL=OptionsTab.js.map