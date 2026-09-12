"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SymbolsPage = void 0;
const React = require("react");
const SymbolsTreePage_1 = require("./SymbolsTreePage");
const AllSymbolsPage_1 = require("./AllSymbolsPage");
function SymbolsPage({ selectedPath = '' }) {
    const [activeTab, setActiveTab] = React.useState('hierarchy');
    return (React.createElement("div", { className: "adm-page", style: { display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' } },
        React.createElement("div", { className: "adm-tabs", style: { padding: '0 16px', background: 'var(--theia-editor-background)', borderBottom: '1px solid var(--theia-border)', flexShrink: 0 } },
            React.createElement("button", { type: "button", className: `adm-tab ${activeTab === 'hierarchy' ? 'active' : ''}`, onClick: () => setActiveTab('hierarchy') },
                React.createElement("i", { className: "codicon codicon-list-tree", style: { marginRight: 6 } }),
                "Symbols"),
            React.createElement("button", { type: "button", className: `adm-tab ${activeTab === 'flat' ? 'active' : ''}`, onClick: () => setActiveTab('flat') },
                React.createElement("i", { className: "codicon codicon-search", style: { marginRight: 6 } }),
                "All Symbols")),
        React.createElement("div", { style: { flex: 1, minHeight: 0, overflow: 'hidden' } }, activeTab === 'hierarchy' ? (React.createElement(SymbolsTreePage_1.SymbolsTreePage, { selectedPath: selectedPath })) : (React.createElement(AllSymbolsPage_1.AllSymbolsPage, null)))));
}
exports.SymbolsPage = SymbolsPage;
//# sourceMappingURL=SymbolsPage.js.map