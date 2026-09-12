// @ts-nocheck
import * as React from 'react';
import { ConnectStep } from './ConnectStep';
import { SelectSymbolsStep } from './SelectSymbolsStep';
import { ImportSummary } from './ImportSummary';
import { API } from '../../api';

interface ImportWizardProps {
    activeFolder: string;
    onClose: () => void;
    onImported: () => void;
}

export function ImportWizard({ activeFolder, onClose, onImported }: ImportWizardProps): React.ReactElement {
    const [step, setStep] = React.useState(1);
    const [loading, setLoading] = React.useState(false);
    const [error, setError] = React.useState<string | null>(null);

    // Form inputs
    const [connectData, setConnectData] = React.useState({
        serverType: 'MT5',
        address: 'demo.metaquotes.net:443',
        login: '1000',
        password: '',
        useCert: false,
        certFile: '',
        certPassword: ''
    });

    const [selectedSymbols, setSelectedSymbols] = React.useState<string[]>([]);
    const [overwriteExisting, setOverwriteExisting] = React.useState(false);

    const handleConnectChange = (fields: any) => {
        setConnectData(prev => ({ ...prev, ...fields }));
    };

    const handleNext = async () => {
        setError(null);

        if (step === 1) {
            // Validate credentials and simulate connection
            if (!connectData.address || !connectData.login || !connectData.password) {
                setError('Please fill in all connection parameters.');
                return;
            }
            setLoading(true);
            // Simulate connection delay
            setTimeout(() => {
                setLoading(false);
                setStep(2);
            }, 800);
        } else if (step === 2) {
            if (selectedSymbols.length === 0) {
                setError('Please select at least one symbol to import.');
                return;
            }
            setLoading(true);
            try {
                // Mock symbols details list matching the selection
                const remoteMockSymbols = [
                    { symbol: 'EURUSD', path: 'Forex\\Majors\\EURUSD', digits: 5, contract_size: 100000.0, currency: 'USD' },
                    { symbol: 'GBPUSD', path: 'Forex\\Majors\\GBPUSD', digits: 5, contract_size: 100000.0, currency: 'USD' },
                    { symbol: 'EURGBP', path: 'Forex\\Minors\\EURGBP', digits: 5, contract_size: 100000.0, currency: 'GBP' },
                    { symbol: 'AAPL', path: 'CFD\\Stocks\\AAPL', digits: 2, contract_size: 100.0, currency: 'USD' },
                    { symbol: 'MSFT', path: 'CFD\\Stocks\\MSFT', digits: 2, contract_size: 100.0, currency: 'USD' },
                    { symbol: 'BTCUSD', path: 'Cryptos\\BTCUSD', digits: 2, contract_size: 1.0, currency: 'USD' },
                    { symbol: 'US500', path: 'Indices\\US500', digits: 1, contract_size: 10.0, currency: 'USD' }
                ];

                for (const fullPath of selectedSymbols) {
                    const match = remoteMockSymbols.find(m => m.path === fullPath);
                    if (!match) continue;

                    // MT4-sourced imports land in the currently-selected folder; MT5 preserves structure
                    let finalSymbolPath = fullPath;
                    if (connectData.serverType === 'MT4') {
                        finalSymbolPath = activeFolder ? `${activeFolder}\\${match.symbol}` : match.symbol;
                    }

                    // Trading is set to disabled regardless of source settings
                    const settingsObj = {
                        trade_mode: 'disabled',
                        import_source: connectData.address,
                        import_time: new Date().toISOString()
                    };

                    await API.createSymbol({
                        symbol: finalSymbolPath,
                        digits: match.digits,
                        contract_size: match.contract_size,
                        currency: match.currency,
                        margin_initial: 1.0,
                        margin_maintenance: 1.0,
                        spread_base: 10,
                        session_hours: 'MON,00:00-23:59;TUE,00:00-23:59;WED,00:00-23:59;THU,00:00-23:59;FRI,00:00-23:59',
                        settings_json: JSON.stringify(settingsObj)
                    });
                }
                setLoading(false);
                setStep(3);
            } catch (err: any) {
                setLoading(false);
                setError(err.message || 'Failed to ingest symbols on trade server.');
            }
        }
    };

    const handleBack = () => {
        setError(null);
        if (step > 1) setStep(step - 1);
    };

    const handleDone = () => {
        onImported();
        onClose();
    };

    const renderStepContent = () => {
        switch (step) {
            case 1:
                return <ConnectStep data={connectData} onChange={handleConnectChange} />;
            case 2:
                return (
                    <SelectSymbolsStep 
                        connectData={connectData}
                        selectedSymbols={selectedSymbols}
                        onSelectSymbolsChange={setSelectedSymbols}
                        overwriteExisting={overwriteExisting}
                        onOverwriteChange={setOverwriteExisting}
                    />
                );
            case 3:
                return <ImportSummary count={selectedSymbols.length} overwrite={overwriteExisting} />;
            default:
                return null;
        }
    };

    return (
        <div className="adm-modal-overlay" style={{ zIndex: 1100 }} onClick={onClose}>
            <div className="adm-modal" style={{ width: 500 }} onClick={e => e.stopPropagation()}>
                <div className="adm-modal-header">
                    <h2>Import Symbols Configuration Wizard</h2>
                    <span style={{ fontSize: 11, color: 'var(--theia-descriptionForeground)' }}>
                        Step {step} of 3
                    </span>
                </div>

                {error && (
                    <div className="adm-hint" style={{ background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)', margin: '10px 16px 0 16px' }}>
                        <i className="codicon codicon-error" /> {error}
                    </div>
                )}

                {loading ? (
                    <div className="adm-modal-body" style={{ height: '30vh', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                        <span>Processing steps...</span>
                    </div>
                ) : (
                    renderStepContent()
                )}

                <div className="adm-modal-footer">
                    {step === 3 ? (
                        <button type="button" className="adm-btn adm-btn-primary" onClick={handleDone}>
                            Done
                        </button>
                    ) : (
                        <>
                            <button 
                                type="button" 
                                className="adm-btn" 
                                disabled={step === 1 || loading} 
                                onClick={handleBack}
                            >
                                Back
                            </button>
                            <button 
                                type="button" 
                                className="adm-btn adm-btn-primary" 
                                disabled={loading} 
                                onClick={handleNext}
                            >
                                {step === 1 ? 'Connect' : 'Ingest Symbols'}
                            </button>
                        </>
                    )}
                    <button type="button" className="adm-btn" onClick={onClose} disabled={loading}>
                        Cancel
                    </button>
                </div>
            </div>
        </div>
    );
}
