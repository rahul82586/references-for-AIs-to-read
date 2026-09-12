"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.BulkEditBanner = void 0;
const React = require("react");
function BulkEditBanner({ count }) {
    return (React.createElement("div", { className: "adm-hint", style: { background: 'var(--theia-sideBarSectionHeader-background)', color: 'var(--theia-foreground)', margin: '0 0 16px 0', borderLeft: '3px solid #3498db', padding: '8px 12px' } },
        React.createElement("div", { style: { fontWeight: '600', marginBottom: 4, display: 'flex', alignItems: 'center', gap: 6 } },
            React.createElement("i", { className: "codicon codicon-info", style: { color: '#3498db' } }),
            React.createElement("span", null,
                "Bulk Editing ",
                count,
                " Symbols")),
        React.createElement("div", { style: { fontSize: 11, lineHeight: '1.4', opacity: 0.9 } },
            "Only the fields you modify will be saved and applied as a batch update.",
            React.createElement("br", null),
            React.createElement("strong", { style: { color: '#e67e22' } }, "Pro-Tip:"),
            " Entering a suffix starting with a period (e.g. ",
            React.createElement("code", null, ".x"),
            ") in the Symbol name input will create duplicated copies of all selected symbols with that suffix appended, rather than renaming them!")));
}
exports.BulkEditBanner = BulkEditBanner;
//# sourceMappingURL=BulkEditBanner.js.map