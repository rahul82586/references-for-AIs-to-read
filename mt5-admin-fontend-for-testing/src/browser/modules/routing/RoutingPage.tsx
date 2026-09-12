// @ts-nocheck
import * as React from 'react';
import { API } from '../api';

const ACTION_COLOR: Record<string, string> = {
    INSTANT_EXECUTE: '#27ae60',
    TO_DEALER:       '#9b59b6',
    TO_GATEWAY:      '#3498db',
    REJECT:          '#e74c3c',
};

export function RoutingPage(): React.ReactElement {
    const [rules, setRules] = React.useState<any[]>([]);
    const [gateways, setGateways] = React.useState<any[]>([]);
    const [accounts, setAccounts] = React.useState<any[]>([]);
    const [selected, setSelected] = React.useState<number | null>(null);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState<string | null>(null);
    
    // Modal states
    const [showModal, setShowModal] = React.useState(false);
    const [modalMode, setModalMode] = React.useState<'create' | 'edit'>('create');
    const [modalTab, setModalTab] = React.useState<'common' | 'dealers'>('common');
    
    const [ruleForm, setRuleForm] = React.useState({
        id: null as number | null,
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
    const [modalError, setModalError] = React.useState<string | null>(null);

    const loadData = async () => {
        setLoading(true);
        setError(null);
        try {
            const rulesData = await API.getRoutingRules();
            setRules(rulesData);
            const gwsData = await API.getGateways();
            setGateways(gwsData);
            const accsData = await API.getAccounts();
            setAccounts(accsData);
        } catch (err: any) {
            setError(err.message || 'Failed to fetch routing rules, gateways, or accounts.');
        } finally {
            setLoading(false);
        }
    };

    React.useEffect(() => {
        loadData();
    }, []);

    const toggleRule = async (id: number, currentEnabled: boolean) => {
        setError(null);
        try {
            if (currentEnabled) {
                await API.disableRoutingRule(id);
            } else {
                await API.enableRoutingRule(id);
            }
            await loadData();
        } catch (err: any) {
            setError(err.message || 'Failed to toggle rule state.');
        }
    };

    const handleDelete = async () => {
        if (!selected) return;
        if (!confirm('Are you sure you want to delete this routing rule?')) return;
        setError(null);
        try {
            await API.deleteRoutingRule(selected);
            setSelected(null);
            await loadData();
        } catch (err: any) {
            setError(err.message || 'Failed to delete routing rule.');
        }
    };

    const moveUp = async (id: number) => {
        const idx = rules.findIndex(r => r.id === id);
        if (idx <= 0) return;
        
        const newOrderIds = rules.map(r => r.id);
        [newOrderIds[idx - 1], newOrderIds[idx]] = [newOrderIds[idx], newOrderIds[idx - 1]];
        
        setError(null);
        try {
            await API.reorderRoutingRules(newOrderIds);
            await loadData();
        } catch (err: any) {
            setError(err.message || 'Failed to reorder rules.');
        }
    };

    const moveDown = async (id: number) => {
        const idx = rules.findIndex(r => r.id === id);
        if (idx < 0 || idx >= rules.length - 1) return;
        
        const newOrderIds = rules.map(r => r.id);
        [newOrderIds[idx], newOrderIds[idx + 1]] = [newOrderIds[idx + 1], newOrderIds[idx]];
        
        setError(null);
        try {
            await API.reorderRoutingRules(newOrderIds);
            await loadData();
        } catch (err: any) {
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

    const openEditModal = (r: any) => {
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

    const handleSubmitRule = async (e: React.FormEvent) => {
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
                await API.createRoutingRule(payload);
            } else {
                await API.updateRoutingRule(ruleForm.id!, payload);
            }
            setShowModal(false);
            await loadData();
        } catch (err: any) {
            setModalError(err.message || 'Failed to save routing rule.');
        }
    };

    const selectedRule = rules.find(r => r.id === selected);

    // Selected gateway info inside the Dealers tab
    const ruleGateway = gateways.find(g => String(g.id) === ruleForm.gateway_id);
    const ruleManager = accounts.find(a => String(a.login) === ruleForm.gateway_id);

    return (
        <div className="adm-page">
            <div className="adm-toolbar">
                <button className="adm-btn adm-btn-primary" onClick={openCreateModal}>
                    <i className="codicon codicon-add" /> Add Rule
                </button>
                <button className="adm-btn" disabled={!selectedRule} onClick={() => selectedRule && openEditModal(selectedRule)}>
                    <i className="codicon codicon-edit" /> Edit Rule
                </button>
                <button className="adm-btn adm-btn-danger" disabled={selected === null} onClick={handleDelete}>
                    <i className="codicon codicon-trash" /> Delete
                </button>
                <div className="adm-toolbar-sep" />
                <button className="adm-btn" disabled={selected === null || rules.findIndex(r => r.id === selected) === 0} onClick={() => selected && moveUp(selected)}>
                    <i className="codicon codicon-arrow-up" /> Move Up
                </button>
                <button className="adm-btn" disabled={selected === null || rules.findIndex(r => r.id === selected) === rules.length - 1} onClick={() => selected && moveDown(selected)}>
                    <i className="codicon codicon-arrow-down" /> Move Down
                </button>
                <div className="adm-toolbar-sep" />
                <button className="adm-btn" onClick={loadData} title="Reload data">
                    <i className="codicon codicon-refresh" /> Refresh
                </button>
                <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 6 }}>
                    <a 
                        href="file:///c:/Users/DELL/Downloads/server3/MT5-Administrator/MetaTrader-5-Trading-Platform/Platform-Setup/Routing.md" 
                        target="_blank" 
                        rel="noreferrer"
                        className="adm-btn"
                        style={{ display: 'inline-flex', alignItems: 'center', gap: 4, textDecoration: 'none', color: 'inherit' }}
                    >
                        <i className="codicon codicon-book" /> Routing Guide
                    </a>
                </div>
            </div>

            <div className="adm-hint">
                <i className="codicon codicon-info" />
                Rules are executed <strong>top-to-bottom</strong> based on priority. First matching rule wins. Double-click to Edit.
            </div>

            {error && (
                <div className="adm-hint" style={{ background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)' }}>
                    <i className="codicon codicon-error" /> {error}
                </div>
            )}

            <div className="adm-split-view">
                <div className="adm-table-wrap" style={{ flex: selectedRule ? '0 0 55%' : '1' }}>
                    {loading ? (
                        <div style={{ padding: 20, textAlign: 'center', opacity: 0.7 }}>Loading routing rules...</div>
                    ) : rules.length === 0 ? (
                        <div style={{ padding: 20, textAlign: 'center', opacity: 0.7 }}>No routing rules configured. Create one to route orders.</div>
                    ) : (
                        <table className="adm-table">
                            <thead>
                                <tr>
                                    <th>Priority</th>
                                    <th>Enabled</th>
                                    <th>Rule Name</th>
                                    <th>Action</th>
                                    <th>Match Specs</th>
                                    <th>Gateway Route</th>
                                </tr>
                            </thead>
                            <tbody>
                                {rules.map((r, idx) => (
                                    <tr 
                                        key={r.id} 
                                        className={`${selected === r.id ? 'selected' : ''} ${!r.is_enabled ? 'adm-row-disabled' : ''}`} 
                                        onClick={() => setSelected(r.id)}
                                        onDoubleClick={() => openEditModal(r)}
                                    >
                                        <td style={{ opacity: 0.5 }}>{idx + 1}</td>
                                        <td>
                                            <button
                                                className={`adm-toggle ${r.is_enabled ? 'on' : 'off'}`}
                                                onClick={e => { e.stopPropagation(); toggleRule(r.id, r.is_enabled); }}
                                            >
                                                {r.is_enabled ? '✓' : '✗'}
                                            </button>
                                        </td>
                                        <td><strong>{r.name}</strong></td>
                                        <td>
                                            <span className="adm-tag" style={{ color: ACTION_COLOR[r.action] || '#aaa', border: `1px solid ${(ACTION_COLOR[r.action] || '#aaa')}55` }}>
                                                {r.action}
                                            </span>
                                        </td>
                                        <td>
                                            {r.match_symbols.length > 0 && <span className="adm-condition-chip" title="Symbols">Sym: {r.match_symbols.join(',')}</span>}
                                            {r.match_groups.length > 0 && <span className="adm-condition-chip" title="Groups">Grp: {r.match_groups.join(',')}</span>}
                                            {r.match_accounts.length > 0 && <span className="adm-condition-chip" title="Accounts">Acc: {r.match_accounts.join(',')}</span>}
                                            {r.match_volume_min !== null && <span className="adm-condition-chip">Min Vol: {r.match_volume_min}</span>}
                                            {r.match_volume_max !== null && <span className="adm-condition-chip">Max Vol: {r.match_volume_max}</span>}
                                            {r.match_symbols.length === 0 && r.match_groups.length === 0 && r.match_accounts.length === 0 && r.match_volume_min === null && r.match_volume_max === null && (
                                                <span style={{ opacity: 0.5 }}>— Catchall —</span>
                                            )}
                                        </td>
                                        <td>
                                            {r.gateway_id ? (
                                                <strong>{gateways.find(g => g.id === r.gateway_id)?.name || `Gateway #${r.gateway_id}`}</strong>
                                            ) : (
                                                <span style={{ opacity: 0.5 }}>—</span>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>

                {selectedRule && (
                    <div className="adm-detail-panel">
                        <div className="adm-detail-header">
                            <span>Rule Detail: {selectedRule.name}</span>
                            <button className="adm-icon-btn" onClick={() => setSelected(null)}><i className="codicon codicon-close" /></button>
                        </div>
                        <div className="adm-detail-body">
                            <div className="adm-detail-section">General</div>
                            <div className="adm-kv"><span>Name</span><strong>{selectedRule.name}</strong></div>
                            <div className="adm-kv"><span>Priority</span><span>{rules.findIndex(r => r.id === selectedRule.id) + 1}</span></div>
                            <div className="adm-kv"><span>Action</span><span style={{ color: ACTION_COLOR[selectedRule.action] }}>{selectedRule.action}</span></div>
                            <div className="adm-kv">
                                <span>Gateway Route</span>
                                <strong>{gateways.find(g => g.id === selectedRule.gateway_id)?.name || 'Local Matching (B-Book)'}</strong>
                            </div>
                            <div className="adm-kv"><span>Delay Seconds</span><span>{selectedRule.delay_seconds || 0} s</span></div>

                            <div className="adm-detail-section">Filter Rules</div>
                            <div className="adm-kv"><span>Symbols</span><span>{selectedRule.match_symbols.length > 0 ? selectedRule.match_symbols.join(', ') : 'All'}</span></div>
                            <div className="adm-kv"><span>Groups</span><span>{selectedRule.match_groups.length > 0 ? selectedRule.match_groups.join(', ') : 'All'}</span></div>
                            <div className="adm-kv"><span>Accounts</span><span>{selectedRule.match_accounts && selectedRule.match_accounts.length > 0 ? selectedRule.match_accounts.join(', ') : 'All'}</span></div>
                            <div className="adm-kv"><span>Order Types</span><span>{selectedRule.match_order_types.length > 0 ? selectedRule.match_order_types.join(', ') : 'All'}</span></div>
                            <div className="adm-kv"><span>Min Vol</span><span>{selectedRule.match_volume_min !== null ? selectedRule.match_volume_min : 'Any'}</span></div>
                            <div className="adm-kv"><span>Max Vol</span><span>{selectedRule.match_volume_max !== null ? selectedRule.match_volume_max : 'Any'}</span></div>
                        </div>
                    </div>
                )}
            </div>

            {showModal && (
                <div className="adm-modal-overlay" onClick={() => setShowModal(false)}>
                    <form 
                        className="adm-modal" 
                        style={{ width: 750, height: '65vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }} 
                        onClick={e => e.stopPropagation()} 
                        onSubmit={handleSubmitRule}
                    >
                        <div className="adm-modal-header">
                            <h2>
                                <i className="codicon codicon-split-horizontal" style={{ marginRight: 8, color: '#3498db' }} />
                                {modalMode === 'create' ? 'Add Routing Rule' : `Edit Routing Rule — ${ruleForm.name}`}
                            </h2>
                            <button type="button" className="adm-modal-close" onClick={() => setShowModal(false)}>×</button>
                        </div>
                        
                        {/* Modal tabs */}
                        <div className="adm-tabs" style={{ padding: '0 16px', borderBottom: '1px solid var(--theia-border)' }}>
                            <button 
                                type="button" 
                                className={`adm-tab ${modalTab === 'common' ? 'active' : ''}`}
                                onClick={() => setModalTab('common')}
                            >
                                Common
                            </button>
                            <button 
                                type="button" 
                                className={`adm-tab ${modalTab === 'dealers' ? 'active' : ''}`}
                                onClick={() => setModalTab('dealers')}
                            >
                                Dealers
                            </button>
                        </div>

                        <div className="adm-modal-body" style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
                            {modalError && (
                                <div className="adm-hint" style={{ background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)', margin: '0 0 16px 0' }}>
                                    <i className="codicon codicon-error" /> {modalError}
                                </div>
                            )}

                            {modalTab === 'common' ? (
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 24px' }}>
                                    
                                    {/* Left Column - General Setup */}
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                                        <div style={{ fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2 }}>
                                            General Properties
                                        </div>
                                        <div className="adm-form-row">
                                            <label>Rule Name</label>
                                            <input className="adm-input" style={{ width: '100%', height: 20 }} required placeholder="e.g. Route EURUSD to LP" value={ruleForm.name} onChange={e => setRuleForm({ ...ruleForm, name: e.target.value })} />
                                        </div>
                                        <div className="adm-form-row">
                                            <label>Execution Action</label>
                                            <select className="adm-select" style={{ width: '100%', height: 20 }} value={ruleForm.action} onChange={e => setRuleForm({ ...ruleForm, action: e.target.value })}>
                                                <option value="INSTANT_EXECUTE">Instant Execute (B-Book)</option>
                                                <option value="TO_GATEWAY">To Gateway (A-Book)</option>
                                                <option value="TO_DEALER">To Dealer Queue (Manual confirmation)</option>
                                                <option value="REJECT">Reject (Block Execution)</option>
                                            </select>
                                        </div>
                                        <div className="adm-form-row">
                                            <label>Delay Seconds</label>
                                            <input className="adm-input" style={{ width: '100%', height: 20 }} type="number" placeholder="0" value={ruleForm.delay_seconds} onChange={e => setRuleForm({ ...ruleForm, delay_seconds: e.target.value })} />
                                        </div>
                                        <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', marginTop: 8, fontSize: 11 }}>
                                            <input type="checkbox" checked={ruleForm.is_enabled} onChange={e => setRuleForm({ ...ruleForm, is_enabled: e.target.checked })} />
                                            Enable this rule
                                        </label>
                                    </div>

                                    {/* Right Column - Filtering criteria */}
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                                        <div style={{ fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2 }}>
                                            Filtering Criteria (Comma-separated)
                                        </div>
                                        <div className="adm-form-row">
                                            <label>Match Groups</label>
                                            <input className="adm-input" style={{ width: '100%', height: 20 }} placeholder="e.g. demo_group, real_group" value={ruleForm.match_groups} onChange={e => setRuleForm({ ...ruleForm, match_groups: e.target.value })} />
                                        </div>
                                        <div className="adm-form-row">
                                            <label>Match Symbols</label>
                                            <input className="adm-input" style={{ width: '100%', height: 20 }} placeholder="e.g. EURUSD, GBPUSD" value={ruleForm.match_symbols} onChange={e => setRuleForm({ ...ruleForm, match_symbols: e.target.value })} />
                                        </div>
                                        <div className="adm-form-row">
                                            <label>Match Accounts (Logins)</label>
                                            <input className="adm-input" style={{ width: '100%', height: 20 }} placeholder="e.g. 50080, 50081" value={ruleForm.match_accounts} onChange={e => setRuleForm({ ...ruleForm, match_accounts: e.target.value })} />
                                        </div>
                                        <div className="adm-form-row">
                                            <label>Match Order Types</label>
                                            <input className="adm-input" style={{ width: '100%', height: 20 }} placeholder="e.g. BUY, SELL" value={ruleForm.match_order_types} onChange={e => setRuleForm({ ...ruleForm, match_order_types: e.target.value })} />
                                        </div>
                                        <div style={{ display: 'flex', gap: 8 }}>
                                            <div className="adm-form-row" style={{ flex: 1 }}>
                                                <label>Min Volume</label>
                                                <input className="adm-input" style={{ width: '100%', height: 20 }} type="number" step="0.01" placeholder="Any" value={ruleForm.match_volume_min} onChange={e => setRuleForm({ ...ruleForm, match_volume_min: e.target.value })} />
                                            </div>
                                            <div className="adm-form-row" style={{ flex: 1 }}>
                                                <label>Max Volume</label>
                                                <input className="adm-input" style={{ width: '100%', height: 20 }} type="number" step="0.01" placeholder="Any" value={ruleForm.match_volume_max} onChange={e => setRuleForm({ ...ruleForm, match_volume_max: e.target.value })} />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ) : (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                                    <div style={{ fontSize: 11, color: 'var(--theia-descriptionForeground)', borderBottom: '1px solid var(--theia-border)', paddingBottom: 4 }}>
                                        Configure Dealers (Managers) or ECN Gateways associated with this routing rule.
                                    </div>

                                    {/* Action execution warning/helper */}
                                    {ruleForm.action !== 'TO_DEALER' && ruleForm.action !== 'TO_GATEWAY' ? (
                                        <div className="adm-hint" style={{ background: 'var(--theia-inputValidation-infoBackground)', color: 'var(--theia-inputValidation-infoForeground)' }}>
                                            <i className="codicon codicon-info" /> The Dealers/Gateways list is only active when the rule action is set to <strong>Process to dealers</strong> or <strong>To Gateway (A-Book)</strong>.
                                        </div>
                                    ) : ruleForm.action === 'TO_DEALER' ? (
                                        <>
                                            {/* Dealers Table */}
                                            <div style={{ border: '1px solid var(--theia-border)', borderRadius: 4 }}>
                                                <table className="adm-table" style={{ margin: 0 }}>
                                                    <thead>
                                                        <tr>
                                                            <th>Manager Login</th>
                                                            <th>Group Name</th>
                                                            <th>Balance</th>
                                                            <th>Leverage</th>
                                                            <th>Status</th>
                                                            <th style={{ width: 80 }}>Action</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody>
                                                        {ruleManager ? (
                                                            <tr>
                                                                <td><strong>{ruleManager.login}</strong></td>
                                                                <td><strong>{ruleManager.group_name}</strong></td>
                                                                <td>{parseFloat(ruleManager.balance || 0).toFixed(2)} USD</td>
                                                                <td>1:{ruleManager.leverage}</td>
                                                                <td>
                                                                    <span className="adm-status-dot online" style={{ marginRight: 6 }} />
                                                                    Dealing
                                                                </td>
                                                                <td>
                                                                    <button 
                                                                        type="button" 
                                                                        className="adm-btn" 
                                                                        style={{ padding: '2px 6px', color: 'var(--theia-errorForeground)' }}
                                                                        onClick={() => setRuleForm({ ...ruleForm, gateway_id: '' })}
                                                                    >
                                                                        <i className="codicon codicon-trash" /> Delete
                                                                    </button>
                                                                </td>
                                                            </tr>
                                                        ) : (
                                                            <tr>
                                                                <td colSpan={6} style={{ textAlign: 'center', opacity: 0.6, padding: 16 }}>
                                                                    No dealer accounts currently assigned. Use the selection below to assign one.
                                                                </td>
                                                            </tr>
                                                        )}
                                                    </tbody>
                                                </table>
                                            </div>

                                            {/* Dealer assign selector */}
                                            {!ruleForm.gateway_id && (
                                                <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginTop: 12 }}>
                                                    <span style={{ fontSize: 11 }}>Select Manager Account:</span>
                                                    <select 
                                                        className="adm-select" 
                                                        style={{ width: 260, height: 22 }}
                                                        value="" 
                                                        onChange={e => {
                                                            if (e.target.value) {
                                                                setRuleForm({ ...ruleForm, gateway_id: e.target.value });
                                                            }
                                                        }}
                                                    >
                                                        <option value="">Choose Dealing Manager...</option>
                                                        {accounts.filter(a => a.group_name && a.group_name.toLowerCase().includes('manager')).map(m => (
                                                            <option key={m.login} value={m.login}>
                                                                {m.login} ({m.group_name})
                                                            </option>
                                                        ))}
                                                    </select>
                                                </div>
                                            )}
                                        </>
                                    ) : (
                                        <>
                                            {/* Gateways table */}
                                            <div style={{ border: '1px solid var(--theia-border)', borderRadius: 4 }}>
                                                <table className="adm-table" style={{ margin: 0 }}>
                                                    <thead>
                                                        <tr>
                                                            <th>Dealer/Gateway ID</th>
                                                            <th>Gateway Name</th>
                                                            <th>Type</th>
                                                            <th>Connection Host</th>
                                                            <th>Status</th>
                                                            <th style={{ width: 80 }}>Action</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody>
                                                        {ruleGateway ? (
                                                            <tr>
                                                                <td><strong>{ruleGateway.id}</strong></td>
                                                                <td><strong>{ruleGateway.name}</strong></td>
                                                                <td><span className="adm-tag" style={{ fontSize: 9 }}>{ruleGateway.type}</span></td>
                                                                <td><code className="adm-code">{ruleGateway.host || 'localhost'}</code></td>
                                                                <td>
                                                                    <span className={`adm-status-dot ${ruleGateway.is_active ? 'online' : 'offline'}`} style={{ marginRight: 6 }} />
                                                                    {ruleGateway.is_active ? 'Active' : 'Offline'}
                                                                </td>
                                                                <td>
                                                                    <button 
                                                                        type="button" 
                                                                        className="adm-btn" 
                                                                        style={{ padding: '2px 6px', color: 'var(--theia-errorForeground)' }}
                                                                        onClick={() => setRuleForm({ ...ruleForm, gateway_id: '' })}
                                                                    >
                                                                        <i className="codicon codicon-trash" /> Delete
                                                                    </button>
                                                                </td>
                                                            </tr>
                                                        ) : (
                                                            <tr>
                                                                <td colSpan={6} style={{ textAlign: 'center', opacity: 0.6, padding: 16 }}>
                                                                    No gateways currently assigned. Use the selection below to assign one.
                                                                </td>
                                                            </tr>
                                                        )}
                                                    </tbody>
                                                </table>
                                            </div>

                                            {/* Gateway assign selector */}
                                            {!ruleForm.gateway_id && (
                                                <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginTop: 12 }}>
                                                    <span style={{ fontSize: 11 }}>Select Gateway:</span>
                                                    <select 
                                                        className="adm-select" 
                                                        style={{ width: 220, height: 22 }}
                                                        value="" 
                                                        onChange={e => {
                                                            if (e.target.value) {
                                                                setRuleForm({ ...ruleForm, gateway_id: e.target.value });
                                                            }
                                                        }}
                                                    >
                                                        <option value="">Choose LP Gateway...</option>
                                                        {gateways.map(g => (
                                                            <option key={g.id} value={g.id}>
                                                                {g.name} ({g.type}) — {g.host || 'localhost'}
                                                            </option>
                                                        ))}
                                                    </select>
                                                </div>
                                            )}
                                        </>
                                    )}
                                </div>
                            )}
                        </div>

                        <div className="adm-modal-footer">
                            <button type="submit" className="adm-btn adm-btn-primary">
                                {modalMode === 'create' ? 'Create Rule' : 'Save Changes'}
                            </button>
                            <button type="button" className="adm-btn" onClick={() => setShowModal(false)}>
                                Cancel
                            </button>
                        </div>
                    </form>
                </div>
            )}

            <div className="adm-statusbar">
                <span>Total Rules: {rules.length}</span>
                <span className="adm-sep">|</span>
                <span>Active: {rules.filter(r => r.is_enabled).length}</span>
            </div>
        </div>
    );
}
