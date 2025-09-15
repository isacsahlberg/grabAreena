# %% [setup]
"""
lab_playground.py — scratchpad with cell-style sections.

How to run:
  uv run python lab_playground.py

Edit the variables in the CONFIG cell below (channel/date or a direct JSON path).
"""


# %% [imports & constants]
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timedelta
import argparse
import json
import os
import re
import sys

try:
    import requests
except Exception as e:
    print("Requests not installed. Run: uv add requests")
    raise

API_BASE = "https://areena.api.yle.fi/v1/ui/schedules/{channel}/{date}.json"
PARAMS = {
    "app_id": "areena-web-items",
    "app_key": "wlTs5D9OjIdeS9krPzRQR4I1PYVzoazN",
    "language": "fi",  # or "sv"
    "v": 10,
}
HEADERS = {
    "User-Agent": "grabAreena/0.1 (+https://github.com/isacsahlberg/grabAreena)",
    "Accept": "application/json",
}



# %% [CONFIG]
# Option A: use channel + date (recommended)
CHANNEL = "yle-klassinen"
DATE = "2025-09-14"  # YYYY-MM-DD

# Option B: hardcode a path to an existing JSON file for experiments (leave as None to skip)
JSON_PATH: str | None = None  # e.g., "/Users/you/.cache/grabareena/yle-klassinen/2025-09-14.json"
JSON_PATH = "./.cache_/2025-09-14.json"

# Cache location: ~/.cache/grabareena/{channel}/{date}.json
def cache_path(channel: str, date: str) -> Path:
    return Path.home() / ".cache" / "grabareena" / channel / f"{date}.json"



# %% [fetch or load]
def fetch_schedule(channel: str, date: str, *, force: bool = False) -> dict:
    """Fetch from API (or read from cache), then return JSON dict."""
    cpath = cache_path(channel, date)
    if cpath.exists() and not force:
        print(f"Reading from cache: {cpath}")
        return json.loads(cpath.read_text(encoding="utf-8"))

    url = API_BASE.format(channel=channel, date=date)
    print(f"Fetching from API: {url}")
    r = requests.get(url, params=PARAMS, headers=HEADERS, timeout=20)
    r.raise_for_status()
    data = r.json()

    cpath.parent.mkdir(parents=True, exist_ok=True)
    cpath.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved cache: {cpath}")
    return data

def load_data() -> dict:
    """Load JSON either from JSON_PATH or via fetch_schedule."""
    if JSON_PATH:
        p = Path(JSON_PATH)
        print(f"Loading JSON from explicit path: {p}")
        return json.loads(p.read_text(encoding="utf-8"))
    return fetch_schedule(CHANNEL, DATE, force=False)

DATA = load_data()
programme_items = DATA.get("data", [])
print(f"Loaded {len(programme_items)} programme items for {CHANNEL} on {DATE}.")

# # The most important of these is 'data
# programs_ = DATA['data']  # list of dicts, each with keys 



# %% [peek first item]
if items:
    first = items[0]
    print("First item keys:", list(first.keys()))
    # Labels are a list of dicts: [{'type': 'broadcastStartDate', 'formatted': ..., 'raw': ...}, ...]
    print("Available label types:", [lab.get("type") for lab in first.get("labels", [])])



# %% [helpers: labels & time]
def _label(labels: list[dict] | None, typ: str, field: str = "formatted"):
    """Return labels[i][field] where labels[i]['type']==typ, else None."""
    for lab in (labels or []):
        if lab.get("type") == typ:
            return lab.get(field)
    return None

def _iso_to_hhmm(s: str) -> str:
    """Format an ISO timestamp to HH:MM (keeps the given timezone; no conversion)."""
    if not s:
        return ""
    s = s.replace("Z", "+00:00")
    return datetime.fromisoformat(s).strftime("%H:%M")

_ISO_DUR = re.compile(r"^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$")
def _parse_duration_secs(raw: str | None) -> int | None:
    """Parse ISO-8601 durations like 'PT6H15M' to seconds; return None if unknown."""
    if not raw:
        return None
    m = _ISO_DUR.match(raw)
    if not m:
        return None
    h, m_, s = (int(x or 0) for x in m.groups())
    return h * 3600 + m_ * 60 + s



