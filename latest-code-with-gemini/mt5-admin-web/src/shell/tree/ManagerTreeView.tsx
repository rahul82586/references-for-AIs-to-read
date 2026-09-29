import * as React from 'react';
import { MT5_MANAGER_TREE, ManagerTreeNode } from './mt5-manager-tree';

interface Props {
    onOpenNode: (nodeId: string, label: string) => void;
}

const DEFAULT_EXPANDED = ['manager.trade'];

/** Manager navigator — same look & behaviour as the admin tree. */
export function ManagerTreeView({ onOpenNode }: Props): React.ReactElement {
    const [expanded, setExpanded] = React.useState<Set<string>>(() => new Set(DEFAULT_EXPANDED));
    const [selectedId, setSelectedId] = React.useState<string | undefined>();

    const toggle = (id: string) =>
        setExpanded((prev) => {
            const next = new Set(prev);
            if (next.has(id)) next.delete(id);
            else next.add(id);
            return next;
        });

    const select = (node: ManagerTreeNode) => {
        setSelectedId(node.id);
        onOpenNode(node.id, node.label);
    };

    const renderNode = (node: ManagerTreeNode, depth = 0): React.ReactNode => {
        const hasChildren = Boolean(node.children && node.children.length > 0);
        const isExpanded = expanded.has(node.id);
        const isSelected = selectedId === node.id;
        return (
            <React.Fragment key={node.id}>
                <div
                    className={`wb-tree-row${isSelected ? ' selected' : ''}`}
                    style={{ paddingLeft: `${8 + depth * 14}px` }}
                    onClick={() => (hasChildren ? toggle(node.id) : select(node))}
                    onDoubleClick={() => select(node)}
                    title={node.api ? `${node.label} — ${node.api}` : node.label}
                >
                    <span className="wb-tree-arrow">
                        {hasChildren ? (
                            <i className={`codicon codicon-chevron-${isExpanded ? 'down' : 'right'}`} />
                        ) : null}
                    </span>
                    {node.icon && <i className={`codicon codicon-${node.icon}`} />}
                    <span className="wb-tree-label">{node.label}</span>
                </div>
                {hasChildren && isExpanded && <div>{node.children!.map((c) => renderNode(c, depth + 1))}</div>}
            </React.Fragment>
        );
    };

    return (
        <>
            <div className="wb-tree-section-title">
                <span>Manager</span>
                <i className="codicon codicon-shield" title="Manager API session (Connect + rights) — wired in a later milestone" />
            </div>
            <div className="wb-tree">{MT5_MANAGER_TREE.map((n) => renderNode(n, 0))}</div>
        </>
    );
}
