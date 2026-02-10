const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

let mainWindow = null;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1000,
        minHeight: 700,
        title: 'Dive AI',
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.cjs')
        },
        autoHideMenuBar: true,
        backgroundColor: '#1a1a2e'
    });

    // Development mode - load from Vite server
    if (process.env.NODE_ENV === 'development') {
        mainWindow.loadURL('http://localhost:5173');
        mainWindow.webContents.openDevTools();
    } else {
        // Production - load built files
        mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
    }

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (mainWindow === null) {
        createWindow();
    }
});

// IPC handlers for gateway communication
const GATEWAY_URL = process.env.GATEWAY_URL || 'http://127.0.0.1:1879';

ipcMain.handle('gateway-request', async (event, endpoint, data) => {
    try {
        const response = await fetch(`${GATEWAY_URL}${endpoint}`, {
            method: data ? 'POST' : 'GET',
            headers: { 'Content-Type': 'application/json' },
            body: data ? JSON.stringify(data) : undefined
        });
        return await response.json();
    } catch (error) {
        return { error: error.message };
    }
});
