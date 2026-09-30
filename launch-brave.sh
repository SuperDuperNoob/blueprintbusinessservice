#!/usr/bin/env bash
# Launch isolated, lightweight Brave profile
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILE_DIR="$SCRIPT_DIR/.brave-profile"

mkdir -p "$PROFILE_DIR"

URLS=(
  "https://blueprintbusinessservice.com/"
  "https://mail.google.com/"
)

nohup brave-browser \
  --user-data-dir="$PROFILE_DIR" \
  --no-first-run \
  --no-default-browser-check \
  --disable-sync \
  --disable-background-networking \
  --disable-component-update \
  "${URLS[@]}" \
  "$@" > /dev/null 2>&1 &
