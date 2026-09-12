// @ts-nocheck
import * as React from 'react';
import { API } from '../api';

export function ExposurePage(): React.ReactElement {
    const [exposureData, setExposureData] = React.useState<any[]>([]);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState<string | null>(null);
    const [displayCurrency, setDisplayCurrency] = React.useState('USD');

    const loadData = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await API.getRiskExposure();
            setExposureData(data);
        } catch (err: any) {
            setError(err.message || 'Failed to load Exposure data.');
        } finally {
            setLoading(false);
        }
    };

    React.useEffect(() => {
        loadData();
    }, []);

    // Calculated Exposure mapped to custom Display Currency
    const mappedExposure = React.useMemo(() => {
        // Mock conversion rates relative to display currency if needed
        const mockRates: Record<string, number> = {
            'USD': 1.0,
            'EUR': 1.09,
            'GBP': 1.27,
            'JPY': 0.0067,
            'NZD': 0.61,
            'AUD': 0.66,
            'NOK': 0.095,
            'BTC': 62000.0,
            'XAU': 2350.0,
            'XAG': 29.5
        };

        // Standardize everything to displayCurrency
        const currentDisplayRate = mockRates[displayCurrency] || 1.0;

        return exposureData.map(d => {
            const assetRate = mockRates[d.asset] || 1.0;
            // Cross-convert rate from asset to target display currency
            const rate = assetRate / currentDisplayRate;
            const netTotalConverted = d.netTotal * rate;
            const positiveConverted = netTotalConverted > 0 ? netTotalConverted : 0;

            return {
                ...d,
                rate,
                netTotalConverted,
                positiveConverted
            };
        });
    }, [exposureData, displayCurrency]);

    return (
        <div className="adm-page">
            <div className="adm-toolbar">
                <button className="adm-btn" onClick={loadData}>
                    <i className="codicon codicon-refresh" /> Refresh
                </button>
                <div className="adm-toolbar-sep" />
                <span style={{ fontSize: '11px', opacity: 0.8 }}>Dashboard Currency: </span>
                <select 
                    className="adm-select" 
                    style={{ width: 100, height: 24, padding: '2px 6px' }}
                    value={displayCurrency} 
                    onChange={e => setDisplayCurrency(e.target.value)}
                >
                    <option value="USD">USD</option>
                    <option value="EUR">EUR</option>
                    <option value="GBP">GBP</option>
                </select>
            </div>

            {error && (
                <div className="adm-hint" style={{ background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)' }}>
                    <i className="codicon codicon-error" /> {error}
                </div>
            )}

            <div className="adm-table-wrap">
                {loading ? (
                    <div style={{ padding: 20, textAlign: 'center', opacity: 0.7 }}>Loading Exposure assets...</div>
                ) : mappedExposure.length === 0 ? (
                    <div style={{ padding: 20, textAlign: 'center', opacity: 0.7 }}>No exposure assets found.</div>
                ) : (
                    <table className="adm-table">
                        <thead>
                            <tr>
                                <th>Asset</th>
                                <th className="adm-num">Clients (Units)</th>
                                <th className="adm-num">Coverage (Units)</th>
                                <th className="adm-num">Net Total (Units)</th>
                                <th className="adm-num">Rate ({displayCurrency})</th>
                                <th className="adm-num">Net Total ({displayCurrency})</th>
                                <th className="adm-num">Positive ({displayCurrency})</th>
                            </tr>
                        </thead>
                        <tbody>
                            {mappedExposure.map(d => (
                                <tr key={d.asset}>
                                    <td><strong>{d.asset}</strong></td>
                                    <td className="adm-num">{(d.clients || 0).toLocaleString('en-US', { maximumFractionDigits: 2 })}</td>
                                    <td className="adm-num">{(d.coverage || 0).toLocaleString('en-US', { maximumFractionDigits: 2 })}</td>
                                    <td className={`adm-num ${d.netTotal === 0 ? '' : d.netTotal > 0 ? 'adm-pos' : 'adm-neg'}`}>
                                        {d.netTotal > 0 ? '+' : ''}{(d.netTotal || 0).toLocaleString('en-US', { maximumFractionDigits: 2 })}
                                    </td>
                                    <td className="adm-num">{d.rate.toLocaleString('en-US', { minimumFractionDigits: 4, maximumFractionDigits: 4 })}</td>
                                    <td className={`adm-num ${d.netTotalConverted >= 0 ? 'adm-pos' : 'adm-neg'}`}>
                                        {d.netTotalConverted >= 0 ? '+' : ''}{d.netTotalConverted.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                    </td>
                                    <td className="adm-num adm-pos">
                                        {d.positiveConverted > 0 ? d.positiveConverted.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '0.00'}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
}
