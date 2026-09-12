import * as React from 'react';

interface SymbolFilterBarProps {
    symbols: any[];
    onFilterApplied: (filtered: any[]) => void;
}

export function SymbolFilterBar({ symbols, onFilterApplied }: SymbolFilterBarProps): React.ReactElement {
    const [filterQuery, setFilterQuery] = React.useState('');

    const matchPattern = (name: string, pattern: string): boolean => {
        // Escape special chars except *
        const escaped = pattern.replace(/[-\/\{\}\(\)\+\?\.\\\^\$\|]/g, '\\$&');
        const wild = escaped.replace(/\*/g, '.*');
        const regex = new RegExp(`^${wild}$`, 'i');
        // Extract the instrument name (last segment) or match full name
        const lastSegment = name.split('\\').pop() || name;
        return regex.test(lastSegment) || regex.test(name);
    };

    const handleApplyFilter = () => {
        if (!filterQuery.trim()) {
            onFilterApplied(symbols);
            return;
        }

        const parts = filterQuery.split(',').map(p => p.trim()).filter(Boolean);
        const positivePatterns = parts.filter(p => !p.startsWith('!'));
        const negativePatterns = parts.filter(p => p.startsWith('!')).map(p => p.substring(1));

        const filtered = symbols.filter(s => {
            // Must match at least one positive pattern (if any are specified)
            let isPositiveMatch = positivePatterns.length === 0;
            for (const p of positivePatterns) {
                if (matchPattern(s.symbol, p)) {
                    isPositiveMatch = true;
                    break;
                }
            }

            // Must NOT match any negative patterns
            let isNegativeMatch = false;
            for (const p of negativePatterns) {
                if (matchPattern(s.symbol, p)) {
                    isNegativeMatch = true;
                    break;
                }
            }

            return isPositiveMatch && !isNegativeMatch;
        });

        onFilterApplied(filtered);
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            handleApplyFilter();
        }
    };

    return (
        <div className="adm-toolbar" style={{ borderBottom: '1px solid var(--theia-border)', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ fontSize: 11, fontWeight: '600', color: 'var(--theia-descriptionForeground)', whiteSpace: 'nowrap' }}>
                Filter Query:
            </div>
            <div style={{ flex: 1, display: 'flex', gap: 8 }}>
                <input 
                    className="adm-input" 
                    style={{ flex: 1, fontSize: 11, padding: '3px 8px', height: 24 }}
                    placeholder="e.g. EUR*, *USD, !GBPUSD" 
                    value={filterQuery}
                    onChange={e => setFilterQuery(e.target.value)}
                    onKeyDown={handleKeyDown}
                />
                <button 
                    type="button" 
                    className="adm-btn adm-btn-primary" 
                    style={{ padding: '0 12px', height: 24, fontSize: 11 }}
                    onClick={handleApplyFilter}
                >
                    Apply Filter
                </button>
                {filterQuery && (
                    <button 
                        type="button" 
                        className="adm-btn" 
                        style={{ padding: '0 8px', height: 24, fontSize: 11 }}
                        onClick={() => {
                            setFilterQuery('');
                            onFilterApplied(symbols);
                        }}
                    >
                        Clear
                    </button>
                )}
            </div>
        </div>
    );
}
