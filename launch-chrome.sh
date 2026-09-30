#!/usr/bin/env bash
# Launch isolated, lightweight Google Chrome profile
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILE_DIR="$SCRIPT_DIR/.chrome-profile"

mkdir -p "$PROFILE_DIR"

URLS=(
  "https://blueprintbusinessservice.com/"
  "https://mail.google.com/"
)

nohup google-chrome \
  --user-data-dir="$PROFILE_DIR" \
  --no-first-run \
  --no-default-browser-check \
  --disable-sync \
  --disable-background-networking \
  --disable-component-update \
  --disable-features=Translate,OptimizationHints,MediaRouter \
  "${URLS[@]}" \
  "$@" > /dev/null 2>&1 &
