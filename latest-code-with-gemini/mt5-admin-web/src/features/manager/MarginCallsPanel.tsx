import * as React from 'react';
import { API } from '../../services/api';
import { money, percent } from '../../shared/format';

interface GroupThresholds { name: string; margin_call: number; stop_out: number }

/**
 * Margin Calls window — accounts that breached their group's margin-call or
 * stop-out level (doc §Margin Call/Stop Out; values come from the backend,
 * the comparison is display-side only).
 */
export function MarginCallsPanel(): React.ReactElement {
    const [rows, setRows] = React.useState<any[]>([]);
    const [error, setError] = React.useState<string | null>(null);

    React.useEffect(() => {
        (async () => {
            try {
                const [accounts, groups] = await Promise.all([API.getAccounts(), API.getGroups()]);
                const th = new Map<string, GroupThresholds>();
                for (const g of groups as any[]) {
                    let mc = 60, so = 30;
                    try {
                        const st = JSON.parse(g.settings_json ?? '{}');
                        mc = Number(st.margin_call ?? mc);
                        so = Number(st.margin_stop_out ?? so);
                    } catch { /* defaults */ }
                    th.set(g.name, { name: g.name, margin_call: mc, stop_out: so });
                }
                setRows(
                    accounts
                        .map((a: any) => {
                            const t = th.get(a.group);
                            const level = Number(a.margin_level ?? 0);
                            if (!t || level <= 0) return null;
                            if (level >= t.margin_call) return null;
                            return { ...a, mc: t.margin_call, so: t.stop_out, stopout: level < t.stop_out };
                        })
                        .filter(Boolean)
                );
            } catch (e: any) {
                setError(String(e?.message ?? e));
            }
        })();
    }, []);

    return (
        <div className="ca-page">
            <div className="ca-toolbar">
                <div className="ca-request">
                    <i className="codicon codicon-warning" />
                    <span style={{ fontSize: 12 }}>Accounts below their group margin-call level — stop-out candidates</span>
                </div>
                <button
                    className="wb-btn secondary"
                    onClick={() => setError('Backend gap: margin-call notifications (internal mail / push) are not exposed by the API yet.')}
                >
                    <i className="codicon codicon-mail" /> Notify clients
                </button>
            </div>
            {error && <div className="ca-banner gap"><i className="codicon codicon-warning" /><span>{error}</span></div>}
            <div className="ca-main">
                <div className="ca-table-wrap">
                    <table className="adm-table ca-table">
                        <thead>
                            <tr>
                                <th>Login</th><th>Name</th><th>Group</th>
                                <th className="num">Equity</th><th className="num">Margin</th>
                                <th className="num">Margin Level</th><th className="num">Margin Call</th><th className="num">Stop Out</th>
                                <th>State</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows.map((a: any) => (
                                <tr key={a.login}>
                                    <td><code className="adm-code">{a.login}</code></td>
                                    <td className="ca-name">{a.name}</td>
                                    <td><code className="adm-code ca-group">{a.group}</code></td>
                                    <td className="num">{money(a.equity)}</td>
                                    <td className="num">{money(a.margin)}</td>
                                    <td className={`num ${a.stopout ? 'heat-red' : 'heat-amber'}`}>{percent(a.margin_level)}</td>
                                    <td className="num ca-dim">{percent(a.mc)}</td>
                                    <td className="num ca-dim">{percent(a.so)}</td>
                                    <td>
                                        <span className={`ca-pill ${a.stopout ? 'off' : 'warn'}`}>
                                            {a.stopout ? 'stop out' : 'margin call'}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                            {!error && rows.length === 0 && (
                                <tr><td colSpan={9} className="ca-empty"><i className="codicon codicon-check" /> No margin calls — all accounts above thresholds</td></tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
