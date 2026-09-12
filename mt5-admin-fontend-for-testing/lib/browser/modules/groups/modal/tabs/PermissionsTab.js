"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.PermissionsTab = void 0;
const React = require("react");
const GroupDraftContext_1 = require("../GroupDraftContext");
const SIGNALS_OPTIONS = [
    { value: 'disabled', label: 'Disabled' },
    { value: 'all', label: 'Enable all signals' },
    { value: 'own_only', label: 'From my servers only' }
];
const TRANSFER_OPTIONS = [
    { value: 'disabled', label: 'Disabled' },
    { value: 'same_details', label: 'Same name + email only' },
    { value: 'subgroup', label: 'Within same subgroup' },
    { value: 'subgroup_name', label: 'Same name in group' }
];
function PermissionsTab() {
    const { draft, setDraft } = (0, GroupDraftContext_1.useGroupDraft)();
    const updateField = (field, val) => {
        setDraft(prev => ({ ...prev, [field]: val }));
    };
    const isDemo = draft.name.toLowerCase().includes('demo');
    const isNetting = draft.risk_management_model === 'netting';
    return (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', height: '100%', gap: 10, fontSize: 11 } },
        React.createElement("div", { style: { display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', borderRadius: 4 } },
            React.createElement("div", { style: { width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#e74c3c', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' } }, "P"),
            React.createElement("div", { style: { flex: 1, opacity: 0.9, lineHeight: 1.3 } }, "Configure client permissions, algorithmic trading policies (EAs), maximum active order/position limits, and internal wallet funds transfers.")),
        React.createElement("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 24px', flex: 1, marginTop: 4 } },
            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 6 } },
                React.createElement("div", { style: { fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 } }, "Trading Limits & Finances"),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Max Symbols:"),
                    React.createElement("input", { className: "adm-input", type: "number", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, placeholder: "0 = unlimited", value: draft.max_symbols, onChange: e => updateField('max_symbols', parseInt(e.target.value) || 0) })),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Max Positions:"),
                    React.createElement("input", { className: "adm-input", type: "number", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, placeholder: "0 = unlimited", value: draft.max_positions, onChange: e => updateField('max_positions', parseInt(e.target.value) || 0) })),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Max Orders:"),
                    React.createElement("input", { className: "adm-input", type: "number", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, placeholder: "0 = unlimited", value: draft.max_orders, onChange: e => updateField('max_orders', parseInt(e.target.value) || 0) })),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "History Scope:"),
                    React.createElement("select", { className: "adm-select", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.available_history, onChange: e => updateField('available_history', e.target.value) },
                        React.createElement("option", { value: "All" }, "All history logs"),
                        React.createElement("option", { value: "1 month" }, "1 Month"),
                        React.createElement("option", { value: "3 months" }, "3 Months"),
                        React.createElement("option", { value: "6 months" }, "6 Months"),
                        React.createElement("option", { value: "1 year" }, "1 Year"))),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Interest Rate (%):"),
                    React.createElement("input", { className: "adm-input", type: "number", step: "0.01", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, placeholder: "e.g. 2.50", value: draft.interest_rate, onChange: e => updateField('interest_rate', parseFloat(e.target.value) || 0) })),
                isDemo && (React.createElement(React.Fragment, null,
                    React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                        React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Default Deposit:"),
                        React.createElement("input", { className: "adm-input", type: "number", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.default_deposit, onChange: e => updateField('default_deposit', parseInt(e.target.value) || 10000) })),
                    React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                        React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Default Leverage:"),
                        React.createElement("input", { className: "adm-input", type: "number", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, placeholder: "1:100", value: draft.default_leverage, onChange: e => updateField('default_leverage', parseInt(e.target.value) || 100) })),
                    React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                        React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Expiry days:"),
                        React.createElement("input", { className: "adm-input", type: "number", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, placeholder: "Inactivity limit", value: draft.inactivity_days, onChange: e => updateField('inactivity_days', parseInt(e.target.value) || 0) }))))),
            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 6 } },
                React.createElement("div", { style: { fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 } }, "Signals & Algorithm Policies"),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 90, textAlign: 'right', opacity: 0.8 } }, "Signals:"),
                    React.createElement("select", { className: "adm-select", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.trade_signals_mode, onChange: e => updateField('trade_signals_mode', e.target.value) }, SIGNALS_OPTIONS.map(o => React.createElement("option", { key: o.value, value: o.value }, o.label)))),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 90, textAlign: 'right', opacity: 0.8 } }, "Transfers:"),
                    React.createElement("select", { className: "adm-select", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.transfer_funds_mode, onChange: e => updateField('transfer_funds_mode', e.target.value) }, TRANSFER_OPTIONS.map(o => React.createElement("option", { key: o.value, value: o.value }, o.label)))),
                React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', height: 18, marginTop: 4 } },
                    React.createElement("input", { type: "checkbox", checked: draft.enable_swaps, onChange: e => updateField('enable_swaps', e.target.checked) }),
                    "Enable swaps calculations and charging"),
                React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', height: 18 } },
                    React.createElement("input", { type: "checkbox", checked: draft.enable_trailing_stops, onChange: e => updateField('enable_trailing_stops', e.target.checked) }),
                    "Allow client terminal trailing stops"),
                React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', height: 18 } },
                    React.createElement("input", { type: "checkbox", checked: draft.enable_ea_trading, onChange: e => updateField('enable_ea_trading', e.target.checked) }),
                    "Allow Expert Advisor algorithmic trading"),
                React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', height: 18, opacity: isNetting ? 1 : 0.5 } },
                    React.createElement("input", { type: "checkbox", disabled: !isNetting, checked: isNetting && draft.fifo_rule, onChange: e => updateField('fifo_rule', e.target.checked) }),
                    "Close positions strictly by FIFO rules"),
                React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', height: 18, opacity: !isNetting ? 1 : 0.5 } },
                    React.createElement("input", { type: "checkbox", disabled: isNetting, checked: !isNetting && draft.prohibit_hedge, onChange: e => updateField('prohibit_hedge', e.target.checked) }),
                    "Prohibit hedge positions (hedging only)"),
                React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', height: 18 } },
                    React.createElement("input", { type: "checkbox", checked: draft.deal_cost_calc, onChange: e => updateField('deal_cost_calc', e.target.checked) }),
                    "Enable real-time deal cost calculation")))));
}
exports.PermissionsTab = PermissionsTab;
//# sourceMappingURL=PermissionsTab.js.map