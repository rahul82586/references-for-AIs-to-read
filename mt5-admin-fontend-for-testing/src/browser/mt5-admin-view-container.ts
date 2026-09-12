// @ts-nocheck
import { injectable, inject } from '@theia/core/shared/inversify';
import {
    codicon,
    ViewContainer,
    ViewContainerTitleOptions,
    WidgetFactory,
    WidgetManager
} from '@theia/core/lib/browser';
import { MT5_ADMIN_TREE_WIDGET_ID } from './mt5-admin-tree-widget';

export const MT5_ADMIN_CONTAINER_ID = 'mt5-admin-view-container';
export const MT5_ADMIN_CONTAINER_TITLE_OPTIONS: ViewContainerTitleOptions = {
    label: 'MT5 Admin',
    iconClass: codicon('server'),
    closeable: true
};

@injectable()
export class Mt5AdminViewContainerFactory implements WidgetFactory {

    static ID = MT5_ADMIN_CONTAINER_ID;
    readonly id = Mt5AdminViewContainerFactory.ID;

    @inject(ViewContainer.Factory)
    protected readonly viewContainerFactory: ViewContainer.Factory;

    @inject(WidgetManager)
    protected readonly widgetManager: WidgetManager;

    async createWidget(): Promise<ViewContainer> {
        const viewContainer = this.viewContainerFactory({
            id: MT5_ADMIN_CONTAINER_ID,
            progressLocationId: 'mt5-admin'
        });

        viewContainer.addClass('mt5-admin-view-container');
        viewContainer.setTitleOptions(MT5_ADMIN_CONTAINER_TITLE_OPTIONS);

        // Add the tree widget as the single sub-view
        const treeWidget = await this.widgetManager.getOrCreateWidget(MT5_ADMIN_TREE_WIDGET_ID);
        viewContainer.addWidget(treeWidget, {
            order: 0,
            canHide: false,
            initiallyCollapsed: false,
            weight: 100
        });

        return viewContainer;
    }
}
