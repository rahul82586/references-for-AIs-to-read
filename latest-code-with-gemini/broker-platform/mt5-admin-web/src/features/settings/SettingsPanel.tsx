import * as React from 'react';
import { API, isBackendGap } from '../../services/api';
import { useSettingsStore } from '../../store/settingsStore';

interface Props {
    close(): void;
}

/**
 * Connection Settings — the single place backend coordinates are configured.
 * Nothing in the codebase hardcodes a backend URL or API key anymore.
 */
export function SettingsPanel(_props: Props): React.ReactElement {
    const { apiMode, baseUrl, adminKey, setApiMode, setBaseUrl, setAdminKey } = useSettingsStore();

    const [mode, setMode] = React.useState(apiMode);
    const [url, setUrl] = React.useState(baseUrl);
    const [key, setKey] = React.useState(adminKey);
    const [test, setTest] = React.useState<{ ok: boolean; text: string } | null>(null);
    const [testing, setTesting] = React.useState(false);

    const save = () => {
        setApiMode(mode);
        setBaseUrl(url.trim() || '/backend');
        setAdminKey(key.trim());
        setTest({ ok: true, text: 'Saved. All panels pick this up on their next request.' });
    };

    const runTest = async () => {
        save();
        setTesting(true);
        setTest(null);
        try {
            const s = await API.getStatus();
            setTest({ ok: true, text: `Connected: ${JSON.stringify(s).slice(0, 200)}` });
        } catch (e: any) {
            const msg = String(e?.message ?? e);
            setTest({ ok: false, text: isBackendGap(e) ? msg : `Failed: ${msg}` });
        } finally {
            setTesting(false);
        }
    };

    return (
        <div className="wb-settings">
            <h2>
                <i className="codicon codicon-settings-gear" style={{ marginRight: 8 }} />
                Connection Settings
            </h2>
            <div className="wb-settings-hint">
                The frontend holds no logic — every screen is driven by the API configured here.
            </div>

            <div className="wb-settings-section">
                <div className="wb-settings-row">
                    <label>API mode</label>
                    <select value={mode} onChange={(e) => setMode(e.target.value as any)}>
                        <option value="mock">Mock — in-memory fixtures, no backend needed</option>
                        <option value="live">Live — real broker platform API</option>
                    </select>
                    <div className="wb-settings-hint">
                        Mock is the executable spec of the ideal admin API; anything Live cannot
                        serve yet surfaces as a “backend gap” error instead of fake data.
                    </div>
                </div>

                <div className="wb-settings-row">
                    <label>Backend base URL</label>
                    <input
                        type="text"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        placeholder="/backend (dev proxy) or http://localhost:8000"
                    />
                    <div className="wb-settings-hint">
                        In dev, <code>/backend</code> proxies to http://localhost:8000 (see
                        vite.config.ts — override target with VITE_PROXY_TARGET). The transport
                        appends <code>/api/v1</code> to every call.
                    </div>
                </div>

                <div className="wb-settings-row">
                    <label>Admin API key (X-Admin-API-Key)</label>
                    <input
                        type="password"
                        value={key}
                        onChange={(e) => setKey(e.target.value)}
                        placeholder="must match the backend's ADMIN_API_KEY env var"
                    />
                    <div className="wb-settings-hint">
                        Stored only in this browser's localStorage. The backend is fail-closed:
                        unset key ⇒ 503, wrong key ⇒ 403.
                    </div>
                </div>

                <div className="wb-settings-actions">
                    <button className="wb-btn" onClick={save}>
                        Save
                    </button>
                    <button className="wb-btn secondary" onClick={() => void runTest()} disabled={testing}>
                        {testing ? 'Testing…' : 'Save & Test Connection'}
                    </button>
                </div>

                {test && (
                    <div className={`wb-settings-test-result ${test.ok ? 'ok' : 'err'}`}>
                        <i className={`codicon codicon-${test.ok ? 'pass' : 'error'}`} style={{ marginRight: 6 }} />
                        {test.text}
                    </div>
                )}
            </div>

            <div className="wb-settings-section">
                <div className="wb-settings-hint">
                    Keyboard: <b>Ctrl+Shift+P</b> command palette · <b>Ctrl+B</b> toggle sidebar ·
                    drag panel tabs to split/dock the workbench (layout is saved automatically).
                </div>
            </div>
        </div>
    );
}
