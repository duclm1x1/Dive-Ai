$ErrorActionPreference = "Stop"

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "       Dive Coder V19.5 - Installer" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# 1. Check Python Version
Write-Host "[1/4] Checking Python version..."
$pythonVersion = python --version 2>&1
Write-Host "Found: $pythonVersion"

# 2. Install Dependencies
Write-Host "[2/4] Installing dependencies from requirements.txt..."
python -m pip install -r requirements.txt --quiet
Write-Host "✅ Dependencies installed."

# 3. Apply Python 3.14 Patches
Write-Host "[3/4] Applying compatibility patches..."
python scripts/patch_v19_5.py
Write-Host "✅ Patches applied."

# 4. Verify Installation
Write-Host "[4/4] Verifying V19.5 system status..."
python divecoder_v19_5.py status
Write-Host "✅ System verified."

Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "   Dive Coder V19.5 Installed Successfully!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "To start: python divecoder_v19_5.py process --prompt 'Your Goal'"
