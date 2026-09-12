"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.TradeTab = void 0;
const React = require("react");
const SymbolDraftContext_1 = require("../SymbolDraftContext");
const CALC_MODES = [
    'Forex',
    'Forex No Leverage',
    'CFD',
    'CFD Index',
    'CFD Leverage',
    'Exchange Stocks',
    'Exchange MOEX Stocks',
    'Exchange Bonds',
    'Exchange MOEXBonds',
    'Exchange Futures',
    'Exchange FORTS Futures',
    'Exchange Option',
    'Collateral'
];
const TRADE_MODES = [
    { value: 'disabled', label: 'Disabled (No trading)' },
    { value: 'long_only', label: 'Long Only (Buys allowed)' },
    { value: 'short_only', label: 'Short Only (Sells allowed)' },
    { value: 'close_only', label: 'Close Only (Liquidation only)' },
    { value: 'full', label: 'Full Access (Long & Short)' }
];
function TradeTab() {
    const { draft, setDraft } = (0, SymbolDraftContext_1.useSymbolDraft)();
    const updateField = (field, val) => {
        setDraft(prev => ({ ...prev, [field]: val }));
    };
    const handleCheckboxArrayChange = (field, value, checked) => {
        const current = draft[field] || [];
        const next = checked ? [...current, value] : current.filter(item => item !== value);
        updateField(field, next);
    };
    const isForex = draft.calculation.startsWith('Forex');
    return (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', height: '100%', gap: 10, fontSize: 11 } },
        React.createElement("div", { style: { display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', borderRadius: 4 } },
            React.createElement("div", { style: { width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#e74c3c', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' } }, "T"),
            React.createElement("div", { style: { flex: 1, opacity: 0.9, lineHeight: 1.3 } }, "Set up contract size, calculation models, trade session modes, and volume order parameters.")),
        React.createElement("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 24px', flex: 1 } },
            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 6 } },
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Contract size:"),
                    React.createElement("input", { className: "adm-input", type: "number", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.contract_size, onChange: e => updateField('contract_size', parseFloat(e.target.value) || 0.0) })),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Tick size:"),
                    React.createElement("input", { className: "adm-input", type: "number", step: "0.00001", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.margin_initial, onChange: e => updateField('margin_initial', parseFloat(e.target.value) || 1.0) })),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Tick value:"),
                    React.createElement("input", { className: "adm-input", type: "number", step: "0.01", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.margin_maintenance, onChange: e => updateField('margin_maintenance', parseFloat(e.target.value) || 1.0) })),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Calculation:"),
                    React.createElement("select", { className: "adm-select", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.calculation, onChange: e => updateField('calculation', e.target.value) }, CALC_MODES.map(c => React.createElement("option", { key: c, value: c }, c)))),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Trade mode:"),
                    React.createElement("select", { className: "adm-select", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.trade_mode, onChange: e => updateField('trade_mode', e.target.value) }, TRADE_MODES.map(m => React.createElement("option", { key: m.value, value: m.value }, m.label)))),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Limit/Stop level:"),
                    React.createElement("input", { className: "adm-input", type: "number", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.limit_stop_level, onChange: e => updateField('limit_stop_level', parseInt(e.target.value) || 0) })),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Freeze level:"),
                    React.createElement("input", { className: "adm-input", type: "number", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.freeze_level, onChange: e => updateField('freeze_level', parseInt(e.target.value) || 0) }))),
            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 6 } },
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "GTC mode:"),
                    React.createElement("select", { className: "adm-select", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.gtc_mode, onChange: e => updateField('gtc_mode', parseInt(e.target.value) || 0) },
                        React.createElement("option", { value: 0 }, "Day canceled"),
                        React.createElement("option", { value: 1 }, "Kept GTC"),
                        React.createElement("option", { value: 2 }, "Kept except SL/TP"))),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Max quote delay:"),
                    React.createElement("input", { className: "adm-input", type: "number", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.max_quote_delay, onChange: e => updateField('max_quote_delay', parseInt(e.target.value) || 15) })),
                React.createElement("div", { style: { display: 'flex', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Filling flags:"),
                    React.createElement("div", { style: { display: 'flex', gap: 8, fontSize: 10 } },
                        React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 2 } },
                            React.createElement("input", { type: "checkbox", checked: draft.orders_allowed.includes('fok'), onChange: e => handleCheckboxArrayChange('orders_allowed', 'fok', e.target.checked) }),
                            " FOK"),
                        React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 2 } },
                            React.createElement("input", { type: "checkbox", checked: draft.orders_allowed.includes('ioc'), onChange: e => handleCheckboxArrayChange('orders_allowed', 'ioc', e.target.checked) }),
                            " IOC"),
                        React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 2 } },
                            React.createElement("input", { type: "checkbox", checked: draft.orders_allowed.includes('boc'), onChange: e => handleCheckboxArrayChange('orders_allowed', 'boc', e.target.checked) }),
                            " BOC"))),
                React.createElement("div", { style: { display: 'flex', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Expirations:"),
                    React.createElement("div", { style: { display: 'flex', gap: 8, fontSize: 10 } },
                        React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 2 } },
                            React.createElement("input", { type: "checkbox", checked: draft.expiration_flags.includes('gtc'), onChange: e => handleCheckboxArrayChange('expiration_flags', 'gtc', e.target.checked) }),
                            " GTC"),
                        React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 2 } },
                            React.createElement("input", { type: "checkbox", checked: draft.expiration_flags.includes('day'), onChange: e => handleCheckboxArrayChange('expiration_flags', 'day', e.target.checked) }),
                            " Day"),
                        React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 2 } },
                            React.createElement("input", { type: "checkbox", checked: draft.expiration_flags.includes('time'), onChange: e => handleCheckboxArrayChange('expiration_flags', 'time', e.target.checked) }),
                            " Time"))),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Volumes (min/max):"),
                    React.createElement("div", { style: { flex: 1, display: 'flex', gap: 4 } },
                        React.createElement("input", { className: "adm-input", type: "number", step: "0.01", style: { flex: 1, height: 20, padding: '2px 4px', fontSize: 11 }, value: draft.min_volume, onChange: e => updateField('min_volume', parseFloat(e.target.value) || 0.01) }),
                        React.createElement("input", { className: "adm-input", type: "number", step: "0.01", style: { flex: 1, height: 20, padding: '2px 4px', fontSize: 11 }, value: draft.max_volume, onChange: e => updateField('max_volume', parseFloat(e.target.value) || 100.0) }))),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Volume step:"),
                    React.createElement("input", { className: "adm-input", type: "number", step: "0.01", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.step_volume, onChange: e => updateField('step_volume', parseFloat(e.target.value) || 0.01) })),
                isForex && (React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Profit conversion:"),
                    React.createElement("select", { className: "adm-select", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.limit_volume, onChange: e => updateField('limit_volume', parseInt(e.target.value) || 0) },
                        React.createElement("option", { value: 0 }, "By deals records"),
                        React.createElement("option", { value: 1 }, "By real-time rates"))))))));
}
exports.TradeTab = TradeTab;
//# sourceMappingURL=TradeTab.js.map