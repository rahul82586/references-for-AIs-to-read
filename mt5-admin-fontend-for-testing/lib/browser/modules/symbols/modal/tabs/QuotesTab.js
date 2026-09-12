"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.QuotesTab = void 0;
const React = require("react");
const SymbolDraftContext_1 = require("../SymbolDraftContext");
function QuotesTab() {
    const { draft, setDraft } = (0, SymbolDraftContext_1.useSymbolDraft)();
    const updateField = (field, val) => {
        setDraft(prev => ({ ...prev, [field]: val }));
    };
    const isExchangeOrDOM = draft.market_depth > 0 || draft.calculation.toLowerCase().includes('exchange');
    const isFutures = draft.calculation.toLowerCase().includes('futures');
    return (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', height: '100%', gap: 10, fontSize: 11 } },
        React.createElement("div", { style: { display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', borderRadius: 4 } },
            React.createElement("div", { style: { width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#2ecc71', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' } }, "Q"),
            React.createElement("div", { style: { flex: 1, opacity: 0.9, lineHeight: 1.3 } }, "Configure pricing data feeds transmission, subscription delays, and automated quote filtration thresholds.")),
        React.createElement("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 24px', flex: 1 } },
            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 6 } },
                React.createElement("div", { style: { fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 } }, "Ingestion Transmission"),
                React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', height: 20 } },
                    React.createElement("input", { type: "checkbox", checked: draft.allow_realtime_quotes, onChange: e => updateField('allow_realtime_quotes', e.target.checked) }),
                    "Allow real-time quotes feeds"),
                React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', height: 20 } },
                    React.createElement("input", { type: "checkbox", checked: draft.save_raw_prices, onChange: e => updateField('save_raw_prices', e.target.checked) }),
                    "Save raw, unfiltered ticks"),
                React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', height: 20 } },
                    React.createElement("input", { type: "checkbox", checked: draft.receive_market_stats, onChange: e => updateField('receive_market_stats', e.target.checked) }),
                    "Receive market statistics"),
                React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', height: 20, opacity: isFutures ? 1 : 0.6 } },
                    React.createElement("input", { type: "checkbox", disabled: !isFutures, checked: isFutures && draft.allow_negative_prices, onChange: e => updateField('allow_negative_prices', e.target.checked) }),
                    "Allow negative prices (Futures)"),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8, marginTop: 4 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Delay (mins):"),
                    React.createElement("input", { className: "adm-input", type: "number", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.delay_subscriptions, onChange: e => updateField('delay_subscriptions', parseInt(e.target.value) || 0) })),
                React.createElement("div", { style: { fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginTop: 4, marginBottom: 2 } }, "Gap Pricing Checks"),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Gap Level (pts):"),
                    React.createElement("input", { className: "adm-input", type: "number", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.gap_mode_level, onChange: e => updateField('gap_mode_level', parseInt(e.target.value) || 0) })),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Disable ticks:"),
                    React.createElement("input", { className: "adm-input", type: "number", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.gap_disable_ticks, onChange: e => updateField('gap_disable_ticks', parseInt(e.target.value) || 0) }))),
            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 6, opacity: isExchangeOrDOM ? 0.6 : 1 } },
                React.createElement("div", { style: { fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 } },
                    "Spam Filtration ",
                    isExchangeOrDOM && '(N/A for DOM)'),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 110, textAlign: 'right', opacity: 0.8 } }, "Soft level (pts):"),
                    React.createElement("input", { disabled: isExchangeOrDOM, className: "adm-input", type: "number", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.soft_filter_level, onChange: e => updateField('soft_filter_level', parseInt(e.target.value) || 0) })),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 110, textAlign: 'right', opacity: 0.8 } }, "Soft repeats:"),
                    React.createElement("input", { disabled: isExchangeOrDOM, className: "adm-input", type: "number", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.soft_filter_repeats, onChange: e => updateField('soft_filter_repeats', parseInt(e.target.value) || 0) })),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 110, textAlign: 'right', opacity: 0.8 } }, "Hard level (pts):"),
                    React.createElement("input", { disabled: isExchangeOrDOM, className: "adm-input", type: "number", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.hard_filter_level, onChange: e => updateField('hard_filter_level', parseInt(e.target.value) || 0) })),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 110, textAlign: 'right', opacity: 0.8 } }, "Hard repeats:"),
                    React.createElement("input", { disabled: isExchangeOrDOM, className: "adm-input", type: "number", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.hard_filter_repeats, onChange: e => updateField('hard_filter_repeats', parseInt(e.target.value) || 0) })),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 110, textAlign: 'right', opacity: 0.8 } }, "Discard level (pts):"),
                    React.createElement("input", { disabled: isExchangeOrDOM, className: "adm-input", type: "number", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.discard_filter_level, onChange: e => updateField('discard_filter_level', parseInt(e.target.value) || 0) })),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 110, textAlign: 'right', opacity: 0.8 } }, "Min spread limit:"),
                    React.createElement("input", { disabled: isExchangeOrDOM, className: "adm-input", type: "number", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.min_spread, onChange: e => updateField('min_spread', parseInt(e.target.value) || 0) })),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 110, textAlign: 'right', opacity: 0.8 } }, "Max spread limit:"),
                    React.createElement("input", { disabled: isExchangeOrDOM, className: "adm-input", type: "number", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.max_spread, onChange: e => updateField('max_spread', parseInt(e.target.value) || 0) }))))));
}
exports.QuotesTab = QuotesTab;
//# sourceMappingURL=QuotesTab.js.map