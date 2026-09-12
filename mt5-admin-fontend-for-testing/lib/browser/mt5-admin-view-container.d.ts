import { ViewContainer, ViewContainerTitleOptions, WidgetFactory, WidgetManager } from '@theia/core/lib/browser';
export declare const MT5_ADMIN_CONTAINER_ID = "mt5-admin-view-container";
export declare const MT5_ADMIN_CONTAINER_TITLE_OPTIONS: ViewContainerTitleOptions;
export declare class Mt5AdminViewContainerFactory implements WidgetFactory {
    static ID: string;
    readonly id: string;
    protected readonly viewContainerFactory: ViewContainer.Factory;
    protected readonly widgetManager: WidgetManager;
    createWidget(): Promise<ViewContainer>;
}
//# sourceMappingURL=mt5-admin-view-container.d.ts.map