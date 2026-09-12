// @ts-nocheck
import * as React from 'react';
import { API } from '../api';

interface Order {
    ticket: number;
    login: number;
    symbol: string;
    volume: number;
    volume_current: number;
    price_order: number;
    price_sl: number;
    price_tp: number;
    type: number; // 0=BUY, 1=SELL, 2=BUY LIMIT, 3=SELL LIMIT, 4=BUY STOP, 5=SELL STOP
    state: number; // 0=STARTED, 1=PARTIAL, 4=FILLED, 5=REJECTED/CANCELED, 6=PENDING_DEALER, 7=PENDING_GATEWAY
    reason: number;
    time_setup: string;
    time_done?: string;
}

const TYPE_MAP: Record<number, string> = {
    0: 'BUY',
    1: 'SELL',
    2: 'BUY LIMIT',
    3: 'SELL LIMIT',
    4: 'BUY STOP',
    5: 'SELL STOP'
};

const STATE_MAP: Record<number, string> = {
    0: 'PLACED',
    1: 'PARTIAL',
    4: 'FILLED',
    5: 'CANCELED',
    6: 'DEALER',
    7: 'GATEWAY'
};

const TYPE_COLOR: Record<string, string> = {
    'BUY':        '#27ae60', 'BUY LIMIT': '#2ecc71', 'BUY STOP': '#16a085',
    'SELL':       '#e74c3c', 'SELL LIMIT':'#c0392b', 'SELL STOP':'#922b21',
};
const STATE_COLOR: Record<string, string> = {
    PLACED: '#3498db', PARTIAL: '#f39c12', CANCELED: '#95a5a6', FILLED: '#27ae60', DEALER: '#9b59b6', GATEWAY: '#e67e22'
};

interface Props { view: 'active' | 'history' | 'new'; }

