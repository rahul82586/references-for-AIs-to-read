"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Mt5AdminContribution = exports.Mt5AdminCommands = void 0;
const tslib_1 = require("tslib");
// @ts-nocheck
const inversify_1 = require("@theia/core/shared/inversify");
const view_contribution_1 = require("@theia/core/lib/browser/shell/view-contribution");
const mt5_admin_tree_widget_1 = require("./mt5-admin-tree-widget");
const browser_1 = require("@theia/core/lib/browser");
const mt5_admin_view_container_1 = require("./mt5-admin-view-container");
const mt5_admin_content_widget_1 = require("./mt5-admin-content-widget");
var Mt5AdminCommands;
(function (Mt5AdminCommands) {
    Mt5AdminCommands.OPEN_ADMIN = {
        id: 'mt5-admin:open',
        label: 'MT5 Administrator'
    };
    Mt5AdminCommands.OPEN_VIEW = {
        id: 'mt5-admin:open-view',
        label: 'MT5 Admin: Open Section'
    };
})(Mt5AdminCommands || (exports.Mt5AdminCommands = Mt5AdminCommands = {}));
let Mt5AdminContribution = class Mt5AdminContribution extends view_contribution_1.AbstractViewContribution {
    constructor() {
        super({
            viewContainerId: mt5_admin_view_container_1.MT5_ADMIN_CONTAINER_ID,
            widgetId: mt5_admin_tree_widget_1.MT5_ADMIN_TREE_WIDGET_ID,
            widgetName: 'MT5 Admin',
            defaultWidgetOptions: {
                area: 'left',
                rank: 600
            },
            toggleCommandId: 'mt5-admin:toggle',
            toggleKeybinding: 'ctrlcmd+shift+a'
        });
    }
    async initializeLayout(app) {
        await this.shell.revealWidget(mt5_admin_view_container_1.MT5_ADMIN_CONTAINER_ID);
    }
    registerCommands(commands) {
        super.registerCommands(commands);
        commands.registerCommand(Mt5AdminCommands.OPEN_ADMIN, {
            execute: () => this.shell.revealWidget(mt5_admin_view_container_1.MT5_ADMIN_CONTAINER_ID)
        });
        // Called by the tree widget when user clicks a node
        commands.registerCommand(Mt5AdminCommands.OPEN_VIEW, {
            execute: async (nodeId, nodeLabel) => {
                let targetNodeId = nodeId;
                let filterPath = '';
                if (nodeId.startsWith('groups:')) {
                    targetNodeId = 'groups';
                    filterPath = nodeId.substring(7);
                }
                else if (nodeId.startsWith('symbols:')) {
                    targetNodeId = 'symbols';
                    filterPath = nodeId.substring(8);
                }
                const widgetId = mt5_admin_content_widget_1.Mt5AdminContentWidget.createId(targetNodeId);
                // Check if already open
                const existing = this.shell.getWidgetById(widgetId);
                if (existing) {
                    this.shell.activateWidget(widgetId);
                    if (targetNodeId === 'groups' || targetNodeId === 'symbols') {
                        existing.setFilterPath(filterPath);
                    }
                    return;
                }
                // Create a fresh content widget for this section
                const widget = new mt5_admin_content_widget_1.Mt5AdminContentWidget();
                widget.initialize(targetNodeId, targetNodeId === 'groups' ? 'Groups' : targetNodeId === 'symbols' ? 'Symbols' : nodeLabel);
                if (targetNodeId === 'groups' || targetNodeId === 'symbols') {
                    widget.setFilterPath(filterPath);
                }
                this.shell.addWidget(widget, {
                    area: 'main',
                    mode: 'tab-after'
                });
                this.shell.activateWidget(widgetId);
            }
        });
    }
    registerMenus(menus) {
        super.registerMenus(menus);
    }
};
exports.Mt5AdminContribution = Mt5AdminContribution;
tslib_1.__decorate([
    (0, inversify_1.inject)(browser_1.WidgetManager),
    tslib_1.__metadata("design:type", browser_1.WidgetManager)
], Mt5AdminContribution.prototype, "widgetManager", void 0);
tslib_1.__decorate([
    (0, inversify_1.inject)(browser_1.ApplicationShell),
    tslib_1.__metadata("design:type", browser_1.ApplicationShell)
], Mt5AdminContribution.prototype, "shell", void 0);
exports.Mt5AdminContribution = Mt5AdminContribution = tslib_1.__decorate([
    (0, inversify_1.injectable)(),
    tslib_1.__metadata("design:paramtypes", [])
], Mt5AdminContribution);
//# sourceMappingURL=mt5-admin-contribution.js.map