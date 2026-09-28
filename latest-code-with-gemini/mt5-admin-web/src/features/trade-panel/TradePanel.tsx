import * as React from 'react';
import { API } from '../../services/api';
import './trade-panel.css';

interface Props {
    instanceId?: string;
    setTitle?: (title: string) => void;
    close?: () => void;
}

interface AccountItem {
    login: number;
    name: string;
    group: string;
    balance: number;
    equity: number;
    margin: number;
    margin_free: number;
    margin_level: number;
    leverage: number;
    currency: string;
}

interface PositionItem {
    position_id: string | number;
    ticket?: string | number;
    login: number;
    symbol: string;
    type: number | string;
    volume: number;
    price_open: number;
    price_current: number;
    sl: number;
    tp: number;
    profit: number;
    open_time?: string;
    comment?: string;
}

interface OrderItem {
    ticket: string | number;
    login: number;
    symbol: string;
    type: number | string;
    volume: number;
    price_order: number;
    price_current?: number;
    price_sl?: number;
    price_tp?: number;
    state?: string | number;
    time_setup?: string;
    comment?: string;
}

interface LogEntry {
    id: string;
    time: string;
    action: string;
    success: boolean;
    message: string;
    data?: any;
}

const COMMON_SYMBOLS = ['BTCUSD', 'ETHUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'SOLUSD'];
const VOLUME_PRESETS = [0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0];

export function TradePanel({ instanceId, setTitle }: Props): React.ReactElement {
    // Unique ID for this panel instance
    const panelId = React.useMemo(() => instanceId || `panel-${Math.floor(Math.random() * 10000)}`, [instanceId]);

    // Data lists
    const [accounts, setAccounts] = React.useState<AccountItem[]>([]);
    const [symbols, setSymbols] = React.useState<string[]>(COMMON_SYMBOLS);
    const [positions, setPositions] = React.useState<PositionItem[]>([]);
    const [orders, setOrders] = React.useState<OrderItem[]>([]);
    const [quotes, setQuotes] = React.useState<Record<string, { bid: number; ask: number; spread: number }>>({});
    const [logs, setLogs] = React.useState<LogEntry[]>([]);

    // Active Selection
    const [selectedLogin, setSelectedLogin] = React.useState<number>(10001);
    const [customLogin, setCustomLogin] = React.useState<string>('10001');
    const [selectedSymbol, setSelectedSymbol] = React.useState<string>('BTCUSD');
    const [filterAccountOnly, setFilterAccountOnly] = React.useState<boolean>(true);

    // Order Draft State
    const [orderType, setOrderType] = React.useState<string>('buy'); // buy, sell, buy_limit, sell_limit, buy_stop, sell_stop
    const [volume, setVolume] = React.useState<number>(0.10);
    const [orderPrice, setOrderPrice] = React.useState<string>('');
    const [sl, setSl] = React.useState<string>('');
    const [tp, setTp] = React.useState<string>('');
    const [routing, setRouting] = React.useState<string>('Auto'); // Auto, A-Book, B-Book
    const [fillType, setFillType] = React.useState<string>('FOK'); // FOK, IOC, RETURN
    const [deviation, setDeviation] = React.useState<number>(10);
    const [comment, setComment] = React.useState<string>(`Debug Trade`);

    // UI State
    const [isSubmitting, setIsSubmitting] = React.useState<boolean>(false);
    const [autoRefresh, setAutoRefresh] = React.useState<boolean>(true);
    const [advancedOpen, setAdvancedOpen] = React.useState<boolean>(false);

    // Modify Position / Order Modal State
    const [modifyingItem, setModifyingItem] = React.useState<{ kind: 'position' | 'order'; item: any } | null>(null);
    const [modSl, setModSl] = React.useState<string>('');
    const [modTp, setModTp] = React.useState<string>('');
    const [modPrice, setModPrice] = React.useState<string>('');

    // Partial close state
    const [partialItem, setPartialItem] = React.useState<PositionItem | null>(null);
    const [partialLots, setPartialLots] = React.useState<number>(0.05);

    // Flash states for live quote changes
    const [flashBid, setFlashBid] = React.useState<'up' | 'down' | null>(null);
    const [flashAsk, setFlashAsk] = React.useState<'up' | 'down' | null>(null);
    const prevQuoteRef = React.useRef<{ bid: number; ask: number } | null>(null);

    // 1. Initial Load of Accounts & Symbols
    const loadMetadata = React.useCallback(async () => {
        try {
            const [accs, syms] = await Promise.all([
                API.getAccounts().catch(() => []),
                API.getSymbols().catch(() => []),
            ]);
            if (Array.isArray(accs) && accs.length > 0) {
                setAccounts(accs);
                // If 10001 or 744209 exist, keep default; otherwise select first
                if (!accs.some(a => a.login === selectedLogin)) {
                    setSelectedLogin(accs[0].login);
                    setCustomLogin(String(accs[0].login));
                }
            }
            if (Array.isArray(syms) && syms.length > 0) {
                const names = Array.from(new Set(syms.map(s => s.name || s.symbol).filter(Boolean)));
                setSymbols(names);
            }
        } catch (err) {
            console.error('Failed to load accounts/symbols for trade panel', err);
        }
    }, [selectedLogin]);

    // 2. Fetch Live Quotes & Open Positions/Orders
    const refreshData = React.useCallback(async () => {
        try {
            const [ticksData, posData, ordData] = await Promise.all([
                API.getTicks().catch(() => ({})),
                API.getPositions().catch(() => []),
                API.getOrders({ openOnly: true }).catch(() => []),
            ]);

            // Update Quotes
            if (ticksData && typeof ticksData === 'object') {
                const nextQuotes: Record<string, { bid: number; ask: number; spread: number }> = {};
                for (const [k, v] of Object.entries(ticksData as Record<string, any>)) {
                    nextQuotes[k.toUpperCase()] = {
                        bid: Number(v.bid || 0),
                        ask: Number(v.ask || 0),
                        spread: Number(v.spread || 0),
                    };
                }
                setQuotes(nextQuotes);

                // Check flash for selected symbol
                const cur = nextQuotes[selectedSymbol.toUpperCase()];
                if (cur && prevQuoteRef.current) {
                    if (cur.bid > prevQuoteRef.current.bid) setFlashBid('up');
                    else if (cur.bid < prevQuoteRef.current.bid) setFlashBid('down');

                    if (cur.ask > prevQuoteRef.current.ask) setFlashAsk('up');
                    else if (cur.ask < prevQuoteRef.current.ask) setFlashAsk('down');

                    setTimeout(() => {
                        setFlashBid(null);
                        setFlashAsk(null);
                    }, 400);
                }
                if (cur) {
                    prevQuoteRef.current = cur;
                }
            }

            // Update Positions & Orders
            if (Array.isArray(posData)) {
                setPositions(posData);
            }
            if (Array.isArray(ordData)) {
                setOrders(ordData);
            }
        } catch (err) {
            console.error('TradePanel refreshData error', err);
        }
    }, [selectedSymbol]);

    // Auto-refresh loop
    React.useEffect(() => {
        loadMetadata();
        refreshData();
    }, [loadMetadata, refreshData]);

    React.useEffect(() => {
        if (!autoRefresh) return;
        const interval = setInterval(() => {
            refreshData();
        }, 2000);
        return () => clearInterval(interval);
    }, [autoRefresh, refreshData]);

    // Update panel title dynamically
    React.useEffect(() => {
        if (setTitle) {
            setTitle(`Trade #${selectedLogin} • ${selectedSymbol}`);
        }
    }, [selectedLogin, selectedSymbol, setTitle]);

    // Active Account Details
    const activeAccount = React.useMemo(() => {
        return accounts.find(a => a.login === selectedLogin) || {
            login: selectedLogin,
            name: `Account #${selectedLogin}`,
            group: 'standard',
            balance: 10000,
            equity: 10000,
            margin: 0,
            margin_free: 10000,
            margin_level: 0,
            leverage: 100,
            currency: 'USD'
        };
    }, [accounts, selectedLogin]);

    // Active Quote
    const activeQuote = quotes[selectedSymbol.toUpperCase()] || { bid: 0, ask: 0, spread: 0 };

    // Filtered Positions & Orders (only genuinely open positions & active pending orders)
    const displayedPositions = React.useMemo(() => {
        const active = positions.filter(p => Number(p.volume) > 0);
        if (!filterAccountOnly) return active;
        return active.filter(p => Number(p.login) === Number(selectedLogin));
    }, [positions, filterAccountOnly, selectedLogin]);

    const displayedOrders = React.useMemo(() => {
        const pending = orders.filter(o => {
            const s = String(o.state || '').toLowerCase();
            return s !== 'filled' && s !== 'cancelled' && s !== 'rejected' && s !== 'expired';
        });
        if (!filterAccountOnly) return pending;
        return pending.filter(o => Number(o.login) === Number(selectedLogin));
    }, [orders, filterAccountOnly, selectedLogin]);

    // Logging helper
    const addLog = (action: string, success: boolean, message: string, data?: any) => {
        const entry: LogEntry = {
            id: `log-${Date.now()}-${Math.random()}`,
            time: new Date().toLocaleTimeString(),
            action,
            success,
            message,
            data,
        };
        setLogs(prev => [entry, ...prev.slice(0, 49)]); // keep last 50
    };

    // Quick Place Order Function
    const handlePlaceTrade = async (overrideType?: string) => {
        const finalOp = overrideType || orderType;
        const isMarket = finalOp === 'buy' || finalOp === 'sell';
        setIsSubmitting(true);

        const payload: any = {
            login: selectedLogin,
            symbol: selectedSymbol,
            volume: volume,
            operation: finalOp,
            deviation: deviation,
            fill_type: fillType,
            routing: routing !== 'Auto' ? routing : undefined,
            comment: comment || 'Debug Trade',
        };

        if (!isMarket && orderPrice) {
            payload.price = orderPrice;
        } else if (isMarket) {
            // Optional price reference
            payload.price = finalOp === 'buy' ? activeQuote.ask : activeQuote.bid;
        }

        if (sl) payload.stoploss = sl;
        if (tp) payload.takeprofit = tp;

        try {
            const res = await API.placeOrder(payload);
            const success = res.retcode === 0 || !res.retcode;
            addLog(
                `OrderSend (${finalOp.toUpperCase()} ${volume} ${selectedSymbol})`,
                success,
                res.message || (success ? 'Order executed successfully' : 'Order rejected'),
                res
            );
            await refreshData();
        } catch (err: any) {
            addLog(
                `OrderSend (${finalOp.toUpperCase()}) FAILED`,
                false,
                err.message || 'Execution error',
                err
            );
        } finally {
            setIsSubmitting(false);
        }
    };

    // Close Single Position
    const handleClosePosition = async (ticket: string | number, lots?: number) => {
        try {
            const res = await API.closePosition(ticket, lots);
            const success = res.retcode === 0 || !res.retcode;
            addLog(
                `OrderClose #${ticket} (${lots ? `${lots} lots` : 'Full'})`,
                success,
                res.message || 'Position closed successfully',
                res
            );
            await refreshData();
        } catch (err: any) {
            addLog(`OrderClose #${ticket} FAILED`, false, err.message || 'Close failed', err);
        }
    };

    // Delete / Cancel Pending Order
    const handleCancelOrder = async (ticket: string | number, force = false) => {
        try {
            const res = await API.cancelOrder(ticket, force);
            const success = res.retcode === 0 || !res.retcode;
            addLog(`OrderDelete #${ticket}`, success, res.message || 'Order deleted successfully', res);
            await refreshData();
        } catch (err: any) {
            const errMsg = err.message || 'Cancel failed';
            addLog(`OrderDelete #${ticket} FAILED`, false, errMsg, err);
            if (!force && confirm(`Order cancellation notice:\n"${errMsg}"\n\nDo you want to permanently force-purge this order record from the database?`)) {
                await handleCancelOrder(ticket, true);
            }
        }
    };

    // Bulk Close Positions
    const handleCloseAll = async () => {
        if (!confirm(`Close all open positions for account ${selectedLogin}?`)) return;
        try {
            for (const p of displayedPositions) {
                const posId = p.position_id ?? p.ticket;
                if (posId !== undefined) {
                    await API.closePosition(posId);
                }
            }
            addLog(`CloseAllPositions`, true, `Requested closure of ${displayedPositions.length} positions`);
            await refreshData();
        } catch (err: any) {
            addLog(`CloseAllPositions FAILED`, false, err.message || 'Bulk close failed');
        }
    };

    // Open Modify Dialog
    const startModify = (item: any, kind: 'position' | 'order') => {
        setModifyingItem({ kind, item });
        setModSl(item.sl || item.price_sl ? String(item.sl || item.price_sl) : '');
        setModTp(item.tp || item.price_tp ? String(item.tp || item.price_tp) : '');
        setModPrice(item.price_order ? String(item.price_order) : '');
    };

    // Submit Modification
    const submitModify = async () => {
        if (!modifyingItem) return;
        const { kind, item } = modifyingItem;
        const ticket = item.position_id || item.ticket;

        try {
            let res;
            if (kind === 'position') {
                res = await API.modifyPosition(ticket, modSl ? parseFloat(modSl) : undefined, modTp ? parseFloat(modTp) : undefined);
            } else {
                res = await API.modifyOrder(
                    ticket,
                    modPrice ? parseFloat(modPrice) : undefined,
                    modSl ? parseFloat(modSl) : undefined,
                    modTp ? parseFloat(modTp) : undefined
                );
            }
            const success = res.retcode === 0 || !res.retcode;
            addLog(`Modify #${ticket}`, success, res.message || 'Modified successfully', res);
            setModifyingItem(null);
            await refreshData();
        } catch (err: any) {
            addLog(`Modify #${ticket} FAILED`, false, err.message || 'Modify failed', err);
        }
    };

    // Open another independent trade panel instance
    const handleSpawnNewPanel = () => {
        window.dispatchEvent(new CustomEvent('mt5-admin:open-node', {
            detail: {
                id: 'trade-panel',
                label: `Trade Terminal #${Math.floor(Math.random() * 100) + 2}`,
            }
        }));
    };

    return (
        <div className="tp-container">
            {/* Top Toolbar */}
            <div className="tp-header">
                <div className="tp-header-left">
                    <span className="tp-badge">
                        <i className="codicon codicon-pulse" /> DEBUG TRADING TERMINAL
                    </span>
                    <span className="tp-instance-id">{panelId}</span>
                </div>

                <div className="tp-header-actions">
                    <button className="tp-btn secondary" onClick={handleSpawnNewPanel} title="Open another independent Trade Panel instance">
                        <i className="codicon codicon-split-horizontal" /> + New Trade Panel
                    </button>
                    <button className="tp-btn secondary" onClick={() => refreshData()} title="Refresh live data">
                        <i className="codicon codicon-refresh" /> Refresh
                    </button>
                    <label className="tp-checkbox-label">
                        <input type="checkbox" checked={autoRefresh} onChange={e => setAutoRefresh(e.target.checked)} />
                        Auto-Refresh
                    </label>
                </div>
            </div>

            {/* Account & Symbol Quick Select Bar */}
            <div className="tp-subbar">
                {/* Account Selection */}
                <div className="tp-field-group">
                    <label>Account (Login):</label>
                    <select
                        className="tp-select"
                        value={selectedLogin}
                        onChange={e => {
                            const val = Number(e.target.value);
                            setSelectedLogin(val);
                            setCustomLogin(String(val));
                        }}
                    >
                        {accounts.map(a => (
                            <option key={a.login} value={a.login}>
                                #{a.login} — {a.name || 'Trader'} ({a.group || 'standard'})
                            </option>
                        ))}
                    </select>
                    <input
                        className="tp-input tp-short-input"
                        type="text"
                        placeholder="Custom Login"
                        value={customLogin}
                        onChange={e => setCustomLogin(e.target.value)}
                        onBlur={() => {
                            const num = parseInt(customLogin);
                            if (!isNaN(num) && num > 0) setSelectedLogin(num);
                        }}
                    />
                </div>

                {/* Account Metrics Badge */}
                <div className="tp-account-chips">
                    <span className="tp-chip">
                        Bal: <strong>${activeAccount.balance?.toLocaleString(undefined, { minimumFractionDigits: 2 })}</strong>
                    </span>
                    <span className="tp-chip">
                        Eq: <strong>${activeAccount.equity?.toLocaleString(undefined, { minimumFractionDigits: 2 })}</strong>
                    </span>
                    <span className="tp-chip">
                        Free: <strong>${activeAccount.margin_free?.toLocaleString(undefined, { minimumFractionDigits: 2 })}</strong>
                    </span>
                    <span className="tp-chip group">
                        Group: <strong>{activeAccount.group}</strong>
                    </span>
                </div>

                <div style={{ flex: 1 }} />

                {/* Symbol Selection */}
                <div className="tp-field-group">
                    <label>Symbol:</label>
                    <select
                        className="tp-select"
                        value={selectedSymbol}
                        onChange={e => setSelectedSymbol(e.target.value)}
                    >
                        {symbols.map(s => (
                            <option key={s} value={s}>{s}</option>
                        ))}
                    </select>
                </div>

                {/* Quick Symbol Pills */}
                <div className="tp-symbol-pills">
                    {COMMON_SYMBOLS.map(s => (
                        <button
                            key={s}
                            className={`tp-pill ${selectedSymbol === s ? 'active' : ''}`}
                            onClick={() => setSelectedSymbol(s)}
                        >
                            {s}
                        </button>
                    ))}
                </div>
            </div>

            {/* Main Interactive Grid */}
            <div className="tp-main-grid">
                
                {/* Left Column: Execution Console */}
                <div className="tp-order-card">
                    {/* Live Ticker display */}
                    <div className="tp-ticker-header">
                        <div className="tp-ticker-title">
                            <h3>{selectedSymbol}</h3>
                            <span className="tp-spread-badge">Spread: {activeQuote.spread || (activeQuote.ask && activeQuote.bid ? (activeQuote.ask - activeQuote.bid).toFixed(2) : '0.0')} pts</span>
                        </div>
                        <div className="tp-live-quotes">
                            <div className={`tp-quote-box bid ${flashBid || ''}`}>
                                <span className="label">BID</span>
                                <span className="val">{activeQuote.bid > 0 ? activeQuote.bid.toFixed(2) : '—'}</span>
                            </div>
                            <div className={`tp-quote-box ask ${flashAsk || ''}`}>
                                <span className="label">ASK</span>
                                <span className="val">{activeQuote.ask > 0 ? activeQuote.ask.toFixed(2) : '—'}</span>
                            </div>
                        </div>
                    </div>

                    {/* Quick One-Click Trading Controls */}
                    <div className="tp-one-click-box">
                        <button
                            className="tp-btn-trade sell"
                            disabled={isSubmitting}
                            onClick={() => handlePlaceTrade('sell')}
                        >
                            <span className="action">SELL</span>
                            <span className="price">{activeQuote.bid > 0 ? activeQuote.bid.toFixed(2) : 'Market'}</span>
                        </button>

                        <div className="tp-volume-box">
                            <label>Lots:</label>
                            <input
                                className="tp-input volume-input"
                                type="number"
                                step="0.01"
                                min="0.01"
                                value={volume}
                                onChange={e => setVolume(parseFloat(e.target.value) || 0.01)}
                            />
                            <div className="tp-volume-presets">
                                {VOLUME_PRESETS.map(v => (
                                    <button
                                        key={v}
                                        className={`preset ${volume === v ? 'active' : ''}`}
                                        onClick={() => setVolume(v)}
                                    >
                                        {v}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <button
                            className="tp-btn-trade buy"
                            disabled={isSubmitting}
                            onClick={() => handlePlaceTrade('buy')}
                        >
                            <span className="action">BUY</span>
                            <span className="price">{activeQuote.ask > 0 ? activeQuote.ask.toFixed(2) : 'Market'}</span>
                        </button>
                    </div>

                    {/* Advanced Parameters Toggle */}
                    <div className="tp-advanced-toggle" onClick={() => setAdvancedOpen(!advancedOpen)}>
                        <span>
                            <i className={`codicon ${advancedOpen ? 'codicon-chevron-down' : 'codicon-chevron-right'}`} />
                            Advanced Parameters (SL, TP, Limits, Routing, Fill Type)
                        </span>
                    </div>

                    {advancedOpen && (
                        <div className="tp-advanced-form">
                            <div className="tp-form-row">
                                <div className="tp-form-col">
                                    <label>Order Type:</label>
                                    <select className="tp-select" value={orderType} onChange={e => setOrderType(e.target.value)}>
                                        <option value="buy">Market Buy</option>
                                        <option value="sell">Market Sell</option>
                                        <option value="buy_limit">Buy Limit</option>
                                        <option value="sell_limit">Sell Limit</option>
                                        <option value="buy_stop">Buy Stop</option>
                                        <option value="sell_stop">Sell Stop</option>
                                    </select>
                                </div>
                                <div className="tp-form-col">
                                    <label>Order Price (Pending):</label>
                                    <input
                                        className="tp-input"
                                        type="number"
                                        placeholder={orderType.startsWith('buy') ? String(activeQuote.ask) : String(activeQuote.bid)}
                                        value={orderPrice}
                                        onChange={e => setOrderPrice(e.target.value)}
                                        disabled={orderType === 'buy' || orderType === 'sell'}
                                    />
                                </div>
                            </div>

                            <div className="tp-form-row">
                                <div className="tp-form-col">
                                    <label>Stop Loss (SL):</label>
                                    <input className="tp-input" type="number" placeholder="Optional" value={sl} onChange={e => setSl(e.target.value)} />
                                </div>
                                <div className="tp-form-col">
                                    <label>Take Profit (TP):</label>
                                    <input className="tp-input" type="number" placeholder="Optional" value={tp} onChange={e => setTp(e.target.value)} />
                                </div>
                            </div>

                            <div className="tp-form-row">
                                <div className="tp-form-col">
                                    <label>Routing:</label>
                                    <select className="tp-select" value={routing} onChange={e => setRouting(e.target.value)}>
                                        <option value="Auto">Auto (Routing Table)</option>
                                        <option value="B-Book">B-Book (Internal Warehouse)</option>
                                        <option value="A-Book">A-Book (LP Bridge Direct)</option>
                                    </select>
                                </div>
                                <div className="tp-form-col">
                                    <label>Fill Policy:</label>
                                    <select className="tp-select" value={fillType} onChange={e => setFillType(e.target.value)}>
                                        <option value="FOK">FOK (Fill Or Kill)</option>
                                        <option value="IOC">IOC (Immediate Or Cancel)</option>
                                        <option value="RETURN">RETURN (Partial Fill)</option>
                                    </select>
                                </div>
                            </div>

                            <div className="tp-form-row">
                                <div className="tp-form-col">
                                    <label>Slippage / Deviation:</label>
                                    <input className="tp-input" type="number" value={deviation} onChange={e => setDeviation(parseInt(e.target.value) || 0)} />
                                </div>
                                <div className="tp-form-col">
                                    <label>Comment:</label>
                                    <input className="tp-input" type="text" value={comment} onChange={e => setComment(e.target.value)} />
                                </div>
                            </div>

                            <button className="tp-btn primary full" disabled={isSubmitting} onClick={() => handlePlaceTrade()}>
                                <i className="codicon codicon-send" /> Place {orderType.toUpperCase()} Order
                            </button>
                        </div>
                    )}
                </div>

                {/* Right Column: Positions, Pending Orders & Debug Logs */}
                <div className="tp-tables-container">
                    
                    {/* Positions Card */}
                    <div className="tp-card">
                        <div className="tp-card-header">
                            <div className="tp-card-title">
                                <i className="codicon codicon-graph-scatter" />
                                <span>Open Positions ({displayedPositions.length})</span>
                            </div>
                            <div className="tp-card-actions">
                                <label className="tp-checkbox-label">
                                    <input
                                        type="checkbox"
                                        checked={filterAccountOnly}
                                        onChange={e => setFilterAccountOnly(e.target.checked)}
                                    />
                                    Login #{selectedLogin} only
                                </label>
                                {displayedPositions.length > 0 && (
                                    <button className="tp-btn danger small" onClick={handleCloseAll}>
                                        Close All
                                    </button>
                                )}
                            </div>
                        </div>

                        <div className="tp-table-wrap">
                            <table className="tp-table">
                                <thead>
                                    <tr>
                                        <th>Ticket</th>
                                        <th>Login</th>
                                        <th>Symbol</th>
                                        <th>Type</th>
                                        <th>Lots</th>
                                        <th>Open Price</th>
                                        <th>Current</th>
                                        <th>S/L</th>
                                        <th>T/P</th>
                                        <th>Profit ($)</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {displayedPositions.length === 0 ? (
                                        <tr>
                                            <td colSpan={11} className="tp-empty">
                                                No open positions found {filterAccountOnly ? `for account ${selectedLogin}` : ''}.
                                            </td>
                                        </tr>
                                    ) : (
                                        displayedPositions.map(p => {
                                            const isBuy = String(p.type).toLowerCase() === '0' || String(p.type).toLowerCase() === 'buy';
                                            const profitVal = Number(p.profit || 0);
                                            const ticket = p.position_id ?? p.ticket ?? 0;
                                            return (
                                                <tr key={ticket}>
                                                    <td className="mono bold">#{ticket}</td>
                                                    <td>{p.login}</td>
                                                    <td className="bold">{p.symbol}</td>
                                                    <td>
                                                        <span className={`tp-type-badge ${isBuy ? 'buy' : 'sell'}`}>
                                                            {isBuy ? 'BUY' : 'SELL'}
                                                        </span>
                                                    </td>
                                                    <td>{p.volume}</td>
                                                    <td>{p.price_open?.toFixed ? p.price_open.toFixed(2) : p.price_open}</td>
                                                    <td>{p.price_current?.toFixed ? p.price_current.toFixed(2) : (p.price_current || '—')}</td>
                                                    <td>{p.sl || '—'}</td>
                                                    <td>{p.tp || '—'}</td>
                                                    <td className={`bold ${profitVal >= 0 ? 'text-green' : 'text-red'}`}>
                                                        {profitVal >= 0 ? `+$${profitVal.toFixed(2)}` : `-$${Math.abs(profitVal).toFixed(2)}`}
                                                    </td>
                                                    <td className="tp-actions-cell">
                                                        <button
                                                            className="tp-action-btn close"
                                                            title="Close at market price"
                                                            onClick={() => handleClosePosition(ticket)}
                                                        >
                                                            ⚡ Close
                                                        </button>
                                                        <button
                                                            className="tp-action-btn partial"
                                                            title="Partial volume close"
                                                            onClick={() => {
                                                                setPartialItem(p);
                                                                setPartialLots(Math.round((p.volume / 2) * 100) / 100 || 0.01);
                                                            }}
                                                        >
                                                            ✂️ Partial
                                                        </button>
                                                        <button
                                                            className="tp-action-btn modify"
                                                            title="Modify SL & TP"
                                                            onClick={() => startModify(p, 'position')}
                                                        >
                                                            ✏️ Mod
                                                        </button>
                                                    </td>
                                                </tr>
                                            );
                                        })
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* Pending Orders Card */}
                    <div className="tp-card">
                        <div className="tp-card-header">
                            <div className="tp-card-title">
                                <i className="codicon codicon-list-ordered" />
                                <span>Pending Orders ({displayedOrders.length})</span>
                            </div>
                        </div>

                        <div className="tp-table-wrap">
                            <table className="tp-table">
                                <thead>
                                    <tr>
                                        <th>Ticket</th>
                                        <th>Login</th>
                                        <th>Symbol</th>
                                        <th>Type</th>
                                        <th>Lots</th>
                                        <th>Target Price</th>
                                        <th>S/L</th>
                                        <th>T/P</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {displayedOrders.length === 0 ? (
                                        <tr>
                                            <td colSpan={9} className="tp-empty">
                                                No pending orders.
                                            </td>
                                        </tr>
                                    ) : (
                                        displayedOrders.map(o => (
                                            <tr key={o.ticket}>
                                                <td className="mono bold">#{o.ticket}</td>
                                                <td>{o.login}</td>
                                                <td className="bold">{o.symbol}</td>
                                                <td><span className="tp-type-badge pending">{String(o.type)}</span></td>
                                                <td>{o.volume}</td>
                                                <td>{o.price_order}</td>
                                                <td>{o.price_sl || '—'}</td>
                                                <td>{o.price_tp || '—'}</td>
                                                <td className="tp-actions-cell">
                                                    <button
                                                        className="tp-action-btn close"
                                                        title="Cancel Order"
                                                        onClick={() => handleCancelOrder(o.ticket)}
                                                    >
                                                        ❌ Cancel
                                                    </button>
                                                    <button
                                                        className="tp-action-btn modify"
                                                        title="Modify Price/SL/TP"
                                                        onClick={() => startModify(o, 'order')}
                                                    >
                                                        ✏️ Mod
                                                    </button>
                                                </td>
                                            </tr>
                                        ))
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* Real-time Debug Log / Output Viewer */}
                    <div className="tp-card tp-log-card">
                        <div className="tp-card-header">
                            <div className="tp-card-title">
                                <i className="codicon codicon-terminal" />
                                <span>Execution Log & JSON Responses ({logs.length})</span>
                            </div>
                            {logs.length > 0 && (
                                <button className="tp-btn small secondary" onClick={() => setLogs([])}>
                                    Clear
                                </button>
                            )}
                        </div>
                        <div className="tp-log-wrap">
                            {logs.length === 0 ? (
                                <div className="tp-empty">No trade requests executed yet in this session.</div>
                            ) : (
                                logs.map(l => (
                                    <div key={l.id} className={`tp-log-entry ${l.success ? 'success' : 'error'}`}>
                                        <span className="time">[{l.time}]</span>
                                        <span className="action">{l.action}</span>
                                        <span className="msg">{l.message}</span>
                                        {l.data && (
                                            <span className="data">
                                                {JSON.stringify(l.data)}
                                            </span>
                                        )}
                                    </div>
                                ))
                            )}
                        </div>
                    </div>

                </div>
            </div>

            {/* Modify Modal */}
            {modifyingItem && (
                <div className="tp-modal-overlay">
                    <div className="tp-modal-box">
                        <div className="tp-modal-header">
                            <h4>Modify {modifyingItem.kind === 'position' ? 'Position' : 'Order'} #{modifyingItem.item.position_id || modifyingItem.item.ticket}</h4>
                            <button className="tp-close-btn" onClick={() => setModifyingItem(null)}>✕</button>
                        </div>
                        <div className="tp-modal-body">
                            {modifyingItem.kind === 'order' && (
                                <div className="tp-field-row">
                                    <label>New Price:</label>
                                    <input className="tp-input" type="number" value={modPrice} onChange={e => setModPrice(e.target.value)} />
                                </div>
                            )}
                            <div className="tp-field-row">
                                <label>Stop Loss (SL):</label>
                                <input className="tp-input" type="number" value={modSl} onChange={e => setModSl(e.target.value)} placeholder="0.00" />
                            </div>
                            <div className="tp-field-row">
                                <label>Take Profit (TP):</label>
                                <input className="tp-input" type="number" value={modTp} onChange={e => setModTp(e.target.value)} placeholder="0.00" />
                            </div>
                        </div>
                        <div className="tp-modal-footer">
                            <button className="tp-btn secondary" onClick={() => setModifyingItem(null)}>Cancel</button>
                            <button className="tp-btn primary" onClick={submitModify}>Save Changes</button>
                        </div>
                    </div>
                </div>
            )}

            {/* Partial Close Modal */}
            {partialItem && (
                <div className="tp-modal-overlay">
                    <div className="tp-modal-box">
                        <div className="tp-modal-header">
                            <h4>Partial Close Position #{partialItem.position_id || partialItem.ticket}</h4>
                            <button className="tp-close-btn" onClick={() => setPartialItem(null)}>✕</button>
                        </div>
                        <div className="tp-modal-body">
                            <p style={{ margin: '0 0 10px 0', opacity: 0.8 }}>
                                Total Volume: <strong>{partialItem.volume} lots</strong> ({partialItem.symbol})
                            </p>
                            <div className="tp-field-row">
                                <label>Volume to Close:</label>
                                <input
                                    className="tp-input"
                                    type="number"
                                    step="0.01"
                                    min="0.01"
                                    max={partialItem.volume}
                                    value={partialLots}
                                    onChange={e => setPartialLots(parseFloat(e.target.value) || 0.01)}
                                />
                            </div>
                        </div>
                        <div className="tp-modal-footer">
                            <button className="tp-btn secondary" onClick={() => setPartialItem(null)}>Cancel</button>
                            <button
                                className="tp-btn danger"
                                onClick={() => {
                                    const t = partialItem.position_id ?? partialItem.ticket ?? 0;
                                    handleClosePosition(t, partialLots);
                                    setPartialItem(null);
                                }}
                            >
                                Close {partialLots} Lots
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
