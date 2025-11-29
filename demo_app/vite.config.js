import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
    plugins: [react()],
    root: '.', // Serve from root to access src/
    server: {
        port: 3000,
        proxy: {
            '/api': 'http://localhost:5001', // Proxy API calls to Backend
            '/ws': {
                target: 'ws://localhost:5001',
                ws: true
            }
        }
    },
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
        },
    },
});
