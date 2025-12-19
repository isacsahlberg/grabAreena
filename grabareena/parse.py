from datetime import datetime, date
import re

from .models import Piece, Program


# ----- Aux functions
def _label(labels, type_, field="raw"):
    """Find the first dict in labels with type==type_ and return its field (default: 'raw')."""
    for lab in labels:
        if lab.get("type") == type_:
            return lab.get(field)
    return None


_ID_RE = re.compile(r"\b1-\d+\b")
def _url_from_pointer(pointer: dict):
    if not isinstance(pointer, dict):
        return None
    uri = pointer.get("uri")  # e.g. "yleareena://items/1-75853752"
    if not isinstance(uri, str):
        return None
    m = _ID_RE.search(uri)
    return f"https://areena.yle.fi/{m.group(0)}" if m else None


def _hhmm_to_min(hhmm: str) -> int:
    """Express "HH:MM" in minutes"""
    h, m = map(int, hhmm.split(":"))
    return h*60 + m


def _iso_to_hhmm(iso: str) -> str:
    """
    Convert an ISO timestamp to 'HH:MM', e.g.
    '2025-09-14T00:45:00+03:00' -> '00:45'
    """
    if not iso:
        raise ValueError("Missing ISO timestamp")
    iso = iso.replace("Z", "+00:00")
    return datetime.fromisoformat(iso).strftime("%H:%M")


def _iso_to_date(iso: str) -> date:
    """
    Convert an ISO timestamp to date object, e.g.
    '2025-09-14T00:45:00+03:00' -> datetime.date(2025, 9, 14)
    """
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).date()


def _prefixed_time(t, offset):
    if offset < 0: return "-" + t
    if offset > 0: return "+" + t
    return t


def fix_times(times, date_: date, start_iso, end_iso):
    """Return times with '+' prefixes where appropriate, and add start/end times."""
    # Convert the start/end times to nicer format, and fix times like 06.30 --> 06:30
    start = _iso_to_hhmm(start_iso)
    end   = _iso_to_hhmm(end_iso)
    times = [start] + [t.replace(".", ":") for t in times] + [end]

    # Dates
    start_date = _iso_to_date(start_iso)
    end_date   = _iso_to_date(end_iso)

    # Find out which times need an extra "+"
    # If both the start time and the end time is on this date, none of them will need it
    if start_date == date_ and end_date == date_:
        return times
    # If all pieces are after midnight, all of them will need it
    if start_date > date_:
        return ["+" + t for t in times]
    
    # Determine starting offset: -1 if yesterday, 0 if today
    offset = -1 if start_date < date_ else 0
    # If we cross the midnight point, either from yesterday to today or from today to tomorrow,
    # let's check when that happens, when the time "drops"
            # times_fixed = [times[0]]  # we already know the first one doesn't need the "+"
            # plus_offset = False
    times_fixed = [_prefixed_time(times[0], offset)]
    previous = _hhmm_to_min(times[0])
    for t in times[1:]:
        current = _hhmm_to_min(t)  # Express the current time t in minutes
        if current < previous:
                    # plus_offset = True
            offset += 1
                # times_fixed.append(("+" if plus_offset else "") + t)
        times_fixed.append(_prefixed_time(t, offset))
        previous = current
    return times_fixed


# ----- Parsing functions
def parse_program(dict_: dict, date_) -> Program:
    """Take a raw programme dict from the JSON and return a Program object."""
    title  = dict_.get("title", "")
    desc   = dict_.get("description", "")
    labels = dict_.get("labels", [])
    url = _url_from_pointer(dict_.get("pointer"))  # pointer = dict_.get("pointer", {})
    start_iso = _label(labels, "broadcastStartDate", field="raw")
    end_iso   = _label(labels, "broadcastEndDate", field="raw")
    if not start_iso or not end_iso:
        raise ValueError(f"Missing broadcastStartDate/broadcastEndDate for {title!r}")
    start = _iso_to_hhmm(start_iso)
    end   = _iso_to_hhmm(end_iso)
    if not desc:
        print(f"⚠️ Missing description for {title} ({start} -> {end})")
    
    # Split description into times + pieces
    time_pattern = r"\d{1,2}[:.]\d{2}"  # that's "1 or 2 digits" + ":"" + "2 digits" (or with a dot)
    # Find all substrings that have that pattern, and split the string with that pattern as the delimiter
    raw_times = re.findall(time_pattern, desc)
    chunks = re.split(time_pattern, desc)

    # Since the description doesn't start with a time, we need to fix that manually
    # Also add an additional "+" for times that are past midnight
    times = fix_times(raw_times, date_, start_iso, end_iso)
    
    # Loop through the times and texts (end times just shifted)
    pieces = []
    for t1, t2, text_chunk in zip(times, times[1:], chunks):
        if text_chunk.strip():
            pieces.append(Piece(start=t1, end=t2, description=text_chunk.strip()))
    
    return Program(title=title, start=start, end=end, description=desc, pieces=pieces, date=date_, url=url)


def parse_programs(payload: dict, date_: date) -> list[Program]:
    """Take the whole JSON blob and return a list of Programs."""
    items = payload["data"]
    if not isinstance(items, list):
        raise ValueError(
            f"Expected payload['data'] to be a list, got {type(items).__name__}. "
            f"Top-level keys: {list(payload)[:10]}"
        )
    return [parse_program(item, date_) for item in items]
