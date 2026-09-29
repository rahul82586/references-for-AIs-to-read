// @ts-nocheck
import * as React from 'react';

interface SelectSymbolsStepProps {
    connectData: any;
    selectedSymbols: string[];
    onSelectSymbolsChange: (syms: string[]) => void;
    overwriteExisting: boolean;
    onOverwriteChange: (val: boolean) => void;
}

// Mock remote server symbols database
const MOCK_REMOTE_SYMBOLS = [
    { symbol: 'Forex\\Majors\\EURUSD', digits: 5, contract_size: 100000.0, currency: 'USD' },
    { symbol: 'Forex\\Majors\\GBPUSD', digits: 5, contract_size: 100000.0, currency: 'USD' },
    { symbol: 'Forex\\Minors\\EURGBP', digits: 5, contract_size: 100000.0, currency: 'GBP' },
    { symbol: 'CFD\\Stocks\\AAPL', digits: 2, contract_size: 100.0, currency: 'USD' },
    { symbol: 'CFD\\Stocks\\MSFT', digits: 2, contract_size: 100.0, currency: 'USD' },
    { symbol: 'Cryptos\\BTCUSD', digits: 2, contract_size: 1.0, currency: 'USD' },
    { symbol: 'Indices\\US500', digits: 1, contract_size: 10.0, currency: 'USD' }
];

