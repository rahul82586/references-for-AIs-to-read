"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CommonTab = void 0;
const React = require("react");
const GroupDraftContext_1 = require("../GroupDraftContext");
const CURRENCIES = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD'];
const AUTH_METHODS = ['Normal', '1024-bit RSA SSL', '2048-bit RSA SSL', 'Custom SSL certificate'];
const SERVERS = ['MetaQuotes-Demo', 'History-01', 'Access-01', 'Backup-01'];
function CommonTab() {
    const { draft, setDraft, errors, setErrors } = (0, GroupDraftContext_1.useGroupDraft)();
    const updateField = (field, val) => {
        setDraft(prev => ({ ...prev, [field]: val }));
        // Validation logic
        setErrors(prev => {
            const next = { ...prev };
            if (field === 'name') {
                if (!val) {
                    next.name = 'Group name is required';
                }
                else if (/[/:*?"<>|]/.test(val)) {
                    next.name = 'Group name cannot contain special characters like /, :, *, ?, ", <, >, |';
                }
                else {
                    delete next.name;
                }
            }
            return next;
        });
    };
    // Auto digit lock for standard currencies
    React.useEffect(() => {
        if (CURRENCIES.includes(draft.currency)) {
            updateField('digits', 2);
        }
    }, [draft.currency]);
    const isDemoGroup = draft.name.toLowerCase().includes('demo');
    return (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', height: '100%', gap: 10, fontSize: 11 } },
        React.createElement("div", { style: { display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', borderRadius: 4 } },
            React.createElement("div", { style: { width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#3498db', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' } }, "G"),
            React.createElement("div", { style: { flex: 1, opacity: 0.9, lineHeight: 1.3 } }, "Configure group identification, accounting deposit currency, connection servers, and security authentication parameters.")),
        React.createElement("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 24px', flex: 1 } },
            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 6 } },
                React.createElement("div", { style: { fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 } }, "General & Authentication"),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 90, textAlign: 'right', opacity: 0.8 } }, "Name (path):"),
                    React.createElement("div", { style: { flex: 1, display: 'flex', flexDirection: 'column' } },
                        React.createElement("input", { className: `adm-input ${errors.name ? 'error' : ''}`, style: { height: 20, padding: '2px 6px', fontSize: 11 }, placeholder: "e.g. demo\\forex", value: draft.name, onChange: e => updateField('name', e.target.value) }),
                        errors.name && React.createElement("span", { className: "adm-input-error-text", style: { fontSize: 9, color: 'var(--theia-errorForeground)' } }, errors.name))),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 90, textAlign: 'right', opacity: 0.8 } }, "Currency:"),
                    React.createElement("div", { style: { flex: 1, display: 'flex', gap: 6 } },
                        React.createElement("select", { className: "adm-select", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: CURRENCIES.includes(draft.currency) ? draft.currency : 'other', onChange: e => {
                                const val = e.target.value;
                                if (val !== 'other') {
                                    updateField('currency', val);
                                }
                            } },
                            CURRENCIES.map(c => React.createElement("option", { key: c, value: c }, c)),
                            React.createElement("option", { value: "other" }, "Custom...")),
                        !CURRENCIES.includes(draft.currency) && (React.createElement("input", { className: "adm-input", style: { width: 60, height: 20, padding: '2px 6px', fontSize: 11 }, placeholder: "e.g. USD", value: draft.currency, onChange: e => updateField('currency', e.target.value.toUpperCase()) })))),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 90, textAlign: 'right', opacity: 0.8 } }, "Digits:"),
                    React.createElement("input", { className: "adm-input", type: "number", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, disabled: CURRENCIES.includes(draft.currency), value: draft.digits, onChange: e => updateField('digits', parseInt(e.target.value) || 0) })),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 90, textAlign: 'right', opacity: 0.8 } }, "Trade Server:"),
                    React.createElement("select", { className: "adm-select", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.trade_server, onChange: e => updateField('trade_server', e.target.value) }, SERVERS.map(s => React.createElement("option", { key: s, value: s }, s)))),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 90, textAlign: 'right', opacity: 0.8 } }, "Auth Mode:"),
                    React.createElement("select", { className: "adm-select", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.authentication, onChange: e => updateField('authentication', e.target.value) }, AUTH_METHODS.map(a => React.createElement("option", { key: a, value: a }, a)))),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 90, textAlign: 'right', opacity: 0.8 } }, "Min Pass Len:"),
                    React.createElement("input", { className: "adm-input", type: "number", max: 16, min: 5, style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.min_password_len, onChange: e => updateField('min_password_len', Math.min(16, parseInt(e.target.value) || 8)) }))),
            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 6 } },
                React.createElement("div", { style: { fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 } }, "Security & Regulatory Options"),
                React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', height: 18 } },
                    React.createElement("input", { type: "checkbox", checked: draft.enable_cert_confirm, onChange: e => updateField('enable_cert_confirm', e.target.checked) }),
                    "Confirm client SSL certificates"),
                React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', height: 18 } },
                    React.createElement("input", { type: "checkbox", checked: draft.change_pass_first_login, onChange: e => updateField('change_pass_first_login', e.target.checked) }),
                    "Force password change first login"),
                React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', height: 18 } },
                    React.createElement("input", { type: "checkbox", checked: draft.enable_connections, onChange: e => updateField('enable_connections', e.target.checked) }),
                    "Enable group client connections"),
                React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', height: 18 } },
                    React.createElement("input", { type: "checkbox", checked: draft.regulatory_restrictions, onChange: e => updateField('regulatory_restrictions', e.target.checked) }),
                    "Enforce retail leverage restrictions (ESMA)"),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 70, textAlign: 'right', opacity: 0.8 } }, "OTP Mode:"),
                    React.createElement("select", { className: "adm-select", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.otp_mode, onChange: e => updateField('otp_mode', e.target.value) },
                        React.createElement("option", { value: "disabled" }, "Disabled"),
                        React.createElement("option", { value: "all" }, "Required for all"),
                        React.createElement("option", { value: "web" }, "Required for Web Platform"))),
                draft.otp_mode !== 'disabled' && (React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', height: 18, paddingLeft: 10 } },
                    React.createElement("input", { type: "checkbox", checked: draft.force_otp, onChange: e => updateField('force_otp', e.target.checked) }),
                    "Force OTP registration window")),
                React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', height: 18, opacity: isDemoGroup ? 0.6 : 1 } },
                    React.createElement("input", { type: "checkbox", disabled: isDemoGroup, checked: !isDemoGroup && draft.show_risk_warning, onChange: e => updateField('show_risk_warning', e.target.checked) }),
                    "Show connection risk warnings")))));
}
exports.CommonTab = CommonTab;
//# sourceMappingURL=CommonTab.js.map