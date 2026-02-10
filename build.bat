@echo off
echo.
echo ========================================
echo   Building Dive AI Desktop
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python 3.9 or higher
    pause
    exit /b 1
)

echo [1/5] Installing build dependencies...
python -m pip install --upgrade pip
python -m pip install pyinstaller pystray Pillow requests

echo.
echo [2/5] Installing Dive AI dependencies...
python -m pip install -r requirements.txt

echo.
echo [3/5] Building System Tray application...
pyinstaller --onefile --windowed --name "DiveAI-Tray" --icon assets\diveai.ico diveai_tray.py

echo.
echo [4/5] Building Setup Wizard...
pyinstaller --onefile --windowed --name "DiveAI-Setup-Wizard" first_run_setup.py

echo.
echo [5/5] Creating distribution folder...
if not exist "dist\DiveAI" mkdir "dist\DiveAI"

REM Copy files to dist
xcopy /E /I /Y "core" "dist\DiveAI\core"
xcopy /E /I /Y "gateway" "dist\DiveAI\gateway"
xcopy /E /I /Y "channels" "dist\DiveAI\channels"
copy /Y ".env.example" "dist\DiveAI\.env.example"
copy /Y "README.md" "dist\DiveAI\README.md"
copy /Y "requirements.txt" "dist\DiveAI\requirements.txt"
copy /Y "dist\DiveAI-Tray.exe" "dist\DiveAI\"
copy /Y "dist\DiveAI-Setup-Wizard.exe" "dist\DiveAI\"

echo.
echo ========================================
echo   Build Complete!
echo ========================================
echo.
echo Files created:
echo   - dist\DiveAI-Tray.exe (System Tray)
echo   - dist\DiveAI-Setup-Wizard.exe (Setup)
echo   - dist\DiveAI\ (Full installation)
echo.
echo To create installer, run:
echo   install_builder.bat
echo.
pause