export function OrdersPage({ view }: Props): React.ReactElement {
    const [orders, setOrders] = React.useState<Order[]>([]);
    const [sel, setSel] = React.useState<number | null>(null);
    const [filter, setFilter] = React.useState('');
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState<string | null>(null);

    // Initial configuration lists
    const [accounts, setAccounts] = React.useState<any[]>([]);
    const [symbols, setSymbols] = React.useState<any[]>([]);
    const [groups, setGroups] = React.useState<any[]>([]);
    const [ticks, setTicks] = React.useState<Record<string, { bid: number; ask: number; age: number }>>({});

    // Hierarchical tree state
    const [treeOpen, setTreeOpen] = React.useState(false);
    const [searchQuery, setSearchQuery] = React.useState('');
    const [expandedFolders, setExpandedFolders] = React.useState<Record<string, boolean>>({
        'forex': true, 'Metals': true, 'crypto': true, 'Custom': true
    });

    // New order form state
    const [newOrder, setNewOrder] = React.useState({
        login: '',
        symbol: 'forex\\EURUSD',
        type: '0', // OP_BUY
        volume: '0.10',
        price_request: '',
        price_sl: '0',
        price_tp: '0',
        type_filling: 'FOK',
        comment: ''
    });
    const [formMsg, setFormMsg] = React.useState<{ status: 'SUCCESS' | 'ERROR'; text: string } | null>(null);

    // Compute if the selected symbol is allowed under the current account's group settings
    const isSymbolAllowed = React.useMemo(() => {
        if (!newOrder.symbol) return true;
        const selectedAcc = accounts.find(a => String(a.login) === String(newOrder.login));
        if (!selectedAcc) return true;

        const groupName = selectedAcc.group_name;
        const group = groups.find(g => g.name === groupName);
        if (!group) return true;

        let symbolRules: any[] = [];
        if (group.settings_json) {
            try {
                const settings = typeof group.settings_json === 'string' ? JSON.parse(group.settings_json) : group.settings_json;
                symbolRules = settings.symbol_rules || [];
            } catch {}
        }

        if (symbolRules.length === 0) return true;

        let matchingRules = symbolRules.filter(rule => {
            try {
                const pattern = rule.symbol;
                const regexStr = '^' + pattern
                    .replace(/[\-+^${}()|[\]\.]/g, '\\$&')
                    .replace(/\\/g, '\\\\')
                    .replace(/\*/g, '.*')
                    .replace(/\?/g, '.') + '$';
                const regex = new RegExp(regexStr, 'i');
                return regex.test(newOrder.symbol);
            } catch {
                return false;
            }
        });

        if (matchingRules.length === 0) return false;
        matchingRules.sort((a, b) => b.symbol.length - a.symbol.length);
        return matchingRules[0].trade_allowed;
    }, [newOrder.symbol, newOrder.login, accounts, groups]);

    // Parse symbols list into directory structure
    const tree = React.useMemo(() => {
        const root: any = { files: [], dirs: {} };
        symbols.forEach(s => {
            const parts = s.symbol.split('\\');
            let curr = root;
            for (let i = 0; i < parts.length - 1; i++) {
                const dirName = parts[i];
                if (!curr.dirs[dirName]) {
                    curr.dirs[dirName] = { name: dirName, files: [], dirs: {} };
                }
                curr = curr.dirs[dirName];
            }
            curr.files.push(s.symbol);
        });
        return root;
    }, [symbols]);

    // Live price variables for the selected symbol
    const currentTick = ticks[newOrder.symbol] || ticks[newOrder.symbol.split('\\').pop() || ''] || null;
    const bidPrice = currentTick ? currentTick.bid : 1.08000;
    const askPrice = currentTick ? currentTick.ask : 1.08010;

    const loadOrders = async () => {
        setLoading(true);
        setError(null);
        try {
            if (view === 'active') {
                const data = await API.getOrders();
                setOrders(data);
            } else if (view === 'history') {
                const data = await API.getOrderHistory();
                setOrders(data);
            }
        } catch (err: any) {
            setError(err.message || 'Failed to load orders.');
        } finally {
            setLoading(false);
        }
    };

    React.useEffect(() => {
        if (view !== 'new') {
            loadOrders();
        } else {
            // Load setup metadata
            const loadMetadata = async () => {
                try {
                    const [accs, syms, grps] = await Promise.all([
                        API.getAccounts(),
                        API.getSymbols(),
                        API.getGroups()
                    ]);
                    setAccounts(accs);
                    setSymbols(syms);
                    setGroups(grps);
                    if (accs.length > 0) {
                        setNewOrder(prev => ({ ...prev, login: String(accs[0].login) }));
                    }
                    if (syms.length > 0) {
                        // Select first symbol path that is not dummy
                        const valid = syms.find(s => !s.symbol.includes('.dummy'));
                        if (valid) {
                            setNewOrder(prev => ({ ...prev, symbol: valid.symbol }));
                        }
                    }
                } catch (err: any) {
                    setError(err.message || 'Failed to load accounts, symbols, and groups list.');
                }
            };
            loadMetadata();

            // Setup tick polling interval
            const tickPoll = setInterval(async () => {
                try {
                    const data = await API.getTicks();
                    setTicks(data);
                } catch {
                    // Ignore transient network errors
                }
            }, 1000);
            return () => clearInterval(tickPoll);
        }
    }, [view]);

    const handleExecuteOrder = async (overrideType?: number, overridePrice?: number) => {
        setFormMsg(null);
        try {
            const login = parseInt(newOrder.login);
            if (!login) throw new Error('Please select a valid account login.');

            const oType = overrideType !== undefined ? overrideType : parseInt(newOrder.type);
            
            let price_req = overridePrice !== undefined ? overridePrice : parseFloat(newOrder.price_request);
            if ([0, 1].includes(oType)) {
                // If it is market buy or sell, default to streaming quotes if empty
                if (!price_req) {
                    price_req = oType === 0 ? askPrice : bidPrice;
                }
            } else {
                if (!price_req) throw new Error('Execution trigger price is required for pending orders.');
            }

            const payload = {
                login,
                symbol: newOrder.symbol,
                volume: parseFloat(newOrder.volume) || 0.1,
                price_request: price_req,
                type: oType,
                price_sl: parseFloat(newOrder.price_sl) || 0,
                price_tp: parseFloat(newOrder.price_tp) || 0,
                type_filling: newOrder.type_filling
            };

            const resp = await API.placeOrder(payload);
            setFormMsg({ 
                status: 'SUCCESS', 
                text: `Order filled successfully! Ticket #${resp.ticket}. Match status: ${resp.status}. Detail: ${resp.message}` 
            });
        } catch (err: any) {
            setFormMsg({ status: 'ERROR', text: err.message || 'Order execution failed.' });
        }
    };

    const handlePlaceOrder = async (e: React.FormEvent) => {
        e.preventDefault();
        await handleExecuteOrder();
    };

    const handleCancelOrder = async () => {
        if (!sel) return;
        setError(null);
        try {
            await API.cancelOrder(sel);
            setSel(null);
            await loadOrders();
        } catch (err: any) {
            setError(err.message || 'Failed to cancel order.');
        }
    };

    const renderNode = (node: any, path: string = '', depth: number = 0) => {
        const elements: any[] = [];
        
        // Render directories
        Object.keys(node.dirs).sort().forEach(dirName => {
            const dir = node.dirs[dirName];
            const fullDirPath = path ? `${path}\\${dirName}` : dirName;
            const isExpanded = !!expandedFolders[fullDirPath];
            elements.push(
                <div key={fullDirPath} style={{ paddingLeft: depth * 10 }}>
                    <div 
                        style={{ 
                            display: 'flex', 
                            alignItems: 'center', 
                            gap: 6, 
                            height: 24, 
                            cursor: 'pointer', 
                            opacity: 0.9,
                            fontSize: '11.5px',
                            fontWeight: 600,
                            color: 'var(--theia-descriptionForeground)'
                        }}
                        onClick={(e) => {
                            e.stopPropagation();
                            setExpandedFolders(prev => ({ ...prev, [fullDirPath]: !isExpanded }));
                        }}
                    >
                        <i className={`codicon ${isExpanded ? 'codicon-chevron-down' : 'codicon-chevron-right'}`} style={{ fontSize: 10 }} />
                        <i className="codicon codicon-folder" style={{ color: '#f39c12', fontSize: 12 }} />
                        <span>{dirName}</span>
                    </div>
                    {isExpanded && renderNode(dir, fullDirPath, depth + 1)}
                </div>
            );
        });
        
        // Render leaf files
        node.files.sort().forEach((symPath: string) => {
            const baseName = symPath.split('\\').pop() || symPath;
            if (baseName.includes('.dummy')) return; // hide dummy nodes
            
            elements.push(
                <div 
                    key={symPath} 
                    style={{ 
                        paddingLeft: (depth * 10) + 16, 
                        display: 'flex', 
                        alignItems: 'center', 
                        gap: 6, 
                        height: 24, 
                        cursor: 'pointer',
                        background: newOrder.symbol === symPath ? 'var(--theia-list-activeSelectionBackground)' : 'transparent',
                        color: newOrder.symbol === symPath ? 'var(--theia-list-activeSelectionForeground)' : 'inherit',
                        borderRadius: 3,
                        fontSize: '11px'
                    }}
                    onClick={(e) => {
                        e.stopPropagation();
                        setNewOrder(prev => ({ ...prev, symbol: symPath }));
                        setTreeOpen(false);
                    }}
                >
                    <i className="codicon codicon-symbol-variable" style={{ fontSize: 11, opacity: 0.8 }} />
                    <span>{baseName}</span>
                </div>
            );
        });
        
        return elements;
    };

    if (view === 'new') {
        const isMarket = ['0', '1'].includes(newOrder.type);
        const filteredSymbols = symbols.filter(s => 
            s.symbol.toLowerCase().includes(searchQuery.toLowerCase()) && !s.symbol.includes('.dummy')
        );

        return (
            <div className="adm-page">
                <form onSubmit={handlePlaceOrder} style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                    <div className="adm-toolbar">
                        {!isMarket && (
                            <button type="submit" className="adm-btn adm-btn-primary">
                                <i className="codicon codicon-check" /> Place Pending Order
                            </button>
                        )}
                        <button 
                            type="button" 
                            className="adm-btn" 
                            onClick={() => {
                                setFormMsg(null);
                                setNewOrder({
                                    login: accounts.length > 0 ? String(accounts[0].login) : '',
                                    symbol: symbols.length > 0 ? symbols[0].symbol : 'forex\\EURUSD',
                                    type: '0',
                                    volume: '0.10',
                                    price_request: '',
                                    price_sl: '0',
                                    price_tp: '0',
                                    type_filling: 'FOK',
                                    comment: ''
                                });
                            }}
                        >
                            <i className="codicon codicon-discard" /> Reset fields
                        </button>
                    </div>
                    {formMsg && (
                        <div className="adm-hint" style={{
                            background: formMsg.status === 'SUCCESS' ? 'var(--theia-inputValidation-infoBackground)' : 'var(--theia-inputValidation-errorBackground)',
                            color: formMsg.status === 'SUCCESS' ? 'var(--theia-successForeground)' : 'var(--theia-errorForeground)'
                        }}>
                            <i className={formMsg.status === 'SUCCESS' ? 'codicon codicon-info' : 'codicon codicon-error'} /> {formMsg.text}
                        </div>
                    )}
                    <div className="adm-form-body" style={{ maxWidth: 520 }}>
                        <div className="adm-form-section">1. Client Account</div>
                        <div className="adm-form-row">
                            <label>Login ID</label>
                            <select 
                                className="adm-select" 
                                style={{ width: 320 }}
                                value={newOrder.login} 
                                onChange={e => setNewOrder({ ...newOrder, login: e.target.value })}
                            >
                                {accounts.length === 0 ? (
                                    <option value="">No accounts found</option>
                                ) : (
                                    accounts.map(acc => (
                                        <option key={acc.login} value={acc.login}>
                                            {acc.login} ({acc.group_name}) — Balance: ${acc.balance.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                                        </option>
                                    ))
                                )}
                            </select>
                        </div>

                        <div className="adm-form-section">2. Instrument & Volume</div>
                        <div className="adm-form-row" style={{ zIndex: 100 }}>
                            <label>Symbol Path</label>
                            <div style={{ position: 'relative', width: 320 }}>
                                <div 
                                    className="adm-select" 
                                    style={{ 
                                        display: 'flex', 
                                        justifyContent: 'space-between', 
                                        alignItems: 'center', 
                                        width: '100%', 
                                        boxSizing: 'border-box',
                                        background: 'var(--theia-input-background)',
                                        border: '1px solid var(--theia-input-border)',
                                        cursor: 'pointer'
                                    }}
                                    onClick={() => setTreeOpen(!treeOpen)}
                                >
                                    <span style={{ fontFamily: 'monospace' }}>{newOrder.symbol || 'Choose platform path...'}</span>
                                    <i className={`codicon ${treeOpen ? 'codicon-chevron-up' : 'codicon-chevron-down'}`} />
                                </div>
                                {!isSymbolAllowed && (
                                    <div style={{
                                        color: 'var(--theia-errorForeground)',
                                        fontSize: '11px',
                                        marginTop: 4,
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: 4
                                    }}>
                                        <i className="codicon codicon-warning" style={{ fontSize: 12 }} />
                                        <span>Warning: Trading is not allowed for this symbol under your group settings</span>
                                    </div>
                                )}
                                {treeOpen && (
                                    <div style={{
                                        position: 'absolute',
                                        top: '100%',
                                        left: 0,
                                        width: '100%',
                                        maxHeight: 220,
                                        overflowY: 'auto',
                                        background: 'var(--theia-editor-background)',
                                        border: '1px solid var(--theia-widget-border)',
                                        borderRadius: '0 0 4px 4px',
                                        zIndex: 1000,
                                        boxShadow: '0 4px 16px rgba(0,0,0,0.5)',
                                        padding: 8,
                                        boxSizing: 'border-box'
                                    }}>
                                        <input 
                                            className="adm-input" 
                                            placeholder="Filter symbols..." 
                                            style={{ width: '100%', marginBottom: 8, boxSizing: 'border-box' }}
                                            value={searchQuery}
                                            onChange={e => setSearchQuery(e.target.value)}
                                            onClick={e => e.stopPropagation()}
                                        />
                                        {searchQuery ? (
                                            filteredSymbols.length === 0 ? (
                                                <div style={{ opacity: 0.5, padding: 4 }}>No symbols match</div>
                                            ) : (
                                                filteredSymbols.map(s => (
                                                    <div 
                                                        key={s.symbol}
                                                        style={{ 
                                                            display: 'flex', 
                                                            alignItems: 'center', 
                                                            gap: 6, 
                                                            height: 22, 
                                                            cursor: 'pointer',
                                                            padding: '2px 6px',
                                                            borderRadius: 3,
                                                            background: newOrder.symbol === s.symbol ? 'var(--theia-list-activeSelectionBackground)' : 'transparent',
                                                            color: newOrder.symbol === s.symbol ? 'var(--theia-list-activeSelectionForeground)' : 'inherit',
                                                            fontSize: '11px'
                                                        }}
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            setNewOrder(prev => ({ ...prev, symbol: s.symbol }));
                                                            setTreeOpen(false);
                                                        }}
                                                    >
                                                        <i className="codicon codicon-symbol-variable" />
                                                        <span>{s.symbol}</span>
                                                    </div>
                                                ))
                                            )
                                        ) : (
                                            renderNode(tree)
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="adm-form-row">
                            <label>Volume (Lots)</label>
                            <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                                <input 
                                    className="adm-input" 
                                    type="number" 
                                    step="0.01" 
                                    min="0.01" 
                                    value={newOrder.volume} 
                                    onChange={e => setNewOrder({ ...newOrder, volume: e.target.value })} 
                                />
                                {['0.01', '0.10', '1.00', '10.00'].map(vol => (
                                    <button 
                                        type="button" 
                                        key={vol} 
                                        className="adm-btn" 
                                        style={{ padding: '3px 6px', fontSize: 10 }}
                                        onClick={() => setNewOrder({ ...newOrder, volume: vol })}
                                    >
                                        {vol} Lot
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="adm-form-section">3. Execution & Price</div>
                        <div className="adm-form-row">
                            <label>Order Type</label>
                            <select 
                                className="adm-select" 
                                style={{ width: 320 }}
                                value={newOrder.type} 
                                onChange={e => setNewOrder({ ...newOrder, type: e.target.value })}
                            >
                                <option value="0">Buy (Market)</option>
                                <option value="1">Sell (Market)</option>
                                <option value="2">Buy Limit (Pending)</option>
                                <option value="3">Sell Limit (Pending)</option>
                                <option value="4">Buy Stop (Pending)</option>
                                <option value="5">Sell Stop (Pending)</option>
                            </select>
                        </div>

                        {/* Interactive BUY/SELL Execution Panel for Market Orders */}
                        {isMarket && (
                            <div style={{ margin: '14px 0', width: 320 }}>
                                <div style={{ fontSize: 11, color: 'var(--theia-descriptionForeground)', marginBottom: 6, fontWeight: 600 }}>
                                    Live streaming quotes (Click bid/ask to execute instantly)
                                </div>
                                <div style={{ display: 'flex', gap: 12 }}>
                                    <button 
                                        type="button"
                                        className="adm-btn"
                                        style={{ 
                                            flex: 1, 
                                            height: 52, 
                                            display: 'flex', 
                                            flexDirection: 'column', 
                                            alignItems: 'center', 
                                            justifyContent: 'center',
                                            borderColor: '#e74c3c',
                                            color: '#fff',
                                            background: '#e74c3c',
                                            borderRadius: 4
                                        }}
                                        onClick={() => handleExecuteOrder(1, bidPrice)}
                                    >
                                        <span style={{ fontSize: 10, fontWeight: 700, opacity: 0.9 }}>SELL (Market)</span>
                                        <span style={{ fontSize: 16, fontWeight: 700, fontFamily: 'monospace', letterSpacing: 0.5 }}>{bidPrice.toFixed(5)}</span>
                                    </button>
                                    <button 
                                        type="button"
                                        className="adm-btn adm-btn-primary"
                                        style={{ 
                                            flex: 1, 
                                            height: 52, 
                                            display: 'flex', 
                                            flexDirection: 'column', 
                                            alignItems: 'center', 
                                            justifyContent: 'center',
                                            background: '#27ae60',
                                            borderColor: 'transparent',
                                            color: '#fff',
                                            borderRadius: 4
                                        }}
                                        onClick={() => handleExecuteOrder(0, askPrice)}
                                    >
                                        <span style={{ fontSize: 10, fontWeight: 700, opacity: 0.9 }}>BUY (Market)</span>
                                        <span style={{ fontSize: 16, fontWeight: 700, fontFamily: 'monospace', letterSpacing: 0.5 }}>{askPrice.toFixed(5)}</span>
                                    </button>
                                </div>
                                {currentTick && (
                                    <div style={{ fontSize: 10, opacity: 0.6, marginTop: 4, textAlign: 'center' }}>
                                        Quote latency: {currentTick.age.toFixed(1)}s old
                                    </div>
                                )}
                            </div>
                        )}

                        {!isMarket && (
                            <div className="adm-form-row">
                                <label>Pending Activation Price</label>
                                <input 
                                    className="adm-input" 
                                    type="number" 
                                    step="0.00001" 
                                    placeholder="Enter target trigger price" 
                                    value={newOrder.price_request} 
                                    onChange={e => setNewOrder({ ...newOrder, price_request: e.target.value })} 
                                />
                            </div>
                        )}

                        <div className="adm-form-row">
                            <label>Stop Loss (SL)</label>
                            <input 
                                className="adm-input" 
                                type="number" 
                                step="0.00001" 
                                placeholder="0 = No SL limits" 
                                value={newOrder.price_sl} 
                                onChange={e => setNewOrder({ ...newOrder, price_sl: e.target.value })} 
                            />
                        </div>
                        <div className="adm-form-row">
                            <label>Take Profit (TP)</label>
                            <input 
                                className="adm-input" 
                                type="number" 
                                step="0.00001" 
                                placeholder="0 = No TP limits" 
                                value={newOrder.price_tp} 
                                onChange={e => setNewOrder({ ...newOrder, price_tp: e.target.value })} 
                            />
                        </div>

                        <div className="adm-form-section">4. Filling Policy & Meta</div>
                        <div className="adm-form-row">
                            <label>Filling Policy (Mode)</label>
                            <select 
                                className="adm-select" 
                                style={{ width: 320 }}
                                value={newOrder.type_filling} 
                                onChange={e => setNewOrder({ ...newOrder, type_filling: e.target.value })}
                            >
                                <option value="FOK">Fill or Kill (FOK)</option>
                                <option value="IOC">Immediate or Cancel (IOC)</option>
                                <option value="RETURN">Return (Partial execution allowed)</option>
                            </select>
                            <span className="adm-hint-text" style={{ maxWidth: 320 }}>
                                FOK executes full size or cancels. IOC executes what matches, cancels remainder. Return allows partial matches.
                            </span>
                        </div>
                        <div className="adm-form-row">
                            <label>Order Comment</label>
                            <input 
                                className="adm-input" 
                                placeholder="Enter audit/test remarks" 
                                style={{ width: 320 }} 
                                value={newOrder.comment} 
                                onChange={e => setNewOrder({ ...newOrder, comment: e.target.value })} 
                            />
                        </div>
                    </div>
                </form>
            </div>
        );
    }

    const filtered = orders.filter(o =>
        String(o.login).includes(filter) ||
        o.symbol.toLowerCase().includes(filter.toLowerCase()) ||
        String(o.ticket).includes(filter)
    );

    return (
        <div className="adm-page">
            <div className="adm-toolbar">
                {view === 'active' && <>
                    <button className="adm-btn adm-btn-danger" disabled={!sel} onClick={handleCancelOrder}><i className="codicon codicon-close" /> Cancel Order</button>
                    <div className="adm-toolbar-sep" />
                </>}
                <button className="adm-btn" onClick={loadOrders} title="Reload data">
                    <i className="codicon codicon-refresh" /> Refresh
                </button>
                <div className="adm-toolbar-sep" />
                <div className="adm-search-wrap">
                    <i className="codicon codicon-search" />
                    <input className="adm-search" placeholder="Filter by login, symbol, ticket..." value={filter} onChange={e => setFilter(e.target.value)} />
                </div>
            </div>

            {error && (
                <div className="adm-hint" style={{ background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)' }}>
                    <i className="codicon codicon-error" /> {error}
                </div>
            )}

            <div className="adm-table-wrap">
                {loading ? (
                    <div style={{ padding: 20, textAlign: 'center', opacity: 0.7 }}>Loading orders...</div>
                ) : filtered.length === 0 ? (
                    <div style={{ padding: 20, textAlign: 'center', opacity: 0.7 }}>No orders found.</div>
                ) : (
                    <table className="adm-table">
                        <thead>
                            <tr>
                                <th>Ticket</th><th>Login</th><th>Symbol</th><th>Type</th><th>Volume</th><th>Current Volume</th>
                                <th>Order Price</th><th>S/L</th><th>T/P</th><th>State</th><th>Reason</th><th>Time Placed</th>
                                {view === 'history' && <th>Time Settled</th>}
                            </tr>
                        </thead>
                        <tbody>
                            {filtered.map(o => {
                                const typeStr = TYPE_MAP[o.type] || 'UNKNOWN';
                                const stateStr = STATE_MAP[o.state] || 'UNKNOWN';
                                const reasonStr = o.reason === 0 ? 'CLIENT' : o.reason === 4 ? 'S/L' : o.reason === 5 ? 'T/P' : 'S/O';
                                
                                return (
                                    <tr key={o.ticket} className={sel === o.ticket ? 'selected' : ''} onClick={() => setSel(o.ticket)}>
                                        <td><strong>{o.ticket}</strong></td>
                                        <td>{o.login}</td>
                                        <td><strong>{o.symbol}</strong></td>
                                        <td>
                                            <span className="adm-side-badge" style={{
                                                background: (TYPE_COLOR[typeStr] || '#888') + '22',
                                                color: TYPE_COLOR[typeStr] || '#888',
                                                border: `1px solid ${(TYPE_COLOR[typeStr] || '#888')}55`
                                            }}>{typeStr}</span>
                                        </td>
                                        <td>{(o.volume || 0).toFixed(2)}</td>
                                        <td>{(o.volume_current || 0).toFixed(2)}</td>
                                        <td className="adm-num">{(o.price_order || 0).toFixed(5)}</td>
                                        <td className="adm-num">{o.price_sl || '—'}</td>
                                        <td className="adm-num">{o.price_tp || '—'}</td>
                                        <td>
                                            <span className="adm-tag" style={{
                                                color: STATE_COLOR[stateStr] || '#aaa',
                                                border: `1px solid ${(STATE_COLOR[stateStr] || '#aaa')}55`
                                            }}>{stateStr}</span>
                                        </td>
                                        <td>{reasonStr}</td>
                                        <td>{o.time_setup || '—'}</td>
                                        {view === 'history' && <td>{o.time_done || '—'}</td>}
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                )}
            </div>

            <div className="adm-statusbar">
                <span>{view === 'active' ? 'Active' : 'Settled'} Orders: {filtered.length}</span>
            </div>
        </div>
    );
}
