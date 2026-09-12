"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.GatewaysPage = void 0;
const React = require("react");
const api_1 = require("../api");
const STATUS_COLOR = {
    connected: 'var(--theia-successForeground)',
    disconnected: 'var(--theia-descriptionForeground)',
    error: 'var(--theia-errorForeground)',
};
const TYPE_COLOR = {
    FIX: '#3498db', MT5: '#9b59b6', REST: '#27ae60', Custom: '#f39c12'
};
function GatewaysPage() {
    const [gateways, setGateways] = React.useState([]);
    const [availableGroups, setAvailableGroups] = React.useState([]);
    const [selected, setSelected] = React.useState(null);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState(null);
    // Modal state
    const [showModal, setShowModal] = React.useState(false);
    const [modalMode, setModalMode] = React.useState('create');
    const [activeTab, setActiveTab] = React.useState('general');
    const [gatewayForm, setGatewayForm] = React.useState({
        id: null,
        name: '',
        type: 'FIX',
        host: '',
        port: '',
        username: '',
        api_key: '',
        is_active: true
    });
    // Groups state matching standard MT5 tab settings
    const [gatewayGroups, setGatewayGroups] = React.useState(['*']);
    const [allowImportBalances, setAllowImportBalances] = React.useState(false);
    const [selectedGroupIdx, setSelectedGroupIdx] = React.useState(null);
    const [editingGroupIdx, setEditingGroupIdx] = React.useState(null);
    const [editingGroupVal, setEditingGroupVal] = React.useState('');
    // Translations state
    const [translations, setTranslations] = React.useState([]);
    const [newRule, setNewRule] = React.useState({
        symbol: '',
        source: '',
        bid_adj: 0,
        ask_adj: 0
    });
    const [modalError, setModalError] = React.useState(null);
    const loadGateways = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await api_1.API.getGateways();
            // Filter out price feeders (they will be displayed on DataFeedsPage.tsx)
            const filtered = data.filter((g) => !g.type.startsWith('Feeder_'));
            setGateways(filtered);
        }
        catch (err) {
            setError(err.message || 'Failed to load gateways.');
        }
        finally {
            setLoading(false);
        }
    };
    const loadDbGroups = async () => {
        try {
            const data = await api_1.API.getGroups();
            setAvailableGroups(data);
        }
        catch (e) {
            console.error('Failed to load groups for gateway settings dropdown:', e);
        }
    };
    React.useEffect(() => {
        loadGateways();
        loadDbGroups();
    }, []);
    const openCreateModal = () => {
        setModalMode('create');
        setActiveTab('general');
        setGatewayForm({
            id: null,
            name: '',
            type: 'FIX',
            host: '',
            port: '',
            username: '',
            api_key: '',
            is_active: true
        });
        setTranslations([]);
        setGatewayGroups(['*']);
        setAllowImportBalances(false);
        setSelectedGroupIdx(null);
        setEditingGroupIdx(null);
        setEditingGroupVal('');
        setModalError(null);
        setShowModal(true);
    };
    const openEditModal = (g) => {
        setModalMode('edit');
        setActiveTab('general');
        setGatewayForm({
            id: g.id,
            name: g.name,
            type: g.type,
            host: g.host || '',
            port: g.port ? String(g.port) : '',
            username: g.username || '',
            api_key: g.api_key || '',
            is_active: g.is_active === 1
        });
        let rules = [];
        let groups = ['*'];
        let allow_import = false;
        if (g.settings_json) {
            try {
                const parsed = JSON.parse(g.settings_json);
                rules = parsed.translations || [];
                if (parsed.groups) {
                    groups = parsed.groups;
                }
                if (parsed.allow_import_balances !== undefined) {
                    allow_import = parsed.allow_import_balances;
                }
            }
            catch (err) {
                // ignore
            }
        }
        setTranslations(rules);
        setGatewayGroups(groups);
        setAllowImportBalances(allow_import);
        setSelectedGroupIdx(null);
        setEditingGroupIdx(null);
        setEditingGroupVal('');
        setModalError(null);
        setShowModal(true);
    };
    const handleAddRule = () => {
        if (!newRule.symbol.trim() || !newRule.source.trim()) {
            alert('Symbol and Source pattern are required.');
            return;
        }
        setTranslations([...translations, {
                symbol: newRule.symbol.trim(),
                source: newRule.source.trim(),
                bid_adj: Number(newRule.bid_adj) || 0,
                ask_adj: Number(newRule.ask_adj) || 0
            }]);
        setNewRule({ symbol: '', source: '', bid_adj: 0, ask_adj: 0 });
    };
    const handleRemoveRule = (idx) => {
        setTranslations(translations.filter((_, i) => i !== idx));
    };
    const handleSubmit = async (e) => {
        e.preventDefault();
        setModalError(null);
        const payload = {
            name: gatewayForm.name,
            type: gatewayForm.type,
            host: gatewayForm.host || undefined,
            port: gatewayForm.port ? parseInt(gatewayForm.port) : undefined,
            username: gatewayForm.username || undefined,
            api_key: gatewayForm.api_key || undefined,
            is_active: gatewayForm.is_active,
            settings_json: JSON.stringify({
                translations,
                groups: gatewayGroups,
                allow_import_balances: allowImportBalances
            })
        };
        try {
            if (modalMode === 'create') {
                await api_1.API.createGateway(payload);
            }
            else {
                await api_1.API.updateGateway(gatewayForm.id, payload);
            }
            setShowModal(false);
            await loadGateways();
        }
        catch (err) {
            setModalError(err.message || 'Failed to save gateway.');
        }
    };
    const handleTestGateway = async () => {
        if (!selected)
            return;
        setError(null);
        try {
            const resp = await api_1.API.testGateway(selected);
            alert(`Gateway Connection Test: ${resp.message}`);
        }
        catch (err) {
            setError(err.message || 'Gateway test failed.');
        }
    };
    const selectedGateway = gateways.find(g => g.id === selected);
    return (React.createElement("div", { className: "adm-page" },
        React.createElement("div", { className: "adm-toolbar" },
            React.createElement("button", { className: "adm-btn adm-btn-primary", onClick: openCreateModal },
                React.createElement("i", { className: "codicon codicon-add" }),
                " Add Gateway"),
            React.createElement("button", { className: "adm-btn", disabled: !selected, onClick: () => selectedGateway && openEditModal(selectedGateway) },
                React.createElement("i", { className: "codicon codicon-edit" }),
                " Edit Gateway"),
            React.createElement("button", { className: "adm-btn", disabled: !selected, onClick: handleTestGateway },
                React.createElement("i", { className: "codicon codicon-beaker" }),
                " Test Connection"),
            React.createElement("button", { className: "adm-btn", onClick: loadGateways, title: "Reload data" },
                React.createElement("i", { className: "codicon codicon-refresh" }),
                " Refresh")),
        error && (React.createElement("div", { className: "adm-hint", style: { background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)' } },
            React.createElement("i", { className: "codicon codicon-error" }),
            " ",
            error)),
        React.createElement("div", { className: "adm-table-wrap" }, loading ? (React.createElement("div", { style: { padding: 20, textAlign: 'center', opacity: 0.7 } }, "Loading gateways...")) : gateways.length === 0 ? (React.createElement("div", { style: { padding: 20, textAlign: 'center', opacity: 0.7 } }, "No gateways configured. Add a gateway to route orders to external liquidity providers.")) : (React.createElement("table", { className: "adm-table" },
            React.createElement("thead", null,
                React.createElement("tr", null,
                    React.createElement("th", null),
                    React.createElement("th", null, "Name"),
                    React.createElement("th", null, "Type"),
                    React.createElement("th", null, "Host / Server"),
                    React.createElement("th", null, "Port"),
                    React.createElement("th", null, "Username / Account"),
                    React.createElement("th", null, "Status"),
                    React.createElement("th", null, "Created At"))),
            React.createElement("tbody", null, gateways.map(g => {
                const statusStr = g.is_active ? 'connected' : 'disconnected';
                return (React.createElement("tr", { key: g.id, className: selected === g.id ? 'selected' : '', onClick: () => setSelected(g.id), onDoubleClick: () => openEditModal(g) },
                    React.createElement("td", null,
                        React.createElement("span", { className: `adm-status-dot ${g.is_active ? 'online' : 'offline'}` })),
                    React.createElement("td", null,
                        React.createElement("strong", null, g.name)),
                    React.createElement("td", null,
                        React.createElement("span", { className: "adm-tag", style: { color: TYPE_COLOR[g.type] || '#ccc', border: `1px solid ${(TYPE_COLOR[g.type] || '#ccc')}55` } }, g.type)),
                    React.createElement("td", null,
                        React.createElement("code", { className: "adm-code" }, g.host || '—')),
                    React.createElement("td", null, g.port || '—'),
                    React.createElement("td", null, g.username || '—'),
                    React.createElement("td", { style: { color: STATUS_COLOR[statusStr] } }, statusStr),
                    React.createElement("td", null, g.created_at || '—')));
            }))))),
        showModal && (React.createElement("div", { className: "adm-modal-overlay", onClick: () => setShowModal(false) },
            React.createElement("form", { className: "adm-modal", style: { width: 750, height: '65vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }, onClick: e => e.stopPropagation(), onSubmit: handleSubmit },
                React.createElement("div", { className: "adm-modal-header" },
                    React.createElement("h2", null, modalMode === 'create' ? 'Add Liquidity Gateway' : `Edit Gateway: ${gatewayForm.name}`),
                    React.createElement("button", { type: "button", className: "adm-modal-close", onClick: () => setShowModal(false) }, "\u00D7")),
                React.createElement("div", { className: "adm-tabs", style: { padding: '0 16px', borderBottom: '1px solid var(--theia-border)', flexShrink: 0 } },
                    React.createElement("button", { type: "button", className: `adm-tab ${activeTab === 'general' ? 'active' : ''}`, onClick: () => setActiveTab('general') }, "Common"),
                    React.createElement("button", { type: "button", className: `adm-tab ${activeTab === 'groups' ? 'active' : ''}`, onClick: () => setActiveTab('groups') }, "Groups"),
                    React.createElement("button", { type: "button", className: `adm-tab ${activeTab === 'translations' ? 'active' : ''}`, onClick: () => setActiveTab('translations') }, "Translations")),
                React.createElement("div", { className: "adm-modal-body", style: { flex: 1, overflowY: 'auto', padding: 16 } },
                    modalError && (React.createElement("div", { className: "adm-hint", style: { background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)', margin: '0 0 12px 0' } },
                        React.createElement("i", { className: "codicon codicon-error" }),
                        " ",
                        modalError)),
                    activeTab === 'general' ? (React.createElement("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 } },
                        React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 12 } },
                            React.createElement("div", { className: "adm-form-row" },
                                React.createElement("label", null, "Gateway Name"),
                                React.createElement("input", { className: "adm-input", required: true, placeholder: "e.g. LP-Gateway-1", value: gatewayForm.name, onChange: e => setGatewayForm({ ...gatewayForm, name: e.target.value }) })),
                            React.createElement("div", { className: "adm-form-row" },
                                React.createElement("label", null, "Type"),
                                React.createElement("select", { className: "adm-select", value: gatewayForm.type, onChange: e => setGatewayForm({ ...gatewayForm, type: e.target.value }) },
                                    React.createElement("option", { value: "FIX" }, "FIX Protocol"),
                                    React.createElement("option", { value: "MT5" }, "MetaTrader 5 Bridge"),
                                    React.createElement("option", { value: "REST" }, "REST API Gateway"),
                                    React.createElement("option", { value: "Custom" }, "Custom Provider"))),
                            React.createElement("div", { className: "adm-form-row" },
                                React.createElement("label", null, "Host / Hostname"),
                                React.createElement("input", { className: "adm-input", placeholder: "e.g. localhost or lp.broker.com", value: gatewayForm.host, onChange: e => setGatewayForm({ ...gatewayForm, host: e.target.value }) })),
                            React.createElement("div", { className: "adm-form-row" },
                                React.createElement("label", null, "Port"),
                                React.createElement("input", { className: "adm-input", type: "number", placeholder: "e.g. 8003", value: gatewayForm.port, onChange: e => setGatewayForm({ ...gatewayForm, port: e.target.value }) }))),
                        React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 12 } },
                            React.createElement("div", { className: "adm-form-row" },
                                React.createElement("label", null, "Username / Account ID"),
                                React.createElement("input", { className: "adm-input", placeholder: "Login ID", value: gatewayForm.username, onChange: e => setGatewayForm({ ...gatewayForm, username: e.target.value }) })),
                            React.createElement("div", { className: "adm-form-row" },
                                React.createElement("label", null, "API Key / Password"),
                                React.createElement("input", { className: "adm-input", type: "password", placeholder: "Access key/token", value: gatewayForm.api_key, onChange: e => setGatewayForm({ ...gatewayForm, api_key: e.target.value }) })),
                            React.createElement("div", { className: "adm-form-row", style: { marginTop: 24, flexDirection: 'row', alignItems: 'center', gap: 8 } },
                                React.createElement("input", { type: "checkbox", id: "gw_active", checked: gatewayForm.is_active, onChange: e => setGatewayForm({ ...gatewayForm, is_active: e.target.checked }) }),
                                React.createElement("label", { htmlFor: "gw_active", style: { cursor: 'pointer', margin: 0 } }, "Enable Gateway Connection"))))) : activeTab === 'groups' ? (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 12 } },
                        React.createElement("div", { style: { fontSize: 11, color: 'var(--theia-descriptionForeground)', borderBottom: '1px solid var(--theia-border)', paddingBottom: 4 } }, "Please specify the client groups whose trade operations shall be processed by this gateway."),
                        React.createElement("div", { style: { display: 'flex', gap: 16, height: 260 } },
                            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 8, width: 80 } },
                                React.createElement("button", { type: "button", className: "adm-btn", onClick: () => {
                                        const nextIdx = gatewayGroups.length;
                                        setGatewayGroups([...gatewayGroups, 'new_group\\*']);
                                        setSelectedGroupIdx(nextIdx);
                                        setEditingGroupIdx(nextIdx);
                                        setEditingGroupVal('new_group\\*');
                                    } }, "Add"),
                                React.createElement("button", { type: "button", className: "adm-btn", disabled: selectedGroupIdx === null, onClick: () => {
                                        if (selectedGroupIdx !== null) {
                                            setEditingGroupIdx(selectedGroupIdx);
                                            setEditingGroupVal(gatewayGroups[selectedGroupIdx]);
                                        }
                                    } }, "Edit"),
                                React.createElement("button", { type: "button", className: "adm-btn adm-btn-danger", disabled: selectedGroupIdx === null, onClick: () => {
                                        if (selectedGroupIdx !== null) {
                                            const updated = gatewayGroups.filter((_, idx) => idx !== selectedGroupIdx);
                                            setGatewayGroups(updated);
                                            setSelectedGroupIdx(null);
                                            setEditingGroupIdx(null);
                                        }
                                    } }, "Delete")),
                            React.createElement("div", { style: {
                                    flex: 1,
                                    border: '1px solid var(--theia-border)',
                                    borderRadius: 4,
                                    background: 'var(--theia-input-background)',
                                    overflowY: 'auto',
                                    display: 'flex',
                                    flexDirection: 'column'
                                } },
                                gatewayGroups.map((gStr, idx) => {
                                    const isSelected = selectedGroupIdx === idx;
                                    const isEditing = editingGroupIdx === idx;
                                    if (isEditing) {
                                        return (React.createElement("div", { key: idx, style: { padding: '4px 8px', borderBottom: '1px solid var(--theia-border)', display: 'flex', gap: 8, alignItems: 'center' } },
                                            React.createElement("input", { className: "adm-input", style: { flex: 1, height: 20, fontSize: 11 }, value: editingGroupVal, autoFocus: true, onChange: e => setEditingGroupVal(e.target.value), placeholder: "e.g. real\\*", onKeyDown: e => {
                                                    if (e.key === 'Enter') {
                                                        const updated = [...gatewayGroups];
                                                        updated[idx] = editingGroupVal.trim() || '*';
                                                        setGatewayGroups(updated);
                                                        setEditingGroupIdx(null);
                                                    }
                                                    else if (e.key === 'Escape') {
                                                        setEditingGroupIdx(null);
                                                    }
                                                } }),
                                            React.createElement("select", { className: "adm-select", style: { width: 180, height: 20, fontSize: 11 }, value: "", onChange: e => {
                                                    const chosen = e.target.value;
                                                    if (chosen) {
                                                        setEditingGroupVal(chosen);
                                                        const updated = [...gatewayGroups];
                                                        updated[idx] = chosen;
                                                        setGatewayGroups(updated);
                                                        setEditingGroupIdx(null);
                                                    }
                                                } },
                                                React.createElement("option", { value: "" }, "-- Select group... --"),
                                                React.createElement("option", { value: "*" }, "* (All Groups)"),
                                                availableGroups.map(g => (React.createElement("option", { key: g.name, value: g.name }, g.name)))),
                                            React.createElement("button", { type: "button", className: "adm-btn adm-btn-primary", style: { height: 20, padding: '0 8px', fontSize: 10, minWidth: 40 }, onClick: () => {
                                                    const updated = [...gatewayGroups];
                                                    updated[idx] = editingGroupVal.trim() || '*';
                                                    setGatewayGroups(updated);
                                                    setEditingGroupIdx(null);
                                                } }, "Save")));
                                    }
                                    return (React.createElement("div", { key: idx, style: {
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: 8,
                                            padding: '6px 12px',
                                            cursor: 'pointer',
                                            fontSize: 11,
                                            borderBottom: '1px solid var(--theia-border)',
                                            background: isSelected ? 'var(--theia-list-activeSelectionBackground)' : 'transparent',
                                            color: isSelected ? 'var(--theia-list-activeSelectionForeground)' : 'inherit'
                                        }, onClick: () => setSelectedGroupIdx(idx), onDoubleClick: () => {
                                            setSelectedGroupIdx(idx);
                                            setEditingGroupIdx(idx);
                                            setEditingGroupVal(gStr);
                                        } },
                                        React.createElement("i", { className: "codicon codicon-organization", style: { color: isSelected ? 'inherit' : '#3498db' } }),
                                        React.createElement("strong", null, gStr)));
                                }),
                                React.createElement("div", { style: {
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: 8,
                                        padding: '6px 12px',
                                        cursor: 'pointer',
                                        fontSize: 11,
                                        color: 'var(--theia-successForeground)'
                                    }, onClick: () => {
                                        const nextIdx = gatewayGroups.length;
                                        setGatewayGroups([...gatewayGroups, '']);
                                        setSelectedGroupIdx(nextIdx);
                                        setEditingGroupIdx(nextIdx);
                                        setEditingGroupVal('');
                                    } },
                                    React.createElement("i", { className: "codicon codicon-add" }),
                                    React.createElement("span", null, "click to add...")))),
                        React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', fontSize: 11, marginTop: 4 } },
                            React.createElement("input", { type: "checkbox", checked: allowImportBalances, onChange: e => setAllowImportBalances(e.target.checked) }),
                            "Allow importing traders balances"))) : (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 12 } },
                        React.createElement("div", { style: { display: 'flex', gap: 8, alignItems: 'flex-end', background: 'var(--theia-editor-background)', padding: 10, border: '1px solid var(--theia-border)', borderRadius: 4 } },
                            React.createElement("div", { className: "adm-form-row", style: { flex: 2 } },
                                React.createElement("label", null, "Platform Symbol (Local)"),
                                React.createElement("input", { className: "adm-input", placeholder: "e.g. EURUSD or *", value: newRule.symbol, onChange: e => setNewRule({ ...newRule, symbol: e.target.value }) })),
                            React.createElement("div", { className: "adm-form-row", style: { flex: 2 } },
                                React.createElement("label", null, "Source Symbol (External)"),
                                React.createElement("input", { className: "adm-input", placeholder: "e.g. EURUSD.pro or *", value: newRule.source, onChange: e => setNewRule({ ...newRule, source: e.target.value }) })),
                            React.createElement("div", { className: "adm-form-row", style: { flex: 1 } },
                                React.createElement("label", null, "Bid Adj (Pts)"),
                                React.createElement("input", { className: "adm-input", type: "number", placeholder: "e.g. -2", value: newRule.bid_adj, onChange: e => setNewRule({ ...newRule, bid_adj: parseInt(e.target.value) || 0 }) })),
                            React.createElement("div", { className: "adm-form-row", style: { flex: 1 } },
                                React.createElement("label", null, "Ask Adj (Pts)"),
                                React.createElement("input", { className: "adm-input", type: "number", placeholder: "e.g. 2", value: newRule.ask_adj, onChange: e => setNewRule({ ...newRule, ask_adj: parseInt(e.target.value) || 0 }) })),
                            React.createElement("button", { type: "button", className: "adm-btn adm-btn-primary", style: { height: 26 }, onClick: handleAddRule },
                                React.createElement("i", { className: "codicon codicon-add" }),
                                " Add")),
                        React.createElement("div", { style: { maxHeight: '25vh', overflowY: 'auto', border: '1px solid var(--theia-border)', borderRadius: 4 } },
                            React.createElement("table", { className: "adm-table", style: { margin: 0 } },
                                React.createElement("thead", null,
                                    React.createElement("tr", null,
                                        React.createElement("th", null, "Platform Symbol"),
                                        React.createElement("th", null, "Source Symbol"),
                                        React.createElement("th", null, "Bid Adj (Points)"),
                                        React.createElement("th", null, "Ask Adj (Points)"),
                                        React.createElement("th", { style: { width: 60 } }, "Action"))),
                                React.createElement("tbody", null, translations.length === 0 ? (React.createElement("tr", null,
                                    React.createElement("td", { colSpan: 5, style: { textAlign: 'center', opacity: 0.6, padding: 12 } }, "No symbol translations configured. Direct matching (* <- *) active."))) : (translations.map((t, idx) => (React.createElement("tr", { key: idx },
                                    React.createElement("td", null, t.symbol),
                                    React.createElement("td", null, t.source),
                                    React.createElement("td", null, t.bid_adj),
                                    React.createElement("td", null, t.ask_adj),
                                    React.createElement("td", null,
                                        React.createElement("button", { type: "button", className: "adm-btn", style: { padding: '2px 6px', color: 'var(--theia-errorForeground)' }, onClick: () => handleRemoveRule(idx) },
                                            React.createElement("i", { className: "codicon codicon-trash" }),
                                            " Delete")))))))))))),
                React.createElement("div", { className: "adm-modal-footer" },
                    React.createElement("button", { type: "submit", className: "adm-btn adm-btn-primary" }, modalMode === 'create' ? 'Add Gateway' : 'Save Changes'),
                    React.createElement("button", { type: "button", className: "adm-btn", onClick: () => setShowModal(false) }, "Cancel"))))),
        React.createElement("div", { className: "adm-statusbar" },
            React.createElement("span", null,
                "Gateways: ",
                gateways.length),
            React.createElement("span", { className: "adm-sep" }, "|"),
            React.createElement("span", { style: { color: STATUS_COLOR.connected } },
                "Active: ",
                gateways.filter(g => g.is_active).length))));
}
exports.GatewaysPage = GatewaysPage;
//# sourceMappingURL=GatewaysPage.js.map