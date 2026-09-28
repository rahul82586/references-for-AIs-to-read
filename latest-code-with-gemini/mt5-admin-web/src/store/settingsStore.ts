import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/**
 * Connection settings — the only place backend coordinates live.
 * Pages and shell never read these directly; the API facade picks the
 * transport based on this store at call time.
 */
export type ApiMode = 'mock' | 'live';

export interface SettingsState {
    apiMode: ApiMode;
    /** Base URL of the broker platform API. In dev use '/backend' (Vite proxy). */
    baseUrl: string;
    /** Value sent as X-Admin-API-Key on live admin calls. Never persisted to git. */
    adminKey: string;
    setApiMode: (mode: ApiMode) => void;
    setBaseUrl: (url: string) => void;
    setAdminKey: (key: string) => void;
}

export const useSettingsStore = create<SettingsState>()(
    persist(
        (set) => ({
            apiMode: 'mock',
            baseUrl: '/backend',
            adminKey: '',
            setApiMode: (apiMode) => set({ apiMode }),
            setBaseUrl: (baseUrl) => set({ baseUrl }),
            setAdminKey: (adminKey) => set({ adminKey }),
        }),
        { name: 'mt5-admin-settings' }
    )
);

export function getSettings(): Pick<SettingsState, 'apiMode' | 'baseUrl' | 'adminKey'> {
    const { apiMode, baseUrl, adminKey } = useSettingsStore.getState();
    return { apiMode, baseUrl, adminKey };
}
