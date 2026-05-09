# =============================================================================
# Kimari — Health Check (Windows PowerShell)
# =============================================================================

$ErrorActionPreference = "Stop"
$KIMARI_ROOT = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$CONFIG_FILE = Join-Path $KIMARI_ROOT "config\kimari.profiles.json"

# --- Read config ---
if (-not (Test-Path $CONFIG_FILE)) {
    Write-Host "[ERROR] Config not found: $CONFIG_FILE" -ForegroundColor Red
    exit 1
}

$config = Get-Content $CONFIG_FILE | ConvertFrom-Json
$profileName = $config.default_profile
if (-not $profileName) { $profileName = "gtx1060" }
$PORT = $config.profiles.$profileName.port

$HEALTH_URL = "http://127.0.0.1:${PORT}/health"

try {
    $response = Invoke-RestMethod -Uri $HEALTH_URL -TimeoutSec 5 -ErrorAction Stop
    Write-Host "[OK] Kimari server is healthy" -ForegroundColor Green
    if ($response.model) {
        Write-Host "     Model: $($response.model)"
    }
    if ($response.n_ctx) {
        Write-Host "     Context: $($response.n_ctx) tokens"
    }
    exit 0
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Host "[FAIL] Kimari server is not responding (HTTP ${statusCode})" -ForegroundColor Red
    Write-Host "[INFO] Start the server: .\scripts\windows\start-kimari-1060.ps1" -ForegroundColor Yellow
    exit 1
}
