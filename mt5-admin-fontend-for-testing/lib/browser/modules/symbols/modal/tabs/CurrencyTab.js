"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CurrencyTab = void 0;
const React = require("react");
const SymbolDraftContext_1 = require("../SymbolDraftContext");
function CurrencyTab() {
    const { draft, setDraft } = (0, SymbolDraftContext_1.useSymbolDraft)();
    const updateField = (field, val) => {
        setDraft(prev => ({ ...prev, [field]: val }));
    };
    return (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', height: '100%', gap: 12, fontSize: 11 } },
        React.createElement("div", { style: { display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '8px 12px', borderRadius: 4 } },
            React.createElement("div", { style: { width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#3498db', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' } }, "\u20AC"),
            React.createElement("div", { style: { flex: 1, opacity: 0.9, lineHeight: 1.3 } }, "Specify financial accounting currencies. Base currency represents the asset units, Profit currency calculates trade returns, and Margin currency holds collateral.")),
        React.createElement("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 24px', marginTop: 8 } },
            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 8 } },
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Base currency:"),
                    React.createElement("input", { className: "adm-input", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, required: true, placeholder: "e.g. EUR", value: draft.base_currency, onChange: e => updateField('base_currency', e.target.value.toUpperCase()) })),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Profit currency:"),
                    React.createElement("input", { className: "adm-input", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, required: true, placeholder: "e.g. USD", value: draft.profit_currency, onChange: e => updateField('profit_currency', e.target.value.toUpperCase()) }))),
            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 8 } },
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Margin currency:"),
                    React.createElement("input", { className: "adm-input", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, required: true, placeholder: "e.g. EUR", value: draft.margin_currency, onChange: e => updateField('margin_currency', e.target.value.toUpperCase()) })))),
        React.createElement("div", { className: "adm-hint", style: { marginTop: 'auto', marginBottom: 0, padding: '8px 12px' } },
            React.createElement("i", { className: "codicon codicon-info", style: { marginRight: 6 } }),
            "Platform Lock: Standard fiat currencies decimal precision is fixed by system conventions. Overrides apply only to custom cryptocurrencies.")));
}
exports.CurrencyTab = CurrencyTab;
//# sourceMappingURL=CurrencyTab.js.map