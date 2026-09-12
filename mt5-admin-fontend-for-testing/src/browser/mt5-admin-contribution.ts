// @ts-nocheck
import { injectable, inject } from '@theia/core/shared/inversify';
import { AbstractViewContribution } from '@theia/core/lib/browser/shell/view-contribution';
import { Mt5AdminTreeWidget, MT5_ADMIN_TREE_WIDGET_ID } from './mt5-admin-tree-widget';
import {
    FrontendApplicationContribution,
    FrontendApplication,
    WidgetManager,
    ApplicationShell
} from '@theia/core/lib/browser';
import { CommandRegistry, Command } from '@theia/core/lib/common/command';
import { MenuModelRegistry } from '@theia/core/lib/common';
import { MT5_ADMIN_CONTAINER_ID } from './mt5-admin-view-container';
import { Mt5AdminContentWidget } from './mt5-admin-content-widget';

export namespace Mt5AdminCommands {
    export const OPEN_ADMIN: Command = {
        id: 'mt5-admin:open',
        label: 'MT5 Administrator'
    };

    export const OPEN_VIEW: Command = {
        id: 'mt5-admin:open-view',
        label: 'MT5 Admin: Open Section'
    };
}

@injectable()
export class Mt5AdminContribution
    extends AbstractViewContribution<Mt5AdminTreeWidget>
    implements FrontendApplicationContribution {

    @inject(WidgetManager)
    protected readonly widgetManager: WidgetManager;

    @inject(ApplicationShell)
    protected readonly shell: ApplicationShell;

    constructor() {
        super({
            viewContainerId: MT5_ADMIN_CONTAINER_ID,
            widgetId: MT5_ADMIN_TREE_WIDGET_ID,
            widgetName: 'MT5 Admin',
            defaultWidgetOptions: {
                area: 'left',
                rank: 600
            },
            toggleCommandId: 'mt5-admin:toggle',
            toggleKeybinding: 'ctrlcmd+shift+a'
        });
    }

    async initializeLayout(app: FrontendApplication): Promise<void> {
        await this.shell.revealWidget(MT5_ADMIN_CONTAINER_ID);
    }

    override registerCommands(commands: CommandRegistry): void {
        super.registerCommands(commands);

        commands.registerCommand(Mt5AdminCommands.OPEN_ADMIN, {
            execute: () => this.shell.revealWidget(MT5_ADMIN_CONTAINER_ID)
        });

        // Called by the tree widget when user clicks a node
        commands.registerCommand(Mt5AdminCommands.OPEN_VIEW, {
            execute: async (nodeId: string, nodeLabel: string) => {
                let targetNodeId = nodeId;
                let filterPath = '';
                if (nodeId.startsWith('groups:')) {
                    targetNodeId = 'groups';
                    filterPath = nodeId.substring(7);
                } else if (nodeId.startsWith('symbols:')) {
                    targetNodeId = 'symbols';
                    filterPath = nodeId.substring(8);
                }

                const widgetId = Mt5AdminContentWidget.createId(targetNodeId);

                // Check if already open
                const existing = this.shell.getWidgetById(widgetId) as Mt5AdminContentWidget;
                if (existing) {
                    this.shell.activateWidget(widgetId);
                    if (targetNodeId === 'groups' || targetNodeId === 'symbols') {
                        existing.setFilterPath(filterPath);
                    }
                    return;
                }

                // Create a fresh content widget for this section
                const widget = new Mt5AdminContentWidget();
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

    override registerMenus(menus: MenuModelRegistry): void {
        super.registerMenus(menus);
    }
}
