"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SelectSymbolsStep = void 0;
// @ts-nocheck
const React = require("react");
// Mock remote server symbols database
const MOCK_REMOTE_SYMBOLS = [
    { symbol: 'Forex\\Majors\\EURUSD', digits: 5, contract_size: 100000.0, currency: 'USD' },
    { symbol: 'Forex\\Majors\\GBPUSD', digits: 5, contract_size: 100000.0, currency: 'USD' },
    { symbol: 'Forex\\Minors\\EURGBP', digits: 5, contract_size: 100000.0, currency: 'GBP' },
    { symbol: 'CFD\\Stocks\\AAPL', digits: 2, contract_size: 100.0, currency: 'USD' },
    { symbol: 'CFD\\Stocks\\MSFT', digits: 2, contract_size: 100.0, currency: 'USD' },
    { symbol: 'Cryptos\\BTCUSD', digits: 2, contract_size: 1.0, currency: 'USD' },
    { symbol: 'Indices\\US500', digits: 1, contract_size: 10.0, currency: 'USD' }
];
function SelectSymbolsStep({ connectData, selectedSymbols, onSelectSymbolsChange, overwriteExisting, onOverwriteChange }) {
    const [activeFolder, setActiveFolder] = React.useState('Forex\\Majors');
    const [previewSymbol, setPreviewSymbol] = React.useState(null);
    // Extract folders
    const folders = React.useMemo(() => {
        const set = new Set();
        for (const s of MOCK_REMOTE_SYMBOLS) {
            const parts = s.symbol.split('\\');
            let pathAccum = '';
            for (let i = 0; i < parts.length - 1; i++) {
                pathAccum = pathAccum ? `${pathAccum}\\${parts[i]}` : parts[i];
                set.add(pathAccum);
            }
        }
        return Array.from(set).sort();
    }, []);
    // Filter contents of selected activeFolder
    const contents = React.useMemo(() => {
        return MOCK_REMOTE_SYMBOLS.filter(s => {
            const parts = s.symbol.split('\\');
            const parent = parts.slice(0, -1).join('\\');
            return parent === activeFolder;
        });
    }, [activeFolder]);
    const toggleSelectSymbol = (symbol) => {
        if (selectedSymbols.includes(symbol)) {
            onSelectSymbolsChange(selectedSymbols.filter(s => s !== symbol));
        }
        else {
            onSelectSymbolsChange([...selectedSymbols, symbol]);
        }
    };
    const handleSelectFolderSymbols = (folder) => {
        const folderSymbols = MOCK_REMOTE_SYMBOLS.filter(s => s.symbol.startsWith(folder + '\\')).map(s => s.symbol);
        const allSelected = folderSymbols.every(s => selectedSymbols.includes(s));
        if (allSelected) {
            // Deselect all in folder
            onSelectSymbolsChange(selectedSymbols.filter(s => !folderSymbols.includes(s)));
        }
        else {
            // Select all in folder
            onSelectSymbolsChange(Array.from(new Set([...selectedSymbols, ...folderSymbols])));
        }
    };
    const handleSelectAll = () => {
        const allNames = MOCK_REMOTE_SYMBOLS.map(s => s.symbol);
        if (selectedSymbols.length === allNames.length) {
            onSelectSymbolsChange([]);
        }
        else {
            onSelectSymbolsChange(allNames);
        }
    };
    return (React.createElement("div", { className: "adm-modal-body", style: { display: 'flex', flexDirection: 'column', height: '50vh', gap: 10 } },
        React.createElement("div", { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' } },
            React.createElement("span", { style: { fontSize: 11, color: 'var(--theia-descriptionForeground)' } },
                "Connected to ",
                React.createElement("strong", null, connectData.address),
                ". Select the instruments you want to ingest:"),
            React.createElement("button", { type: "button", className: "adm-btn", style: { fontSize: 11, padding: '2px 8px' }, onClick: handleSelectAll }, selectedSymbols.length === MOCK_REMOTE_SYMBOLS.length ? 'Deselect All' : 'Select All')),
        React.createElement("div", { className: "adm-split-view", style: { flex: 1, minHeight: 0, border: '1px solid var(--theia-border)' } },
            React.createElement("div", { style: { width: 160, borderRight: '1px solid var(--theia-border)', overflowY: 'auto', padding: 6, display: 'flex', flexDirection: 'column', gap: 2 } }, folders.map(f => {
                const parts = f.split('\\');
                const depth = parts.length - 1;
                return (React.createElement("div", { key: f, className: `adm-tree-pane-row ${activeFolder === f ? 'active' : ''}`, style: { paddingLeft: `${4 + depth * 10}px`, fontSize: 11, height: 20 }, onClick: () => setActiveFolder(f), onDoubleClick: () => handleSelectFolderSymbols(f), title: "Double-click to select all symbols in folder" },
                    React.createElement("i", { className: "codicon codicon-folder", style: { fontSize: 11 } }),
                    React.createElement("span", null, parts[parts.length - 1])));
            })),
            React.createElement("div", { style: { flex: 1, overflowY: 'auto', padding: 4 } },
                React.createElement("table", { className: "adm-table", style: { fontSize: 11 } },
                    React.createElement("thead", null,
                        React.createElement("tr", null,
                            React.createElement("th", { style: { width: 40 } }, "Sel"),
                            React.createElement("th", null, "Symbol Name"),
                            React.createElement("th", null, "Digits"),
                            React.createElement("th", null, "Contract Size"))),
                    React.createElement("tbody", null, contents.map(s => {
                        const isSelected = selectedSymbols.includes(s.symbol);
                        const lastPart = s.symbol.split('\\').pop() || s.symbol;
                        return (React.createElement("tr", { key: s.symbol, className: isSelected ? 'selected' : '', onClick: () => toggleSelectSymbol(s.symbol) },
                            React.createElement("td", null,
                                React.createElement("input", { type: "checkbox", checked: isSelected, onChange: () => toggleSelectSymbol(s.symbol), onClick: e => e.stopPropagation() })),
                            React.createElement("td", null,
                                React.createElement("span", { style: { textDecoration: 'underline', cursor: 'help' }, onClick: (e) => {
                                        e.stopPropagation();
                                        setPreviewSymbol(s);
                                    }, title: "Click to view specifications preview" }, lastPart)),
                            React.createElement("td", null, s.digits),
                            React.createElement("td", null, s.contract_size.toLocaleString())));
                    }))))),
        React.createElement("div", { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 6 } },
            React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, cursor: 'pointer' } },
                React.createElement("input", { type: "checkbox", checked: overwriteExisting, onChange: e => onOverwriteChange(e.target.checked) }),
                React.createElement("span", null, "Overwrite existing symbols with matching names")),
            React.createElement("span", { style: { fontSize: 11 } },
                "Selected: ",
                React.createElement("strong", null, selectedSymbols.length),
                " symbol(s)")),
        previewSymbol && (React.createElement("div", { className: "adm-modal-overlay", style: { zIndex: 1200 }, onClick: () => setPreviewSymbol(null) },
            React.createElement("div", { className: "adm-modal", style: { width: 300 }, onClick: e => e.stopPropagation() },
                React.createElement("div", { className: "adm-modal-header" },
                    React.createElement("h3", null,
                        "Remote Specifications - ",
                        previewSymbol.symbol.split('\\').pop()),
                    React.createElement("button", { type: "button", className: "adm-modal-close", onClick: () => setPreviewSymbol(null) }, "\u00D7")),
                React.createElement("div", { className: "adm-modal-body", style: { fontSize: 11, display: 'flex', flexDirection: 'column', gap: 6 } },
                    React.createElement("div", { className: "adm-kv" },
                        React.createElement("span", null, "Full Path"),
                        React.createElement("strong", null, previewSymbol.symbol)),
                    React.createElement("div", { className: "adm-kv" },
                        React.createElement("span", null, "Digits Precision"),
                        React.createElement("span", null, previewSymbol.digits)),
                    React.createElement("div", { className: "adm-kv" },
                        React.createElement("span", null, "Contract Size"),
                        React.createElement("span", null, previewSymbol.contract_size.toLocaleString())),
                    React.createElement("div", { className: "adm-kv" },
                        React.createElement("span", null, "Base Currency"),
                        React.createElement("span", null, previewSymbol.currency)),
                    React.createElement("div", { className: "adm-kv" },
                        React.createElement("span", null, "Trade Session"),
                        React.createElement("span", null, "MON-FRI 00:00-24:00 (Standard)"))),
                React.createElement("div", { className: "adm-modal-footer" },
                    React.createElement("button", { type: "button", className: "adm-btn", onClick: () => setPreviewSymbol(null) }, "Close Preview")))))));
}
exports.SelectSymbolsStep = SelectSymbolsStep;
//# sourceMappingURL=SelectSymbolsStep.js.map