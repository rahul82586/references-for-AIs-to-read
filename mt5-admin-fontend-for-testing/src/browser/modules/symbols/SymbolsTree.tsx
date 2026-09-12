import * as React from 'react';
import { splitSymbolPath } from './SymbolFolderUtils';

interface SymbolsTreeProps {
    folders: string[];
    activeFolder: string;
    onSelectFolder: (folder: string) => void;
}

export function SymbolsTree({ folders, activeFolder, onSelectFolder }: SymbolsTreeProps): React.ReactElement {
    return (
        <div className="adm-tree-pane" style={{ width: 220, borderRight: '1px solid var(--theia-border)', overflowY: 'auto', padding: 8 }}>
            <div className="adm-tree-pane-header" style={{ fontWeight: 'bold', fontSize: 11, marginBottom: 8, opacity: 0.7 }}>
                SYMBOL GROUPS & FOLDERS
            </div>
            
            {/* All Symbols root folder */}
            <div 
                className={`adm-tree-pane-row ${activeFolder === '' ? 'active' : ''}`}
                onClick={() => onSelectFolder('')}
            >
                <i className="codicon codicon-home" style={{ marginRight: 6 }} />
                <span>All Symbols</span>
            </div>

            {/* Folder list with indentation levels */}
            {folders.map(f => {
                const parts = splitSymbolPath(f);
                const depth = parts.length - 1;
                return (
                    <div 
                        key={f} 
                        className={`adm-tree-pane-row ${activeFolder === f ? 'active' : ''}`}
                        style={{ paddingLeft: `${8 + depth * 14}px` }}
                        onClick={() => onSelectFolder(f)}
                    >
                        <i className="codicon codicon-folder" style={{ marginRight: 6 }} />
                        <span>{parts[parts.length - 1]}</span>
                    </div>
                );
            })}
        </div>
    );
}
