from datetime import date, datetime, timedelta
from termcolor import colored

DEFAULT_PATTERNS = ["Bach", "Mozart", "Schumann"]


def parse_patterns(args_pattern) -> list[str]:
    if not args_pattern:                 # if no -p given, use defaults
        return DEFAULT_PATTERNS.copy()
    patterns = []
    for arg in args_pattern:
        patterns.extend(s.strip() for s in arg.split(",") if s.strip())
    return patterns


def _parse_date_arg(s: str) -> date:
    # try full ISO first (YYYY-MM-DD)
    try:
        return date.fromisoformat(s)
    except ValueError:
        pass
    # then allow MM-DD (assume current year)
    try:
        m, d = map(int, s.split("-", 1))
        today = date.today()
        return date(today.year, m, d)
    except Exception:
        raise SystemExit(f"Invalid --date: {s} (use YYYY-MM-DD or MM-DD)")


def resolve_date(date_str: str, tomorrow: bool, yesterday: bool, after_tomorrow: bool, before_yesterday: bool) -> date:
    # These arguments will have been mutually exclusive, so simple if statements will do
    if date_str:  return _parse_date_arg(date_str)
    if tomorrow:         return date.today() + timedelta(days=1)
    if yesterday:        return date.today() - timedelta(days=1)
    if after_tomorrow:   return date.today() + timedelta(days=2)
    if before_yesterday: return date.today() - timedelta(days=2)
    return date.today()  # If none of the timing flags were used, default to today
