import * as React from 'react';
import { CommissionRule } from '../../GroupDraftContext';

interface CommissionRuleDialogProps {
    rule: CommissionRule | null;
    onClose: () => void;
    onSave: (rule: CommissionRule) => void;
}

export function CommissionRuleDialog({ rule, onClose, onSave }: CommissionRuleDialogProps): React.ReactElement {
    const [name, setName] = React.useState(rule ? rule.name : '');
    const [symbols, setSymbols] = React.useState(rule ? rule.symbols : '*');
    const [rate, setRate] = React.useState(rule ? String(rule.rate) : '0.0');
    const [type, setType] = React.useState<any>(rule ? rule.type : 'money');
    const [error, setError] = React.useState<string | null>(null);

    const handleSave = (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);

        if (!name.trim()) {
            setError('Commission name is required.');
            return;
        }

        if (!symbols.trim()) {
            setError('Please define symbols pattern.');
            return;
        }

        onSave({
            name: name.trim(),
            symbols: symbols.trim(),
            rate: parseFloat(rate) || 0.0,
            type
        });
        onClose();
    };

    return (
        <div className="adm-modal-overlay" style={{ zIndex: 1100 }} onClick={onClose}>
            <form className="adm-modal" style={{ width: 360 }} onClick={e => e.stopPropagation()} onSubmit={handleSave}>
                <div className="adm-modal-header">
                    <h2>{rule ? 'Edit Commission Rule' : 'Add Commission Rule'}</h2>
                    <button type="button" className="adm-modal-close" onClick={onClose}>×</button>
                </div>
                <div className="adm-modal-body">
                    {error && (
                        <div className="adm-hint" style={{ background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)', margin: '0 0 12px 0' }}>
                            <i className="codicon codicon-error" /> {error}
                        </div>
                    )}

                    <div className="adm-form-row">
                        <label className="required">Name</label>
                        <input className="adm-input" required placeholder="e.g. Standard Commission" value={name} onChange={e => setName(e.target.value)} />
                    </div>

                    <div className="adm-form-row">
                        <label className="required">Symbols Pattern</label>
                        <input className="adm-input" required placeholder="e.g. * or EURUSD" value={symbols} onChange={e => setSymbols(e.target.value)} />
                    </div>

                    <div className="adm-form-row">
                        <label>Commission Type</label>
                        <select className="adm-select" value={type} onChange={e => setType(e.target.value)}>
                            <option value="points">In points of spread</option>
                            <option value="percent">In percentage of deal volume</option>
                            <option value="money">In absolute money value per lot</option>
                        </select>
                    </div>

                    <div className="adm-form-row">
                        <label>Rate / Fee</label>
                        <input className="adm-input" type="number" step="0.001" value={rate} onChange={e => setRate(e.target.value)} />
                    </div>
                </div>
                <div className="adm-modal-footer">
                    <button type="submit" className="adm-btn adm-btn-primary">Save Commission</button>
                    <button type="button" className="adm-btn" onClick={onClose}>Cancel</button>
                </div>
            </form>
        </div>
    );
}
