#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# Kimari — Launch Server + Open Browser
# =============================================================================
# Starts the Kimari server in the background, waits for it to become healthy,
# then opens the web UI in the default browser.
#
# Usage:
#   bash launch-kimari-web.sh           # Uses gtx1080 profile
#   bash launch-kimari-web.sh gtx1060   # Uses gtx1060 profile
#
# The web UI is expected at http://127.0.0.1:5173 (Vite dev server).
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
PROFILE="${1:-gtx1080}"
HOST="127.0.0.1"
API_PORT="11435"
WEB_PORT="5173"
MAX_WAIT=30

echo "========================================"
echo "  Kimari Local AI — Web Launcher"
echo "  Profile: $PROFILE"
echo "========================================"
echo ""

# --- Start server in background -----------------------------------------
echo "Starting Kimari server (profile: $PROFILE)..."
python3 "$PROJECT_ROOT/cli/kimari_cli.py" start --profile "$PROFILE" &
SERVER_PID=$!
echo "Server PID: $SERVER_PID"
echo ""

# --- Cleanup on exit ----------------------------------------------------
cleanup() {
    echo ""
    echo "Shutting down server (PID: $SERVER_PID)..."
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
    echo "Done."
}
trap cleanup EXIT INT TERM

# --- Wait for server to be healthy -------------------------------------
echo "Waiting for server (max ${MAX_WAIT}s)..."
for i in $(seq 1 "$MAX_WAIT"); do
    if curl -sf --max-time 2 "http://$HOST:$API_PORT/health" > /dev/null 2>&1; then
        echo "✓ Server is ready after ${i}s"
        echo ""
        echo "API:  http://$HOST:$API_PORT"
        echo "Web:  http://$HOST:$WEB_PORT"
        echo ""

        # Open browser
        if command -v xdg-open >/dev/null 2>&1; then
            xdg-open "http://$HOST:$WEB_PORT" 2>/dev/null || true
        elif command -v sensible-browser >/dev/null 2>&1; then
            sensible-browser "http://$HOST:$WEB_PORT" 2>/dev/null || true
        elif command -v gnome-open >/dev/null 2>&1; then
            gnome-open "http://$HOST:$WEB_PORT" 2>/dev/null || true
        else
            echo "Could not detect browser. Open manually:"
            echo "  http://$HOST:$WEB_PORT"
        fi

        echo ""
        echo "Press Ctrl+C to stop the server."
        wait "$SERVER_PID"
        exit 0
    fi
    sleep 1
done

echo "✗ Server failed to start within ${MAX_WAIT}s."
echo "  Check logs above for errors."
exit 1
