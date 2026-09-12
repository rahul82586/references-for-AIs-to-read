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
export declare function DayScheduleEditor({ day, schedule, onClose, onSave }: DayScheduleEditorProps): React.ReactElement;
export {};
//# sourceMappingURL=DayScheduleEditor.d.ts.map