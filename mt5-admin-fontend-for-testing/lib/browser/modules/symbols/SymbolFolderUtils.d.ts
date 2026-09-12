/**
 * Pure helper utilities for validation and segmentation of MT5 symbol folder paths and names.
 */
/**
 * Validates a folder or group name based on MT5 rules.
 * Allowed characters: letters, digits, '.', '_', '&', '#'.
 * Blocked characters: < > : " / | ? * and comma.
 */
export declare function validateFolderName(name: string): string | null;
/**
 * Validates a symbol name.
 * Rules: No leading/trailing spaces, must not contain invalid characters.
 */
export declare function validateSymbolName(name: string, existingSymbols: string[]): string | null;
/**
 * Splits a full symbol path (e.g. "Forex\\Majors\\EURUSD") into folder segments.
 */
export declare function splitSymbolPath(fullPath: string): string[];
/**
 * Extracts highest order group/type from a symbol path name (e.g. "Forex\\Majors\\EURUSD" -> "Forex").
 */
export declare function getHighestOrderGroup(fullPath: string): string;
//# sourceMappingURL=SymbolFolderUtils.d.ts.map