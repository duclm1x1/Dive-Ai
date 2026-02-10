/**
 * 🖥️ DIVE AI DESKTOP - Electron Main Process
 * Multi-Agent Coordinator in a native desktop window
 */

const { app, BrowserWindow, Tray, Menu, nativeImage, ipcMain, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

// Keep references
let mainWindow = null;
let tray = null;
let pythonServer = null;

// Configuration
const CONFIG = {
    serverPort: 8080,
    serverUrl: 'http://localhost:8080',
    windowWidth: 1400,
    windowHeight: 900,
    minWidth: 1000,
    minHeight: 700
};

/**
 * Start Python dashboard server
 */
function startPythonServer() {
    console.log('🐍 Starting Python server...');
    
    const serverPath = path.join(__dirname, '..', 'dashboard_server.py');
    
    pythonServer = spawn('python', [serverPath], {
        cwd: path.join(__dirname, '..'),
        stdio: ['pipe', 'pipe', 'pipe']
    });
    
    pythonServer.stdout.on('data', (data) => {
        console.log(`Server: ${data}`);
    });
    
    pythonServer.stderr.on('data', (data) => {
        console.error(`Server Error: ${data}`);
    });
    
    pythonServer.on('close', (code) => {
        console.log(`Python server exited with code ${code}`);
    });
    
    // Wait for server to start
    return new Promise((resolve) => {
        setTimeout(resolve, 2000);
    });
}

/**
 * Create main window
 */
function createWindow() {
    mainWindow = new BrowserWindow({
        width: CONFIG.windowWidth,
        height: CONFIG.windowHeight,
        minWidth: CONFIG.minWidth,
        minHeight: CONFIG.minHeight,
        title: 'Dive AI - Multi-Agent Coordinator',
        icon: path.join(__dirname, '..', 'assets', 'icon.png'),
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
        backgroundColor: '#0a0a1a',
        show: false,
        frame: true,
        autoHideMenuBar: true
    });
    
    // Load dashboard
    mainWindow.loadURL(CONFIG.serverUrl);
    
    // Show when ready
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
        console.log('✅ Main window ready');
    });
    
    // Handle close
    mainWindow.on('close', (event) => {
        if (tray) {
            event.preventDefault();
            mainWindow.hide();
        }
    });
    
    // Handle external links
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        shell.openExternal(url);
        return { action: 'deny' };
    });
}

/**
 * Create system tray
 */
function createTray() {
    // Create tray icon (placeholder - use actual icon in production)
    const iconPath = path.join(__dirname, '..', 'assets', 'tray-icon.png');
    let trayIcon;
    
    try {
        trayIcon = nativeImage.createFromPath(iconPath);
    } catch {
        // Create fallback icon
        trayIcon = nativeImage.createEmpty();
    }
    
    tray = new Tray(trayIcon.isEmpty() ? nativeImage.createFromDataURL('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAdgAAAHYBTnsmCAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAADASURBVDiN1ZMxCsIwFIa/F0WHgoOrg4uLg4OjYBdB8AQOrt7B2cHB1VM4iAcQHDyBg4OLlxAXp9Ja0qqDf0kI3/fy8hIIgP+EUAK3QLrpmwN3wD0lXb9vIA+0gGfgxXbYBJLAE9ABWrYZpYEnoB0Ao8ARMB4L9IAc0LEdS7YZB6CxkAH6GkEQhVIC90AbuKAU9EPgBbiFZyR1DjzJElARrCWdAO+BT5ZqkuYkzQNtYBm4B2qD2ZuAiqAapIWkJb0BL4Y0Rm3y3DQAAAAASUVORK5CYII=') : trayIcon);
    
    const contextMenu = Menu.buildFromTemplate([
        {
            label: 'Show Dashboard',
            click: () => {
                if (mainWindow) {
                    mainWindow.show();
                    mainWindow.focus();
                }
            }
        },
        {
            label: '512 Agents Online',
            enabled: false
        },
        { type: 'separator' },
        {
            label: 'Status',
            submenu: [
                { label: '🟢 Coordinator: Online', enabled: false },
                { label: '📊 Tasks: 0 running', enabled: false }
            ]
        },
        { type: 'separator' },
        {
            label: 'Quick Actions',
            submenu: [
                {
                    label: '📅 Generate 24h Plan',
                    click: () => sendToRenderer('quick-action', 'generate-plan')
                },
                {
                    label: '🔍 Check Status',
                    click: () => sendToRenderer('quick-action', 'check-status')
                }
            ]
        },
        { type: 'separator' },
        {
            label: 'Quit',
            click: () => {
                tray = null;
                app.quit();
            }
        }
    ]);
    
    tray.setToolTip('Dive AI - Multi-Agent Coordinator');
    tray.setContextMenu(contextMenu);
    
    tray.on('click', () => {
        if (mainWindow) {
            if (mainWindow.isVisible()) {
                mainWindow.hide();
            } else {
                mainWindow.show();
                mainWindow.focus();
            }
        }
    });
    
    console.log('✅ System tray created');
}

/**
 * Send message to renderer
 */
function sendToRenderer(channel, data) {
    if (mainWindow && mainWindow.webContents) {
        mainWindow.webContents.send(channel, data);
    }
}

/**
 * Setup IPC handlers
 */
function setupIPC() {
    ipcMain.handle('get-status', async () => {
        try {
            const response = await fetch(`${CONFIG.serverUrl}/api/status`);
            return await response.json();
        } catch (error) {
            return { error: error.message };
        }
    });
    
    ipcMain.handle('spawn-agents', async () => {
        try {
            const response = await fetch(`${CONFIG.serverUrl}/api/spawn`);
            return await response.json();
        } catch (error) {
            return { error: error.message };
        }
    });
    
    ipcMain.handle('submit-task', async (event, task) => {
        try {
            const response = await fetch(`${CONFIG.serverUrl}/api/task`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ task })
            });
            return await response.json();
        } catch (error) {
            return { error: error.message };
        }
    });
    
    ipcMain.handle('generate-plan', async () => {
        try {
            const response = await fetch(`${CONFIG.serverUrl}/api/plan`);
            return await response.json();
        } catch (error) {
            return { error: error.message };
        }
    });
    
    console.log('✅ IPC handlers registered');
}

/**
 * App lifecycle
 */
app.whenReady().then(async () => {
    console.log('🚀 Dive AI Desktop starting...');
    
    // Start Python server
    await startPythonServer();
    
    // Setup IPC
    setupIPC();
    
    // Create window
    createWindow();
    
    // Create tray
    createTray();
    
    // Handle activate (macOS)
    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('before-quit', () => {
    // Kill Python server
    if (pythonServer) {
        pythonServer.kill();
        console.log('🛑 Python server stopped');
    }
});

// Prevent multiple instances
const gotTheLock = app.requestSingleInstanceLock();

if (!gotTheLock) {
    app.quit();
} else {
    app.on('second-instance', () => {
        if (mainWindow) {
            if (mainWindow.isMinimized()) mainWindow.restore();
            mainWindow.focus();
        }
    });
}

console.log('📦 Dive AI Desktop module loaded');
