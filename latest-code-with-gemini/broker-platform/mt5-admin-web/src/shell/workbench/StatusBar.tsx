import * as React from 'react';
import { useSettingsStore } from '../../store/settingsStore';
import { API } from '../../services/api';

interface StatusBarProps {
    onOpenSettings: () => void;
}

type Health = 'unknown' | 'ok' | 'err';

/**
 * VS Code-style status bar: connection mode, backend health, coordinates.
 * Health polls API.getStatus(); in mock mode it's trivially ok, in live mode
 * it reflects the real /api/v1/admin/status of the broker platform.
 */
export function StatusBar({ onOpenSettings }: StatusBarProps): React.ReactElement {
    const { apiMode, baseUrl } = useSettingsStore();
    const [health, setHealth] = React.useState<Health>('unknown');
    const [detail, setDetail] = React.useState('');

    React.useEffect(() => {
        let cancelled = false;
        const check = async () => {
            try {
                const s = await API.getStatus();
                if (cancelled) return;
                setHealth('ok');
                setDetail(s?.version ?? s?.status ?? 'ok');
            } catch (e: any) {
                if (cancelled) return;
                setHealth('err');
                setDetail(String(e?.message ?? e).slice(0, 90));
            }
        };
        void check();
        const iv = window.setInterval(check, 15000);
        return () => {
            cancelled = true;
            window.clearInterval(iv);
        };
    }, [apiMode, baseUrl]);

    return (
        <div className="wb-statusbar">
            <button className="wb-status-item" onClick={onOpenSettings} title="Open connection settings">
                <i className={`codicon codicon-${apiMode === 'live' ? 'cloud' : 'beaker'}`} />
                {apiMode === 'live' ? 'LIVE' : 'MOCK'}
            </button>
            <span className="wb-status-item" title={detail || 'backend status'}>
                <span className={`wb-status-dot ${health === 'ok' ? 'ok' : health === 'err' ? 'err' : 'warn'}`} />
                {apiMode === 'live' ? baseUrl : 'in-memory backend'}
                {health === 'err' && apiMode === 'live' ? ' — unreachable' : ''}
            </span>
            <div className="wb-status-spacer" />
            <span className="wb-status-item">MT5 Administrator</span>
        </div>
    );
}
