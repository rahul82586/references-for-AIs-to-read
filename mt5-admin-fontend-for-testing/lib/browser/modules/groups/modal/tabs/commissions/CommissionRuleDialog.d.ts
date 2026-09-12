import * as React from 'react';
import { CommissionRule } from '../../GroupDraftContext';
interface CommissionRuleDialogProps {
    rule: CommissionRule | null;
    onClose: () => void;
    onSave: (rule: CommissionRule) => void;
}
export declare function CommissionRuleDialog({ rule, onClose, onSave }: CommissionRuleDialogProps): React.ReactElement;
export {};
//# sourceMappingURL=CommissionRuleDialog.d.ts.map