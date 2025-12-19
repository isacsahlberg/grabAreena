from typing import Sequence
import argparse
import logging

from .cache import get_schedule, prefetch
from .parse import parse_programs
from .print import print_programs, print_all_pieces, print_matches
from .utils import resolve_date, parse_patterns
from .log   import setup_logging, log_invocation


def main(argv: Sequence[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="grabareena", description="Yle Klassinen schedule grabber")
    ap.add_argument("-a", "--all", action="store_true", help="Print all pieces (for highlighting, explicitly pass the --pattern)")
    ap.add_argument("-p", "--pattern", metavar="PAT", action="append", help='Pattern(s). Can repeat or use commas, e.g. -p Bach -p Mozart or -p "Bach, Mozart"')
    ap.add_argument("-P", "--programs", action="store_true", help="List program titles/times")
    ap.add_argument("-r", "--refresh", action="store_true", help="Bypass cache (force fetch)")
    ap.add_argument("-v", "--verbose", action="store_true", help="Output (debug-level) log to the console")
    ap.add_argument("-F", "--prefetch", action="store_true", help="Prefetch the next 5 days (stop on first error)")
    # Prevent using more than one of the timing options
    when = ap.add_mutually_exclusive_group()
    when.add_argument("-d", "--date", metavar="DATE", help="Date (default: today, Finnish time); format: MM-DD or YYYY-MM-DD")
    when.add_argument("-t", "--tomorrow", action="store_true", help="Use tomorrow's date")
    when.add_argument("-y", "--yesterday", action="store_true", help="Use yesterday's date")
    when.add_argument("-T", "--after_tomorrow", action="store_true", help="Use date for day after tomorrow")
    when.add_argument("-Y", "--before_yesterday", action="store_true", help="Use date for day before yesterday")

    args = ap.parse_args(argv)
    
    # Init logging, record the full invocation
    setup_logging(verbose=args.verbose)
    log_invocation(list(argv) if argv is not None else None, program_name=__name__)
    log = logging.getLogger(__name__)

    # If run with --prefetch, then we do only that and exit
    if args.prefetch:
        return 0 if prefetch() else 1

    # Single source of truth for the date: used by cache, endpoint, and parsing
    day = resolve_date(args.date, args.tomorrow, args.yesterday, args.after_tomorrow, args.before_yesterday)
    log.debug("resolved date: %s", day.isoformat())
    
    # Fetch the schedule, log possible errors
    try:
        payload = get_schedule(day=day, force=args.refresh)
    except Exception as e:
        log.error("fetch failed for %s: %s", day, e)
        raise

    # Parse
    programs = parse_programs(payload, day)
    log.debug("parsed programs: %d", len(programs))

    patterns = parse_patterns(args.pattern)
    explicitly_passed_patterns = bool(args.pattern)
    
    # Print list of programs only
    if args.programs:
        log.debug("mode=programs")
        print_programs(programs)
        log.debug("mode=programs done")
        return

    # Print all pieces
    if args.all:
        log.debug("mode=all_pieces highlight=%s", explicitly_passed_patterns)
        # Only highlight if user explicitly passed -p
        if explicitly_passed_patterns:
            from .print import _highlight_one
            def _apply_many(text: str) -> str:
                out = text
                for pat in patterns:
                    out = _highlight_one(out, pat)
                return out
            for prog in programs:
                print(f"\n{prog.start:>5} - {prog.end:<5}  --  {prog.title}  --  {prog.url}")
                for piece in prog.pieces:
                    print(f"  {piece.start:>6} - {piece.end:>6}  --  {_apply_many(piece.description)}")
        else:
            print_all_pieces(programs)
        log.debug("mode=all_pieces done")
        return

    # Default mode (no -a/-P): show matches grouped by pattern
    log.debug("mode=matches patterns=%s", patterns)
    matched = print_matches(programs, patterns)
    if matched == 0:
        print(f"\n(No matches for {patterns})")
    log.debug(f"mode=matches patterns done (there were {matched} matches)")


if __name__ == "__main__":
    main()
