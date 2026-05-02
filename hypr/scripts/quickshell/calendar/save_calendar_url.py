#!/usr/bin/env python3
import os
import pathlib
import sys

if len(sys.argv) < 2:
    sys.exit(1)

url = sys.argv[1].strip()
if not url:
    sys.exit(1)

path = pathlib.Path(os.path.expanduser("~")) / ".config/hypr/scripts/quickshell/calendar/apple_calendar_url"
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(url + "\n", encoding="utf-8")
