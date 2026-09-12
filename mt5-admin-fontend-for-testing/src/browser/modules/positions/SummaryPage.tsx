// @ts-nocheck
import * as React from 'react';
import { API } from '../api';

export function SummaryPage(): React.ReactElement {
    const [summaryData, setSummaryData] = React.useState<any[]>([]);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState<string | null>(null);

    const loadData = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await API.getRiskSummary();
            setSummaryData(data);
        } catch (err: any) {
            setError(err.message || 'Failed to load summary positions data.');
        } finally {
            setLoading(false);
        }
    };

    React.useEffect(() => {
        loadData();
    }, []);

    return (
        <div className="adm-page">
            <div className="adm-toolbar">
                <button className="adm-btn" onClick={loadData}>
                    <i className="codicon codicon-refresh" /> Refresh
                </button>
            </div>

            {error && (
                <div className="adm-hint" style={{ background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)' }}>
                    <i className="codicon codicon-error" /> {error}
                </div>
            )}

            <div className="adm-table-wrap">
                {loading ? (
                    <div style={{ padding: 20, textAlign: 'center', opacity: 0.7 }}>Loading Summary positions...</div>
                ) : summaryData.length === 0 ? (
                    <div style={{ padding: 20, textAlign: 'center', opacity: 0.7 }}>No summary positions available.</div>
                ) : (
                    <table className="adm-table">
                        <thead>
                            <tr>
                                <th rowSpan={2}>Symbol</th>
                                <th colSpan={4} style={{ textAlign: 'center', borderBottom: '1px solid var(--theia-widget-border)' }}>Clients Summary</th>
                                <th colSpan={4} style={{ textAlign: 'center', borderBottom: '1px solid var(--theia-widget-border)' }}>Coverage Summary</th>
                                <th rowSpan={2} className="adm-num">Net Vol (Lots)</th>
                                <th rowSpan={2} className="adm-num">Uncovered Profit</th>
                            </tr>
                            <tr>
                                <th className="adm-num">Buy Vol</th>
                                <th className="adm-num">Buy Price</th>
                                <th className="adm-num">Sell Vol</th>
                                <th className="adm-num">Sell Price</th>
                                <th className="adm-num">Buy Vol</th>
                                <th className="adm-num">Buy Price</th>
                                <th className="adm-num">Sell Vol</th>
                                <th className="adm-num">Sell Price</th>
                            </tr>
                        </thead>
                        <tbody>
                            {summaryData.map(d => (
                                <tr key={d.symbol}>
                                    <td><strong>{d.symbol}</strong></td>
                                    <td className="adm-num">{(d.clientBuyVol || 0).toFixed(2)}</td>
                                    <td className="adm-num">{d.clientBuyAvg > 0 ? d.clientBuyAvg.toFixed(5) : '—'}</td>
                                    <td className="adm-num">{(d.clientSellVol || 0).toFixed(2)}</td>
                                    <td className="adm-num">{d.clientSellAvg > 0 ? d.clientSellAvg.toFixed(5) : '—'}</td>
                                    <td className="adm-num">{(d.covBuyVol || 0).toFixed(2)}</td>
                                    <td className="adm-num">{d.covBuyAvg > 0 ? d.covBuyAvg.toFixed(5) : '—'}</td>
                                    <td className="adm-num">{(d.covSellVol || 0).toFixed(2)}</td>
                                    <td className="adm-num">{d.covSellAvg > 0 ? d.covSellAvg.toFixed(5) : '—'}</td>
                                    <td className={`adm-num ${d.netVol === 0 ? '' : d.netVol > 0 ? 'adm-pos' : 'adm-neg'}`}>
                                        {d.netVol > 0 ? '+' : ''}{(d.netVol || 0).toFixed(2)}
                                    </td>
                                    <td className={`adm-num ${d.uncoveredProfit >= 0 ? 'adm-pos' : 'adm-neg'}`}>
                                        {d.uncoveredProfit >= 0 ? '+' : ''}{(d.uncoveredProfit || 0).toFixed(2)} USD
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
