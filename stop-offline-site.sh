#!/usr/bin/env bash
# Stop the BBS local streaming server and close the dedicated Chrome profile

echo "Stopping BBS local streaming server (port 5500)..."
pkill -f "python3.*bbs_server.py"

echo "Closing dedicated Chrome profile instance..."
pkill -f "google-chrome.*\.chrome-profile"

echo "All BBS offline processes closed."
