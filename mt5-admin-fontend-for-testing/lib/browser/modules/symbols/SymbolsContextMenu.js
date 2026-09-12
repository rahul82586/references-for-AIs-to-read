"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SymbolsContextMenu = void 0;
const React = require("react");
function SymbolsContextMenu({ menu, isSingleSymbolSelected, onClose, onAddSymbol, onAddFolder, onEdit, onDelete, onSort, onImportServer }) {
    React.useEffect(() => {
        const handleOutsideClick = () => onClose();
        window.addEventListener('click', handleOutsideClick);
        return () => window.removeEventListener('click', handleOutsideClick);
    }, [onClose]);
    const handleAction = (actionFn) => {
        actionFn();
        onClose();
    };
    return (React.createElement("div", { className: "adm-context-menu", style: { top: menu.y, left: menu.x }, onClick: e => e.stopPropagation() },
        React.createElement("button", { type: "button", className: "adm-context-item", onClick: () => handleAction(onAddSymbol) },
            React.createElement("i", { className: "codicon codicon-add" }),
            " Add Symbol"),
        React.createElement("button", { type: "button", className: "adm-context-item", onClick: () => handleAction(onAddFolder) },
            React.createElement("i", { className: "codicon codicon-new-folder" }),
            " Add Folder"),
        React.createElement("button", { type: "button", className: "adm-context-item", disabled: !isSingleSymbolSelected, onClick: () => handleAction(onEdit) },
            React.createElement("i", { className: "codicon codicon-edit" }),
            " Edit settings"),
        React.createElement("button", { type: "button", className: "adm-context-item adm-context-item-danger", onClick: () => handleAction(onDelete) },
            React.createElement("i", { className: "codicon codicon-trash" }),
            " Delete"),
        React.createElement("div", { className: "adm-context-sep" }),
        React.createElement("button", { type: "button", className: "adm-context-item", onClick: () => handleAction(onSort) },
            React.createElement("i", { className: "codicon codicon-symbol-class" }),
            " Sort Alphabetically"),
        React.createElement("button", { type: "button", className: "adm-context-item", onClick: () => handleAction(onImportServer) },
            React.createElement("i", { className: "codicon codicon-cloud-download" }),
            " Import from Server"),
        React.createElement("div", { className: "adm-context-sep" }),
        React.createElement("button", { type: "button", className: "adm-context-item", onClick: () => handleAction(() => alert(`Navigating to journal logs for: ${menu.target}`)) },
            React.createElement("i", { className: "codicon codicon-notebook" }),
            " Journal logs"),
        React.createElement("button", { type: "button", className: "adm-context-item", onClick: () => handleAction(() => alert(`Jumping to 1-minute charts for: ${menu.target}`)) },
            React.createElement("i", { className: "codicon codicon-graph-line" }),
            " Charts"),
        React.createElement("button", { type: "button", className: "adm-context-item", onClick: () => handleAction(() => alert(`Jumping to ticks database for: ${menu.target}`)) },
            React.createElement("i", { className: "codicon codicon-history" }),
            " Tick history")));
}
exports.SymbolsContextMenu = SymbolsContextMenu;
//# sourceMappingURL=SymbolsContextMenu.js.map