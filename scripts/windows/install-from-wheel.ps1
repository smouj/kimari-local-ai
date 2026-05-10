# install-from-wheel.ps1 — Install Kimari Local AI from a local wheel file
# Usage: powershell -ExecutionPolicy Bypass -File scripts\windows\install-from-wheel.ps1 -WheelPath dist\kimari_local_ai-0.1.15-py3-none-any.whl
#        powershell -ExecutionPolicy Bypass -File scripts\windows\install-from-wheel.ps1 -WheelPath dist\kimari_local_ai-0.1.15-py3-none-any.whl -VenvPath .venv

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, HelpMessage = "Path to the .whl file to install")]
    [string]$WheelPath,

    [Parameter(Mandatory = $false, HelpMessage = "Path to create/activate a virtual environment")]
    [string]$VenvPath
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Kimari Local AI - Install from Wheel" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# --- Validate wheel path ---
if (-not (Test-Path $WheelPath)) {
    Write-Host "[ERROR] Wheel file not found: $WheelPath" -ForegroundColor Red
    exit 1
}

$WheelPath = (Resolve-Path $WheelPath).Path
Write-Host "  Wheel: $WheelPath" -ForegroundColor White

# --- Step 1: Create venv if requested ---
$pythonCmd = "python"

if ($VenvPath) {
    Write-Host ""
    Write-Host "[1/4] Creating virtual environment at $VenvPath..." -ForegroundColor Yellow

    & python -m venv $VenvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to create virtual environment." -ForegroundColor Red
        exit 1
    }

    # Activate the venv
    $activateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
    if (-not (Test-Path $activateScript)) {
        Write-Host "[ERROR] Activation script not found: $activateScript" -ForegroundColor Red
        exit 1
    }

    . $activateScript
    Write-Host "  Virtual environment created and activated." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[1/4] Skipping venv creation (no -VenvPath provided)." -ForegroundColor Yellow
}

# --- Step 2: Install the wheel ---
Write-Host ""
Write-Host "[2/4] Installing wheel..." -ForegroundColor Yellow

& python -m pip install --quiet $WheelPath
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to install wheel." -ForegroundColor Red
    exit 1
}
Write-Host "  Wheel installed successfully." -ForegroundColor Green

# --- Step 3: Verify installation ---
Write-Host ""
Write-Host "[3/4] Verifying installation..." -ForegroundColor Yellow

Write-Host "  Running: kimari --version" -ForegroundColor Gray
& kimari --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] kimari --version failed (may need PATH restart)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "  Running: kimari setup --json" -ForegroundColor Gray
& kimari setup --json
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] kimari setup --json failed" -ForegroundColor Yellow
}

# --- Step 4: Dry-run start ---
Write-Host ""
Write-Host "[4/4] Dry-run start..." -ForegroundColor Yellow

Write-Host "  Running: kimari start --dry-run" -ForegroundColor Gray
& kimari start --dry-run
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] kimari start --dry-run failed" -ForegroundColor Yellow
} else {
    Write-Host "  Dry-run passed." -ForegroundColor Green
}

# --- Summary ---
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Installation Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Installed from: $WheelPath" -ForegroundColor Green
if ($VenvPath) {
    Write-Host "  Virtual env:    $VenvPath" -ForegroundColor Green
}
Write-Host ""
Write-Host "  Next steps:" -ForegroundColor Yellow
Write-Host "    kimari doctor          # Check system requirements"
Write-Host "    kimari pull test       # Download test model"
Write-Host "    kimari start           # Start the server"
Write-Host ""

# --- PowerShell ExecutionPolicy Note ---
Write-Host "NOTE: If you encountered execution policy errors, run one of:" -ForegroundColor Yellow
Write-Host "  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned" -ForegroundColor White
Write-Host "  powershell -ExecutionPolicy Bypass -File <script.ps1>" -ForegroundColor White
