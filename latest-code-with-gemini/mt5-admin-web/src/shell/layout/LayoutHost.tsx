/**
 * LayoutHost — the dockview adapter. The ONLY file that imports dockview.
 * If we ever swap layout engines, only this file (and its CSS) change.
 *
 * Responsibilities:
 *  - render the dockview grid with a single generic 'panel' component
 *  - open/activate panels resolved through the panel registry (singletons)
 *  - deep-link prop updates (e.g. Groups filter path) via updateParameters
 *  - persist/restore the workbench layout (localStorage, debounced) — VS Code
 *    style: reload restores your exact arrangement
 */
import * as React from 'react';
import { DockviewReact } from 'dockview';
import type { DockviewReadyEvent, IDockviewPanelProps, DockviewApi } from 'dockview';
import 'dockview/dist/styles/dockview.css';

import { getPanelDefinition, resolveTreeNode, type ResolvedPanel } from '../registry/panel-registry';

const STORAGE_KEY = 'mt5-admin-layout-v1';

/* ------------------------------------------------------------------ */
/* panel host — renders the registered feature component              */
/* ------------------------------------------------------------------ */

function PanelLoading() {
    return (
        <div className="wb-placeholder">
            <i className="codicon codicon-loading codicon-modifier-spin" />
            <span>Loading…</span>
        </div>
    );
}

function PanelHost(dvProps: IDockviewPanelProps): React.ReactElement {
    const { api } = dvProps;
    const [params, setParams] = React.useState<Record<string, any>>(dvProps.params ?? {});

    React.useEffect(() => {
        const sub = api.onDidParametersChange((next: Record<string, any>) => setParams(next ?? {}));
        return () => sub.dispose();
    }, [api]);

    const def = getPanelDefinition(String(params.defId ?? ''));
    if (!def) {
        return (
            <div className="wb-placeholder">
                <i className="codicon codicon-warning" />
                <span>Unknown panel “{String(params.defId)}” — registry entry missing after restore.</span>
            </div>
        );
    }
    const Comp = def.component as React.ComponentType<any>;
    const featureProps = {
        ...(params.props ?? {}),
        close: () => api.close(),
        setTitle: (t: string) => api.setTitle(t),
    };
    return (
        <React.Suspense fallback={<PanelLoading />}>
            <div style={{ height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                <Comp {...featureProps} />
            </div>
        </React.Suspense>
    );
}

const components = { panel: PanelHost };

/* ------------------------------------------------------------------ */
/* host                                                               */
/* ------------------------------------------------------------------ */

export interface LayoutHostHandle {
    /** Open (or activate + update) the panel for a sidebar tree node. */
    openNode(nodeId: string, label?: string, extraProps?: Record<string, unknown>): void;
    closeAll(): void;
}

export const LayoutHost = React.forwardRef<LayoutHostHandle, object>(function LayoutHost(_props, ref) {
    const apiRef = React.useRef<DockviewApi | null>(null);

    const openResolved = React.useCallback((r: ResolvedPanel) => {
        const api = apiRef.current;
        if (!api) return;

        const existing = api.panels.find((p) => p.id === r.panelId);
        if (existing) {
            // singleton behaviour: activate + push new props (filter deep links)
            existing.api.updateParameters({ defId: r.defId, title: r.title, icon: r.icon, props: r.props });
            existing.api.setTitle(r.title);
            existing.api.setActive();
            return;
        }

        api.addPanel({
            id: r.panelId,
            component: 'panel',
            title: r.title,
            params: { defId: r.defId, title: r.title, icon: r.icon, props: r.props },
        });
    }, []);

    React.useImperativeHandle(
        ref,
        () => ({
            openNode(nodeId: string, label?: string, extraProps?: Record<string, unknown>) {
                const r = resolveTreeNode(nodeId, label);
                if (extraProps) r.props = { ...r.props, ...extraProps };
                openResolved(r);
            },
            closeAll() {
                apiRef.current?.closeAllGroups();
            },
        }),
        [openResolved]
    );

    const onReady = React.useCallback(
        (event: DockviewReadyEvent) => {
            const api = event.api;
            apiRef.current = api;

            // restore persisted layout
            let restored = false;
            try {
                const saved = localStorage.getItem(STORAGE_KEY);
                if (saved) {
                    api.fromJSON(JSON.parse(saved));
                    restored = api.panels.length > 0;
                }
            } catch (e) {
                console.warn('[layout] restore failed, starting fresh:', e);
            }
            if (!restored) {
                openResolved(resolveTreeNode('start-page', 'Start Page'));
            }

            // persist (debounced) on every structural change
            let timer: number | undefined;
            const save = () => {
                window.clearTimeout(timer);
                timer = window.setTimeout(() => {
                    try {
                        localStorage.setItem(STORAGE_KEY, JSON.stringify(api.toJSON()));
                    } catch (e) {
                        console.warn('[layout] persist failed:', e);
                    }
                }, 350);
            };
            api.onDidAddPanel(save);
            api.onDidRemovePanel(save);
            api.onDidMovePanel(save);
            api.onDidActivePanelChange(save);
            api.onDidAddGroup(save);
            api.onDidRemoveGroup(save);
        },
        [openResolved]
    );

    return (
        <div className="wb-dockview-host dockview-theme-dark">
            <DockviewReact components={components} onReady={onReady} />
        </div>
    );
});
