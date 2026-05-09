# =============================================================================
# Kimari — Start with GTX 1080 Profile (Windows PowerShell)
# =============================================================================

$ErrorActionPreference = "Stop"

Write-Host "=== Kimari — Starting with profile: gtx1080 ===" -ForegroundColor Cyan

# Prefer installed kimari command; fall back to python -m
if (Get-Command kimari -ErrorAction SilentlyContinue) {
    kimari start --profile gtx1080
} else {
    python -m kimari.cli.main start --profile gtx1080
}
