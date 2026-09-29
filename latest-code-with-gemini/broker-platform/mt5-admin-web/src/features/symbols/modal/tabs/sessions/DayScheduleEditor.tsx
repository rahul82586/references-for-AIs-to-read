import * as React from 'react';

interface SessionBlock {
    start: string;
    end: string;
}

interface DayScheduleEditorProps {
    day: string;
    schedule: {
        quotes: SessionBlock[];
        trade: SessionBlock[];
        separateTrade: boolean;
    };
    onClose: () => void;
    onSave: (schedule: any) => void;
}

export function DayScheduleEditor({ day, schedule, onClose, onSave }: DayScheduleEditorProps): React.ReactElement {
    const [quotes, setQuotes] = React.useState<SessionBlock[]>([...schedule.quotes]);
    const [trade, setTrade] = React.useState<SessionBlock[]>([...schedule.trade]);
    const [separateTrade, setSeparateTrade] = React.useState(schedule.separateTrade);

    const handleAddBlock = (type: 'quotes' | 'trade') => {
        const newBlock = { start: '08:00', end: '17:00' };
        if (type === 'quotes') {
            setQuotes([...quotes, newBlock]);
        } else {
            setTrade([...trade, newBlock]);
        }
    };

    const handleRemoveBlock = (type: 'quotes' | 'trade', index: number) => {
        if (type === 'quotes') {
            setQuotes(quotes.filter((_, i) => i !== index));
        } else {
            setTrade(trade.filter((_, i) => i !== index));
        }
    };

    const handleTimeChange = (type: 'quotes' | 'trade', index: number, field: 'start' | 'end', value: string) => {
        if (type === 'quotes') {
            const next = [...quotes];
            next[index] = { ...next[index], [field]: value };
            setQuotes(next);
        } else {
            const next = [...trade];
            next[index] = { ...next[index], [field]: value };
            setTrade(next);
        }
    };

    const handleSave = () => {
        onSave({
            quotes,
            trade: separateTrade ? trade : [...quotes],
            separateTrade
        });
    };

    return (
        <div className="adm-modal-overlay" style={{ zIndex: 1200 }} onClick={onClose}>
            <div className="adm-modal" style={{ width: 440 }} onClick={e => e.stopPropagation()}>
                <div className="adm-modal-header">
                    <h2>Edit Time Sessions — {day}</h2>
                    <button type="button" className="adm-modal-close" onClick={onClose}>×</button>
                </div>
                <div className="adm-modal-body" style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                    
                    {/* Quotes Session Blocks */}
                    <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                            <span style={{ fontSize: 12, fontWeight: 'bold' }}>Quotes Sessions</span>
                            <button type="button" className="adm-btn" style={{ fontSize: 10, padding: '2px 8px' }} onClick={() => handleAddBlock('quotes')}>
                                <i className="codicon codicon-add" /> Add Session
                            </button>
                        </div>

                        {quotes.length === 0 ? (
                            <div style={{ padding: 12, background: 'var(--theia-sideBarSectionHeader-background)', fontSize: 11, textAlign: 'center', opacity: 0.6 }}>
                                No quotes session active. Market will be offline.
                            </div>
                        ) : (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                                {quotes.map((block, idx) => (
                                    <div key={idx} style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                                        <input className="adm-input" type="time" style={{ width: 110, fontSize: 11, padding: 3, height: 22 }} value={block.start} onChange={e => handleTimeChange('quotes', idx, 'start', e.target.value)} />
                                        <span>to</span>
                                        <input className="adm-input" type="time" style={{ width: 110, fontSize: 11, padding: 3, height: 22 }} value={block.end} onChange={e => handleTimeChange('quotes', idx, 'end', e.target.value)} />
                                        <button type="button" className="adm-icon-btn" onClick={() => handleRemoveBlock('quotes', idx)}>
                                            <i className="codicon codicon-trash" style={{ color: 'var(--theia-errorForeground)' }} />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Trade Session Separate Checkbox */}
                    <div className="adm-form-row" style={{ flexDirection: 'row', alignItems: 'center', gap: 8, borderTop: '1px solid var(--theia-border)', paddingTop: 10 }}>
                        <input type="checkbox" id="sep-trade" checked={separateTrade} onChange={e => setSeparateTrade(e.target.checked)} />
                        <label htmlFor="sep-trade" style={{ cursor: 'pointer', margin: 0, fontSize: 12 }}>Enable separate trading sessions (different from quotes)</label>
                    </div>

                    {/* Trade Session Blocks */}
                    {separateTrade && (
                        <div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                                <span style={{ fontSize: 12, fontWeight: 'bold' }}>Trade Sessions</span>
                                <button type="button" className="adm-btn" style={{ fontSize: 10, padding: '2px 8px' }} onClick={() => handleAddBlock('trade')}>
                                    <i className="codicon codicon-add" /> Add Session
                                </button>
                            </div>

                            {trade.length === 0 ? (
                                <div style={{ padding: 12, background: 'var(--theia-sideBarSectionHeader-background)', fontSize: 11, textAlign: 'center', opacity: 0.6 }}>
                                    No trading session active. Clients cannot execute trades.
                                </div>
                            ) : (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                                    {trade.map((block, idx) => (
                                        <div key={idx} style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                                            <input className="adm-input" type="time" style={{ width: 110, fontSize: 11, padding: 3, height: 22 }} value={block.start} onChange={e => handleTimeChange('trade', idx, 'start', e.target.value)} />
                                            <span>to</span>
                                            <input className="adm-input" type="time" style={{ width: 110, fontSize: 11, padding: 3, height: 22 }} value={block.end} onChange={e => handleTimeChange('trade', idx, 'end', e.target.value)} />
                                            <button type="button" className="adm-icon-btn" onClick={() => handleRemoveBlock('trade', idx)}>
                                                <i className="codicon codicon-trash" style={{ color: 'var(--theia-errorForeground)' }} />
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}
                </div>
                <div className="adm-modal-footer">
                    <button type="button" className="adm-btn adm-btn-primary" onClick={handleSave}>Save changes</button>
                    <button type="button" className="adm-btn" onClick={onClose}>Cancel</button>
                </div>
            </div>
        </div>
    );
}
