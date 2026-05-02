#!/usr/bin/env python3
import json
import os
import pathlib
import re
import subprocess
import sys
from datetime import datetime, date, timezone

try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None

HOME = pathlib.Path(os.path.expanduser("~"))
CAL_FILE = HOME / ".config/hypr/scripts/quickshell/calendar/apple_calendar_url"

if not CAL_FILE.exists():
    print("[]")
    sys.exit(0)

url = CAL_FILE.read_text(encoding="utf-8").strip()
if not url:
    print("[]")
    sys.exit(0)

if url.startswith("http://") or url.startswith("https://"):
    try:
        data = subprocess.check_output(["curl", "-fsSL", url], text=True)
    except Exception:
        print("[]")
        sys.exit(0)
else:
    path = pathlib.Path(os.path.expanduser(url))
    if not path.exists():
        print("[]")
        sys.exit(0)
    data = path.read_text(encoding="utf-8")

lines = []
for raw in data.splitlines():
    if raw.startswith(" ") or raw.startswith("\t"):
        if lines:
            lines[-1] += raw[1:]
    else:
        lines.append(raw)


def parse_prop(line):
    if ":" not in line:
        return None, {}, ""
    namepart, value = line.split(":", 1)
    parts = namepart.split(";")
    name = parts[0].upper()
    params = {}
    for p in parts[1:]:
        if "=" in p:
            key, val = p.split("=", 1)
            params[key.upper()] = val
    return name, params, value


def parse_dt(value, params):
    if params.get("VALUE", "").upper() == "DATE":
        return datetime.strptime(value, "%Y%m%d").date()

    if value.endswith("Z"):
        dt = datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc).astimezone()
        return dt

    try:
        dt = datetime.strptime(value, "%Y%m%dT%H%M%S")
    except ValueError:
        try:
            dt = datetime.strptime(value, "%Y%m%dT%H%M")
        except ValueError:
            dt = None
    if dt is None:
        return None

    tzid = params.get("TZID")
    if tzid and ZoneInfo is not None:
        try:
            dt = dt.replace(tzinfo=ZoneInfo(tzid)).astimezone()
        except Exception:
            pass
    return dt


def format_time(value):
    if isinstance(value, date) and not isinstance(value, datetime):
        return "All day"
    if not value:
        return ""
    local = value
    if value.tzinfo is not None:
        local = value.astimezone()
    return local.strftime("%-I:%M %p")


events = []
current = {}
in_event = False
for line in lines:
    if line == "BEGIN:VEVENT":
        current = {}
        in_event = True
        continue
    if line == "END:VEVENT":
        if not in_event:
            continue
        dtstart_raw = current.get("DTSTART")
        dtend_raw = current.get("DTEND")
        if not dtstart_raw:
            in_event = False
            continue

        start = parse_dt(dtstart_raw[1], dtstart_raw[0]) if isinstance(dtstart_raw, tuple) else None
        end = parse_dt(dtend_raw[1], dtend_raw[0]) if isinstance(dtend_raw, tuple) else None
        summary = current.get("SUMMARY", "").strip()
        description = current.get("DESCRIPTION", "").strip()
        location = current.get("LOCATION", "").strip()

        today = datetime.now().date()
        if isinstance(start, date) and not isinstance(start, datetime):
            if start == today:
                events.append({
                    "start": format_time(start),
                    "end": format_time(end) if end else "",
                    "summary": summary,
                    "description": description,
                    "location": location,
                    "all_day": True
                })
        elif isinstance(start, datetime):
            if start.date() == today:
                events.append({
                    "start": format_time(start),
                    "end": format_time(end) if end else "",
                    "summary": summary,
                    "description": description,
                    "location": location,
                    "all_day": False
                })
        in_event = False
        current = {}
        continue

    if not in_event:
        continue

    name, params, value = parse_prop(line)
    if not name:
        continue
    if name in ["DTSTART", "DTEND"]:
        current[name] = (params, value)
    else:
        current[name] = value


events.sort(key=lambda ev: ev["start"])
print(json.dumps(events))
