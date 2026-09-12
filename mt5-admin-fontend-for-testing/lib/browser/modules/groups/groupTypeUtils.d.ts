/**
 * Pure functions for MT5-Admin Groups module.
 * Single source of truth for group naming and path validations.
 */
export type GroupType = 'Demo' | 'Manager' | 'Contest' | 'Coverage' | 'Preliminary' | 'Real';
export declare function getGroupType(path: string): GroupType;
export declare function validateGroupName(path: string): string | null;
export declare function splitPathIntoSections(path: string): string[];
//# sourceMappingURL=groupTypeUtils.d.ts.map