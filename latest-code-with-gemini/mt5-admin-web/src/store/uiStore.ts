import { create } from 'zustand';

/**
 * Workbench sections — the Activity Bar switches between complete
 * navigation domains inside ONE application (operator spec):
 *   admin   = MT5 Administrator (existing tree & panels)
 *   manager = MT5 Manager (own tree; Manager API session later)
 *   clients = client portal/backoffice section (planned)
 *   server  = server/cluster section (planned)
 */
export type WorkbenchSection = 'admin' | 'manager' | 'clients' | 'server';

export interface UiState {
    section: WorkbenchSection;
    setSection: (s: WorkbenchSection) => void;
}

export const useUiStore = create<UiState>()((set) => ({
    section: 'admin',
    setSection: (section) => set({ section }),
}));
