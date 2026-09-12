"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.RoutingPage = void 0;
// @ts-nocheck
const React = require("react");
const api_1 = require("../api");
const ACTION_COLOR = {
    INSTANT_EXECUTE: '#27ae60',
    TO_DEALER: '#9b59b6',
    TO_GATEWAY: '#3498db',
    REJECT: '#e74c3c',
};
function RoutingPage() {
    const [rules, setRules] = React.useState([]);
    const [gateways, setGateways] = React.useState([]);
    const [accounts, setAccounts] = React.useState([]);
    const [selected, setSelected] = React.useState(null);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState(null);
    // Modal states
    const [showModal, setShowModal] = React.useState(false);
    const [modalMode, setModalMode] = React.useState('create');
    const [modalTab, setModalTab] = React.useState('common');
    const [ruleForm, setRuleForm] = React.useState({
        id: null,
        name: '',
        is_enabled: true,
        action: 'INSTANT_EXECUTE',
        gateway_id: '',
        delay_seconds: '0',
        match_groups: '',
        match_symbols: '',
        match_accounts: '',
        match_order_types: '',
        match_volume_min: '',
        match_volume_max: ''
    });
    const [modalError, setModalError] = React.useState(null);
    const loadData = async () => {
        setLoading(true);
        setError(null);
        try {
            const rulesData = await api_1.API.getRoutingRules();
            setRules(rulesData);
            const gwsData = await api_1.API.getGateways();
            setGateways(gwsData);
            const accsData = await api_1.API.getAccounts();
            setAccounts(accsData);
        }
        catch (err) {
            setError(err.message || 'Failed to fetch routing rules, gateways, or accounts.');
        }
        finally {
            setLoading(false);
        }
    };
    React.useEffect(() => {
        loadData();
    }, []);
    const toggleRule = async (id, currentEnabled) => {
        setError(null);
        try {
            if (currentEnabled) {
                await api_1.API.disableRoutingRule(id);
            }
            else {
                await api_1.API.enableRoutingRule(id);
            }
            await loadData();
        }
        catch (err) {
            setError(err.message || 'Failed to toggle rule state.');
        }
    };
    const handleDelete = async () => {
        if (!selected)
            return;
        if (!confirm('Are you sure you want to delete this routing rule?'))
            return;
        setError(null);
        try {
            await api_1.API.deleteRoutingRule(selected);
            setSelected(null);
            await loadData();
        }
        catch (err) {
            setError(err.message || 'Failed to delete routing rule.');
        }
    };
    const moveUp = async (id) => {
        const idx = rules.findIndex(r => r.id === id);
        if (idx <= 0)
            return;
        const newOrderIds = rules.map(r => r.id);
        [newOrderIds[idx - 1], newOrderIds[idx]] = [newOrderIds[idx], newOrderIds[idx - 1]];
        setError(null);
        try {
            await api_1.API.reorderRoutingRules(newOrderIds);
            await loadData();
        }
        catch (err) {
            setError(err.message || 'Failed to reorder rules.');
        }
    };
    const moveDown = async (id) => {
        const idx = rules.findIndex(r => r.id === id);
        if (idx < 0 || idx >= rules.length - 1)
            return;
        const newOrderIds = rules.map(r => r.id);
        [newOrderIds[idx], newOrderIds[idx + 1]] = [newOrderIds[idx + 1], newOrderIds[idx]];
        setError(null);
        try {
            await api_1.API.reorderRoutingRules(newOrderIds);
            await loadData();
        }
        catch (err) {
            setError(err.message || 'Failed to reorder rules.');
        }
    };
    const openCreateModal = () => {
        setModalMode('create');
        setModalTab('common');
        setRuleForm({
            id: null,
            name: '',
            is_enabled: true,
            action: 'INSTANT_EXECUTE',
            gateway_id: '',
            delay_seconds: '0',
            match_groups: '',
            match_symbols: '',
            match_accounts: '',
            match_order_types: '',
            match_volume_min: '',
            match_volume_max: ''
        });
        setModalError(null);
        setShowModal(true);
    };
    const openEditModal = (r) => {
        setModalMode('edit');
        setModalTab('common');
        setRuleForm({
            id: r.id,
            name: r.name,
            is_enabled: r.is_enabled,
            action: r.action,
            gateway_id: r.gateway_id ? String(r.gateway_id) : '',
            delay_seconds: String(r.delay_seconds || 0),
            match_groups: r.match_groups ? r.match_groups.join(', ') : '',
            match_symbols: r.match_symbols ? r.match_symbols.join(', ') : '',
            match_accounts: r.match_accounts ? r.match_accounts.join(', ') : '',
            match_order_types: r.match_order_types ? r.match_order_types.join(', ') : '',
            match_volume_min: r.match_volume_min !== null ? String(r.match_volume_min) : '',
            match_volume_max: r.match_volume_max !== null ? String(r.match_volume_max) : ''
        });
        setModalError(null);
        setShowModal(true);
    };
    const handleSubmitRule = async (e) => {
        e.preventDefault();
        setModalError(null);
        try {
            const currentRule = rules.find(r => r.id === ruleForm.id);
            const payload = {
                name: ruleForm.name,
                priority: modalMode === 'create' ? rules.length + 1 : (currentRule ? currentRule.priority : 1),
                is_enabled: ruleForm.is_enabled,
                action: ruleForm.action,
                gateway_id: ruleForm.gateway_id ? parseInt(ruleForm.gateway_id) : undefined,
                delay_seconds: parseInt(ruleForm.delay_seconds) || 0,
                match_groups: ruleForm.match_groups ? ruleForm.match_groups.split(',').map(s => s.trim()).filter(Boolean) : undefined,
                match_symbols: ruleForm.match_symbols ? ruleForm.match_symbols.split(',').map(s => s.trim()).filter(Boolean) : undefined,
                match_accounts: ruleForm.match_accounts ? ruleForm.match_accounts.split(',').map(s => s.trim()).filter(Boolean) : undefined,
                match_order_types: ruleForm.match_order_types ? ruleForm.match_order_types.split(',').map(s => s.trim()).filter(Boolean) : undefined,
                match_volume_min: ruleForm.match_volume_min ? parseFloat(ruleForm.match_volume_min) : undefined,
                match_volume_max: ruleForm.match_volume_max ? parseFloat(ruleForm.match_volume_max) : undefined,
            };
            if (modalMode === 'create') {
                await api_1.API.createRoutingRule(payload);
            }
            else {
                await api_1.API.updateRoutingRule(ruleForm.id, payload);
            }
            setShowModal(false);
            await loadData();
        }
        catch (err) {
            setModalError(err.message || 'Failed to save routing rule.');
        }
    };
    const selectedRule = rules.find(r => r.id === selected);
    // Selected gateway info inside the Dealers tab
    const ruleGateway = gateways.find(g => String(g.id) === ruleForm.gateway_id);
    const ruleManager = accounts.find(a => String(a.login) === ruleForm.gateway_id);
    return (React.createElement("div", { className: "adm-page" },
        React.createElement("div", { className: "adm-toolbar" },
            React.createElement("button", { className: "adm-btn adm-btn-primary", onClick: openCreateModal },
                React.createElement("i", { className: "codicon codicon-add" }),
                " Add Rule"),
            React.createElement("button", { className: "adm-btn", disabled: !selectedRule, onClick: () => selectedRule && openEditModal(selectedRule) },
                React.createElement("i", { className: "codicon codicon-edit" }),
                " Edit Rule"),
            React.createElement("button", { className: "adm-btn adm-btn-danger", disabled: selected === null, onClick: handleDelete },
                React.createElement("i", { className: "codicon codicon-trash" }),
                " Delete"),
            React.createElement("div", { className: "adm-toolbar-sep" }),
            React.createElement("button", { className: "adm-btn", disabled: selected === null || rules.findIndex(r => r.id === selected) === 0, onClick: () => selected && moveUp(selected) },
                React.createElement("i", { className: "codicon codicon-arrow-up" }),
                " Move Up"),
            React.createElement("button", { className: "adm-btn", disabled: selected === null || rules.findIndex(r => r.id === selected) === rules.length - 1, onClick: () => selected && moveDown(selected) },
                React.createElement("i", { className: "codicon codicon-arrow-down" }),
                " Move Down"),
            React.createElement("div", { className: "adm-toolbar-sep" }),
            React.createElement("button", { className: "adm-btn", onClick: loadData, title: "Reload data" },
                React.createElement("i", { className: "codicon codicon-refresh" }),
                " Refresh"),
            React.createElement("div", { style: { marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 6 } },
                React.createElement("a", { href: "file:///c:/Users/DELL/Downloads/server3/MT5-Administrator/MetaTrader-5-Trading-Platform/Platform-Setup/Routing.md", target: "_blank", rel: "noreferrer", className: "adm-btn", style: { display: 'inline-flex', alignItems: 'center', gap: 4, textDecoration: 'none', color: 'inherit' } },
                    React.createElement("i", { className: "codicon codicon-book" }),
                    " Routing Guide"))),
        React.createElement("div", { className: "adm-hint" },
            React.createElement("i", { className: "codicon codicon-info" }),
            "Rules are executed ",
            React.createElement("strong", null, "top-to-bottom"),
            " based on priority. First matching rule wins. Double-click to Edit."),
        error && (React.createElement("div", { className: "adm-hint", style: { background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)' } },
            React.createElement("i", { className: "codicon codicon-error" }),
            " ",
            error)),
        React.createElement("div", { className: "adm-split-view" },
            React.createElement("div", { className: "adm-table-wrap", style: { flex: selectedRule ? '0 0 55%' : '1' } }, loading ? (React.createElement("div", { style: { padding: 20, textAlign: 'center', opacity: 0.7 } }, "Loading routing rules...")) : rules.length === 0 ? (React.createElement("div", { style: { padding: 20, textAlign: 'center', opacity: 0.7 } }, "No routing rules configured. Create one to route orders.")) : (React.createElement("table", { className: "adm-table" },
                React.createElement("thead", null,
                    React.createElement("tr", null,
                        React.createElement("th", null, "Priority"),
                        React.createElement("th", null, "Enabled"),
                        React.createElement("th", null, "Rule Name"),
                        React.createElement("th", null, "Action"),
                        React.createElement("th", null, "Match Specs"),
                        React.createElement("th", null, "Gateway Route"))),
                React.createElement("tbody", null, rules.map((r, idx) => (React.createElement("tr", { key: r.id, className: `${selected === r.id ? 'selected' : ''} ${!r.is_enabled ? 'adm-row-disabled' : ''}`, onClick: () => setSelected(r.id), onDoubleClick: () => openEditModal(r) },
                    React.createElement("td", { style: { opacity: 0.5 } }, idx + 1),
                    React.createElement("td", null,
                        React.createElement("button", { className: `adm-toggle ${r.is_enabled ? 'on' : 'off'}`, onClick: e => { e.stopPropagation(); toggleRule(r.id, r.is_enabled); } }, r.is_enabled ? '✓' : '✗')),
                    React.createElement("td", null,
                        React.createElement("strong", null, r.name)),
                    React.createElement("td", null,
                        React.createElement("span", { className: "adm-tag", style: { color: ACTION_COLOR[r.action] || '#aaa', border: `1px solid ${(ACTION_COLOR[r.action] || '#aaa')}55` } }, r.action)),
                    React.createElement("td", null,
                        r.match_symbols.length > 0 && React.createElement("span", { className: "adm-condition-chip", title: "Symbols" },
                            "Sym: ",
                            r.match_symbols.join(',')),
                        r.match_groups.length > 0 && React.createElement("span", { className: "adm-condition-chip", title: "Groups" },
                            "Grp: ",
                            r.match_groups.join(',')),
                        r.match_accounts.length > 0 && React.createElement("span", { className: "adm-condition-chip", title: "Accounts" },
                            "Acc: ",
                            r.match_accounts.join(',')),
                        r.match_volume_min !== null && React.createElement("span", { className: "adm-condition-chip" },
                            "Min Vol: ",
                            r.match_volume_min),
                        r.match_volume_max !== null && React.createElement("span", { className: "adm-condition-chip" },
                            "Max Vol: ",
                            r.match_volume_max),
                        r.match_symbols.length === 0 && r.match_groups.length === 0 && r.match_accounts.length === 0 && r.match_volume_min === null && r.match_volume_max === null && (React.createElement("span", { style: { opacity: 0.5 } }, "\u2014 Catchall \u2014"))),
                    React.createElement("td", null, r.gateway_id ? (React.createElement("strong", null, gateways.find(g => g.id === r.gateway_id)?.name || `Gateway #${r.gateway_id}`)) : (React.createElement("span", { style: { opacity: 0.5 } }, "\u2014")))))))))),
            selectedRule && (React.createElement("div", { className: "adm-detail-panel" },
                React.createElement("div", { className: "adm-detail-header" },
                    React.createElement("span", null,
                        "Rule Detail: ",
                        selectedRule.name),
                    React.createElement("button", { className: "adm-icon-btn", onClick: () => setSelected(null) },
                        React.createElement("i", { className: "codicon codicon-close" }))),
                React.createElement("div", { className: "adm-detail-body" },
                    React.createElement("div", { className: "adm-detail-section" }, "General"),
                    React.createElement("div", { className: "adm-kv" },
                        React.createElement("span", null, "Name"),
                        React.createElement("strong", null, selectedRule.name)),
                    React.createElement("div", { className: "adm-kv" },
                        React.createElement("span", null, "Priority"),
                        React.createElement("span", null, rules.findIndex(r => r.id === selectedRule.id) + 1)),
                    React.createElement("div", { className: "adm-kv" },
                        React.createElement("span", null, "Action"),
                        React.createElement("span", { style: { color: ACTION_COLOR[selectedRule.action] } }, selectedRule.action)),
                    React.createElement("div", { className: "adm-kv" },
                        React.createElement("span", null, "Gateway Route"),
                        React.createElement("strong", null, gateways.find(g => g.id === selectedRule.gateway_id)?.name || 'Local Matching (B-Book)')),
                    React.createElement("div", { className: "adm-kv" },
                        React.createElement("span", null, "Delay Seconds"),
                        React.createElement("span", null,
                            selectedRule.delay_seconds || 0,
                            " s")),
                    React.createElement("div", { className: "adm-detail-section" }, "Filter Rules"),
                    React.createElement("div", { className: "adm-kv" },
                        React.createElement("span", null, "Symbols"),
                        React.createElement("span", null, selectedRule.match_symbols.length > 0 ? selectedRule.match_symbols.join(', ') : 'All')),
                    React.createElement("div", { className: "adm-kv" },
                        React.createElement("span", null, "Groups"),
                        React.createElement("span", null, selectedRule.match_groups.length > 0 ? selectedRule.match_groups.join(', ') : 'All')),
                    React.createElement("div", { className: "adm-kv" },
                        React.createElement("span", null, "Accounts"),
                        React.createElement("span", null, selectedRule.match_accounts && selectedRule.match_accounts.length > 0 ? selectedRule.match_accounts.join(', ') : 'All')),
                    React.createElement("div", { className: "adm-kv" },
                        React.createElement("span", null, "Order Types"),
                        React.createElement("span", null, selectedRule.match_order_types.length > 0 ? selectedRule.match_order_types.join(', ') : 'All')),
                    React.createElement("div", { className: "adm-kv" },
                        React.createElement("span", null, "Min Vol"),
                        React.createElement("span", null, selectedRule.match_volume_min !== null ? selectedRule.match_volume_min : 'Any')),
                    React.createElement("div", { className: "adm-kv" },
                        React.createElement("span", null, "Max Vol"),
                        React.createElement("span", null, selectedRule.match_volume_max !== null ? selectedRule.match_volume_max : 'Any')))))),
        showModal && (React.createElement("div", { className: "adm-modal-overlay", onClick: () => setShowModal(false) },
            React.createElement("form", { className: "adm-modal", style: { width: 750, height: '65vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }, onClick: e => e.stopPropagation(), onSubmit: handleSubmitRule },
                React.createElement("div", { className: "adm-modal-header" },
                    React.createElement("h2", null,
                        React.createElement("i", { className: "codicon codicon-split-horizontal", style: { marginRight: 8, color: '#3498db' } }),
                        modalMode === 'create' ? 'Add Routing Rule' : `Edit Routing Rule — ${ruleForm.name}`),
                    React.createElement("button", { type: "button", className: "adm-modal-close", onClick: () => setShowModal(false) }, "\u00D7")),
                React.createElement("div", { className: "adm-tabs", style: { padding: '0 16px', borderBottom: '1px solid var(--theia-border)' } },
                    React.createElement("button", { type: "button", className: `adm-tab ${modalTab === 'common' ? 'active' : ''}`, onClick: () => setModalTab('common') }, "Common"),
                    React.createElement("button", { type: "button", className: `adm-tab ${modalTab === 'dealers' ? 'active' : ''}`, onClick: () => setModalTab('dealers') }, "Dealers")),
                React.createElement("div", { className: "adm-modal-body", style: { flex: 1, overflowY: 'auto', padding: '16px' } },
                    modalError && (React.createElement("div", { className: "adm-hint", style: { background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)', margin: '0 0 16px 0' } },
                        React.createElement("i", { className: "codicon codicon-error" }),
                        " ",
                        modalError)),
                    modalTab === 'common' ? (React.createElement("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 24px' } },
                        React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 10 } },
                            React.createElement("div", { style: { fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2 } }, "General Properties"),
                            React.createElement("div", { className: "adm-form-row" },
                                React.createElement("label", null, "Rule Name"),
                                React.createElement("input", { className: "adm-input", style: { width: '100%', height: 20 }, required: true, placeholder: "e.g. Route EURUSD to LP", value: ruleForm.name, onChange: e => setRuleForm({ ...ruleForm, name: e.target.value }) })),
                            React.createElement("div", { className: "adm-form-row" },
                                React.createElement("label", null, "Execution Action"),
                                React.createElement("select", { className: "adm-select", style: { width: '100%', height: 20 }, value: ruleForm.action, onChange: e => setRuleForm({ ...ruleForm, action: e.target.value }) },
                                    React.createElement("option", { value: "INSTANT_EXECUTE" }, "Instant Execute (B-Book)"),
                                    React.createElement("option", { value: "TO_GATEWAY" }, "To Gateway (A-Book)"),
                                    React.createElement("option", { value: "TO_DEALER" }, "To Dealer Queue (Manual confirmation)"),
                                    React.createElement("option", { value: "REJECT" }, "Reject (Block Execution)"))),
                            React.createElement("div", { className: "adm-form-row" },
                                React.createElement("label", null, "Delay Seconds"),
                                React.createElement("input", { className: "adm-input", style: { width: '100%', height: 20 }, type: "number", placeholder: "0", value: ruleForm.delay_seconds, onChange: e => setRuleForm({ ...ruleForm, delay_seconds: e.target.value }) })),
                            React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', marginTop: 8, fontSize: 11 } },
                                React.createElement("input", { type: "checkbox", checked: ruleForm.is_enabled, onChange: e => setRuleForm({ ...ruleForm, is_enabled: e.target.checked }) }),
                                "Enable this rule")),
                        React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 10 } },
                            React.createElement("div", { style: { fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2 } }, "Filtering Criteria (Comma-separated)"),
                            React.createElement("div", { className: "adm-form-row" },
                                React.createElement("label", null, "Match Groups"),
                                React.createElement("input", { className: "adm-input", style: { width: '100%', height: 20 }, placeholder: "e.g. demo_group, real_group", value: ruleForm.match_groups, onChange: e => setRuleForm({ ...ruleForm, match_groups: e.target.value }) })),
                            React.createElement("div", { className: "adm-form-row" },
                                React.createElement("label", null, "Match Symbols"),
                                React.createElement("input", { className: "adm-input", style: { width: '100%', height: 20 }, placeholder: "e.g. EURUSD, GBPUSD", value: ruleForm.match_symbols, onChange: e => setRuleForm({ ...ruleForm, match_symbols: e.target.value }) })),
                            React.createElement("div", { className: "adm-form-row" },
                                React.createElement("label", null, "Match Accounts (Logins)"),
                                React.createElement("input", { className: "adm-input", style: { width: '100%', height: 20 }, placeholder: "e.g. 50080, 50081", value: ruleForm.match_accounts, onChange: e => setRuleForm({ ...ruleForm, match_accounts: e.target.value }) })),
                            React.createElement("div", { className: "adm-form-row" },
                                React.createElement("label", null, "Match Order Types"),
                                React.createElement("input", { className: "adm-input", style: { width: '100%', height: 20 }, placeholder: "e.g. BUY, SELL", value: ruleForm.match_order_types, onChange: e => setRuleForm({ ...ruleForm, match_order_types: e.target.value }) })),
                            React.createElement("div", { style: { display: 'flex', gap: 8 } },
                                React.createElement("div", { className: "adm-form-row", style: { flex: 1 } },
                                    React.createElement("label", null, "Min Volume"),
                                    React.createElement("input", { className: "adm-input", style: { width: '100%', height: 20 }, type: "number", step: "0.01", placeholder: "Any", value: ruleForm.match_volume_min, onChange: e => setRuleForm({ ...ruleForm, match_volume_min: e.target.value }) })),
                                React.createElement("div", { className: "adm-form-row", style: { flex: 1 } },
                                    React.createElement("label", null, "Max Volume"),
                                    React.createElement("input", { className: "adm-input", style: { width: '100%', height: 20 }, type: "number", step: "0.01", placeholder: "Any", value: ruleForm.match_volume_max, onChange: e => setRuleForm({ ...ruleForm, match_volume_max: e.target.value }) })))))) : (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 12 } },
                        React.createElement("div", { style: { fontSize: 11, color: 'var(--theia-descriptionForeground)', borderBottom: '1px solid var(--theia-border)', paddingBottom: 4 } }, "Configure Dealers (Managers) or ECN Gateways associated with this routing rule."),
                        ruleForm.action !== 'TO_DEALER' && ruleForm.action !== 'TO_GATEWAY' ? (React.createElement("div", { className: "adm-hint", style: { background: 'var(--theia-inputValidation-infoBackground)', color: 'var(--theia-inputValidation-infoForeground)' } },
                            React.createElement("i", { className: "codicon codicon-info" }),
                            " The Dealers/Gateways list is only active when the rule action is set to ",
                            React.createElement("strong", null, "Process to dealers"),
                            " or ",
                            React.createElement("strong", null, "To Gateway (A-Book)"),
                            ".")) : ruleForm.action === 'TO_DEALER' ? (React.createElement(React.Fragment, null,
                            React.createElement("div", { style: { border: '1px solid var(--theia-border)', borderRadius: 4 } },
                                React.createElement("table", { className: "adm-table", style: { margin: 0 } },
                                    React.createElement("thead", null,
                                        React.createElement("tr", null,
                                            React.createElement("th", null, "Manager Login"),
                                            React.createElement("th", null, "Group Name"),
                                            React.createElement("th", null, "Balance"),
                                            React.createElement("th", null, "Leverage"),
                                            React.createElement("th", null, "Status"),
                                            React.createElement("th", { style: { width: 80 } }, "Action"))),
                                    React.createElement("tbody", null, ruleManager ? (React.createElement("tr", null,
                                        React.createElement("td", null,
                                            React.createElement("strong", null, ruleManager.login)),
                                        React.createElement("td", null,
                                            React.createElement("strong", null, ruleManager.group_name)),
                                        React.createElement("td", null,
                                            parseFloat(ruleManager.balance || 0).toFixed(2),
                                            " USD"),
                                        React.createElement("td", null,
                                            "1:",
                                            ruleManager.leverage),
                                        React.createElement("td", null,
                                            React.createElement("span", { className: "adm-status-dot online", style: { marginRight: 6 } }),
                                            "Dealing"),
                                        React.createElement("td", null,
                                            React.createElement("button", { type: "button", className: "adm-btn", style: { padding: '2px 6px', color: 'var(--theia-errorForeground)' }, onClick: () => setRuleForm({ ...ruleForm, gateway_id: '' }) },
                                                React.createElement("i", { className: "codicon codicon-trash" }),
                                                " Delete")))) : (React.createElement("tr", null,
                                        React.createElement("td", { colSpan: 6, style: { textAlign: 'center', opacity: 0.6, padding: 16 } }, "No dealer accounts currently assigned. Use the selection below to assign one.")))))),
                            !ruleForm.gateway_id && (React.createElement("div", { style: { display: 'flex', gap: 8, alignItems: 'center', marginTop: 12 } },
                                React.createElement("span", { style: { fontSize: 11 } }, "Select Manager Account:"),
                                React.createElement("select", { className: "adm-select", style: { width: 260, height: 22 }, value: "", onChange: e => {
                                        if (e.target.value) {
                                            setRuleForm({ ...ruleForm, gateway_id: e.target.value });
                                        }
                                    } },
                                    React.createElement("option", { value: "" }, "Choose Dealing Manager..."),
                                    accounts.filter(a => a.group_name && a.group_name.toLowerCase().includes('manager')).map(m => (React.createElement("option", { key: m.login, value: m.login },
                                        m.login,
                                        " (",
                                        m.group_name,
                                        ")")))))))) : (React.createElement(React.Fragment, null,
                            React.createElement("div", { style: { border: '1px solid var(--theia-border)', borderRadius: 4 } },
                                React.createElement("table", { className: "adm-table", style: { margin: 0 } },
                                    React.createElement("thead", null,
                                        React.createElement("tr", null,
                                            React.createElement("th", null, "Dealer/Gateway ID"),
                                            React.createElement("th", null, "Gateway Name"),
                                            React.createElement("th", null, "Type"),
                                            React.createElement("th", null, "Connection Host"),
                                            React.createElement("th", null, "Status"),
                                            React.createElement("th", { style: { width: 80 } }, "Action"))),
                                    React.createElement("tbody", null, ruleGateway ? (React.createElement("tr", null,
                                        React.createElement("td", null,
                                            React.createElement("strong", null, ruleGateway.id)),
                                        React.createElement("td", null,
                                            React.createElement("strong", null, ruleGateway.name)),
                                        React.createElement("td", null,
                                            React.createElement("span", { className: "adm-tag", style: { fontSize: 9 } }, ruleGateway.type)),
                                        React.createElement("td", null,
                                            React.createElement("code", { className: "adm-code" }, ruleGateway.host || 'localhost')),
                                        React.createElement("td", null,
                                            React.createElement("span", { className: `adm-status-dot ${ruleGateway.is_active ? 'online' : 'offline'}`, style: { marginRight: 6 } }),
                                            ruleGateway.is_active ? 'Active' : 'Offline'),
                                        React.createElement("td", null,
                                            React.createElement("button", { type: "button", className: "adm-btn", style: { padding: '2px 6px', color: 'var(--theia-errorForeground)' }, onClick: () => setRuleForm({ ...ruleForm, gateway_id: '' }) },
                                                React.createElement("i", { className: "codicon codicon-trash" }),
                                                " Delete")))) : (React.createElement("tr", null,
                                        React.createElement("td", { colSpan: 6, style: { textAlign: 'center', opacity: 0.6, padding: 16 } }, "No gateways currently assigned. Use the selection below to assign one.")))))),
                            !ruleForm.gateway_id && (React.createElement("div", { style: { display: 'flex', gap: 8, alignItems: 'center', marginTop: 12 } },
                                React.createElement("span", { style: { fontSize: 11 } }, "Select Gateway:"),
                                React.createElement("select", { className: "adm-select", style: { width: 220, height: 22 }, value: "", onChange: e => {
                                        if (e.target.value) {
                                            setRuleForm({ ...ruleForm, gateway_id: e.target.value });
                                        }
                                    } },
                                    React.createElement("option", { value: "" }, "Choose LP Gateway..."),
                                    gateways.map(g => (React.createElement("option", { key: g.id, value: g.id },
                                        g.name,
                                        " (",
                                        g.type,
                                        ") \u2014 ",
                                        g.host || 'localhost'))))))))))),
                React.createElement("div", { className: "adm-modal-footer" },
                    React.createElement("button", { type: "submit", className: "adm-btn adm-btn-primary" }, modalMode === 'create' ? 'Create Rule' : 'Save Changes'),
                    React.createElement("button", { type: "button", className: "adm-btn", onClick: () => setShowModal(false) }, "Cancel"))))),
        React.createElement("div", { className: "adm-statusbar" },
            React.createElement("span", null,
                "Total Rules: ",
                rules.length),
            React.createElement("span", { className: "adm-sep" }, "|"),
            React.createElement("span", null,
                "Active: ",
                rules.filter(r => r.is_enabled).length))));
}
exports.RoutingPage = RoutingPage;
//# sourceMappingURL=RoutingPage.js.map