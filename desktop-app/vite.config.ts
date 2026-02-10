import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
    plugins: [react()],
    root: 'src',
    base: './',  // Important for Electron file:// protocol
    build: {
        outDir: '../dist',
        emptyOutDir: true
    },
    resolve: {
        alias: {
            '@': resolve(__dirname, 'src')
        }
    },
    server: {
        port: 5173,
        host: true
    }
});
