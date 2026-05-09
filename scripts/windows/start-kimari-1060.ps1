<#
.SYNOPSIS
    Starts Kimari with the GTX 1060 hardware profile.
.DESCRIPTION
    Launches the Kimari local AI server configured for GTX 1060 6GB GPUs.
    Uses the gtx1060 profile which limits context and batch size to fit
    within 6GB VRAM.
.NOTES
    Requires Python 3.8+ and Kimari CLI installed.
#>

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$KimariCli = Join-Path $ProjectRoot "cli\kimari_cli.py"

if (-not (Test-Path $KimariCli)) {
    Write-Error "Kimari CLI not found at: $KimariCli" 
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Kimari Local AI" -ForegroundColor Cyan
Write-Host "  Profile: gtx1060" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

python "$KimariCli" start --profile gtx1060
