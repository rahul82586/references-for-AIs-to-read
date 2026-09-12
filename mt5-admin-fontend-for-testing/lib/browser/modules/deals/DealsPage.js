"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DealsPage = void 0;
// @ts-nocheck
const React = require("react");
const MOCK_DEALS = [
    { id: '1', deal: 30001, order: 10001, login: 50080, symbol: 'EURUSD', action: 'BUY', entry: 'IN', volume: 0.10, price: 1.08250, profit: 0.00, swap: 0.00, commission: -0.50, time: '2026-08-19 10:22:11', comment: '', reason: 'CLIENT' },
    { id: '2', deal: 30002, order: 10002, login: 50080, symbol: 'EURUSD', action: 'SELL', entry: 'OUT', volume: 0.10, price: 1.08340, profit: 9.00, swap: -0.32, commission: -0.50, time: '2026-08-19 15:44:22', comment: '', reason: 'CLIENT' },
    { id: '3', deal: 30003, order: 20003, login: 50082, symbol: 'GBPUSD', action: 'SELL', entry: 'IN', volume: 0.50, price: 1.27100, profit: 0.00, swap: 0.00, commission: -2.50, time: '2026-08-19 14:22:10', comment: 'EA order', reason: 'EXPERT' },
];
function DealsPage() {
    const [deals] = React.useState(MOCK_DEALS);
    const [selected, setSelected] = React.useState(null);
    const [filter, setFilter] = React.useState('');
    const [dateFrom, setDateFrom] = React.useState('');
    const [dateTo, setDateTo] = React.useState('');
    const filtered = deals.filter(d => String(d.login).includes(filter) ||
        d.symbol.toLowerCase().includes(filter.toLowerCase()) ||
        String(d.deal).includes(filter));
    const totalProfit = filtered.reduce((s, d) => s + d.profit, 0);
    const totalComm = filtered.reduce((s, d) => s + d.commission, 0);
    return (React.createElement("div", { className: "adm-page" },
        React.createElement("div", { className: "adm-toolbar" },
            React.createElement("div", { className: "adm-search-wrap" },
                React.createElement("i", { className: "codicon codicon-search" }),
                React.createElement("input", { className: "adm-search", placeholder: "Filter by login, symbol, deal...", value: filter, onChange: e => setFilter(e.target.value) })),
            React.createElement("div", { className: "adm-toolbar-sep" }),
            React.createElement("label", { style: { fontSize: 11, opacity: 0.7 } }, "From:"),
            React.createElement("input", { type: "date", className: "adm-input", style: { width: 130 }, value: dateFrom, onChange: e => setDateFrom(e.target.value) }),
            React.createElement("label", { style: { fontSize: 11, opacity: 0.7 } }, "To:"),
            React.createElement("input", { type: "date", className: "adm-input", style: { width: 130 }, value: dateTo, onChange: e => setDateTo(e.target.value) }),
            React.createElement("button", { className: "adm-btn adm-btn-primary" },
                React.createElement("i", { className: "codicon codicon-search" }),
                " Request"),
            React.createElement("div", { className: "adm-toolbar-sep" }),
            React.createElement("button", { className: "adm-btn" },
                React.createElement("i", { className: "codicon codicon-export" }),
                " Export")),
        React.createElement("div", { className: "adm-table-wrap" },
            React.createElement("table", { className: "adm-table" },
                React.createElement("thead", null,
                    React.createElement("tr", null,
                        React.createElement("th", null, "Deal #"),
                        React.createElement("th", null, "Order #"),
                        React.createElement("th", null, "Login"),
                        React.createElement("th", null, "Symbol"),
                        React.createElement("th", null, "Action"),
                        React.createElement("th", null, "Entry"),
                        React.createElement("th", null, "Volume"),
                        React.createElement("th", null, "Price"),
                        React.createElement("th", null, "Profit"),
                        React.createElement("th", null, "Swap"),
                        React.createElement("th", null, "Commission"),
                        React.createElement("th", null, "Reason"),
                        React.createElement("th", null, "Time"),
                        React.createElement("th", null, "Comment"))),
                React.createElement("tbody", null, filtered.map(d => (React.createElement("tr", { key: d.id, className: selected === d.id ? 'selected' : '', onClick: () => setSelected(d.id) },
                    React.createElement("td", null,
                        React.createElement("strong", null, d.deal)),
                    React.createElement("td", null, d.order),
                    React.createElement("td", null, d.login),
                    React.createElement("td", null,
                        React.createElement("strong", null, d.symbol)),
                    React.createElement("td", null,
                        React.createElement("span", { className: `adm-side-badge ${d.action.toLowerCase()}` }, d.action)),
                    React.createElement("td", null,
                        React.createElement("span", { className: "adm-tag" }, d.entry)),
                    React.createElement("td", null, d.volume.toFixed(2)),
                    React.createElement("td", { className: "adm-num" }, d.price.toFixed(5)),
                    React.createElement("td", { className: `adm-num ${d.profit >= 0 ? 'adm-pos' : 'adm-neg'}` },
                        d.profit >= 0 ? '+' : '',
                        d.profit.toFixed(2)),
                    React.createElement("td", { className: "adm-num" }, d.swap.toFixed(2)),
                    React.createElement("td", { className: "adm-num adm-neg" }, d.commission.toFixed(2)),
                    React.createElement("td", null, d.reason),
                    React.createElement("td", null, d.time),
                    React.createElement("td", null, d.comment))))))),
        React.createElement("div", { className: "adm-statusbar" },
            React.createElement("span", null,
                "Deals: ",
                filtered.length),
            React.createElement("span", { className: "adm-sep" }, "|"),
            React.createElement("span", { className: totalProfit >= 0 ? 'adm-pos' : 'adm-neg' },
                "Profit: ",
                totalProfit >= 0 ? '+' : '',
                totalProfit.toFixed(2)),
            React.createElement("span", { className: "adm-sep" }, "|"),
            React.createElement("span", { className: "adm-neg" },
                "Commission: ",
                totalComm.toFixed(2)))));
}
exports.DealsPage = DealsPage;
//# sourceMappingURL=DealsPage.js.map