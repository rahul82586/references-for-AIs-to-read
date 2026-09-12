"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.MarketWatchPage = void 0;
const React = require("react");
const api_1 = require("../api");
function formatPrice(v) {
    if (v >= 10000)
        return v.toFixed(2);
    if (v >= 100)
        return v.toFixed(3);
    return v.toFixed(5);
}
function formatAge(s) {
    if (s < 1)
        return '<1s';
    if (s < 60)
        return `${Math.round(s)}s`;
    if (s < 3600)
        return `${Math.floor(s / 60)}m ${Math.round(s % 60)}s`;
    return `${Math.floor(s / 3600)}h`;
}
function ageColor(age) {
    if (age < 5)
        return 'var(--theia-successForeground, #2ecc71)';
    if (age < 30)
        return 'var(--theia-warningForeground, #f1c40f)';
    return 'var(--theia-errorForeground, #e74c3c)';
}
function MarketWatchPage() {
    const [quotes, setQuotes] = React.useState([]);
    const [error, setError] = React.useState(null);
    const [lastUpdate, setLastUpdate] = React.useState(null);
    const [filter, setFilter] = React.useState('');
    const prevRef = React.useRef({});
    const flashTimers = React.useRef({});
    const fetchQuotes = React.useCallback(async () => {
        try {
            const data = await api_1.API.getTicks();
            setError(null);
            setLastUpdate(new Date());
            setQuotes(prev => {
                const prevMap = {};
                prev.forEach(r => { prevMap[r.symbol] = r; });
                const rows = Object.entries(data)
                    .filter(([_, q]) => q.age <= 60)
                    .map(([symbol, q]) => {
                    const old = prevRef.current[symbol];
                    let flashBid;
                    let flashAsk;
                    if (old) {
                        if (q.bid > old.bid)
                            flashBid = 'up';
                        else if (q.bid < old.bid)
                            flashBid = 'down';
                        if (q.ask > old.ask)
                            flashAsk = 'up';
                        else if (q.ask < old.ask)
                            flashAsk = 'down';
                    }
                    prevRef.current[symbol] = { bid: q.bid, ask: q.ask };
                    return {
                        symbol,
                        bid: q.bid,
                        ask: q.ask,
                        age: q.age,
                        spread: Math.round((q.ask - q.bid) * 100000) / 10,
                        prevBid: old?.bid,
                        prevAsk: old?.ask,
                        flashBid,
                        flashAsk,
                    };
                })
                    .sort((a, b) => a.symbol.localeCompare(b.symbol));
                return rows;
            });
        }
        catch (e) {
            setError(e?.message || 'Failed to fetch quotes');
        }
    }, []);
    React.useEffect(() => {
        fetchQuotes();
        const iv = setInterval(fetchQuotes, 1000);
        return () => clearInterval(iv);
    }, [fetchQuotes]);
    // Clear flash state after 400ms
    React.useEffect(() => {
        quotes.forEach(row => {
            if (row.flashBid || row.flashAsk) {
                if (flashTimers.current[row.symbol])
                    clearTimeout(flashTimers.current[row.symbol]);
                flashTimers.current[row.symbol] = setTimeout(() => {
                    setQuotes(prev => prev.map(r => r.symbol === row.symbol ? { ...r, flashBid: undefined, flashAsk: undefined } : r));
                }, 400);
            }
        });
    }, [quotes]);
    const filtered = filter.trim()
        ? quotes.filter(r => r.symbol.toLowerCase().includes(filter.toLowerCase()))
        : quotes;
    const connected = quotes.length > 0 && quotes.some(r => r.age < 30);
    return (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' } },
        React.createElement("div", { style: {
                display: 'flex', alignItems: 'center', gap: 12, padding: '8px 12px',
                borderBottom: '1px solid var(--theia-panel-border)',
                background: 'var(--theia-editor-background)',
                flexShrink: 0
            } },
            React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 6 } },
                React.createElement("span", { style: {
                        width: 8, height: 8, borderRadius: '50%', display: 'inline-block',
                        background: connected ? '#2ecc71' : (error ? '#e74c3c' : '#95a5a6'),
                        boxShadow: connected ? '0 0 6px #2ecc7188' : 'none',
                        animation: connected ? 'pulse 2s infinite' : 'none'
                    } }),
                React.createElement("span", { style: { fontWeight: 600, fontSize: 13 } }, "Market Watch"),
                React.createElement("span", { style: {
                        fontSize: 10, padding: '1px 6px', borderRadius: 3,
                        background: 'var(--theia-badge-background)',
                        color: 'var(--theia-badge-foreground)'
                    } }, "DEBUG")),
            React.createElement("input", { type: "text", placeholder: "Filter symbols...", value: filter, onChange: e => setFilter(e.target.value), style: {
                    flex: 1, maxWidth: 200,
                    padding: '3px 8px', fontSize: 12,
                    background: 'var(--theia-input-background)',
                    color: 'var(--theia-input-foreground)',
                    border: '1px solid var(--theia-input-border)',
                    borderRadius: 4, outline: 'none'
                } }),
            React.createElement("span", { style: { fontSize: 11, color: 'var(--theia-descriptionForeground)', marginLeft: 'auto' } },
                quotes.length,
                " symbol",
                quotes.length !== 1 ? 's' : '',
                lastUpdate && ` · updated ${lastUpdate.toLocaleTimeString()}`),
            React.createElement("button", { onClick: fetchQuotes, style: {
                    padding: '3px 10px', fontSize: 11, cursor: 'pointer',
                    background: 'var(--theia-button-background)',
                    color: 'var(--theia-button-foreground)',
                    border: 'none', borderRadius: 4
                } }, "\u21BB Refresh")),
        error && (React.createElement("div", { style: {
                padding: '6px 12px', fontSize: 12,
                background: 'var(--theia-inputValidation-errorBackground, #5a1d1d)',
                color: 'var(--theia-errorForeground)',
                borderBottom: '1px solid var(--theia-inputValidation-errorBorder)',
                flexShrink: 0
            } },
            "\u26A0 ",
            error)),
        React.createElement("div", { style: { flex: 1, overflow: 'auto' } }, filtered.length === 0 ? (React.createElement("div", { style: {
                display: 'flex', flexDirection: 'column', alignItems: 'center',
                justifyContent: 'center', height: '100%', gap: 8,
                color: 'var(--theia-descriptionForeground)', fontSize: 13
            } },
            React.createElement("span", { style: { fontSize: 32 } }, "\uD83D\uDCCA"),
            React.createElement("span", null, filter ? `No symbols matching "${filter}"` : 'No live quotes yet.'),
            React.createElement("span", { style: { fontSize: 11 } }, !filter && 'Make sure the Data Feed is connected and symbols are configured.'))) : (React.createElement("table", { style: { width: '100%', borderCollapse: 'collapse', fontSize: 12 } },
            React.createElement("thead", null,
                React.createElement("tr", { style: {
                        background: 'var(--theia-sideBarSectionHeader-background)',
                        position: 'sticky', top: 0, zIndex: 1
                    } },
                    React.createElement("th", { style: thStyle }, "Symbol"),
                    React.createElement("th", { style: { ...thStyle, textAlign: 'right' } }, "Bid"),
                    React.createElement("th", { style: { ...thStyle, textAlign: 'right' } }, "Ask"),
                    React.createElement("th", { style: { ...thStyle, textAlign: 'right' } }, "Spread (pts)"),
                    React.createElement("th", { style: { ...thStyle, textAlign: 'right' } }, "Last Update"),
                    React.createElement("th", { style: { ...thStyle, textAlign: 'center' } }, "Status"))),
            React.createElement("tbody", null, filtered.map(row => (React.createElement("tr", { key: row.symbol, style: {
                    borderBottom: '1px solid var(--theia-panel-border)',
                    transition: 'background 0.2s'
                } },
                React.createElement("td", { style: { ...tdStyle, fontWeight: 600, letterSpacing: '0.5px' } }, row.symbol),
                React.createElement("td", { style: {
                        ...tdStyle, textAlign: 'right', fontFamily: 'monospace',
                        fontWeight: 600, fontSize: 13,
                        color: row.flashBid === 'up' ? '#2ecc71'
                            : row.flashBid === 'down' ? '#e74c3c'
                                : 'var(--theia-foreground)',
                        transition: 'color 0.3s'
                    } },
                    row.flashBid === 'up' ? '▲ ' : row.flashBid === 'down' ? '▼ ' : '',
                    formatPrice(row.bid)),
                React.createElement("td", { style: {
                        ...tdStyle, textAlign: 'right', fontFamily: 'monospace',
                        fontWeight: 600, fontSize: 13,
                        color: row.flashAsk === 'up' ? '#2ecc71'
                            : row.flashAsk === 'down' ? '#e74c3c'
                                : 'var(--theia-foreground)',
                        transition: 'color 0.3s'
                    } },
                    row.flashAsk === 'up' ? '▲ ' : row.flashAsk === 'down' ? '▼ ' : '',
                    formatPrice(row.ask)),
                React.createElement("td", { style: { ...tdStyle, textAlign: 'right', color: 'var(--theia-descriptionForeground)' } }, row.spread.toFixed(1)),
                React.createElement("td", { style: { ...tdStyle, textAlign: 'right', color: ageColor(row.age), fontFamily: 'monospace' } }, formatAge(row.age)),
                React.createElement("td", { style: { ...tdStyle, textAlign: 'center' } },
                    React.createElement("span", { style: {
                            display: 'inline-block', width: 7, height: 7,
                            borderRadius: '50%',
                            background: row.age < 5 ? '#2ecc71' : row.age < 30 ? '#f1c40f' : '#e74c3c',
                            boxShadow: row.age < 5 ? '0 0 5px #2ecc7188' : 'none'
                        } }))))))))),
        React.createElement("style", null, `
                @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
            `)));
}
exports.MarketWatchPage = MarketWatchPage;
const thStyle = {
    padding: '6px 10px',
    textAlign: 'left',
    fontWeight: 600,
    fontSize: 11,
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    color: 'var(--theia-descriptionForeground)',
    borderBottom: '1px solid var(--theia-panel-border)',
    whiteSpace: 'nowrap'
};
const tdStyle = {
    padding: '5px 10px',
    whiteSpace: 'nowrap'
};
//# sourceMappingURL=MarketWatchPage.js.map