"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SummaryPage = void 0;
// @ts-nocheck
const React = require("react");
const api_1 = require("../api");
function SummaryPage() {
    const [summaryData, setSummaryData] = React.useState([]);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState(null);
    const loadData = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await api_1.API.getRiskSummary();
            setSummaryData(data);
        }
        catch (err) {
            setError(err.message || 'Failed to load summary positions data.');
        }
        finally {
            setLoading(false);
        }
    };
    React.useEffect(() => {
        loadData();
    }, []);
    return (React.createElement("div", { className: "adm-page" },
        React.createElement("div", { className: "adm-toolbar" },
            React.createElement("button", { className: "adm-btn", onClick: loadData },
                React.createElement("i", { className: "codicon codicon-refresh" }),
                " Refresh")),
        error && (React.createElement("div", { className: "adm-hint", style: { background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)' } },
            React.createElement("i", { className: "codicon codicon-error" }),
            " ",
            error)),
        React.createElement("div", { className: "adm-table-wrap" }, loading ? (React.createElement("div", { style: { padding: 20, textAlign: 'center', opacity: 0.7 } }, "Loading Summary positions...")) : summaryData.length === 0 ? (React.createElement("div", { style: { padding: 20, textAlign: 'center', opacity: 0.7 } }, "No summary positions available.")) : (React.createElement("table", { className: "adm-table" },
            React.createElement("thead", null,
                React.createElement("tr", null,
                    React.createElement("th", { rowSpan: 2 }, "Symbol"),
                    React.createElement("th", { colSpan: 4, style: { textAlign: 'center', borderBottom: '1px solid var(--theia-widget-border)' } }, "Clients Summary"),
                    React.createElement("th", { colSpan: 4, style: { textAlign: 'center', borderBottom: '1px solid var(--theia-widget-border)' } }, "Coverage Summary"),
                    React.createElement("th", { rowSpan: 2, className: "adm-num" }, "Net Vol (Lots)"),
                    React.createElement("th", { rowSpan: 2, className: "adm-num" }, "Uncovered Profit")),
                React.createElement("tr", null,
                    React.createElement("th", { className: "adm-num" }, "Buy Vol"),
                    React.createElement("th", { className: "adm-num" }, "Buy Price"),
                    React.createElement("th", { className: "adm-num" }, "Sell Vol"),
                    React.createElement("th", { className: "adm-num" }, "Sell Price"),
                    React.createElement("th", { className: "adm-num" }, "Buy Vol"),
                    React.createElement("th", { className: "adm-num" }, "Buy Price"),
                    React.createElement("th", { className: "adm-num" }, "Sell Vol"),
                    React.createElement("th", { className: "adm-num" }, "Sell Price"))),
            React.createElement("tbody", null, summaryData.map(d => (React.createElement("tr", { key: d.symbol },
                React.createElement("td", null,
                    React.createElement("strong", null, d.symbol)),
                React.createElement("td", { className: "adm-num" }, (d.clientBuyVol || 0).toFixed(2)),
                React.createElement("td", { className: "adm-num" }, d.clientBuyAvg > 0 ? d.clientBuyAvg.toFixed(5) : '—'),
                React.createElement("td", { className: "adm-num" }, (d.clientSellVol || 0).toFixed(2)),
                React.createElement("td", { className: "adm-num" }, d.clientSellAvg > 0 ? d.clientSellAvg.toFixed(5) : '—'),
                React.createElement("td", { className: "adm-num" }, (d.covBuyVol || 0).toFixed(2)),
                React.createElement("td", { className: "adm-num" }, d.covBuyAvg > 0 ? d.covBuyAvg.toFixed(5) : '—'),
                React.createElement("td", { className: "adm-num" }, (d.covSellVol || 0).toFixed(2)),
                React.createElement("td", { className: "adm-num" }, d.covSellAvg > 0 ? d.covSellAvg.toFixed(5) : '—'),
                React.createElement("td", { className: `adm-num ${d.netVol === 0 ? '' : d.netVol > 0 ? 'adm-pos' : 'adm-neg'}` },
                    d.netVol > 0 ? '+' : '',
                    (d.netVol || 0).toFixed(2)),
                React.createElement("td", { className: `adm-num ${d.uncoveredProfit >= 0 ? 'adm-pos' : 'adm-neg'}` },
                    d.uncoveredProfit >= 0 ? '+' : '',
                    (d.uncoveredProfit || 0).toFixed(2),
                    " USD"))))))))));
}
exports.SummaryPage = SummaryPage;
//# sourceMappingURL=SummaryPage.js.map