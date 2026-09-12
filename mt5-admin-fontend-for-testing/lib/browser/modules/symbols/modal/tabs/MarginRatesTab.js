"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.MarginRatesTab = void 0;
const React = require("react");
const SymbolDraftContext_1 = require("../SymbolDraftContext");
function MarginRatesTab() {
    const { draft, setDraft } = (0, SymbolDraftContext_1.useSymbolDraft)();
    const updateField = (field, val) => {
        setDraft(prev => ({ ...prev, [field]: val }));
    };
    return (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', height: '100%', gap: 10, fontSize: 11 } },
        React.createElement("div", { style: { display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', borderRadius: 4 } },
            React.createElement("div", { style: { width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#9b59b6', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' } }, "%"),
            React.createElement("div", { style: { flex: 1, opacity: 0.9, lineHeight: 1.3 } }, "Specify margin requirements multiplier rates per transaction order type and stock collateral valuations.")),
        React.createElement("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 24px', flex: 1, marginTop: 4 } },
            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 6 } },
                React.createElement("div", { style: { display: 'flex', gap: 8, fontWeight: 'bold', fontSize: 10, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 } },
                    React.createElement("span", { style: { width: 90 } }, "Order Type"),
                    React.createElement("span", { style: { flex: 1, textAlign: 'center' } }, "Initial"),
                    React.createElement("span", { style: { flex: 1, textAlign: 'center' } }, "Maint")),
                React.createElement("div", { style: { display: 'flex', gap: 8, alignItems: 'center' } },
                    React.createElement("span", { style: { width: 90, opacity: 0.8 } }, "Market Buy:"),
                    React.createElement("input", { className: "adm-input", type: "number", step: "0.1", style: { flex: 1, height: 20, padding: '2px 4px', fontSize: 11 }, value: draft.rate_market_buy_init, onChange: e => updateField('rate_market_buy_init', parseFloat(e.target.value) || 1.0) }),
                    React.createElement("input", { className: "adm-input", type: "number", step: "0.1", style: { flex: 1, height: 20, padding: '2px 4px', fontSize: 11 }, value: draft.rate_market_buy_maint, onChange: e => updateField('rate_market_buy_maint', parseFloat(e.target.value) || 1.0) })),
                React.createElement("div", { style: { display: 'flex', gap: 8, alignItems: 'center' } },
                    React.createElement("span", { style: { width: 90, opacity: 0.8 } }, "Market Sell:"),
                    React.createElement("input", { className: "adm-input", type: "number", step: "0.1", style: { flex: 1, height: 20, padding: '2px 4px', fontSize: 11 }, value: draft.rate_market_sell_init, onChange: e => updateField('rate_market_sell_init', parseFloat(e.target.value) || 1.0) }),
                    React.createElement("input", { className: "adm-input", type: "number", step: "0.1", style: { flex: 1, height: 20, padding: '2px 4px', fontSize: 11 }, value: draft.rate_market_sell_maint, onChange: e => updateField('rate_market_sell_maint', parseFloat(e.target.value) || 1.0) })),
                React.createElement("div", { style: { display: 'flex', gap: 8, alignItems: 'center' } },
                    React.createElement("span", { style: { width: 90, opacity: 0.8 } }, "Buy Limit:"),
                    React.createElement("input", { className: "adm-input", type: "number", step: "0.1", style: { flex: 1, height: 20, padding: '2px 4px', fontSize: 11 }, value: draft.rate_limit_buy_init, onChange: e => updateField('rate_limit_buy_init', parseFloat(e.target.value) || 1.0) }),
                    React.createElement("input", { className: "adm-input", type: "number", step: "0.1", style: { flex: 1, height: 20, padding: '2px 4px', fontSize: 11 }, value: draft.rate_limit_buy_maint, onChange: e => updateField('rate_limit_buy_maint', parseFloat(e.target.value) || 1.0) })),
                React.createElement("div", { style: { display: 'flex', gap: 8, alignItems: 'center' } },
                    React.createElement("span", { style: { width: 90, opacity: 0.8 } }, "Sell Limit:"),
                    React.createElement("input", { className: "adm-input", type: "number", step: "0.1", style: { flex: 1, height: 20, padding: '2px 4px', fontSize: 11 }, value: draft.rate_limit_sell_init, onChange: e => updateField('rate_limit_sell_init', parseFloat(e.target.value) || 1.0) }),
                    React.createElement("input", { className: "adm-input", type: "number", step: "0.1", style: { flex: 1, height: 20, padding: '2px 4px', fontSize: 11 }, value: draft.rate_limit_sell_maint, onChange: e => updateField('rate_limit_sell_maint', parseFloat(e.target.value) || 1.0) }))),
            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 6 } },
                React.createElement("div", { style: { display: 'flex', gap: 8, fontWeight: 'bold', fontSize: 10, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 } },
                    React.createElement("span", { style: { width: 90 } }, "Order Type"),
                    React.createElement("span", { style: { flex: 1, textAlign: 'center' } }, "Initial"),
                    React.createElement("span", { style: { flex: 1, textAlign: 'center' } }, "Maint")),
                React.createElement("div", { style: { display: 'flex', gap: 8, alignItems: 'center' } },
                    React.createElement("span", { style: { width: 90, opacity: 0.8 } }, "Stops (Buy/Sell):"),
                    React.createElement("input", { className: "adm-input", type: "number", step: "0.1", style: { flex: 1, height: 20, padding: '2px 4px', fontSize: 11 }, value: draft.rate_limit_buy_init, onChange: e => updateField('rate_limit_buy_init', parseFloat(e.target.value) || 1.0) }),
                    React.createElement("input", { className: "adm-input", type: "number", step: "0.1", style: { flex: 1, height: 20, padding: '2px 4px', fontSize: 11 }, value: draft.rate_limit_buy_maint, onChange: e => updateField('rate_limit_buy_maint', parseFloat(e.target.value) || 1.0) })),
                React.createElement("div", { style: { fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginTop: 4, marginBottom: 2 } }, "Collateral Values"),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 110, textAlign: 'right', opacity: 0.8 } }, "Liquidity Margin:"),
                    React.createElement("input", { className: "adm-input", type: "number", step: "0.01", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, placeholder: "0.00", value: draft.discard_filter_level, onChange: e => updateField('discard_filter_level', parseFloat(e.target.value) || 0.0) })),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 110, textAlign: 'right', opacity: 0.8 } }, "Currency Margin:"),
                    React.createElement("input", { className: "adm-input", type: "number", step: "0.01", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.delay_subscriptions, onChange: e => updateField('delay_subscriptions', parseFloat(e.target.value) || 0.0) }))))));
}
exports.MarginRatesTab = MarginRatesTab;
//# sourceMappingURL=MarginRatesTab.js.map