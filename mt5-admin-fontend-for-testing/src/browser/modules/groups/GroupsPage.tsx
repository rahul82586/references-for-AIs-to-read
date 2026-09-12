// @ts-nocheck
import * as React from 'react';
import { API } from '../api';
import { getGroupType, splitPathIntoSections, validateGroupName } from './groupTypeUtils';
import { GroupSettingsModal } from './modal/GroupSettingsModal';

const TYPE_COLORS: Record<string, string> = {
    Demo: '#3498db',
    Manager: '#9b59b6',
    Contest: '#e67e22',
    Coverage: '#16a085',
    Preliminary: '#e74c3c',
    Real: '#27ae60'
};

interface GroupsOverviewPageProps {
    selectedPath?: string;
}

export function GroupsOverviewPage({ selectedPath = '' }: GroupsOverviewPageProps): React.ReactElement {
    const [groups, setGroups] = React.useState<any[]>([]);
    const [gateways, setGateways] = React.useState<any[]>([]);
    const [selectedRows, setSelectedRows] = React.useState<string[]>([]);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState<string | null>(null);

    // Active folder path (e.g. "", "demo", "real\IB")
    const [activeFolder, setActiveFolder] = React.useState(selectedPath);
    const [searchQuery, setSearchQuery] = React.useState('');

    // Context menu states
    const [contextMenu, setContextMenu] = React.useState<{ x: number, y: number, target: string | null } | null>(null);

    // Modal state
    const [modalGroup, setModalGroup] = React.useState<string | null>(null);
    const [showModal, setShowModal] = React.useState(false);
    const [addInitialName, setAddInitialName] = React.useState('');

    // Track active folder changes from sidebar tree clicks
    React.useEffect(() => {
        // Strip out "groups:" prefix if it exists from tree node ID
        let folder = selectedPath;
        if (folder.startsWith('groups:')) {
            folder = folder.substring(7);
        }
        setActiveFolder(folder);
    }, [selectedPath]);

    const loadData = async () => {
        setLoading(true);
        setError(null);
        try {
            const [gData, gwData] = await Promise.all([
                API.getGroups(),
                API.getGateways()
            ]);
            setGroups(gData);
            setGateways(gwData);
        } catch (err: any) {
            setError(err.message || 'Failed to fetch groups.');
        } finally {
            setLoading(false);
        }
    };

    React.useEffect(() => {
        loadData();
    }, []);

    // Left pane list of sections
    const folders = React.useMemo(() => {
        const set = new Set<string>();
        for (const g of groups) {
            const sections = splitPathIntoSections(g.name);
            let pathAccum = '';
            for (let i = 0; i < sections.length - 1; i++) {
                pathAccum = pathAccum ? `${pathAccum}\\${sections[i]}` : sections[i];
                set.add(pathAccum);
            }
        }
        return Array.from(set).sort();
    }, [groups]);

    // Explorer rows: filters children or groups inside the current active folder
    const explorerRows = React.useMemo(() => {
        const rowsMap = new Map<string, {
            type: 'folder' | 'group';
            name: string;      // Display label (e.g. "forex" or "preliminary")
            fullName: string;  // Full DB path (e.g. "demo\forex" or "preliminary")
            groupData?: any;   // DB record
        }>();

        const activeLower = activeFolder.toLowerCase();

        for (const g of groups) {
            const nameLower = g.name.toLowerCase();

            if (activeFolder === '') {
                // Root level: only show top-level folders or groups at root level
                if (g.name.includes('\\')) {
                    const firstFolder = g.name.split('\\')[0];
                    rowsMap.set(firstFolder.toLowerCase(), {
                        type: 'folder',
                        name: firstFolder,
                        fullName: firstFolder
                    });
                } else {
                    rowsMap.set(nameLower, {
                        type: 'group',
                        name: g.name,
                        fullName: g.name,
                        groupData: g
                    });
                }
            } else {
                // Inside a folder path
                if (nameLower.startsWith(activeLower + '\\')) {
                    const relativePath = g.name.substring(activeFolder.length + 1);
                    const parts = relativePath.split('\\');

                    if (parts.length === 1) {
                        rowsMap.set(nameLower, {
                            type: 'group',
                            name: parts[0],
                            fullName: g.name,
                            groupData: g
                        });
                    } else {
                        const subfolderName = parts[0];
                        const subfolderFullName = `${activeFolder}\\${subfolderName}`;
                        rowsMap.set(subfolderFullName.toLowerCase(), {
                            type: 'folder',
                            name: subfolderName,
                            fullName: subfolderFullName
                        });
                    }
                }
            }
        }

        let result = Array.from(rowsMap.values());
        if (searchQuery) {
            result = result.filter(r => r.name.toLowerCase().includes(searchQuery.toLowerCase()));
        }

        // Sort folders first, then groups alphabetically
        return result.sort((a, b) => {
            if (a.type !== b.type) {
                return a.type === 'folder' ? -1 : 1;
            }
            return a.name.localeCompare(b.name);
        });
    }, [groups, activeFolder, searchQuery]);

    const handleSelectRow = (fullName: string, type: 'folder' | 'group', e: React.MouseEvent) => {
        if (e.ctrlKey || e.metaKey) {
            if (selectedRows.includes(fullName)) {
                setSelectedRows(prev => prev.filter(r => r !== fullName));
            } else {
                setSelectedRows(prev => [...prev, fullName]);
            }
        } else if (e.shiftKey && selectedRows.length > 0) {
            const lastSelected = selectedRows[selectedRows.length - 1];
            const lastIdx = explorerRows.findIndex(r => r.fullName === lastSelected);
            const currentIdx = explorerRows.findIndex(r => r.fullName === fullName);
            if (lastIdx !== -1 && currentIdx !== -1) {
                const start = Math.min(lastIdx, currentIdx);
                const end = Math.max(lastIdx, currentIdx);
                const range = explorerRows.slice(start, end + 1).map(r => r.fullName);
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

    const handleEdit = (name?: string) => {
        const target = name || selectedRows[0];
        if (!target) return;
        // Verify it is a group, not a virtual folder
        const isGroup = groups.some(g => g.name === target);
        if (!isGroup) return;

        setModalGroup(target);
        setAddInitialName('');
        setShowModal(true);
    };

    const handleAdd = () => {
        setModalGroup(null);
        // Pre-fill path prefix if inside a folder
        setAddInitialName(activeFolder ? `${activeFolder}\\` : '');
        setShowModal(true);
    };

    const handleDelete = async () => {
        if (selectedRows.length === 0) return;
        
        // Filter out virtual folders, can only delete groups
        const targetGroups = selectedRows.filter(r => groups.some(g => g.name === r));
        if (targetGroups.length === 0) {
            alert("Please select actual group records to delete, virtual folders are deleted dynamically when empty.");
            return;
        }

        const confirmMsg = targetGroups.length === 1 
            ? `Are you sure you want to delete the group "${targetGroups[0]}"?`
            : `Are you sure you want to delete the ${targetGroups.length} selected groups?`;
            
        if (!confirm(confirmMsg)) return;

        setError(null);
        try {
            for (const name of targetGroups) {
                await API.deleteGroup(name);
            }
            setSelectedRows([]);
            await loadData();
        } catch (err: any) {
            setError(err.message || 'Failed to delete groups. Make sure no client accounts exist inside them.');
        }
    };

    const handleRightClick = (row: any, e: React.MouseEvent) => {
        e.preventDefault();
        if (!selectedRows.includes(row.fullName)) {
            setSelectedRows([row.fullName]);
        }
        setContextMenu({
            x: e.clientX,
            y: e.clientY,
            target: row.fullName
        });
    };

    React.useEffect(() => {
        const closeMenu = () => setContextMenu(null);
        window.addEventListener('click', closeMenu);
        return () => window.removeEventListener('click', closeMenu);
    }, []);

    const handleMove = (direction: 'up' | 'down') => {
        if (selectedRows.length !== 1) return;
        alert(`Moved row ${direction} on server.`);
    };

    const isSingleGroupSelected = selectedRows.length === 1 && groups.some(g => g.name === selectedRows[0]);

    return (
        <div className="adm-page" style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
            {/* Main Action Toolbar */}
            <div className="adm-toolbar">
                <button type="button" className="adm-btn adm-btn-primary" onClick={handleAdd}>
                    <i className="codicon codicon-add" /> Add
                </button>
                <button type="button" className="adm-btn" disabled={!isSingleGroupSelected} onClick={() => handleEdit()}>
                    <i className="codicon codicon-edit" /> Edit
                </button>
                <button type="button" className="adm-btn adm-btn-danger" disabled={selectedRows.length === 0} onClick={handleDelete}>
                    <i className="codicon codicon-trash" /> Delete
                </button>
                <button type="button" className="adm-btn" onClick={loadData} title="Reload list">
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
                        placeholder="Search current view..." 
                        value={searchQuery}
                        onChange={e => setSearchQuery(e.target.value)}
                    />
                </div>
            </div>

            {/* Split View: Tree Nav Pane & Details Table */}
            <div className="adm-split-view" style={{ flex: 1, overflow: 'hidden' }}>
                
                {/* Left navigation tree pane */}
                <div className="adm-tree-pane" style={{ width: 220, borderRight: '1px solid var(--theia-border)', overflowY: 'auto', padding: 8 }}>
                    <div className="adm-tree-pane-header" style={{ fontWeight: 'bold', fontSize: 11, marginBottom: 8, opacity: 0.7 }}>
                        SECTIONS & FOLDERS
                    </div>
                    <div 
                        className={`adm-tree-pane-row ${activeFolder === '' ? 'active' : ''}`}
                        onClick={() => { setActiveFolder(''); setSelectedRows([]); }}
                    >
                        <i className="codicon codicon-home" style={{ marginRight: 6 }} />
                        <span>All Groups</span>
                    </div>

                    {folders.map(f => {
                        const parts = splitPathIntoSections(f);
                        const depth = parts.length - 1;
                        return (
                            <div 
                                key={f} 
                                className={`adm-tree-pane-row ${activeFolder === f ? 'active' : ''}`}
                                style={{ paddingLeft: `${8 + depth * 14}px` }}
                                onClick={() => { setActiveFolder(f); setSelectedRows([]); }}
                            >
                                <i className="codicon codicon-folder" style={{ marginRight: 6 }} />
                                <span>{parts[parts.length - 1]}</span>
                            </div>
                        );
                    })}
                </div>

                {/* Right Explorer-style Details Table */}
                <div className="adm-table-wrap" style={{ flex: 1, overflowY: 'auto' }}>
                    {error && (
                        <div className="adm-hint" style={{ background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)', margin: '10px 16px' }}>
                            <i className="codicon codicon-error" /> {error}
                        </div>
                    )}

                    {loading ? (
                        <div style={{ padding: 30, textAlign: 'center', opacity: 0.7 }}>Loading groups...</div>
                    ) : explorerRows.length === 0 ? (
                        <div style={{ padding: 30, textAlign: 'center', opacity: 0.6 }}>This folder is empty.</div>
                    ) : (
                        <table className="adm-table">
                            <thead>
                                <tr>
                                    <th>Group</th>
                                    <th>Server</th>
                                    <th>Authorization</th>
                                    <th>Currency</th>
                                    <th>Default Gateway</th>
                                </tr>
                            </thead>
                            <tbody>
                                {explorerRows.map(row => {
                                    const isSelected = selectedRows.includes(row.fullName);
                                    
                                    if (row.type === 'folder') {
                                        return (
                                            <tr 
                                                key={row.fullName} 
                                                className={isSelected ? 'selected' : ''}
                                                onClick={e => handleSelectRow(row.fullName, 'folder', e)}
                                                onDoubleClick={() => handleRowDoubleClick(row)}
                                                onContextMenu={e => handleRightClick(row, e)}
                                            >
                                                <td>
                                                    <i className="codicon codicon-folder" style={{ color: '#f1c40f', marginRight: 6 }} />
                                                    <strong>{row.name}</strong>
                                                </td>
                                                <td>—</td>
                                                <td>—</td>
                                                <td>—</td>
                                                <td>—</td>
                                            </tr>
                                        );
                                    }

                                    // Render Group Row
                                    const g = row.groupData;
                                    const type = getGroupType(g.name);
                                    
                                    let settings: any = {};
                                    if (g.settings_json) {
                                        try { settings = JSON.parse(g.settings_json); } catch {}
                                    }
                                    
                                    const authStr = settings.authentication || 'Normal';
                                    const currStr = settings.currency || 'USD';
                                    const serverStr = settings.trade_server || 'MetaQuotes-Demo';
                                    const isConnEnabled = settings.enable_connections !== false;

                                    const gwy = gateways.find(gw => gw.id === settings.gateway_id);
                                    const gwName = gwy ? gwy.name : (settings.gateway_id ? `Gateway #${settings.gateway_id}` : 'None (B-Book)');

                                    return (
                                        <tr 
                                            key={g.name} 
                                            className={`${isSelected ? 'selected' : ''} ${!isConnEnabled ? 'adm-row-disabled' : ''}`}
                                            onClick={e => handleSelectRow(row.fullName, 'group', e)}
                                            onDoubleClick={() => handleRowDoubleClick(row)}
                                            onContextMenu={e => handleRightClick(row, e)}
                                        >
                                            <td>
                                                <i className="codicon codicon-organization" style={{ color: TYPE_COLORS[type] || '#ccc', marginRight: 6 }} />
                                                <strong>{row.name}</strong>
                                            </td>
                                            <td>{serverStr}</td>
                                            <td>{authStr}</td>
                                            <td>{currStr}</td>
                                            <td>
                                                {settings.gateway_id ? (
                                                    <span className="adm-tag" style={{ color: '#3498db', border: '1px solid #3498db55' }}>
                                                        A-Book: {gwName}
                                                    </span>
                                                ) : (
                                                    <span style={{ opacity: 0.5 }}>B-Book Local</span>
                                                )}
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>

            {/* Custom context menu popup */}
            {contextMenu && (
                <div 
                    className="adm-context-menu"
                    style={{ top: contextMenu.y, left: contextMenu.x }}
                    onClick={e => e.stopPropagation()}
                >
                    <button type="button" className="adm-context-item" disabled={!isSingleGroupSelected} onClick={() => handleEdit()}><i className="codicon codicon-edit" /> Edit Group</button>
                    <button type="button" className="adm-context-item" onClick={handleAdd}><i className="codicon codicon-add" /> Add Group</button>
                    <button type="button" className="adm-context-item adm-context-item-danger" disabled={selectedRows.length === 0} onClick={handleDelete}><i className="codicon codicon-trash" /> Delete</button>
                    <div className="adm-context-sep" />
                    <button type="button" className="adm-context-item" disabled={selectedRows.length !== 1} onClick={() => handleMove('up')}><i className="codicon codicon-arrow-up" /> Move Up</button>
                    <button type="button" className="adm-context-item" disabled={selectedRows.length !== 1} onClick={() => handleMove('down')}><i className="codicon codicon-arrow-down" /> Move Down</button>
                </div>
            )}

            {/* Rebuilt Group Settings Modal */}
            {showModal && (
                <GroupSettingsModal 
                    groupName={modalGroup}
                    initialName={addInitialName}
                    onClose={() => setShowModal(false)}
                    onSaved={loadData}
                />
            )}

            {/* Page Statusbar footer */}
            <div className="adm-statusbar">
                <span>Items: {explorerRows.length}</span>
                <span className="adm-sep">|</span>
                <span>Folders: {explorerRows.filter(r => r.type === 'folder').length}</span>
                <span className="adm-sep">|</span>
                <span>Groups: {explorerRows.filter(r => r.type === 'group').length}</span>
            </div>
        </div>
    );
}
