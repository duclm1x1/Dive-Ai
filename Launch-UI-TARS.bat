@echo off
REM UI-TARS Desktop Launcher
REM Starts Gateway Proxy + UI-TARS Desktop Application
REM Double-click to run!

echo ========================================
echo    UI-TARS Desktop Launcher v1.0
echo    Powered by Dive AI V29.4
echo ========================================
echo.

REM Set API Key
echo [1/3] Setting V98 API Key...
set V98_API_KEY=YOUR_V98_API_KEY_HERE
echo       API Key Set: %V98_API_KEY:~0,20%...
echo.

REM Navigate to Dive AI directory
cd /d "D:\Antigravity\Dive AI"

REM Start Gateway Proxy in background
echo [2/3] Starting Gateway Proxy Server...
start "UI-TARS Gateway Proxy" /MIN cmd /c "python gateway\ui_tars_proxy.py"
timeout /t 3 /nobreak >nul
echo       Proxy started at http://localhost:8765
echo.

REM Start UI-TARS Desktop
echo [3/3] Launching UI-TARS Desktop...
cd "UI-TARS-Desktop"
echo       Starting Electron app...
echo.
start "UI-TARS Desktop" cmd /k "pnpm run dev:ui-tars"

echo ========================================
echo    UI-TARS Desktop is starting!
echo.
echo    Gateway Proxy: http://localhost:8765
echo    UI-TARS Desktop: Opening...
echo.
echo    To stop: Close this window
echo ========================================
echo.

REM Keep this window open to monitor
echo Press any key to stop all services and exit...
pause >nul

REM Cleanup - kill processes
echo.
echo Stopping services...
taskkill /FI "WINDOWTITLE eq UI-TARS Gateway Proxy*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq UI-TARS Desktop*" /F >nul 2>&1
echo Services stopped. Goodbye!
timeout /t 2 >nul
