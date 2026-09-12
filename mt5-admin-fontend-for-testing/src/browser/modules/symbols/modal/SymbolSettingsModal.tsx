// @ts-nocheck
import * as React from 'react';
import { SymbolDraft, DEFAULT_SYMBOL_DRAFT, SymbolDraftContext } from './SymbolDraftContext';
import { BulkEditBanner } from './BulkEditBanner';
import { CommonTab } from './tabs/CommonTab';
import { CurrencyTab } from './tabs/CurrencyTab';
import { QuotesTab } from './tabs/QuotesTab';
import { TradeTab } from './tabs/TradeTab';
import { ExecutionTab } from './tabs/ExecutionTab';
import { MarginTab } from './tabs/MarginTab';
import { MarginRatesTab } from './tabs/MarginRatesTab';
import { SwapsTab } from './tabs/SwapsTab';
import { SessionsTab } from './tabs/SessionsTab';
import { FuturesTab } from './tabs/FuturesTab';
import { OptionsTab } from './tabs/OptionsTab';
import { BondsTab } from './tabs/BondsTab';
import { API } from '../../api';

interface SymbolSettingsModalProps {
    symbolName: string | null; // Comma-separated names if bulk editing
    initialPath?: string;
    onClose: () => void;
    onSaved: () => void;
}

