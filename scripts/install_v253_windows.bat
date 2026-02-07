@echo off
REM Dive AI V25.3 - Windows Installation Script
REM Installs all dependencies for multimodal voice + vision

echo.
echo ========================================================================
echo                    DIVE AI V25.3 - INSTALLATION
echo ========================================================================
echo.
echo Installing multimodal voice + vision assistant...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.11+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/6] Checking Python version...
python --version

REM Upgrade pip
echo.
echo [2/6] Upgrading pip...
python -m pip install --upgrade pip

REM Install core dependencies
echo.
echo [3/6] Installing core dependencies...
pip install openai>=1.10.0 anthropic>=0.18.0 python-dotenv>=1.0.0

REM Install voice dependencies
echo.
echo [4/6] Installing voice dependencies...
pip install pyaudio websockets pyttsx3 SpeechRecognition

REM Install vision dependencies
echo.
echo [5/6] Installing vision dependencies...
pip install Pillow mss pyautogui opencv-python

REM Install all requirements
echo.
echo [6/6] Installing remaining requirements...
pip install -r requirements_v253.txt

REM Create .env if not exists
if not exist .env (
    echo.
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo [IMPORTANT] Please edit .env file and add your OPENAI_API_KEY!
)

echo.
echo ========================================================================
echo                    INSTALLATION COMPLETE!
echo ========================================================================
echo.
echo Next steps:
echo   1. Edit .env file and add your OPENAI_API_KEY
echo   2. Run: python dive_v253.py
echo   3. Say "hey dive" to activate
echo.
echo For more information, see README_V25.3.md
echo.
pause
