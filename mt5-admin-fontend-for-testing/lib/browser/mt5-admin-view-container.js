"use strict";
var Mt5AdminViewContainerFactory_1;
Object.defineProperty(exports, "__esModule", { value: true });
exports.Mt5AdminViewContainerFactory = exports.MT5_ADMIN_CONTAINER_TITLE_OPTIONS = exports.MT5_ADMIN_CONTAINER_ID = void 0;
const tslib_1 = require("tslib");
// @ts-nocheck
const inversify_1 = require("@theia/core/shared/inversify");
const browser_1 = require("@theia/core/lib/browser");
const mt5_admin_tree_widget_1 = require("./mt5-admin-tree-widget");
exports.MT5_ADMIN_CONTAINER_ID = 'mt5-admin-view-container';
exports.MT5_ADMIN_CONTAINER_TITLE_OPTIONS = {
    label: 'MT5 Admin',
    iconClass: (0, browser_1.codicon)('server'),
    closeable: true
};
let Mt5AdminViewContainerFactory = class Mt5AdminViewContainerFactory {
    constructor() {
        this.id = Mt5AdminViewContainerFactory_1.ID;
    }
    static { Mt5AdminViewContainerFactory_1 = this; }
    static { this.ID = exports.MT5_ADMIN_CONTAINER_ID; }
    async createWidget() {
        const viewContainer = this.viewContainerFactory({
            id: exports.MT5_ADMIN_CONTAINER_ID,
            progressLocationId: 'mt5-admin'
        });
        viewContainer.addClass('mt5-admin-view-container');
        viewContainer.setTitleOptions(exports.MT5_ADMIN_CONTAINER_TITLE_OPTIONS);
        // Add the tree widget as the single sub-view
        const treeWidget = await this.widgetManager.getOrCreateWidget(mt5_admin_tree_widget_1.MT5_ADMIN_TREE_WIDGET_ID);
        viewContainer.addWidget(treeWidget, {
            order: 0,
            canHide: false,
            initiallyCollapsed: false,
            weight: 100
        });
        return viewContainer;
    }
};
exports.Mt5AdminViewContainerFactory = Mt5AdminViewContainerFactory;
tslib_1.__decorate([
    (0, inversify_1.inject)(browser_1.ViewContainer.Factory),
    tslib_1.__metadata("design:type", Function)
], Mt5AdminViewContainerFactory.prototype, "viewContainerFactory", void 0);
tslib_1.__decorate([
    (0, inversify_1.inject)(browser_1.WidgetManager),
    tslib_1.__metadata("design:type", browser_1.WidgetManager)
], Mt5AdminViewContainerFactory.prototype, "widgetManager", void 0);
exports.Mt5AdminViewContainerFactory = Mt5AdminViewContainerFactory = Mt5AdminViewContainerFactory_1 = tslib_1.__decorate([
    (0, inversify_1.injectable)()
], Mt5AdminViewContainerFactory);
//# sourceMappingURL=mt5-admin-view-container.js.map