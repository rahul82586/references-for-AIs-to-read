/**
 * TreeView — pure-React port of the Theia Mt5AdminTreeWidget.
 * Same look (mt5-admin-tree-* / wb-tree-* classes), same behaviour:
 *  - renders MT5_ADMIN_TREE with expand/collapse
 *  - 'groups' node dynamically grows the real group folder subtree
 *    (backslash paths → nested folders), fetched through the API facade
 *  - click on a leaf (or double-click anywhere) → onOpenNode(id, label)
 */
import * as React from 'react';
import { MT5_ADMIN_TREE, AdminTreeNode } from './mt5-admin-tree';
import { API } from '../../services/api';

interface TreeViewProps {
    onOpenNode: (nodeId: string, label: string) => void;
}

const DEFAULT_EXPANDED = ['groups', 'clients-and-accounts', 'positions', 'routing', 'symbols'];

export function TreeView({ onOpenNode }: TreeViewProps): React.ReactElement {
    const [expanded, setExpanded] = React.useState<Set<string>>(() => new Set(DEFAULT_EXPANDED));
    const [selectedId, setSelectedId] = React.useState<string | undefined>();
    const [groupsList, setGroupsList] = React.useState<any[]>([]);

    const refreshGroups = React.useCallback(async () => {
        try {
            const data = await API.getGroups();
            setGroupsList(Array.isArray(data) ? data : []);
        } catch (e) {
            console.error('Failed to load groups for sidebar tree:', e);
        }
    }, []);

    React.useEffect(() => {
        void refreshGroups();
    }, [refreshGroups]);

    const toggle = React.useCallback((id: string) => {
        setExpanded((prev) => {
            const next = new Set(prev);
            if (next.has(id)) next.delete(id);
            else next.add(id);
            return next;
        });
    }, []);

    const select = React.useCallback(
        (node: AdminTreeNode) => {
            setSelectedId(node.id);
            onOpenNode(node.id, node.label);
        },
        [onOpenNode]
    );

    /* builds the live groups subtree (ported verbatim from the Theia widget) */
    const buildGroupsSubtree = React.useCallback((): AdminTreeNode[] => {
        const root: AdminTreeNode[] = [];
        const findOrCreateNode = (
            parentList: AdminTreeNode[],
            name: string,
            fullPath: string,
            isLeaf: boolean
        ): AdminTreeNode => {
            const id = `groups:${fullPath}`;
            let existing = parentList.find((n) => n.id === id);
            if (!existing) {
                existing = { id, label: name, icon: isLeaf ? 'folder' : 'folder-active', children: [] };
                parentList.push(existing);
            }
            return existing;
        };
        for (const g of groupsList) {
            if (!g?.name) continue;
            const parts = String(g.name).split('\\').map((p: string) => p.trim()).filter(Boolean);
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
                if (n.children && n.children.length === 0) delete n.children;
                else if (n.children) cleanChildren(n.children);
            }
        };
        cleanChildren(root);
        return root;
    }, [groupsList]);

    const renderNode = (nodeIn: AdminTreeNode, depth = 0): React.ReactNode => {
        const node = nodeIn.id === 'groups' ? { ...nodeIn, children: buildGroupsSubtree() } : nodeIn;
        const hasChildren = Boolean(node.children && node.children.length > 0);
        const isExpanded = expanded.has(node.id);
        const isSelected = selectedId === node.id;
        const indent = depth * 14;

        return (
            <React.Fragment key={node.id}>
                <div
                    className={`wb-tree-row${isSelected ? ' selected' : ''}`}
                    style={{ paddingLeft: `${8 + indent}px` }}
                    onClick={() => (hasChildren ? toggle(node.id) : select(node))}
                    onDoubleClick={() => select(node)}
                    title={node.label}
                >
                    <span className="wb-tree-arrow">
                        {hasChildren ? (
                            <i className={`codicon codicon-chevron-${isExpanded ? 'down' : 'right'}`} />
                        ) : null}
                    </span>
                    {node.icon && <i className={`codicon codicon-${node.icon}`} />}
                    <span className="wb-tree-label">{node.label}</span>
                </div>
                {hasChildren && isExpanded && (
                    <div>{node.children!.map((child) => renderNode(child, depth + 1))}</div>
                )}
            </React.Fragment>
        );
    };

    return (
        <>
            <div className="wb-tree-section-title">
                <span>Administrator</span>
                <i className="codicon codicon-refresh" title="Refresh sidebar tree" onClick={() => void refreshGroups()} />
            </div>
            <div className="wb-tree">{MT5_ADMIN_TREE.map((n) => renderNode(n, 0))}</div>
        </>
    );
}
