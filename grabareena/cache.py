from datetime import date, timedelta
import json
from pathlib import Path
from typing import Optional
import logging

from .fetch import fetch_schedule

log = logging.getLogger(__name__)     # TODO: add debug statements to the functions below


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
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None  # no cache yet


def save_cache(day: date, payload: dict) -> None:
    path = get_cache_path(day)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def get_schedule(day: date, force=False) -> dict:
    if not force:
        cached = load_cache(day)
        if cached is not None:
            return cached
    fresh = fetch_schedule(day)
    save_cache(day, fresh)
    log.info("cached %s", day)
    return fresh


"""
For pre-fetching, check that you the schedule programs are valid. For a week ahead, there are
usually program descriptions missing, or just short templates. If we see placeholder content,
we don't save those schedules to the cache.
"""
def schedule_valid(json_, min_len=30) -> bool:
    # Look into the schedule, to see if the descriptions for all the programs 
    # are long, or just placeholder descriptions
    datas = json_.get("data")
    if not datas:
        return False
    return_ = True
    for i, data in enumerate(datas):
        descr_ = data.get("description")
        log.debug("(program #%d) len=%4d: %.30s", i, len(descr_), descr_)
        if len(descr_) < min_len:
            return_ = False
    return return_


def get_schedule_validated(day: date, force=False, min_len=30):
    # if cached, just return that
    if not force:
        cached = load_cache(day)
        if cached is not None:
            log.debug(f"schedule already cached: {day.isoformat()}")
            return cached
    # fetch a fresh schedule, validate it, only then save
    fresh = fetch_schedule(day)
    if not schedule_valid(fresh, min_len=min_len):
        raise ValueError(f"schedule includes a placeholder program")
    save_cache(day, fresh)
    log.info("pre-fetch: cached schedule for %s", day.isoformat())
    return fresh


def prefetch(days_ahead=5):
    days = [date.today() + timedelta(days=i) for i in range(1, days_ahead + 1)]
    for day in days:
        try:
            log.debug("pre-fetch: fetching %s", day.isoformat())
            _ = get_schedule_validated(day, force=False)
        except Exception as e:
            log.debug("pre-fetch: stopped on %s: %r", day.isoformat(), e)
            return False
    return True

