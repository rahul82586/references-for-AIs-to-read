import * as React from 'react';
import { useSymbolDraft } from '../SymbolDraftContext';

export function MarginTab(): React.ReactElement {
    const { draft, setDraft } = useSymbolDraft();

    const updateField = (field: keyof typeof draft, val: any) => {
        setDraft(prev => ({ ...prev, [field]: val }));
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 10, fontSize: 11 }}>
            {/* Top header info banner side-by-side */}
            <div style={{ display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', borderRadius: 4 }}>
                <div style={{ width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#9b59b6', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' }}>
                    M
                </div>
                <div style={{ flex: 1, opacity: 0.9, lineHeight: 1.3 }}>
                    Configure margin calculations, absolute multiplier overrides, and automated transaction validation limits.
                </div>
            </div>

            {/* Grid fields */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 24px', flex: 1, marginTop: 8 }}>
                
                {/* Left Column (Rates overrides) */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    <div style={{ fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 }}>
                        Multiplier Overrides
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 120, textAlign: 'right', opacity: 0.8 }}>Initial Margin rate:</span>
                        <input 
                            className="adm-input" 
                            type="number" 
                            step="0.01" 
                            style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                            value={draft.margin_initial} 
                            onChange={e => updateField('margin_initial', parseFloat(e.target.value) || 0.0)} 
                        />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 120, textAlign: 'right', opacity: 0.8 }}>Maintenance rate:</span>
                        <input 
                            className="adm-input" 
                            type="number" 
                            step="0.01" 
                            style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                            value={draft.margin_maintenance} 
                            onChange={e => updateField('margin_maintenance', parseFloat(e.target.value) || 0.0)} 
                        />
                    </div>

                    <div style={{ fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginTop: 4, marginBottom: 2 }}>
                        Hedging Margin Calculation
                    </div>

                    <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, cursor: 'pointer', height: 20 }}>
                        <input 
                            type="checkbox" 
                            checked={draft.calc_hedged_larger_leg} 
                            onChange={e => updateField('calc_hedged_larger_leg', e.target.checked)} 
                        />
                        Calculate using larger leg size
                    </label>
                </div>

                {/* Right Column (Verification Triggers) */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    <div style={{ fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 }}>
                        Verification Checks
                    </div>

                    <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, cursor: 'pointer', height: 20 }}>
                        <input 
                            type="checkbox" 
                            checked={draft.check_before_execution} 
                            onChange={e => updateField('check_before_execution', e.target.checked)} 
                        />
                        Check before execution
                    </label>

                    <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, cursor: 'pointer', height: 20 }}>
                        <input 
                            type="checkbox" 
                            checked={draft.check_on_sltp} 
                            onChange={e => updateField('check_on_sltp', e.target.checked)} 
                        />
                        Check on SL / TP order triggers
                    </label>

                    <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, cursor: 'pointer', height: 20 }}>
                        <input 
                            type="checkbox" 
                            checked={draft.exclude_long_pnl} 
                            onChange={e => updateField('exclude_long_pnl', e.target.checked)} 
                        />
                        Exclude long PnL from free margin
                    </label>

                    <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, cursor: 'pointer', height: 20 }}>
                        <input 
                            type="checkbox" 
                            checked={draft.recalc_margin_eod} 
                            onChange={e => updateField('recalc_margin_eod', e.target.checked)} 
                        />
                        Recalculate rate EOD
                    </label>
                </div>
            </div>
        </div>
    );
}
