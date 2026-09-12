"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SymbolsTab = void 0;
const React = require("react");
const GroupDraftContext_1 = require("../GroupDraftContext");
const SymbolRuleDialog_1 = require("./symbols/SymbolRuleDialog");
const api_1 = require("../../../api");
function SymbolsTab() {
    const { draft, setDraft } = (0, GroupDraftContext_1.useGroupDraft)();
    const [symbolsList, setSymbolsList] = React.useState([]);
    const [selectedIdx, setSelectedIdx] = React.useState(null);
    // Modal states
    const [showDialog, setShowDialog] = React.useState(false);
    const [editRule, setEditRule] = React.useState(null);
    const loadSymbols = async () => {
        try {
            const data = await api_1.API.getSymbols();
            setSymbolsList(data.map((s) => s.symbol));
        }
        catch (e) {
            console.error('Failed to load active symbols checklist:', e);
        }
    };
    React.useEffect(() => {
        loadSymbols();
    }, []);
    const handleAdd = () => {
        setEditRule(null);
        setShowDialog(true);
    };
    const handleEdit = () => {
        if (selectedIdx === null)
            return;
        setEditRule(draft.symbol_rules[selectedIdx]);
        setShowDialog(true);
    };
    const handleDelete = () => {
        if (selectedIdx === null)
            return;
        setDraft(prev => ({
            ...prev,
            symbol_rules: prev.symbol_rules.filter((_, idx) => idx !== selectedIdx)
        }));
        setSelectedIdx(null);
    };
    const handleSaveRule = (rule) => {
        setDraft(prev => {
            const nextRules = [...prev.symbol_rules];
            if (editRule && selectedIdx !== null) {
                nextRules[selectedIdx] = rule;
            }
            else {
                nextRules.push(rule);
            }
            return { ...prev, symbol_rules: nextRules };
        });
    };
    // Helper to check if a strict symbol (no wildcard) exists in the database
    const checkSymbolExists = (pattern) => {
        if (pattern.includes('*') || pattern.includes('!'))
            return true; // pattern mask
        return symbolsList.includes(pattern);
    };
    return (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', height: '100%', gap: 10, fontSize: 11 } },
        React.createElement("div", { style: { display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', borderRadius: 4, flexShrink: 0 } },
            React.createElement("div", { style: { width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#2ecc71', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' } }, "S"),
            React.createElement("div", { style: { flex: 1, opacity: 0.9, lineHeight: 1.3 } }, "Configure financial instrument settings, trade permissions, overrides for spreads, commissions, and margin rates.")),
        React.createElement("div", { style: { display: 'flex', gap: 16, flex: 1, minHeight: 0 } },
            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 8, width: 90, flexShrink: 0 } },
                React.createElement("button", { type: "button", className: "adm-btn adm-btn-primary", onClick: handleAdd, style: { fontSize: 11, width: '100%', height: 24, padding: '2px 8px' } }, "Add"),
                React.createElement("button", { type: "button", className: "adm-btn", disabled: selectedIdx === null, onClick: handleEdit, style: { fontSize: 11, width: '100%', height: 24, padding: '2px 8px' } }, "Edit"),
                React.createElement("button", { type: "button", className: "adm-btn adm-btn-danger", disabled: selectedIdx === null, onClick: handleDelete, style: { fontSize: 11, width: '100%', height: 24, padding: '2px 8px' } }, "Delete")),
            React.createElement("div", { className: "adm-table-wrap", style: { border: '1px solid var(--theia-border)', flex: 1, overflowY: 'auto', height: '100%' } },
                React.createElement("table", { className: "adm-table", style: { fontSize: 11 } },
                    React.createElement("thead", null,
                        React.createElement("tr", null,
                            React.createElement("th", null, "Symbol Pattern"),
                            React.createElement("th", null, "Trade Status"),
                            React.createElement("th", null, "Spread Diff"),
                            React.createElement("th", null, "Commission"),
                            React.createElement("th", null, "Margin Multiplier"))),
                    React.createElement("tbody", null, draft.symbol_rules.map((rule, idx) => {
                        const exists = checkSymbolExists(rule.symbol);
                        return (React.createElement("tr", { key: idx, className: `${selectedIdx === idx ? 'selected' : ''} ${!exists ? 'adm-row-warning' : ''}`, onClick: () => setSelectedIdx(idx), onDoubleClick: handleEdit, style: { height: 22 }, title: !exists ? `Symbol "${rule.symbol}" does not exist in the active symbols database.` : '' },
                            React.createElement("td", null,
                                !exists && React.createElement("i", { className: "codicon codicon-warning", style: { color: '#f0ad4e', marginRight: 4 } }),
                                React.createElement("strong", null, rule.symbol)),
                            React.createElement("td", null,
                                React.createElement("span", { className: `adm-toggle ${rule.trade_allowed ? 'on' : 'off'}`, style: { padding: '1px 4px', fontSize: 9 } }, rule.trade_allowed ? '✓ ALLOW' : '✗ BLOCK')),
                            React.createElement("td", null,
                                rule.spread_diff > 0 ? `+${rule.spread_diff}` : rule.spread_diff,
                                " pts"),
                            React.createElement("td", null,
                                rule.commission_rate,
                                " money"),
                            React.createElement("td", null,
                                rule.margin_rate,
                                "x")));
                    }))))),
        showDialog && (React.createElement(SymbolRuleDialog_1.SymbolRuleDialog, { rule: editRule, availableSymbols: symbolsList, onClose: () => setShowDialog(false), onSave: handleSaveRule }))));
}
exports.SymbolsTab = SymbolsTab;
//# sourceMappingURL=SymbolsTab.js.map