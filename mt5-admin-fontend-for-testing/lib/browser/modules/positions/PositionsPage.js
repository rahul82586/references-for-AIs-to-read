"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.PositionsPage = void 0;
// @ts-nocheck
const React = require("react");
const api_1 = require("../api");
function PositionsPage({ view }) {
    const [positions, setPositions] = React.useState([]);
    const [sel, setSel] = React.useState(null);
    const [filter, setFilter] = React.useState('');
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState(null);
    const loadData = async () => {
        setLoading(true);
        setError(null);
        try {
            if (view === 'open') {
                const data = await api_1.API.getPositions();
                setPositions(data);
            }
            else {
                // For history, list deals
                const data = await api_1.API.getDeals();
                setPositions(data);
            }
        }
        catch (err) {
            setError(err.message || 'Failed to fetch positions/deals.');
        }
        finally {
            setLoading(false);
        }
    };
    React.useEffect(() => {
        loadData();
    }, [view]);
    const filtered = positions.filter(p => String(p.login).includes(filter) ||
        p.symbol.toLowerCase().includes(filter.toLowerCase()) ||
        String(p.ticket).includes(filter));
    const totalProfit = filtered.reduce((s, p) => s + (p.profit || 0), 0);
    return (React.createElement("div", { className: "adm-page" },
        React.createElement("div", { className: "adm-toolbar" },
            React.createElement("button", { className: "adm-btn", onClick: loadData, title: "Reload data" },
                React.createElement("i", { className: "codicon codicon-refresh" }),
                " Refresh"),
            React.createElement("div", { className: "adm-toolbar-sep" }),
            React.createElement("div", { className: "adm-search-wrap" },
                React.createElement("i", { className: "codicon codicon-search" }),
                React.createElement("input", { className: "adm-search", placeholder: "Filter by login, symbol, ticket...", value: filter, onChange: e => setFilter(e.target.value) }))),
        error && (React.createElement("div", { className: "adm-hint", style: { background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)' } },
            React.createElement("i", { className: "codicon codicon-error" }),
            " ",
            error)),
        React.createElement("div", { className: "adm-table-wrap" }, loading ? (React.createElement("div", { style: { padding: 20, textAlign: 'center', opacity: 0.7 } }, "Loading data...")) : filtered.length === 0 ? (React.createElement("div", { style: { padding: 20, textAlign: 'center', opacity: 0.7 } }, "No records found.")) : (React.createElement("table", { className: "adm-table" },
            React.createElement("thead", null, view === 'open' ? (React.createElement("tr", null,
                React.createElement("th", null, "Ticket"),
                React.createElement("th", null, "Login"),
                React.createElement("th", null, "Symbol"),
                React.createElement("th", null, "Type"),
                React.createElement("th", null, "Volume"),
                React.createElement("th", null, "Open Price"),
                React.createElement("th", null, "Current Price"),
                React.createElement("th", null, "S/L"),
                React.createElement("th", null, "T/P"),
                React.createElement("th", null, "Float Profit"),
                React.createElement("th", null, "Swap"),
                React.createElement("th", null, "Open Time"))) : (React.createElement("tr", null,
                React.createElement("th", null, "Ticket"),
                React.createElement("th", null, "Order Ticket"),
                React.createElement("th", null, "Login"),
                React.createElement("th", null, "Symbol"),
                React.createElement("th", null, "Action"),
                React.createElement("th", null, "Entry"),
                React.createElement("th", null, "Volume"),
                React.createElement("th", null, "Execution Price"),
                React.createElement("th", null, "Realized Profit"),
                React.createElement("th", null, "Swap"),
                React.createElement("th", null, "Commission"),
                React.createElement("th", null, "Timestamp")))),
            React.createElement("tbody", null, filtered.map(p => {
                const isBuy = p.action === 0;
                const typeStr = isBuy ? 'BUY' : 'SELL';
                const ticketId = p.ticket;
                if (view === 'open') {
                    return (React.createElement("tr", { key: ticketId, className: sel === ticketId ? 'selected' : '', onClick: () => setSel(ticketId) },
                        React.createElement("td", null,
                            React.createElement("strong", null, p.ticket)),
                        React.createElement("td", null, p.login),
                        React.createElement("td", null,
                            React.createElement("strong", null, p.symbol)),
                        React.createElement("td", null,
                            React.createElement("span", { className: `adm-side-badge ${typeStr.toLowerCase()}` }, typeStr)),
                        React.createElement("td", null, (p.volume || 0).toFixed(2)),
                        React.createElement("td", { className: "adm-num" }, (p.price_open || 0).toFixed(5)),
                        React.createElement("td", { className: "adm-num" }, (p.price_current || 0).toFixed(5)),
                        React.createElement("td", { className: "adm-num" }, p.price_sl || '—'),
                        React.createElement("td", { className: "adm-num" }, p.price_tp || '—'),
                        React.createElement("td", { className: `adm-num ${(p.profit || 0) >= 0 ? 'adm-pos' : 'adm-neg'}` },
                            (p.profit || 0) >= 0 ? '+' : '',
                            (p.profit || 0).toFixed(2)),
                        React.createElement("td", { className: "adm-num" }, (p.storage || 0).toFixed(2)),
                        React.createElement("td", null, p.time_create || '—')));
                }
                else {
                    // Deal history format
                    const entryStr = p.entry === 0 ? 'IN' : p.entry === 1 ? 'OUT' : 'IN/OUT';
                    return (React.createElement("tr", { key: ticketId, className: sel === ticketId ? 'selected' : '', onClick: () => setSel(ticketId) },
                        React.createElement("td", null,
                            React.createElement("strong", null, p.ticket)),
                        React.createElement("td", null, p.order_ticket || '—'),
                        React.createElement("td", null, p.login),
                        React.createElement("td", null,
                            React.createElement("strong", null, p.symbol)),
                        React.createElement("td", null,
                            React.createElement("span", { className: `adm-side-badge ${typeStr.toLowerCase()}` }, typeStr)),
                        React.createElement("td", null,
                            React.createElement("span", { className: "adm-tag" }, entryStr)),
                        React.createElement("td", null, (p.volume || 0).toFixed(2)),
                        React.createElement("td", { className: "adm-num" }, (p.price || 0).toFixed(5)),
                        React.createElement("td", { className: `adm-num ${(p.profit || 0) >= 0 ? 'adm-pos' : 'adm-neg'}` },
                            (p.profit || 0) >= 0 ? '+' : '',
                            (p.profit || 0).toFixed(2)),
                        React.createElement("td", { className: "adm-num" }, (p.storage || 0).toFixed(2)),
                        React.createElement("td", { className: "adm-num adm-neg" }, (p.commission || 0).toFixed(2)),
                        React.createElement("td", null, p.timestamp || '—')));
                }
            }))))),
        React.createElement("div", { className: "adm-statusbar" },
            React.createElement("span", null,
                view === 'open' ? 'Open Positions' : 'Closed Deals',
                ": ",
                filtered.length),
            React.createElement("span", { className: "adm-sep" }, "|"),
            React.createElement("span", { className: totalProfit >= 0 ? 'adm-pos' : 'adm-neg' },
                "Total ",
                view === 'open' ? 'Float P&L' : 'Realized P&L',
                ": ",
                totalProfit >= 0 ? '+' : '',
                totalProfit.toFixed(2),
                " USD"))));
}
exports.PositionsPage = PositionsPage;
//# sourceMappingURL=PositionsPage.js.map