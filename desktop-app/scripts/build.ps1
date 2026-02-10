# Dive AI V29.4 Build Script
# PowerShell build script for production

param(
    [switch]$Dev,
    [switch]$Build,
    [switch]$Package,
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot | Split-Path -Parent

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Dive AI V29.4 Build Script" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Functions
function Write-Step($msg) {
    Write-Host "[STEP] $msg" -ForegroundColor Green
}

function Write-Error($msg) {
    Write-Host "[ERROR] $msg" -ForegroundColor Red
}

# Clean
if ($Clean) {
    Write-Step "Cleaning build artifacts..."
    
    if (Test-Path "$ProjectRoot\dist") {
        Remove-Item -Recurse -Force "$ProjectRoot\dist"
    }
    if (Test-Path "$ProjectRoot\release") {
        Remove-Item -Recurse -Force "$ProjectRoot\release"
    }
    if (Test-Path "$ProjectRoot\node_modules") {
        Remove-Item -Recurse -Force "$ProjectRoot\node_modules"
    }
    
    Write-Host "Clean complete!" -ForegroundColor Green
    exit 0
}

# Check prerequisites
Write-Step "Checking prerequisites..."

$nodeVersion = node --version 2>$null
if (-not $nodeVersion) {
    Write-Error "Node.js not found. Please install Node.js 18+"
    exit 1
}
Write-Host "  Node.js: $nodeVersion"

$pythonVersion = py --version 2>$null
if (-not $pythonVersion) {
    Write-Error "Python not found. Please install Python 3.10+"
    exit 1
}
Write-Host "  Python: $pythonVersion"

# Install dependencies
Write-Step "Installing npm dependencies..."
Set-Location $ProjectRoot
npm install

Write-Step "Installing Python dependencies..."
Set-Location "$ProjectRoot\backend"
py -m pip install -r requirements.txt -q

# Development mode
if ($Dev) {
    Write-Step "Starting development servers..."
    
    # Start backend in background
    Start-Job -ScriptBlock {
        Set-Location $using:ProjectRoot\backend
        py gateway_server.py
    }
    
    # Start frontend
    Set-Location $ProjectRoot
    npm run dev
    
    exit 0
}

# Build
if ($Build) {
    Write-Step "Building production..."
    
    Set-Location $ProjectRoot
    npm run build
    
    Write-Host ""
    Write-Host "Build complete!" -ForegroundColor Green
    Write-Host "Output: $ProjectRoot\dist"
    exit 0
}

# Package
if ($Package) {
    Write-Step "Building and packaging..."
    
    Set-Location $ProjectRoot
    npm run build
    
    Write-Step "Creating installer..."
    # electron-builder will be run by npm
    
    Write-Host ""
    Write-Host "Package complete!" -ForegroundColor Green
    Write-Host "Output: $ProjectRoot\release"
    exit 0
}

# Default: show help
Write-Host "Usage: .\build.ps1 [-Dev] [-Build] [-Package] [-Clean]"
Write-Host ""
Write-Host "Options:"
Write-Host "  -Dev      Start development servers"
Write-Host "  -Build    Build production"
Write-Host "  -Package  Build and create installer"
Write-Host "  -Clean    Clean build artifacts"
