"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DataFeedsPage = void 0;
const React = require("react");
const api_1 = require("../api");
const STATUS_COLOR = {
    connected: 'var(--theia-successForeground)',
    connecting: 'var(--theia-warningForeground, #f1c40f)',
    disconnected: 'var(--theia-descriptionForeground)',
    error: 'var(--theia-errorForeground)',
};
const AVAILABLE_MODULES = [
    { id: 'MT5', name: 'MetaTrader 5 Feeder', dll: 'mt5_feeder.dll', description: 'Quotes and news synchronization feed bridge for MT5 clusters.' },
    { id: 'LMAX', name: 'LMAX Global Feeder', dll: 'lmax_feeder.dll', description: 'High-frequency institutional liquidity and price feed connector.' },
    { id: 'Bloomberg', name: 'Bloomberg Feeder', dll: 'bloomberg_feeder.dll', description: 'Financial news and terminal market book provider.' },
    { id: 'IQFeed', name: 'IQFeed Feeder', dll: 'iqfeed_feeder.dll', description: 'Retail market data feed covering forex, futures, and equities.' },
    { id: 'CboeFX', name: 'Cboe FX Feeder', dll: 'cboefx_feeder.dll', description: 'Hotspot / Cboe institutional spot FX market pricing.' },
    { id: 'Currenex', name: 'Currenex Feeder', dll: 'currenex_feeder.dll', description: 'Ecn quotes and trades ingestion adapter.' },
    { id: 'Custom', name: 'Custom Feeder Module', dll: 'custom_feeder.dll', description: 'User-defined custom price source API driver.' }
];
function buildSymbolTree(symbols) {
    const root = {};
    symbols.forEach(s => {
        const fullPath = s.symbol || s.name || '';
        if (!fullPath)
            return;
        const parts = fullPath.split('\\');
        let current = root;
        let accumPath = '';
        for (let i = 0; i < parts.length; i++) {
            const part = parts[i];
            // skip empty components or dummies
            if (!part || part.startsWith('.'))
                continue;
            accumPath = accumPath ? `${accumPath}\\${part}` : part;
            const isLast = i === parts.length - 1;
            if (!current[part]) {
                current[part] = {
                    name: part,
                    path: accumPath,
                    type: isLast ? 'symbol' : 'folder',
                    children: {}
                };
            }
            current = current[part].children;
        }
    });
    return root;
}
function TreeSelect({ tree, onSelect, depth = 0 }) {
    const [expanded, setExpanded] = React.useState({
        '*': true,
        'forex': true,
        'crypto': true
    });
    const toggle = (path) => {
        setExpanded(prev => ({ ...prev, [path]: !prev[path] }));
    };
    return (React.createElement("div", { style: { paddingLeft: depth > 0 ? 12 : 0 } }, Object.values(tree).map((node) => {
        const isFolder = node.type === 'folder';
        const hasChildren = Object.keys(node.children).length > 0;
        const isExpanded = expanded[node.path];
        return (React.createElement("div", { key: node.path, style: { fontSize: 11, userSelect: 'none', fontFamily: 'var(--theia-ui-font-family)' } },
            React.createElement("div", { style: {
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6,
                    padding: '3px 6px',
                    cursor: 'pointer',
                    borderRadius: 3,
                }, className: "adm-tree-select-row", onClick: (e) => {
                    e.stopPropagation();
                    if (isFolder && hasChildren) {
                        toggle(node.path);
                    }
                    else {
                        onSelect(node.path, node.type);
                    }
                }, onDoubleClick: (e) => {
                    e.stopPropagation();
                    onSelect(node.path, node.type);
                } },
                isFolder ? (React.createElement("span", { style: { width: 10, display: 'inline-flex', justifyContent: 'center', fontSize: 8, opacity: 0.7 } }, hasChildren ? (isExpanded ? '▼' : '▶') : '')) : (React.createElement("span", { style: { width: 10 } })),
                React.createElement("span", { style: { fontSize: 12 } }, isFolder ? '📁' : '💰'),
                React.createElement("span", { style: {
                        fontWeight: isFolder ? 600 : 'normal',
                        color: isFolder ? 'var(--theia-foreground)' : 'var(--theia-descriptionForeground)'
                    } }, node.name),
                isFolder && (React.createElement("button", { type: "button", onClick: (e) => {
                        e.stopPropagation();
                        onSelect(node.path === '*' ? '*' : `${node.path}\\*`, 'folder');
                    }, style: {
                        marginLeft: 'auto',
                        fontSize: 9,
                        padding: '1px 5px',
                        background: 'var(--theia-button-background, #34495e)',
                        color: 'var(--theia-button-foreground, #fff)',
                        border: 'none',
                        borderRadius: 2,
                        cursor: 'pointer'
                    } }, "Select"))),
            isFolder && isExpanded && hasChildren && (React.createElement(TreeSelect, { tree: node.children, onSelect: onSelect, depth: depth + 1 }))));
    })));
}
function DataFeedsPage() {
    const [activeViewTab, setActiveViewTab] = React.useState('selected');
    const [feeds, setFeeds] = React.useState([]);
    const [selectedFeedId, setSelectedFeedId] = React.useState(null);
    const [selectedModuleId, setSelectedModuleId] = React.useState(null);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState(null);
    // Modal state
    const [showModal, setShowModal] = React.useState(false);
    const [modalMode, setModalMode] = React.useState('create');
    const [modalActiveTab, setModalActiveTab] = React.useState('common');
    const [modalError, setModalError] = React.useState(null);
    // Form fields (Common Tab)
    const [feedForm, setFeedForm] = React.useState({
        id: null,
        name: '',
        module: 'mt5_feeder.dll',
        host: '',
        port: '',
        username: '',
        api_key: '',
        is_active: true
    });
    // Form fields (Gateway Tab)
    const [gwSettings, setGwSettings] = React.useState({
        gateway_server: '86.104.251.194:443',
        gateway_login: '',
        gateway_password: ''
    });
    const [dbGateways, setDbGateways] = React.useState([]);
    // Form fields (Groups Tab)
    const [groupsFilter, setGroupsFilter] = React.useState(['*']);
    const [selectedGroupIdx, setSelectedGroupIdx] = React.useState(null);
    const [editingGroupIdx, setEditingGroupIdx] = React.useState(null);
    const [editingGroupVal, setEditingGroupVal] = React.useState('');
    // Form fields (Symbols Tab)
    const [symbolsFilter, setSymbolsFilter] = React.useState('');
    // Form fields (Translations Tab)
    const [translations, setTranslations] = React.useState([]);
    const [newRule, setNewRule] = React.useState({
        symbol: '',
        source: '',
        bid_adj: 0,
        ask_adj: 0
    });
    // Form fields (Parameters Tab)
    const [parameters, setParameters] = React.useState([]);
    const [newParam, setNewParam] = React.useState({ key: '', val: '' });
    const lastFeedsRef = React.useRef([]);
    const [tickRates, setTickRates] = React.useState({});
    // Symbols tab custom nested tree editor states
    const [dbSymbols, setDbSymbols] = React.useState([]);
    const [availableGroups, setAvailableGroups] = React.useState([]);
    const [editingIndex, setEditingIndex] = React.useState(null);
    const [editValue, setEditValue] = React.useState('');
    const [showTreeIndex, setShowTreeIndex] = React.useState(null);
    const [selectedRuleIndex, setSelectedRuleIndex] = React.useState(null);
    const [allowImport, setAllowImport] = React.useState(false);
    const symbolTree = React.useMemo(() => {
        const rawTree = buildSymbolTree(dbSymbols);
        return {
            'Symbols': {
                name: 'Symbols',
                path: '*',
                type: 'folder',
                children: rawTree
            }
        };
    }, [dbSymbols]);
    const loadDbSymbols = async () => {
        try {
            const data = await api_1.API.getSymbols();
            setDbSymbols(data);
        }
        catch (e) {
            console.error('Failed to load symbols for data feeds tree view:', e);
        }
    };
    const loadDbGroups = async () => {
        try {
            const data = await api_1.API.getGroups();
            setAvailableGroups(data);
        }
        catch (e) {
            console.error('Failed to load groups for feed settings dropdown:', e);
        }
    };
    const loadFeeds = async (isPoll = false) => {
        if (!isPoll)
            setLoading(true);
        setError(null);
        try {
            const data = await api_1.API.getGateways();
            const filtered = data.filter((g) => g.type.startsWith('Feeder_'));
            const tradeGws = data.filter((g) => !g.type.startsWith('Feeder_'));
            setDbGateways(tradeGws);
            // Calculate tick rates
            const newRates = {};
            filtered.forEach((f) => {
                const old = lastFeedsRef.current.find(o => o.id === f.id);
                if (old) {
                    const diffTicks = Math.max(0, (f.ticks_count || 0) - (old.ticks_count || 0));
                    newRates[f.id] = diffTicks / 2.0; // Polled every 2 seconds
                }
                else {
                    newRates[f.id] = 0;
                }
            });
            setTickRates(prev => ({ ...prev, ...newRates }));
            lastFeedsRef.current = filtered;
            setFeeds(filtered);
        }
        catch (err) {
            setError(err.message || 'Failed to load data feeds.');
        }
        finally {
            if (!isPoll)
                setLoading(false);
        }
    };
    React.useEffect(() => {
        loadFeeds(false);
        loadDbSymbols();
        loadDbGroups();
        let interval = null;
        if (activeViewTab === 'selected') {
            interval = setInterval(() => loadFeeds(true), 2000);
        }
        return () => {
            if (interval)
                clearInterval(interval);
        };
    }, [activeViewTab]);
    const openCreateModal = (mod) => {
        setModalMode('create');
        setModalActiveTab('common');
        setModalError(null);
        setFeedForm({
            id: null,
            name: mod.name + ' 1',
            module: mod.dll,
            host: 'localhost',
            port: '8005',
            username: '',
            api_key: '',
            is_active: true
        });
        setGwSettings({
            gateway_server: '86.104.251.194:443',
            gateway_login: '',
            gateway_password: ''
        });
        setGroupsFilter(['*']);
        setSelectedGroupIdx(null);
        setEditingGroupIdx(null);
        setEditingGroupVal('');
        setSymbolsFilter('Forex*,!Forex\\EURUSD');
        setTranslations([]);
        // Reset symbols filter rules edit states
        setEditingIndex(null);
        setSelectedRuleIndex(null);
        setShowTreeIndex(null);
        setAllowImport(false);
        setParameters([
            { key: 'NewsCategory', val: 'General' },
            { key: 'Quotes Delay', val: '0' },
            { key: 'Quotes Ticks Sample', val: '1000' },
            { key: 'Quotes Books Sample', val: '1000' }
        ]);
        setShowModal(true);
    };
    const openEditModal = (f) => {
        setModalMode('edit');
        setModalActiveTab('common');
        setModalError(null);
        // Parse feeder type back to dll
        const dllName = f.type.replace('Feeder_', '');
        setFeedForm({
            id: f.id,
            name: f.name,
            module: dllName,
            host: f.host || '',
            port: f.port ? String(f.port) : '',
            username: f.username || '',
            api_key: f.api_key || '',
            is_active: f.is_active === 1
        });
        // Parse settings json
        let gateway = { gateway_server: '86.104.251.194:443', gateway_login: '', gateway_password: '' };
        let groups = ['*'];
        let symFilter = '';
        let rules = [];
        let params = [];
        if (f.settings_json) {
            try {
                const parsed = typeof f.settings_json === 'string' ? JSON.parse(f.settings_json) : f.settings_json;
                if (parsed.gateway)
                    gateway = { ...gateway, ...parsed.gateway };
                if (parsed.groups)
                    groups = parsed.groups;
                if (parsed.symbols_filter)
                    symFilter = parsed.symbols_filter;
                if (parsed.translations)
                    rules = parsed.translations;
                if (parsed.parameters) {
                    params = Object.entries(parsed.parameters).map(([k, v]) => ({ key: k, val: String(v) }));
                }
            }
            catch (err) {
                // ignore
            }
        }
        // Fill default params if missing
        if (params.length === 0) {
            params = [
                { key: 'NewsCategory', val: 'General' },
                { key: 'Quotes Delay', val: '0' },
                { key: 'Quotes Ticks Sample', val: '1000' },
                { key: 'Quotes Books Sample', val: '1000' }
            ];
        }
        setGwSettings(gateway);
        setGroupsFilter(groups);
        setSelectedGroupIdx(null);
        setEditingGroupIdx(null);
        setEditingGroupVal('');
        setSymbolsFilter(symFilter);
        setTranslations(rules);
        setParameters(params);
        // Reset symbols filter rules edit states
        setEditingIndex(null);
        setSelectedRuleIndex(null);
        setShowTreeIndex(null);
        setAllowImport(false);
        setShowModal(true);
    };
    const filterRules = React.useMemo(() => {
        return symbolsFilter.split(',').map(s => s.trim()).filter(Boolean);
    }, [symbolsFilter]);
    const handleAddFilterRule = () => {
        const newRules = [...filterRules, '*'];
        setSymbolsFilter(newRules.join(','));
        setSelectedRuleIndex(newRules.length - 1);
        setEditingIndex(newRules.length - 1);
        setEditValue('*');
    };
    const handleEditFilterRule = (idx) => {
        setEditingIndex(idx);
        setEditValue(filterRules[idx] || '');
        setSelectedRuleIndex(idx);
    };
    const handleDeleteFilterRule = (idx) => {
        const newRules = filterRules.filter((_, i) => i !== idx);
        setSymbolsFilter(newRules.join(','));
        setEditingIndex(null);
        setSelectedRuleIndex(null);
        setShowTreeIndex(null);
    };
    const handleSaveFilterRule = (idx, val) => {
        const newRules = [...filterRules];
        newRules[idx] = val.trim();
        setSymbolsFilter(newRules.filter(Boolean).join(','));
        setEditingIndex(null);
        setShowTreeIndex(null);
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
    const handleAddParam = () => {
        if (!newParam.key.trim())
            return;
        setParameters([...parameters, { key: newParam.key.trim(), val: newParam.val.trim() }]);
        setNewParam({ key: '', val: '' });
    };
    const handleRemoveParam = (idx) => {
        setParameters(parameters.filter((_, i) => i !== idx));
    };
    const handleSubmit = async (e) => {
        e.preventDefault();
        setModalError(null);
        // Construct settings_json
        const paramObj = parameters.reduce((acc, curr) => {
            if (curr.key.trim())
                acc[curr.key.trim()] = curr.val;
            return acc;
        }, {});
        const settings = {
            gateway: gwSettings,
            groups: groupsFilter,
            symbols_filter: symbolsFilter,
            translations,
            parameters: paramObj
        };
        const payload = {
            name: feedForm.name,
            type: 'Feeder_' + feedForm.module,
            host: feedForm.host || undefined,
            port: feedForm.port ? parseInt(feedForm.port) : undefined,
            username: feedForm.username || undefined,
            api_key: feedForm.api_key || undefined,
            is_active: feedForm.is_active,
            settings_json: JSON.stringify(settings)
        };
        try {
            if (modalMode === 'create') {
                await api_1.API.createGateway(payload);
            }
            else {
                await api_1.API.updateGateway(feedForm.id, payload);
            }
            setShowModal(false);
            setActiveViewTab('selected');
            await loadFeeds();
        }
        catch (err) {
            setModalError(err.message || 'Failed to save data feed.');
        }
    };
    const handleTestFeed = async () => {
        if (!selectedFeedId)
            return;
        setError(null);
        try {
            const resp = await api_1.API.testGateway(selectedFeedId);
            alert(`Feeder Connection Test: ${resp.message}`);
        }
        catch (err) {
            setError(err.message || 'Feeder connection test failed.');
        }
    };
    const selectedFeed = feeds.find(f => f.id === selectedFeedId);
    const selectedModule = AVAILABLE_MODULES.find(m => m.id === selectedModuleId);
    return (React.createElement("div", { className: "adm-page" },
        React.createElement("div", { className: "adm-tabs", style: { background: 'var(--theia-editor-background)', borderBottom: '1px solid var(--theia-border)', flexShrink: 0 } },
            React.createElement("button", { className: `adm-tab ${activeViewTab === 'selected' ? 'active' : ''}`, onClick: () => setActiveViewTab('selected') }, "Selected Feeds"),
            React.createElement("button", { className: `adm-tab ${activeViewTab === 'available' ? 'active' : ''}`, onClick: () => setActiveViewTab('available') }, "Available Connectors")),
        React.createElement("div", { className: "adm-toolbar" }, activeViewTab === 'selected' ? (React.createElement(React.Fragment, null,
            React.createElement("button", { className: "adm-btn", disabled: !selectedFeedId, onClick: () => selectedFeed && openEditModal(selectedFeed) },
                React.createElement("i", { className: "codicon codicon-edit" }),
                " Edit Feed"),
            React.createElement("button", { className: "adm-btn", disabled: !selectedFeedId, onClick: handleTestFeed },
                React.createElement("i", { className: "codicon codicon-beaker" }),
                " Test Connection"),
            React.createElement("button", { className: "adm-btn", onClick: () => loadFeeds(false), title: "Reload list" },
                React.createElement("i", { className: "codicon codicon-refresh" }),
                " Refresh"))) : (React.createElement("button", { className: "adm-btn adm-btn-primary", disabled: !selectedModuleId, onClick: () => selectedModule && openCreateModal(selectedModule) },
            React.createElement("i", { className: "codicon codicon-add" }),
            " Configure Feed..."))),
        error && (React.createElement("div", { className: "adm-hint", style: { background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)' } },
            React.createElement("i", { className: "codicon codicon-error" }),
            " ",
            error)),
        React.createElement("div", { className: "adm-table-wrap" }, activeViewTab === 'selected' ? (loading ? (React.createElement("div", { style: { padding: 20, textAlign: 'center', opacity: 0.7 } }, "Loading feeders...")) : feeds.length === 0 ? (React.createElement("div", { style: { padding: 20, textAlign: 'center', opacity: 0.7 } }, "No configured price feeders found. Go to the \"Available Connectors\" tab to setup a price feed source.")) : (React.createElement("table", { className: "adm-table" },
            React.createElement("thead", null,
                React.createElement("tr", null,
                    React.createElement("th", null),
                    React.createElement("th", null, "Feed Name"),
                    React.createElement("th", null, "Feeder Module"),
                    React.createElement("th", null, "Server Address"),
                    React.createElement("th", null, "Login ID"),
                    React.createElement("th", null, "Ticks/sec"),
                    React.createElement("th", null, "Status"),
                    React.createElement("th", null, "Last Tick"))),
            React.createElement("tbody", null, feeds.map(f => {
                const dll = f.type.replace('Feeder_', '');
                const hasTicks = (f.ticks_count || 0) > 0;
                const tickAgeSec = f.last_tick_age_s != null ? f.last_tick_age_s : null;
                // Consider disconnected if last tick was > 45 seconds ago
                const isTickFresh = tickAgeSec !== null && tickAgeSec < 45;
                let statusStr = 'disconnected';
                let dotClass = 'offline';
                let dotStyle = {};
                if (f.is_active) {
                    if (hasTicks && isTickFresh) {
                        statusStr = 'connected';
                        dotClass = 'online';
                    }
                    else if (hasTicks && !isTickFresh) {
                        // Was connected but ticks stopped - truly disconnected
                        statusStr = 'disconnected';
                        dotClass = 'offline';
                    }
                    else {
                        statusStr = 'connecting';
                        dotClass = '';
                        dotStyle = {
                            backgroundColor: 'var(--theia-warningForeground, #f1c40f)',
                            boxShadow: '0 0 4px #f1c40f88'
                        };
                    }
                }
                const rate = tickRates[f.id] || 0;
                const ticksText = f.is_active ? (hasTicks ? `${rate.toFixed(1)} /s (${f.ticks_count} total)` : '0.0 /s') : '—';
                let lastTickText = '—';
                if (f.last_active) {
                    try {
                        const date = new Date(f.last_active);
                        lastTickText = date.toLocaleTimeString();
                        if (tickAgeSec !== null && tickAgeSec > 60) {
                            lastTickText += ` (${Math.round(tickAgeSec)}s ago)`;
                        }
                    }
                    catch (e) {
                        lastTickText = '—';
                    }
                }
                return (React.createElement("tr", { key: f.id, className: selectedFeedId === f.id ? 'selected' : '', onClick: () => setSelectedFeedId(f.id), onDoubleClick: () => openEditModal(f) },
                    React.createElement("td", null,
                        React.createElement("span", { className: `adm-status-dot ${dotClass}`, style: dotStyle })),
                    React.createElement("td", null,
                        React.createElement("strong", null, f.name)),
                    React.createElement("td", null,
                        React.createElement("code", { className: "adm-code" }, dll)),
                    React.createElement("td", null, f.host ? `${f.host}:${f.port || '80'}` : '—'),
                    React.createElement("td", null, f.username || '—'),
                    React.createElement("td", { className: "adm-num" }, ticksText),
                    React.createElement("td", { style: { color: STATUS_COLOR[statusStr] } }, statusStr),
                    React.createElement("td", null, lastTickText)));
            }))))) : (React.createElement("table", { className: "adm-table" },
            React.createElement("thead", null,
                React.createElement("tr", null,
                    React.createElement("th", null, "Connector Name"),
                    React.createElement("th", null, "Feeder Module DLL"),
                    React.createElement("th", null, "Description"))),
            React.createElement("tbody", null, AVAILABLE_MODULES.map(m => (React.createElement("tr", { key: m.id, className: selectedModuleId === m.id ? 'selected' : '', onClick: () => setSelectedModuleId(m.id), onDoubleClick: () => openCreateModal(m) },
                React.createElement("td", null,
                    React.createElement("strong", null, m.name)),
                React.createElement("td", null,
                    React.createElement("code", { className: "adm-code" }, m.dll)),
                React.createElement("td", { style: { opacity: 0.8 } }, m.description)))))))),
        showModal && (React.createElement("div", { className: "adm-modal-overlay", onClick: () => setShowModal(false) },
            React.createElement("form", { className: "adm-modal", style: { width: 750, height: '65vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }, onClick: e => e.stopPropagation(), onSubmit: handleSubmit },
                React.createElement("div", { className: "adm-modal-header" },
                    React.createElement("h2", null, modalMode === 'create' ? `Configure New Feed: ${feedForm.module}` : `Edit Feed settings: ${feedForm.name}`),
                    React.createElement("button", { type: "button", className: "adm-modal-close", onClick: () => setShowModal(false) }, "\u00D7")),
                React.createElement("div", { className: "adm-tabs", style: { padding: '0 16px', borderBottom: '1px solid var(--theia-border)', flexShrink: 0 } },
                    React.createElement("button", { type: "button", className: `adm-tab ${modalActiveTab === 'common' ? 'active' : ''}`, onClick: () => setModalActiveTab('common') }, "Common"),
                    React.createElement("button", { type: "button", className: `adm-tab ${modalActiveTab === 'gateway' ? 'active' : ''}`, onClick: () => setModalActiveTab('gateway') }, "Gateway"),
                    React.createElement("button", { type: "button", className: `adm-tab ${modalActiveTab === 'groups' ? 'active' : ''}`, onClick: () => setModalActiveTab('groups') }, "Groups"),
                    React.createElement("button", { type: "button", className: `adm-tab ${modalActiveTab === 'symbols' ? 'active' : ''}`, onClick: () => setModalActiveTab('symbols') }, "Symbols"),
                    React.createElement("button", { type: "button", className: `adm-tab ${modalActiveTab === 'translations' ? 'active' : ''}`, onClick: () => setModalActiveTab('translations') }, "Translations"),
                    React.createElement("button", { type: "button", className: `adm-tab ${modalActiveTab === 'parameters' ? 'active' : ''}`, onClick: () => setModalActiveTab('parameters') }, "Parameters")),
                React.createElement("div", { className: "adm-modal-body", style: { flex: 1, overflowY: 'auto', padding: 16 } },
                    modalError && (React.createElement("div", { className: "adm-hint", style: { background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)', margin: '0 0 12px 0' } },
                        React.createElement("i", { className: "codicon codicon-error" }),
                        " ",
                        modalError)),
                    modalActiveTab === 'common' && (React.createElement("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 } },
                        React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 12 } },
                            React.createElement("div", { className: "adm-form-row" },
                                React.createElement("label", null, "Feed Name"),
                                React.createElement("input", { className: "adm-input", required: true, placeholder: "e.g. My-LMAX-Feeder", value: feedForm.name, onChange: e => setFeedForm({ ...feedForm, name: e.target.value }) })),
                            React.createElement("div", { className: "adm-form-row" },
                                React.createElement("label", null, "Module DLL"),
                                React.createElement("input", { className: "adm-input", disabled: true, value: feedForm.module })),
                            React.createElement("div", { className: "adm-form-row", style: { marginTop: 12, flexDirection: 'row', alignItems: 'center', gap: 8 } },
                                React.createElement("input", { type: "checkbox", id: "feed_enabled", checked: feedForm.is_active, onChange: e => setFeedForm({ ...feedForm, is_active: e.target.checked }) }),
                                React.createElement("label", { htmlFor: "feed_enabled", style: { cursor: 'pointer', margin: 0 } }, "Enable Data Feed"))),
                        React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 12 } },
                            React.createElement("div", { className: "adm-form-row" },
                                React.createElement("label", null, "Feed Server Host"),
                                React.createElement("input", { className: "adm-input", required: true, placeholder: "e.g. feed.lmax.com", value: feedForm.host, onChange: e => setFeedForm({ ...feedForm, host: e.target.value }) })),
                            React.createElement("div", { className: "adm-form-row" },
                                React.createElement("label", null, "Port"),
                                React.createElement("input", { className: "adm-input", type: "number", required: true, placeholder: "e.g. 443", value: feedForm.port, onChange: e => setFeedForm({ ...feedForm, port: e.target.value }) })),
                            React.createElement("div", { className: "adm-form-row" },
                                React.createElement("label", null, "Feed Login"),
                                React.createElement("input", { className: "adm-input", placeholder: "Login ID", value: feedForm.username, onChange: e => setFeedForm({ ...feedForm, username: e.target.value }) })),
                            React.createElement("div", { className: "adm-form-row" },
                                React.createElement("label", null, "Password / Token"),
                                React.createElement("input", { className: "adm-input", type: "password", placeholder: "API access password", value: feedForm.api_key, onChange: e => setFeedForm({ ...feedForm, api_key: e.target.value }) }))))),
                    modalActiveTab === 'gateway' && (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 12, maxWidth: 400 } },
                        React.createElement("div", { className: "adm-hint", style: { marginBottom: 10 } },
                            React.createElement("i", { className: "codicon codicon-info" }),
                            " Define loopback interface routing servers settings for secure history/trading component tunnels."),
                        React.createElement("div", { className: "adm-form-row" },
                            React.createElement("label", { style: { color: 'var(--theia-successForeground)', fontWeight: 'bold' } }, "Link with Trade Gateway Profile"),
                            React.createElement("select", { className: "adm-select", style: { width: '100%', height: 22, padding: '2px 6px', fontSize: 11 }, value: "", onChange: e => {
                                    const chosenId = e.target.value;
                                    if (chosenId) {
                                        const match = dbGateways.find(g => String(g.id) === chosenId);
                                        if (match) {
                                            setGwSettings({
                                                gateway_server: `${match.host || 'localhost'}:${match.port || '8003'}`,
                                                gateway_login: match.username || '',
                                                gateway_password: match.api_key || ''
                                            });
                                        }
                                    }
                                } },
                                React.createElement("option", { value: "" }, "-- Choose Profile to Auto-Fill Server Details --"),
                                dbGateways.map(g => (React.createElement("option", { key: g.id, value: g.id },
                                    g.name,
                                    " (",
                                    g.type,
                                    ")"))))),
                        React.createElement("div", { className: "adm-form-row" },
                            React.createElement("label", null, "Gateway Server (IP:Port)"),
                            React.createElement("input", { className: "adm-input", value: gwSettings.gateway_server, onChange: e => setGwSettings({ ...gwSettings, gateway_server: e.target.value }) })),
                        React.createElement("div", { className: "adm-form-row" },
                            React.createElement("label", null, "Gateway Login"),
                            React.createElement("input", { className: "adm-input", placeholder: "Numeric Login", value: gwSettings.gateway_login, onChange: e => setGwSettings({ ...gwSettings, gateway_login: e.target.value }) })),
                        React.createElement("div", { className: "adm-form-row" },
                            React.createElement("label", null, "Gateway Password"),
                            React.createElement("input", { className: "adm-input", type: "password", placeholder: "Loopback key", value: gwSettings.gateway_password, onChange: e => setGwSettings({ ...gwSettings, gateway_password: e.target.value }) })))),
                    modalActiveTab === 'groups' && (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 12 } },
                        React.createElement("div", { className: "adm-hint", style: { fontSize: 11, color: 'var(--theia-descriptionForeground)' } }, "Please specify the client groups whose trade operations shall be routed to the liquidity provider through this feed."),
                        React.createElement("div", { style: { display: 'flex', gap: 16, height: 260 } },
                            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 8, width: 90, flexShrink: 0 } },
                                React.createElement("button", { type: "button", className: "adm-btn", onClick: () => {
                                        const nextIdx = groupsFilter.length;
                                        setGroupsFilter([...groupsFilter, 'new_group\\*']);
                                        setSelectedGroupIdx(nextIdx);
                                        setEditingGroupIdx(nextIdx);
                                        setEditingGroupVal('new_group\\*');
                                    }, style: { fontSize: 11, width: '100%', height: 24, padding: '2px 8px' } }, "Add"),
                                React.createElement("button", { type: "button", className: "adm-btn", disabled: selectedGroupIdx === null, onClick: () => {
                                        if (selectedGroupIdx !== null) {
                                            setEditingGroupIdx(selectedGroupIdx);
                                            setEditingGroupVal(groupsFilter[selectedGroupIdx]);
                                        }
                                    }, style: { fontSize: 11, width: '100%', height: 24, padding: '2px 8px' } }, "Edit"),
                                React.createElement("button", { type: "button", className: "adm-btn adm-btn-danger", disabled: selectedGroupIdx === null, onClick: () => {
                                        if (selectedGroupIdx !== null) {
                                            const updated = groupsFilter.filter((_, idx) => idx !== selectedGroupIdx);
                                            setGroupsFilter(updated);
                                            setSelectedGroupIdx(null);
                                            setEditingGroupIdx(null);
                                        }
                                    }, style: { fontSize: 11, width: '100%', height: 24, padding: '2px 8px' } }, "Delete")),
                            React.createElement("div", { style: {
                                    flex: 1,
                                    border: '1px solid var(--theia-input-border, #ccc)',
                                    background: 'var(--theia-input-background, #fff)',
                                    color: 'var(--theia-input-foreground, #333)',
                                    borderRadius: 3,
                                    height: '100%',
                                    overflowY: 'auto',
                                    display: 'flex',
                                    flexDirection: 'column'
                                } },
                                groupsFilter.map((gStr, idx) => {
                                    const isSelected = selectedGroupIdx === idx;
                                    const isEditing = editingGroupIdx === idx;
                                    if (isEditing) {
                                        return (React.createElement("div", { key: idx, style: { padding: '4px 8px', borderBottom: '1px solid var(--theia-panel-border, #eee)', display: 'flex', gap: 8, alignItems: 'center' } },
                                            React.createElement("input", { className: "adm-input", style: { flex: 1, height: 20, fontSize: 11 }, value: editingGroupVal, autoFocus: true, onChange: e => setEditingGroupVal(e.target.value), placeholder: "e.g. real\\*", onKeyDown: e => {
                                                    if (e.key === 'Enter') {
                                                        const updated = [...groupsFilter];
                                                        updated[idx] = editingGroupVal.trim() || '*';
                                                        setGroupsFilter(updated);
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
                                                        const updated = [...groupsFilter];
                                                        updated[idx] = chosen;
                                                        setGroupsFilter(updated);
                                                        setEditingGroupIdx(null);
                                                    }
                                                } },
                                                React.createElement("option", { value: "" }, "-- Select group... --"),
                                                React.createElement("option", { value: "*" }, "* (All Groups)"),
                                                availableGroups.map(g => (React.createElement("option", { key: g.name, value: g.name }, g.name)))),
                                            React.createElement("button", { type: "button", className: "adm-btn adm-btn-primary", style: { height: 20, padding: '0 8px', fontSize: 10, minWidth: 40 }, onClick: () => {
                                                    const updated = [...groupsFilter];
                                                    updated[idx] = editingGroupVal.trim() || '*';
                                                    setGroupsFilter(updated);
                                                    setEditingGroupIdx(null);
                                                } }, "Save")));
                                    }
                                    return (React.createElement("div", { key: idx, style: {
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: 8,
                                            padding: '6px 12px',
                                            cursor: 'default',
                                            fontSize: 11,
                                            borderBottom: '1px solid var(--theia-panel-border, #eee)',
                                            background: isSelected ? 'var(--theia-list-activeSelectionBackground, #3498db)' : 'transparent',
                                            color: isSelected ? 'var(--theia-list-activeSelectionForeground, #fff)' : 'inherit'
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
                                        const nextIdx = groupsFilter.length;
                                        setGroupsFilter([...groupsFilter, '']);
                                        setSelectedGroupIdx(nextIdx);
                                        setEditingGroupIdx(nextIdx);
                                        setEditingGroupVal('');
                                    } },
                                    React.createElement("i", { className: "codicon codicon-add" }),
                                    React.createElement("span", null, "click to add...")))))),
                    modalActiveTab === 'symbols' && (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 12 } },
                        React.createElement("div", { className: "adm-hint", style: { fontSize: 11, color: 'var(--theia-descriptionForeground)' } }, "Please specify the symbols for which the data feed will translate quotes."),
                        React.createElement("div", { style: { display: 'flex', gap: 16, height: 260 } },
                            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 8, width: 90, flexShrink: 0 } },
                                React.createElement("button", { type: "button", className: "adm-btn", onClick: handleAddFilterRule, style: { fontSize: 11, width: '100%', height: 24, padding: '2px 8px' } }, "Add"),
                                React.createElement("button", { type: "button", className: "adm-btn", disabled: selectedRuleIndex === null, onClick: () => selectedRuleIndex !== null && handleEditFilterRule(selectedRuleIndex), style: { fontSize: 11, width: '100%', height: 24, padding: '2px 8px' } }, "Edit"),
                                React.createElement("button", { type: "button", className: "adm-btn", disabled: selectedRuleIndex === null, onClick: () => selectedRuleIndex !== null && handleDeleteFilterRule(selectedRuleIndex), style: { fontSize: 11, width: '100%', height: 24, padding: '2px 8px' } }, "Delete")),
                            React.createElement("div", { style: {
                                    flex: 1,
                                    border: '1px solid var(--theia-input-border, #ccc)',
                                    background: 'var(--theia-input-background, #fff)',
                                    color: 'var(--theia-input-foreground, #333)',
                                    borderRadius: 3,
                                    height: '100%',
                                    overflowY: 'auto',
                                    position: 'relative'
                                } },
                                filterRules.map((rule, idx) => {
                                    const isSelected = selectedRuleIndex === idx;
                                    const isEditing = editingIndex === idx;
                                    const showTree = showTreeIndex === idx;
                                    return (React.createElement("div", { key: idx, style: {
                                            display: 'flex',
                                            alignItems: 'center',
                                            padding: '4px 8px',
                                            background: isSelected && !isEditing ? 'var(--theia-list-activeSelectionBackground, #3498db)' : 'transparent',
                                            color: isSelected && !isEditing ? 'var(--theia-list-activeSelectionForeground, #fff)' : 'inherit',
                                            cursor: 'default',
                                            borderBottom: '1px solid var(--theia-panel-border, #eee)',
                                            fontSize: 12,
                                            position: 'relative'
                                        }, onClick: () => {
                                            if (!isEditing) {
                                                setSelectedRuleIndex(idx);
                                            }
                                        }, onDoubleClick: () => {
                                            handleEditFilterRule(idx);
                                        } },
                                        React.createElement("span", { style: { marginRight: 8, display: 'inline-flex', alignItems: 'center' } },
                                            React.createElement("span", { style: {
                                                    display: 'inline-block',
                                                    background: '#f1c40f',
                                                    color: '#2980b9',
                                                    fontSize: 9,
                                                    fontWeight: 'bold',
                                                    padding: '1px 3px',
                                                    borderRadius: 2,
                                                    border: '1px solid #d35400',
                                                    lineHeight: 1
                                                } }, "$")),
                                        isEditing ? (React.createElement("div", { style: { display: 'flex', flex: 1, gap: 4, alignItems: 'center', position: 'relative' } },
                                            React.createElement("input", { className: "adm-input", value: editValue, onChange: e => setEditValue(e.target.value), onBlur: (e) => {
                                                    // Wait, if they clicked on the tree popup, don't save immediately
                                                    if (e.relatedTarget && e.relatedTarget.closest('.adm-tree-popup')) {
                                                        return;
                                                    }
                                                    handleSaveFilterRule(idx, editValue);
                                                }, onKeyDown: e => {
                                                    if (e.key === 'Enter') {
                                                        handleSaveFilterRule(idx, editValue);
                                                    }
                                                    else if (e.key === 'Escape') {
                                                        setEditingIndex(null);
                                                        setShowTreeIndex(null);
                                                    }
                                                }, autoFocus: true, style: {
                                                    flex: 1,
                                                    fontSize: 11,
                                                    height: 20,
                                                    padding: '2px 6px',
                                                    background: 'var(--theia-input-background)',
                                                    color: 'var(--theia-input-foreground)',
                                                    border: '1px solid var(--theia-input-border)'
                                                } }),
                                            React.createElement("button", { type: "button", onClick: (e) => {
                                                    e.stopPropagation();
                                                    setShowTreeIndex(showTree ? null : idx);
                                                }, style: {
                                                    padding: '2px 6px',
                                                    fontSize: 8,
                                                    cursor: 'pointer',
                                                    height: 20,
                                                    background: 'var(--theia-button-background)',
                                                    color: 'var(--theia-button-foreground)',
                                                    border: 'none',
                                                    borderRadius: 2
                                                } }, "\u25BC"),
                                            showTree && (React.createElement("div", { className: "adm-tree-popup", tabIndex: -1, style: {
                                                    position: 'absolute',
                                                    top: 24,
                                                    left: 0,
                                                    right: 0,
                                                    maxHeight: 180,
                                                    overflowY: 'auto',
                                                    background: 'var(--theia-editor-background, #fff)',
                                                    color: 'var(--theia-foreground, #333)',
                                                    border: '1px solid var(--theia-border, #ccc)',
                                                    borderRadius: 3,
                                                    boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
                                                    zIndex: 999,
                                                    padding: 6
                                                } },
                                                React.createElement(TreeSelect, { tree: symbolTree, onSelect: (path, type) => {
                                                        let val = path;
                                                        if (type === 'folder') {
                                                            // Append wildcard for folders
                                                            val = path === '*' ? '*' : `${path}\\*`;
                                                        }
                                                        setEditValue(val);
                                                        handleSaveFilterRule(idx, val);
                                                    } }))))) : (React.createElement("span", null, rule))));
                                }),
                                editingIndex === null && (React.createElement("div", { style: {
                                        display: 'flex',
                                        alignItems: 'center',
                                        padding: '4px 8px',
                                        color: 'var(--theia-successForeground, #2ecc71)',
                                        cursor: 'pointer',
                                        fontSize: 12
                                    }, onClick: handleAddFilterRule },
                                    React.createElement("span", { style: { marginRight: 6 } }, "\u2795"),
                                    React.createElement("span", null, "click to add..."))))),
                        React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 6, marginTop: 8 } },
                            React.createElement("input", { type: "checkbox", id: "allow_import", checked: allowImport, onChange: e => setAllowImport(e.target.checked) }),
                            React.createElement("label", { htmlFor: "allow_import", style: { cursor: 'pointer', fontSize: 11, userSelect: 'none', margin: 0 } }, "Allow importing symbol settings")))),
                    modalActiveTab === 'translations' && (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 12 } },
                        React.createElement("div", { style: { display: 'flex', gap: 8, alignItems: 'flex-end', background: 'var(--theia-editor-background)', padding: 10, border: '1px solid var(--theia-border)', borderRadius: 4 } },
                            React.createElement("div", { className: "adm-form-row", style: { flex: 2 } },
                                React.createElement("label", null, "Platform Symbol"),
                                React.createElement("input", { className: "adm-input", placeholder: "e.g. EURUSD or *", value: newRule.symbol, onChange: e => setNewRule({ ...newRule, symbol: e.target.value }) })),
                            React.createElement("div", { className: "adm-form-row", style: { flex: 2 } },
                                React.createElement("label", null, "Source Symbol"),
                                React.createElement("input", { className: "adm-input", placeholder: "e.g. EURUSD_pro or *.pro", value: newRule.source, onChange: e => setNewRule({ ...newRule, source: e.target.value }) })),
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
                                            " Delete"))))))))))),
                    modalActiveTab === 'parameters' && (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 12 } },
                        React.createElement("div", { style: { display: 'flex', gap: 8, alignItems: 'flex-end', background: 'var(--theia-editor-background)', padding: 10, border: '1px solid var(--theia-border)', borderRadius: 4 } },
                            React.createElement("div", { className: "adm-form-row", style: { flex: 1 } },
                                React.createElement("label", null, "Parameter Key"),
                                React.createElement("input", { className: "adm-input", placeholder: "e.g. Quotes Delay", value: newParam.key, onChange: e => setNewParam({ ...newParam, key: e.target.value }) })),
                            React.createElement("div", { className: "adm-form-row", style: { flex: 1 } },
                                React.createElement("label", null, "Value"),
                                React.createElement("input", { className: "adm-input", placeholder: "Value expression", value: newParam.val, onChange: e => setNewParam({ ...newParam, val: e.target.value }) })),
                            React.createElement("button", { type: "button", className: "adm-btn adm-btn-primary", style: { height: 26 }, onClick: handleAddParam },
                                React.createElement("i", { className: "codicon codicon-add" }),
                                " Add Param")),
                        React.createElement("div", { style: { maxHeight: '25vh', overflowY: 'auto', border: '1px solid var(--theia-border)', borderRadius: 4 } },
                            React.createElement("table", { className: "adm-table", style: { margin: 0 } },
                                React.createElement("thead", null,
                                    React.createElement("tr", null,
                                        React.createElement("th", null, "Parameter Name"),
                                        React.createElement("th", null, "Value"),
                                        React.createElement("th", { style: { width: 60 } }, "Action"))),
                                React.createElement("tbody", null, parameters.map((p, idx) => (React.createElement("tr", { key: idx },
                                    React.createElement("td", null,
                                        React.createElement("strong", null, p.key)),
                                    React.createElement("td", null,
                                        React.createElement("input", { className: "adm-input", style: { width: '100%', border: 'none', background: 'transparent', height: 20, padding: 0 }, value: p.val, onChange: e => {
                                                const updated = [...parameters];
                                                updated[idx].val = e.target.value;
                                                setParameters(updated);
                                            } })),
                                    React.createElement("td", null,
                                        React.createElement("button", { type: "button", className: "adm-btn", style: { padding: '2px 6px', color: 'var(--theia-errorForeground)' }, onClick: () => handleRemoveParam(idx) },
                                            React.createElement("i", { className: "codicon codicon-trash" }),
                                            " Delete"))))))))))),
                React.createElement("div", { className: "adm-modal-footer" },
                    React.createElement("button", { type: "submit", className: "adm-btn adm-btn-primary" }, modalMode === 'create' ? 'Add Feed Connector' : 'Save Changes'),
                    React.createElement("button", { type: "button", className: "adm-btn", onClick: () => setShowModal(false) }, "Cancel"))))),
        React.createElement("div", { className: "adm-statusbar" },
            React.createElement("span", null,
                "Total Configured Feeds: ",
                feeds.length),
            React.createElement("span", { className: "adm-sep" }, "|"),
            React.createElement("span", { style: { color: STATUS_COLOR.connected } },
                "Running: ",
                feeds.filter(f => f.is_active).length))));
}
exports.DataFeedsPage = DataFeedsPage;
//# sourceMappingURL=DataFeedsPage.js.map