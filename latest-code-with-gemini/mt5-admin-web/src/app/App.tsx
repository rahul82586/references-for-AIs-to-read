import * as React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Workbench } from '../shell/workbench/Workbench';
// panel definitions must be registered before the workbench resolves nodes
import '../shell/registry/panels';

const queryClient = new QueryClient({
    defaultOptions: {
        queries: { retry: 1, refetchOnWindowFocus: false, staleTime: 5_000 },
    },
});

export function App(): React.ReactElement {
    return (
        <QueryClientProvider client={queryClient}>
            <Workbench />
        </QueryClientProvider>
    );
}
