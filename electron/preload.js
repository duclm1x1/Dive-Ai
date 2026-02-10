/**
 * 🔒 Preload Script
 * Exposes safe APIs to renderer process
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose protected APIs to renderer
contextBridge.exposeInMainWorld('diveAI', {
    // Status
    getStatus: () => ipcRenderer.invoke('get-status'),
    
    // Agents
    spawnAgents: () => ipcRenderer.invoke('spawn-agents'),
    
    // Tasks
    submitTask: (task) => ipcRenderer.invoke('submit-task', task),
    
    // Plan
    generatePlan: () => ipcRenderer.invoke('generate-plan'),
    
    // Listen for quick actions
    onQuickAction: (callback) => {
        ipcRenderer.on('quick-action', (event, action) => callback(action));
    },
    
    // Platform info
    platform: process.platform,
    version: '1.0.0'
});

console.log('✅ Dive AI preload script loaded');
