import { app, BrowserWindow, ipcMain } from 'electron';
import * as path from 'path';

let mainWindow: BrowserWindow | null = null;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        backgroundColor: '#1a1a2e',
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, '../preload/preload.js')
        },
        icon: path.join(__dirname, '../../resources/icon.png'),
        titleBarStyle: 'hiddenInset',
        show: false
    });

    mainWindow.once('ready-to-show', () => {
        mainWindow?.show();
    });

    // Development vs Production
    if (process.env.NODE_ENV === 'development') {
        mainWindow.loadURL('http://localhost:5173');
        mainWindow.webContents.openDevTools();
    } else {
        mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));
    }

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

// Gateway URL
const GATEWAY_URL = 'http://127.0.0.1:1879';

// IPC Handlers
ipcMain.handle('gateway:request', async (_event, endpoint: string, data: any) => {
    const isGet = !data || (typeof data === 'object' && Object.keys(data).length === 0);
    const options: RequestInit = isGet 
        ? { method: 'GET' }
        : {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        };
    const response = await fetch(`${GATEWAY_URL}${endpoint}`, options);
    return response.json();
});

ipcMain.handle('gateway:chat', async (_event, message: string, options?: any) => {
    const response = await fetch(`${GATEWAY_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            message,
            model_id: options?.model_id,
            system: options?.system,
            conversation_id: options?.conversation_id,
        })
    });
    return response.json();
});

ipcMain.handle('gateway:health', async () => {
    try {
        const response = await fetch(`${GATEWAY_URL}/health`);
        return response.json();
    } catch {
        return { status: 'disconnected' };
    }
});

ipcMain.handle('automation:screenshot', async () => {
    const response = await fetch(`${GATEWAY_URL}/automation/screenshot`);
    return response.json();
});

ipcMain.handle('automation:execute', async (_event, action: string, params: any) => {
    const response = await fetch(`${GATEWAY_URL}/automation/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, params })
    });
    return response.json();
});

ipcMain.handle('terminal:execute', async (_event, command: string, cwd: string) => {
    const response = await fetch(`${GATEWAY_URL}/terminal/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command, cwd })
    });
    return response.json();
});

ipcMain.handle('fs:read', async (_event, filePath: string) => {
    const response = await fetch(`${GATEWAY_URL}/fs/read`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: filePath })
    });
    return response.json();
});

ipcMain.handle('fs:write', async (_event, filePath: string, content: string) => {
    const response = await fetch(`${GATEWAY_URL}/fs/write`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: filePath, content })
    });
    return response.json();
});

// App lifecycle
app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});
