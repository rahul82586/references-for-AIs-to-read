"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.AllSymbolsPage = void 0;
// @ts-nocheck
const React = require("react");
const api_1 = require("../api");
const SymbolFolderUtils_1 = require("./SymbolFolderUtils");
const SymbolFilterBar_1 = require("./SymbolFilterBar");
const SymbolSettingsModal_1 = require("./modal/SymbolSettingsModal");
function AllSymbolsPage() {
    const [symbols, setSymbols] = React.useState([]);
    const [filtered, setFiltered] = React.useState([]);
    const [selectedRows, setSelectedRows] = React.useState([]);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState(null);
    // Modal state
    const [showSettingsModal, setShowSettingsModal] = React.useState(false);
    const [settingsSymbol, setSettingsSymbol] = React.useState(null);
    const loadData = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await api_1.API.getSymbols();
            // Filter out dummy folders
            const validSymbols = data.filter((s) => !s.symbol.endsWith('.dummy'));
            setSymbols(validSymbols);
            setFiltered(validSymbols);
        }
        catch (err) {
            setError(err.message || 'Failed to load symbols.');
        }
        finally {
            setLoading(false);
        }
    };
    React.useEffect(() => {
        loadData();
    }, []);
    // Selection handlers
    const handleSelectRow = (symbol, e) => {
        if (e.ctrlKey || e.metaKey) {
            if (selectedRows.includes(symbol)) {
                setSelectedRows(prev => prev.filter(r => r !== symbol));
            }
            else {
                setSelectedRows(prev => [...prev, symbol]);
            }
        }
        else if (e.shiftKey && selectedRows.length > 0) {
            const last = selectedRows[selectedRows.length - 1];
            const lastIdx = filtered.findIndex(r => r.symbol === last);
            const currIdx = filtered.findIndex(r => r.symbol === symbol);
            if (lastIdx !== -1 && currIdx !== -1) {
                const start = Math.min(lastIdx, currIdx);
                const end = Math.max(lastIdx, currIdx);
                const range = filtered.slice(start, end + 1).map(r => r.symbol);
                setSelectedRows(prev => Array.from(new Set([...prev, ...range])));
            }
        }
        else {
            setSelectedRows([symbol]);
        }
    };
    const handleEdit = (name) => {
        const target = name || selectedRows[0];
        if (!target)
            return;
        setSettingsSymbol(target);
        setShowSettingsModal(true);
    };
    const handleFilterApplied = (filteredList) => {
        setFiltered(filteredList);
        setSelectedRows([]);
    };
    const isSingleSelected = selectedRows.length === 1;
    return (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' } },
        React.createElement(SymbolFilterBar_1.SymbolFilterBar, { symbols: symbols, onFilterApplied: handleFilterApplied }),
        React.createElement("div", { className: "adm-toolbar", style: { borderBottom: 'none', padding: '4px 12px' } },
            React.createElement("button", { type: "button", className: "adm-btn", disabled: !isSingleSelected, onClick: () => handleEdit() },
                React.createElement("i", { className: "codicon codicon-edit" }),
                " Edit Selected Symbol"),
            React.createElement("button", { type: "button", className: "adm-btn", onClick: loadData },
                React.createElement("i", { className: "codicon codicon-refresh" }),
                " Refresh")),
        error && (React.createElement("div", { className: "adm-hint", style: { background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)', margin: '10px 16px' } },
            React.createElement("i", { className: "codicon codicon-error" }),
            " ",
            error)),
        React.createElement("div", { className: "adm-table-wrap", style: { flex: 1, overflowY: 'auto' } }, loading ? (React.createElement("div", { style: { padding: 20, textAlign: 'center', opacity: 0.7 } }, "Loading all symbols...")) : filtered.length === 0 ? (React.createElement("div", { style: { padding: 20, textAlign: 'center', opacity: 0.6 } }, "No symbols found matching active search parameters.")) : (React.createElement("table", { className: "adm-table" },
            React.createElement("thead", null,
                React.createElement("tr", null,
                    React.createElement("th", null, "Symbol Path Name"),
                    React.createElement("th", null, "Type (Highest Group)"),
                    React.createElement("th", null, "Execution Mode"),
                    React.createElement("th", null, "Digits"))),
            React.createElement("tbody", null, filtered.map(s => {
                const isSelected = selectedRows.includes(s.symbol);
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
                return (React.createElement("tr", { key: s.symbol, className: isSelected ? 'selected' : '', onClick: e => handleSelectRow(s.symbol, e), onDoubleClick: () => handleEdit(s.symbol) },
                    React.createElement("td", null,
                        React.createElement("i", { className: "codicon codicon-graph", style: { color: '#2ecc71', marginRight: 6 } }),
                        React.createElement("strong", null, s.symbol)),
                    React.createElement("td", null, highestGroup),
                    React.createElement("td", null,
                        React.createElement("span", { className: "adm-tag" }, execMode)),
                    React.createElement("td", null, digitsVal)));
            }))))),
        React.createElement("div", { className: "adm-statusbar" },
            React.createElement("span", null,
                "Matching symbols: ",
                filtered.length,
                " of ",
                symbols.length),
            selectedRows.length > 0 && (React.createElement(React.Fragment, null,
                React.createElement("span", { className: "adm-sep" }, "|"),
                React.createElement("span", null,
                    "Selected: ",
                    selectedRows.length)))),
        showSettingsModal && (React.createElement(SymbolSettingsModal_1.SymbolSettingsModal, { symbolName: settingsSymbol, onClose: () => setShowSettingsModal(false), onSaved: loadData }))));
}
exports.AllSymbolsPage = AllSymbolsPage;
//# sourceMappingURL=AllSymbolsPage.js.map