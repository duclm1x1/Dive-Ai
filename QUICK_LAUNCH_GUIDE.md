# UI-TARS Desktop - Quick Launch Guide

## 🚀 One-Click Launch (Easiest!)

### Method 1: Interactive Launcher

**Double-click**: `Launch-UI-TARS.bat`

**What it does**:

1. ✅ Sets V98 API key automatically
2. ✅ Starts Gateway Proxy (background)
3. ✅ Launches UI-TARS Desktop
4. ✅ Shows status in console window

**How to stop**:

- Press any key in the launcher window, OR
- Double-click `Stop-UI-TARS.bat`

---

### Method 2: Silent Launcher

**Double-click**: `Launch-UI-TARS-Silent.bat`

**What it does**:

- Same as Method 1 but runs completely in background
- No console windows shown
- Exits immediately after launching

**How to stop**:

- Double-click `Stop-UI-TARS.bat`, OR
- End `node.exe` and `python.exe` in Task Manager

---

## 📋 Available Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `Launch-UI-TARS.bat` | Start with console | Double-click |
| `Launch-UI-TARS-Silent.bat` | Start in background | Double-click |
| `Stop-UI-TARS.bat` | Stop all services | Double-click |

---

## 🎯 What Gets Started

When you run the launcher:

```
Launch-UI-TARS.bat
    │
    ├─► Set V98_API_KEY environment variable
    │
    ├─► Start Gateway Proxy
    │   └─► python gateway\ui_tars_proxy.py
    │       └─► Runs on http://localhost:8765
    │
    └─► Start UI-TARS Desktop
        └─► pnpm run dev:ui-tars
            └─► Electron app opens
```

---

## ✅ First Time Setup

Before using the launcher:

1. **No setup needed!** Everything is configured in the launcher script.

2. **Optional - Pin to Desktop**:
   - Right-click `Launch-UI-TARS.bat`
   - Send to → Desktop (create shortcut)
   - Rename shortcut to "UI-TARS Desktop"

3. **Optional - Custom Icon**:
   - Right-click shortcut → Properties
   - Click "Change Icon"
   - Browse to: `D:\Antigravity\Dive AI\UI-TARS-Desktop\apps\ui-tars\resources\icon.ico`

---

## 🔧 Customization

### Change API Key

Edit `Launch-UI-TARS.bat`, line 14:

```batch
set V98_API_KEY=your-new-api-key-here
```

### Change Proxy Port

Edit `gateway\ui_tars_proxy.py`, line 317:

```python
uvicorn.run(app, host="0.0.0.0", port=8765)  # Change 8765 to your port
```

---

## 🐛 Troubleshooting

### "App doesn't start"

**Check**:

1. Is proxy running? Visit <http://localhost:8765/health>
2. Are ports 8765 and 5173 available?
3. Run `Stop-UI-TARS.bat` and try again

### "Can't stop services"

```batch
# Manual cleanup
taskkill /F /IM node.exe
taskkill /F /IM python.exe
taskkill /F /IM electron.exe
```

### "API key not working"

The key is set automatically in the launcher. If v98store.com still returns errors:

1. Check if v98store.com is accessible
2. Verify API key is still valid
3. Try direct Anthropic API (see CONFIGURATION_GUIDE.md)

---

## 📍 File Locations

**Launchers**: `D:\Antigravity\Dive AI\`

- Launch-UI-TARS.bat
- Launch-UI-TARS-Silent.bat
- Stop-UI-TARS.bat

**UI-TARS App**: `D:\Antigravity\Dive AI\UI-TARS-Desktop\`

**Gateway Proxy**: `D:\Antigravity\Dive AI\gateway\ui_tars_proxy.py`

---

## 🎉 You're Ready

Just **double-click `Launch-UI-TARS.bat`** and you're good to go!

No need to:

- ❌ Open terminals manually
- ❌ Type commands
- ❌ Set environment variables
- ❌ Navigate directories

Everything runs automatically! 🚀
