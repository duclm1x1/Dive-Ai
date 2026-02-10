import { contextBridge, ipcRenderer } from 'electron';

// Type definitions
interface DiveAPI {
    gateway: {
        request: (endpoint: string, data?: any) => Promise<any>;
        chat: (message: string, options?: { system?: string; model_id?: string; conversation_id?: string }) => Promise<any>;
        health: () => Promise<any>;
    };
    automation: {
        screenshot: () => Promise<any>;
        execute: (action: string, params?: any) => Promise<any>;
    };
    terminal: {
        execute: (command: string, cwd?: string) => Promise<any>;
    };
    fs: {
        readFile: (path: string) => Promise<any>;
        writeFile: (path: string, content: string) => Promise<any>;
    };
}

const api: DiveAPI = {
    gateway: {
        request: (endpoint: string, data?: any) =>
            ipcRenderer.invoke('gateway:request', endpoint, data),
        chat: (message: string, options?: { system?: string; model_id?: string; conversation_id?: string }) =>
            ipcRenderer.invoke('gateway:chat', message, options),
        health: () =>
            ipcRenderer.invoke('gateway:health')
    },
    automation: {
        screenshot: () =>
            ipcRenderer.invoke('automation:screenshot'),
        execute: (action: string, params?: any) =>
            ipcRenderer.invoke('automation:execute', action, params)
    },
    terminal: {
        execute: (command: string, cwd: string = '.') =>
            ipcRenderer.invoke('terminal:execute', command, cwd)
    },
    fs: {
        readFile: (path: string) =>
            ipcRenderer.invoke('fs:read', path),
        writeFile: (path: string, content: string) =>
            ipcRenderer.invoke('fs:write', path, content)
    }
};

// Expose API to renderer
contextBridge.exposeInMainWorld('diveAPI', api);

// Declare global type
declare global {
    interface Window {
        diveAPI: DiveAPI;
    }
}
