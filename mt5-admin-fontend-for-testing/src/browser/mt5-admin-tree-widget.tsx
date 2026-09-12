// @ts-nocheck
import * as React from 'react';
import { injectable, postConstruct, inject } from '@theia/core/shared/inversify';
import { ReactWidget } from '@theia/core/lib/browser';
import { CommandService } from '@theia/core/lib/common/command';
import { MT5_ADMIN_TREE, AdminTreeNode } from '../common/mt5-admin-tree';
import { API } from './modules/api';

export const MT5_ADMIN_TREE_WIDGET_ID = 'mt5-admin-tree-widget';

@injectable()
export class Mt5AdminTreeWidget extends ReactWidget {

    @inject(CommandService)
    protected readonly commandService: CommandService;

    protected expandedNodes = new Set<string>();
    protected selectedNodeId: string | undefined;
    protected groupsList: any[] = [];

    @postConstruct()
    protected init(): void {
        this.id = MT5_ADMIN_TREE_WIDGET_ID;
        this.title.label = 'MT5 Admin';
        this.title.caption = 'MT5 Administrator';
        this.title.closable = false;
        this.title.iconClass = 'codicon codicon-server';
        this.addClass('mt5-admin-tree-widget');
        this.node.tabIndex = 0;

        // Expand top-level sections by default
        this.expandedNodes.add('groups');
        this.expandedNodes.add('clients-and-accounts');
        this.expandedNodes.add('positions');
        this.expandedNodes.add('routing');
        this.expandedNodes.add('symbols');
        
        this.refreshTree();
        this.update();
    }

    async refreshTree(): Promise<void> {
        try {
            const data = await API.getGroups();
            this.groupsList = data;
            this.update();
        } catch (e) {
            console.error('Failed to load groups list for sidebar tree:', e);
        }
    }

    protected toggleNode(id: string): void {
        if (this.expandedNodes.has(id)) {
            this.expandedNodes.delete(id);
        } else {
            this.expandedNodes.add(id);
        }
        this.update();
    }

    protected selectNode(node: AdminTreeNode): void {
        this.selectedNodeId = node.id;
        this.update();
        
        if (node.id.startsWith('groups:')) {
            // Open the master Groups page and pass the selected path
            this.commandService.executeCommand('mt5-admin:open-view', node.id, 'Groups');
        } else {
            this.commandService.executeCommand('mt5-admin:open-view', node.id, node.label);
        }
    }

    protected buildGroupsSubtree(): AdminTreeNode[] {
        const root: AdminTreeNode[] = [];

        const findOrCreateNode = (parentList: AdminTreeNode[], name: string, fullPath: string, isLeaf: boolean): AdminTreeNode => {
            const id = `groups:${fullPath}`;
            let existing = parentList.find(n => n.id === id);
            if (!existing) {
                existing = {
                    id,
                    label: name,
                    icon: isLeaf ? 'folder' : 'folder-active',
                    children: []
                };
                parentList.push(existing);
            }
            return existing;
        };

        for (const g of this.groupsList) {
            const parts = g.name.split('\\').map(p => p.trim()).filter(Boolean);
            let currentLevel = root;
            let pathAccum = '';
            for (let i = 0; i < parts.length; i++) {
                const part = parts[i];
                pathAccum = pathAccum ? `${pathAccum}\\${part}` : part;
                const isLeaf = i === parts.length - 1;
                const node = findOrCreateNode(currentLevel, part, pathAccum, isLeaf);
                currentLevel = node.children!;
            }
        }

        const cleanChildren = (list: AdminTreeNode[]) => {
            for (const n of list) {
                if (n.children && n.children.length === 0) {
                    delete n.children;
                } else if (n.children) {
                    cleanChildren(n.children);
                }
            }
        };
        cleanChildren(root);
        return root;
    }

    protected renderNode(node: AdminTreeNode, depth: number = 0): React.ReactNode {
        // Dynamically compute child items for the groups parent node
        if (node.id === 'groups') {
            node.children = this.buildGroupsSubtree();
        }

        const hasChildren = node.children && node.children.length > 0;
        const isExpanded = this.expandedNodes.has(node.id);
        const isSelected = this.selectedNodeId === node.id;
        const indent = depth * 16;

        return (
            <React.Fragment key={node.id}>
                <div
                    className={`mt5-admin-tree-row${isSelected ? ' selected' : ''}`}
                    style={{ paddingLeft: `${8 + indent}px` }}
                    onClick={() => {
                        if (hasChildren) {
                            this.toggleNode(node.id);
                        } else {
                            this.selectNode(node);
                        }
                    }}
                    onDoubleClick={() => {
                        this.selectNode(node);
                    }}
                    title={node.label}
                >
                    {/* Expand/collapse arrow */}
                    <span className={`mt5-admin-tree-arrow${hasChildren ? ' visible' : ''}`}>
                        {hasChildren
                            ? (isExpanded
                                ? <i className="codicon codicon-chevron-down" />
                                : <i className="codicon codicon-chevron-right" />)
                            : <span style={{ display: 'inline-block', width: '16px' }} />}
                    </span>
                    {/* Node icon */}
                    {node.icon && (
                        <i className={`codicon codicon-${node.icon} mt5-admin-tree-icon`} />
                    )}
                    {/* Node label */}
                    <span className="mt5-admin-tree-label">{node.label}</span>
                </div>

                {/* Children (collapsed if not expanded) */}
                {hasChildren && isExpanded && (
                    <div className="mt5-admin-tree-children">
                        {node.children!.map(child => this.renderNode(child, depth + 1))}
                    </div>
                )}
            </React.Fragment>
        );
    }

    protected render(): React.ReactNode {
        return (
            <div className="mt5-admin-tree-container">
                <div className="mt5-admin-tree-header">
                    <span className="mt5-admin-tree-header-label">ADMINISTRATOR</span>
                    <button className="adm-icon-btn" style={{ marginLeft: 'auto', marginRight: 8 }} onClick={() => this.refreshTree()} title="Refresh sidebar tree">
                        <i className="codicon codicon-refresh" />
                    </button>
                </div>
                <div className="mt5-admin-tree-body">
                    {MT5_ADMIN_TREE.map(node => this.renderNode(node, 0))}
                </div>
            </div>
        );
    }
}
