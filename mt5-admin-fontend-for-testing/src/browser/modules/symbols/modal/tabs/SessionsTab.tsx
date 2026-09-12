// @ts-nocheck
import * as React from 'react';
import { useSymbolDraft } from '../SymbolDraftContext';
import { DayScheduleEditor } from './sessions/DayScheduleEditor';

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

export function SessionsTab(): React.ReactElement {
    const { draft, setDraft } = useSymbolDraft();
    const [selectedDay, setSelectedDay] = React.useState<string | null>(null);

    const [schedules, setSchedules] = React.useState<Record<string, {
        quotes: Array<{ start: string, end: string }>;
        trade: Array<{ start: string, end: string }>;
        separateTrade: boolean;
    }>>({});

    React.useEffect(() => {
        const initialScheds: typeof schedules = {};
        DAYS.forEach(day => {
            initialScheds[day] = {
                quotes: [{ start: '00:00', end: '24:00' }],
                trade: [{ start: '00:00', end: '24:00' }],
                separateTrade: false
            };
        });
        setSchedules(initialScheds);
    }, []);

    const updateField = (field: keyof typeof draft, val: any) => {
        setDraft(prev => ({ ...prev, [field]: val }));
    };

    const handleSaveDaySchedule = (day: string, daySched: any) => {
        setSchedules(prev => ({ ...prev, [day]: daySched }));
        setSelectedDay(null);
    };

    const [useLimits, setUseLimits] = React.useState(false);
    const [limitFrom, setLimitFrom] = React.useState('');
    const [limitTo, setLimitTo] = React.useState('');

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 10, fontSize: 11 }}>
            {/* Top header info banner side-by-side */}
            <div style={{ display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', borderRadius: 4 }}>
                <div style={{ width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#f1c40f', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' }}>
                    T
                </div>
                <div style={{ flex: 1, opacity: 0.9, lineHeight: 1.3 }}>
                    Configure active timetables for quotes collection, client trade sessions, and calendar contract expirations.
                </div>
            </div>

            {/* Grid fields */}
            <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 0.9fr', gap: '8px 24px', flex: 1, marginTop: 4 }}>
                
                {/* Left Column (Timetable) */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    <div style={{ fontWeight: 'bold', fontSize: 10, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 }}>
                        Weekly Timetable
                    </div>

                    <div className="adm-table-wrap" style={{ border: '1px solid var(--theia-border)', height: 140, overflowY: 'auto' }}>
                        <table className="adm-table" style={{ fontSize: 10 }}>
                            <thead>
                                <tr>
                                    <th>Day</th>
                                    <th>Quotes Session</th>
                                    <th>Trade Session</th>
                                </tr>
                            </thead>
                            <tbody>
                                {DAYS.map(day => {
                                    const sched = schedules[day] || { quotes: [], trade: [], separateTrade: false };
                                    const quotesStr = sched.quotes.map(q => `${q.start}-${q.end}`).join(', ') || 'No session';
                                    const tradeStr = sched.separateTrade 
                                        ? (sched.trade.map(t => `${t.start}-${t.end}`).join(', ') || 'No session')
                                        : 'Same as Quotes';

                                    return (
                                        <tr 
                                            key={day} 
                                            className={selectedDay === day ? 'selected' : ''}
                                            onClick={() => setSelectedDay(day)}
                                            onDoubleClick={() => setSelectedDay(day)}
                                            style={{ cursor: 'pointer', height: 18 }}
                                        >
                                            <td><strong>{day.substring(0, 3)}</strong></td>
                                            <td>{quotesStr}</td>
                                            <td>{tradeStr}</td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Right Column (Expiration limits) */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    <div style={{ fontWeight: 'bold', fontSize: 10, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 }}>
                        Contract Expirations
                    </div>

                    <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, cursor: 'pointer', height: 20 }}>
                        <input type="checkbox" checked={useLimits} onChange={e => setUseLimits(e.target.checked)} />
                        Limit active date interval
                    </label>

                    {useLimits && (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                <span style={{ width: 50, opacity: 0.8 }}>From:</span>
                                <input className="adm-input" type="date" style={{ flex: 1, height: 20, padding: '2px 4px', fontSize: 11 }} value={limitFrom} onChange={e => setLimitFrom(e.target.value)} />
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                <span style={{ width: 50, opacity: 0.8 }}>To:</span>
                                <input className="adm-input" type="date" style={{ flex: 1, height: 20, padding: '2px 4px', fontSize: 11 }} value={limitTo} onChange={e => setLimitTo(e.target.value)} />
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {selectedDay && (
                <DayScheduleEditor 
                    day={selectedDay}
                    schedule={schedules[selectedDay]}
                    onClose={() => setSelectedDay(null)}
                    onSave={(sched) => handleSaveDaySchedule(selectedDay, sched)}
                />
            )}
        </div>
    );
}
