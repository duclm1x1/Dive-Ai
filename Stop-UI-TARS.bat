@echo off
REM Stop All UI-TARS Services
echo Stopping UI-TARS Desktop services...

REM Kill Node processes (UI-TARS)
taskkill /F /IM node.exe /FI "WINDOWTITLE eq *ui-tars*" >nul 2>&1

REM Kill Python processes (Gateway Proxy)
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *proxy*" >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1

REM Kill Electron processes
taskkill /F /IM electron.exe >nul 2>&1

echo All services stopped.
timeout /t 2 >nul
