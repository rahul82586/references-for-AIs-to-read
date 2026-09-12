import * as React from 'react';
import { API } from '../api';

const STATUS_COLOR: Record<string, string> = {
    connected: 'var(--theia-successForeground)',
    disconnected: 'var(--theia-descriptionForeground)',
    error: 'var(--theia-errorForeground)',
};
const TYPE_COLOR: Record<string, string> = {
    FIX: '#3498db', MT5: '#9b59b6', REST: '#27ae60', Custom: '#f39c12'
};

export function GatewaysPage(): React.ReactElement {
    const [gateways, setGateways] = React.useState<any[]>([]);
    const [availableGroups, setAvailableGroups] = React.useState<any[]>([]);
    const [selected, setSelected] = React.useState<number | null>(null);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState<string | null>(null);

    // Modal state
    const [showModal, setShowModal] = React.useState(false);
    const [modalMode, setModalMode] = React.useState<'create' | 'edit'>('create');
    const [activeTab, setActiveTab] = React.useState<'general' | 'groups' | 'translations'>('general');
    
    const [gatewayForm, setGatewayForm] = React.useState({
        id: null as number | null,
        name: '',
        type: 'FIX',
        host: '',
        port: '',
        username: '',
        api_key: '',
        is_active: true
    });
    
    // Groups state matching standard MT5 tab settings
    const [gatewayGroups, setGatewayGroups] = React.useState<string[]>(['*']);
    const [allowImportBalances, setAllowImportBalances] = React.useState(false);
    const [selectedGroupIdx, setSelectedGroupIdx] = React.useState<number | null>(null);
    const [editingGroupIdx, setEditingGroupIdx] = React.useState<number | null>(null);
    const [editingGroupVal, setEditingGroupVal] = React.useState('');

    // Translations state
    const [translations, setTranslations] = React.useState<any[]>([]);
    const [newRule, setNewRule] = React.useState({
        symbol: '',
        source: '',
        bid_adj: 0,
        ask_adj: 0
    });
    
    const [modalError, setModalError] = React.useState<string | null>(null);

    const loadGateways = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await API.getGateways();
            // Filter out price feeders (they will be displayed on DataFeedsPage.tsx)
            const filtered = data.filter((g: any) => !g.type.startsWith('Feeder_'));
            setGateways(filtered);
        } catch (err: any) {
            setError(err.message || 'Failed to load gateways.');
        } finally {
            setLoading(false);
        }
    };

    const loadDbGroups = async () => {
        try {
            const data = await API.getGroups();
            setAvailableGroups(data);
        } catch (e) {
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

    const openEditModal = (g: any) => {
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
            } catch (err) {
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

    const handleRemoveRule = (idx: number) => {
        setTranslations(translations.filter((_, i) => i !== idx));
    };

    const handleSubmit = async (e: React.FormEvent) => {
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
                await API.createGateway(payload);
            } else {
                await API.updateGateway(gatewayForm.id!, payload);
            }
            setShowModal(false);
            await loadGateways();
        } catch (err: any) {
            setModalError(err.message || 'Failed to save gateway.');
        }
    };

    const handleTestGateway = async () => {
        if (!selected) return;
        setError(null);
        try {
            const resp = await API.testGateway(selected);
            alert(`Gateway Connection Test: ${resp.message}`);
        } catch (err: any) {
            setError(err.message || 'Gateway test failed.');
        }
    };

    const selectedGateway = gateways.find(g => g.id === selected);

    return (
        <div className="adm-page">
            <div className="adm-toolbar">
                <button className="adm-btn adm-btn-primary" onClick={openCreateModal}>
                    <i className="codicon codicon-add" /> Add Gateway
                </button>
                <button className="adm-btn" disabled={!selected} onClick={() => selectedGateway && openEditModal(selectedGateway)}>
                    <i className="codicon codicon-edit" /> Edit Gateway
                </button>
                <button className="adm-btn" disabled={!selected} onClick={handleTestGateway}>
                    <i className="codicon codicon-beaker" /> Test Connection
                </button>
                <button className="adm-btn" onClick={loadGateways} title="Reload data">
                    <i className="codicon codicon-refresh" /> Refresh
                </button>
            </div>

            {error && (
                <div className="adm-hint" style={{ background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)' }}>
                    <i className="codicon codicon-error" /> {error}
                </div>
            )}

            <div className="adm-table-wrap">
                {loading ? (
                    <div style={{ padding: 20, textAlign: 'center', opacity: 0.7 }}>Loading gateways...</div>
                ) : gateways.length === 0 ? (
                    <div style={{ padding: 20, textAlign: 'center', opacity: 0.7 }}>No gateways configured. Add a gateway to route orders to external liquidity providers.</div>
                ) : (
                    <table className="adm-table">
                        <thead>
                            <tr>
                                <th></th>
                                <th>Name</th>
                                <th>Type</th>
                                <th>Host / Server</th>
                                <th>Port</th>
                                <th>Username / Account</th>
                                <th>Status</th>
                                <th>Created At</th>
                            </tr>
                        </thead>
                        <tbody>
                            {gateways.map(g => {
                                const statusStr = g.is_active ? 'connected' : 'disconnected';
                                return (
                                    <tr key={g.id} className={selected === g.id ? 'selected' : ''} onClick={() => setSelected(g.id)} onDoubleClick={() => openEditModal(g)}>
                                        <td><span className={`adm-status-dot ${g.is_active ? 'online' : 'offline'}`} /></td>
                                        <td><strong>{g.name}</strong></td>
                                        <td><span className="adm-tag" style={{ color: TYPE_COLOR[g.type] || '#ccc', border: `1px solid ${(TYPE_COLOR[g.type] || '#ccc')}55` }}>{g.type}</span></td>
                                        <td><code className="adm-code">{g.host || '—'}</code></td>
                                        <td>{g.port || '—'}</td>
                                        <td>{g.username || '—'}</td>
                                        <td style={{ color: STATUS_COLOR[statusStr] }}>{statusStr}</td>
                                        <td>{g.created_at || '—'}</td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                )}
            </div>

            {showModal && (
                <div className="adm-modal-overlay" onClick={() => setShowModal(false)}>
                    <form className="adm-modal" style={{ width: 750, height: '65vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }} onClick={e => e.stopPropagation()} onSubmit={handleSubmit}>
                        <div className="adm-modal-header">
                            <h2>{modalMode === 'create' ? 'Add Liquidity Gateway' : `Edit Gateway: ${gatewayForm.name}`}</h2>
                            <button type="button" className="adm-modal-close" onClick={() => setShowModal(false)}>×</button>
                        </div>
                        
                        {/* Tab Switcher */}
                        <div className="adm-tabs" style={{ padding: '0 16px', borderBottom: '1px solid var(--theia-border)', flexShrink: 0 }}>
                            <button type="button" className={`adm-tab ${activeTab === 'general' ? 'active' : ''}`} onClick={() => setActiveTab('general')}>Common</button>
                            <button type="button" className={`adm-tab ${activeTab === 'groups' ? 'active' : ''}`} onClick={() => setActiveTab('groups')}>Groups</button>
                            <button type="button" className={`adm-tab ${activeTab === 'translations' ? 'active' : ''}`} onClick={() => setActiveTab('translations')}>Translations</button>
                        </div>

                        <div className="adm-modal-body" style={{ flex: 1, overflowY: 'auto', padding: 16 }}>
                            {modalError && (
                                <div className="adm-hint" style={{ background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)', margin: '0 0 12px 0' }}>
                                    <i className="codicon codicon-error" /> {modalError}
                                </div>
                            )}

                            {activeTab === 'general' ? (
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                                        <div className="adm-form-row">
                                            <label>Gateway Name</label>
                                            <input className="adm-input" required placeholder="e.g. LP-Gateway-1" value={gatewayForm.name} onChange={e => setGatewayForm({ ...gatewayForm, name: e.target.value })} />
                                        </div>
                                        <div className="adm-form-row">
                                            <label>Type</label>
                                            <select className="adm-select" value={gatewayForm.type} onChange={e => setGatewayForm({ ...gatewayForm, type: e.target.value })}>
                                                <option value="FIX">FIX Protocol</option>
                                                <option value="MT5">MetaTrader 5 Bridge</option>
                                                <option value="REST">REST API Gateway</option>
                                                <option value="Custom">Custom Provider</option>
                                            </select>
                                        </div>
                                        <div className="adm-form-row">
                                            <label>Host / Hostname</label>
                                            <input className="adm-input" placeholder="e.g. localhost or lp.broker.com" value={gatewayForm.host} onChange={e => setGatewayForm({ ...gatewayForm, host: e.target.value })} />
                                        </div>
                                        <div className="adm-form-row">
                                            <label>Port</label>
                                            <input className="adm-input" type="number" placeholder="e.g. 8003" value={gatewayForm.port} onChange={e => setGatewayForm({ ...gatewayForm, port: e.target.value })} />
                                        </div>
                                    </div>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                                        <div className="adm-form-row">
                                            <label>Username / Account ID</label>
                                            <input className="adm-input" placeholder="Login ID" value={gatewayForm.username} onChange={e => setGatewayForm({ ...gatewayForm, username: e.target.value })} />
                                        </div>
                                        <div className="adm-form-row">
                                            <label>API Key / Password</label>
                                            <input className="adm-input" type="password" placeholder="Access key/token" value={gatewayForm.api_key} onChange={e => setGatewayForm({ ...gatewayForm, api_key: e.target.value })} />
                                        </div>
                                        <div className="adm-form-row" style={{ marginTop: 24, flexDirection: 'row', alignItems: 'center', gap: 8 }}>
                                            <input type="checkbox" id="gw_active" checked={gatewayForm.is_active} onChange={e => setGatewayForm({ ...gatewayForm, is_active: e.target.checked })} />
                                            <label htmlFor="gw_active" style={{ cursor: 'pointer', margin: 0 }}>Enable Gateway Connection</label>
                                        </div>
                                    </div>
                                </div>
                            ) : activeTab === 'groups' ? (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                                    <div style={{ fontSize: 11, color: 'var(--theia-descriptionForeground)', borderBottom: '1px solid var(--theia-border)', paddingBottom: 4 }}>
                                        Please specify the client groups whose trade operations shall be processed by this gateway.
                                    </div>
                                    <div style={{ display: 'flex', gap: 16, height: 260 }}>
                                        {/* Left Control Buttons */}
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, width: 80 }}>
                                            <button 
                                                type="button" 
                                                className="adm-btn"
                                                onClick={() => {
                                                    const nextIdx = gatewayGroups.length;
                                                    setGatewayGroups([...gatewayGroups, 'new_group\\*']);
                                                    setSelectedGroupIdx(nextIdx);
                                                    setEditingGroupIdx(nextIdx);
                                                    setEditingGroupVal('new_group\\*');
                                                }}
                                            >
                                                Add
                                            </button>
                                            <button 
                                                type="button" 
                                                className="adm-btn"
                                                disabled={selectedGroupIdx === null}
                                                onClick={() => {
                                                    if (selectedGroupIdx !== null) {
                                                        setEditingGroupIdx(selectedGroupIdx);
                                                        setEditingGroupVal(gatewayGroups[selectedGroupIdx]);
                                                    }
                                                }}
                                            >
                                                Edit
                                            </button>
                                            <button 
                                                type="button" 
                                                className="adm-btn adm-btn-danger"
                                                disabled={selectedGroupIdx === null}
                                                onClick={() => {
                                                    if (selectedGroupIdx !== null) {
                                                        const updated = gatewayGroups.filter((_, idx) => idx !== selectedGroupIdx);
                                                        setGatewayGroups(updated);
                                                        setSelectedGroupIdx(null);
                                                        setEditingGroupIdx(null);
                                                    }
                                                }}
                                            >
                                                Delete
                                            </button>
                                        </div>

                                        {/* Right List Box container */}
                                        <div style={{ 
                                            flex: 1, 
                                            border: '1px solid var(--theia-border)', 
                                            borderRadius: 4, 
                                            background: 'var(--theia-input-background)',
                                            overflowY: 'auto',
                                            display: 'flex',
                                            flexDirection: 'column'
                                        }}>
                                            {gatewayGroups.map((gStr, idx) => {
                                                const isSelected = selectedGroupIdx === idx;
                                                const isEditing = editingGroupIdx === idx;
                                                
                                                if (isEditing) {
                                                    return (
                                                        <div key={idx} style={{ padding: '4px 8px', borderBottom: '1px solid var(--theia-border)', display: 'flex', gap: 8, alignItems: 'center' }}>
                                                            <input 
                                                                className="adm-input" 
                                                                style={{ flex: 1, height: 20, fontSize: 11 }}
                                                                value={editingGroupVal}
                                                                autoFocus
                                                                onChange={e => setEditingGroupVal(e.target.value)}
                                                                placeholder="e.g. real\*"
                                                                onKeyDown={e => {
                                                                    if (e.key === 'Enter') {
                                                                        const updated = [...gatewayGroups];
                                                                        updated[idx] = editingGroupVal.trim() || '*';
                                                                        setGatewayGroups(updated);
                                                                        setEditingGroupIdx(null);
                                                                    } else if (e.key === 'Escape') {
                                                                        setEditingGroupIdx(null);
                                                                    }
                                                                }}
                                                            />
                                                            <select
                                                                className="adm-select"
                                                                style={{ width: 180, height: 20, fontSize: 11 }}
                                                                value=""
                                                                onChange={e => {
                                                                    const chosen = e.target.value;
                                                                    if (chosen) {
                                                                        setEditingGroupVal(chosen);
                                                                        const updated = [...gatewayGroups];
                                                                        updated[idx] = chosen;
                                                                        setGatewayGroups(updated);
                                                                        setEditingGroupIdx(null);
                                                                    }
                                                                }}
                                                            >
                                                                <option value="">-- Select group... --</option>
                                                                <option value="*">* (All Groups)</option>
                                                                {availableGroups.map(g => (
                                                                    <option key={g.name} value={g.name}>{g.name}</option>
                                                                ))}
                                                            </select>
                                                            <button 
                                                                type="button"
                                                                className="adm-btn adm-btn-primary"
                                                                style={{ height: 20, padding: '0 8px', fontSize: 10, minWidth: 40 }}
                                                                onClick={() => {
                                                                    const updated = [...gatewayGroups];
                                                                    updated[idx] = editingGroupVal.trim() || '*';
                                                                    setGatewayGroups(updated);
                                                                    setEditingGroupIdx(null);
                                                                }}
                                                            >
                                                                Save
                                                            </button>
                                                        </div>
                                                    );
                                                }

                                                return (
                                                    <div 
                                                        key={idx}
                                                        style={{ 
                                                            display: 'flex', 
                                                            alignItems: 'center', 
                                                            gap: 8, 
                                                            padding: '6px 12px', 
                                                            cursor: 'pointer',
                                                            fontSize: 11,
                                                            borderBottom: '1px solid var(--theia-border)',
                                                            background: isSelected ? 'var(--theia-list-activeSelectionBackground)' : 'transparent',
                                                            color: isSelected ? 'var(--theia-list-activeSelectionForeground)' : 'inherit'
                                                        }}
                                                        onClick={() => setSelectedGroupIdx(idx)}
                                                        onDoubleClick={() => {
                                                            setSelectedGroupIdx(idx);
                                                            setEditingGroupIdx(idx);
                                                            setEditingGroupVal(gStr);
                                                        }}
                                                    >
                                                        <i className="codicon codicon-organization" style={{ color: isSelected ? 'inherit' : '#3498db' }} />
                                                        <strong>{gStr}</strong>
                                                    </div>
                                                );
                                            })}

                                            <div 
                                                style={{ 
                                                    display: 'flex', 
                                                    alignItems: 'center', 
                                                    gap: 8, 
                                                    padding: '6px 12px', 
                                                    cursor: 'pointer',
                                                    fontSize: 11,
                                                    color: 'var(--theia-successForeground)'
                                                }}
                                                onClick={() => {
                                                    const nextIdx = gatewayGroups.length;
                                                    setGatewayGroups([...gatewayGroups, '']);
                                                    setSelectedGroupIdx(nextIdx);
                                                    setEditingGroupIdx(nextIdx);
                                                    setEditingGroupVal('');
                                                }}
                                            >
                                                <i className="codicon codicon-add" />
                                                <span>click to add...</span>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Import traders balance option */}
                                    <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', fontSize: 11, marginTop: 4 }}>
                                        <input 
                                            type="checkbox" 
                                            checked={allowImportBalances} 
                                            onChange={e => setAllowImportBalances(e.target.checked)} 
                                        />
                                        Allow importing traders balances
                                    </label>
                                </div>
                            ) : (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                                    <div style={{ display: 'flex', gap: 8, alignItems: 'flex-end', background: 'var(--theia-editor-background)', padding: 10, border: '1px solid var(--theia-border)', borderRadius: 4 }}>
                                        <div className="adm-form-row" style={{ flex: 2 }}>
                                            <label>Platform Symbol (Local)</label>
                                            <input className="adm-input" placeholder="e.g. EURUSD or *" value={newRule.symbol} onChange={e => setNewRule({ ...newRule, symbol: e.target.value })} />
                                        </div>
                                        <div className="adm-form-row" style={{ flex: 2 }}>
                                            <label>Source Symbol (External)</label>
                                            <input className="adm-input" placeholder="e.g. EURUSD.pro or *" value={newRule.source} onChange={e => setNewRule({ ...newRule, source: e.target.value })} />
                                        </div>
                                        <div className="adm-form-row" style={{ flex: 1 }}>
                                            <label>Bid Adj (Pts)</label>
                                            <input className="adm-input" type="number" placeholder="e.g. -2" value={newRule.bid_adj} onChange={e => setNewRule({ ...newRule, bid_adj: parseInt(e.target.value) || 0 })} />
                                        </div>
                                        <div className="adm-form-row" style={{ flex: 1 }}>
                                            <label>Ask Adj (Pts)</label>
                                            <input className="adm-input" type="number" placeholder="e.g. 2" value={newRule.ask_adj} onChange={e => setNewRule({ ...newRule, ask_adj: parseInt(e.target.value) || 0 })} />
                                        </div>
                                        <button type="button" className="adm-btn adm-btn-primary" style={{ height: 26 }} onClick={handleAddRule}>
                                            <i className="codicon codicon-add" /> Add
                                        </button>
                                    </div>

                                    <div style={{ maxHeight: '25vh', overflowY: 'auto', border: '1px solid var(--theia-border)', borderRadius: 4 }}>
                                        <table className="adm-table" style={{ margin: 0 }}>
                                            <thead>
                                                <tr>
                                                    <th>Platform Symbol</th>
                                                    <th>Source Symbol</th>
                                                    <th>Bid Adj (Points)</th>
                                                    <th>Ask Adj (Points)</th>
                                                    <th style={{ width: 60 }}>Action</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {translations.length === 0 ? (
                                                    <tr>
                                                        <td colSpan={5} style={{ textAlign: 'center', opacity: 0.6, padding: 12 }}>
                                                            No symbol translations configured. Direct matching (* &lt;- *) active.
                                                        </td>
                                                    </tr>
                                                ) : (
                                                    translations.map((t, idx) => (
                                                        <tr key={idx}>
                                                            <td>{t.symbol}</td>
                                                            <td>{t.source}</td>
                                                            <td>{t.bid_adj}</td>
                                                            <td>{t.ask_adj}</td>
                                                            <td>
                                                                <button type="button" className="adm-btn" style={{ padding: '2px 6px', color: 'var(--theia-errorForeground)' }} onClick={() => handleRemoveRule(idx)}>
                                                                    <i className="codicon codicon-trash" /> Delete
                                                                </button>
                                                            </td>
                                                        </tr>
                                                    ))
                                                )}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            )}
                        </div>
                        <div className="adm-modal-footer">
                            <button type="submit" className="adm-btn adm-btn-primary">{modalMode === 'create' ? 'Add Gateway' : 'Save Changes'}</button>
                            <button type="button" className="adm-btn" onClick={() => setShowModal(false)}>Cancel</button>
                        </div>
                    </form>
                </div>
            )}

            <div className="adm-statusbar">
                <span>Gateways: {gateways.length}</span>
                <span className="adm-sep">|</span>
                <span style={{ color: STATUS_COLOR.connected }}>Active: {gateways.filter(g => g.is_active).length}</span>
            </div>
        </div>
    );
}
