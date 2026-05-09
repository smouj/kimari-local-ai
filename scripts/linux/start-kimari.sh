#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# Kimari — Universal Start Script
# =============================================================================
# Starts the Kimari local AI server using the specified hardware profile.
# Defaults to the "test" profile if none is provided.
#
# Usage:
#   bash start-kimari.sh              # Uses test profile (default)
#   bash start-kimari.sh gtx1080      # Uses gtx1080 profile
#   bash start-kimari.sh custom       # Uses "custom" profile from config
# =============================================================================

PROFILE="${1:-test}"

echo "============================================"
echo "  Kimari Local AI"
echo "  Profile: $PROFILE"
echo "============================================"

# Prefer the installed kimari command, fall back to python -m
if command -v kimari >/dev/null 2>&1; then
  kimari start --profile "$PROFILE"
else
  python3 -m kimari.cli.main start --profile "$PROFILE"
fi
