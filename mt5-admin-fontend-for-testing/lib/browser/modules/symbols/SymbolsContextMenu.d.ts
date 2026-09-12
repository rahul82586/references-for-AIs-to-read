import * as React from 'react';
interface SymbolsContextMenuProps {
    menu: {
        x: number;
        y: number;
        target: string;
        type: 'folder' | 'symbol' | 'root';
    };
    isSingleSymbolSelected: boolean;
    onClose: () => void;
    onAddSymbol: () => void;
    onAddFolder: () => void;
    onEdit: () => void;
    onDelete: () => void;
    onSort: () => void;
    onImportServer: () => void;
}
export declare function SymbolsContextMenu({ menu, isSingleSymbolSelected, onClose, onAddSymbol, onAddFolder, onEdit, onDelete, onSort, onImportServer }: SymbolsContextMenuProps): React.ReactElement;
export {};
//# sourceMappingURL=SymbolsContextMenu.d.ts.map