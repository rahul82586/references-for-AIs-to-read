"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Mt5AdminTreeWidget = exports.MT5_ADMIN_TREE_WIDGET_ID = void 0;
const tslib_1 = require("tslib");
// @ts-nocheck
const React = require("react");
const inversify_1 = require("@theia/core/shared/inversify");
const browser_1 = require("@theia/core/lib/browser");
const command_1 = require("@theia/core/lib/common/command");
const mt5_admin_tree_1 = require("../common/mt5-admin-tree");
const api_1 = require("./modules/api");
exports.MT5_ADMIN_TREE_WIDGET_ID = 'mt5-admin-tree-widget';
let Mt5AdminTreeWidget = class Mt5AdminTreeWidget extends browser_1.ReactWidget {
    constructor() {
        super(...arguments);
        this.expandedNodes = new Set();
        this.groupsList = [];
    }
    init() {
        this.id = exports.MT5_ADMIN_TREE_WIDGET_ID;
        this.title.label = 'MT5 Admin';
        this.title.caption = 'MT5 Administrator';
        this.title.closable = false;
        this.title.iconClass = 'codicon codicon-server';
        this.addClass('mt5-admin-tree-widget');
        this.node.tabIndex = 0;
        // Expand top-level sections by default
        this.expandedNodes.add('groups');
        this.expandedNodes.add('clients-and-accounts');
        this.expandedNodes.add('routing');
        this.expandedNodes.add('symbols');
        this.refreshTree();
        this.update();
    }
    async refreshTree() {
        try {
            const data = await api_1.API.getGroups();
            this.groupsList = data;
            this.update();
        }
        catch (e) {
            console.error('Failed to load groups list for sidebar tree:', e);
        }
    }
    toggleNode(id) {
        if (this.expandedNodes.has(id)) {
            this.expandedNodes.delete(id);
        }
        else {
            this.expandedNodes.add(id);
        }
        this.update();
    }
    selectNode(node) {
        this.selectedNodeId = node.id;
        this.update();
        if (node.id.startsWith('groups:')) {
            // Open the master Groups page and pass the selected path
            this.commandService.executeCommand('mt5-admin:open-view', node.id, 'Groups');
        }
        else {
            this.commandService.executeCommand('mt5-admin:open-view', node.id, node.label);
        }
    }
    buildGroupsSubtree() {
        const root = [];
        const findOrCreateNode = (parentList, name, fullPath, isLeaf) => {
            const id = `groups:${fullPath}`;
            let existing = parentList.find(n => n.id === id);
            if (!existing) {
                existing = {
                    id,
                    label: name,
                    icon: isLeaf ? 'folder' : 'folder-active',
                    children: []
                };
                parentList.push(existing);
            }
            return existing;
        };
        for (const g of this.groupsList) {
            const parts = g.name.split('\\').map(p => p.trim()).filter(Boolean);
            let currentLevel = root;
            let pathAccum = '';
            for (let i = 0; i < parts.length; i++) {
                const part = parts[i];
                pathAccum = pathAccum ? `${pathAccum}\\${part}` : part;
                const isLeaf = i === parts.length - 1;
                const node = findOrCreateNode(currentLevel, part, pathAccum, isLeaf);
                currentLevel = node.children;
            }
        }
        const cleanChildren = (list) => {
            for (const n of list) {
                if (n.children && n.children.length === 0) {
                    delete n.children;
                }
                else if (n.children) {
                    cleanChildren(n.children);
                }
            }
        };
        cleanChildren(root);
        return root;
    }
    renderNode(node, depth = 0) {
        // Dynamically compute child items for the groups parent node
        if (node.id === 'groups') {
            node.children = this.buildGroupsSubtree();
        }
        const hasChildren = node.children && node.children.length > 0;
        const isExpanded = this.expandedNodes.has(node.id);
        const isSelected = this.selectedNodeId === node.id;
        const indent = depth * 16;
        return (React.createElement(React.Fragment, { key: node.id },
            React.createElement("div", { className: `mt5-admin-tree-row${isSelected ? ' selected' : ''}`, style: { paddingLeft: `${8 + indent}px` }, onClick: () => {
                    if (hasChildren) {
                        this.toggleNode(node.id);
                    }
                    else {
                        this.selectNode(node);
                    }
                }, onDoubleClick: () => {
                    this.selectNode(node);
                }, title: node.label },
                React.createElement("span", { className: `mt5-admin-tree-arrow${hasChildren ? ' visible' : ''}` }, hasChildren
                    ? (isExpanded
                        ? React.createElement("i", { className: "codicon codicon-chevron-down" })
                        : React.createElement("i", { className: "codicon codicon-chevron-right" }))
                    : React.createElement("span", { style: { display: 'inline-block', width: '16px' } })),
                node.icon && (React.createElement("i", { className: `codicon codicon-${node.icon} mt5-admin-tree-icon` })),
                React.createElement("span", { className: "mt5-admin-tree-label" }, node.label)),
            hasChildren && isExpanded && (React.createElement("div", { className: "mt5-admin-tree-children" }, node.children.map(child => this.renderNode(child, depth + 1))))));
    }
    render() {
        return (React.createElement("div", { className: "mt5-admin-tree-container" },
            React.createElement("div", { className: "mt5-admin-tree-header" },
                React.createElement("span", { className: "mt5-admin-tree-header-label" }, "ADMINISTRATOR"),
                React.createElement("button", { className: "adm-icon-btn", style: { marginLeft: 'auto', marginRight: 8 }, onClick: () => this.refreshTree(), title: "Refresh sidebar tree" },
                    React.createElement("i", { className: "codicon codicon-refresh" }))),
            React.createElement("div", { className: "mt5-admin-tree-body" }, mt5_admin_tree_1.MT5_ADMIN_TREE.map(node => this.renderNode(node, 0)))));
    }
};
exports.Mt5AdminTreeWidget = Mt5AdminTreeWidget;
tslib_1.__decorate([
    (0, inversify_1.inject)(command_1.CommandService),
    tslib_1.__metadata("design:type", Object)
], Mt5AdminTreeWidget.prototype, "commandService", void 0);
tslib_1.__decorate([
    (0, inversify_1.postConstruct)(),
    tslib_1.__metadata("design:type", Function),
    tslib_1.__metadata("design:paramtypes", []),
    tslib_1.__metadata("design:returntype", void 0)
], Mt5AdminTreeWidget.prototype, "init", null);
exports.Mt5AdminTreeWidget = Mt5AdminTreeWidget = tslib_1.__decorate([
    (0, inversify_1.injectable)()
], Mt5AdminTreeWidget);
//# sourceMappingURL=mt5-admin-tree-widget.js.map