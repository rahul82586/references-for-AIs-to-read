"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
// @ts-nocheck
const inversify_1 = require("@theia/core/shared/inversify");
const mt5_admin_tree_widget_1 = require("./mt5-admin-tree-widget");
const mt5_admin_contribution_1 = require("./mt5-admin-contribution");
const mt5_admin_view_container_1 = require("./mt5-admin-view-container");
const browser_1 = require("@theia/core/lib/browser");
require("./style/index.css");
exports.default = new inversify_1.ContainerModule(bind => {
    // Register the sidebar contribution (activity bar panel + commands)
    (0, browser_1.bindViewContribution)(bind, mt5_admin_contribution_1.Mt5AdminContribution);
    bind(browser_1.FrontendApplicationContribution).toDynamicValue(ctx => ctx.container.get(mt5_admin_contribution_1.Mt5AdminContribution));
    // Register the tree widget
    bind(mt5_admin_tree_widget_1.Mt5AdminTreeWidget).toSelf();
    bind(browser_1.WidgetFactory).toDynamicValue(ctx => ({
        id: mt5_admin_tree_widget_1.MT5_ADMIN_TREE_WIDGET_ID,
        createWidget: () => ctx.container.getAsync(mt5_admin_tree_widget_1.Mt5AdminTreeWidget)
    }));
    // Register the sidebar ViewContainer
    bind(mt5_admin_view_container_1.Mt5AdminViewContainerFactory).toSelf().inSingletonScope();
    bind(browser_1.WidgetFactory).toService(mt5_admin_view_container_1.Mt5AdminViewContainerFactory);
});
//# sourceMappingURL=mt5-admin-frontend-module.js.map