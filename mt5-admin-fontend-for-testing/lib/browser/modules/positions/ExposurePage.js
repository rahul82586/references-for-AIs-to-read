"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ExposurePage = void 0;
// @ts-nocheck
const React = require("react");
const api_1 = require("../api");
function ExposurePage() {
    const [exposureData, setExposureData] = React.useState([]);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState(null);
    const [displayCurrency, setDisplayCurrency] = React.useState('USD');
    const loadData = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await api_1.API.getRiskExposure();
            setExposureData(data);
        }
        catch (err) {
            setError(err.message || 'Failed to load Exposure data.');
        }
        finally {
            setLoading(false);
        }
    };
    React.useEffect(() => {
        loadData();
    }, []);
    // Calculated Exposure mapped to custom Display Currency
    const mappedExposure = React.useMemo(() => {
        // Mock conversion rates relative to display currency if needed
        const mockRates = {
            'USD': 1.0,
            'EUR': 1.09,
            'GBP': 1.27,
            'JPY': 0.0067,
            'NZD': 0.61,
            'AUD': 0.66,
            'NOK': 0.095,
            'BTC': 62000.0,
            'XAU': 2350.0,
            'XAG': 29.5
        };
        // Standardize everything to displayCurrency
        const currentDisplayRate = mockRates[displayCurrency] || 1.0;
        return exposureData.map(d => {
            const assetRate = mockRates[d.asset] || 1.0;
            // Cross-convert rate from asset to target display currency
            const rate = assetRate / currentDisplayRate;
            const netTotalConverted = d.netTotal * rate;
            const positiveConverted = netTotalConverted > 0 ? netTotalConverted : 0;
            return {
                ...d,
                rate,
                netTotalConverted,
                positiveConverted
            };
        });
    }, [exposureData, displayCurrency]);
    return (React.createElement("div", { className: "adm-page" },
        React.createElement("div", { className: "adm-toolbar" },
            React.createElement("button", { className: "adm-btn", onClick: loadData },
                React.createElement("i", { className: "codicon codicon-refresh" }),
                " Refresh"),
            React.createElement("div", { className: "adm-toolbar-sep" }),
            React.createElement("span", { style: { fontSize: '11px', opacity: 0.8 } }, "Dashboard Currency: "),
            React.createElement("select", { className: "adm-select", style: { width: 100, height: 24, padding: '2px 6px' }, value: displayCurrency, onChange: e => setDisplayCurrency(e.target.value) },
                React.createElement("option", { value: "USD" }, "USD"),
                React.createElement("option", { value: "EUR" }, "EUR"),
                React.createElement("option", { value: "GBP" }, "GBP"))),
        error && (React.createElement("div", { className: "adm-hint", style: { background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)' } },
            React.createElement("i", { className: "codicon codicon-error" }),
            " ",
            error)),
        React.createElement("div", { className: "adm-table-wrap" }, loading ? (React.createElement("div", { style: { padding: 20, textAlign: 'center', opacity: 0.7 } }, "Loading Exposure assets...")) : mappedExposure.length === 0 ? (React.createElement("div", { style: { padding: 20, textAlign: 'center', opacity: 0.7 } }, "No exposure assets found.")) : (React.createElement("table", { className: "adm-table" },
            React.createElement("thead", null,
                React.createElement("tr", null,
                    React.createElement("th", null, "Asset"),
                    React.createElement("th", { className: "adm-num" }, "Clients (Units)"),
                    React.createElement("th", { className: "adm-num" }, "Coverage (Units)"),
                    React.createElement("th", { className: "adm-num" }, "Net Total (Units)"),
                    React.createElement("th", { className: "adm-num" },
                        "Rate (",
                        displayCurrency,
                        ")"),
                    React.createElement("th", { className: "adm-num" },
                        "Net Total (",
                        displayCurrency,
                        ")"),
                    React.createElement("th", { className: "adm-num" },
                        "Positive (",
                        displayCurrency,
                        ")"))),
            React.createElement("tbody", null, mappedExposure.map(d => (React.createElement("tr", { key: d.asset },
                React.createElement("td", null,
                    React.createElement("strong", null, d.asset)),
                React.createElement("td", { className: "adm-num" }, (d.clients || 0).toLocaleString('en-US', { maximumFractionDigits: 2 })),
                React.createElement("td", { className: "adm-num" }, (d.coverage || 0).toLocaleString('en-US', { maximumFractionDigits: 2 })),
                React.createElement("td", { className: `adm-num ${d.netTotal === 0 ? '' : d.netTotal > 0 ? 'adm-pos' : 'adm-neg'}` },
                    d.netTotal > 0 ? '+' : '',
                    (d.netTotal || 0).toLocaleString('en-US', { maximumFractionDigits: 2 })),
                React.createElement("td", { className: "adm-num" }, d.rate.toLocaleString('en-US', { minimumFractionDigits: 4, maximumFractionDigits: 4 })),
                React.createElement("td", { className: `adm-num ${d.netTotalConverted >= 0 ? 'adm-pos' : 'adm-neg'}` },
                    d.netTotalConverted >= 0 ? '+' : '',
                    d.netTotalConverted.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })),
                React.createElement("td", { className: "adm-num adm-pos" }, d.positiveConverted > 0 ? d.positiveConverted.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '0.00'))))))))));
}
exports.ExposurePage = ExposurePage;
//# sourceMappingURL=ExposurePage.js.map