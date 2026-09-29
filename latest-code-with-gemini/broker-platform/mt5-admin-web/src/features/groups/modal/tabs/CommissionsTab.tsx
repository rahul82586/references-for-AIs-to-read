import * as React from 'react';
import { useGroupDraft, CommissionRule } from '../GroupDraftContext';
import { CommissionRuleDialog } from './commissions/CommissionRuleDialog';

export function CommissionsTab(): React.ReactElement {
    const { draft, setDraft } = useGroupDraft();
    const [selectedIdx, setSelectedIdx] = React.useState<number | null>(null);

    const [showDialog, setShowDialog] = React.useState(false);
    const [editRule, setEditRule] = React.useState<CommissionRule | null>(null);

    const handleAdd = () => {
        setEditRule(null);
        setShowDialog(true);
    };

    const handleEdit = () => {
        if (selectedIdx === null) return;
        setEditRule(draft.commission_rules[selectedIdx]);
        setShowDialog(true);
    };

    const handleDelete = () => {
        if (selectedIdx === null) return;
        setDraft(prev => ({
            ...prev,
            commission_rules: prev.commission_rules.filter((_, idx) => idx !== selectedIdx)
        }));
        setSelectedIdx(null);
    };

    const handleSaveRule = (rule: CommissionRule) => {
        setDraft(prev => {
            const nextRules = [...prev.commission_rules];
            if (editRule && selectedIdx !== null) {
                nextRules[selectedIdx] = rule;
            } else {
                nextRules.push(rule);
            }
            return { ...prev, commission_rules: nextRules };
        });
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 10, fontSize: 11 }}>
            {/* Top header info banner side-by-side */}
            <div style={{ display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', borderRadius: 4 }}>
                <div style={{ width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#e74c3c', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' }}>
                    %
                </div>
                <div style={{ flex: 1, opacity: 0.9, lineHeight: 1.3 }}>
                    Configure automated client deal commission rules, charging formulas, and target symbol pattern constraints.
                </div>
            </div>

            {/* Toolbar */}
            <div className="adm-toolbar" style={{ padding: '0px 0px 4px 0px', borderBottom: 'none', display: 'flex', gap: 6, flexShrink: 0 }}>
                <button type="button" className="adm-btn adm-btn-primary" style={{ padding: '2px 8px', height: 22, fontSize: 11 }} onClick={handleAdd}><i className="codicon codicon-add" /> Add Commission</button>
                <button type="button" className="adm-btn" style={{ padding: '2px 8px', height: 22, fontSize: 11 }} disabled={selectedIdx === null} onClick={handleEdit}><i className="codicon codicon-edit" /> Edit</button>
                <button type="button" className="adm-btn adm-btn-danger" style={{ padding: '2px 8px', height: 22, fontSize: 11 }} disabled={selectedIdx === null} onClick={handleDelete}><i className="codicon codicon-trash" /> Delete</button>
            </div>

            {/* Table Area */}
            <div className="adm-table-wrap" style={{ border: '1px solid var(--theia-border)', flex: 1, overflowY: 'auto' }}>
                <table className="adm-table" style={{ fontSize: 11 }}>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Symbols Pattern</th>
                            <th>Rate</th>
                            <th>Type</th>
                        </tr>
                    </thead>
                    <tbody>
                        {draft.commission_rules.length === 0 ? (
                            <tr>
                                <td colSpan={4} style={{ textAlign: 'center', opacity: 0.6, padding: 20 }}>
                                    No commissions configured for this group. Deals will run with zero charges.
                                </td>
                            </tr>
                        ) : (
                            draft.commission_rules.map((rule, idx) => (
                                <tr 
                                    key={idx} 
                                    className={selectedIdx === idx ? 'selected' : ''}
                                    onClick={() => setSelectedIdx(idx)}
                                    onDoubleClick={handleEdit}
                                    style={{ height: 22 }}
                                >
                                    <td><strong>{rule.name}</strong></td>
                                    <td><code>{rule.symbols}</code></td>
                                    <td>{rule.rate}</td>
                                    <td>
                                        <span className="adm-tag" style={{ padding: '1px 4px', fontSize: 9 }}>
                                            {rule.type === 'points' ? 'points' : rule.type === 'percent' ? 'percent' : 'money/lot'}
                                        </span>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            {showDialog && (
                <CommissionRuleDialog 
                    rule={editRule}
                    onClose={() => setShowDialog(false)}
                    onSave={handleSaveRule}
                />
            )}
        </div>
    );
}
