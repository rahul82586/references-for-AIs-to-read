/**
 * Pure helper utilities for validation and segmentation of MT5 symbol folder paths and names.
 */

/**
 * Validates a folder or group name based on MT5 rules.
 * Allowed characters: letters, digits, '.', '_', '&', '#'.
 * Blocked characters: < > : " / | ? * and comma.
 */
export function validateFolderName(name: string): string | null {
    if (!name || !name.trim()) {
        return 'Folder name cannot be empty.';
    }
    // Check if it contains invalid characters
    const invalidRegex = /[<>:"/\\|?*,]/;
    if (invalidRegex.test(name)) {
        return 'Folder name cannot contain special characters like <, >, :, ", /, \\, |, ?, * or comma.';
    }
    // Ensure only letters, digits, dot, underscore, ampersand, and hash are used
    const allowedRegex = /^[a-zA-Z0-9._&#\s-]+$/;
    if (!allowedRegex.test(name)) {
        return 'Folder name contains invalid characters. Only letters, numbers, spaces, and . _ & # - are allowed.';
    }
    return null;
}

/**
 * Validates a symbol name.
 * Rules: No leading/trailing spaces, must not contain invalid characters.
 */
export function validateSymbolName(name: string, existingSymbols: string[]): string | null {
    const trimmed = name.trim();
    if (!trimmed) {
        return 'Symbol name cannot be empty.';
    }
    if (name !== trimmed) {
        return 'Symbol name cannot contain leading or trailing whitespace.';
    }
    const invalidRegex = /[<>:"/\\|?*,]/;
    if (invalidRegex.test(trimmed)) {
        return 'Symbol name cannot contain special characters like <, >, :, ", /, \\, |, ?, * or comma.';
    }
    const allowedRegex = /^[a-zA-Z0-9._&#-]+$/;
    if (!allowedRegex.test(trimmed)) {
        return 'Symbol name can only contain alphanumeric characters and . _ & # -';
    }
    // Case insensitivity checks to prevent Apple vs APPLE duplicate issues
    const matchCaseInsensitive = existingSymbols.some(
        s => s.toLowerCase() === trimmed.toLowerCase()
    );
    if (matchCaseInsensitive) {
        return `A symbol with the name "${trimmed}" (or a case-variant like "${trimmed.toUpperCase()}") already exists.`;
    }
    return null;
}

/**
 * Splits a full symbol path (e.g. "Forex\\Majors\\EURUSD") into folder segments.
 */
export function splitSymbolPath(fullPath: string): string[] {
    return fullPath.split('\\').map(p => p.trim()).filter(Boolean);
}

/**
 * Extracts highest order group/type from a symbol path name (e.g. "Forex\\Majors\\EURUSD" -> "Forex").
 */
export function getHighestOrderGroup(fullPath: string): string {
    const parts = splitSymbolPath(fullPath);
    return parts.length > 0 ? parts[0] : '';
}
