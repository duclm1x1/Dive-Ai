# Dive AI V25 - Full-Duplex Voice Installation (Windows PowerShell)
Write-Host "==========================================================================" -ForegroundColor Green
Write-Host "Dive AI V25 - Full-Duplex Voice Installation (Windows Edition)" -ForegroundColor Green
Write-Host "==========================================================================" -ForegroundColor Green

# 1. Python Dependencies
Write-Host "[1/3] Installing Python dependencies..." -ForegroundColor Blue
python -m pip install --quiet SpeechRecognition pyttsx3 pyaudio openai pygame webrtcvad numpy
python -m pip install --quiet pyautogui pynput pillow opencv-python
python -m pip install --quiet requests python-dotenv

if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Some Python dependencies failed to install. Please check your internet connection or Python setup." -ForegroundColor Yellow
}
else {
    Write-Host "[v] Python dependencies installed" -ForegroundColor Green
}

# 2. Configure Environment
Write-Host "[2/3] Configuring environment..." -ForegroundColor Blue
$envFile = Join-Path $PSScriptRoot ".env"

if (-not (Test-Path $envFile)) {
    $envContent = @"
# Dive AI V25 - Full-Duplex Voice Configuration

# OpenAI API Key (for Whisper STT and GPT)
OPENAI_API_KEY=your-api-key-here

# V98 API Configuration
V98_API_KEY=YOUR_V98_API_KEY_HERE
V98_BASE_URL=https://v98store.com/v1

# AI Coding API Configuration
AICODING_API_KEY=YOUR_AICODING_API_KEY_HERECJCk
AICODING_BASE_URL=https://aicoding.io.vn/v1

# Voice Configuration
VOICE_STT_PROVIDER=google
VOICE_TTS_PROVIDER=pyttsx3
VOICE_WAKE_WORD=hey dive
VOICE_LANGUAGE=en-US

# Full-Duplex Features
ENABLE_STREAMING_TTS=true
ENABLE_VAD_BARGEIN=true
ENABLE_TALK_WHILE_ACT=true
NARRATION_STYLE=detailed

# UI-TARS Configuration
UITARS_PATH=`$HOME/UI-TARS-desktop
UITARS_API_URL=http://localhost:8080
UITARS_MODEL=ui-tars-1.5

# Dive Memory
DIVE_MEMORY_PATH=./memory/dive_memory.db
"@
    Set-Content -Path $envFile -Value $envContent
    Write-Host "[v] Created .env file" -ForegroundColor Green
}
else {
    Write-Host "[v] .env file exists" -ForegroundColor Green
}

# 3. Create Launch Script
Write-Host "[3/3] Creating launch script..." -ForegroundColor Blue
$startScript = Join-Path $PSScriptRoot "start_fullduplex.ps1"
$startContent = @"
# Launch Dive AI Full-Duplex Voice Control
Set-Location `$PSScriptRoot

# Start full-duplex orchestrator
python core/dive_fullduplex_orchestrator.py `$args
"@
Set-Content -Path $startScript -Value $startContent
Write-Host "[v] Launch script created: start_fullduplex.ps1" -ForegroundColor Green

Write-Host "==========================================================================" -ForegroundColor Green
Write-Host "[OK] Installation Complete!" -ForegroundColor Green
Write-Host "==========================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Edit .env and add your OpenAI API key"
Write-Host "  2. Run: .\start_fullduplex.ps1"
Write-Host "  3. Say 'hey dive' to activate"
