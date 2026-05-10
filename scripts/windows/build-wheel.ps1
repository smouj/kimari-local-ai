# build-wheel.ps1 — Build a Kimari Local AI wheel package and validate it
# Usage: powershell -ExecutionPolicy Bypass -File scripts\windows\build-wheel.ps1

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Kimari Local AI - Build Wheel" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# --- Step 1: Check Python 3.10+ ---
Write-Host "[1/4] Checking Python version..." -ForegroundColor Yellow

$pythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python (\d+)\.(\d+)") {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            if ($major -gt 3 -or ($major -eq 3 -and $minor -ge 10)) {
                $pythonCmd = $cmd
                Write-Host "  Found: $ver" -ForegroundColor Green
                break
            }
        }
    }
    catch {
        continue
    }
}

if (-not $pythonCmd) {
    Write-Host "[ERROR] Python 3.10+ is required but not found." -ForegroundColor Red
    Write-Host "  Install Python 3.10 or later: https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

# --- Step 2: Install build tools ---
Write-Host ""
Write-Host "[2/4] Installing build tools (build, twine)..." -ForegroundColor Yellow

& $pythonCmd -m pip install --quiet build twine
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to install build/twine." -ForegroundColor Red
    exit 1
}
Write-Host "  build and twine installed." -ForegroundColor Green

# --- Step 3: Build the wheel ---
Write-Host ""
Write-Host "[3/4] Building wheel package..." -ForegroundColor Yellow

& $pythonCmd -m build
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Build failed." -ForegroundColor Red
    exit 1
}
Write-Host "  Build succeeded." -ForegroundColor Green

# --- Step 4: Validate with twine ---
Write-Host ""
Write-Host "[4/4] Validating distribution with twine..." -ForegroundColor Yellow

& $pythonCmd -m twine check dist/*
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Twine check failed. Fix package metadata before publishing." -ForegroundColor Red
    exit 1
}
Write-Host "  Twine check passed." -ForegroundColor Green

# --- Summary ---
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Build Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$distDir = Join-Path $PSScriptRoot "..\..\dist"
$resolvedDist = Resolve-Path $distDir -ErrorAction SilentlyContinue
if ($resolvedDist) {
    Write-Host "  Wheel location: $resolvedDist" -ForegroundColor Green
    Get-ChildItem $resolvedDist -Filter "*.whl" | ForEach-Object {
        Write-Host "    $($_.Name)" -ForegroundColor White
    }
} else {
    Write-Host "  Wheel location: dist/" -ForegroundColor Green
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  Test install:  .\scripts\windows\install-from-wheel.ps1 -WheelPath dist\kimari_local_ai-<version>-py3-none-any.whl"
Write-Host "  Upload to PyPI:  twine upload dist/*"
