import * as React from 'react';

interface ConnectStepProps {
    data: any;
    onChange: (fields: any) => void;
}

export function ConnectStep({ data, onChange }: ConnectStepProps): React.ReactElement {
    return (
        <div className="adm-modal-body" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div className="adm-hint" style={{ background: 'var(--theia-sideBarSectionHeader-background)', color: 'var(--theia-foreground)', margin: '0 0 12px 0' }}>
                <i className="codicon codicon-info" /> Connect to a remote MetaTrader 4/5 server to download symbols configurations directly.
            </div>

            <div className="adm-form-row">
                <label className="required">Server Type</label>
                <select 
                    className="adm-select" 
                    value={data.serverType} 
                    onChange={e => onChange({ serverType: e.target.value })}
                >
                    <option value="MT5">MetaTrader 5 Server</option>
                    <option value="MT4">MetaTrader 4 Server</option>
                </select>
            </div>

            <div className="adm-form-row">
                <label className="required">Server IP / Address</label>
                <input 
                    className="adm-input" 
                    required 
                    placeholder="e.g. 192.168.1.100:443" 
                    value={data.address} 
                    onChange={e => onChange({ address: e.target.value })} 
                />
            </div>

            <div className="adm-form-row">
                <label className="required">Login / Manager ID</label>
                <input 
                    className="adm-input" 
                    type="number" 
                    required 
                    placeholder="1000" 
                    value={data.login} 
                    onChange={e => onChange({ login: e.target.value })} 
                />
            </div>

            <div className="adm-form-row">
                <label className="required">Password</label>
                <input 
                    className="adm-input" 
                    type="password" 
                    required 
                    placeholder="••••••••" 
                    value={data.password} 
                    onChange={e => onChange({ password: e.target.value })} 
                />
            </div>

            {data.serverType === 'MT5' && (
                <>
                    <div className="adm-form-row" style={{ flexDirection: 'row', alignItems: 'center', gap: 8, marginTop: 8 }}>
                        <input 
                            type="checkbox" 
                            id="use-cert" 
                            checked={data.useCert} 
                            onChange={e => onChange({ useCert: e.target.checked })} 
                        />
                        <label htmlFor="use-cert" style={{ cursor: 'pointer', margin: 0 }}>Use certificate file (.pfx) for extended login authorization</label>
                    </div>

                    {data.useCert && (
                        <div style={{ paddingLeft: 20, display: 'flex', flexDirection: 'column', gap: 10 }}>
                            <div className="adm-form-row">
                                <label className="required">Certificate File</label>
                                <input 
                                    className="adm-input" 
                                    type="text" 
                                    placeholder="Click to choose certificate metadata..." 
                                    value={data.certFile} 
                                    onChange={e => onChange({ certFile: e.target.value })} 
                                />
                            </div>
                            <div className="adm-form-row">
                                <label className="required">Certificate Password</label>
                                <input 
                                    className="adm-input" 
                                    type="password" 
                                    placeholder="Cert key password" 
                                    value={data.certPassword} 
                                    onChange={e => onChange({ certPassword: e.target.value })} 
                                />
                            </div>
                        </div>
                    )}
                </>
            )}
        </div>
    );
}
