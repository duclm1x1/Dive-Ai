@echo off
REM UI-TARS Desktop Silent Launcher (No console windows)
REM Starts services in background

REM Set API Key
set V98_API_KEY=YOUR_V98_API_KEY_HERE

REM Navigate to Dive AI directory
cd /d "D:\Antigravity\Dive AI"

REM Start Gateway Proxy (hidden window)
start /B pythonw gateway\ui_tars_proxy.py

REM Wait 3 seconds for proxy to start
timeout /t 3 /nobreak >nul

REM Start UI-TARS Desktop
cd "UI-TARS-Desktop"
start /B cmd /c "pnpm run dev:ui-tars"

REM Exit silently
exit
