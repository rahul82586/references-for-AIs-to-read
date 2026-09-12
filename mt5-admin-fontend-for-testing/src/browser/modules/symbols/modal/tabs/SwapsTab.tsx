import * as React from 'react';
import { useSymbolDraft } from '../SymbolDraftContext';

const SWAP_TYPES = [
    { value: 'points', label: 'In points of spread' },
    { value: 'money', label: 'In absolute money values' },
    { value: 'percent', label: 'In percentage terms of position value' },
    { value: 'reopen_close', label: 'Reopen by Close Price' },
    { value: 'reopen_bid', label: 'Reopen by Bid Price' }
];

const DAYS_IN_YEAR = [360, 365, 366];

export function SwapsTab(): React.ReactElement {
    const { draft, setDraft } = useSymbolDraft();

    const updateField = (field: keyof typeof draft, val: any) => {
        setDraft(prev => ({ ...prev, [field]: val }));
    };

    const handleMultiplierChange = (day: string, value: number) => {
        const nextMult = { ...draft.swap_multipliers, [day]: value };
        updateField('swap_multipliers', nextMult);
    };

    const applyForexPreset = () => {
        setDraft(prev => ({
            ...prev,
            swap_multipliers: {
                'Mon': 1, 'Tue': 1, 'Wed': 3, 'Thu': 1, 'Fri': 1, 'Sat': 0, 'Sun': 0
            }
        }));
    };

    const applyAllWeekPreset = () => {
        setDraft(prev => ({
            ...prev,
            swap_multipliers: {
                'Mon': 1, 'Tue': 1, 'Wed': 1, 'Thu': 1, 'Fri': 1, 'Sat': 1, 'Sun': 1
            }
        }));
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 10, fontSize: 11 }}>
            {/* Top header info banner side-by-side */}
            <div style={{ display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', borderRadius: 4 }}>
                <div style={{ width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#e67e22', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' }}>
                    S
                </div>
                <div style={{ flex: 1, opacity: 0.9, lineHeight: 1.3 }}>
                    Configure automatic rollover swap interest charges, day multipliers, and holiday accrual rules.
                </div>
            </div>

            {/* Grid fields */}
            <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 0.9fr', gap: '8px 24px', flex: 1, marginTop: 4 }}>
                
                {/* Left Column (Rates overrides) */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, cursor: 'pointer', height: 20 }}>
                        <input 
                            type="checkbox" 
                            checked={draft.enable_swaps} 
                            onChange={e => updateField('enable_swaps', e.target.checked)} 
                        />
                        <strong>Enable rollover swaps calculation</strong>
                    </label>

                    <fieldset disabled={!draft.enable_swaps} style={{ border: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: 6 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>Swap Type:</span>
                            <select className="adm-select" style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }} value={draft.swap_type} onChange={e => updateField('swap_type', e.target.value)}>
                                {SWAP_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                            </select>
                        </div>

                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>Long rate:</span>
                            <input className="adm-input" type="number" step="0.01" style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }} value={draft.swap_long} onChange={e => updateField('swap_long', parseFloat(e.target.value) || 0.0)} />
                        </div>

                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>Short rate:</span>
                            <input className="adm-input" type="number" step="0.01" style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }} value={draft.swap_short} onChange={e => updateField('swap_short', parseFloat(e.target.value) || 0.0)} />
                        </div>

                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>Yearly base:</span>
                            <select className="adm-select" style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }} value={draft.swap_days_in_year} onChange={e => updateField('swap_days_in_year', parseInt(e.target.value) || 360)}>
                                {DAYS_IN_YEAR.map(d => <option key={d} value={d}>{d} Days</option>)}
                            </select>
                        </div>

                        {draft.swap_type === 'money' && (
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>Currency Basis:</span>
                                <select className="adm-select" style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }} value={draft.currency} onChange={e => updateField('currency', e.target.value)}>
                                    <option value="base">Base currency</option>
                                    <option value="margin">Margin currency</option>
                                    <option value="profit">Profit currency</option>
                                </select>
                            </div>
                        )}
                    </fieldset>
                </div>

                {/* Right Column (Multiplier grid) */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6, opacity: draft.enable_swaps ? 1 : 0.6 }}>
                    <div style={{ fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 }}>
                        Accrual Multipliers
                    </div>

                    <div style={{ display: 'flex', gap: 4, marginBottom: 6 }}>
                        <button type="button" className="adm-btn" style={{ flex: 1, fontSize: 10, padding: '2px 4px' }} disabled={!draft.enable_swaps} onClick={applyForexPreset}>Wed x3</button>
                        <button type="button" className="adm-btn" style={{ flex: 1, fontSize: 10, padding: '2px 4px' }} disabled={!draft.enable_swaps} onClick={applyAllWeekPreset}>All x1</button>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                        {Object.keys(draft.swap_multipliers).map(day => (
                            <div key={day} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                <span style={{ width: 40, opacity: 0.8, textTransform: 'capitalize' }}>{day}:</span>
                                <input 
                                    disabled={!draft.enable_swaps}
                                    className="adm-input" 
                                    type="number"
                                    style={{ flex: 1, height: 18, padding: '2px 4px', fontSize: 11, textAlign: 'center' }}
                                    value={draft.swap_multipliers[day]} 
                                    onChange={e => handleMultiplierChange(day, parseInt(e.target.value) || 0)} 
                                />
                            </div>
                        ))}
                    </div>
                </div>

            </div>
        </div>
    );
}
