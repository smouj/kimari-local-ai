<#
.SYNOPSIS
    Starts Kimari with the GTX 1060 hardware profile.
.DESCRIPTION
    Launches the Kimari local AI server configured for GTX 1060 6GB GPUs.
    Uses the gtx1060 profile which limits context and batch size to fit
    within 6GB VRAM.
.NOTES
    Requires Python 3.10+ and Kimari CLI installed (pip install -e .).
#>

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Kimari Local AI" -ForegroundColor Cyan
Write-Host "  Profile: gtx1060" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Prefer installed kimari command; fall back to python -m
if (Get-Command kimari -ErrorAction SilentlyContinue) {
    kimari start --profile gtx1060
} else {
    python -m kimari.cli.main start --profile gtx1060
}
