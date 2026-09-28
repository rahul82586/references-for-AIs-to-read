import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Dev proxy: the frontend never hardcodes a backend origin. In dev, `/backend`
// is proxied to the broker platform API (default http://localhost:8000), which
// also removes CORS from the equation. Override with VITE_PROXY_TARGET.
export default defineConfig({
    plugins: [react()],
    server: {
        port: 5173,
        proxy: {
            '/backend': {
                target: process.env.VITE_PROXY_TARGET || 'http://127.0.0.1:8001',
                changeOrigin: true,
                rewrite: (path) => path.replace(/^\/backend/, ''),
            },
        },
    },
    build: {
        outDir: 'dist',
        sourcemap: true,
    },
});
