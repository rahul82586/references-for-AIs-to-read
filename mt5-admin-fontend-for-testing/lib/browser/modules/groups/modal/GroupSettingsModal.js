"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.GroupSettingsModal = void 0;
const React = require("react");
const GroupDraftContext_1 = require("./GroupDraftContext");
const CommonTab_1 = require("./tabs/CommonTab");
const GatewayTab_1 = require("./tabs/GatewayTab");
const CompanyTab_1 = require("./tabs/CompanyTab");
const NewsMailTab_1 = require("./tabs/NewsMailTab");
const PermissionsTab_1 = require("./tabs/PermissionsTab");
const MarginTab_1 = require("./tabs/MarginTab");
const SymbolsTab_1 = require("./tabs/SymbolsTab");
const CommissionsTab_1 = require("./tabs/CommissionsTab");
const ReportsTab_1 = require("./tabs/ReportsTab");
const api_1 = require("../../api");
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
function GroupSettingsModal({ groupName, initialName = '', onClose, onSaved }) {
    const [draft, setDraft] = React.useState(GroupDraftContext_1.DEFAULT_DRAFT);
    const [activeTab, setActiveTab] = React.useState('common');
    const [errors, setErrors] = React.useState({});
    const [loading, setLoading] = React.useState(false);
    const [saveError, setSaveError] = React.useState(null);
    const isEditing = !!groupName;
    // Load existing group details on edit mode
    React.useEffect(() => {
        if (groupName) {
            setLoading(true);
            api_1.API.getGroupDetail(groupName)
                .then(data => {
                let parsedSettings = {};
                if (data.settings_json) {
                    try {
                        parsedSettings = JSON.parse(data.settings_json);
                    }
                    catch (e) {
                        console.error('Failed to parse settings JSON block', e);
                    }
                }
                setDraft({
                    ...GroupDraftContext_1.DEFAULT_DRAFT,
                    name: data.name,
                    max_leverage: data.max_leverage,
                    margin_call: data.margin_call,
                    margin_stop_out: data.margin_stop_out,
                    spread_override: data.spread_override,
                    ...parsedSettings
                });
            })
                .catch(err => {
                setSaveError(err.message || 'Failed to fetch group details.');
            })
                .finally(() => {
                setLoading(false);
            });
        }
        else if (initialName) {
            setDraft(prev => ({
                ...prev,
                name: initialName
            }));
        }
    }, [groupName, initialName]);
    // Validation check across all fields to place error badges on tab headings
    const validateAll = () => {
        const nextErrors = {};
        // 1. Common Tab
        if (!draft.name) {
            nextErrors.name = 'Group name is required';
        }
        else if (/[/:*?"<>|]/.test(draft.name)) {
            nextErrors.name = 'Group name cannot contain special characters like /, :, *, ?, ", <, >, |';
        }
        // 2. Company Tab
        if (!draft.company) {
            nextErrors.company = 'Company designation is required';
        }
        setErrors(nextErrors);
        return Object.keys(nextErrors).length === 0;
    };
    const tabHasErrors = (tabId) => {
        if (tabId === 'common' && errors.name)
            return true;
        if (tabId === 'company' && errors.company)
            return true;
        return false;
    };
    const handleSave = async (e) => {
        e.preventDefault();
        setSaveError(null);
        if (!validateAll()) {
            setSaveError('Please correct validation errors on marked tabs before saving.');
            return;
        }
        setLoading(true);
        try {
            // Pack settings JSON string
            const settingsData = { ...draft };
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
                await api_1.API.updateGroup(groupName, payload);
            }
            else {
                await api_1.API.createGroup(payload);
            }
            onSaved();
            onClose();
        }
        catch (err) {
            setSaveError(err.message || 'Failed to save group details.');
        }
        finally {
            setLoading(false);
        }
    };
    const renderActiveTabContent = () => {
        switch (activeTab) {
            case 'common': return React.createElement(CommonTab_1.CommonTab, null);
            case 'gateway': return React.createElement(GatewayTab_1.GatewayTab, null);
            case 'company': return React.createElement(CompanyTab_1.CompanyTab, null);
            case 'newsMail': return React.createElement(NewsMailTab_1.NewsMailTab, null);
            case 'permissions': return React.createElement(PermissionsTab_1.PermissionsTab, null);
            case 'margin': return React.createElement(MarginTab_1.MarginTab, null);
            case 'symbols': return React.createElement(SymbolsTab_1.SymbolsTab, null);
            case 'commissions': return React.createElement(CommissionsTab_1.CommissionsTab, null);
            case 'reports': return React.createElement(ReportsTab_1.ReportsTab, null);
            default: return React.createElement(CommonTab_1.CommonTab, null);
        }
    };
    return (React.createElement(GroupDraftContext_1.GroupDraftContext.Provider, { value: { draft, setDraft, errors, setErrors, isEditing } },
        React.createElement("div", { className: "adm-modal-overlay", onClick: onClose },
            React.createElement("div", { className: "adm-modal", style: { width: 750, height: '65vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }, onClick: e => e.stopPropagation() },
                React.createElement("div", { className: "adm-modal-header" },
                    React.createElement("h2", null,
                        React.createElement("i", { className: "codicon codicon-organization", style: { marginRight: 8, color: '#3498db' } }),
                        isEditing ? `Group Settings — ${groupName}` : 'Add New Trading Group'),
                    React.createElement("button", { type: "button", className: "adm-modal-close", onClick: onClose }, "\u00D7")),
                React.createElement("div", { className: "adm-tabs", style: { padding: '0 16px', borderBottom: '1px solid var(--theia-border)' } }, TABS.map(t => {
                    const err = tabHasErrors(t.id);
                    return (React.createElement("button", { key: t.id, type: "button", className: `adm-tab ${activeTab === t.id ? 'active' : ''} ${err ? 'tab-error' : ''}`, onClick: () => setActiveTab(t.id), style: { position: 'relative' } },
                        t.label,
                        err && React.createElement("span", { className: "adm-tab-error-dot" })));
                })),
                React.createElement("div", { className: "adm-modal-body", style: { flex: 1, overflow: 'hidden', padding: '12px 16px', display: 'flex', flexDirection: 'column' } },
                    loading && (React.createElement("div", { style: { position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.2)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 10 } },
                        React.createElement("span", null, "Loading details..."))),
                    saveError && (React.createElement("div", { className: "adm-hint", style: { background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)', margin: '0 0 16px 0' } },
                        React.createElement("i", { className: "codicon codicon-error" }),
                        " ",
                        saveError)),
                    renderActiveTabContent()),
                React.createElement("div", { className: "adm-modal-footer", style: { borderTop: '1px solid var(--theia-border)' } },
                    React.createElement("button", { type: "button", className: "adm-btn adm-btn-primary", onClick: handleSave, disabled: loading }, "OK"),
                    React.createElement("button", { type: "button", className: "adm-btn", onClick: onClose, disabled: loading }, "Cancel"))))));
}
exports.GroupSettingsModal = GroupSettingsModal;
//# sourceMappingURL=GroupSettingsModal.js.map