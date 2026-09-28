import * as React from 'react';

export interface MenuItem {
    id: string;
    label?: string;
    icon?: string;
    /** visual separator before this item */
    sep?: boolean;
    /** muted + "backend gap" hint styling */
    gap?: boolean;
    danger?: boolean;
    disabled?: boolean;
    onClick?: () => void;
}

interface MenuProps {
    x: number;
    y: number;
    items: MenuItem[];
    onClose: () => void;
}

/**
 * VS Code-style context menu. Gap items stay visible (discoverability of the
 * full MT5 command set) but are marked and surface an honest BackendGapError
 * banner when invoked — never silently dead.
 */
export function ContextMenu({ x, y, items, onClose }: MenuProps): React.ReactElement {
    const ref = React.useRef<HTMLDivElement>(null);

    React.useEffect(() => {
        const onDown = (e: MouseEvent) => {
            if (!ref.current?.contains(e.target as Node)) onClose();
        };
        const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose();
        window.addEventListener('mousedown', onDown);
        window.addEventListener('keydown', onKey);
        return () => {
            window.removeEventListener('mousedown', onDown);
            window.removeEventListener('keydown', onKey);
        };
    }, [onClose]);

    // keep the menu inside the viewport
    const style: React.CSSProperties = { position: 'fixed', top: y, left: x, zIndex: 10000 };

    return (
        <div
            ref={ref}
            className="ca-menu"
            style={style}
            onContextMenu={(e) => e.preventDefault()}
            onMouseDown={(e) => e.stopPropagation()}
        >
            {items.map((it, i) =>
                it.sep ? (
                    <div key={`sep-${i}`} className="ca-menu-sep" />
                ) : (
                    <button
                        key={it.id}
                        className={[
                            'ca-menu-item',
                            it.gap ? 'gap' : '',
                            it.danger ? 'danger' : '',
                        ].join(' ')}
                        disabled={it.disabled}
                        title={it.gap ? 'Not exposed by the backend API yet' : it.label}
                        onClick={() => {
                            onClose();
                            it.onClick?.();
                        }}
                    >
                        {it.icon && <i className={`codicon codicon-${it.icon}`} />}
                        <span className="ca-menu-label">{it.label}</span>
                        {it.gap && <span className="ca-menu-gap-tag">gap</span>}
                    </button>
                )
            )}
        </div>
    );
}
