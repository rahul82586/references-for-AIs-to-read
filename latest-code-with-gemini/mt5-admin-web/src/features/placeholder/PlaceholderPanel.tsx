import * as React from 'react';

interface Props {
    sectionLabel?: string;
    close?(): void;
}

/** Rendered for tree sections that have no feature yet (ported behaviour). */
export function PlaceholderPanel({ sectionLabel }: Props): React.ReactElement {
    return (
        <div className="wb-placeholder">
            <i className="codicon codicon-tools" />
            <div>
                <strong>{sectionLabel ?? 'Section'}</strong> — this section is being implemented.
            </div>
            <span className="wb-gap-badge">
                <i className="codicon codicon-info" />
                Ports over in F1 (bulk page migration) — see ARCHITECTURE.md
            </span>
        </div>
    );
}
