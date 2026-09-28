import * as React from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './app/App';

// styles: VS Code tokens first, then the ported adm-* component CSS, then the
// workbench chrome, then dockview's own CSS (imported inside LayoutHost)
import '@vscode/codicons/dist/codicon.css';
import './theme/tokens.css';
import './theme/adm.css';
import './theme/workbench.css';

const container = document.getElementById('root');
if (!container) throw new Error('#root not found');
createRoot(container).render(<App />);
