from datetime import datetime
import re

from .models import Piece, Program


def _label(labels, type_, field="raw"):
    """Find the first dict in labels with type==type_ and return its field (default: 'raw')."""
    for lab in labels:
        if lab.get("type") == type_:
            return lab.get(field)
    return None


def _iso_to_hhmm(iso: str) -> str:
    """Convert an ISO timestamp (e.g. '2025-09-14T00:45:00+03:00') to 'HH:MM'."""
    if not iso:
        return ""
    iso = iso.replace("Z", "+00:00")
    return datetime.fromisoformat(iso).strftime("%H:%M")


def parse_program(dict_: dict) -> Program:
    """Take a raw programme dict from the JSON and return a Program object."""
    title  = dict_.get("title", "")
    desc   = dict_.get("description", "")
    labels = dict_.get("labels", [])
    
    start_iso = _label(labels, "broadcastStartDate", field="raw")
    end_iso   = _label(labels, "broadcastEndDate", field="raw")
    
    # Convert to nicer format
    start = _iso_to_hhmm(start_iso)
    end   = _iso_to_hhmm(end_iso)

    # Split description into times + pieces
    time_pattern = r"\d{1,2}:\d{2}"  # that's "1 or 2 digits" + ":"" + "2 digits"
    # Find all substrings that have that pattern
    times = re.findall(time_pattern, desc)
    # Split the string with that pattern as the delimiter
    chunks = re.split(time_pattern, desc)

    # Since the description doesn't start with a time, we now have, say,
    #   times = ["00:55", "01:16"]
    #   chunks = [before_first_time, after_00:55, after_01:16]
    # The time for 'before_first_time' we can get from the start time of the program
    # --> Make the times list have start and end time as well
    times = [start] + times + [end]
    
    # Loop through the times and texts (end times just shifted)
    pieces = []
    for t1, t2, text_chunk in zip(times, times[1:], chunks):
        if text_chunk.strip():
            pieces.append(Piece(start=t1, end=t2, text=text_chunk.strip()))
    
    return Program(
        title=title,
        start=start,
        end=end,
        description=desc,
        pieces=pieces,
    )


def parse_programs(data: dict) -> list[Program]:
    """Take the whole JSON blob and return a list of Programs."""
    return [parse_program(dict_) for dict_ in data["data"]]

