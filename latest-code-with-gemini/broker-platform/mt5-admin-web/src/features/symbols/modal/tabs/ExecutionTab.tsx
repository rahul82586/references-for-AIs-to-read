import * as React from 'react';
import { useSymbolDraft } from '../SymbolDraftContext';

export function ExecutionTab(): React.ReactElement {
    const { draft, setDraft } = useSymbolDraft();

    const updateField = (field: keyof typeof draft, val: any) => {
        setDraft(prev => ({ ...prev, [field]: val }));
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 10, fontSize: 11 }}>
            {/* Top header info banner side-by-side */}
            <div style={{ display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', borderRadius: 4 }}>
                <div style={{ width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#34495e', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' }}>
                    E
                </div>
                <div style={{ flex: 1, opacity: 0.9, lineHeight: 1.3 }}>
                    Configure execution modes and order routing paths for trade request processing.
                </div>
            </div>

            {/* Grid fields */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 24px', flex: 1, marginTop: 8 }}>
                {/* Left Column (Routing Mode Selection) */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>Execution mode:</span>
                        <select 
                            className="adm-select" 
                            style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                            value={draft.execution_mode} 
                            onChange={e => updateField('execution_mode', e.target.value)}
                        >
                            <option value="Instant">Instant Execution</option>
                            <option value="Request">Request Execution</option>
                            <option value="Market">Market Execution</option>
                            <option value="Exchange">Exchange Execution</option>
                        </select>
                    </div>

                    {draft.execution_mode === 'Instant' && (
                        <>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>Max dev (pts):</span>
                                <input 
                                    className="adm-input" 
                                    type="number" 
                                    style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                                    value={draft.instant_max_time_dev} 
                                    onChange={e => updateField('instant_max_time_dev', parseInt(e.target.value) || 0)} 
                                />
                            </div>

                            <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, cursor: 'pointer', paddingLeft: 10 }}>
                                <input 
                                    type="checkbox" 
                                    checked={draft.instant_fast_requotes} 
                                    onChange={e => updateField('instant_fast_requotes', e.target.checked)} 
                                />
                                Auto-confirm requotes within dev
                            </label>
                        </>
                    )}

                    {draft.execution_mode === 'Request' && (
                        <>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>Timeout (sec):</span>
                                <input 
                                    className="adm-input" 
                                    type="number" 
                                    style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                                    value={draft.request_timeout} 
                                    onChange={e => updateField('request_timeout', parseInt(e.target.value) || 10)} 
                                />
                            </div>

                            <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, cursor: 'pointer', paddingLeft: 10 }}>
                                <input 
                                    type="checkbox" 
                                    checked={draft.request_confirm} 
                                    onChange={e => updateField('request_confirm', e.target.checked)} 
                                />
                                Require manager check first
                            </label>
                        </>
                    )}
                </div>

                {/* Right Column (Info Display Cards) */}
                <div style={{ display: 'flex', flexDirection: 'column' }}>
                    {draft.execution_mode === 'Market' && (
                        <div className="adm-hint" style={{ margin: 0, padding: '8px 12px' }}>
                            <i className="codicon codicon-info" style={{ marginRight: 6 }} />
                            <strong>Market Mode:</strong> Trades execute at the next available server price. Requotes are disabled because prices are accepted upfront.
                        </div>
                    )}

                    {draft.execution_mode === 'Exchange' && (
                        <div className="adm-hint" style={{ margin: 0, padding: '8px 12px', borderLeft: '3px solid #e67e22' }}>
                            <i className="codicon codicon-info" style={{ marginRight: 6, color: '#e67e22' }} />
                            <strong>Exchange Mode:</strong> Routed directly to liquidity providers. Limit and freeze boundaries are bypassed, leaving filling choices to the exchange order book.
                        </div>
                    )}

                    {draft.execution_mode === 'Instant' && (
                        <div className="adm-hint" style={{ margin: 0, padding: '8px 12px' }}>
                            <i className="codicon codicon-info" style={{ marginRight: 6 }} />
                            <strong>Instant Mode:</strong> Order executes exactly at the requested price. If the price moves beyond client-side deviation, the broker returns a requote.
                        </div>
                    )}

                    {draft.execution_mode === 'Request' && (
                        <div className="adm-hint" style={{ margin: 0, padding: '8px 12px' }}>
                            <i className="codicon codicon-info" style={{ marginRight: 6 }} />
                            <strong>Request Mode:</strong> Client asks for quotes first, then sends confirmation to execute. Best suited for manual voice or high-ticket desk dealers.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
