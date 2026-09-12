"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DayScheduleEditor = void 0;
const React = require("react");
function DayScheduleEditor({ day, schedule, onClose, onSave }) {
    const [quotes, setQuotes] = React.useState([...schedule.quotes]);
    const [trade, setTrade] = React.useState([...schedule.trade]);
    const [separateTrade, setSeparateTrade] = React.useState(schedule.separateTrade);
    const handleAddBlock = (type) => {
        const newBlock = { start: '08:00', end: '17:00' };
        if (type === 'quotes') {
            setQuotes([...quotes, newBlock]);
        }
        else {
            setTrade([...trade, newBlock]);
        }
    };
    const handleRemoveBlock = (type, index) => {
        if (type === 'quotes') {
            setQuotes(quotes.filter((_, i) => i !== index));
        }
        else {
            setTrade(trade.filter((_, i) => i !== index));
        }
    };
    const handleTimeChange = (type, index, field, value) => {
        if (type === 'quotes') {
            const next = [...quotes];
            next[index] = { ...next[index], [field]: value };
            setQuotes(next);
        }
        else {
            const next = [...trade];
            next[index] = { ...next[index], [field]: value };
            setTrade(next);
        }
    };
    const handleSave = () => {
        onSave({
            quotes,
            trade: separateTrade ? trade : [...quotes],
            separateTrade
        });
    };
    return (React.createElement("div", { className: "adm-modal-overlay", style: { zIndex: 1200 }, onClick: onClose },
        React.createElement("div", { className: "adm-modal", style: { width: 440 }, onClick: e => e.stopPropagation() },
            React.createElement("div", { className: "adm-modal-header" },
                React.createElement("h2", null,
                    "Edit Time Sessions \u2014 ",
                    day),
                React.createElement("button", { type: "button", className: "adm-modal-close", onClick: onClose }, "\u00D7")),
            React.createElement("div", { className: "adm-modal-body", style: { display: 'flex', flexDirection: 'column', gap: 14 } },
                React.createElement("div", null,
                    React.createElement("div", { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 } },
                        React.createElement("span", { style: { fontSize: 12, fontWeight: 'bold' } }, "Quotes Sessions"),
                        React.createElement("button", { type: "button", className: "adm-btn", style: { fontSize: 10, padding: '2px 8px' }, onClick: () => handleAddBlock('quotes') },
                            React.createElement("i", { className: "codicon codicon-add" }),
                            " Add Session")),
                    quotes.length === 0 ? (React.createElement("div", { style: { padding: 12, background: 'var(--theia-sideBarSectionHeader-background)', fontSize: 11, textAlign: 'center', opacity: 0.6 } }, "No quotes session active. Market will be offline.")) : (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 6 } }, quotes.map((block, idx) => (React.createElement("div", { key: idx, style: { display: 'flex', gap: 8, alignItems: 'center' } },
                        React.createElement("input", { className: "adm-input", type: "time", style: { width: 110, fontSize: 11, padding: 3, height: 22 }, value: block.start, onChange: e => handleTimeChange('quotes', idx, 'start', e.target.value) }),
                        React.createElement("span", null, "to"),
                        React.createElement("input", { className: "adm-input", type: "time", style: { width: 110, fontSize: 11, padding: 3, height: 22 }, value: block.end, onChange: e => handleTimeChange('quotes', idx, 'end', e.target.value) }),
                        React.createElement("button", { type: "button", className: "adm-icon-btn", onClick: () => handleRemoveBlock('quotes', idx) },
                            React.createElement("i", { className: "codicon codicon-trash", style: { color: 'var(--theia-errorForeground)' } })))))))),
                React.createElement("div", { className: "adm-form-row", style: { flexDirection: 'row', alignItems: 'center', gap: 8, borderTop: '1px solid var(--theia-border)', paddingTop: 10 } },
                    React.createElement("input", { type: "checkbox", id: "sep-trade", checked: separateTrade, onChange: e => setSeparateTrade(e.target.checked) }),
                    React.createElement("label", { htmlFor: "sep-trade", style: { cursor: 'pointer', margin: 0, fontSize: 12 } }, "Enable separate trading sessions (different from quotes)")),
                separateTrade && (React.createElement("div", null,
                    React.createElement("div", { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 } },
                        React.createElement("span", { style: { fontSize: 12, fontWeight: 'bold' } }, "Trade Sessions"),
                        React.createElement("button", { type: "button", className: "adm-btn", style: { fontSize: 10, padding: '2px 8px' }, onClick: () => handleAddBlock('trade') },
                            React.createElement("i", { className: "codicon codicon-add" }),
                            " Add Session")),
                    trade.length === 0 ? (React.createElement("div", { style: { padding: 12, background: 'var(--theia-sideBarSectionHeader-background)', fontSize: 11, textAlign: 'center', opacity: 0.6 } }, "No trading session active. Clients cannot execute trades.")) : (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 6 } }, trade.map((block, idx) => (React.createElement("div", { key: idx, style: { display: 'flex', gap: 8, alignItems: 'center' } },
                        React.createElement("input", { className: "adm-input", type: "time", style: { width: 110, fontSize: 11, padding: 3, height: 22 }, value: block.start, onChange: e => handleTimeChange('trade', idx, 'start', e.target.value) }),
                        React.createElement("span", null, "to"),
                        React.createElement("input", { className: "adm-input", type: "time", style: { width: 110, fontSize: 11, padding: 3, height: 22 }, value: block.end, onChange: e => handleTimeChange('trade', idx, 'end', e.target.value) }),
                        React.createElement("button", { type: "button", className: "adm-icon-btn", onClick: () => handleRemoveBlock('trade', idx) },
                            React.createElement("i", { className: "codicon codicon-trash", style: { color: 'var(--theia-errorForeground)' } })))))))))),
            React.createElement("div", { className: "adm-modal-footer" },
                React.createElement("button", { type: "button", className: "adm-btn adm-btn-primary", onClick: handleSave }, "Save changes"),
                React.createElement("button", { type: "button", className: "adm-btn", onClick: onClose }, "Cancel")))));
}
exports.DayScheduleEditor = DayScheduleEditor;
//# sourceMappingURL=DayScheduleEditor.js.map