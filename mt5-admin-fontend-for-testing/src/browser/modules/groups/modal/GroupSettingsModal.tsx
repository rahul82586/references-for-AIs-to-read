import * as React from 'react';
import { GroupDraft, DEFAULT_DRAFT, GroupDraftContext } from './GroupDraftContext';
import { CommonTab } from './tabs/CommonTab';
import { GatewayTab } from './tabs/GatewayTab';
import { CompanyTab } from './tabs/CompanyTab';
import { NewsMailTab } from './tabs/NewsMailTab';
import { PermissionsTab } from './tabs/PermissionsTab';
import { MarginTab } from './tabs/MarginTab';
import { SymbolsTab } from './tabs/SymbolsTab';
import { CommissionsTab } from './tabs/CommissionsTab';
import { ReportsTab } from './tabs/ReportsTab';
import { API } from '../../api';

interface GroupSettingsModalProps {
    groupName: string | null; // null if adding new group
    initialName?: string;
    onClose: () => void;
    onSaved: () => void;
}

const TABS = [
    { id: 'common', label: 'Common' },
    { id: 'gateway', label: 'Gateway' },
    { id: 'company', label: 'Company' },
    { id: 'newsMail', label: 'News & Mail' },
    { id: 'permissions', label: 'Permissions' },
    { id: 'margin', label: 'Margin' },
    { id: 'symbols', label: 'Symbols' },
    { id: 'commissions', label: 'Commissions' },
    { id: 'reports', label: 'Reports' }
];

