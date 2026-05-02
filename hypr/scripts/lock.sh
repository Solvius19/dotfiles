#!/usr/bin/env bash

# Pause any active music
if command -v playerctl &> /dev/null; then
  playerctl pause 2>/dev/null || true
fi

# Lock with hyprlock
hyprlock

