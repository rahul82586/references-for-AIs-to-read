"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ClientsPage = void 0;
// @ts-nocheck
const React = require("react");
const api_1 = require("../api");
const STATUS_MAP = {
    0: 'active',
    1: 'readonly',
    2: 'disabled'
};
const STATUS_COLOR = {
    active: 'var(--theia-successForeground)',
    disabled: 'var(--theia-errorForeground)',
    readonly: '#f0ad4e',
};
function ClientsPage({ initialTab = 'accounts' }) {
    const [clients, setClients] = React.useState([]);
    const [selected, setSelected] = React.useState(null);
    const [filter, setFilter] = React.useState('');
    const [tab, setTab] = React.useState(initialTab);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState(null);
    // Context Menu State
    const [contextMenu, setContextMenu] = React.useState(null);
    // Create Modal State
    const [showCreateModal, setShowCreateModal] = React.useState(false);
    const [newAccount, setNewAccount] = React.useState({
        login: '',
        group_name: 'demo_group',
        initial_balance: '10000',
        leverage: '100',
        password: 'password123',
        name: '',
        last_name: '',
        middle_name: '',
        company: '',
        email: '',
        phone: '',
        country: '',
        state: '',
        city: '',
        zip_code: '',
        address: '',
        investor_password: '',
        phone_password: ''
    });
    const [createError, setCreateError] = React.useState(null);
    // Edit Modal State
    const [showEditModal, setShowEditModal] = React.useState(false);
    const [editingTab, setEditingTab] = React.useState('overview');
    const [editingAccount, setEditingAccount] = React.useState(null);
    const [editError, setEditError] = React.useState(null);
    const loadAccounts = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await api_1.API.getAccounts();
            setClients(data);
        }
        catch (err) {
            setError(err.message || 'Failed to fetch accounts from broker server.');
        }
        finally {
            setLoading(false);
        }
    };
    React.useEffect(() => {
        loadAccounts();
    }, []);
    React.useEffect(() => {
        const handleOutsideClick = () => setContextMenu(null);
        window.addEventListener('click', handleOutsideClick);
        return () => window.removeEventListener('click', handleOutsideClick);
    }, []);
    const handleCreateAccount = async (e) => {
        e.preventDefault();
        setCreateError(null);
        try {
            const payload = {
                group_name: newAccount.group_name,
                initial_balance: parseFloat(newAccount.initial_balance) || 0,
                leverage: parseInt(newAccount.leverage) || 100,
                password: newAccount.password,
                // Extra fields stored in settings_json on create
                name: newAccount.name,
                last_name: newAccount.last_name,
                middle_name: newAccount.middle_name,
                company: newAccount.company,
                email: newAccount.email,
                phone: newAccount.phone,
                country: newAccount.country,
                state: newAccount.state,
                city: newAccount.city,
                zip_code: newAccount.zip_code,
                address: newAccount.address,
                investor_password: newAccount.investor_password,
                phone_password: newAccount.phone_password
            };
            if (newAccount.login && newAccount.login.toLowerCase() !== 'next') {
                payload.login = parseInt(newAccount.login);
            }
            await api_1.API.createAccount(payload);
            setShowCreateModal(false);
            setNewAccount({
                login: '',
                group_name: 'demo_group',
                initial_balance: '10000',
                leverage: '100',
                password: 'password123',
                name: '',
                last_name: '',
                middle_name: '',
                company: '',
                email: '',
                phone: '',
                country: '',
                state: '',
                city: '',
                zip_code: '',
                address: '',
                investor_password: '',
                phone_password: ''
            });
            await loadAccounts();
        }
        catch (err) {
            setCreateError(err.message || 'Failed to create account.');
        }
    };
    const handleOpenEdit = (login) => {
        const client = clients.find(c => c.login === login);
        if (!client)
            return;
        // Parse custom settings or set defaults
        const custom = client.settings_json || {};
        setEditingAccount({
            ...client,
            name: custom.name || '',
            last_name: custom.last_name || '',
            middle_name: custom.middle_name || '',
            company: custom.company || '',
            email: custom.email || '',
            phone: custom.phone || '',
            country: custom.country || '',
            state: custom.state || '',
            city: custom.city || '',
            zip_code: custom.zip_code || '',
            address: custom.address || '',
            registered: custom.registered || new Date().toLocaleDateString(),
            language: custom.language || 'English',
            resident_status: custom.resident_status || 'RE',
            id_number: custom.id_number || '',
            lead_source: custom.lead_source || '',
            lead_campaign: custom.lead_campaign || '',
            metaquotes_id: custom.metaquotes_id || '',
            comment: custom.comment || '',
            // Account Tab
            color: custom.color || '#000000',
            bank_account: custom.bank_account || '',
            agent_account: custom.agent_account || '',
            enable_account: custom.enable_account ?? true,
            allow_change_password: custom.allow_change_password ?? true,
            enable_otp: custom.enable_otp ?? false,
            change_pass_next_login: custom.change_pass_next_login ?? false,
            // Limits Tab
            show_to_regular_managers: custom.show_to_regular_managers ?? true,
            include_in_server_reports: custom.include_in_server_reports ?? true,
            enable_daily_reports: custom.enable_daily_reports ?? true,
            enable_sponsored_vps: custom.enable_sponsored_vps ?? false,
            enable_trading: custom.enable_trading ?? true,
            enable_ea: custom.enable_ea ?? true,
            enable_trailing_stops: custom.enable_trailing_stops ?? true,
            limit_position_value: custom.limit_position_value || '',
            limit_active_orders: custom.limit_active_orders || '',
            // Security Passwords State
            master_pass: '',
            investor_pass: '',
            phone_pass: '',
            otp_secret: custom.otp_secret || 'A1B2C3D4E5F6'
        });
        setEditingTab('overview');
        setShowEditModal(true);
    };
    const handleSaveEditAccount = async (e) => {
        e.preventDefault();
        setEditError(null);
        try {
            // In a real application, we would call an update API.
            // Let's call the API if it supports PUT /admin/accounts or update locally
            const payload = {
                login: editingAccount.login,
                group_name: editingAccount.group_name,
                leverage: editingAccount.leverage,
                status: editingAccount.enable_account ? 0 : 2,
                settings_json: {
                    ...editingAccount
                }
            };
            // Call API update if available, or fallback
            if (api_1.API.updateAccount) {
                await api_1.API.updateAccount(payload.login, payload);
            }
            else {
                // Mock local update
                setClients(prev => prev.map(c => c.login === editingAccount.login ? {
                    ...c,
                    group_name: editingAccount.group_name,
                    leverage: editingAccount.leverage,
                    status: editingAccount.enable_account ? 0 : 2,
                    settings_json: editingAccount
                } : c));
            }
            setShowEditModal(false);
            await loadAccounts();
        }
        catch (err) {
            setEditError(err.message || 'Failed to update account.');
        }
    };
    const handleDeleteAccount = async (login) => {
        if (!confirm(`Are you sure you want to delete account #${login}?`))
            return;
        try {
            await api_1.API.deleteAccount(login);
            setSelected(null);
            await loadAccounts();
        }
        catch (err) {
            alert(err.message || 'Failed to delete account.');
        }
    };
    const handleContextMenu = (e, login) => {
        e.preventDefault();
        setContextMenu({
            x: e.clientX,
            y: e.clientY,
            login
        });
    };
    const filtered = clients.filter(c => String(c.login).includes(filter) ||
        c.group_name.toLowerCase().includes(filter.toLowerCase()));
    const selectedClient = clients.find(c => c.login === selected);
    return (React.createElement("div", { className: "adm-page", onContextMenu: e => handleContextMenu(e, null) },
        React.createElement("div", { className: "adm-tabs" }, ['accounts', 'clients', 'managers', 'allocations'].map(t => (React.createElement("button", { key: t, className: `adm-tab ${tab === t ? 'active' : ''}`, onClick: () => setTab(t) }, t === 'accounts' ? 'Trading Accounts' : t.charAt(0).toUpperCase() + t.slice(1))))),
        React.createElement("div", { className: "adm-toolbar" },
            React.createElement("button", { className: "adm-btn adm-btn-primary", onClick: () => setShowCreateModal(true) },
                React.createElement("i", { className: "codicon codicon-add" }),
                " New Account"),
            selected !== null && (React.createElement(React.Fragment, null,
                React.createElement("button", { className: "adm-btn", onClick: () => handleOpenEdit(selected) },
                    React.createElement("i", { className: "codicon codicon-edit" }),
                    " Edit"),
                React.createElement("button", { className: "adm-btn", onClick: () => handleDeleteAccount(selected), style: { color: 'var(--theia-errorForeground)' } },
                    React.createElement("i", { className: "codicon codicon-trash" }),
                    " Delete"))),
            React.createElement("button", { className: "adm-btn", onClick: loadAccounts, title: "Reload list" },
                React.createElement("i", { className: "codicon codicon-refresh" }),
                " Refresh"),
            React.createElement("div", { className: "adm-toolbar-sep" }),
            React.createElement("div", { className: "adm-search-wrap" },
                React.createElement("i", { className: "codicon codicon-search" }),
                React.createElement("input", { className: "adm-search", placeholder: "Search login or group...", value: filter, onChange: e => setFilter(e.target.value) }))),
        error && (React.createElement("div", { className: "adm-hint", style: { background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)' } },
            React.createElement("i", { className: "codicon codicon-error" }),
            " ",
            error)),
        React.createElement("div", { className: "adm-split-view", style: { flex: 1, minHeight: 0 } },
            React.createElement("div", { className: "adm-table-wrap", style: { flex: selectedClient ? '0 0 60%' : '1', overflowY: 'auto' } }, loading ? (React.createElement("div", { style: { padding: 20, textAlign: 'center', opacity: 0.7 } }, "Loading accounts...")) : filtered.length === 0 ? (React.createElement("div", { style: { padding: 20, textAlign: 'center', opacity: 0.7 } }, "No accounts found. Use \"New Account\" to create one.")) : (React.createElement("table", { className: "adm-table" },
                React.createElement("thead", null,
                    React.createElement("tr", null,
                        React.createElement("th", null, "Login"),
                        React.createElement("th", null, "Group Name"),
                        React.createElement("th", null, "Balance"),
                        React.createElement("th", null, "Equity"),
                        React.createElement("th", null, "Free Margin"),
                        React.createElement("th", null, "Leverage"),
                        React.createElement("th", null, "Status"))),
                React.createElement("tbody", null, filtered.map(c => {
                    const statusStr = STATUS_MAP[c.status] || 'unknown';
                    return (React.createElement("tr", { key: c.login, className: selected === c.login ? 'selected' : '', onClick: () => setSelected(c.login), onDoubleClick: () => handleOpenEdit(c.login), onContextMenu: e => handleContextMenu(e, c.login) },
                        React.createElement("td", null,
                            React.createElement("strong", null, c.login)),
                        React.createElement("td", null,
                            React.createElement("code", { className: "adm-code" }, c.group_name)),
                        React.createElement("td", { className: "adm-num" }, c.balance.toLocaleString('en', { minimumFractionDigits: 2 })),
                        React.createElement("td", { className: `adm-num ${c.equity >= c.balance ? 'adm-pos' : 'adm-neg'}` }, c.equity.toLocaleString('en', { minimumFractionDigits: 2 })),
                        React.createElement("td", { className: "adm-num" }, c.free_margin.toLocaleString('en', { minimumFractionDigits: 2 })),
                        React.createElement("td", null,
                            "1:",
                            c.leverage),
                        React.createElement("td", null,
                            React.createElement("span", { className: "adm-dot", style: { background: STATUS_COLOR[statusStr] || '#888' } }),
                            statusStr)));
                }))))),
            selectedClient && (React.createElement("div", { className: "adm-detail-panel", style: { overflowY: 'auto' } },
                React.createElement("div", { className: "adm-detail-header" },
                    React.createElement("span", null,
                        "Account #",
                        selectedClient.login),
                    React.createElement("button", { className: "adm-icon-btn", onClick: () => setSelected(null) },
                        React.createElement("i", { className: "codicon codicon-close" }))),
                React.createElement("div", { className: "adm-detail-body" },
                    React.createElement("div", { className: "adm-detail-section" }, "General Information"),
                    React.createElement("div", { className: "adm-kv" },
                        React.createElement("span", null, "Login"),
                        React.createElement("strong", null, selectedClient.login)),
                    React.createElement("div", { className: "adm-kv" },
                        React.createElement("span", null, "Group"),
                        React.createElement("code", { className: "adm-code" }, selectedClient.group_name)),
                    React.createElement("div", { className: "adm-kv" },
                        React.createElement("span", null, "Leverage"),
                        React.createElement("span", null,
                            "1:",
                            selectedClient.leverage)),
                    React.createElement("div", { className: "adm-detail-section" }, "Balance & Margins"),
                    React.createElement("div", { className: "adm-kv" },
                        React.createElement("span", null, "Balance"),
                        React.createElement("strong", null,
                            (selectedClient.balance ?? 0).toFixed(2),
                            " USD")),
                    React.createElement("div", { className: "adm-kv" },
                        React.createElement("span", null, "Equity"),
                        React.createElement("strong", { className: (selectedClient.equity ?? 0) >= (selectedClient.balance ?? 0) ? 'adm-pos' : 'adm-neg' },
                            (selectedClient.equity ?? 0).toFixed(2),
                            " USD")),
                    React.createElement("div", { className: "adm-kv" },
                        React.createElement("span", null, "Margin"),
                        React.createElement("span", null,
                            (selectedClient.margin ?? 0).toFixed(2),
                            " USD")),
                    React.createElement("div", { className: "adm-kv" },
                        React.createElement("span", null, "Free Margin"),
                        React.createElement("span", null,
                            (selectedClient.free_margin ?? 0).toFixed(2),
                            " USD")),
                    React.createElement("div", { className: "adm-detail-section" }, "Security & Status"),
                    React.createElement("div", { className: "adm-kv" },
                        React.createElement("span", null, "Status"),
                        React.createElement("span", { style: { color: STATUS_COLOR[STATUS_MAP[selectedClient.status]] || '#888' } }, STATUS_MAP[selectedClient.status] || 'unknown'))),
                React.createElement("div", { className: "adm-detail-footer" },
                    React.createElement("button", { className: "adm-btn adm-btn-primary", onClick: () => handleOpenEdit(selectedClient.login) }, "Edit Details"))))),
        contextMenu && (React.createElement("div", { className: "adm-context-menu", style: {
                position: 'fixed',
                top: contextMenu.y,
                left: contextMenu.x,
                background: 'var(--theia-menu-background, #252526)',
                border: '1px solid var(--theia-menu-border, #454545)',
                boxShadow: '0 2px 8px rgba(0,0,0,0.5)',
                zIndex: 10000,
                padding: '4px 0',
                minWidth: 170
            }, onClick: e => e.stopPropagation() },
            React.createElement("div", { className: "adm-menu-item", onClick: () => { setShowCreateModal(true); setContextMenu(null); }, style: { padding: '6px 12px', fontSize: 11, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 } },
                React.createElement("i", { className: "codicon codicon-add" }),
                " New Account"),
            contextMenu.login !== null ? (React.createElement(React.Fragment, null,
                React.createElement("div", { className: "adm-menu-item", onClick: () => { handleOpenEdit(contextMenu.login); setContextMenu(null); }, style: { padding: '6px 12px', fontSize: 11, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 } },
                    React.createElement("i", { className: "codicon codicon-edit" }),
                    " Edit"),
                React.createElement("div", { className: "adm-menu-item", onClick: () => {
                        const c = clients.find(cl => cl.login === contextMenu.login);
                        if (c)
                            alert(`Open group settings for: ${c.group_name}`);
                        setContextMenu(null);
                    }, style: { padding: '6px 12px', fontSize: 11, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 } },
                    React.createElement("i", { className: "codicon codicon-organization" }),
                    " Edit Group"),
                React.createElement("div", { className: "adm-menu-item", onClick: () => {
                        alert(`Edit manager profile linked to login ${contextMenu.login}`);
                        setContextMenu(null);
                    }, style: { padding: '6px 12px', fontSize: 11, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 } },
                    React.createElement("i", { className: "codicon codicon-person" }),
                    " Edit Manager"),
                React.createElement("div", { className: "adm-menu-item", onClick: () => { handleDeleteAccount(contextMenu.login); setContextMenu(null); }, style: { padding: '6px 12px', fontSize: 11, cursor: 'pointer', color: 'var(--theia-errorForeground)', display: 'flex', alignItems: 'center', gap: 6 } },
                    React.createElement("i", { className: "codicon codicon-trash" }),
                    " Delete"),
                React.createElement("div", { style: { height: 1, background: 'var(--theia-menu-border, #454545)', margin: '4px 0' } }),
                React.createElement("div", { className: "adm-menu-item", onClick: () => {
                        alert(`Move account #${contextMenu.login} to archive`);
                        setContextMenu(null);
                    }, style: { padding: '6px 12px', fontSize: 11, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 } },
                    React.createElement("i", { className: "codicon codicon-archive" }),
                    " Move to Archive"),
                React.createElement("div", { className: "adm-menu-item", onClick: () => {
                        alert(`Checking balance consistency for account #${contextMenu.login}`);
                        setContextMenu(null);
                    }, style: { padding: '6px 12px', fontSize: 11, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 } },
                    React.createElement("i", { className: "codicon codicon-check" }),
                    " Check Balance"),
                React.createElement("div", { className: "adm-menu-item", onClick: () => {
                        alert(`Fixing balance fields for account #${contextMenu.login}`);
                        setContextMenu(null);
                    }, style: { padding: '6px 12px', fontSize: 11, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 } },
                    React.createElement("i", { className: "codicon codicon-tools" }),
                    " Fix Balance"),
                React.createElement("div", { style: { height: 1, background: 'var(--theia-menu-border, #454545)', margin: '4px 0' } }),
                React.createElement("div", { className: "adm-menu-item", onClick: () => {
                        navigator.clipboard.writeText(`Login: ${contextMenu.login}`);
                        setContextMenu(null);
                    }, style: { padding: '6px 12px', fontSize: 11, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 } },
                    React.createElement("i", { className: "codicon codicon-copy" }),
                    " Copy Lines"),
                React.createElement("div", { className: "adm-menu-item", onClick: () => {
                        navigator.clipboard.writeText(String(contextMenu.login));
                        setContextMenu(null);
                    }, style: { padding: '6px 12px', fontSize: 11, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 } },
                    React.createElement("i", { className: "codicon codicon-list-unordered" }),
                    " Copy Login"),
                React.createElement("div", { style: { height: 1, background: 'var(--theia-menu-border, #454545)', margin: '4px 0' } }),
                React.createElement("div", { className: "adm-menu-item", onClick: () => {
                        alert(`Exporting trade account #${contextMenu.login} data to CSV/HTML`);
                        setContextMenu(null);
                    }, style: { padding: '6px 12px', fontSize: 11, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 } },
                    React.createElement("i", { className: "codicon codicon-cloud-upload" }),
                    " Export Account"),
                React.createElement("div", { className: "adm-menu-item", onClick: () => {
                        alert(`Opening email compose window for: ${contextMenu.login}`);
                        setContextMenu(null);
                    }, style: { padding: '6px 12px', fontSize: 11, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 } },
                    React.createElement("i", { className: "codicon codicon-mail" }),
                    " Send E-Mail"),
                React.createElement("div", { className: "adm-menu-item", onClick: () => {
                        alert(`Loading server journal entries for account #${contextMenu.login}`);
                        setContextMenu(null);
                    }, style: { padding: '6px 12px', fontSize: 11, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 } },
                    React.createElement("i", { className: "codicon codicon-output" }),
                    " View Journal"))) : (React.createElement(React.Fragment, null,
                React.createElement("div", { style: { height: 1, background: 'var(--theia-menu-border, #454545)', margin: '4px 0' } }),
                React.createElement("div", { className: "adm-menu-item", onClick: () => { loadAccounts(); setContextMenu(null); }, style: { padding: '6px 12px', fontSize: 11, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 } },
                    React.createElement("i", { className: "codicon codicon-refresh" }),
                    " Request Accounts"),
                React.createElement("div", { className: "adm-menu-item", onClick: () => { alert('Import accounts from CSV file'); setContextMenu(null); }, style: { padding: '6px 12px', fontSize: 11, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 } },
                    React.createElement("i", { className: "codicon codicon-cloud-download" }),
                    " Import from File"))))),
        showCreateModal && (React.createElement("div", { className: "adm-modal-overlay", style: { zIndex: 1200 }, onClick: () => setShowCreateModal(false) },
            React.createElement("form", { className: "adm-modal", style: { width: 650, height: '65vh', display: 'flex', flexDirection: 'column' }, onClick: e => e.stopPropagation(), onSubmit: handleCreateAccount },
                React.createElement("div", { className: "adm-modal-header", style: { flexShrink: 0 } },
                    React.createElement("h2", null, "Create New Trade Account"),
                    React.createElement("button", { type: "button", className: "adm-modal-close", onClick: () => setShowCreateModal(false) }, "\u00D7")),
                React.createElement("div", { className: "adm-modal-body", style: { flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 16, padding: 16 } },
                    createError && (React.createElement("div", { className: "adm-hint", style: { background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)', margin: 0 } },
                        React.createElement("i", { className: "codicon codicon-error" }),
                        " ",
                        createError)),
                    React.createElement("div", { style: { border: '1px solid var(--theia-border)', borderRadius: 4, padding: 12 } },
                        React.createElement("h3", { style: { margin: '0 0 12px 0', fontSize: 12, borderBottom: '1px solid var(--theia-border)', paddingBottom: 4 } }, "Details"),
                        React.createElement("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 } },
                            React.createElement("div", { className: "adm-form-row", style: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 } },
                                React.createElement("span", { style: { fontSize: 10 } }, "Preferred Login"),
                                React.createElement("input", { className: "adm-input", placeholder: "Next", value: newAccount.login, onChange: e => setNewAccount({ ...newAccount, login: e.target.value }) })),
                            React.createElement("div", { className: "adm-form-row", style: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 } },
                                React.createElement("span", { style: { fontSize: 10 } }, "Group Name"),
                                React.createElement("input", { className: "adm-input", required: true, placeholder: "demo_group", value: newAccount.group_name, onChange: e => setNewAccount({ ...newAccount, group_name: e.target.value }) })),
                            React.createElement("div", { className: "adm-form-row", style: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 } },
                                React.createElement("span", { style: { fontSize: 10 } }, "Name"),
                                React.createElement("input", { className: "adm-input", required: true, placeholder: "First name", value: newAccount.name, onChange: e => setNewAccount({ ...newAccount, name: e.target.value }) })),
                            React.createElement("div", { className: "adm-form-row", style: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 } },
                                React.createElement("span", { style: { fontSize: 10 } }, "Last Name"),
                                React.createElement("input", { className: "adm-input", required: true, placeholder: "Last name", value: newAccount.last_name, onChange: e => setNewAccount({ ...newAccount, last_name: e.target.value }) })),
                            React.createElement("div", { className: "adm-form-row", style: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 } },
                                React.createElement("span", { style: { fontSize: 10 } }, "Middle Name"),
                                React.createElement("input", { className: "adm-input", placeholder: "Middle name", value: newAccount.middle_name, onChange: e => setNewAccount({ ...newAccount, middle_name: e.target.value }) })),
                            React.createElement("div", { className: "adm-form-row", style: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 } },
                                React.createElement("span", { style: { fontSize: 10 } }, "Company"),
                                React.createElement("input", { className: "adm-input", placeholder: "Company (optional)", value: newAccount.company, onChange: e => setNewAccount({ ...newAccount, company: e.target.value }) })),
                            React.createElement("div", { className: "adm-form-row", style: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 } },
                                React.createElement("span", { style: { fontSize: 10 } }, "E-Mail"),
                                React.createElement("input", { className: "adm-input", required: true, type: "email", placeholder: "email@address.com", value: newAccount.email, onChange: e => setNewAccount({ ...newAccount, email: e.target.value }) })),
                            React.createElement("div", { className: "adm-form-row", style: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 } },
                                React.createElement("span", { style: { fontSize: 10 } }, "Phone"),
                                React.createElement("input", { className: "adm-input", required: true, placeholder: "+1234567890", value: newAccount.phone, onChange: e => setNewAccount({ ...newAccount, phone: e.target.value }) })),
                            React.createElement("div", { className: "adm-form-row", style: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 } },
                                React.createElement("span", { style: { fontSize: 10 } }, "Country"),
                                React.createElement("input", { className: "adm-input", placeholder: "Country", value: newAccount.country, onChange: e => setNewAccount({ ...newAccount, country: e.target.value }) })),
                            React.createElement("div", { className: "adm-form-row", style: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 } },
                                React.createElement("span", { style: { fontSize: 10 } }, "State"),
                                React.createElement("input", { className: "adm-input", placeholder: "State/Region", value: newAccount.state, onChange: e => setNewAccount({ ...newAccount, state: e.target.value }) })),
                            React.createElement("div", { className: "adm-form-row", style: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 } },
                                React.createElement("span", { style: { fontSize: 10 } }, "City"),
                                React.createElement("input", { className: "adm-input", placeholder: "City", value: newAccount.city, onChange: e => setNewAccount({ ...newAccount, city: e.target.value }) })),
                            React.createElement("div", { className: "adm-form-row", style: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 } },
                                React.createElement("span", { style: { fontSize: 10 } }, "Zip Code"),
                                React.createElement("input", { className: "adm-input", placeholder: "Zip code", value: newAccount.zip_code, onChange: e => setNewAccount({ ...newAccount, zip_code: e.target.value }) }))),
                        React.createElement("div", { className: "adm-form-row", style: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4, marginTop: 10 } },
                            React.createElement("span", { style: { fontSize: 10 } }, "Address"),
                            React.createElement("input", { className: "adm-input", placeholder: "Street address", value: newAccount.address, onChange: e => setNewAccount({ ...newAccount, address: e.target.value }) }))),
                    React.createElement("div", { style: { border: '1px solid var(--theia-border)', borderRadius: 4, padding: 12 } },
                        React.createElement("h3", { style: { margin: '0 0 12px 0', fontSize: 12, borderBottom: '1px solid var(--theia-border)', paddingBottom: 4 } }, "Passwords"),
                        React.createElement("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 } },
                            React.createElement("div", { className: "adm-form-row", style: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 } },
                                React.createElement("span", { style: { fontSize: 10 } }, "Master Password"),
                                React.createElement("input", { className: "adm-input", required: true, type: "password", placeholder: "Master password", value: newAccount.password, onChange: e => setNewAccount({ ...newAccount, password: e.target.value }) })),
                            React.createElement("div", { className: "adm-form-row", style: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 } },
                                React.createElement("span", { style: { fontSize: 10 } }, "Investor Password"),
                                React.createElement("input", { className: "adm-input", type: "password", placeholder: "Investor password", value: newAccount.investor_password, onChange: e => setNewAccount({ ...newAccount, investor_password: e.target.value }) })),
                            React.createElement("div", { className: "adm-form-row", style: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 } },
                                React.createElement("span", { style: { fontSize: 10 } }, "Phone Password"),
                                React.createElement("input", { className: "adm-input", type: "password", placeholder: "Phone password", value: newAccount.phone_password, onChange: e => setNewAccount({ ...newAccount, phone_password: e.target.value }) })),
                            React.createElement("div", { className: "adm-form-row", style: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 } },
                                React.createElement("span", { style: { fontSize: 10 } }, "Initial Balance (USD)"),
                                React.createElement("input", { className: "adm-input", type: "number", required: true, placeholder: "10000", value: newAccount.initial_balance, onChange: e => setNewAccount({ ...newAccount, initial_balance: e.target.value }) }))))),
                React.createElement("div", { className: "adm-modal-footer", style: { flexShrink: 0 } },
                    React.createElement("button", { type: "submit", className: "adm-btn adm-btn-primary" }, "Create"),
                    React.createElement("button", { type: "button", className: "adm-btn", onClick: () => setShowCreateModal(false) }, "Cancel"))))),
        showEditModal && editingAccount && (React.createElement("div", { className: "adm-modal-overlay", style: { zIndex: 1200 }, onClick: () => setShowEditModal(false) },
            React.createElement("form", { className: "adm-modal", style: { width: 650, height: '65vh', display: 'flex', flexDirection: 'column' }, onClick: e => e.stopPropagation(), onSubmit: handleSaveEditAccount },
                React.createElement("div", { className: "adm-modal-header", style: { flexShrink: 0 } },
                    React.createElement("h2", null,
                        "Edit Account - #",
                        editingAccount.login),
                    React.createElement("button", { type: "button", className: "adm-modal-close", onClick: () => setShowEditModal(false) }, "\u00D7")),
                React.createElement("div", { style: { display: 'flex', background: 'var(--theia-editor-background)', borderBottom: '1px solid var(--theia-border)', padding: '0 12px', gap: 8, flexShrink: 0 } }, ['overview', 'personal', 'account', 'limits', 'security'].map((tabId) => (React.createElement("button", { key: tabId, type: "button", className: `adm-tab ${editingTab === tabId ? 'active' : ''}`, onClick: () => setEditingTab(tabId), style: {
                        border: 'none',
                        background: 'transparent',
                        padding: '8px 12px',
                        fontSize: 11,
                        cursor: 'pointer',
                        textTransform: 'capitalize',
                        borderBottom: editingTab === tabId ? '2px solid var(--theia-accentColor, #3498db)' : '2px solid transparent',
                        color: editingTab === tabId ? 'var(--theia-foreground)' : 'var(--theia-descriptionForeground)'
                    } }, tabId)))),
                React.createElement("div", { className: "adm-modal-body", style: { flex: 1, overflowY: 'auto', padding: 16 } },
                    editError && (React.createElement("div", { className: "adm-hint", style: { background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)', margin: '0 0 12px 0' } },
                        React.createElement("i", { className: "codicon codicon-error" }),
                        " ",
                        editError)),
                    editingTab === 'overview' && (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 12 } },
                        React.createElement("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, background: 'var(--theia-sideBarSectionHeader-background)', padding: 8, borderRadius: 4 } },
                            React.createElement("div", { style: { fontSize: 11 } },
                                React.createElement("strong", null, "Registered:"),
                                " ",
                                editingAccount.registered),
                            React.createElement("div", { style: { fontSize: 11 } },
                                React.createElement("strong", null, "Last access:"),
                                " ",
                                editingAccount.registered),
                            React.createElement("div", { style: { fontSize: 11 } },
                                React.createElement("strong", null, "Visitor ID:"),
                                " ",
                                editingAccount.login * 3),
                            React.createElement("div", { style: { fontSize: 11 } },
                                React.createElement("strong", null, "Affiliate:"),
                                " Web Portal")),
                        React.createElement("div", null,
                            React.createElement("h4", { style: { margin: '0 0 4px 0', fontSize: 11 } }, "Open Positions"),
                            React.createElement("div", { style: { border: '1px solid var(--theia-border)', maxHeight: 100, overflowY: 'auto' } },
                                React.createElement("table", { className: "adm-table", style: { fontSize: 10 } },
                                    React.createElement("thead", null,
                                        React.createElement("tr", null,
                                            React.createElement("th", null, "Symbol"),
                                            React.createElement("th", null, "Ticket"),
                                            React.createElement("th", null, "Type"),
                                            React.createElement("th", null, "Volume"),
                                            React.createElement("th", null, "Price"),
                                            React.createElement("th", null, "Profit"))),
                                    React.createElement("tbody", null,
                                        React.createElement("tr", null,
                                            React.createElement("td", null, "EURUSD"),
                                            React.createElement("td", null, "94812"),
                                            React.createElement("td", { style: { color: 'var(--theia-successForeground)' } }, "Buy"),
                                            React.createElement("td", null, "1.00"),
                                            React.createElement("td", null, "1.09210"),
                                            React.createElement("td", { className: "adm-pos" }, "+120.00")))))),
                        React.createElement("div", { style: { display: 'flex', justifyContent: 'space-between', padding: 8, background: 'var(--theia-sideBar-background)', border: '1px solid var(--theia-border)', fontSize: 11 } },
                            React.createElement("div", null,
                                "Balance: ",
                                React.createElement("strong", null, editingAccount.balance?.toFixed(2) || '0.00')),
                            React.createElement("div", null,
                                "Credit: ",
                                React.createElement("strong", null, "0.00")),
                            React.createElement("div", null,
                                "Commission: ",
                                React.createElement("strong", null, "0.00")),
                            React.createElement("div", null,
                                "Profit: ",
                                React.createElement("strong", null, "+120.00"))),
                        React.createElement("div", null,
                            React.createElement("h4", { style: { margin: '0 0 4px 0', fontSize: 11 } }, "Pending Orders"),
                            React.createElement("div", { style: { border: '1px solid var(--theia-border)', maxHeight: 100, overflowY: 'auto' } },
                                React.createElement("table", { className: "adm-table", style: { fontSize: 10 } },
                                    React.createElement("thead", null,
                                        React.createElement("tr", null,
                                            React.createElement("th", null, "Symbol"),
                                            React.createElement("th", null, "Ticket"),
                                            React.createElement("th", null, "Type"),
                                            React.createElement("th", null, "Volume"),
                                            React.createElement("th", null, "Price"))),
                                    React.createElement("tbody", null,
                                        React.createElement("tr", null,
                                            React.createElement("td", null, "GBPUSD"),
                                            React.createElement("td", null, "94813"),
                                            React.createElement("td", null, "Buy Limit"),
                                            React.createElement("td", null, "0.50"),
                                            React.createElement("td", null, "1.26100")))))))),
                    editingTab === 'personal' && (React.createElement("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 } },
                        React.createElement("div", { className: "adm-form-row", style: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 } },
                            React.createElement("span", { style: { fontSize: 10 } }, "Name"),
                            React.createElement("input", { className: "adm-input", value: editingAccount.name, onChange: e => setEditingAccount({ ...editingAccount, name: e.target.value }) })),
                        React.createElement("div", { className: "adm-form-row", style: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 } },
                            React.createElement("span", { style: { fontSize: 10 } }, "Last Name"),
                            React.createElement("input", { className: "adm-input", value: editingAccount.last_name, onChange: e => setEditingAccount({ ...editingAccount, last_name: e.target.value }) })),
                        React.createElement("div", { className: "adm-form-row", style: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 } },
                            React.createElement("span", { style: { fontSize: 10 } }, "Middle Name"),
                            React.createElement("input", { className: "adm-input", value: editingAccount.middle_name, onChange: e => setEditingAccount({ ...editingAccount, middle_name: e.target.value }) })),
                        React.createElement("div", { className: "adm-form-row", style: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 } },
                            React.createElement("span", { style: { fontSize: 10 } }, "Company"),
                            React.createElement("input", { className: "adm-input", value: editingAccount.company, onChange: e => setEditingAccount({ ...editingAccount, company: e.target.value }) })),
                        React.createElement("div", { className: "adm-form-row", style: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 } },
                            React.createElement("span", { style: { fontSize: 10 } }, "Language"),
                            React.createElement("input", { className: "adm-input", value: editingAccount.language, onChange: e => setEditingAccount({ ...editingAccount, language: e.target.value }) })),
                        React.createElement("div", { className: "adm-form-row", style: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 } },
                            React.createElement("span", { style: { fontSize: 10 } }, "Status (RE / NR)"),
                            React.createElement("select", { className: "adm-input", value: editingAccount.resident_status, onChange: e => setEditingAccount({ ...editingAccount, resident_status: e.target.value }) },
                                React.createElement("option", { value: "RE" }, "Resident (RE)"),
                                React.createElement("option", { value: "NR" }, "Non-Resident (NR)"))),
                        React.createElement("div", { className: "adm-form-row", style: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 } },
                            React.createElement("span", { style: { fontSize: 10 } }, "ID Number"),
                            React.createElement("input", { className: "adm-input", value: editingAccount.id_number, onChange: e => setEditingAccount({ ...editingAccount, id_number: e.target.value }) })),
                        React.createElement("div", { className: "adm-form-row", style: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 } },
                            React.createElement("span", { style: { fontSize: 10 } }, "MetaQuotes ID"),
                            React.createElement("input", { className: "adm-input", value: editingAccount.metaquotes_id, onChange: e => setEditingAccount({ ...editingAccount, metaquotes_id: e.target.value }) })),
                        React.createElement("div", { className: "adm-form-row", style: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 } },
                            React.createElement("span", { style: { fontSize: 10 } }, "E-Mail"),
                            React.createElement("input", { className: "adm-input", value: editingAccount.email, onChange: e => setEditingAccount({ ...editingAccount, email: e.target.value }) })),
                        React.createElement("div", { className: "adm-form-row", style: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 } },
                            React.createElement("span", { style: { fontSize: 10 } }, "Phone"),
                            React.createElement("input", { className: "adm-input", value: editingAccount.phone, onChange: e => setEditingAccount({ ...editingAccount, phone: e.target.value }) })),
                        React.createElement("div", { className: "adm-form-row", style: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 } },
                            React.createElement("span", { style: { fontSize: 10 } }, "Country"),
                            React.createElement("input", { className: "adm-input", value: editingAccount.country, onChange: e => setEditingAccount({ ...editingAccount, country: e.target.value }) })),
                        React.createElement("div", { className: "adm-form-row", style: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 } },
                            React.createElement("span", { style: { fontSize: 10 } }, "City"),
                            React.createElement("input", { className: "adm-input", value: editingAccount.city, onChange: e => setEditingAccount({ ...editingAccount, city: e.target.value }) })))),
                    editingTab === 'account' && (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 10 } },
                        React.createElement("div", { className: "adm-form-row" },
                            React.createElement("label", null, "Group"),
                            React.createElement("input", { className: "adm-input", value: editingAccount.group_name, onChange: e => setEditingAccount({ ...editingAccount, group_name: e.target.value }) })),
                        React.createElement("div", { className: "adm-form-row" },
                            React.createElement("label", null, "Leverage"),
                            React.createElement("input", { className: "adm-input", type: "number", value: editingAccount.leverage, onChange: e => setEditingAccount({ ...editingAccount, leverage: parseInt(e.target.value) || 100 }) })),
                        React.createElement("div", { className: "adm-form-row" },
                            React.createElement("label", null, "Color"),
                            React.createElement("input", { className: "adm-input", style: { width: 80, height: 28, padding: 0 }, type: "color", value: editingAccount.color, onChange: e => setEditingAccount({ ...editingAccount, color: e.target.value }) })),
                        React.createElement("div", { className: "adm-form-row" },
                            React.createElement("label", null, "Bank Account"),
                            React.createElement("input", { className: "adm-input", value: editingAccount.bank_account, onChange: e => setEditingAccount({ ...editingAccount, bank_account: e.target.value }) })),
                        React.createElement("div", { className: "adm-form-row" },
                            React.createElement("label", null, "Agent Account"),
                            React.createElement("input", { className: "adm-input", value: editingAccount.agent_account, onChange: e => setEditingAccount({ ...editingAccount, agent_account: e.target.value }) })),
                        React.createElement("div", { className: "adm-form-row", style: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 } },
                            React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' } },
                                React.createElement("input", { type: "checkbox", checked: editingAccount.enable_account, onChange: e => setEditingAccount({ ...editingAccount, enable_account: e.target.checked }) }),
                                React.createElement("span", null, "Enable this account")),
                            React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' } },
                                React.createElement("input", { type: "checkbox", checked: editingAccount.allow_change_password, onChange: e => setEditingAccount({ ...editingAccount, allow_change_password: e.target.checked }) }),
                                React.createElement("span", null, "Allow client to change password")),
                            React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' } },
                                React.createElement("input", { type: "checkbox", checked: editingAccount.enable_otp, onChange: e => setEditingAccount({ ...editingAccount, enable_otp: e.target.checked }) }),
                                React.createElement("span", null, "Enable one-time password (OTP)")),
                            React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' } },
                                React.createElement("input", { type: "checkbox", checked: editingAccount.change_pass_next_login, onChange: e => setEditingAccount({ ...editingAccount, change_pass_next_login: e.target.checked }) }),
                                React.createElement("span", null, "Force password change at next login"))))),
                    editingTab === 'limits' && (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 8 } },
                        React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' } },
                            React.createElement("input", { type: "checkbox", checked: editingAccount.show_to_regular_managers, onChange: e => setEditingAccount({ ...editingAccount, show_to_regular_managers: e.target.checked }) }),
                            React.createElement("span", null, "Show to regular managers")),
                        React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' } },
                            React.createElement("input", { type: "checkbox", checked: editingAccount.include_in_server_reports, onChange: e => setEditingAccount({ ...editingAccount, include_in_server_reports: e.target.checked }) }),
                            React.createElement("span", null, "Include in server reports")),
                        React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' } },
                            React.createElement("input", { type: "checkbox", checked: editingAccount.enable_daily_reports, onChange: e => setEditingAccount({ ...editingAccount, enable_daily_reports: e.target.checked }) }),
                            React.createElement("span", null, "Enable daily reports")),
                        React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' } },
                            React.createElement("input", { type: "checkbox", checked: editingAccount.enable_sponsored_vps, onChange: e => setEditingAccount({ ...editingAccount, enable_sponsored_vps: e.target.checked }) }),
                            React.createElement("span", null, "Enable sponsored VPS hosting")),
                        React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' } },
                            React.createElement("input", { type: "checkbox", checked: editingAccount.enable_trading, onChange: e => setEditingAccount({ ...editingAccount, enable_trading: e.target.checked }) }),
                            React.createElement("span", null, "Enable trading")),
                        React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' } },
                            React.createElement("input", { type: "checkbox", checked: editingAccount.enable_ea, onChange: e => setEditingAccount({ ...editingAccount, enable_ea: e.target.checked }) }),
                            React.createElement("span", null, "Enable algo trading (Expert Advisors)")),
                        React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' } },
                            React.createElement("input", { type: "checkbox", checked: editingAccount.enable_trailing_stops, onChange: e => setEditingAccount({ ...editingAccount, enable_trailing_stops: e.target.checked }) }),
                            React.createElement("span", null, "Enable trailing stops")),
                        React.createElement("div", { className: "adm-form-row", style: { marginTop: 6 } },
                            React.createElement("label", null, "Limit positions value"),
                            React.createElement("input", { className: "adm-input", placeholder: "unlimited", value: editingAccount.limit_position_value, onChange: e => setEditingAccount({ ...editingAccount, limit_position_value: e.target.value }) })),
                        React.createElement("div", { className: "adm-form-row" },
                            React.createElement("label", null, "Limit active orders"),
                            React.createElement("input", { className: "adm-input", placeholder: "default", value: editingAccount.limit_active_orders, onChange: e => setEditingAccount({ ...editingAccount, limit_active_orders: e.target.value }) })))),
                    editingTab === 'security' && (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 10 } },
                        React.createElement("div", { style: { border: '1px solid var(--theia-border)', padding: 10, borderRadius: 4 } },
                            React.createElement("span", { style: { fontSize: 11, fontWeight: 'bold' } }, "Master Password"),
                            React.createElement("div", { style: { display: 'flex', gap: 6, marginTop: 6 } },
                                React.createElement("input", { className: "adm-input", type: "password", placeholder: "New master password", value: editingAccount.master_pass, onChange: e => setEditingAccount({ ...editingAccount, master_pass: e.target.value }) }),
                                React.createElement("button", { type: "button", className: "adm-btn", onClick: () => setEditingAccount({ ...editingAccount, master_pass: Math.random().toString(36).slice(-8) + 'A1!' }) }, "Generate"))),
                        React.createElement("div", { style: { border: '1px solid var(--theia-border)', padding: 10, borderRadius: 4 } },
                            React.createElement("span", { style: { fontSize: 11, fontWeight: 'bold' } }, "Investor Password"),
                            React.createElement("div", { style: { display: 'flex', gap: 6, marginTop: 6 } },
                                React.createElement("input", { className: "adm-input", type: "password", placeholder: "New investor password", value: editingAccount.investor_pass, onChange: e => setEditingAccount({ ...editingAccount, investor_pass: e.target.value }) }))),
                        React.createElement("div", { style: { border: '1px solid var(--theia-border)', padding: 10, borderRadius: 4 } },
                            React.createElement("span", { style: { fontSize: 11, fontWeight: 'bold' } }, "Phone Password"),
                            React.createElement("div", { style: { display: 'flex', gap: 6, marginTop: 6 } },
                                React.createElement("input", { className: "adm-input", type: "password", placeholder: "New phone password", value: editingAccount.phone_pass, onChange: e => setEditingAccount({ ...editingAccount, phone_pass: e.target.value }) }))),
                        React.createElement("div", { className: "adm-form-row" },
                            React.createElement("label", null, "OTP Secret Key"),
                            React.createElement("input", { className: "adm-input", value: editingAccount.otp_secret, onChange: e => setEditingAccount({ ...editingAccount, otp_secret: e.target.value }) }))))),
                React.createElement("div", { className: "adm-modal-footer", style: { flexShrink: 0 } },
                    React.createElement("button", { type: "submit", className: "adm-btn adm-btn-primary" }, "Save Changes"),
                    React.createElement("button", { type: "button", className: "adm-btn", onClick: () => setShowEditModal(false) }, "Cancel"))))),
        React.createElement("div", { className: "adm-statusbar" },
            React.createElement("span", null,
                "Accounts: ",
                filtered.length),
            React.createElement("span", { className: "adm-sep" }, "|"),
            React.createElement("span", null,
                "Active: ",
                filtered.filter(c => c.status === 0).length),
            React.createElement("span", { className: "adm-sep" }, "|"),
            React.createElement("span", null,
                "ReadOnly/Disabled: ",
                filtered.filter(c => c.status !== 0).length))));
}
exports.ClientsPage = ClientsPage;
//# sourceMappingURL=ClientsPage.js.map