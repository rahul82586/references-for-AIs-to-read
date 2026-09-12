"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ImportSummary = void 0;
const React = require("react");
function ImportSummary({ count, overwrite }) {
    return (React.createElement("div", { className: "adm-modal-body", style: { display: 'flex', flexDirection: 'column', gap: 12 } },
        React.createElement("div", { className: "adm-hint", style: { background: 'rgba(46, 204, 113, 0.1)', border: '1px solid #2ecc71', color: '#2ecc71', margin: '0 0 12px 0' } },
            React.createElement("i", { className: "codicon codicon-check" }),
            " Symbols ingestion completed successfully!"),
        React.createElement("div", { style: { fontSize: 13, lineHeight: '1.6' } },
            React.createElement("p", null, "Import summary metrics:"),
            React.createElement("ul", null,
                React.createElement("li", null,
                    "Instruments Ingested: ",
                    React.createElement("strong", null, count)),
                React.createElement("li", null,
                    "Collision Overwrite policy: ",
                    React.createElement("strong", null, overwrite ? 'Enabled (Overwritten)' : 'Disabled (Skipped)')))),
        React.createElement("div", { className: "adm-hint", style: { background: 'var(--theia-inputValidation-warningBackground)', color: 'var(--theia-warningForeground)', margin: '12px 0 0 0' } },
            React.createElement("i", { className: "codicon codicon-warning" }),
            React.createElement("strong", null, "Important:"),
            " All newly imported symbols have been set to ",
            React.createElement("strong", null, "Trading Disabled"),
            " by default to prevent client terminals from executing orders until spread rates and execution gates are configured manually.")));
}
exports.ImportSummary = ImportSummary;
//# sourceMappingURL=ImportSummary.js.map