param(
  [string]$DiveBaseUrl = $env:DIVE_BASE_URL,
  [string]$DiveApiKey = $env:DIVE_API_KEY,
  [string]$InstallDir = "$env:USERPROFILE\.dive\bin"
)

Write-Host "Dive Coder installer (local scaffold)."
Write-Host "NOTE: This script does not download remote binaries. It prepares local config + PATH."

New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

# Create a shim that runs the repo CLI if present
$shim = Join-Path $InstallDir "dive.ps1"
@"
`$repo = (Get-Location).Path
python3 `"$repo\.shared\vibe-coder-v13\vibe.py`" @Args
"@ | Set-Content -Encoding UTF8 $shim

# Config
$configDir = Join-Path $env:USERPROFILE ".config\dive"
New-Item -ItemType Directory -Force -Path $configDir | Out-Null
$configPath = Join-Path $configDir "config.json"

if (-not $DiveBaseUrl) { $DiveBaseUrl = "https://aicoding.io.vn/v1" }

$config = @{
  provider = "openai-compatible"
  base_url = $DiveBaseUrl
  api_key  = if ($DiveApiKey) { "<set-via-env>" } else { "<missing>" }
  model    = "claude-sonnet-4-5-20250929"
}

($config | ConvertTo-Json -Depth 5) | Set-Content -Encoding UTF8 $configPath

Write-Host ""
Write-Host "Installed shim: $shim"
Write-Host "Config written: $configPath"
Write-Host ""
Write-Host "Next:"
Write-Host "  1) Set env var: DIVE_API_KEY=YOUR_KEY"
Write-Host "  2) Add to PATH: $InstallDir"
Write-Host "  3) Run: dive.ps1 doctor --repo ."
