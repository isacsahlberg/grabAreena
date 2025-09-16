from datetime import datetime, date
import re

from .models import Piece, Program


def _label(labels, type_, field="raw"):
    """Find the first dict in labels with type==type_ and return its field (default: 'raw')."""
    for lab in labels:
        if lab.get("type") == type_:
            return lab.get(field)
    return None


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


def _iso_date(iso: str) -> date:
    """
    Convert an ISO timestamp to date object, e.g.
    '2025-09-14T00:45:00+03:00' -> datetime.date(2025, 9, 14)
    """
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).date()


def fix_times(times, date_: date, start_iso, end_iso):
    """Return times with '+' prefixes where appropriate, and add start/end times."""
    # Convert the start/end times to nicer format, and fix times like 06.30 --> 06:30
    start = _iso_to_hhmm(start_iso)
    end   = _iso_to_hhmm(end_iso)
    times = [start] + [t.replace(".", ":") for t in times] + [end]

    # Find out which times need an extra "+"
    # If the end time is on this date, none of them will need it
    if _iso_date(end_iso) == date_:
        return times
    # If all pieces are after midnight, all of them will need it
    if _iso_date(start_iso) > date_:
        return ["+" + t for t in times]
    # If we cross the midnight point, let's check when that happens, when the time "drops"
    times_fixed = [times[0]]  # we already know the first one doesn't need the "+"
    plus_offset = False
    previous = _hhmm_to_min(times[0])
    for t in times[1:]:
        # Express the current time t in minutes
        current = _hhmm_to_min(t)
        if current < previous:
            plus_offset = True
        times_fixed.append(("+" if plus_offset else "") + t)
        previous = current
    return times_fixed


def parse_program(dict_: dict, date_) -> Program:
    """Take a raw programme dict from the JSON and return a Program object."""
    title  = dict_.get("title", "")
    desc   = dict_.get("description", "")
    labels = dict_.get("labels", [])
    start_iso = _label(labels, "broadcastStartDate", field="raw")
    end_iso   = _label(labels, "broadcastEndDate", field="raw")
    
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
            pieces.append(Piece(start=t1, end=t2, text=text_chunk.strip()))
    
    return Program(title=title, start=start_iso, end=end_iso, description=desc, pieces=pieces)


def parse_programs(data: dict, date_) -> list[Program]:
    """Take the whole JSON blob and return a list of Programs."""
    return [parse_program(dict_, date_) for dict_ in data["data"]]
    
    
# def parse_programs(data: dict, date_) -> list[Program]:
#     """Take the whole JSON blob and return a list of Programs."""
#     previous_time = 0  # in minutes
#     programs = []
#     for dict_ in data["data"]:
#         previous_time, program = parse_program(dict_)
#         # stuff
        
#     return programs

