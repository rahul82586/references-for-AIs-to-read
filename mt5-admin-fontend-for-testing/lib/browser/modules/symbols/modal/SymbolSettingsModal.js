"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SymbolSettingsModal = void 0;
// @ts-nocheck
const React = require("react");
const SymbolDraftContext_1 = require("./SymbolDraftContext");
const BulkEditBanner_1 = require("./BulkEditBanner");
const CommonTab_1 = require("./tabs/CommonTab");
const CurrencyTab_1 = require("./tabs/CurrencyTab");
const QuotesTab_1 = require("./tabs/QuotesTab");
const TradeTab_1 = require("./tabs/TradeTab");
const ExecutionTab_1 = require("./tabs/ExecutionTab");
const MarginTab_1 = require("./tabs/MarginTab");
const MarginRatesTab_1 = require("./tabs/MarginRatesTab");
const SwapsTab_1 = require("./tabs/SwapsTab");
const SessionsTab_1 = require("./tabs/SessionsTab");
const FuturesTab_1 = require("./tabs/FuturesTab");
const OptionsTab_1 = require("./tabs/OptionsTab");
const BondsTab_1 = require("./tabs/BondsTab");
const api_1 = require("../../api");
function SymbolSettingsModal({ symbolName, initialPath = '', onClose, onSaved }) {
    const [draft, setDraft] = React.useState(SymbolDraftContext_1.DEFAULT_SYMBOL_DRAFT);
    const [activeTab, setActiveTab] = React.useState('common');
    const [errors, setErrors] = React.useState({});
    const [loading, setLoading] = React.useState(false);
    const [saveError, setSaveError] = React.useState(null);
    const selectedNames = symbolName ? symbolName.split(',') : [];
    const isBulk = selectedNames.length > 1;
    const isEditing = selectedNames.length > 0;
    // Load details
    React.useEffect(() => {
        if (isEditing && !isBulk) {
            setLoading(true);
            api_1.API.getSymbolDetail(selectedNames[0])
                .then(data => {
                let parsedSettings = {};
                if (data.settings_json) {
                    try {
                        parsedSettings = JSON.parse(data.settings_json);
                    }
                    catch { }
                }
                setDraft({
                    ...SymbolDraftContext_1.DEFAULT_SYMBOL_DRAFT,
                    symbol: data.symbol,
                    digits: data.digits,
                    contract_size: data.contract_size,
                    currency: data.currency,
                    margin_initial: data.margin_initial,
                    margin_maintenance: data.margin_maintenance,
                    spread_base: data.spread_base,
                    session_hours: data.session_hours,
                    ...parsedSettings
                });
            })
                .catch(err => {
                setSaveError(err.message || 'Failed to fetch symbol specifications.');
            })
                .finally(() => {
                setLoading(false);
            });
        }
        else if (initialPath) {
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
        }
        else if (calc === 'Exchange Option') {
            base.push({ id: 'options', label: 'Options' });
        }
        else if (calc === 'Exchange Bonds' || calc === 'Exchange MOEXBonds') {
            base.push({ id: 'bonds', label: 'Bonds' });
        }
        return base;
    }, [draft.calculation]);
    const validateAll = () => {
        const nextErrors = {};
        if (!draft.symbol.trim()) {
            nextErrors.symbol = 'Symbol name cannot be empty.';
        }
        setErrors(nextErrors);
        return Object.keys(nextErrors).length === 0;
    };
    const handleSave = async (e) => {
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
                        await api_1.API.createSymbol(payload);
                    }
                    else {
                        // Apply partial bulk updates
                        const original = await api_1.API.getSymbolDetail(name);
                        let origSettings = {};
                        if (original.settings_json) {
                            try {
                                origSettings = JSON.parse(original.settings_json);
                            }
                            catch { }
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
                        await api_1.API.updateSymbol(name, payload);
                    }
                }
            }
            else {
                // Single symbol add or update
                const settingsData = { ...draft };
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
                    await api_1.API.updateSymbol(selectedNames[0], payload);
                }
                else {
                    await api_1.API.createSymbol(payload);
                }
            }
            onSaved();
            onClose();
        }
        catch (err) {
            setSaveError(err.message || 'Failed to save symbol specifications.');
        }
        finally {
            setLoading(false);
        }
    };
    const renderActiveTabContent = () => {
        switch (activeTab) {
            case 'common': return React.createElement(CommonTab_1.CommonTab, null);
            case 'currency': return React.createElement(CurrencyTab_1.CurrencyTab, null);
            case 'quotes': return React.createElement(QuotesTab_1.QuotesTab, null);
            case 'trade': return React.createElement(TradeTab_1.TradeTab, null);
            case 'execution': return React.createElement(ExecutionTab_1.ExecutionTab, null);
            case 'margin': return React.createElement(MarginTab_1.MarginTab, null);
            case 'marginRates': return React.createElement(MarginRatesTab_1.MarginRatesTab, null);
            case 'swaps': return React.createElement(SwapsTab_1.SwapsTab, null);
            case 'sessions': return React.createElement(SessionsTab_1.SessionsTab, null);
            case 'futures': return React.createElement(FuturesTab_1.FuturesTab, null);
            case 'options': return React.createElement(OptionsTab_1.OptionsTab, null);
            case 'bonds': return React.createElement(BondsTab_1.BondsTab, null);
            default: return React.createElement(CommonTab_1.CommonTab, null);
        }
    };
    return (React.createElement(SymbolDraftContext_1.SymbolDraftContext.Provider, { value: { draft, setDraft, errors, setErrors, isEditing } },
        React.createElement("div", { className: "adm-modal-overlay", onClick: onClose },
            React.createElement("div", { className: "adm-modal", style: { width: 750, height: '65vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }, onClick: e => e.stopPropagation() },
                React.createElement("div", { className: "adm-modal-header" },
                    React.createElement("h2", null,
                        React.createElement("i", { className: "codicon codicon-graph", style: { marginRight: 8, color: '#2ecc71' } }),
                        isBulk ? 'Bulk Edit Symbol Configurations' : isEditing ? `Symbol Settings — ${selectedNames[0]}` : 'Add New Financial Symbol'),
                    React.createElement("button", { type: "button", className: "adm-modal-close", onClick: onClose }, "\u00D7")),
                isBulk && React.createElement(BulkEditBanner_1.BulkEditBanner, { count: selectedNames.length }),
                React.createElement("div", { className: "adm-tabs", style: { padding: '0 16px', borderBottom: '1px solid var(--theia-border)', flexShrink: 0 } }, visibleTabs.map(t => (React.createElement("button", { key: t.id, type: "button", className: `adm-tab ${activeTab === t.id ? 'active' : ''} ${errors.symbol && t.id === 'common' ? 'tab-error' : ''}`, onClick: () => setActiveTab(t.id) },
                    t.label,
                    errors.symbol && t.id === 'common' && React.createElement("span", { className: "adm-tab-error-dot" }))))),
                React.createElement("div", { className: "adm-modal-body", style: { flex: 1, overflow: 'hidden', padding: '12px 16px', display: 'flex', flexDirection: 'column' } },
                    loading && (React.createElement("div", { style: { position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.1)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 10 } },
                        React.createElement("span", null, "Ingesting details..."))),
                    saveError && (React.createElement("div", { className: "adm-hint", style: { background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)', margin: '0 0 16px 0' } },
                        React.createElement("i", { className: "codicon codicon-error" }),
                        " ",
                        saveError)),
                    renderActiveTabContent()),
                React.createElement("div", { className: "adm-modal-footer", style: { borderTop: '1px solid var(--theia-border)' } },
                    React.createElement("button", { type: "button", className: "adm-btn adm-btn-primary", onClick: handleSave, disabled: loading }, "OK"),
                    React.createElement("button", { type: "button", className: "adm-btn", onClick: onClose, disabled: loading }, "Cancel"))))));
}
exports.SymbolSettingsModal = SymbolSettingsModal;
//# sourceMappingURL=SymbolSettingsModal.js.map