export function GroupSettingsModal({ groupName, initialName = '', onClose, onSaved }: GroupSettingsModalProps): React.ReactElement {
    const [draft, setDraft] = React.useState<GroupDraft>(DEFAULT_DRAFT);
    const [activeTab, setActiveTab] = React.useState('common');
    const [errors, setErrors] = React.useState<Record<string, string>>({});
    const [loading, setLoading] = React.useState(false);
    const [saveError, setSaveError] = React.useState<string | null>(null);

    const isEditing = !!groupName;

    // Load existing group details on edit mode
    React.useEffect(() => {
        if (groupName) {
            setLoading(true);
            API.getGroupDetail(groupName)
                .then(data => {
                    let parsedSettings: Partial<GroupDraft> = {};
                    if (data.settings_json) {
                        try {
                            parsedSettings = JSON.parse(data.settings_json);
                        } catch (e) {
                            console.error('Failed to parse settings JSON block', e);
                        }
                    }
                    
                    setDraft({
                        ...DEFAULT_DRAFT,
                        name: data.name,
                        max_leverage: data.max_leverage,
                        margin_call: data.margin_call,
                        margin_stop_out: data.margin_stop_out,
                        spread_override: data.spread_override,
                        ...parsedSettings
                    } as any);
                })
                .catch(err => {
                    setSaveError(err.message || 'Failed to fetch group details.');
                })
                .finally(() => {
                    setLoading(false);
                });
        } else if (initialName) {
            setDraft(prev => ({
                ...prev,
                name: initialName
            }));
        }
    }, [groupName, initialName]);

    // Validation check across all fields to place error badges on tab headings
    const validateAll = (): boolean => {
        const nextErrors: Record<string, string> = {};
        
        // 1. Common Tab
        if (!draft.name) {
            nextErrors.name = 'Group name is required';
        } else if (/[/:*?"<>|]/.test(draft.name)) {
            nextErrors.name = 'Group name cannot contain special characters like /, :, *, ?, ", <, >, |';
        }

        // 2. Company Tab
        if (!draft.company) {
            nextErrors.company = 'Company designation is required';
        }

        setErrors(nextErrors);
        return Object.keys(nextErrors).length === 0;
    };

    const tabHasErrors = (tabId: string): boolean => {
        if (tabId === 'common' && errors.name) return true;
        if (tabId === 'company' && errors.company) return true;
        return false;
    };

    const handleSave = async (e: React.FormEvent) => {
        e.preventDefault();
        setSaveError(null);

        if (!validateAll()) {
            setSaveError('Please correct validation errors on marked tabs before saving.');
            return;
        }

        setLoading(true);
        try {
            // Pack settings JSON string
            const settingsData = { ...draft } as any;
            // Avoid duplicate name/leverages in settings JSON block to keep DB cleaner
            delete settingsData.name;
            delete settingsData.max_leverage;
            delete settingsData.margin_call;
            delete settingsData.margin_stop_out;
            delete settingsData.spread_override;

            const payload = {
                name: draft.name,
                max_leverage: draft.max_leverage,
                margin_call: draft.margin_call,
                margin_stop_out: draft.margin_stop_out,
                spread_override: draft.spread_override,
                settings_json: JSON.stringify(settingsData)
            };

            if (isEditing) {
                await API.updateGroup(groupName!, payload);
            } else {
                await API.createGroup(payload);
            }

            onSaved();
            onClose();
        } catch (err: any) {
            setSaveError(err.message || 'Failed to save group details.');
        } finally {
            setLoading(false);
        }
    };

    const renderActiveTabContent = () => {
        switch (activeTab) {
            case 'common': return <CommonTab />;
            case 'gateway': return <GatewayTab />;
            case 'company': return <CompanyTab />;
            case 'newsMail': return <NewsMailTab />;
            case 'permissions': return <PermissionsTab />;
            case 'margin': return <MarginTab />;
            case 'symbols': return <SymbolsTab />;
            case 'commissions': return <CommissionsTab />;
            case 'reports': return <ReportsTab />;
            default: return <CommonTab />;
        }
    };

    return (
        <GroupDraftContext.Provider value={{ draft, setDraft, errors, setErrors, isEditing }}>
            <div className="adm-modal-overlay" onClick={onClose}>
                <div className="adm-modal" style={{ width: 750, height: '65vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }} onClick={e => e.stopPropagation()}>
                    <div className="adm-modal-header">
                        <h2>
                            <i className="codicon codicon-organization" style={{ marginRight: 8, color: '#3498db' }} />
                            {isEditing ? `Group Settings — ${groupName}` : 'Add New Trading Group'}
                        </h2>
                        <button type="button" className="adm-modal-close" onClick={onClose}>×</button>
                    </div>

                    <div className="adm-tabs" style={{ padding: '0 16px', borderBottom: '1px solid var(--theia-border)' }}>
                        {TABS.map(t => {
                            const err = tabHasErrors(t.id);
                            return (
                                <button 
                                    key={t.id} 
                                    type="button"
                                    className={`adm-tab ${activeTab === t.id ? 'active' : ''} ${err ? 'tab-error' : ''}`}
                                    onClick={() => setActiveTab(t.id)}
                                    style={{ position: 'relative' }}
                                >
                                    {t.label}
                                    {err && <span className="adm-tab-error-dot" />}
                                </button>
                            );
                        })}
                    </div>

                    <div className="adm-modal-body" style={{ flex: 1, overflow: 'hidden', padding: '12px 16px', display: 'flex', flexDirection: 'column' }}>
                        {loading && (
                            <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.2)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 10 }}>
                                <span>Loading details...</span>
                            </div>
                        )}
                        
                        {saveError && (
                            <div className="adm-hint" style={{ background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)', margin: '0 0 16px 0' }}>
                                <i className="codicon codicon-error" /> {saveError}
                            </div>
                        )}

                        {renderActiveTabContent()}
                    </div>

                    <div className="adm-modal-footer" style={{ borderTop: '1px solid var(--theia-border)' }}>
                        <button type="button" className="adm-btn adm-btn-primary" onClick={handleSave} disabled={loading}>
                            OK
                        </button>
                        <button type="button" className="adm-btn" onClick={onClose} disabled={loading}>
                            Cancel
                        </button>
                    </div>
                </div>
            </div>
        </GroupDraftContext.Provider>
    );
}
