import * as React from 'react';
import { useGroupDraft } from '../GroupDraftContext';

const SIGNALS_OPTIONS = [
    { value: 'disabled', label: 'Disabled' },
    { value: 'all', label: 'Enable all signals' },
    { value: 'own_only', label: 'From my servers only' }
];

const TRANSFER_OPTIONS = [
    { value: 'disabled', label: 'Disabled' },
    { value: 'same_details', label: 'Same name + email only' },
    { value: 'subgroup', label: 'Within same subgroup' },
    { value: 'subgroup_name', label: 'Same name in group' }
];

export function PermissionsTab(): React.ReactElement {
    const { draft, setDraft } = useGroupDraft();

    const updateField = (field: keyof typeof draft, val: any) => {
        setDraft(prev => ({ ...prev, [field]: val }));
    };

    const isDemo = draft.name.toLowerCase().includes('demo');
    const isNetting = draft.risk_management_model === 'netting';

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 10, fontSize: 11 }}>
            {/* Top header info banner side-by-side */}
            <div style={{ display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', borderRadius: 4 }}>
                <div style={{ width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#e74c3c', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' }}>
                    P
                </div>
                <div style={{ flex: 1, opacity: 0.9, lineHeight: 1.3 }}>
                    Configure client permissions, algorithmic trading policies (EAs), maximum active order/position limits, and internal wallet funds transfers.
                </div>
            </div>

            {/* Grid fields */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 24px', flex: 1, marginTop: 4 }}>
                
                {/* Left Column (Limits & Demo specs) */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    <div style={{ fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 }}>
                        Trading Limits & Finances
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>Max Symbols:</span>
                        <input className="adm-input" type="number" style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }} placeholder="0 = unlimited" value={draft.max_symbols} onChange={e => updateField('max_symbols', parseInt(e.target.value) || 0)} />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>Max Positions:</span>
                        <input className="adm-input" type="number" style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }} placeholder="0 = unlimited" value={draft.max_positions} onChange={e => updateField('max_positions', parseInt(e.target.value) || 0)} />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>Max Orders:</span>
                        <input className="adm-input" type="number" style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }} placeholder="0 = unlimited" value={draft.max_orders} onChange={e => updateField('max_orders', parseInt(e.target.value) || 0)} />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>History Scope:</span>
                        <select className="adm-select" style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }} value={draft.available_history} onChange={e => updateField('available_history', e.target.value)}>
                            <option value="All">All history logs</option>
                            <option value="1 month">1 Month</option>
                            <option value="3 months">3 Months</option>
                            <option value="6 months">6 Months</option>
                            <option value="1 year">1 Year</option>
                        </select>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>Interest Rate (%):</span>
                        <input className="adm-input" type="number" step="0.01" style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }} placeholder="e.g. 2.50" value={draft.interest_rate} onChange={e => updateField('interest_rate', parseFloat(e.target.value) || 0)} />
                    </div>

                    {isDemo && (
                        <>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>Default Deposit:</span>
                                <input className="adm-input" type="number" style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }} value={draft.default_deposit} onChange={e => updateField('default_deposit', parseInt(e.target.value) || 10000)} />
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>Default Leverage:</span>
                                <input className="adm-input" type="number" style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }} placeholder="1:100" value={draft.default_leverage} onChange={e => updateField('default_leverage', parseInt(e.target.value) || 100)} />
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>Expiry days:</span>
                                <input className="adm-input" type="number" style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }} placeholder="Inactivity limit" value={draft.inactivity_days} onChange={e => updateField('inactivity_days', parseInt(e.target.value) || 0)} />
                            </div>
                        </>
                    )}
                </div>

                {/* Right Column (Permissions & EAs) */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    <div style={{ fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 }}>
                        Signals & Algorithm Policies
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 90, textAlign: 'right', opacity: 0.8 }}>Signals:</span>
                        <select className="adm-select" style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }} value={draft.trade_signals_mode} onChange={e => updateField('trade_signals_mode', e.target.value)}>
                            {SIGNALS_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                        </select>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 90, textAlign: 'right', opacity: 0.8 }}>Transfers:</span>
                        <select className="adm-select" style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }} value={draft.transfer_funds_mode} onChange={e => updateField('transfer_funds_mode', e.target.value)}>
                            {TRANSFER_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                        </select>
                    </div>

                    <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', height: 18, marginTop: 4 }}>
                        <input type="checkbox" checked={draft.enable_swaps} onChange={e => updateField('enable_swaps', e.target.checked)} />
                        Enable swaps calculations and charging
                    </label>

                    <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', height: 18 }}>
                        <input type="checkbox" checked={draft.enable_trailing_stops} onChange={e => updateField('enable_trailing_stops', e.target.checked)} />
                        Allow client terminal trailing stops
                    </label>

                    <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', height: 18 }}>
                        <input type="checkbox" checked={draft.enable_ea_trading} onChange={e => updateField('enable_ea_trading', e.target.checked)} />
                        Allow Expert Advisor algorithmic trading
                    </label>

                    <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', height: 18, opacity: isNetting ? 1 : 0.5 }}>
                        <input type="checkbox" disabled={!isNetting} checked={isNetting && draft.fifo_rule} onChange={e => updateField('fifo_rule', e.target.checked)} />
                        Close positions strictly by FIFO rules
                    </label>

                    <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', height: 18, opacity: !isNetting ? 1 : 0.5 }}>
                        <input type="checkbox" disabled={isNetting} checked={!isNetting && draft.prohibit_hedge} onChange={e => updateField('prohibit_hedge', e.target.checked)} />
                        Prohibit hedge positions (hedging only)
                    </label>

                    <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', height: 18 }}>
                        <input type="checkbox" checked={draft.deal_cost_calc} onChange={e => updateField('deal_cost_calc', e.target.checked)} />
                        Enable real-time deal cost calculation
                    </label>
                </div>

            </div>
        </div>
    );
}
