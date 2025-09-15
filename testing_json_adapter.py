# json_adapter.py
from datetime import datetime, timedelta
import re

def _label(labels, typ, field="formatted"):
    for lab in labels or []:
        if lab.get("type") == typ:
            return lab.get(field)
    return None

def _iso_to_hhmm(s: str) -> str:
    s = (s or "").replace("Z", "+00:00")
    return datetime.fromisoformat(s).strftime("%H:%M")

_iso_dur = re.compile(r"^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$")
def _parse_duration_secs(raw: str | None) -> int | None:
    if not raw: return None
    m = _iso_dur.match(raw)
    if not m: return None
    h, m_, s = (int(x or 0) for x in m.groups())
    return h*3600 + m_*60 + s

def json_to_legacy_structs(data: dict):
    items = data.get("data", [])
    # collect start times first (ISO)
    starts_iso = [
        _label(it.get("labels"), "broadcastStartDate", "formatted") for it in items
    ]

    programs, program_times, program_contents = [], [], []
    for i, it in enumerate(items):
        title = it.get("title", "")
        desc = (it.get("description") or "").strip()

        start_iso = starts_iso[i]
        start_hhmm = _iso_to_hhmm(start_iso)

        # end = next start, or start + duration
        next_start_iso = starts_iso[i+1] if i+1 < len(starts_iso) else None
        dur_raw = _label(it.get("labels"), "duration", "raw")
        if next_start_iso:
            end_hhmm = _iso_to_hhmm(next_start_iso)
        else:
            secs = _parse_duration_secs(dur_raw)
            if secs is not None:
                end_hhmm = (datetime.fromisoformat(start_iso.replace("Z","+00:00"))
                            + timedelta(seconds=secs)).strftime("%H:%M")
            else:
                end_hhmm = start_hhmm  # fallback

        # prepend programme start time so your regex captures the first piece
        content = f"{start_hhmm} {desc}"
        # normalize any "HH.MM " to "HH:MM "
        content = re.sub(r"(?<!\d)(\d{1,2})\.(\d{2})\s", r"\1:\2 ", content)

        programs.append(title)
        program_times.append((start_hhmm, end_hhmm))
        program_contents.append(content)

    endtime = "+" + (program_times[-1][1] if program_times else "06:00")
    return programs, program_times, program_contents, endtime
