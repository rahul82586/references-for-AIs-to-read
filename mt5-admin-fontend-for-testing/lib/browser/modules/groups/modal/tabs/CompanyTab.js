"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CompanyTab = void 0;
const React = require("react");
const GroupDraftContext_1 = require("../GroupDraftContext");
function CompanyTab() {
    const { draft, setDraft, errors, setErrors } = (0, GroupDraftContext_1.useGroupDraft)();
    const updateField = (field, val) => {
        setDraft(prev => ({ ...prev, [field]: val }));
        // Remove error if valid
        if (field === 'company' && val) {
            setErrors(prev => {
                const next = { ...prev };
                delete next.company;
                return next;
            });
        }
    };
    return (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', height: '100%', gap: 10, fontSize: 11 } },
        React.createElement("div", { style: { display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', borderRadius: 4 } },
            React.createElement("div", { style: { width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#34495e', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' } }, "C"),
            React.createElement("div", { style: { flex: 1, opacity: 0.9, lineHeight: 1.3 } }, "Configure licensee business parameters, automated templates paths, client support portals, and website routing URLs.")),
        React.createElement("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 24px', flex: 1, marginTop: 4 } },
            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 6 } },
                React.createElement("div", { style: { fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 } }, "Licensee Credentials"),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 }, className: "required" }, "Company:"),
                    React.createElement("div", { style: { flex: 1, display: 'flex', flexDirection: 'column' } },
                        React.createElement("select", { className: `adm-select ${errors.company ? 'error' : ''}`, style: { height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.company, onChange: e => updateField('company', e.target.value) },
                            React.createElement("option", { value: "" }, "Select Company..."),
                            React.createElement("option", { value: "MetaQuotes Software Corp." }, "MetaQuotes Software Corp."),
                            React.createElement("option", { value: "Demo Brokerage Ltd." }, "Demo Broker brokerage Ltd."),
                            React.createElement("option", { value: "Global Clearing Inc." }, "Global Clearing Inc.")),
                        errors.company && React.createElement("span", { className: "adm-input-error-text", style: { fontSize: 9, color: 'var(--theia-errorForeground)' } }, errors.company))),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Website URL:"),
                    React.createElement("input", { className: "adm-input", type: "url", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, placeholder: "https://www.company.com", value: draft.company_website, onChange: e => updateField('company_website', e.target.value) })),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Corporate Email:"),
                    React.createElement("input", { className: "adm-input", type: "email", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, placeholder: "info@company.com", value: draft.company_email, onChange: e => updateField('company_email', e.target.value) })),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Templates Dir:"),
                    React.createElement("input", { className: "adm-input", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, placeholder: "e.g. standard_templates", value: draft.templates_folder, onChange: e => updateField('templates_folder', e.target.value) }))),
            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 6 } },
                React.createElement("div", { style: { fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 } }, "Client Support & Portals"),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Deposit URL:"),
                    React.createElement("input", { className: "adm-input", type: "url", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, placeholder: "https://client.company.com/deposit", value: draft.deposit_url, onChange: e => updateField('deposit_url', e.target.value) })),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Withdrawal URL:"),
                    React.createElement("input", { className: "adm-input", type: "url", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, placeholder: "https://client.company.com/withdraw", value: draft.withdrawal_url, onChange: e => updateField('withdrawal_url', e.target.value) })),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Support URL:"),
                    React.createElement("input", { className: "adm-input", type: "url", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, placeholder: "https://support.company.com", value: draft.support_site, onChange: e => updateField('support_site', e.target.value) })),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "Support Email:"),
                    React.createElement("input", { className: "adm-input", type: "email", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, placeholder: "support@company.com", value: draft.support_email, onChange: e => updateField('support_email', e.target.value) }))))));
}
exports.CompanyTab = CompanyTab;
//# sourceMappingURL=CompanyTab.js.map