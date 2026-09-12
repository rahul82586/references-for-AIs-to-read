import * as React from 'react';
import { SymbolRule } from '../../GroupDraftContext';
interface SymbolRuleDialogProps {
    rule: SymbolRule | null;
    onClose: () => void;
    onSave: (rule: SymbolRule) => void;
    availableSymbols: string[];
}
export declare function SymbolRuleDialog({ rule, onClose, onSave, availableSymbols }: SymbolRuleDialogProps): React.ReactElement;
export {};
//# sourceMappingURL=SymbolRuleDialog.d.ts.map