export function SelectSymbolsStep({ 
    connectData, 
    selectedSymbols, 
    onSelectSymbolsChange, 
    overwriteExisting, 
    onOverwriteChange 
}: SelectSymbolsStepProps): React.ReactElement {
    
    const [activeFolder, setActiveFolder] = React.useState('Forex\\Majors');
    const [previewSymbol, setPreviewSymbol] = React.useState<any | null>(null);

    // Extract folders
    const folders = React.useMemo(() => {
        const set = new Set<string>();
        for (const s of MOCK_REMOTE_SYMBOLS) {
            const parts = s.symbol.split('\\');
            let pathAccum = '';
            for (let i = 0; i < parts.length - 1; i++) {
                pathAccum = pathAccum ? `${pathAccum}\\${parts[i]}` : parts[i];
                set.add(pathAccum);
            }
        }
        return Array.from(set).sort();
    }, []);

    // Filter contents of selected activeFolder
    const contents = React.useMemo(() => {
        return MOCK_REMOTE_SYMBOLS.filter(s => {
            const parts = s.symbol.split('\\');
            const parent = parts.slice(0, -1).join('\\');
            return parent === activeFolder;
        });
    }, [activeFolder]);

    const toggleSelectSymbol = (symbol: string) => {
        if (selectedSymbols.includes(symbol)) {
            onSelectSymbolsChange(selectedSymbols.filter(s => s !== symbol));
        } else {
            onSelectSymbolsChange([...selectedSymbols, symbol]);
        }
    };

    const handleSelectFolderSymbols = (folder: string) => {
        const folderSymbols = MOCK_REMOTE_SYMBOLS.filter(s => s.symbol.startsWith(folder + '\\')).map(s => s.symbol);
        const allSelected = folderSymbols.every(s => selectedSymbols.includes(s));
        
        if (allSelected) {
            // Deselect all in folder
            onSelectSymbolsChange(selectedSymbols.filter(s => !folderSymbols.includes(s)));
        } else {
            // Select all in folder
            onSelectSymbolsChange(Array.from(new Set([...selectedSymbols, ...folderSymbols])));
        }
    };

    const handleSelectAll = () => {
        const allNames = MOCK_REMOTE_SYMBOLS.map(s => s.symbol);
        if (selectedSymbols.length === allNames.length) {
            onSelectSymbolsChange([]);
        } else {
            onSelectSymbolsChange(allNames);
        }
    };

    return (
        <div className="adm-modal-body" style={{ display: 'flex', flexDirection: 'column', height: '50vh', gap: 10 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: 11, color: 'var(--theia-descriptionForeground)' }}>
                    Connected to <strong>{connectData.address}</strong>. Select the instruments you want to ingest:
                </span>
                <button type="button" className="adm-btn" style={{ fontSize: 11, padding: '2px 8px' }} onClick={handleSelectAll}>
                    {selectedSymbols.length === MOCK_REMOTE_SYMBOLS.length ? 'Deselect All' : 'Select All'}
                </button>
            </div>

            <div className="adm-split-view" style={{ flex: 1, minHeight: 0, border: '1px solid var(--theia-border)' }}>
                {/* Left remote folders */}
                <div style={{ width: 160, borderRight: '1px solid var(--theia-border)', overflowY: 'auto', padding: 6, display: 'flex', flexDirection: 'column', gap: 2 }}>
                    {folders.map(f => {
                        const parts = f.split('\\');
                        const depth = parts.length - 1;
                        return (
                            <div 
                                key={f} 
                                className={`adm-tree-pane-row ${activeFolder === f ? 'active' : ''}`}
                                style={{ paddingLeft: `${4 + depth * 10}px`, fontSize: 11, height: 20 }}
                                onClick={() => setActiveFolder(f)}
                                onDoubleClick={() => handleSelectFolderSymbols(f)}
                                title="Double-click to select all symbols in folder"
                            >
                                <i className="codicon codicon-folder" style={{ fontSize: 11 }} />
                                <span>{parts[parts.length - 1]}</span>
                            </div>
                        );
                    })}
                </div>

                {/* Right symbols list */}
                <div style={{ flex: 1, overflowY: 'auto', padding: 4 }}>
                    <table className="adm-table" style={{ fontSize: 11 }}>
                        <thead>
                            <tr>
                                <th style={{ width: 40 }}>Sel</th>
                                <th>Symbol Name</th>
                                <th>Digits</th>
                                <th>Contract Size</th>
                            </tr>
                        </thead>
                        <tbody>
                            {contents.map(s => {
                                const isSelected = selectedSymbols.includes(s.symbol);
                                const lastPart = s.symbol.split('\\').pop() || s.symbol;
                                return (
                                    <tr 
                                        key={s.symbol}
                                        className={isSelected ? 'selected' : ''}
                                        onClick={() => toggleSelectSymbol(s.symbol)}
                                    >
                                        <td>
                                            <input 
                                                type="checkbox" 
                                                checked={isSelected}
                                                onChange={() => toggleSelectSymbol(s.symbol)}
                                                onClick={e => e.stopPropagation()} 
                                            />
                                        </td>
                                        <td>
                                            <span 
                                                style={{ textDecoration: 'underline', cursor: 'help' }}
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    setPreviewSymbol(s);
                                                }}
                                                title="Click to view specifications preview"
                                            >
                                                {lastPart}
                                            </span>
                                        </td>
                                        <td>{s.digits}</td>
                                        <td>{s.contract_size.toLocaleString()}</td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 6 }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, cursor: 'pointer' }}>
                    <input 
                        type="checkbox" 
                        checked={overwriteExisting} 
                        onChange={e => onOverwriteChange(e.target.checked)} 
                    />
                    <span>Overwrite existing symbols with matching names</span>
                </label>
                <span style={{ fontSize: 11 }}>Selected: <strong>{selectedSymbols.length}</strong> symbol(s)</span>
            </div>

            {/* Read-only specification preview dialog */}
            {previewSymbol && (
                <div className="adm-modal-overlay" style={{ zIndex: 1200 }} onClick={() => setPreviewSymbol(null)}>
                    <div className="adm-modal" style={{ width: 300 }} onClick={e => e.stopPropagation()}>
                        <div className="adm-modal-header">
                            <h3>Remote Specifications - {previewSymbol.symbol.split('\\').pop()}</h3>
                            <button type="button" className="adm-modal-close" onClick={() => setPreviewSymbol(null)}>×</button>
                        </div>
                        <div className="adm-modal-body" style={{ fontSize: 11, display: 'flex', flexDirection: 'column', gap: 6 }}>
                            <div className="adm-kv"><span>Full Path</span><strong>{previewSymbol.symbol}</strong></div>
                            <div className="adm-kv"><span>Digits Precision</span><span>{previewSymbol.digits}</span></div>
                            <div className="adm-kv"><span>Contract Size</span><span>{previewSymbol.contract_size.toLocaleString()}</span></div>
                            <div className="adm-kv"><span>Base Currency</span><span>{previewSymbol.currency}</span></div>
                            <div className="adm-kv"><span>Trade Session</span><span>MON-FRI 00:00-24:00 (Standard)</span></div>
                        </div>
                        <div className="adm-modal-footer">
                            <button type="button" className="adm-btn" onClick={() => setPreviewSymbol(null)}>Close Preview</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
