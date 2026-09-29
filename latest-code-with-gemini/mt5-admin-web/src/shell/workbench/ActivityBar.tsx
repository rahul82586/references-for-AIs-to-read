import * as React from 'react';
import { useUiStore, WorkbenchSection } from '../../store/uiStore';

interface ActivityBarProps {
    sidebarVisible: boolean;
    onToggleSidebar: () => void;
    onOpenSettings: () => void;
}

interface SectionDef {
    id: WorkbenchSection;
    icon: string;
    title: string;
    planned?: boolean;
}

const SECTIONS: SectionDef[] = [
    { id: 'admin', icon: 'server-environment', title: 'MT5 Administrator' },
    { id: 'manager', icon: 'shield', title: 'Manager — Manager API session (tree ready, panels next milestone)' },
    { id: 'clients', icon: 'organization', title: 'Clients (planned section)', planned: true },
    { id: 'server', icon: 'server', title: 'Server (planned section)', planned: true },
];

/**
 * Workbench Activity Bar — one button per navigation domain inside the SAME
 * application (operator spec): MT5 Administrator · Manager · Clients · Server.
 * Selecting a section swaps the sidebar tree; the editor area (dockview) is
 * shared, so admin and manager panels coexist as tabs.
 */
export function ActivityBar({ sidebarVisible, onToggleSidebar, onOpenSettings }: ActivityBarProps): React.ReactElement {
    const { section, setSection } = useUiStore();

    const click = (def: SectionDef) => {
        if (def.id === section) {
            onToggleSidebar();
            return;
        }
        setSection(def.id);
        if (!sidebarVisible) onToggleSidebar();
    };

    return (
        <div className="wb-activitybar">
            {SECTIONS.map((def) => (
                <button
                    key={def.id}
                    className={[
                        'wb-activity-item',
                        section === def.id && sidebarVisible ? ' active' : '',
                        def.planned ? ' planned' : '',
                    ].join('')}
                    onClick={() => click(def)}
                    title={def.planned ? `${def.title} — lands in a later milestone` : `${def.title} (click again to toggle sidebar)`}
                >
                    <i className={`codicon codicon-${def.icon}`} />
                </button>
            ))}
            <div className="wb-activity-spacer" />
            <button className="wb-activity-item" onClick={onOpenSettings} title="Connection Settings">
                <i className="codicon codicon-settings-gear" />
            </button>
        </div>
    );
}
