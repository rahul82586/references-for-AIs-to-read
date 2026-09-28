import * as React from 'react';

interface ImportSummaryProps {
    count: number;
    overwrite: boolean;
}

export function ImportSummary({ count, overwrite }: ImportSummaryProps): React.ReactElement {
    return (
        <div className="adm-modal-body" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div className="adm-hint" style={{ background: 'rgba(46, 204, 113, 0.1)', border: '1px solid #2ecc71', color: '#2ecc71', margin: '0 0 12px 0' }}>
                <i className="codicon codicon-check" /> Symbols ingestion completed successfully!
            </div>

            <div style={{ fontSize: 13, lineHeight: '1.6' }}>
                <p>Import summary metrics:</p>
                <ul>
                    <li>Instruments Ingested: <strong>{count}</strong></li>
                    <li>Collision Overwrite policy: <strong>{overwrite ? 'Enabled (Overwritten)' : 'Disabled (Skipped)'}</strong></li>
                </ul>
            </div>

            <div className="adm-hint" style={{ background: 'var(--theia-inputValidation-warningBackground)', color: 'var(--theia-warningForeground)', margin: '12px 0 0 0' }}>
                <i className="codicon codicon-warning" />
                <strong>Important:</strong> All newly imported symbols have been set to <strong>Trading Disabled</strong> by default to prevent client terminals from executing orders until spread rates and execution gates are configured manually.
            </div>
        </div>
    );
}
