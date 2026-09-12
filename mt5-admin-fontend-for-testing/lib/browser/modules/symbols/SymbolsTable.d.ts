import * as React from 'react';
interface SymbolsTableProps {
    contents: any[];
    selectedRows: string[];
    onSelectRow: (fullName: string, e: React.MouseEvent) => void;
    onDoubleClick: (row: any) => void;
    onContextMenu: (row: any, e: React.MouseEvent) => void;
    loading: boolean;
}
export declare function SymbolsTable({ contents, selectedRows, onSelectRow, onDoubleClick, onContextMenu, loading }: SymbolsTableProps): React.ReactElement;
export {};
//# sourceMappingURL=SymbolsTable.d.ts.map