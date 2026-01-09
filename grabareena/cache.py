from datetime import date, timedelta
from pathlib import Path
import json
import logging
import re

from .fetch import fetch_schedule

log = logging.getLogger(__name__)
timestamp_pattern = re.compile(r"\d{1,2}[:.]\d{2}")


def get_cache_path(day: date) -> Path:
    """
    ~/.grabareena/cache/yle-klassinen-{YYYY-MM-DD}.json
    """
    root = Path.home() / ".grabareena" / "cache"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"yle-klassinen-{day.isoformat()}.json"


def load_cache(day: date) -> dict | None:
    path = get_cache_path(day)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        log.debug("loaded cache file: %s", path.name)
        return data
    except FileNotFoundError:
        return None


def save_cache(day: date, payload: dict) -> None:
    path = get_cache_path(day)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)
    log.info("cached schedule for %s", day.isoformat())


def schedule_valid(json_, min_len=30) -> bool:
    """
    Look into the schedule, to see if the descriptions for all the programs 
    are long, or just placeholder descriptions
    Additionally, if there are no timestamps in the program descriptions, log and print a warning
    """
    datas = json_.get("data")
    if not datas:
        return False
    valid = True
    for i, data in enumerate(datas):
        descr_ = data.get("description")
        log.debug("(program #%d) len=%4d: %.30s", i, len(descr_), descr_)
        if len(descr_) < min_len:
            valid = False
        elif not timestamp_pattern.search(descr_):
            title = data.get("title", "[Unknown]")
            log.warning("Program '%s' has no timestamps in description", title)
            print(f"WARNING: Program '{title}' has no timestamps in description")
    return valid


def get_schedule(day: date, force=False, allow_placeholders=True, print_=False) -> dict:
    """
    Get schedule for the input date.
    Prints and logs a warning if the descriptions in the schedule do not include timestamps.
    If force=True, skip checking the cache, instead fetching a new schedule (and write to cache).
    If allow_placeholders=False, throw an error if the schedule is not valid (description length too short).
    """
    if not force:
        cached = load_cache(day)
        if cached is not None:
            log.debug(f"schedule already cached: {day.isoformat()}")
            return cached
    fresh = fetch_schedule(day)
    valid = schedule_valid(fresh)
    if not allow_placeholders and not valid:
        raise ValueError(f"fetched schedule for {day.isoformat()} includes a placeholder program")
    save_cache(day, fresh)
    if print_: print(f"cached schedule for {day.isoformat()}")
    return fresh


def _prefetch_forward(days_ahead=5):
    """
    Pre-fetch upcoming schedules.
    For a week ahead, there are usually program descriptions missing, or just short templates. This
    stops at the first placeholder schedule.
    """
    days = [date.today() + timedelta(days=i) for i in range(days_ahead + 1)]
    log.debug("pre-fetch forward: %s to %s", days[0], days[-1])
    for day in days:
        try:
            log.debug("pre-fetch: fetching %s", day.isoformat())
            _ = get_schedule(day, force=False, allow_placeholders=False, print_=True)
        except Exception as e:
            log.debug("pre-fetch: stopped on %s: %r", day.isoformat(), e)
            break


def _prefetch_backward(days_back=10):
    """
    Pre-fetch (backfill) past schedules.
    The database typically contains data for roughly 10 days backward. For regular use, past
    schedules are most of the time already cached.
    """
    days = [date.today() - timedelta(days=i) for i in range(1, days_back + 1)]
    cached = [d for d in days if get_cache_path(d).exists()]
    missing = [d for d in days if d not in cached]
    log.debug("pre-fetch backward: %d/%d days cached (%s to %s)",
              len(cached), len(days), days[-1], days[0])
    if not missing:
        return
    log.debug("pre-fetch backward: missing %s", [d.isoformat() for d in missing])
    for day in missing:
        try:
            log.debug("pre-fetch: fetching %s", day.isoformat())
            _ = get_schedule(day, force=False, allow_placeholders=False, print_=True)
        except Exception as e:
            log.debug("pre-fetch: failed %s: %r", day.isoformat(), e)


def prefetch():
    _prefetch_forward()
    _prefetch_backward()
