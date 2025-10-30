from datetime import date
import json
from pathlib import Path
from typing import Optional
import requests
# import logging
# log = logging.getLogger(__name__)     # TODO: add debug statements to the functions below

API_BASE = "https://areena.api.yle.fi/v1/ui/schedules/yle-klassinen/{day}.json"
PARAMS = {
    "app_id": "areena-web-items",
    "app_key": "wlTs5D9OjIdeS9krPzRQR4I1PYVzoazN",
    "language": "fi",
    "v": 10,
    "limit": 100,
}
HEADERS = {
    "User-Agent": "testing 0.1",
    "Accept": "application/json",
}
# "User-Agent": "grabAreena/0.1 (+https://github.com/isacsahlberg/grabAreena)",


def cache_path(day: date) -> Path:
    """
    ~/.grabareena/cache/yle-klassinen-{YYYY-MM-DD}.json
    """
    root = Path.home() / ".grabareena" / "cache"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"yle-klassinen-{day.isoformat()}.json"


def load_cache(day: date) -> dict | None:
    path = cache_path(day)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None  # no cache yet


def save_cache(day: date, payload: dict) -> None:
    path = cache_path(day)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def fetch_schedule(day: date) -> dict:
    url = API_BASE.format(day=day.isoformat())
    r = requests.get(url, params=PARAMS, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.json()


def get_schedule(day: date, force: bool = False) -> dict:
    if not force:
        cached = load_cache(day)
        if cached is not None:
            return cached
    fresh = fetch_schedule(day)
    save_cache(day, fresh)
    return fresh
