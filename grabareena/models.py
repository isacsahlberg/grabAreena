from dataclasses import dataclass
from datetime import date
from typing import List


# for simplicity, use dataclasses
@dataclass
class Piece:
    start: str  # "HH:MM" (or "+HH:MM", "-HH:MM")
    end: str
    description: str
    def __str__(self):
        return f"{self.start:>6} - {self.end:>6}  --  {self.description}"


@dataclass
class Program:
    title: str
    start: str
    end: str
    description: str
    pieces: List[Piece]
    date: date
    url: str | None = None

    def __str__(self):
        return f"=== {self.title} ({self.start} -> {self.end}) ==="

    def matches(self, pattern: str) -> List[Piece]:
        """Return pieces where pattern appears (case-insensitive)."""
        return [p for p in self.pieces if pattern.lower() in p.description.lower()]
