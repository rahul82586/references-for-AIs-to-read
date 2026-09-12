import * as React from 'react';
interface SelectSymbolsStepProps {
    connectData: any;
    selectedSymbols: string[];
    onSelectSymbolsChange: (syms: string[]) => void;
    overwriteExisting: boolean;
    onOverwriteChange: (val: boolean) => void;
}
export declare function SelectSymbolsStep({ connectData, selectedSymbols, onSelectSymbolsChange, overwriteExisting, onOverwriteChange }: SelectSymbolsStepProps): React.ReactElement;
export {};
//# sourceMappingURL=SelectSymbolsStep.d.ts.map