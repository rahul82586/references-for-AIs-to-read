"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ExecutionTab = void 0;
const React = require("react");
const SymbolDraftContext_1 = require("../SymbolDraftContext");
function ExecutionTab() {
    const { draft, setDraft } = (0, SymbolDraftContext_1.useSymbolDraft)();
    const updateField = (field, val) => {
        setDraft(prev => ({ ...prev, [field]: val }));
    };
    return (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', height: '100%', gap: 10, fontSize: 11 } },
        React.createElement("div", { style: { display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', borderRadius: 4 } },
            React.createElement("div", { style: { width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#34495e', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' } }, "E"),
            React.createElement("div", { style: { flex: 1, opacity: 0.9, lineHeight: 1.3 } }, "Configure execution modes and order routing paths for trade request processing.")),
        React.createElement("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 24px', flex: 1, marginTop: 8 } },
            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 8 } },
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Execution mode:"),
                    React.createElement("select", { className: "adm-select", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.execution_mode, onChange: e => updateField('execution_mode', e.target.value) },
                        React.createElement("option", { value: "Instant" }, "Instant Execution"),
                        React.createElement("option", { value: "Request" }, "Request Execution"),
                        React.createElement("option", { value: "Market" }, "Market Execution"),
                        React.createElement("option", { value: "Exchange" }, "Exchange Execution"))),
                draft.execution_mode === 'Instant' && (React.createElement(React.Fragment, null,
                    React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                        React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Max dev (pts):"),
                        React.createElement("input", { className: "adm-input", type: "number", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.instant_max_time_dev, onChange: e => updateField('instant_max_time_dev', parseInt(e.target.value) || 0) })),
                    React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, cursor: 'pointer', paddingLeft: 10 } },
                        React.createElement("input", { type: "checkbox", checked: draft.instant_fast_requotes, onChange: e => updateField('instant_fast_requotes', e.target.checked) }),
                        "Auto-confirm requotes within dev"))),
                draft.execution_mode === 'Request' && (React.createElement(React.Fragment, null,
                    React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                        React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Timeout (sec):"),
                        React.createElement("input", { className: "adm-input", type: "number", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.request_timeout, onChange: e => updateField('request_timeout', parseInt(e.target.value) || 10) })),
                    React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, cursor: 'pointer', paddingLeft: 10 } },
                        React.createElement("input", { type: "checkbox", checked: draft.request_confirm, onChange: e => updateField('request_confirm', e.target.checked) }),
                        "Require manager check first")))),
            React.createElement("div", { style: { display: 'flex', flexDirection: 'column' } },
                draft.execution_mode === 'Market' && (React.createElement("div", { className: "adm-hint", style: { margin: 0, padding: '8px 12px' } },
                    React.createElement("i", { className: "codicon codicon-info", style: { marginRight: 6 } }),
                    React.createElement("strong", null, "Market Mode:"),
                    " Trades execute at the next available server price. Requotes are disabled because prices are accepted upfront.")),
                draft.execution_mode === 'Exchange' && (React.createElement("div", { className: "adm-hint", style: { margin: 0, padding: '8px 12px', borderLeft: '3px solid #e67e22' } },
                    React.createElement("i", { className: "codicon codicon-info", style: { marginRight: 6, color: '#e67e22' } }),
                    React.createElement("strong", null, "Exchange Mode:"),
                    " Routed directly to liquidity providers. Limit and freeze boundaries are bypassed, leaving filling choices to the exchange order book.")),
                draft.execution_mode === 'Instant' && (React.createElement("div", { className: "adm-hint", style: { margin: 0, padding: '8px 12px' } },
                    React.createElement("i", { className: "codicon codicon-info", style: { marginRight: 6 } }),
                    React.createElement("strong", null, "Instant Mode:"),
                    " Order executes exactly at the requested price. If the price moves beyond client-side deviation, the broker returns a requote.")),
                draft.execution_mode === 'Request' && (React.createElement("div", { className: "adm-hint", style: { margin: 0, padding: '8px 12px' } },
                    React.createElement("i", { className: "codicon codicon-info", style: { marginRight: 6 } }),
                    React.createElement("strong", null, "Request Mode:"),
                    " Client asks for quotes first, then sends confirmation to execute. Best suited for manual voice or high-ticket desk dealers."))))));
}
exports.ExecutionTab = ExecutionTab;
//# sourceMappingURL=ExecutionTab.js.map