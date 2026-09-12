"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ReportsTab = void 0;
const React = require("react");
const GroupDraftContext_1 = require("../GroupDraftContext");
const MAIL_SERVERS = ['Default', 'Local-Postfix', 'AWS-SES', 'SendGrid-SMTP'];
function ReportsTab() {
    const { draft, setDraft } = (0, GroupDraftContext_1.useGroupDraft)();
    const updateField = (field, val) => {
        setDraft(prev => ({ ...prev, [field]: val }));
    };
    const hasReports = draft.report_generation !== 'off';
    return (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', height: '100%', gap: 10, fontSize: 11 } },
        React.createElement("div", { style: { display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', borderRadius: 4 } },
            React.createElement("div", { style: { width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#1abc9c', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' } }, "R"),
            React.createElement("div", { style: { flex: 1, opacity: 0.9, lineHeight: 1.3 } }, "Configure automated daily/monthly statement generation schedules, template output files, and email SMTP servers.")),
        React.createElement("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 24px', flex: 1, marginTop: 4 } },
            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 6 } },
                React.createElement("div", { style: { fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 } }, "Statement Generation"),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 110, textAlign: 'right', opacity: 0.8 } }, "Generate Data:"),
                    React.createElement("select", { className: "adm-select", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.report_generation, onChange: e => updateField('report_generation', e.target.value) },
                        React.createElement("option", { value: "off" }, "Off (No reports)"),
                        React.createElement("option", { value: "daily" }, "End of Day (Daily)"),
                        React.createElement("option", { value: "monthly" }, "End of Month (Monthly)"),
                        React.createElement("option", { value: "both" }, "Both Daily & Monthly"))),
                React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', height: 18, opacity: hasReports ? 1 : 0.5, marginTop: 4 } },
                    React.createElement("input", { type: "checkbox", disabled: !hasReports, checked: hasReports && draft.generate_statements, onChange: e => updateField('generate_statements', e.target.checked) }),
                    "Generate HTML/PDF statements")),
            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 6 } },
                React.createElement("div", { style: { fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 } }, "Email Transmission Settings"),
                React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', height: 18, opacity: hasReports && draft.generate_statements ? 1 : 0.5 } },
                    React.createElement("input", { type: "checkbox", disabled: !hasReports || !draft.generate_statements, checked: hasReports && draft.generate_statements && draft.send_statements_email, onChange: e => updateField('send_statements_email', e.target.checked) }),
                    "Send statements via email to clients"),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 110, textAlign: 'right', opacity: 0.8 } }, "Mail Server:"),
                    React.createElement("select", { className: "adm-select", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, disabled: !draft.send_statements_email, value: draft.mail_server, onChange: e => updateField('mail_server', e.target.value) }, MAIL_SERVERS.map(m => React.createElement("option", { key: m, value: m }, m)))),
                React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', height: 18, opacity: draft.send_statements_email ? 1 : 0.5, marginTop: 4 } },
                    React.createElement("input", { type: "checkbox", disabled: !draft.send_statements_email, checked: draft.send_statements_email && draft.send_copies_support, onChange: e => updateField('send_copies_support', e.target.checked) }),
                    "Send copies to corporate support"),
                draft.send_copies_support && (React.createElement("div", { style: { fontSize: 10, color: 'var(--theia-descriptionForeground)', paddingLeft: 20 } },
                    "To: ",
                    React.createElement("strong", null, draft.support_email || '(No support email configured)')))))));
}
exports.ReportsTab = ReportsTab;
//# sourceMappingURL=ReportsTab.js.map