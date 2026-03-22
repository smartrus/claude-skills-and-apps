#!/bin/bash
# sync-health-data.sh — Pull/push health_data.json from your OpenClaw server
#
# Usage:
#   ./sync-health-data.sh          # pull from server → local
#   ./sync-health-data.sh --push   # push local → server (careful!)
#
# Runs daily via LaunchAgent/crontab, or manually on demand.
#
# Setup:
#   1. Set the variables below (server IP, SSH key, paths)
#   2. Make executable: chmod +x sync-health-data.sh
#   3. Test: ./sync-health-data.sh

set -euo pipefail

# ── Configuration ────────────────────────────────────────────────
# Replace these with your actual values
SERVER_SSH="ssh -o ConnectTimeout=10 -o BatchMode=yes -i $HOME/.ssh/YOUR_SSH_KEY root@YOUR_SERVER_IP"
CONTAINER_NAME="openclaw-gateway"           # Docker container name filter
CONTAINER_FILE="/home/node/health_data.json" # Path inside the container
LOCAL_FILE="$HOME/health-coach/data/health_data.json"
# ─────────────────────────────────────────────────────────────────

mkdir -p "$(dirname "$LOCAL_FILE")"

# Find the running container
get_container_id() {
    $SERVER_SSH "docker ps --filter name=$CONTAINER_NAME -q"
}

if [ "${1:-}" = "--push" ]; then
    echo "⬆️  Pushing local → server..."
    if [ ! -f "$LOCAL_FILE" ]; then
        echo "Error: $LOCAL_FILE not found"
        exit 1
    fi
    CONTAINER=$(get_container_id)
    if [ -z "$CONTAINER" ]; then
        echo "Error: Container '$CONTAINER_NAME' not running on server"
        exit 1
    fi
    cat "$LOCAL_FILE" | $SERVER_SSH "docker exec -i $CONTAINER bash -c 'cat > $CONTAINER_FILE'"
    echo "✅ Pushed $(wc -c < "$LOCAL_FILE" | tr -d ' ') bytes to server"
else
    echo "⬇️  Pulling server → local..."
    CONTAINER=$(get_container_id)
    if [ -z "$CONTAINER" ]; then
        echo "Error: Container '$CONTAINER_NAME' not running on server"
        exit 1
    fi
    REMOTE_DATA=$($SERVER_SSH "docker exec $CONTAINER cat $CONTAINER_FILE 2>/dev/null || echo '{}'")

    # Validate JSON before writing
    if echo "$REMOTE_DATA" | python3 -m json.tool > /dev/null 2>&1; then
        echo "$REMOTE_DATA" > "$LOCAL_FILE"
        # Count entries
        DAYS=$(echo "$REMOTE_DATA" | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d))" 2>/dev/null || echo "0")
        echo "✅ Synced $DAYS day(s) of data to $LOCAL_FILE"
    else
        echo "⚠️  Invalid JSON from server, skipping write"
        exit 1
    fi
fi
