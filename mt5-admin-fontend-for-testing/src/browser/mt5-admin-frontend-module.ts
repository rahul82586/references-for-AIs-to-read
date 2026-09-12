// @ts-nocheck
import { ContainerModule } from '@theia/core/shared/inversify';
import { Mt5AdminTreeWidget, MT5_ADMIN_TREE_WIDGET_ID } from './mt5-admin-tree-widget';
import { Mt5AdminContribution } from './mt5-admin-contribution';
import { Mt5AdminViewContainerFactory } from './mt5-admin-view-container';
import {
    bindViewContribution,
    FrontendApplicationContribution,
    WidgetFactory
} from '@theia/core/lib/browser';
import './style/index.css';

export default new ContainerModule(bind => {
    // Register the sidebar contribution (activity bar panel + commands)
    bindViewContribution(bind, Mt5AdminContribution);
    bind(FrontendApplicationContribution).toDynamicValue(
        ctx => ctx.container.get(Mt5AdminContribution)
    );

    // Register the tree widget
    bind(Mt5AdminTreeWidget).toSelf();
    bind(WidgetFactory).toDynamicValue(ctx => ({
        id: MT5_ADMIN_TREE_WIDGET_ID,
        createWidget: () => ctx.container.getAsync<Mt5AdminTreeWidget>(Mt5AdminTreeWidget)
    }));

    // Register the sidebar ViewContainer
    bind(Mt5AdminViewContainerFactory).toSelf().inSingletonScope();
    bind(WidgetFactory).toService(Mt5AdminViewContainerFactory);
});
