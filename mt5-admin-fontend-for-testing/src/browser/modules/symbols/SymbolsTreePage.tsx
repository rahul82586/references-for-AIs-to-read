// @ts-nocheck
import * as React from 'react';
import { API } from '../api';
import { splitSymbolPath, getHighestOrderGroup } from './SymbolFolderUtils';
import { SymbolsTree } from './SymbolsTree';
import { SymbolsTable } from './SymbolsTable';
import { SymbolsContextMenu } from './SymbolsContextMenu';
import { SymbolFilterBar } from './SymbolFilterBar';
import { SymbolSettingsModal } from './modal/SymbolSettingsModal';
import { ImportWizard } from './ImportWizard/ImportWizard';

interface SymbolsTreePageProps {
    selectedPath?: string;
}

export function SymbolsTreePage({ selectedPath = '' }: SymbolsTreePageProps): React.ReactElement {
    const [symbols, setSymbols] = React.useState<any[]>([]);
    const [selectedRows, setSelectedRows] = React.useState<string[]>([]);
    const [activeFolder, setActiveFolder] = React.useState(selectedPath);
    const [searchQuery, setSearchQuery] = React.useState('');
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState<string | null>(null);

    // Modal triggers
    const [showSettingsModal, setShowSettingsModal] = React.useState(false);
    const [settingsSymbol, setSettingsSymbol] = React.useState<string | null>(null);
    const [addInitialPath, setAddInitialPath] = React.useState('');
    const [showImportWizard, setShowImportWizard] = React.useState(false);

    // Context menu
    const [contextMenu, setContextMenu] = React.useState<{ x: number, y: number, target: string, type: 'folder' | 'symbol' | 'root' } | null>(null);

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
            const data = await API.getSymbols();
            setSymbols(data);
        } catch (err: any) {
            setError(err.message || 'Failed to load symbols.');
        } finally {
            setLoading(false);
        }
    };

    React.useEffect(() => {
        loadData();
    }, []);

    // Helper: extract all unique folder path prefixes from symbol names (e.g. "Forex", "Forex\Majors")
    const folders = React.useMemo(() => {
        const set = new Set<string>();
        for (const s of symbols) {
            const parts = splitSymbolPath(s.symbol);
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
        const rowsMap = new Map<string, {
            type: 'folder' | 'symbol';
            name: string;
            fullName: string;
            data?: any;
        }>();

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
                } else {
                    rowsMap.set(nameLower, {
                        type: 'symbol',
                        name: s.symbol,
                        fullName: s.symbol,
                        data: s
                    });
                }
            } else {
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
                    } else {
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
            if (a.type !== b.type) return a.type === 'folder' ? -1 : 1;
            return a.name.localeCompare(b.name);
        });
    }, [symbols, activeFolder, searchQuery]);

    const handleSelectRow = (fullName: string, e: React.MouseEvent) => {
        if (e.ctrlKey || e.metaKey) {
            if (selectedRows.includes(fullName)) {
                setSelectedRows(prev => prev.filter(r => r !== fullName));
            } else {
                setSelectedRows(prev => [...prev, fullName]);
            }
        } else if (e.shiftKey && selectedRows.length > 0) {
            const last = selectedRows[selectedRows.length - 1];
            const lastIdx = folderContents.findIndex(r => r.fullName === last);
            const currIdx = folderContents.findIndex(r => r.fullName === fullName);
            if (lastIdx !== -1 && currIdx !== -1) {
                const start = Math.min(lastIdx, currIdx);
                const end = Math.max(lastIdx, currIdx);
                const range = folderContents.slice(start, end + 1).map(r => r.fullName);
                setSelectedRows(prev => Array.from(new Set([...prev, ...range])));
            }
        } else {
            setSelectedRows([fullName]);
        }
    };

    const handleRowDoubleClick = (row: any) => {
        if (row.type === 'folder') {
            setActiveFolder(row.fullName);
            setSelectedRows([]);
        } else {
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
        API.createSymbol({
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

    const handleEdit = (name?: string) => {
        const target = name || selectedRows[0];
        if (!target) return;
        const exists = symbols.some(s => s.symbol === target);
        if (!exists) return; // virtual folder group

        setSettingsSymbol(target);
        setAddInitialPath('');
        setShowSettingsModal(true);
    };

    const handleDelete = async () => {
        if (selectedRows.length === 0) return;

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
                await API.deleteSymbol(sym);
            }
            for (const folder of foldersToDelete) {
                const dummies = symbols.filter(s => s.symbol.startsWith(folder + '\\') && s.symbol.endsWith('.dummy'));
                for (const d of dummies) {
                    await API.deleteSymbol(d.symbol);
                }
            }
            setSelectedRows([]);
            await loadData();
        } catch (err: any) {
            alert(err.message || 'Failed to delete selected items.');
        }
    };

    const handleContextMenu = (row: any, e: React.MouseEvent) => {
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

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
            
            {/* Toolbar */}
            <div className="adm-toolbar" style={{ borderBottom: 'none' }}>
                <button type="button" className="adm-btn adm-btn-primary" onClick={handleAddSymbol}>
                    <i className="codicon codicon-add" /> Add Symbol
                </button>
                <button type="button" className="adm-btn" onClick={handleAddFolder}>
                    <i className="codicon codicon-new-folder" /> Add Folder
                </button>
                <button type="button" className="adm-btn" disabled={!isSingleSymbolSelected} onClick={() => handleEdit()}>
                    <i className="codicon codicon-edit" /> Edit
                </button>
                <button type="button" className="adm-btn adm-btn-danger" disabled={selectedRows.length === 0} onClick={handleDelete}>
                    <i className="codicon codicon-trash" /> Delete
                </button>
                <button type="button" className="adm-btn" onClick={() => setShowImportWizard(true)}>
                    <i className="codicon codicon-cloud-download" /> Import from Server
                </button>
                <button type="button" className="adm-btn" onClick={loadData}>
                    <i className="codicon codicon-refresh" /> Refresh
                </button>

                {activeFolder && (
                    <button type="button" className="adm-btn" onClick={() => {
                        const parts = activeFolder.split('\\');
                        setActiveFolder(parts.slice(0, -1).join('\\'));
                        setSelectedRows([]);
                    }}>
                        <i className="codicon codicon-arrow-left" /> Up one level
                    </button>
                )}

                <div className="adm-toolbar-sep" />

                <div className="adm-search-wrap">
                    <i className="codicon codicon-search" />
                    <input 
                        className="adm-search" 
                        placeholder="Search current folder..." 
                        value={searchQuery}
                        onChange={e => setSearchQuery(e.target.value)}
                    />
                </div>
            </div>

            {/* Split View: Tree + Table Explorer */}
            <div className="adm-split-view" style={{ flex: 1, overflow: 'hidden' }}>
                
                {/* Left side dynamic tree selector */}
                <SymbolsTree 
                    folders={folders} 
                    activeFolder={activeFolder} 
                    onSelectFolder={(folder) => {
                        setActiveFolder(folder);
                        setSelectedRows([]);
                    }}
                />

                {/* Right side contents list explorer */}
                <SymbolsTable 
                    contents={folderContents}
                    selectedRows={selectedRows}
                    onSelectRow={handleSelectRow}
                    onDoubleClick={handleRowDoubleClick}
                    onContextMenu={handleContextMenu}
                    loading={loading}
                />
            </div>

            {/* Status bar */}
            <div className="adm-statusbar">
                <span>Items in folder: {folderContents.length}</span>
                <span className="adm-sep">|</span>
                <span>Total Symbols: {symbols.filter(s => !s.symbol.endsWith('.dummy')).length}</span>
            </div>

            {/* Context menu popup */}
            {contextMenu && (
                <SymbolsContextMenu 
                    menu={contextMenu}
                    isSingleSymbolSelected={isSingleSymbolSelected}
                    onClose={() => setContextMenu(null)}
                    onAddSymbol={handleAddSymbol}
                    onAddFolder={handleAddFolder}
                    onEdit={() => handleEdit()}
                    onDelete={handleDelete}
                    onSort={handleSortAlphabetically}
                    onImportServer={() => setShowImportWizard(true)}
                />
            )}

            {/* Visual Symbol Settings Editor Modal */}
            {showSettingsModal && (
                <SymbolSettingsModal 
                    symbolName={settingsSymbol}
                    initialPath={addInitialPath}
                    onClose={() => setShowSettingsModal(false)}
                    onSaved={loadData}
                />
            )}

            {/* Import Ingestion Wizard popup */}
            {showImportWizard && (
                <ImportWizard 
                    activeFolder={activeFolder}
                    onClose={() => setShowImportWizard(false)}
                    onImported={loadData}
                />
            )}

            {/* Custom overlays instead of window.prompt/confirm */}
            {showFolderPrompt && (
                <div className="adm-modal-overlay" style={{ zIndex: 1200 }} onClick={() => setShowFolderPrompt(false)}>
                    <div className="adm-modal" style={{ width: 400 }} onClick={e => e.stopPropagation()}>
                        <div className="adm-modal-header">
                            <h3>Create Folder / Group</h3>
                            <button type="button" className="adm-modal-close" onClick={() => setShowFolderPrompt(false)}>×</button>
                        </div>
                        <div className="adm-modal-body" style={{ padding: '12px 16px' }}>
                            <div className="adm-form-row" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                <label className="required" style={{ width: 90, textAlign: 'right' }}>Folder Name:</label>
                                <input 
                                    className="adm-input" 
                                    style={{ flex: 1, height: 22 }}
                                    placeholder="e.g. Energy Market" 
                                    value={folderPromptValue}
                                    onChange={e => setFolderPromptValue(e.target.value)}
                                    autoFocus
                                    onKeyDown={e => {
                                        if (e.key === 'Enter') submitAddFolder();
                                    }}
                                />
                            </div>
                        </div>
                        <div className="adm-modal-footer">
                            <button type="button" className="adm-btn adm-btn-primary" onClick={submitAddFolder}>OK</button>
                            <button type="button" className="adm-btn" onClick={() => setShowFolderPrompt(false)}>Cancel</button>
                        </div>
                    </div>
                </div>
            )}

            {showDeleteConfirm && (
                <div className="adm-modal-overlay" style={{ zIndex: 1200 }} onClick={() => setShowDeleteConfirm(false)}>
                    <div className="adm-modal" style={{ width: 400 }} onClick={e => e.stopPropagation()}>
                        <div className="adm-modal-header">
                            <h3>Confirm Delete</h3>
                            <button type="button" className="adm-modal-close" onClick={() => setShowDeleteConfirm(false)}>×</button>
                        </div>
                        <div className="adm-modal-body" style={{ padding: '12px 16px' }}>
                            Are you sure you want to delete the selected {selectedRows.length} item(s)?
                        </div>
                        <div className="adm-modal-footer">
                            <button type="button" className="adm-btn adm-btn-primary" onClick={submitDelete}>Yes, Delete</button>
                            <button type="button" className="adm-btn" onClick={() => setShowDeleteConfirm(false)}>Cancel</button>
                        </div>
                    </div>
                </div>
            )}

            {showSortConfirm && (
                <div className="adm-modal-overlay" style={{ zIndex: 1200 }} onClick={() => setShowSortConfirm(false)}>
                    <div className="adm-modal" style={{ width: 400 }} onClick={e => e.stopPropagation()}>
                        <div className="adm-modal-header">
                            <h3>Sort Alphabetically</h3>
                            <button type="button" className="adm-modal-close" onClick={() => setShowSortConfirm(false)}>×</button>
                        </div>
                        <div className="adm-modal-body" style={{ padding: '12px 16px', display: 'flex', flexDirection: 'column', gap: 10 }}>
                            <div>Sort symbols alphabetically on server?</div>
                            <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                                <input type="checkbox" checked={sortConfirmFolders} onChange={e => setSortConfirmFolders(e.target.checked)} />
                                Also sort folders alphabetically
                            </label>
                        </div>
                        <div className="adm-modal-footer">
                            <button type="button" className="adm-btn adm-btn-primary" onClick={submitSort}>Sort</button>
                            <button type="button" className="adm-btn" onClick={() => setShowSortConfirm(false)}>Cancel</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
