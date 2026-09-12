// @ts-nocheck
import * as React from 'react';
import { API } from '../api';

export function MarginCallPage(): React.ReactElement {
    const [processedAccounts, setProcessedAccounts] = React.useState<any[]>([]);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState<string | null>(null);
    const [filterRiskOnly, setFilterRiskOnly] = React.useState(true);

    const loadData = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await API.getRiskMarginCalls();
            setProcessedAccounts(data);
        } catch (err: any) {
            setError(err.message || 'Failed to load margin call accounts list.');
        } finally {
            setLoading(false);
        }
    };

    React.useEffect(() => {
        loadData();
    }, []);

    // Filter accounts based on checkbox selection
    const filteredAccounts = React.useMemo(() => {
        if (filterRiskOnly) {
            return processedAccounts.filter(acc => acc.status !== 'OK');
        }
        return processedAccounts;
    }, [processedAccounts, filterRiskOnly]);

    return (
        <div className="adm-page">
            <div className="adm-toolbar">
                <button className="adm-btn" onClick={loadData}>
                    <i className="codicon codicon-refresh" /> Refresh
                </button>
                <div className="adm-toolbar-sep" />
                <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '11px', cursor: 'pointer' }}>
                    <input 
                        type="checkbox" 
                        checked={filterRiskOnly} 
                        onChange={e => setFilterRiskOnly(e.target.checked)} 
                    />
                    <span>Show accounts under risk only (Margin Call / Stop Out)</span>
                </label>
            </div>

            {error && (
                <div className="adm-hint" style={{ background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)' }}>
                    <i className="codicon codicon-error" /> {error}
                </div>
            )}

            <div className="adm-table-wrap">
                {loading ? (
                    <div style={{ padding: 20, textAlign: 'center', opacity: 0.7 }}>Loading margin accounts...</div>
                ) : filteredAccounts.length === 0 ? (
                    <div style={{ padding: 20, textAlign: 'center', opacity: 0.7 }}>
                        {filterRiskOnly ? 'No accounts are currently in Margin Call or Stop Out state.' : 'No accounts found.'}
                    </div>
                ) : (
                    <table className="adm-table">
                        <thead>
                            <tr>
                                <th>Login ID</th>
                                <th>Group</th>
                                <th className="adm-num">Balance</th>
                                <th className="adm-num">Equity</th>
                                <th className="adm-num">Margin</th>
                                <th className="adm-num">Free Margin</th>
                                <th className="adm-num">Margin Level (%)</th>
                                <th className="adm-num">MC / SO Limits</th>
                                <th style={{ textAlign: 'center' }}>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredAccounts.map(acc => {
                                const isRisk = acc.status !== 'OK';
                                return (
                                    <tr 
                                        key={acc.login} 
                                        style={{ 
                                            background: acc.colorCode,
                                            transition: 'background 0.2s'
                                        }}
                                    >
                                        <td><strong>{acc.login}</strong></td>
                                        <td>{acc.group_name}</td>
                                        <td className="adm-num">{(acc.balance || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })} {acc.currency}</td>
                                        <td className="adm-num">{(acc.equity || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })} {acc.currency}</td>
                                        <td className="adm-num">{acc.margin > 0 ? `${(acc.margin || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })} ${acc.currency}` : '—'}</td>
                                        <td className="adm-num">{(acc.freeMargin || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })} {acc.currency}</td>
                                        <td className="adm-num">
                                            {acc.margin > 0 ? (
                                                <strong className={acc.status === 'Stop Out' ? 'adm-neg' : acc.status === 'Margin Call' ? 'adm-neg' : 'adm-pos'}>
                                                    {(acc.marginLevel || 0).toFixed(2)}%
                                                </strong>
                                            ) : '—'}
                                        </td>
                                        <td className="adm-num" style={{ fontSize: '10.5px', opacity: 0.8 }}>
                                            {acc.marginCallLevel}% / {acc.stopOutLevel}%
                                        </td>
                                        <td style={{ textAlign: 'center' }}>
                                            {isRisk ? (
                                                <span 
                                                    className={`adm-tag`}
                                                    style={{ 
                                                        background: acc.status === 'Stop Out' ? 'var(--theia-errorForeground)' : '#f39c12',
                                                        color: '#fff',
                                                        fontWeight: 'bold',
                                                        padding: '2px 8px',
                                                        borderRadius: '3px'
                                                    }}
                                                >
                                                    {acc.status.toUpperCase()}
                                                </span>
                                            ) : (
                                                <span style={{ opacity: 0.6 }}>OK</span>
                                            )}
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
}
