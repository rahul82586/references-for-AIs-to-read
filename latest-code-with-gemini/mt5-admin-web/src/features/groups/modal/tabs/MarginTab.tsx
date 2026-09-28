import * as React from 'react';
import { useGroupDraft } from '../GroupDraftContext';

const MODELS = [
    { value: 'netting', label: 'Retail Forex/CFD/Futures (netting)' },
    { value: 'hedging', label: 'Retail Forex/CFD/Futures with hedging' },
    { value: 'discount', label: 'Stock Exchange (margin discount rates)' }
];

const LEVERAGES = ['Default', 'Forex-Standard', 'CFD-HighRisk', 'MiniAccounts'];

export function MarginTab(): React.ReactElement {
    const { draft, setDraft } = useGroupDraft();

    const updateField = (field: keyof typeof draft, val: any) => {
        setDraft(prev => ({ ...prev, [field]: val }));
    };

    const isHedging = draft.risk_management_model === 'hedging';

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 10, fontSize: 11 }}>
            {/* Top header info banner side-by-side */}
            <div style={{ display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', borderRadius: 4 }}>
                <div style={{ width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#e67e22', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' }}>
                    M
                </div>
                <div style={{ flex: 1, opacity: 0.9, lineHeight: 1.3 }}>
                    Configure group risk management calculations, margin stop out levels, stop out balance compensation, and floating leverage rules.
                </div>
            </div>

            {/* Grid fields */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 24px', flex: 1, marginTop: 4 }}>
                
                {/* Left Column (Risk Model & Levels) */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    <div style={{ fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 }}>
                        Model & Margin Levels
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>Risk Model:</span>
                        <select className="adm-select" style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }} value={draft.risk_management_model} onChange={e => updateField('risk_management_model', e.target.value)}>
                            {MODELS.map(m => <option key={m.value} value={m.value}>{m.label}</option>)}
                        </select>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>Calculation Base:</span>
                        <select className="adm-select" style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }} value={draft.stop_out_mode} onChange={e => updateField('stop_out_mode', e.target.value)}>
                            <option value="percent">In percent of margin level</option>
                            <option value="money">In absolute money value</option>
                        </select>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>Margin Call:</span>
                        <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 4 }}>
                            <input className="adm-input" type="number" style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }} value={draft.margin_call} onChange={e => updateField('margin_call', parseFloat(e.target.value) || 0)} />
                            <span>{draft.stop_out_mode === 'percent' ? '%' : 'USD'}</span>
                        </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>Stop Out Level:</span>
                        <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 4 }}>
                            <input className="adm-input" type="number" style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }} value={draft.margin_stop_out} onChange={e => updateField('margin_stop_out', parseFloat(e.target.value) || 0)} />
                            <span>{draft.stop_out_mode === 'percent' ? '%' : 'USD'}</span>
                        </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>Leverage Profile:</span>
                        <select className="adm-select" style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }} value={draft.floating_leverage_profile} onChange={e => updateField('floating_leverage_profile', e.target.value)}>
                            {LEVERAGES.map(l => <option key={l} value={l}>{l}</option>)}
                        </select>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>Virtual Credit:</span>
                        <input className="adm-input" type="number" style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }} placeholder="0.00" value={draft.virtual_credit} onChange={e => updateField('virtual_credit', parseFloat(e.target.value) || 0)} />
                    </div>
                </div>

                {/* Right Column (Policies & Profit modes) */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    <div style={{ fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 }}>
                        Stop Out Policy & Free Margin
                    </div>

                    <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', height: 18, opacity: isHedging ? 1 : 0.5 }}>
                        <input type="checkbox" disabled={!isHedging} checked={isHedging && draft.stop_out_hedged} onChange={e => updateField('stop_out_hedged', e.target.checked)} />
                        Stop out fully hedged accounts
                    </label>

                    <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', height: 18 }}>
                        <input type="checkbox" checked={draft.compensate_negative_balance} onChange={e => updateField('compensate_negative_balance', e.target.checked)} />
                        Compensate negative balance automatically
                    </label>

                    <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', height: 18, opacity: draft.compensate_negative_balance ? 1 : 0.5 }}>
                        <input type="checkbox" disabled={!draft.compensate_negative_balance} checked={draft.compensate_negative_balance && draft.withdraw_credit_after_comp} onChange={e => updateField('withdraw_credit_after_comp', e.target.checked)} />
                        Withdraw virtual credit after compensation
                    </label>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 4 }}>
                        <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>Unrealized Profit:</span>
                        <select className="adm-select" style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }} value={draft.unrealized_profit_mode} onChange={e => updateField('unrealized_profit_mode', parseInt(e.target.value))}>
                            <option value={0}>Do not use unrealized profit/loss</option>
                            <option value={1}>Use both profit and loss</option>
                            <option value={2}>Use unrealized loss only</option>
                            <option value={3}>Use unrealized profit only</option>
                        </select>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>Daily Profit:</span>
                        <select className="adm-select" style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }} value={draft.daily_fixed_profit_mode} onChange={e => updateField('daily_fixed_profit_mode', parseInt(e.target.value))}>
                            <option value={0}>Do not use daily fixed profit/loss</option>
                            <option value={1}>Use daily fixed profit/loss</option>
                        </select>
                    </div>

                    <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', height: 18, opacity: draft.daily_fixed_profit_mode === 1 ? 1 : 0.5, paddingLeft: 10 }}>
                        <input type="checkbox" disabled={draft.daily_fixed_profit_mode !== 1} checked={draft.daily_fixed_profit_mode === 1 && draft.release_fixed_profit} onChange={e => updateField('release_fixed_profit', e.target.checked)} />
                        Release fixed profit daily (netting)
                    </label>
                </div>

            </div>
        </div>
    );
}