export function SymbolSettingsModal({ symbolName, initialPath = '', onClose, onSaved }: SymbolSettingsModalProps): React.ReactElement {
    const [draft, setDraft] = React.useState<SymbolDraft>(DEFAULT_SYMBOL_DRAFT);
    const [activeTab, setActiveTab] = React.useState('common');
    const [errors, setErrors] = React.useState<Record<string, string>>({});
    const [loading, setLoading] = React.useState(false);
    const [saveError, setSaveError] = React.useState<string | null>(null);

    const selectedNames = symbolName ? symbolName.split(',') : [];
    const isBulk = selectedNames.length > 1;
    const isEditing = selectedNames.length > 0;

    // Load details
    React.useEffect(() => {
        if (isEditing && !isBulk) {
            setLoading(true);
            API.getSymbolDetail(selectedNames[0])
                .then(data => {
                    let parsedSettings = {};
                    if (data.settings_json) {
                        try {
                            parsedSettings = JSON.parse(data.settings_json);
                        } catch {}
                    }
                    setDraft({
                        ...DEFAULT_SYMBOL_DRAFT,
                        symbol: data.symbol,
                        digits: data.digits,
                        contract_size: data.contract_size,
                        currency: data.currency,
                        margin_initial: data.margin_initial,
                        margin_maintenance: data.margin_maintenance,
                        spread_base: data.spread_base,
                        session_hours: data.session_hours,
                        ...parsedSettings
                    } as any);
                })
                .catch(err => {
                    setSaveError(err.message || 'Failed to fetch symbol specifications.');
                })
                .finally(() => {
                    setLoading(false);
                });
        } else if (initialPath) {
            setDraft(prev => ({
                ...prev,
                symbol: initialPath
            }));
        }
    }, [symbolName, initialPath]);

    // Derive tab strips dynamically based on Trade Tab's "Calculation" field
    const visibleTabs = React.useMemo(() => {
        const base = [
            { id: 'common', label: 'Common' },
            { id: 'currency', label: 'Currency' },
            { id: 'quotes', label: 'Quotes' },
            { id: 'trade', label: 'Trade' },
            { id: 'execution', label: 'Execution' },
            { id: 'margin', label: 'Margin' },
            { id: 'marginRates', label: 'Margin Rates' },
            { id: 'swaps', label: 'Swaps' },
            { id: 'sessions', label: 'Sessions' }
        ];

        const calc = draft.calculation;
        if (calc === 'Exchange Futures' || calc === 'Exchange FORTS Futures') {
            base.push({ id: 'futures', label: 'Futures' });
        } else if (calc === 'Exchange Option') {
            base.push({ id: 'options', label: 'Options' });
        } else if (calc === 'Exchange Bonds' || calc === 'Exchange MOEXBonds') {
            base.push({ id: 'bonds', label: 'Bonds' });
        }
        return base;
    }, [draft.calculation]);

    const validateAll = (): boolean => {
        const nextErrors: Record<string, string> = {};

        if (!draft.symbol.trim()) {
            nextErrors.symbol = 'Symbol name cannot be empty.';
        }

        setErrors(nextErrors);
        return Object.keys(nextErrors).length === 0;
    };

    const handleSave = async (e: React.FormEvent) => {
        e.preventDefault();
        setSaveError(null);

        if (!validateAll()) {
            setSaveError('Please correct validation warnings before saving.');
            return;
        }

        setLoading(true);
        try {
            // Trim name
            const trimmedSymbolName = draft.symbol.trim();

            if (isBulk) {
                // If postfix copy is active (postfix starting with .)
                const isPostfixCopy = trimmedSymbolName.startsWith('.');
                
                for (const name of selectedNames) {
                    if (isPostfixCopy) {
                        // Create copy EURUSD -> EURUSD.x
                        const copyName = name + trimmedSymbolName;
                        const payload = {
                            symbol: copyName,
                            digits: draft.digits,
                            contract_size: draft.contract_size,
                            currency: draft.currency,
                            margin_initial: draft.margin_initial,
                            margin_maintenance: draft.margin_maintenance,
                            spread_base: draft.spread_base,
                            session_hours: draft.session_hours,
                            settings_json: JSON.stringify({ ...draft, symbol: copyName })
                        };
                        await API.createSymbol(payload);
                    } else {
                        // Apply partial bulk updates
                        const original = await API.getSymbolDetail(name);
                        let origSettings = {};
                        if (original.settings_json) {
                            try { origSettings = JSON.parse(original.settings_json); } catch {}
                        }

                        // Overwrite only settings draft
                        const mergedSettings = { ...origSettings, ...draft };
                        delete mergedSettings.symbol;
                        delete mergedSettings.digits;
                        delete mergedSettings.contract_size;
                        delete mergedSettings.currency;
                        delete mergedSettings.margin_initial;
                        delete mergedSettings.margin_maintenance;
                        delete mergedSettings.spread_base;
                        delete mergedSettings.session_hours;

                        const payload = {
                            symbol: name,
                            digits: draft.digits,
                            contract_size: draft.contract_size,
                            currency: draft.currency,
                            margin_initial: draft.margin_initial,
                            margin_maintenance: draft.margin_maintenance,
                            spread_base: draft.spread_base,
                            session_hours: draft.session_hours,
                            settings_json: JSON.stringify(mergedSettings)
                        };
                        await API.updateSymbol(name, payload);
                    }
                }
            } else {
                // Single symbol add or update
                const settingsData = { ...draft } as any;
                delete settingsData.symbol;
                delete settingsData.digits;
                delete settingsData.contract_size;
                delete settingsData.currency;
                delete settingsData.margin_initial;
                delete settingsData.margin_maintenance;
                delete settingsData.spread_base;
                delete settingsData.session_hours;

                const payload = {
                    symbol: trimmedSymbolName,
                    digits: draft.digits,
                    contract_size: draft.contract_size,
                    currency: draft.currency,
                    margin_initial: draft.margin_initial,
                    margin_maintenance: draft.margin_maintenance,
                    spread_base: draft.spread_base,
                    session_hours: draft.session_hours,
                    settings_json: JSON.stringify(settingsData)
                };

                if (isEditing) {
                    await API.updateSymbol(selectedNames[0], payload);
                } else {
                    await API.createSymbol(payload);
                }
            }

            onSaved();
            onClose();
        } catch (err: any) {
            setSaveError(err.message || 'Failed to save symbol specifications.');
        } finally {
            setLoading(false);
        }
    };

    const renderActiveTabContent = () => {
        switch (activeTab) {
            case 'common': return <CommonTab />;
            case 'currency': return <CurrencyTab />;
            case 'quotes': return <QuotesTab />;
            case 'trade': return <TradeTab />;
            case 'execution': return <ExecutionTab />;
            case 'margin': return <MarginTab />;
            case 'marginRates': return <MarginRatesTab />;
            case 'swaps': return <SwapsTab />;
            case 'sessions': return <SessionsTab />;
            case 'futures': return <FuturesTab />;
            case 'options': return <OptionsTab />;
            case 'bonds': return <BondsTab />;
            default: return <CommonTab />;
        }
    };

    return (
        <SymbolDraftContext.Provider value={{ draft, setDraft, errors, setErrors, isEditing }}>
            <div className="adm-modal-overlay" onClick={onClose}>
                <div className="adm-modal" style={{ width: 750, height: '65vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }} onClick={e => e.stopPropagation()}>
                    <div className="adm-modal-header">
                        <h2>
                            <i className="codicon codicon-graph" style={{ marginRight: 8, color: '#2ecc71' }} />
                            {isBulk ? 'Bulk Edit Symbol Configurations' : isEditing ? `Symbol Settings — ${selectedNames[0]}` : 'Add New Financial Symbol'}
                        </h2>
                        <button type="button" className="adm-modal-close" onClick={onClose}>×</button>
                    </div>

                    {isBulk && <BulkEditBanner count={selectedNames.length} />}

                    <div className="adm-tabs" style={{ padding: '0 16px', borderBottom: '1px solid var(--theia-border)', flexShrink: 0 }}>
                        {visibleTabs.map(t => (
                            <button 
                                key={t.id} 
                                type="button"
                                className={`adm-tab ${activeTab === t.id ? 'active' : ''} ${errors.symbol && t.id === 'common' ? 'tab-error' : ''}`}
                                onClick={() => setActiveTab(t.id)}
                            >
                                {t.label}
                                {errors.symbol && t.id === 'common' && <span className="adm-tab-error-dot" />}
                            </button>
                        ))}
                    </div>

                    <div className="adm-modal-body" style={{ flex: 1, overflow: 'hidden', padding: '12px 16px', display: 'flex', flexDirection: 'column' }}>
                        {loading && (
                            <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.1)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 10 }}>
                                <span>Ingesting details...</span>
                            </div>
                        )}
                        
                        {saveError && (
                            <div className="adm-hint" style={{ background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)', margin: '0 0 16px 0' }}>
                                <i className="codicon codicon-error" /> {saveError}
                            </div>
                        )}

                        {renderActiveTabContent()}
                    </div>

                    <div className="adm-modal-footer" style={{ borderTop: '1px solid var(--theia-border)' }}>
                        <button type="button" className="adm-btn adm-btn-primary" onClick={handleSave} disabled={loading}>
                            OK
                        </button>
                        <button type="button" className="adm-btn" onClick={onClose} disabled={loading}>
                            Cancel
                        </button>
                    </div>
                </div>
            </div>
        </SymbolDraftContext.Provider>
    );
}
