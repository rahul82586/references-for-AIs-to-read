import * as React from 'react';
import { ReactWidget } from '@theia/core/lib/browser';
import { CommandService } from '@theia/core/lib/common/command';
import { AdminTreeNode } from '../common/mt5-admin-tree';
export declare const MT5_ADMIN_TREE_WIDGET_ID = "mt5-admin-tree-widget";
export declare class Mt5AdminTreeWidget extends ReactWidget {
    protected readonly commandService: CommandService;
    protected expandedNodes: Set<string>;
    protected selectedNodeId: string | undefined;
    protected groupsList: any[];
    protected init(): void;
    refreshTree(): Promise<void>;
    protected toggleNode(id: string): void;
    protected selectNode(node: AdminTreeNode): void;
    protected buildGroupsSubtree(): AdminTreeNode[];
    protected renderNode(node: AdminTreeNode, depth?: number): React.ReactNode;
    protected render(): React.ReactNode;
}
//# sourceMappingURL=mt5-admin-tree-widget.d.ts.map