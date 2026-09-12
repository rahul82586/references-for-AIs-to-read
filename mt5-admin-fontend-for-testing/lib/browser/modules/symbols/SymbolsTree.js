"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SymbolsTree = void 0;
const React = require("react");
const SymbolFolderUtils_1 = require("./SymbolFolderUtils");
function SymbolsTree({ folders, activeFolder, onSelectFolder }) {
    return (React.createElement("div", { className: "adm-tree-pane", style: { width: 220, borderRight: '1px solid var(--theia-border)', overflowY: 'auto', padding: 8 } },
        React.createElement("div", { className: "adm-tree-pane-header", style: { fontWeight: 'bold', fontSize: 11, marginBottom: 8, opacity: 0.7 } }, "SYMBOL GROUPS & FOLDERS"),
        React.createElement("div", { className: `adm-tree-pane-row ${activeFolder === '' ? 'active' : ''}`, onClick: () => onSelectFolder('') },
            React.createElement("i", { className: "codicon codicon-home", style: { marginRight: 6 } }),
            React.createElement("span", null, "All Symbols")),
        folders.map(f => {
            const parts = (0, SymbolFolderUtils_1.splitSymbolPath)(f);
            const depth = parts.length - 1;
            return (React.createElement("div", { key: f, className: `adm-tree-pane-row ${activeFolder === f ? 'active' : ''}`, style: { paddingLeft: `${8 + depth * 14}px` }, onClick: () => onSelectFolder(f) },
                React.createElement("i", { className: "codicon codicon-folder", style: { marginRight: 6 } }),
                React.createElement("span", null, parts[parts.length - 1])));
        })));
}
exports.SymbolsTree = SymbolsTree;
//# sourceMappingURL=SymbolsTree.js.map