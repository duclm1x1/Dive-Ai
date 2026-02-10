const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('diveAPI', {
    gateway: {
        request: (endpoint, data) => ipcRenderer.invoke('gateway-request', endpoint, data),
        chat: (message, options = {}) => ipcRenderer.invoke('gateway-request', '/chat', { message, ...options }),
        health: () => ipcRenderer.invoke('gateway-request', '/health'),
        models: () => ipcRenderer.invoke('gateway-request', '/models')
    },
    automation: {
        screenshot: () => ipcRenderer.invoke('gateway-request', '/automation/screenshot'),
        click: (x, y) => ipcRenderer.invoke('gateway-request', '/automation/execute', { action: 'click', params: { x, y } }),
        type: (text) => ipcRenderer.invoke('gateway-request', '/automation/execute', { action: 'type', params: { text } }),
        execute: (action, params) => ipcRenderer.invoke('gateway-request', '/automation/execute', { action, params })
    },
    terminal: {
        execute: (command, cwd) => ipcRenderer.invoke('gateway-request', '/terminal/execute', { command, cwd })
    },
    fs: {
        read: (path) => ipcRenderer.invoke('gateway-request', '/fs/read', { path }),
        write: (path, content) => ipcRenderer.invoke('gateway-request', '/fs/write', { path, content }),
        // Aliases for components
        readFile: (path) => ipcRenderer.invoke('gateway-request', '/fs/read', { path }),
        writeFile: (path, content) => ipcRenderer.invoke('gateway-request', '/fs/write', { path, content })
    }
});
