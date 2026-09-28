import * as React from 'react';
import { ActivityBar } from './ActivityBar';
import { SideBar } from './SideBar';
import { StatusBar } from './StatusBar';
import { LayoutHost, LayoutHostHandle } from '../layout/LayoutHost';
import { CommandPalette } from '../command-palette/CommandPalette';

/**
 * The workbench — VS Code's layout grammar applied to MT5 administration:
 * title bar · activity bar · sidebar (admin tree) · editor area (dockview) ·
 * status bar · command palette.
 *
 * The workbench contains ZERO business logic: opening a section delegates to
 * the panel registry via LayoutHost.openNode.
 */
export function Workbench(): React.ReactElement {
    const layoutRef = React.useRef<LayoutHostHandle>(null);
    const [sidebarVisible, setSidebarVisible] = React.useState(true);
    const [paletteOpen, setPaletteOpen] = React.useState(false);

    const openNode = React.useCallback((nodeId: string, label: string, extraProps?: Record<string, unknown>) => {
        layoutRef.current?.openNode(nodeId, label, extraProps);
    }, []);

    const openSettings = React.useCallback(() => {
        layoutRef.current?.openNode('settings', 'Settings');
    }, []);

    React.useEffect(() => {
        const onKey = (e: KeyboardEvent) => {
            const mod = e.ctrlKey || e.metaKey;
            if (mod && e.shiftKey && e.key.toLowerCase() === 'p') {
                e.preventDefault();
                setPaletteOpen((v) => !v);
            } else if (mod && e.key.toLowerCase() === 'b') {
                e.preventDefault();
                setSidebarVisible((v) => !v);
            }
        };
        // panels (e.g. Welcome quick links) request navigation through this event
        const onOpenEvent = (e: Event) => {
            const { id, label, props } = (e as CustomEvent).detail ?? {};
            if (typeof id === 'string') openNode(id, label ?? id, props);
        };
        window.addEventListener('keydown', onKey);
        window.addEventListener('mt5-admin:open-node', onOpenEvent);
        return () => {
            window.removeEventListener('keydown', onKey);
            window.removeEventListener('mt5-admin:open-node', onOpenEvent);
        };
    }, [openNode]);

    return (
        <div className="wb-root">
            <div className="wb-titlebar">
                <span className="wb-titlebar-logo">
                    <i className="codicon codicon-symbol-namespace" />
                    MT5 Administrator
                </span>
                <div className="wb-titlebar-center" />
                <button className="wb-titlebar-search" onClick={() => setPaletteOpen(true)}>
                    <i className="codicon codicon-search" />
                    Go to section <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd>
                </button>
                <div className="wb-titlebar-center">
                    <button
                        onClick={() => openNode('trade-panel', 'Trade Terminal')}
                        title="Open a new Trade Terminal (Multi-instance: can open multiple tabs side-by-side)"
                        style={{
                            background: 'linear-gradient(135deg, #0e639c, #1177bb)',
                            color: '#fff',
                            border: '1px solid #1177bb',
                            borderRadius: '4px',
                            padding: '3px 10px',
                            fontSize: '11px',
                            fontWeight: 600,
                            cursor: 'pointer',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '6px',
                        }}
                    >
                        <i className="codicon codicon-pulse" />
                        + Trade Terminal
                    </button>
                </div>
            </div>

            <div className="wb-body">
                <ActivityBar
                    sidebarVisible={sidebarVisible}
                    onToggleSidebar={() => setSidebarVisible((v) => !v)}
                    onOpenSettings={openSettings}
                />
                <SideBar visible={sidebarVisible} onOpenNode={openNode} />
                <div className="wb-editor-area">
                    <LayoutHost ref={layoutRef} />
                </div>
            </div>

            <StatusBar onOpenSettings={openSettings} />

            {paletteOpen && (
                <CommandPalette onClose={() => setPaletteOpen(false)} onOpenNode={openNode} />
            )}
        </div>
    );
}
