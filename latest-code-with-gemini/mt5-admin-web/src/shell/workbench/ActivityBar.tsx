import * as React from 'react';

interface ActivityBarProps {
    sidebarVisible: boolean;
    onToggleSidebar: () => void;
    onOpenSettings: () => void;
}

/**
 * VS Code-style activity bar. F0 ships two views (MT5 tree, settings);
 * later milestones can add Search, Reports, etc. as sidebar view switches.
 */
export function ActivityBar({ sidebarVisible, onToggleSidebar, onOpenSettings }: ActivityBarProps): React.ReactElement {
    return (
        <div className="wb-activitybar">
            <button
                className={`wb-activity-item${sidebarVisible ? ' active' : ''}`}
                onClick={onToggleSidebar}
                title="MT5 Administrator (Ctrl+B toggles sidebar)"
            >
                <i className="codicon codicon-server-environment" />
            </button>
            <div className="wb-activity-spacer" />
            <button className="wb-activity-item" onClick={onOpenSettings} title="Connection Settings">
                <i className="codicon codicon-settings-gear" />
            </button>
        </div>
    );
}
