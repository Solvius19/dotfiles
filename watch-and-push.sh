#!/bin/bash
REPO_DIR="$HOME/dotfiles"

while true; do
  sleep 10
  cd "$REPO_DIR"
  if ! git diff --quiet || [ -n "$(git ls-files --others --exclude-standard)" ]; then
    git add .
    git commit -m "auto: save changes $(date '+%Y-%m-%d %H:%M:%S')"
    git push
  fi
done
