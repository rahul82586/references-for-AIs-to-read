import * as React from 'react';
import { MT5_MANAGER_TREE, findManagerNode } from '../../shell/tree/mt5-manager-tree';

interface Props {
    nodeId: string;
    sectionLabel?: string;
    api?: string;
    close?(): void;
}

/**
 * Manager section drop-in point: nodes without a dedicated panel yet render
 * their Manager API family so the next milestone can replace this component
 * per node without touching shell, registry or tree.
 */
export function ManagerSectionPanel({ nodeId, sectionLabel, api }: Props): React.ReactElement {
    const node = findManagerNode(MT5_MANAGER_TREE, nodeId);
    return (
        <div className="wb-placeholder">
            <i className={`codicon codicon-${node?.icon ?? 'shield'}`} />
            <div>
                <strong>{sectionLabel ?? node?.label ?? nodeId}</strong> — Manager section
            </div>
            {(api || node?.api) && (
                <div className="ca-gap-badge" style={{ maxWidth: 620 }}>
                    <i className="codicon codicon-info" />
                    <span>Manager API family: <code className="adm-code">{api ?? node?.api}</code></span>
                </div>
            )}
            <div className="wb-settings-hint" style={{ maxWidth: 520, textAlign: 'center' }}>
                Panel lands in the Manager modules milestone — navigation, registry and
                transport hooks are already in place.
            </div>
        </div>
    );
}
