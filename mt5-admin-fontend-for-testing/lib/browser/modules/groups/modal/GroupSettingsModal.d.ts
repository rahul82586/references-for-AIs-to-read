import * as React from 'react';
interface GroupSettingsModalProps {
    groupName: string | null;
    initialName?: string;
    onClose: () => void;
    onSaved: () => void;
}
export declare function GroupSettingsModal({ groupName, initialName, onClose, onSaved }: GroupSettingsModalProps): React.ReactElement;
export {};
//# sourceMappingURL=GroupSettingsModal.d.ts.map