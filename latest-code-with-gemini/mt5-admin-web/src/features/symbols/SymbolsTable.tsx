import * as React from 'react';
import { getHighestOrderGroup } from './SymbolFolderUtils';

interface SymbolsTableProps {
    contents: any[];
    selectedRows: string[];
    onSelectRow: (fullName: string, e: React.MouseEvent) => void;
    onDoubleClick: (row: any) => void;
    onContextMenu: (row: any, e: React.MouseEvent) => void;
    loading: boolean;
}

export function SymbolsTable({ contents, selectedRows, onSelectRow, onDoubleClick, onContextMenu, loading }: SymbolsTableProps): React.ReactElement {
    if (loading) {
        return (
            <div className="adm-table-wrap" style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center', opacity: 0.7 }}>
                <span>Loading folder contents...</span>
            </div>
        );
    }

    // Filter out dummy folder node indicators
    const visibleContents = contents.filter(c => !c.fullName.endsWith('.dummy'));

    if (visibleContents.length === 0) {
        return (
            <div className="adm-table-wrap" style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center', opacity: 0.6 }}>
                <span>Folder is empty. Right-click or use toolbar to add items.</span>
            </div>
        );
    }

    return (
        <div className="adm-table-wrap" style={{ flex: 1, overflowY: 'auto' }}>
            <table className="adm-table">
                <thead>
                    <tr>
                        <th>Symbol / Folder</th>
                        <th>Type (Highest Group)</th>
                        <th>Execution Mode</th>
                        <th>Digits</th>
                    </tr>
                </thead>
                <tbody>
                    {visibleContents.map(row => {
                        const isSelected = selectedRows.includes(row.fullName);

                        if (row.type === 'folder') {
                            return (
                                <tr 
                                    key={row.fullName}
                                    className={isSelected ? 'selected' : ''}
                                    onClick={e => onSelectRow(row.fullName, e)}
                                    onDoubleClick={() => onDoubleClick(row)}
                                    onContextMenu={e => onContextMenu(row, e)}
                                >
                                    <td>
                                        <i className="codicon codicon-folder" style={{ color: '#f1c40f', marginRight: 6 }} />
                                        <strong>{row.name}</strong>
                                    </td>
                                    <td>—</td>
                                    <td>—</td>
                                    <td>—</td>
                                </tr>
                            );
                        }

                        // Render Symbol
                        const s = row.data;
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
                                onClick={e => onSelectRow(row.fullName, e)}
                                onDoubleClick={() => onDoubleClick(row)}
                                onContextMenu={e => onContextMenu(row, e)}
                            >
                                <td>
                                    <i className="codicon codicon-graph" style={{ color: '#2ecc71', marginRight: 6 }} />
                                    <strong>{row.name}</strong>
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
        </div>
    );
}
