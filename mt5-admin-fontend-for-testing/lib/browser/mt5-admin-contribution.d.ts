import { AbstractViewContribution } from '@theia/core/lib/browser/shell/view-contribution';
import { Mt5AdminTreeWidget } from './mt5-admin-tree-widget';
import { FrontendApplicationContribution, FrontendApplication, WidgetManager, ApplicationShell } from '@theia/core/lib/browser';
import { CommandRegistry, Command } from '@theia/core/lib/common/command';
import { MenuModelRegistry } from '@theia/core/lib/common';
export declare namespace Mt5AdminCommands {
    const OPEN_ADMIN: Command;
    const OPEN_VIEW: Command;
}
export declare class Mt5AdminContribution extends AbstractViewContribution<Mt5AdminTreeWidget> implements FrontendApplicationContribution {
    protected readonly widgetManager: WidgetManager;
    protected readonly shell: ApplicationShell;
    constructor();
    initializeLayout(app: FrontendApplication): Promise<void>;
    registerCommands(commands: CommandRegistry): void;
    registerMenus(menus: MenuModelRegistry): void;
}
//# sourceMappingURL=mt5-admin-contribution.d.ts.map