"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CommissionsTab = void 0;
const React = require("react");
const GroupDraftContext_1 = require("../GroupDraftContext");
const CommissionRuleDialog_1 = require("./commissions/CommissionRuleDialog");
function CommissionsTab() {
    const { draft, setDraft } = (0, GroupDraftContext_1.useGroupDraft)();
    const [selectedIdx, setSelectedIdx] = React.useState(null);
    const [showDialog, setShowDialog] = React.useState(false);
    const [editRule, setEditRule] = React.useState(null);
    const handleAdd = () => {
        setEditRule(null);
        setShowDialog(true);
    };
    const handleEdit = () => {
        if (selectedIdx === null)
            return;
        setEditRule(draft.commission_rules[selectedIdx]);
        setShowDialog(true);
    };
    const handleDelete = () => {
        if (selectedIdx === null)
            return;
        setDraft(prev => ({
            ...prev,
            commission_rules: prev.commission_rules.filter((_, idx) => idx !== selectedIdx)
        }));
        setSelectedIdx(null);
    };
    const handleSaveRule = (rule) => {
        setDraft(prev => {
            const nextRules = [...prev.commission_rules];
            if (editRule && selectedIdx !== null) {
                nextRules[selectedIdx] = rule;
            }
            else {
                nextRules.push(rule);
            }
            return { ...prev, commission_rules: nextRules };
        });
    };
    return (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', height: '100%', gap: 10, fontSize: 11 } },
        React.createElement("div", { style: { display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', borderRadius: 4 } },
            React.createElement("div", { style: { width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#e74c3c', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' } }, "%"),
            React.createElement("div", { style: { flex: 1, opacity: 0.9, lineHeight: 1.3 } }, "Configure automated client deal commission rules, charging formulas, and target symbol pattern constraints.")),
        React.createElement("div", { className: "adm-toolbar", style: { padding: '0px 0px 4px 0px', borderBottom: 'none', display: 'flex', gap: 6, flexShrink: 0 } },
            React.createElement("button", { type: "button", className: "adm-btn adm-btn-primary", style: { padding: '2px 8px', height: 22, fontSize: 11 }, onClick: handleAdd },
                React.createElement("i", { className: "codicon codicon-add" }),
                " Add Commission"),
            React.createElement("button", { type: "button", className: "adm-btn", style: { padding: '2px 8px', height: 22, fontSize: 11 }, disabled: selectedIdx === null, onClick: handleEdit },
                React.createElement("i", { className: "codicon codicon-edit" }),
                " Edit"),
            React.createElement("button", { type: "button", className: "adm-btn adm-btn-danger", style: { padding: '2px 8px', height: 22, fontSize: 11 }, disabled: selectedIdx === null, onClick: handleDelete },
                React.createElement("i", { className: "codicon codicon-trash" }),
                " Delete")),
        React.createElement("div", { className: "adm-table-wrap", style: { border: '1px solid var(--theia-border)', flex: 1, overflowY: 'auto' } },
            React.createElement("table", { className: "adm-table", style: { fontSize: 11 } },
                React.createElement("thead", null,
                    React.createElement("tr", null,
                        React.createElement("th", null, "Name"),
                        React.createElement("th", null, "Symbols Pattern"),
                        React.createElement("th", null, "Rate"),
                        React.createElement("th", null, "Type"))),
                React.createElement("tbody", null, draft.commission_rules.length === 0 ? (React.createElement("tr", null,
                    React.createElement("td", { colSpan: 4, style: { textAlign: 'center', opacity: 0.6, padding: 20 } }, "No commissions configured for this group. Deals will run with zero charges."))) : (draft.commission_rules.map((rule, idx) => (React.createElement("tr", { key: idx, className: selectedIdx === idx ? 'selected' : '', onClick: () => setSelectedIdx(idx), onDoubleClick: handleEdit, style: { height: 22 } },
                    React.createElement("td", null,
                        React.createElement("strong", null, rule.name)),
                    React.createElement("td", null,
                        React.createElement("code", null, rule.symbols)),
                    React.createElement("td", null, rule.rate),
                    React.createElement("td", null,
                        React.createElement("span", { className: "adm-tag", style: { padding: '1px 4px', fontSize: 9 } }, rule.type === 'points' ? 'points' : rule.type === 'percent' ? 'percent' : 'money/lot'))))))))),
        showDialog && (React.createElement(CommissionRuleDialog_1.CommissionRuleDialog, { rule: editRule, onClose: () => setShowDialog(false), onSave: handleSaveRule }))));
}
exports.CommissionsTab = CommissionsTab;
//# sourceMappingURL=CommissionsTab.js.map