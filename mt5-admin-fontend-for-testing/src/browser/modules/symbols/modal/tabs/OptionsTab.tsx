import * as React from 'react';
import { useSymbolDraft } from '../SymbolDraftContext';

export function OptionsTab(): React.ReactElement {
    const { draft, setDraft } = useSymbolDraft();

    const updateField = (field: keyof typeof draft, val: any) => {
        setDraft(prev => ({ ...prev, [field]: val }));
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 10, fontSize: 11 }}>
            {/* Top header info banner side-by-side */}
            <div style={{ display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', borderRadius: 4 }}>
                <div style={{ width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#e67e22', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' }}>
                    O
                </div>
                <div style={{ flex: 1, opacity: 0.9, lineHeight: 1.3 }}>
                    Configure options derivative settings. Options can be Call or Put, and structured as American or European exercise styles.
                </div>
            </div>

            {/* Grid fields */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 24px', flex: 1, marginTop: 8 }}>
                {/* Left Column */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    <div style={{ fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 }}>
                        Option Classification
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 90, textAlign: 'right', opacity: 0.8 }}>Option Type:</span>
                        <div style={{ flex: 1, display: 'flex', gap: 12 }}>
                            <label style={{ display: 'flex', alignItems: 'center', gap: 4, cursor: 'pointer' }}>
                                <input type="radio" name="opt-type" checked={draft.option_type === 'call'} onChange={() => updateField('option_type', 'call')} />
                                Call
                            </label>
                            <label style={{ display: 'flex', alignItems: 'center', gap: 4, cursor: 'pointer' }}>
                                <input type="radio" name="opt-type" checked={draft.option_type === 'put'} onChange={() => updateField('option_type', 'put')} />
                                Put
                            </label>
                        </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 90, textAlign: 'right', opacity: 0.8 }}>Option Style:</span>
                        <div style={{ flex: 1, display: 'flex', gap: 12 }}>
                            <label style={{ display: 'flex', alignItems: 'center', gap: 4, cursor: 'pointer' }}>
                                <input type="radio" name="opt-style" checked={draft.option_style === 'american'} onChange={() => updateField('option_style', 'american')} />
                                American
                            </label>
                            <label style={{ display: 'flex', alignItems: 'center', gap: 4, cursor: 'pointer' }}>
                                <input type="radio" name="opt-style" checked={draft.option_style === 'european'} onChange={() => updateField('option_style', 'european')} />
                                European
                            </label>
                        </div>
                    </div>
                </div>

                {/* Right Column */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    <div style={{ fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 }}>
                        Pricing Limits
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 90, textAlign: 'right', opacity: 0.8 }}>Strike Price:</span>
                        <input 
                            className="adm-input" 
                            type="number" 
                            step="0.0001" 
                            style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                            placeholder="Strike boundary price" 
                            value={draft.strike_price} 
                            onChange={e => updateField('strike_price', parseFloat(e.target.value) || 0.0)} 
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}
