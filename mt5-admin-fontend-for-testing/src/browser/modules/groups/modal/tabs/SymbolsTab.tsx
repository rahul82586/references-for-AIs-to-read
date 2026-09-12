import * as React from 'react';
import { useGroupDraft, SymbolRule } from '../GroupDraftContext';
import { SymbolRuleDialog } from './symbols/SymbolRuleDialog';
import { API } from '../../../api';

export function SymbolsTab(): React.ReactElement {
    const { draft, setDraft } = useGroupDraft();
    const [symbolsList, setSymbolsList] = React.useState<string[]>([]);
    const [selectedIdx, setSelectedIdx] = React.useState<number | null>(null);
    
    // Modal states
    const [showDialog, setShowDialog] = React.useState(false);
    const [editRule, setEditRule] = React.useState<SymbolRule | null>(null);

    const loadSymbols = async () => {
        try {
            const data = await API.getSymbols();
            setSymbolsList(data.map((s: any) => s.symbol));
        } catch (e) {
            console.error('Failed to load active symbols checklist:', e);
        }
    };

    React.useEffect(() => {
        loadSymbols();
    }, []);

    const handleAdd = () => {
        setEditRule(null);
        setShowDialog(true);
    };

    const handleEdit = () => {
        if (selectedIdx === null) return;
        setEditRule(draft.symbol_rules[selectedIdx]);
        setShowDialog(true);
    };

    const handleDelete = () => {
        if (selectedIdx === null) return;
        setDraft(prev => ({
            ...prev,
            symbol_rules: prev.symbol_rules.filter((_, idx) => idx !== selectedIdx)
        }));
        setSelectedIdx(null);
    };

    const handleSaveRule = (rule: SymbolRule) => {
        setDraft(prev => {
            const nextRules = [...prev.symbol_rules];
            if (editRule && selectedIdx !== null) {
                nextRules[selectedIdx] = rule;
            } else {
                nextRules.push(rule);
            }
            return { ...prev, symbol_rules: nextRules };
        });
    };

    // Helper to check if a strict symbol (no wildcard) exists in the database
    const checkSymbolExists = (pattern: string) => {
        if (pattern.includes('*') || pattern.includes('!')) return true; // pattern mask
        return symbolsList.includes(pattern);
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 10, fontSize: 11 }}>
            {/* Top header info banner side-by-side */}
            <div style={{ display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', borderRadius: 4, flexShrink: 0 }}>
                <div style={{ width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#2ecc71', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' }}>
                    S
                </div>
                <div style={{ flex: 1, opacity: 0.9, lineHeight: 1.3 }}>
                    Configure financial instrument settings, trade permissions, overrides for spreads, commissions, and margin rates.
                </div>
            </div>

            {/* Layout Container: Action Buttons on Left, Table on Right */}
            <div style={{ display: 'flex', gap: 16, flex: 1, minHeight: 0 }}>
                {/* Action Buttons on Left */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8, width: 90, flexShrink: 0 }}>
                    <button 
                        type="button" 
                        className="adm-btn adm-btn-primary" 
                        onClick={handleAdd}
                        style={{ fontSize: 11, width: '100%', height: 24, padding: '2px 8px' }}
                    >
                        Add
                    </button>
                    <button 
                        type="button" 
                        className="adm-btn" 
                        disabled={selectedIdx === null} 
                        onClick={handleEdit}
                        style={{ fontSize: 11, width: '100%', height: 24, padding: '2px 8px' }}
                    >
                        Edit
                    </button>
                    <button 
                        type="button" 
                        className="adm-btn adm-btn-danger" 
                        disabled={selectedIdx === null} 
                        onClick={handleDelete}
                        style={{ fontSize: 11, width: '100%', height: 24, padding: '2px 8px' }}
                    >
                        Delete
                    </button>
                </div>

                {/* Table Area (Fills remaining container height with auto overflow) */}
                <div className="adm-table-wrap" style={{ border: '1px solid var(--theia-border)', flex: 1, overflowY: 'auto', height: '100%' }}>
                    <table className="adm-table" style={{ fontSize: 11 }}>
                        <thead>
                            <tr>
                                <th>Symbol Pattern</th>
                                <th>Trade Status</th>
                                <th>Spread Diff</th>
                                <th>Commission</th>
                                <th>Margin Multiplier</th>
                            </tr>
                        </thead>
                        <tbody>
                            {draft.symbol_rules.map((rule, idx) => {
                                const exists = checkSymbolExists(rule.symbol);
                                return (
                                    <tr 
                                        key={idx} 
                                        className={`${selectedIdx === idx ? 'selected' : ''} ${!exists ? 'adm-row-warning' : ''}`}
                                        onClick={() => setSelectedIdx(idx)}
                                        onDoubleClick={handleEdit}
                                        style={{ height: 22 }}
                                        title={!exists ? `Symbol "${rule.symbol}" does not exist in the active symbols database.` : ''}
                                    >
                                        <td>
                                            {!exists && <i className="codicon codicon-warning" style={{ color: '#f0ad4e', marginRight: 4 }} />}
                                            <strong>{rule.symbol}</strong>
                                        </td>
                                        <td>
                                            <span className={`adm-toggle ${rule.trade_allowed ? 'on' : 'off'}`} style={{ padding: '1px 4px', fontSize: 9 }}>
                                                {rule.trade_allowed ? '✓ ALLOW' : '✗ BLOCK'}
                                            </span>
                                        </td>
                                        <td>{rule.spread_diff > 0 ? `+${rule.spread_diff}` : rule.spread_diff} pts</td>
                                        <td>{rule.commission_rate} money</td>
                                        <td>{rule.margin_rate}x</td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </div>

            {showDialog && (
                <SymbolRuleDialog 
                    rule={editRule}
                    availableSymbols={symbolsList}
                    onClose={() => setShowDialog(false)}
                    onSave={handleSaveRule}
                />
            )}
        </div>
    );
}
