import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// Browser fallback for diveAPI (when not running in Electron)
if (!window.diveAPI) {
    const GATEWAY_URL = 'http://127.0.0.1:1879';
    
    const makeRequest = async (endpoint: string, data?: any) => {
        try {
            const response = await fetch(`${GATEWAY_URL}${endpoint}`, {
                method: data ? 'POST' : 'GET',
                headers: { 'Content-Type': 'application/json' },
                body: data ? JSON.stringify(data) : undefined
            });
            return await response.json();
        } catch (error) {
            return { error: String(error) };
        }
    };
    
    (window as any).diveAPI = {
        gateway: {
            request: makeRequest,
            chat: (message: string, options = {}) => makeRequest('/chat', { message, ...options }),
            health: () => makeRequest('/health'),
            models: () => makeRequest('/models')
        },
        automation: {
            screenshot: () => makeRequest('/automation/screenshot'),
            click: (x: number, y: number) => makeRequest('/automation/execute', { action: 'click', params: { x, y } }),
            type: (text: string) => makeRequest('/automation/execute', { action: 'type', params: { text } }),
            execute: (action: string, params: any) => makeRequest('/automation/execute', { action, params })
        },
        terminal: {
            execute: (command: string, cwd?: string) => makeRequest('/terminal/execute', { command, cwd })
        },
        fs: {
            read: (path: string) => makeRequest('/fs/read', { path }),
            write: (path: string, content: string) => makeRequest('/fs/write', { path, content }),
            readFile: (path: string) => makeRequest('/fs/read', { path }),
            writeFile: (path: string, content: string) => makeRequest('/fs/write', { path, content })
        }
    };
    
    console.log('🌐 Dive AI: Browser mode (using direct API calls to gateway)');
}

ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
        <App />
    </React.StrictMode>
);
