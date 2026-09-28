import * as React from 'react';
import { TreeView } from '../tree/TreeView';

interface SideBarProps {
    visible: boolean;
    onOpenNode: (nodeId: string, label: string) => void;
}

/** Resizable sidebar hosting the MT5 Administrator tree. */
export function SideBar({ visible, onOpenNode }: SideBarProps): React.ReactElement | null {
    const [width, setWidth] = React.useState<number>(() => {
        const saved = Number(localStorage.getItem('mt5-admin-sidebar-width'));
        return saved >= 180 && saved <= 560 ? saved : 280;
    });
    const dragging = React.useRef(false);
    const widthRef = React.useRef(width);
    widthRef.current = width;

    React.useEffect(() => {
        const onMove = (e: MouseEvent) => {
            if (!dragging.current) return;
            const w = Math.min(560, Math.max(180, e.clientX - 48));
            setWidth(w);
        };
        const onUp = () => {
            if (dragging.current) {
                dragging.current = false;
                localStorage.setItem('mt5-admin-sidebar-width', String(widthRef.current));
                document.body.style.cursor = '';
                document.body.style.userSelect = '';
            }
        };
        window.addEventListener('mousemove', onMove);
        window.addEventListener('mouseup', onUp);
        return () => {
            window.removeEventListener('mousemove', onMove);
            window.removeEventListener('mouseup', onUp);
        };
    }, []);

    if (!visible) return null;

    return (
        <>
            <div className="wb-sidebar" style={{ width }}>
                <div className="wb-sidebar-content">
                    <TreeView onOpenNode={onOpenNode} />
                </div>
            </div>
            <div
                className="wb-sidebar-resizer"
                onMouseDown={() => {
                    dragging.current = true;
                    document.body.style.cursor = 'col-resize';
                    document.body.style.userSelect = 'none';
                }}
            />
        </>
    );
}
