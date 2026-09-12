"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CommissionRuleDialog = void 0;
const React = require("react");
function CommissionRuleDialog({ rule, onClose, onSave }) {
    const [name, setName] = React.useState(rule ? rule.name : '');
    const [symbols, setSymbols] = React.useState(rule ? rule.symbols : '*');
    const [rate, setRate] = React.useState(rule ? String(rule.rate) : '0.0');
    const [type, setType] = React.useState(rule ? rule.type : 'money');
    const [error, setError] = React.useState(null);
    const handleSave = (e) => {
        e.preventDefault();
        setError(null);
        if (!name.trim()) {
            setError('Commission name is required.');
            return;
        }
        if (!symbols.trim()) {
            setError('Please define symbols pattern.');
            return;
        }
        onSave({
            name: name.trim(),
            symbols: symbols.trim(),
            rate: parseFloat(rate) || 0.0,
            type
        });
        onClose();
    };
    return (React.createElement("div", { className: "adm-modal-overlay", style: { zIndex: 1100 }, onClick: onClose },
        React.createElement("form", { className: "adm-modal", style: { width: 360 }, onClick: e => e.stopPropagation(), onSubmit: handleSave },
            React.createElement("div", { className: "adm-modal-header" },
                React.createElement("h2", null, rule ? 'Edit Commission Rule' : 'Add Commission Rule'),
                React.createElement("button", { type: "button", className: "adm-modal-close", onClick: onClose }, "\u00D7")),
            React.createElement("div", { className: "adm-modal-body" },
                error && (React.createElement("div", { className: "adm-hint", style: { background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)', margin: '0 0 12px 0' } },
                    React.createElement("i", { className: "codicon codicon-error" }),
                    " ",
                    error)),
                React.createElement("div", { className: "adm-form-row" },
                    React.createElement("label", { className: "required" }, "Name"),
                    React.createElement("input", { className: "adm-input", required: true, placeholder: "e.g. Standard Commission", value: name, onChange: e => setName(e.target.value) })),
                React.createElement("div", { className: "adm-form-row" },
                    React.createElement("label", { className: "required" }, "Symbols Pattern"),
                    React.createElement("input", { className: "adm-input", required: true, placeholder: "e.g. * or EURUSD", value: symbols, onChange: e => setSymbols(e.target.value) })),
                React.createElement("div", { className: "adm-form-row" },
                    React.createElement("label", null, "Commission Type"),
                    React.createElement("select", { className: "adm-select", value: type, onChange: e => setType(e.target.value) },
                        React.createElement("option", { value: "points" }, "In points of spread"),
                        React.createElement("option", { value: "percent" }, "In percentage of deal volume"),
                        React.createElement("option", { value: "money" }, "In absolute money value per lot"))),
                React.createElement("div", { className: "adm-form-row" },
                    React.createElement("label", null, "Rate / Fee"),
                    React.createElement("input", { className: "adm-input", type: "number", step: "0.001", value: rate, onChange: e => setRate(e.target.value) }))),
            React.createElement("div", { className: "adm-modal-footer" },
                React.createElement("button", { type: "submit", className: "adm-btn adm-btn-primary" }, "Save Commission"),
                React.createElement("button", { type: "button", className: "adm-btn", onClick: onClose }, "Cancel")))));
}
exports.CommissionRuleDialog = CommissionRuleDialog;
//# sourceMappingURL=CommissionRuleDialog.js.map