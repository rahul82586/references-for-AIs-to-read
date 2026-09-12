/**
 * MT5 Admin tree node types — mirrors the full MT5 Administrator sidebar.
 */
export interface AdminTreeNode {
    id: string;
    label: string;
    icon?: string;
    children?: AdminTreeNode[];
}
/**
 * Full MT5 Administrator sidebar tree, taken from the official documentation.
 * Each leaf node opens a dedicated tab in the main area.
 */
export declare const MT5_ADMIN_TREE: AdminTreeNode[];
//# sourceMappingURL=mt5-admin-tree.d.ts.map