import * as React from 'react';
import { leverage } from '../../shared/format';

interface Props {
    settings: any;
    onError: (msg: string, gap?: boolean) => void;
    onInfo: (msg: string) => void;
}

/**
 * Account Allocation Settings (doc §Account-Allocation-Settings):
 * general URLs on top, per-country group rules, agreements, verification.
 * Changes save only via Apply (doc semantics) — a backend gap in live mode.
 */
export function AllocationsPanel({ settings, onError, onInfo }: Props): React.ReactElement {
    const [draft, setDraft] = React.useState<any>(settings);

    React.useEffect(() => setDraft(settings), [settings]);

    if (!draft) return <div className="ca-empty">Loading allocation settings…</div>;

    return (
        <div className="ca-alloc">
            <div className="ca-box">
                <div className="ca-box-title"><i className="codicon codicon-globe" /> General</div>
                <div className="ca-modal-grid">
                    <div className="wb-settings-row" style={{ gridColumn: '1 / -1' }}>
                        <label>Demo account allocation URL</label>
                        <input
                            className="adm-input"
                            value={draft.demo_url ?? ''}
                            onChange={(e) => setDraft({ ...draft, demo_url: e.target.value })}
                            placeholder="https://your-site.example/open-demo — when set, all other allocation settings are inactive"
                        />
                    </div>
                    <div className="wb-settings-row">
                        <label>Deposit URL</label>
                        <input className="adm-input" value={draft.deposit_url ?? ''} onChange={(e) => setDraft({ ...draft, deposit_url: e.target.value })} />
                    </div>
                    <div className="wb-settings-row">
                        <label>Withdrawal URL</label>
                        <input className="adm-input" value={draft.withdrawal_url ?? ''} onChange={(e) => setDraft({ ...draft, withdrawal_url: e.target.value })} />
                    </div>
                </div>
            </div>

            <div className="ca-box">
                <div className="ca-box-title"><i className="codicon codicon-organization" /> Group allocation rules</div>
                <table className="adm-table ca-table ca-mini">
                    <thead>
                        <tr><th>Kind</th><th>Group</th><th>Countries</th><th className="num">Leverage</th><th>Extended registration form</th></tr>
                    </thead>
                    <tbody>
                        {(draft.rules ?? []).map((r: any) => (
                            <tr key={r.id}>
                                <td><span className={`ca-pill ${r.kind === 'real' ? 'ok' : r.kind === 'demo' ? 'info' : 'warn'}`}>{r.kind}</span></td>
                                <td><code className="adm-code ca-group">{r.group}</code></td>
                                <td className="ca-dim">{r.countries}</td>
                                <td className="num">{leverage(r.leverage)}</td>
                                <td>{r.extended_form ? <i className="codicon codicon-check" style={{ color: 'var(--theia-successForeground)' }} /> : <span className="ca-dim">—</span>}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <div className="ca-box">
                <div className="ca-box-title"><i className="codicon codicon-file" /> Agreements (accepted on account opening)</div>
                <div className="ca-checks ca-checks-col">
                    {(draft.agreements ?? []).map((a: any) => (
                        <label className="ca-check" key={a.id}>
                            <input type="checkbox" readOnly disabled checked={a.required} />
                            {a.name} {a.required ? <span className="ca-dim">(required)</span> : <span className="ca-dim">(optional)</span>}
                        </label>
                    ))}
                </div>
            </div>

            <div className="ca-box">
                <div className="ca-box-title"><i className="codicon codicon-verified" /> Phone & Email verification</div>
                <div className="ca-checks">
                    <label className="ca-check"><input type="checkbox" readOnly disabled checked={draft.verification?.phone} /> Phone verification</label>
                    <label className="ca-check"><input type="checkbox" readOnly disabled checked={draft.verification?.email} /> Email verification</label>
                    <span className="ca-dim" style={{ fontSize: 11 }}>provider: {draft.verification?.provider ?? '—'}</span>
                </div>
            </div>

            <div className="ca-alloc-actions">
                <button
                    className="wb-btn"
                    onClick={() => onError('Backend gap: allocation settings have no write endpoint yet (mock keeps them in memory).', true)}
                >
                    <i className="codicon codicon-check" /> Apply Changes
                </button>
                <button className="wb-btn secondary" onClick={() => { setDraft(settings); onInfo('Allocation settings reverted.'); }}>
                    Revert
                </button>
            </div>
        </div>
    );
}
