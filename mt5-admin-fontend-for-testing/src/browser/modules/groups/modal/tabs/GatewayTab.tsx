import * as React from 'react';
import { useGroupDraft } from '../GroupDraftContext';
import { API } from '../../../api';

export function GatewayTab(): React.ReactElement {
    const { draft, setDraft } = useGroupDraft();
    const [gateways, setGateways] = React.useState<any[]>([]);

    React.useEffect(() => {
        API.getGateways()
            .then((data: any) => {
                const filtered = data.filter((g: any) => !g.type.startsWith('Feeder_'));
                setGateways(filtered);
            })
            .catch(console.error);
    }, []);

    const updateField = (field: keyof typeof draft, val: any) => {
        setDraft(prev => ({ ...prev, [field]: val }));
    };

    const selectedGateway = gateways.find(g => g.id === draft.gateway_id);

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 10, fontSize: 11 }}>
            {/* Top header info banner */}
            <div style={{ display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', borderRadius: 4 }}>
                <div style={{ width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#3498db', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' }}>
                    G
                </div>
                <div style={{ flex: 1, opacity: 0.9, lineHeight: 1.3 }}>
                    Define loopback interface routing servers settings for secure history/trading component tunnels.
                    Trading operations of this group will be routed to A-Book channels through the gateway selected below.
                </div>
            </div>

            {/* Form controls */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 24px', flex: 1, marginTop: 4 }}>
                
                {/* Left Column - Selection & Server */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                    <div style={{ fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 }}>
                        ECN Route Assignment
                    </div>
                    
                    <div className="adm-form-row">
                        <label>Default A-Book Gateway</label>
                        <select 
                            className="adm-select" 
                            style={{ width: '100%', height: 20, padding: '2px 6px', fontSize: 11 }} 
                            value={draft.gateway_id || ''} 
                            onChange={e => updateField('gateway_id', e.target.value ? parseInt(e.target.value) : undefined)}
                        >
                            <option value="">None (B-Book Local Matching)</option>
                            {gateways.map(g => (
                                <option key={g.id} value={g.id}>
                                    {g.name} ({g.type})
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="adm-form-row">
                        <label>Gateway Server (IP:Port)</label>
                        <input 
                            className="adm-input" 
                            style={{ width: '100%', height: 20 }} 
                            disabled 
                            value={selectedGateway ? `${selectedGateway.host || 'localhost'}:${selectedGateway.port || '8003'}` : '—'} 
                        />
                    </div>
                </div>

                {/* Right Column - Authentication Details */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                    <div style={{ fontWeight: 'bold', fontSize: 11, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 }}>
                        Gateway Authentication Details
                    </div>

                    <div className="adm-form-row">
                        <label>Gateway Login</label>
                        <input 
                            className="adm-input" 
                            style={{ width: '100%', height: 20 }} 
                            disabled 
                            value={selectedGateway ? (selectedGateway.username || 'Numeric Login') : '—'} 
                        />
                    </div>

                    <div className="adm-form-row">
                        <label>Gateway Password</label>
                        <input 
                            className="adm-input" 
                            type="password" 
                            style={{ width: '100%', height: 20 }} 
                            disabled 
                            value={selectedGateway ? '••••••••' : ''} 
                            placeholder={selectedGateway ? 'Loopback key' : '—'} 
                        />
                    </div>
                </div>

            </div>
        </div>
    );
}
