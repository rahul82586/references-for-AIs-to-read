import * as React from 'react';

interface SymbolsContextMenuProps {
    menu: { x: number, y: number, target: string, type: 'folder' | 'symbol' | 'root' };
    isSingleSymbolSelected: boolean;
    onClose: () => void;
    onAddSymbol: () => void;
    onAddFolder: () => void;
    onEdit: () => void;
    onDelete: () => void;
    onSort: () => void;
    onImportServer: () => void;
}

export function SymbolsContextMenu({ 
    menu, 
    isSingleSymbolSelected, 
    onClose, 
    onAddSymbol, 
    onAddFolder, 
    onEdit, 
    onDelete, 
    onSort, 
    onImportServer 
}: SymbolsContextMenuProps): React.ReactElement {
    React.useEffect(() => {
        const handleOutsideClick = () => onClose();
        window.addEventListener('click', handleOutsideClick);
        return () => window.removeEventListener('click', handleOutsideClick);
    }, [onClose]);

    const handleAction = (actionFn: () => void) => {
        actionFn();
        onClose();
    };

    return (
        <div 
            className="adm-context-menu"
            style={{ top: menu.y, left: menu.x }}
            onClick={e => e.stopPropagation()}
        >
            <button type="button" className="adm-context-item" onClick={() => handleAction(onAddSymbol)}>
                <i className="codicon codicon-add" /> Add Symbol
            </button>
            <button type="button" className="adm-context-item" onClick={() => handleAction(onAddFolder)}>
                <i className="codicon codicon-new-folder" /> Add Folder
            </button>
            <button type="button" className="adm-context-item" disabled={!isSingleSymbolSelected} onClick={() => handleAction(onEdit)}>
                <i className="codicon codicon-edit" /> Edit settings
            </button>
            <button type="button" className="adm-context-item adm-context-item-danger" onClick={() => handleAction(onDelete)}>
                <i className="codicon codicon-trash" /> Delete
            </button>

            <div className="adm-context-sep" />

            <button type="button" className="adm-context-item" onClick={() => handleAction(onSort)}>
                <i className="codicon codicon-symbol-class" /> Sort Alphabetically
            </button>
            <button type="button" className="adm-context-item" onClick={() => handleAction(onImportServer)}>
                <i className="codicon codicon-cloud-download" /> Import from Server
            </button>

            <div className="adm-context-sep" />

            <button type="button" className="adm-context-item" onClick={() => handleAction(() => alert(`Navigating to journal logs for: ${menu.target}`))}>
                <i className="codicon codicon-notebook" /> Journal logs
            </button>
            <button type="button" className="adm-context-item" onClick={() => handleAction(() => alert(`Jumping to 1-minute charts for: ${menu.target}`))}>
                <i className="codicon codicon-graph-line" /> Charts
            </button>
            <button type="button" className="adm-context-item" onClick={() => handleAction(() => alert(`Jumping to ticks database for: ${menu.target}`))}>
                <i className="codicon codicon-history" /> Tick history
            </button>
        </div>
    );
}
