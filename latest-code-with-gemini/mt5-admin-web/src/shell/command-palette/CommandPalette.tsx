import * as React from 'react';
import { MT5_ADMIN_TREE, AdminTreeNode } from '../tree/mt5-admin-tree';

interface CommandPaletteProps {
    onClose: () => void;
    onOpenNode: (nodeId: string, label: string) => void;
}

interface FlatNode {
    id: string;
    label: string;
    icon?: string;
    path: string;
}

function flatten(nodes: AdminTreeNode[], parentPath = ''): FlatNode[] {
    const out: FlatNode[] = [];
    for (const n of nodes) {
        const path = parentPath ? `${parentPath} › ${n.label}` : n.label;
        const isLeaf = !n.children || n.children.length === 0;
        if (isLeaf) out.push({ id: n.id, label: n.label, icon: n.icon, path });
        else out.push(...flatten(n.children!, path));
    }
    return out;
}

const ALL_NODES: FlatNode[] = [
    ...flatten(MT5_ADMIN_TREE),
    { id: 'settings', label: 'Connection Settings', icon: 'settings-gear', path: 'Settings' },
];

/**
 * Ctrl+Shift+P — jump to any admin section, VS Code style.
 * Simple subsequence match; keyboard navigable.
 */
export function CommandPalette({ onClose, onOpenNode }: CommandPaletteProps): React.ReactElement {
    const [query, setQuery] = React.useState('');
    const [activeIdx, setActiveIdx] = React.useState(0);
    const inputRef = React.useRef<HTMLInputElement>(null);
    const listRef = React.useRef<HTMLDivElement>(null);

    React.useEffect(() => {
        inputRef.current?.focus();
    }, []);

    const matches = React.useMemo(() => {
        const q = query.trim().toLowerCase();
        if (!q) return ALL_NODES.slice(0, 60);
        return ALL_NODES.filter(
            (n) => n.label.toLowerCase().includes(q) || n.path.toLowerCase().includes(q)
        ).slice(0, 60);
    }, [query]);

    React.useEffect(() => setActiveIdx(0), [query]);

    React.useEffect(() => {
        const el = listRef.current?.children[activeIdx] as HTMLElement | undefined;
        el?.scrollIntoView({ block: 'nearest' });
    }, [activeIdx]);

    const pick = (n: FlatNode) => {
        onOpenNode(n.id, n.label);
        onClose();
    };

    return (
        <div className="wb-palette-overlay" onMouseDown={onClose}>
            <div className="wb-palette" onMouseDown={(e) => e.stopPropagation()}>
                <input
                    ref={inputRef}
                    className="wb-palette-input"
                    placeholder="Go to section… (type to filter)"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === 'Escape') onClose();
                        else if (e.key === 'ArrowDown') {
                            e.preventDefault();
                            setActiveIdx((i) => Math.min(matches.length - 1, i + 1));
                        } else if (e.key === 'ArrowUp') {
                            e.preventDefault();
                            setActiveIdx((i) => Math.max(0, i - 1));
                        } else if (e.key === 'Enter' && matches[activeIdx]) {
                            pick(matches[activeIdx]);
                        }
                    }}
                />
                <div className="wb-palette-list" ref={listRef}>
                    {matches.map((n, i) => (
                        <div
                            key={n.id}
                            className={`wb-palette-item${i === activeIdx ? ' active' : ''}`}
                            onMouseEnter={() => setActiveIdx(i)}
                            onClick={() => pick(n)}
                        >
                            <i className={`codicon codicon-${n.icon ?? 'server'}`} />
                            <span>{n.label}</span>
                            <span className="wb-palette-item-path">{n.path}</span>
                        </div>
                    ))}
                    {matches.length === 0 && (
                        <div className="wb-palette-item" style={{ opacity: 0.6 }}>
                            No matching section
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
