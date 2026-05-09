# install-dev.ps1 — Install Kimari Local AI development environment (Windows)
# Usage: powershell -ExecutionPolicy Bypass -File scripts\windows\install-dev.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Kimari Local AI - Dev Setup (Windows)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
try {
    $pyVersion = python --version 2>&1
    Write-Host "[OK] Found: $pyVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found. Install Python 3.10+ and try again." -ForegroundColor Red
    exit 1
}

# Install dev dependencies
Write-Host ""
Write-Host "[1/3] Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements-dev.txt

# Install kimari in editable mode
Write-Host ""
Write-Host "[2/3] Installing kimari package (editable)..." -ForegroundColor Yellow
pip install -e ".[dev]"

# Check environment
Write-Host ""
Write-Host "[3/3] Checking environment..." -ForegroundColor Yellow
python scripts/linux/check-env.py 2>$null

Write-Host ""
Write-Host "Development environment ready!" -ForegroundColor Green
Write-Host ""
Write-Host "Quick start:"
Write-Host "  kimari doctor          # Check system"
Write-Host "  kimari pull test       # Download test model"
Write-Host "  make test              # Run tests"
