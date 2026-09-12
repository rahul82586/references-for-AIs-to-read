import * as React from 'react';
import { useSymbolDraft } from '../SymbolDraftContext';

export function FuturesTab(): React.ReactElement {
    const { draft, setDraft } = useSymbolDraft();

    const updateField = (field: keyof typeof draft, val: any) => {
        setDraft(prev => ({ ...prev, [field]: val }));
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 10, fontSize: 11 }}>
            <div style={{ display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', borderRadius: 4 }}>
                <div style={{ width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#1abc9c', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' }}>
                    F
                </div>
                <div style={{ flex: 1, opacity: 0.9, lineHeight: 1.3 }}>
                    Configure exchange futures contract specifications, settlement price, and expiry rollover splice settings.
                    These parameters are normally fed automatically by the gateway.
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 24px', flex: 1, marginTop: 8 }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    <div style={{ fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 }}>
                        Contract Bounds
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 120, textAlign: 'right', opacity: 0.8 }}>Settlement price:</span>
                        <input className="adm-input" type="number" step="0.0001" style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }} value={draft.strike_price} onChange={e => updateField('strike_price', parseFloat(e.target.value) || 0.0)} />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 120, textAlign: 'right', opacity: 0.8 }}>Min price bound:</span>
                        <input className="adm-input" type="number" style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }} value={draft.bond_face_value} onChange={e => updateField('bond_face_value', parseFloat(e.target.value) || 0.0)} />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 120, textAlign: 'right', opacity: 0.8 }}>Max price bound:</span>
                        <input className="adm-input" type="number" style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }} value={draft.bond_accrued_interest} onChange={e => updateField('bond_accrued_interest', parseFloat(e.target.value) || 0.0)} />
                    </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    <div style={{ fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 }}>
                        Splice Rollover
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 90, textAlign: 'right', opacity: 0.8 }}>Splice type:</span>
                        <select className="adm-select" style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }} value={draft.splice_type} onChange={e => updateField('splice_type', e.target.value)}>
                            <option value="none">None</option>
                            <option value="unadjusted">Unadjusted</option>
                            <option value="adjusted">Adjusted</option>
                        </select>
                    </div>

                    {draft.splice_type !== 'none' && (
                        <>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                <span style={{ width: 90, textAlign: 'right', opacity: 0.8 }}>Expiry date:</span>
                                <input className="adm-input" type="date" style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }} value={draft.splice_date_extension} onChange={e => updateField('splice_date_extension', e.target.value)} />
                            </div>

                            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                <span style={{ width: 90, textAlign: 'right', opacity: 0.8 }}>Shift days:</span>
                                <input className="adm-input" type="number" style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }} value={draft.splice_shift_days} onChange={e => updateField('splice_shift_days', parseInt(e.target.value) || 0)} />
                            </div>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}
