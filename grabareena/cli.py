import argparse
from typing import Sequence

from .cache import get_schedule
from .parse import parse_programs
from .print import print_programs, print_all_pieces, print_matches
from .utils import resolve_date, parse_patterns


def main(argv: Sequence[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="grabareena", description="Yle Klassinen schedule grabber")
    ap.add_argument("-a", "--all", action="store_true", help="Print all pieces")
    ap.add_argument("-p", "--pattern", action="append", help='Pattern(s). Can repeat or use commas, e.g. -p Bach -p Mozart or -p "Bach, Mozart"')
    ap.add_argument("-P", "--programs", action="store_true", help="List program titles/times")
    ap.add_argument("-r", "--refresh", action="store_true", help="Bypass cache (force fetch)")
    # Prevent using more than one of the timing options
    when = ap.add_mutually_exclusive_group()
    when.add_argument("-d", "--date", metavar="YYYY-MM-DD|MM-DD", help="Date (default: today, Finnish time)")
    when.add_argument("-t", "--tomorrow", action="store_true", help="Use tomorrow's date")
    when.add_argument("-y", "--yesterday", action="store_true", help="Use yesterday's date")

    args = ap.parse_args(argv)
    day = resolve_date(args.date, args.tomorrow, args.yesterday)

    # Single source of truth for the date: used by cache, endpoint, and parsing
    payload = get_schedule(day=day, force=args.refresh)
    programs = parse_programs(payload, day)

    patterns = parse_patterns(args.pattern)
    explicitly_passed_patterns = bool(args.pattern)
    
    # Print list of programs only
    if args.programs:
        print_programs(programs)
        return

    # Print all pieces
    if args.all:
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
        return

    # Default mode (no -a/-P): show matches grouped by pattern
    matched = print_matches(programs, patterns)
    if matched == 0:
        print(f"\n(No matches for {patterns})")


if __name__ == "__main__":
    main()
