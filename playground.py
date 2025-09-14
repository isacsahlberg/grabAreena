#!/usr/bin/env python3
"""
Playground for fetching Yle Areena schedule JSON with caching.

Usage:
  uv run python playground.py --date 2025-09-14 --channel yle-klassinen
"""

import argparse, json, os
from datetime import datetime
from pathlib import Path
import requests

API_BASE = "https://areena.api.yle.fi/v1/ui/schedules/{channel}/{date}.json"
PARAMS = {
    "app_id": "areena-web-items",
    "app_key": "wlTs5D9OjIdeS9krPzRQR4I1PYVzoazN",
    "language": "fi",
    "v": 10,
}
HEADERS = {
    "User-Agent": "testing 0.1",
    "Accept": "application/json",
}
# "User-Agent": "grabAreena/0.1 (+https://github.com/isacsahlberg/grabAreena)",

def cache_path(channel: str, date: str) -> Path:
    # let's point to: ~/.cache/grabareena/{channel}/{YYYY-MM-DD}.json
    # idiomatic pathlib style:
    return Path.home() / ".cache" / "grabareena" / channel / f"{date}.json"

def fetch_schedule(channel: str, date: str, force: bool = False) -> dict:
    path = cache_path(channel, date)
    if path.exists() and not force:
        print(f"Reading from cache: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    url = API_BASE.format(channel=channel, date=date)
    print(f"Fetching from API: {url}")
    r = requests.get(url, params=PARAMS, headers=HEADERS, timeout=20)
    r.raise_for_status()
    data = r.json()

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved cache: {path}")
    return data

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--channel", default="yle-klassinen")
    ap.add_argument("--force", action="store_true", help="ignore cache and re-fetch")
    args = ap.parse_args()

    data = fetch_schedule(args.channel, args.date, force=args.force)
    programmes = data.get("data", [])
    print(f"Got {len(programmes)} programmes.")
    if programmes:
        first = programmes[0]
        print("First programme:", first.get("title"))

if __name__ == "__main__":
    main()