# %% [try _label on the first item]
if items:
    labs = items[0].get("labels", [])
    start_fmt = _label(labs, "broadcastStartDate", "formatted")
    start_raw = _label(labs, "broadcastStartDate", "raw")
    dur_fmt   = _label(labs, "duration", "formatted")
    dur_raw   = _label(labs, "duration", "raw")

    print("broadcastStartDate formatted:", start_fmt)
    print("broadcastStartDate raw      :", start_raw)
    print("duration formatted          :", dur_fmt)
    print("duration raw                :", dur_raw)
    print("start HH:MM                 :", _iso_to_hhmm(start_fmt))
    if dur_raw:
        print("duration seconds            :", _parse_duration_secs(dur_raw))



# %% [adapter: JSON -> legacy shapes]
def json_to_legacy_structs(data: dict):
    """
    Produce the shapes your original pipeline expects:
      programs: list[str]
      program_times: list[tuple[HH:MM, HH:MM]]
      program_contents: list[str]  (starts with programme start time)
      endtime: '+HH:MM'
    """
    items = data.get("data", [])
    # Gather all start ISO timestamps (to look up "next start" easily)
    starts_iso = [
        _label(it.get("labels"), "broadcastStartDate", "formatted")
        for it in items
    ]

    programs, program_times, program_contents = [], [], []

    for i, it in enumerate(items):
        title = it.get("title", "")
        desc  = (it.get("description") or "").strip()
        labs  = it.get("labels", [])

        start_iso  = starts_iso[i]
        start_hhmm = _iso_to_hhmm(start_iso)

        # End time: next programme's start, else start + duration
        next_iso = starts_iso[i + 1] if i + 1 < len(starts_iso) else None
        if next_iso:
            end_hhmm = _iso_to_hhmm(next_iso)
        else:
            dur_raw = _label(labs, "duration", "raw")
            secs = _parse_duration_secs(dur_raw)
            if secs is not None:
                end_hhmm = (datetime.fromisoformat(start_iso.replace("Z", "+00:00"))
                            + timedelta(seconds=secs)).strftime("%H:%M")
            else:
                end_hhmm = start_hhmm

        # Prepend programme start time so the first piece gets a time
        content = f"{start_hhmm} {desc}"

        # Normalize HH.MM → HH:MM inside descriptions
        content = re.sub(r"(?<!\d)(\d{1,2})\.(\d{2})\s", r"\1:\2 ", content)

        programs.append(title)
        program_times.append((start_hhmm, end_hhmm))
        program_contents.append(content)

    last_end = program_times[-1][1] if program_times else "06:00"
    endtime = f"+{last_end}"
    return programs, program_times, program_contents, endtime

programs, program_times, program_contents, endtime = json_to_legacy_structs(DATA)
print(f"programs: {len(programs)}, program_times: {len(program_times)}, endtime: {endtime}")



# %% [inspect adapter output]
if programs:
    print("First programme:", programs[0])
    print("Its times (start, end):", program_times[0])
    print("First 200 chars of its content:\n", program_contents[0][:200].replace("\n", " "))





# %% [optional: use your old helpers, if importable]
try:
    from grabAreena_functions import getPieces, massagePieces, printAllPieces
    print("Imported grabAreena_functions — using your original helpers.")
    # Flatten all pieces for the day:
    all_pieces = []
    for content in program_contents:
        all_pieces.extend(getPieces(content))
    all_pieces = massagePieces(all_pieces, addMorningPlus=True)
    print(f"Total pieces parsed: {len(all_pieces)}")
    # Show first 10:
    for t, p in all_pieces[:10]:
        print(t, "--", p.strip().split("\n")[0][:100])
except Exception as e:
    print("Could not import grabAreena_functions (this is fine for now).", e)



# %% [args mode (optional)]
# You can also run this file with CLI args:
#   uv run python lab_playground.py --channel yle-klassinen --date 2025-09-14
if __name__ == "__main__" and any(a.startswith("--") for a in sys.argv[1:]):
    argp = argparse.ArgumentParser()
    argp.add_argument("--channel", default=CHANNEL)
    argp.add_argument("--date", default=DATE)
    argp.add_argument("--force", action="store_true")
    args = argp.parse_args()
    data = fetch_schedule(args.channel, args.date, force=args.force)
    print(f"Fetched {len(data.get('data', []))} programmes for {args.channel} on {args.date}.")
