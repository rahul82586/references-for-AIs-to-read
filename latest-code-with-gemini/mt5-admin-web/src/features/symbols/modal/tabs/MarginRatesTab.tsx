import * as React from 'react';
import { useSymbolDraft } from '../SymbolDraftContext';

export function MarginRatesTab(): React.ReactElement {
    const { draft, setDraft } = useSymbolDraft();

    const updateField = (field: keyof typeof draft, val: any) => {
        setDraft(prev => ({ ...prev, [field]: val }));
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 10, fontSize: 11 }}>
            {/* Top header info banner side-by-side */}
            <div style={{ display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', borderRadius: 4 }}>
                <div style={{ width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#9b59b6', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' }}>
                    %
                </div>
                <div style={{ flex: 1, opacity: 0.9, lineHeight: 1.3 }}>
                    Specify margin requirements multiplier rates per transaction order type and stock collateral valuations.
                </div>
            </div>

            {/* Grid fields */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 24px', flex: 1, marginTop: 4 }}>
                
                {/* Left Column (Market & Limits) */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    <div style={{ display: 'flex', gap: 8, fontWeight: 'bold', fontSize: 10, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 }}>
                        <span style={{ width: 90 }}>Order Type</span>
                        <span style={{ flex: 1, textAlign: 'center' }}>Initial</span>
                        <span style={{ flex: 1, textAlign: 'center' }}>Maint</span>
                    </div>

                    <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                        <span style={{ width: 90, opacity: 0.8 }}>Market Buy:</span>
                        <input className="adm-input" type="number" step="0.1" style={{ flex: 1, height: 20, padding: '2px 4px', fontSize: 11 }} value={draft.rate_market_buy_init} onChange={e => updateField('rate_market_buy_init', parseFloat(e.target.value) || 1.0)} />
                        <input className="adm-input" type="number" step="0.1" style={{ flex: 1, height: 20, padding: '2px 4px', fontSize: 11 }} value={draft.rate_market_buy_maint} onChange={e => updateField('rate_market_buy_maint', parseFloat(e.target.value) || 1.0)} />
                    </div>

                    <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                        <span style={{ width: 90, opacity: 0.8 }}>Market Sell:</span>
                        <input className="adm-input" type="number" step="0.1" style={{ flex: 1, height: 20, padding: '2px 4px', fontSize: 11 }} value={draft.rate_market_sell_init} onChange={e => updateField('rate_market_sell_init', parseFloat(e.target.value) || 1.0)} />
                        <input className="adm-input" type="number" step="0.1" style={{ flex: 1, height: 20, padding: '2px 4px', fontSize: 11 }} value={draft.rate_market_sell_maint} onChange={e => updateField('rate_market_sell_maint', parseFloat(e.target.value) || 1.0)} />
                    </div>

                    <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                        <span style={{ width: 90, opacity: 0.8 }}>Buy Limit:</span>
                        <input className="adm-input" type="number" step="0.1" style={{ flex: 1, height: 20, padding: '2px 4px', fontSize: 11 }} value={draft.rate_limit_buy_init} onChange={e => updateField('rate_limit_buy_init', parseFloat(e.target.value) || 1.0)} />
                        <input className="adm-input" type="number" step="0.1" style={{ flex: 1, height: 20, padding: '2px 4px', fontSize: 11 }} value={draft.rate_limit_buy_maint} onChange={e => updateField('rate_limit_buy_maint', parseFloat(e.target.value) || 1.0)} />
                    </div>

                    <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                        <span style={{ width: 90, opacity: 0.8 }}>Sell Limit:</span>
                        <input className="adm-input" type="number" step="0.1" style={{ flex: 1, height: 20, padding: '2px 4px', fontSize: 11 }} value={draft.rate_limit_sell_init} onChange={e => updateField('rate_limit_sell_init', parseFloat(e.target.value) || 1.0)} />
                        <input className="adm-input" type="number" step="0.1" style={{ flex: 1, height: 20, padding: '2px 4px', fontSize: 11 }} value={draft.rate_limit_sell_maint} onChange={e => updateField('rate_limit_sell_maint', parseFloat(e.target.value) || 1.0)} />
                    </div>
                </div>

                {/* Right Column (Stops & Collaterals) */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    <div style={{ display: 'flex', gap: 8, fontWeight: 'bold', fontSize: 10, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 }}>
                        <span style={{ width: 90 }}>Order Type</span>
                        <span style={{ flex: 1, textAlign: 'center' }}>Initial</span>
                        <span style={{ flex: 1, textAlign: 'center' }}>Maint</span>
                    </div>

                    <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                        <span style={{ width: 90, opacity: 0.8 }}>Stops (Buy/Sell):</span>
                        <input className="adm-input" type="number" step="0.1" style={{ flex: 1, height: 20, padding: '2px 4px', fontSize: 11 }} value={draft.rate_limit_buy_init} onChange={e => updateField('rate_limit_buy_init', parseFloat(e.target.value) || 1.0)} />
                        <input className="adm-input" type="number" step="0.1" style={{ flex: 1, height: 20, padding: '2px 4px', fontSize: 11 }} value={draft.rate_limit_buy_maint} onChange={e => updateField('rate_limit_buy_maint', parseFloat(e.target.value) || 1.0)} />
                    </div>

                    <div style={{ fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginTop: 4, marginBottom: 2 }}>
                        Collateral Values
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 110, textAlign: 'right', opacity: 0.8 }}>Liquidity Margin:</span>
                        <input className="adm-input" type="number" step="0.01" style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }} placeholder="0.00" value={draft.discard_filter_level} onChange={e => updateField('discard_filter_level', parseFloat(e.target.value) || 0.0)} />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 110, textAlign: 'right', opacity: 0.8 }}>Currency Margin:</span>
                        <input className="adm-input" type="number" step="0.01" style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }} value={draft.delay_subscriptions} onChange={e => updateField('delay_subscriptions', parseFloat(e.target.value) || 0.0)} />
                    </div>
                </div>

            </div>
        </div>
    );
}
