import * as React from 'react';

let Z_TOP = 1000;
let OPEN_COUNT = 0;

interface FloatingWindowProps {
    /** element rendered inside the floating frame (usually the .adm-modal markup) */
    children: React.ReactNode;
    /** selector inside the frame used as the drag handle (defaults to the modal header) */
    handleSelector?: string;
    width?: number;
    height?: number;
    onClose?: () => void;
}

/**
 * FloatingWindow — makes any dialog a floatable, draggable, resizable window
 * instead of a fixed centered overlay (operator requirement).
 *  - drag: press the title bar (elements matching handleSelector)
 *  - resize: bottom-right grip
 *  - click anywhere on the window raises it (z-index)
 *  - multiple windows cascade on open
 * The backdrop is click-through: the workbench stays usable behind dialogs.
 */
export function FloatingWindow({
    children,
    handleSelector = '.adm-modal-header',
    width = 1020,
    height = 640,
    onClose,
}: FloatingWindowProps): React.ReactElement {
    const slot = OPEN_COUNT++;
    React.useEffect(() => () => { OPEN_COUNT = Math.max(0, OPEN_COUNT - 1); }, []);

    const [pos, setPos] = React.useState({ x: 90 + (slot % 6) * 34, y: 60 + (slot % 6) * 28 });
    const [size, setSize] = React.useState({ w: width, h: height });
    const [z, setZ] = React.useState(() => ++Z_TOP);

    React.useEffect(() => {
        if (!onClose) return;
        const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
        window.addEventListener('keydown', onKey);
        return () => window.removeEventListener('keydown', onKey);
    }, [onClose]);
    const drag = React.useRef<{ dx: number; dy: number } | null>(null);
    const resize = React.useRef<{ x: number; y: number; w: number; h: number } | null>(null);

    const onPointerDown = (e: React.PointerEvent) => {
        setZ(++Z_TOP);
        const target = e.target as HTMLElement;
        if (target.closest('button, input, select, textarea, a')) {
            // still allow drag when pressing the header background around buttons?
            if (!target.closest(handleSelector) || target.closest('button')) return;
        }
        if (target.closest(handleSelector)) {
            drag.current = { dx: e.clientX - pos.x, dy: e.clientY - pos.y };
            (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
            e.preventDefault();
        }
    };

    const onPointerMove = (e: React.PointerEvent) => {
        if (drag.current) {
            setPos({
                x: Math.max(-size.w + 120, Math.min(window.innerWidth - 120, e.clientX - drag.current.dx)),
                y: Math.max(0, Math.min(window.innerHeight - 60, e.clientY - drag.current.dy)),
            });
        } else if (resize.current) {
            setSize({
                w: Math.max(420, resize.current.w + (e.clientX - resize.current.x)),
                h: Math.max(280, resize.current.h + (e.clientY - resize.current.y)),
            });
        }
    };

    const onPointerUp = () => {
        drag.current = null;
        resize.current = null;
    };

    return (
        <div className="fw-layer">
            <div
                className="fw-window"
                style={{ left: pos.x, top: pos.y, width: size.w, height: size.h, zIndex: z }}
                onPointerDown={onPointerDown}
                onPointerMove={onPointerMove}
                onPointerUp={onPointerUp}
            >
                <div className="fw-content">{children}</div>
                <div
                    className="fw-resize-grip"
                    onPointerDown={(e) => {
                        setZ(++Z_TOP);
                        resize.current = { x: e.clientX, y: e.clientY, w: size.w, h: size.h };
                        (e.currentTarget.parentElement as HTMLElement).setPointerCapture(e.pointerId);
                        e.stopPropagation();
                        e.preventDefault();
                    }}
                >
                    <i className="codicon codicon-chevron-right" style={{ transform: 'rotate(45deg)' }} />
                </div>
                {onClose && (
                    <button className="fw-close" onPointerDown={(e) => e.stopPropagation()} onClick={onClose} title="Close window (Esc)">
                        <i className="codicon codicon-close" />
                    </button>
                )}
            </div>
        </div>
    );
}
