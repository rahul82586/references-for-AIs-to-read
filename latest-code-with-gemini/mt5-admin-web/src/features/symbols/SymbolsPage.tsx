import * as React from 'react';
import { SymbolsTreePage } from './SymbolsTreePage';
import { AllSymbolsPage } from './AllSymbolsPage';

interface SymbolsPageProps {
    selectedPath?: string;
}

export function SymbolsPage({ selectedPath = '' }: SymbolsPageProps): React.ReactElement {
    const [activeTab, setActiveTab] = React.useState<'hierarchy' | 'flat'>('hierarchy');

    return (
        <div className="adm-page" style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
            {/* Top switcher tabs */}
            <div className="adm-tabs" style={{ padding: '0 16px', background: 'var(--theia-editor-background)', borderBottom: '1px solid var(--theia-border)', flexShrink: 0 }}>
                <button 
                    type="button" 
                    className={`adm-tab ${activeTab === 'hierarchy' ? 'active' : ''}`}
                    onClick={() => setActiveTab('hierarchy')}
                >
                    <i className="codicon codicon-list-tree" style={{ marginRight: 6 }} />
                    Symbols
                </button>
                <button 
                    type="button" 
                    className={`adm-tab ${activeTab === 'flat' ? 'active' : ''}`}
                    onClick={() => setActiveTab('flat')}
                >
                    <i className="codicon codicon-search" style={{ marginRight: 6 }} />
                    All Symbols
                </button>
            </div>

            {/* Sub-pages */}
            <div style={{ flex: 1, minHeight: 0, overflow: 'hidden' }}>
                {activeTab === 'hierarchy' ? (
                    <SymbolsTreePage selectedPath={selectedPath} />
                ) : (
                    <AllSymbolsPage />
                )}
            </div>
        </div>
    );
}
