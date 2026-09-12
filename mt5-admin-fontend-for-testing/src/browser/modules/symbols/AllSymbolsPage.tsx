// @ts-nocheck
import * as React from 'react';
import { API } from '../api';
import { getHighestOrderGroup } from './SymbolFolderUtils';
import { SymbolFilterBar } from './SymbolFilterBar';
import { SymbolSettingsModal } from './modal/SymbolSettingsModal';

export function AllSymbolsPage(): React.ReactElement {
    const [symbols, setSymbols] = React.useState<any[]>([]);
    const [filtered, setFiltered] = React.useState<any[]>([]);
    const [selectedRows, setSelectedRows] = React.useState<string[]>([]);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState<string | null>(null);

    // Modal state
    const [showSettingsModal, setShowSettingsModal] = React.useState(false);
    const [settingsSymbol, setSettingsSymbol] = React.useState<string | null>(null);

    const loadData = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await API.getSymbols();
            // Filter out dummy folders
            const validSymbols = data.filter((s: any) => !s.symbol.endsWith('.dummy'));
            setSymbols(validSymbols);
            setFiltered(validSymbols);
        } catch (err: any) {
            setError(err.message || 'Failed to load symbols.');
        } finally {
            setLoading(false);
        }
    };

    React.useEffect(() => {
        loadData();
    }, []);

    // Selection handlers
    const handleSelectRow = (symbol: string, e: React.MouseEvent) => {
        if (e.ctrlKey || e.metaKey) {
            if (selectedRows.includes(symbol)) {
                setSelectedRows(prev => prev.filter(r => r !== symbol));
            } else {
                setSelectedRows(prev => [...prev, symbol]);
            }
        } else if (e.shiftKey && selectedRows.length > 0) {
            const last = selectedRows[selectedRows.length - 1];
            const lastIdx = filtered.findIndex(r => r.symbol === last);
            const currIdx = filtered.findIndex(r => r.symbol === symbol);
            if (lastIdx !== -1 && currIdx !== -1) {
                const start = Math.min(lastIdx, currIdx);
                const end = Math.max(lastIdx, currIdx);
                const range = filtered.slice(start, end + 1).map(r => r.symbol);
                setSelectedRows(prev => Array.from(new Set([...prev, ...range])));
            }
        } else {
            setSelectedRows([symbol]);
        }
    };

    const handleEdit = (name?: string) => {
        const target = name || selectedRows[0];
        if (!target) return;
        setSettingsSymbol(target);
        setShowSettingsModal(true);
    };

    const handleFilterApplied = (filteredList: any[]) => {
        setFiltered(filteredList);
        setSelectedRows([]);
    };

    const isSingleSelected = selectedRows.length === 1;

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
            {/* Filter controls */}
            <SymbolFilterBar 
                symbols={symbols} 
                onFilterApplied={handleFilterApplied} 
            />

            {/* Toolbar for flat list operations */}
            <div className="adm-toolbar" style={{ borderBottom: 'none', padding: '4px 12px' }}>
                <button type="button" className="adm-btn" disabled={!isSingleSelected} onClick={() => handleEdit()}>
                    <i className="codicon codicon-edit" /> Edit Selected Symbol
                </button>
                <button type="button" className="adm-btn" onClick={loadData}>
                    <i className="codicon codicon-refresh" /> Refresh
                </button>
            </div>

            {/* Error notifications */}
            {error && (
                <div className="adm-hint" style={{ background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)', margin: '10px 16px' }}>
                    <i className="codicon codicon-error" /> {error}
                </div>
            )}

            {/* Flat Table */}
            <div className="adm-table-wrap" style={{ flex: 1, overflowY: 'auto' }}>
                {loading ? (
                    <div style={{ padding: 20, textAlign: 'center', opacity: 0.7 }}>Loading all symbols...</div>
                ) : filtered.length === 0 ? (
                    <div style={{ padding: 20, textAlign: 'center', opacity: 0.6 }}>No symbols found matching active search parameters.</div>
                ) : (
                    <table className="adm-table">
                        <thead>
                            <tr>
                                <th>Symbol Path Name</th>
                                <th>Type (Highest Group)</th>
                                <th>Execution Mode</th>
                                <th>Digits</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filtered.map(s => {
                                const isSelected = selectedRows.includes(s.symbol);
                                
                                let settings: any = {};
                                if (s.settings_json) {
                                    try { settings = JSON.parse(s.settings_json); } catch {}
                                }
                                
                                const highestGroup = getHighestOrderGroup(s.symbol) || 'Root';
                                const execMode = settings.execution_mode || 'Instant';
                                const digitsVal = s.digits !== undefined ? s.digits : 5;

                                return (
                                    <tr 
                                        key={s.symbol}
                                        className={isSelected ? 'selected' : ''}
                                        onClick={e => handleSelectRow(s.symbol, e)}
                                        onDoubleClick={() => handleEdit(s.symbol)}
                                    >
                                        <td>
                                            <i className="codicon codicon-graph" style={{ color: '#2ecc71', marginRight: 6 }} />
                                            <strong>{s.symbol}</strong>
                                        </td>
                                        <td>{highestGroup}</td>
                                        <td>
                                            <span className="adm-tag">{execMode}</span>
                                        </td>
                                        <td>{digitsVal}</td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                )}
            </div>

            {/* Status bar */}
            <div className="adm-statusbar">
                <span>Matching symbols: {filtered.length} of {symbols.length}</span>
                {selectedRows.length > 0 && (
                    <>
                        <span className="adm-sep">|</span>
                        <span>Selected: {selectedRows.length}</span>
                    </>
                )}
            </div>

            {/* Settings Modal */}
            {showSettingsModal && (
                <SymbolSettingsModal 
                    symbolName={settingsSymbol}
                    onClose={() => setShowSettingsModal(false)}
                    onSaved={loadData}
                />
            )}
        </div>
    );
}
