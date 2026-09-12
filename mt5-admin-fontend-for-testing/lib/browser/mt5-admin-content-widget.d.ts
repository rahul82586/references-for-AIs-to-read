import * as React from 'react';
import { ReactWidget } from '@theia/core/lib/browser';
export declare class Mt5AdminContentWidget extends ReactWidget {
    static createId(nodeId: string): string;
    protected nodeId: string;
    protected nodeLabel: string;
    protected filterPath: string;
    setFilterPath(path: string): void;
    initialize(nodeId: string, nodeLabel: string): void;
    protected getIconForNode(id: string): string;
    protected postInit(): void;
    /**
     * Each node ID maps to a DISTINCT React component / view.
     * Sub-nodes must render different content from their parent.
     */
    protected renderPage(nodeId: string): React.ReactNode;
    protected renderPlaceholder(nodeId: string): React.ReactNode;
    protected render(): React.ReactNode;
}
//# sourceMappingURL=mt5-admin-content-widget.d.ts.map