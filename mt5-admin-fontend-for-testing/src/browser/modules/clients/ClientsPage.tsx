// @ts-nocheck
import * as React from 'react';
import { API } from '../api';

interface Client {
    login: number;
    group_name: string;
    balance: number;
    equity: number;
    margin: number;
    free_margin: number;
    leverage: number;
    status: number; // 0 = Normal, 1 = ReadOnly, 2 = Blocked
    settings_json?: any;
}

const STATUS_MAP: Record<number, string> = {
    0: 'active',
    1: 'readonly',
    2: 'disabled'
};

const STATUS_COLOR: Record<string, string> = {
    active:   'var(--theia-successForeground)',
    disabled: 'var(--theia-errorForeground)',
    readonly: '#f0ad4e',
};

interface Props {
    initialTab?: 'accounts' | 'clients' | 'managers' | 'allocations';
}

export function ClientsPage({ initialTab = 'accounts' }: Props): React.ReactElement {
    const [clients, setClients] = React.useState<Client[]>([]);
    const [selected, setSelected] = React.useState<number | null>(null);
    const [filter, setFilter] = React.useState('');
    const [tab, setTab] = React.useState(initialTab);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState<string | null>(null);

    // Context Menu State
    const [contextMenu, setContextMenu] = React.useState<{ x: number; y: number; login: number | null } | null>(null);

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
    const [createError, setCreateError] = React.useState<string | null>(null);

    // Edit Modal State
    const [showEditModal, setShowEditModal] = React.useState(false);
    const [editingTab, setEditingTab] = React.useState<'overview' | 'personal' | 'account' | 'limits' | 'security'>('overview');
    const [editingAccount, setEditingAccount] = React.useState<any>(null);
    const [editError, setEditError] = React.useState<string | null>(null);

    const loadAccounts = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await API.getAccounts();
            setClients(data);
        } catch (err: any) {
            setError(err.message || 'Failed to fetch accounts from broker server.');
        } finally {
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

    const handleCreateAccount = async (e: React.FormEvent) => {
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
            await API.createAccount(payload);
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
        } catch (err: any) {
            setCreateError(err.message || 'Failed to create account.');
        }
    };

    const handleOpenEdit = (login: number) => {
        const client = clients.find(c => c.login === login);
        if (!client) return;

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

    const handleSaveEditAccount = async (e: React.FormEvent) => {
        e.preventDefault();
        setEditError(null);
        try {
            // In a real application, we would call an update API.
            // Let's call the API if it supports PUT /admin/accounts or update locally
            const payload = {
                login: editingAccount.login,
                group_name: editingAccount.group_name,
                leverage: editingAccount.leverage,
                status: editingAccount.enable_account ? 0 : 2, // Map to active/disabled
                settings_json: {
                    ...editingAccount
                }
            };
            
            // Call API update if available, or fallback
            if (API.updateAccount) {
                await API.updateAccount(payload.login, payload);
            } else {
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
        } catch (err: any) {
            setEditError(err.message || 'Failed to update account.');
        }
    };

    const handleDeleteAccount = async (login: number) => {
        if (!confirm(`Are you sure you want to delete account #${login}?`)) return;
        try {
            await API.deleteAccount(login);
            setSelected(null);
            await loadAccounts();
        } catch (err: any) {
            alert(err.message || 'Failed to delete account.');
        }
    };

    const handleContextMenu = (e: React.MouseEvent, login: number | null) => {
        e.preventDefault();
        setContextMenu({
            x: e.clientX,
            y: e.clientY,
            login
        });
    };

    const filtered = clients.filter(c =>
        String(c.login).includes(filter) ||
        c.group_name.toLowerCase().includes(filter.toLowerCase())
    );

    const selectedClient = clients.find(c => c.login === selected);

    return (
        <div className="adm-page" onContextMenu={e => handleContextMenu(e, null)}>
            <div className="adm-tabs">
                {(['accounts', 'clients', 'managers', 'allocations'] as const).map(t => (
                    <button key={t} className={`adm-tab ${tab === t ? 'active' : ''}`} onClick={() => setTab(t)}>
                        {t === 'accounts' ? 'Trading Accounts' : t.charAt(0).toUpperCase() + t.slice(1)}
                    </button>
                ))}
            </div>

            <div className="adm-toolbar">
                <button className="adm-btn adm-btn-primary" onClick={() => setShowCreateModal(true)}>
                    <i className="codicon codicon-add" /> New Account
                </button>
                {selected !== null && (
                    <>
                        <button className="adm-btn" onClick={() => handleOpenEdit(selected)}>
                            <i className="codicon codicon-edit" /> Edit
                        </button>
                        <button className="adm-btn" onClick={() => handleDeleteAccount(selected)} style={{ color: 'var(--theia-errorForeground)' }}>
                            <i className="codicon codicon-trash" /> Delete
                        </button>
                    </>
                )}
                <button className="adm-btn" onClick={loadAccounts} title="Reload list">
                    <i className="codicon codicon-refresh" /> Refresh
                </button>
                <div className="adm-toolbar-sep" />
                <div className="adm-search-wrap">
                    <i className="codicon codicon-search" />
                    <input className="adm-search" placeholder="Search login or group..." value={filter} onChange={e => setFilter(e.target.value)} />
                </div>
            </div>

            {error && (
                <div className="adm-hint" style={{ background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)' }}>
                    <i className="codicon codicon-error" /> {error}
                </div>
            )}

            <div className="adm-split-view" style={{ flex: 1, minHeight: 0 }}>
                <div className="adm-table-wrap" style={{ flex: selectedClient ? '0 0 60%' : '1', overflowY: 'auto' }}>
                    {loading ? (
                        <div style={{ padding: 20, textAlign: 'center', opacity: 0.7 }}>Loading accounts...</div>
                    ) : filtered.length === 0 ? (
                        <div style={{ padding: 20, textAlign: 'center', opacity: 0.7 }}>No accounts found. Use "New Account" to create one.</div>
                    ) : (
                        <table className="adm-table">
                            <thead>
                                <tr>
                                    <th>Login</th>
                                    <th>Group Name</th>
                                    <th>Balance</th>
                                    <th>Equity</th>
                                    <th>Free Margin</th>
                                    <th>Leverage</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filtered.map(c => {
                                    const statusStr = STATUS_MAP[c.status] || 'unknown';
                                    return (
                                        <tr 
                                            key={c.login} 
                                            className={selected === c.login ? 'selected' : ''} 
                                            onClick={() => setSelected(c.login)}
                                            onDoubleClick={() => handleOpenEdit(c.login)}
                                            onContextMenu={e => handleContextMenu(e, c.login)}
                                        >
                                            <td><strong>{c.login}</strong></td>
                                            <td><code className="adm-code">{c.group_name}</code></td>
                                            <td className="adm-num">{c.balance.toLocaleString('en', { minimumFractionDigits: 2 })}</td>
                                            <td className={`adm-num ${c.equity >= c.balance ? 'adm-pos' : 'adm-neg'}`}>{c.equity.toLocaleString('en', { minimumFractionDigits: 2 })}</td>
                                            <td className="adm-num">{c.free_margin.toLocaleString('en', { minimumFractionDigits: 2 })}</td>
                                            <td>1:{c.leverage}</td>
                                            <td><span className="adm-dot" style={{ background: STATUS_COLOR[statusStr] || '#888' }} />{statusStr}</td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    )}
                </div>

                {selectedClient && (
                    <div className="adm-detail-panel" style={{ overflowY: 'auto' }}>
                        <div className="adm-detail-header">
                            <span>Account #{selectedClient.login}</span>
                            <button className="adm-icon-btn" onClick={() => setSelected(null)}><i className="codicon codicon-close" /></button>
                        </div>
                        <div className="adm-detail-body">
                            <div className="adm-detail-section">General Information</div>
                            <div className="adm-kv"><span>Login</span><strong>{selectedClient.login}</strong></div>
                            <div className="adm-kv"><span>Group</span><code className="adm-code">{selectedClient.group_name}</code></div>
                            <div className="adm-kv"><span>Leverage</span><span>1:{selectedClient.leverage}</span></div>
                            
                            <div className="adm-detail-section">Balance & Margins</div>
                            <div className="adm-kv"><span>Balance</span><strong>{(selectedClient.balance ?? 0).toFixed(2)} USD</strong></div>
                            <div className="adm-kv"><span>Equity</span><strong className={(selectedClient.equity ?? 0) >= (selectedClient.balance ?? 0) ? 'adm-pos' : 'adm-neg'}>{(selectedClient.equity ?? 0).toFixed(2)} USD</strong></div>
                            <div className="adm-kv"><span>Margin</span><span>{(selectedClient.margin ?? 0).toFixed(2)} USD</span></div>
                            <div className="adm-kv"><span>Free Margin</span><span>{(selectedClient.free_margin ?? 0).toFixed(2)} USD</span></div>
                            
                            <div className="adm-detail-section">Security & Status</div>
                            <div className="adm-kv"><span>Status</span><span style={{ color: STATUS_COLOR[STATUS_MAP[selectedClient.status]] || '#888' }}>{STATUS_MAP[selectedClient.status] || 'unknown'}</span></div>
                        </div>
                        <div className="adm-detail-footer">
                            <button className="adm-btn adm-btn-primary" onClick={() => handleOpenEdit(selectedClient.login)}>Edit Details</button>
                        </div>
                    </div>
                )}
            </div>

            {/* Context Menu Render */}
            {contextMenu && (
                <div 
                    className="adm-context-menu"
                    style={{
                        position: 'fixed',
                        top: contextMenu.y,
                        left: contextMenu.x,
                        background: 'var(--theia-menu-background, #252526)',
                        border: '1px solid var(--theia-menu-border, #454545)',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.5)',
                        zIndex: 10000,
                        padding: '4px 0',
                        minWidth: 170
                    }}
                    onClick={e => e.stopPropagation()}
                >
                    <div 
                        className="adm-menu-item" 
                        onClick={() => { setShowCreateModal(true); setContextMenu(null); }}
                        style={{ padding: '6px 12px', fontSize: 11, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}
                    >
                        <i className="codicon codicon-add" /> New Account
                    </div>
                    {contextMenu.login !== null ? (
                        <>
                            <div 
                                className="adm-menu-item" 
                                onClick={() => { handleOpenEdit(contextMenu.login!); setContextMenu(null); }}
                                style={{ padding: '6px 12px', fontSize: 11, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}
                            >
                                <i className="codicon codicon-edit" /> Edit
                            </div>
                            <div 
                                className="adm-menu-item" 
                                onClick={() => {
                                    const c = clients.find(cl => cl.login === contextMenu.login);
                                    if (c) alert(`Open group settings for: ${c.group_name}`);
                                    setContextMenu(null);
                                }}
                                style={{ padding: '6px 12px', fontSize: 11, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}
                            >
                                <i className="codicon codicon-organization" /> Edit Group
                            </div>
                            <div 
                                className="adm-menu-item" 
                                onClick={() => {
                                    alert(`Edit manager profile linked to login ${contextMenu.login}`);
                                    setContextMenu(null);
                                }}
                                style={{ padding: '6px 12px', fontSize: 11, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}
                            >
                                <i className="codicon codicon-person" /> Edit Manager
                            </div>
                            <div 
                                className="adm-menu-item" 
                                onClick={() => { handleDeleteAccount(contextMenu.login!); setContextMenu(null); }}
                                style={{ padding: '6px 12px', fontSize: 11, cursor: 'pointer', color: 'var(--theia-errorForeground)', display: 'flex', alignItems: 'center', gap: 6 }}
                            >
                                <i className="codicon codicon-trash" /> Delete
                            </div>
                            <div style={{ height: 1, background: 'var(--theia-menu-border, #454545)', margin: '4px 0' }} />
                            <div 
                                className="adm-menu-item" 
                                onClick={() => {
                                    alert(`Move account #${contextMenu.login} to archive`);
                                    setContextMenu(null);
                                }}
                                style={{ padding: '6px 12px', fontSize: 11, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}
                            >
                                <i className="codicon codicon-archive" /> Move to Archive
                            </div>
                            <div 
                                className="adm-menu-item" 
                                onClick={() => {
                                    alert(`Checking balance consistency for account #${contextMenu.login}`);
                                    setContextMenu(null);
                                }}
                                style={{ padding: '6px 12px', fontSize: 11, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}
                            >
                                <i className="codicon codicon-check" /> Check Balance
                            </div>
                            <div 
                                className="adm-menu-item" 
                                onClick={() => {
                                    alert(`Fixing balance fields for account #${contextMenu.login}`);
                                    setContextMenu(null);
                                }}
                                style={{ padding: '6px 12px', fontSize: 11, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}
                            >
                                <i className="codicon codicon-tools" /> Fix Balance
                            </div>
                            <div style={{ height: 1, background: 'var(--theia-menu-border, #454545)', margin: '4px 0' }} />
                            <div 
                                className="adm-menu-item" 
                                onClick={() => {
                                    navigator.clipboard.writeText(`Login: ${contextMenu.login}`);
                                    setContextMenu(null);
                                }}
                                style={{ padding: '6px 12px', fontSize: 11, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}
                            >
                                <i className="codicon codicon-copy" /> Copy Lines
                            </div>
                            <div 
                                className="adm-menu-item" 
                                onClick={() => {
                                    navigator.clipboard.writeText(String(contextMenu.login));
                                    setContextMenu(null);
                                }}
                                style={{ padding: '6px 12px', fontSize: 11, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}
                            >
                                <i className="codicon codicon-list-unordered" /> Copy Login
                            </div>
                            <div style={{ height: 1, background: 'var(--theia-menu-border, #454545)', margin: '4px 0' }} />
                            <div 
                                className="adm-menu-item" 
                                onClick={() => {
                                    alert(`Exporting trade account #${contextMenu.login} data to CSV/HTML`);
                                    setContextMenu(null);
                                }}
                                style={{ padding: '6px 12px', fontSize: 11, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}
                            >
                                <i className="codicon codicon-cloud-upload" /> Export Account
                            </div>
                            <div 
                                className="adm-menu-item" 
                                onClick={() => {
                                    alert(`Opening email compose window for: ${contextMenu.login}`);
                                    setContextMenu(null);
                                }}
                                style={{ padding: '6px 12px', fontSize: 11, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}
                            >
                                <i className="codicon codicon-mail" /> Send E-Mail
                            </div>
                            <div 
                                className="adm-menu-item" 
                                onClick={() => {
                                    alert(`Loading server journal entries for account #${contextMenu.login}`);
                                    setContextMenu(null);
                                }}
                                style={{ padding: '6px 12px', fontSize: 11, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}
                            >
                                <i className="codicon codicon-output" /> View Journal
                            </div>
                        </>
                    ) : (
                        <>
                            <div style={{ height: 1, background: 'var(--theia-menu-border, #454545)', margin: '4px 0' }} />
                            <div 
                                className="adm-menu-item" 
                                onClick={() => { loadAccounts(); setContextMenu(null); }}
                                style={{ padding: '6px 12px', fontSize: 11, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}
                            >
                                <i className="codicon codicon-refresh" /> Request Accounts
                            </div>
                            <div 
                                className="adm-menu-item" 
                                onClick={() => { alert('Import accounts from CSV file'); setContextMenu(null); }}
                                style={{ padding: '6px 12px', fontSize: 11, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}
                            >
                                <i className="codicon codicon-cloud-download" /> Import from File
                            </div>
                        </>
                    )}
                </div>
            )}

            {/* CREATE ACCOUNT DIALOG (Boxed layout: Details & Passwords) */}
            {showCreateModal && (
                <div className="adm-modal-overlay" style={{ zIndex: 1200 }} onClick={() => setShowCreateModal(false)}>
                    <form 
                        className="adm-modal" 
                        style={{ width: 650, height: '65vh', display: 'flex', flexDirection: 'column' }} 
                        onClick={e => e.stopPropagation()} 
                        onSubmit={handleCreateAccount}
                    >
                        <div className="adm-modal-header" style={{ flexShrink: 0 }}>
                            <h2>Create New Trade Account</h2>
                            <button type="button" className="adm-modal-close" onClick={() => setShowCreateModal(false)}>×</button>
                        </div>
                        <div className="adm-modal-body" style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 16, padding: 16 }}>
                            {createError && (
                                <div className="adm-hint" style={{ background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)', margin: 0 }}>
                                    <i className="codicon codicon-error" /> {createError}
                                </div>
                            )}

                            {/* Details Box */}
                            <div style={{ border: '1px solid var(--theia-border)', borderRadius: 4, padding: 12 }}>
                                <h3 style={{ margin: '0 0 12px 0', fontSize: 12, borderBottom: '1px solid var(--theia-border)', paddingBottom: 4 }}>Details</h3>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                                    <div className="adm-form-row" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                                        <span style={{ fontSize: 10 }}>Preferred Login</span>
                                        <input className="adm-input" placeholder="Next" value={newAccount.login} onChange={e => setNewAccount({ ...newAccount, login: e.target.value })} />
                                    </div>
                                    <div className="adm-form-row" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                                        <span style={{ fontSize: 10 }}>Group Name</span>
                                        <input className="adm-input" required placeholder="demo_group" value={newAccount.group_name} onChange={e => setNewAccount({ ...newAccount, group_name: e.target.value })} />
                                    </div>
                                    <div className="adm-form-row" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                                        <span style={{ fontSize: 10 }}>Name</span>
                                        <input className="adm-input" required placeholder="First name" value={newAccount.name} onChange={e => setNewAccount({ ...newAccount, name: e.target.value })} />
                                    </div>
                                    <div className="adm-form-row" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                                        <span style={{ fontSize: 10 }}>Last Name</span>
                                        <input className="adm-input" required placeholder="Last name" value={newAccount.last_name} onChange={e => setNewAccount({ ...newAccount, last_name: e.target.value })} />
                                    </div>
                                    <div className="adm-form-row" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                                        <span style={{ fontSize: 10 }}>Middle Name</span>
                                        <input className="adm-input" placeholder="Middle name" value={newAccount.middle_name} onChange={e => setNewAccount({ ...newAccount, middle_name: e.target.value })} />
                                    </div>
                                    <div className="adm-form-row" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                                        <span style={{ fontSize: 10 }}>Company</span>
                                        <input className="adm-input" placeholder="Company (optional)" value={newAccount.company} onChange={e => setNewAccount({ ...newAccount, company: e.target.value })} />
                                    </div>
                                    <div className="adm-form-row" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                                        <span style={{ fontSize: 10 }}>E-Mail</span>
                                        <input className="adm-input" required type="email" placeholder="email@address.com" value={newAccount.email} onChange={e => setNewAccount({ ...newAccount, email: e.target.value })} />
                                    </div>
                                    <div className="adm-form-row" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                                        <span style={{ fontSize: 10 }}>Phone</span>
                                        <input className="adm-input" required placeholder="+1234567890" value={newAccount.phone} onChange={e => setNewAccount({ ...newAccount, phone: e.target.value })} />
                                    </div>
                                    <div className="adm-form-row" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                                        <span style={{ fontSize: 10 }}>Country</span>
                                        <input className="adm-input" placeholder="Country" value={newAccount.country} onChange={e => setNewAccount({ ...newAccount, country: e.target.value })} />
                                    </div>
                                    <div className="adm-form-row" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                                        <span style={{ fontSize: 10 }}>State</span>
                                        <input className="adm-input" placeholder="State/Region" value={newAccount.state} onChange={e => setNewAccount({ ...newAccount, state: e.target.value })} />
                                    </div>
                                    <div className="adm-form-row" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                                        <span style={{ fontSize: 10 }}>City</span>
                                        <input className="adm-input" placeholder="City" value={newAccount.city} onChange={e => setNewAccount({ ...newAccount, city: e.target.value })} />
                                    </div>
                                    <div className="adm-form-row" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                                        <span style={{ fontSize: 10 }}>Zip Code</span>
                                        <input className="adm-input" placeholder="Zip code" value={newAccount.zip_code} onChange={e => setNewAccount({ ...newAccount, zip_code: e.target.value })} />
                                    </div>
                                </div>
                                <div className="adm-form-row" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4, marginTop: 10 }}>
                                    <span style={{ fontSize: 10 }}>Address</span>
                                    <input className="adm-input" placeholder="Street address" value={newAccount.address} onChange={e => setNewAccount({ ...newAccount, address: e.target.value })} />
                                </div>
                            </div>

                            {/* Passwords Box */}
                            <div style={{ border: '1px solid var(--theia-border)', borderRadius: 4, padding: 12 }}>
                                <h3 style={{ margin: '0 0 12px 0', fontSize: 12, borderBottom: '1px solid var(--theia-border)', paddingBottom: 4 }}>Passwords</h3>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                                    <div className="adm-form-row" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                                        <span style={{ fontSize: 10 }}>Master Password</span>
                                        <input className="adm-input" required type="password" placeholder="Master password" value={newAccount.password} onChange={e => setNewAccount({ ...newAccount, password: e.target.value })} />
                                    </div>
                                    <div className="adm-form-row" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                                        <span style={{ fontSize: 10 }}>Investor Password</span>
                                        <input className="adm-input" type="password" placeholder="Investor password" value={newAccount.investor_password} onChange={e => setNewAccount({ ...newAccount, investor_password: e.target.value })} />
                                    </div>
                                    <div className="adm-form-row" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                                        <span style={{ fontSize: 10 }}>Phone Password</span>
                                        <input className="adm-input" type="password" placeholder="Phone password" value={newAccount.phone_password} onChange={e => setNewAccount({ ...newAccount, phone_password: e.target.value })} />
                                    </div>
                                    <div className="adm-form-row" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                                        <span style={{ fontSize: 10 }}>Initial Balance (USD)</span>
                                        <input className="adm-input" type="number" required placeholder="10000" value={newAccount.initial_balance} onChange={e => setNewAccount({ ...newAccount, initial_balance: e.target.value })} />
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="adm-modal-footer" style={{ flexShrink: 0 }}>
                            <button type="submit" className="adm-btn adm-btn-primary">Create</button>
                            <button type="button" className="adm-btn" onClick={() => setShowCreateModal(false)}>Cancel</button>
                        </div>
                    </form>
                </div>
            )}

            {/* EDIT ACCOUNT DIALOG (Tabs: Overview, Personal, Account, Limits, Security) */}
            {showEditModal && editingAccount && (
                <div className="adm-modal-overlay" style={{ zIndex: 1200 }} onClick={() => setShowEditModal(false)}>
                    <form 
                        className="adm-modal" 
                        style={{ width: 650, height: '65vh', display: 'flex', flexDirection: 'column' }} 
                        onClick={e => e.stopPropagation()} 
                        onSubmit={handleSaveEditAccount}
                    >
                        <div className="adm-modal-header" style={{ flexShrink: 0 }}>
                            <h2>Edit Account - #{editingAccount.login}</h2>
                            <button type="button" className="adm-modal-close" onClick={() => setShowEditModal(false)}>×</button>
                        </div>

                        {/* Dialogue Tab Selector */}
                        <div style={{ display: 'flex', background: 'var(--theia-editor-background)', borderBottom: '1px solid var(--theia-border)', padding: '0 12px', gap: 8, flexShrink: 0 }}>
                            {(['overview', 'personal', 'account', 'limits', 'security'] as const).map((tabId) => (
                                <button
                                    key={tabId}
                                    type="button"
                                    className={`adm-tab ${editingTab === tabId ? 'active' : ''}`}
                                    onClick={() => setEditingTab(tabId)}
                                    style={{
                                        border: 'none',
                                        background: 'transparent',
                                        padding: '8px 12px',
                                        fontSize: 11,
                                        cursor: 'pointer',
                                        textTransform: 'capitalize',
                                        borderBottom: editingTab === tabId ? '2px solid var(--theia-accentColor, #3498db)' : '2px solid transparent',
                                        color: editingTab === tabId ? 'var(--theia-foreground)' : 'var(--theia-descriptionForeground)'
                                    }}
                                >
                                    {tabId}
                                </button>
                            ))}
                        </div>

                        <div className="adm-modal-body" style={{ flex: 1, overflowY: 'auto', padding: 16 }}>
                            {editError && (
                                <div className="adm-hint" style={{ background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)', margin: '0 0 12px 0' }}>
                                    <i className="codicon codicon-error" /> {editError}
                                </div>
                            )}

                            {/* --- OVERVIEW TAB --- */}
                            {editingTab === 'overview' && (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, background: 'var(--theia-sideBarSectionHeader-background)', padding: 8, borderRadius: 4 }}>
                                        <div style={{ fontSize: 11 }}><strong>Registered:</strong> {editingAccount.registered}</div>
                                        <div style={{ fontSize: 11 }}><strong>Last access:</strong> {editingAccount.registered}</div>
                                        <div style={{ fontSize: 11 }}><strong>Visitor ID:</strong> {editingAccount.login * 3}</div>
                                        <div style={{ fontSize: 11 }}><strong>Affiliate:</strong> Web Portal</div>
                                    </div>

                                    {/* Open Positions Grid */}
                                    <div>
                                        <h4 style={{ margin: '0 0 4px 0', fontSize: 11 }}>Open Positions</h4>
                                        <div style={{ border: '1px solid var(--theia-border)', maxHeight: 100, overflowY: 'auto' }}>
                                            <table className="adm-table" style={{ fontSize: 10 }}>
                                                <thead>
                                                    <tr>
                                                        <th>Symbol</th>
                                                        <th>Ticket</th>
                                                        <th>Type</th>
                                                        <th>Volume</th>
                                                        <th>Price</th>
                                                        <th>Profit</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <tr>
                                                        <td>EURUSD</td>
                                                        <td>94812</td>
                                                        <td style={{ color: 'var(--theia-successForeground)' }}>Buy</td>
                                                        <td>1.00</td>
                                                        <td>1.09210</td>
                                                        <td className="adm-pos">+120.00</td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>

                                    {/* Account State Bar */}
                                    <div style={{ display: 'flex', justifyContent: 'space-between', padding: 8, background: 'var(--theia-sideBar-background)', border: '1px solid var(--theia-border)', fontSize: 11 }}>
                                        <div>Balance: <strong>{editingAccount.balance?.toFixed(2) || '0.00'}</strong></div>
                                        <div>Credit: <strong>0.00</strong></div>
                                        <div>Commission: <strong>0.00</strong></div>
                                        <div>Profit: <strong>+120.00</strong></div>
                                    </div>

                                    {/* Pending Orders Grid */}
                                    <div>
                                        <h4 style={{ margin: '0 0 4px 0', fontSize: 11 }}>Pending Orders</h4>
                                        <div style={{ border: '1px solid var(--theia-border)', maxHeight: 100, overflowY: 'auto' }}>
                                            <table className="adm-table" style={{ fontSize: 10 }}>
                                                <thead>
                                                    <tr>
                                                        <th>Symbol</th>
                                                        <th>Ticket</th>
                                                        <th>Type</th>
                                                        <th>Volume</th>
                                                        <th>Price</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <tr>
                                                        <td>GBPUSD</td>
                                                        <td>94813</td>
                                                        <td>Buy Limit</td>
                                                        <td>0.50</td>
                                                        <td>1.26100</td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* --- PERSONAL TAB --- */}
                            {editingTab === 'personal' && (
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                                    <div className="adm-form-row" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                                        <span style={{ fontSize: 10 }}>Name</span>
                                        <input className="adm-input" value={editingAccount.name} onChange={e => setEditingAccount({ ...editingAccount, name: e.target.value })} />
                                    </div>
                                    <div className="adm-form-row" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                                        <span style={{ fontSize: 10 }}>Last Name</span>
                                        <input className="adm-input" value={editingAccount.last_name} onChange={e => setEditingAccount({ ...editingAccount, last_name: e.target.value })} />
                                    </div>
                                    <div className="adm-form-row" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                                        <span style={{ fontSize: 10 }}>Middle Name</span>
                                        <input className="adm-input" value={editingAccount.middle_name} onChange={e => setEditingAccount({ ...editingAccount, middle_name: e.target.value })} />
                                    </div>
                                    <div className="adm-form-row" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                                        <span style={{ fontSize: 10 }}>Company</span>
                                        <input className="adm-input" value={editingAccount.company} onChange={e => setEditingAccount({ ...editingAccount, company: e.target.value })} />
                                    </div>
                                    <div className="adm-form-row" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                                        <span style={{ fontSize: 10 }}>Language</span>
                                        <input className="adm-input" value={editingAccount.language} onChange={e => setEditingAccount({ ...editingAccount, language: e.target.value })} />
                                    </div>
                                    <div className="adm-form-row" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                                        <span style={{ fontSize: 10 }}>Status (RE / NR)</span>
                                        <select className="adm-input" value={editingAccount.resident_status} onChange={e => setEditingAccount({ ...editingAccount, resident_status: e.target.value })}>
                                            <option value="RE">Resident (RE)</option>
                                            <option value="NR">Non-Resident (NR)</option>
                                        </select>
                                    </div>
                                    <div className="adm-form-row" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                                        <span style={{ fontSize: 10 }}>ID Number</span>
                                        <input className="adm-input" value={editingAccount.id_number} onChange={e => setEditingAccount({ ...editingAccount, id_number: e.target.value })} />
                                    </div>
                                    <div className="adm-form-row" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                                        <span style={{ fontSize: 10 }}>MetaQuotes ID</span>
                                        <input className="adm-input" value={editingAccount.metaquotes_id} onChange={e => setEditingAccount({ ...editingAccount, metaquotes_id: e.target.value })} />
                                    </div>
                                    <div className="adm-form-row" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                                        <span style={{ fontSize: 10 }}>E-Mail</span>
                                        <input className="adm-input" value={editingAccount.email} onChange={e => setEditingAccount({ ...editingAccount, email: e.target.value })} />
                                    </div>
                                    <div className="adm-form-row" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                                        <span style={{ fontSize: 10 }}>Phone</span>
                                        <input className="adm-input" value={editingAccount.phone} onChange={e => setEditingAccount({ ...editingAccount, phone: e.target.value })} />
                                    </div>
                                    <div className="adm-form-row" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                                        <span style={{ fontSize: 10 }}>Country</span>
                                        <input className="adm-input" value={editingAccount.country} onChange={e => setEditingAccount({ ...editingAccount, country: e.target.value })} />
                                    </div>
                                    <div className="adm-form-row" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                                        <span style={{ fontSize: 10 }}>City</span>
                                        <input className="adm-input" value={editingAccount.city} onChange={e => setEditingAccount({ ...editingAccount, city: e.target.value })} />
                                    </div>
                                </div>
                            )}

                            {/* --- ACCOUNT TAB --- */}
                            {editingTab === 'account' && (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                                    <div className="adm-form-row">
                                        <label>Group</label>
                                        <input className="adm-input" value={editingAccount.group_name} onChange={e => setEditingAccount({ ...editingAccount, group_name: e.target.value })} />
                                    </div>
                                    <div className="adm-form-row">
                                        <label>Leverage</label>
                                        <input className="adm-input" type="number" value={editingAccount.leverage} onChange={e => setEditingAccount({ ...editingAccount, leverage: parseInt(e.target.value) || 100 })} />
                                    </div>
                                    <div className="adm-form-row">
                                        <label>Color</label>
                                        <input className="adm-input" style={{ width: 80, height: 28, padding: 0 }} type="color" value={editingAccount.color} onChange={e => setEditingAccount({ ...editingAccount, color: e.target.value })} />
                                    </div>
                                    <div className="adm-form-row">
                                        <label>Bank Account</label>
                                        <input className="adm-input" value={editingAccount.bank_account} onChange={e => setEditingAccount({ ...editingAccount, bank_account: e.target.value })} />
                                    </div>
                                    <div className="adm-form-row">
                                        <label>Agent Account</label>
                                        <input className="adm-input" value={editingAccount.agent_account} onChange={e => setEditingAccount({ ...editingAccount, agent_account: e.target.value })} />
                                    </div>
                                    <div className="adm-form-row" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                                        <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                                            <input type="checkbox" checked={editingAccount.enable_account} onChange={e => setEditingAccount({ ...editingAccount, enable_account: e.target.checked })} />
                                            <span>Enable this account</span>
                                        </label>
                                        <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                                            <input type="checkbox" checked={editingAccount.allow_change_password} onChange={e => setEditingAccount({ ...editingAccount, allow_change_password: e.target.checked })} />
                                            <span>Allow client to change password</span>
                                        </label>
                                        <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                                            <input type="checkbox" checked={editingAccount.enable_otp} onChange={e => setEditingAccount({ ...editingAccount, enable_otp: e.target.checked })} />
                                            <span>Enable one-time password (OTP)</span>
                                        </label>
                                        <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                                            <input type="checkbox" checked={editingAccount.change_pass_next_login} onChange={e => setEditingAccount({ ...editingAccount, change_pass_next_login: e.target.checked })} />
                                            <span>Force password change at next login</span>
                                        </label>
                                    </div>
                                </div>
                            )}

                            {/* --- LIMITS TAB --- */}
                            {editingTab === 'limits' && (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                                    <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                                        <input type="checkbox" checked={editingAccount.show_to_regular_managers} onChange={e => setEditingAccount({ ...editingAccount, show_to_regular_managers: e.target.checked })} />
                                        <span>Show to regular managers</span>
                                    </label>
                                    <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                                        <input type="checkbox" checked={editingAccount.include_in_server_reports} onChange={e => setEditingAccount({ ...editingAccount, include_in_server_reports: e.target.checked })} />
                                        <span>Include in server reports</span>
                                    </label>
                                    <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                                        <input type="checkbox" checked={editingAccount.enable_daily_reports} onChange={e => setEditingAccount({ ...editingAccount, enable_daily_reports: e.target.checked })} />
                                        <span>Enable daily reports</span>
                                    </label>
                                    <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                                        <input type="checkbox" checked={editingAccount.enable_sponsored_vps} onChange={e => setEditingAccount({ ...editingAccount, enable_sponsored_vps: e.target.checked })} />
                                        <span>Enable sponsored VPS hosting</span>
                                    </label>
                                    <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                                        <input type="checkbox" checked={editingAccount.enable_trading} onChange={e => setEditingAccount({ ...editingAccount, enable_trading: e.target.checked })} />
                                        <span>Enable trading</span>
                                    </label>
                                    <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                                        <input type="checkbox" checked={editingAccount.enable_ea} onChange={e => setEditingAccount({ ...editingAccount, enable_ea: e.target.checked })} />
                                        <span>Enable algo trading (Expert Advisors)</span>
                                    </label>
                                    <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                                        <input type="checkbox" checked={editingAccount.enable_trailing_stops} onChange={e => setEditingAccount({ ...editingAccount, enable_trailing_stops: e.target.checked })} />
                                        <span>Enable trailing stops</span>
                                    </label>
                                    <div className="adm-form-row" style={{ marginTop: 6 }}>
                                        <label>Limit positions value</label>
                                        <input className="adm-input" placeholder="unlimited" value={editingAccount.limit_position_value} onChange={e => setEditingAccount({ ...editingAccount, limit_position_value: e.target.value })} />
                                    </div>
                                    <div className="adm-form-row">
                                        <label>Limit active orders</label>
                                        <input className="adm-input" placeholder="default" value={editingAccount.limit_active_orders} onChange={e => setEditingAccount({ ...editingAccount, limit_active_orders: e.target.value })} />
                                    </div>
                                </div>
                            )}

                            {/* --- SECURITY TAB --- */}
                            {editingTab === 'security' && (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                                    <div style={{ border: '1px solid var(--theia-border)', padding: 10, borderRadius: 4 }}>
                                        <span style={{ fontSize: 11, fontWeight: 'bold' }}>Master Password</span>
                                        <div style={{ display: 'flex', gap: 6, marginTop: 6 }}>
                                            <input className="adm-input" type="password" placeholder="New master password" value={editingAccount.master_pass} onChange={e => setEditingAccount({ ...editingAccount, master_pass: e.target.value })} />
                                            <button type="button" className="adm-btn" onClick={() => setEditingAccount({ ...editingAccount, master_pass: Math.random().toString(36).slice(-8) + 'A1!' })}>Generate</button>
                                        </div>
                                    </div>
                                    <div style={{ border: '1px solid var(--theia-border)', padding: 10, borderRadius: 4 }}>
                                        <span style={{ fontSize: 11, fontWeight: 'bold' }}>Investor Password</span>
                                        <div style={{ display: 'flex', gap: 6, marginTop: 6 }}>
                                            <input className="adm-input" type="password" placeholder="New investor password" value={editingAccount.investor_pass} onChange={e => setEditingAccount({ ...editingAccount, investor_pass: e.target.value })} />
                                        </div>
                                    </div>
                                    <div style={{ border: '1px solid var(--theia-border)', padding: 10, borderRadius: 4 }}>
                                        <span style={{ fontSize: 11, fontWeight: 'bold' }}>Phone Password</span>
                                        <div style={{ display: 'flex', gap: 6, marginTop: 6 }}>
                                            <input className="adm-input" type="password" placeholder="New phone password" value={editingAccount.phone_pass} onChange={e => setEditingAccount({ ...editingAccount, phone_pass: e.target.value })} />
                                        </div>
                                    </div>
                                    <div className="adm-form-row">
                                        <label>OTP Secret Key</label>
                                        <input className="adm-input" value={editingAccount.otp_secret} onChange={e => setEditingAccount({ ...editingAccount, otp_secret: e.target.value })} />
                                    </div>
                                </div>
                            )}
                        </div>

                        <div className="adm-modal-footer" style={{ flexShrink: 0 }}>
                            <button type="submit" className="adm-btn adm-btn-primary">Save Changes</button>
                            <button type="button" className="adm-btn" onClick={() => setShowEditModal(false)}>Cancel</button>
                        </div>
                    </form>
                </div>
            )}

            <div className="adm-statusbar">
                <span>Accounts: {filtered.length}</span>
                <span className="adm-sep">|</span>
                <span>Active: {filtered.filter(c => c.status === 0).length}</span>
                <span className="adm-sep">|</span>
                <span>ReadOnly/Disabled: {filtered.filter(c => c.status !== 0).length}</span>
            </div>
        </div>
    );
}
