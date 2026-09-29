import * as React from 'react';
import { useSymbolDraft } from '../SymbolDraftContext';

export function BondsTab(): React.ReactElement {
    const { draft, setDraft } = useSymbolDraft();

    const updateField = (field: keyof typeof draft, val: any) => {
        setDraft(prev => ({ ...prev, [field]: val }));
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 10, fontSize: 11 }}>
            {/* Top header info banner side-by-side */}
            <div style={{ display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', borderRadius: 4 }}>
                <div style={{ width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#3498db', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' }}>
                    B
                </div>
                <div style={{ flex: 1, opacity: 0.9, lineHeight: 1.3 }}>
                    Configure bond debt instrument specifications, face par values, and accrued interest parameters.
                </div>
            </div>

            {/* Grid fields */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 24px', flex: 1, marginTop: 8 }}>
                {/* Left Column */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    <div style={{ fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 }}>
                        Par Value
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 90, textAlign: 'right', opacity: 0.8 }}>Face Value:</span>
                        <input 
                            className="adm-input" 
                            type="number" 
                            step="0.01" 
                            style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                            placeholder="Bond face par value" 
                            value={draft.bond_face_value} 
                            onChange={e => updateField('bond_face_value', parseFloat(e.target.value) || 0.0)} 
                        />
                    </div>
                </div>

                {/* Right Column */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    <div style={{ fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 }}>
                        Interest Accumulation
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 110, textAlign: 'right', opacity: 0.8 }}>Accrued Interest:</span>
                        <input 
                            className="adm-input" 
                            type="number" 
                            step="0.0001" 
                            style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                            placeholder="Accumulated interest index" 
                            value={draft.bond_accrued_interest} 
                            onChange={e => updateField('bond_accrued_interest', parseFloat(e.target.value) || 0.0)} 
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}
