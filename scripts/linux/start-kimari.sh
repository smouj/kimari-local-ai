#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# Kimari — Universal Start Script
# =============================================================================
# Starts the Kimari local AI server using the specified hardware profile.
# Defaults to the "gtx1060" profile if none is provided.
#
# Usage:
#   bash start-kimari.sh              # Uses gtx1060 profile
#   bash start-kimari.sh gtx1080      # Uses gtx1080 profile
#   bash start-kimari.sh custom       # Uses "custom" profile from config
# =============================================================================

PROFILE="${1:-gtx1060}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "============================================"
echo "  Kimari Local AI"
echo "  Profile: $PROFILE"
echo "============================================"

python3 "$PROJECT_ROOT/cli/kimari_cli.py" start --profile "$PROFILE"
