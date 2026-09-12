import * as React from 'react';
import { useSymbolDraft } from '../SymbolDraftContext';

export function CommonTab(): React.ReactElement {
    const { draft, setDraft } = useSymbolDraft();

    const updateField = (field: keyof typeof draft, val: any) => {
        setDraft(prev => ({ ...prev, [field]: val }));
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 10, fontSize: 11 }}>
            {/* Top header info banner side-by-side */}
            <div style={{ display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', borderRadius: 4 }}>
                <div style={{ width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#f39c12', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' }}>
                    $
                </div>
                <div style={{ flex: 1, opacity: 0.9, lineHeight: 1.3 }}>
                    The setting up of main parameters of the symbol. Please specify its name, description, and other parameters.
                </div>
            </div>

            {/* Grid fields */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 24px' }}>
                {/* Left Column */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 80, textAlign: 'right', opacity: 0.8 }}>Symbol:</span>
                        <input 
                            className="adm-input" 
                            style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                            required 
                            value={draft.symbol}
                            onChange={e => updateField('symbol', e.target.value)}
                        />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 80, textAlign: 'right', opacity: 0.8 }}>Exchange:</span>
                        <input 
                            className="adm-input" 
                            style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                            value={draft.exchange}
                            onChange={e => updateField('exchange', e.target.value)}
                        />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 80, textAlign: 'right', opacity: 0.8 }}>ISIN:</span>
                        <input 
                            className="adm-input" 
                            style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                            value={draft.isin}
                            onChange={e => updateField('isin', e.target.value)}
                        />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 80, textAlign: 'right', opacity: 0.8 }}>CFI:</span>
                        <input 
                            className="adm-input" 
                            style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                            value={draft.cfi}
                            onChange={e => updateField('cfi', e.target.value)}
                        />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 80, textAlign: 'right', opacity: 0.8 }}>Basis:</span>
                        <input 
                            className="adm-input" 
                            style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                            value={draft.basis}
                            onChange={e => updateField('basis', e.target.value)}
                        />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 80, textAlign: 'right', opacity: 0.8 }}>Source:</span>
                        <input 
                            className="adm-input" 
                            style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                            value={draft.quote_source}
                            onChange={e => updateField('quote_source', e.target.value)}
                        />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 80, textAlign: 'right', opacity: 0.8 }}>Background:</span>
                        <div style={{ flex: 1, display: 'flex', gap: 6, alignItems: 'center' }}>
                            <input 
                                type="color"
                                style={{ width: 30, height: 20, border: 'none', cursor: 'pointer', padding: 0 }}
                                value={draft.bg_color}
                                onChange={e => updateField('bg_color', e.target.value)}
                            />
                            <input 
                                className="adm-input" 
                                style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                                value={draft.bg_color}
                                onChange={e => updateField('bg_color', e.target.value)}
                            />
                        </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 80, textAlign: 'right', opacity: 0.8 }}>Digits:</span>
                        <select 
                            className="adm-select" 
                            style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                            value={draft.digits}
                            onChange={e => updateField('digits', parseInt(e.target.value) || 0)}
                        >
                            <option value={0}>0</option>
                            <option value={1}>1</option>
                            <option value={2}>2</option>
                            <option value={3}>3</option>
                            <option value={4}>4</option>
                            <option value={5}>5</option>
                        </select>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 80, textAlign: 'right', opacity: 0.8 }}>Spread:</span>
                        <div style={{ flex: 1, display: 'flex', gap: 6, alignItems: 'center' }}>
                            <input 
                                className="adm-input" 
                                style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                                type="number"
                                value={draft.fixed_spread}
                                onChange={e => updateField('fixed_spread', parseInt(e.target.value) || 0)}
                            />
                            <span>pt</span>
                        </div>
                    </div>
                </div>

                {/* Right Column */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 80, textAlign: 'right', opacity: 0.8 }}>Description:</span>
                        <input 
                            className="adm-input" 
                            style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                            value={draft.description}
                            onChange={e => updateField('description', e.target.value)}
                        />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 80, textAlign: 'right', opacity: 0.8 }}>International:</span>
                        <input 
                            className="adm-input" 
                            style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                            value={draft.intl_name}
                            onChange={e => updateField('intl_name', e.target.value)}
                        />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 80, textAlign: 'right', opacity: 0.8 }}>Sector:</span>
                        <input 
                            className="adm-input" 
                            style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                            value={draft.sector}
                            onChange={e => updateField('sector', e.target.value)}
                        />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 80, textAlign: 'right', opacity: 0.8 }}>Industry:</span>
                        <input 
                            className="adm-input" 
                            style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                            value={draft.industry}
                            onChange={e => updateField('industry', e.target.value)}
                        />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 80, textAlign: 'right', opacity: 0.8 }}>Country:</span>
                        <input 
                            className="adm-input" 
                            style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                            value={draft.country}
                            onChange={e => updateField('country', e.target.value)}
                        />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 80, textAlign: 'right', opacity: 0.8 }}>Category:</span>
                        <input 
                            className="adm-input" 
                            style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                            value={draft.category}
                            onChange={e => updateField('category', e.target.value)}
                        />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 80, textAlign: 'right', opacity: 0.8 }}>Page:</span>
                        <input 
                            className="adm-input" 
                            style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                            value={draft.info_page}
                            onChange={e => updateField('info_page', e.target.value)}
                        />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 80, textAlign: 'right', opacity: 0.8 }}>Market depth:</span>
                        <select 
                            className="adm-select" 
                            style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                            value={draft.market_depth}
                            onChange={e => updateField('market_depth', parseInt(e.target.value) || 0)}
                        >
                            <option value={0}>off</option>
                            <option value={5}>5</option>
                            <option value={10}>10</option>
                            <option value={20}>20</option>
                            <option value={32}>32</option>
                        </select>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 80, textAlign: 'right', opacity: 0.8 }}>Chart mode:</span>
                        <select 
                            className="adm-select" 
                            style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                            value={draft.chart_mode}
                            onChange={e => updateField('chart_mode', e.target.value)}
                        >
                            <option value="bid">by bid price</option>
                            <option value="last">by last price</option>
                        </select>
                    </div>
                </div>
            </div>

            {/* Slider Spread balance */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 4 }}>
                <span style={{ width: 80, textAlign: 'right', opacity: 0.8 }}>Spread balance:</span>
                <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 10 }}>
                    <input 
                        type="range"
                        min="-100"
                        max="100"
                        style={{ flex: 1, cursor: 'pointer', height: 16 }}
                        value={draft.spread_balance_bid}
                        onChange={e => {
                            const val = parseInt(e.target.value) || 0;
                            updateField('spread_balance_bid', val);
                            updateField('spread_balance_ask', -val);
                        }}
                    />
                    <span style={{ width: 100, fontSize: 11 }}>{draft.spread_balance_bid} bid / {draft.spread_balance_ask} ask</span>
                </div>
            </div>
        </div>
    );
}
