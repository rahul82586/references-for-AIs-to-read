import * as React from 'react';
import { useGroupDraft } from '../GroupDraftContext';

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

export function NewsMailTab(): React.ReactElement {
    const { draft, setDraft } = useGroupDraft();

    const updateField = (field: keyof typeof draft, val: any) => {
        setDraft(prev => ({ ...prev, [field]: val }));
    };

    const toggleLanguage = (lang: string) => {
        let nextLangs = [...draft.news_languages];
        if (lang === 'Any language') {
            nextLangs = ['Any language'];
        } else {
            // Remove 'Any language' if specific language is chosen
            nextLangs = nextLangs.filter(l => l !== 'Any language');
            if (nextLangs.includes(lang)) {
                nextLangs = nextLangs.filter(l => l !== lang);
            } else {
                nextLangs.push(lang);
            }
            if (nextLangs.length === 0) {
                nextLangs = ['Any language'];
            }
        }
        updateField('news_languages', nextLangs);
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 10, fontSize: 11 }}>
            {/* Top header info banner side-by-side */}
            <div style={{ display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', borderRadius: 4 }}>
                <div style={{ width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#9b59b6', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' }}>
                    N
                </div>
                <div style={{ flex: 1, opacity: 0.9, lineHeight: 1.3 }}>
                    Configure news categories, client terminal news distribution modes, language filters, and internal email availability.
                </div>
            </div>

            {/* Grid fields */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 24px', flex: 1, marginTop: 4 }}>
                
                {/* Left Column (News Delivery & Mailbox) */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    <div style={{ fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 }}>
                        News & Messaging Settings
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>News Mode:</span>
                        <select 
                            className="adm-select"
                            style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                            value={draft.news_mode}
                            onChange={e => updateField('news_mode', e.target.value)}
                        >
                            <option value="none">None</option>
                            <option value="headers">Headers Only</option>
                            <option value="full">Full Package</option>
                        </select>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>News Categories:</span>
                        <input 
                            className="adm-input" 
                            style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                            placeholder="e.g. Forex, Stocks\US" 
                            value={draft.news_categories}
                            onChange={e => updateField('news_categories', e.target.value)}
                        />
                    </div>

                    <div style={{ fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginTop: 8, marginBottom: 2 }}>
                        Mailbox Settings
                    </div>

                    <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', height: 18 }}>
                        <input 
                            type="checkbox" 
                            checked={draft.enable_internal_mail}
                            onChange={e => updateField('enable_internal_mail', e.target.checked)}
                        />
                        <span>Enable client mailbox in terminal</span>
                    </label>
                </div>

                {/* Right Column (News Languages list) */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    <div style={{ fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 }}>
                        Language Filters
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px 12px' }}>
                        {LANG_OPTIONS.map(lang => {
                            const isChecked = draft.news_languages.includes(lang);
                            return (
                                <label key={lang} style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', fontSize: 11 }}>
                                    <input 
                                        type="checkbox"
                                        checked={isChecked}
                                        onChange={() => toggleLanguage(lang)}
                                    />
                                    {lang}
                                </label>
                            );
                        })}
                    </div>
                </div>

            </div>
        </div>
    );
}
