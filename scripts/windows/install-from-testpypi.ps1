# install-from-testpypi.ps1 — Install Kimari Local AI from TestPyPI
# Usage: powershell -ExecutionPolicy Bypass -File scripts\windows\install-from-testpypi.ps1
#        powershell -ExecutionPolicy Bypass -File scripts\windows\install-from-testpypi.ps1 -VenvPath .venv

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false, HelpMessage = "Path to create/activate a virtual environment")]
    [string]$VenvPath
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Kimari Local AI - Install from TestPyPI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# --- Step 1: Create venv if requested ---
if ($VenvPath) {
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
    Write-Host "[1/4] Skipping venv creation (no -VenvPath provided)." -ForegroundColor Yellow
}

# --- Step 2: Install from TestPyPI ---
Write-Host ""
Write-Host "[2/4] Installing kimari-local-ai from TestPyPI..." -ForegroundColor Yellow
Write-Host "  Index: https://test.pypi.org/simple/" -ForegroundColor Gray

& python -m pip install --index-url https://test.pypi.org/simple/ kimari-local-ai
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to install from TestPyPI." -ForegroundColor Red
    Write-Host "  The package may not be published yet, or the version may differ." -ForegroundColor Red
    Write-Host "  Check: https://test.pypi.org/project/kimari-local-ai/" -ForegroundColor Red
    exit 1
}
Write-Host "  Package installed from TestPyPI." -ForegroundColor Green

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
Write-Host "  TestPyPI Installation Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
if ($VenvPath) {
    Write-Host "  Virtual env: $VenvPath" -ForegroundColor Green
}
Write-Host ""
Write-Host "  IMPORTANT: This installs from TestPyPI only." -ForegroundColor Yellow
Write-Host "  Models are NOT auto-downloaded. To get a model:" -ForegroundColor Yellow
Write-Host "    kimari pull test       # Download small test model"
Write-Host "    kimari pull --list     # See available models"
Write-Host ""
Write-Host "  Next steps:" -ForegroundColor Yellow
Write-Host "    kimari doctor          # Check system requirements"
Write-Host "    kimari start           # Start the server"
Write-Host ""

# --- PowerShell ExecutionPolicy Note ---
Write-Host "NOTE: If you encountered execution policy errors, run one of:" -ForegroundColor Yellow
Write-Host "  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned" -ForegroundColor White
Write-Host "  powershell -ExecutionPolicy Bypass -File <script.ps1>" -ForegroundColor White
