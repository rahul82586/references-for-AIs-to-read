import * as React from 'react';

interface BulkEditBannerProps {
    count: number;
}

export function BulkEditBanner({ count }: BulkEditBannerProps): React.ReactElement {
    return (
        <div className="adm-hint" style={{ background: 'var(--theia-sideBarSectionHeader-background)', color: 'var(--theia-foreground)', margin: '0 0 16px 0', borderLeft: '3px solid #3498db', padding: '8px 12px' }}>
            <div style={{ fontWeight: '600', marginBottom: 4, display: 'flex', alignItems: 'center', gap: 6 }}>
                <i className="codicon codicon-info" style={{ color: '#3498db' }} />
                <span>Bulk Editing {count} Symbols</span>
            </div>
            <div style={{ fontSize: 11, lineHeight: '1.4', opacity: 0.9 }}>
                Only the fields you modify will be saved and applied as a batch update. 
                <br />
                <strong style={{ color: '#e67e22' }}>Pro-Tip:</strong> Entering a suffix starting with a period (e.g. <code>.x</code>) in the Symbol name input will create duplicated copies of all selected symbols with that suffix appended, rather than renaming them!
            </div>
        </div>
    );
}
