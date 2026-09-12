"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SwapsTab = void 0;
const React = require("react");
const SymbolDraftContext_1 = require("../SymbolDraftContext");
const SWAP_TYPES = [
    { value: 'points', label: 'In points of spread' },
    { value: 'money', label: 'In absolute money values' },
    { value: 'percent', label: 'In percentage terms of position value' },
    { value: 'reopen_close', label: 'Reopen by Close Price' },
    { value: 'reopen_bid', label: 'Reopen by Bid Price' }
];
const DAYS_IN_YEAR = [360, 365, 366];
function SwapsTab() {
    const { draft, setDraft } = (0, SymbolDraftContext_1.useSymbolDraft)();
    const updateField = (field, val) => {
        setDraft(prev => ({ ...prev, [field]: val }));
    };
    const handleMultiplierChange = (day, value) => {
        const nextMult = { ...draft.swap_multipliers, [day]: value };
        updateField('swap_multipliers', nextMult);
    };
    const applyForexPreset = () => {
        setDraft(prev => ({
            ...prev,
            swap_multipliers: {
                'Mon': 1, 'Tue': 1, 'Wed': 3, 'Thu': 1, 'Fri': 1, 'Sat': 0, 'Sun': 0
            }
        }));
    };
    const applyAllWeekPreset = () => {
        setDraft(prev => ({
            ...prev,
            swap_multipliers: {
                'Mon': 1, 'Tue': 1, 'Wed': 1, 'Thu': 1, 'Fri': 1, 'Sat': 1, 'Sun': 1
            }
        }));
    };
    return (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', height: '100%', gap: 10, fontSize: 11 } },
        React.createElement("div", { style: { display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', borderRadius: 4 } },
            React.createElement("div", { style: { width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#e67e22', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' } }, "S"),
            React.createElement("div", { style: { flex: 1, opacity: 0.9, lineHeight: 1.3 } }, "Configure automatic rollover swap interest charges, day multipliers, and holiday accrual rules.")),
        React.createElement("div", { style: { display: 'grid', gridTemplateColumns: '1.1fr 0.9fr', gap: '8px 24px', flex: 1, marginTop: 4 } },
            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 6 } },
                React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, cursor: 'pointer', height: 20 } },
                    React.createElement("input", { type: "checkbox", checked: draft.enable_swaps, onChange: e => updateField('enable_swaps', e.target.checked) }),
                    React.createElement("strong", null, "Enable rollover swaps calculation")),
                React.createElement("fieldset", { disabled: !draft.enable_swaps, style: { border: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: 6 } },
                    React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                        React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Swap Type:"),
                        React.createElement("select", { className: "adm-select", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.swap_type, onChange: e => updateField('swap_type', e.target.value) }, SWAP_TYPES.map(t => React.createElement("option", { key: t.value, value: t.value }, t.label)))),
                    React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                        React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Long rate:"),
                        React.createElement("input", { className: "adm-input", type: "number", step: "0.01", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.swap_long, onChange: e => updateField('swap_long', parseFloat(e.target.value) || 0.0) })),
                    React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                        React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Short rate:"),
                        React.createElement("input", { className: "adm-input", type: "number", step: "0.01", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.swap_short, onChange: e => updateField('swap_short', parseFloat(e.target.value) || 0.0) })),
                    React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                        React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Yearly base:"),
                        React.createElement("select", { className: "adm-select", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.swap_days_in_year, onChange: e => updateField('swap_days_in_year', parseInt(e.target.value) || 360) }, DAYS_IN_YEAR.map(d => React.createElement("option", { key: d, value: d },
                            d,
                            " Days")))),
                    draft.swap_type === 'money' && (React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                        React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Currency Basis:"),
                        React.createElement("select", { className: "adm-select", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.currency, onChange: e => updateField('currency', e.target.value) },
                            React.createElement("option", { value: "base" }, "Base currency"),
                            React.createElement("option", { value: "margin" }, "Margin currency"),
                            React.createElement("option", { value: "profit" }, "Profit currency")))))),
            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 6, opacity: draft.enable_swaps ? 1 : 0.6 } },
                React.createElement("div", { style: { fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 } }, "Accrual Multipliers"),
                React.createElement("div", { style: { display: 'flex', gap: 4, marginBottom: 6 } },
                    React.createElement("button", { type: "button", className: "adm-btn", style: { flex: 1, fontSize: 10, padding: '2px 4px' }, disabled: !draft.enable_swaps, onClick: applyForexPreset }, "Wed x3"),
                    React.createElement("button", { type: "button", className: "adm-btn", style: { flex: 1, fontSize: 10, padding: '2px 4px' }, disabled: !draft.enable_swaps, onClick: applyAllWeekPreset }, "All x1")),
                React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 4 } }, Object.keys(draft.swap_multipliers).map(day => (React.createElement("div", { key: day, style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 40, opacity: 0.8, textTransform: 'capitalize' } },
                        day,
                        ":"),
                    React.createElement("input", { disabled: !draft.enable_swaps, className: "adm-input", type: "number", style: { flex: 1, height: 18, padding: '2px 4px', fontSize: 11, textAlign: 'center' }, value: draft.swap_multipliers[day], onChange: e => handleMultiplierChange(day, parseInt(e.target.value) || 0) })))))))));
}
exports.SwapsTab = SwapsTab;
//# sourceMappingURL=SwapsTab.js.map