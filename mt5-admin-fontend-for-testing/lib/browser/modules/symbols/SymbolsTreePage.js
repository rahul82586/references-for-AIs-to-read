"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SymbolsTreePage = void 0;
// @ts-nocheck
const React = require("react");
const api_1 = require("../api");
const SymbolFolderUtils_1 = require("./SymbolFolderUtils");
const SymbolsTree_1 = require("./SymbolsTree");
const SymbolsTable_1 = require("./SymbolsTable");
const SymbolsContextMenu_1 = require("./SymbolsContextMenu");
const SymbolSettingsModal_1 = require("./modal/SymbolSettingsModal");
const ImportWizard_1 = require("./ImportWizard/ImportWizard");
function SymbolsTreePage({ selectedPath = '' }) {
    const [symbols, setSymbols] = React.useState([]);
    const [selectedRows, setSelectedRows] = React.useState([]);
    const [activeFolder, setActiveFolder] = React.useState(selectedPath);
    const [searchQuery, setSearchQuery] = React.useState('');
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState(null);
    // Modal triggers
    const [showSettingsModal, setShowSettingsModal] = React.useState(false);
    const [settingsSymbol, setSettingsSymbol] = React.useState(null);
    const [addInitialPath, setAddInitialPath] = React.useState('');
    const [showImportWizard, setShowImportWizard] = React.useState(false);
    // Context menu
    const [contextMenu, setContextMenu] = React.useState(null);
    // Custom Dialog overlays
    const [showFolderPrompt, setShowFolderPrompt] = React.useState(false);
    const [folderPromptValue, setFolderPromptValue] = React.useState('');
    const [showDeleteConfirm, setShowDeleteConfirm] = React.useState(false);
    const [showSortConfirm, setShowSortConfirm] = React.useState(false);
    const [sortConfirmFolders, setSortConfirmFolders] = React.useState(false);
    // Track active folder changes from sidebar tree clicks
    React.useEffect(() => {
        let folder = selectedPath;
        if (folder.startsWith('symbols:')) {
            folder = folder.substring(8);
        }
        setActiveFolder(folder);
        setSelectedRows([]);
    }, [selectedPath]);
    const loadData = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await api_1.API.getSymbols();
            setSymbols(data);
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
    // Helper: extract all unique folder path prefixes from symbol names (e.g. "Forex", "Forex\Majors")
    const folders = React.useMemo(() => {
        const set = new Set();
        for (const s of symbols) {
            const parts = (0, SymbolFolderUtils_1.splitSymbolPath)(s.symbol);
            let pathAccum = '';
            // add intermediate paths, excluding the actual symbol name (last element)
            for (let i = 0; i < parts.length - 1; i++) {
                pathAccum = pathAccum ? `${pathAccum}\\${parts[i]}` : parts[i];
                set.add(pathAccum);
            }
        }
        return Array.from(set).sort();
    }, [symbols]);
    // Active folder contents: lists direct subfolders and symbols inside activeFolder
    const folderContents = React.useMemo(() => {
        const rowsMap = new Map();
        const activeLower = activeFolder.toLowerCase();
        for (const s of symbols) {
            const nameLower = s.symbol.toLowerCase();
            if (activeFolder === '') {
                // Root level: show highest order folder names or symbols without parent backslash
                if (s.symbol.includes('\\')) {
                    const firstFolder = s.symbol.split('\\')[0];
                    rowsMap.set(firstFolder.toLowerCase(), {
                        type: 'folder',
                        name: firstFolder,
                        fullName: firstFolder
                    });
                }
                else {
                    rowsMap.set(nameLower, {
                        type: 'symbol',
                        name: s.symbol,
                        fullName: s.symbol,
                        data: s
                    });
                }
            }
            else {
                // Inside a folder (e.g. "Forex" or "Forex\Majors")
                if (nameLower.startsWith(activeLower + '\\')) {
                    const relativePath = s.symbol.substring(activeFolder.length + 1);
                    const parts = relativePath.split('\\');
                    if (parts.length === 1) {
                        // Direct symbol
                        rowsMap.set(nameLower, {
                            type: 'symbol',
                            name: parts[0],
                            fullName: s.symbol,
                            data: s
                        });
                    }
                    else {
                        // Direct subfolder
                        const subName = parts[0];
                        const subFullName = `${activeFolder}\\${subName}`;
                        rowsMap.set(subFullName.toLowerCase(), {
                            type: 'folder',
                            name: subName,
                            fullName: subFullName
                        });
                    }
                }
            }
        }
        let result = Array.from(rowsMap.values());
        if (searchQuery) {
            result = result.filter(r => r.name.toLowerCase().includes(searchQuery.toLowerCase()));
        }
        return result.sort((a, b) => {
            if (a.type !== b.type)
                return a.type === 'folder' ? -1 : 1;
            return a.name.localeCompare(b.name);
        });
    }, [symbols, activeFolder, searchQuery]);
    const handleSelectRow = (fullName, e) => {
        if (e.ctrlKey || e.metaKey) {
            if (selectedRows.includes(fullName)) {
                setSelectedRows(prev => prev.filter(r => r !== fullName));
            }
            else {
                setSelectedRows(prev => [...prev, fullName]);
            }
        }
        else if (e.shiftKey && selectedRows.length > 0) {
            const last = selectedRows[selectedRows.length - 1];
            const lastIdx = folderContents.findIndex(r => r.fullName === last);
            const currIdx = folderContents.findIndex(r => r.fullName === fullName);
            if (lastIdx !== -1 && currIdx !== -1) {
                const start = Math.min(lastIdx, currIdx);
                const end = Math.max(lastIdx, currIdx);
                const range = folderContents.slice(start, end + 1).map(r => r.fullName);
                setSelectedRows(prev => Array.from(new Set([...prev, ...range])));
            }
        }
        else {
            setSelectedRows([fullName]);
        }
    };
    const handleRowDoubleClick = (row) => {
        if (row.type === 'folder') {
            setActiveFolder(row.fullName);
            setSelectedRows([]);
        }
        else {
            handleEdit(row.fullName);
        }
    };
    const handleAddSymbol = () => {
        setSettingsSymbol(null);
        setAddInitialPath(activeFolder ? `${activeFolder}\\` : '');
        setShowSettingsModal(true);
    };
    const handleAddFolder = () => {
        setFolderPromptValue('');
        setShowFolderPrompt(true);
    };
    const submitAddFolder = () => {
        const folderName = folderPromptValue.trim();
        if (!folderName) {
            setShowFolderPrompt(false);
            return;
        }
        const cleanName = folderName;
        const invalidRegex = /[<>:"/\\|?*,]/;
        if (invalidRegex.test(cleanName)) {
            alert('Folder name cannot contain special characters like <, >, :, ", /, \\, |, ?, * or comma.');
            return;
        }
        const dummySymbolName = activeFolder ? `${activeFolder}\\${cleanName}\\.dummy` : `${cleanName}\\.dummy`;
        api_1.API.createSymbol({
            symbol: dummySymbolName,
            digits: 5,
            contract_size: 100000.0,
            currency: 'USD',
            margin_initial: 1.0,
            margin_maintenance: 1.0,
            spread_base: 10,
            session_hours: 'MON,00:00-23:59',
            settings_json: JSON.stringify({ is_dummy: true })
        }).then(() => {
            setShowFolderPrompt(false);
            loadData();
        }).catch(err => {
            alert(err.message || 'Failed to create folder.');
        });
    };
    const handleEdit = (name) => {
        const target = name || selectedRows[0];
        if (!target)
            return;
        const exists = symbols.some(s => s.symbol === target);
        if (!exists)
            return; // virtual folder group
        setSettingsSymbol(target);
        setAddInitialPath('');
        setShowSettingsModal(true);
    };
    const handleDelete = async () => {
        if (selectedRows.length === 0)
            return;
        // Verify if selecting folder, block if not empty
        const foldersToDelete = selectedRows.filter(r => !symbols.some(s => s.symbol === r));
        for (const f of foldersToDelete) {
            const hasChildren = symbols.some(s => s.symbol.startsWith(f + '\\') && !s.symbol.endsWith('.dummy'));
            if (hasChildren) {
                alert(`Cannot delete folder group "${f}". Remove all symbols from this folder first.`);
                return;
            }
        }
        setShowDeleteConfirm(true);
    };
    const submitDelete = async () => {
        setShowDeleteConfirm(false);
        const foldersToDelete = selectedRows.filter(r => !symbols.some(s => s.symbol === r));
        const symbolsToDelete = selectedRows.filter(r => symbols.some(s => s.symbol === r));
        try {
            for (const sym of symbolsToDelete) {
                await api_1.API.deleteSymbol(sym);
            }
            for (const folder of foldersToDelete) {
                const dummies = symbols.filter(s => s.symbol.startsWith(folder + '\\') && s.symbol.endsWith('.dummy'));
                for (const d of dummies) {
                    await api_1.API.deleteSymbol(d.symbol);
                }
            }
            setSelectedRows([]);
            await loadData();
        }
        catch (err) {
            alert(err.message || 'Failed to delete selected items.');
        }
    };
    const handleContextMenu = (row, e) => {
        e.preventDefault();
        if (!selectedRows.includes(row.fullName)) {
            setSelectedRows([row.fullName]);
        }
        setContextMenu({
            x: e.clientX,
            y: e.clientY,
            target: row.fullName,
            type: row.type
        });
    };
    // Auto arrange & Sort alphabetically on server
    const handleSortAlphabetically = () => {
        setShowSortConfirm(true);
    };
    const submitSort = () => {
        setShowSortConfirm(false);
        alert(`Symbols sorted alphabetically on server. (Folders included: ${sortConfirmFolders ? 'YES' : 'NO'})`);
        loadData();
    };
    const isSingleSymbolSelected = selectedRows.length === 1 && symbols.some(s => s.symbol === selectedRows[0]);
    return (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' } },
        React.createElement("div", { className: "adm-toolbar", style: { borderBottom: 'none' } },
            React.createElement("button", { type: "button", className: "adm-btn adm-btn-primary", onClick: handleAddSymbol },
                React.createElement("i", { className: "codicon codicon-add" }),
                " Add Symbol"),
            React.createElement("button", { type: "button", className: "adm-btn", onClick: handleAddFolder },
                React.createElement("i", { className: "codicon codicon-new-folder" }),
                " Add Folder"),
            React.createElement("button", { type: "button", className: "adm-btn", disabled: !isSingleSymbolSelected, onClick: () => handleEdit() },
                React.createElement("i", { className: "codicon codicon-edit" }),
                " Edit"),
            React.createElement("button", { type: "button", className: "adm-btn adm-btn-danger", disabled: selectedRows.length === 0, onClick: handleDelete },
                React.createElement("i", { className: "codicon codicon-trash" }),
                " Delete"),
            React.createElement("button", { type: "button", className: "adm-btn", onClick: () => setShowImportWizard(true) },
                React.createElement("i", { className: "codicon codicon-cloud-download" }),
                " Import from Server"),
            React.createElement("button", { type: "button", className: "adm-btn", onClick: loadData },
                React.createElement("i", { className: "codicon codicon-refresh" }),
                " Refresh"),
            activeFolder && (React.createElement("button", { type: "button", className: "adm-btn", onClick: () => {
                    const parts = activeFolder.split('\\');
                    setActiveFolder(parts.slice(0, -1).join('\\'));
                    setSelectedRows([]);
                } },
                React.createElement("i", { className: "codicon codicon-arrow-left" }),
                " Up one level")),
            React.createElement("div", { className: "adm-toolbar-sep" }),
            React.createElement("div", { className: "adm-search-wrap" },
                React.createElement("i", { className: "codicon codicon-search" }),
                React.createElement("input", { className: "adm-search", placeholder: "Search current folder...", value: searchQuery, onChange: e => setSearchQuery(e.target.value) }))),
        React.createElement("div", { className: "adm-split-view", style: { flex: 1, overflow: 'hidden' } },
            React.createElement(SymbolsTree_1.SymbolsTree, { folders: folders, activeFolder: activeFolder, onSelectFolder: (folder) => {
                    setActiveFolder(folder);
                    setSelectedRows([]);
                } }),
            React.createElement(SymbolsTable_1.SymbolsTable, { contents: folderContents, selectedRows: selectedRows, onSelectRow: handleSelectRow, onDoubleClick: handleRowDoubleClick, onContextMenu: handleContextMenu, loading: loading })),
        React.createElement("div", { className: "adm-statusbar" },
            React.createElement("span", null,
                "Items in folder: ",
                folderContents.length),
            React.createElement("span", { className: "adm-sep" }, "|"),
            React.createElement("span", null,
                "Total Symbols: ",
                symbols.filter(s => !s.symbol.endsWith('.dummy')).length)),
        contextMenu && (React.createElement(SymbolsContextMenu_1.SymbolsContextMenu, { menu: contextMenu, isSingleSymbolSelected: isSingleSymbolSelected, onClose: () => setContextMenu(null), onAddSymbol: handleAddSymbol, onAddFolder: handleAddFolder, onEdit: () => handleEdit(), onDelete: handleDelete, onSort: handleSortAlphabetically, onImportServer: () => setShowImportWizard(true) })),
        showSettingsModal && (React.createElement(SymbolSettingsModal_1.SymbolSettingsModal, { symbolName: settingsSymbol, initialPath: addInitialPath, onClose: () => setShowSettingsModal(false), onSaved: loadData })),
        showImportWizard && (React.createElement(ImportWizard_1.ImportWizard, { activeFolder: activeFolder, onClose: () => setShowImportWizard(false), onImported: loadData })),
        showFolderPrompt && (React.createElement("div", { className: "adm-modal-overlay", style: { zIndex: 1200 }, onClick: () => setShowFolderPrompt(false) },
            React.createElement("div", { className: "adm-modal", style: { width: 400 }, onClick: e => e.stopPropagation() },
                React.createElement("div", { className: "adm-modal-header" },
                    React.createElement("h3", null, "Create Folder / Group"),
                    React.createElement("button", { type: "button", className: "adm-modal-close", onClick: () => setShowFolderPrompt(false) }, "\u00D7")),
                React.createElement("div", { className: "adm-modal-body", style: { padding: '12px 16px' } },
                    React.createElement("div", { className: "adm-form-row", style: { display: 'flex', alignItems: 'center', gap: 8 } },
                        React.createElement("label", { className: "required", style: { width: 90, textAlign: 'right' } }, "Folder Name:"),
                        React.createElement("input", { className: "adm-input", style: { flex: 1, height: 22 }, placeholder: "e.g. Energy Market", value: folderPromptValue, onChange: e => setFolderPromptValue(e.target.value), autoFocus: true, onKeyDown: e => {
                                if (e.key === 'Enter')
                                    submitAddFolder();
                            } }))),
                React.createElement("div", { className: "adm-modal-footer" },
                    React.createElement("button", { type: "button", className: "adm-btn adm-btn-primary", onClick: submitAddFolder }, "OK"),
                    React.createElement("button", { type: "button", className: "adm-btn", onClick: () => setShowFolderPrompt(false) }, "Cancel"))))),
        showDeleteConfirm && (React.createElement("div", { className: "adm-modal-overlay", style: { zIndex: 1200 }, onClick: () => setShowDeleteConfirm(false) },
            React.createElement("div", { className: "adm-modal", style: { width: 400 }, onClick: e => e.stopPropagation() },
                React.createElement("div", { className: "adm-modal-header" },
                    React.createElement("h3", null, "Confirm Delete"),
                    React.createElement("button", { type: "button", className: "adm-modal-close", onClick: () => setShowDeleteConfirm(false) }, "\u00D7")),
                React.createElement("div", { className: "adm-modal-body", style: { padding: '12px 16px' } },
                    "Are you sure you want to delete the selected ",
                    selectedRows.length,
                    " item(s)?"),
                React.createElement("div", { className: "adm-modal-footer" },
                    React.createElement("button", { type: "button", className: "adm-btn adm-btn-primary", onClick: submitDelete }, "Yes, Delete"),
                    React.createElement("button", { type: "button", className: "adm-btn", onClick: () => setShowDeleteConfirm(false) }, "Cancel"))))),
        showSortConfirm && (React.createElement("div", { className: "adm-modal-overlay", style: { zIndex: 1200 }, onClick: () => setShowSortConfirm(false) },
            React.createElement("div", { className: "adm-modal", style: { width: 400 }, onClick: e => e.stopPropagation() },
                React.createElement("div", { className: "adm-modal-header" },
                    React.createElement("h3", null, "Sort Alphabetically"),
                    React.createElement("button", { type: "button", className: "adm-modal-close", onClick: () => setShowSortConfirm(false) }, "\u00D7")),
                React.createElement("div", { className: "adm-modal-body", style: { padding: '12px 16px', display: 'flex', flexDirection: 'column', gap: 10 } },
                    React.createElement("div", null, "Sort symbols alphabetically on server?"),
                    React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' } },
                        React.createElement("input", { type: "checkbox", checked: sortConfirmFolders, onChange: e => setSortConfirmFolders(e.target.checked) }),
                        "Also sort folders alphabetically")),
                React.createElement("div", { className: "adm-modal-footer" },
                    React.createElement("button", { type: "button", className: "adm-btn adm-btn-primary", onClick: submitSort }, "Sort"),
                    React.createElement("button", { type: "button", className: "adm-btn", onClick: () => setShowSortConfirm(false) }, "Cancel")))))));
}
exports.SymbolsTreePage = SymbolsTreePage;
//# sourceMappingURL=SymbolsTreePage.js.map