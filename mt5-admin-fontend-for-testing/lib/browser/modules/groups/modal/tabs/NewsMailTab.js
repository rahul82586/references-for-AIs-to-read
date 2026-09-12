"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.NewsMailTab = void 0;
const React = require("react");
const GroupDraftContext_1 = require("../GroupDraftContext");
const LANG_OPTIONS = [
    'Any language',
    'English',
    'German',
    'Chinese',
    'Russian',
    'Spanish',
    'French',
    'Arabic'
];
function NewsMailTab() {
    const { draft, setDraft } = (0, GroupDraftContext_1.useGroupDraft)();
    const updateField = (field, val) => {
        setDraft(prev => ({ ...prev, [field]: val }));
    };
    const toggleLanguage = (lang) => {
        let nextLangs = [...draft.news_languages];
        if (lang === 'Any language') {
            nextLangs = ['Any language'];
        }
        else {
            // Remove 'Any language' if specific language is chosen
            nextLangs = nextLangs.filter(l => l !== 'Any language');
            if (nextLangs.includes(lang)) {
                nextLangs = nextLangs.filter(l => l !== lang);
            }
            else {
                nextLangs.push(lang);
            }
            if (nextLangs.length === 0) {
                nextLangs = ['Any language'];
            }
        }
        updateField('news_languages', nextLangs);
    };
    return (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', height: '100%', gap: 10, fontSize: 11 } },
        React.createElement("div", { style: { display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', borderRadius: 4 } },
            React.createElement("div", { style: { width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#9b59b6', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' } }, "N"),
            React.createElement("div", { style: { flex: 1, opacity: 0.9, lineHeight: 1.3 } }, "Configure news categories, client terminal news distribution modes, language filters, and internal email availability.")),
        React.createElement("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 24px', flex: 1, marginTop: 4 } },
            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 8 } },
                React.createElement("div", { style: { fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 } }, "News & Messaging Settings"),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "News Mode:"),
                    React.createElement("select", { className: "adm-select", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, value: draft.news_mode, onChange: e => updateField('news_mode', e.target.value) },
                        React.createElement("option", { value: "none" }, "None"),
                        React.createElement("option", { value: "headers" }, "Headers Only"),
                        React.createElement("option", { value: "full" }, "Full Package"))),
                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                    React.createElement("span", { style: { width: 100, textAlign: 'right', opacity: 0.8 } }, "News Categories:"),
                    React.createElement("input", { className: "adm-input", style: { flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }, placeholder: "e.g. Forex, Stocks\\US", value: draft.news_categories, onChange: e => updateField('news_categories', e.target.value) })),
                React.createElement("div", { style: { fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginTop: 8, marginBottom: 2 } }, "Mailbox Settings"),
                React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', height: 18 } },
                    React.createElement("input", { type: "checkbox", checked: draft.enable_internal_mail, onChange: e => updateField('enable_internal_mail', e.target.checked) }),
                    React.createElement("span", null, "Enable client mailbox in terminal"))),
            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 6 } },
                React.createElement("div", { style: { fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 } }, "Language Filters"),
                React.createElement("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px 12px' } }, LANG_OPTIONS.map(lang => {
                    const isChecked = draft.news_languages.includes(lang);
                    return (React.createElement("label", { key: lang, style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', fontSize: 11 } },
                        React.createElement("input", { type: "checkbox", checked: isChecked, onChange: () => toggleLanguage(lang) }),
                        lang));
                }))))));
}
exports.NewsMailTab = NewsMailTab;
//# sourceMappingURL=NewsMailTab.js.map