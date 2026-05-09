#!/usr/bin/env bash
# =============================================================================
# Kimari — Healthcheck
# =============================================================================
# Verifies that the Kimari server is running and responding on port 11435.
#
# Usage:
#   bash healthcheck.sh
#   bash healthcheck.sh              # Checks 127.0.0.1:11435
#
# Exit codes:
#   0 — Server is healthy
#   1 — Server is not responding
# =============================================================================

HOST="127.0.0.1"
PORT="11435"
TIMEOUT=5

echo "Checking Kimari at $HOST:$PORT..."

if curl -sf --max-time "$TIMEOUT" "http://$HOST:$PORT/health" > /dev/null 2>&1; then
    echo "✓ Kimari is READY"
    curl -s --max-time "$TIMEOUT" "http://$HOST:$PORT/health" | python3 -m json.tool 2>/dev/null || true
    exit 0
else
    echo "✗ Kimari is not responding"
    exit 1
fi
