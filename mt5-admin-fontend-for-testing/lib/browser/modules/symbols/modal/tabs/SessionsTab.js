"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SessionsTab = void 0;
// @ts-nocheck
const React = require("react");
const SymbolDraftContext_1 = require("../SymbolDraftContext");
const DayScheduleEditor_1 = require("./sessions/DayScheduleEditor");
const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
function SessionsTab() {
    const { draft, setDraft } = (0, SymbolDraftContext_1.useSymbolDraft)();
    const [selectedDay, setSelectedDay] = React.useState(null);
    const [schedules, setSchedules] = React.useState({});
    React.useEffect(() => {
        const initialScheds = {};
        DAYS.forEach(day => {
            initialScheds[day] = {
                quotes: [{ start: '00:00', end: '24:00' }],
                trade: [{ start: '00:00', end: '24:00' }],
                separateTrade: false
            };
        });
        setSchedules(initialScheds);
    }, []);
    const updateField = (field, val) => {
        setDraft(prev => ({ ...prev, [field]: val }));
    };
    const handleSaveDaySchedule = (day, daySched) => {
        setSchedules(prev => ({ ...prev, [day]: daySched }));
        setSelectedDay(null);
    };
    const [useLimits, setUseLimits] = React.useState(false);
    const [limitFrom, setLimitFrom] = React.useState('');
    const [limitTo, setLimitTo] = React.useState('');
    return (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', height: '100%', gap: 10, fontSize: 11 } },
        React.createElement("div", { style: { display: 'flex', gap: 12, alignItems: 'center', background: 'var(--theia-sideBarSectionHeader-background)', padding: '6px 12px', borderRadius: 4 } },
            React.createElement("div", { style: { width: 32, height: 32, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#f1c40f', borderRadius: 4, color: '#fff', fontSize: 18, fontWeight: 'bold' } }, "T"),
            React.createElement("div", { style: { flex: 1, opacity: 0.9, lineHeight: 1.3 } }, "Configure active timetables for quotes collection, client trade sessions, and calendar contract expirations.")),
        React.createElement("div", { style: { display: 'grid', gridTemplateColumns: '1.1fr 0.9fr', gap: '8px 24px', flex: 1, marginTop: 4 } },
            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 6 } },
                React.createElement("div", { style: { fontWeight: 'bold', fontSize: 10, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 } }, "Weekly Timetable"),
                React.createElement("div", { className: "adm-table-wrap", style: { border: '1px solid var(--theia-border)', height: 140, overflowY: 'auto' } },
                    React.createElement("table", { className: "adm-table", style: { fontSize: 10 } },
                        React.createElement("thead", null,
                            React.createElement("tr", null,
                                React.createElement("th", null, "Day"),
                                React.createElement("th", null, "Quotes Session"),
                                React.createElement("th", null, "Trade Session"))),
                        React.createElement("tbody", null, DAYS.map(day => {
                            const sched = schedules[day] || { quotes: [], trade: [], separateTrade: false };
                            const quotesStr = sched.quotes.map(q => `${q.start}-${q.end}`).join(', ') || 'No session';
                            const tradeStr = sched.separateTrade
                                ? (sched.trade.map(t => `${t.start}-${t.end}`).join(', ') || 'No session')
                                : 'Same as Quotes';
                            return (React.createElement("tr", { key: day, className: selectedDay === day ? 'selected' : '', onClick: () => setSelectedDay(day), onDoubleClick: () => setSelectedDay(day), style: { cursor: 'pointer', height: 18 } },
                                React.createElement("td", null,
                                    React.createElement("strong", null, day.substring(0, 3))),
                                React.createElement("td", null, quotesStr),
                                React.createElement("td", null, tradeStr)));
                        }))))),
            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 6 } },
                React.createElement("div", { style: { fontWeight: 'bold', fontSize: 10, borderBottom: '1px solid var(--theia-border)', paddingBottom: 2, marginBottom: 2 } }, "Contract Expirations"),
                React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, cursor: 'pointer', height: 20 } },
                    React.createElement("input", { type: "checkbox", checked: useLimits, onChange: e => setUseLimits(e.target.checked) }),
                    "Limit active date interval"),
                useLimits && (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 6 } },
                    React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                        React.createElement("span", { style: { width: 50, opacity: 0.8 } }, "From:"),
                        React.createElement("input", { className: "adm-input", type: "date", style: { flex: 1, height: 20, padding: '2px 4px', fontSize: 11 }, value: limitFrom, onChange: e => setLimitFrom(e.target.value) })),
                    React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 8 } },
                        React.createElement("span", { style: { width: 50, opacity: 0.8 } }, "To:"),
                        React.createElement("input", { className: "adm-input", type: "date", style: { flex: 1, height: 20, padding: '2px 4px', fontSize: 11 }, value: limitTo, onChange: e => setLimitTo(e.target.value) })))))),
        selectedDay && (React.createElement(DayScheduleEditor_1.DayScheduleEditor, { day: selectedDay, schedule: schedules[selectedDay], onClose: () => setSelectedDay(null), onSave: (sched) => handleSaveDaySchedule(selectedDay, sched) }))));
}
exports.SessionsTab = SessionsTab;
//# sourceMappingURL=SessionsTab.js.map