"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.MarginCallPage = void 0;
// @ts-nocheck
const React = require("react");
const api_1 = require("../api");
function MarginCallPage() {
    const [processedAccounts, setProcessedAccounts] = React.useState([]);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState(null);
    const [filterRiskOnly, setFilterRiskOnly] = React.useState(true);
    const loadData = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await api_1.API.getRiskMarginCalls();
            setProcessedAccounts(data);
        }
        catch (err) {
            setError(err.message || 'Failed to load margin call accounts list.');
        }
        finally {
            setLoading(false);
        }
    };
    React.useEffect(() => {
        loadData();
    }, []);
    // Filter accounts based on checkbox selection
    const filteredAccounts = React.useMemo(() => {
        if (filterRiskOnly) {
            return processedAccounts.filter(acc => acc.status !== 'OK');
        }
        return processedAccounts;
    }, [processedAccounts, filterRiskOnly]);
    return (React.createElement("div", { className: "adm-page" },
        React.createElement("div", { className: "adm-toolbar" },
            React.createElement("button", { className: "adm-btn", onClick: loadData },
                React.createElement("i", { className: "codicon codicon-refresh" }),
                " Refresh"),
            React.createElement("div", { className: "adm-toolbar-sep" }),
            React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, fontSize: '11px', cursor: 'pointer' } },
                React.createElement("input", { type: "checkbox", checked: filterRiskOnly, onChange: e => setFilterRiskOnly(e.target.checked) }),
                React.createElement("span", null, "Show accounts under risk only (Margin Call / Stop Out)"))),
        error && (React.createElement("div", { className: "adm-hint", style: { background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)' } },
            React.createElement("i", { className: "codicon codicon-error" }),
            " ",
            error)),
        React.createElement("div", { className: "adm-table-wrap" }, loading ? (React.createElement("div", { style: { padding: 20, textAlign: 'center', opacity: 0.7 } }, "Loading margin accounts...")) : filteredAccounts.length === 0 ? (React.createElement("div", { style: { padding: 20, textAlign: 'center', opacity: 0.7 } }, filterRiskOnly ? 'No accounts are currently in Margin Call or Stop Out state.' : 'No accounts found.')) : (React.createElement("table", { className: "adm-table" },
            React.createElement("thead", null,
                React.createElement("tr", null,
                    React.createElement("th", null, "Login ID"),
                    React.createElement("th", null, "Group"),
                    React.createElement("th", { className: "adm-num" }, "Balance"),
                    React.createElement("th", { className: "adm-num" }, "Equity"),
                    React.createElement("th", { className: "adm-num" }, "Margin"),
                    React.createElement("th", { className: "adm-num" }, "Free Margin"),
                    React.createElement("th", { className: "adm-num" }, "Margin Level (%)"),
                    React.createElement("th", { className: "adm-num" }, "MC / SO Limits"),
                    React.createElement("th", { style: { textAlign: 'center' } }, "Status"))),
            React.createElement("tbody", null, filteredAccounts.map(acc => {
                const isRisk = acc.status !== 'OK';
                return (React.createElement("tr", { key: acc.login, style: {
                        background: acc.colorCode,
                        transition: 'background 0.2s'
                    } },
                    React.createElement("td", null,
                        React.createElement("strong", null, acc.login)),
                    React.createElement("td", null, acc.group_name),
                    React.createElement("td", { className: "adm-num" },
                        (acc.balance || 0).toLocaleString('en-US', { minimumFractionDigits: 2 }),
                        " ",
                        acc.currency),
                    React.createElement("td", { className: "adm-num" },
                        (acc.equity || 0).toLocaleString('en-US', { minimumFractionDigits: 2 }),
                        " ",
                        acc.currency),
                    React.createElement("td", { className: "adm-num" }, acc.margin > 0 ? `${(acc.margin || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })} ${acc.currency}` : '—'),
                    React.createElement("td", { className: "adm-num" },
                        (acc.freeMargin || 0).toLocaleString('en-US', { minimumFractionDigits: 2 }),
                        " ",
                        acc.currency),
                    React.createElement("td", { className: "adm-num" }, acc.margin > 0 ? (React.createElement("strong", { className: acc.status === 'Stop Out' ? 'adm-neg' : acc.status === 'Margin Call' ? 'adm-neg' : 'adm-pos' },
                        (acc.marginLevel || 0).toFixed(2),
                        "%")) : '—'),
                    React.createElement("td", { className: "adm-num", style: { fontSize: '10.5px', opacity: 0.8 } },
                        acc.marginCallLevel,
                        "% / ",
                        acc.stopOutLevel,
                        "%"),
                    React.createElement("td", { style: { textAlign: 'center' } }, isRisk ? (React.createElement("span", { className: `adm-tag`, style: {
                            background: acc.status === 'Stop Out' ? 'var(--theia-errorForeground)' : '#f39c12',
                            color: '#fff',
                            fontWeight: 'bold',
                            padding: '2px 8px',
                            borderRadius: '3px'
                        } }, acc.status.toUpperCase())) : (React.createElement("span", { style: { opacity: 0.6 } }, "OK")))));
            })))))));
}
exports.MarginCallPage = MarginCallPage;
//# sourceMappingURL=MarginCallPage.js.map