import { defineConfig } from 'electron-vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
    main: {
        build: {
            lib: {
                entry: 'electron/main.ts'
            },
            outDir: 'dist/main'
        }
    },
    preload: {
        build: {
            lib: {
                entry: 'electron/preload.ts'
            },
            outDir: 'dist/preload'
        }
    },
    renderer: {
        build: {
            rollupOptions: {
                input: 'src/index.html'
            },
            outDir: 'dist/renderer'
        },
        plugins: [react()],
        resolve: {
            alias: {
                '@': resolve(__dirname, 'src')
            }
        }
    }
});
