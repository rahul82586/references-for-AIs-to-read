"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SymbolsTable = void 0;
const React = require("react");
const SymbolFolderUtils_1 = require("./SymbolFolderUtils");
function SymbolsTable({ contents, selectedRows, onSelectRow, onDoubleClick, onContextMenu, loading }) {
    if (loading) {
        return (React.createElement("div", { className: "adm-table-wrap", style: { flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center', opacity: 0.7 } },
            React.createElement("span", null, "Loading folder contents...")));
    }
    // Filter out dummy folder node indicators
    const visibleContents = contents.filter(c => !c.fullName.endsWith('.dummy'));
    if (visibleContents.length === 0) {
        return (React.createElement("div", { className: "adm-table-wrap", style: { flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center', opacity: 0.6 } },
            React.createElement("span", null, "Folder is empty. Right-click or use toolbar to add items.")));
    }
    return (React.createElement("div", { className: "adm-table-wrap", style: { flex: 1, overflowY: 'auto' } },
        React.createElement("table", { className: "adm-table" },
            React.createElement("thead", null,
                React.createElement("tr", null,
                    React.createElement("th", null, "Symbol / Folder"),
                    React.createElement("th", null, "Type (Highest Group)"),
                    React.createElement("th", null, "Execution Mode"),
                    React.createElement("th", null, "Digits"))),
            React.createElement("tbody", null, visibleContents.map(row => {
                const isSelected = selectedRows.includes(row.fullName);
                if (row.type === 'folder') {
                    return (React.createElement("tr", { key: row.fullName, className: isSelected ? 'selected' : '', onClick: e => onSelectRow(row.fullName, e), onDoubleClick: () => onDoubleClick(row), onContextMenu: e => onContextMenu(row, e) },
                        React.createElement("td", null,
                            React.createElement("i", { className: "codicon codicon-folder", style: { color: '#f1c40f', marginRight: 6 } }),
                            React.createElement("strong", null, row.name)),
                        React.createElement("td", null, "\u2014"),
                        React.createElement("td", null, "\u2014"),
                        React.createElement("td", null, "\u2014")));
                }
                // Render Symbol
                const s = row.data;
                let settings = {};
                if (s.settings_json) {
                    try {
                        settings = JSON.parse(s.settings_json);
                    }
                    catch { }
                }
                const highestGroup = (0, SymbolFolderUtils_1.getHighestOrderGroup)(s.symbol) || 'Root';
                const execMode = settings.execution_mode || 'Instant';
                const digitsVal = s.digits !== undefined ? s.digits : 5;
                return (React.createElement("tr", { key: s.symbol, className: isSelected ? 'selected' : '', onClick: e => onSelectRow(row.fullName, e), onDoubleClick: () => onDoubleClick(row), onContextMenu: e => onContextMenu(row, e) },
                    React.createElement("td", null,
                        React.createElement("i", { className: "codicon codicon-graph", style: { color: '#2ecc71', marginRight: 6 } }),
                        React.createElement("strong", null, row.name)),
                    React.createElement("td", null, highestGroup),
                    React.createElement("td", null,
                        React.createElement("span", { className: "adm-tag" }, execMode)),
                    React.createElement("td", null, digitsVal)));
            })))));
}
exports.SymbolsTable = SymbolsTable;
//# sourceMappingURL=SymbolsTable.js.map