#!/usr/bin/env bash

# Stop all active music players
if command -v playerctl &> /dev/null; then
  playerctl pause 2>/dev/null || true
else
  # Fallback: kill common media players
  killall -SIGTERM mpv vlc ncmpcpp spotify 2>/dev/null || true
fi

# Lock the screen
exec quickshell -p ~/.config/hypr/scripts/quickshell/Lock.qml

