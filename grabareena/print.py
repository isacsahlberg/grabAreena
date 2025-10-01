import re
from termcolor import colored
from typing import Iterable, Sequence

from .models import Program, Piece


def _highlight_one(text: str, pattern: str) -> str:
    rx = re.compile(re.escape(pattern), re.IGNORECASE)
    return rx.sub(lambda m: colored(m.group(0), "blue", "on_cyan"), text)


def print_matches(programs: list[Program],
                             patterns: Sequence[str],
                             divider: str = " --------------") -> int:
    """
    Print matching pieces, grouped by pattern in the order given.
    Insert `divider` between pattern groups that produced output.
    Returns total number of printed lines.
    """
    pats = [p for p in patterns]
    total = 0
    printed_any_group = False

    for pat in pats:
        group_printed = False
        pat_ci = pat.casefold()
        for prog in programs:
            for piece in prog.pieces:
                if pat_ci in piece.description.casefold():
                    if printed_any_group and not group_printed and divider:
                        print(divider)  # divider between pattern groups
                    print(f"{piece.start:>6} - {piece.end:>6}  --  {_highlight_one(piece.description, pat)}")
                    group_printed = True
                    total += 1
        if group_printed:
            printed_any_group = True
    return total


def print_programs(programs: list[Program]) -> None:
    title_w = max(len(p.title) for p in programs)
    for p in programs:
        print(f"{p.start:>5} - {p.end:<5}  --  {p.title:<{title_w}}  --  {p.url}")



def print_all_pieces(programs: list[Program]) -> None:
    for p in programs:
        print(f"\n{p.start:>5} - {p.end:<5}  --  {p.title}  --  {p.url}")
        for piece in p.pieces:
            print(f"  {piece}")
