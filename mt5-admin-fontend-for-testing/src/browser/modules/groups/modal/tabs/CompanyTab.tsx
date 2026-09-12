import * as React from 'react';
import { useGroupDraft } from '../GroupDraftContext';

export function CompanyTab(): React.ReactElement {
    const { draft, setDraft, errors, setErrors } = useGroupDraft();

    const updateField = (field: keyof typeof draft, val: any) => {
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

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 10, fontSize: 11 }}>
            {/* Top header info banner side-by-side */}
            <div style={{ display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', borderRadius: 4 }}>
                <div style={{ width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#34495e', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' }}>
                    C
                </div>
                <div style={{ flex: 1, opacity: 0.9, lineHeight: 1.3 }}>
                    Configure licensee business parameters, automated templates paths, client support portals, and website routing URLs.
                </div>
            </div>

            {/* Grid fields */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 24px', flex: 1, marginTop: 4 }}>
                
                {/* Left Column (Licensee info) */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    <div style={{ fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 }}>
                        Licensee Credentials
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }} className="required">Company:</span>
                        <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                            <select 
                                className={`adm-select ${errors.company ? 'error' : ''}`}
                                style={{ height: 20, padding: '2px 6px', fontSize: 11 }}
                                value={draft.company}
                                onChange={e => updateField('company', e.target.value)}
                            >
                                <option value="">Select Company...</option>
                                <option value="MetaQuotes Software Corp.">MetaQuotes Software Corp.</option>
                                <option value="Demo Brokerage Ltd.">Demo Broker brokerage Ltd.</option>
                                <option value="Global Clearing Inc.">Global Clearing Inc.</option>
                            </select>
                            {errors.company && <span className="adm-input-error-text" style={{ fontSize: 9, color: 'var(--theia-errorForeground)' }}>{errors.company}</span>}
                        </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>Website URL:</span>
                        <input 
                            className="adm-input" 
                            type="url"
                            style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                            placeholder="https://www.company.com" 
                            value={draft.company_website} 
                            onChange={e => updateField('company_website', e.target.value)} 
                        />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>Corporate Email:</span>
                        <input 
                            className="adm-input" 
                            type="email"
                            style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                            placeholder="info@company.com" 
                            value={draft.company_email} 
                            onChange={e => updateField('company_email', e.target.value)} 
                        />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>Templates Dir:</span>
                        <input 
                            className="adm-input" 
                            style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                            placeholder="e.g. standard_templates" 
                            value={draft.templates_folder} 
                            onChange={e => updateField('templates_folder', e.target.value)} 
                        />
                    </div>
                </div>

                {/* Right Column (Web Portals & Support) */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    <div style={{ fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 }}>
                        Client Support & Portals
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>Deposit URL:</span>
                        <input 
                            className="adm-input" 
                            type="url"
                            style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                            placeholder="https://client.company.com/deposit" 
                            value={draft.deposit_url} 
                            onChange={e => updateField('deposit_url', e.target.value)} 
                        />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>Withdrawal URL:</span>
                        <input 
                            className="adm-input" 
                            type="url"
                            style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                            placeholder="https://client.company.com/withdraw" 
                            value={draft.withdrawal_url} 
                            onChange={e => updateField('withdrawal_url', e.target.value)} 
                        />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>Support URL:</span>
                        <input 
                            className="adm-input" 
                            type="url"
                            style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                            placeholder="https://support.company.com" 
                            value={draft.support_site} 
                            onChange={e => updateField('support_site', e.target.value)} 
                        />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 100, textAlign: 'right', opacity: 0.8 }}>Support Email:</span>
                        <input 
                            className="adm-input" 
                            type="email"
                            style={{ flex: 1, height: 20, padding: '2px 6px', fontSize: 11 }}
                            placeholder="support@company.com" 
                            value={draft.support_email} 
                            onChange={e => updateField('support_email', e.target.value)} 
                        />
                    </div>
                </div>

            </div>
        </div>
    );
}
