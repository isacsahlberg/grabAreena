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


def prefetch(days_ahead=5):
    """
    For pre-fetching, check that the schedule programs are valid. For a week ahead, there are
    usually program descriptions missing, or just short templates.
    If we see placeholder content, we don't save those schedules to the cache.
    If we find new schedules that we add to the cache, print that to the console.
    """
    days = [date.today() + timedelta(days=i) for i in range(1, days_ahead + 1)]
    for day in days:
        try:
            log.debug("pre-fetch: fetching %s", day.isoformat())
            _ = get_schedule(day, force=False, allow_placeholders=False, print_=True)
        except Exception as e:
            log.debug("pre-fetch: stopped on %s: %r", day.isoformat(), e)
            return False
    return True
