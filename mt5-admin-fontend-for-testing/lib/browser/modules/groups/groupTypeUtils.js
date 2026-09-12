"use strict";
/**
 * Pure functions for MT5-Admin Groups module.
 * Single source of truth for group naming and path validations.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.splitPathIntoSections = exports.validateGroupName = exports.getGroupType = void 0;
function getGroupType(path) {
    if (!path)
        return 'Real';
    if (path.includes('demo')) {
        return 'Demo';
    }
    if (path.includes('manager')) {
        return 'Manager';
    }
    if (path.includes('contest')) {
        return 'Contest';
    }
    if (path.includes('coverage')) {
        return 'Coverage';
    }
    // Get last component of path
    const parts = path.split('\\');
    const leaf = parts[parts.length - 1];
    if (leaf === 'preliminary') {
        return 'Preliminary';
    }
    return 'Real';
}
exports.getGroupType = getGroupType;
function validateGroupName(path) {
    if (!path)
        return 'Group path cannot be empty.';
    // Check for invalid characters
    if (/[/:*?"<>|]/.test(path)) {
        return 'Group name cannot contain special characters like /, :, *, ?, ", <, >, |';
    }
    const pathLower = path.toLowerCase();
    const matches = [];
    if (pathLower.includes('demo'))
        matches.push('demo');
    if (pathLower.includes('manager'))
        matches.push('manager');
    if (pathLower.includes('contest'))
        matches.push('contest');
    if (pathLower.includes('coverage'))
        matches.push('coverage');
    if (pathLower.includes('preliminary'))
        matches.push('preliminary');
    if (matches.length > 1) {
        return `Warning: Group name mixes multiple type keywords (${matches.join(', ')}). This might cause unexpected type matching.`;
    }
    return null;
}
exports.validateGroupName = validateGroupName;
function splitPathIntoSections(path) {
    if (!path)
        return [];
    return path.split('\\').map(p => p.trim()).filter(Boolean);
}
exports.splitPathIntoSections = splitPathIntoSections;
//# sourceMappingURL=groupTypeUtils.js.map