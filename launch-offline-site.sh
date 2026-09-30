#!/usr/bin/env bash
# Start BBS Local Streaming Server and open in Chrome
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILE_DIR="$SCRIPT_DIR/.chrome-profile"
SERVER_SCRIPT="$SCRIPT_DIR/bbs_server.py"

# Check if server is responding on port 5500
if ! python3 -c "import socket; s=socket.socket(); s.settimeout(0.5); exit(0 if s.connect_ex(('127.0.0.1', 5500)) == 0 else 1)" 2>/dev/null; then
  echo "Starting BBS local streaming server on http://127.0.0.1:5500..."
  nohup python3 "$SERVER_SCRIPT" > /tmp/bbs_server.log 2>&1 &
  sleep 1
else
  echo "BBS local streaming server is already running."
fi

# Open in Chrome
nohup google-chrome \
  --user-data-dir="$PROFILE_DIR" \
  --no-first-run \
  --no-default-browser-check \
  "http://127.0.0.1:5500/" > /dev/null 2>&1 &

echo "Ready! Visit: http://127.0.0.1:5500/"
