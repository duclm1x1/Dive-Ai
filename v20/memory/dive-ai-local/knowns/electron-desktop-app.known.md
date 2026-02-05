---
title: "Electron Desktop App Architecture"
category: "Desktop Development"
tags: ["electron", "desktop", "architecture", "beacon"]
created: "2026-02-03"
---

# Electron Desktop App Architecture

## Purpose

Build a cross-platform desktop application for Dive AI Local that:
1. Runs the web dashboard locally
2. Provides system tray integration
3. Acts as a storage beacon for remote Dive AI instances
4. Auto-starts on boot (optional)

## Technology Stack

### Electron
- **Version**: Latest stable (Electron 28+)
- **Process Architecture**: Main process + Renderer process
- **IPC**: electron-ipc for communication between processes

### Integration Points
- **Web App**: Embed existing React dashboard
- **Backend**: Run Express server in main process
- **Database**: SQLite + ChromaDB in user data directory

## Architecture Design

### 1. Main Process (Node.js)

Responsibilities:
- Create and manage browser windows
- Run Express server
- Handle system tray
- Manage application lifecycle
- File system operations
- Auto-updater

```
main.js
├── createWindow() - Create browser window
├── startServer() - Start Express + tRPC server
├── createTray() - System tray icon
├── handleDeepLinks() - Handle dive:// protocol
└── autoUpdater() - Check for updates
```

### 2. Renderer Process (Browser)

Responsibilities:
- Display React dashboard UI
- Handle user interactions
- Communicate with main process via IPC

```
renderer/
├── index.html - Entry point
├── preload.js - Secure IPC bridge
└── React App - Existing dashboard
```

### 3. System Tray

Features:
- Show/hide window
- Quick actions (new project, sync status)
- Quit application

### 4. Storage Beacon

HTTP server that allows remote access:
- GET /api/memory/:projectId - Fetch project memory
- POST /api/memory/:projectId - Update project memory
- GET /api/knowledge/:projectId - List knowledge docs
- Authentication via API key

## File Structure

```
electron/
├── main.js - Main process entry
├── preload.js - Preload script
├── tray.js - System tray logic
├── server.js - Express server wrapper
├── beacon.js - Beacon HTTP server
└── package.json - Electron config
```

## Configuration

### package.json (Electron)

```json
{
  "name": "dive-ai-local",
  "version": "1.0.0",
  "main": "electron/main.js",
  "build": {
    "appId": "com.dive.ai.local",
    "productName": "Dive AI Local",
    "directories": {
      "output": "dist-electron"
    },
    "files": [
      "electron/**/*",
      "dist/**/*",
      "server/**/*",
      "drizzle/**/*"
    ],
    "mac": {
      "category": "public.app-category.developer-tools"
    },
    "win": {
      "target": "nsis"
    },
    "linux": {
      "target": "AppImage",
      "category": "Development"
    }
  }
}
```

## Data Storage

User data directory:
- macOS: `~/Library/Application Support/dive-ai-local/`
- Windows: `%APPDATA%/dive-ai-local/`
- Linux: `~/.config/dive-ai-local/`

Structure:
```
dive-ai-local/
├── projects/ - Project data
├── chroma/ - Vector database
├── database.sqlite - Metadata
└── config.json - User preferences
```

## Security Considerations

1. **Context Isolation**: Enable `contextIsolation` in BrowserWindow
2. **Node Integration**: Disable `nodeIntegration` in renderer
3. **Preload Scripts**: Use preload.js for secure IPC
4. **CSP**: Set Content Security Policy headers
5. **Beacon Auth**: Require API key for remote access

## Development Workflow

1. **Development Mode**:
   ```bash
   npm run dev:electron
   ```
   - Runs Vite dev server
   - Starts Electron with hot reload

2. **Production Build**:
   ```bash
   npm run build:electron
   ```
   - Builds React app
   - Packages Electron app
   - Creates installers

## Implementation Steps

1. ✅ Install Electron dependencies
2. ✅ Create main process (main.js)
3. ✅ Create preload script (preload.js)
4. ✅ Integrate Express server
5. ✅ Add system tray
6. ✅ Configure electron-builder
7. ✅ Test packaging
8. ✅ Add auto-updater

## Testing Strategy

1. **Unit Tests**: Test main process logic
2. **Integration Tests**: Test IPC communication
3. **E2E Tests**: Test full application flow
4. **Manual Testing**: Test on all platforms

## Deployment

1. **Auto-updater**: Use electron-updater with GitHub releases
2. **Code Signing**: Sign macOS and Windows builds
3. **Distribution**: GitHub Releases + website download

## Known Issues & Solutions

### Issue: CORS in Electron
**Solution**: Set `webSecurity: false` in development, use proper CSP in production

### Issue: SQLite native modules
**Solution**: Use electron-rebuild to recompile native modules

### Issue: File paths
**Solution**: Use `app.getPath('userData')` for all data storage

## References

- [Electron Documentation](https://www.electronjs.org/docs)
- [electron-builder](https://www.electron.build/)
- [Security Best Practices](https://www.electronjs.org/docs/tutorial/security)

## Next Steps

1. Implement main.js with window management
2. Add system tray integration
3. Integrate existing Express server
4. Add beacon HTTP server
5. Configure electron-builder
6. Test on all platforms
